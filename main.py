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

class mainControl(QtWidgets.QMainWindow,Ui_ImpedanceApp):
    """The Impedance program module."""

    def __init__(self, *args, obj=None, **kwargs):
        super(mainControl, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.fixFreq.clicked.connect(self.freqOption)
        self.fixTemp.clicked.connect(self.tempOption)
        self.measureMode.currentIndexChanged.connect(self.measureModeSet)
        self.measureModeSet()
        
        self.show()
    
    def freqOption(self):
        if self.fixFreq.isChecked() == True:
            self.fixedFreq.setEnabled(True)
            self.fixedFreqUnit.setEnabled(True)
            self.startFreq.setEnabled(False)
            self.startFreqUnit.setEnabled(False)
            self.stopFreq.setEnabled(False)
            self.stopFreqUnit.setEnabled(False)
            self.npoints.setEnabled(False)
            self.spacingType.setEnabled(False)
        else:
            self.fixedFreq.setEnabled(False)
            self.fixedFreqUnit.setEnabled(False)
            self.startFreq.setEnabled(True)
            self.startFreqUnit.setEnabled(True)
            self.stopFreq.setEnabled(True)
            self.stopFreqUnit.setEnabled(True)
            self.npoints.setEnabled(True)
            self.spacingType.setEnabled(True)
    
    def tempOption(self):
        if self.fixTemp.isChecked() == True:
            self.fixedTemp.setEnabled(True)
            self.startTemp.setEnabled(False)
            self.stopTemp.setEnabled(False)
            self.measureMode.setEnabled(False)
            self.tempInterval.setEnabled(False)
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
            #self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 1:
            #self.frame.show()
            self.tempInterval.setEnabled(True)
            self.loadTempButton.setEnabled(False)
            #self.loadTempButton.hide()
        elif self.measureMode.currentIndex() == 2:
            self.tempInterval.setEnabled(False)
            #self.frame.hide()
            #self.loadTempButton.show()
            self.loadTempButton.setEnabled(True)
            

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = mainControl()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()