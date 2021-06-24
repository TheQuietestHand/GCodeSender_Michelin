import os
import sys
import serial.tools.list_ports
import time
import threading

from OpenGLVisualisation import MyOpenGlWidget

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


class RuntimeClock(threading.Thread):
    def __init__(self, labelRuntimeVar=None, last_state=None):
        threading.Thread.__init__(self)
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())
        self.run_time_sec = -1
        self.labelRuntimeVar = labelRuntimeVar
        self.last_state = last_state

    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()

                self.run_time_sec += 1
                self.labelRuntimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.run_time_sec)))
                time.sleep(1)

    def pause(self):
        self.paused = True
        self.pause_cond.acquire()

    def resume(self):
        self.paused = False
        self.pause_cond.notify()
        self.pause_cond.release()

    def reset(self):
        self.paused = True
        self.labelRuntimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(0)))
        self.run_time_sec = -1


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

        self.console_model = QtGui.QStandardItemModel()
        self.listViewConsole.setModel(self.console_model)
        self.listViewCode.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.connect_signals_slots()
        self.sender = GCodeSender(self.callback)
        self.sender.setup_log_handler()

        self.is_file_load = False
        self.is_polling_on = False
        self.is_incremental_streaming = True
        self.is_first_run = True

        self.run_time_clock = RuntimeClock(self.labelRuntimeVar, self.labelLastStateVar.text())
        self.last_state_checker = threading.Thread(target=self.check_state)

        self.last_distance_mode = None

        self.openGL = MyOpenGlWidget(parent=self.frameGL)
        self.openGL.setMinimumSize(985, 711)

    def connect_signals_slots(self):
        # Menu bar
        self.actionLoad.triggered.connect(self.load_file)
        self.actionExit.triggered.connect(self.close)
        self.actionGeneral.triggered.connect(self.general)
        self.actionFiltering.triggered.connect(self.filtering)
        self.actionDisplay.triggered.connect(self.display)
        self.actionConnect.triggered.connect(self.connect)
        self.actionDisconnect.triggered.connect(self.disconnect)
        self.actionSoft_reset.triggered.connect(self.soft_reset)

        # State
        self.pushButtonPause.clicked.connect(self.feed_hold)
        self.pushButtonResume.clicked.connect(self.resume)
        self.pushButtonStop.clicked.connect(self.kill_alarm)

        # XYZ Motion
        self.pushButtonHome.clicked.connect(self.homing)

        # Manual control
        self.pushButtonXManualControlPlus.clicked.connect(self.manual_X_plus)
        self.pushButtonXManualControlMinus.clicked.connect(self.manual_X_minus)

        self.pushButtonYManualControlPlus.clicked.connect(self.manual_Y_plus)
        self.pushButtonYManualControlMinus.clicked.connect(self.manual_Y_minus)

        self.pushButtonZManualControlPlus.clicked.connect(self.manual_Z_plus)
        self.pushButtonZManualControlMinus.clicked.connect(self.manual_Z_minus)

        # Code
        self.pushButtonRunCode.clicked.connect(self.start_stream_code)
        self.spinBoxStartFrom.valueChanged.connect(self.set_starting_line)
        self.spinBoxDoTo.valueChanged.connect(self.set_ending_line)

        # Console
        self.pushButtonSendCode.clicked.connect(self.send_code_manual)

    def load_file(self):
        file_filter = "Text files (*.txt)|*.txt"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a data file",
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter="Text files (*.txt)|*.txt"
        )

        self.sender.load_file(response[0])

        counter = 1
        for command in self.sender.buffer:
            word = str(counter) + ") " + command
            item = QtGui.QStandardItem(word)
            self.code_model.appendRow(item)
            counter += 1

        self.labelCodeLineQty.setNum(self.sender.buffer_size)

        self.spinBoxStartFrom.setEnabled(True)
        self.spinBoxStartFrom.setValue(1)
        self.spinBoxStartFrom.setMinimum(1)
        self.spinBoxStartFrom.setMaximum(self.sender.buffer_size)

        self.spinBoxDoTo.setEnabled(True)
        self.spinBoxDoTo.setValue(self.sender.buffer_size)
        self.spinBoxDoTo.setMinimum(1)
        self.spinBoxDoTo.setMaximum(self.sender.buffer_size)

        self.is_file_load = True
        self.prepare_to_streaming()

    def manual_X_plus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("X" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 X" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def manual_X_minus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("X-" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 X-" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def manual_Y_plus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("Y" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 Y" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def manual_Y_minus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("Y-" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 Y-" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def manual_Z_plus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("Z" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 Z" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def manual_Z_minus(self):
        if self.last_distance_mode == "G91":
            self.sender.send_immediately("Z-" + str(self.doubleSpinBoxStep.value()))
        else:
            self.sender.send_immediately("G91 Z-" + str(self.doubleSpinBoxStep.value()))
            self.sender.send_immediately("G90")

    def send_code_manual(self):
        line = self.lineEditCodeToSend.text()
        self.lineEditCodeToSend.setText("")
        self.sender.send_immediately(line)
        item = QtGui.QStandardItem("> {}".format(line))
        self.console_model.appendRow(item)

    def feed_hold(self):
        self.pushButtonPause.setEnabled(False)
        self.pushButtonResume.setEnabled(True)

        self.sender.feed_hold()
        self.labelLastStateVar.setText("Hold")

    def resume(self):
        self.pushButtonPause.setEnabled(True)
        self.pushButtonResume.setEnabled(False)

        self.sender.resume()
        self.labelLastStateVar.setText("Run")

    def kill_alarm(self):
        self.pushButtonPause.setEnabled(False)
        self.pushButtonResume.setEnabled(False)
        self.pushButtonStop.setEnabled(False)

        self.sender.kill_alarm()
        self.labelLastStateVar.setText("Hold")

    def homing(self):
        self.sender.homing()
        if self.pushButtonPause.isEnabled() is False and self.pushButtonPause.isEnabled() is False \
                and self.pushButtonStop.isEnabled() is False:
            self.pushButtonResume.setEnabled(True)
            self.pushButtonStop.setEnabled(True)
            self.labelLastStateVar.setText("Run")

    def start_stream_code(self):
        self.pushButtonPause.setEnabled(True)
        self.pushButtonStop.setEnabled(True)
        self.pushButtonRunCode.setEnabled(False)

        self.sender.job_run()
        self.labelLastStateVar.setText("Run")

        if self.is_first_run:
            self.run_time_clock.start()
            self.last_state_checker.start()
            self.is_first_run = False

    def general(self):
        dialog_general = DialogGeneral(self, self.sender, self.is_incremental_streaming)
        dialog_general.exec()

    def filtering(self):
        dialog_filtering = DialogFiltering(self)
        dialog_filtering.exec()

    def display(self):
        dialog_display = DialogDisplay(self, self.sender, self.is_polling_on)
        dialog_display.exec()
        self.is_polling_on = dialog_display.is_polling_on

    def soft_reset(self):
        self.sender.soft_reset()

    def prepare_to_streaming(self):
        if self.is_file_load is True and self.actionDisconnect.isEnabled() is True:
            self.pushButtonRunCode.setEnabled(True)
            self.spinBoxPeriod.setEnabled(True)

        self.pushButtonHome.setEnabled(True)
        self.pushButtonSetZero.setEnabled(True)
        self.pushButtonZero.setEnabled(True)

        self.pushButtonXManualControlPlus.setEnabled(True)
        self.pushButtonXManualControlMinus.setEnabled(True)
        self.pushButtonYManualControlPlus.setEnabled(True)
        self.pushButtonYManualControlMinus.setEnabled(True)
        self.pushButtonZManualControlPlus.setEnabled(True)
        self.pushButtonZManualControlMinus.setEnabled(True)
        self.doubleSpinBoxStep.setEnabled(True)
        self.checkBoxG90Step.setEnabled(True)

        if self.is_polling_on:
            self.sender.poll_start()

        if self.is_first_run is False:
            self.run_time_clock.reset()

    def connect(self):
        dialog_connect = DialogConnect(self, self.sender)
        dialog_connect.exec()
        time.sleep(2)
        if self.sender.is_connected() is True:
            self.actionDisconnect.setEnabled(True)
            self.actionSoft_reset.setEnabled(True)
            self.actionReset.setEnabled(True)
            self.actionConnect.setEnabled(False)
            self.pushButtonSendCode.setEnabled(True)
            self.lineEditCodeToSend.setEnabled(True)

            self.prepare_to_streaming()

        self.sender.incremental_streaming = self.is_incremental_streaming
        self.labelLastStateVar.setText("Idle")

    def disconnect(self):
        self.sender.disconnect()
        if self.sender.is_connected() is False:
            self.actionDisconnect.setDisabled(True)
            self.actionSoft_reset.setDisabled(True)
            self.actionReset.setDisabled(True)
            self.actionConnect.setDisabled(False)
            self.set_buttons_disabled()

        self.labelLastStateVar.setText("NaN")

    def set_starting_line(self):
        self.sender.starting_line = self.spinBoxStartFrom.value()
        self.spinBoxDoTo.setMinimum(self.spinBoxStartFrom.value())

    def set_ending_line(self):
        self.sender.ending_line = self.spinBoxDoTo.value()
        self.spinBoxStartFrom.setMaximum(self.spinBoxDoTo.value())

    def set_buttons_disabled(self):
        self.pushButtonRunCode.setEnabled(False)
        self.spinBoxPeriod.setEnabled(False)

        self.pushButtonPause.setEnabled(False)
        self.pushButtonResume.setEnabled(False)
        self.pushButtonStop.setEnabled(False)

        self.pushButtonHome.setEnabled(False)
        self.pushButtonSetZero.setEnabled(False)
        self.pushButtonZero.setEnabled(False)

        self.pushButtonXManualControlPlus.setEnabled(False)
        self.pushButtonXManualControlMinus.setEnabled(False)
        self.pushButtonYManualControlPlus.setEnabled(False)
        self.pushButtonYManualControlMinus.setEnabled(False)
        self.pushButtonZManualControlPlus.setEnabled(False)
        self.pushButtonZManualControlMinus.setEnabled(False)
        self.doubleSpinBoxStep.setEnabled(False)
        self.checkBoxG90Step.setEnabled(False)

        self.pushButtonSendCode.setEnabled(False)
        self.lineEditCodeToSend.setEnabled(False)

    def callback(self, eventstring, *data):
        args = []
        for d in data:
            args.append(str(d))

        if eventstring == "Gcode parser state update":
            self.last_distance_mode = d[4]
            self.lineEditFeedRate.setText(str(d[10]))
            self.lineEditSpeedSpindle.setText(str(d[11]))

        if eventstring == "Writing":
            if "G90" in d:
                self.last_distance_mode = "G90"
            elif "G91" in d:
                self.last_distance_mode = "G91"

        if eventstring == "State update":
            self.labelLastStateVar.setText(args[0])

            mpos = tuple(map(float, args[1][1:-1].split(', ')))
            self.lineEditXMachine.setText(str(mpos[0]))
            self.lineEditYMachine.setText(str(mpos[1]))
            self.lineEditZMachine.setText(str(mpos[2]))

            wpos = tuple(map(float, args[2][1:-1].split(', ')))
            self.lineEditXWork.setText(str(wpos[0]))
            self.lineEditYWork.setText(str(wpos[1]))
            self.lineEditZWork.setText(str(wpos[2]))

        log = "{}: {}".format(eventstring.ljust(30), ", ".join(args))
        item = QtGui.QStandardItem(log)
        self.logs_model.appendRow(item)

    def check_state(self):
        is_running = True
        while True:
            if self.labelLastStateVar.text() != "Run" and is_running is True:
                self.run_time_clock.pause()
                is_running = False
            elif self.labelLastStateVar.text() == "Run" and is_running is False:
                self.run_time_clock.resume()
                is_running = True


class DialogGeneral(QDialog, Ui_DialogGeneral):
    def __init__(self, parent=None, sender=None, is_incremental_streaming=True):
        super().__init__(parent)
        self.setupUi(self)
        self.is_incremental_streaming = is_incremental_streaming
        self.sender = sender
        if self.is_incremental_streaming:
            self.checkBoxAgresivePreload.setChecked(False)
        else:
            self.checkBoxAgresivePreload.setChecked(True)
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.checkBoxCalculate.stateChanged.connect(self.calculate_feed)
        self.pushButtonOk.clicked.connect(self.closing_dialog)

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

    def closing_dialog(self):
        if self.checkBoxAgresivePreload.isChecked():
            self.is_incremental_streaming = False
        else:
            self.is_incremental_streaming = True

        self.sender.incremental_streaming = self.is_incremental_streaming


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
    def __init__(self, parent=None, sender=None, is_polling_on=False):
        super().__init__(parent)
        self.sender = sender
        self.is_polling_on = is_polling_on
        self.setupUi(self)

        self.checkBoxEnablePositionRequest.setChecked(self.is_polling_on)
        self.doubleSpinBoxRequestFrequency.setEnabled(self.is_polling_on)

        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.pushButtonOk.clicked.connect(self.closing_dialog)
        self.checkBoxEnablePositionRequest.clicked.connect(self.onof_spin_box)

    def closing_dialog(self):
        if self.checkBoxEnablePositionRequest.isChecked():
            self.doubleSpinBoxRequestFrequency.setEnabled(True)
            self.sender.poll_start()
            self.is_polling_on = True
        else:
            self.doubleSpinBoxRequestFrequency.setEnabled(False)
            self.sender.poll_stop()
            self.is_polling_on = False

        self.sender.poll_interval = self.doubleSpinBoxRequestFrequency.value()

    def onof_spin_box(self):
        self.doubleSpinBoxRequestFrequency.setEnabled(self.checkBoxEnablePositionRequest.isChecked())


class DialogConnect(QDialog, Ui_DialogConnect, GCodeSender):
    def __init__(self, parent=None, sender=None):
        super().__init__(parent)
        self.sender = sender
        self.setupUi(self)
        self.connect_signals_slots()
        self.load_port_selector()

    def connect_signals_slots(self):
        self.pushButtonConnect.clicked.connect(self.connect_device)

    def connect_device(self):
        self.sender.connect(self.comboBoxPortName.currentText(), int(self.comboBoxBaudRate.currentText()))
        self.close()

    def load_port_selector(self):
        self.comboBoxPortName.clear()
        ports = list(serial.tools.list_ports.comports())

        if len(ports) == 0:
            self.comboBoxPortName.addItem('')
            return

        for port in ports:
            self.comboBoxPortName.addItem(port.name)


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
