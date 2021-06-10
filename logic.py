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

        # "firmware" - serial port, "simulator" - simulator
        self.target = "firmware"

        # "True" if connected to grbl
        self.connected = False

        # Preprocesor is the gcode state machine emulator.
        # It helps to parse code before they are sent out via serial port
        self.preprocesor = GcodeMachine()
        self.preprocesor.callback = self.preprocesor.callback

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
        self.streaming_complete = True
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

        self._callback("on_settings_downloaded", self.settings)
        self._callback("on_hash_stateupdate", self.settings_hash)
        self.preprocesor.cs_offsets = self.settings_hash
        self._callback("on_gcode_parser_stateupdate", self.gps)

    def load_file(self, filepath):
        if not self.job_finished:
            self.logger.warning("You cant load file if another project is running!"
                                "Abort current project or wait until end.")
            return

        self.reset_all_settings()

        with open(filepath) as file:
            self._load_file_into_buffer(file.read())

        self._set_starting_line()
        self._set_ending_line()

    def reset_all_settings(self):
        del self.buffer[:]
        self.buffer_size = 0
        self._current_line_nr = 0
        self._callback("on_line_number_change", 0)
        self._callback("on_buffer_size_change", 0)
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

        if len(file) > 0:
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

            self._callback("on_bufsize_change", self.buffer_size)
            self._callback("on_vars_change", self.preprocessor.vars)
        else:
            self.logger.error("Cant load empty file!")

    def disconnect(self):
        return

    def _set_streaming_complete(self, x):
        self.streaming_complete = x

    def _set_streaming_src_ends(self, x):
        self._streaming_src_ends = x

    def _set_starting_line(self, x=0):

        if self.buffer_size > 0:
            if x > 0:
                self._starting_line = x - 1
            else:
                self._starting_line = 0

    def _set_ending_line(self, x=0):

        if self.buffer_size > 0:
            if x > 0:
                self._ending_line = x - 1
            else:
                self._ending_line = self.buffer_size - 1
