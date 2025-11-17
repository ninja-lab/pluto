import instrument_strings
import pyvisa
import MDO3014
import Agilent33120
import time
import matplotlib.pyplot as plt
import numpy as np

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.MDO3014:
            tek = MDO3014.MDO3014(inst)
            print("Connected to: " + tek.name.rstrip('\n'))
        elif name_str == instrument_strings.FG33120A:
            func_gen = Agilent33120.f33120a(inst)
            print("Connected to: " + func_gen.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not Tektronix MDO3014, continuing...\n")


ch1 = MDO3014.channel(tek, 1, yunit='V', atten=1) #input signal
ch2 = MDO3014.channel(tek, 2, yunit='V', atten=1) #trigger input since there is no external trigger
ch3 = MDO3014.channel(tek, 3, yunit='V', atten=1) #output signal of an RC filter 

tek.unselectChannels([1,2,3,4])
tek.selectChannels([1,2,3])

#Set up channels and scope
freq = 40.0
func_gen.applyFunction('SIN', freq, 2.0, 0)
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
freq=10.0
func_gen.applyFunction('SIN', freq, 2.0, 0)
tek.set_hScale(frequency = freq, cycles = 5)
tek.set_averaging(0)
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


#Now show binary transfer format
ch1.set_waveformParams()#default encoding is RPBinary
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


print('Test did_clip() using get_timeToCapture()')
ch1.set_Position(3.5)
func_gen.outputAmpl(2.0)
time.sleep(tek.get_timeToCapture(freq, 6)[1])
if ch1.did_clip(debug=True, get_new_waveform=True):
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')

print('Test did_clip() using wait parameter of get_waveform')
ch1.set_Position(-3.5)
data_x, data_y = ch1.get_waveform(debug=False, wait=True)
if ch1.did_clip(debug=True, get_new_waveform=False):
    print('Channel 1 should have clipped and it was caught')
else:
    print('Channel 1 should have clipped but it wasn\'t caught')


print("Testing center() ('autorange')")
ch1.set_Position(3.5)











