import pyvisa
import Rigol_DP832
import tek2024b
import numpy as np
from math import sqrt
import time
'''
Uses tektronix tps2024b in conjuction with Rigol_DP832. 
Load resistor used to test current limiting and current protection. 
Current limit:

Over current protection:

Sweeps channel 1 output between 2 and 4 Volts, in .2V increments. 

'''
rm = pyvisa.ResourceManager()
dc_supply = Rigol_DP832.Rigol_DP832(rm)
tek = tek2024b.tek2024b(rm)
ch1 = tek2024b.channel(tek, 1)
dc_supply.write('*CLS')
resistance = float(input('What value resistor do you have for a load?\n'))
power = float(input('What is the power rating of your load?\n'))
v_rating = sqrt(power*resistance)
print('The resistor can handle {0:.3G} volts, and {1:.3G} amps\n'.format(v_rating, power/v_rating))

tek.selectedChannel = 1
tek.trigger('DC', 1, 'AUTO')
ch1.set_vScale(v_rating*.2)
tek.set_hScale(tdiv=2.5)

current_limit = sqrt(power*resistance) - .1
print('current limit is {:.3G}'.format(current_limit))
shut_off_current = sqrt(power*resistance)

print('the output will turn off if current exceeds {:.3G}\n if that is the protection limit'.format(shut_off_current))

print('test over current protection\n')
dc_supply.apply(10.0)
time.sleep(4)
dc_supply.turn_off()
dc_supply.write(':OUTPut:OCP:CLEAR CH{}'.format(1))
print('test current limit\n')
dc_supply.i_protection_level = 3.0
dc_supply.apply(10.0, current_limit = 1.0/4.7)
time.sleep(4)
dc_supply.turn_off()
#test sweeping DC levels

dc_levels = np.arange(1, 3, .3)
dc_supply.apply(0)

for level in dc_levels:
    dc_supply.apply(level, current_limit = 3)
    time.sleep(2)

dc_supply.turn_off()
print(dc_supply.query('*ESR?'))