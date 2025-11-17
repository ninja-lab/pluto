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


# ac_supply.flush_buffer()
# print("AC current on phase 1 is: " + ac_supply.measure_current(1))
# print("AC frequency on phase 1 is: " + ac_supply.measure_frequency(1))

# ac_supply.sendReset()
# ac_supply.output_on();

try:
    (ac_supply.read_until_flush())
except UnboundLocalError:
    pass
'''
ac_supply.source_voltage(0, 10)
ac_supply.source_frequency(367, 0)
ac_supply.set_current_limit(13)

print('measured current with output on:')
print(ac_supply.measure_current(1))
print(ac_supply.measure_current(2))
print(ac_supply.measure_current(3))
print(ac_supply.measure_frequency(1))
print(ac_supply.measure_phase_power(1))
print(ac_supply.measure_phase_power(2))
print(ac_supply.measure_phase_power(3))
print(ac_supply.measure_phase_va(1))
print(ac_supply.measure_phase_va(2))
print(ac_supply.measure_phase_va(3))
print(ac_supply.measure_total_power())
print(ac_supply.measure_total_va())
ac_supply.output_off()

'''


