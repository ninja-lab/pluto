import tek2024b
import Agilent33120
import pyvisa
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

rm = pyvisa.ResourceManager()
print(rm.list_resources())
#for comparison:
rogers_currents = [7,8,9,10,11,12,13]
rogers_gains = [1032, 1082, 1042, 912, 740, 590, 484]



dc_supply = Rigol_DP832.Rigol_DP832(rm)



def setup_dc_supply():
    '''
    Output1: +24V. Needs to supply I^2*5ohm watts, 3A max
    Output3: Current command offset, 5A/V
    '''
    dc_supply.write('*CLS')
    dc_supply.apply(24, 3, 1)
    dc_supply.set_increment(3, .03)


setup_dc_supply()
forces = []
dc_gains = []
dc_currents = []

def take_gain_measurement():
    '''
    append to lists
    '''
  
    force = float(input('enter load cell amp reading: '))*4096.0/5.0
    forces.append(round(force,1))
    
    
def take_current_measurement():
    
    current_level = round(float(input('enter current in Amps: ')),3)
    dc_currents.append(current_level)
    return current_level
 
def generate_plot(x_data, y_data):
    save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
    plt.plot(x_data, y_data, 'r-') #color='green', linestyle='dashed')
    plt.plot(rogers_currents, rogers_gains, 'b-')
    plt.legend(['measured', 'simulated'])
    plt.xlabel('DC Current [A]')
    plt.ylabel('DC Gain [lbs/A]')
    plt.title('delta Force / delta Current vs Current (dc sweep method)')
    fig = plt.gcf()
    plt.show()
    time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
    name = 'DCgain' + time_stamp
    filename = (save_loc + name + '.png').replace(' ','_')
    fig.savefig(filename)
 
input('Adjust channel 3 on DC supply for as low a force\n' +
        'as possible without dropping rotor')   

max_current = 10
current_level = 0
while(current_level < max_current):
    
    current_level = take_current_measurement()
    take_gain_measurement()
    dc_supply.increment_up(3)
    time.sleep(10)
 
dc_gains = [(forces[n]-forces[n-1])/(dc_currents[n]-dc_currents[n-1]) for n in range(1, len(forces))]
 
generate_plot(dc_currents[1:], dc_gains)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    