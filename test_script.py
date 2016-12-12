import serial_instruments_modified
import visa

rm = visa.ResourceManager()
print(rm.list_resources())
tek = serial_instruments_modified.tek2024(rm.list_resources()[3], rm)
ch1 = serial_instruments_modified.channel(tek, 1)
