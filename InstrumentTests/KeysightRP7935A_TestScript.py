# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 13:04:33 2022

@author: eriki
"""


import pyvisa
import KeysightRP7935A
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
        elif name_str == instrument_strings.KeysightRP7935A:
            supply = KeysightRP7935A.KeysightRP7935A(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
def test1():
    print('executing test')
    supply.set_voltage(30)
    supply.set_current(4)
    
    load.set_mode('CRM')
    load.set_resistance(20)
    print('turning load on')
    load.turn_on()
    time.sleep(2)
    
    supply.turn_on()
    time.sleep(1)
    print(f'supply says Vout = {supply.measure_voltage()}')
    print(f'load says Vin = {load.measure_voltage()}')
    print(f'supply says Iout = {supply.measure_current()}')
    print(f'load says Iin = {load.measure_current()}')

    
    time.sleep(2)
    supply.turn_off()
    time.sleep(1)
    print('turning off load')
    load.turn_off()



#print(f'supply says Iout = {supply.measure_current()}')
#time.sleep(.5)
def test2():
    print('setting load to constant current 2.4A and turning on')
    load.set_mode('CCL')
    load.set_load_current(2.5)
    load.turn_on()
    time.sleep(2)
    supply.turn_on()
    time.sleep(1)
    print(f'supply says Vout = {supply.measure_voltage()}')
    print(f'load says Vin = {load.measure_voltage()}')
    print(f'supply says Iout = {supply.measure_current()}')
    print(f'load says Iin = {load.measure_current()}')
    
    supply.turn_off()
    time.sleep(1)
    load.turn_off()
