# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 18:24:27 2021

@author: eriki
"""
from __future__ import absolute_import, division, print_function

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QTimer, QThread, QObject
from scipy import interpolate
'''
Rigol Scope:
'''
from rigol_ds1054z import rigol_ds1054z
import sdm3045x
import pyvisa
import re
import pandas as pd
from datetime import datetime
import instrument_strings
from math import exp, log

RLtemp_list = []
SStemp_list = []

beta = 3892 #PS103J2 thermistor
r_o = 10e3
t_o = 25
r_inf = r_o*exp(-beta/t_o)

# def meas_temp(meter):
#     res = meter.measure_resistance()
#     print(res)
#     return beta/log(res/r_inf)
    
# def meas_temp(meter):
#     R = meter.measure_resistance()
#     mu1 = 5579.51717676452
#     mu2 = 4902.82313965069
#     p = [0.0953777064727060,-1.02775949386833,4.24523578150887,-8.03909876318775,
#          7030623504828,1.03402905548280	,-0.00828671441737146,-7.58247197203019,12.2964652728744,
#          -21.6985739156885,
#          38.7852077865839]
#     x = (R-mu1)/mu2
#     T = p[0]*x**10 + p[1]*x**9 + p[2]*x**8 + p[3]*x**7 + p[4]*x**6 + p[5]*x**5 + p[6]*x**4 + p[7] * x**3 + p[8] * x**2 + p[9] * x + p[10]
    
#     return T


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

class Worker(QObject):

    RL_temp = pyqtSignal(float)
    RL_power = pyqtSignal(float)
    SS_temp = pyqtSignal(float)
    SS_power = pyqtSignal(float)
    
    def __init__(self):
        QObject.__init__(self)
        self.timer = QTimer()
        self.timer.setInterval(250) #mSec
        ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
        rm = pyvisa.ResourceManager()
        tup =  rm.list_resources()
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
        #gate signal is channel 1
        self.scope.setup_channel(channel=1,on=1,offset_divs=-2.0, volts_per_div=10.0)
        #RLVout channel 2
        self.scope.setup_channel(channel=2,on=1,offset_divs=0,volts_per_div=10.0)
        #SSVout channel 3
        self.scope.setup_channel(channel=3,on=1,offset_divs=0,volts_per_div=10.0)
        
        self.scope.setup_timebase(time_per_div='5us',delay='0us')
        self.scope.setup_mem_depth(memory_depth=6e3)
        self.scope.setup_trigger(channel=1,slope_pos=1,level='5v')
        self.scope.repeat_trigger()
        df2 = pd.read_csv('PS103J2_RT_Table.csv')
        temps = df2['temp']
        res = df2['resistance']
        self.f = interpolate.interp1d(res, temps)
        return 
    '''
https://stackoverflow.com/questions/25995305/pyqt-code-is-blocking-although-moved-to-a-different-qthread?rq=1
    '''    
    def initialize(self):
        self.timer.timeout.connect(self.update_vals)
        self.timer.start()
        
    def meas_temp(self,meter):
        R = meter.measure_resistance()
        return float(self.f(R))
        
    def update_vals(self):
        
        RLrms = self.scope.get_measurement(channel=2, meas_type=self.scope.rms_voltage)
        SSrms = self.scope.get_measurement(channel=3, meas_type=self.scope.rms_voltage)
        RLtemp = round(self.meas_temp(self.RLmeter),2)
        SStemp = round(self.meas_temp(self.SSmeter),2)
        
        RLtemp_list.append(RLtemp)
        SStemp_list.append(SStemp)
        
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
        '''

class MyApp(QMainWindow, Ui_MainWindow):
    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 600, 400)
        
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        
        #self.thread.started.connect(self.worker.run)
        self.worker.RL_temp.connect(self.RL_TempLCD.display)
        self.worker.RL_power.connect(self.RL_PowerLCD.display)
        self.worker.SS_temp.connect(self.SS_TempLCD.display)
        self.worker.SS_power.connect(self.SS_PowerLCD.display)
        self.worker.initialize()
        self.thread.start()
       
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()

    sys.exit(app.exec_())