import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
'''
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

'''

data = np.array([['','Col1','Col2'],
                ['Row1',1,2],
                ['Row2',3,4]])
print("data is:\n")
print(data)
print()
                
#print(data[1:,0])
my_dict = {1: ['1', '3'], 2: ['1', '2'], 3: ['2', '4']}
print(my_dict)
print()
#indices are made as 0, 1,...
print(pd.DataFrame(my_dict))


my_df = pd.DataFrame(data=[4,5,6,7], index=range(0,4), columns=['A'])
print("my_df:\n")
print(my_df)

#make a series out of a dictionary
my_series = pd.Series({"Belgium":"Brussels", "India":"New Delhi", "United Kingdom":"London", "United States":"Washington"})
#make a DataFrame with indices as countries and capitals the data, 
my_df = pd.DataFrame(my_series, columns = ['capitals'])
print("my_df:\n")
print(my_df)

df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [.1, .2, .5]]), columns=['some', 'words', 'here'])
print(df.shape)
print(df.index)
print(len(df.index))
print(df.columns.values)
print(type(df.columns.values))
print(type(df.columns.values[0]))

#section 3
print(df.shape)
print(df)
print(df.set_index('words'))
print(df.shape)

#add rows to a dataframe
#frequencies are the indices
freqs = [.2, .5, 1.0, 2.0, 5.0]
#currents are the columns
currents = ['8.0 auto', '8.0 cursor', '9.0', '10.0']

freq_data = pd.DataFrame(index= freqs, columns = currents )
print(freq_data)
#write whole DataFrame to CSV
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
title_str = 'For Pandas Test'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
freq_data.to_csv(path_or_buf=filename)

#edit dataframe given a frequency and current, then overwrite
freq = .5
current = '8.0 cursor'
value = 7
freq_data.at[freq, current] = 7
print(freq_data)
freq_data.to_csv(path_or_buf=filename)














