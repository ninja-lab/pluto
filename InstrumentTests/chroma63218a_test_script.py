# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 10:51:17 2022

@author: eriki
"""

import pyvisa
import Rigol_DP832
import chroma63218a 

import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.chroma63218a:
            load = chroma63218a.chroma63218a(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.RigolDP832_3:
            supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
supply_chan = 2
print('executing test')
supply.apply(30, 3, supply_chan)
supply.turn_on(supply_chan)
load.set_mode('CRM')
load.set_resistance(50)
print(f'supply says Vout = {supply.get_voltage(supply_chan)}')

print('turning load on')
load.turn_on()
time.sleep(2)
print(f'supply says Iout = {supply.get_current(supply_chan)}')
print(f'load says Iin = {load.measure_current()}')
time.sleep(.5)
print('turning off load')
load.turn_off()
print(f'supply says Iout = {supply.get_current(supply_chan)}')
time.sleep(.5)
print('setting load to constant current 2.4A and turning on')
load.set_mode('CCL')
load.set_load_current(2.5)
load.turn_on()
time.sleep(3)
print(f'supply says Iout = {supply.get_current(supply_chan)}')
print(f'load says Iin = {load.measure_current()}')
print(f'load says Vin = {load.measure_voltage()}')


supply.turn_off(supply_chan)
load.turn_off()