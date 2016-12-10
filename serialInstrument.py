
class serialInstrument:
    '''
    A base class? for instruments that use RS232. 
    '''
    def __init__(self, asrl_num, rm):
        self.device = asrl_num
        
        self.inst = rm.open_resource(asrl_num)
        #flush serial queue?

    def getName(self):
        ''' Returns the instrument identifier name
        '''
        return self.inst.query("*IDN?")
        
    
