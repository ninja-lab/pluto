# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 10:47:07 2021

@author: eriki
"""




from __future__ import absolute_import, division, print_function

import sys

'''
Rigol Scope:
'''



from math import sqrt

'''
MCC DAQ IMPORTS:
'''

#from builtins import *  # @UnusedWildImport
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


print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, sensor12, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor13, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor8, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, sensor7, BoardInfo.CHANTCTYPE, TcType.K)



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





