import pyvisa
from Instruments.rigol_dsa815 import rigol_dsa815
import numpy as np
from math import sqrt
import time
#from Instruments.instrument_strings import *
from Instruments import instrument_strings

rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.RigolDSA815:
            spec_an = rigol_dsa815(inst)
            print("Connected to: " + spec_an.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")