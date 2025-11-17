# -*- coding: utf-8 -*-
"""
Created on Mon May 31 13:11:02 2021

@author: eriki
"""


from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul

from mcculw.enums import TempScale, InfoType, BoardInfo, TcType
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device

import pyvisa
import Rigol_DP832
import bk8614
import sdm3045x
import sl600
from datetime import datetime
import numpy as np
import pandas as pd
from math import sqrt
import time
import instrument_strings
import matplotlib.pyplot as plt
save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'BuckConverter'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        if resource_id.find('ASRL') != -1:
            inst.baud_rate = 19200
            inst.read_termination = '\r\n'
            inst.write_termination = '\r\n'
            
        name_str = inst.query('*IDN?').strip()
        if name_str == instrument_strings.bk8614:
            load = bk8614.bk8614(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.sl600:
            supply = sl600.sl600(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
        elif name_str == instrument_strings.sdm3045x:
            meter = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
use_device_detection = True
dev_id_list = []
board_num = 0      

config_first_detected_device(board_num, dev_id_list)

daq_dev_info = DaqDeviceInfo(board_num)
fet1_chan = 0
fet2_chan = 1
hs1_chan = 2
hs2_chan = 3
print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, fet1_chan, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, fet2_chan, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, hs1_chan, BoardInfo.CHANTCTYPE, TcType.J)
ul.set_config(InfoType.BOARDINFO, board_num, hs2_chan, BoardInfo.CHANTCTYPE, TcType.J)

def meas_tempfet1():
    return ul.t_in(board_num, fet1_chan, TempScale.CELSIUS)
def meas_tempfet2():
    return ul.t_in(board_num, fet2_chan, TempScale.CELSIUS)
def meas_hs1():
    return ul.t_in(board_num, hs1_chan, TempScale.CELSIUS)
def meas_hs2():
    return ul.t_in(board_num, hs2_chan, TempScale.CELSIUS)
# Display the value
print('Channel', fet1_chan, 'Value (deg C):', meas_tempfet1())
print('Channel', fet2_chan, 'Value (deg C):', meas_tempfet2())
print('Channel', hs1_chan, 'Value (deg C):', meas_hs1())
print('Channel', hs2_chan, 'Value (deg C):', meas_hs2())

stamps = []
seconds_elapsed = []
vin = []
iin = []
vout = []
iout = []
tempfet1 = []
tempfet2 = []
hs1 = []
hs2 = []
freqs = []
supply.source(100, 5)
supply.turn_on()
time.sleep(2)
load.set_current(3)
load.turn_on()
start = datetime.now()
while True:
    
    
    val = input('q to quit, or switching frequency: ')
    if val == 'q':
        supply.source(0, .2)
        supply.turn_off()
        load.turn_off()
        break
    else:
        freq = float(val)
        
    freqs.append(freq)
 
    val = input('hit any key to take measurement')
    stamp = datetime.now()
    stamps.append(stamp.strftime('%Y-%m-%d %H:%M:%S'))
    seconds_elapsed.append((stamp - start).seconds)
    
    vin.append(meter.measure_voltage())
    iin.append(meter.measure_current())
    vout.append(load.measure_voltage())
    iout.append(load.measure_current())
    t1 = meas_tempfet1()
    t2 = meas_tempfet2()
    t3 = meas_hs1()
    t4 = meas_hs2()
    print('Channel', fet1_chan, 'Value (deg C):', t1)
    print('Channel', fet2_chan, 'Value (deg C):', t2)
    print('Channel', hs1_chan, 'Value (deg C):', t3)
    print('Channel', hs2_chan, 'Value (deg C):', t4)
    tempfet1.append(t1)
    tempfet2.append(t2)
    hs1.append(t3)
    hs2.append(t4)
    
 
    
df = pd.DataFrame(data = {'time': stamps, 'vin': vin, 'iin':iin, 'vout':vout, 'iout':iout,
                          'tempfet1': tempfet1, 'tempfet2': tempfet2, 'hs1': hs1, 'hs2':hs2,
                          'seconds':seconds_elapsed, 'frequency':freqs})
df.to_csv(path_or_buf=filename)