import logging
import os
import sys

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QFileDialog, QAbstractItemView
)
from PyQt5.uic import loadUi
from pyqt5_plugins.examplebuttonplugin import QtGui

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

        self.logs_model = QtGui.QStandardItemModel()
        self.listViewLogs.setModel(self.logs_model)
        self.listViewLogs.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.code_model = QtGui.QStandardItemModel()
        self.listViewCode.setModel(self.code_model)
        self.listViewCode.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.connect_signals_slots()
        self.GCodeSender = GCodeSender(self.callback)
        self.GCodeSender.setup_log_handler()

    def connect_signals_slots(self):
        self.actionLoad.triggered.connect(self.load_file)
        self.actionExit.triggered.connect(self.close)
        self.actionGeneral.triggered.connect(self.general)
        self.actionFiltering.triggered.connect(self.filtering)
        self.actionDisplay.triggered.connect(self.display)
        self.actionConnect.triggered.connect(self.connect)
        self.spinBoxStartFrom.valueChanged.connect(self.set_starting_line)
        self.spinBoxDoTo.valueChanged.connect(self.set_ending_line)

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

        counter = 1
        for command in self.GCodeSender.buffer:
            word = str(counter) + ") " + command
            item = QtGui.QStandardItem(word)
            self.code_model.appendRow(item)
            counter += 1


        self.labelCodeLineQty.setNum(self.GCodeSender.buffer_size)

        self.spinBoxStartFrom.setEnabled(True)
        self.spinBoxStartFrom.setValue(1)
        self.spinBoxStartFrom.setMinimum(1)
        self.spinBoxStartFrom.setMaximum(self.GCodeSender.buffer_size)

        self.spinBoxDoTo.setEnabled(True)
        self.spinBoxDoTo.setValue(self.GCodeSender.buffer_size)
        self.spinBoxDoTo.setMinimum(1)
        self.spinBoxDoTo.setMaximum(self.GCodeSender.buffer_size)

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

    def set_starting_line(self):
        self.GCodeSender._set_starting_line(self.spinBoxStartFrom.value())

    def set_ending_line(self):
        self.GCodeSender._set_ending_line(self.spinBoxDoTo.value())

    def callback(self, eventstring, *data):
        args = []
        for d in data:
            args.append(str(d))
        log = "{} data={}".format(eventstring.ljust(30), ", ".join(args))
        item = QtGui.QStandardItem(log)
        self.logs_model.appendRow(item)


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


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
