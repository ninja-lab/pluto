# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 09:12:06 2018

@author: Erik


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
        if name_str == instrument_strings.PSW800:
            hv_supply = PSW800.PSW800(inst)
            print("Connected to: " + dc_supply.name.rstrip('\n'))
        if name_str == instrument_strings.PSW80V:
            lv_supply = PSW
            
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")