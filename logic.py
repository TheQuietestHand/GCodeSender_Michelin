import logging
import time
import re
import threading
import atexit
import os
import collections

from queue import Queue


class GCodeSender:
    __version__ = 0.01

    def __init__(self):

        #Grbl's mode
        self.cmode = None
        self.last_cmode = None

        #Coordinates relative to the machine origin
        self.cmpos = (0, 0, 0)
        self.last_cmpos = (0, 0, 0)
        #Working coordinates
        self.cwpos = (0, 0, 0)
        self.last_cwpos = (0, 0, 0)

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

        #Interval of polling grbl`s state (0.2 = 5 per second, '?')
        self.poll_interval = 0.2

        #EPROM settings ('$$')
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

        # The total distance of all G-Codes in the buffer.
        self.buffer_travel_distance = {}

        # "True" if the machine is moving
        self.is_moving = False

        self.standstill_watchdog_increment = 0

        self.rx_buffer_size = 128
        self.rx_buffer_fill = []
        self.rx_buffer_backlog = []
        self.rx_buffer_backlog_line_number = []
        self.rx_buffer_fill_percent = 0

        self.starting_line = 0
        self.ending_line = 0
        self.current_line = ""
        self.current_line_sent = True
        self.streaming_mode = None
        self.wait_empty_buffer = False
        self.streaming_complete = True
        self.job_finished = True
        self.streaming_src_ends = True
        self.streaming_enabled = False
        self.error = False
        self.incremental_streaming = False
        self.hash_state_sent = False

        self.buffer = []
        self.buffer_size = 0
        self.current_line_nr = 0

        self.buffer_stash = []
        self.buffer_size_stash = 0
        self.current_line_nr_stash = 0

        self.poll_keep_alive = False

        self.thread_polling = None

        self.queue = Queue()

        self.longhandler = None

        self.counter = 0

        atexit.register(self.disconnect)

    def loadFile(self, filepath):
        self.filepath = filepath
