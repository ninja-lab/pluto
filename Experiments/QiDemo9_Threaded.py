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
'''
Rigol Scope:
'''
from rigol_ds1054z import rigol_ds1054z
import sdm3045x
import pyvisa
import re
from datetime import datetime
import instrument_strings
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

class Worker(QObject):

    RL_temp = pyqtSignal(float)
    RL_power = pyqtSignal(float)
    SS_temp = pyqtSignal(float)
    SS_power = pyqtSignal(float)
    
    def __init__(self):
        QObject.__init__(self)
        self.timer = QTimer()
        self.timer.setInterval(1000) #mSec
   
        ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
        rm = pyvisa.ResourceManager()
        tup =  rm.list_resources()
        
        return 
    '''
https://stackoverflow.com/questions/25995305/pyqt-code-is-blocking-although-moved-to-a-different-qthread?rq=1
    '''    
    def initialize(self):
        self.timer.timeout.connect(self.update_vals)
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
       

class MyApp(QMainWindow, Ui_MainWindow):
    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 400, 400)
        
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