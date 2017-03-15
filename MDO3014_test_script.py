import serialInstrument
import MDO3014
import pyvisa
import matplotlib.pyplot as plt
import Agilent33120
import time

'''
A test script to demonstrate functionality of the python
class for the tektronix MDO3014 oscilloscope.
Setup: Function generator outputs 1 + .5*sin(2*pi*2*t)
on oscilloscope channel 1
#no external trigger - input sync signal to channel 2 and trigger off that

If relying on wait parameter in get_waveform(wait=True), use stop and then run again,
because the number of acquisitions (stored in scope) doesn't reset unless you change a 
trigger setting or hit stop then run: 
tek.stop()
tek.run()
Otherwise, get_timeToCapture() waits a worst case amount amount of time, 

self.wait() queries BUSY?, and is used when a measurement needs to wait 
on an acquisition to finish
'''

freq = 4.0
rm = pyvisa.ResourceManager()
print(rm.list_resources())
func_gen = Agilent33120.f33120a(rm)
#func_gen.displayText("'Hi Erik'")
func_gen.applyFunction('SIN', freq, 2.0, 0)
tek = MDO3014.MDO3014(rm)
'''
Set up scope channels: 
channel 1 is test signal
channel 2 is used for triggering
'''
ch1 = MDO3014.channel(tek, 1) #input signal
ch2 = MDO3014.channel(tek, 2) #trigger input since there is no external trigger
ch3 = MDO3014.channel(tek, 3) #output signal of an RC filter 
ch2.set_vScale(5.0)
ch2.set_Position(3.0)
tek.setup_measurements() #change this function in library as desired
 
tek.set_hScale(frequency = freq, cycles = 5)
ch1.set_vScale(.5, debug = True)
ch1.set_Position(0)
ch3.set_vScale(1.0, debug = True)
ch3.set_Position(0)
tek.trigger('DC', 'CH2', 'NORMal', level = 2.5)

tek.set_averaging(4)
tek.acquisition(True) #like hitting Run on front panel
'''
print('Test wait(), with STOPfter SEQUENCE enabled')
tek.wait() 
tek.setImmedMeas(1, "PK2pk")
print('Channel 1 amplitude is: ' + tek.getImmedMeas())
#time.sleep(tek.get_timeToCapture(freq, 5, averaging=4)[1])
tek.setImmedMeas(1, "MEAN")
print('Channel 1 mean is: ' + tek.getImmedMeas() )
tek.setImmedMeas(1, "FREQ")
print('Channel 1 frequency is: ' + tek.getImmedMeas() )
print("All those values should be correct")
print()

print('Use and test waitForAcquisitions() before taking measurements')
tek.issueCommand("ACQuire:STOPAfter RUNStop")
freq=1.0
func_gen.applyFunction('SIN', freq, 2.0, 0)
tek.set_hScale(frequency = freq, cycles = 5)
tek.set_averaging(8)
tek.waitForAcquisitions()
tek.setImmedMeas(3, "PK2pk")
print('Channel 3 amplitude is: ' + tek.getImmedMeas())
#time.sleep(tek.get_timeToCapture(freq, 5, averaging=4)[1])
tek.setImmedMeas(3, "MEAN")
print('Channel 3 mean is: ' + tek.getImmedMeas() )
tek.setImmedMeas(3, "FREQ")
print('Channel 3 frequency is: ' + tek.getImmedMeas() )
print("All those values should be correct")
print()
'''
'''
Show ascii transfer format.
Note that the did_clip is set up to be accurate only for RPBinary encoding. 

ch1.set_waveformParams(encoding='ASCII', stop = 2000, width=1)
time.sleep(tek.get_timeToCapture(freq, 5, averaging=4)[1])
data_x, data_y = ch1.get_waveform(debug=True)
#tek.inst.flush(visa.constants.VI_IO_OUT_BUF)
#tek.inst.flush(visa.constants.VI_IO_IN_BUF)
plt.plot(data_x, data_y)
plt.show()
'''


#Now show binary transfer format
ch1.set_waveformParams(stop = 10000, width=1)#default encoding is RPBinary
func_gen.outputAmpl(1.0)
tek.issueCommand("ACQuire:STOPAfter RUNStop")
tek.run()
time.sleep(tek.get_timeToCapture(freq, 5, averaging=4)[1])
data_x, data_y = ch1.get_waveform(debug=False, wait=False)
fig, ax1 = plt.subplots()
ax1.plot(data_x, data_y, 'b-')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Volts [V]')
ax1.set_ylim(-3, 3)
plt.show()

#Test did_clip() using get_timeToCapture()
ch1.set_Position(3.5)
func_gen.outputAmpl(2.0)
time.sleep(tek.get_timeToCapture(freq, 5, averaging=tek.numAvg)[1])
if ch1.did_clip(debug=True, get_new_waveform=True):
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')



#Test did_clip() using wait parameter of get_waveform
ch1.set_Position(-3.5)
data_x, data_y = ch1.get_waveform(debug=False, wait=True)
if ch1.did_clip(debug=True, get_new_waveform=False):
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')
    
#Test vertical rescaling when clipping occurs. 


