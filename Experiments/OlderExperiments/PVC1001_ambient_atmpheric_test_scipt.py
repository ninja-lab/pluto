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
ambient = daq.measure_temp(101)
for i in range(15):
    print('Taking measurement #{}'.format(i))
    temp = {}
    temperature = daq.measure_temp(101)
    print('temperature is {}C'.format(temperature))
    temp['temp'] = temperature
    temp['V_Rref'] = daq.measure_DCV(102)
    temp['V_Rsns'] = daq.measure_DCV(103)
    temp['time [sec]'] = round(time.clock(),2)
    temp['time_stamp']= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp['Rsns'] = round(temp['V_Rsns'] / ((24 - temp['V_Rsns'])/3200), 1)
    temp['Rref'] = round(temp['V_Rref'] / ((24 - temp['V_Rref'])/3200), 1)
    results = results.append(temp, ignore_index=True)
    time.sleep(1)

results['delta_T'] = results['temp'] - ambient
results['Rsns_TC'] = ((results['Rsns']/results['Rsns'][0]) - 1)/results['delta_T']
results['Rref_TC'] = ((results['Rref']/results['Rref'][0]) - 1)/results['delta_T']  
  
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')

fig, ax1 = plt.subplots()
ax1.plot(results['temp'], results['Rsns'], 'g--')
ax1.plot(results['temp'], results['Rref'], 'b--')
ax1.set_xlabel('Temperature [C]')
ax1.set_ylabel('Resistance [ohm]', color = 'b')
ax1.legend(['Rsns', 'Rref'])
ax1.set_ylim(100, 300)
for tl in ax1.get_yticklabels():
    tl.set_color('b')
name = '1atm pressure and PVC1001 temperature dependence' + time_stamp
plt.title(name)
fig = plt.gcf()
plt.show()
filename = (save_loc + name + '.png').replace(' ','_')
fig.savefig(filename)

fig, ax1 = plt.subplots()
ax1.plot(results['temp'], results['Rsns_TC'], 'g--')
ax1.plot(results['temp'], results['Rref_TC'], 'b--')
ax1.set_xlabel('Temperature [C]')
ax1.set_ylabel('Temperature Coefficient', color = 'b')
ax1.legend(['Rsns_TC', 'Rref_TC'])
ax1.set_ylim(-.002, .004)
for tl in ax1.get_yticklabels():
    tl.set_color('b')
name = '1atm pressure and PVC1001 temperature coefficient' + time_stamp
plt.title(name)
fig = plt.gcf()
plt.show()
filename = (save_loc + name + '.png').replace(' ','_')
fig.savefig(filename)

title_str = 'PVC1001 Characterization'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
results.to_csv(path_or_buf=filename)

    
