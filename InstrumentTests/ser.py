# -*- coding: utf-8 -*-
"""
Created on Thu May 27 16:56:25 2021

@author: eriki
"""

import serial

import time

port = 'com4'
baud = 19200
conn = serial.Serial(port, baud, timeout=.2, parity=serial.PARITY_NONE)
conn.write(b'*IDN?\n')
time.sleep(.25)
#print(conn.read(70))
print(conn.read_until())                     
                     