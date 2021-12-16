# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:52:57 2021

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
12. D6_HBa1 cathode
13. D6HBa2 cathode 


'''
#MCC DAQ channels

sensor12 = 0
sensor13 = 1
#sensor4 = 2
sensor7 = 2
sensor10 = 2
sensor11 = 3


'''
end MCC set up
'''


print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, sensor12, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor13, BoardInfo.CHANTCTYPE, TcType.K)
#ul.set_config(InfoType.BOARDINFO, board_num, sensor4, BoardInfo.CHANTCTYPE, TcType.J)
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

sensor1data = []
sensor7data = []
sensor10data = []
sensor11data = []
sensor12data = []
sensor13data = []
seconds_elapsed = []
voutdata = []
ioutdata = []
vindata = []
iindata = []
stamps = []
start = datetime.now()
#get quiescent values first 
for i in range(5):
    sensor1data.append(meas_sensor1())
    sensor7data.append(meas_sensor7())
    sensor10data.append(meas_sensor10())
    sensor11data.append(meas_sensor11())
    sensor12data.append(meas_sensor12())
    sensor13data.append(meas_sensor13())
    voutdata.append(0)
    ioutdata.append(0)
    vindata.append(0)
    iindata.append(0)
    print(f'i = {i}')
    print(f'sensor1: {sensor1data[-1]:.2f}')
    print(f'sensor7: {sensor7data[-1]:.2f}')
    print(f'sensor10: {sensor10data[-1]:.2f}')
    print(f'sensor11: {sensor11data[-1]:.2f}')
    print(f'sensor12: {sensor12data[-1]:.2f}')
    print(f'sensor13: {sensor13data[-1]:.2f}')
    print()
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    seconds_elapsed.append((stamp - start).seconds)
    time.sleep(.8)
    
load.set_current(6)
load.turn_on()
time.sleep(1)
supply.apply(150, 2)
supply.turn_on()

for i in range(150):
    sensor1data.append(meas_sensor1())
    sensor7data.append(meas_sensor7())
    sensor10data.append(meas_sensor10())
    sensor11data.append(meas_sensor11())
    sensor12data.append(meas_sensor12())
    sensor13data.append(meas_sensor13())
    voutdata.append(load.measure_voltage())
    ioutdata.append(load.measure_current())
    vindata.append(supply.measure_voltage())
    iindata.append(supply.measure_current())
    print(f'i = {i}')
    print(f'sensor1: {sensor1data[-1]:.2f}')
    print(f'sensor7: {sensor7data[-1]:.2f}')
    print(f'sensor10: {sensor10data[-1]:.2f}')
    print(f'sensor11: {sensor11data[-1]:.2f}')
    print(f'sensor12: {sensor12data[-1]:.2f}')
    print(f'sensor13: {sensor13data[-1]:.2f}')
    print()
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    seconds_elapsed.append((stamp - start).seconds)
    time.sleep(.8)

supply.turn_off()

for i in range(150):
    sensor1data.append(meas_sensor1())
    sensor7data.append(meas_sensor7())
    sensor10data.append(meas_sensor10())
    sensor11data.append(meas_sensor11())
    sensor12data.append(meas_sensor12())
    sensor13data.append(meas_sensor13())
    voutdata.append(0)
    ioutdata.append(0)
    vindata.append(0)
    iindata.append(0)
    print(f'i = {i}')
    print(f'sensor1: {sensor1data[-1]:.2f}')
    print(f'sensor7: {sensor7data[-1]:.2f}')
    print(f'sensor10: {sensor10data[-1]:.2f}')
    print(f'sensor11: {sensor11data[-1]:.2f}')
    print(f'sensor12: {sensor12data[-1]:.2f}')
    print(f'sensor13: {sensor13data[-1]:.2f}')
    print()
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    seconds_elapsed.append((stamp - start).seconds)
    time.sleep(.8)
    
load.turn_off()


    
df = pd.DataFrame(data = {'time': stamps, 'sensor1':sensor1data,'sensor7':sensor7data, 'sensor10': sensor10data,
                          'sensor11': sensor11data,'sensor12':sensor12data, 
                          'sensor13':sensor13data, 'vin': vindata, 'iin': iindata,
                          'vout': voutdata, 'iout': ioutdata,
                          'seconds':seconds_elapsed})
df.to_csv(path_or_buf=filename)