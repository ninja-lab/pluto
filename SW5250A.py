import Visa_Instrument
import time


class SW5250A(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):  
        super().__init__(resource, debug)
        self.inst.timeout = 10000
        
        
    def measure_current(self, phase):
        current_string = self.query('MEASure{}:CURRent?'.format(phase))
    
    
    def measure_frequency(self, phase = 1):
        freq_string = self.query('MEASure{}:FREQuency?'.format(phase))
    
    def measure_phase(self, phase = 1):
        ''' Returns output phase angle relative to phase A in degrees. 
        All phase offsets are in terms of phase lead with respect to the
        reference signal and phase A.
        '''
        phase_string = self.query('MEASure{}:PHASe?'.format(phase))
    
    def measure_phase_power(self, phase):
        power_string = self.query('MEASure{}:POWer?'.format(phase))
        
    def measure_total_power(self):
        '''The phase has no effect '''
        power_string = self.query('MEASure1:POWer?:TOTal?')
        
    def measure_phase_va(self, phase):
        power_string = self.query('MEASure{}:VA?'.format(phase))
        
    def measure_total_va(self):
        '''The phase has no effect '''
        power_string = self.query('MEASure1:VA?:TOTal?')
        
    def measure_vab(self):
        voltage_string = self.query('MEASure:VOLTage?:VAB?')
        
    def measure_vbc(self):
        voltage_string = self.query('MEASure:VOLTage?:VBC?')
    def measure_vca(self):
        voltage_string = self.query('MEASure:VOLTage?:VCA?')
    
    
    def clear_measurements(self):
        self.write('MEASure:CLEar')
        return
        
    
        