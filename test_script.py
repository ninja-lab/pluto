import serial_instruments_modified
import visa

rm = visa.ResourceManager()
print(rm.list_resources())
tek = serial_instruments_modified.tek2024(rm.list_resources()[3], rm)
ch1 = serial_instruments_modified.channel(tek, 1)
tek.set_averaging(4)

tek.inst.timeout = 20000 #10,000 milliseconds

#tek.inst.flush(visa.constants.VI_IO_OUT_BUF)
#tek.inst.flush(visa.constants.VI_IO_IN_BUF)

data_x, data_y = ch1.get_waveform()
print(type(data_x))
print(type(data_y))
tek.query("ALLEV?")
