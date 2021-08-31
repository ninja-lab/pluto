from math import pi
from math import tan
import time


def take_current_amplitude_measurement(freq, tek):
    '''
    Current magnitudes measured by clamp on probe, tp16, and manual cursor.
    Voltage magnitudes measured by channel2, and manual cursor. 
    
    '''
    '''
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4)[1])
    current_mag_val = round(float(tek.getImmedMeas()),3)
    print('channel 4 measured value is {0}Apk_pk'.format(current_mag_val))
    '''
    '''
    tek.selectedChannel = 3
    tek.setImmedMeas(3, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4,averaging=4)[1])
    tp16_val = round(float(tek.getImmedMeas()),3)
    print('channel 3 tp16 measured value is {0}Vpk_pk = {1}Apk_pk'.format(tp16_val, tp16_val*5.0))
    '''
    
    '''
    tek.selectedChannel = 2
    tek.setImmedMeas(2, "PK2pk")
    time.sleep(tek.get_timeToCapture(freq, 4,averaging=4)[1])
    coil_voltage_val = round(float(tek.getImmedMeas()),3)
    print('channel 2 coil voltage measured value is {0}Vpk_pk'.format(coil_voltage_val))
    '''
    #take manual measurements with cursors for comparison:
    
    tek.selectedChannel = 4
    tek.set_hbars()
    current_val = float(input('Enter current amplitude in Amps:'))
    if current_val == 0:
        current_val = .00001
    
    '''
    tek.selectedChannel = 2
    tek.set_hbars()
    voltage_val = float(input('Enter coil voltage in Volts'))
    '''
    return current_val
    
    
def take_current_phase_measurement(freq, tek):
    '''
    return phase in radians
    '''
    #set up vertical cursors on channel 4 for current to voltage phase lag:
    tek.selectedChannel = 4
    tek.set_vbars()
    #prompt user for time delay in seconds
    junk =input('Place cursors to get delay FROM voltage TO current')
    current_delay = tek.get_vbars_delta()
    #float(input("Enter time [sec] delay FROM voltage TO current: "))
    
    return 2*pi*current_delay*freq


def get_L_at_freq(freq, tek, func_gen):

    '''
    At a particuluar DC current level, sweep frequencies and measure 
    current amplitude, voltage amplitude, and phase. 
    Compute inductance at each frequency using law of cosines
    V should lead I by some phase, which would be 90 degrees for a perfect
    inductor. 
    theta = V lead phase to current (positive)
    tan(theta) = wL/I
    
    '''
    func_gen.outputFreq(freq)
    print('Programmed Frequency is: ' + str(freq) + 'Hz') 
    junk = input('Adjust scaling now and then hit enter')  
    amplitude = take_current_amplitude_measurement(freq, tek)
    theta = take_current_phase_measurement(freq, tek)
    return tan(theta)*amplitude/(2*pi*freq)

def get_L_vs_freq(freqs, func_gen, scope):
    '''
    return list of inductances measured at each frequency
    '''
    
    return [get_L_at_freq(freq, scope, func_gen) for freq in freqs]
        

    