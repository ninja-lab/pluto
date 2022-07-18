# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 10:51:17 2022

@author: eriki
"""

import pyvisa
import Rigol_DP832
#import 

import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()

'''
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.bk8614:
            load = bk8614.bk8614(inst)
            print("Connected to: " + load.name.rstrip('\n'))
        elif name_str == instrument_strings.RigolDP832:
            supply = Rigol_DP832.Rigol_DP832(inst)
            print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
'''