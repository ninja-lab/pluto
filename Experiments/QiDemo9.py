# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 13:53:43 2021

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
import sdm3045x
import time
import pyvisa
import re
from datetime import datetime
import instrument_strings
import numpy as np
import pandas as pd
from math import exp, log

beta = 3892 #PS103J2 thermistor
r_o = 10e3
t_o = 25
r_inf = r_o*exp(-beta/t_o)


def meas_temp(meter):
    return beta/log(meter.measure_resistance()/r_inf)
    
def calc_power(vout):
    RLoad = 8.4 #ohms
    return round(vout**2/RLoad,3)

save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'RL_AC'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'


qtCreatorFile = "Qi5 - Copy.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow, Ui_MainWindow):
    
    RL_temp = pyqtSignal(float)
    RL_power = pyqtSignal(float)
    SS_temp = pyqtSignal(float)
    SS_power = pyqtSignal(float)

    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 400, 400)
        self.timer = QTimer()
        self.timer.setInterval(1000) #mSec
        self.timer.timeout.connect(self.update_vals)
        
     
        self.RL_temp.connect(self.RL_TempLCD.display)
        self.RL_power.connect(self.RL_PowerLCD.display)
        self.SS_temp.connect(self.SS_TempLCD.display)
        self.SS_power.connect(self.SS_PowerLCD.display)

        
        
        ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
        rm = pyvisa.ResourceManager()
        tup =  rm.list_resources()
        '''
        for resource_id in tup :
            try:
                inst = rm.open_resource(resource_id, send_end=True)
                name_str = inst.query('*IDN?').strip()
                if ScopePattern.match(name_str) is not None:
                    print(name_str)
                    self.scope = rigol_ds1054z(inst)
                    print('Connected to: {}'.format(name_str))
                if name_str == instrument_strings.sdm3045x_2:
                    self.RLmeter = sdm3045x.sdm3045x(inst)
                    print("Connected to: " + self.RLmeter.name.rstrip('\n'))
                if name_str == instrument_strings.sdm3045x_4:
                    self.SSmeter = sdm3045x.sdm3045x(inst)
                    print("Connected to: " + self.SSmeter.name.rstrip('\n'))
            except pyvisa.errors.VisaIOError:
                pass
        #sw node is channel 1
        self.scope.setup_channel(channel=1,on=1,offset_divs=-2.0, volts_per_div=10.0)
        #RLVout channel 
        self.scope.setup_channel(channel=2,on=1,offset_divs=0,volts_per_div=10.0)
        #SSVout channel 
        self.scope.setup_channel(channel=3,on=1,offset_divs=0,volts_per_div=10.0)
        
        self.scope.setup_timebase(time_per_div='5us',delay='0us')
        self.scope.setup_mem_depth(memory_depth=6e3)
        self.scope.setup_trigger(channel=1,slope_pos=1,level='5v')
        self.scope.repeat_trigger()
        '''
        self.timer.start()
  
    def update_vals(self):
        '''
        RLrms = self.scope.get_measurement(channel=2, meas_type=self.scope.rms_voltage)
        SSrms = self.scope.get_measurement(channel=3, meas_type=self.scope.rms_voltage)
        RLtemp = round(meas_temp(self.RLmeter),1)
        SStemp = round(meas_temp(self.SSmeter),1)
        self.RL_power.emit(calc_power(RLrms))
        self.SS_power.emit(calc_power(SSrms))
        self.RL_temp.emit(RLtemp)
        self.SS_temp.emit(SStemp)
        
        print(f'RLcoil = {RLtemp:.3f}C')
        print(f'SScoil = {SStemp:.3f}C')
        print(f'RLrms = {RLrms:.3f} V')
        print(f'SSrms = {SSrms:.3f} V')
        '''
        self.RL_power.emit(1.0)
        self.SS_power.emit(2)
        self.RL_temp.emit(3)
        self.SS_temp.emit(5)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()

    sys.exit(app.exec_())