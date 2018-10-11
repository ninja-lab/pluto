# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 14:43:29 2018

@author: Erik

SETUP:
    multifunction module 34907A in slot 1
    20 channel multiplexer in slot 2
    
    34907A CH4 to (@201)
    First two bits of Digital Port1/Ch1 go to (@202), (@203)
"""

import Keysight34972A
import pyvisa
import instrument_strings
import random
import time


rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")


for i in range(20):
    voltage = round(random.random()*12, 3)
    daq.analog_source(104, voltage)
    print('Supplying {} volts'.format(voltage))
    readback = round(daq.measure_DCV(201),3)
    print('Read back: {}V'.format(readback))
    time.sleep(2)

for i in range(4):
    bit0 = round(random.random())
    bit1 = round(random.random())
    print("Byte before: {:#010b}".format(daq.byte1))
    print("Set bit 0 to: {}".format(bit0))
    print("Set bit 1 to: {}".format(bit1))
    daq.digital_source1(101, 0, bit0)
    daq.digital_source1(101, 1, bit1)
    print("Byte after: {:#010b}".format(daq.byte1))
    print("Bit 0 measures: {:.1f}".format(daq.measure_DCV(202)))
    print("Bit 1 measures: {:.1f}".format(daq.measure_DCV(203)))
    print()
    time.sleep(1)
    

    