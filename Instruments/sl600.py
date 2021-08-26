# -*- coding: utf-8 -*-
"""
Created on Thu May 27 17:24:25 2021

@author: eriki
"""

import Visa_Instrument
import time

class sl600(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
    def source(self, voltage, maxcurrent):
        self.write(f'SOURce:VOLTage:IMMediate:AMPlitude {voltage}')
        self.write(f'SOURce:CURRent:IMMediate:AMPlitude {maxcurrent}')

    def measure_voltage(self):
        return float(self.query('MEAS:VOLT?'))

    def measure_current(self):
        return float(self.query('MEAS:CURR?'))
    
    def turn_on(self):
        self.write('OUTPut:START')
        
    def turn_off(self):
        self.write('OUTPut:STOP')
        