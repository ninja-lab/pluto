# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 11:15:59 2021

@author: eriki
"""
import pyvisa
import Rigol_DP832
import chroma63003
import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.RigolDP832_2:
            dc_supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + dc_supply.name.rstrip('\n'))
        if name_str == instrument_strings.chroma63003:
            load = chroma63003.chroma63003(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
    
    
'''
The Rigol DP832 channel 1 is hooked up to the load
'''

for v in range(1, 10):
    dc_supply.apply(v, 1, channel=1)
    load.set_resistance(500)
    load.turn_on()
    print(f'Supply says i = {dc_supply.get_current(1):.3f}A') 
    print(f'load says i = {load.measure_current():.3f}A')
    print(f'Supply says v = {dc_supply.get_voltage(1):.3f}V')
    print(f'Load says v = {load.measure_voltage():.3f}V')
    print()
    time.sleep(1)
dc_supply.turn_off(1)
load.turn_off()
