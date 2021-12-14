# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 10:28:23 2021

@author: eriki
"""

# -*- coding: utf-8 -*-
"""
Created on Thu May 20 14:15:36 2021

@author: eriki
"""

import pyvisa
import dl3031a
import it6933a

import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.RigolDL3031A:
            load = dl3031a.dl3031a(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.itech6933A:
            supply = it6933a.it6933a(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
'''
supply.display_text('RESONATE')
time.sleep(2)
supply.display_text('AAAAAAAAAAAA')
time.sleep(2)
supply.display_text('BBBBBBBBBBBB')
time.sleep(2)
supply.clear_text()
'''
vcomm = 10
ilimit = 2
supply.apply(vcomm, ilimit)
supply.turn_on()
time.sleep(2)
vmeas = load.measure_voltage()
print(f'Commanded: {vcomm}V')
print(f'Measured: {vmeas}V')
print(f'Supply says: {supply.measure_voltage()}V')

load.set_current(1)
load.turn_on()
time.sleep(2)
imeas = load.measure_current()
print(f'Load says: {imeas}A')
time.sleep(2)
load.turn_off()
supply.turn_off()

vcomm = 100
ilimit = 2
supply.apply(vcomm, ilimit)
supply.turn_on()
time.sleep(2)
vmeas = load.measure_voltage()
print(f'Commanded: {vcomm}V')
print(f'Measured: {vmeas}V')
print(f'Supply says: {supply.measure_voltage()}V')

load.set_current(1)
load.turn_on()
time.sleep(5)
imeas = load.measure_current()
print(f'Load says: {imeas}A')
load.turn_off()
supply.turn_off()
