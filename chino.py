# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 12:15:20 2021
program for Keithley 6512 programmable electrometer
@author: badar
"""

from time import sleep
import serial
import re
DEBUG = False

reply_pattern = re.compile(r"\x02..(.*)\x03.", re.DOTALL)
device_address = '01'
EOT = '\x04'
STX = '\x02'
ENQ = '\x05'
ETX = '\x03'
ACK = '\x06'
NAK = '\x15'
CR = '\r'
LF = '\n'


def checksum(message):
    message = message + ETX
    bcc = format(sum(map(ord, message)), 'b')[-8:]
    bcc = format(int(bcc[:4], 2), 'X') + format(int(bcc[4:], 2), 'X')
    return "".join([bcc[1], bcc[0]])


class ChinoKP1000C(object):
    def __init__(self, serial_device, baudrate=19200, temp=-1):
        self.device = device_address
        # timeout: 110 ms to get all answers.
        self.s = serial.Serial(serial_device,
                               baudrate=baudrate,
                               bytesize=7,
                               parity='E',
                               stopbits=1,
                               timeout=0.11,
                               write_timeout=1)
        self._expect_len = 120
        self.connection = self._connect()
        self.filename = "kp100c.txt"
        self._temp = temp
        self.startT = 300
        self.stopT = 10
        self.rate = 1 # degreee per minute
        self.mode = 0
        self.tCount = 0
        self.traceback = False
        self.interval = 1
        self.all_modes_lock()
        #self.real_data_request()
        self.stabilizationTime = 10 # 10 minutes

    def read_param(self, param):
        self.write_param(param)
        answer = self.s.read(200).decode('UTF-8')
        sleep(0.1)
        if answer != '':
            if answer[0] == ACK:
                return 'Accepted'
            elif answer[0] == NAK:
                return 'Not accepted:', answer[1:3]
            elif checksum(answer[1:-5]) == answer[-4:-2]:
                return answer[1:-5]
            else:
                print("Some Problem in output")
        else:
            print("No response!")

    def _connect(self):
        # make connection with the device
        self.s.write(bytes(ENQ+'01'+CR+LF, 'UTF-8'))
        sleep(0.1)
        self.connection = self.s.read(100).decode('UTF-8')[1:3]
        if self.connection[0] == NAK:
            print("Error Connecting to the instrument")
            self.s.close()

    def write_param(self, message):
        bcc = checksum(message)
        mes = STX+message+ETX+bcc+CR+LF
        if DEBUG:
            for i in mes:
                print(i, hex(ord(i)))
        self.s.flushInput()
        wanswer = self.s.write(bytes(mes, 'UTF-8'))
        sleep(0.1)
        answer = self.s.read(200).decode('UTF-8')
        sleep(0.1)
        if answer != '':
            if answer[0] == ACK:
                print('Accepted')
            elif answer[0] == NAK:
                print('Not accepted: error code:', answer[1:3])
        else:
            print('No response!')
        return wanswer
        
    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, value):
        #FIXED CONTROL
        self.write_param(' 2, 4,1,{0}'.format(value))

    def real_data_request(self):
        # get current status from the controller
        self.data = self.read_param(' 1, 1,')
        if not self.data:
            return None
        # example response: ' 1, 1, 0,0,  276.42,       0,1,2,  0.00,6,       0,0,       0,'
        temp = self.data.split(',')
        self.pattern_no = int(temp[1].replace(" ", ""))
        self.step_no = int(temp[2].replace(" ", ""))
        self.pv_status = int(temp[3].replace(" ", ""))
        self.PV = float(temp[4].replace(" ", ""))
        self.SV = float(temp[5].replace(" ", ""))
        self.time_display_system = int(temp[6].replace(" ", ""))
        self.time_unit = int(temp[7].replace(" ", "")) # 1 = minute, 2 = Hours, 3 = days
        self.time = temp[8].replace(" ", "")  # hours/minutes
        self.status = int(temp[9].replace(" ", ""))
        self.MV1 = float(temp[10].replace(" ", ""))
        self._temp = self.PV
        # TODO: if self.PV is showing out of range, then set self._temp = -1
        return 1

    def get_current_temperature(self):
        self.real_data_request()
        return self.PV

    def get_set_temperature(self):
        self.real_data_request()
        return self.SV

    def all_modes_lock(self):
        self.write_param(' 2, 7,1,1,1,1,1,1,1,1,1,1,')

    def all_modes_unlock(self):
        self.write_param(' 2, 7,0,0,0,0,0,0,0,0,0,0,')
    
    def set_time_display_system(self,show=1):
        # 1-elapsed step, 2-elapsed pattern, 3-remaining steps, 4-remaining pattern
        self.write_param(' 2, 8,{}'.format(show))
    
    def clear_pattern(self,pattern='00'):
        # 00 - clear all patterns, other wise clear specified pattern number
        self.write_param(' 3, 8,{}'.format(pattern))

    def program_drive(self, task, pattern_no):
        self.write_param(' 2, 1, {0}, {1},'.format(task, pattern_no))

    def set_temperature(self, t):  # temperature t is in Kelvin
        self.write_param(' 2, 4,1,{0}'.format(t))

    def auto_tuning(self, tune):
        # tune = 0: stop, 1: AT1 start, 2: AT2 start, 3: AT3 start
        self.write_param(' 2, 6, {0}'.format(tune))

        PN = 1
        onstate = 1
        # AT2 individual settings
        # PN = 1 to 8 = Parameter Number
        # PN = 0 = copy to No. 1 to 8
        # onstate = 1 (ON), 0 (OFF)
        self.write_param('45,{0},{1}AT2SV,'.format(PN, onstate))

        # SV section (AT3) (1 to 7)
        # PN = 1 to 7
        self.write_param('46,{0},------,'.format(PN))

        # AT3 individual settings
        # PN = 1 to 8 = Parameter Number
        # PN = 0 = copy to No. 1 to 8
        # onstate = 1 (ON), 0 (OFF)
        self.write_param('47,{0},{1}AT3SV,'.format(PN, onstate))

        # AT start direction 0 = up, 1 = down
        dirn = 1
        self.write_param('48,{0},'.format(dirn))

    def rampT(self):
        # maybe go to start temperature first?
        self.write_param(' 2, 4,0, ,') # set to program mode
        rampTime = round(abs((self.startT-self.stopT)/self.rate)/60,2)
        self.write_param(' 3, 1,1,00, ,1,')   # step 0, start from present value
        self.write_param(' 3, 2,1,01,{0},{1},'.format(self.stopT,rampTime)) # go to stop temperature K at rate k/min rate
        if self.traceback:
            self.write_param(' 3, 2,1,02,{0},{1},'.format(self.startT,rampTime))  # go to 20K at 5k/min
            self.write_param(' 3, 3,1,03,00,0,') # end program, and set output to zero
        else:
            self.write_param(' 3, 3,1,02,00,0,') # end program, and set output to zero
        
        self.write_param(' 2, 1,1,01,') # run pattern 1
    
    def clearPattern(self,pattern_no=1):
        self.write_param(' 3, 8,1,')
        
    def abort(self):
        # abort pattern 1, programs maintains the current temperature
        self.write_param(' 2, 1, 2, 01,')
        
    def reset(self):
        self.write_param(' 2, 1, 4, 01,')
    
    def isRunning(self):
        #TODO: verify the value stored in self.status
        if self.real_data_request() is not None:
            if self.status == 0:
                return True
            else:
                return False
        else:
            return False
    
    def execution_parameter_request(self):
        ans = self.read_param(' 1, 2,')
        return ans
    
    def set_pattern_request(self, pattern_no=1, step_no=0):
        # if step = 0, returns pattern_no, 0. start SV, startSV/PV
        # if step > 0, returns pattern no, step no, SV, Time, Repeat count
        # PID No., ALM No., OPL No., OSL No., Sensor correction No.,
        # Waiting time No., TS1, TS2, TS3, TS4, TS5
        # if step == end, returns pattern no, step no, link dest. pattern, 
        # output in case of END 0 or fixed control
        # if repeat pattern output, returns repeat count
        ans = self.read_param(' 1, 3,{0},{1}'.format(pattern_no,step_no))
        return ans
    
    def mode0_execution_parameter_request(self):
        # returns execution target SV, Execution P, Execution I
        # Execution D, Execution AL1, Execution AL2, Execution Al3
        # Execution Al4, Execution OL, Execution OH, Execution variation limit
        # Execution sensor correction
        # second P, second I, Second D
        ans = self.read_param(' 1, 2,')
        return ans
    
    def program_pattern_setting_status_request(self,pattern_no=1):
        # returns pattern no, setting step count (0 = not set)
        ans = self.read_param(' 1, 5,{},'.format(pattern_no))
        return ans
    
    def device_status_request(self):
        # returns controller/setter, setter, output1, output2, transmission, 
        # time signal, external drive, select pattern, time unit
        ans = self.read_param(' 1, 6,')
        return ans
        
    def mode_Lock_status_request(self):
        # returns lock status of each mode
        # FNC key, mode 0, 1, 2, 3, 4, 5, 6, 7, 8
        # 0 = Not locked, 1 = locked
        ans = self.read_param(' 1, 7,')
        return ans
    
    def status1_request(self):
        # returns alarm status: Al1, Al2, Al3, Al4, waiting time alarm, error,
        # TS1, TS2, TS3, TS4, TS5
        # Alarm: 00-off, 01= Alarm on, 10 = waiting alarm OFF
        ans = self.read_param(' 1, 8,')
        return ans
    
    def status2_request(self):
        # something about running program status:
            # run, stop, reset, end, adv, const. 
            # MAN1, MAN2, wait, AT, FNC key lock, M/s
        ans = self.read_param(' 1, 9,')
        return ans
    
    def autoModeSet(self, mode = True, MV1 = 0):
        # MV1 = manual output value
        if mode == True:
            self.write(' 2, 3,0, ,0, ,')
        else:
            self.write(' 2, 3,1,{},0, ,'.format(MV1))
    
    def alarm_cancel_output(self):
        self.write(' 2, 5,')
    
    # AT3 can do automatic PID switching? it is better to try AT3 first
    # AT2 looks like for specific setpoint stabilization (you can set 8 temperatures)
    def AT2_SV(self,parameter_number,status,setTemperature):
        # parameter_number =  1 to 8; 0 --> copy to 1 to 8
        # status = 0(off) or 1(on)
        self.write('45,{0},{1},{2}'.format(parameter_number,status,setTemperature))
    
    def AT3_SV_section(self,parameter_number,delimiterSV): # AT2 or AT3?
        # paramter number = 1 to 7
        self.write('46,{0},{1}'.format(parameter_number,delimiterSV))
    
    def AT3_SV(self,parameter_number,status,setTemperature):
        # parameter_number =  1 to 8; 0 --> copy to 1 to 8
        # status = 0(off) or 1(on)
        self.write('47,{0},{1},{2}'.format(parameter_number,status,setTemperature))
    
    def AT_start_direction(self,direction):
        # direction = 0(UP), 1(down)
        self.write('48,{}'.format(direction))
    
    def SV_during_reset(self,value):
        self.write('49,{}'.format(value))
    
        
    def close(self):
        self.s.close()

    # def continue_program(self):

    # def run_program(self):
            #TODO: make wait time a user defined parameter

    # def stop_program(self):

    # def hold_program(self):