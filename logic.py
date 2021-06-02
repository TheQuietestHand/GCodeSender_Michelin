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

        #Coordinates relative to the machine origin
        self.cmpos = (0, 0, 0)
        #Working coordinates
        self.cwpos = (0, 0, 0)

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

        self.buffer = []
        self.buffer_size = 0

    def loadFile(self, filepath):
        self.filepath = filepath
