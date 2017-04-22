
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
    
    def configure_DCV_channels(self, scan_list):
        self.inst.write('CONFigure:VOLTage:DC {}'.format(scan_list))
    
    def configure_ACV_channels(self, scan_list):
        self.inst.write('CONFigure:VOLTage:AC {}'.format(scan_list))
        
    def configure_temp_channels(self, scan_list, probe_type='TCouple', thermocouple='K' ):
        self.inst.write('CONFigure:TEMPerature {0}, {1}, {2}'.format(probe_type, thermocouple, scan_list))
    
    def set_scan(self, scan_list):
        self.inst.write(self.inst.write('ROUTe:SCAN {}'.format(scan_list)))
    
    def set_delay(self, seconds, scan_list):
        ''' Only valid while scanning. CONFigure and MEASure? set the channel delay to automatic
        '''
        self.inst.write('ROUTe:CHANnel:DELay {0}, {1}'.format(seconds, scan_list))
        
    def set_trigger(self, source):
        '''
        BUS | IMMediate | EXTernal | TIMer | ALARm[n]
        For IMMediate, trigger is always present, and when instrument goes in to 'wait for trigger' state, the 
        trigger is issued immediately. 
        '''
        self.inst.write('TRIger:SOUrce {}'.format(source))
        
    def get_NPLC(self, scan_list):
        val = self.inst.query('SENSe:VOLTage:DC:NPLC? ({})'.format(scan_list))
        return float(val)
        
    def wait_for_trigger(self):
        self.inst.write('INITiate')
        
    def fetch_readings(self):
        ''' Returns a list of floats corresponding to data from the channels in the scan list'''
        data = self.inst.query('FETCh?')
        return [float(el) for el in data.split(',')]
        
    def read(self):
        ''' Same as an INITiate command immediately followed with a FETCh
         Returns a list of floats corresponding to data from the channels in the scan list 
        '''
        data = self.inst.query('READ?')
        return [float(el) for el in data.split(',')]
        
    def format_reading(self, time=0, channel=0, alarm=0):
        self.inst.write('FORMat:READing:ALARm {}'.format(alarm))
        self.inst.write('FORMat:READing:CHANnel {}'.format(channel))
        self.inst.write('FORMat:READing:TIME {}'.format(time))
        return 
        
        