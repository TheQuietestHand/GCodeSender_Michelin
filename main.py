import logging
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QFileDialog
)
from PyQt5.uic import loadUi

from components.main_window import Ui_MainWindow
from components.general_window import Ui_DialogGeneral
from components.display_window import Ui_DialogDisplay
from components.connect_window import Ui_DialogConnect
from components.filtering_window import Ui_DialogFiltering
from logic import GCodeSender

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()
        self.logger = logging.getLogger("GCodeSender")
        self.logger.setLevel(5)
        self.logger.propagate = False
        self.GCodeSender = GCodeSender(callback)

    def connect_signals_slots(self):
        self.actionLoad.triggered.connect(self.load_file)
        self.actionExit.triggered.connect(self.close)
        self.actionGeneral.triggered.connect(self.general)
        self.actionFiltering.triggered.connect(self.filtering)
        self.actionDisplay.triggered.connect(self.display)
        self.actionConnect.triggered.connect(self.connect)

    def load_file(self):
        file_filter = "Text files (*.txt)|*.txt"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a data file",
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter="Text files (*.txt)|*.txt"
        )
        self.GCodeSender.load_file(response[0])

    def general(self):
        dialog_general = DialogGeneral(self)
        dialog_general.exec()

    def filtering(self):
        dialog_filtering = DialogFiltering(self)
        dialog_filtering.exec()

    def display(self):
        dialog_display = DialogDisplay(self)
        dialog_display.exec()

    def connect(self):
        dialog_connect = DialogConnect(self)
        dialog_connect.exec()



class DialogGeneral(QDialog, Ui_DialogGeneral):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.checkBoxCalculate.stateChanged.connect(self.calculate_feed)

    def calculate_feed(self):
        if self.checkBoxCalculate.isChecked():
            self.doubleSpinBoxCutterDiameter.setEnabled(True)
            self.spinBoxSurfaceSpeed.setEnabled(True)
            self.doubleSpinBoxToothLoad.setEnabled(True)
            self.spinBoxNumberOfTeeth.setEnabled(True)
        else:
            self.doubleSpinBoxCutterDiameter.setEnabled(False)
            self.spinBoxSurfaceSpeed.setEnabled(False)
            self.doubleSpinBoxToothLoad.setEnabled(False)
            self.spinBoxNumberOfTeeth.setEnabled(False)


class DialogFiltering(QDialog, Ui_DialogFiltering):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.checkBoxLimitZRate.stateChanged.connect(self.limit_z_rate)

    def limit_z_rate(self):
        if self.checkBoxLimitZRate.isChecked():
            self.doubleSpinBoxZRateLimit.setEnabled(True)
            self.doubleSpinBoxXYRate.setEnabled(True)
        else:
            self.doubleSpinBoxZRateLimit.setEnabled(False)
            self.doubleSpinBoxXYRate.setEnabled(False)


class DialogDisplay(QDialog, Ui_DialogDisplay):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.checkBoxEnablePositionRequest.stateChanged.connect(self.enable_position_request)

    def enable_position_request(self):
        if self.checkBoxEnablePositionRequest.isChecked():
            self.radioButtonAlwaysRequest.setEnabled(True)
            self.radioButtonAlwaysWithoutIDLE.setEnabled(True)
            self.radioButtonNotDuringManual.setEnabled(True)
            self.doubleSpinBoxRequestFrequency.setEnabled(True)
        else:
            self.radioButtonAlwaysRequest.setEnabled(False)
            self.radioButtonAlwaysWithoutIDLE.setEnabled(False)
            self.radioButtonNotDuringManual.setEnabled(False)
            self.doubleSpinBoxRequestFrequency.setEnabled(False)


class DialogConnect(QDialog, Ui_DialogConnect):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

def callback(eventstring, *data):
    args = []
    for d in data:
        args.append(str(d))
    print("MY CALLBACK: event={} data={}".format(eventstring.ljust(30), ", ".join(args)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
