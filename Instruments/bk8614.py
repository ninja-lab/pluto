# -*- coding: utf-8 -*-
"""
Created on Thu May 20 14:14:08 2021

@author: eriki
"""

import Visa_Instrument
import time

class bk8614(Visa_Instrument.Visa_Instrument):
    
  
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
    def turn_on(self):
        self.write(':SOURce:INPut:STATe ON')
    
    def turn_off(self):
        self.write(':SOURce:INPut:STATe OFF')
        
    def set_voltage(self, voltage):
        '''
        

        Parameters
        ----------
        voltage : the voltage that that electronic load will regulate when operating
        in CV mode

        Returns
        -------
        None.

        '''
        self.write('SOURce:FUNCtion VOLTage')
        self.write(f':SOURce:VOLTage:LEVel:IMMediate {voltage} ')
        
    def set_resistance(self, resistance):
        '''
        

        Parameters
        ----------
        resistance :  sets the resistance of the electronic load when operating in constant resistance mode.

        Returns
        -------
        None.

        '''
        self.write(f':SOURce:RESistance:LEVel:IMMediate {resistance}' )
        self.write('SOURce:FUNCtion RESistance')
        
    def set_current(self, current):
        '''
        

        Parameters
        ----------
        current : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        self.write('SOURce:FUNCtion CURRent')
        self.write(f':SOURce:CURRent:LEVel:IMMediate {current}' )
        
    def soft_power_protection_level(self, power):
        '''
        

        Parameters
        ----------
        power [W] : soft power protection level. If the input power exceeds the 
        soft power protection level for the time specified by POW:PROT:DEL, 
        the input is turned off.

        Returns
        -------
        None.

        '''
        self.write(f':SOURce:POWer:PROTection:LEvel {power}')
    
    def power_protection_delay(self, seconds):
        '''
        

        Parameters
        ----------
        delay : the time that the input power can exceed the protection level 
        before the input is turned off.

        Returns
        -------
        None.

        '''
        self.write(f':SOURce:POWer:PROTection:DELay {seconds}')
        
    def measure_voltage(self):
        '''
        

        Returns
        -------
        the voltage read by the load

        '''
        return float(self.query(':MEASure:VOLTage:DC?'))
    def measure_current(self):
        '''
        

        Returns
        -------
        the current read by the load

        '''
        return float(self.query(':MEASure:CURRent:DC?'))
    
    def num_samples(self, samples):
        '''
        

        Parameters
        ----------
        samples : specify the filter count, between 2 and 16
        Returns
        -------
        None.

        '''
        self.write(f':SENSe:AVERage:COUNt {samples}')
    
    def set_sense(self, val):
        '''
        Parameters
        ----------
        val : 0|1|ON|OFF

        Returns
        -------
        None.

        '''
        self.write(f':SOURCe:SENSE {val}')