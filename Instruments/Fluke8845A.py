# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 17:19:11 2021

@author: Erik.Iverson
"""

from datetime import datetime
import Visa_Instrument
import numpy as np
import time


class Fluke8845A(Visa_Instrument.Visa_Instrument):
    ''' The class for Fluke benchtop DMM 8845A
    
    The configure command takes a function and can change range, resolution, and 
    diode measurment function current/voltage. 
    
    The sense command sets meter functions and function parameters. 
    
    The *OPC? query doesn't work when the instrument 
    is still undergoing measurements.
    
    
    
    '''
    
    
    
    def __init__(self, resource, debug=False):
 
        super().__init__(resource, debug)
        self.write('SYStem:REMote')
        self.inst.timeout=10000
        self.write('TRIGger:DELay:AUTO OFF')
        #self.inst.set_visa_attribute()
    def measure_resistance(self):
        return self.query('MEASure:SCALar:RESistance?')
    
    def set_date(self):
        self.write('SYSTem:DATE {}'.format(datetime.today().strftime('%m-%d-%Y')))
    
    def get_date(self):
        '''
        
        This function doesn't work. The DMM always issues 
        a -102 syntax error
        WHen experimenting with termination characters, and inserting \r\n 
        myself, pyvisa issues a warning saying the message already ends with those. 
        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        #self.write('SYST:DATE?')
        #return self.read()
        return self.query('SYSTem:DATE ?')
    
    def beep(self):
        self.write('SYSTem:BEEPer')
    def display(self, text):
        self.write('DISPlay:TEXT "{}"'.format(text))
        
    def configure_res(self,nplcs=.2, delay=0, samples=1):
        '''
        The CONFigure command does not initiate a measurement and 
        will need to be followed by READ? command, or INITiate and FETCh? commands. 
        
        nplcs: number of power line cycles [.02, .2, 1, 10, 100]
        
        '''
        self.write('CONFigure:SCALar:RESistance')
        time.sleep(.1)
        self.write('SENSe:RES:NPLCycles {}'.format(nplcs))
        time.sleep(.1)
        self.write('TRIGger:DELay {}'.format(delay))
        time.sleep(.1)
        self.write('SAMPle:COUNt {}'.format(samples))
        return
    def configure_cap(self):
        self.write('CONFigure:SCALar:CAPacitance ')
        
        return 
    
    
    def trig_ext(self):
        return
    
    def get_max(self):
        return self.query('CALCulate:AVERage:MAXimum?')
    def get_min(self):
        return self.query('CALCulate:AVERage:MINimum?')
    def get_average(self):
        return self.query('CALCulate:AVERage:AVERage?')
    
    def measure_cap(self):
        return self.query('MEASure:SCALar:CAPacitance?')
    
    def measure_dcv(self):
        return self.query('MEASure:SCALar:VOLTage:DC?')
        

    def initiate(self):
        
        '''
        After being configured, the INITiate command causes the meter
        to take a measurement(s) when the trigger conditions have been met. 
        Up to 5000 readings are placed in internal memory to be read later
        with using FETCh?
        
        On if trigger source is set to BUS and a *TRG is issued, 
        will the meter respond. Otherwise the meter does not accept 
        any other commands. 
        '''
        self.write('INITiate')
        return
    def read8845(self):
        '''
        Set trigger system to wait-for-trigger
        Trigger source default is IMMediate
        
        This causes the meter to take a measurement the next 
        time the trigger condition is met. 
        
        The measurement is sent to the output buffer, and
        so must be read out. 
        
        Funtion name is suffixed with 8845 
        because the Visa_Instrument already has a function
        called read()
        
        Returns
        -------
        #The measurement
        Nothing, make sure to read back with read() after
        '''
        self.write('READ?')
        #time.sleep(.2) #is this enough? 
        #return self.read() 
        return
    
    def set_trigger(self, trg):
        '''
        trg is a string: 'BUS', 'IMM', 'EXT'
        
        Returns nothing
        '''
        self.write('TRIGger:SOURce {}'.format(trg))
        return

    def samples(self, num):
        '''
        num: sets the number of measurements the meter takes per trigger, 0-50k
        Does this reset other configuration items? 
        '''
        self.write('SAMPle:COUNt {}'.format(num))
        return
    def get_num_points(self):
        '''
        retrieves the number of measurements contained in the meter's
        internal memory

        Returns
        -------
        the number of measurements

        '''
        return self.query('DATA:POINts?')
    
    def trigger_count(self,num):
        '''
        

        Parameters
        ----------
        num : the number of triggers the meter will take 
        before switching to an idle state, 0-50k

        Returns
        -------
        None.

        '''
        self.write('TRIGger:COUNt {}'.format(num))
        return
    
    def fetch(self):
        '''
        Moves measurements stored in the meter's internal
        memory to the output buffer. 
        
        Continual calls to FETCh? return the same data
        because it is still in memory. 
        
        Where to put the data? 
        Use read() after. 

        Returns
        -------
        All the data from the meter's internal memory
        '''
        datastr = self.query('FETCh?')
        #print('data: ')
        #print(datastr)
        #datastr = self.read()
        datalist = datastr.split(',')
        self.data = np.array([float(el) for el in datalist])
        return self.data
    
    def get_samples(self):
        '''
        retrieves the number of samples per trigger

        Returns
        -------
        an int: the number of samples per trigger

        '''
        return int(self.query('SAMP:COUN?'))
    
    
    
    def get_nplcs(self, func):
        '''
        functions:
            CAPacitance
            CURRent
            VOLTage
            RESistance
            FRESistance
            FREQuency
            PERiod
            TEMPerature:RTD
            TEMPerature:FRTD
            DIODe
            CONTinuity
            
        

        Returns
        -------
        a float that is the number of power line cycles

        '''
        return float(self.query('SENSe:{}:NPLC?'.format(func)))
    
    def get_trig_delay(self):
        '''
        

        Returns
        -------
        a float that is the trigger delay

        '''
        return float(self.query('TRIG:DEL?'))
    
    def compute_delay(self):
        '''
        Get the number of samples to make,
        the trigger delay, 
        the number of PLCs for integration time
        
        The delay is before each sample is taken. 
        
        Returns
        -------
        the expected delay in seconds, based on the settings
        sec/samp as a function of nplcs 
        is m*nplcs+b, by characterization
    
        '''
        m = .029 
        b= .08
        trg_delay = self.get_trig_delay()
        num_samples = self.get_samples()
        nplcs = self.get_nplcs('RES')
        return (trg_delay+nplcs*m+b)*num_samples
    
    def read_errors(self):
        '''
        

        Returns
        -------
        A list of the errors

        '''
        no_error = '+0, "No error"'
        errorlist=[]
        while True:
            err = self.query('SYSTem:Error?') 
            if 'No error' in err:
                break
            else:
                errorlist.append(err )
        return errorlist