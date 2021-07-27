import datetime
import os
import sys
import serial.tools.list_ports
import time
import threading
import configparser

from PyQt5.QtCore import QTimer

from OpenGLVisualisation import MyOpenGlWidget

from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QFileDialog, QAbstractItemView
)
from pyqt5_plugins.examplebuttonplugin import QtGui

from components.main_window import Ui_MainWindow
from components.general_window import Ui_DialogGeneral
from components.display_window import Ui_DialogDisplay
from components.connect_window import Ui_DialogConnect
from components.filtering_window import Ui_DialogFiltering
from components.feedrate_window import Ui_DialogFeedRate
from logic import GCodeSender


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Some flags
        self.is_file_load = False
        self.is_polling_on = False
        self.is_incremental_streaming = True
        self.is_rt_feed_rate_on = False
        self.is_simple_take_feed_min = False
        self.is_simple_take_feed_max = False
        self.last_distance_mode = None
        self.save_logs_to_file = False

        # Logs file name
        self.logs = "Logs file - " + str(datetime.datetime.now()).replace(':', "") + ".txt"

        # Logs list view model init
        self.logs_model = QtGui.QStandardItemModel()
        self.listViewLogs.setModel(self.logs_model)
        self.listViewLogs.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Code list view model init
        self.code_model = QtGui.QStandardItemModel()
        self.listViewCode.setModel(self.code_model)
        self.listViewCode.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Console list view model init
        self.console_model = QtGui.QStandardItemModel()
        self.listViewConsole.setModel(self.console_model)
        self.listViewCode.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # OpenGL widget init
        self.openGL = MyOpenGlWidget(parent=self.frameGL)
        self.openGL.setGeometry(0, 0, 0, 0)
        self.openGL.resize(1, 1)
        self.openGL_timer = QTimer(self)
        self.openGL_timer.setInterval(20)
        self.openGL_timer.timeout.connect(self.updateGL)
        self.openGL_timer.start()
        self.render_start_point = 0
        self.render_end_point = 0

        # Settings from config file init
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
            self.save_logs_to_file = config["SENDER"].getbool("SaveLogs")
            self.is_incremental_streaming = config["SENDER"].getbool("IncrementalStreaming")
            self.is_polling_on = config["SENDER"].getbool("Polling")
        except:
            pass

        # Sender init
        self.sender = GCodeSender(self.callback)
        self.sender.setup_log_handler()

        # Runtime clock init
        self.run_time_timer = QTimer(self)
        self.run_time_timer.setInterval(1000)
        self.run_time_timer.timeout.connect(self.timer)
        self.run_time_sec = 0
        self.remaining_time = 0
        self.run_time_timer.start()

        # Connecting signal slots
        self.connect_signals_slots()

    def connect_signals_slots(self):
        # Menu bar
        self.actionLoad.triggered.connect(self.load_file)
        self.actionExit.triggered.connect(self.closeEvent)
        self.actionGeneral.triggered.connect(self.general)
        self.actionFeed_rate.triggered.connect(self.feed_rate)
        self.actionFiltering.triggered.connect(self.filtering)
        self.actionDisplay.triggered.connect(self.display)
        self.actionConnect.triggered.connect(self.connect)
        self.actionDisconnect.triggered.connect(self.disconnect)
        self.actionSoft_reset.triggered.connect(self.soft_reset)
        self.actionReset.triggered.connect(self.reset)

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

    def updateGL(self):
        size = self.frameGL.size()
        self.openGL.resize(size.width(), size.height())
        self.openGL.resizeGL(size.width(), size.height())
        self.openGL.updateGL()

    def timer(self, reset=False):
        if self.labelLastStateVar.text() == "Run" and reset is False:
            self.run_time_sec += 1
            self.remaining_time -= 1
            self.labelRuntimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.run_time_sec)))
            self.labelRemainingTimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.remaining_time)))
        if reset is True:
            self.run_time_sec = 0
            self.labelRuntimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.run_time_sec)))
            self.labelRemainingTimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.run_time_sec)))
        self.remaining_time = self.sender.remaining_time

    def load_file(self):
        self.code_model.clear()

        file_filter = "NC files (*.nc)|*.nc"
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select a data file",
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter="NC files (*.nc)|*.nc"
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
        self.spinBoxDoTo.setMaximum(self.sender.buffer_size)
        self.spinBoxDoTo.setValue(self.sender.buffer_size)
        self.spinBoxDoTo.setMinimum(1)

        self.render_start_point = 0
        self.render_end_point = len(self.sender.points)

        self.is_file_load = True
        self.prepare_to_streaming()

        self.sender.calculate_remaining_time()
        self.labelRemainingTimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.sender.remaining_time)))
        self.labelQueuedCommandsVar.setText(str(self.sender.buffer_size))

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
        self.spinBoxStartFrom.setEnabled(False)
        self.spinBoxDoTo.setEnabled(False)

        self.sender.job_run()
        self.labelLastStateVar.setText("Run")

    def general(self):
        dialog_general = DialogGeneral(self, self.sender, self.is_incremental_streaming, self.save_logs_to_file)
        dialog_general.exec()
        self.is_incremental_streaming = dialog_general.is_incremental_streaming
        self.save_logs_to_file = dialog_general.save_logs_to_file

    def feed_rate(self):
        dialog_feed_rate = DialogFeedRate(self, self.sender, self.is_file_load, self.is_rt_feed_rate_on,
                                          self.is_simple_take_feed_min, self.is_simple_take_feed_max)
        dialog_feed_rate.exec()

        self.is_rt_feed_rate_on = dialog_feed_rate.is_rt_feed_rate_on
        self.is_simple_take_feed_min = dialog_feed_rate.is_simple_take_feed_min
        self.is_simple_take_feed_max = dialog_feed_rate.is_simple_take_feed_max

    def filtering(self):
        dialog_filtering = DialogFiltering(self)
        dialog_filtering.exec()

    def display(self):
        dialog_display = DialogDisplay(self, self.sender, self.is_polling_on)
        dialog_display.exec()
        self.is_polling_on = dialog_display.is_polling_on

    def soft_reset(self):
        self.sender.soft_reset()

    def reset(self):
        self.sender.reset()

    def prepare_to_streaming(self):
        if self.is_file_load is True and self.sender.is_connected() is True:
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

            self.sender.incremental_streaming = self.is_incremental_streaming

            if self.is_polling_on:
                self.sender.poll_start()

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
        self.sender.calculate_buffer_travel_distance()
        self.sender.calculate_remaining_time()
        self.labelRemainingTimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.sender.remaining_time)))
        self.labelQueuedCommandsVar.setText(str(self.sender.ending_line - self.sender.starting_line + 1))
        if self.sender.starting_line == 1 and self.sender.ending_line == self.sender.buffer_size:
            self.render_start_point = 0
            self.render_end_point = self.sender.buffer_size
            self.openGL.initGeometry(self.sender.points, self.sender.colors, self.sender.cube_points,
                                     self.sender.cube_edges, self.sender.cube_colors, self.sender.difX,
                                     self.sender.difY, self.sender.difZ)
        else:
            self.render_start_point = self.spinBoxStartFrom.value() - \
                                      self.sender.is_motion_line[0:self.spinBoxStartFrom.value()].count(False)
            self.openGL.initGeometry(self.sender.points[self.render_start_point:self.render_end_point],
                                     self.sender.colors[self.render_start_point:self.render_end_point],
                                     self.sender.cube_points, self.sender.cube_edges, self.sender.cube_colors,
                                     self.sender.difX, self.sender.difY, self.sender.difZ)

    def set_ending_line(self):
        self.sender.ending_line = self.spinBoxDoTo.value()
        self.spinBoxStartFrom.setMaximum(self.spinBoxDoTo.value())
        self.sender.calculate_buffer_travel_distance()
        self.sender.calculate_remaining_time()
        self.labelRemainingTimeVar.setText(time.strftime('%H:%M:%S', time.gmtime(self.sender.remaining_time)))
        self.labelQueuedCommandsVar.setText(str(self.sender.ending_line - self.sender.starting_line + 1))
        if self.sender.starting_line == 1 and self.sender.ending_line == self.sender.buffer_size:
            self.render_start_point = 0
            self.render_end_point = self.sender.buffer_size
            self.openGL.initGeometry(self.sender.points, self.sender.colors, self.sender.cube_points,
                                     self.sender.cube_edges, self.sender.cube_colors, self.sender.difX,
                                     self.sender.difY, self.sender.difZ)
        else:
            self.render_end_point = self.spinBoxDoTo.value() - \
                                      self.sender.is_motion_line[self.spinBoxStartFrom.value() - 1:
                                                                 self.spinBoxDoTo.value()].count(False)
            self.openGL.initGeometry(self.sender.points[self.render_start_point:self.render_end_point],
                                     self.sender.colors[self.render_start_point:self.render_end_point],
                                     self.sender.cube_points, self.sender.cube_edges, self.sender.cube_colors,
                                     self.sender.difX, self.sender.difY, self.sender.difZ)

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

        if eventstring == "Streaming source ends" or eventstring == "Streaming disabled":
            self.labelLastStateVar.setText("Idle")

        if eventstring == "Q":
            self.labelQueuedCommandsVar.setText(args[0])
            return

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

        if self.save_logs_to_file is True:
            with open(self.logs, 'a') as f:
                f.writelines(log + "\n")

    def closeEvent(self, event):
        config = configparser.ConfigParser()
        config['SENDER'] = {'SaveLogs': str(self.save_logs_to_file),
                             'IncrementalStreaming': str(self.is_incremental_streaming),
                             'Polling': str(self.is_polling_on)}
        with open("config.ini", 'w') as configfile:
            config.write(configfile)


