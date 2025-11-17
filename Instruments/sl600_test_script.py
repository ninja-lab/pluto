# -*- coding: utf-8 -*-
"""
Created on Thu May 27 17:37:28 2021

@author: eriki
"""

import pyvisa
import Rigol_DP832
import bk8614
import sdm3045x
import sl600

import numpy as np
from math import sqrt
import time
import instrument_strings
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        if resource_id.find('ASRL') != -1:
            inst.baud_rate = 19200
            inst.read_termination = '\r\n'
            inst.write_termination = '\r\n'
            
        name_str = inst.query('*IDN?').strip()
        print(name_str)
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
        
supply.source(5, 1)
resistance  = 300
load.set_resistance(resistance)
load.turn_on()
time.sleep(1)
supply.turn_on()
time.sleep(1)

def percent_diff(l1, l2):
    return [(x-y)*100/y for x,y in zip(l1,l2)]

def offset(l1, l2):
    return [x-y for x,y in zip(l1,l2)]

magna_voltage = []
magna_current = []
load_voltage = []
load_current = []
meter_voltage = []
meter_current = []

command_voltages = range(20, 100, 15)
command_currents = [el / resistance for el in command_voltages]
for i in command_voltages:
    '''
    only draw .5A to test
    '''
    
    supply.source(i, 1)
    time.sleep(3)
    i1 = supply.measure_current()
    magna_current.append(i1)
    
    v1 = supply.measure_voltage()
    magna_voltage.append(v1)
    
    v2 = load.measure_voltage()
    load_voltage.append(v2)
    
    i2 = load.measure_current()
    load_current.append(i2)
    
    v3 = meter.measure_voltage()
    meter_voltage.append(v3)
    i3 = meter.measure_current()
    meter_current.append(i3)
    
    print(f'supply says Vin = {v1:.3f} V')
    print(f'supply says Iin = {i1:.3f}A')
    print(f'load says Vin = {v2:.3f} V')
    print(f'load says Iin = {i2:.3f} A')
    print(f'meter says Vin = {v3:.3f} V')
    print(f'meter says Iin = {i3:.3f} A')
    print(f'percent difference in V: {(v1-v2)*100/v2:.3f}%')

    print(f'percent difference in I: {(i1-i2)*100/i2:.3f}%')
    print(f'voltage offset = {v2-v1:.3f} V')
    print(f'current offset = {i2 - i1:.3f} A')
    print() 
supply.turn_off()
load.turn_off()
temp = meter_current.copy()
meter_current= [-1*el for el in temp]
fig, ax = plt.subplots()
ax.plot(command_voltages, magna_voltage, label='supply')
ax.plot(command_voltages, load_voltage, label = 'load')
ax.plot(command_voltages, meter_voltage, label='meter')
ax.legend()
ax.set_ylabel('measured voltages')
ax.set_xlabel('command voltages')

fig, ax = plt.subplots()
ax.plot(command_currents, magna_current, label='supply')
ax.plot(command_currents, load_current, label = 'load')
ax.plot(command_currents, meter_current, label='meter')
ax.legend()
ax.set_ylabel('measured currents')
ax.set_xlabel('command currents')

fig, ax = plt.subplots()
ax.plot(command_currents, percent_diff(magna_current, meter_current), label='supply')
ax.plot(command_currents, percent_diff(load_current, meter_current), label = 'load')
ax.legend()
ax.set_xlabel('commanded currents')
ax.set_ylabel('(x-y)*100/y as percent difference from meter')
ax.set_title('percent differences of current')

fig, ax = plt.subplots()
ax.plot(command_voltages, percent_diff(magna_voltage, meter_voltage), label='supply')
ax.plot(command_voltages, percent_diff(load_voltage, meter_voltage), label = 'load')
ax.legend()
ax.set_xlabel('command voltages')
ax.set_ylabel('(x-y)*100/y as percent difference from meter')
ax.set_title('percent differences of voltages')

fig, ax = plt.subplots()
ax.plot(command_currents, offset(magna_current, meter_current), label='supply')
ax.plot(command_currents, offset(load_current, meter_current), label = 'load')
ax.legend()
ax.set_xlabel('commanded current')
ax.set_ylabel('(x-y) offset from meter')
ax.set_title('offsets of current from meter')

fig, ax = plt.subplots()
ax.plot(command_voltages, offset(magna_voltage, meter_voltage), label='supply')
ax.plot(command_voltages, offset(load_voltage, meter_voltage), label = 'load')
ax.legend()
ax.set_xlabel('commanded voltages')
ax.set_ylabel('(x-y) offset from meter')
ax.set_title('offset of voltage from meter')
