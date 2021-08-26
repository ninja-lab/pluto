# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 10:59:31 2021

@author: eriki
"""

from rigol_ds1054z import rigol_ds1054z
import time
import pyvisa
import re

#had to change from 1104 to 1054 on this next line
ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')
rm = pyvisa.ResourceManager()
tup =  rm.list_resources()

for resource_id in tup :
    try:
        inst = rm.open_resource(resource_id, send_end=True )
        print('hi')
        name_str = inst.query('*IDN?').strip()
        if ScopePattern.match(name_str) is not None:
            print(name_str)
            scope = rigol_ds1054z(inst)
            print('Connected to: {}'.format(name_str))

    except pyvisa.errors.VisaIOError:
        pass
print(scope.getName())
#scope.print_info()
#scope.reset()
#sw node is channel 1
scope.setup_channel(channel=1,on=1,offset_divs=2.0, volts_per_div=2.0)
#Vout is channel 2
scope.setup_channel(channel=2,on=1,offset_divs=0,volts_per_div=5.0)
scope.setup_channel(channel=3,on=1,offset_divs=-2,volts_per_div=.5, probe=1)
scope.setup_timebase(time_per_div='5us',delay='10us')
scope.setup_mem_depth(memory_depth=6e3)
scope.setup_trigger(channel=2,slope_pos=1,level='0v')
scope.repeat_trigger()
#scope.setup_i2c_decode(sda_channel=1, scl_channel=2)
#scope.single_trigger()
#i2c = smbus.SMBus(1)
#i2c.write_quick(0x50) #
#time.sleep(3)
'''
for measurement in scope.single_measurement_list:
	scope.get_measurement(channel=1, meas_type=measurement)
for measurement in scope.single_measurement_list:
	scope.get_measurement(channel=2, meas_type=measurement)
'''
time.sleep(1)
scope.get_measurement(channel=2, meas_type=scope.max_voltage)
scope.get_measurement(channel=2, meas_type=scope.rms_voltage)
#scope.write_screen_capture(filename='squarewave.png')
#scope.write_waveform_data(channel=1)
#scope.write_waveform_data(channel=2)
#scope.close()
