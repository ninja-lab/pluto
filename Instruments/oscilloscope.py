
import serialInstrument
import MDO3014
import pyvisa
import matplotlib.pyplot as plt
import Agilent33120
import time

freq = 2.0
amplitude = 2.0
offset = 0.0
rm = pyvisa.ResourceManager()
print(rm.list_resources())

tek = MDO3014.MDO3014(rm)
func_gen = Agilent33120.f33120a(rm)
func_gen.displayText("'Hi Erik'")
func_gen.applyFunction('SIN', freq, amplitude, offset)
tek.unselectChannels([1,2,3,4])
tek.selectChannels([1,2,3])
'''
Set up scope channels: 
channel 1 is test signal
channel 2 is used for triggering
'''
#set up event enable registers
#tek.writeDESER(1)
#tek.writeSRER(48)
#tek.writeESER(1)
#tek.write('*OPC')



ch1 = MDO3014.channel(tek, 1)
ch2 = MDO3014.channel(tek, 2)
ch3 = MDO3014.channel(tek, 3)
ch2.set_vScale(5.0)
ch2.set_Position(3.0)

tek.setup_measurements() #change this function in library as desired
 
tek.set_hScale(frequency = freq, cycles = 3)
ch1.set_vScale(.5, debug = True)
ch1.set_Position(0)
ch3.set_vScale(.5)
ch3.set_Position(0)
tek.trigger('DC', 'CH2', 'NORMal', level = 2.5)
tek.set_averaging(False)
tek.acquisition(True) #like hitting Run on front panel


tek.setImmedMeas(1, "PK2pk")
tek.wait()
# all three measurements are valid off the same trigger, 
#so there is no need to wait for 3 acquisitions..... 
print('Channel 1 amplitude is: {0:.1f}Vpk_pk'.format(float(tek.getImmedMeas())))
tek.setImmedMeas(1, "MEAN")
print('Channel 1 mean is: {0:.1f}V'.format(float(tek.getImmedMeas())))
tek.setImmedMeas(1, "FREQ")
print('Channel 1 frequency is: {0:.1f}Hz'.format(float(tek.getImmedMeas())))
tek.setImmedMeas(1, "PHAse", 3)

for i in range(4):
    tek.run()
    tek.wait()
    print("Phase difference is: {0:.2f} degrees".format(float(tek.getImmedMeas())))
    time.sleep(3)
    
'''
#Test "autorange"
ch1.set_Position(6.0)
ch1.center()
ch1.set_vScale(10.0)
ch1.set_Position(-5)
ch1.center()
ch1.set_vScale(.02)
ch1.set_Position(5)
ch1.center()
'''