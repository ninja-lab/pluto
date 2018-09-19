# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 15:13:41 2017

@author: Erik
"""

import pandas as pd
import numpy as np
#import time
from datetime import datetime
import matplotlib.pyplot as plt
from cycler import cycler

save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
ls_cycle = cycler(ls=['--', '-.'])
marker_cycle= cycler(marker=['+', 'x'] )

results = pd.read_csv(save_loc+'ControlsPowerTrainEfficiency2017-10-17_10_55.csv', index_col=['f_sw', 'command'])

#results 2 has the command as the higher level index- easier to use this 
#when plotting at 1 switching frequency

results2 = results.swaplevel()
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')

'''
PLOT EFFICIENCY VS OUTPUT CURRENT WITH FAMILY OF CURVES OF DIFFERING SWITCHING FREQUENCY

title_str = 'Efficiency and Switching Freq, CSD18563Q5A '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for freq in results2.index.levels[1]:
    ax.plot(results2['i_out'].loc[:,freq],results2['efficiency'].loc[:,freq], label = str(round(freq/1000,0))+'kHz')
ax.grid()
ax.legend(loc=4) 
ax.set_xlabel('DC Load Current')
ax.set_ylabel('% Efficiency')
ax.set_ylim(bottom = 0.6, top = 1.00)
ax.set_xlim(left=0, right = 25)
fig.savefig(filename)
'''

'''
PLOT TEMPERATURES OF POINTS MEASURED ACROSS OUTPUT CURRENT WITH FAMILY OF CURVES OF DIFFERING SWITCHING FREQUENCY

title_str = 'Top FET (1 of 2) Temp and Switching Freq, CSD18563Q5A '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for freq in results2.index.levels[1]:
    ax.plot(results2['i_out'].loc[:,freq],results2['top_fet_temp'].loc[:,freq], label = str(round(freq/1000,0))+'kHz')
ax.grid()
ax.legend(loc=0) 
ax.set_xlabel('DC Load Current')
ax.set_ylabel('Temp [C]')
ax.set_ylim(bottom = 25, top = 125)
ax.set_xlim(left=0, right = 25)
fig.savefig(filename)

title_str = 'Bot FET Temp and Switching Freq, CSD18563Q5A '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
fig, ax = plt.subplots(subplot_kw={'title': name})
ax.set_prop_cycle(color_cycle*ls_cycle)
for freq in results2.index.levels[1]:
    ax.plot(results2['i_out'].loc[:,freq],results2['bot_fet_temp'].loc[:,freq], label = str(round(freq/1000,0))+'kHz')
ax.grid()
ax.legend(loc=0) 
ax.set_xlabel('DC Load Current')
ax.set_ylabel('Temp [C]')
ax.set_ylim(bottom = 25, top = 125)
ax.set_xlim(left=0, right = 25)
fig.savefig(filename)
'''
'''
PLOT LOSSES MEASURED ACROSS OUTPUT CURRENT WITH FAMILY OF CURVES OF DIFFERING SWITCHING FREQUENCY 
'''
title_str = 'Losses and Switching Freq, CSD18563Q5A '
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_') 
fig, ax = plt.subplots(subplot_kw={'title': name})

ax.set_prop_cycle(color_cycle*ls_cycle)
results2['losses'] = results2['v_in']*results2['i_in'] - results2['v_out']*results2['i_out']
for freq in results2.index.levels[1]:
    ax.plot(results2['i_out'].loc[:,freq],results2['losses'].loc[:,freq], label = str(round(freq/1000,0))+'kHz')
ax.grid()
ax.legend(loc=4) 
ax.set_xlabel('DC Load Current')
ax.set_ylabel('Losses [W]')
ax.set_ylim(bottom = 0, top = 10)
ax.set_xlim(left=0, right = 25)
fig.savefig(filename)