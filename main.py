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
        self.gsender = GCodeSender()
        self.setupUi(self)
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.actionLoad.triggered.connect(self.getFileName)
        self.actionExit.triggered.connect(self.close)
        self.actionGeneral.triggered.connect(self.general)
        self.actionFiltering.triggered.connect(self.filtering)
        self.actionDisplay.triggered.connect(self.display)
        self.actionConnect.triggered.connect(self.connect)

    def getFileName(self):
        file_filter = "Text files (*.txt)|*.txt"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a data file",
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter="Text files (*.txt)|*.txt"
        )
        self.gsender.loadFile(response[0])

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
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.checkBoxCalculate.stateChanged.connect(self.calculateFeed)

    def calculateFeed(self):
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
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.checkBoxLimitZRate.stateChanged.connect(self.limitZRate)

    def limitZRate(self):
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
        self.connectSignalsSlots()

    def connectSignalsSlots(self):
        self.checkBoxEnablePositionRequest.stateChanged.connect(self.enablePositionRequest)

    def enablePositionRequest(self):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
