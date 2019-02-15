# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 12:49:00 2019

@author: Erik
"""

import Keysight34972A
import pyvisa
import instrument_strings

#import plotting

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
        
daq.configure_DCV_channels('(@201:202)')
daq.format_reading(time=1, channel=1)
daq.format_time_type(time_type='ABS')
for i in range(3):
    adict = daq.read_with_absolute_time()
    #   print(adict)
    #data = daq.query('READ?').split(',')
    #print('len: ' + str(len(data)))
    #print('mod8?: ' +str(len(data)%8))
    
daq.configure_DCV_channels('(@201:215)')
daq.format_reading(time=1, channel=1)
daq.format_time_type(time_type='ABS')
for i in range(3):
    adict = daq.read_with_absolute_time()
    #   print(adict)
    #data = daq.query('READ?').split(',')
    #print('len: ' + str(len(data)))
    #print('mod8?: ' +str(len(data)%8))

daq.configure_DCV_channels('(@201:202,204:215)')
daq.format_reading(time=1, channel=1)
daq.format_time_type(time_type='ABS')
for i in range(3):
    adict = daq.read_with_absolute_time()
    #   print(adict)
    #data = daq.query('READ?').split(',')
    #print('len: ' + str(len(data)))
    #print('mod8?: ' +str(len(data)%8))