# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:08:25 2022

@author: Badari


from pyqtgraph import PlotWidget, ViewBox, mkPen
self.ImpdPlot = PlotWidget(self.centralwidget,viewBox=ViewBox(border = mkPen(color='k',width = 2)))
self.ImpdPlot.setBackground((255,182,193,25))
"""
# Long term goals
# TODO: Option to just continuously do freqsweep and monitor the temperature (no temperature control)
# TODO: Option to monitor temperature from other sensors
# TODO: If MUX is connected, option to switch sample and do parallel measurements
    # If in cryochamber, switch between sample cr1 and cr2
    # If using probe and linkam heater, switch between sample1, 2 and 3
    # In advanced settings, set an option for sample sweep
# TODO: If sample is in cryochamber, temperature sensor can be Chino, K195 or advantest
# TODO: If sample is in cryochamber, save temperature data of all sensors that are available (maybe in a separate file?)
# TODO: if sample is on linkam, temperature sensor can only be linkam
# TODO: If sample is in cryochamber, and Chino is not connected, then temperature sensor can still sense from K195 or advntest, and just do a simple monitoring temperature sweep
# TODO: If no temperature controller or sensor is detected, disable temperature controller and sensor menu. (only continuous or interval measurement can be made)
# TODO: Option to do temperature scan using custom list of temperatures (enable only if controller is present)    
# TODO: Other sweep functions?

# Short Term goals
# TODO: functionalize option for DC bias sweep.
# TODO: In advanced settings: measurement: option to set measurement time per point, multiple counts, etc. for idleWorder, and f&t sweep
# TODO: Facility to alert by email if any alarm is triggered.
# Parameters to be modified in advanced section:
# TODO: Monitor actual AC and DC volts applied, and display it

import sys, os
from PyQt5 import QtWidgets, QtGui
from dielectric import Ui_ImpedanceApp
from pyqtgraph import mkPen, intColor, ViewBox, PlotDataItem
from numpy import loadtxt, array, vstack, hstack, linspace, savetxt, concatenate
from templist import Ui_Form
from pandas import DataFrame, Series, concat
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from utilities import IdleWorker, FrequencySweepWorker, get_valid_filename,\
                    unique_filename, TemperatureSweepWorkerF, checkInstrument, initializeEmail,\
                    DCSweepWorker
from math import log10
from time import sleep
from functools import partial
import warnings
warnings.filterwarnings("ignore")
from setAlert import AlertSetting

# creating VLine class
class VLine(QtWidgets.QFrame):
  
    # a simple Vertical line
    def __init__(self):
  
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

# worker class to connect instrument
class Worker(QObject):
    finished = pyqtSignal()
    adapters = pyqtSignal(list)
    
    def __init__(self):
        super(Worker,self).__init__()
        
    def connect_instrument(self,a1=None,a2=None,a3=None,a4=None,a5=None,test=True):
        instruments = list(checkInstrument(a1,a2,a3,a4,a5,test))
        self.adapters.emit(instruments)
        self.finished.emit()

class mainControl(QtWidgets.QMainWindow,Ui_ImpedanceApp):
    """The Impedance program module."""

    def __init__(self, *args, obj=None, **kwargs):
        super(mainControl, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.leftPlot = self.ImpdPlot.plotItem
        self.rightPlot = ViewBox()
        self.leftPlot.scene().addItem(self.rightPlot)
        self.leftPlot.getAxis('right').linkToView(self.rightPlot)
        self.rightPlot.setXLink(self.leftPlot)
        self.updateViews()
        self.leftPlot.vb.sigResized.connect(self.updateViews)
        #self.rightPlot.hide()
        self.checkPaths()
        self.alert = AlertSetting(self.settingPath,self.currPath)
        self.fixFreq.clicked.connect(self.freqOption)
        self.fixTemp.clicked.connect(self.tempOption)
        self.fixDCvolts.clicked.connect(self.DCvoltOption)
        self.traceback.clicked.connect(self.setVoltageCycles)
        self.startButton.clicked.connect(self.startProgram)
        self.stopButton.clicked.connect(self.stopProgram)
        self.loadTempButton.clicked.connect(self.loadTemperatures)
        self.fixedFreq.editingFinished.connect(self.updateFixedFrequency)
        self.fixedFreqUnit.currentIndexChanged.connect(self.updateFixedFrequency)
        self.startFreq.valueChanged.connect(self.updateStartFrequency)
        self.startFreqUnit.currentIndexChanged.connect(self.updateStartFrequency)
        self.stopFreq.valueChanged.connect(self.updateStopFrequency)
        self.stopFreqUnit.currentIndexChanged.connect(self.updateStopFrequency)
        self.fixedTemp.valueChanged.connect(self.updateFixedTemperature)
        self.inst.currentIndexChanged.connect(self.updateTemperatureController)
        self.fixedACvolt.valueChanged.connect(self.updateACVoltage)
        self.fixedDCvolt.valueChanged.connect(self.updateFixedDCVoltage)
        self.tempTraceback.stateChanged.connect(self.updateTempTraceback)
        self.tempInterval.valueChanged.connect(self.updateTempInterval)
        self.stopHeater.clicked.connect(self.stop_Temperature_Controller)
        self.measureMode.currentIndexChanged.connect(self.updateMeasureMode)
        self.startTemp.valueChanged.connect(self.updateStartTemp)
        self.stopTemp.valueChanged.connect(self.updateStopTemp)
        self.heatRate.valueChanged.connect(self.updateRateTemp)
        self.stabilizationTime.valueChanged.connect(self.updateStabilizationTime)
        self.actionExit.triggered.connect(self.close)
        self.measureMode.currentIndexChanged.connect(self.measureModeSet)
        self.setFixedTemperature.clicked.connect(self.setTemperature)
        self.setFixedACV.clicked.connect(self.setACVolts)
        self.setFixedDCV.clicked.connect(self.setDCVolts)
        self.saveDir.clicked.connect(self.chooseSaveDir)
        self.choosePlot.currentIndexChanged.connect(self.updatePlotOption)
        self.phaseButton.clicked.connect(self.phasePlot)
        self.lossButton.clicked.connect(self.lossPlot)
        self.filenameText.editingFinished.connect(self.setFileName)
        self.actionSend_Alert.triggered.connect(self.AlertSettings)
        self.setFileName(1)
        self.measureModeSet()
        self.tempOption()
        self.show()
        freqAxis = self.ImpdPlot.plotItem.getAxis('bottom')
        freqAxis.autoSIPrefix = False
        self.temperatures = []
        self.plotIndex = 2 # 0 - z, 1 - z+phase, 2- C, 3-C+loss
        self.freqsweep = True
        self.idleRun = False
        self.TFsweepRun = False
        self.FsweepRun = False
        self.finished = False
        self.currentView = 0 # 0: Frequency Sweep, 1: Temperature Sweep, 2: DC Bias sweep, 3: AC amplitude sweep...
        self.updatePlotOption()
        self.lastfreqstate = 'sweep'
        self.yaxis = 'z'
        """ Display list of custom temperatures, which can be edited
        self.Form = QtWidgets.QWidget()
        self.temptable = Ui_Form()
        self.temptable.setupUi(self.Form)
        self.loadTempButton.clicked.connect(self.showTempTable)
        # TODO: Make a default temperature table, and load it in the beginning.
        """
        self.connectInstrumentThread()
        
    
    def updateNames(self):
        for user in self.alert.userList:
            self.alertNames.addAction(user[0])
    
    def connectInstrumentThread(self):
        self.statusBar().showMessage("Connecting instruments, please wait...")
        self.parameterBox.setEnabled(False)
        self.fileBox.setEnabled(False)
        self.measureControlBox.setEnabled(False)
        self.plotBox.setEnabled(False)
        self.statusBox.setEnabled(False)
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(partial(self.worker.connect_instrument,
                                            a1="GPIB0::17::INSTR",
                                            a5='com3'))
        #self.thread.started.connect(partial(self.worker.connect_instrument,
        #                                    E4990Addr="GPIB0::17::INSTR")
        #self.thread.started.connect(partial(self.worker.connect_instrument,
        #                                    TControlAddr='com3'))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.adapters.connect(self.getInstruments)
        self.thread.finished.connect(self.afterConnect)
        self.thread.start()
        
    def getInstruments(self,instruments):
        self.impd = instruments[0]
        self.TCont = instruments[4]
        self.modeLabel = QtWidgets.QLabel("")
        self.modeLabel.setText("Simulation mode running")
        simulation = False
        self.statusLabel =  QtWidgets.QLabel("")
        if self.impd.ID == 'Fake' and self.TCont.ID == 'Fake':
            self.statusLabel.setText('Impedance Analyzer, Temperature Controller not connected.')
            simulation = True
        elif self.TCont.ID == 'Fake':
            self.statusLabel.setText('Temperature Controller not connected.')
            simulation = True
        elif self.impd.ID == 'Fake':
            self.statusLabel.setText('Impedance Analyzer not connected.')
            simulation = True
        if simulation == True:
            self.statusBar().addPermanentWidget(self.modeLabel)
            self.statusBar().addPermanentWidget(VLine())
        if self.TCont.ID == 'Chino':
            self.fixedTemp.setValue(20)
        self.statusBar().addPermanentWidget(self.statusLabel)
    
    def AlertSettings(self):
        self.alert.exec_()
    
    def afterConnect(self):
        self.statusBar().showMessage("Connected")
        self.parameterBox.setEnabled(True)
        self.fileBox.setEnabled(True)
        self.measureControlBox.setEnabled(True)
        self.plotBox.setEnabled(True)
        self.statusBox.setEnabled(True)
        self.initializeParameters()
        self.stopButton.setEnabled(False)
        self.finished = True
        self.continuousDisplay()
    
    def checkPaths(self):
        """
        Check for paths to store data and setting files.
        
        address.txt stores path where SettingFile.dnd is stored.
        If address.txt not found, or path in it is invalid, 
        put SettingFile.dnd in current working directory.
        
        SettingFile.dnd stores path where last measurement data is stored,
        and also the last used filename. 
        If SettingFile.dnd does not exist or if path given in SettingFile.dnd 
        does not exist, set desktop as the default path to store the 
        measurement data. 
        If desktop is not found in C: drive, then make current working 
        directory as default path to store measurement data. 
        Use default sample name as "Sample".

        Returns
        -------
        None.

        """
        self.settingPath = ""
        self.sampleID = ''
        self.initialPath = os.getcwd()
        try:
            with open('address.txt') as f:
                self.settingPath = f.readline().strip()# get path of SettingFile.dnd
                self.E49990Addr = f.readline().strip().split() # get address of K2450 if present
                if self.E49990Addr:
                    self.E49990Addr = self.E49990Addr[0]
                else:
                    self.E49990Addr = ''
                self.k2700Addr = f.readline().strip().split() # get address of K700 if present
                if self.k2700Addr:
                    self.k2700Addr = self.k2700Addr[0]
                else:
                    self.k2700Addr = ''
                self.TControlAddr = f.readline().strip().split() # get address of AFG1022 if present
                if self.TControlAddr:
                    self.TControlAddr = self.TControlAddr[0]
                else:
                    self.TControlAddr = ''
                self.TSensorAddr = f.readline().strip().split() # get address of AFG1022 if present
                if self.TSensorAddr:
                    self.TSensorAddr = self.TSensorAddr[0]
                else:
                    self.TSensorAddr = ''
                os.chdir(self.settingPath)
        except FileNotFoundError:
            with open('address.txt','w') as f:
                f.write(self.initialPath)
            self.settingPath = self.initialPath
            self.E49990Addr = ''
            self.k2700Addr = ''
            self.TControlAddr = ''
            self.TSensorAddr = ''
            
        # set default path to store measured data as desktop
        self.defaultPath = os.path.join(
            os.path.expandvars("%userprofile%"), "Desktop")
        # set default path as current directory if desktop is not found in C drive
        if not os.path.exists(self.defaultPath):
            self.defaultPath = self.initialPath 

        # SettingFile contains last used filename & its location, which is loaded initially
        try:
            with open('SettingFile.dnd', 'r') as f:
                self.currPath = f.readline().strip('\n\r')
                self.sampleID = get_valid_filename(f.readline().strip())
                if self.sampleID == '' or self.sampleID.isspace():
                    self.sampleID = "Sample"
                os.chdir(self.currPath)
                self.filenameText.setText(self.sampleID)
        except FileNotFoundError: # if SettingFile does not exist, set default name
            self.currPath = self.defaultPath
            os.chdir(self.defaultPath)
            self.sampleID = "Sample"
    
    def initializeParameters(self):
        self.updateFixedDCVoltage()
        self.updateACVoltage()
        self.updateFixedTemperature()
        self.updateFixedFrequency()
        self.updateTempTraceback()
        self.updateTempInterval()
        self.updateMeasureMode()
        self.updateStartTemp()
        self.updateStopTemp()
        self.updateRateTemp()
        # Format bottom axis
        styles = {'color': (0, 0, 0), 'font-size': '20px'}
        pen = mkPen(color = (0, 0, 0), width=2)
        font = QtGui.QFont("Roman times", 11)
        self.leftPlot.setLabel('bottom', 'Frequency', units = 'Hz',**styles)
        self.leftPlot.getAxis('bottom').setPen(pen)
        self.leftPlot.getAxis('bottom').setTickFont(font)
        self.leftPlot.setLogMode(True, False)
        self.leftPlot.setRange(xRange=(log10(20), log10(1e7)), padding=0.05)
        self.plotView = self.choosePlot.view()
        self.plotView.setRowHidden(1,True)
        self.plotView.setRowHidden(3,True)
        self.TsensorView = self.sensor.view()
        self.updateTemperatureController()
    
    def updateStartTemp(self):
        self.TCont.startT = self.startTemp.value()
    
    def updateStopTemp(self):
        self.TCont.stopT = self.stopTemp.value()
    
    def updateRateTemp(self):
        self.TCont.rate = self.heatRate.value()
        
    def updateFixedDCVoltage(self):
        self.impd.Vdc = self.fixedDCvolt.value()
        
    def updateACVoltage(self):
        self.impd.Vac = self.fixedACvolt.value()
        
    def updateFixedTemperature(self):
        self.TCont.temp = self.fixedTemp.value()
        
    def updateTemperatureController(self):
        if self.inst.currentIndex() == 0:
            if self.sensor.currentIndex() == 1:
                self.sensor.setCurrentIndex(0)
            self.TsensorView.setRowHidden(1,True)
            self.TsensorView.setRowHidden(0,False)
            self.TsensorView.setRowHidden(2,False)
            self.TsensorView.setRowHidden(3,False)
        elif self.inst.currentIndex() == 1:
            self.sensor.setCurrentIndex(1)
            self.TsensorView.setRowHidden(0,True)
            self.TsensorView.setRowHidden(2,True)
            self.TsensorView.setRowHidden(3,True)
            self.TsensorView.setRowHidden(1,False)
     
    def updateStartFrequency(self):
        multiply = 1
        if self.startFreqUnit.currentIndex() == 0:
            self.startFreq.setMinimum(20)
        elif self.startFreqUnit.currentIndex() == 1:
            self.startFreq.setMinimum(1)
            multiply = 1000
        elif self.startFreqUnit.currentIndex() == 2:
            self.startFreq.setMinimum(1)
            multiply = 1000000
        self.startFreq.setMaximum(10000000/multiply)
    
    def updateStopFrequency(self):
        multiply = 1
        if self.stopFreqUnit.currentIndex() == 0:
            self.stopFreq.setMinimum(20)
        elif self.stopFreqUnit.currentIndex() == 1:
            self.stopFreq.setMinimum(1)
            multiply = 1000
        elif self.stopFreqUnit.currentIndex() == 2:
            self.stopFreq.setMinimum(1)
            multiply = 1000000
        self.stopFreq.setMaximum(10000000/multiply)
    
    def updateFixedFrequency(self):
        multiply = 1
        if self.fixedFreqUnit.currentIndex() == 0:
            self.fixedFreq.setMinimum(20)
        elif self.fixedFreqUnit.currentIndex() == 1:
            self.fixedFreq.setMinimum(1)
            multiply = 1000
        elif self.fixedFreqUnit.currentIndex() == 2:
            self.fixedFreq.setMinimum(1)
            multiply = 1000000
        self.impd._freq = self.fixedFreq.value()*multiply
        self.impd.fix_frequency()
        self.fixedFreq.setMaximum(10000000/multiply)
        self.impd.getFreqUnit()
        #TODO maybe show the frequency returned by the instrument?
        self.freqStatus.setText("{0} {1}".format(self.impd.freq, self.impd.freqUnit))
    
    def updateStabilizationTime(self):
        self.TCont.stabilizationTime = self.stabilizationTime.value()
        
    def updateTempTraceback(self):
        if self.tempTraceback.isChecked():
            self.TCont.traceback = True
        else:
            self.TCont.traceback = False
    
    def updateTempInterval(self):
        self.TCont.interval = self.tempInterval.value()
    
    def updateMeasureMode(self):
        self.TCont.mode = self.measureMode.currentIndex()
    
    def setTemperature(self):
        self.TCont.temp = self.fixedTemp.value()
        #self.tempStatus.setText("{} K".format(round(self.TCont.temp,2)))
    
    def setACVolts(self):
        self.impd.setVac()
        self.ACvoltStatus.setText("{} V".format(round(self.impd.Vac,3)))
    
    def setDCVolts(self):
        if self.impd.Vdc != 0 :
            self.impd.enable_DC_Bias(True)
            self.impd.setVdc()
        else:
            self.impd.setVdc()
            self.impd.enable_DC_Bias(False)
        self.DCvoltStatus.setText("{} V".format(round(self.impd.Vdc,3)))
    
    def stop_Temperature_Controller(self):
        self.TCont.reset()
        
    def showTempTable(self):
        self.Form.show()
        
    def freqOption(self):
        if self.fixFreq.isChecked() == True:
            self.fixedFreq.setEnabled(True)
            self.fixedFreqUnit.setEnabled(True)
            self.startFrequencyLabel.setEnabled(False)
            self.startFreq.setEnabled(False)
            self.startFreqUnit.setEnabled(False)
            self.stopFrequencyLabel.setEnabled(False)
            self.stopFreq.setEnabled(False)
            self.stopFreqUnit.setEnabled(False)
            self.pointsLabel.setEnabled(False)
            self.npoints.setEnabled(False)
            self.pointSpacingLabel.setEnabled(False)
            self.spacingType.setEnabled(False)
            self.freqsweep = False
        else:
            self.fixedFreq.setEnabled(False)
            self.fixedFreqUnit.setEnabled(False)
            self.startFrequencyLabel.setEnabled(True)
            self.startFreq.setEnabled(True)
            self.startFreqUnit.setEnabled(True)
            self.stopFrequencyLabel.setEnabled(True)
            self.stopFreq.setEnabled(True)
            self.stopFreqUnit.setEnabled(True)
            self.pointsLabel.setEnabled(True)
            self.npoints.setEnabled(True)
            self.pointSpacingLabel.setEnabled(True)
            self.spacingType.setEnabled(True)
            self.freqsweep = True
    
    def tempOption(self):
        if self.fixTemp.isChecked() == True and self.temperatureBox.isChecked():
            self.fixedTemp.setEnabled(True)
            self.setFixedTemperature.setEnabled(True)
            self.startTemp.setEnabled(False)
            self.stopTemp.setEnabled(False)
            self.measureMode.setEnabled(False)
            self.tempInterval.setEnabled(False)
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            self.heatRate.setEnabled(False)
            self.stabilizationTime.setEnabled(False)
            self.tempTraceback.setEnabled(False)
            self.frame.hide()
            self.loadTempButton.setEnabled(False)
            self.loadTempButton.hide()
        else:
            self.fixedTemp.setEnabled(False)
            self.setFixedTemperature.setEnabled(False)
            self.startTemp.setEnabled(True)
            self.stopTemp.setEnabled(True)
            self.heatRate.setEnabled(True)
            self.measureMode.setEnabled(True)
            self.tempTraceback.setEnabled(True)
            self.measureModeSet()
    
    def measureModeSet(self):
        if self.measureMode.currentIndex() == 0:
            self.tempInterval.setEnabled(False)
            self.frame.hide()
            self.tempTraceback.show()
            self.loadTempButton.setEnabled(False)
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 1:
            self.frame.show()
            self.tempTraceback.show()
            self.measureLabel.setEnabled(True)
            self.tempInterval.setEnabled(True)
            self.degreesLabel.setEnabled(True)
            self.loadTempButton.setEnabled(False)
            self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 2:
            self.tempInterval.setEnabled(False)
            self.frame.hide()
            self.tempTraceback.hide()
            self.loadTempButton.show()
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            self.loadTempButton.setEnabled(True)
    
    def DCvoltOption(self):
        if self.fixDCvolts.isChecked() == True:
            if self.lastfreqstate == 'sweep':
                self.fixFreq.setChecked(False)
                self.freqOption()
            self.fixedDCvolt.setEnabled(True)
            self.setFixedDCV.setEnabled(True)
            self.startVoltageLabel.setEnabled(False)
            self.startVoltage.setEnabled(False)
            self.stopVoltageLabel.setEnabled(False)
            self.stopVoltage.setEnabled(False)
            self.voltagePointsLabel.setEnabled(False)
            self.voltageNpoints.setEnabled(False)
            self.traceback.setEnabled(False)
            self.fixTemp.setEnabled(True)
            if not self.temperatureBox.isChecked():
                self.temperatureBox.setChecked(True)
                self.temperatureBox.setChecked(False)
        else:
            if not self.fixFreq.isChecked():
                self.lastfreqstate = 'sweep'
                self.fixFreq.setChecked(True)
                self.freqOption()
            else:
                self.lastfreqstate = 'fix'
            self.fixedDCvolt.setEnabled(False)
            self.setFixedDCV.setEnabled(False)
            self.startVoltageLabel.setEnabled(True)
            self.startVoltage.setEnabled(True)
            self.stopVoltageLabel.setEnabled(True)
            self.stopVoltage.setEnabled(True)
            self.voltagePointsLabel.setEnabled(True)
            self.voltageNpoints.setEnabled(True)
            self.traceback.setEnabled(True)
            
            # disable temperature sweep option
            tbox = True
            if not self.temperatureBox.isChecked():
                self.temperatureBox.setChecked(True)
                tbox = False
            self.fixTemp.setChecked(True)
            self.tempOption()
            self.fixTemp.setEnabled(False)
            if not tbox:
                self.temperatureBox.setChecked(False)
        self.setVoltageCycles()
        
    def loadTemperatures(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Temperature Files (*.txt)", options=options)
        if files:
            self.temperatures = loadtxt(files[0])
    
    def setVoltageCycles(self):
        if self.traceback.isChecked() and not self.fixDCvolts.isChecked():
            self.voltageNcyclesLabel.setEnabled(True)
            self.Vncycles.setEnabled(True)
        else:
            self.voltageNcyclesLabel.setEnabled(False)
            self.Vncycles.setEnabled(False)
    
    def continuousDisplay(self):
        if not self.idleRun and self.finished:
            self.idleRun = True
            self.showControllerStatus()
            self.startIdleThread()
        
    def startIdleThread(self):
        self.idlethread = QThread()
        self.idleWorker = IdleWorker(self.impd,self.TCont)
        self.idleWorker.moveToThread(self.idlethread)
        self.idlethread.started.connect(self.idleWorker.start)
        self.idleWorker.finished.connect(self.idlethread.quit)
        self.idleWorker.finished.connect(self.idleWorker.deleteLater)
        self.idlethread.finished.connect(self.idlethread.deleteLater)
        self.idleWorker.data.connect(self.showStatus)
        #self.thread.finished.connect(self.finishAction)
        self.idlethread.start()
        
    def showControllerStatus(self):
        self.freqStatus.setText("{0} {1}".format(self.impd.freq, self.impd.freqUnit))
        self.TCont.real_data_request()
        if self.TCont.temp != -1:
            self.tempStatus.setText("{} K".format(self.TCont.temp))
        else:
            self.tempStatus.setText("NA")
        self.ACvoltStatus.setText("{} V".format(self.impd.Vac))
        self.DCvoltStatus.setText("{} V".format(self.impd.Vdc))
        
    def showStatus(self, data):
        self.ZImStatus.setText("{}".format(round(data[1],3)))
        ZAbs = data[0]
        if ZAbs >= 1e9:
            ZUnit = 'GΩ'
            ZAbs/=1e6
        elif 1e9 > ZAbs >= 1e6:
            ZUnit = 'MΩ'
            ZAbs/=1e6
        elif 1e6 > ZAbs >= 1e3:
            ZUnit = 'kΩ'
            ZAbs/=1e3
        elif 1e3 > ZAbs > 0.1:
            ZUnit = 'Ω'
        elif 0.1 >= ZAbs > 1e-4:
            ZUnit = 'mΩ'
            ZAbs*=1000
        elif 1e-4 >= ZAbs:
            ZUnit = 'μΩ'
            ZAbs*=1e6
        elif 1e-7 >= ZAbs > 1e-10:
            ZUnit = 'nF'
            ZAbs*=1e9
        elif 1e-10 >= ZAbs:
            ZUnit = 'pF'
            ZAbs*=1e12
        self.ZReStatus.setText("{0} {1}".format(round(ZAbs,3),ZUnit))
        capacitance = data[2]
        if capacitance > 0.1:
            capUnit = 'F'
        elif 0.1 >= capacitance > 1e-4:
            capUnit = 'mF'
            capacitance*=1000
        elif 1e-4 >= capacitance > 1e-7:
            capUnit = 'μF'
            capacitance*=1e6
        elif 1e-7 >= capacitance > 1e-10:
            capUnit = 'nF'
            capacitance*=1e9
        elif 1e-10 >= capacitance:
            capUnit = 'pF'
            capacitance*=1e12
        self.capStatus.setText("{0} {1}".format(round(capacitance,3), capUnit))
        self.tandStatus.setText("{}".format(round(data[3],3)))
        temperature = data[-1]
        if temperature != -1:
            self.tempStatus.setText("{} K".format(temperature))
        else:
            self.tempStatus.setText("NA")
    
    def startProgram(self):
        #print(self.temptable.model._data)
        self.parameterBox.setEnabled(False)
        self.statusBox.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.FsweepRun = False
        self.TFsweepRun = False
        self.finished = False
        if not self.fixFreq.isChecked():
            self.idleWorker.stopcall.emit()
            self.idleRun = False
            self.setFileName()
            self.impd.startf = self.impd.get_absolute_frequency(self.startFreq.value(),self.startFreqUnit.currentIndex())
            self.impd.endf = self.impd.get_absolute_frequency(self.stopFreq.value(),self.stopFreqUnit.currentIndex())
            self.impd.npointsf = self.npoints.value()
            self.impd.sweeptypef = self.spacingType.currentIndex()
            self.ImpdPlot.enableAutoRange()
            if not self.temperatureBox.isChecked() or self.fixTemp.isChecked(): # frequency sweep
                self.startFreqSweepThread()
                self.FsweepRun = True
                self.currentView = 0
            elif self.temperatureBox.isChecked() and not self.fixTemp.isChecked(): # temperature sweep
                self.filenameText.setEnabled(False)
                self.saveDir.setEnabled(False)
                self.startTempSweepThreadF()
                self.TFsweepRun = True
                self.currentView = 1
        elif self.DCvoltageBox.isChecked() and not self.fixDCvolts.isChecked():
            self.idleWorker.stopcall.emit()
            self.idleRun = False
            self.setFileName()
            self.impd._freq = self.fixedFreq.value()
            units = ['Hz','kHz','MHz']
            self.impd.freqUnit = units[self.fixedFreqUnit.currentIndex()]
            self.impd.dcStart = self.startVoltage.value()
            self.impd.dcStop = self.stopVoltage.value()
            self.impd.dcPoints = self.voltageNpoints.value()
            self.impd.dcTraceback = self.traceback.isChecked()
            self.impd.dcNcycles = self.Vncycles.value()
            self.ImpdPlot.enableAutoRange()
            if not self.temperatureBox.isChecked() or self.fixTemp.isChecked(): # DC bias sweep
                self.startDCbiasSweepThread()
                self.DCsweepRun = True
                self.currentView = 2
            elif self.temperatureBox.isChecked() and not self.fixTemp.isChecked(): # temperature sweep
                self.filenameText.setEnabled(False)
                self.startTempSweepThreadDC()
                self.TDCsweepRun = True
                self.currentView = 4
        else:
            self.statusBar().showMessage("No sweep program selected.")
            self.stopProgram()
    
    def startFreqSweepThread(self):
        self.freqthread = QThread()
        self.fSweepWorker = FrequencySweepWorker(self.impd,
                                                 self.TCont,
                                                 self.alert.currentUser,
                                                 self.settingpath)
        self.fSweepWorker.moveToThread(self.freqthread)
        self.freqthread.started.connect(self.fSweepWorker.start_frequency_sweep)
        self.fSweepWorker.finished.connect(self.freqthread.quit)
        self.fSweepWorker.finished.connect(self.fSweepWorker.deleteLater)
        self.freqthread.finished.connect(self.freqthread.deleteLater)
        self.fSweepWorker.data.connect(self.plotFsweepData)
        self.fSweepWorker.showStatus.connect(self.statusBar().showMessage)
        self.freqthread.finished.connect(self.finishAction)
        self.freqthread.start()
        self.initialize_frequencySweep_plot()
    
    def initialize_frequencySweep_plot(self):
        """
        Initialize the plot to display frequency sweep.

        Returns
        -------
        None.

        """
        self.plotView.setRowHidden(1,True)
        self.plotView.setRowHidden(3,True)
        self.phaseButton.setEnabled(True)
        self.lossButton.setEnabled(True)
        self.ImpdPlot.clear()
        self.rightPlot.clear()
        styles = {'color': (0, 0, 0), 'font-size': '20px'}
        pen = mkPen(color = (0, 0, 0), width=2)
        font = QtGui.QFont("Roman times", 11)
        self.leftPlot.setLabel('bottom', 'Frequency', units = 'Hz',**styles)
        self.leftPlot.getAxis('bottom').setPen(pen)
        self.leftPlot.getAxis('bottom').setTickFont(font)
        if self.spacingType.currentIndex() == 0:
            self.leftPlot.setLogMode(False, False)
            self.leftPlot.setRange(xRange=(self.impd.startf, self.impd.endf), padding=0.05)
            #self.ImpdPlot.getAxis('bottom').setLogMode(False)
        else:
            self.leftPlot.setLogMode(True, False)
            self.leftPlot.setRange(xRange=(log10(self.impd.endf), log10(self.impd.startf)), padding=0.05)
        self.ImpdPlot.addLegend()
        
    def plotFsweepData(self,data=-1):
        if data != -1:
            fdata = list(zip(data[0],data[1],data[2],data[3],data[4]))
            self.frequency_sweep_data = DataFrame(fdata,columns=['Frequency(Hz)','Absolute Impedance Z','Absolute Phase TZ','Capacitance CP (F)', 'Loss (tanδ)'])
            try:
                temperature = data[-2]
                deltaT = data[-1]
            except:
                temperature = 'NA'
                deltaT = 0
            # Save the data to file
            with open(self.sampleID_fSweep, 'w') as f:
                f.write("#AC Voltage = {0}V, DC Bias = {1}V, Temperature = {2}K, ΔT = {3}\n\n".format(self.impd.Vac, self.impd.Vdc, temperature, deltaT))
                self.frequency_sweep_data.to_csv(f,index=False)
        else:
            self.ImpdPlot.clear()
            self.rightPlot.clear()
        if self.plotIndex in (0,1): # impedance only
            pen1 = mkPen(color = (170, 85, 0), width=2)
            pen2 = mkPen(color = (0, 170, 127), width=2)
            self.leftPlot.plot(self.frequency_sweep_data.iloc[:,0], self.frequency_sweep_data.iloc[:,1], name="Vac = {}".format(self.fixedACvolt.value()), pen=pen1)
            self.rightData = PlotDataItem(self.frequency_sweep_data.iloc[:,0], self.frequency_sweep_data.iloc[:,2], pen=pen2)
            if self.spacingType.currentIndex() == 0:
                self.rightData.setLogMode(False, False)
            else:
                self.rightData.setLogMode(True, False)
            self.rightPlot.addItem(self.rightData)
            if self.plotIndex == 0:
                self.leftPlot.hideAxis('right')
                self.rightPlot.hide()
            else:
                self.leftPlot.showAxis('right')
                self.leftPlot.getAxis('right').setLabel('Phase')
                self.rightPlot.show()
        elif self.plotIndex in (2,3): #Capacitance only
            pen1 = mkPen(color = (0, 0, 255), width=2)
            pen2 = mkPen(color = (255, 127, 0), width=2)
            self.leftPlot.plot(self.frequency_sweep_data.iloc[:,0], self.frequency_sweep_data.iloc[:,3], name="Vac = {}".format(self.fixedACvolt.value()), pen=pen1)
            self.rightData = PlotDataItem(self.frequency_sweep_data.iloc[:,0], self.frequency_sweep_data.iloc[:,4], pen=pen2)
            if self.spacingType.currentIndex() == 0:
                self.rightData.setLogMode(False, False)
            else:
                self.rightData.setLogMode(True, False)
            self.rightPlot.addItem(self.rightData)
            if self.plotIndex == 2:
                self.leftPlot.hideAxis('right')
                self.rightPlot.hide()
            else:
                self.leftPlot.showAxis('right')
                self.leftPlot.getAxis('right').setLabel('tan(δ)')
                self.rightPlot.show()
        
    def startDCbiasSweepThread(self):
        self.dcSweepthread = QThread()
        self.dcSweepWorker = DCSweepWorker(self.impd,
                                           self.TCont,
                                           self.alert.currentUser,
                                           self.settingpath)
        self.dcSweepWorker.moveToThread(self.dcSweepthread)
        self.dcSweepthread.started.connect(self.dcSweepWorker.start_dc_sweep)
        self.dcSweepWorker.finished.connect(self.dcSweepthread.quit)
        self.dcSweepWorker.finished.connect(self.dcSweepWorker.deleteLater)
        self.dcSweepthread.finished.connect(self.dcSweepthread.deleteLater)
        self.dcSweepWorker.data.connect(self.plotDCsweepData)
        self.dcSweepWorker.showStatus.connect(self.statusBar().showMessage)
        self.dcSweepthread.finished.connect(self.finishAction)
        self.freqthread.start()
        self.initialize_dcSweep_plot()
    
    def initialize_dcSweep_plot(self):
        """
        Initialize the plot to display DC bias sweep.

        Returns
        -------
        None.

        """
        self.plotView.setRowHidden(1,True)
        self.plotView.setRowHidden(3,True)
        self.phaseButton.setEnabled(True)
        self.lossButton.setEnabled(True)
        self.ImpdPlot.clear()
        self.rightPlot.clear()
        styles = {'color': (0, 0, 0), 'font-size': '20px'}
        pen = mkPen(color = (0, 0, 0), width=2)
        font = QtGui.QFont("Roman times", 11)
        self.leftPlot.setLabel('bottom', 'Voltage', units = 'V',**styles)
        self.leftPlot.getAxis('bottom').setPen(pen)
        self.leftPlot.getAxis('bottom').setTickFont(font)
        self.leftPlot.setLogMode(False, False)
        self.leftPlot.setRange(xRange=(self.impd.startf, self.impd.endf), padding=0.05)
        self.ImpdPlot.addLegend()
        
    def plotDCsweepData(self,data=-1):
        if data != -1:
            vdata = list(zip(data[0],data[1],data[2],data[3],data[4]))
            self.DC_sweep_data = DataFrame(vdata,columns=['DC Bias(V)','Absolute Impedance Z','Absolute Phase TZ','Capacitance CP (F)', 'Loss (tanδ)'])
            try:
                temperature = data[-2]
                deltaT = data[-1]
            except:
                temperature = 'NA'
                deltaT = 0
            # Save the data to file
            with open(self.sampleID_dcSweep, 'w') as f:
                f.write("#AC Voltage = {0}V, Frequency = {1}{2}, Temperature = {3}K, ΔT = {4}\n\n".format(self.impd.Vac, 
                                                                                                          self.impd._freq, 
                                                                                                          self.impd.freqUnit, 
                                                                                                          temperature, 
                                                                                                          deltaT))
                self.DC_sweep_data.to_csv(f,index=False)
        else:
            self.ImpdPlot.clear()
            self.rightPlot.clear()
        if self.plotIndex in (0,1): # impedance only
            pen1 = mkPen(color = (170, 85, 0), width=2)
            pen2 = mkPen(color = (0, 170, 127), width=2)
            self.leftPlot.plot(self.DC_sweep_data.iloc[:,0], self.DC_sweep_data.iloc[:,1], name="Frequency = {0}{1}".format(self.impd._freq,self.impd.freqUnit), pen=pen1)
            self.rightData = PlotDataItem(self.DC_sweep_data.iloc[:,0], self.DC_sweep_data.iloc[:,2], pen=pen2)
            self.rightPlot.addItem(self.rightData)
            if self.plotIndex == 0:
                self.leftPlot.hideAxis('right')
                self.rightPlot.hide()
            else:
                self.leftPlot.showAxis('right')
                self.leftPlot.getAxis('right').setLabel('Phase')
                self.rightPlot.show()
        elif self.plotIndex in (2,3): #Capacitance only
            pen1 = mkPen(color = (0, 0, 255), width=2)
            pen2 = mkPen(color = (255, 127, 0), width=2)
            self.leftPlot.plot(self.DC_sweep_data.iloc[:,0], self.DC_sweep_data.iloc[:,3], name="Frequency = {0}{1}".format(self.impd._freq,self.impd.freqUnit), pen=pen1)
            self.rightData = PlotDataItem(self.DC_sweep_data.iloc[:,0], self.DC_sweep_data.iloc[:,4], pen=pen2)
            self.rightPlot.addItem(self.rightData)
            if self.plotIndex == 2:
                self.leftPlot.hideAxis('right')
                self.rightPlot.hide()
            else:
                self.leftPlot.showAxis('right')
                self.leftPlot.getAxis('right').setLabel('tan(δ)')
                self.rightPlot.show()
                
    def startTempSweepThreadDC(self):
        pass
    
    def setFileName(self, initial = 0):
        """
        Autogenerate the filenames for various operations.

            Generate only if changes to existing filename are made,
            except when initial not equal to 0

        Parameters
        ----------
        initial : int, optional
            Set initial = 1 to generate the default names.
            The default is 0.

        Returns
        -------
        None.

        """
        if self.filenameText.isModified() or initial:
            self.sampleID = get_valid_filename(self.filenameText.text())
            if self.sampleID.find('.') != -1:
                # rindex returns the last location of '.'
                index = self.sampleID.rindex('.')
                self.sampleID = self.sampleID[:index]
            self.filenameText.setText(self.sampleID)
        self.sampleID_fSweep = unique_filename(directory='.', prefix = self.sampleID+'_Fsweep', datetimeformat="", ext='csv')
        self.sampleID_dcSweep = unique_filename(directory='.', prefix = self.sampleID+'_DCsweep', datetimeformat="", ext='csv')
        self.sampleID_tSweepF = unique_filename(directory='.', prefix = self.sampleID+'_TsweepF', datetimeformat="", ext='csv')
        
    def chooseSaveDir(self):
        """
        Open the dialog for selecting directory.

        Returns
        -------
        None.

        """
        options = QtWidgets.QFileDialog()
        options.setFileMode(QtWidgets.QFileDialog.Directory)
        options.setDirectory(os.getcwd())
        dirName = options.getExistingDirectory()
        if dirName:
            os.chdir(dirName)
            self.currPath = dirName
            self.sampleID_fSweep = unique_filename(directory='.', prefix = self.sampleID+'_Fsweep', datetimeformat="", ext='txt')
            self.sampleID_dcSweep = unique_filename(directory='.', prefix = self.sampleID+'_DCsweep', datetimeformat="", ext='txt')
            self.sampleID_tSweepF = unique_filename(directory='.', prefix = self.sampleID+'_TsweepF', datetimeformat="", ext='txt')
        
    def finishAction(self):
        if self.FsweepRun:
            self.FsweepRun = False
        elif self.TFsweepRun:
            self.filenameText.setEnabled(True)
            self.saveDir.setEnabled(True)
            self.TFsweepRun = False
            self.ImpdPlot.enableAutoRange()
        self.finished = True
        self.parameterBox.setEnabled(True)
        self.statusBox.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.continuousDisplay()
        
    def startTempSweepThreadF(self): # temperature and frequency sweep
        self.tempthreadf = QThread()
        self.tSweepWorker = TemperatureSweepWorkerF(self.impd, 
                                                    self.TCont,
                                                    self.alert.currentUser,
                                                    self.settingPath)
        self.tSweepWorker.moveToThread(self.tempthreadf)
        self.tempthreadf.started.connect(self.tSweepWorker.start_temperature_sweep)
        self.tSweepWorker.finished.connect(self.tempthreadf.quit)
        self.tSweepWorker.finished.connect(self.tSweepWorker.deleteLater)
        self.tempthreadf.finished.connect(self.tempthreadf.deleteLater)
        self.tSweepWorker.data.connect(self.plotTsweepData)
        self.tSweepWorker.showStatus.connect(self.statusBar().showMessage)
        self.tSweepWorker.freqSig.connect(self.initialize_temperatureFSweep_plot)
        self.tempthreadf.finished.connect(self.finishAction)
        self.tempthreadf.start()
        
    def initialize_temperatureFSweep_plot(self,fdata):
        """
        Initialize the plot to display temperature-frequency sweep.

        Returns
        -------
        None.

        """
        self.plotView.setRowHidden(1,False)
        self.plotView.setRowHidden(3,False)
        self.phaseButton.setEnabled(False)
        self.lossButton.setEnabled(False)
        self.ImpdPlot.clear()
        self.rightPlot.clear()
        self.ImpdPlot.setLogMode(False, False)
        #self.ImpdPlot.getAxis('bottom').setLogMode(False)
        styles = {'color': 'b', 'font-size': '20px'}
        pen = mkPen(color = (0, 0, 0), width=2)
        font = QtGui.QFont("Roman times", 11)
        self.leftPlot.setLabel('bottom', 'Temperature', units = 'K', **styles)
        self.leftPlot.getAxis('bottom').setPen(pen)
        self.leftPlot.getAxis('bottom').setTickFont(font)
        self.ImpdPlot.addLegend()
        mintemp = min(self.startTemp.value(),self.stopTemp.value())
        maxtemp = max(self.startTemp.value(),self.stopTemp.value())
        self.leftPlot.setRange(xRange=(mintemp, maxtemp), padding=0.05)
        self.TFPlots = []
        pData = [fdata[-2],fdata[-1]]
        for i in range(len(fdata[0])):
            pData.append(fdata[1][i])
            pData.append(fdata[2][i])
            pData.append(fdata[3][i])
            pData.append(fdata[4][i])
        self.tempData = [fdata[-2]]
        l = len(fdata[0])
        header = ['Temperature(K)', 'ΔT(K)']
        self.plotPoints = linspace(0,l,6,dtype=int,endpoint=False)
        for i,Fdata in enumerate(fdata[0]):
            pen1 = mkPen(intColor((i+1), values=3), width=2)
            if Fdata < 1e3:
                freqlabel = "{} Hz".format(round(Fdata,2))
                header.append('Z {}Hz'.format(round(Fdata,2)))
                header.append('p {}Hz'.format(round(Fdata,2)))
                header.append('C {}Hz'.format(round(Fdata,2)))
                header.append('d {}Hz'.format(round(Fdata,2)))
            elif 1e6 > Fdata >= 1e3:
                freqlabel = "{} kHz".format(round(Fdata/1e3,2))
                header.append('Z {}kHz'.format(round(Fdata/1e3,2)))
                header.append('p {}kHz'.format(round(Fdata/1e3,2)))
                header.append('C {}kHz'.format(round(Fdata/1e3,2)))
                header.append('d {}kHz'.format(round(Fdata/1e3,2)))
            elif Fdata >= 1e6:
                freqlabel = "{} MHz".format(round(Fdata/1e6,2))
                header.append('Z {}MHz'.format(round(Fdata/1e6,2)))
                header.append('p {}MHz'.format(round(Fdata/1e6,2)))
                header.append('C {}MHz'.format(round(Fdata/1e6,2)))
                header.append('d {}MHz'.format(round(Fdata/1e6,2)))
            self.TFPlots.append(self.ImpdPlot.plot([pData[0]],[pData[2+self.plotIndex+i*4]], pen = pen1))
            if i not in self.plotPoints:
                self.TFPlots[i].hide()
            else:
                self.ImpdPlot.plotItem.legend.addItem(self.TFPlots[i], name = freqlabel)
        self.dfData = DataFrame(data = [pData],columns=header)
        with open(self.sampleID_tSweepF, 'w',newline='') as f:
            f.write("#AC Voltage = {0}V, DC Bias = {1}V\n\n".format(self.impd.Vac, self.impd.Vdc))
            self.dfData.to_csv(f,index=False)
        
    def plotTsweepData(self, data=-1):
        if data != -1:
            self.tempData.append(data[-2])
            pData = [data[-2],data[-1]]
            for i in range(len(data[0])):
                pData.append(data[0][i])
                pData.append(data[1][i])
                pData.append(data[2][i])
                pData.append(data[3][i])
            self.dfRow = Series(pData,self.dfData.columns)
            self.dfData = self.dfData.append(self.dfRow,ignore_index=True)
            rData = DataFrame(data = [pData],columns=self.dfData.columns)
            rData.to_csv(self.sampleID_tSweepF,index=False,mode='a',header=False)
        else:
            self.ImpdPlot.enableAutoRange()
        for i in self.plotPoints:
            self.TFPlots[i].setData(self.dfData.iloc[:,0],self.dfData.iloc[:,2+self.plotIndex+i*4])
                
        ## Handle view resizing 
    def updateViews(self):
        ## view has resized; update auxiliary views to match
        self.rightPlot.setGeometry(self.leftPlot.vb.sceneBoundingRect())
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.rightPlot.linkedViewChanged(self.leftPlot.vb, self.rightPlot.XAxis)
    
    def phasePlot(self):
        styles = {'color': (0, 170, 127), 'font-size': '20px'}
        pen = mkPen(color = (0, 170, 127), width=2)
        font = QtGui.QFont("Roman times", 11)
        if self.phaseButton.isChecked():
            self.plotIndex = 1
            #set phase as y-axis right
            self.leftPlot.showAxis('right')
            self.leftPlot.getAxis('right').setLabel('Phase', **styles)
            self.leftPlot.getAxis('right').setPen(pen)
            self.leftPlot.getAxis('right').setTickFont(font)
            self.rightPlot.show()
        else:
            self.plotIndex = 0
            self.leftPlot.getAxis('right').setLabel('', **styles)
            self.leftPlot.hideAxis('right')
            self.rightPlot.hide()
            # hide phase plot
    
    def lossPlot(self):
        styles = {'color': (255, 127, 0), 'font-size': '20px'}
        pen = mkPen(color = (255, 127, 0), width=2)
        font = QtGui.QFont("Roman times", 11)
        if self.lossButton.isChecked():
            self.plotIndex = 3
            #set loss as y-axis right
            self.leftPlot.showAxis('right')
            self.leftPlot.getAxis('right').setLabel('tan(δ)', **styles)
            self.leftPlot.getAxis('right').setPen(pen)
            self.leftPlot.getAxis('right').setTickFont(font)
            self.rightPlot.show()
        else:
            self.plotIndex = 2
            self.leftPlot.getAxis('right').setLabel('', **styles)
            self.leftPlot.hideAxis('right')
            self.rightPlot.hide()
            # hide loss plot
    
    def updatePlotOption(self):
        font = QtGui.QFont("Roman times", 11)
        if self.currentView == 0:
            self.ImpdPlot.enableAutoRange()
        elif self.currentView == 1:
            mintemp = min(self.startTemp.value(),self.stopTemp.value())
            maxtemp = max(self.startTemp.value(),self.stopTemp.value())
            self.ImpdPlot.setRange(xRange=(mintemp, maxtemp), padding=0.05)
            self.ImpdPlot.enableAutoRange(axis='y')
        if self.choosePlot.currentIndex() == 0:
            self.phaseButton.show()
            self.lossButton.hide()
            if self.phaseButton.isChecked() and self.currentView == 0:
                self.plotIndex = 1
            else:
                self.plotIndex = 0
            pen = mkPen(color = (170, 85, 0), width=2)
            styles = {'color': (170, 85, 0), 'font-size': '20px'}
            self.leftPlot.setLabel('left', 'Impedance Z', units = 'Ω', **styles)
            self.leftPlot.getAxis('left').setPen(pen)
            self.leftPlot.getAxis('left').setTickFont(font)
            # hide capacitance and loss plot
            # display impedance on y-axis left
        elif self.choosePlot.currentIndex() == 2:
            self.phaseButton.hide()
            self.lossButton.show()
            if self.lossButton.isChecked() and self.currentView == 0:
                self.plotIndex = 3
            else:
                self.plotIndex = 2
            styles = {'color': (0, 0, 255), 'font-size': '20px'}
            pen = mkPen(color = (0, 0, 255), width=2)
            self.leftPlot.setLabel('left', 'Capacitance Cp', units = 'F', **styles)
            self.leftPlot.getAxis('left').setPen(pen)
            self.leftPlot.getAxis('left').setTickFont(font)
            # hide impedance and phase plot
            # display capacitance on y-axis left
        elif self.choosePlot.currentIndex() == 1:
            styles = {'color': (0, 0, 255), 'font-size': '20px'}
            pen = mkPen(color = (0, 170, 127), width=2)
            self.leftPlot.setLabel('left', 'Phase', units = '', **styles)
            self.plotIndex = 1
        elif self.choosePlot.currentIndex() == 3:
            styles = {'color': (0, 0, 255), 'font-size': '20px'}
            pen = mkPen(color = (255, 127, 0), width=2)
            self.leftPlot.setLabel('left', 'tan(δ)', units = '', **styles)
            self.plotIndex = 3
        self.leftPlot.getAxis('left').setPen(pen)
        self.leftPlot.getAxis('left').setTickFont(font)
        if self.finished == True:
            if self.currentView == 0:
                try:
                    self.plotFsweepData()
                except AttributeError:
                    pass
            elif self.currentView == 1:
                try:
                    self.plotTsweepData()
                except AttributeError:
                    pass
    
    def stopProgram(self):
        if not self.finished:
            if self.FsweepRun:
                self.fSweepWorker.stopcall.emit()
            elif self.TFsweepRun:
                self.tSweepWorker.stopcall.emit()
            else:
                self.finished = True
        self.parameterBox.setEnabled(True)
        self.statusBox.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.continuousDisplay()
    
    def closeEvent(self, event):
        try:
            self.idleWorker.stopcall.emit()
            sleep(0.1)
            self.impd.write(":SENS1:SWE:POIN 50")
            self.impd.display_on()
            sleep(0.1)
            self.idleRun = False
        except:
            pass
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Confirm Exit',
                                           quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.impd.close()
            self.TCont.close()
            # TODO: Close all connected instruments (Other multimeters? multiplexer)
            if self.TFsweepRun:
                self.tSweepWorker.stopcall.emit()
            if self.FsweepRun:
                self.fSweepWorker.stopcall.emit()
            os.chdir(self.settingPath)
            with open('SettingFile.dnd', 'w') as f:
                f.write(self.currPath+'\n')
                f.write(self.sampleID)
            os.chdir(self.initialPath)
            event.accept()
        else:
            event.ignore()
            self.continuousDisplay()
            
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = mainControl()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()