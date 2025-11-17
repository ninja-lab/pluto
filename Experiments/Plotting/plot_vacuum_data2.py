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

sensors = []

currents = [.007, .009, .011, .013, .015, .017, .019]
'''
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
    
 
 the rate of disipation is dependent on the thermal conductivity of the air
 which is proportional to pressure
 so measure power disippation at such  
 '''
 
#plot resistance vs current for each sensor.
#get 4 curves for each current level, representing different pressure intervals

#some sensor data is messed up- sensors were damaged in test
for i in sensors:
    title_str = 'Effect of Heating Current on Resistance (sensor{})'.format(i)
    name = title_str + time_stamp
    filename = (save_loc + name + '.png').replace(' ','_')
    fig, ax = plt.subplots(subplot_kw={'title': name})
    ax.set_prop_cycle(color_cycle*marker_cycle)
    
    #get a single sensor data
    sensor_data = results.filter(regex='#{}'.format(i))
    #distinquish between current levels first, since indexes of pressure levels will be different for each
    c1 = []
    c2 = []
    c3 = []
    c4 = []
    
    for level in currents:
        #filter on current
        current_frame = sensor_data.filter(regex = '{:.3f}A'.format(level))
        vals = []
        for interval in [(0,50),(51,100), (101,200), (600,1000)]:
            #find where pressure levels are in a certain interval
            bools = (interval[0] < current_frame['pressure#{}_{:.3f}A'.format(i,level)]) & (current_frame['pressure#{}_{:.3f}A'.format(i,level)] < interval[1]) 
            print('interval {} to {} at current: {:.3f}'.format(interval[0],interval[1],level))
            print('number of true: {}'.format(np.sum(bools)))
            #get a dataframe of sensor data for the certain interval
            pressure_interval = current_frame[bools] 
            #average the resistances found
            Ravg = pressure_interval.filter(regex = '^Rsns').mean()[0]
            print('ravg is {:.3f}'.format(Ravg))
            vals.append(Ravg)
        #add the vals to the lists
        c1.append(vals[0])
        c2.append(vals[1])
        c3.append(vals[2])
        c4.append(vals[3])
        
    ax.plot(currents, c1, label = 'snsr#{},0<p<50'.format(i))   
    ax.plot(currents, c2, label = 'snsr#{},51<p<100'.format(i))
    ax.plot(currents, c3, label = 'snsr#{},101<p<200'.format(i))
    ax.plot(currents, c4, label = 'snsr#{},201<p<1000'.format(i))    
    ax.grid(which='both', axis='x')
    ax.legend(loc='best')
    ax.set_xlabel('Current')
    ax.set_ylabel('Resistance')
    ax.set_ylim(bottom = 120, top = 500)
    ax.set_xlim(left = .006, right = .02)
    fig.savefig(filename)        
            
'''
start the lists []...
for each current, divide up into pressure intervals
each current level is a datapoint for 4 curves, representing 4 different pressure intervals
add average resistance value for each interval to the respective curves



'''
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    