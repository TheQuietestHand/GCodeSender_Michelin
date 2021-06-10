import serial
import time
import threading
import logging
import sys


class Interface:
    def __init__(self, port, baud=115200):

        self.port = port
        self.baud = baud
        self.queue = None
        self.logger = logging.getLogger("connection_interface")

        self._buf_receive = ""
        self._do_receive = False

    def start(self, queue):

        self.queue = queue

        self.logger.info("Connecting to %s with baudrate %i", self.port, self.baud)

        try:
            self.serialport = serial.Serial(self.port, self.baud, parity=serial.PARITY_NONE,
                                            stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1,
                                            writeTimeout=0)
            self.serialport.flushInput()
            self.serialport.flushOutput()
            self._do_receive = True
            self.serial_thread = threading.Thread(target=self._receiving)
            self.logger.info("Connected!")
            self.serial_thread.start()
        except:
            self.logger.error("Cant connect: ", sys.exc_info()[0])

    def stop(self):

        self._do_receive = False
        self.logger.info("Ending connection")
        self.serial_thread.join()
        self.logger.info("Joined thread")
        self.logger.info("Closing port")
        self.serialport.flushInput()
        self.serialport.flushOutput()
        self.serialport.close()
        self.logger.info("Port closed!")

    def write(self, data):

        try:
            if len(data) > 0:
                # Number of written chars is returned
                return self.serialport.write(bytes(data, "ascii"))
            else:
                self.logger.debug("Nothing to write!")
        except:
            self.logger.error("Cant write data: ", sys.exc_info()[0])

    def _receiving(self):

        try:
            while self._do_receive is True:
                data = self.serialport.read(1)
                waiting = self.serialport.inWaiting()
                data += self.serialport.read(waiting)
                self._handle_data(data)
        except:
            self.logger.error("Cant receive data:", sys.exc_info()[0])

    def _handle_data(self, data):

        try:
            asci = data.decode("ascii")
        except UnicodeDecodeError:
            self.logger.info("Received a non-ascii byte. Dropping it.")
            asci = ""

        for i in range(0, len(asci)):
            char = asci[i]
            self._buf_receive += char
            # not all received lines are complete (end with \n)
            if char == "\n":
                self.queue.put(self._buf_receive.strip())
                self._buf_receive = ""