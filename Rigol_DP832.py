import Visa_Instrument
import time

class Rigol_DP832(Visa_Instrument.Visa_Instrument):
    
    selectedChannel = 1
    #output is turned off automatically if current exceeds the OCP level
    ocp_levels = [.1, .1, .1]
    
    def __init__(self, rm, debug=False):
        
        for resource_id in rm.list_resources():
            try:
                super().__init__(resource_id, rm, debug)
                if self.query('*IDN?').strip() == 'RIGOL TECHNOLOGIES,DP832,DP8C184350296,00.01.14':
                    print("Connected to: " + self.name.rstrip('\n'))
                    self.inst.timeout = 10000
                    break
                else:
                    #need to close a session if it started!
                    self.inst.close()
            except pyvisa.errors.VisaIOError:
                print(resource_id + "is not DP832, continuing...\n")
                #need to close a session if it started! 
            
    
    def apply(self, voltage, current_limit, channel = 1):
        if self.ocp_levels[channel - 1] < current_limit:
            self.ocp_levels[channel - 1] = current_limit + .2
        #set current protection level
        q = ':OUTPut:OCP:VALue CH{0}, {1:.2f}'.format(channel, self.ocp_levels[channel - 1])
        #print(q)
        self.write(q)
        q =':OUTPut:OCP:STATe CH{channel}, ON'.format(channel = channel)
        #print(q)
        self.write(q)
        
        #apply settings, with current limit
        apply_comm = ':APPLy CH{channel}, {v_level:.1f}, {i_limit:.1f}'.format(channel = channel, v_level = voltage, i_limit = current_limit)
        #print(apply_comm)
        self.write(apply_comm)
        self.turn_on(channel)
        time.sleep(1)
        #check and report back if current limiting is activated:
        q = ':OUTPut:OCP:ALAR? CH{0}'.format(channel)
        stat = self.query(q)
        if stat == 'YES':
            print('Caution! Output on Channel{ch_num} hit current protection level and turned off!'.format(ch_num = channel))
        actual_voltage = float(self.query(':MEASure:VOLTage:DC? CH{0}'.format(channel)))
        print('actual voltage on CH{0} is {1:.3f}'.format(channel, actual_voltage))
        mode = self.query(':OUTPut:MODE? CH{0}'.format(channel))
        if mode == 'CC' or mode == 'UR':
            print('Caution! Current Limiting is active!\n')
        
    
    def turn_off(self, channel = 1):
        self.write(':OUTP CH{channel},OFF'.format(channel = channel))

    def turn_on(self, channel = 1):
        self.write(':OUTP CH{channel},ON'.format(channel = channel))