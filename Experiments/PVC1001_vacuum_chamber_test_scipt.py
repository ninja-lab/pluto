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

'''
DAQ channel assignments:
1: (green)K type thermocouple 
2: (blue) reference resistor
3: (black - blue's twisted mate) sense resistor
4: (white) DCVT linear analog out


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
ambient_temperature = daq.measure_temp(101)
for i in range(1000):
    print('Taking measurement #{}'.format(i))
    temp = {}
    temperature = daq.measure_temp(101)
    temp['temp'] = temperature
    temp['V_Rref'] = daq.measure_DCV(102)
    temp['V_Rsns'] = daq.measure_DCV(103)
    temp['linear_pressure'] = daq.measure_DCV(104)
    temp['time [sec]'] = round(time.clock(),2)
    temp['time_stamp']= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results = results.append(temp, ignore_index=True)
    time.sleep(2)
    if i%20 == 0:
        stop = input('enter 1 to exit, or any other key to continue')
        if stop == 1:
            break
    
    
results['Rsns'] = round(results['V_Rsns'] / ((24 - results['V_Rsns'])/3200), 1)
results['Rref'] = round(results['V_Rref'] / ((24 - results['V_Rref'])/3200), 1)
results['pressure'] = round(results['linear_pressure']*1000/5, 2) #result in mTorr

    
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'PVC1001 Characterization'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
results.to_csv(path_or_buf=filename)


#plot the non linear curve
fig, ax1 = plt.subplots()
ax1.plot(results['pressure'], results['V_Rsns'], 'g--')
ax1.set_xlabel('Pressure [mTorr]')
ax1.set_ylabel('Non-Linear Voltage From Sensor', color = 'b')
#ax1.legend(['Posifa'])
for tl in ax1.get_yticklabels():
    tl.set_color('b')
name = 'PVC1001 at {}C '.format(ambient_temperature) + time_stamp
plt.title(name)
fig = plt.gcf()
plt.show()
filename = (save_loc + name + '.png').replace(' ','_')
fig.savefig(filename)

#plot linearized pressure voltage using a lookup table along with DCVT out

    
    



    
    
    
    
    
    
    
    