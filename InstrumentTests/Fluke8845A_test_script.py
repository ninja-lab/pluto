# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 17:28:02 2021

@author: Erik.Iverson
"""

import pyvisa

import numpy as np
from math import sqrt
import time
import instrument_strings
from Fluke8845A import Fluke8845A
from serial import SerialException
import sys


rm = pyvisa.ResourceManager('C:\\Windows\\System32\\visa64.dll')
for resource_id in rm.list_resources():
    try:

        inst = rm.open_resource(resource_id,send_end=True, 
                                baud_rate=230400)#,
                                #parity=pyvisa.constants.Parity.even)#,
                                #stop_bits=pyvisa.constants.StopBits.two,
                                #serialtermination=pyvisa.constants.SerialTermination.none) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.DMM8845A:
            dmm = Fluke8845A(inst)
            
            print("Connected to: " + dmm.name.rstrip('\n'))
            break
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
    except SerialException:
        print('port is closed!')
        sys.exit()

try: 
    print(dmm.measure_resistance())
    #dmm.set_date() #this works, but can't read back
    #print(dmm.get_date()) can't get this to work
    dmm.beep()
    #dmm.beep()
    #dmm.beep()
    #dmm.display('liquid')
    
  
    '''
    set up for 100 resistance readings to
    be read all at .
    Trigger is IMM by default.
    '''
    dmm.configure_res(nplcs=1, samples=100)
    time.sleep(.1)
 
    time.sleep(.1)
    dmm.set_trigger('IMM')
    time.sleep(.1)
    delay = dmm.compute_delay()
    print('delay should be {} seconds'.format(delay))
    
    dmm.initiate()
    time.sleep(delay)
    print('trying to get data now')
    data = dmm.fetch()
    print('fetch returned')
    #print(data) 
    print('received {} measurements'.format(data.size))
    
    dmm.configure_res(nplcs=.2, samples=200)
    delay = dmm.compute_delay()
    dmm.initiate()
    time.sleep(delay)
    print('trying to get data now')
    data = dmm.fetch()
    print('fetch returned')
    #print(data) 
    print('received {} measurements'.format(data.size))
    
    dmm.configure_res(nplcs=.2, samples=10, delay=.6)
    delay = dmm.compute_delay()
    dmm.initiate()
    time.sleep(delay)
    print('trying to get data now')
    data = dmm.fetch()
    print('fetch returned')
    #print(data) 
    print('received {} measurements'.format(data.size))
    
    
    #dmm.write('SYStem:LOCal')
    #dmm.close()
    
    
except pyvisa.VisaIOError:
    print('something bad happened')
    print(dmm.read_errors())
    
except NameError:
    print('DMM did not connect!')


#rm.close()
