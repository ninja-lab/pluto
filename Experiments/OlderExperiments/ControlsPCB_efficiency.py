# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 13:41:30 2017

@author: Erik

Sweep DC current levels and measure efficiency. 
Sweep switching frequencies and measure efficiency. 

Keysight DAQ allocations:
    101  J15-1 fw_isense RED
    102  input voltage 
    103  output voltage on resistor
    104  output current across 20mOhm resistor RED

    106 input current across 20mOhm resistor WHITE 
    107 thermocouple on inductor
    108 thermocouple on top fet
    109 thermocouple on bottom fet
    
    
"""
import Keysight34972A
import pyvisa
import Rigol_DP832
import Agilent33120
import instrument_strings
import pandas as pd
import numpy as np
from datetime import datetime
import time

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'ControlsPowerTrainEfficiency' + time_stamp
name = title_str
filename = save_loc + name.replace(' ','_') +'.csv'

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        elif name_str == instrument_strings.DP832A:
            DCsupply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + DCsupply.name.rstrip('\n'))
        elif name_str == instrument_strings.FG33120A:
            func_gen = Agilent33120.f33120a(inst)
            print("Connected to: " + func_gen.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

#20mOhm sense resistors with 1% tolerance
rsns_in = 0.0208
rsns_out = 0.0203         

temp_scan = '(@107:109)'
dcv_scan = '(@101:104,106)'
all = '(@101:104,106,107,108,109)'
daq.configure_temp_channels(temp_scan, thermocouple='J')
daq.configure_DCV_channels(dcv_scan)
daq.set_scan(all)
daq.set_delay(.3, all)
daq.set_trigger('IMM')
daq.format_reading()
daq.set_NPLC(20, dcv_scan)
#start switching frequency at 90kHz, ampmlitude and offset to match sync pin i.a.w. datasheet
func_gen.applyFunction('SQU', 100e3, 1.2, .84)
#5A/V command
DCsupply.apply(0, .2, 3)
#1A increments
DCsupply.set_increment(3, .2) 
commands = np.arange(.2, 4.0, .2)
#commands = np.arange(.5, 1.5, .5)
commands = [str(elem) for elem in commands]
#freqs = np.arange(100e3, 140e3, 20e3)
freqs = np.arange(100e3, 550e3, 40e3)
freqs = [str(elem) for elem in freqs]

'''
Data is stored in a pandas dataframe with a multi-index of [f_sw, commands]
'''
index = pd.MultiIndex.from_product([freqs, commands])
columns = ['isense', 'v_in', 'v_out', 'i_out', 'i_in', 'L_temp', 'top_fet_temp', 'bot_fet_temp', 'efficiency', 'command', 'power']
df = pd.DataFrame(index=index, columns= columns)
DCsupply.apply(.2, .2, 3)
for j in commands:
    for i in freqs:
        func_gen.outputFreq(i)
         #sweep bias current points and record all measurements
        data = daq.read()
        #remove offset and scale for the ACS724 current sensor
        data[0] = (data[0] - .5)/.2
        data[3] = data[3]/rsns_out
        data[4] = data[4]/rsns_in
        data.append(data[2]*data[3]/(data[1]*data[4]))
        data.append(float(j))
        data.append(data[2]*data[3])
        data_ = [round(elem, 3) for elem in data]
        df.loc[i, j] = data_
    DCsupply.increment_up(3)
    #save periodically just in case of crashes
    df.to_csv(path_or_buf=filename)
    
    
    
    
    

