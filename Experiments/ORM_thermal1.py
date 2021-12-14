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

'''
MCC DAQ IMPORTS:
'''

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import TempScale, InfoType, BoardInfo, TcType
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

'''
#MCC DAQ channels
sensor2 = 0
sensor5 = 1
sensor4 = 2
sensor6 = 3


'''
end MCC set up
'''


print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, sensor2, BoardInfo.CHANTCTYPE, TcType.J)
ul.set_config(InfoType.BOARDINFO, board_num, sensor5, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor4, BoardInfo.CHANTCTYPE, TcType.J)
ul.set_config(InfoType.BOARDINFO, board_num, sensor6, BoardInfo.CHANTCTYPE, TcType.K)


rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.sdm3045x_3:
            meter = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter.name.rstrip('\n'))

    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
 

def meas_sensor2():
    return round(ul.t_in(board_num, sensor2, TempScale.CELSIUS), 2)
def meas_sensor5():
    return round(ul.t_in(board_num, sensor5, TempScale.CELSIUS), 2)
def meas_sensor4():
    return round(ul.t_in(board_num, sensor4, TempScale.CELSIUS), 2)
def meas_sensor6():
    return round(ul.t_in(board_num, sensor6, TempScale.CELSIUS), 2)
def meas_sensor1():
    return meter.measure_resistance()



save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'ORMthermal1'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'

sensor1data = []
sensor2data = []
sensor5data = []
sensor4data = []
sensor6data = []
seconds_elapsed=[]
stamps = []
start = datetime.now()
for i in range(200):
    sensor1data.append(meas_sensor1())
    sensor2data.append(meas_sensor2())
    sensor5data.append(meas_sensor5())
    sensor4data.append(meas_sensor4())
    sensor6data.append(meas_sensor6())
    print(f'i = {i}')
    print(f'sensor1: {sensor1data[-1]:.2f}')
    print(f'sensor2: {sensor2data[-1]:.2f}')
    print(f'sensor5: {sensor5data[-1]:.2f}')
    print(f'sensor4: {sensor4data[-1]:.2f}')
    print(f'sensor6: {sensor6data[-1]:.2f}')

    print()
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    seconds_elapsed.append((stamp - start).seconds)
    time.sleep(.8)
    
df = pd.DataFrame(data = {'time': stamps, 'sensor1':sensor1data, 'sensor2':sensor2data, 
                          'sensor5':sensor5data, 'sensor4':sensor4data, 'sensor6':sensor6data,
                          'seconds':seconds_elapsed})
df.to_csv(path_or_buf=filename)