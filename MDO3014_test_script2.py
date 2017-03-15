from instrument_strings import *
import pyvisa

rm = pyvisa.ResourceManager()
for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        if inst.query('*IDN?').strip() == MDO3014:
            tek = MDO3014.MDO3014(inst)
            
            
            
            print("Connected to: " + tek.name.rstrip('\n'))
            self.inst.timeout = 50000
            self.inst.values_format.container = np.array
            self.x_incr = False
            self.x_num = False
            self.numAvg = 0 #the averages setting, all channels use this
            self.selectedChannel = 1
            self.debug = False
            break
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not Tektronix MDO3014, continuing...\n")
        
def connect_to_instrument(inst_str):        