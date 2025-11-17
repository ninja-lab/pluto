# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:17:51 2022

@author: eriki
"""

import pyvisa
import instrument_strings
from datetime import datetime
import Keysight34972A
import time

save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'RLDaqTest'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        
            
             
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        if 'ASRL' in resource_id:
            inst.baud_rate = 115200
            
        name_str = inst.query('*IDN?').strip()
        print(name_str)
        if name_str == instrument_strings.Keysight34970A:
            daq = Keysight34972A.Keysight34972A(inst)

    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        
''' 
temp_chan_scan = '(@117:120)'
#volt_chan_scan = '(@116)'
all_chan = '(@116:120)'

daq.configure_temp_channels(temp_chan_scan)
#daq.configure_DCV_channels(volt_chan_scan)

daq.set_scan(temp_chan_scan)
daq.set_trigger('IMM')

for i in range(5):
    print(daq.read())
    time.sleep(1)
 '''
start = datetime.now() 

def scan_temps():
    for i in range(5):
        seconds_elapsed[i] = (stamp - start).total_seconds()
        daq.measure_temp(117)
        seconds_elapsed[i] = (stamp - start).total_seconds()
        daq.measure_temp(118)
        seconds_elapsed[i] = (stamp - start).total_seconds()
        daq.measure_temp(119)
        seconds_elapsed[i] = (stamp - start).total_seconds()
        daq.measure_temp(120)
    