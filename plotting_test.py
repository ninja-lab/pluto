import plotting
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
from cycler import cycler

testR1 = np.arange(100, 200, 10)
testR2 = np.arange(110, 210, 10)
xvals = np.arange (1, 2, .1)
legend_strs = ['R1', 'R2']
xlabel = 'current'
ylabel = 'resistance'
title_str = 'Sample Plot'

#plotting.easy_plot([testR1, testR2], xvals, legend_strs, xlabel, ylabel, title_str)
'''
xvals1 = np.arange(1.1, 2.1, .1)
xvals2 = np.arange(1.3, 2.3, .1)

fig, ax1 = plt.subplots()
ax1.plot(xvals1, testR1, 'g--')
ax1.plot(xvals2, testR2, 'b--')

ax1.set_xlabel('xlabel')
ax1.set_ylabel('ylabel', color = 'b')
ax1.legend(['123', '456'])

for tl in ax1.get_yticklabels():
    tl.set_color('b')

time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
name = title_str + time_stamp
print(name)
plt.title(name)
fig = plt.gcf()
plt.show()
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
filename = (save_loc + name + '.png').replace(' ','_')
print(filename)
fig.savefig(filename)
'''
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
xvals1 = np.arange(1.1, 2.1, .1)
xvals2 = np.arange(1.3, 2.3, .1)
df = pd.DataFrame()
df['testR1'] = testR1
df['xvals1'] = xvals1
title_str1 = 'Sample Plot1'
title_str2 = 'Sample Plot2'
name1 = title_str1 + time_stamp
name2 = title_str2 + time_stamp

fig1, ax1 = plt.subplots(subplot_kw={'title': name1})
color_cycle =  cycler(color= ['g', 'b', 'r', 'k', 'c', 'm', 'y'])
#marker_cycle = cycler(marker = ['o', 'v', 'x', '*', 's', '+' ])
ls_cycle = cycler(ls=['--'])
ax1.set_prop_cycle(color_cycle*ls_cycle)

fig2, ax2 = plt.subplots(subplot_kw={'title': name2})

ax1.plot(xvals2, testR2, label='some data')
ax1.plot(df['xvals1'], df['testR1'], label = 'more data')
ax1.legend()
ax1.text(.8, .05, 'avg is __', transform=ax1.transAxes)
ax1.grid()
ax1.set_ylim(bottom = 20, top=80)
ax2.plot(xvals2, testR2, 'b--')

#ax1.set_xlabel('xlabel')
#ax1.set_ylabel('ylabel', color = 'b')


#for tl in ax1.get_yticklabels():
 #   tl.set_color('b')



save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
filename1 = (save_loc + name1 + '.png').replace(' ','_')
filename2 = (save_loc + name2 + '.png').replace(' ','_')
fig1.show()
fig1.savefig(filename1)
fig2.show()
fig2.savefig(filename2)


