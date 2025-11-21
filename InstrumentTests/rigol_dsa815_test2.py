

import pyvisa
from Instruments.rigol_dsa815 import rigol_dsa815
import numpy as np
from math import sqrt
import time
import matplotlib.pyplot as plt
#from Instruments.instrument_strings import *
from Instruments import instrument_strings

rm = pyvisa.ResourceManager()

for resource_id in rm.list_resources():
    try:
        inst = rm.open_resource(resource_id, send_end=True) #the VISA resource
        name_str = inst.query('*IDN?').strip()
        
        if name_str == instrument_strings.RigolDSA815:
            spec_an = rigol_dsa815(inst)
            print("Connected to: " + spec_an.name.rstrip('\n'))
        
    except pyvisa.errors.VisaIOError:
        print(resource_id + " is not what we're looking for, continuing...\n")
# Commanded values
cmd_units      = "DBM"
cmd_f_start_hz = 10e3      # 10 kHz
cmd_f_stop_hz  = 150e3     # 150 kHz
cmd_rbw_hz     = 1e3       # 1 kHz
cmd_vbw_ratio  = 0.1       # VBW = 0.1 * RBW
cmd_det_type   = "POSitive"  # pos-peak

# Write settings
spec_an.set_units(cmd_units)
spec_an.set_start_stop_freq(cmd_f_start_hz, cmd_f_stop_hz)
#spec_an.set_rbw(cmd_rbw_hz, auto=False)
#spec_an.set_vbw_rbw_ratio(cmd_vbw_ratio)
spec_an.set_detector(cmd_det_type)

# Read back
rb_units      = spec_an.get_units()
rb_f_start_hz = spec_an.get_start_freq()
rb_f_stop_hz  = spec_an.get_stop_freq()
rb_rbw_hz     = spec_an.get_rbw()
rb_vbw_hz     = spec_an.get_vbw()           # derived from ratio on the instrument
rb_ratio      = spec_an.get_vbw_rbw_ratio()
rb_det_type   = spec_an.get_detector()

# Print commanded vs read back
print("\n--- Analyzer configuration check ---")
print(f"Units:        commanded = {cmd_units:>8s} | read back = {rb_units}")
print(f"Start freq:   commanded = {cmd_f_start_hz:>10.1f} Hz | read back = {rb_f_start_hz:.1f} Hz")
print(f"Stop freq:    commanded = {cmd_f_stop_hz:>10.1f} Hz | read back = {rb_f_stop_hz:.1f} Hz")
#print(f"RBW:          commanded = {cmd_rbw_hz:>10.1f} Hz | read back = {rb_rbw_hz:.1f} Hz")
#print(f"VBW/RBW ratio commanded = {cmd_vbw_ratio:>10.3f}   | read back = {rb_ratio:.3f}")
print(f"VBW (calc):   (instrument)              | read back = {rb_vbw_hz:.1f} Hz")
print(f"Detector:     commanded = {cmd_det_type:>8s} | read back = {rb_det_type}")
print("-------------------------------------------------\n")