import numpy as np

class serialInstrument:
    """ The base class for a serial instrument.
    Extend this class to implement other instruments with a serial interface.
    """
    prevCommand = ''
    debug = False

    def __init__(self, asrl_num, rm, debug=False):
        self.device = asrl_num
        self.debug = debug
        self.inst = rm.open_resource(asrl_num, send_end=True) #the VISA resource
        self.name = self.getName()
        self.inst.values_format.container = np.array
        
    def getName(self):
        """ Returns the instruments identifier string.
        This is a fairly universal command so should work on most devices.
        """
        return self.inst.query("*IDN?")

    def sendReset(self):
        """ Resets the instrument.
        This is a fairly universal command so should work on most devices.
        """
        print("Resetting machine")
        self.inst.write("*RST")

    def query(self, command):
        return self.inst.query(command).strip()

    def write(self, command):
        # Send an arbitrary command directly to the scope
        self.inst.write(command)

    def read(self):
        return self.inst.read()
    