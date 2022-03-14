# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 17:07:10 2022

@author: Badari
"""

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pyvisa.errors import VisaIOError

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
""",
                              validator=strict_discrete_set,
                              values=["CPD", "CPQ", "CPG", "CPRP",
                                      "CSD", "CSQ", "CSRS",
                                      "LPD", "LPQ", "LPG", "LPRP",
                                      "LSD", "LSQ", "LSRS",
                                      "RX", "ZTD", "ZTR", "GB", "YTD", "YTR", ])

    trigger_source = Instrument.control("TRIG:SOUR?", "TRIG:SOUR %s",
                                        """
Select trigger source; accept the values:
    * HOLD: manual
    * INT: internal
    * BUS: external bus (GPIB/LAN/USB)
    * EXT: external connector""",
                                        validator=strict_discrete_set,
                                        values=["HOLD", "INT", "BUS", "EXT"])

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Agilent E4980A/AL LCR meter", **kwargs
        )
        self.timeout = 30000
        # format: output ascii
        self.write("FORM ASC")

    def freq_sweep(self, freq_list, return_freq=False):
        """
        Run frequency list sweep using sequential trigger.
        :param freq_list: list of frequencies
        :param return_freq: if True, returns the frequencies read from the instrument
        Returns values as configured with :attr:`~.AgilentE4980.mode`
            """
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

    # TODO: maybe refactor as property?
    def aperture(self, time=None, averages=1):
        """
        Set and get aperture.
        :param time: integration time as string: SHORT, MED, LONG (case insensitive);
            if None, get values
        :param averages: number of averages, numeric
        """
        if time is None:
            read_values = self.ask(":APER?").split(',')
            return read_values[0], int(read_values[1])
        else:
            if time.upper() in ["SHORT", "MED", "LONG"]:
                self.write(f":APER {time}, {averages}")
            else:
                raise Exception("Time must be a string: SHORT, MED, LONG")
