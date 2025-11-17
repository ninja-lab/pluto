import instrument_strings
import pyvisa
import MSO3054
import Agilent33120
import time
import matplotlib.pyplot as plt
import numpy as np

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.MSO3054:
            tek = MSO3054.MSO3054(inst)
            print("Connected to: " + tek.name.rstrip('\n'))
        elif name_str == instrument_strings.FG33120A:
            func_gen = Agilent33120.f33120a(inst)
            print("Connected to: " + func_gen.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")


ch1 = MSO3054.channel(tek, 1, yunit='V', atten=1) #input signal
ch3 = MSO3054.channel(tek, 3, yunit='V', atten=1) #output signal of an RC filter 

tek.unselectChannels([1,2,3,4])
tek.selectChannels([1,3])

#Set up channels and scope
freq = 40.0
ampl = 2.0
offset = 0
func_gen.applyFunction('SIN', freq, ampl, offset)
tek.setup_measurements() #change this function in library as desired
tek.set_hScale(frequency = freq, cycles = 5)
ch1.set_vScale(.5, debug = True)
ch1.set_Position(0)
ch3.set_vScale(1.0, debug = True)
ch3.set_Position(0)
tek.trigger(tek.trigger_dict)
tek.set_averaging(8)
tek.acquisition(True) #like hitting Run on front panel

print('Test wait(), with STOPfter SEQUENCE enabled')
tek.wait() 
#multiple measurements are made on the same acquisition
tek.setImmedMeas(1, "PK2pk")
print('Channel 1 amplitude: Measured = {:.2f}V, Programmed = {:.2f}V'.format(tek.getImmedMeas(), ampl))#time.sleep(tek.get_timeToCapture(freq, 5, averaging=4)[1])
tek.setImmedMeas(1, "MEAN")
print('Channel 1 mean: Measured = {:.2f}V, Programmed = {:.2f}V '.format(tek.getImmedMeas(), offset))
tek.setImmedMeas(1, "FREQ")
print('Channel 1 frequency: Measured = {:.2f}Hz, Programmed = {:.2f}Hz'.format(tek.getImmedMeas(), freq))
print("All those values should be correct")
print()

tek.set_averaging(4)
print('Use and test waitForAcquisitions() in continuous acquisition mode')
tek.issueCommand("ACQuire:STOPAfter RUNStop")
freq=10.0
ampl=2.0
offset=0
func_gen.applyFunction('SIN', freq, ampl, offset)
tek.set_hScale(frequency = freq, cycles = 5)
tek.set_averaging(4)
tek.stop()
tek.run()
tek.waitForAcquisitions()
tek.setImmedMeas(3, "PK2pk")
print('Channel 3 amplitude: Measured = {:.2f}V, Programmed = {:.2f}V'.format(tek.getImmedMeas(), ampl))
tek.setImmedMeas(3, "MEAN")
print('Channel 3 mean: Measured = {:.2f}V, Programmed = {:.2f}V '.format(tek.getImmedMeas(), offset))
tek.setImmedMeas(3, "FREQ")
print('Channel 3 frequency: Measured = {:.2f}Hz, Programmed = {:.2f}Hz'.format(tek.getImmedMeas(), freq))
print("All those values should be correct")
print()


#Show binary transfer format
ch1.set_waveformParams()#default encoding is RPBinary
ampl = 1.0
func_gen.outputAmpl(ampl)
tek.stop()
tek.run()
time.sleep(tek.get_timeToCapture(freq, 5)[1])
data_x, data_y = ch1.get_waveform(debug=False, wait=False)
fig, ax1 = plt.subplots()
ax1.plot(data_x, data_y, 'b-')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Volts [V]')
ax1.set_ylim(-3, 3)
plt.show()


print('Test did_clip() using get_timeToCapture()')
ampl = 2.0
ch1.set_Position(3.5)
func_gen.outputAmpl(ampl)
time.sleep(tek.get_timeToCapture(freq, 6)[1])
if ch1.did_clip(debug=True, get_new_waveform=True): #no waiting provisions in did_clip()
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')

print('Test did_clip() using wait parameter of get_waveform')

ch1.set_Position(-3.5)
tek.stop()
tek.run()
data_x, data_y = ch1.get_waveform(debug=False, wait=True)
if ch1.did_clip(debug=True, get_new_waveform=False):
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')


print("Testing center() ('autorange')")
ch1.set_Position(3.0)
ch1.center()
ch1.set_Position(-4.0)
ch1.center()









