# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 17:29:12 2021

@author: eriki
"""

import Visa_Instrument
import time

class chroma63003(Visa_Instrument.Visa_Instrument):
    
    '''
    Constant voltage Ranges: 
        Low <= 16
        16 <= Med <= 80
        80 <= Hi <= 150
    
    Constant current Ranges: 
        Low <= 2
        2 <= Med <= 4
        4 <= Hi <= 40
    
    Constant resistance ranges: 
        .075 <= Low <= 375
        25 <= Med <= 1875
        90 <= Hi <= 3750
        
    Constant Power 
        Low <= 5
        5 <= Med <= 25
        25 <= Hi <= 250
        
    '''
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
    def turn_on(self):
        self.write(':LOAD:STATe ON')
    
    def turn_off(self):
        self.write('LOAD:STATe OFF')
        
    def short(self, b):
        '''
        
        Parameters
        ----------
        b : boolean, True turns on short circuit, False turns off. 

        Returns
        -------
        None.

        '''
        if b: 
            self.write('LOAD:SHORt:STATe ON')
        else:
            self.write('LOAD:SHORt:STATe OFF')
            
    def set_window(self, t):
        '''
                Parameters
        ----------
        t : window measurement time, 0.02s < t < 2s

        Returns
        -------
        None.

        '''
        self.write(f':CONFigure:WINDow {t}')
        return 
    
    def set_load_current(self, amps):
        '''
        

        Parameters
        ----------
        amps : set the static load current for constant current static mode

        Returns
        -------
        None.

        '''
        self.write(f':CURRent:STATic:L1 {amps}')
        return 
    def set_current_slew(self, slew_rate, direction):
        '''
        

        Parameters
        ----------
        slew_rate : A/us slew rate
        direction: 0: rising, 1:falling

        Returns
        -------
        None.

        '''
        if direction == 0: 
            self.write(f':CURRent:STATic:RISE {slew_rate}')
        elif direction == 1:
            self.write(f':CURRent:STATic:FALL {slew_rate}')
    def set_vmeas_range(self, vrange):
        '''
        

        Parameters
        ----------
        range : the expected voltage range to be measured
            'LOW', 'MIDDLE', 'HIGH'

        Returns
        -------
        None.

        '''
        self.write(f':CURRent:STATic: {vrange}')
    
    def set_resistance(self, resistance):
        '''
        

        Parameters
        ----------
        resistance : set static resistance level for constant resistance mode

        Returns
        -------
        None.

        '''
        self.write(f':RESistance:STATic:L1 {resistance}')
    def set_imeas_range_cr(self, irange):
        '''
        

        Parameters
        ----------
        irange : set the current measurement range in CR mode
            'LOW', 'MIDDLE', 'HIGH'

        Returns
        -------
        

        '''
        self.write(f':RESistance:STATic:IRNG {irange}')
        
    def measure_current(self):
        return float(self.query(':MEASure:CURRent?'))
    def measure_input(self, port):
        '''
        selects the input port of electronic load to measure voltage

        Parameters
        ----------
        port : 'UUT' or 'LOAD'

        Returns
        -------
        None.

        '''
        self.write(f':MEASure:INPut {port}')
        
    def measure_voltage(self):
        return float(self.query(':MEASure:VOLTage?'))
    def measure_power(self):
        return float(self.query(':MEASure:POWer?'))
        
            
       