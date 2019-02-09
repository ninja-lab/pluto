
# coding: utf-8

# ![alt text](http://localhost:8888/tree/Images/pwr_test_title.PNG "Title")

# ### Introduction   
# Welcome to the script to operate the PWR board test jig. To run, ensure the jig's USB cable is plugged into your computer, and the power strip is powered. This test sytem leverages industry standard communication protocol called [SCPI] [1] to control 3 instruments:
#     1. Keysight data aquisition unit, 34972A
#     2. Instek PSW high-voltage supply
#     3. Instek PSW low-voltage supply
# 
# The instrument control software is implemented with the [VISA] [2] model, using [PyVISA] [3]
# In addition, an interface board (AK part # 385-0036-00) is used to route signals and power paths to the Device-Under-Test (DUT).
# #### Dependencies
#     1.  Python 3 (latest version)
#     2.  PyVisa
#     3.  Pandas
#     4.  Numpy
#     5.  Scipy
#     
# [1]: https://en.wikipedia.org/wiki/Standard\_Commands\_for\_Programmable\_Instruments "SCPI"
# [2]: https://en.wikipedia.org/wiki/Virtual\_instrument\_software_architecture "VISA"
# [3]: https://pyvisa.readthedocs.io/en/master/ "PyVISA"
# [4]: 

# In[9]:


from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import pandas as pd
import numpy as np
from PWRTestIO import *
import Keysight34972A
import InstekPSW
import pyvisa
import instrument_strings
import random
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os, sys
from pwr_board_test_class import pwr_board_test_class, quantity


# In[10]:


#ConfigPath = os.path.join(os.path.expanduser('~'), 'git', 'pluto', 'PWRAutomatedTest', 'PWR_Board_TestReportTemplate.xlsx')
ConfigPath = os.path.join(os.path.expanduser('~'), 'Desktop', 'PWRAutomatedTest', 'PWR_Board_TestReportTemplate.xlsx')
test_df = pd.read_excel(ConfigPath, 'Report')
quantity_df= pd.read_excel(ConfigPath, 'Quantities')


# In[11]:


SerialNumber = input('Enter 385-0036-00 serial number: ')


# In[12]:


#column_names = df1.columns.tolist()
tests = []

for row in test_df.iterrows():
    ser = row[1] #(index, Series) comes from iterrows()
    column_names = ser.index.tolist()
    my_dict = {}
    for column_name in column_names:
        my_dict[column_name] = ser[column_name]
    tests.append(pwr_board_test_class(my_dict))
quantities = {}
for row in quantity_df.iterrows():
    ser = row[1] #(index, Series) comes from iterrows()
    column_names = ser.index.tolist()
    my_dict = {}
    for column_name in column_names:
        my_dict[column_name] = ser[column_name]
    new_quantity = quantity(my_dict)
    quantities[new_quantity.getStringName()] = new_quantity


# In[13]:


rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        if name_str == instrument_strings.Keysight34972A:
            daq = Keysight34972A.Keysight34972A(inst)
            print("Connected to: " + daq.name.rstrip('\n'))
        if name_str == instrument_strings.PSW800:
            hv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + hv_supply.name.rstrip('\n'))
        if name_str == instrument_strings.PSW80V:
            lv_supply = InstekPSW.InstekPSW(inst)
            print("Connected to: " + lv_supply.name.rstrip('\n'))
            
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")


# Here is some initial setup and configuration of the jig.   
#     1.   Turn off the loads     
#     2.   Turn of the flyback and hvbuck converters   
#     3.   Turn off the supplies   
#     4.   Use the Mx+b scaling feature of the Keysight 34972A   

# In[14]:


daq.configure_DCV_channels('(@201:208,210:214)')
daq.format_reading()
for my_quantity in quantities.values():
    daq.setScale(my_quantity.getScale(), my_quantity.getChannel())
    daq.setOffset(my_quantity.getOffset(), my_quantity.getChannel())
daq.useScaling()  
load1_off(daq)
load2_off(daq)
load3_off(daq)
flyback_off(daq)
buck_off(daq)
lv_supply.apply(0,.1)
lv_supply.set_output('OFF')
lv_supply.set_output_mode(0) #no slew rate limit
hv_supply.set_output_mode(0) #no slew rate limit
print('hi')


