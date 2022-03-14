# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:07:55 2022

@author: Badari
"""
from datetime import datetime
from os.path import abspath, join, exists
from pyvisa import ResourceManager, VisaIOError
from os import makedirs
from copy import copy
from re import sub
from PyQt5.QtCore import QObject, QTimer, QEventLoop, pyqtSignal
from PyQt5.QtWidgets import QTimeEdit, QSpinBox
from math import log10
from numpy import logspace, linspace, diff
from time import sleep
from PyQt5.QtWidgets import QMessageBox
from E4990A import KeysightE44990A
from random import randint, uniform
from time import sleep
from PyQt5.QtCore import pyqtSignal
#from keithley195 import Keithley195
#from advantestTR6845 import AdvantestTR6845

class FakeAdapter():
    """Provides a fake adapter for debugging purposes.

    Bounces back the command so that arbitrary values testing is possible.

    Note: Adopted from Pymeasure package

    .. code-block:: python

        a = FakeAdapter()
        assert a.read() == ""
        a.write("5")
        assert a.read() == "5"
        assert a.read() == ""
        assert a.ask("10") == "10"
        assert a.values("10") == [10]

    """

    _buffer = ""

    def __init__(self, freq = 1000, Vac = 0.1, Vdc = 0, temp = 'NA'):
        self.address = ''
        self.ID = 'Fake'
        self._freq = freq
        self.getFreqUnit()
        self.Vac = Vac
        self.Vdc = Vdc
        self.temperature = temp

    def getFreqUnit(self):
        if 20 <= self._freq < 1000:
            self.freqUnit = 'Hz'
            self.freq = self._freq
        elif 1000 <= self._freq < 1000000:
            self.freqUnit = 'kHz'
            self.freq = self._freq/1000
        elif self._freq >= 1000000:
            self.freqUnit = 'MHz'
            self.freq = self._freq/1000000

    def read(self):
        """Return last commands given after the last read call."""
        result = copy(self._buffer)
        # Reset the buffer
        self._buffer = ""
        return result

    def write(self, command):
        """Write the command to a buffer, so that it can be read back."""
        self._buffer += command

    def __repr__(self):
        """Return the class name as a string."""
        return "<FakeAdapter>"

    def __getattr__(self,name):  
        """If any undefined method is called, do nothing."""
        def method(*args):
            pass
        return method
    
    def get_current_values(self):
        z = randint(1000,10000)
        p = randint(1,100)
        c = uniform(1e-7,1e-12)
        d = uniform(0,1)
        sleep(0.2)
        return z,p,c,d
        # now emit it to the GUI
    
    def update_frequency(self, freq):
        self._freq = freq
        self.getFreqUnit()
    
    def update_temperature(self, temp):
        self.temperature = temp
    
    def update_Vac(self, Vac):
        self.Vac = Vac
    
    def update_Vdc(self, Vdc):
        self.Vdc = Vdc
        
def connectDevice(inst,addr,test = False):
    try:
        return inst(addr), 1
    except VisaIOError:
        if test == True:
            return FakeAdapter(), 0
        else:
            msg = QMessageBox()
            title = "No Instrument connected"
            text = "Cannot find required instruments. Check connections again and restart program."
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setWindowTitle(title)
            msg.setText(text)
            msg.exec()
            return 0,0

def checkInstrument(E4990Addr = None, k2700Addr = None, K195Addr = None, TR6845Addr = None, 
                    test = False):
    """
    Obtain instrument address of K2450, K2700 and function generator.

    Returns: list of instrument objects
    -------
    Instrument objects pointing to K2450, K2700 and AFG1022
    if test is True,
        return FakeAdapter if any instrument is not found
    else exit program
    """
    deviceAddr = [E4990Addr,k2700Addr,K195Addr, TR6845Addr]
    rm = ResourceManager()
    E4990Status = k2700Status = K195Status = TR6845Status = 0
    if E4990Addr:
        E4990, E4990Status = connectDevice(KeysightE44990A,E4990Addr,test=True)
    if k2700Addr:
        k2700, k2700Status = connectDevice(Keithley2700,k2700Addr,test=True)
    if K195Addr:
        K195, K195Status = connectDevice(Keithley195,K195Addr,test=True)
    if TR6845Addr:
        TR6845, TR6845Status = connectDevice(AdvantestTR6845,TR6845Addr,test=True)
    status = [E4990Status,k2700Status,K195Status, TR6845Addr]
    deviceInfo = [['Agilent Technologies','E4990A'],['KEITHLEY','2700'],['NDCV',''],['','']]
    notConnected = [x for x,y in enumerate(status) if y == 0]
    if notConnected:
        instList = rm.list_resources()
        for inst in instList:
            for deviceNo in notConnected:
                try:
                    myInst = rm.open_resource(inst)
                    instID = myInst.query('*IDN?').split(',')
                    if deviceInfo[deviceNo][0] in instID[0] and deviceInfo[deviceNo][1] in instID[1]:
                        deviceAddr[deviceNo] = inst
                        notConnected.remove(deviceNo)
                        break
                except VisaIOError:
                    pass
        E4990Addr = deviceAddr[0]
        k2700Addr = deviceAddr[1]
        K195Addr = deviceAddr[3]
        TR6845Addr = deviceAddr[4]
        if E4990Status == 0:
            E4990,_ = connectDevice(KeysightE44990A,E4990Addr,test)
            if _ == 0 and test == False:
                return 0,0,0,0
        if k2700Status == 0:
            k2700,_ = connectDevice(Keithley2700,k2700Addr,test)
            if _ == 0 and test == False:
                return 0,0,0,0
        if K195Status == 0:
            K195,_ = connectDevice(Keithley195,K195Addr,test)
            if _ == 0 and test == False:
                return 0,0,0,0
        if TR6845Status == 0:
            TR6845,_ = connectDevice(AdvantestTR6845,TR6845Addr,test)
            if _ == 0 and test == False:
                return 0,0,0,0
    if k2700.ID != 'Fake':
        k2700.write('DISPLAY:TEXT:STATE ON')
        k2700.write('DISPLAY:TEXT:DATA "KEYSIGHT USE"')
    return E4990, k2700, K195, TR6845

class IdleWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)
    stopcall = pyqtSignal()
    
    def __init__(self, impd = None):
        super(IdleWorker,self).__init__()
        self.impd = impd
        self.stopCall = False
        self.stopcall.connect(self.stopcalled)
    
    def stopcalled(self):
        self.stopCall = True
    
    def get_status(self):
        z, p, c, d = self.impd.get_current_values()
        self.data.emit([z,p,c,d])
    
    def start(self):
        while True:
            self.get_status()
            if self.stopCall == True:
                break
        self.finished.emit()