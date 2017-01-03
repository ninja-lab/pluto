import serial_instruments_modified
import visa
import matplotlib.pyplot as plt

'''
A test script to demonstrate functionality of the python
class for the tektronix TPS2024B oscilloscope.
Setup: Function generator outputs 1 + .5*sin(2*pi*2*t)
on oscilloscope channel 1
'''

rm = visa.ResourceManager()
print(rm.list_resources())
tek = serial_instruments_modified.tek2024(rm.list_resources()[2], rm)
tek.inst.timeout = 20000 #20,000 milliseconds
ch1 = serial_instruments_modified.channel(tek, 1)
tek.setup_measurements() #change this function in library as desired
 
tek.set_hScale(tdiv = .25)
ch1.set_vScale(.2, debug = True)
ch1.set_Position(-3.0)
tek.trigger('DC', 1, 'NORMal')
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
This works for ascii:
tek.issueCommand('DATa:ENCdg ASCII')
stuff = tek.query("CURVe?")
plt.plot([float(el) for el in stuff.split(',')])
plt.show()
'''


#tek.inst.flush(visa.constants.VI_IO_OUT_BUF)
#tek.inst.flush(visa.constants.VI_IO_IN_BUF)
ch1.set_waveformParams(stop = 800, width=1)
out = tek.query("WFMPre?")

'''
dl is digitizer level
value in YUNits =
    ((curve_in_dl - YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
'''

out = out.split(';')
print(out)
encoding = out[2] #ASC or BIN
channelStats = out[6] #WFID: channel num, coupling, V/div, s/div, num points, Sample mode 
parts = channelStats.split(', ')
# x_incr = float(parts[3].replace(' s/div',''))
x_incr = float(out[8])
x_num = int(parts[4].replace(' points',''))
y_mult = float(out[12])
y_zero = float(out[13])
y_offset = float(out[14])
stuff = tek.inst.query_binary_values("CURVe?", 'B') #format character for struct
#module, 'B' is unsigned char, which, matches RP binary format from scope
#width is one so byte order doesn't matter, but it could be specified (page 2-41
#in scope manual)
data_y = [((int(x) - y_offset) * y_mult) + y_zero for x in stuff]
data_x = [x * x_incr for x in range(len(data_y))]
#data_x, data_y = ch1.get_waveform()

print(type(data_x))
print(type(data_y))
plt.plot(data_x, data_y)
plt.show()
tek.query("ALLEV?")

