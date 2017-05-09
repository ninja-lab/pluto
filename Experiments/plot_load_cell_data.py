

import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler



load_cells = ['1','2']
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--'])
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'HT characterization data'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'       
results = pd.read_csv(save_loc+'HT_characterization_data2017-04-22_11_25.csv')

       
#plot the error at each point of each load cell, compared to force
title_str = 'Error % of Full Scale'
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
error_fig, error_ax = plt.subplots(subplot_kw={'title': name})
avg_error = 0
error_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    error_ax.plot(results['{}forces'.format(load_cell_num)], results['{}error'.format(load_cell_num)], label = 'HT#{}'.format(load_cell_num))
    avg_error = np.mean((avg_error, np.mean(results['{}error'.format(load_cell_num)])))
error_ax.text(.8, .05, 'avg is {:.2f}%'.format(avg_error), transform=error_ax.transAxes)         
error_ax.grid()
error_ax.legend() 
error_ax.set_xlabel('Force [lb]')
error_ax.set_ylabel('% Full Scale Error')
error_ax.set_ylim(bottom = -5, top = 5)
filename = (save_loc + name + '.png').replace(' ','_')
error_fig.savefig(filename)
   
#plot the sensitivity with range .01 to .03 mV/V 
title_str = 'Sensitivity of the Load Cells '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
avg_sensitivity = 0
sns_fig, sns_ax= plt.subplots(subplot_kw={'title': name})
sns_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    x_data = results['{}forces'.format(load_cell_num)]
    length = results['{}forces'.format(load_cell_num)].size
    x_data = x_data[3: length - 3]
    y_data = results['{}sensitivity'.format(load_cell_num)][3:length-3]
    sns_ax.plot(x_data, y_data, label = 'HT#{}'.format(load_cell_num))
    avg_sensitivity = np.mean((avg_sensitivity, np.mean(results['{}sensitivity'.format(load_cell_num)])))
    
sns_ax.text(.8, .05, 'avg is {:.4f}mV/V'.format(avg_sensitivity), transform=error_ax.transAxes) 
sns_ax.scatter(np.arange(0, 2000, 100),[.001 for i in range(20)] , c='r', marker='*', label='ideal')#r*', label = 'ideal')
sns_ax.grid()
sns_ax.legend()
sns_ax.set_ylim(bottom = 0, top = .003)
sns_ax.set_xlim(left = 0, right=2500)
sns_ax.set_xlabel('Force [lbs]')
sns_ax.set_ylabel('Sensitivity in V/V')
filename = (save_loc + name + '.png').replace(' ','_')
sns_fig.savefig(filename)

#Plot bridge voltages below 500 lbs in force
title_str = 'Bridge Voltage of the Load Cells below 500lbs '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
brdg_fig, brdg_ax= plt.subplots(subplot_kw={'title': name})
brdg_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    bool_array = results['{}forces'.format(load_cell_num)] < 501
    y_data = results['{}HT_brdg'.format(load_cell_num)][bool_array]
    x_data = results['{}forces'.format(load_cell_num)][bool_array]
    brdg_ax.plot(x_data,y_data ,label = 'HT#{}'.format(load_cell_num))
brdg_ax.scatter([i*10 for i in range(50)], [(.01*i/50)*500/2204 for i in range(0, 50)], c='r', marker='*', label = 'ideal')
brdg_ax.grid()
brdg_ax.legend(loc=4)
brdg_ax.set_xlabel('Force [lb]')
brdg_ax.set_ylabel('bridge output [V]')
filename = (save_loc + name + '.png').replace(' ','_')
brdg_fig.savefig(filename)

#Plot bridge voltages from 0 to full scale
title_str = 'Bridge Voltage of the Load Cells '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
brdg_fig, brdg_ax= plt.subplots(subplot_kw={'title': name})
brdg_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    y_data = results['{}HT_brdg'.format(load_cell_num)]
    x_data = results['{}forces'.format(load_cell_num)]
    brdg_ax.plot(x_data, y_data ,label = 'HT#{}'.format(load_cell_num))
brdg_ax.scatter([i*2204/50 for i in range(50)], [(.01*i/50) for i in range(0, 50)], c='r', marker='*', label = 'ideal')
brdg_ax.grid()
brdg_ax.legend(loc=4)
brdg_ax.set_xlabel('Force [lb]')
brdg_ax.set_ylabel('bridge output [V]')
filename = (save_loc + name + '.png').replace(' ','_')
brdg_fig.savefig(filename)