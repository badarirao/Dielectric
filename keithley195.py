# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 17:39:27 2020

@author: badar
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 17:07:57 2020

@author: badar

Driver for the Keithley 195 digital multimeter
"""

# IMPORTS #####################################################################

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

import sys

import logging
import time
import pandas as pd
from pymeasure.experiment import unique_filename
from pymeasure.instruments import Instrument

#from instruments.abstract_instruments import Multimeter
#from instruments.units import ureg as u

# find out what is the source of this formula?
def vtoK(v): # enter voltage in mV
    if v < -3.554:
        T0 = -1.2147164E+02
        v0 = -4.1790858E+00
        p1 = 3.6069513E+01
        p2 = 3.0722076E+01
        p3 = 7.7913860E+00
        p4 = 5.2593991E-01
        q1 = 9.3939547E-01
        q2 = 2.7791285E-01
        q3 = 2.5163349E-02
    elif v >=-3.554 and v < 4.096:
        T0 = -8.7935962E+00
        v0 = -3.4489914E-01
        p1 = 2.5678719E+01
        p2 = -4.9887904E-01
        p3 = -4.4705222E-01
        p4 = -4.4869203E-02
        q1 = 2.3893439E-04
        q2 = -2.0397750E-02
        q3 = -1.8424107E-03
    
    P = p1*(v-v0)+p2*(v-v0)**2+p3*(v-v0)**3+p4*(v-v0)**4
    Q = 1 + q1*(v-v0)+q2*(v-v0)**2+q3*(v-v0)**3
    Tc = T0 + P/Q
    return round(Tc+273.15,2)

# CLASSES #####################################################################


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
        self._temp = -1
    
    @property
    def temp(self):
        self._v = self.read()
        self._temp = vtoK(self._v)
        return self._temp
        
#k195 = Keithley195a("GPIB0::2::INSTR")


    
#fig = plt.figure()
#ax1 = fig.add_subplot(1,1,1)

def powerseries(v):
    B = [6.9864426367,
         9.0607276605e-1,
         -4.3469694773e-2,
         1.2468246660e-3,
         -2.3500537590e-5,
         3.0837610415e-7,
         -2.9032251684e-9,
         1.9881512159e-11,
         -9.9174829612e-14,
         3.5645229362e-16,
         -8.9864698504e-19,
         1.5071673023e-21,
         -1.5093916059e-24,
         6.8264293980e-28]
    T = v/B[0]
    while True:
        v1 = 0
        for i,j in enumerate(B):
            v1 = v1 + B[i]*T**(i+1)
        d = v - v1
        if d <= 0.00001 and d >= 0.00001:
            return T
        elif d > 0.00001:
            if d > 1:
                T = T-0.1
            elif d > 0.1:
                T = T-0.01
            elif d > 0.01:
                T = T-0.001
            elif d > 0.001:
                T = T - 0.0001
        else:
            if d < 1:
                T = T-0.1
            elif d < 0.1:
                T = T-0.01
            elif d < 0.01:
                T = T-0.001
            elif d < 0.001:
                T = T - 0.0001
"""
count = 1
zerotime = time.time()
file = "temp_test"
file2 = unique_filename(directory='./',prefix=file,datetimeformat="")
while True:
    try:
        x_time = int(time.time()-zerotime)
        v = float(k195.read())*1000.0
        y_temp = vtodegC(v)
        time.sleep(10)
        data = pd.DataFrame({
                'Time Stamp (s)': [time.time()],
                'Time difference (s)': [x_time],
                'Voltage (mV)': [v],
                'Temperature (C)': [y_temp],
                'Temperature (K)': [y_temp+273.15]   
                })
        if count == 1:
            data.to_csv(file2,mode='a')
        else:
            data.to_csv(file2,mode='a',header=False)
        if count%200==0 or count == 1:
            print("Temperature after {0} seconds is {1} C".format(x_time,y_temp))
        count = count+1
    except KeyboardInterrupt:
        print("Temperature at exiting, after {0} seconds is {1} C".format(x_time,y_temp))
        print("User interrupted! Data saved")
        sys.exit(0)
#ani = animation.FuncAnimation(fig, animate, frames= count, interval=1000)
#plt.show()

"""

"""
k195.write('F6X')   # set to read temperature in degree C
k195.write('R0X')   # set autorange
k195.write('T3X')   # trigger one shot on get
k195.ask('G0X')






ani = animation.FuncAnimation(fig, animate, frames= count, interval=1000)
plt.show()
"""
"""
import visa
rm = visa.ResourceManager()
rm.list_resources()
"""
