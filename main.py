# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:08:25 2022

@author: Badari


from pyqtgraph import PlotWidget, ViewBox, mkPen
self.ImpdPlot = PlotWidget(self.centralwidget,viewBox=ViewBox(border = mkPen(color='k',width = 2)))
self.ImpdPlot.setBackground((255,182,193,25))
"""
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from dielectric import Ui_ImpedanceApp
from pyqtgraph import PlotWidget, ViewBox, mkPen, intColor
from numpy import loadtxt
from templist import Ui_Form
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from utilities import IdleWorker, FakeImpd, FrequencySweepWorker
from time import sleep

class mainControl(QtWidgets.QMainWindow,Ui_ImpedanceApp):
    """The Impedance program module."""

    def __init__(self, *args, obj=None, **kwargs):
        super(mainControl, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.fixFreq.clicked.connect(self.freqOption)
        self.fixTemp.clicked.connect(self.tempOption)
        self.fixDCvolts.clicked.connect(self.DCvoltOption)
        self.traceback.clicked.connect(self.setVoltageCycles)
        self.startButton.clicked.connect(self.startProgram)
        self.stopButton.clicked.connect(self.stopProgram)
        self.loadTempButton.clicked.connect(self.loadTemperatures)
        self.fixedFreq.valueChanged.connect(self.updateFixedFrequency)
        self.fixedFreqUnit.currentIndexChanged.connect(self.updateFixedFrequency)
        self.fixedTemp.valueChanged.connect(self.updateFixedTemperature)
        self.fixedACvolt.valueChanged.connect(self.updateACVoltage)
        self.fixedDCvolt.valueChanged.connect(self.updateFixedDCVoltage)
        self.actionExit.triggered.connect(self.close)
        self.measureMode.currentIndexChanged.connect(self.measureModeSet)
        self.measureModeSet()
        self.show()
        self.temperatures = []
        self.freqsweep = True
        self.lastfreqstate = 'sweep'
        self.impd = FakeImpd()
        self.stopButton.setEnabled(False)
        self.continuousDisplay()
        """ Display list of custom temperatures, which can be edited
        self.Form = QtWidgets.QWidget()
        self.temptable = Ui_Form()
        self.temptable.setupUi(self.Form)
        self.loadTempButton.clicked.connect(self.showTempTable)
        # TODO: Make a default temperature table, and load it in the beginning.
        """
    
    def updateFixedDCVoltage(self):
        self.impd.Vdc = self.fixedDCvolt.value()
        self.DCvoltStatus.setText("{} V".format(round(self.impd.Vdc,3)))
        
    def updateACVoltage(self):
        self.impd.Vac = self.fixedACvolt.value()
        self.ACvoltStatus.setText("{} V".format(round(self.impd.Vac,3)))
        
    def updateFixedTemperature(self):
        self.impd.temperature = self.fixedTemp.value()
        # TODO: change it to actual temperature (currently showing set temperature)
        self.tempStatus.setText("{}".format(round(self.impd.temperature,2)))
        
    def updateFixedFrequency(self):
        multiply = 1
        if self.fixedFreqUnit.currentIndex() == 0:
            self.fixedFreq.setMinimum(20)
        elif self.fixedFreqUnit.currentIndex() == 1:
            self.fixedFreq.setMinimum(0)
            multiply = 1000
        elif self.fixedFreqUnit.currentIndex() == 2:
            self.fixedFreq.setMinimum(0)
            multiply = 1000000
        self.impd._freq = self.fixedFreq.value()*multiply
        self.fixedFreq.setMaximum(10000000/multiply)
        self.impd.getFreqUnit()
        self.freqStatus.setText("{0} {1}".format(self.impd.freq, self.impd.freqUnit))
    
    
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
        if self.fixTemp.isChecked() == True:
            self.fixedTemp.setEnabled(True)
            self.startTemp.setEnabled(False)
            self.stopTemp.setEnabled(False)
            self.measureMode.setEnabled(False)
            self.tempInterval.setEnabled(False)
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            #self.frame.hide()
            self.loadTempButton.setEnabled(False)
            #self.loadTempButton.hide()
        else:
            self.fixedTemp.setEnabled(False)
            self.startTemp.setEnabled(True)
            self.stopTemp.setEnabled(True)
            self.measureMode.setEnabled(True)
            self.measureModeSet()
    
    def measureModeSet(self):
        if self.measureMode.currentIndex() == 0:
            self.tempInterval.setEnabled(False)
            #self.frame.hide()
            self.loadTempButton.setEnabled(False)
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            #self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 1:
            #self.frame.show()
            self.measureLabel.setEnabled(True)
            self.tempInterval.setEnabled(True)
            self.degreesLabel.setEnabled(True)
            self.loadTempButton.setEnabled(False)
            #self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 2:
            self.tempInterval.setEnabled(False)
            #self.frame.hide()
            #self.loadTempButton.show()
            self.measureLabel.setEnabled(False)
            self.degreesLabel.setEnabled(False)
            self.loadTempButton.setEnabled(True)
    
    def DCvoltOption(self):
        if self.fixDCvolts.isChecked() == True:
            if self.lastfreqstate == 'sweep':
                self.fixFreq.setChecked(False)
                self.freqOption()
            self.fixedDCvolt.setEnabled(True)
            self.startVoltageLabel.setEnabled(False)
            self.startVoltage.setEnabled(False)
            self.stopVoltageLabel.setEnabled(False)
            self.stopVoltage.setEnabled(False)
            self.voltagePointsLabel.setEnabled(False)
            self.voltageNpoints.setEnabled(False)
            self.traceback.setEnabled(False)
        else:
            if not self.fixFreq.isChecked():
                self.lastfreqstate = 'sweep'
                self.fixFreq.setChecked(True)
                self.freqOption()
            else:
                self.lastfreqstate = 'fix'
            self.fixedDCvolt.setEnabled(False)
            self.startVoltageLabel.setEnabled(True)
            self.startVoltage.setEnabled(True)
            self.stopVoltageLabel.setEnabled(True)
            self.stopVoltage.setEnabled(True)
            self.voltagePointsLabel.setEnabled(True)
            self.voltageNpoints.setEnabled(True)
            self.traceback.setEnabled(True)
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
        self.startIdleThread()
        self.showControllerStatus()
        
    def startIdleThread(self):
        self.idlethread = QThread()
        self.idleWorker = IdleWorker(self.impd)
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
        if self.impd.temperature != 'NA':
            self.tempStatus.setText("{} K".format(self.impd.temperature))
        else:
            self.tempStatus.setText("{}".format(self.impd.temperature))
        self.ACvoltStatus.setText("{} V".format(self.impd.Vac))
        self.DCvoltStatus.setText("{} V".format(self.impd.Vdc))
        
    def showStatus(self, data):
        self.ZReStatus.setText("{} Ω".format(data[0]))
        self.ZImStatus.setText("{}".format(data[1]))
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
    
    def startProgram(self):
        #print(self.temptable.model._data)
        self.idleWorker.stopcall.emit()
        self.statusBox.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        if not self.fixFreq.isChecked():
            self.startFreqSweepThread()
    
    def startFreqSweepThread(self):
        self.freqthread = QThread()
        sf = self.startFreq.value()
        su = self.startFreqUnit.currentIndex()
        ef = self.stopFreq.value()
        eu = self.stopFreqUnit.currentIndex()
        np = self.npoints.value()
        sp = self.spacingType.currentIndex()
        self.fSweepWorker = FrequencySweepWorker(self.impd,sf,su,ef,eu,np,sp)
        self.fSweepWorker.moveToThread(self.freqthread)
        self.freqthread.started.connect(self.fSweepWorker.start_frequency_sweep)
        self.fSweepWorker.finished.connect(self.finishAction)
        self.fSweepWorker.finished.connect(self.freqthread.quit)
        self.fSweepWorker.finished.connect(self.fSweepWorker.deleteLater)
        self.freqthread.finished.connect(self.freqthread.deleteLater)
        self.fSweepWorker.data.connect(self.plotFsweepData)
        #self.thread.finished.connect(self.finishAction)
        self.freqthread.start()
    
    def plotFsweepData(self,data):
        print(len(data[0]),len(data[1]))
        
    def finishAction(self):
        self.stopProgram()
        
    def stopProgram(self):
        self.startIdleThread()
        self.showControllerStatus()
        self.statusBox.setEnabled(True)
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
    
    def closeEvent(self, event):
        self.idleWorker.stopcall.emit()
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Confirm Exit',
                                           quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            # TODO: Close all instrument connections
            event.accept()
        else:
            event.ignore()
            self.startIdleThread()
            self.showControllerStatus()
            
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = mainControl()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()