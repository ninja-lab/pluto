import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--', '-.'])
results = pd.read_csv(save_loc+'PVC1001_TCR_Characterization.csv')
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
sensors = [1,2,3,4,5,6,7,8]

title_str = 'Sense Resistance vs Temperature'
data_sheet_TCR = .0025
data_sheet_resistance_min = [100*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_resistance_typ = [130*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_resistance_max = [185*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_temps = range(-20, 130, 10)
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)

for i in sensors:
    ax.plot(results['Temp'], results['Rsns{}'.format(i)], label='#{}'.format(i))
ax.plot(data_sheet_temps, data_sheet_resistance_min, marker='*', label='spec_min')
ax.plot(data_sheet_temps, data_sheet_resistance_typ, marker='*', label='spec_typ')
ax.plot(data_sheet_temps, data_sheet_resistance_max, marker='*', label='spec_max')
ax.grid(which='both')
ax.legend(loc='best')
ax.set_xlabel('Temperature [Celsius]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 80, top = 190)
ax.set_xlim(left = -30, right = 130)
fig.savefig(filename)

title_str = 'Reference Resistance vs Temperature'
data_sheet_TCR = .0025
data_sheet_resistance_min = [200*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_resistance_typ = [260*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_resistance_max = [370*(1+data_sheet_TCR*i) for i in range(-20, 130, 10)]
data_sheet_temps = range(-20, 130, 10)
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.plot(results['Temp'], results['Rref{}'.format(i)], label='#{}'.format(i))
ax.plot(data_sheet_temps, data_sheet_resistance_min, marker='*', label='spec_min')
ax.plot(data_sheet_temps, data_sheet_resistance_typ, marker='*', label='spec_typ')
ax.plot(data_sheet_temps, data_sheet_resistance_max, marker='*', label='spec_max')
ax.grid(which='both')
ax.legend(loc='best')
ax.set_xlabel('Temperature [Celsius]')
ax.set_ylabel('Resistance [ohm]')
ax.set_ylim(bottom = 180, top = 420)
ax.set_xlim(left = -30, right = 130)
fig.savefig(filename)


title_str = 'Rsns over Rref vs Temperature'
data_sheet_TCR = .0025
data_sheet_temps = range(-20, 130, 10)
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for i in sensors:
    ax.plot(results['Temp'], results['Rsns/Rref {}'.format(i)], label='#{}'.format(i))
ax.plot(data_sheet_temps, [.5 for i in data_sheet_temps], marker='*', label='datasheet')
ax.grid(which='both')
ax.legend(loc='best')
ax.set_xlabel('Temperature [Celsius]')
ax.set_ylabel('ratio of Rsns to Rref')
ax.set_ylim(bottom = .45, top = .55)
ax.set_xlim(left = -30, right = 130)
fig.savefig(filename)

#plot TCR across temperature datapoints
def find_TCR(aseries, temps):
    alist = []
    for i in range(len(aseries) - 1):
        alist.append(((aseries[i+1]/aseries[i])-1)/(temps[i+1]-temps[i]))
    return alist
adict = {}
title_str = 'point-wise TCR vs Temperature'
data_sheet_TCR = .0025
data_sheet_temps = range(-20, 130, 10)
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
means = []
for i in sensors:
    adict['Rsns{}'.format(i)] = find_TCR(results['Rsns{}'.format(i)],results['Temp'])
    adict['Rref{}'.format(i)] = find_TCR(results['Rref{}'.format(i)],results['Temp'])
    means.append(np.mean(adict['Rsns{}'.format(i) ]))
    means.append(np.mean(adict['Rref{}'.format(i) ]))
    ax.plot(results['Temp'][1:], adict['Rsns{}'.format(i)])
    ax.plot(results['Temp'][1:], adict['Rref{}'.format(i)])
ax.plot(data_sheet_temps, [np.mean(means) for i in data_sheet_temps],'rs', label='mean of data gathered')
ax.plot(data_sheet_temps, [.0025 for i in data_sheet_temps], 'go', label='datasheet')
ax.grid(which='both')
ax.legend(loc='best')
ax.set_xlabel('Temperature [Celsius]')
ax.set_ylabel('TCR [/K]')
ax.set_ylim(bottom = .001, top = .005)
ax.set_xlim(left = -30, right = 130)
fig.savefig(filename)
    



