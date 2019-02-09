
class Visa_Instrument:
    """ The base class for a serial instrument.
    Extend this class to implement other instruments with a serial interface.
    
    There is a first filter that screens what events make it to the SESR and Event Queue. 
    There is a second filter that screens what events make it to bit 4 of the Status Byte Register. 
    
    When output is sent to the Output Queue, the MAV bit in the SBR is set to 1. 
    
    When a bit in the SBR is set to 1 and corresponding bit in the SRER is enabled, the 
    MSS bit in SBR is also set to 1, and a service request is generated via...
    """
    prevCommand = ''
    

    def __init__(self, inst, debug=False):
        
        self.debug = debug
        self.inst = inst #the VISA resource
        self.name = self.getName()
        
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
        return self.inst.read().strip()
        
    def readESR(self):
        '''
        The SESR (standard event status register) records 8 types events.
        Reading clears the bits. 
        Events enabled by ___ will cause bit5 (Event Summary Bit) of the status byte register. 
        
        
        '''
        return self.query('*ESR?')
        
    def readSTB(self):
        ''' 
        Records whether output is available in Output queue (bit 4, message available)
        Records if any (enabled) events have been recorderd in SESR. 
        Reading does not clear bits. 
        
        Reading Status Byte Register like this, bit 6 is interpreted as MSS (Master Status Summary)
            which "summarizes ESB and MAV bits"
              * Reading as a "Serial Poll" interprets bit 6 as RQS *
        Bits are set and cleared depending on lots of things. 
        '''
        return self.query('*STB?')
        
    def writeDESER(self, decimal_sum):
        '''
        Control which types of events are reported to SESR (and found by readESR()) and 
        the Event Queue. 
        BIT     EVENT
        7       PON
        6       URQ ?
        5       CME command error
        4       EXE execution event
        3       DDE device error (self test or calibration error)
        2       QYE query error
        1       RQC ? 
        0       OPC - dependent on ...
        It may make sense to have the same argument to writeESER()
        
        '''
        self.write('DESE {}'.format(decimal_sum))
        
        
    def writeSRER(self, decimal_sum):
        '''
        This register (Service Request Enable Register) controls which bits in the SBR
        generate a Service Request and are summarized by the Master Status Summary. 
        0   service request is disabled
        16  request service (how? )via MAV bit (bit 4 of SBR) true.
        32  request service when the ESB (event status) bit (bit 5 of SBR) is true.
        48  request service when either MAV or ESB of SBR is true
        '''
        self.write("*SRE {}".format(decimal_sum))
        
    def readSRER(self):
        return self.query('*SRE?')
        
    def writeESER(self, decimal_sum ):
        '''
        Set bits in the Event Status Enable Register.
        Events whose bits are cleared will not be reported to the Status Byte Register, 
        from the SESR.
        It may make sense to have the values the same as DESER. 
        '''
        self.write('*ESE {}'.format(decimal_sum))
        
        
    def readLastEvent(self):
        '''
        You must first use readESR() query to read the summary of the event from the SESR.
        This makes events summarized by the *ESR? read available to EVENT? and EVNMSG?
        Events that follow a readESR() are put in the event queue but are not available until
        another readESR() is used. 
        '''
        print(self.readESR())
        return self.query('ENVMSG?')
    
    def close(self):
        #self.inst.clear()
        self.inst.before_close()
        self.inst.close()
    
    