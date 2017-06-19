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



df1 = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],
                    'B1': ['B0', 'B1', 'B2', 'B3'],
                    'C': ['C0', 'C1', 'C2', 'C3'],
                    'D': ['D0', 'D1', 'D2', 'D3']},
                    index=[0, 1, 2, 3])
   

df2 = pd.DataFrame({'A2': ['A4', 'A5', 'A6', 'A7'],
                    'B1': ['B4', 'B5', 'B6', 'B7'],
                    'C2': ['C4', 'C5', 'C6', 'C7'],
                    'D2': ['D4', 'D5', 'D6', 'D7']},
                     index=[0,1,2,3])
 

df3 = pd.DataFrame({'A': ['A8', 'A9', 'A10', 'A11'],
                    'B1': ['B8', 'B9', 'B10', 'B11'],
                    'C': ['C8', 'C9', 'C10', 'C11'],
                    'D': ['D8', 'D9', 'D10', 'D11']},
                    index=[0,1,2,3])
                    
print(df1)
print(df3)
print(pd.concat([df1, df1], axis = 0, ignore_index=True))
adict = {'A': 555}
print('a new df:')
print(pd.DataFrame(adict, index=['string']))
#print(pd.concat([df1, df3], axis = 0, ignore_index=True))
'''

sensors = [1,2,3]
places = ['p1', 'p2', 'p3']
columns = ['data1_{}'.format(i) for i in sensors]
columns.extend(['data2_{}'.format(i) for i in sensors])
results = pd.DataFrame(columns = columns)
print('results before:')
print(results)
data = [1, 10, 1.3, 10.1, .9,10.1] #[data1_1, data2_1, data1_2, etc]
for place in places:
    print(place)
    dict = {}
    for i in sensors: 
        dict['data1_{}'.format(i)] = round(data[i-1],1)
        dict['data2_{}'.format(i)] = round(data[i],1)
    dict['Location'] = place
    this_location = pd.DataFrame(dict, index = np.arange(1))   
    print('this location:')
    print(this_location)
    #results = results.merge(this_location)
    results = pd.concat([results, this_location])
    print('results after ' + place)
    print(results)
    
'''    
sensors = [1,2,3]
places = ['p1', 'p2', 'p3']
columns = ['data1_{}'.format(i) for i in sensors]
columns.extend(['data2_{}'.format(i) for i in sensors])
results = pd.DataFrame(index = places, columns = columns)
print(results)
data_acquired = [1, 10, 1.3, 10.1, .9,10.1] #[data1_1, data2_1, data1_2, etc]
for i in sensors: 
    dict['data1_{}'.format(i)] = data[i-1]
    dict['data2_{}'.format(i)] = data[i]
    
'''    
    
    
    
'''      
print('before')
print(df2)
for key in df3.keys():
    if key in df2.keys():
        print(key)
        print(type(key))
        df2[key] = df3[key]
print('after')
print(df2)


left = pd.DataFrame({'key1': ['Knan', 'Knan', 'Knan', 'Knan'],
                      'key2': ['Kxx1', 'Kxx2', 'Kxx3', 'Kxx4'],
                      'A': ['A0', 'A1', 'A2', 'A3'],
                      'B': ['B0', 'B1', 'B2', 'B3']})
 

right = pd.DataFrame({'key1': ['K0', 'K1', 'K1', 'K2'],
                       'key2': ['K5', 'K6', 'K7', 'K8']})
 
 
 
print('left:')
print(left)
print('right:')
print(right)
result = pd.concat([left, right], ignore_index=True)
print(result)
for key in right.keys():
    if key in left.keys():
        print(key)
        print(type(key))
        left[key] = right[key]
print('after')
print(left)

results1 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization2017-04-28.csv')
results2 = pd.read_csv(instrument_strings.save_loc+'PVC1001_Characterization2017-04-28_14_58.csv')

results = results2.combine_first(results1)


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


df = pd.DataFrame({'A#1_': [1,2,4,6],
                    'B#1_': [50, 101, 200, 100],
                    'I_Rsns#1': [.007, .009, .0071, .0072],
                    'A#2_': [1,2,3,4],
                    'B#2_': [60,200,400,500]},
                    index=[0, 1, 2, 3])

#return a new dataframe with those values in df1.B1 > 100, along with all the values with the same index

data1 = df.filter(regex='#1')[df['B#1_'] > 100]
data2 = df.filter(regex='#2')[df['B#2_'] > 100]
print(data1)
print(data2)
#dataframe mean returns a series
current_lev = data1.filter(regex = 'I_Rsns').mean()[0]
print(current_lev)
#series mean returns a scalar
avg_R = data1['A#1_'].mean()
print(avg_R)

results = pd.concat([data1, data2], axis = 1)
print(results)
'''
#now average the resistance levels in the range obtained, plot this number against the current level
