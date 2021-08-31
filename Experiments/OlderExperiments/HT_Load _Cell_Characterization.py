import Keysight34972A
import pyvisa
import instrument_strings
import pandas as pd
import numpy as np
import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler

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
101: transducer techniques bridge output
102: transducer techniques amplified output
103: HT Load Cell bridge output
104: HT Load Cell amplified output

Use a transducer techniques 3000 lb load cell for a baseline. 
Calibrate transducer techniques load cell amp with TEDS reader. 
Use hydraulic press to cycle through force points.  

'''

results = pd.DataFrame()
TT_zeros = pd.DataFrame()
HT_zeros = pd.DataFrame()
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'HT characterization data'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
load_cells = []
gain = .000701 # V/pound
for i in range(2):
    TT_brdg = []
    TT_ampl = []
    HT_brdg = []
    HT_ampl = []
    load_cell_num = input('Enter HT Load Cell serial number: ')
    load_cells.append(load_cell_num)
    print('Measuring zero force voltage - ensure 0 force on load cell')
    TT_zero = daq.measure_DCV(101)
    TT_brdg.append(TT_zero)
    TT_zeros = TT_zeros.append({'TTzeros': TT_zero, 'TTzeroForce': TT_zero/gain}, ignore_index=True)
    TT_ampl.append(daq.measure_DCV(102))
    HT_zero = daq.measure_DCV(103)
    HT_brdg.append(HT_zero)
    HT_zeros = HT_zeros.append({'HT_zeros': HT_zero, 'HTzeroForce': HT_zero/gain}, ignore_index=True)
    HT_ampl.append(daq.measure_DCV(104))
    junk = input('Hit enter and cycle through force levels')
    num_meas = 20
    for k in range(num_meas):
        time.sleep(3)
        print('Taking measurement #{}'.format(k))
        if k == num_meas - 2:
            print('get max scale reading now')
            junk = input('hit enter when force is at full scale')
        TT_brdg.append(daq.measure_DCV(101))
        force = daq.measure_DCV(102)
        TT_ampl.append(force)
        HT_brdg.append(daq.measure_DCV(103))
        HT_ampl.append(daq.measure_DCV(104))    
        print('Force is currently {:.1f}lbs'.format(force*3000/5))
    
    junk = input('Ensure 0 force for the last measurement and hit enter')
    TT_zero = daq.measure_DCV(101)
    TT_brdg.append(TT_zero)
    TT_zeros = TT_zeros.append({'TTzeros': TT_zero, 'TTzeroForce': TT_zero/gain}, ignore_index=True)
    TT_ampl.append(daq.measure_DCV(102))
    HT_zero = daq.measure_DCV(103)
    HT_brdg.append(HT_zero)
    HT_zeros = HT_zeros.append({'HT_zeros':HT_zero, 'HTzeroForce': HT_zero/gain} ignore_index=True)
    HT_ampl.append(daq.measure_DCV(104)) 
    results['{}TT_brdg'.format(load_cell_num)] = TT_brdg
    results['{}HT_brdg'.format(load_cell_num)] = HT_brdg
    results['{}TT_ampl'.format(load_cell_num)] = TT_ampl
    results['{}HT_ampl'.format(load_cell_num)] = HT_ampl
    forces = [(3000/5)*i for i in TT_ampl]
    results['{}forces'.format(load_cell_num)] = forces
    # sensitivity = mv fullscale / excitation = force / fullscale force    in units of mV/V
    results['{}sensitivity'.format(load_cell_num)] = [( i/10)*(2204/j) for i,j in zip(HT_brdg, forces)]
    TT_corrected_brdg = [i*.02/5 for i in TT_ampl]
    results['{}error'.format(load_cell_num)] = [(i-j)*100/2204 for i,j in zip(HT_brdg, TT_corrected_brdg)] 
    results = pd.concat([results, TT_zeros, HT_zeros], axis=1) 
    results.to_csv(path_or_buf=filename)
        
'''        
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
   
#plot the sensitivity with range .01 to .03 mV/V 
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
sns_ax.plot([.001 for i in range(30)], np.arange(0, 3000, 100), 'r*', label = 'ideal')
sns_ax.grid()
sns_ax.legend()
sns_ax.set_ylim(bottom = 0, top = .005)
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
brdg_ax.grid()
brdg_ax.legend()
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
brdg_ax.plot([i*60 for i in range(50)], [i*60*.02/3000 for i in range(50)], 'r*', label = 'ideal')
brdg_ax.grid()
brdg_ax.legend()
brdg_ax.set_xlabel('Force [lb]')
brdg_ax.set_ylabel('bridge output [V]')
filename = (save_loc + name + '.png').replace(' ','_')
brdg_fig.savefig(filename)
'''
        