# ### Test 0
# Measure the rising UVLO threshold on the LTC4417 PSUA channel, with zero load. 

# In[15]:


close_rl5(daq)
time.sleep(0.1)
lv_supply.apply(0,.1)
lv_supply.set_output('ON')
for i in np.arange(20, 24, .01): #sweep voltage range
    lv_supply.apply(i, 1) #(voltage, current)
    time.sleep(.1)
    quantities['24Vout'].measure(daq)
    if quantities['24Vout'].isValid():
        quantities['PSUA'].measure(daq)
        tests[0].setMeasurement(quantities['PSUA'].getMeasurement())
        break
print(tests[0].report())
   


# ### Test 1
# Measure the decreasing UVLO threshold on the LTC4417 PSUA channel, with zero load. 

# In[16]:


#close_rl5(daq)
lv_supply.apply(24,1)
#lv_supply.set_output('ON')
time.sleep(1)
for i in np.arange(21, 19, -.01):
    lv_supply.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure(daq)
    if not quantities['24Vout'].isValid():
        quantities['PSUA'].measure(daq)
        tests[1].setMeasurement(quantities['PSUA'].getMeasurement())
        break
print(tests[1].report())
lv_supply.apply(0,.1)
lv_supply.set_output('OFF')


# ### Test 2
# Measure the increasing OVLO threshold on the LTC4417 PSUA channel, zero load.

# ### Test 3
# Measure the falling OVLO threshold on the LTC4417 PSUA channel, zero load.

# ### Test 4
# Measure the increasing UVLO threshold on the LTC4417 PSUB channel, zero load. 

# In[17]:


lv_supply.apply(0,.1)
lv_supply.set_output('ON')

open_rl5(daq)
time.sleep(0.1)

for i in np.arange(20, 24, .01): #sweep voltage range
    lv_supply.apply(i, 1) #(voltage, current)
    time.sleep(.1)
    quantities['24Vout'].measure(daq)
    if quantities['24Vout'].isValid():
        quantities['PSUB'].measure(daq)
        tests[4].setMeasurement(quantities['PSUA'].getMeasurement())
        break
print(tests[4].report()) 


# ### Test 5
# Measure the decreasing UVLO threshold on the LTC4417 PSUB channel, zero load.

# In[18]:


lv_supply.apply(24,1)
lv_supply.set_output('ON')
time.sleep(1)
for i in np.arange(21, 19, -.01):
    lv_supply.apply(i, 1)
    time.sleep(.1)
    quantities['24Vout'].measure(daq)
    if not quantities['24Vout'].isValid():
        quantities['PSUB'].measure(daq)
        tests[5].setMeasurement(quantities['PSUB'].getMeasurement())
        break
print(tests[5].report())
lv_supply.apply(0,.1)
lv_supply.set_output('OFF')


# ## High Voltage Diode Checks
# 

# In[19]:


DcBusChannel = quantities['TP1B'].getChannel()
daq.monitorQuantity(quantities['TP1B'])
daq.format_time_type(time_type='RELative')
daq.format_reading(time=1)
daq.set_scan('(@{})'.format(DcBusChannel))
daq.set_trigger('TIMer')
daq.set_timer(.2)
daq.set_trigger_count(75)
DC_level = 200
def SetupDiodeTestAndWait(daq, hv_supply, DC_level):
    hv_supply.apply(DC_level,1)
    hv_supply.set_output('ON')
    time.sleep(2)
    hv_supply.set_output('OFF')
    daq.wait_for_trigger() 
    time.sleep(15)


# ### Test 13
# D7H, D8H forward bias test
# D5H, D6H, D9H, D10H reverse bias. 
# Relay config: all open / default state

# In[20]:


open_rl1(daq)
open_rl2(daq)
open_rl3(daq)
open_rl4(daq)

