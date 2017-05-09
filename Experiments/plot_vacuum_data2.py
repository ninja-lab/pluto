import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--', '-.'])
marker_cycle= cycler(marker=['+', 'x'] )

results = pd.read_csv(save_loc+'PVC1001_Characterization_varying_current2017-05-02.csv')
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')

sensors = [1,2,3]
currents = [.007, .009, .011, .013, .015, .017, .019]
data_sheet_voltage = [1.12, 1.12, 1.145,1.275,1.52,1.53,1.53]
data_sheet_pressure = [1000e3, 100e3, 10e3,1e3,0.1e3,0.001e3,1.00E-03]
for i in sensors:
    title_str = 'Effect of Heating Current on Voltage (sensor{})'.format(i)
    name = title_str + time_stamp
    filename = (save_loc + name + '.png').replace(' ','_')
    fig, ax = plt.subplots(subplot_kw={'title': name})
    ax.set_prop_cycle(color_cycle*marker_cycle)
    for current in currents:
        ax.semilogx(results['pressure#{}_{:.3f}A'.format(i, current)], results['V_Rsns#{}_{:.3f}A'.format(i, current)], label='{:.3f}A'.format(current))
    ax.semilogx(data_sheet_pressure, data_sheet_voltage, marker='*', label='DATASHEET')
    ax.grid(which='both', axis='x')
    ax.legend(loc='best')
    ax.set_xlabel('Pressure [mTorr]')
    ax.set_ylabel('Voltage')
    ax.set_ylim(bottom = .6, top = 4)
    ax.set_xlim(left = 1e-3, right = 1e6)
    fig.savefig(filename)
    
 '''
 the rate of disipation is dependent on the thermal conductivity of the air
 which is proportional to pressure
 so measure power disippation at such  