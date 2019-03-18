# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 11:24:36 2018

@author: Erik
"""

import Visa_Instrument
import time

class InstekPSW(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.set_averaging(2)
        
        self.write('STATus:OPERation:ENABle 1024')
    
    def apply(self, voltage, current):
        '''
        The APPLy command is used to set both the
        voltage and current. The voltage and current will
        NOT be output as soon as the function is executed if the
        programmed values are within the accepted range.
        An execution error will occur if the programmed
        values are not within accepted ranges.
        '''
        self.write('APPLy {},{}'.format(voltage, current))
    
    def clear_screen(self):
        self.write('DISPlay:TEXT:CLEar')
    def display_screen(self, string):
        '''
        Only ASCII characters 20H
        to 7EH can be used in the <string>.
        '''
        self.write('DISPlay:TEXT "{}"'.format(string))
    def display(self, page):
        '''
        Parameter/
        <NR1> Description
        0 Measurement-Voltage / Measurement-Current
        1 Measurement-Voltage / Measurement-Power
        2 Measurement-Power / Measurement-Current
        3 Set Menu
        4 OVP / OCP Menu
        5~99 Not Used.
        100~199 F-00~99 Menu.
        '''
        self.write('DISPlay:MENU {}'.format(page))
    def get_voltage(self):
        return float(self.query('MEASure:VOLTage?'))
    def get_current(self):
        return float(self.query('MEASure:CURRent?'))
    def get_power(self):
        return float(self.query('MEASure:POWer?'))
    def set_output_mode(self, mode):
        '''
        Parameter:
        0 CV high speed priority
        CVHS CV high speed priority
        1 CC high speed priority
        CCHS CC high speed priority
        2 CV slew rate priority
        CVLS CV slew rate priority
        3 CC slew rate priority
        CCLS CC slew rate priority
        '''
        self.write('OUTPut:MODE {}'.format(mode))
        
    def set_output(self, state):
        '''
        Parameter :
        0 <NR1> Turns the output off.
        OFF Turns the output off.
        1 <NR1> Turns the output on.
        ON Turns the output on.
        '''
        self.write('OUTPut {}'.format(state))
        
    def clear_protection(self):
        self.write('OUTPut:PROTection:CLEar')
    def get_protection_state(self):
        state = int(self.query('OUTPut:PROTection:TRIPped?'))
        return (True if state==1 else False)
    def set_averaging(self,level):
        '''
        0 Low level of smoothing.
        1 Middle level of smoothing.
        2 High level of smoothing.
        '''
        self.write('SENse:AVERage:COUNt {}'.format(level))
        
    def get_current_protection_state(self):
        '''
        Returns current protection status (0 or 1).
        '''
        #state = int(self.query('CURRent:PROTection:STATe?'))
        #return (True if state==1 else False)
    
        #status = self.query('STATus:OPERation:EVENt?')
        status = self.query('STATus:OPERation:CONDition?')
        status = status.strip()
        return int(status) == 1024
    
    def set_bleed_resistor(self,state):
        '''
        0 <NR1> Turns the bleeder off.
        OFF Turns the bleeder off.
        1 <NR1> Turns the bleeder on.
        ON Turns the bleeder on.
        '''
        self.write( 'SYSTem:CONFigure:BLEeder {}'.format(state))
    
    def source_voltage(self, level):
        self.write('VOLTage: {}'.format(level))
    def set_rising_voltage_slew(self, rate):
        self.write('VOLTage:SLEW:RISing {}'.format(rate))
    def set_falling_voltage_slew(self, rate):
        self.write('VOLTage:SLEW:FALLing {}'.format(rate))
    
    
        
    
    
    
        
    