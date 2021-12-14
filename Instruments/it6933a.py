# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 10:31:05 2021

@author: eriki
"""

import Visa_Instrument
import time

class it6933a(Visa_Instrument.Visa_Instrument):
    
    #output is turned off automatically if current exceeds the OCP level
    ocp_levels = [.1, .1, .1]
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        
        
    def display_text(self, text):
        self.write(f'DISPlay:TEXT \'{text}\'')
        
    def clear_text(self):
        self.write('DISPlay:TEXT:CLEar')
        
    def turn_on(self):
        self.write('OUTPut ON')
        
    def turn_off(self):
        self.write('OUTPut OFF')
        
    def set_voltage(self, voltage):
        self.write(f'VOLTage {voltage}')
    
    def get_voltage(self):
        return float(self.query('VOLTage?'))
    
    def apply(self, voltage, current):
        self.write(f'APPLy {voltage}, {current}')
    
    def measure_current(self):
        return float(self.query('MEASure:CURRent?'))
    def measure_voltage(self):
        return float(self.query('MEASure:VOLTage?'))
    def measure_power(self):
        return float(self.query('MEASure:POWer?'))
    
    def measure_dvm(self):
        return float(self.query('MEASure:DVM?'))
    