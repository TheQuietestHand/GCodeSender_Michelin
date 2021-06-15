import logging
import time
import re
import threading
import atexit
import os
import collections
from gcode_machine.gcode_machine import GcodeMachine
from connection_interface import Interface

from queue import Queue

import callback


class GCodeSender:
    __version__ = 0.01

    def __init__(self, callback):

        # Grbl's mode
        self.cmode = None
        self._last_cmode = None

        # Coordinates relative to the machine origin
        self.cmpos = (0, 0, 0)
        self._last_cmpos = (0, 0, 0)

        # Working coordinates
        self.cwpos = (0, 0, 0)
        self._last_cwpos = (0, 0, 0)

        # List of 12 elements containing the 12 Gcode Parser State variables of Grbl ('$G')
        self.gps = [
            "0",  # motion mode
            "54",  # current coordinate system
            "17",  # current plane mode
            "21",  # units
            "90",  # current distance mode
            "94",  # feed rate mode
            "0",  # program mode
            "0",  # spindle state
            "5",  # coolant state
            "0",  # tool number
            "99",  # current feed
            "0",  # spindle speed
        ]

        # Interval of polling grbl`s state (0.2 = 5 per second, '?')
        self.poll_interval = 0.2

        # EPROM settings ('$$')
        self.settings = {
            130: {"val": "1000", "cmt": "width"},
            131: {"val": "1000", "cmt": "height"}
        }

        # Hash settings ('$#')
        self.settings_hash = {
            "G54": (-600, -300, 0),
            "G55": (-400, -300, 0),
            "G56": (-200, -300, 0),
            "G57": (-600, -600, 0),
            "G58": (-400, -600, 0),
            "G59": (-200, -600, 0),
            "G28": (0, 0, 0),
            "G30": (0, 0, 0),
            "G92": (0, 0, 0),
            "TLO": 0,
            "PRB": (0, 0, 0),
        }

        # Set 'True' to send to grbl '$G' command.
        self.view_gcode_parser_state = False

        # Set 'True' to get callback with the hash settings
        self.view_hash_state = False

        self.logger = logging.getLogger("GCodeSender")
        self.logger.setLevel(5)
        self.logger.propagate = False

        # "True" if connected to grbl
        self.connected = False

        # Preprocessor is the gcode state machine emulator.
        # It helps to parse code before they are sent out via serial port
        self.preprocessor = GcodeMachine()
        self.preprocessor.callback = self._preprocessor_callback

        # The total distance of all G-Codes in the buffer.
        self.travel_distance_buffer = {}

        # The currently travelled distance.
        self.travel_distance_current = {}

        # "True" if the machine is moving
        self.is_moving = False

        self._standstill_watchdog_increment = 0

        # Name of serial port to connect
        self._interface_port = None
        self._last_setting_number = 132

        self._rx_buffer_size = 128
        self._rx_buffer_fill = []
        self._rx_buffer_backlog = []
        self._rx_buffer_backlog_line_number = []
        self._rx_buffer_fill_percent = 0

        self._starting_line = 0
        self._ending_line = 0
        self._current_line = ""
        self._current_line_sent = True
        self._streaming_mode = None
        self._wait_empty_buffer = False
        self._streaming_complete = True
        self.job_finished = True
        self._streaming_src_ends = True
        self._streaming_enabled = False
        self._error = False
        self._incremental_streaming = False
        self._hash_state_sent = False

        self.buffer = []
        self.buffer_size = 0
        self._current_line_nr = 0

        self.buffer_stash = []
        self.buffer_size_stash = 0
        self._current_line_nr_stash = 0

        self._poll_keep_alive = False
        self._interface_read_do = False

        self._thread_polling = None
        self._thread_read_interface = None

        self._interface = None
        self._queue = Queue()

        self._longhandler = None

        self._counter = 0

        self._callback = callback

        atexit.register(self.disconnect)

        self._callback("Settings downloaded", self.settings)
        self._callback("Hash state update", self.settings_hash)
        self.preprocessor.cs_offsets = self.settings_hash
        self._callback("Gcode parser state update", self.gps)

    def setup_log_handler(self):
        lh = CallbackLogHandler()
        self._longhandler = lh
        self.logger.addHandler(self._longhandler)
        self._longhandler.callback = self._callback

    def load_file(self, filepath):
        if not self.job_finished:
            self.logger.warning("You cant load file if another project is running!"
                                "Abort current project or wait until end.")
            return

        self.reset_all_settings()

        try:
            with open(filepath) as file:
                self._load_file_into_buffer(file.read())
        except:
            return

    def connect(self, port=None, baudrate=115200):
        if port is None or port.strip() == "":
            self.logger.error("Cant connect. Variable ""port"" is empty!")
            return
        else:
            self._interface_port = port

        if self._interface is None:
            self.logger.info("Launching interface on port {}".format(self._interface_port))
            self._interface = Interface(self._interface_port, self._callback, baudrate)
            self._interface.setup_log_handler()
            self._interface.start(self._queue)
        else:
            self.logger.error("Cant launch interface if another is running!")

        self._interface_read_do = True
        self._thread_read_interface = threading.Thread(target=self._on_read)
        self._thread_read_interface.start()

        self.soft_reset()

    def reset_all_settings(self):
        del self.buffer[:]
        self.buffer_size = 0
        self._current_line_nr = 0
        self._callback("Line number change", 0)
        self._callback("Buffer size change", 0)
        self._set_streaming_complete(True)
        self.job_finished = True
        self._set_streaming_src_ends(True)
        self._error = False
        self._current_line = ""
        self._current_line_sent = True
        self.travel_distance_buffer = {}
        self.travel_distance_current = {}

    def _load_file_into_buffer(self, file):

        lines = file.split("\n")

        for line in lines:
            self.preprocessor.set_line(line)
            splited_lines = self.preprocessor.split_lines()

            for l1 in splited_lines:
                self.preprocessor.set_line(l1)
                self.preprocessor.strip()
                self.preprocessor.tidy()
                self.preprocessor.parse_state()
                self.preprocessor.find_vars()
                fractionized_lines = self.preprocessor.fractionize()

                for l2 in fractionized_lines:
                    self.buffer.append(l2)
                    self.buffer_size += 1

                self.preprocessor.done()

        self._callback("Buffer size change", self.buffer_size)
        self._callback("Vars change", self.preprocessor.vars)

    def disconnect(self):
        if not self.is_connected():
            return

        self.poll_stop()

        self._interface.stop()
        self._interface = None

        self.logger.debug("Please wait, joining reading thread.")
        self._interface_read_do = False
        self._queue.put("Lubie_zielone_banany_i_niebieskie_pomidory")
        self._thread_read_interface.join()
        self.logger.debug("Reading thread successfully joined.")

        self.connected = False

        self._callback("Disconnected")

    def view_settings(self):
        self._interface_write("$$\n")

    def soft_reset(self):
        self._interface_write("\x18")
        self.update_preprocessor_position()

    def _preprocessor_callback(self, event, *data):
        if event == "Var undefined":
            self.logger.critical("Streaming stopped because undefined var founded: {}".format(data[0]))
            self._set_streaming_src_ends(True)
            self.stop_streaming()
        else:
            self._callback(event, *data)

    def _on_read(self):
        while self._interface_read_do is True:
            line = self._queue.get()

            if len(line) > 0:
                if line[0] == "<":
                    self._update_state(line)

                elif line == "ok":
                    self._handle_ok()

                elif re.match("^\[G[0123] .*", line):
                    self._update_gcode_parser_state(line)
                    self._callback("Read", line)

                elif re.match("^\[...:.*", line):
                    self._update_hash_state(line)
                    self._callback("Read", line)

                    if "PRB" in line:
                        if self.view_hash_state == True:
                            self._hash_state_sent = False
                            self.view_hash_state = False
                            self._callback("Hash state update", self.settings_hash)
                            self.preprocessor.cs_offsets = self.settings_hash
                        else:
                            self._callback("Probe", self.settings_hash["PRB"])

                elif "ALARM" in line:
                    self.cmode = "Alarm"
                    self._callback("State update", self.cmode, self.cmpos, self.cwpos)
                    self._callback("Read", line)
                    self._callback("Alarm", line)

                elif "error" in line:
                    self.logger.debug("Error")
                    self._error = True
                    self.logger.debug("Rx_buffer_backlog at time of error: {}".format(self._rx_buffer_backlog))
                    if len(self._rx_buffer_backlog) > 0:
                        problem_command = self._rx_buffer_backlog[0]
                        problem_line = self._rx_buffer_backlog_line_number[0]
                    else:
                        problem_command = "unknown"
                        problem_line = -1
                    self._callback("Error", line, problem_command, problem_line)
                    self._set_streaming_complete(True)
                    self._set_streaming_src_ends(True)

                elif "Grbl " in line:
                    self._callback("Read", line)
                    self._on_bootup()
                    self.view_hash_state = True
                    self.view_settings()
                    self.view_gcode_parser_state = True

                else:
                    m = re.match("\$(.*)=(.*) \((.*)\)", line)
                    if m:
                        key = int(m.group(1))
                        val = m.group(2)
                        comment = m.group(3)
                        self.settings[key] = {
                            "val": val,
                            "cmt": comment
                        }
                        self._callback("Read", line)
                        if key == self._last_setting_number:
                            self._callback("Settings downloaded", self.settings)
                    else:
                        self._callback("Read", line)
                        self.logger.info("Could not parse settings: {}".format(line))

    def update_preprocessor_position(self):
        self.preprocessor.position_m = list(self.cmpos)

    def _update_hash_state(self, line):
        line = line.replace("]", "").replace("[", "")
        parts = line.split(":")
        key = parts[0]
        tpl_str = parts[1].split(",")
        tpl = tuple([float(x) for x in tpl_str])
        self.settings_hash[key] = tpl

    def _update_state(self, line):
        match = re.match("<(.*?),MPos:(.*?),WPos:(.*?)>", line)
        self.cmode = match.group(1)
        mpos_parts = match.group(2).split(",")
        wpos_parts = match.group(3).split(",")
        self.cmpos = (float(mpos_parts[0]), float(mpos_parts[1]), float(mpos_parts[2]))
        self.cwpos = (float(wpos_parts[0]), float(wpos_parts[1]), float(wpos_parts[2]))

        if (self.cmode != self._last_cmode or
                self.cmpos != self._last_cmpos or
                self.cwpos != self._last_cwpos):
            self._callback("State update", self.cmode, self.cmpos, self.cwpos)
            if self._streaming_complete is True and self.cmode == "Idle":
                self.update_preprocessor_position()
                self.gcode_parser_state_requested = True

        if self.cmpos != self._last_cmpos:
            if self.is_moving is False:
                self._standstill_watchdog_increment = 0
                self.is_moving = True
                self._callback("Movement")
        else:
            self._standstill_watchdog_increment += 1

        if self.is_moving is True and self._standstill_watchdog_increment > 10:
            self.is_moving = False
            self._callback("Standstill")

        self._last_cmode = self.cmode
        self._last_cmpos = self.cmpos
        self._last_cwpos = self.cwpos

    def _update_gcode_parser_state(self, line):
        m = re.match(
            "\[G(\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) M(\d) M(\d) M(\d) T(\d) F([\d.-]*?) S([\d.-]*?)\]", line)
        if m:
            self.gps[0] = m.group(1)  # motionmode
            self.gps[1] = m.group(2)  # current coordinate system
            self.gps[2] = m.group(3)  # plane
            self.gps[3] = m.group(4)  # units
            self.gps[4] = m.group(5)  # dist
            self.gps[5] = m.group(6)  # feed rate mode
            self.gps[6] = m.group(7)  # program mode
            self.gps[7] = m.group(8)  # spindle state
            self.gps[8] = m.group(9)  # coolant state
            self.gps[9] = m.group(10)  # tool number
            self.gps[10] = m.group(11)  # current feed
            self.gps[11] = m.group(12)  # current rpm
            self._callback("Gcode parser state update", self.gps)

            self.update_preprocessor_position()
        else:
            self.logger.error("Could not parse gcode parser report: '{}'".format(line))


    def _rx_buffer_fill_pop(self):
        if len(self._rx_buffer_fill) > 0:
            self._rx_buffer_fill.pop(0)
            processed_command = self._rx_buffer_backlog.pop(0)
            ln = self._rx_buffer_backlog_line_number.pop(0) - 1
            self._callback("Processed command", ln, processed_command)

        if self._streaming_src_ends is True and len(self._rx_buffer_fill) == 0:
            self._set_job_finished(True)
            self._set_streaming_complete(True)

    def _handle_ok(self):
        if self._streaming_complete is False:
            self._rx_buffer_fill_pop()
            if not (self._wait_empty_buffer and len(self._rx_buffer_fill) > 0):
                self._wait_empty_buffer = False
                self._stream()

    def _on_bootup(self):
        self._onboot_init()
        self.connected = True
        self._callback("Grbl has booted!")

    def _onboot_init(self):
        del self._rx_buffer_fill[:]
        del self._rx_buffer_backlog[:]
        del self._rx_buffer_backlog_line_number[:]
        self._set_streaming_complete(True)
        self._set_job_finished(True)
        self._set_streaming_src_ends(True)
        self._error = False
        self._current_line = ""
        self._current_line_sent = True
        self._clear_queue()
        self.is_standstill = False
        self.preprocessor.reset()
        self._callback("Progress as a percentage", 0)
        self._callback("Rx buffer as a percentage", 0)

    def _clear_queue(self):
        try:
            junk = self._queue.get_nowait()
            self.logger.debug("Discarding junk {}".format(junk))
        except:
            pass

    def poll_stop(self):
        if self.is_connected() is False:
            return
        if self._thread_polling is not None:
            self._poll_keep_alive = False
            self.logger.debug("Please wait, joining polling thread.")
            self._thread_polling.join()
            self.logger.debug("Polling thread has successfully joined!")
        else:
            self.logger.debug("Cannot start a polling thread. Another one is already running.")

        self._thread_polling = None

    def _stream(self):
        if self._streaming_src_ends:
            return

        if self._streaming_enabled is False:
            return

        if self._incremental_streaming:
            self._set_next_line()
            if self._streaming_src_ends is False:
                self._send_current_line()
            else:
                self._set_job_finished(True)
        else:
            self._fill_rx_buffer_until_full()

    def stop_streaming(self):
        self._streaming_enabled = False

    def is_connected(self):
        return self.connected

    def _fill_rx_buffer_until_full(self):
        while True:
            if self._current_line_sent is True:
                self._set_next_line()

            if self._streaming_src_ends is False and self._rx_buffer_can_receive_current_line():
                self._send_current_line()
            else:
                break

    def _rx_buffer_can_receive_current_line(self):
        rx_free_bytes = self._rx_buffer_size - sum(self._rx_buffer_fill)
        required_bytes = len(self._current_line) + 1
        return rx_free_bytes >= required_bytes

    def _send_current_line(self):
        if self._error:
            self.logger.error("Firmware reported error. Stopping streaming!")
            self._set_streaming_src_ends(True)
            self._set_streaming_complete(True)
            return

        self._set_streaming_complete(False)

        line_length = len(self._current_line) + 1
        self._rx_buffer_fill.append(line_length)
        self._rx_buffer_backlog.append(self._current_line)
        self._rx_buffer_backlog_line_number.append(self._current_line_nr)
        self._interface_write(self._current_line + "\n")

        self._current_line_sent = True
        self._callback("Line sent", self._current_line_nr, self._current_line)

    def _interface_write(self, line):
        if self._interface:
            self._callback("Writing", line)
            self._interface.write(line)

    def _set_next_line(self, send_comments=False):
        progress_percent = int(100 * self._current_line_nr / self.buffer_size)
        self._callback("Progress as a percentage", progress_percent)

        if self._current_line_nr < self.buffer_size:
            line = self.buffer[self._current_line_nr].strip()
            self.preprocessor.set_line(line)
            self.preprocessor.substitute_vars()
            self.preprocessor.parse_state()
            self.preprocessor.override_feed()
            self.preprocessor.scale_spindle()

            if send_comments is True:
                self._current_line = self.preprocessor.line + self.preprocessor.comment
            else:
                self._current_line = self.preprocessor.line

            self._current_line_sent = False
            self._current_line_nr += 1

            self.preprocessor.done()

        else:
            self._set_streaming_src_ends(True)

    def _set_job_finished(self, x):
        self.job_finished = x

    def _set_streaming_complete(self, x):
        self._streaming_complete = x

    def _set_streaming_src_ends(self, x):
        self._streaming_src_ends = x

    def _set_starting_line(self, x=0):
        self._starting_line = x

    def _set_ending_line(self, x=0):
        self._ending_line = x


class CallbackLogHandler(logging.StreamHandler):
    def __init__(self, callback=None):
        super(CallbackLogHandler, self).__init__()
        self.callback = callback

    def emit(self, log):
        if self.callback:
            self.callback("Program log", log)
