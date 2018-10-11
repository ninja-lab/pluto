# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 14:15:10 2018

@author: Erik
"""
import time
from scipy.optimize import curve_fit
import numpy as np

def open_rl1(daq):
    daq.digital_source1(1, 0)
def close_rl1(daq):
    daq.digital_source1(1, 1)
def open_rl2(daq):
    daq.digital_source1(2, 0)
def close_rl2(daq):
    daq.digital_source1(2, 1)
def open_rl3(daq):
    daq.digital_source1(3, 0)
def close_rl3(daq):
    daq.digital_source1(3, 1)
def open_rl4(daq):
    daq.digital_source1(4, 0)
def close_rl4(daq):
    daq.digital_source1(4, 1)
def open_rl5(daq):
    '''
    RL5 in open state feeds PSU80V to PSUB
    '''
    daq.digital_source2(4, 0)
def close_rl5(daq):
    '''
    RL5 in closed state feeds PSU80V to PSUA
    '''
    daq.digital_source2(4, 1)
def flyback_on(daq):
    daq.digital_source1(6, 0)
def flyback_off(daq):
    daq.digital_source1(6, 1)
def buck_on(daq):
    daq.digital_source1(7, 1)
def buck_off(daq):
    daq.digital_source1(7, 0)
#********************************

def load1_on(daq):
    daq.digital_source2(1,0)
def load1_off(daq):
    daq.digital_source2(1,1)
def load2_on(daq):
    daq.digital_source2(2,0)
def load2_off(daq):
    daq.digital_source2(2,1)
def load3_on(daq):
    daq.digital_source2(3,0)
def load3_off(daq):
    daq.digital_source2(3,1)

def set_discharge_Vgs(daq, voltage):
    daq.analog_source(104, voltage)
voltages = []
currents = []
powers = []
def discharge_caps(vgs, voltage, current, daq):
    set_discharge_Vgs(daq, vgs)
    voltages.append(voltage)
    currents.append(currents)
    powers.append(voltage*current)
    if voltage < 1 and current < .1:
        set_discharge_Vgs(daq, 10)
        time.sleep(5)
        print('caps should be discharged')
        set_discharge_Vgs(daq, 0)
        return 
    else:
        power = voltage*current
        if power > 100:
            discharge_caps(max(0,vgs-.1),measure_HVCap(daq),measure_buckCurrent(daq),daq )
        elif power < 60:
            discharge_caps(min(vgs+.1,10),measure_HVCap(daq),measure_buckCurrent(daq),daq )
        else:
            discharge_caps(vgs, measure_HVCap(daq),measure_buckCurrent(daq),daq )
            
            
def get_tau(xdata, ydata, dclevel):
    def func(x, a, b, c):
        return a * np.exp(-b * x) + c
    popt, pcov = curve_fit(func, xdata, ydata, p0=[dclevel,.15,0])
    return round(1/popt[1],3)    










