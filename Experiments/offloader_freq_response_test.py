import tek2024b
import Agilent33120
import visa
import time
import matplotlib.pyplot as plt
from math import log10
from datetime import datetime
'''
Command a sinusoidal current, measure current amplitude and phase, 
and force amplitude and phase
ch1: command
ch2: force from load cell amplifier
ch4: coil current
Trigger off of function generator sync signal 
TO-DO: Repeat at different quiescient current levels with rotor lifted.
    Integrate DC supply that steps quiescent value
    Record DC set points and plot to compare to static magnetic simulation
    Use offset function to try and keep waveform big and on screen
    Fix saving of image (name gets cut off and file is "empty" with no extension)
'''


rm = visa.ResourceManager()
print(rm.list_resources())

func_gen = Agilent33120.f33120a(rm.list_resources()[3], rm)
func_gen.displayText("'Hi Erik'")
tek = tek2024b.tek2024(rm.list_resources()[2], rm)
ch1 = tek2024b.channel(tek, 1) #input current command
ch2 = tek2024b.channel(tek, 2) #force from load cell amp
ch4 = tek2024b.channel(tek, 4, yunit='A') #current from clamp-on probe
tek.setup_measurements()
ch1.set_Position(-2)
ch1.set_vScale(.5)
#use external SYNC from function generator to scope external trigger input
tek.trigger('DC', 'EXT', 'NORMal', 2.5)
tek.set_averaging(False)
tek.setImmedMeas(1, "FREQ")
tek.setup_measurements()
freqs = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
current_mag = [] #dB
manual_current_mag = []
current_phase = []
force_mag = []
manual_force_mag = []
force_phase = []
input_amplitude = .1 #pk2pk
func_gen.applyFunction('SIN', .5, input_amplitude, 0)
tek.acquisition(True)
DC_command = input('Enter DC command value: ')
DC_current = input('Enter DC current value: ')

def take_current_mag_measurement():
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    current_mag.append(20*log10(float(tek.getImmedMeas())/input_amplitude))
    #take manual measurement with cursors for comparison:
    tek.set_hbars()
    current_val = float(input('Enter current amplitude in Amps:'))
    if current_val == 0:
        current_val = .00001
        
    manual_current_mag.append(20*log10(current_val/input_amplitude))

def take_force_mag_measurement():
    tek.selectedChannel = 2
    tek.setImmedMeas(2, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    force_mag.append(20*log10(float(tek.getImmedMeas())*(4096.0/5.0)/input_amplitude))
    tek.set_hbars()
    force_val = float(input('Enter force amplitude in Volts:'))
    if force_val == 0:
        force_val = .00001
    manual_force_mag.append(20*log10(force_val/input_amplitude))

def take_current_phase_measurement(freq):
    #set up vertical cursors on channel 4 for current to command phase lag:
    tek.selectedChannel = 4
    tek.set_vbars()
    #prompt user for time delay in seconds
    current_delay = input("Enter time [sec] delay between current command waveform and measured current: ")
    if current_delay == 0:
        current_delay = 1.0/freq
    current_phase.append(-360*float(current_delay)*freq)

def take_force_phase_measurement(freq):
    #set up vertical cursors on channel 2 for force to current command phase lag:
    tek.selectedChannel = 2
    tek.set_vbars()
    #prompt user for time delay in seconds
    force_delay = input("Enter time [sec] delay between current command waveform and measured force: ")
    if force_delay == 0:
        force_delay = 1.0/freq
    force_phase.append(-360*float(force_delay)*freq)

def generate_bode_plot(mag1, mag2, phase, freqs, quantity):
    '''
    Generates a plot with left vertical axis as magnitude, right vertical as phase,
    along log frequency horizontal axis. 
    '''
    fig, ax1 = plt.subplots()
    ax1.set_ylim(min(mag1) - 20, max(mag1) + 20)
    ax1.semilogx(freqs, mag1, 'gs', freqs, mag2, 'bs')
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Magnitude [dB]', color = 'b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax2 = ax1.twinx()
    ax2.set_ylim(-360, 360)
    ax2.semilogx(freqs, phase, 'r--')
    ax2.set_ylabel('Phase [deg]', color = 'r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H:%M')
    name = quantity + ' Frequency Response ' + time_stamp
    plt.title(name)
    plt.savefig((name + '.png').replace(' ','_'))
    plt.show()

for freq in freqs:
    func_gen.outputFreq(freq)
    print()
    print('Programmed Frequency is: ' + str(freq) + 'Hz')
    tek.set_hScale(frequency = freq, cycles = 3)
    junk = input('Adjust vertical scaling now and then hit enter')

    take_current_mag_measurement()
    take_force_mag_measurement()
    take_current_phase_measurement(freq)
    take_force_phase_measurement(freq)
    
    #sanity check on frequency 
    tek.setImmedMeas(1, "FREQ")
    time.sleep(.5)
    print('Frequency measured is: ' + tek.getImmedMeas())
    time.sleep(.5)

generate_bode_plot(current_mag, manual_current_mag, current_phase, freqs, 'Current')
generate_bode_plot(force_mag, manual_force_mag, force_phase, freqs, 'Force')





