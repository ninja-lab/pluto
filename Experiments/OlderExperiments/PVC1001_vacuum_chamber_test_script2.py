import Keysight34972A
import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
import Rigol_DP832

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        if name_str == instrument_strings.RigolDP832:
            dc_supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + dc_supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        


'''
Cycle through 10 different sensors, running same characterization
Write to csv at the end of each, and read at the beginning.
Measurements start at 1000mTorr and continue until minumum pressure is reached, 
then continue as pressure increases back to 1000mTorr. 

DAQ channel assignments:
1: (green)K type thermocouple 
2: (blue) sense resistor
3: (black - blue's twisted mate) reference resistor
4: (white) - reference resistor current
5: (black) - sense resistor current
6: DCVT analog out

    |   |
    v   v  7mA 
    |   |
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
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'PVC1001 Characterization varying current'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
sensors = [2,3]
dc_supply.apply(5, channel=3)
for i in sensors:
    if i == 2:
        results = pd.DataFrame()
    else:
        results = pd.read_csv(filename)
    for current in [.007, .009, .011, .013, .015, .017, .019]:
        start_sec = time.clock()
        temperatures = []
        V_Rrefs = []
        V_Rsnss = []
        I_Rrefs = []
        I_Rsnss = []
        linear_pressures = []
        seconds = []
        stamps = []
        this_sensor = pd.DataFrame()
        meas_num = 1
        j=1
        dc_supply.apply(7, current, 1)
        dc_supply.apply(7, current, 2)
        while True: 
            
            j += 1
            linear_pressure = daq.measure_DCV(106)
            if linear_pressure < .75:  #150mTorr
                while (linear_pressure < 5.0):
                    linear_pressure = daq.measure_DCV(106)
                    linear_pressures.append(linear_pressure)
                    temperatures.append(daq.measure_temp(101))
                    V_ref = daq.measure_DCV(103)
                    I_ref = (daq.measure_DCV(104) - V_ref) / 9.9
                    V_sns = daq.measure_DCV(102)
                    I_sns = (daq.measure_DCV(105) - V_sns) / 9.9
                    V_Rrefs.append(V_ref)
                    V_Rsnss.append(V_sns)
                    I_Rrefs.append(I_ref)
                    I_Rsnss.append(I_sns)
                    print('Taking measurement #{} with {}Amps'.format(meas_num, current))
                    meas_num += 1
                    print('Pressure is: {:.0f}mTorr'.format(linear_pressure*1000/5))
                    seconds.append(round(time.clock() - start_sec,1))
                    stamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(1) 
                this_sensor['V_Rref#{}_{:.3f}A'.format(i, current)] = V_Rrefs
                this_sensor['V_Rsns#{}_{:.3f}A'.format(i, current)] = V_Rsnss
                this_sensor['I_Rref#{}_{:.3f}A'.format(i, current)] = I_Rrefs
                this_sensor['I_Rsns#{}_{:.3f}A'.format(i, current)] = I_Rsnss
                this_sensor['DCVT#{}_{:.3f}A'.format(i, current)] = linear_pressures
                this_sensor['seconds#{}_{:.3f}A'.format(i, current)] = seconds
                this_sensor['time_stamp#{}_{:.3f}A'.format(i, current)] = stamps
                this_sensor['temp#{}_{:.3f}A'.format(i, current)] = temperatures
                break
            else:  
                print('Pressure not below 150mTorr {}'.format(j))
                time.sleep(.5)       
        this_sensor['Rsns#{}_{:.3f}A'.format(i, current)] = round(this_sensor['V_Rsns#{}_{:.3f}A'.format(i, current)] / this_sensor['I_Rsns#{}_{:.3f}A'.format(i, current)] , 2)
        this_sensor['Rref#{}_{:.3f}A'.format(i, current)] = round(this_sensor['V_Rref#{}_{:.3f}A'.format(i, current)] / this_sensor['I_Rref#{}_{:.3f}A'.format(i, current)] , 2)
        this_sensor['pressure#{}_{:.3f}A'.format(i, current)] = round(this_sensor['DCVT#{}_{:.3f}A'.format(i, current)]*1000/5, 2) #result in mTorr
        results = pd.concat([results, this_sensor], axis=1) 
        results.to_csv(path_or_buf=filename)
    junk = input('Change jumper position for the next sensor and hit enter')




    
    
    
    
    
    
    
    