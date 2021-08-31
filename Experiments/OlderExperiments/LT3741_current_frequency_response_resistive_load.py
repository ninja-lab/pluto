import tek2024b
import Agilent33120
import visa
import time
import matplotlib.pyplot as plt
from math import log10
from datetime import datetime
import Rigol_DP832
'''
Command a sinusoidal current, measure current amplitude and phase, 
ch1: command
ch3: load current from TP16, scaled to 5A/V
ch4: load current with clamp on probe
Trigger off of function generator sync signal 
TO-DO: Repeat at different quiescient current levels with rotor lifted.
    DC supply steps quiescent value
    Record DC set points and plot to compare to static magnetic simulation
    Use offset function to try and keep waveform big and on screen
    Fix saving of image (name gets cut off and file is "empty" with no extension)
    Save image of step response
'''


rm = visa.ResourceManager()
print(rm.list_resources())

func_gen = Agilent33120.f33120a(rm) #doesn't work anymore! 
func_gen.displayText("'Hi Erik'")
tek = tek2024b.tek2024b(rm)
ch1 = tek2024b.channel(tek, 1) #input current command
ch3 = tek2024b.channel(tek, 3) 
ch4 = tek2024b.channel(tek, 4, yunit='A') #current from clamp-on probe
dc_supply = Rigol_DP832.Rigol_DP832(rm)

def setup_scope():
    tek.unselectChannels([1,2,3,4])
    tek.selectChannels([1,3,4])
    tek.setup_measurements()
    ch1.set_Position(-4)
    ch1.set_vScale(.2)
    ch3.set_Position(-3.5)
    ch3.set_vScale(.2)
    ch4.set_Position(-9)
    ch4.set_vScale(.5)
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
    dc_supply.apply(1, .4, 3)
    
setup_scope()
setup_dc_supply()

freqs = [.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0, 10000.0, 20000.0  ]
current_mag = [] #dB
tp16 = []
manual_current_mag = []
current_phase = []
input_amplitude = .1 #Vpk = 1Apk2pk
func_gen.applyFunction('SIN', 1, input_amplitude, 0) # .5Hz, amplitude, offset

    
def take_current_mag_measurement():
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    current_mag.append(20*log10(float(tek.getImmedMeas())/(input_amplitude*5.0*2.0)))
    
    tek.selectedChannel = 3
    tek.setImmedMeas(3, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    tp16.append(20*log10(float(tek.getImmedMeas())/(input_amplitude*2.0)))
    
    #take manual measurement with cursors for comparison:
    
    tek.selectedChannel = 4
    tek.set_hbars()
    current_val = float(input('Enter current amplitude in Amps:'))
    
    if current_val == 0:
        current_val = .00001
        
    manual_current_mag.append(20*log10(current_val/(input_amplitude*5.0*2.0)))

def take_current_phase_measurement(freq):
    #set up vertical cursors on channel 4 for current to command phase lag:
    tek.selectedChannel = 4
    tek.set_vbars()
    #prompt user for time delay in seconds
    current_delay = input("Enter time [sec] delay between current command waveform and measured current: ")
    if current_delay == 0:
        current_delay = 1.0/freq
    current_phase.append(-360*float(current_delay)*freq)

def generate_bode_plot(mag1, mag2, mag3, phase, freqs, quantity):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    '''
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mag1) - 20, max(mag1) + 20)
    ax1.semilogx(freqs, mag1, 'gs')
    ax1.semilogx(freqs, mag2, 'bs')
    ax1.semilogx(freqs, mag3, 'rs')
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Magnitude [dB]', color = 'b')
    ax1.legend(['scope measurement of load current', 'cursor measurement of load current','tp16*5.0A/V'])
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 90)
    ax2.semilogx(freqs, phase, 'r--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    ax2.legend(['phase'], loc=4)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = quantity + ' FreqResp ' + time_stamp
    #print(name)
    plt.title(name)
    fig = plt.gcf()
    plt.show()
    filename = (save_loc + name + '.png').replace(' ','_')
    #print(filename)
    fig.savefig(filename)

junk = input('Everything look all right? Press any key and enter\n')    

for freq in freqs:
    func_gen.outputFreq(freq)
    print()
    print('Programmed Frequency is: ' + str(freq) + 'Hz')
    tek.set_hScale(frequency = freq, cycles = 3)
    #junk = input('Adjust vertical scaling now and then hit enter')
     
    take_current_mag_measurement()
    take_current_phase_measurement(freq)
    
    #sanity check on frequency 
    tek.setImmedMeas(1, "FREQ")
    time.sleep(.5)
    print('Frequency measured is: {0:.3f}Hz'.format(float(tek.getImmedMeas())))
    time.sleep(.5)

dc_supply.turn_off(1)
dc_supply.turn_off(3)
generate_bode_plot(current_mag, manual_current_mag, tp16, current_phase, freqs, 'Current')





