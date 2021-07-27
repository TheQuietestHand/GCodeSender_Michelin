# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UIDesign/v0.01_Main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(1767, 970)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        MainWindow.setBaseSize(QtCore.QSize(0, 0))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.groupBoxState = QtWidgets.QGroupBox(self.widget)
        self.groupBoxState.setObjectName("groupBoxState")
        self.gridLayout_14 = QtWidgets.QGridLayout(self.groupBoxState)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.pushButtonPause = QtWidgets.QPushButton(self.groupBoxState)
        self.pushButtonPause.setEnabled(False)
        self.pushButtonPause.setObjectName("pushButtonPause")
        self.gridLayout_14.addWidget(self.pushButtonPause, 0, 0, 1, 1)
        self.pushButtonResume = QtWidgets.QPushButton(self.groupBoxState)
        self.pushButtonResume.setEnabled(False)
        self.pushButtonResume.setObjectName("pushButtonResume")
        self.gridLayout_14.addWidget(self.pushButtonResume, 0, 1, 1, 3)
        self.pushButtonStop = QtWidgets.QPushButton(self.groupBoxState)
        self.pushButtonStop.setEnabled(False)
        self.pushButtonStop.setFlat(False)
        self.pushButtonStop.setObjectName("pushButtonStop")
        self.gridLayout_14.addWidget(self.pushButtonStop, 0, 4, 1, 1)
        self.labelRuntime = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelRuntime.setFont(font)
        self.labelRuntime.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelRuntime.setObjectName("labelRuntime")
        self.gridLayout_14.addWidget(self.labelRuntime, 1, 0, 1, 2)
        self.labelRemainingTime = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelRemainingTime.setFont(font)
        self.labelRemainingTime.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelRemainingTime.setObjectName("labelRemainingTime")
        self.gridLayout_14.addWidget(self.labelRemainingTime, 2, 0, 1, 2)
        self.labelQueuedCommands = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelQueuedCommands.setFont(font)
        self.labelQueuedCommands.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelQueuedCommands.setObjectName("labelQueuedCommands")
        self.gridLayout_14.addWidget(self.labelQueuedCommands, 3, 0, 1, 2)
        self.labelLastState = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelLastState.setFont(font)
        self.labelLastState.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelLastState.setObjectName("labelLastState")
        self.gridLayout_14.addWidget(self.labelLastState, 4, 0, 1, 2)
        self.labelRuntimeVar = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelRuntimeVar.setFont(font)
        self.labelRuntimeVar.setAlignment(QtCore.Qt.AlignCenter)
        self.labelRuntimeVar.setObjectName("labelRuntimeVar")
        self.gridLayout_14.addWidget(self.labelRuntimeVar, 1, 4, 1, 1)
        self.labelRemainingTimeVar = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelRemainingTimeVar.setFont(font)
        self.labelRemainingTimeVar.setAlignment(QtCore.Qt.AlignCenter)
        self.labelRemainingTimeVar.setObjectName("labelRemainingTimeVar")
        self.gridLayout_14.addWidget(self.labelRemainingTimeVar, 2, 4, 1, 1)
        self.labelQueuedCommandsVar = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.labelQueuedCommandsVar.setFont(font)
        self.labelQueuedCommandsVar.setAlignment(QtCore.Qt.AlignCenter)
        self.labelQueuedCommandsVar.setObjectName("labelQueuedCommandsVar")
        self.gridLayout_14.addWidget(self.labelQueuedCommandsVar, 3, 4, 1, 1)
        self.labelLastStateVar = QtWidgets.QLabel(self.groupBoxState)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.labelLastStateVar.setFont(font)
        self.labelLastStateVar.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLastStateVar.setObjectName("labelLastStateVar")
        self.gridLayout_14.addWidget(self.labelLastStateVar, 4, 4, 1, 1)
        self.gridLayout.addWidget(self.groupBoxState, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBoxXYZ = QtWidgets.QGroupBox(self.widget)
        self.groupBoxXYZ.setObjectName("groupBoxXYZ")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBoxXYZ)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.labelMachineXYZ = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(False)
        self.labelMachineXYZ.setFont(font)
        self.labelMachineXYZ.setFocusPolicy(QtCore.Qt.NoFocus)
        self.labelMachineXYZ.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelMachineXYZ.setAlignment(QtCore.Qt.AlignCenter)
        self.labelMachineXYZ.setObjectName("labelMachineXYZ")
        self.gridLayout_8.addWidget(self.labelMachineXYZ, 0, 1, 1, 1)
        self.labelWorkXYZ = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(False)
        self.labelWorkXYZ.setFont(font)
        self.labelWorkXYZ.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelWorkXYZ.setAlignment(QtCore.Qt.AlignCenter)
        self.labelWorkXYZ.setObjectName("labelWorkXYZ")
        self.gridLayout_8.addWidget(self.labelWorkXYZ, 0, 3, 1, 2)
        self.labelFeedRate = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(False)
        self.labelFeedRate.setFont(font)
        self.labelFeedRate.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelFeedRate.setAlignment(QtCore.Qt.AlignCenter)
        self.labelFeedRate.setObjectName("labelFeedRate")
        self.gridLayout_8.addWidget(self.labelFeedRate, 0, 5, 1, 2)
        self.labelSpindleSpeed = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(False)
        self.labelSpindleSpeed.setFont(font)
        self.labelSpindleSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelSpindleSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSpindleSpeed.setObjectName("labelSpindleSpeed")
        self.gridLayout_8.addWidget(self.labelSpindleSpeed, 0, 7, 1, 2)
        self.labelXMachine = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.labelXMachine.setFont(font)
        self.labelXMachine.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelXMachine.setAutoFillBackground(False)
        self.labelXMachine.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelXMachine.setAlignment(QtCore.Qt.AlignCenter)
        self.labelXMachine.setObjectName("labelXMachine")
        self.gridLayout_8.addWidget(self.labelXMachine, 1, 0, 1, 1)
        self.lineEditXMachine = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditXMachine.setReadOnly(True)
        self.lineEditXMachine.setObjectName("lineEditXMachine")
        self.gridLayout_8.addWidget(self.lineEditXMachine, 1, 1, 1, 1)
        self.labelXWork = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.labelXWork.setFont(font)
        self.labelXWork.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelXWork.setAutoFillBackground(False)
        self.labelXWork.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelXWork.setAlignment(QtCore.Qt.AlignCenter)
        self.labelXWork.setObjectName("labelXWork")
        self.gridLayout_8.addWidget(self.labelXWork, 1, 2, 1, 1)
        self.lineEditXWork = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditXWork.setFrame(True)
        self.lineEditXWork.setReadOnly(True)
        self.lineEditXWork.setObjectName("lineEditXWork")
        self.gridLayout_8.addWidget(self.lineEditXWork, 1, 3, 1, 1)
        self.labelXUnits = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.labelXUnits.setFont(font)
        self.labelXUnits.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelXUnits.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelXUnits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelXUnits.setObjectName("labelXUnits")
        self.gridLayout_8.addWidget(self.labelXUnits, 1, 4, 1, 1)
        self.lineEditFeedRate = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditFeedRate.setReadOnly(True)
        self.lineEditFeedRate.setObjectName("lineEditFeedRate")
        self.gridLayout_8.addWidget(self.lineEditFeedRate, 1, 5, 1, 1)
        self.labelFeedRateUnits = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.labelFeedRateUnits.setFont(font)
        self.labelFeedRateUnits.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelFeedRateUnits.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelFeedRateUnits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelFeedRateUnits.setObjectName("labelFeedRateUnits")
        self.gridLayout_8.addWidget(self.labelFeedRateUnits, 1, 6, 1, 1)
        self.lineEditSpeedSpindle = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditSpeedSpindle.setReadOnly(True)
        self.lineEditSpeedSpindle.setObjectName("lineEditSpeedSpindle")
        self.gridLayout_8.addWidget(self.lineEditSpeedSpindle, 1, 7, 1, 1)
        self.labelSpeedSpindleUnits = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.labelSpeedSpindleUnits.setFont(font)
        self.labelSpeedSpindleUnits.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelSpeedSpindleUnits.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelSpeedSpindleUnits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSpeedSpindleUnits.setObjectName("labelSpeedSpindleUnits")
        self.gridLayout_8.addWidget(self.labelSpeedSpindleUnits, 1, 8, 1, 1)
        self.labelYMachine = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelYMachine.setFont(font)
        self.labelYMachine.setAlignment(QtCore.Qt.AlignCenter)
        self.labelYMachine.setObjectName("labelYMachine")
        self.gridLayout_8.addWidget(self.labelYMachine, 2, 0, 1, 1)
        self.lineEditYMachine = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditYMachine.setReadOnly(True)
        self.lineEditYMachine.setObjectName("lineEditYMachine")
        self.gridLayout_8.addWidget(self.lineEditYMachine, 2, 1, 1, 1)
        self.labelYWork = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelYWork.setFont(font)
        self.labelYWork.setAlignment(QtCore.Qt.AlignCenter)
        self.labelYWork.setObjectName("labelYWork")
        self.gridLayout_8.addWidget(self.labelYWork, 2, 2, 1, 1)
        self.lineEditYWork = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditYWork.setReadOnly(True)
        self.lineEditYWork.setObjectName("lineEditYWork")
        self.gridLayout_8.addWidget(self.lineEditYWork, 2, 3, 1, 1)
        self.labelYUnits = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.labelYUnits.setFont(font)
        self.labelYUnits.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelYUnits.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelYUnits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelYUnits.setObjectName("labelYUnits")
        self.gridLayout_8.addWidget(self.labelYUnits, 2, 4, 1, 1)
        self.pushButtonHome = QtWidgets.QPushButton(self.groupBoxXYZ)
        self.pushButtonHome.setEnabled(False)
        self.pushButtonHome.setObjectName("pushButtonHome")
        self.gridLayout_8.addWidget(self.pushButtonHome, 2, 5, 1, 2)
        self.pushButtonZero = QtWidgets.QPushButton(self.groupBoxXYZ)
        self.pushButtonZero.setEnabled(False)
        self.pushButtonZero.setObjectName("pushButtonZero")
        self.gridLayout_8.addWidget(self.pushButtonZero, 2, 7, 1, 2)
        self.labelZMachine = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelZMachine.setFont(font)
        self.labelZMachine.setAlignment(QtCore.Qt.AlignCenter)
        self.labelZMachine.setObjectName("labelZMachine")
        self.gridLayout_8.addWidget(self.labelZMachine, 3, 0, 1, 1)
        self.lineEditZMachine = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditZMachine.setReadOnly(True)
        self.lineEditZMachine.setObjectName("lineEditZMachine")
        self.gridLayout_8.addWidget(self.lineEditZMachine, 3, 1, 1, 1)
        self.labelZWork = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelZWork.setFont(font)
        self.labelZWork.setAlignment(QtCore.Qt.AlignCenter)
        self.labelZWork.setObjectName("labelZWork")
        self.gridLayout_8.addWidget(self.labelZWork, 3, 2, 1, 1)
        self.lineEditZWork = QtWidgets.QLineEdit(self.groupBoxXYZ)
        self.lineEditZWork.setReadOnly(True)
        self.lineEditZWork.setObjectName("lineEditZWork")
        self.gridLayout_8.addWidget(self.lineEditZWork, 3, 3, 1, 1)
        self.labelZUnits = QtWidgets.QLabel(self.groupBoxXYZ)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.labelZUnits.setFont(font)
        self.labelZUnits.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelZUnits.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.labelZUnits.setAlignment(QtCore.Qt.AlignCenter)
        self.labelZUnits.setObjectName("labelZUnits")
        self.gridLayout_8.addWidget(self.labelZUnits, 3, 4, 1, 1)
        self.pushButtonSetZero = QtWidgets.QPushButton(self.groupBoxXYZ)
        self.pushButtonSetZero.setEnabled(False)
        self.pushButtonSetZero.setObjectName("pushButtonSetZero")
        self.gridLayout_8.addWidget(self.pushButtonSetZero, 3, 5, 1, 4)
        self.gridLayout_4.addWidget(self.groupBoxXYZ, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout_4, 0, 1, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBoxManualControl = QtWidgets.QGroupBox(self.widget)
        self.groupBoxManualControl.setObjectName("groupBoxManualControl")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBoxManualControl)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.labelStep = QtWidgets.QLabel(self.groupBoxManualControl)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(False)
        self.labelStep.setFont(font)
        self.labelStep.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelStep.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStep.setObjectName("labelStep")
        self.gridLayout_9.addWidget(self.labelStep, 0, 3, 1, 1)
        self.labelXManualControl = QtWidgets.QLabel(self.groupBoxManualControl)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.labelXManualControl.setFont(font)
        self.labelXManualControl.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelXManualControl.setAutoFillBackground(False)
        self.labelXManualControl.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelXManualControl.setAlignment(QtCore.Qt.AlignCenter)
        self.labelXManualControl.setObjectName("labelXManualControl")
        self.gridLayout_9.addWidget(self.labelXManualControl, 1, 0, 1, 1)
        self.pushButtonXManualControlPlus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonXManualControlPlus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButtonXManualControlPlus.setFont(font)
        self.pushButtonXManualControlPlus.setObjectName("pushButtonXManualControlPlus")
        self.gridLayout_9.addWidget(self.pushButtonXManualControlPlus, 1, 1, 1, 1)
        self.pushButtonXManualControlMinus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonXManualControlMinus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonXManualControlMinus.setFont(font)
        self.pushButtonXManualControlMinus.setObjectName("pushButtonXManualControlMinus")
        self.gridLayout_9.addWidget(self.pushButtonXManualControlMinus, 1, 2, 1, 1)
        self.doubleSpinBoxStep = QtWidgets.QDoubleSpinBox(self.groupBoxManualControl)
        self.doubleSpinBoxStep.setEnabled(False)
        self.doubleSpinBoxStep.setAccelerated(True)
        self.doubleSpinBoxStep.setSingleStep(0.1)
        self.doubleSpinBoxStep.setProperty("value", 1.0)
        self.doubleSpinBoxStep.setObjectName("doubleSpinBoxStep")
        self.gridLayout_9.addWidget(self.doubleSpinBoxStep, 1, 3, 1, 1)
        self.labelYManualControl = QtWidgets.QLabel(self.groupBoxManualControl)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelYManualControl.setFont(font)
        self.labelYManualControl.setAlignment(QtCore.Qt.AlignCenter)
        self.labelYManualControl.setObjectName("labelYManualControl")
        self.gridLayout_9.addWidget(self.labelYManualControl, 2, 0, 1, 1)
        self.pushButtonYManualControlPlus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonYManualControlPlus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonYManualControlPlus.setFont(font)
        self.pushButtonYManualControlPlus.setObjectName("pushButtonYManualControlPlus")
        self.gridLayout_9.addWidget(self.pushButtonYManualControlPlus, 2, 1, 1, 1)
        self.pushButtonYManualControlMinus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonYManualControlMinus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonYManualControlMinus.setFont(font)
        self.pushButtonYManualControlMinus.setObjectName("pushButtonYManualControlMinus")
        self.gridLayout_9.addWidget(self.pushButtonYManualControlMinus, 2, 2, 1, 1)
        self.checkBoxG90Step = QtWidgets.QCheckBox(self.groupBoxManualControl)
        self.checkBoxG90Step.setEnabled(False)
        self.checkBoxG90Step.setObjectName("checkBoxG90Step")
        self.gridLayout_9.addWidget(self.checkBoxG90Step, 2, 3, 1, 1)
        self.labelZManualControl = QtWidgets.QLabel(self.groupBoxManualControl)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.labelZManualControl.setFont(font)
        self.labelZManualControl.setAlignment(QtCore.Qt.AlignCenter)
        self.labelZManualControl.setObjectName("labelZManualControl")
        self.gridLayout_9.addWidget(self.labelZManualControl, 3, 0, 1, 1)
        self.pushButtonZManualControlPlus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonZManualControlPlus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonZManualControlPlus.setFont(font)
        self.pushButtonZManualControlPlus.setObjectName("pushButtonZManualControlPlus")
        self.gridLayout_9.addWidget(self.pushButtonZManualControlPlus, 3, 1, 1, 1)
        self.pushButtonZManualControlMinus = QtWidgets.QPushButton(self.groupBoxManualControl)
        self.pushButtonZManualControlMinus.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButtonZManualControlMinus.setFont(font)
        self.pushButtonZManualControlMinus.setObjectName("pushButtonZManualControlMinus")
        self.gridLayout_9.addWidget(self.pushButtonZManualControlMinus, 3, 2, 1, 1)
        self.gridLayout_5.addWidget(self.groupBoxManualControl, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout_5, 0, 2, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.widget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.tabCode = QtWidgets.QWidget()
        self.tabCode.setObjectName("tabCode")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.tabCode)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.labelCodeLines = QtWidgets.QLabel(self.tabCode)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelCodeLines.setFont(font)
        self.labelCodeLines.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCodeLines.setObjectName("labelCodeLines")
        self.gridLayout_12.addWidget(self.labelCodeLines, 0, 1, 2, 1)
        self.labelCodeLineQty = QtWidgets.QLabel(self.tabCode)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelCodeLineQty.setFont(font)
        self.labelCodeLineQty.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCodeLineQty.setObjectName("labelCodeLineQty")
        self.gridLayout_12.addWidget(self.labelCodeLineQty, 2, 1, 1, 1)
        self.spinBoxStartFrom = QtWidgets.QSpinBox(self.tabCode)
        self.spinBoxStartFrom.setEnabled(False)
        self.spinBoxStartFrom.setMinimum(1)
        self.spinBoxStartFrom.setObjectName("spinBoxStartFrom")
        self.gridLayout_12.addWidget(self.spinBoxStartFrom, 6, 1, 1, 1)
        self.labelPeriod = QtWidgets.QLabel(self.tabCode)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setItalic(False)
        self.labelPeriod.setFont(font)
        self.labelPeriod.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.labelPeriod.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPeriod.setObjectName("labelPeriod")
        self.gridLayout_12.addWidget(self.labelPeriod, 9, 1, 1, 1)
        self.labelStartFrom_2 = QtWidgets.QLabel(self.tabCode)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelStartFrom_2.setFont(font)
        self.labelStartFrom_2.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStartFrom_2.setObjectName("labelStartFrom_2")
        self.gridLayout_12.addWidget(self.labelStartFrom_2, 7, 1, 1, 1)
        self.spinBoxDoTo = QtWidgets.QSpinBox(self.tabCode)
        self.spinBoxDoTo.setEnabled(False)
        self.spinBoxDoTo.setMinimum(1)
        self.spinBoxDoTo.setObjectName("spinBoxDoTo")
        self.gridLayout_12.addWidget(self.spinBoxDoTo, 8, 1, 1, 1)
        self.spinBoxPeriod = QtWidgets.QSpinBox(self.tabCode)
        self.spinBoxPeriod.setEnabled(False)
        self.spinBoxPeriod.setMinimum(60)
        self.spinBoxPeriod.setMaximum(500)
        self.spinBoxPeriod.setProperty("value", 100)
        self.spinBoxPeriod.setObjectName("spinBoxPeriod")
        self.gridLayout_12.addWidget(self.spinBoxPeriod, 10, 1, 1, 1)
        self.pushButtonRunCode = QtWidgets.QPushButton(self.tabCode)
        self.pushButtonRunCode.setEnabled(False)
        self.pushButtonRunCode.setObjectName("pushButtonRunCode")
        self.gridLayout_12.addWidget(self.pushButtonRunCode, 11, 1, 1, 1)
        self.labelStartFrom = QtWidgets.QLabel(self.tabCode)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.labelStartFrom.setFont(font)
        self.labelStartFrom.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStartFrom.setObjectName("labelStartFrom")
        self.gridLayout_12.addWidget(self.labelStartFrom, 5, 1, 1, 1)
        self.listViewCode = QtWidgets.QListView(self.tabCode)
        self.listViewCode.setObjectName("listViewCode")
        self.gridLayout_12.addWidget(self.listViewCode, 0, 0, 12, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_12.addItem(spacerItem, 4, 1, 1, 1)
        self.labelCodeLines.raise_()
        self.labelStartFrom.raise_()
        self.spinBoxStartFrom.raise_()
        self.labelStartFrom_2.raise_()
        self.spinBoxDoTo.raise_()
        self.labelPeriod.raise_()
        self.spinBoxPeriod.raise_()
        self.pushButtonRunCode.raise_()
        self.listViewCode.raise_()
        self.labelCodeLineQty.raise_()
        self.tabWidget.addTab(self.tabCode, "")
        self.tabConsole = QtWidgets.QWidget()
        self.tabConsole.setObjectName("tabConsole")
        self.gridLayout_13 = QtWidgets.QGridLayout(self.tabConsole)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.listViewConsole = QtWidgets.QListView(self.tabConsole)
        self.listViewConsole.setObjectName("listViewConsole")
        self.gridLayout_13.addWidget(self.listViewConsole, 0, 0, 1, 2)
        self.lineEditCodeToSend = QtWidgets.QLineEdit(self.tabConsole)
        self.lineEditCodeToSend.setEnabled(False)
        self.lineEditCodeToSend.setObjectName("lineEditCodeToSend")
        self.gridLayout_13.addWidget(self.lineEditCodeToSend, 1, 0, 1, 1)
        self.pushButtonSendCode = QtWidgets.QPushButton(self.tabConsole)
        self.pushButtonSendCode.setEnabled(False)
        self.pushButtonSendCode.setObjectName("pushButtonSendCode")
        self.gridLayout_13.addWidget(self.pushButtonSendCode, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tabConsole, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.groupBoxVisualisation = QtWidgets.QGroupBox(self.widget)
        self.groupBoxVisualisation.setAutoFillBackground(False)
        self.groupBoxVisualisation.setObjectName("groupBoxVisualisation")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.groupBoxVisualisation)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.frameGL = QtWidgets.QFrame(self.groupBoxVisualisation)
        self.frameGL.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameGL.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameGL.setObjectName("frameGL")
        self.gridLayout_10.addWidget(self.frameGL, 0, 0, 1, 1)
        self.gridLayout_6.addWidget(self.groupBoxVisualisation, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout_6, 1, 1, 2, 2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBoxLogs = QtWidgets.QGroupBox(self.widget)
        self.groupBoxLogs.setObjectName("groupBoxLogs")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.groupBoxLogs)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.listViewLogs = QtWidgets.QListView(self.groupBoxLogs)
        self.listViewLogs.setAutoScroll(False)
        self.listViewLogs.setProperty("isWrapping", False)
        self.listViewLogs.setObjectName("listViewLogs")
        self.gridLayout_11.addWidget(self.listViewLogs, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBoxLogs, 0, 0, 1, 1)
        self.gridLayout_15.addLayout(self.gridLayout_3, 2, 0, 1, 1)
        self.gridLayout_7.addWidget(self.widget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1767, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuConnection = QtWidgets.QMenu(self.menubar)
        self.menuConnection.setObjectName("menuConnection")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionSoft_reset = QtWidgets.QAction(MainWindow)
        self.actionSoft_reset.setEnabled(False)
        self.actionSoft_reset.setObjectName("actionSoft_reset")
        self.actionReset = QtWidgets.QAction(MainWindow)
        self.actionReset.setEnabled(False)
        self.actionReset.setObjectName("actionReset")
        self.actionConnect = QtWidgets.QAction(MainWindow)
        self.actionConnect.setObjectName("actionConnect")
        self.actionGeneral = QtWidgets.QAction(MainWindow)
        self.actionGeneral.setObjectName("actionGeneral")
        self.actionFiltering = QtWidgets.QAction(MainWindow)
        self.actionFiltering.setObjectName("actionFiltering")
        self.actionDisplay = QtWidgets.QAction(MainWindow)
        self.actionDisplay.setObjectName("actionDisplay")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionManual = QtWidgets.QAction(MainWindow)
        self.actionManual.setObjectName("actionManual")
        self.actionDisconnect = QtWidgets.QAction(MainWindow)
        self.actionDisconnect.setEnabled(False)
        self.actionDisconnect.setObjectName("actionDisconnect")
        self.actionFeed_rate = QtWidgets.QAction(MainWindow)
        self.actionFeed_rate.setObjectName("actionFeed_rate")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuConnection.addAction(self.actionSoft_reset)
        self.menuConnection.addAction(self.actionReset)
        self.menuConnection.addSeparator()
        self.menuConnection.addAction(self.actionConnect)
        self.menuConnection.addSeparator()
        self.menuConnection.addAction(self.actionDisconnect)
        self.menuSettings.addAction(self.actionGeneral)
        self.menuSettings.addAction(self.actionFiltering)
        self.menuSettings.addAction(self.actionDisplay)
        self.menuSettings.addAction(self.actionFeed_rate)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionManual)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuConnection.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBoxState.setTitle(_translate("MainWindow", "State"))
        self.pushButtonPause.setText(_translate("MainWindow", "Pause"))
        self.pushButtonResume.setText(_translate("MainWindow", "Resume"))
        self.pushButtonStop.setText(_translate("MainWindow", "STOP"))
        self.labelRuntime.setText(_translate("MainWindow", "Runtime:"))
        self.labelRemainingTime.setText(_translate("MainWindow", "Remaining Time:"))
        self.labelQueuedCommands.setText(_translate("MainWindow", "Queued commands:"))
        self.labelLastState.setText(_translate("MainWindow", "Last state:"))
        self.labelRuntimeVar.setText(_translate("MainWindow", "00:00:00"))
        self.labelRemainingTimeVar.setText(_translate("MainWindow", "00:00:00"))
        self.labelQueuedCommandsVar.setText(_translate("MainWindow", "0"))
        self.labelLastStateVar.setText(_translate("MainWindow", "NaN"))
        self.groupBoxXYZ.setTitle(_translate("MainWindow", "XYZ Motion"))
        self.labelMachineXYZ.setText(_translate("MainWindow", "Machine"))
        self.labelWorkXYZ.setText(_translate("MainWindow", "Work"))
        self.labelFeedRate.setText(_translate("MainWindow", "Feed rate"))
        self.labelSpindleSpeed.setText(_translate("MainWindow", "Spindle speed"))
        self.labelXMachine.setText(_translate("MainWindow", "X:"))
        self.lineEditXMachine.setText(_translate("MainWindow", "0"))
        self.labelXWork.setText(_translate("MainWindow", "X:"))
        self.lineEditXWork.setText(_translate("MainWindow", "0"))
        self.labelXUnits.setText(_translate("MainWindow", "mm"))
        self.lineEditFeedRate.setText(_translate("MainWindow", "0"))
        self.labelFeedRateUnits.setText(_translate("MainWindow", "mm/min"))
        self.lineEditSpeedSpindle.setText(_translate("MainWindow", "0"))
        self.labelSpeedSpindleUnits.setText(_translate("MainWindow", "rpm"))
        self.labelYMachine.setText(_translate("MainWindow", "Y:"))
        self.lineEditYMachine.setText(_translate("MainWindow", "0"))
        self.labelYWork.setText(_translate("MainWindow", "Y:"))
        self.lineEditYWork.setText(_translate("MainWindow", "0"))
        self.labelYUnits.setText(_translate("MainWindow", "mm"))
        self.pushButtonHome.setText(_translate("MainWindow", "Home"))
        self.pushButtonZero.setText(_translate("MainWindow", "Zero"))
        self.labelZMachine.setText(_translate("MainWindow", "Z:"))
        self.lineEditZMachine.setText(_translate("MainWindow", "0"))
        self.labelZWork.setText(_translate("MainWindow", "Z:"))
        self.lineEditZWork.setText(_translate("MainWindow", "0"))
        self.labelZUnits.setText(_translate("MainWindow", "mm"))
        self.pushButtonSetZero.setText(_translate("MainWindow", "Set zero"))
        self.groupBoxManualControl.setTitle(_translate("MainWindow", "Manual control"))
        self.labelStep.setText(_translate("MainWindow", "Step"))
        self.labelXManualControl.setText(_translate("MainWindow", "X:"))
        self.pushButtonXManualControlPlus.setText(_translate("MainWindow", "+"))
        self.pushButtonXManualControlMinus.setText(_translate("MainWindow", "-"))
        self.labelYManualControl.setText(_translate("MainWindow", "Y:"))
        self.pushButtonYManualControlPlus.setText(_translate("MainWindow", "+"))
        self.pushButtonYManualControlMinus.setText(_translate("MainWindow", "-"))
        self.checkBoxG90Step.setText(_translate("MainWindow", "G90"))
        self.labelZManualControl.setText(_translate("MainWindow", "Z:"))
        self.pushButtonZManualControlPlus.setText(_translate("MainWindow", "+"))
        self.pushButtonZManualControlMinus.setText(_translate("MainWindow", "-"))
        self.labelCodeLines.setText(_translate("MainWindow", "Lines:"))
        self.labelCodeLineQty.setText(_translate("MainWindow", "0"))
        self.labelPeriod.setText(_translate("MainWindow", "Period"))
        self.labelStartFrom_2.setText(_translate("MainWindow", "Do to:"))
        self.pushButtonRunCode.setText(_translate("MainWindow", "Run"))
        self.labelStartFrom.setText(_translate("MainWindow", "Start from:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCode), _translate("MainWindow", "Code"))
        self.pushButtonSendCode.setText(_translate("MainWindow", "Send"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabConsole), _translate("MainWindow", "Console"))
        self.groupBoxVisualisation.setTitle(_translate("MainWindow", "Visualisation"))
        self.groupBoxLogs.setTitle(_translate("MainWindow", "Logs"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuConnection.setTitle(_translate("MainWindow", "Connection"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionSoft_reset.setText(_translate("MainWindow", "Soft reset"))
        self.actionReset.setText(_translate("MainWindow", "Reset"))
        self.actionConnect.setText(_translate("MainWindow", "Connect"))
        self.actionGeneral.setText(_translate("MainWindow", "General"))
        self.actionFiltering.setText(_translate("MainWindow", "Filtering"))
        self.actionDisplay.setText(_translate("MainWindow", "Display"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionManual.setText(_translate("MainWindow", "Manual"))
        self.actionDisconnect.setText(_translate("MainWindow", "Disconnect"))
        self.actionFeed_rate.setText(_translate("MainWindow", "Feed rate"))
