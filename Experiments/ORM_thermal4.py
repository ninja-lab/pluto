# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 10:03:50 2022

@author: eriki
"""




from __future__ import absolute_import, division, print_function

import sys

'''
Rigol Scope:
'''

import time
import pyvisa
import re
from datetime import datetime
import instrument_strings
import numpy as np
import pandas as pd
import sdm3045x
import dl3031a
import it6933a
import Keysight34972A
from math import sqrt

'''
MCC DAQ IMPORTS:
'''


'''
SENSORS
1. coil thermistor PS103J2
2. coil shielded junction, shielded cable, JTSS-M15U-300
3. coil unsheilded 5TC-TT-K-40-36-ROHS type K
4. high side diode D5-HBa1 shielded junction, shielded cable type J
5. coil shielded junction, shielded cable, 5TC-TT-K-40-36-ROHS type K
6. coil unshielded junction, shielded cable 5TC-TT-K-40-36-ROHS type K
7. high side diode D5_HBa2 5TC-TT-K-40-36-ROHS type K
7. under board next to U16_HBa1 (sensor 11)
8. unshielded back of aluminum, type K Reed 
9. thermistor back of aluminum PS103J2
10. TP25 SW1_temp (bottom half)
11. TP31 SW4_temp (top half)
12. D6_HBa1 cathode unsheilded 5TC-TT-K-40-36-ROHS type K
13. D6HBa2 cathode  unsheilded 5TC-TT-K-40-36-ROHS type K


'''
#MCC DAQ channels

sensor12 = 0
sensor13 = 1
sensor8 = 3
sensor7 = 2
sensor10 = 2
sensor11 = 3


'''
end MCC set up
'''


rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
                   
        if 'ASRL' in resource_id:
            inst.baud_rate = 115200
            
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.sdm3045x_3:
            meter = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter.name.rstrip('\n'))
        if name_str == instrument_strings.RigolDL3031A:
            load = dl3031a.dl3031a(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.itech6953A:
            supply = it6933a.it6933a(inst)
            print("Connected to: " + supply.name.rstrip('\n'))

        if name_str == instrument_strings.Keysight34970A:
            daq = Keysight34972A.Keysight34972A(inst)
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")


def meas_sensor8():
    return daq.measure_temp(117)
def meas_sensor12():
    return daq.measure_temp(118)
def meas_sensor13():
    return daq.measure_temp(119)
def meas_sensor7():
    return daq.measure_temp(120)
#def meas_sensor6():
#    return round(ul.t_in(board_num, sensor6, TempScale.CELSIUS), 2)
def meas_sensor1():
    return meter.measure_resistance()
def meas_sensor10():
    Rtop = 74.24e3
    Rbot = 74.19e3
    v = daq.measure_DCV(115)
    return t(v*(1+Rtop/Rbot))

def meas_sensor11(): 
    Rtop = 74.48e3
    Rbot = 74.03e3
    v = daq.measure_DCV(116)
    return t(v*(1+Rtop/Rbot))

def t(v):
    return -1481.96 + sqrt(2.1962e6 + (1.8639 - v)/3.88e-6)

save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'ORMthermal1'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'


'''
Only change these next two variables
'''
rampuptime = 10 #seconds
rampdowntime = 4 #seconds
numtempchannels = 4 
numdcvchannels = 2
temp_sampling_time = 133e-3 #seconds
dcv_sampling_time = 288e-3  #seconds
sampling_time = temp_sampling_time*numtempchannels+dcv_sampling_time*numdcvchannels 

dwelltime = 0
rampupsamples = int(rampuptime/sampling_time)
rampdownsamples = int(rampdowntime/sampling_time)
quiescent_samples = 0
est_samples = rampupsamples+rampdownsamples+quiescent_samples


sensor7data = np.zeros(est_samples)
sensor12data = np.zeros(est_samples)
sensor8data = np.zeros(est_samples)
sensor13data = np.zeros(est_samples)
sensor10data = np.zeros(est_samples)
sensor11data = np.zeros(est_samples)

sensor7time = np.zeros(est_samples)
sensor12time = np.zeros(est_samples)
sensor8time = np.zeros(est_samples)
sensor13time = np.zeros(est_samples)
sensor10time = np.zeros(est_samples)
sensor11time = np.zeros(est_samples)


voutdata = np.zeros(est_samples)
ioutdata = np.zeros(est_samples)
vindata = np.zeros(est_samples)
iindata = np.zeros(est_samples)

start = datetime.now()
#load.turn_off()

#get quiescent values first 
for i in range(est_samples):
    
    sensor7data[i] = meas_sensor7()
    sensor7time[i] = (datetime.now() - start).total_seconds()
    
    sensor12data[i] = meas_sensor12()
    sensor12time[i] = (datetime.now() - start).total_seconds()
    
    sensor8data[i] = meas_sensor8()
    sensor8time[i] = (datetime.now() - start).total_seconds()
    
    sensor13data[i] = meas_sensor13()
    sensor13time[i] = (datetime.now() - start).total_seconds()
    
    sensor10data[i] = meas_sensor10()
    sensor10time[i] = (datetime.now() - start).total_seconds()
    
    sensor11data[i] = meas_sensor11()
    sensor11time[i] = (datetime.now() - start).total_seconds()
    
    print(f'i = {i}')
    print(f'sensor7: {sensor7data[i]:.2f}')
    print(f'sensor12: {sensor12data[i]:.2f}')
    print()

    time.sleep(.1)



    
df = pd.DataFrame(data = {'sensor7':sensor7data, 'sensor7time': sensor7time,
                          'sensor12':sensor12data, 'sensor12time': sensor12time,
                          'sensor8':sensor8data, 'sensor8time': sensor8time,
                          'sensor10':sensor10data, 'sensor10time': sensor10time,
                          'sensor11':sensor11data,'sensor11time': sensor11time,
                          'sensor13':sensor13data,'sensor13time': sensor13time,
                           'vin': vindata, 'iin': iindata,
                          'vout': voutdata, 'iout': ioutdata})
df.to_csv(path_or_buf=filename)