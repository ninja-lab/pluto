import Keysight34972A
import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
sensors = [1,2,3,4,5,6,7,8]
'''
The experiment will be moved from place to place (freezer to fridge to ambient, etc)
and thus the DAQ needs to be unplugged. The script needs to pick up where it left off, 
deduced by the results. 

'''
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

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'PVC1001 TCR Characterization'
name = title_str
filename = save_loc + name.replace(' ','_') +'.csv'
#try to find the results CSV to add to it
try:
    results = pd.read_csv(filename) 
except FileNotFoundError:
    places = ['freezer', 'fridge', 'ambient', 'oven1', 'oven2', 'oven3']
    columns = ['Rsns{}'.format(i) for i in sensors]
    columns.extend(['Rref{}'.format(i) for i in sensors])
    columns.extend(['Rsns/Rref {}'.format(i) for i in sensors])
    columns.append('Temp')
    columns.append('Location')
    #results = pd.DataFrame(index = places, columns = columns)
    results = pd.DataFrame(columns = columns)
#print(results)    
'''
DAQ channel assignments:
ch1-16: pressure sensors with Rref, Rsns on adjacent channels
1 ref1
2 sns1
3 ref2
4 sns2

20: K type thermocouple 
'''
res_scan = '(@101:116)'
temp_scan = '(@120)'
all = '(@101:116,120)'
daq.configure_resistance_channels(res_scan)
daq.configure_temp_channels(temp_scan)
daq.set_scan(all)
daq.set_delay(.3, all)
daq.set_trigger('IMM')
daq.format_reading()
data = daq.read()
#print(data)
#this_temp = pd.DataFrame()
dict = {}
location = input('What location?')
for i in sensors: 
    #print('CH{} and Rsns{} is {:.1f}ohms'.format(i,round(data[i],1 )
    dict['Rsns{}'.format(i)] = round(data[2*(i-1)],1)
    #print('Rref{} is {:.1f}ohms'.format(i,round(data[i-1],1 )
    dict['Rref{}'.format(i)] = round(data[2*i-1],1)
    dict['Rsns/Rref {}'.format(i)] = dict['Rsns{}'.format(i)]/dict['Rref{}'.format(i)]
    dict['Temp'] = round(data[16],1)
    dict['Location'] = location
    

this_temp = pd.DataFrame(dict, index = [0])
print('this_temp:')
print(this_temp)
results = pd.concat([results, this_temp], join='inner', ignore_index=True)
#results = results.append(this_temp, ignore_index =True)
print('results:')
print(results)
results.to_csv(path_or_buf=filename)

    
