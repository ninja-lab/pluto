import Keysight34972A
import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt

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
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'TT characterization data'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'

'''
101: transducer techniques bridge output
102: transducer techniques amplified output

Use a transducer techniques TEDS reader and 3000 lb load cell for a baseline. 
Calibrate transducer techniques load cell amp with calibration sheet from
the load cell under test.  
Use hydraulic press to cycle through force points.  

'''
load_cells = []
for i in range(8):
    TEDS = []
    brdg = []
    ampl = []
    load_cell_num = input('Enter TT Load Cell serial number: ')
    load_cells.append(load_cell_num)
    print('Measuring zero force voltage')
    TEDS.append(int(input('Enter TEDS reader force and hit enter: ')))
    brdg.append(daq.measure_DCV(101))
    ampl.append(daq.measure_DCV(102))
    for k in range(20):
        print('Taking measurement #{}'.format(k))
        TEDS.append(int(input('Enter TEDS reader force and hit enter: ')))
        brdg.append(daq.measure_DCV(101))
        ampl.append(daq.measure_DCV(102))
    junk = input('Ensure 0 force for the last measurement and hit enter')
    TEDS.append(int(input('Enter TEDS reader force and hit enter: ')))
    brdg.append(daq.measure_DCV(101))
    ampl.append(daq.measure_DCV(102))
    results['{}TEDS'.format(load_cell_num)] = TEDS
    results['{}brdg'.format(load_cell_num)] = brdg
    results['{}ampl'.format(load_cell_num) = ampl 
    results.to_csv(path_or_buf=filename)

'''
    #sensitivity vs TEDS
    fig1, ax1 = plt.subplots()
    title_str1 = 'TT vs TEDS Characterization'
    name1 = title_str + time_stamp
    filename1 = save_loc + name.replace(' ','_') +'.csv'

    #error vs. TEDS
    fig2, ax2 = plt.subplots()
    title_str2 = 'TT vs TEDS Characterization'
    name2 = title_str + time_stamp
    filename2 = save_loc + name.replace(' ','_') +'.csv'

    #bridge voltages vs. TEDS
    fig3, ax3 = plt.subplots()
    title_str3 = 'TT vs TEDS Characterization'
    name = title_str3 + time_stamp
    filename3 = save_loc + name.replace(' ','_') +'.csv'
    '''
for load_cell_num in load_cells:
    
    results['{}sensitivity'.format(load_cell_num)] =(results['{}brdg'.format(load_cell_num)] / 10) * (3000 / (.1 + results['{}TEDS'.format(load_cell_num)]))
    results['{}error'.format(load_cell_num)] = round((results['{}ampl'.format(load_cell_num)] - results['{}TEDS'.format(load_cell_num)])*100/3000,2)
    results['{}force'.format(load_cell_num)] = (results['{}brdg'.format(load_cell_num)] * 3000/ .02).astype(int)

    
        


results.to_csv(path_or_buf=filename)
         
        
        
        
        
        
        
        
        
        