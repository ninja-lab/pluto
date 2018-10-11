# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 09:12:06 2018

@author: Erik


"""

import Keysight34972A
import pyvisa
import InstekPSW
import instrument_strings
from pwr_board_test_class import pwr_board_test_class
import random
import time
import pandas as pd
'''
The final deliverable is a dataframe/spreadsheet of all the tests, which details 
the test number, description, measurement value, pass/fail status, margins, and timestamp.
Ultimately, the deliverable can describe how one particular DUT compares to all the others.


'''

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        if name_str == instrument_strings.PSW800:
            hv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + hv_supply.name.rstrip('\n'))
        if name_str == instrument_strings.PSW80V:
            lv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + lv_supply.name.rstrip('\n'))
            
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

df = pd.read_excel('C:\\Users\\Erik\\git\\pluto\\PWR_Board_TestReportTemplate.xlsx')
test_dict = {} #get keys from the right df column
'''
use enumerations to get relevant test out of a list
'''
tests = [pwr_board_test_class(row[1] for row in df.iterrows())]
quantities = 

def measure_24Vout():
    return daq.measure_DCV(204)
def measure_PSUA():
    return daq.measure_DCV(201)
def measure_PSUB():
    return daq.measure_DCV(202)
def measure_PSUC():
    return daq.measure_DCV(203)
def measure_FLTOUT():
    return daq.measure_DCV(205)
def measure_temp():
    #return temperature in degrees from LM94022
    return (daq.measure(206)-2.3)/(-.0136)        
def measure_SPM():
    return daq.measure(207)
def measure_PSUFault():
    return daq.measure(208)
def measure_HVCap():
    return daq.measure(210)*4
def measure_HVBuck():
    return daq.measure(211)*4
def measure_DCBus():
    return daq.measure(212)*6
def measure_bootstrap():
    return daq.measure(214)
def measure_16V():
    return daq.measure(213)
def measure_buckCurrent():
    v_rsns = daq.measure_DCV(215)
    return v_rsns/.28


print('Welcome to  385-0030-00 PWR Board Automated Test')
start = input('Start Test? Enter y or n')
if start == 'n':
    exit()
set_discharge_Vgs(0) #turn off Q1 completely

load1_off()
load2_off()
load3_off()
flyback_off()
buck_off()
test_num = 1
'''************************
Test 1
Ramp up PSUA from UV and check 
increasing UVLO thresholds with zero load
***************************'''
close_rl5()

for i in range(12, 24, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange(test_num):
        tests[3].SetMeasurement(quantities['PSUA'].measure())
    
'''***********************
Test 2
Ramp down PSUA from valid and check 
decreasing UVLO thresholds with zero load
***********************'''
PSU80V.apply(24,1)
for i in range(24, 18, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if not quantities['24Vout'].inRange():
        tests[2].SetMeasurement(i)
PSU80V.apply(0,1)        

'''******************
Test 3
Ramp up PSUA from valid and check 
increasing OVLO thresholds with zero load
******************'''

for i in range(24, 32, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange():
        tests[3].SetMeasurement(quantities['PSUA'].measure())

'''******************
Test 4
Ramp down PSUA from invalid and check 
decreasing OVLO thresholds with zero load
******************'''
for i in range(32, 24, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange():
        tests[4].SetMeasurement(i)

'''******************
Test 5
Configure PSU80V to PSUB
Ramp up PSUB from invalid and check 
increasing UVLO thresholds with zero load
******************'''
open_rl5()

for i in range(12, 24, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange():
        tests[5].SetMeasurement(i)
'''******************
Test 6
Ramp down PSUB from valid and check 
decreasing UVLO thresholds with zero load
******************'''
PSU80V.apply(24,1)
for i in range(24, 18, .1):
    PSU80V.apply(i, 1)
    quantities['24Vout'].measure()
    if not quantities['24Vout'].inRange():
        tests[2].SetMeasurement(i)
PSU80V.apply(0,1)     


'''******************
Test 7

******************'''
for i in range(24, 32, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange():
        tests[7].SetMeasurement(i)
'''******************
Test 8
Ramp down PSUB from invalid and check 
decreasing OVLO thresholds with zero load
******************'''
for i in range(32, 24, .1):
    PSU80V.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure()
    if quantities['24Vout'].inRange():
        tests[8].SetMeasurement(i)
        
PSU80V.apply(0,1)
'''******************
Test 9
Time the flyback cap charging
******************'''
flyback_on()
close_rl5()
PSU80V.apply(24, 4)



'''******************
Test 10

******************'''

'''******************
Test 11

******************'''

'''******************
Test 12

******************'''

'''******************
Test 13

******************'''

'''******************
Test 14

******************'''

'''******************
Test 15

******************'''

































