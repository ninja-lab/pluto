import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
rogers_currents = [7,8,9,10,11,12,13]
rogers_gains = [1032, 1082, 1042, 912, 740, 590, 484]
x = np.arange(3, 10, .5)
y = x*50 
save_loc = 'C:\\Users\\Erik\\Desktop\\PythonPlots\\'
plt.plot(x, y, 'r-') #color='green', linestyle='dashed')
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