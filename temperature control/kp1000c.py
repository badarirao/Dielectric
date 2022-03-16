# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 12:15:20 2021
program for Keithley 6512 programmable electrometer
@author: badar
"""

from time import sleep
import serial
import re
import operator
from functools import reduce
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


class Chino(object):
    def __init__(self, serial_device, baudrate=19200):
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

    def read_param(self, param):
        self.write_param(param)
        answer = self.s.read(200).decode('UTF-8')
        sleep(0.1)
        if answer[0] == ACK:
            return 'Accepted'
        elif answer[0] == NAK:
            return 'Not accepted:', answer[1:3]
        elif checksum(answer[1:-5]) == answer[-4:-2]:
            return answer[1:-5]
        else:
            print("Some Problem in output")

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
        answer = self.s.write(bytes(mes, 'UTF-8'))
        sleep(0.1)

    def real_data_request(self):
        self.data = self.read_param(' 1, 1,')
        temp = self.data.split(',')
        self.pattern_no = int(temp[1].replace(" ", ""))
        self.step_no = int(temp[2].replace(" ", ""))
        self.pv_status = int(temp[3].replace(" ", ""))
        self.PV = float(temp[4].replace(" ", ""))
        self.SV = float(temp[5].replace(" ", ""))
        self.time_display_system = int(temp[6].replace(" ", ""))
        self.time_unit = int(temp[7].replace(" ", ""))
        self.time = temp[8].replace(" ", "")  # hours/minutes
        self.status = int(temp[9].replace(" ", ""))
        self.MV1 = float(temp[10].replace(" ", ""))

    def get_current_temperature(self):
        self.real_data_request()
        return float(self.PV)

    def get_set_temperature(self):
        self.read_data_request()
        return float(self.SV)

    def all_modes_lock(self):
        self.read_param(' 2, 7,1,1,1,1,1,1,1,1,1,1,')

    def all_modes_unlock(self):
        self.read_param(' 2, 7,0,0,0,0,0,0,0,0,0,0,')

    def program_drive(self, task, pattern_no):
        self.write_param(' 2, 1, {0}, {1},'.format(task, pattern_no))

    def set_temperature(self, t):  # temperature t is in Kelvin
        self.read_param(' 2, 4,1,{0}'.format(t))

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

    def load_settings(self):
        self.params = []
        with open(self.filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                lp = line.split()
                if self.isfloat(lp[0]):
                    self.params.append([float(lp[1]), float(
                        lp[2]), float(lp[3]), float(lp[4]), int(lp[5])])

    # def continue_program(self):

    # def run_program(self):

    # def stop_program(self):

    # def hold_program(self):
