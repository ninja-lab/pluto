# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:53:46 2019

@author: Erik
"""

from rigol_ds1054z import rigol_ds1054z
import time
import pyvisa
import re
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import pandas as pd
import sys
from math import ceil 
'''
With USB: 
%time scope.query('*IDN?')
Wall time: 1e+03 µs
Out[53]: 'RIGOL TECHNOLOGIES,DS1104Z,DS1ZA191605554,00.04.04.SP4'


'''

#had to change from 1104 to 1054 on this next line
ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
rm = pyvisa.ResourceManager()
tup =  rm.list_resources()

for resource_id in tup :
    try:
        inst = rm.open_resource(resource_id, send_end=True )
        #print('hi')
        name_str = inst.query('*IDN?').strip()
        if ScopePattern.match(name_str) is not None:
            print(name_str)
            scope = rigol_ds1054z(inst)
            print('Connected to: {}'.format(name_str))

    except pyvisa.errors.VisaIOError:
        pass
try: 
    x = scope
except NameError:
    sys.exit()

# first TMC byte is '#'
# second is '0'..'9', and tells how many of the next ASCII chars
#   should be converted into an integer.
#   The integer will be the length of the data stream (in bytes)
# after all the data bytes, the last char is '\n'
def tmc_header_bytes(buff):
    return 2 + int(buff[1])
def expected_data_bytes(buff):
    return int(buff[2:tmc_header_bytes(buff)])
def expected_buff_bytes(buff):
    return tmc_header_bytes(buff) + expected_data_bytes(buff) + 1

scope.write('WAV:SOUR CHAN' + str(3))
scope.write('WAV:MODE MAX')
scope.write('WAV:FORM BYTE')


params = scope.query('WAV:PRE?').split(',')
form = params[0]
typ = params[1]
x_num = int(params[2])
x_incr = float(params[4])
x_origin = float(params[5])
y_increment = float(params[7])
y_origin = float(params[8])
y_ref = float(params[9])
'''
print(params)
print('form: {}'.format(form))
print('type: {}'.format(typ))
print('x origin {}'.format(x_origin))
print('yincrement {}'.format(y_increment))
print('yorigin {}'.format(y_origin))
print('y_ref {}'.format(y_ref))
print('x_num {}'.format(x_num))
print('x_incr {}'.format(x_incr))
'''
#data_y = scope.inst.query_binary_values(':WAV:DATA?').split(',')[1:]
#query_binary_values must skip the tmc header? 

#tmcHeaderLen = tmc_header_bytes(buff)
#expectedDataLen = expected_data_bytes(buff)
#buff = buff[tmcHeaderLen: tmcHeaderLen+expectedDataLen]
#print('tmcHeaderLen: {}'.format(tmc_headerLen))
#print('expectedDataLen: {}'.format(expectedDataLen))

def myConverter(elem):
    try:
        return float(elem)
    except ValueError:
        return float(elem[11:])

def capture():
    '''
    Capture all points on all channels. 
    Find out the memory depth to see if there are more points 
    than can be read at one time (in byte mode). 
    Max read amount is 250,000 pts in byte mode.
    1 channel: Only the smalled memdepth setting of 120,000 can be read at once. 
        The larger memdepth settings require multiple reads.
    2 channels:
        The two smallest memdepth settings of 6,000 and 60,000 pts can be read at once. 
        The larger ones require multiple reads. 
    3/4 channels: 
        The two smallest memdepth settings of 3,000 and 30,000 pts can be read at once. 
        The larger ones require multiple reads. 
        
    '''
    pass


if form == '0':
    '''
    query_binary_values runs in 2ms for 1200 points
    There is no TMC header
    '''
    #Find out how many points there are to read first. 
    #Is it less than 250,000? 
    
        # Scan for displayed channels
    chanList = []
    for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH"]:
        response = scope.query(channel + ":DISP?")
        # If channel is active
        if response == '1':
            chanList += [channel]
    
    
    memdepth = int(scope.query('ACQuire:MDepth?'))
    max_read = 250000
    num_reads = ceil(memdepth / max_read)
    data = pd.DataFrame(data=np.zeros((memdepth,len(chanList))),columns = chanList)
    #find out if the mode is normal, max, or raw
    #if not in normal mode, stop the scope from triggering
    mode = scope.query('WAV:MODE?')
    if mode in ['MAX', 'RAW']:
        scope.write('STOP')
    for channel in chanList:
        
        scope.write('WAV:SOUR {}'.format(channel))
        params = scope.query('WAV:PRE?').split(',')
        form = params[0]
        typ = params[1]
        x_num = int(params[2])
        x_incr = float(params[4])
        x_origin = float(params[5])
        y_increment = float(params[7])
        y_origin = float(params[8])
        y_ref = float(params[9])
        ser = pd.Series()
        for i in range(num_reads):
            start = max_read*i + 1 #1, 250,001, 500,001, ...
            if i == num_reads - 1:
                stop = memdepth
            else:
                stop = start + max_read - 1 #250,000, 500,000, 750,000, ...
            scope.write('WAVeform:STARt {}'.format(start))
            scope.write('WAVeform:STOP {}'.format(stop))
            chunk = scope.inst.query_binary_values(':WAV:DATA?', datatype='B')
            scaled_data_y = [(y-y_origin-y_ref)*y_increment for y in chunk]
            ser = ser.append(pd.Series(scaled_data_y))
    
        data[channel][:] = ser[:]
    
    data['time'] = [x * x_incr for x in range(x_num)] #x_num same as memdepth? 

elif form == '2':
    '''
    query_ascii_values returns the tmc header in the first element, combined 
    with the first data point in a single string: '#90000157702.879998e+00'
    runs in 5ms
    '''
    #scaled_data_y = scope.inst.query_ascii_values(':WAV:DATA?', converter=myConverter)
    
    '''
    query returns the whole response in a single string,
    and the header could be useful 
    It runs in 15ms for 1200 pts
    '''
    buff = scope.inst.query(':WAV:DATA?')#, converter=myConverter)
    # Append data chunks
    # Strip TMC Blockheader and terminator bytes
    buff = buff[tmc_header_bytes(buff):-1] 
    # Strip the last \n char
    newbuff = buff[:-1].split(',')
    scaled_data_y = list(map(float, newbuff))
    
#print('buff[0:20]: ')
#print(buff[0:20])
#YINCrement is Vertical Scale / 25
'''
for 200mV/div, YINCrement = 8mV
is this the y resolution? 
'''


#data_x = [x * x_incr for x in range(len(scaled_data_y))]





#data_x,data_y = scope.get_waveform(2)
#plt.plot(data['time'][0:10000], data['CHAN3'][0:10000] ,label='Measured' )

#plt.xlabel('Time [sec]')
#plt.ylabel('Voltage [V]')
#plt.title("Interesting Square Wave")
#plt.grid()
#plt.legend()
#plt.show()
'''
plt.plot(data_x, buff ,label='Measured' )
plt.xlabel('Time [sec]')
plt.ylabel('Voltage [V]')
plt.title("Interesting Square Wave")
plt.grid()
plt.legend()
plt.show()
'''