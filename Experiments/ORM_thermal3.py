# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:09:22 2022

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
from math import sqrt

'''
MCC DAQ IMPORTS:
'''

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import TempScale, InfoType, BoardInfo, TcType, AiChanType, ULRange
from mcculw.device_info import DaqDeviceInfo
print(sys.path)
sys.path.append('C:\GitRepos\mcculw\examples\console')
print(sys.path)
#try:
from console_examples_util import config_first_detected_device
#except ImportError:
#    from .console_examples_util import config_first_detected_device

use_device_detection = True
dev_id_list = []
board_num = 0      

config_first_detected_device(board_num, dev_id_list)
daq_dev_info = DaqDeviceInfo(board_num)
'''
SENSORS
1. coil thermistor PS103J2
2. coil shielded junction, shielded cable, JTSS-M15U-300
3. coil unsheilded 5TC-TT-K-40-36-ROHS type K
4. high side diode D5-HBa1 shielded junction, shielded cable type J
5. coil shielded junction, shielded cable, 5TC-TT-K-40-36-ROHS type K
6. coil unshielded junction, shielded cable 5TC-TT-K-40-36-ROHS type K
7. high side diode D5_HBa2 5TC-TT-K-40-36-ROHS type K
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

def ramp_to_vin(target_vin):
    current_vin = supply.measure_voltage()
    difference = target_vin - current_vin
    step_voltage = 5
    num_steps = int(np.abs(difference/step_voltage))
    print(f'difference = {difference}')
    print(f'numsteps = {num_steps}')
    for i in np.linspace(current_vin, target_vin,num_steps):
        print(f'commanding {i}\n')
        supply.apply(i, 4)
        current_vin = supply.measure_voltage()
        if 0 < current_vin < 15:
            correct_iout(7)
            continue
        if 15<= current_vin < 30:
            correct_iout(10)
            continue
        if 30 <= current_vin <= 50: 
            correct_iout(25)
            continue
        if 50 <= current_vin: 
            correct_iout(30)
            continue
        time.sleep(.5)
    return

def correct_iout(target_vout):

    current_increment = .1
    current_iout = load.measure_current()
    current_vout = load.measure_voltage()
    while np.abs(current_vout - target_vout) > 3:
        print(f'current vout = {current_vout}')
        sign = np.sign(current_vout - target_vout)
        #increase current if current_vout > target_vout
        new_iout = max(min(current_iout + sign*current_increment, 1), 0)
        print(f'commanding {new_iout}A')
        load.set_current(new_iout)
        time.sleep(.05)
        current_iout = load.measure_current()
        current_vout = load.measure_voltage()
        
    
    
    
print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, sensor12, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor13, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor8, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor7, BoardInfo.CHANTCTYPE, TcType.K)

rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
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
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

ai_info = daq_dev_info.get_ai_info()
ai_range = ai_info.supported_ranges[0]
def meas_sensor8():
    return round(ul.t_in(board_num, sensor8, TempScale.CELSIUS), 2)
def meas_sensor12():
    return round(ul.t_in(board_num, sensor12, TempScale.CELSIUS), 2)
def meas_sensor13():
    return round(ul.t_in(board_num, sensor13, TempScale.CELSIUS), 2)
def meas_sensor7():
    return round(ul.t_in(board_num, sensor7, TempScale.CELSIUS), 2)
#def meas_sensor6():
#    return round(ul.t_in(board_num, sensor6, TempScale.CELSIUS), 2)
def meas_sensor1():
    return meter.measure_resistance()
def meas_sensor10():
    Rtop = 74.24e3
    Rbot = 74.19e3
    v = ul.v_in(board_num, sensor10,  ULRange.BIP10VOLTS)
    return t(v*(1+Rtop/Rbot))

def meas_sensor11(): 
    Rtop = 74.48e3
    Rbot = 74.03e3
    v = ul.v_in(board_num, sensor11,  ULRange.BIP10VOLTS)
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
ramptime = 9
fast_sampling_time = 10 #sample really fast for 10 seconds after turnoff
#######
numchannels = 6
sampletime = numchannels*7e-3 #7ms/sample to poll a single channel , 3 channels used
fastdwelltime = 50e-3 #sleep time in each loop
slowdwelltime = 500e-3
num_fast_samples = fast_sampling_time / (sampletime+fastdwelltime)
num_slow_samples = 2*ramptime / (sampletime + slowdwelltime) 
est_samples = int(num_fast_samples + num_slow_samples)
quiescent_samples = 5
rampsamples = int((est_samples-quiescent_samples)/2)

sensor7data = np.zeros(est_samples)
sensor12data = np.zeros(est_samples)
sensor8data = np.zeros(est_samples)
sensor13data = np.zeros(est_samples)
sensor10data = np.zeros(est_samples)
sensor11data = np.zeros(est_samples)
seconds_elapsed = np.zeros(est_samples)
voutdata = np.zeros(est_samples)
ioutdata = np.zeros(est_samples)
vindata = np.zeros(est_samples)
iindata = np.zeros(est_samples)
stamps = np.ndarray(est_samples, dtype=object)
start = datetime.now()
load.set_slew(.2)
load.set_range()
load.set_current(.05)
load.turn_on()
supply.apply(0, 4)
supply.turn_on()
ramp_to_vin(35)
for i in range(quiescent_samples):
 
    sensor7data[i] = meas_sensor7()
    sensor12data[i] = meas_sensor12()
    sensor8data[i] = meas_sensor8()
    sensor13data[i] = meas_sensor13()
    sensor10data[i] = meas_sensor10()
    sensor11data[i] = meas_sensor11()
 #6.4ms
    print(f'i = {i}')
    print(f'sensor7: {sensor7data[i]:.2f}')
    print(f'sensor12: {sensor12data[i]:.2f}')
    print()
    stamp = datetime.now()
    stamps[i] = stamp.strftime('%Y-%m-%d %H:%M:%S')
    seconds_elapsed[i] = (stamp - start).total_seconds()
    time.sleep(.1)

ramp_to_vin(0)
supply.apply(0, 4)
supply.turn_off()    
load.turn_off()

for i in range(quiescent_samples, quiescent_samples+rampsamples):
    stamp = datetime.now()
    sensor7data[i] = meas_sensor7() #7ms
    sensor12data[i] = meas_sensor12() #7ms
    sensor8data[i] = meas_sensor8() #7ms
    sensor13data[i] = meas_sensor13() #7ms
    sensor10data[i] = meas_sensor10() #4ms
    sensor11data[i] = meas_sensor11() #4ms
    voutdata[i] = load.measure_voltage() # .5ms
    ioutdata[i] = load.measure_current() # .5ms
    vindata[i] = supply.measure_voltage() #6.6ms
    iindata[i] = supply.measure_current() #6.4ms
    #all queries together take 57ms
    print(f'i = {i} of {rampsamples}')
    print(f'sensor7: {sensor7data[i]:.2f}')
    print(f'sensor12: {sensor12data[i]:.2f}')
    print()
    
    
    stamps[i] = stamp.strftime('%Y-%m-%d %H:%M:%S')
    seconds_elapsed[i] = (stamp - start).total_seconds()
    time.sleep(slowdwelltime)



for i in range(quiescent_samples + rampsamples, est_samples):
    stamp = datetime.now()
    sensor7data[i] = meas_sensor7()
    sensor12data[i] = meas_sensor12()
    sensor8data[i] = meas_sensor8()
    sensor13data[i] = meas_sensor13() #7ms
    sensor10data[i] = meas_sensor10() #4ms
    sensor11data[i] = meas_sensor11() #4ms
    print(f'i = {i}')
    print(f'sensor7: {sensor7data[i]:.2f}')
    print(f'sensor12: {sensor12data[i]:.2f}')
    print()
    
    stamps[i] = stamp.strftime('%Y-%m-%d %H:%M:%S')
    seconds_elapsed[i] = (stamp - start).total_seconds()
    if (i-(quiescent_samples + rampsamples)) > num_fast_samples:
        time.sleep(slowdwelltime)
    else: 
        time.sleep(fastdwelltime)
    



    
df = pd.DataFrame(data = {'time': stamps, 'sensor7':sensor7data, 
                          'sensor12':sensor12data, 'sensor8':sensor8data,
                          'sensor10':sensor10data, 'sensor11':sensor11data,
                          'sensor13':sensor13data,
                           'vin': vindata, 'iin': iindata,
                          'vout': voutdata, 'iout': ioutdata,
                          'seconds':seconds_elapsed})
df.to_csv(path_or_buf=filename)