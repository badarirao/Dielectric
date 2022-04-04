# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:07:55 2022

@author: Badari
"""
from datetime import datetime
from os.path import abspath, join, exists
from pyvisa import ResourceManager, VisaIOError
from os import makedirs
import os
from smtplib import SMTP
from email.message import EmailMessage
from copy import copy
from re import sub
from PyQt5.QtCore import QObject, pyqtSignal
from math import log10
from numpy import logspace, linspace, array, append, concatenate
from time import sleep, time
from PyQt5.QtWidgets import QMessageBox
from E4990A import KeysightE44990A
from random import randint, uniform
from math import ceil
from chino import ChinoKP1000C
import requests
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

    def __init__(self):
        self.address = ''
        self.ID = 'Fake'

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

    def __getattr__(self, name):
        """If any undefined method is called, do nothing."""
        def method(*args):
            pass
        return method

class FakeTempController(FakeAdapter):
    """Provides a fake Temperature controler for debugging purposes.

    Bounces back the command so that arbitrary values testing is possible.

    """
    def __init__(self, temp=300):
        super().__init__()
        self._temp = temp
        self.startT = 300
        self.stopT = 10
        self.rate = -1 # degreee per minute
        self.mode = 0
        self.tCount = 0
        self.traceback = False
        self.interval = 1
        self.stabilizationTime = 10 # 10 minutes
    
    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, value):
        if self._temp != value:
            self._temp = value
    
    def rampT(self):
        fsweeptime = 1 # time taken for 1 cycle of frequency sweep in minutes, need to be calculated later
        total_time = abs((self.startT-self.stopT)/self.rate) # minutes
        tpoints = int(total_time/fsweeptime)
        self.templist = linspace(self.startT,self.stopT,tpoints+1)
        if self.traceback == True:
            templist2 = linspace(self.stopT,self.startT,tpoints+1)
            self.templist = concatenate((self.templist,templist2))
    
    def isRunning(self):
        if self.tCount >= len(self.templist):
            return False
        self.temp = self.templist[self.tCount]
        if self.tCount > 0:
            self.tCount += 1
        return True
    
class FakeImpd(FakeAdapter):
    """Provides a fake Impedance analyzer for debugging purposes.

    Bounces back the command so that arbitrary values testing is possible.

    """

    def __init__(self, freq=1000, Vac=0.1, Vdc=0):
        super().__init__()
        self._freq = freq
        self.getFreqUnit()
        self.Vac = Vac
        self.Vdc = Vdc
        self.sweepCount = 0
        self.startf = 20
        self.endf = 1e7
        self.npointsf = 50
        self.sweeptypef = 1
        self.dcStart = -1
        self.dcStop = 1
        self.dcPoints = 21
        self.dcTraceback = 0 
        self.dcNcycles = 1
        self.stopCall = False

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

    def get_current_values(self):
        z = randint(1000, 10000)
        p = randint(1, 100)
        c = uniform(1e-7, 1e-12)
        d = uniform(0, 1)
        sleep(0.2)
        return z, p, c, d
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
    
    def get_absolute_frequency(self, freq, units):
        if units == 0: # Hz
            return freq
        elif units == 1: # kHz
            return freq*1e3
        elif units == 2: # MHz
            return freq*1e6
        
    def wait_to_complete(self,counts=10):
        sweepCount = 0
        self.stopCall = False
        while sweepCount <= counts :
            sweepCount += 1
            if self.stopCall == True:
                self.abort()
                break
            sleep(0.1)
    
    def start_fSweep(self):
        self.scannedFrequencies = get_frequencies_list(self.startf, self.endf, self.npointsf, self.sweeptypef)
        self.zArray = []
        self.pArray = []
        self.cArray = []
        self.dArray = []
        for i in range(len(self.scannedFrequencies)):
            z = randint(1000, 10000)
            p = randint(1, 100)
            c = uniform(1e-7, 1e-12)
            d = uniform(0, 1)
            self.zArray.append(z)
            self.pArray.append(p)
            self.cArray.append(c)
            self.dArray.append(d)
    
    def start_dcSweep(self,i=0):
        self.scannedDCvs = linspace(self.dcStart,self.dcStop,self.dcPoints)
        self.zArray = []
        self.pArray = []
        self.cArray = []
        self.dArray = []
        for i in range(len(self.scannedDCvs)):
            z = randint(1000, 10000)
            p = randint(1, 100)
            c = uniform(1e-7, 1e-12)
            d = uniform(0, 1)
            self.zArray.append(z)
            self.pArray.append(p)
            self.cArray.append(c)
            self.dArray.append(d)
    
    def read_measurement_data(self):
        return [self.zArray,self.pArray,self.cArray,self.dArray]
    
    def get_frequencies(self):
        return self.scannedFrequencies
    
    def get_xVals(self):
        return list(self.scannedDCvs)

def get_linlog_segment_list(start, end, npoints):
    if start < 20:
        start = 20
    if end > 1e7:
        end = 1e7
    if npoints < 2:
        npoints = 2
    if npoints > 1601:
        npoints = 1601
    min_order = int(log10(start))
    max_order = int(log10(end))
    lin_ranges = logspace(min_order, max_order, (max_order-min_order)+1)
    lin_ranges[0] = start
    if lin_ranges[-1] != end:
        lin_ranges = append(lin_ranges, end)
    points_per_order = array([0 for i in range(len(lin_ranges)-1)])
    npoints = round(npoints/9)*9
    oneFactor = len(lin_ranges)*9
    n = npoints+(9*len(lin_ranges))+1
    i = 1
    while n > npoints+(9*len(lin_ranges)):
        mFactor = round(npoints/(9*i))
        n = mFactor*oneFactor
        i += 1
    if n == 0:
        npoints = len(lin_ranges)*9
    else:
        npoints = n
    p = ceil(npoints/len(lin_ranges))
    points_per_order[0] = ceil(
        (lin_ranges[1]-lin_ranges[0])/lin_ranges[1]*9)*mFactor
    points_per_order[-1] = int((lin_ranges[-1] -
                               lin_ranges[-2])/(lin_ranges[-2]*9)*9)*mFactor
    points_per_order[1:-1] = p
    npoints = sum(points_per_order)+1
    segments = []
    for i in range(len(lin_ranges[:-1])):
        frequencies = linspace(lin_ranges[i], lin_ranges[i+1], points_per_order[i]+1, endpoint=True)
        if i == 0:
            segments.append([frequencies[0],frequencies[-1],points_per_order[i]+1])
        else:
            segments.append([frequencies[1],frequencies[-1],points_per_order[i]])
    return segments

def connectDevice(inst, addr, test=False):
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
            return 0, 0


def checkInstrument(E4990Addr=None, k2700Addr=None, K195Addr=None, TR6845Addr=None, TControlAddr = None, test=False):
    impd = None
    mux = None
    k195 = None
    Adv = None
    Tcont = None
    if E4990Addr:
        try:
            impd = KeysightE44990A(E4990Addr)
        except:
            impd = FakeImpd()
    else:
        impd = FakeImpd()
    if TControlAddr:
        try:
            Tcont = ChinoKP1000C(TControlAddr)
        except:
            Tcont = FakeTempController()
    else:
        Tcont = FakeTempController()
    return impd, mux, k195, Adv, Tcont
    """
    Obtain instrument address of K2450, K2700 and function generator.

    Returns: list of instrument objects
    -------
    Instrument objects pointing to K2450, K2700 and AFG1022
    if test is True,
        return FakeAdapter if any instrument is not found
    else exit program
    """
    
    """
    deviceAddr = [E4990Addr, k2700Addr, K195Addr, TR6845Addr]
    rm = ResourceManager()
    E4990Status = k2700Status = K195Status = TR6845Status = 0
    if E4990Addr:
        E4990, E4990Status = connectDevice(
            KeysightE44990A, E4990Addr, test=True)
    if k2700Addr:
        k2700, k2700Status = connectDevice(Keithley2700, k2700Addr, test=True)
    if K195Addr:
        K195, K195Status = connectDevice(Keithley195, K195Addr, test=True)
    if TR6845Addr:
        TR6845, TR6845Status = connectDevice(
            AdvantestTR6845, TR6845Addr, test=True)
    status = [E4990Status, k2700Status, K195Status, TR6845Addr]
    deviceInfo = [['Agilent Technologies', 'E4990A'],
                  ['KEITHLEY', '2700'], ['NDCV', ''], ['', '']]
    notConnected = [x for x, y in enumerate(status) if y == 0]
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
            E4990, _ = connectDevice(KeysightE44990A, E4990Addr, test)
            if _ == 0 and test == False:
                return 0, 0, 0, 0
        if k2700Status == 0:
            k2700, _ = connectDevice(Keithley2700, k2700Addr, test)
            if _ == 0 and test == False:
                return 0, 0, 0, 0
        if K195Status == 0:
            K195, _ = connectDevice(Keithley195, K195Addr, test)
            if _ == 0 and test == False:
                return 0, 0, 0, 0
        if TR6845Status == 0:
            TR6845, _ = connectDevice(AdvantestTR6845, TR6845Addr, test)
            if _ == 0 and test == False:
                return 0, 0, 0, 0
    if k2700.ID != 'Fake':
        k2700.write('DISPLAY:TEXT:STATE ON')
        k2700.write('DISPLAY:TEXT:DATA "KEYSIGHT USE"')
    """


class IdleWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)
    stopcall = pyqtSignal()

    def __init__(self, impd=None, TCont=None):
        super().__init__()
        self.impd = impd
        self.TCont = TCont
        self.stopCall = False
        self.stopcall.connect(self.stopcalled)
        self.impd.setMeasurementSpeed(4)

    def stopcalled(self):
        self.stopCall = True

    def get_status(self):
        if self.initFreq != self.impd._freq:
            sleep(0.1)
            self.change_frequency()
            self.initFreq = self.impd._freq
        z, p, c, d = self.impd.get_current_values()
        self.TCont.real_data_request()
        t = self.TCont.temp
        self.data.emit([z, p, c, d, t])
        sleep(0.5)

    
    def initialize(self): # initialize frequency, AC voltage, DC voltage
        self.impd.write(":INIT1:CONT ON")
        self.impd.write(":SENS1:SWE:TYPE LIN")
        self.impd.write(":SENS1:SWE:POIN 2") # set number of points
        self.impd.write(":SENS1:FREQ:STAR {}".format(self.impd._freq)) # set start frequency
        self.impd.write(":SENS1:FREQ:STOP 1e7") # set stop frequency as 10 MHz
        self.impd.write(":SOUR1:MODE VOLT")  # Set oscillation mode 
        self.impd.write(":SOUR1:VOLT {}".format(self.impd.Vac)) # Set Oscillation level
        if self.impd.Vdc:
            if not self.impd.is_BIAS_ON():
                self.impd.enable_DC_Bias(True)
            self.impd.setVdc()
        self.impd.write(":SOUR1:ALC ON") # Turn on Auto Level Control
        #self.display_off()
        self.impd.trig_from_internal()
        
    def change_frequency(self):
        self.impd.write(":SENS1:FREQ:STAR {}".format(self.impd._freq)) # set start frequency
        self.impd.write(":SENS1:FREQ:STOP 1e7") # set stop frequency as 10 MHz
    
    def start(self):
        self.impd.disable_display_update() # disable display update
        self.impd.display_off()
        self.initialize()
        self.stopCall = False
        self.initFreq = self.impd._freq
        while True:
            if self.stopCall == True:
                break
            self.get_status()
        self.impd.enable_display_update()
        self.finished.emit()

class FrequencySweepWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)
    stopcall = pyqtSignal()
    showStatus = pyqtSignal(str)

    def __init__(self, impd=None, TCont=None, user = None, settingPath = None):
        super().__init__()
        self.impd = impd
        self.TCont = TCont
        self.user = user
        self.start = self.impd.startf
        self.stop = self.impd.endf
        self.npoints = self.impd.npointsf
        self.spacing = self.impd.sweeptypef
        self.settingPath = settingPath
        self.senderemail, self.password, self.server, self.subject = initializeEmail(self.settingPath)
        if self.impd == None:
            self.impd = FakeImpd()
        self.stopCall = False
        self.stopcall.connect(self.stopcalled)
        self.impd.setMeasurementSpeed(2)

    def stopcalled(self):
        self.stopCall = True

    def start_frequency_sweep(self):
        sleep(0.1)
        self.impd.trig_from_PC()
        self.impd.continuous_measurement()
        if self.spacing == 0:   # set sweep type
            self.impd.write(":SENS1:SWE:TYPE LIN")
        elif self.spacing == 1:
            self.impd.write(":SENS1:SWE:TYPE LOG") 
        elif self.spacing == 2:
            self.impd.write(":SENS1:SWE:POIN 1500")
            segments = get_linlog_segment_list(self.start, self.stop, self.npoints)
            Segments = []
            self.impd.write(":SENS1:SWE:TYPE SEGM")
            if self.impd.Vdc:
                bias = 1
            else:
                bias = 0
            segmentFormat =  "7,0,1,{0},0,0,0,0,{1}".format(bias,len(segments))
            for seg in segments:
                seg.extend(["0","{}".format(self.impd.Vac)])
                if bias:
                    seg.extend([",0","{}".format(self.impd.Vdc)])
                Segments.append(','.join([str(s) for s in seg]))
            segCommand = segmentFormat
            for seg in Segments:
                segCommand += ',' + seg
            self.impd.write(":SENS1:SEGM:DATA {}".format(segCommand))
        if self.spacing != 2:
            self.impd.write(":SENS1:SWE:POIN {}".format(self.npoints+1)) # set number of points
            self.impd.write(":SENS1:FREQ:STAR {}".format(self.start)) # set start frequency
            self.impd.write(":SENS1:FREQ:STOP {}".format(self.stop)) # set stop frequency
            self.impd.write(":SOUR1:MODE VOLT")  # Set oscillation mode 
            self.impd.write(":SOUR1:VOLT {}".format(self.impd.Vac)) # Set Oscillation level
            if self.impd.Vdc:
                if not self.impd.is_BIAS_ON():
                    self.impd.enable_DC_Bias(True)
                self.impd.setVdc()
        self.impd.write(":SOUR1:ALC ON") # Turn on Auto Level Control
        self.impd.display_on()
        self.impd.enable_display_update()
        self.impd.setYAutoScale()
        self.showStatus.emit("Started frequency sweep, please wait..")
        startTime = time()
        sweepInitialTemperature = self.TCont.temp
        self.impd.start_fSweep()
        self.impd.wait_to_complete()
        sweepFinalTemperature = self.TCont.temp
        endTime = time()
        averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
        deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
        measuredData = self.impd.read_measurement_data()
        frequencyData = [self.impd.get_frequencies()]
        timeTaken = [round(endTime-startTime,3)]
        wholedata = timeTaken + frequencyData + measuredData + [averageTemperature] + [deltaT]
        self.showStatus.emit("Frequency sweep complete. Data saved.")
        self.data.emit(wholedata)
        self.finished.emit()
        
class DCSweepWorker(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)
    stopcall = pyqtSignal()
    showStatus = pyqtSignal(str)

    def __init__(self, impd=None, TCont=None, user = None, settingPath = None):
        super().__init__()
        self.impd = impd
        self.TCont = TCont
        self.user = user
        self.start = self.impd.dcStart
        self.stop = self.impd.dcStop
        self.npoints = self.impd.dcPoints
        self.traceback = self.impd.dcTraceback
        self.ncycles = self.impd.dcNcycles
        self.settingPath = settingPath
        self.senderemail, self.password, self.server, self.subject = initializeEmail(self.settingPath)
        if self.impd == None:
            self.impd = FakeImpd()
        self.stopCall = False
        self.stopcall.connect(self.stopcalled)
        self.impd.setMeasurementSpeed(2)

    def stopcalled(self):
        self.stopCall = True

    def start_dc_sweep(self):
        sleep(0.1)
        self.impd.trig_from_PC()
        self.impd.continuous_measurement()
        # set DC bias range to 1mA
        # toggle DC bias constant to off
        # set max and min dc bias voltage range
        # you can set delay after DC bias is applied
        self.impd.write(":SENS1:SWE:POIN {}".format(self.npoints+1)) # set number of points
        self.impd.write(":SOURce1:BIAS:VOLTage:STARt {}".format(self.start)) # set start DC voltage
        self.impd.write(":SOURce1:BIAS:VOLTage:STOP {}".format(self.stop)) # set stop DC voltage
        self.impd.write(":SOUR1:MODE VOLT")  # Set oscillation mode 
        self.impd.write(":SOUR1:VOLT {}".format(self.impd.Vac)) # Set Oscillation level
        self.impd.write(":SENS1:SWE:TYPE BIAS")
        self.impd.write(":SOUR1:ALC ON") # Turn on Auto Level Control
        self.impd.display_on()
        self.impd.enable_display_update()
        self.impd.setYAutoScale()
        self.showStatus.emit("Started DC bias sweep, please wait..")
        startTime = time()
        sweepInitialTemperature = self.TCont.temp
        i = 0
        measuredData = [[],[],[],[]]
        dcBiasData = []
        while True:
            self.impd.start_dcSweep(i)
            self.impd.wait_to_complete()
            newdata = self.impd.read_measurement_data()
            for j in range(len(measuredData)):
                measuredData[j].extend(newdata[j])
            xVal = self.impd.get_xVals()
            if i%2 != 0:
                xVal.reverse()
            dcBiasData.extend(xVal)
            if not self.traceback:
                break
            if int((i+1)/2) >= self.ncycles:
                break
            timeTaken = round(time()-startTime,3)
            oneSweepData = [timeTaken] + [dcBiasData] + measuredData
            self.data.emit(oneSweepData)
            i += 1
        sweepFinalTemperature = self.TCont.temp
        endTime = time()
        timeTaken = round(endTime-startTime,3)
        averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
        deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
        wholedata = [timeTaken] + [dcBiasData] + measuredData + [averageTemperature] + [deltaT]
        self.showStatus.emit("DC bias sweep complete. Data saved.")
        self.data.emit(wholedata)
        self.finished.emit()

class TemperatureSweepWorkerF(QObject):
    finished = pyqtSignal()
    data = pyqtSignal(list)
    freqSig = pyqtSignal(list)
    stopcall = pyqtSignal()
    showStatus = pyqtSignal(str)

    def __init__(self, impd=None, TCont = None, user = None, settingPath=None):
        super().__init__()
        self.impd = impd
        self.TCont = TCont
        self.user = user
        self.settingPath = settingPath
        self.senderemail, self.password, self.server, self.subject = initializeEmail(self.settingPath)
        if self.impd == None:
            self.impd = FakeImpd()
        if self.TCont == None:
            self.TCont = FakeTempController()
        self.start = self.impd.startf
        self.end = self.impd.endf
        self.npoints = self.impd.npointsf
        self.spacing = self.impd.sweeptypef
        self.stopCall = False
        self.stopcall.connect(self.stopcalled)
        self.impd.setMeasurementSpeed(2)

    def stopcalled(self):
        self.stopCall = True
        self.impd.stopCall = True

    def start_temperature_sweep(self):
        self.TCont.temp = self.TCont.startT
        # wait till present temperature reaches start temperature
        while abs(self.TCont.temp-self.TCont.startT) > 1:
            self.showStatus.emit("Waiting to reach {} K".format(self.TCont.startT))
            while abs(self.TCont.temp-self.TCont.startT) > 2:
                if self.stopCall == True:
                    self.TCont.reset()
                    self.showStatus.emit("Temperature sweep aborted before start.")
                    self.finished.emit()
                    return
                sleep(2)
            self.showStatus.emit("Stabilizing at {} K".format(self.TCont.startT))
            count = 0
            # wait to stabilize at the start temperature
            waitCount = self.TCont.stabilizationTime*60/2
            while count < waitCount: # write 300 to make wait time as 10 minutes
                if self.stopCall == True:
                    self.TCont.reset()
                    self.showStatus.emit("Temperature sweep aborted before start.")
                    self.finished.emit()
                    return
                count += 1
                sleep(2)
        self.showStatus.emit("Measuring..")
        self.impd.write(":INIT1:CONT ON")
        self.impd.trig_from_PC()
        if self.spacing == 0:   # set sweep type
            self.impd.write(":SENS1:SWE:TYPE LIN")
        elif self.spacing == 1:
            self.impd.write(":SENS1:SWE:TYPE LOG") 
        elif self.spacing == 2:
            segments = get_linlog_segment_list(self.impd.startf, self.impd.endf, self.impd.npointsf)
            Segments = []
            self.impd.write(":SENS1:SWE:TYPE SEGM")
            if self.impd.Vdc:
                bias = 1
            else:
                bias = 0
            segmentFormat =  "7,0,1,{0},0,0,0,0,{1}".format(bias,len(segments))
            for seg in segments:
                seg.extend(["0","{}".format(self.impd.Vac)])
                if bias:
                    seg.extend([",0","{}".format(self.impd.Vdc)])
                Segments.append(','.join([str(s) for s in seg]))
            segCommand = segmentFormat
            for seg in Segments:
                segCommand += ',' + seg
            self.impd.write(":SENS1:SEGM:DATA {}".format(segCommand)) 
        if self.spacing != 2:
            self.impd.write(":SENS1:SWE:POIN {}".format(self.impd.npointsf+1)) # set number of points
            self.impd.write(":SENS1:FREQ:STAR {}".format(self.impd.startf)) # set start frequency
            self.impd.write(":SENS1:FREQ:STOP {}".format(self.impd.endf)) # set stop frequency
            self.impd.write(":SOUR1:MODE VOLT")  # Set oscillation mode 
            self.impd.write(":SOUR1:VOLT {}".format(self.impd.Vac)) # Set Oscillation level
            if self.impd.Vdc:
                if not self.impd.is_BIAS_ON():
                    self.impd.enable_DC_Bias(True)
                self.impd.setVdc()
        self.impd.write(":SOUR1:ALC ON") # Turn on Auto Level Control
        self.impd.display_on()
        self.impd.write(":DISPlay:WINDow1:TRACe1:Y:AUTO")
        if self.TCont.mode == 1:
            npoints = abs(int((self.TCont.startT-self.TCont.stopT)/self.TCont.interval))
            TempList = linspace(self.TCont.startT,self.TCont.stopT,npoints+1,dtype=int)
            if self.TCont.traceback == True:
                TempList2 = linspace(self.TCont.stopT,self.TCont.startT,npoints+1,dtype=int)
                TempList = concatenate((TempList,TempList2))
            TempList = concatenate((TempList,[TempList[-1]]))
            tcount = 0
        message = "Started temperature sweep from {}K".format(self.TCont.temp)
        sendMessage(self.senderemail,
                    self.password,
                    self.server,
                    self.user,
                    self.subject,
                    message)
        startTime = time()
        if self.TCont.mode in (0,1):
            self.TCont.rampT()
            self.TCont.tCount = 0 # required for Fake temperature controller
            while self.TCont.isRunning():
                sweepInitialTemperature = self.TCont.temp
                if self.TCont.mode == 0:
                    self.impd.start_fSweep()
                    self.impd.wait_to_complete()
                    measuredData = self.impd.read_measurement_data()
                else:
                    smallTemp = min(TempList[tcount],TempList[tcount+1])
                    largeTemp = max(TempList[tcount],TempList[tcount+1])
                    if largeTemp >= sweepInitialTemperature >= smallTemp:
                        self.impd.start_fSweep()
                        self.impd.wait_to_complete()
                        measuredData = self.impd.read_measurement_data()
                        tcount += 1
                        if tcount+1 >= len(TempList):
                            self.TCont.reset()
                            sweepFinalTemperature = self.TCont.temp
                            averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
                            deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
                            timeElapsed = round(time() - startTime,3)
                            wholeData = measuredData + [timeElapsed, averageTemperature, deltaT]
                            self.data.emit(wholeData)
                            break
                    else:
                        continue
                sweepFinalTemperature = self.TCont.temp
                averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
                deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
                timeElapsed = round(time() - startTime,3)
                wholeData = measuredData + [timeElapsed, averageTemperature, deltaT]
                if self.TCont.tCount == 0: # Include frequency data initially
                    frequencyData = self.impd.get_frequencies()
                    self.freqSig.emit([frequencyData] + wholeData)
                    self.TCont.tCount += 1
                else:
                    self.data.emit(wholeData)
                if self.stopCall == True:
                    self.TCont.reset()
                    self.showStatus.emit("Temperature sweep aborted. Partial data saved.")
                    break
            if self.stopCall == False:
                self.showStatus.emit("Temperature sweep complete. Data saved.")
        elif self.TCont.mode == 2:
            if len(self.TCont.tempList):
                tcount = 0
                for temperature in list(self.TCont.tempList):
                    self.TCont.temp = temperature
                    # wait till present temperature reaches start temperature
                    while abs(self.TCont.temp-temperature) > 1:
                        self.showStatus.emit("Waiting to reach {} K".format(temperature))
                        while abs(self.TCont.temp-temperature) > 2:
                            if self.stopCall == True:
                                self.TCont.reset()
                                self.showStatus.emit("Temperature dependent scan aborted.")
                                self.finished.emit()
                                return
                            sleep(2)
                        self.showStatus.emit("Stabilizing at {} K".format(self.TCont.startT))
                        count = 0
                        # wait to stabilize at the start temperature
                        waitCount = self.TCont.stabilizationTime*60/2
                        while count < waitCount: # write 300 to make wait time as 10 minutes
                            if self.stopCall == True:
                                self.TCont.reset()
                                self.showStatus.emit("Temperature dependent scan aborted.")
                                self.finished.emit()
                                return
                            count += 1
                            sleep(2)
                    sweepInitialTemperature = self.TCont.temp
                    self.impd.start_fSweep()
                    self.impd.wait_to_complete()
                    measuredData = self.impd.read_measurement_data()
                    sweepFinalTemperature = self.TCont.temp
                    averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
                    deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
                    timeElapsed = round(time() - startTime,3)
                    wholeData = measuredData + [timeElapsed, averageTemperature, deltaT]
                    if tcount == 0:
                        frequencyData = self.impd.get_frequencies()
                        self.freqSig.emit([frequencyData] + wholeData)
                    else:
                        self.data.emit(wholeData)
                    tcount += 1
            else:
                self.showStatus.emit("No temperature points available. Single sweep at current temperature done.")
                sweepInitialTemperature = self.TCont.temp
                self.impd.start_fSweep()
                self.impd.wait_to_complete()
                measuredData = self.impd.read_measurement_data()
                sweepFinalTemperature = self.TCont.temp
                averageTemperature = round((sweepInitialTemperature+sweepFinalTemperature)/2,2)
                deltaT = abs(sweepFinalTemperature-sweepInitialTemperature)
                timeElapsed = round(time() - startTime,3)
                frequencyData = self.impd.get_frequencies()
                wholeData = measuredData + [timeElapsed, averageTemperature, deltaT]
                self.freqSig.emit([frequencyData] + wholeData)
            if self.stopCall == False:
                self.showStatus.emit("Temperature scan complete. Data saved.")
        message = "Stopped temperature dependent scan at {}K".format(self.TCont.temp)
        sendMessage(self.senderemail,
                    self.password,
                    self.server,        
                    self.user,
                    self.subject,
                    message)
        self.finished.emit()
        
def get_frequencies_list(start, end, npoints, spacing):
    # spacing = 0, 1, 2 = linear, log10, linear-Log10
    if start < 20:
        start = 20
    if end > 1e7:
        end = 1e7
    if npoints < 2:
        npoints = 2
    if npoints > 1601:
        npoints = 1601
    if spacing not in (0, 1, 2):
        spacing = 1
    if spacing == 0:
        frequencies = linspace(start, end, npoints, endpoint=True)
    elif spacing == 1:
        frequencies = logspace(log10(start), log10(end),
                               npoints, endpoint=True)
    elif spacing == 2:
        min_order = int(log10(start))
        max_order = int(log10(end))
        lin_ranges = logspace(min_order, max_order, (max_order-min_order)+1)
        lin_ranges[0] = start
        if lin_ranges[-1] != end:
            lin_ranges = append(lin_ranges, end)
        points_per_order = array([0 for i in range(len(lin_ranges)-1)])
        npoints = round(npoints/9)*9
        oneFactor = len(lin_ranges)*9
        n = npoints+(9*len(lin_ranges))+1
        i = 1
        while n > npoints+(9*len(lin_ranges)):
            mFactor = round(npoints/(9*i))
            n = mFactor*oneFactor
            i += 1
        if n == 0:
            npoints = len(lin_ranges)*9
        else:
            npoints = n
        p = ceil(npoints/len(lin_ranges))
        points_per_order[0] = ceil(
            (lin_ranges[1]-lin_ranges[0])/lin_ranges[1]*9)*mFactor
        points_per_order[-1] = int((lin_ranges[-1] -
                                   lin_ranges[-2])/(lin_ranges[-2]*9)*9)*mFactor
        points_per_order[1:-1] = p
        npoints = sum(points_per_order)+1
        frequencies = []
        for i in range(len(lin_ranges[:-1])):
            frequencies.extend(list(
                linspace(lin_ranges[i], lin_ranges[i+1], points_per_order[i], endpoint=False)))
        frequencies.append(end)
    return frequencies

def unique_filename(directory, prefix='DATA', suffix='', ext='csv',
                    dated_folder=False, index=True, datetimeformat="%Y-%m-%d"):
    """
    Return a unique filename based on the directory and prefix.
    Note: adopted from Pymeasure Package.
    """
    now = datetime.now()
    directory = abspath(directory)
    if dated_folder:
        directory = join(directory, now.strftime('%Y-%m-%d'))
    if not exists(directory):
        makedirs(directory)
    if index:
        i = 1
        basename = "%s%s" % (prefix, now.strftime(datetimeformat))
        basepath = join(directory, basename)
        filename = "%s_%d%s.%s" % (basepath, i, suffix, ext)
        while exists(filename):
            i += 1
            filename = "%s_%d%s.%s" % (basepath, i, suffix, ext)
    else:
        basename = "%s%s%s.%s" % (
            prefix, now.strftime(datetimeformat), suffix, ext)
        filename = join(directory, basename)
    return filename

def get_valid_filename(s):
    """
    Check if given filename is valid, and correct it if its not.

    Parameters
    ----------
    s : string
        file-name

    Returns
    -------
    string
        Valid file-name

    """
    s = str(s).strip().replace(' ', '_')
    return sub(r'(?u)[^-\w.]', '', s)

def sendMessage(senderemail,password,server,user,subject,message):
    if len(user) == 5:
        if user[4]:
            sendLineMessage(user[2],"{0}\n{1}".format(subject,message))
        if user[3]:
            sendEmailMessage(senderemail,password,server,user[1],subject,message)

def sendLineMessage(token,message):
    payload = {'message' : message}
    r = requests.post('https://notify-api.line.me/api/notify',
                      headers={'Authorization' : 'Bearer {}'.format(token)},
                      params = payload)
    print("Sent line message", r.text)

def sendEmailMessage(senderemail,password,server,receiveremail,subject, message):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = senderemail
    msg['To'] = receiveremail
    smtp =  SMTP(server,587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(senderemail,password)
    smtp.send_message(msg)
    smtp.quit()

def initializeEmail(settingPath):
    # Sending email has only been tested with outlook.com, but should work with other emails as well.
    # port 587 is generatlly used, if your email server has different port, change it in sendEmailMessage function
    # the first line of users.txt should be following:
    # system email, password, SMTP server, subject
    # example: "abc.outlook.com password smtp-mail.outlook.com Message from Python"
    currPath = os.getcwd()
    os.chdir(settingPath)
    with open("users.txt",'r') as f:
        line = f.readline().split()
        email = line[0]
        password = line[1]
        server = line[2]
        subject = " ".join(line[3:])
    os.chdir(currPath)
    return email,password,server,subject