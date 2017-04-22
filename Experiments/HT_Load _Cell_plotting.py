
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler


        
results = pd.DataFrame()

'''
101: transducer techniques bridge output
102: transducer techniques amplified output
103: HT Load Cell bridge output
104: HT Load Cell amplified output

Use a transducer techniques 3000 lb load cell for a baseline. 
Calibrate transducer techniques load cell amp with TEDS reader. 
Use hydraulic press to cycle through force points.  

'''
results = pd.DataFrame()
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'HT characterization data'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'

load_cells = [1,2,3]
results = pd.DataFrame() 
fake_brdg = [i*.00028 for i in range(1, 70)]
i=.0003
results['1HT_brdg'] = [i + j for j in fake_brdg]
i = -.0004
results['2HT_brdg'] = [i + j for j in fake_brdg]
j = 1
temp = []
for i in fake_brdg:
    j = j*(-1)
    num = i+.0005*(-1)**j
    temp.append(num)
results['3HT_brdg'] = temp

#for i in load_cells:
results['1forces'] = [i*3000/.02 for i in results['1HT_brdg']]
results['2forces'] = [i*3000/.02 for i in fake_brdg]      
results['3forces'] = [i*3000/.02 for i in fake_brdg]  
TT_corrected_brdg = fake_brdg
results['1error'] = [(i-j)/3000 for i,j in zip(results['1HT_brdg'], TT_corrected_brdg)]
results['2error'] = [(i-j)/3000 for i,j in zip(results['2HT_brdg'], TT_corrected_brdg)]
results['3error'] = [(i-j)/3000 for i,j in zip(results['3HT_brdg'], TT_corrected_brdg)] 
results['1sensitivity'] = [(i/10)*(3000/j) for i,j in zip(results['1HT_brdg'], results['1forces'])]
results['2sensitivity'] = [(i/10)*(3000/j) for i,j in zip(results['2HT_brdg'], results['2forces'])]
results['3sensitivity'] = [(i/10)*(3000/j) for i,j in zip(results['3HT_brdg'], results['3forces'])]
results.to_csv(path_or_buf=filename)

color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--'])
        
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
   
#plot the sensitivity with range .001 to .003 mV/V 
title_str = 'Sensitivity of the Load Cells '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
avg_sensitivity = 0
sns_fig, sns_ax= plt.subplots(subplot_kw={'title': name})
sns_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    x_data = results['{}forces'.format(load_cell_num)]
    y_data = results['{}sensitivity'.format(load_cell_num)]
    sns_ax.plot(x_data, y_data, label = 'HT#{}'.format(load_cell_num))
    avg_sensitivity = np.mean((avg_sensitivity, np.mean(results['{}sensitivity'.format(load_cell_num)])))
sns_ax.text(.8, .05, 'avg is {:.4f}mV/V'.format(avg_sensitivity), transform=error_ax.transAxes) 
sns_ax.plot([.002 for i in range(30)], np.arange(0, 3000, 100), 'r*', label = 'ideal')
sns_ax.grid()
sns_ax.legend()
sns_ax.set_ylim(bottom = 0, top = .005)
sns_ax.set_xlabel('Force [lbs]')
sns_ax.set_ylabel('Sensitivity in mV/V')
filename = (save_loc + name + '.png').replace(' ','_')
sns_fig.savefig(filename)

#Plot bridge voltages below 500 lbs in force
title_str = 'Bridge Voltage of the Load Cells below 500lbs '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
brdg_fig, brdg_ax= plt.subplots(subplot_kw={'title': name})
brdg_ax.set_prop_cycle(color_cycle*ls_cycle)
for load_cell_num in load_cells:
    #results['
    bool_array = results['{}forces'.format(load_cell_num)] < 501
    y_data = results['{}HT_brdg'.format(load_cell_num)][bool_array]
    x_data = results['{}forces'.format(load_cell_num)][bool_array]
    brdg_ax.plot(x_data,y_data ,label = 'HT#{}'.format(load_cell_num))
brdg_ax.grid()
brdg_ax.legend()
brdg_ax.set_xlabel('Force [lb]')
brdf_ax.set_ylabel('bridge output [V]')
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
brdg_ax.plot([i*60 for i in range(50)], [i*60*.02/3000 for i in range(50)], 'r*', label = 'ideal')
brdg_ax.grid()
brdg_ax.legend()
brdg_ax.set_xlabel('Force [lb]')
brdg_ax.set_ylabel('bridge output [V]')
filename = (save_loc + name + '.png').replace(' ','_')
brdg_fig.savefig(filename)

        