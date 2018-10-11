# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 16:14:24 2018

@author: Erik
"""

import pyvisa
import instrument_strings
import InstekPSW
import time

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        print(name_str)
        if name_str == instrument_strings.PSW800:
            dc_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + dc_supply.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
dc_supply.clear_screen()
print('Showing text display')
dc_supply.display_screen('AK  Test')
time.sleep(2)
print('Clearing screen')
dc_supply.clear_screen()
print('Put supply into voltage slew mode')
dc_supply.set_output_mode(2)
print('show voltage and power')
dc_supply.display(1)
dc_supply.apply(100,1)
print('turning on output!')
dc_supply.set_output('ON')
time.sleep(1)
print('show voltage and power')
dc_supply.display(0)
time.sleep(2)
print('turning off output')
dc_supply.set_output('OFF')


