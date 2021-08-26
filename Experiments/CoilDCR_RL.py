# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:25:31 2021

@author: eriki
"""


from __future__ import absolute_import, division, print_function

import pyvisa
import Rigol_DP832

import sdm3045x

from datetime import datetime
import numpy as np
import pandas as pd
from math import sqrt
import time
import instrument_strings
import matplotlib.pyplot as plt

from builtins import *  # @UnusedWildImport

from mcculw import ul

from mcculw.enums import TempScale, InfoType, BoardInfo, TcType
from mcculw.device_info import DaqDeviceInfo


from console_examples_util import config_first_detected_device

use_device_detection = True
dev_id_list = []
board_num = 0      

config_first_detected_device(board_num, dev_id_list)

daq_dev_info = DaqDeviceInfo(board_num)
RLtemp_chanDC = 1
SStemp_chan = 0

print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, RLtemp_chanDC, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, SStemp_chan, BoardInfo.CHANTCTYPE, TcType.K)

def meas_RLtemp_chanDC():
    return ul.t_in(board_num, RLtemp_chanDC, TempScale.CELSIUS)
def meas_SStemp_chanDC():
    return ul.t_in(board_num, SStemp_chan, TempScale.CELSIUS)



save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'RL_DCcal'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()

        if name_str == instrument_strings.RigolDP832:
            supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
        
        elif name_str == instrument_strings.sdm3045x_1:
            meter1 = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter1.name.rstrip('\n'))
        elif name_str == instrument_strings.sdm3045x_2:
            meter2 = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter2.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        
stamps = []
seconds_elapsed = []
vin = []
iin = []
pin = []

RL_temps = []
#SS_temps=[]
thermalcam = []
stamp = datetime.now()
stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))

v = meter2.measure_voltage()
i = meter1.measure_current()
vin.append(v)
iin.append(i)
pin.append(v*i)
t = meas_RLtemp_chanDC()
RL_temps.append(t)
cam = input('what does the camera say?\n')
thermalcam.append(float(cam))

supply.apply(5, 0,3)
supply.turn_on(3)


for i in np.linspace(.4, 1.6, 10):
    supply.apply(5, i,3)
    print('sleeping')
    time.sleep(40)

    print(i)
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    #seconds_elapsed.append((stamp - start).seconds)
    v= meter2.measure_voltage()
    i = meter1.measure_current()
    vin.append(v)
    iin.append(i)
    p = v*i
    pin.append(p)
    
    t = meas_RLtemp_chanDC()
    RL_temps.append(t)
    print(f'v={v:.3f}, i={i:.3f}, p={p:.3f}, t={t:.3f}')
    cam = input('what does the camera say?\n')
    thermalcam.append(float(cam))
    
    time.sleep(3)
    
     
supply.turn_off(3)

df = pd.DataFrame(data = {'time': stamps, 'vin': vin, 'iin':iin, 'pin':pin,
                          'RLtemps':RL_temps, 'thermalcam':thermalcam})
df.to_csv(path_or_buf=filename)