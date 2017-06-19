import pyvisa
import SW5250A
import numpy as np
from math import sqrt
import time
import instrument_strings
'''

'''
rm = pyvisa.ResourceManager()


for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.SW5250A:
            ac_supply = SW5250A.SW5250A(inst)
            print("Connected to: " + ac_supply.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")