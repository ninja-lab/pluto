import Visa_Instrument
import time
import pyvisa

query_wait_secs = 1
query_wait_secs_long = 2
query_nattempts = 10

class SW5250A(Visa_Instrument.Visa_Instrument):
    def __init__(self, resource, debug=False):  
        super().__init__(resource, debug)
        self.inst.timeout = 1000
        
        
    def measure_current(self, phase):
        query_string = 'measure{}:current?'.format(phase)
        return self.retry_read(query_string, query_wait_secs, query_nattempts)
        # self.write('measure{}:current?'.format(phase))
        # time.sleep(1)
        # current_string = self.read_until_flush()
        # return current_string

    def measure_frequency(self, phase):
        # print(query_string)
        # self.write('measure{}:frequency?'.format(phase))
        # time.sleep(1)
        query_string = 'measure{}:freq?'.format(phase)
        return self.retry_read(query_string, query_wait_secs, query_nattempts)


    def measure_phase(self, phase = 1):
        ''' Returns output phase angle relative to phase A in degrees. 
        All phase offsets are in terms of phase lead with respect to the
        reference signal and phase A.
        '''
        # phase_string = self.query('MEASure{}:PHASe?'.format(phase))
        query_string = 'MEASure{}:PHASe?'.format(phase)
        return self.retry_read(query_string, query_wait_secs, query_nattempts)


    def measure_phase_power(self, phase):
        # power_string = self.query('MEASure{}:POWer?'.format(phase))
        query_string = 'MEAS{}:POW?'.format(phase)
        return self.retry_read(query_string, query_wait_secs, query_nattempts)
        
    def measure_total_power(self):
        '''The phase has no effect '''
        # power_string = self.query('MEASure1:POWer?:TOTal?')
        query_string = 'MEASure1:POWer:TOTal?'
        return self.retry_read(query_string, query_wait_secs_long, query_nattempts)
        
    def measure_phase_va(self, phase):
        # power_string = self.query('MEASure{}:VA?'.format(phase))
        query_string = 'MEASure{}:VA?'.format(phase)
        return self.retry_read(query_string, query_wait_secs, query_nattempts)
        
    def measure_total_va(self):
        '''The phase has no effect '''
        # power_string = self.query('MEASure1:VA?:TOTal?')
        query_string = 'MEASure1:VA:TOTal?'
        return self.retry_read(query_string, query_wait_secs_long, query_nattempts)
        
    def measure_vab(self):
        # voltage_string = self.query('MEASure1:VOLTage?:VAB?')
        query_string = 'MEASure1:VOLTage:VAB?'
        return self.retry_read(query_string, query_wait_secs_long, query_nattempts)

    def measure_vbc(self):
        # voltage_string = self.query('MEASure1:VOLTage?:VBC?')
        query_string = 'MEASure1:VOLTage:VBC?'
        return self.retry_read(query_string, query_wait_secs_long, query_nattempts)

    def measure_vca(self):
        # voltage_string = self.query('MEASure1:VOLTage?:VCA?')
        query_string = 'MEASure1:VOLTage:VCA?'
        return self.retry_read(query_string, query_wait_secs_long, query_nattempts)

    ###################################################################
    #  Read function
    def retry_read(self, query_str, wait_time, nattempts):
        '''
        This function tries multiple times to read a value and waits a
        set amount of time for each read operation. This is more robust
        than using the query command.
        :param query_str:
        :param wait_time:
        :param nattempts:
        :return:
        '''
        # self.flush_buffer()
        self.write(query_str)
        # self.write(query_str)
        # time.sleep(wait_time)
        for ii in range(1, nattempts):
            # self.flush_buffer()
            # self.write(query_str)
            time.sleep(wait_time)
            try:
                read_string = self.read_until_flush()
                return read_string
            except UnboundLocalError:
                # return self.measure_frequency(phase)
                pass
        return "Did not return meaningful value"
    ###################################################################

    def clear_measurements(self):
        self.write('MEASure:CLEar')
        return

    def output_on(self):
        self.write('OUTPut:STATe 1')
        time.sleep(3)
        return

    def output_off(self):
        self.write('OUTPut:STATe 0')
        time.sleep(3)
        return

    def source_voltage(self, phase, value):
        '''
        phase: {0 | 1 | 2 | 3}
        value:
        '''
        self.write('SOUR{}:VOLT:LEV:IMM:AMPL {}'.format(phase, value))

    def source_frequency(self, freq, phase=0):
        self.write('SOURce{}:FREQuency {}'.format(phase, freq))

    def set_current_limit(self, limit, phase=0):
        '''
        The current level at which the power supply starts
        regulating current.
        .5A_rms is the lowest setting
        '''
        self.write('SOURce{}:CURRent:LEVel:IMMediate:AMPLitude {:.2f}'.format(phase, limit))

    def set_current_shutdown(self, limit, phase=0):
        '''
        The current level at which the output will turn off.
        .5A_rms is the lowest setting.
        '''
        self.write('SOURce{}:CURRent:PROTection:LEVel {}'.format(phase, limit))

    def source_phase(self, degrees, phase):
        self.write('SOURce{}:PHASe:ADJust {}'.format(phase, degrees))

    def flush_buffer(self):
        try:
            while (1):
                self.read()
        except pyvisa.errors.VisaIOError:
            pass
            # print("IO buffer flushed\n")

    def read_until_flush(self):
        '''
        Reads until the buffer is flushed so that there are no errors
        in the read process
        '''
        # self.inst.timeout = 1000
        try:
            while (1):
                read_str = self.read()
                # print(read_str)
        except pyvisa.errors.VisaIOError:
            pass
        return read_str
