import visa, serial_instruments_modified
rm = visa.ResourceManager()
rm.list_resources()
tek = serial_instruments_modified.serialInstrument(rm.list_resources()[2], rm)
