import serialInstrument
import MDO3014
import pyvisa
import matplotlib.pyplot as plt
import Agilent33120

'''
A test script to demonstrate functionality of the python
class for the tektronix TPS2024B oscilloscope.
Setup: Function generator outputs 1 + .5*sin(2*pi*2*t)
on oscilloscope channel 1
'''

rm = pyvisa.ResourceManager()
print(rm.list_resources())
func_gen = Agilent33120.f33120a(rm)
func_gen.displayText("'Hi Erik'")
func_gen.applyFunction('SIN', 2, .5, 1)
tek = MDO3014.MDO3014(rm)

#tek.inst.timeout = 20000 #20,000 milliseconds
ch1 = MDO3014.channel(tek, 1)
tek.setup_measurements() #change this function in library as desired
 
tek.set_hScale(tdiv = .25)
ch1.set_vScale(.5, debug = True)
ch1.set_Position(-3.0)
tek.trigger('DC', 'CH1', 'NORMal', level = 1.0)
tek.set_averaging(False)
tek.acquisition(True) #like hitting Run on front panel
tek.wait() #wait for the scope to get acquisition
tek.setImmedMeas(1, "PK2pk")
tek.issueCommand("*WAI")
print('Channel 1 amplitude is: ' + tek.getImmedMeas())
tek.setImmedMeas(1, "MEAN")
print('Channel 1 mean is: ' + tek.getImmedMeas() )
tek.setImmedMeas(1, "FREQ")
print('Channel 1 frequency is: ' + tek.getImmedMeas() )

print('The oscilloscope status byte is: ' + tek.status())
print('It should be zero')
'''
#Show ascii transfer format
ch1.set_waveformParams(encoding='ASCII', stop = 800, width=1)
data_x, data_y = ch1.get_waveform()

#tek.inst.flush(visa.constants.VI_IO_OUT_BUF)
#tek.inst.flush(visa.constants.VI_IO_IN_BUF)

print(type(data_x))
print(type(data_y))
plt.plot(data_x, data_y)
plt.show()
'''
#Now show binary transfer format
ch1.set_waveformParams(stop = 800, width=1)#default encoding is RPBinary
data_x, data_y = ch1.get_waveform(debug=True)
#need to experiment with other containers
print(type(data_x))
print(type(data_y))
plt.plot(data_x, data_y)
plt.show()

print('measurement 1 is:')
print(tek.getMeas(1))
print('measurement 2 is:')
print(tek.getMeas(2))

tek.query("ALLEV?")

'''
format character for struct module, 'B' is unsigned char, which, 
matches RP binary format from scope. width is one so byte order 
doesn't matter, but it could be specified (page 2-41 in scope manual) 
'''
    
