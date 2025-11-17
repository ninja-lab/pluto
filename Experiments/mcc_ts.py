# -*- coding: utf-8 -*-
"""
Created on Mon May 31 10:28:58 2021

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
#ul.set_config(InfoType.BOARDINFO, board_num, fet2_chan, BoardInfo.CHANTCTYPE, TcType.K)
#ul.set_config(InfoType.BOARDINFO, board_num, hs1_chan, BoardInfo.CHANTCTYPE, TcType.J)
#ul.set_config(InfoType.BOARDINFO, board_num, hs2_chan, BoardInfo.CHANTCTYPE, TcType.J)
# Get the value from the device (optional parameters omitted)
#value = ul.t_in(board_num, tempfet1, TempScale.CELSIUS)
def meas_tempfet1():
    
    return ul.t_in(board_num, fet1_chan, TempScale.CELSIUS)
'''
def meas_tempfet2():
    return ul.t_in(board_num, fet2_chan, TempScale.CELSIUS)
def meas_hs1():
    return ul.t_in(board_num, hs1_chan, TempScale.CELSIUS)
def meas_hs2():
    return ul.t_in(board_num, hs2_chan, TempScale.CELSIUS)
'''
# Display the value
print('Channel', fet1_chan, 'Value (deg C):', meas_tempfet1())
#print('Channel', fet2_chan, 'Value (deg C):', meas_tempfet2())
#print('Channel', hs1_chan, 'Value (deg C):', meas_hs1())
#print('Channel', hs2_chan, 'Value (deg C):', meas_hs2())
#if use_device_detection:
    #ul.release_daq_device(board_num)
stamps = []
vin = []
iin = []
vout = []
iout = []
tempfet1 = []
tempfet2 = []
hs1 = []
hs2 = []

while True:
    val = input('q to quit, or Vin command: ')
    if val == 'q':
  
        break
    else:
        val = float(val)
   
    stamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    tempfet1.append(meas_tempfet1())
    #tempfet2.append(meas_tempfet2())
    #hs1.append(meas_hs1())
    #hs2.append(meas_hs2())
    

