# -*- coding: utf-8 -*-
"""
Created on Thu May 20 17:10:55 2021

@author: eriki
"""
import pyvisa
import Rigol_DP832
import bk4054b
import numpy as np
from math import sqrt
import time
import instrument_strings

rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.bk4054b:
            funcgen = bk4054b.bk4054b(inst)
            print("Connected to: " + funcgen.name.rstrip('\n'))
        #elif name_str == instrument_strings.RigolDP832:
        #    supply = Rigol_DP832.Rigol_DP832(inst)
        #   print("Connected to: " + supply.name.rstrip('\n'))
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
        

funcgen.channel1_on()
funcgen.set_freq(1, 5e3)
funcgen.set_offset(1, 1.65)
funcgen.set_ampl(1, 3.3)
funcgen.set_wtyp(1, 'SQUARE')
funcgen.phase_coupling(180)
#funcgen.channel1_on()
funcgen.channel2_on()
time.sleep(2)
for p in range(140, 220, 10):
    funcgen.phase_coupling(p)
    time.sleep(1)
funcgen.channel1_off()
funcgen.channel2_off()
    