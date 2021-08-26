# -*- coding: utf-8 -*-
"""
Created on Fri May 28 09:47:42 2021

@author: eriki
"""

import Visa_Instrument
import time

class sdm3045x(Visa_Instrument.Visa_Instrument):
    
  
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
    def fetch(self):
        return 
    
    def measure_voltage(self):
        return float(self.query('MEASure:VOLTage:DC?'))
    
    def measure_current(self):
        return float(self.query('MEASure:CURRent:DC?'))
        
        