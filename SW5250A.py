import Visa_Instrument
import time


class SW5250A(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):  
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
        