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
(channel 5 - channel 2) / 20ohm = reference resistor current
(channel 4 - channel 3) / 20ohm = sense resistor current
6: DCVT analog out

    |   |
    v   v  7mA 
    |   |
 ch4|   |ch5
    \   \   <-- 20ohm
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
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'PVC1001 Characterization'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
sensors = [7,8,9,10]

for i in sensors:
    if i == 7:
        results = pd.DataFrame()
        
    else:
        results = pd.read_csv(filename)
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
    j = 0
    while True: 
        j += 1
        linear_pressure = daq.measure_DCV(106)
        if linear_pressure < .75:  #150mTorr
            while (linear_pressure < 5.0):
                linear_pressure = daq.measure_DCV(106)
                linear_pressures.append(linear_pressure)
                temperatures.append(daq.measure_temp(101))
                V_ref = daq.measure_DCV(103)
                I_ref = (daq.measure_DCV(104) - V_ref) / 20
                V_sns = daq.measure_DCV(102)
                I_sns = (daq.measure_DCV(105) - V_sns) / 20
                V_Rrefs.append(V_ref)
                V_Rsnss.append(V_sns)
                I_Rrefs.append(I_ref)
                I_Rsnss.append(I_sns)
                print('Taking measurement #{}'.format(meas_num))
                meas_num += 1
                print('Pressure is: {:.0f}mTorr'.format(linear_pressure*1000/5))
                seconds.append(round(time.clock() - start_sec,1))
                stamps.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                time.sleep(1) 
            this_sensor['V_Rref#{}'.format(i)] = V_Rrefs
            this_sensor['V_Rsns#{}'.format(i)] = V_Rsnss
            this_sensor['I_Rref#{}'.format(i)] = I_Rrefs
            this_sensor['I_Rsns#{}'.format(i)] = I_Rsnss
            this_sensor['DCVT#{}'.format(i)] = linear_pressures
            this_sensor['seconds#{}'.format(i)] = seconds
            this_sensor['time_stamp#{}'.format(i)] = stamps
            this_sensor['temp#{}'.format(i)] = temperatures
            break
        else:  
            print('Pressure not below 150mTorr {}'.format(j))
            time.sleep(.5)       
    this_sensor['Rsns#{}'.format(i)] = round(this_sensor['V_Rsns#{}'.format(i)] / this_sensor['I_Rsns#{}'.format(i)] , 2)
    this_sensor['Rref#{}'.format(i)] = round(this_sensor['V_Rref#{}'.format(i)] / this_sensor['I_Rref#{}'.format(i)] , 2)
    this_sensor['pressure#{}'.format(i)] = round(this_sensor['DCVT#{}'.format(i)]*1000/5, 2) #result in mTorr
    junk = input('Change jumper position for the next sensor and hit enter')
    results = pd.concat([results, this_sensor], axis=1) 
    results.to_csv(path_or_buf=filename)
'''
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

''' 
    



    
    
    
    
    
    
    
    