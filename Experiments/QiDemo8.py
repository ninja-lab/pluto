# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 14:56:11 2021

@author: eriki
"""


from __future__ import absolute_import, division, print_function

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QTimer
'''
Rigol Scope:
'''
from rigol_ds1054z import rigol_ds1054z
import time
import pyvisa
import re
from datetime import datetime
import instrument_strings
import numpy as np
import pandas as pd

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
SS_temp_chanAC = 0
ambient_chan = 1
'''
end MCC set up
'''


print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
      daq_dev_info.unique_id, ')\n', sep='')
ul.set_config(InfoType.BOARDINFO, board_num, SS_temp_chanAC, BoardInfo.CHANTCTYPE, TcType.K)
ul.set_config(InfoType.BOARDINFO, board_num, ambient_chan, BoardInfo.CHANTCTYPE, TcType.K)

def meas_SS_temp():
    return ul.t_in(board_num, SS_temp_chanAC, TempScale.CELSIUS)
def meas_ambient():
    return ul.t_in(board_num, ambient_chan, TempScale.CELSIUS)
def calc_power(vout):
    RLoad = 15.06 #ohms
    return vout**2/RLoad
def calc_loss(temp, ambient):
    theta = 14.284 # C/W
    return (temp-ambient) / theta

save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'SS_AC'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'


qtCreatorFile = "Qi4.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow, Ui_MainWindow):
    
    SS_loss = pyqtSignal(float)
    SS_power = pyqtSignal(float)

    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 400, 400)
        self.timer = QTimer()
        self.timer.setInterval(1000) #mSec
        self.timer.timeout.connect(self.update_vals)
        
   
        self.SS_loss.connect(self.SS_LossLCD.display)
        self.SS_power.connect(self.SS_PowerLCD.display)

        
        self.voltages = np.linspace(10, 30, 10)
        self.i = 0
        
        
        ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
        rm = pyvisa.ResourceManager()
        tup =  rm.list_resources()
        
        for resource_id in tup :
            try:
                inst = rm.open_resource(resource_id, send_end=True )
                print('hi')
                name_str = inst.query('*IDN?').strip()
                if ScopePattern.match(name_str) is not None:
                    print(name_str)
                    self.scope = rigol_ds1054z(inst)
                    print('Connected to: {}'.format(name_str))

            except pyvisa.errors.VisaIOError:
                pass
        #sw node is channel 1
        self.scope.setup_channel(channel=1,on=1,offset_divs=-2.0, volts_per_div=10.0)
        #Vout channel 
        self.scope.setup_channel(channel=2,on=1,offset_divs=0,volts_per_div=10.0)
        #transmit current channel
        self.scope.setup_channel(channel=3,on=1,offset_divs=0,volts_per_div=2.0, probe=1)
        self.scope.setup_timebase(time_per_div='5us',delay='0us')
        self.scope.setup_mem_depth(memory_depth=6e3)
        self.scope.setup_trigger(channel=1,slope_pos=1,level='5v')
        self.scope.repeat_trigger()
        
  
        self.timer.start()
    
    def update_vals(self):

        SSrms = self.scope.get_measurement(channel=2, meas_type=self.scope.rms_voltage)
        self.SS_power.emit(round(calc_power(SSrms),3))
        tcoil = meas_SS_temp()
        tamb = meas_ambient()
        self.SS_loss.emit(round(calc_loss(tcoil, tamb),3))
                          
  
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()
   
    #connect the signals to the slots
   
    sys.exit(app.exec_())
