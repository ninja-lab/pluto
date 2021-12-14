# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 10:30:40 2021

@author: eriki
"""
import Visa_Instrument
import time

class dl3031a(Visa_Instrument.Visa_Instrument):
    
  
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        #self.inst.timeout = 10000
        
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
    
    def measure_power(self):
        return float(self.query('MEASure:POWer:DC?'))
    
    def get_wave_data(self):
        return self.query('MEASure:WAVedata?')
    
    def set_trigger(self, source):
        '''
        Parameters
        ----------
        source : BUS or EXTernal or MANual

        Returns
        -------
        None.

        '''
        self.write(f':TRIGger:SOURce {source}')
        
    def trigger(self):
        '''
        When SCPI command trigger (Bus) is selected to be the trigger source, 
        running the command will immediately initiate a trigger.

        Returns
        -------
        None.

        '''
        self.write(':TRIGger')
        return 
    
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
      