class DialogFeedRate(QDialog, Ui_DialogFeedRate):
    def __init__(self, parent=None, sender=None, is_file_load=None, is_rt_feed_rate_on=False,
                 is_simple_take_feed_min=False, is_simple_take_feed_max=False):
        super().__init__(parent)
        self.setupUi(self)

        self.sender = sender
        self.is_file_load = is_file_load
        self.is_rt_feed_rate_on = is_rt_feed_rate_on
        self.is_simple_take_feed_min = is_simple_take_feed_min
        self.is_simple_take_feed_max = is_simple_take_feed_max

        self.checkBoxEnableFeedRateCalculator.setChecked(self.is_rt_feed_rate_on)
        self.checkBoxTakeMinFeed.setChecked(self.is_simple_take_feed_min)
        self.checkBoxTakeMaxFeed.setChecked(self.is_simple_take_feed_max)

        self.feed_rate_calculator()
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.checkBoxEnableFeedRateCalculator.stateChanged.connect(self.feed_rate_calculator)
        self.checkBoxTakeMinFeed.stateChanged.connect(self.take_min_feed)
        self.checkBoxTakeMaxFeed.stateChanged.connect(self.take_max_feed)
        self.pushButton.clicked.connect(self.closeEvent)
        self.pushButtonSave.clicked.connect(self.save)

    def feed_rate_calculator(self):
        self.simple()
        self.take_min_feed()
        self.take_max_feed()

    def take_min_feed(self):
        if self.is_file_load is False:
            self.checkBoxTakeMinFeed.setChecked(False)

        if self.checkBoxTakeMinFeed.isChecked() is True:
            self.spinBoxMinFeed.setEnabled(False)
            self.spinBoxMinFeed.setValue(self.sender.FMinMax[0])
            self.is_simple_take_feed_min = True
        else:
            self.is_simple_take_feed_min = False
            if self.checkBoxEnableFeedRateCalculator.isChecked() is True:
                self.spinBoxMinFeed.setEnabled(True)

    def take_max_feed(self):
        if self.is_file_load is False:
            self.checkBoxTakeMaxFeed.setChecked(False)

        if self.checkBoxTakeMaxFeed.isChecked() is True:
            self.spinBoxMaxFeed.setEnabled(False)
            self.spinBoxMaxFeed.setValue(self.sender.FMinMax[1])
            self.is_simple_take_feed_max = True
        else:
            self.is_simple_take_feed_max = False
            if self.checkBoxEnableFeedRateCalculator.isChecked() is True:
                self.spinBoxMaxFeed.setEnabled(True)

    def simple(self):
        if self.checkBoxEnableFeedRateCalculator.isChecked() is True:
            self.checkBoxTakeMaxFeed.setEnabled(True)
            self.checkBoxTakeMinFeed.setEnabled(True)
            self.labelMaxFeed.setEnabled(True)
            self.labelMinFeed.setEnabled(True)
            self.spinBoxMaxFeed.setEnabled(True)
            self.spinBoxMinFeed.setEnabled(True)
            self.pushButtonSave.setEnabled(True)
            self.is_rt_feed_rate_on = True
        else:
            self.checkBoxTakeMaxFeed.setEnabled(False)
            self.checkBoxTakeMinFeed.setEnabled(False)
            self.labelMaxFeed.setEnabled(False)
            self.labelMinFeed.setEnabled(False)
            self.spinBoxMaxFeed.setEnabled(False)
            self.spinBoxMinFeed.setEnabled(False)
            self.pushButtonSave.setEnabled(False)
            self.is_rt_feed_rate_on = False

    def save(self):
        if self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value() <= 0:
            self.sender.preprocessor.do_feed_override = False
            if self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value() < 0:
                self.spinBoxMaxFeed.setValue(1)
                self.spinBoxMinFeed.setValue(1)
        else:
            self.sender.difF = self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value()
            self.sender.preprocessor.do_feed_override = self.is_rt_feed_rate_on

        file_filter = "NC files (*.nc)|*.nc"
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption="Select a data file",
            directory='Nowy.nc',
            filter=file_filter,
            initialFilter="NC files (*.nc)|*.nc"
        )
        self.sender.save_buffer_with_new_feed_rate(response)
        self.close()

    def closeEvent(self, event, flag=None):
        if self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value() <= 0:
            self.sender.preprocessor.do_feed_override = False
            if self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value() < 0:
                self.spinBoxMaxFeed.setValue(1)
                self.spinBoxMinFeed.setValue(1)
        else:
            self.sender.difF = self.spinBoxMaxFeed.value() - self.spinBoxMinFeed.value()
            self.sender.preprocessor.do_feed_override = self.is_rt_feed_rate_on

        if flag is not None:
            file_filter = "NC files (*.nc)|*.nc"
            response = QFileDialog.getSaveFileName(
                parent=self,
                caption="Select a data file",
                directory='Nowy.nc',
                filter=file_filter,
                initialFilter="NC files (*.nc)|*.nc"
            )
            self.sender.save_buffer_with_new_feed_rate(response)


