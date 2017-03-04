import serialInstrument
import MDO3014
import pyvisa
import matplotlib.pyplot as plt
import Agilent33120
import time

'''
A test script to demonstrate functionality of the python
class for the tektronix MSO3014 oscilloscope.
Setup: Function generator outputs 1 + .5*sin(2*pi*2*t)
on oscilloscope channel 1
#no external trigger - input sync signal to channel 2 and trigger off that
'''
freq = 5.0
rm = pyvisa.ResourceManager()
print(rm.list_resources())
func_gen = Agilent33120.f33120a(rm)
func_gen.displayText("'Hi Erik'")
func_gen.applyFunction('SIN', freq, 2.0, 0)
tek = MDO3014.MDO3014(rm)
'''
Set up scope channels: 
channel 1 is test signal
channel 2 is used for triggering
'''
ch1 = MDO3014.channel(tek, 1)
ch2 = MDO3014.channel(tek, 2)
ch2.set_vScale(5.0)
ch2.set_Position(3.0)
tek.setup_measurements() #change this function in library as desired
 
tek.set_hScale(frequency = freq, cycles = 5)
ch1.set_vScale(.5, debug = True)
ch1.set_Position(0)
tek.trigger('DC', 'CH2', 'NORMal', level = 2.5)
tek.set_averaging(False)
tek.acquisition(True) #like hitting Run on front panel
tek.setImmedMeas(1, "PK2pk")
print('Channel 1 amplitude is: ' + tek.getImmedMeas())
tek.setImmedMeas(1, "MEAN")
print('Channel 1 mean is: ' + tek.getImmedMeas() )
tek.setImmedMeas(1, "FREQ")
print('Channel 1 frequency is: ' + tek.getImmedMeas() )

print('The oscilloscope status byte is: ' + tek.status())
print('It should be zero')
'''
Show ascii transfer format.
Note that the did_clip is set up to be accurate only for RPBinary encoding. 
'''
ch1.set_waveformParams(encoding='ASCII', stop = 2000, width=1)
time.sleep(tek.get_timeToCapture(freq, 5)[1])
data_x, data_y = ch1.get_waveform()
#tek.inst.flush(visa.constants.VI_IO_OUT_BUF)
#tek.inst.flush(visa.constants.VI_IO_IN_BUF)
plt.plot(data_x, data_y)
plt.show()

#Now show binary transfer format
ch1.set_waveformParams(stop = 10000, width=1)#default encoding is RPBinary
func_gen.outputAmpl(1.0)

time.sleep(tek.get_timeToCapture(freq, 5)[1])
data_x, data_y = ch1.get_waveform(debug=False, wait=False)
#need to experiment with other containers
print(type(data_x))
print(type(data_y))
fig, ax1 = plt.subplots()
ax1.plot(data_x, data_y, 'b-')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Volts [V]')
ax1.set_ylim(-3, 3)
plt.show()

#Test did_clip()
ch1.set_Position(3.5)
func_gen.outputAmpl(1.0)
'''
If relying on wait parameter in get_waveform(wait=True), use stop and then run again,
because the number of acquisitions doesn't reset unless you change a trigger setting
or hit stop then run: 
tek.stop()
tek.run()
Otherwise, get_timeToCapture() is better. 
'''

time.sleep(tek.get_timeToCapture(freq, 5)[1])
data_x, data_y = ch1.get_waveform(debug=False, wait=False)
if ch1.did_clip():
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')

ch1.set_Position(-3.5)
time.sleep(tek.get_timeToCapture(freq, 5)[1])
data_x, data_y = ch1.get_waveform(debug=False, wait=False)
if ch1.did_clip():
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')
    
#Test vertical rescaling when clipping occurs. 

    

