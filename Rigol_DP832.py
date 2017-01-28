import Visa_Instrument

class Rigol_DP832(Visa_Instrument.Visa_Instrument):
    def __init__(self, device, rm, debug=False):
        super().__init__(device, rm, debug)
        if self.name == False:
            print("Uh Oh! The machine on " + device + " isn't responding")
            sys.exit()
        else:
            print("Connected to: " + self.name.rstrip('\n'))
            
    
    