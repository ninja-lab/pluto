
import Visa_Instrument
#import pyvisa
#import sys
import time
from datetime import datetime

class Keysight34972A(Visa_Instrument.Visa_Instrument):
    
    '''
    use the scan list to return all configured readings at once. 
    First, configure the channels how you want them with the configure methods. 
    Then, the channels you want readings from are defined with set_scan(). 
    The read() command places the instrument in the wait-for-trigger state determined by set_trigger(), and
    once triggered and measurements are complete, they are sent to the PC. 
    
    Alternatively, using INIT takes measurements when the trigger is received, but not sent to the PC until FETCh()
    is called. 
    
    To change the integration time (the number of power line cycles), you must 
    
    '''

    
    def __init__(self, resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 5000
        self.inst.read_termination = '\n'
        self.sendReset()
        self.set_time(datetime.now())
        
        '''
        The istrument cannot report what is on the digital output ports, 
        so the info is stored here and kept updated. 
        '''
        self.byte1 = 0b00000000
        self.byte2 = 0b00000000
        
        
        #self.write('SENSe:TEMPerature:TRANsducer:TCouple:RJUNction:TYPE INTernal (@101:110)')
        
    def set_temp_units(self, ch_list):
        self.inst.write('UNIT:TEMPerature {0}, (@{1})'.format('C','101:110'))
      
    def measure_DCV(self, channel_num):
        val =  self.inst.query('MEASure:VOLTage:DC? (@{})'.format(channel_num))
        return round(float(val), 6)
        
    def measure_ACV(self, channel_num, range='AUTO'):
        val = self.inst.query('MEASure:VOLTage:DC? {0}, (@{1})'.format(range, channel_num))
        return round(float(val), 6)
        
    def measure_Resistance(self, channel_num, range='AUTO'):
        val = self.inst.query('MEASure:RESistance? {0}, (@{1})'.format(range, channel_num))
        return round(float(val),2)
    
    def measure_temp(self, channel_num, probe_type='TCouple', thermocouple='K'):
        temp_str = self.inst.query('MEASure:TEMPerature? {0}, {1}, (@{2})'.format(probe_type, thermocouple,channel_num))
        return round(float(temp_str),4)
    
    def configure_DCV_channels(self, scan_list):
        '''
        Calling configure resets other measurement parameters, so 
        call this first when setting up the instrument. 
        '''
        self.inst.write('CONFigure:VOLTage:DC {}'.format(scan_list))
        self.inst.write('INPut:IMPedance:AUTO ON')
    
    def configure_ACV_channels(self, scan_list):
        self.inst.write('CONFigure:VOLTage:AC {}'.format(scan_list))
        
    def configure_resistance_channels(self, scan_list):
        self.inst.write('CONFigure:RESistance {}'.format(scan_list))
    
    def configure_temp_channels(self, scan_list, probe_type='TCouple', thermocouple='K' ):
        self.inst.write('CONFigure:TEMPerature {0}, {1}, {2}'.format(probe_type, thermocouple, scan_list))
    
    def set_scan(self, scan_list):
        '''
        The scan list is in the form of (@202:207, 209, 302:308) 
        That example includes channels 202 through 207, 209, and 302 through 308 in the scan list. 
        '''
        self.inst.write('ROUTe:SCAN {}'.format(scan_list))
        self.inst.write('ROUTe:CHANnel:DELay:AUTO ON')
        self.inst.write('INPut:IMPedance:AUTO ON') #{}'.format(scan_list)) #IM changing the input resistance of the keysite(HVCAP,TP5B,TP1B) from 10M to >10G

    def set_delay(self, seconds, scan_list):
        ''' Only valid while scanning. CONFigure and MEASure? set the channel delay to automatic
        '''
        self.inst.write('ROUTe:CHANnel:DELay {0}, {1}'.format(seconds, scan_list))
        
    def set_trigger(self, source):
        '''
        BUS | IMMediate | EXTernal | TIMer | ALARm[n]
        For IMMediate, trigger is always present, and when 
        instrument goes in to 'wait for trigger' state, the 
        trigger is issued immediately. 
        '''
        self.inst.write('TRIGger:SOUrce {}'.format(source))
    def set_timer(self,seconds):
        '''
        seconds: a number from 0 to 359,999 with 1ms resolution
        (0 to 100 hours)
        '''
        self.inst.write('TRIGger:TIMer {}'.format(seconds))
    def set_trigger_count(self, count):
        '''
        An integer from 1 to 50,000 triggers
        '''
        self.inst.write('TRIGger:COUNt {}'.format(count))
        
    def get_NPLC(self, scan_list):
        val = self.inst.query('SENSe:VOLTage:DC:NPLC? ({})'.format(scan_list))
        return float(val)
    
    def set_NPLC(self, cycles, scan_list):
        ''' cycles is the number of power line cycles used as integration time.
        cycles = {0.02|0.2|1|2|10|20|100|200|MIN|MAX}
        Factory reset value is 1 PLC
        
        TODO: check which channels are measuring what: voltage, resistance, etc
        otherwise it errors
        '''
        self.inst.write('SENSe:VOLTage:DC:NPLC {}, {}'.format(cycles, scan_list))
        
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
    def read_with_absolute_time(self):
        '''
        This function assumes that format_reading has been called
        with format_reading(time=1, channel=1)
        Absolute or Relative time setting should also be set. 
        The readings come back in a string:
            measurement1, year1, month1, day1, hour1, min1, sec1, channel,
            measurement2, year2, ...
        Returns:
            A dictionary of dictionarys. 
            {'201':{'measurement': val,
                    'year': val,
                    ...}
             '202':{'measurement': val,
                    'year': val,
                    ...}
        '''
        def makedict(alist):
            mydict = {}
            mydict['Measurement'] = float(alist[0])
            mydict['year'] = int(alist[1])
            mydict['month'] = int(alist[2])
            mydict['day'] = int(alist[3])
            mydict['hour'] = int(alist[4])
            mydict['minute'] = int(alist[5])
            mydict['sec'] = float(alist[6])
            return mydict
        data = self.inst.query('READ?').split(',')
        num_readings = int(len(data)/8)
        total_dict = {}
        for i in [j*8 for j in range(num_readings)]:
            single_meas = data[i:i+8] #8 things, 0-7
            total_dict[single_meas[7]] = makedict(single_meas[0:7])
        return total_dict
            
            
        
    def format_reading(self, time=0, channel=0, alarm=0):
        self.inst.write('FORMat:READing:ALARm {}'.format(alarm))
        self.inst.write('FORMat:READing:CHANnel {}'.format(channel))
        self.inst.write('FORMat:READing:TIME {}'.format(time))
        return 
    
    def format_time_type(self, time_type='RELative'):
        self.inst.write('FORMat:READing:TIME:TYPE {}'.format(time_type))
    def set_time(self, stamp):
        
        self.inst.write('SYSTem:TIME {}, {}, {:.3f}'.format(stamp.hour, stamp.minute, stamp.second+stamp.microsecond/1e6))
        self.inst.write('SYStem:DATE {}, {}, {}'.format(stamp.year, stamp.month, stamp.day))
    def analog_source(self, channel, voltage):
        '''
        use the multifunction module 34907A DAC to source 
        voltage from -12V to +12V with 1mV resolution and 10mA max current.
        Channel: must end in 04 or 05
        '''
        self.inst.write('SOURce:VOLTage {},(@{})'.format(voltage, channel))
        
    
    def digital_source1(self, bit, level):
        '''
        Check the current state of the digital output 
        OR in the new bit to change, don't change the others
        channel: numbered "s01" (lower byte) and "s02" 
            (upper byte), where s represents the slot number.
        bit: 0 through 7
        level: 0 or 1
        '''
        
        val = self.byte1
        #clear the bit we want to write to
        clr = (0b1 << bit) ^ 0xFF
        val = val & clr 
        #OR in the new bit
        val = val | level << bit
        self.byte1 = val
        self.inst.write('SOURCe:DIGital:DATA:BYTE {},(@{})'.format(val, 101))
        
    def digital_source2(self,bit, level):
        '''
        Check the current state of the digital output 
        OR in the new bit to change, don't change the others
        channel: numbered "s01" (lower byte) and "s02" 
            (upper byte), where s represents the slot number.
        bit: 0 through 7
        level: 0 or 1
        '''
        
        val = self.byte2
        #clear the bit we want to write to
        clr = (0b1 << bit) ^ 0xFF
        val = val & clr 
        #OR in the new bit
        val = val | level << bit
        self.byte2 = val
        self.inst.write('SOURCe:DIGital:DATA:BYTE {},(@{})'.format(val, 102)) 

    def monitorQuantity(self, quantity):
        channel_num = quantity.getChannel()
        self.configure_DCV_channels('(@{})'.format(channel_num))
        time.sleep(.2)
        self.setScale(quantity.getScale(), channel_num)
        time.sleep(.2)
        self.setOffset(quantity.getOffset(), channel_num)
        time.sleep(.2)
        self.useScaling()
        time.sleep(.2)
        self.inst.write('ROUTe:MONitor (@{})'.format(channel_num))
        time.sleep(.2)
        self.inst.write('ROUTe:MONitor:STATe ON')
    def configureQuantityDCV(self, alist):
        '''
        Take a list of quantity objects, configure all for DCV
        measurements
        '''
        #build a list of channel numbers:
        channels = [elem.getChannel() for elem in alist]
        #make a string with commas in between each channel
        ch_str = ''
        for ch in channels:
            ch_str += str(ch) + ','
        #get rid of last comma
        ch_str = ch_str[:-1]
        #put in form required by the instrument
        scan_list = '(@' + ch_str + ')'
        self.configure_DCV_channels(scan_list)
        
    def setQuantityScan(self, alist):
        '''
        Take a list of quantity objects, set the scan list accordingly, use 
        scaling and offset. 
        '''
        #build a list of channel numbers:
        channels = [elem.getChannel() for elem in alist]
        #make a string with commas in between each channel
        ch_str = ''
        for ch in channels:
            ch_str += str(ch) + ','
        #get rid of last comma
        ch_str = ch_str[:-1]
        #put in form required by the instrument
        scan_list = '(@' + ch_str + ')'
        self.set_scan(scan_list)
        for my_quantity in alist:
            self.setScale(my_quantity.getScale(), my_quantity.getChannel())
            self.setOffset(my_quantity.getOffset(), my_quantity.getChannel())
        self.useScaling()
        
    
    def monitor(self, channel_num):
        self.inst.write('ROUTe:MONitor (@{})'.format(channel_num))
        time.sleep(.2)
        self.inst.write('ROUTe:MONitor:STATe ON')
    def monitorData(self):
        return float(self.inst.query('ROUTe:MONitor:DATA?'))
    def setScale(self, scale, channel_num):
        self.inst.write('CALCulate:SCALe:GAIN {},(@{})'.format(scale, channel_num))
    def setOffset(self, offset, channel_num):
        self.inst.write('CALCulate:SCALe:OFFSet {},(@{})'.format(offset, channel_num))
    def useScaling(self):
        '''
        This will apply to all channels
        '''
        self.inst.write('CALCulate:SCALe:STATe ON')