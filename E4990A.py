# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:07:10 2022

@author: Badari
"""

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from pyvisa.errors import VisaIOError
from time import sleep
from random import randint, uniform

"""
Important commands:
    ":SYST:PRES True"
    ":TRIG:SOUR BUS" # measurement is triggered with *TRG command is sent
    ":TRIG:SOUR INT" # measurement is triggered internally, for continuous measurement
    ":INIT1:CONT ON" # for continuous measurement on channel 1
    "*OPC?" # wait for measurement to finish
    
Required functions:
    continuously display impedance
    frequency sweep
    calibration
    set measurement accuracy
    apply DC bias (and sweep option)
    set ac voltage

"""
class KeysightE44990A(Instrument):
    """Represents Impedance Analyzer E44990A"""

    """
    ac_voltage = Instrument.control(":VOLT:LEV?", ":VOLT:LEV %g",
                                    "AC voltage level, in Volts",
                                    validator=strict_range,
                                    values=[0, 20])

    ac_current = Instrument.control(":CURR:LEV?", ":CURR:LEV %g",
                                    "AC current level, in Amps",
                                    validator=strict_range,
                                    values=[0, 0.1])

    frequency = Instrument.control(":FREQ:CW?", ":FREQ:CW %g",
                                   "AC frequency (range depending on model), in Hertz",
                                   validator=strict_range,
                                   values=[20, 2e6])

    # FETCH? returns [A,B,state]: impedance returns only A,B
    impedance = Instrument.measurement(
        ":FETCH?",
        "Measured data A and B, according to :attr:`~.AgilentE4980.mode`",
        get_process=lambda x: x[:2])

    mode = Instrument.control("FUNCtion:IMPedance:TYPE?", "FUNCtion:IMPedance:TYPE %s",
    """
    """
    Select quantities to be measured:
    * CPD: Parallel capacitance [F] and dissipation factor [number]
    * CPQ: Parallel capacitance [F] and quality factor [number]
    * CPG: Parallel capacitance [F] and parallel conductance [S]
    * CPRP: Parallel capacitance [F] and parallel resistance [Ohm]
    * CSD: Series capacitance [F] and dissipation factor [number]
    * CSQ: Series capacitance [F] and quality factor [number]
    * CSRS: Series capacitance [F] and series resistance [Ohm]
   * LPD: Parallel inductance [H] and dissipation factor [number]
   * LPQ: Parallel inductance [H] and quality factor [number]
   * LPG: Parallel inductance [H] and parallel conductance [S]
   * LPRP: Parallel inductance [H] and parallel resistance [Ohm]
    * LSD: Series inductance [H] and dissipation factor [number]
    * LSQ: Seriesinductance [H] and quality factor [number]
    * LSRS: Series inductance [H] and series resistance [Ohm]
    * RX: Resitance [Ohm] and reactance [Ohm]
    * ZTD: Impedance, magnitude [Ohm] and phase [deg]
    * ZTR: Impedance, magnitude [Ohm] and phase [rad]
    * GB: Conductance [S] and susceptance [S]
    * YTD: Admittance, magnitude [Ohm] and phase [deg]
    * YTR: Admittance magnitude [Ohm] and phase [rad]

                              validator=strict_discrete_set,
                              values=["CPD", "CPQ", "CPG", "CPRP",
                                      "CSD", "CSQ", "CSRS",
                                      "LPD", "LPQ", "LPG", "LPRP",
                                      "LSD", "LSQ", "LSRS",
                                      "RX", "ZTD", "ZTR", "GB", "YTD", "YTR", ])

    trigger_source = Instrument.control("TRIG:SOUR?", "TRIG:SOUR %s",
                                        
    Select trigger source; accept the values:
    * HOLD: manual
    * INT: internal
    * BUS: external bus (GPIB/LAN/USB)
    * EXT: external connector
                                        validator=strict_discrete_set,
                                        values=["HOLD", "INT", "BUS", "EXT"])
    """

    def __init__(self, adapter, freq=1000, Vac=0.1, Vdc=0, temp='NA', **kwargs):
        super().__init__(adapter, "Keysight E4990A Impedance Analyzer", timeout = 120000, **kwargs)
        self.timeout = 30000
        self._freq = freq
        self.getFreqUnit()
        self.Vac = Vac
        self.Vdc = Vdc
        self.sweepCount = 0
        self.startf = 20
        self.endf = 1e7
        self.npointsf = 50
        self.sweeptypef = 1
        self.ID = "E4990A"
        # set oscillating mode as voltage
        self.write(":SOUR1:MODE VOLT")
        self.write(":SOUR1:ALC OFF") # tur off auto level control
        # set DC Bias mode as voltage
        self.write(":SOUR1:BIAS:MODE VOLT")
        self.set_measurement_parameter()
        self.set_number_of_traces_to_display(4)
        self.showSplitDisplay()
        self.setYAutoScale()

    def initialize(self):
        # initialize the instrument to obtain absolute Z, phase Z, Capacitance, and loss in respective four channels
        
        pass

    def initializeDisplay(self):
        # initialize the display to view four channels in split view mode
        pass
    
    def enable_DC_Bias(self,ans=True):
        if ans == True:
            self.write(":SOUR:BIAS:STAT ON")
        else:
            self.write(":SOUR:BIAS:STAT OFF")
    
    def is_BIAS_ON(self):
        ans = float(self.ask(":SOUR:BIAS:STAT?"))
        if ans:
            return True
        else:
            return False
        
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

    """    
    def freq_sweep(self, freq_list, return_freq=False):
        
        #Run frequency list sweep using sequential trigger.
        #:param freq_list: list of frequencies
        #:param return_freq: if True, returns the frequencies read from the instrument
        #Returns values as configured with :attr:`~.AgilentE4980.mode`
            
        # manual, page 299
        # self.write("*RST;*CLS")
        self.write("TRIG:SOUR BUS")
        self.write("DISP:PAGE LIST")
        self.write("FORM ASC")
        # trigger in sequential mode
        self.write("LIST:MODE SEQ")
        lista_str = ",".join(['%e' % f for f in freq_list])
        self.write("LIST:FREQ %s" % lista_str)
        # trigger
        self.write("INIT:CONT ON")
        self.write(":TRIG:IMM")
        # wait for completed measurement
        # using the Error signal (there should be a better way)
        while 1:
            try:
                measured = self.values(":FETCh:IMPedance:FORMatted?")
                break
            except VisaIOError:
                pass
        # at the end return to manual trigger
        self.write(":TRIG:SOUR HOLD")
        # gets 4-ples of numbers, first two are data A and B
        a_data = [measured[_] for _ in range(0, 4 * len(freq_list), 4)]
        b_data = [measured[_] for _ in range(1, 4 * len(freq_list), 4)]
        if return_freq:
            read_freqs = self.values("LIST:FREQ?")
            return a_data, b_data, read_freqs
        else:
            return a_data, b_data
    """

    def close(self):
        self.shutdown()
    
    def continuous_measurement(self,continuous="ON"):
        """
        Syntax
        :INITiate<Ch>:CONTinuous {ON|OFF|1|0}
        
        :INITiate<Ch>:CONTinuous?
        
        Description
        This command turns ON/OFF the continuous initiation mode (setting by which the trigger system initiates continuously) in the trigger system.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        ON/OFF of the continuous initiation mode
        
        Data Type
        
        Boolean type (Boolean)
        
        Range
        
        ON|OFF|1|0
        
        Preset Value
        
        OFF
        
        Query Response
        {1|0}<newline><^END>
        
        Examples

        Returns
        -------
        None.

        """
        self.write(":INIT1:CONT {}".format(continuous))
    
    def abort(self):
        """
        This command aborts the current sweep.

        Returns
        -------
        None.

        """
        self.write(":ABOR")
    
    def read_measurement_data(self):
        """
        Syntax
        :CALCulate<Ch>[:SELected]:DATA:FDATa <Value>
        
        :CALCulate<Ch>[:SELected]:DATA:FDATa?
        
        Description
        This command sets/gets the formatted data array.
        
        The array data element varies in the data format. If valid data is not calculated because of the invalid measurement, “1.#QNB” is read out.
        
        Variable
        Parameter
                
        Value
        
        Description
        
        Formatted data array
        
        Where n is an integer between 1 and NOP (number of measurement points):
        
        <numeric n×2-1>:  primary parameter at the n-th measurement point. (For the complex format or the polar format, real part of data)
        
        <numeric n×2>: secondary parameter at the n-th measurement point. Always 0 when the data format is not the complex or polar formats. (For the complex format or the polar format, imaginary part of data)
        
        The number of data is {NOP×2}
        
        Data Type
        
        Variant type Array (Range)
        
        Note
        
        If there is no array data of NOP×2 when setting a formatted data array, an error occurs when executed.
        
        Query Response
        {numeric 1}, .... ,{numeric NOP×2}<newline><^END>

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.write(":Calculate1:Parameter1:Sel")
        z = self.ask(":Calculate1:Data:Fdata?")
        z = z.split(',')
        z = [float(x) for i,x in enumerate(z) if i%2==0]
        sleep(0.1)
        self.write(":Calculate1:Parameter2:Sel")
        p = self.ask(":Calculate1:Data:Fdata?")
        p = p.split(',')
        p = [float(x) for i,x in enumerate(p) if i%2==0]
        sleep(0.1)
        self.write(":Calculate1:Parameter3:Sel")
        c = self.ask(":Calculate1:Data:Fdata?")
        c = c.split(',')
        c = [float(x) for i,x in enumerate(c) if i%2==0]
        sleep(0.1)
        self.write(":Calculate1:Parameter4:Sel")
        d = self.ask(":Calculate1:Data:Fdata?")
        d = d.split(',')
        d = [float(x) for i,x in enumerate(d) if i%2==0]
        sleep(0.1)
        data = [z,p,c,d]
        return data
    
    def get_frequencies(self):
        """
        Description
        This command returns the frequency stimulus data.
        
        Variable
        Parameter
        
        Value
        
        Description
        
        Indicates the array data (frequency) of NOP (number of measurement points). Where n is an integer between 1 and NOP.
        
        Data(n-1): Frequency at the n-th measurement point
        
        The index of the array starts from 0.
        
        Data Type
        
        Variant type Array (Range)
        
        Query Response
        {numeric 1}, .... ,{numeric NOP}<newline><^END>

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        freq = self.ask(":SENS1:FREQ:DATA?")
        freq = freq.split(',')
        return [float(x) for x in freq]
    
    def get_xVals(self):
        """
        X-values depends on sweep type.
        
        Returns
        -------
        Returns x-axis values as list

        """
        xval = self.ask(":CALC1:DATA:XAX?")
        xval = xval.split(',')
        return [float(x) for x in xval]
    
    def reset_to_default_continuous_measurement(self):
        """
        This command presets the setting state of the E4990A to the original factory setting (Default Conditions). 
        This command is different from *RST as the continuous startup mode (:INIT:CONT) of channel 1 is set to ON.

        Returns
        -------
        None.

        """
        
        self.write(":SYST:PRES")
    
    def trig_from_PC(self):
        """
        Syntax
        :TRIGger[:SEQuence]:SOURce {INTernal|EXTernal|MANual|BUS}
        
        :TRIGger[:SEQuence]:SOURce?
        
        Description
        This command sets/gets the trigger source from the following 4 types:
        
        Internal Trigger: Uses the internal trigger to generate continuous triggers automatically.
        
        External Trigger: Generates a trigger when the trigger signal is inputted externally via the Ext Trig connector or the handler interface.
        
        Manual Trigger: Generates a trigger when the key operation of Trigger > Trigger is executed from the front panel.
        
        Bus Trigger: Generates a trigger when the *TRG is executed.
        
        When you change the trigger source during sweep, the sweep is aborted.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        Trigger source
        
        Data Type
        
        Character string type (String)
        
        Range
        
        INTernal|EXTernal|MANual|BUS
        
        Preset Value
        
        INTernal
        
        Query Response
        {INT|EXT|MAN|BUS}<newline><^END>
        


        Returns
        -------
        None.

        """
        self.write(":TRIG:SOUR BUS")
    
    def trig_from_internal(self):
        self.write(":TRIG:SOUR INT")
    
    def set_measurement_parameter(self):
        """
        Syntax
        :CALCulate<Ch>:PARameter<Tr>:DEFine {Z|Y|R|X|G|B|LS|LP|CS|CP|RS|RP|Q|D|TZ|TY|VAC|IAC|VDC|IDC|IMP|ADM}
        
        :CALCulate<Ch>:PARameter<Tr>:DEFine?
        
        Description
        This command sets/gets the measurement parameter. The VDC or IDC can be selected only at bias sweep or log bias sweep.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        Measurement parameter
        
        Data Type
        
        Character string type (String)
        
        Range
        
        Z: Absolute impedance value
        Y: Absolute admittance
        R: Equivalent series resistance
        X: Equivalent series reactance
        G: Equivalent parallel conductance
        B: Equivalent parallel susceptance
        
        LS: Equivalent series inductance
        LP: Equivalent parallel inductance
        
        CS: Equivalent series capacitance
        CP: Equivalent parallel capacitance
        
        RS: Equivalent series resistance
        RP: Equivalent parallel resistance
        
        Q: Q value
        D: Dissipation factor
        
        TZ: Impedance phase
        TY: Absolute phase
        
        VAC: OSC level (Voltage)
        IAC: OSC level (Current)
        VDC: DC Bias (Voltage)
        IDC: DC Bias (Current)
        
        IMP: Impedance (complex value)
        ADM: Admittance (complex value)
        
        Preset Value
        
        Z
        
        Query Response
        {Z|Y|R|X|G|B|LS|LP|CS|CP|RS|RP|Q|D|TZ|TY|VAC|IAC|VDC|IDC|IMP|ADM}<newline><^END>

        Returns
        -------
        None.

        """
        # set channel 1 trace 1 to measure absolute impedance Z
        self.write(":CALC1:PAR1:DEF Z")
        
        #set channel 1 trace 2 to measure impedance phase
        self.write(":CALC1:PAR2:DEF TZ")
        
        #set channel 2 trace 1 to measure Parallel Capacitance
        self.write(":CALC1:PAR3:DEF CP")
        
        #set channel 2 trace 2 to measure Dissipation Factor
        self.write(":CALC1:PAR4:DEF D")
    
    def setYAutoScale(self):
        self.write(":DISPlay:WINDow1:TRACe1:Y:AUTO")
        self.write(":DISPlay:WINDow1:TRACe2:Y:AUTO")
        self.write(":DISPlay:WINDow1:TRACe3:Y:AUTO")
        self.write(":DISPlay:WINDow1:TRACe4:Y:AUTO")
        
    def set_yAxis_log(self):
        """
        Syntax
        :DISPlay:WINDow<Ch>:TRACe<Tr>:Y:SPACing {LINear|LOGarithmic}
        
        :DISPlay:WINDow<Ch>:TRACe<Tr>:Y:SPACing?
        
        Description
        This command sets the display type of the graph vertical axis (Y-axis).
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        Vertical axis display type of the graph
        
        Data Type
        
        Character string type (String)
        
        Range
        
        LINear|LOGarithmic
        
        Preset Value
        
        LINear
        
        Query Response
        {LIN|LOG}<newline><^END>
        


        Returns
        -------
        None.

        """
        self.write(":DISP:WIND1:TRAC1:Y:SPAC LOG")
    
    def fix_frequency(self):
        """
        Description
        This command sets/gets the continuous wave frequency.
        
        Variable
        Parameter
        
        Value
        
        Description
        
        Continuous wave frequency
        
        Data Type
        
        Numeric type (Real)
        
        Range
        
        20 ~ 120M
        
        Preset Value
        
        1M
        
        Unit
        
        Hz
        
        Resolution
        
        1m
        
        Query Response
        {numeric}<newline><^END>
        


        Parameters
        ----------
        freq : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.write(":SENS1:FREQ {}".format(self._freq))
    
    def get_fixedFrequency(self):
        freq = float(self.ask(":SENS1:FREQ?"))
        return freq
        
    def select_voltage_source(self):
        """
        Description
        This command sets/gets the unit for OSC level.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        OSC unit
        
        Data Type
        
        Character string type (String)
        
        Range
        
        VOLTage|CURRent
        
        Preset Value
        
        VOLTage
        
        Query Response
        {VOLT|CURR}<newline><^END>
        


        Returns
        -------
        None.

        """
        self.write(":SOUR1:MODE VOLT")
    
    def fix_AC_Voltage(self,volt):
        """
        Description
        This command sets/gets the source voltage level.
        
        Variable
        Parameter
        
        Value
        
        Description
        
        Voltage level
        
        Data Type
        
        Numeric type (Real)
        
        Range
        
        5m ~ 1
        
        Preset Value
        
        500m
        
        Unit
        
        V
        
        Resolution
        
        1m
        
        Query Response
        {numeric}<newline><^END>
        
        Parameters
               ----------
               volt : TYPE
                   DESCRIPTION.

        Returns
        -------
        None.

        """
        self.write(":SOUR1:VOLT {}".format(volt))
    
    def enable_auto_level_control(self):
        """
        Description
        This command turn on/off the ALC function.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        ALC On/Off status
        
        Data Type
        
        Boolean type (Boolean)
        
        Range
        
        ON|OFF|1|0
        
        Preset Value
        
        OFF
        
        Query Response
        {1|0}<newline><^END>
        


        Returns
        -------
        None.

        """
        self.write(":SOUR1:ALC ON")
    
    def display_off(self):
        """
        Syntax
        :DISPlay:WINDow<Ch>:TRACe<Tr>:STATe {ON|OFF|1|0}
        
        :DISPlay:WINDow<Ch>:TRACe<Tr>:STATe?
        
        Description
        This command turns ON/OFF the data trace display.
        
        Variable
        Parameter
        
        Selection Option
        
        Description
        
        ON/OFF of the data trace display
        
        Data Type
        
        Boolean type (Boolean)
        
        Range
        
        ON|OFF|1|0
        
        Preset Value
        
        ON
        
        Query Response
        {1|0}<newline><^END>

        Returns
        -------
        None.

        """
        self.write(":DISPlay:WINDow1:TRACe1:STATe OFF")
        self.write(":DISPlay:WINDow1:TRACe2:STATe OFF")
        self.write(":DISPlay:WINDow1:TRACe3:STATe OFF")
        self.write(":DISPlay:WINDow1:TRACe4:STATe OFF")
    
    def display_on(self):
        self.write(":DISPlay:WINDow1:TRACe1:STATe ON")
        self.write(":DISPlay:WINDow1:TRACe2:STATe ON")
        self.write(":DISPlay:WINDow1:TRACe3:STATe ON")
        self.write(":DISPlay:WINDow1:TRACe4:STATe ON")
    
    def get_current_values(self):
        self.write(":Calculate1:Parameter1:Sel")
        z = self.ask(":Calculate1:Data:Fdata?")
        z = z.split(',')
        z = float(z[0])
        self.write(":Calculate1:Parameter2:Sel")
        p = self.ask(":Calculate1:Data:Fdata?")
        p = p.split(',')
        p = float(p[0])
        self.write(":Calculate1:Parameter3:Sel")
        c = self.ask(":Calculate1:Data:Fdata?")
        c = c.split(',')
        c = float(c[0])
        self.write(":Calculate1:Parameter4:Sel")
        d = self.ask(":Calculate1:Data:Fdata?")
        d = d.split(',')
        d = float(d[0])
        return z,p,c,d
        """
        z = randint(1000, 10000)
        p = randint(1, 100)
        c = uniform(1e-7, 1e-12)
        d = uniform(0, 1)
        sleep(2)
        return z, p, c, d
        """
    
    def get_absolute_frequency(self, freq, units):
        if units == 0: # Hz
            return freq
        elif units == 1: # kHz
            return freq*1e3
        elif units == 2: # MHz
            return freq*1e6
    
    def wait_to_complete(self):
        ans = float(self.ask("*OPC?"))
        self.setYAutoScale()
        if ans == 1:
            return True
        else:
            return False
    
    def start_fSweep(self):
        self.write(":TRIG:SINGLE")
    
    def start_dcSweep(self, i = 0): # needs to be a different function for Fake adapter to work
        if i%2 == 0:
            self.write(":SENSe1:SWEep:DIRection UP")
        else:
            self.write(":SENSe1:SWEep:DIRection DOWN")
        self.write(":TRIG:SINGLE")
    
    def setVac(self):
        self.write(":SOUR1:VOLT {}".format(self.Vac))
    
    def setVdc(self):
        self.write(":SOUR1:BIAS:VOLT {}".format(self.Vdc))
    
    def set_number_of_traces_to_display(self,value=4):
        self.write(":CALC1:PAR:COUN {}".format(value))
    
    def showSplitDisplay(self):
        self.write(':DISP:WIND1:SPL D1_2')
    
    def activateChannel(self):
        """
        Syntax
        :DISPlay:WINDow<Ch>:ACTivate

        Description
        This command specifies the active channel. You can set only a channel displayed to the active channel. If this object is used to set a channel not displayed to the active channel, an error occurs when executed and the object is ignored.

        Use :CALC:PAR:SEL to activate the trace.

        Examples


        Returns
        -------
        None.

        """
        self.write(":DISP:WIND:ACT")
    
    def setMeasurementSpeed(self,value):
        # This command sets/gets the measurement speed. 1 is the fastest setting, 5 is slowest.
        try:
            if 1 <= value <= 5:
                self.write(":SENS1:APER {}".format(value))
        except:
            pass
    
    def setPointAveragingFactor(self,value):
        ans = int(float(self.ask(":SENS1:AVER?")))
        if ans == 0:
            self.write(":SENS1:AVER ON") # enable point average
        self.write(":SENS1:AVER:COUN {}".format(value))
    
    def disable_display_update(self):
        # disable display update
        self.write(":DISP:ENAB OFF")

    def enable_display_update(self):
        # enable display update        
        self.write(":DISP:ENAB ON")
    
    