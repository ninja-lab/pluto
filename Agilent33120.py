import serialInstrument
import time

class f33120a(serialInstrument.serialInstrument):
    ''' The class for the Agilent 33120a function generator
    '''
    availableShapes = ['SIN' , 'SQU' , 'TRI' , 'RAMP' , 'NOIS' , 'DC' , 'USER']
    
    
    def __init__(self, device, rm, debug=False):
       
        super().__init__(device, rm, debug)
        if self.name == False:
            print("Uh Oh! The machine on " + device + " isn't responding")
            sys.exit()
        else:
            print("Connected to: " + self.name.rstrip('\n'))
            self.write('SYSTEM:REMOTE')
            self.inst.timeout = 10000
            print("Output Load is set to: "+ self.query("OUTPut:Load?")+" [ohms]")
    
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