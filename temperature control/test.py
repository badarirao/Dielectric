# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 16:10:40 2021

@author: Badari
"""

from kp1000c import Chino
from time import sleep
"""
set program from 20K to 280K at 5 K per min
measure temperature every 1 second
plot set temperature and actual temperature with Time
"""


ch = Chino('com3')
ch.write_param(' 3, 1, 01,00,31,0,')   # step 0, start at 20K
ch.write_param(' 3, 2, 01,01,280,0.50,') # go to 280 K at 5k/min rate (in 52 mins)
ch.write_param(' 3, 2, 01,02,280,0.10,') # stay at 280K for 10 mins
ch.write_param(' 3, 2, 01,03,40,0.48,')  # go to 20K at 5k/min
ch.write_param(' 3, 2, 01,04,280,2.00') # go to 280 K at 2K/min rate (in 130 mins)
ch.write_param(' 3, 2, 01,05,280,0.10') # stay at 280K for 10 mins
ch.write_param(' 3, 3, 01,06,00,0,') # end program, and set output to zero

ch.write_param(' 2, 1, 1, 01,') # run pattern 1

set_values = []
p_values = []
time_data = []
output_data = []
while True:
    ch.real_data_request()
    set_values.append(float(ch.sv))
    p_values.append(float(ch.pv))
    t = float(ch.time_greater)*60+float(ch.time_minor)
    time_data.append(t) # in minutes
    output_data.append(float(ch.MV1))
    if ch.status == '3':
        print('Program Successfully Finished')
        break
    sleep(1)
    