class DialogGeneral(QDialog, Ui_DialogGeneral):
    def __init__(self, parent=None, sender=None, is_incremental_streaming=True, save_logs_to_file=False):
        super().__init__(parent)
        self.setupUi(self)
        self.is_incremental_streaming = is_incremental_streaming
        self.save_logs_to_file = save_logs_to_file
        self.sender = sender
        if self.is_incremental_streaming:
            self.checkBoxAgresivePreload.setChecked(False)
        else:
            self.checkBoxAgresivePreload.setChecked(True)

        if self.save_logs_to_file:
            self.checkBoxWriteLogs.setChecked(True)
        else:
            self.checkBoxWriteLogs.setChecked(False)
        self.connect_signals_slots()

    def connect_signals_slots(self):
        self.pushButtonOk.clicked.connect(self.closeEvent)

    def closeEvent(self, event):
        if self.checkBoxAgresivePreload.isChecked():
            self.is_incremental_streaming = False
        else:
            self.is_incremental_streaming = True

        if self.checkBoxWriteLogs.isChecked():
            self.save_logs_to_file = True
        else:
            self.save_logs_to_file = False

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
        self.checkBoxEnablePositionRequest.clicked.connect(self.onof_spin_box)
        self.pushButtonOk.clicked.connect(self.closeEvent)

    def closeEvent(self, event):
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
