# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 12:35:06 2022

@author: eriki
"""

import Visa_Instrument
import time

class KeysightRP7935A(Visa_Instrument.Visa_Instrument):
    
    '''
 
        
    '''
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        self.set_slew_rate('MAX')
        self.set_priority('VOLT')
        
    def turn_on(self):
        self.write('OUTPut:STATe ON')
    
    def turn_off(self):
        self.write('OUTPut:STATe OFF')
        
    def measure_voltage(self):
        return self.query('MEASure:SCALar:VOLTage:DC?')
    def measure_current(self):
        return self.query('MEASure:SCALar:CURRent:DC?')
    def set_voltage(self, voltage):
        self.write(f'SOURCe:VOLTage:LEVel:IMMediate:AMPLitude {voltage}')
    def set_current(self, current):
        self.write(f'SOURce:CURRent:LIMit:POSitive:IMMediate:AMPLitude {current}')
    def set_slew_rate(self, rate):
        self.write(f'SOURce:VOLTage:SLEW:IMMediate {rate}')
    def set_priority(self, mode):
        self.write(f'SOURce:FUNCtion {mode}')
    
    