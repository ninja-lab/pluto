# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 10:00:35 2019

@author: Erik
"""
import pyvisa
import tek2024b
import re
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


rm = pyvisa.ResourceManager()
tup =  rm.list_resources()
tekPattern =re.compile('TEKTRONIX,TPS 2024B,')

for resource_id in tup :
    try:
        
        inst = rm.open_resource(resource_id, send_end=True )
        name_str = inst.query('*IDN?').strip()
        #print(name_str)
        #print('resource_id: {}'.format(resource_id))
        if tekPattern.match(name_str) is not None:
            scope = tek2024b.tek2024b(inst)

    except pyvisa.errors.VisaIOError:
        pass

#ch1 = tek2024b.channel(scope, 1, atten=10)
#ch2 = tek2024b.channel(scope, 2, atten=10)
#ch3 = tek2024b.channel(scope, 3, atten=100)
ch4 = tek2024b.channel(scope, 4, atten=10)
#ch1.set_waveformParams()
#ch2.set_waveformParams()
#ch3.set_waveformParams()
ch4.set_waveformParams()

#psua_time, psua = ch1.get_waveform(debug=False, wait=False)
#time1, step_in = ch2.get_waveform(debug=False, wait=False)
time1, tp9_response  = ch4.get_waveform(debug=False, wait=False)
#vout_time, vout = ch4.get_waveform(debug=False, wait=False)
timeStamp = datetime.now().strftime('-%m_%d_%Y_%H_%M')
#df = pd.DataFrame(data = {'time1': time1, 'input': step_in, 'time2':time2, 'tp9_response': tp9_response})
#save_loc = 'C:\\Users\\Erik\\Dropbox (Amber Kinetics)\\Engineering\\Electrical\\PCBs\\Motherboard\\'
#df.to_csv(path_or_buf=save_loc+'tp10'+timeStamp+'.csv')



        