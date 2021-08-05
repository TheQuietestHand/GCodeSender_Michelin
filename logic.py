import logging
import time
import re
import threading
import atexit

import numpy.linalg

from gcode_machine.gcode_machine import GcodeMachine
from connection_interface import Interface

from queue import Queue


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
            "500",  # current feed
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

        self.view_gcode_parser_state = False

        self.view_hash_state = False

        # Initializing logger
        self.logger = logging.getLogger("GCodeSender")
        self.logger.setLevel(5)
        self.logger.propagate = False

        self.connected = False

        # Preprocessor is the gcode state machine emulator.
        # It helps to parse code before they are sent out via serial port
        self.preprocessor = GcodeMachine()
        self.preprocessor.callback = self._preprocessor_callback

        # The total distance of all G-Codes in the buffer.
        self.travel_distance_buffer = 0.0

        # The currently travelled distance.
        self.travel_distance_current = 0.0

        self.is_standstill = False

        self._standstill_watchdog_increment = 0

        self._interface_port = None
        self._last_setting_number = 132

        self._rx_buffer_size = 128
        self._rx_buffer_fill = []
        self._rx_buffer_backlog = []
        self._rx_buffer_backlog_line_number = []

        self._starting_line = 0
        self._ending_line = 0
        self.is_motion_line = []
        self.motion_line_nr = 0

        self._current_line = ""
        self._current_line_sent = True
        self._wait_empty_buffer = False
        self._streaming_complete = True
        self.job_finished = True
        self._streaming_src_ends = True
        self._streaming_enabled = False
        self._error = False
        self._incremental_streaming = True
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

        self._loghandler = None

        self._counter = 0

        self._callback = callback

        atexit.register(self.disconnect)

        self._callback("Settings downloaded", self.settings)
        self._callback("Hash state update", self.settings_hash)
        self.preprocessor.cs_offsets = self.settings_hash
        self._callback("Gcode parser state update", self.gps)

        self.points = []
        self.cube_points = []
        self.cube_edges = []
        self.colors = []
        self.cube_colors = []

        self.XMinMax = []
        self.YMinMax = []
        self.ZMinMax = []
        self.difX = 0.0
        self.difY = 0.0
        self.difZ = 0.0

        self.FMinMax = []
        self.difF = 0

        self.last_motion_mode = None
        self.last_position = None
        self.current_position = None

        self.remaining_time = 0.0
        self.force_send_command_nr = 0

    @property
    def current_line_number(self):
        return self._current_line_nr

    @current_line_number.setter
    def current_line_number(self, linenr):
        if linenr < self.buffer_size:
            self._current_line_nr = linenr
            self._callback("Line number change", self._current_line_nr)

    @property
    def starting_line(self):
        return self._starting_line

    @starting_line.setter
    def starting_line(self, line):
        if line < 1:
            self._starting_line = 1
        elif line > self.ending_line:
            self._starting_line = self.ending_line
        else:
            self._starting_line = line

    @property
    def ending_line(self):
        return self._ending_line

    @ending_line.setter
    def ending_line(self, line):
        if line > self.buffer_size:
            self._ending_line = self.buffer_size
        elif line < self.starting_line:
            self._ending_line = self.starting_line
        else:
            self._ending_line = line

    @property
    def incremental_streaming(self):
        return self._incremental_streaming

    @incremental_streaming.setter
    def incremental_streaming(self, onoff):
        self._incremental_streaming = onoff
        if self._incremental_streaming:
            self._wait_empty_buffer = True
        self.logger.debug("Incremental streaming set to {}".format(self._incremental_streaming))

    def setup_log_handler(self):
        lh = CallbackLogHandler()
        self._loghandler = lh
        self.logger.addHandler(self._loghandler)
        self._loghandler.callback = self._callback

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
            pass

        self.get_points_from_buffer()
        if len(self.XMinMax) == 2 and len(self.YMinMax) == 2 and len(self.ZMinMax) == 2:
            self.difX = abs(self.XMinMax[1] - self.XMinMax[0])
            self.difY = abs(self.YMinMax[1] - self.YMinMax[0])
            self.difZ = abs(self.ZMinMax[1] - self.ZMinMax[0])
            self.get_cube()
            self.calculate_buffer_travel_distance()

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

        self.ending_line = self.buffer_size
        self._callback("Buffer size change", self.buffer_size)
        self._callback("Vars change", self.preprocessor.vars)

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

    def job_run(self):
        if self.buffer_size == 0:
            self.logger.warning("Cant run job. Nothing in the buffer!")
            return

        self.current_line_number = self._starting_line - 1

        self.travel_distance_current = 0.0

        self._set_streaming_src_ends(False)
        self._set_streaming_complete(False)
        self._streaming_enabled = True
        self._current_line_sent = True
        self._set_job_finished(False)
        self._stream()

    def reset_all_settings(self):
        del self.buffer[:]
        self.buffer_size = 0
        self._current_line_nr = 0
        self.motion_line_nr = 0
        self.force_send_command_nr = 0
        self._callback("Line number change", 0)
        self._callback("Buffer size change", 0)
        self._set_streaming_complete(True)
        self.job_finished = True
        self._set_streaming_src_ends(True)
        self._error = False
        self._current_line = ""
        self._current_line_sent = True
        self.travel_distance_buffer = 0.0
        self.travel_distance_current = 0.0
        self.starting_line = 0
        self.ending_line = 0
        self.last_motion_mode = None
        self.points.clear()
        self.cube_points.clear()
        self.cube_edges.clear()
        self.colors.clear()
        self.cube_colors.clear()
        self.is_motion_line.clear()
        self.XMinMax.clear()
        self.YMinMax.clear()
        self.ZMinMax.clear()
        self.FMinMax.clear()
        self.difX = 0.0
        self.difY = 0.0
        self.difZ = 0.0
        self.difF = 0.0

    def view_settings(self):
        if self.is_connected() is True:
            self._interface_write("$$\n")

    def soft_reset(self):
        if self.is_connected() is True:
            self._interface_write("\x18")
            self.update_preprocessor_position()

    def reset(self):
        if self.is_connected() is True:
            port = self._interface.port
            baud = self._interface.baud
            self.disconnect()
            self.connect(port, baud)

    def kill_alarm(self):
        if self.is_connected() is True:
            self._interface_write("$X\n")

    def feed_hold(self):
        if self.is_connected() is True:
            self._interface_write("!")

    def resume(self):
        if self.is_connected() is True:
            self._interface_write("~")

    def homing(self):
        if self.is_connected() is True:
            self._interface_write("$H\n")

    def send_immediately(self, line):
        if self.cmode == "Alarm":
            self.logger.error("Grbl is in ALARM state. Will not send: {}".format(line))
            return

        self.preprocessor.set_line(line)
        self.preprocessor.strip()
        self.preprocessor.tidy()
        self.preprocessor.parse_state()
        self.preprocessor.override_feed()

        self._interface_write(self.preprocessor.line + "\n")

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
                        if self.view_hash_state:
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

                elif "Grbl" in line:
                    self._callback("Read", line)
                    self._on_boot_up()
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
            if self.is_standstill is True:
                self._standstill_watchdog_increment = 0
                self.is_standstill = False
                self._callback("Movement")
        else:
            self._standstill_watchdog_increment += 1

        if self.is_standstill is False and self._standstill_watchdog_increment > 10:
            self.is_standstill = True
            self._callback("Standstill")

        self._last_cmode = self.cmode
        self._last_cmpos = self.cmpos
        self._last_cwpos = self.cwpos

    def _update_gcode_parser_state(self, line):
        m = re.match(
            "\[G(\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) G(\d\d) M(\d) M(\d) M(\d) T(\d) F([\d.-]*?) S([\d.-]*?)\]", line)
        if m:
            self.gps[0] = m.group(1)  # motion mode
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

    def _handle_ok(self):
        if self.incremental_streaming is False:
            self.force_send_command_nr += 1
            queued_commands = self.ending_line - (self.starting_line + 1) - self.force_send_command_nr
            self._callback("Q", queued_commands)
        if self._streaming_complete is False:
            self._rx_buffer_fill_pop()
            if not (self._wait_empty_buffer and len(self._rx_buffer_fill) > 0):
                self._wait_empty_buffer = False
                self._stream()

    def _on_boot_up(self):
        self._on_boot_init()
        self.connected = True
        self._callback("Grbl has booted!")

    def _on_boot_init(self):
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

    def _clear_queue(self):
        try:
            junk = self._queue.get_nowait()
            self.logger.debug("Discarding junk {}".format(junk))
        except:
            pass

    def _poll_state(self):
        while self._poll_keep_alive:
            self._counter += 1

            if self.view_hash_state:
                self.get_hash_state()
                self.view_hash_state = False

            elif self.view_gcode_parser_state:
                self.get_gcode_parser_state()
                self.view_gcode_parser_state = False

            else:
                self._get_state()

            time.sleep(self.poll_interval)

        self.logger.debug("Polling has been stopped")

    def poll_start(self):
        if self.is_connected() is False:
            return
        self._poll_keep_alive = True
        self._last_cmode = None
        if self._thread_polling is None:
            self._thread_polling = threading.Thread(target=self._poll_state)
            self._thread_polling.start()
            self.logger.debug("{}: Polling thread started")
        else:
            self.logger.debug("Polling thread already running...")

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

        if self.current_line_number == self._ending_line:
            self._set_streaming_src_ends(True)
            return

        if self._incremental_streaming:
            self._set_next_line()

            if self.is_motion_line[self._current_line_nr] is True:
                if self.last_position is not None:
                    self.travel_distance_current += numpy.linalg.norm(self.last_position - self.current_position)
                    self.calculate_remaining_time()
                self.last_position = self.current_position
                self.current_position = numpy.array((self.points[self.motion_line_nr][0],
                                                     self.points[self.motion_line_nr][1],
                                                     self.points[self.motion_line_nr][2]))
                self.motion_line_nr += 1

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

    def _rx_buffer_fill_pop(self):
        if len(self._rx_buffer_fill) > 0:
            self._rx_buffer_fill.pop(0)
            processed_command = self._rx_buffer_backlog.pop(0)
            ln = self._rx_buffer_backlog_line_number.pop(0)
            self._callback("Processed command", ln, processed_command)

        if self._streaming_src_ends is True and len(self._rx_buffer_fill) == 0:
            self._set_job_finished(True)
            self._set_streaming_complete(True)

    def _fill_rx_buffer_until_full(self):
        while True:
            if self._current_line_sent is True:
                self._set_next_line()

            if self._streaming_src_ends is False and self._rx_buffer_can_receive_current_line() and \
                    self.current_line_number < self._ending_line:
                self._send_current_line()
            else:
                break

    def _rx_buffer_can_receive_current_line(self):
        rx_free_bytes = self._rx_buffer_size - sum(self._rx_buffer_fill)
        required_bytes = len(self._current_line) + 1
        return rx_free_bytes >= required_bytes

    def save_buffer_with_new_feed_rate(self, path=None):
        if path is None or self.buffer_size == 0:
            return

        last_feed_rate = None
        buffer_with_new_feed_rate = []

        for line in self.buffer:
            if line.find("G") != -1:
                last_motion_mode = line[line.find("G"):line.find("G") + 3]

            feed_rate = self.calculate_feed_rate(line)
            if line.find("F") != -1:
                start = line.find("F")
                stop = start + 1
                while line[stop].isalpha() is False and stop < len(line) - 1 and line[stop] != ";":
                    stop += 1
                if stop == len(line) - 1:
                    line = line[0:start]
                else:
                    line = line[0:start] + line[stop + 1:len(line)]

            if feed_rate != last_feed_rate and feed_rate is not None and last_motion_mode != "G00":
                line += "F" + str(feed_rate)
                last_feed_rate = feed_rate
            buffer_with_new_feed_rate.append(line)

        with open(path[0], 'w') as file:
            for l in buffer_with_new_feed_rate:
                file.write(l+"\n")

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

    def calculate_remaining_time(self):
        if float(self.gps[10]) > 0:
            self.remaining_time = ((self.travel_distance_buffer - self.travel_distance_current) / float(self.gps[10])) * 60
            if self.remaining_time < 1:
                self.remaining_time = 1.0

    def calculate_buffer_travel_distance(self):
        self.travel_distance_buffer = 0.0
        if self.starting_line == 1 and self.ending_line == self.buffer_size:
            for x in range(0, len(self.points) - 2):
                a = numpy.array((self.points[x][0], self.points[x][1], self.points[x][2]))
                b = numpy.array((self.points[x + 1][0], self.points[x + 1][1], self.points[x + 1][2]))
                self.travel_distance_buffer += numpy.linalg.norm(a - b)
        else:
            motion_line_nr = self.is_motion_line[0:self.starting_line-1].count(True)
            self.motion_line_nr = motion_line_nr
            for x in range(self.starting_line - 1, self.ending_line - 1):
                if self.is_motion_line[x] is True:
                    a = numpy.array((self.points[motion_line_nr][0], self.points[motion_line_nr][1],
                                     self.points[motion_line_nr][2]))
                    while x+1 < len(self.is_motion_line) and self.is_motion_line[x+1] is False:
                        x += 1
                    if x+1 == len(self.is_motion_line) and self.is_motion_line[x] is False:
                        break
                    b = numpy.array((self.points[motion_line_nr+1][0], self.points[motion_line_nr+1][1],
                                     self.points[motion_line_nr+1][2]))
                    motion_line_nr += 1
                    self.travel_distance_buffer += numpy.linalg.norm(a - b)

    def calculate_feed_rate(self, line):
        z = self.get_z(line)
        if z is not None:
            x = z - self.ZMinMax[0]
            x_percent = x / self.difZ * 100
            return int(self.FMinMax[0] + (self.difF * float(x_percent / 100)))
        else:
            return None

    def _set_next_line(self, send_comments=False):
        if self.incremental_streaming:
            queued_commands = self.ending_line - (self._current_line_nr + 1)
            self._callback("Q", queued_commands)

        if self._current_line_nr + 1 < self.buffer_size:
            line = self.buffer[self._current_line_nr].strip()
            if line.find("G") != -1:
                self.last_motion_mode = line[line.find("G"):line.find("G") + 3]
            if self.preprocessor.do_feed_override is True and self.last_motion_mode != "G00" and line.find("Z") != -1:
                self.preprocessor.request_feed = self.calculate_feed_rate(line)
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
        self._callback("Streaming complete")

    def _set_streaming_src_ends(self, x):
        self._streaming_src_ends = x
        self._callback("Streaming source ends")

    def get_hash_state(self):
        if self.cmode == "Hold":
            self.view_hash_state = False
            self.logger.info("$# command not supported in Hold mode.")
            return

        if self._hash_state_sent is False:
            self._interface_write("$#\n")
            self._hash_state_sent = True

    def get_gcode_parser_state(self):
        self._interface_write("$G\n")

    def _get_state(self):
        self._interface.write("?")

    def get_z(self, line):
        if line.find("Z") != -1:
            start = line.find("Z") + 1
            stop = start
            while line[stop].isalpha() is False and stop < len(line) - 1 and line[stop] != ";":
                stop += 1
            if start == stop:
                z = float(line[start])
            else:
                if stop == len(line) - 1:
                    z = float(line[start:stop + 1])
                else:
                    z = float(line[start:stop])

            return z
        else:
            return None

    def get_cube(self):
        self.cube_points = [(self.XMinMax[0], self.YMinMax[0], self.ZMinMax[0]),
                            (self.XMinMax[1], self.YMinMax[0], self.ZMinMax[0]),
                            (self.XMinMax[1], self.YMinMax[0], self.ZMinMax[1]),
                            (self.XMinMax[0], self.YMinMax[0], self.ZMinMax[1]),
                            (self.XMinMax[0], self.YMinMax[1], self.ZMinMax[0]),
                            (self.XMinMax[1], self.YMinMax[1], self.ZMinMax[0]),
                            (self.XMinMax[1], self.YMinMax[1], self.ZMinMax[1]),
                            (self.XMinMax[0], self.YMinMax[1], self.ZMinMax[1])]

        self.cube_edges = [0, 1, 2, 3,
                        3, 2, 6, 7,
                        1, 0, 4, 5,
                        2, 1, 5, 6,
                        0, 3, 7, 4,
                        7, 6, 5, 4]

        self.cube_colors = [(1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0),
                            (1.0, 1.0, 1.0)]

    def get_points_from_buffer(self):
        last_motion_mode = None

        for command in self.buffer:

            if command.find("G") != -1:
                last_motion_mode = command[command.find("G"):command.find("G") + 3]

            if command.find("F") != -1:
                start = command.find("F") + 1
                stop = start
                while command[stop].isalpha() is False and stop < len(command) - 1 and command[stop] != ";":
                    stop += 1
                if start == stop:
                    f = int(command[start])
                else:
                    if stop == len(command) - 1:
                        f = int(command[start:stop+1])
                    else:
                        f = int(command[start:stop])

                if len(self.FMinMax) < 2:
                    self.FMinMax.append(f)
                    self.FMinMax.append(f)
                elif f < self.FMinMax[0]:
                    self.FMinMax[0] = f
                elif f > self.FMinMax[1]:
                    self.FMinMax[1] = f

            if command.find("X") != -1 or command.find("Y") != -1 or command.find("Z") != -1:
                if last_motion_mode == "G00":
                    self.colors.append((131.0/255.0, 224.0/255.0, 30.0/255.0))
                elif last_motion_mode != "G00":
                    self.colors.append((255.0/255.0, 10.0/255.0, 50.0/255.0))

                if command.find("X") != -1:
                    start = command.find("X") + 1
                    stop = start
                    while command[stop].isalpha() is False and stop < len(command) - 1 and command[stop] != ";":
                        stop += 1
                    if start == stop:
                        x = float(command[start])
                    else:
                        if stop == len(command) - 1:
                            x = float(command[start:stop + 1])
                        else:
                            x = float(command[start:stop])

                        if last_motion_mode != "G00" and len(self.XMinMax) < 2:
                            self.XMinMax.append(x)
                            self.XMinMax.append(x)
                        elif last_motion_mode != "G00" and x < self.XMinMax[0]:
                            self.XMinMax[0] = x
                        elif last_motion_mode != "G00" and x > self.XMinMax[1]:
                            self.XMinMax[1] = x

                elif len(self.points) == 0:
                    x = 0
                else:
                    x = self.points[len(self.points) - 1][0]

                if command.find("Y") != -1:
                    start = command.find("Y") + 1
                    stop = start
                    while command[stop].isalpha() is False and stop < len(command) - 1 and command[stop] != ";":
                        stop += 1
                    if start == stop:
                        y = float(command[start])
                    else:
                        if stop == len(command) - 1:
                            y = float(command[start:stop + 1])
                        else:
                            y = float(command[start:stop])

                    if last_motion_mode != "G00" and len(self.YMinMax) < 2:
                        self.YMinMax.append(y)
                        self.YMinMax.append(y)
                    elif last_motion_mode != "G00" and y < self.YMinMax[0]:
                        self.YMinMax[0] = y
                    elif last_motion_mode != "G00" and y > self.YMinMax[1]:
                        self.YMinMax[1] = y

                elif len(self.points) == 0:
                    y = 0
                else:
                    y = self.points[len(self.points) - 1][1]

                if command.find("Z") != -1:
                    z = self.get_z(command)

                    if last_motion_mode != "G00" and len(self.ZMinMax) < 2:
                        self.ZMinMax.append(z)
                        self.ZMinMax.append(z)
                    elif last_motion_mode != "G00" and z < self.ZMinMax[0]:
                        self.ZMinMax[0] = z
                    elif last_motion_mode != "G00" and z > self.ZMinMax[1]:
                        self.ZMinMax[1] = z

                elif len(self.points) == 0:
                    z = 0
                else:
                    z = self.points[len(self.points) - 1][2]

                p = (x, y, z)
                self.points.append(p)
                self.is_motion_line.append(True)
            else:
                self.is_motion_line.append(False)


class CallbackLogHandler(logging.StreamHandler):
    def __init__(self, callback=None):
        super(CallbackLogHandler, self).__init__()
        self.callback = callback

    def emit(self, log):
        if self.callback:
            self.callback("Program log", log)
