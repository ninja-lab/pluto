# -*- coding: utf-8 -*-
"""
Created on Thu May 20 16:49:32 2021

@author: eriki
"""

import Visa_Instrument
import time

class bk4054b(Visa_Instrument.Visa_Instrument):
    
  
    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
    def channel1_on(self):
        self.write('C1:OUTPut ON')
    
    def channel2_on(self):
        self.write('C2:OUTPut ON')
    def channel1_off(self):
        self.write('C1:OUTPut OFF')
    
    def channel2_off(self):
        self.write('C2:OUTPut OFF')
        
    def set_freq(self, channel, freq):
        self.write(f'C{channel}:BaSic_WaVe FRQ,{freq}')
        
    def set_ampl(self, channel, amp):
        self.write(f'C{channel}:BaSic_WaVe AMP,{amp}')
    
    def set_wtyp(self, channel, shape):
        '''
        

        Parameters
        ----------
        channel :
        shape :  [SINE, SQUARE, RAMP, PULSE, NOISE, ARB, DC]

        Returns
        -------
        None.

        '''
        self.write(f'C{channel}:BaSic_WaVe WVTP,{shape}')
    
    def set_duty(self, channel, duty):
        self.write(f'C{channel}:BaSic_WaVe DUTY,{duty}')
    
    def set_offset(self, channel, offset):
        self.write(f'C{channel}:BaSic_WaVe OFST,{offset}')
    def set_period(self, channel, period):
        self.write(f'C{channel}:BaSic_WaVe PERI,{period}')
    def set_phase(self, channel, phase):
        '''
        

        Parameters
        ----------
        channel : TYPE
            DESCRIPTION.
        phase : 0 to 360

        Returns
        -------
        None.

        '''
        self.write(f'C{channel}:BaSic_WaVe PHSE,{phase}')
        
    def num_format(self):
        self.write('NumBer_ForMat PNT,COMMA')
        self.write('NumBer_ForMat SEPT,ON')
    def phase_coupling(self, phase):
        '''
        I think the programming manual 'trace' means the same thing
        as 'track' on the screen of funcgen.
        When 'track' is off, the options for coupling show up. 
        If user isn't using freq or ampl coupling, I think this is 
        the same as phase coupling. 

        Parameters
        ----------
        base : the channel being copied
        phase : degrees

        Returns
        -------
        None.

        '''
        #self.write('COUPling TRACE,ON')
        self.write('COUPLING STATE,ON')
        time.sleep(.2)
        #self.write(f'COUPling {base} ')
        self.write(f'COUPling PDEV,{phase}')