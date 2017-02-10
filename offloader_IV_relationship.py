import tek2024b
import Agilent33120
import pyvisa
import time
import matplotlib.pyplot as plt
from math import log10
from datetime import datetime
import Rigol_DP832
import plotting
'''
Command a sinusoidal current, measure current amplitude and phase,
and coil voltage amplitude and phase. Find IV relationship across frequency.
ch1: command
ch2: load voltage
ch3: load current from TP16, scaled to 5A/V
ch4: load current with clamp on probe
Trigger off of function generator sync signal 

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
    tek.selectChannels([1,3,4])
    tek.setup_measurements()
    ch1.set_Position(-6)
    ch1.set_vScale(.2)
    ch2.set_Position(-4)
    ch2.set_vScale(.5)
    ch3.set_Position(-8)
    ch3.set_vScale(.2)
    ch4.set_Position(-13)
    ch4.set_vScale(.5)
    tek.set_hScale(frequency = 1, cycles = 3)
    #use external SYNC from function generator to scope external trigger input
    tek.trigger('DC', 'EXT', 'NORMal', 2.5)
    tek.set_averaging(4)
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
    #dc_supply.apply(1, .4, 3)
    
setup_scope()
setup_dc_supply()

freqs = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 1000.0]
legends = []

input_command = .1 #Vpk = 1Apk2pk
func_gen.applyFunction('SIN', 1, input_command, 0) # 1Hz, amplitude, offset
tek.autoTrigger()
junk = input('adjust DC bias now for around 400lb')

tek.normalTrigger()

junk = input('Everything look all right? Press any key and enter\n')    
for i in range(2):
    junk = input('adjust DC current command for new value')
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "MEAN")
    time.sleep(tek.get_timeToCapture(freq, 4, averaging=4)[1])
    dc_level = round(float(tek.getImmedMeas()),3)
    #idc_levels.append(dc_level)
    legends.append('{0}Amps'.format(dc_level))
    print('channel 4 measured mean value is {0}Apk_pk'.format(dc_level))    
    
    inductance_curves.append(get_L_vs_freq(freqs)) 
    
    
#dc_supply.turn_off(1)
#dc_supply.turn_off(3)
func_gen.outputFreq(1.0)
tek.set_hScale(frequency = 1.0, cycles = 3)


plotting.generate_inductance_plot(inductance_curves, freqs, legends, 'Offloader Inductance vs Frequency')





