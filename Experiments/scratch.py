# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 11:10:47 2021

@author: eriki
"""

import pyvisa

from datetime import datetime

save_loc = 'C:\\Users\\eriki\\Desktop\\PythonPlots\\'
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')    
title_str = 'CoilDCR'
name = title_str + time_stamp
filename = save_loc + name.replace(' ','_') +'.csv'
rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        inst.baud_rate = 115200
            
        name_str = inst.query('*IDN?').strip()
        print(name_str)

    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")