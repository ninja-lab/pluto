# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 15:07:57 2021

@author: eriki
"""

import time
import pyvisa
import re
from datetime import datetime
import instrument_strings

import sdm3045x

rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        print(name_str)
        if name_str == instrument_strings.sdm3045x_1:
            meter = sdm3045x.sdm3045x(inst)
            print("Connected to: " + meter.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")

#it takes 1 second! 