# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:11:19 2021

@author: Erik.Iverson
"""


import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
from Fluke8845A import Fluke8845A




rm = pyvisa.ResourceManager('C:\\Windows\\System32\\visa64.dll')
for resource_id in rm.list_resources():
    try:

        inst = rm.open_resource(resource_id,send_end=True, 
                                baud_rate=230400)#,
                                #parity=pyvisa.constants.Parity.even)#,
                                #stop_bits=pyvisa.constants.StopBits.two,
                                #serialtermination=pyvisa.constants.SerialTermination.none) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.DMM8845A:
            dmm = Fluke8845A(inst)
            
            print("Connected to: " + dmm.name.rstrip('\n'))
            break
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

'''
There are n (5?) sensors to characterize

For each one - log k samples at known calibration weights in the jig

Desired:
    1. plot each sensor resistance (all samples) at known weights (time info between samples 
    is not important). This will #weights plots with n curves per plot
    
    2. plot max, avg, min curves against known weights, one plot per sensor, 3 curves per plot
    
    

'''

save_loc = 'C:\\Users\\Erik.Iverson\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'FSR8_'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'

this_sensor = pd.DataFrame()
#this_sensor = results = pd.read_csv(os.path.join(save_loc, filename), index_col=0)
dmm.configure_res(nplcs=1, samples=100, delay=.1)
time.sleep(.1)
dmm.set_trigger('IMM')
time.sleep(.1)
delay = dmm.compute_delay()
for i in [0,15.7,33.1,33.7,34.8,35.2,81.5,114.8,
          211.6,229.4,329.4,425.3,444.8,525.3,543.1,838.1]:
# for i in [211.6,229.4,329.4,425.3,444.8]:   
    weight = input('put on {}g and hit enter'.format(i))
    print('delay should be {} seconds'.format(delay))
    dmm.initiate()
    time.sleep(delay)
    print('trying to get data now')
    data = dmm.fetch()
    this_sensor['{}g'.format(i)] = data
this_sensor.to_csv(path_or_buf=filename)

#take 100 samples at each weight
#each weight gets a column in the dataframe
