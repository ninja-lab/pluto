import Keysight34972A
import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
import plotting

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        
results = pd.DataFrame()

'''
DAQ channel assignments:
1: K type thermocouple 
2: (blue) reference resistor
3: (black) sense resistor

___________+24VDC
    |   |
    |   |
    \   \   <-- 3.2kOhm
    /   /
    \   \
    /   /
 ch3|   |ch2
    |   |
    \   \
    /   /
    \   \
    /   /
    |   |
    |   |
____|___|___GROUND

'''
for i in range(60):
    print('Taking measurement #{}'.format(i))
    temp = {}
    temperature = daq.measure_temp(101)
    temp['temp'] = temperature
    temp['V_Rref'] = daq.measure_DCV(102)
    temp['V_Rsns'] = daq.measure_DCV(103)
    temp['time [sec]'] = round(time.clock(),2)
    temp['time_stamp']= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp['Rsns'] = round(temp['V_Rsns'] / ((24 - temp['V_Rsns'])/3200), 1)
    temp['Rref'] = round(temp['V_Rref'] / ((24 - temp['V_Rref'])/3200), 1)
    results = results.append(temp, ignore_index=True)
    time.sleep(1)

results['delta_T'] = results['temp'].diff(1)
results['Rsns_TC'] = ((results['Rsns']/3200.0) - 1)/results['delta_T']
results['Rref_TC'] = ((results['Rref']/3200.0) - 1)/results['delta_T']  

plotting.easy_plot([results['Rsns'], results['Rref']], results['temp'],
    ['Rsns', 'Rref'], 'Temperature [C]', 'Resistance [ohm]', '1atm pressure and PVC1001 temperature dependence')    
plotting.easy_plot([results['Rsns_TC'], results['Rref_TC']], results['temp'],
    ['Rsns_TC', 'Rref_TC'], 'Temperature [C]', 'temp coefficient', '1atm pressure and PVC1001 temperature coefficient')
    
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'PVC1001 Characterization'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
results.to_csv(path_or_buf=filename)

    
