import serial_instruments_modified
import visa

rm = visa.ResourceManager()
print(rm.list_resources())
tek = serial_instruments_modified.tek2024(rm.list_resources()[2], rm)
ch1 = serial_instruments_modified.channel(tek, 1)
#tek.set_averaging(4)

tek.inst.timeout = 2500
