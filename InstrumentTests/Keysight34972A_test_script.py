import Keysight34972A
import pyvisa
import Rigol_DP832
import instrument_strings
import Agilent33120
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
#import plotting

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        elif name_str == instrument_strings.DP832A:
            DCsupply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + DCsupply.name.rstrip('\n'))
        elif name_str == instrument_strings.FG33120A:
            func_gen = Agilent33120.f33120a(inst)
            print("Connected to: " + func_gen.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        
'''        
freq = 10.0
ampl = 1.0
offset = .5
func_gen.applyFunction('SIN', freq, ampl, offset)
dc_command = 1.0
DCsupply.apply(dc_command, .1, 3)
results = pd.DataFrame()
daq.set_NPLC(200, '(@101)')
dc_voltage = daq.measure_DCV(101)
ac_voltage = daq.measure_ACV(102)
temp = daq.measure_temp(103)

print('Channel 1: Measured = {:.2f}V, Programmed = {:.2f}V'.format(dc_voltage, dc_command))
print('Channel 2: Measured = {:.2f}V, Programmed = {:.2f}V'.format(ac_voltage, ampl))
print('Channel 3: Measured = {:.2f}C, Ambient about 25C'.format(temp))

for i in range(60):
    print('Taking measurement #{}'.format(i))
    temp = {}
    temperature = daq.measure_temp(103)
    temp['temp'] = temperature
    temp['time [sec]'] = round(time.clock(),2)
    temp['time_stamp']= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    results = results.append(temp, ignore_index=True)
    time.sleep(.5)

DCsupply.turn_off(3)
#plotting.easy_plot(results['temp'], results['time [sec]'],'temperature', 'temperature [C]', 'elapsed time [sec]', 'Thermocouple data log test')
plt.plot(results['time [sec]'],results['temp'])
plt.show()
'''