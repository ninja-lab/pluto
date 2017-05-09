import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--', '-.'])
filename = save_loc+'PVC1001_Characterization2017-04-27.csv'
results = pd.read_csv(save_loc+'PVC1001_Characterization2017-05-01.csv')
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
#title_str = 'PVC1001 Characterization Data'
#name = title_str + time_stamp
sensors = [1,2,3,4,5,6,7,8,9,10]
#plot resistance vs pressure of all sensors on one plot
'''

title_str = 'Sense Resistance vs Pressure'
data_sheet_voltage = [, 1.12, 1.145,1.275,1.52,1.53,1.53]
data_sheet_pressure = [1000e3, 100e3, 10e3,1e3,0.1e3,0.001e3,1.00E-03]
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['Rsns#{}'.format(i)], label='#{}'.format(i))
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 100, top = 200)
ax.set_xlim(left = 1e-3, right = 1e6)
fig.savefig(filename)
'''
title_str = 'Sense Resistance vs Pressure'
data_sheet_resistance = [160, 160,164,182,217, 219, 219]
data_sheet_pressure = [1000e3, 100e3, 10e3,1e3,0.1e3,0.001e3,1.00E-03]
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['Rsns#{}'.format(i)], label='#{}'.format(i))
ax.semilogx(data_sheet_pressure, data_sheet_resistance, label='DATASHEET')
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 100, top = 300)
ax.set_xlim(left = 1e-3, right = 1e6)
fig.savefig(filename)
'''
#use * markers
title_str = 'Sense Resistance vs Pressure'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['Rsns#{}'.format(i)], label='#{}'.format(i), marker='*')
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 120, top = 180)
ax.set_xlim(left = 10, right = 1200)
fig.savefig(filename)


title_str = 'Reference Resistance vs Pressure'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['Rref#{}'.format(i)], label='#{}'.format(i))
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 100, top = 400)
ax.set_xlim(left = 10, right = 1200)
fig.savefig(filename)

#two plot panes, one of pressure and one of sense resistance vs time
title_str = 'Sense Resistance and Pressure vs Time'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, axs = plt.subplots(nrows = 2, ncols = 1, sharex = True)

axs[0].set_prop_cycle(color_cycle*ls_cycle)
axs[1].set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    axs[0].plot(results['seconds#{}'.format(i)], results['Rsns#{}'.format(i)], label='#{}'.format(i))
    axs[1].plot(results['seconds#{}'.format(i)], results['pressure#{}'.format(i)])
axs[0].grid(which='both', axis='x')
#ax.legend(loc='best')
axs[1].set_xlabel('Time [sec]')
axs[0].set_ylabel('Resistance [ohm')
axs[0].set_title('Rsns vs Time')
axs[1].set_ylabel('DAVC analog out [mTorr]')
axs[1].set_title('DAVC Pressure reading vs Time')
axs[0].set_ylim(bottom = 120, top = 180)
axs[0].set_xlim(left = 0, right = 1200)
fig.savefig(filename)

#plot ratio of resistances vs pressure
title_str = 'Rsns over Rref vs Pressure'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['Rsns#{}'.format(i)]/results['Rref#{}'.format(i)], label='#{}'.format(i))
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Rsns / Rref')
ax.set_ylim(bottom = 0.4, top = .8)
ax.set_xlim(left = 10, right = 1200)
fig.savefig(filename)

#plot all pressures vs time
title_str = 'Pressure vs Time'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.plot(results['seconds#{}'.format(i)], results['pressure#{}'.format(i)], label='#{}'.format(i))
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Time [sec]')
ax.set_ylabel('Pressure [mTorr]')
ax.set_ylim(bottom = 10, top = 200)
ax.set_xlim(left = 0, right = 1200)
fig.savefig(filename)

#plot all temperatures vs time
title_str = 'Thermocouple measurement vs Time'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.plot(results['seconds#{}'.format(i)], results['temp#{}'.format(i)], label='#{}'.format(i))
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Time [sec]')
ax.set_ylabel('Temperature [degree C]')
ax.set_ylim(bottom = 10, top = 40)
ax.set_xlim(left = 0, right = 1000)
fig.savefig(filename)
#plot ratio of rsns over rref vs time


#plot voltage of Rsns with 7mA current into, and compare to data sheet curve
data_sheet_voltage = [1.12, 1.12, 1.145,1.275,1.52,1.53,1.53]
data_sheet_pressure = [1000e3, 100e3, 10e3,1e3,0.1e3,0.001e3,1.00E-03]
title_str = 'Sense Voltage vs Pressure'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.semilogx(results['pressure#{}'.format(i)], results['V_Rsns#{}'.format(i)], label='#{}'.format(i))
ax.semilogx(data_sheet_pressure, data_sheet_voltage, marker='*', label='DATASHEET')
ax.grid(which='both', axis='x')
ax.legend(loc='best')
ax.set_xlabel('Pressure [mTorr]')
ax.set_ylabel('Voltage [ohm]')
ax.set_ylim(bottom = 1, top = 1.55)
ax.set_xlim(left = 1e-3, right = 1e6)
fig.savefig(filename)
'''
