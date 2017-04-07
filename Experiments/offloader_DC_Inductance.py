import tek2024b
import Agilent33120
import pyvisa
import time
import matplotlib.pyplot as plt
from datetime import datetime
import Rigol_DP832
import pandas as pd
from get_L_vs_freq import get_L_at_freq
from plotting import easy_plot
'''
Command a sinusoidal current, measure current amplitude and phase,
and coil voltage amplitude and phase. Find IV relationship across frequency.
ch1: command
ch2: load voltage
ch3: load current from TP16, scaled to 5A/V
ch4: load current with clamp on probe
Trigger off of function generator sync signal 
TO-DO
slow down func gen after each current level
have visa read delta Time from cursors so it doesn't need to be entered 
add offset automatically. 
Step DC supply remotely 
increase number of DC levels 
Send all raw data to a CSV
'''
rm = pyvisa.ResourceManager()
print(rm.list_resources())

func_gen = Agilent33120.f33120a(rm)
func_gen.displayText("'Hi Erik'")
tek = tek2024b.tek2024b(rm)
ch1 = tek2024b.channel(tek, 1) #input current command
ch2 = tek2024b.channel(tek, 2)
ch3 = tek2024b.channel(tek, 3) 
ch4 = tek2024b.channel(tek, 4, yunit='A') #current from clamp-on probe
dc_supply = Rigol_DP832.Rigol_DP832(rm)

def setup_scope():
    tek.unselectChannels([1,2,3,4])
    tek.selectChannels([1,2,3,4])
    tek.setup_measurements()
    ch1.set_Position(-3)
    ch1.set_vScale(.1)
    ch2.set_Position(-4)
    ch2.set_vScale(.5)
    ch3.set_Position(-10)
    ch3.set_vScale(.2)
    ch4.set_Position(-40)
    ch4.set_vScale(.2)
    tek.set_hScale(frequency = 1, cycles = 3)
    #use external SYNC from function generator to scope external trigger input
    tek.trigger('DC', 'EXT', 'NORMal', 2.5)
    tek.set_averaging(False)
    tek.setImmedMeas(1, "FREQ")
    tek.setup_measurements()
    tek.acquisition(True)
    
def setup_dc_supply():
    '''
    Output1: +24V. Needs to supply I^2*5ohm watts, 3A max
    Output3: Current command offset, 5A/V
    '''
    dc_supply.write('*CLS')
    dc_supply.apply(24, 3, 1)
    dc_supply.set_increment(3, .1)
    

    
setup_scope()
setup_dc_supply()
dc_levels = []
dc_Inductances = []
freq = .2
input_command = .2 #Vpk = 1Apk2pk
func_gen.applyFunction('SIN', freq, input_command, 0) # 1Hz, amplitude, offset
tek.set_hScale(frequency = freq, cycles = 3) 
tek.autoTrigger()
junk = input('adjust DC bias now for around 7.8A')

tek.normalTrigger()
temp = {}
junk = input('Everything look all right? Press any key and enter\n')    
for i in range(9):
    print()
    print('This is run#{0}'.format(i))
    #need to slow func_gen back down!!!!!
    # large distorion around 50 Hz
    #consider .5-50 Hz range and adjustable command
    
    
    junk = input('adjust scaling')
    
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "MEAN")
    tek.normalTrigger()
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    dc_level_str = tek.getImmedMeas()
    dc_levels.append(round(float(dc_level_str),3))
    print('channel 4 measured mean value is {0}Apk_pk'.format(dc_levels[i]))    
    tek.autoTrigger()
    dc_Inductances.append(get_L_at_freq(.2, tek, func_gen)) 
    dc_supply.increment_up(3)
    

func_gen.outputFreq(1.0)
tek.set_hScale(frequency = 1.0, cycles = 3)

title_str = 'Inductance vs DC (.2Hz) current'

easy_plot([dc_Inductances], dc_levels, ['DC Inductance'], 'DC Inductance vs (.2Hz) DC Current')







