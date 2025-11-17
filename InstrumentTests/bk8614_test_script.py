# -*- coding: utf-8 -*-
"""
Created on Thu May 20 14:15:36 2021

@author: eriki
"""

import pyvisa
import Rigol_DP832
import bk8614

import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.bk8614:
            load = bk8614.bk8614(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.RigolDP832:
            supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

print('executing test')
supply.apply(5, 2)
supply.turn_on(1)
load.set_resistance(100)
print(f'supply says Vout = {supply.get_voltage(1)}')
print('turning load on')
load.turn_on()
time.sleep(2)
print(f'supply says Iout = {supply.get_current(1)}')
print(f'load says Iin = {load.measure_current()}')
time.sleep(.5)
print('turning off load')
load.turn_off()
print(f'supply says Iout = {supply.get_current(1)}')
time.sleep(.5)
print('setting load to constant current 1A and turning on')
load.set_current(1)
load.turn_on()
time.sleep(2)
print(f'supply says Iout = {supply.get_current(1)}')
print(f'load says Iin = {load.measure_current()}')
print(f'load says Vin = {load.measure_voltage()}')
supply.turn_off(1)
load.turn_off()
