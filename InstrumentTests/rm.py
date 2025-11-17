# -*- coding: utf-8 -*-
"""
Created on Thu May 27 15:27:05 2021

@author: erik
"""

import pyvisa
import time

rm = pyvisa.ResourceManager()
#rm = pyvisa.ResourceManager('C:\\Windows\\system32\\visa64.dll')

print(rm.list_resources())
#s = rm.open_resource('ASRL4::INSTR')
#s.baud_rate = 19200
#s.read_termination = '\r\n'
#s.write_termination = '\r\n'
#s.query('*IDN?') #tried with \n too, it just times out
#print(s.query('*IDN?'))

meter = rm.open_resource(rm.list_resources()[1])
print(meter.query('*IDN?'))