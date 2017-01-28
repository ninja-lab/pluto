import pyvisa
import Rigol_DP832

rm = pyvisa.ResourceManager()
print(rm.list_resources())

dc_supply = Rigol_DP832.Rigol_DP832(rm.list_resources()[0], rm)

dc_supply.getName()

try:
    inst = rm.open_resource(rm.list_resources()[1])
    
except pyvisa.errors.VisaIOError:
    print('nice try')