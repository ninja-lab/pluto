# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 14:12:23 2018

@author: Erik
"""

from PWRTestIO import *

import Keysight34972A
import InstekPSW
import pyvisa
import instrument_strings
import random
import time
import pandas as pd
import numpy as np
'''
The final deliverable is a dataframe/spreadsheet of all the tests, which details 
the test number, description, measurement value, pass/fail status, margins, and timestamp.
Ultimately, the deliverable can describe how one particular DUT compares to all the others.


'''

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        if name_str == instrument_strings.PSW800:
            hv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + hv_supply.name.rstrip('\n'))
        if name_str == instrument_strings.PSW80V:
            lv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + lv_supply.name.rstrip('\n'))
            
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        
for i in range(10):
    print('Toggling Relays: {}'.format(i))
    open_rl1(daq)
    time.sleep(.1)
    open_rl2(daq)
    time.sleep(.1)
    open_rl3(daq)
    time.sleep(.1)
    open_rl4(daq)
    time.sleep(.1)
    open_rl5(daq)
    time.sleep(.1)
    close_rl1(daq)
    time.sleep(.1)
    close_rl2(daq)
    time.sleep(.1)
    close_rl3(daq)
    time.sleep(.1)
    close_rl4(daq)
    time.sleep(.1)
    close_rl5(daq)
    time.sleep(.1)
print()
print('Testing Load Bank')
for i in range(5):
    load1_off(daq)
    load2_off(daq)
    load3_off(daq)
    print('Toggling Load Bank: {} of 10'.format(i))
    print('Open Circuit:')
    print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    load1_on(daq)
    print('7.5 Ohms:')
    print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    load2_on(daq)
    print('3.75 Ohms:')
    print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    #load3_on(daq)
    #print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    load1_off(daq)
    print('7.5 Ohms:')
    print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    load2_off(daq)
    print('Open Circuit:')
    print('Load: {} Ohms'.format(daq.measure_Resistance(204)))
    #load3_off(daq)
    #print('Load: {} Ohms'.format(daq.measure_Resistance(204)))

print()
print('Testing Cap Discharge')
for j in range(2):
    print('Cycle {}'.format(j))
    for i in np.arange(0,10,1):
        daq.analog_source(104, i)
        time.sleep(.1)
    time.sleep(.5)
    for i in np.arange(10, 0, -1):
        daq.analog_source(104, i)
        time.sleep(.1)
    time.sleep(.5)
    
print()
print('Testing Selected Channels')
close_rl5(daq)
lv_supply.apply(0, .1)
lv_supply.set_output(1)
for i in range(0,24,2):
    lv_supply.apply(i, .1)
    time.sleep(.1)
    print('PSUA: {}'.format(daq.measure_DCV(201)))
    print('PSUB: {}'.format(daq.measure_DCV(202)))
    print('PSUC: {}'.format(daq.measure_DCV(203)))
    
lv_supply.set_output(0)
print()
close_rl1(daq)
open_rl2(daq)

hv_supply.apply(0,.1)
hv_supply.set_output(1)
for i in range(0,200,20):
    hv_supply.apply(i,.5)
    time.sleep(.1)
    print('TP1B: {}'.format(4*daq.measure_DCV(212)))
    print('TP5B: {}'.format(4*daq.measure_DCV(211)))
hv_supply.set_output(0)
    

