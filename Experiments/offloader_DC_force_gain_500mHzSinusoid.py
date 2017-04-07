import tek2024b
import Agilent33120
import visa
import time
import matplotlib.pyplot as plt
from datetime import datetime
import Rigol_DP832

'''
Find (delta_Force / delta_I) and plot against DC current level.  
This data can be used to corroborate Roger's static
magnetic simulations, and can also be dropped directly into
LTSpice model of the offloader force loop.
'''

rm = visa.ResourceManager()
print(rm.list_resources())
#for comparison:
rogers_currents = [7,8,9,10,11,12,13]
rogers_gains = [1032, 1082, 1042, 912, 740, 590, 484]


func_gen = Agilent33120.f33120a(rm)
func_gen.displayText("'Hi Erik'")
input_amplitude = .1 #Vpk = 1Apk2pk
input_freq = .5
func_gen.applyFunction('SIN', input_freq, input_amplitude, .1) # .5Hz, amplitude, offset

tek = tek2024b.tek2024b(rm)
ch1 = tek2024b.channel(tek, 1) #input current command
ch3 = tek2024b.channel(tek, 3) #force
ch4 = tek2024b.channel(tek, 4, yunit='A') #current from clamp-on probe
dc_supply = Rigol_DP832.Rigol_DP832(rm)

def setup_scope():
    '''
    ch1: current command
    ch2:
    ch3: force feedback (TP13)
    ch4: clamp on current probe
    '''
    tek.unselectChannels([1,2,3,4])
    tek.selectChannels([1,3,4])
    tek.setup_measurements()
    ch1.set_Position(-4)
    ch1.set_vScale(.5)
    ch3.set_Position(-3.5)
    ch3.set_vScale(.2)
    ch4.set_Position(-9)
    ch4.set_vScale(.5)
    tek.set_hScale(frequency = .5, cycles = 3)
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

setup_scope()
setup_dc_supply()
dc_gains = []
dc_currents = []

def take_gain_measurement():
    '''
    append to lists
    '''
  
    tek.selectedChannel = 3
    tek.setImmedMeas(3, "PK2pk")
    time.sleep(tek.get_timeToCapture(input_freq, 3)[1])
    delta_f = float(tek.getImmedMeas())*4096/5.0
    
    
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "PK2pk")
    time.sleep(tek.get_timeToCapture(input_freq, 3)[1])
    delta_i = float(tek.getImmedMeas())
    dc_gains.append(delta_f/delta_i)
    
def take_current_measurement():
    tek.selectedChannel = 4
    tek.setImmedMeas(4, "MEAN")
    time.sleep(tek.get_timeToCapture(input_freq, 3)[1])
    current_level = float(tek.getImmedMeas())
    dc_currents.append(current_level)
 
def generate_plot(x_data, y_data):
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    plt.plot(x_data, y_data, 'r-') #color='green', linestyle='dashed')
    plt.plot(rogers_currents, rogers_gains, 'b-')
    plt.legend(['measured', 'simulated'])
    plt.xlabel('DC Current [A]')
    plt.ylabel('DC (.5Hz) Gain [lbs/A]')
    plt.title('delta Force / delta Current vs Current')
    fig = plt.gcf()
    plt.show()
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = 'DCgain' + time_stamp
    filename = (save_loc + name + '.png').replace(' ','_')
    fig.savefig(filename)
 
input('Adjust channel 3 on DC supply for as low a force\n' +
        'as possible without dropping rotor')   

while(input('\nKeep going? Enter No to stop\n') != 'No'):
    tek.autoTrigger()
    junk = input('Adjust vertical scaling.\n')
    tek.normalTrigger()
    take_current_measurement()
    take_gain_measurement()
    dc_current_command = dc_supply.get_voltage(3)
    next_level = dc_current_command + .1
    dc_supply.apply(next_level, .4, 3)
 
generate_plot(dc_currents, dc_gains)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    