SetupDiodeTestAndWait(daq, hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[13].setMeasurement(tau)
print(tests[13].report())


# ### Test 14
# D6H,D8H forward bias test
# D5H, D7H, D9H, D10H reverse bias.
# Relay config: RL4 closed, RL1-3 open

# In[21]:


open_rl1(daq)
open_rl2(daq)
open_rl3(daq)
close_rl4(daq)
time.sleep(.1)
SetupDiodeTestAndWait(daq,hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[14].setMeasurement(tau)
print(tests[14].report())


# ### Test 15
# D5H,D9H forward bias test
# D6H, D7H, D8H, D10H reverse bias.
# Relay config: RL3 closed, RL1,2,4 open. 

# In[22]:


open_rl1(daq)
open_rl2(daq)
close_rl3(daq)
open_rl4(daq)
time.sleep(.1)
SetupDiodeTestAndWait(daq,hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[15].setMeasurement(tau)
print(tests[15].report())


# ### Test 16
# D5H,D10H forward bias test
# D6H, D7H, D8H, D9H reverse bias.
# Relay config: RL3,4 closed, RL1,2 open. 

# In[23]:


open_rl1(daq)
open_rl2(daq)
close_rl3(daq)
close_rl4(daq)
time.sleep(.1)
SetupDiodeTestAndWait(daq,hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[16].setMeasurement(tau)
print(tests[16].report())


# ### Test 17
# D2H,D3H forward bias test
# All AC diodes reverse bias.
# Relay config: RL1 closed, RL2 open, other do not matter. 

# In[24]:


close_rl1(daq)
open_rl2(daq)
time.sleep(.1)
SetupDiodeTestAndWait(daq,hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[17].setMeasurement(tau)
print(tests[17].report())


# ### Test 18
# D1H,D4H forward bias test
# All AC diodes reverse bias.
# Relay config: RL1 closed, RL2 closed, other do not matter. 

# In[25]:


close_rl1(daq)
close_rl2(daq)
time.sleep(.1)
SetupDiodeTestAndWait(daq,hv_supply, DC_level)
data = daq.fetch_readings()
ydata = data[0::2]
xdata = data[1::2]
tau = get_tau(xdata,ydata, DC_level)
tests[18].setMeasurement(tau)
print(tests[18].report())


# ### Test 19
# U1 R1S-2424/H isolated converter: TP2B is 24V whenever 24Vout is within range. 

# In[26]:


close_rl5(daq)
time.sleep(.1)
daq.monitorQuantity(quantities['TP2B'])
lv_supply.apply(24,1)
lv_supply.set_output('ON')
time.sleep(5)
bootstrap = daq.monitorData()
tests[19].setMeasurement(bootstrap)
print(tests[19].report())
#lv_supply.set_output('OFF')


# ### Test 20
# Test the boostrap circuit consisting of M1B, D12B, D11B, R1B-R4B, D9B    
# Note: It is not possible to measure the bootstrap    
# steady state while holding the buck off. U1 will override the bootstrap.
# 

# In[27]:


lv_supply.set_output('OFF')
buck_on(daq) #doesn't really do anything without 24Vout present
load1_off(daq)
load2_off(daq)
hv_supply.apply(290, 2)
hv_supply.set_output('ON')
daq.monitorQuantity(quantities['TP5B'])
running_values = np.zeros(20, dtype=float)
start = datetime.now()
while True:
    time.sleep(.1)
    latest = daq.monitorData()
    finish = datetime.now()
    seconds = (finish - start).seconds
    quantities['TP5B'].setMeasurement(latest)
    running_values[:-1] = running_values[1:]
    running_values[-1] = latest
    settled = (np.diff(running_values) < .5).all()
    if quantities['TP5B'].isValid() and settled:
        tests[20].setMeasurement(latest)
        time.sleep(2)
        break
    if seconds > 20:
        tests[20].setMeasurement(np.NaN)
        break
hv_supply.set_output('OFF')
print(tests[20].report())
load1_on(daq)
load2_on(daq)
lv_supply.set_output('OFF')
time.sleep(8)
discharge_caps(2, quantities['HVCAP'], quantities['BuckCurrent'], daq)
load1_off(daq)
load2_off(daq)


# ### Test 9 - 11
# Time the HV Cap charging time, charge voltage, and percent regulation.

# In[28]:


lv_supply.set_output('OFF')
load1_off(daq)
load2_off(daq)
close_rl5(daq)
time.sleep(.2)
daq.monitorQuantity(quantities['HVCAP'])
quantities['HVCAP'].clearMeasurement()
lv_supply.apply(24,2)
lv_supply.set_output('ON')
start = datetime.now()
flyback_on(daq)
set_discharge_Vgs(daq, 0)
running_values = np.arange(0,20,1, dtype=float)
while True:
    time.sleep(.5)
    cap_voltage = daq.monitorData()
    running_values[:-1] = running_values[1:]
    running_values[-1] = cap_voltage
    quantities['HVCAP'].setMeasurement(cap_voltage)
    finish = datetime.now()
    seconds = (finish - start).seconds
    settled = (np.diff(running_values) < .5).all()
    if quantities['HVCAP'].isValid() and settled:
        time.sleep(.1)
        tests[9].setMeasurement(seconds)
        print('Caps are charged')
        print("sleeping for 10 seconds")
        time.sleep(10)
        break
    if seconds > 170:
        #make it fail and explicity write to measurement
        tests[9].setMeasurement(np.NaN)
        tests[10].setMeasurement(np.NaN)
        break

for i in range(11):
    cap_voltage = daq.monitorData()
    running_values[:-1] = running_values[1:]
    running_values[-1] = cap_voltage
    time.sleep(.2)
mean_value = np.mean(running_values)
tests[10].setMeasurement(mean_value)
max_value = np.amax(running_values)
min_value = np.amin(running_values)
reg = (max_value - min_value)*100/mean_value
tests[11].setMeasurement(reg)
print(tests[9].report())
print(tests[10].report())
print(tests[11].report())
print('DANGER: CAPS ARE CHARGED')


# ### From this point forward, the SPM sequence is tested. 
# 1. caps are already charged
# 2. turn on the loads
# 3. allow buck to turn on using buck_on(daq)
# 4. turn on hv_supply
# 5. verify SPM is inactive (test 28)
# 6. turn off PSUA
# 6. verify SPM is active (test 27)
# 7. check the buck is on (test 24)
# 8. log the efficiency (test 25)
# 9. FLT_OUT is measured too
# 

# ### Test 24
# Turn the buck control signal to ON and measure Buck output, using U1 to power HVBuck at startup.     
# The buck must charge the large HV caps, which takes several seconds.

# In[29]:


lv_supply.apply(24, 10) #increase the current limit from the charging test
time.sleep(.5)
load1_on(daq)
load2_on(daq) #loads on to exercise the HVBuck
buck_on(daq)
hv_supply.apply(400, .9)
hv_supply.set_output('ON')
hv_supply.display(1) #show voltage and power
spm_level = daq.measure_DCV(quantities['SPM'].getChannel())
flt_out = daq.measure_DCV(quantities['FLT_OUT'].getChannel())
tests[28].setMeasurement(spm_level) 
tests[32].setMeasurement(flt_out)
lv_supply.set_output('OFF') #shutting off PSUA triggers SPM mode
while True:
    quantities['HVCAP'].measure(daq)
    if quantities['HVCAP'].getMeasurement() < 245:
        break
    time.sleep(.1)
spm_level = daq.measure_DCV(quantities['SPM'].getChannel())
flt_out = daq.measure_DCV(quantities['FLT_OUT'].getChannel())
tests[27].setMeasurement(spm_level)
tests[31].setMeasurement(flt_out)
time.sleep(3) #required to let the hv_supply reach steady state
quantities['TP5B'].measure(daq)
vout= quantities['TP5B'].getMeasurement()
quantities['BuckCurrent'].measure(daq)
iout = quantities['BuckCurrent'].getMeasurement()
print('iout: {}'.format(iout))
tests[24].setMeasurement(vout)
vin = hv_supply.get_voltage()
print('vin: {}'.format(vin))
iin = hv_supply.get_current()
print('iin: {}'.format(iin))
pin = vin*iin
tests[25].setMeasurement(100*vout*iout/pin)
print(tests[24].report())
print(tests[25].report())
print(tests[28].report())   
print(tests[27].report())
print(tests[31].report())
print(tests[32].report())


# In[30]:


#hv_supply.set_output('OFF')
lv_supply.set_output('OFF')
hv_supply.set_output('OFF')
load1_on(daq)
load2_on(daq)
time.sleep(4)
discharge_caps(2, quantities['HVCAP'], quantities['BuckCurrent'], daq)


# In[31]:


results = pd.DataFrame(data=[test.toSeries() for test in tests])
time_stamp = datetime.now().strftime('%Y-%m-%d_%H_%M')
filename = 'SerNum{}_Results{}.csv'.format(SerialNumber, time_stamp)
full_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'PWRAutomatedTest', 'Results', filename)
results.to_csv(path_or_buf=full_path)
print('See Results')
time.sleep(3)



