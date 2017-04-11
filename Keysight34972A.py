
import Visa_Instrument
import pyvisa
import sys

class Keysight34972A(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        self.inst.read_termination = '\n'
        #self.write('SENSe:TEMPerature:TRANsducer:TCouple:RJUNction:TYPE INTernal (@101:110)')
        
    def set_temp_units(self, ch_list):
        self.inst.write('UNIT:TEMPerature {0}, (@{1})'.format('C','101:110'))
      
    def measure_DCV(self, channel_num):
        val =  self.inst.query('MEASure:VOLTage:DC? (@{})'.format(channel_num))
        return round(float(val), 6)
        
    def measure_ACV(self, channel_num, range='AUTO'):
        val = self.inst.query('MEASure:VOLTage:DC? {0}, (@{1})'.format(range, channel_num))
        return round(float(val), 6)
        
    def measure_temp(self, channel_num, probe_type='TCouple', thermocouple='K'):
        temp_str = self.inst.query('MEASure:TEMPerature? {0}, {1}, (@{2})'.format(probe_type, thermocouple,channel_num))
        return round(float(temp_str),4)