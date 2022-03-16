# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:44:48 2021

@author: Badari
"""
#
import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())
from kp1000c import Chino
import sys
import time
import pandas as pd
from pymeasure.experiment import unique_filename
from pymeasure.instruments import Instrument
from numpy import genfromtxt, delete, searchsorted, array

"""
data = genfromtxt('KP_Au_chart.csv', delimiter=',')
data = delete(data,0,0)
data_V = data[:,1]
data_T = data[:,0]

def vtoK1(v): # v should be in microvolts
    global data, data_V
    idx = searchsorted(data_V, v)
    if v < -5301 or v > 598:
        return -1
    if data_V[idx] == v:
        return data_T[idx]
    else:
        T1 = data_T[idx-1]
        dT = ((v-data_V[idx-1])/(data_V[idx]-data_V[idx-1]))*(data_T[idx]-data_T[idx-1])
        return round(T1+dT,2)
"""
# This polynomial works between 1 to 300K only
poly14 = array([-8.83793773e-47, -2.75772877e-42, -3.75525125e-38, -2.92143221e-34,
       -1.42506288e-30, -4.48544398e-27, -8.94912836e-24, -1.03231405e-20,
       -4.54646789e-18,  3.14228734e-15,  4.06003157e-12,  6.76133414e-10,
       -8.98169816e-07,  4.50066407e-02,  2.73164355e+02]) #(Residual sum of squares = 0.196)

# This polynomial has been extrapolated, and works between 1 to 360 K
poly14_extended = array([-4.87150127e-48, -9.84306780e-44, -7.12505142e-40, -1.72832181e-36,
        3.41616465e-33,  2.17361238e-29,  5.61807414e-27, -9.61722627e-23,
       -4.71717673e-20,  2.75525249e-16,  8.56002438e-14, -4.68339127e-10,
       -6.64863663e-07,  4.52106495e-02,  2.73191571e+02])  # Residual sum of squares = 0.69898

def vtoK(v):
    global poly14
    temp = 0
    rank = len(poly14)
    for i,j in enumerate(poly14):
        temp = temp + j*(v**(rank-i-1))
    return round(temp,3)

def vtoK14_ext(v):
    global poly14_extended
    temp = 0
    rank = len(poly14_extended)
    for i,j in enumerate(poly14_extended):
        temp = temp + j*(v**(rank-i-1))
    return round(temp,3)   

class Keithley195a(Instrument):

    """
    The Keithley 195 is a 5 1/2 digit auto-ranging digital multimeter. You can
    find the full specifications list in the `Keithley 195 user's guide`_.

    Example usage:

   .. _Keithley 195 user's guide: http://www.keithley.com/data?asset=803
    """

    def __init__(self, adapter, **kwargs):
        super(Keithley195a, self).__init__(
            adapter, "Keithley 237 High Voltage Source Measure Unit", **kwargs
        )
        self.write('YX')  # Removes the termination CRLF
        self.write('G1DX')  # Disable returning prefix and suffix
    

k195 = Keithley195a("GPIB0::2::INSTR")
ch = Chino('com3')
ch.write_param(' 3, 1, 01,00,31,0,')   # step 0, start at 20K
ch.write_param(' 3, 2, 01,01,280,0.50,') # go to 280 K at 5k/min rate (in 52 mins)
ch.write_param(' 3, 2, 01,02,280,0.10,') # stay at 280K for 10 mins
#ch.write_param(' 3, 2, 01,03,40,0.48,')  # go to 20K at 5k/min
#ch.write_param(' 3, 2, 01,04,280,2.00') # go to 280 K at 2K/min rate (in 130 mins)
#ch.write_param(' 3, 2, 01,05,280,0.10') # stay at 280K for 10 mins
ch.write_param(' 3, 3, 01,03,00,0,') # end program, and set output to zero
ch.write_param(' 2, 1, 1, 01,') # run pattern 1
count = 1
zerotime = time.time()
file = "monitor_data"
file2 = unique_filename(directory='./',prefix=file,datetimeformat="")
#text_file = open("Raw_Output.txt", "w")
while True:
    try:
        v = float(k195.read())*1000.0  # convert v to millivolts
        k_temp = vtoK(v*1000) # send v in microvolts
        ch.real_data_request()
        #text_file.write(ch.data+'\n')
        #text_file.flush()  # force data to be written to hard-disk instead of being kept in buffer
        y_temp = float(ch.PV)
        y_set_temp = float(ch.SV)
        y_output = float(ch.MV1)
        x_time = int(time.time()-zerotime)
        data = pd.DataFrame({
                'Time Stamp (s)': [time.time()],
                'Time Elapsed (s)': [x_time],
                'Keithley195 Voltage (mV)': [v],
                'Keithley195 Temperature (K)': [k_temp],
                'Chino Temperature (K)': [y_temp],
                'Set Temperature (K)': [y_set_temp],
                'Output power (W)' : [y_output]
                })
        time.sleep(2)
        if count == 1:
            data.to_csv(file2,mode='a')
        else:
            data.to_csv(file2,mode='a',header=False)
        if count%200==0 or count == 1:
            print("Temperature after {0} seconds is {1} K(Chino), {2} K(K195), output_power {3}".format(x_time,y_temp,k_temp,y_output))
        if ch.status == 3:
            ch.reset_program()
            break
        count = count+1
    except KeyboardInterrupt:
        print("Temperature at exiting, after {0} seconds is {1} C".format(x_time,y_temp))
        print("User interrupted! Data saved")
        ch.s.close()
        #text_file.close()
        sys.exit(0)
ch.s.close()
#text_file.close()
print("Program finished! Data saved")