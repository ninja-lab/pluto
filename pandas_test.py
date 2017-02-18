import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

results = pd.DataFrame()
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'


# sample inductances
#L1 = np.arange(0, 20 + 2, 2)
L1 = list(range(0,11))
L2 = np.arange(0.5, 22, 2)
L3 = np.arange(.6, 22, 2)
freqs = [.1, .2, .5, 1,2,5,10,20,50, 100, 200]
temp = {}
#as returned from get_L_vs_freq():
temp['8Amps'] = L1
temp['9Amps'] = L2
temp['10Amps'] = L3

results = pd.DataFrame(temp, index=freqs)
results.to_csv(path_or_buf=save_loc + 'test.csv')
title_str = 'Inductance vs Frequency'
axes  = results.plot(kind='line', logx=True, title=title_str)
axes.set_xlabel('Frequency [Hz]')
axes.set_ylabel('Inductance [H]')
fig = plt.gcf()
plt.show()
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
name = title_str + time_stamp
filename = (save_loc + name + '.png').replace(' ','_')
fig.savefig(filename)

