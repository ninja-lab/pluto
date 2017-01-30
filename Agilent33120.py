import Visa_Instrument
import pyvisa
import time

class f33120a(Visa_Instrument.Visa_Instrument):
    ''' The class for the Agilent 33120a function generator
    '''
    availableShapes = ['SIN' , 'SQU' , 'TRI' , 'RAMP' , 'NOIS' , 'DC' , 'USER']
    
    
    def __init__(self, rm, debug=False):
       
        for resource_id in rm.list_resources():
            try:
                super().__init__(resource_id, rm, debug)
                if self.query('*IDN?').strip() == 'HEWLETT-PACKARD,33120A,0,10.0-5.0-1.0':
                    print("Connected to: " + self.name.rstrip('\n'))
                    self.write('SYSTem:REMote')
                    break
            except pyvisa.errors.VisaIOError:
                print(resource_id + " is not Agilent 33120A, continuing...\n")
    
    def selfTest(self):
        return self.query('*TST?')
        
    def displayText(self, str):
        ''' 11 character string can be displayed
        '''
        self.write("DISPlay:TEXT " + str)
        time.sleep(2)
        self.write("DISPlay:TEXT:CLEar")
        
    def applyFunction(self, shape, freq, ampl, offset):
        ''' shape: SIN | SQU | TRI | RAMP | NOIS | DC | USER
            freq: 
        '''
        val = 'APPLy:' + shape + ' ' + str(freq) + ', ' + str(ampl) + ', ' + str(offset)
        print(val)
        self.write(val)
        
    def outputShape(self, shape):
        if shape not in availableShapes:
            print('shape not supported')
        else:
            self.write('FUNCtion:SHAPe ' + shape)
            
    def outputAmpl(self, ampl):
        self.write('VOLT ' + str(ampl))
            
    def outputOffset(self, offset):
        self.write('VOLT:OFFS ' + str(offset))
        
    def outputFreq(self, freq):
        self.write('FREQ ' + str(freq))
    
    def squareDuty(self, percent, ampl):
        ''' 20% < percent < 80% in 1% increments for freq <= 5MHz
            40% < percent < 60% in 1% increments for freq > 5MHz
        '''
        self.outputShape('SQUare')
        self.outputAmpl(str(ampl))
        self.write('PULSE:DCYCle ' + str(percent))