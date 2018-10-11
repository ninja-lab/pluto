import time
import numpy as np
import Visa_Instrument
import pyvisa
import copy
import sys

class MSO3054(Visa_Instrument.Visa_Instrument):
    """ The class for the Tektronix MSO3054 oscilloscope
    This class is responsible for any functionality not specific to a
    particular channel, e.g. horizontal scale adjustment.
    5 Million point record length
    If the command is concatenated with other commands, the beginning colon is required.
    
    TO DO 
    the status byte register MAV (message available) bit tells you
    if message is in the output queue
    
    improve setup_measurements
    implement trigger STOPAfter options
    eliminate redundancy in acquisition and run/stop functions
    get_transferTime doesn't seem to be used
    """
       
    available_tdivs = [1000,
                       400,
                       200,
                       100,
                       40,
                       20,
                       10,
                       4,
                       2,
                       1,
                       0.4,
                       0.2,
                       0.1,
                       0.04,
                       0.02,
                       0.01,
                       0.004,
                       0.002,
                       0.001,
                       0.0004,
                       0.0002,
                       0.0001,
                       0.00004,
                       0.00002,
                       0.00001,
                       0.000004,
                       0.000002,
                       0.000001,
                       0.0000004,
                       0.0000002,
                       0.0000001,
                       0.00000004,
                       0.00000002,
                       0.00000001,
                       0.000000004,
                       0.000000002,
                       0.000000001]

    available_averageSettings = [512, 256, 128, 64, 32, 16, 8, 4, 2]
    available_recordLengths = [1e3, 1e4, 1e5, 1e6, 5e6]
    def __init__(self, resource, debug=False):
        
        super().__init__(resource, debug)
        self.inst.timeout = 50000
        self.inst.values_format.container = np.array
        self.recordLength = 1e5
        self.issueCommand('HEADer OFF')
        self.issueCommand('HORizontal:RECOrdlength {}'.format(1e5))
        self.numAvg = 0
        self.selectedChannel = 1
        
        self.trigger_dict = {'SOUrce': 'EXT',
                             'COUPling' : 'DC',
                             'LEVel:AUXin': '2.0',
                             'MODe': 'NORMal'}
                    

    def status(self):
        '''
        Read contents of the status byte register using Master Summary
        Status bit. SBR records whether output is available in the Output
        Queue, whether to oscope requests service, and whether Event Status
        Register (SESR) has recorded any events.
        '''
        return self.query("*STB?").strip()

    def wait(self):
        i = 0
        while int(self.query("BUSY?")) == 1:
        #Only reports as busy if acquire mode is to stop after an acquisition...
            print("Waiting...")
            time.sleep(1)
            print(i)
            i += 1
            
    #this should do pretty much the same thing as wait() according to the manual....
    def checkComplete(self):
        tmp = self.query("*OPC?").strip()
        while tmp != "1":
            tmp = self.inst.read()
            print(tmp)
    

    def reset(self):
        # Reset the instrument
        self.sendReset()

    def issueCommand(self, command, feedback=None):
        self.write(command)
        if feedback:
            print(feedback)
        
    def setup_measurements(self):
        '''
        5 measurements can be taken,
        from 4 different channels + math
        change to suit needs:
        '''
        self.issueCommand('MEASU:MEAS1:SOUrce CH1')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS1:TYPe PK2pk')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS2:SOUrce CH1')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS2:TYPe FREQ')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS3:SOUrce CH3')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS3:TYPe MEAN')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS4:SOUrce CH4')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS4:typ MEAN')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS5:SOUrce CH1')
        time.sleep(.2)
        self.issueCommand('MEASU:MEAS5:typ MEAN')
    def getMeas(self, meas_num):
        #scope needs to be running to take periodic measurement
        self.acquisition(True)
        #find what channel is on the measurement, and set selectedChannel as such
        self.selectedChannel = self.query('MEASUrement:MEAS' + str(meas_num) + ':SOURce?')[2]
        meas_type = self.query("MEASUrement:MEAS" + str(meas_num) + ':TYPe?')
        #print(meas_type)
        if meas_type in ['FREQUENCY', 'PERIOD', 'RISE', 'FALL', 'PWIDTH', 'NWIDTH']:
            self.set_vbars()
        elif meas_type in ['MEAN', 'PK2PK', 'CRMS', 'MINIMUM', 'MAXIMUM']:
            self.set_hbars()
        time.sleep(1)
        self.setup_measurements() #like pressing measure button, need measurements in foreground
        time.sleep(5)
        return self.query('MEASUrement:MEAS' + str(meas_num) + ':VALue?')
          
    def set_vbars(self):
        self.issueCommand('CURSor:FUNCtion VBArs', wait=False)
        self.issueCommand('CURSor:SELect:SOUrce CH'+ str(self.selectedChannel), wait=False)
    def set_hbars(self):
        self.issueCommand('CURSor:FUNCtion HBArs')
        self.issueCommand('CURSor:SELect:SOUrce CH'+ str(self.selectedChannel))
        
    def get_vbars_delta(self):
        return float(self.query('CURSor:VBars:DELTa?'))
    
    def setImmedMeas(self, channel, kind, channel2=False):
        '''
        The immediate measurement is not displayed on oscope and has
        no front panel equivalent. Immed measurements are computed only when
        requested and slow the waveform update rate less than displayed measurements
        '''
        self.issueCommand("MEASUrement:IMMed:SOUrce1 CH"+ str(channel))
        if channel2:
            self.issueCommand("MEASUrement:IMMed:SOUrce2 CH"+ str(channel2))
        
        self.issueCommand("MEASUrement:IMMed:TYPe " + kind)
        
    def getImmedMeas(self):
        
        return float(self.query("MEASUrement:IMMed:VALue?"))

    def trigger(self, trigger_dict):
        for key in trigger_dict:
            self.issueCommand('TRIGger:A:{0} {1}'.format(key, trigger_dict[key]))
        self.issueCommand("ACQuire:STOPAfter SEQUENCE")
        
    def autoTrigger(self):
        self.issueCommand("TRIGger:MAIn:MODe AUTO")
    def normalTrigger(self):
        self.issueCommand("TRIGger:MAIn:MODe NORMal")
    def run(self):
        self.issueCommand("ACQuire:STATE RUN")
        time.sleep(.5)
        #timing found necessary from experiment to allow scope to reset acquisition number

    def stop(self):
        self.issueCommand("ACQuire:STATE STOP")
    def set_tScale(self, s):
        '''for window zone?  '''
        self.issueCommand("HORIZONTAL:DELAY:SCALE " + str(s),
                          "Setting timebase to " + str(s) + " s/div")

    def set_averaging(self, averages):
        """ Sets or disables averaging (applies to all channels).
        Valid number of averages are either 4,16,64 or 128.
        A value of 0 or False disables averaging
        """

        if averages in self.available_averageSettings:
            if self.debug:
                print("Setting averaging to " + str(averages) + " samples")
            self.write("ACQuire:MODe AVERage")
            self.write("ACQuire:NUMAVg " + str(averages))
            self.numAvg = averages
        elif averages == 0 or averages == False:
            if self.debug:
                print("Disabling averaging")
            self.write("ACQuire:MODe SAMPLE")
            self.write("ACQuire:NUMAVg " + str(0))
            self.numAvg = 0
        else:
            print(("Number of averages must be in "
                  + str(self.available_averageSettings)))
            sys.exit()

    def set_autoRange(self, mode):
        """ Enables or disables autoranging for the device

        Arguments:
        mode = False | 'vertical' | 'horizontal' | 'both'
        the autoRanging mode with False being Disabled
        """

        if mode == False:
            self.issueCommand("AUTORange:STATE OFF", "Disabling auto ranging")
        elif mode.find("or") != -1:
            self.issueCommand("AUTORANGE:SETTINGS HORizontal",
                              "Setting auto range mode to horizontal")
            self.issueCommand("AUTORange:STATE ON", "Enabling auto ranging")
        elif mode.find("er") != -1:
            self.issueCommand("AUTORANGE:SETTINGS VERTICAL",
                              "Setting auto range mode to vertical")
            self.issueCommand("AUTORange:STATE ON", "Enabling auto ranging")
        elif mode.find("th") != -1:
            self.issueCommand("AUTORANGE:SETTINGS BOTH",
                              "Setting auto range mode to both")
            self.issueCommand("AUTORange:STATE ON", "Enabling auto ranging")
        self.wait()

    def acquisition(self, enable):
        """ Sets acquisition parameter.
            Toggling this controls whether the scope acquires a waveform
            (Equivalent to pressing the front-panel RUN/STOP button)
            Arguments:
            enable [bool] Toggles waveform acquisition
            If the last acquisition was a single acquisition sequence, a new
            single sequence acquisition will be started. If the last acquisition was continuous,
            a new continuous acquisition will be started.
            If RUN is issued in the process of completing a single sequence acquisition (for
            example, averaging or enveloping), the acquisition sequence is restarted, and
            any accumulated data is discarded. Also, the oscilloscope resets the number of
            acquisitions. If the RUN argument is issued while in continuous mode, acquisition
            continues.
            """
        if enable:
            self.issueCommand("ACQuire:STATE ON", "Starting waveform acquisition(s)")
        else:
            self.issueCommand("ACQuire:STATE OFF", "Stopping waveform acquisition")

    def get_numAcquisitions(self):
        """ Indicates the number of acquisitions that have taken place since
        starting oscilloscope acquisition. The maximum number of acquisitions
        that can be counted is 231-1. This value is reset to zero when you
        change most Acquisition, Horizontal, Vertical, or Trigger arguments
        that affect the waveform
        """
        num = self.query("ACQuire:NUMACq?")
        return int(num)

    def waitForAcquisitions(self, num=False):
        """ Waits in a loop until the scope has captured the required number of
        acquisitions
        """
        until = 0
        if num == False and self.numAvg == False:
            print("Waiting for a single acquisition to finish")
            until = 1
        elif num != False:
            until = num
            print("Waiting until " + str(until) + " acquisitions have been made")
        else:
            until = self.numAvg
            print("Waiting until " + str(until) + " acquisitions have been made")
        last = 0
        done = 0
        while done < until:
            if done != last:
                print("Waiting for " + str(until - done) + " acquisitions")
                last = done
            done = self.get_numAcquisitions()
            time.sleep(2)

    def set_hScale(self,
                   tdiv=False,
                   frequency=False,
                   cycles=False):
        """ Set the horizontal scale according to the given parameters.
        Parameters:
           tdiv [float] A time division in seconds (1/10 of the width of the display)
           frequency [float] Select a timebase that will capture '# cycles' of this
                             frequency
           cycles [float] Minimum number of frequency cycles to set timebase for
           used in conjunction with 'frequency' parameter
        """
        if tdiv != False:
            set_div = False
            for a_tdiv in self.available_tdivs:
                if set_div == False and float(tdiv) >= a_tdiv:
                     set_div = a_tdiv
        elif frequency != False:

            if cycles != False:
                set_div = self.find_minTdiv(frequency, cycles)
            else:
                set_div = self.find_minTdiv(frequency)

        if set_div != False:
            self.issueCommand("HORizontal:SCAle " + str(set_div),
                              "Setting horizontal scale to " + str(set_div) + " s/div")
           # if frequency != False and cycles != False:
                #print("Window width = " + str(set_div * 10.0) + " seconds")
        else:
            print()
            print("==========================================================")
            print("      WARNING: Appropriate time division not found")
            print("           Horizontal scale remains unchanged")
            print("==========================================================")
            print()
        return set_div * 10.0

    def get_timeToCapture(self, frequency, cycles, averaging=False):
        """ Calculates and returns the time (in seconds) for a capture
        to complete based on the given frequency, cycles, and number
        of averages.
        """
        if not averaging:
            averaging = self.numAvg
        if averaging == 0:
            averaging = 1

        tdiv = self.find_minTdiv(frequency, cycles)
        windowlength = float(tdiv) * 10.0
        wavelength = 1.0 / frequency

        # time if the first cycle triggers instantly and for every average
        time_min = windowlength * averaging

        # time when triggering is delayed by a full wavelength and at each
        # acquire for an average

        time_max = (windowlength * averaging) + (wavelength * averaging)
        return (time_min, time_max)
    '''
    def get_transferTime(self, mode):
        if mode == 'ASCII':
            return 8.43393707275
        elif mode == 'RPBinary':
            return 4.0
        else:
            print("Error getting transfer time")
        '''
    def find_minTdiv(self, frequency, min_cycles=2):
        """ Finds the minimum s/div that will allow a given number of
        cycles at a particular frequency to fit in a capture
        """
        tmp = copy.copy(self.available_tdivs)
        tmp.reverse()
        wavelength = 1.0 / float(frequency)
        min_div = (wavelength * min_cycles) / 10.0
        for tdiv in tmp:
            if min_div <= tdiv:
                return tdiv
        print()
        print('===================================================')
        print(('WARN: Cant fit ' + str(min_cycles) + ' cycles of '
              + str(frequency) + 'Hz into scope!'))
        print(('Will use ' + str(tmp[len(tmp) - 1]) + ' s/div instead,'
              + ' giving ' + str((tmp[len(tmp) - 1] * 10.0) / wavelength)
              + ' cycles'))
        print('===================================================')
        print()
        return tmp[len(tmp) - 1]
    
    def selectChannels(self, list_of_channels):
        for ch in list_of_channels:
            self.write('SELect:CH{0} ON'.format(ch))
    
    def unselectChannels(self, list_of_channels):
        for ch in list_of_channels:
            self.write('SELect:CH{0} OFF'.format(ch))
            


class channel():
    """ Channel class that implements the functionality related to one of
    the oscilloscope's physical channels.
    Channels HAVE-A scope - but this is not how its implemented currently
    this will fix the reference to numAvg and allows more than one scope to be running
    """
    available_vdivs = [50.0,
                       20.0,
                       10.0,
                       5.0,
                       2.0,
                       1.0,
                       0.5,
                       0.2,
                       0.1,
                       0.05,
                       0.02]

    def __init__(self, scope, channel_num, yunit='V', atten=10):
        
        
        self.channel_num = channel_num
        scope.issueCommand('CH{0}:PRObe:GAIN {1}'.format(channel_num, atten))
        scope.issueCommand('CH{0}:YUNits "{1}"'.format(channel_num, yunit))
        self.scope = scope
        self.y_offset = False
        self.y_mult = False
        self.y_zero = False
        self.x_incr = False
        self.x_num = False
        self.curve_raw = False
        self.curve_raw_mean = False
        self.curve_raw_max = False
        self.curve_raw_min = False
    
    def get_numAvg(self):
        return int(self.scope.query('ACQuire:NUMAVg?'))
        
    def set_vScale(self, s, debug=False):
        """ Sets the V/div setting (vertical scale) for this channel
        """
        tmp = copy.copy(self.available_vdivs)
        if debug:
            print('asked to set vdiv to ' + str(s))
        setVdiv = False
        for vdiv in tmp:
            if s <= vdiv:
                setVdiv = vdiv
        if debug:
            print('best match is ' + str(setVdiv))
        if setVdiv == False:
            print()
            print('===================================================')
            print(('WARN: ' + str(s) + ' V/div is outside of scope range '))
            print(('Will use ' + str(tmp[len(tmp) - 1]) + ' V/div instead,'))
            print('===================================================')
            print()

        self.scope.issueCommand("CH" + str(self.channel_num)
                          + ":SCAle " + str(setVdiv),
                          "Setting channel "
                          + str(self.channel_num)
                          + " scale to "
                          + str(setVdiv) + " V/div")
        self.y_mult = setVdiv

    def set_Position(self, level):
        self.scope.issueCommand("CH" + str(self.channel_num) + ":POSition " + str(level))
        
    def did_clip(self, debug=False, get_new_waveform=False):
        """ Checks to see if the last acquisition contained clipped data points.
        This would indicate that the V/div is set too high. Limits make sense for RPBinary only
        with 1 byte width. 
        It is found by experiment that the digitizing levels do extend beyond the top and 
        bottom of the screen! So waveforms clip on the screen before the digitizer level is 255
        A waveform centered in the middle with peaks +/- 2 division has max 180 and min 77,
        approx +/- 50 out of 127
        Page 2-96: "25 digitizing levels per divsion for 1 byte, 6400 levels for 2 byte data"
        """
        count = 0
        if get_new_waveform:
            #to be accurate, you need to trasnfer the full record length
            #otherwise, you might get just a valley or just a peak
            self.get_raw_waveform()
        if debug:
            print("max value is: " + str(self.curve_raw_max))
            print("min value is: " + str(self.curve_raw_min))
            print("mean value is: " + str(self.curve_raw_mean))
        for point in self.curve_raw:
            #these values from experiment
            if point > 230 or point < 25:
                return True
        return False
    
    def get_Position(self):
        return round(float(scope.query("CH{}:POSition?".format(self.channel_num))),2)
        
    def get_Offset(self):
        return
    def set_Offset(self):
        return
    def zoom_in(self):
        '''
        Increase volts per division and adjust position to compensate.
        Assumes waveform is centered when called, and greater than zero. 
        '''
        set_vdiv = self.get_yScale() #current V/div setting
        if self.available_vdivs.index(set_vdiv) < 10:
            #if you can zoom in, find the next smallest V/div
            temp_index = self.available_vdivs.index(set_vdiv) + 1
            temp1 = self.available_vdivs[temp_index]
            temp2 = 'Zooming in channel '+str(self.channel_num)+' to '
            temp2 += str(temp1)
            temp2 += ' V/div'
            self.set_vScale(temp1)
            
        
        
    def zoom_out(self):
        set_vdiv = self.get_yScale() #current V/div setting
        if self.available_vdivs.index(set_vdiv) > 0:
            #if you can zoom out, find the next largest V/div
            temp_index = self.available_vdivs.index(set_vdiv) - 1
            temp1 = self.available_vdivs[temp_index]
            temp2 = 'Zooming out channel '+str(self.channel_num)+' to '
            temp2 += str(temp1)
            temp2 += ' V/div'
            self.set_vScale(temp1)
             
    def center(self):
        '''
        Using mean digitizer level of self.curve_raw, the current V/div and 
        position, zoom out once vertically, and move position such that mean is 127 
        (middle of screen)
        A clipped mean (mean < 25 or mean > 230) means your off center by atleast 5 divisions
        If you zoom out once, that becomes 2.5 divisions
        if()
        '''
        avg = self.get_numAvg()
        self.scope.set_averaging(0)
        self.scope.waitForAcquisitions()
        self.get_raw_waveform()
        if self.curve_raw_mean < 75 or self.curve_raw_mean > 175:
            print("Mean is {}".format(self.curve_raw_mean))
            self.zoom_out() 
            self.set_Position(-1*self.curve_raw_mean*5.0/255.0) #10 divisions (before zooming out), 5 after
            self.center()
        elif (self.curve_raw_max - self.curve_raw_min) < 40:
            print("Max is {}".format(self.curve_raw_max))
            print("Min is {}".format(self.curve_raw_min)) 
            #zoom in to get a bigger waveform
            self.zoom_in() #AND adjust position... 
            self.set_Position(-1*self.curve_raw_mean*5.0/255.0)
            self.center()
        else:
            print("there ya go")
            self.scope.set_averaging(avg)
            
    def get_yScale(self):
        """ Ask the instrument for this channels V/div setting.
        """
        tmp = self.scope.query('CH' + str(self.channel_num) + ':SCAle?')
        return float(tmp)
    '''
    def get_waveform_autoRange(self, debug=False, wait=True, averages=False):
        """ Download a waveform, checking to see whether the V/div for this
        channel has been set too high or too low.
        This function will automatically adjust the V/div for this channel and
        keep re-requesting captures until the data fits correctly
        """
        xs, ys = self.get_waveform(debug, wait=wait)
        # Check if this waveform contained clipped data
        if self.did_clip():
            clipped = True
            while clipped:
                # Increase V/div until no clipped data
                set_vdiv = self.get_yScale()
                if debug:
                    print('set_vdiv = ' + str(set_vdiv))
                if self.available_vdivs.index(set_vdiv) > 0:
                    best_div = self.available_vdivs[self.available_vdivs.index(set_vdiv) - 1]
                    if debug:
                        temp = 'Setting Y-scale on channel '
                        temp += str(self.channel_num) + ' to '
                        temp += str(best_div)
                        temp += ' V/div'

                    self.set_vScale(best_div)
                    self.scope.waitForAcquisitions(self.get_numAvg())
                    xs, ys = self.get_waveform(debug=False)
                    clipped = self.did_clip()
                else:
                    print()
                    print('===================================================')
                    print('WARN: Scope Y-scale maxed out! THIS IS BAD!!!!!!!!!')
                    print('===================================================')
                    print()
                    clipped = False
        else:
            # Detect if decreasing V/div it will cause clipping
            tmp_max = 0
            tmp_min = 0
            for y in ys:
                if y > tmp_max:
                    tmp_max = y
                elif y < tmp_min:
                    tmp_min = y
            datarange = tmp_max - tmp_min

            set_range = self.get_yScale()
            set_window = set_range * 8.0

            # find the best (minimum no-clip) range
            best_window = 0
            tmp_range = copy.copy(self.available_vdivs)
            available_windows = [x * 8.0 for x in tmp_range]

            for available_window in available_windows:
                if datarange <= (available_window * 0.90):
                    best_window = available_window

            if debug:
                print('bestWindow = ' + str(best_window))

            # if it's not the range were already using, set it
            if best_window != set_window:
                if debug:
                    print('Setting new range' + str(best_window / 8.0))
                self.set_vScale(best_window / 8.0)
                print('Disabling averaging')
                self.scope.set_averaging(False)
                time.sleep(1)
                print(('Enabling averaging, setting to ' + str(averages)))
                self.scope.set_averaging(averages)
                time.sleep(1)
                return self.get_waveform_autoRange(averages=averages)
        return [xs, ys]
    '''
    def set_waveformParams(self,
                           encoding='RPBinary',
                           start=0,
                           stop=1e5,
                           width=1):
        """ Sets waveform parameters for the waveform specified by the channel
        parameter.

        Arguments:
           channel [int - 1-4] - specifies which channel to configure
           encoding: (easier to use DATA:ENCdg instead of WFMOutpre:... 3 times - see table 2-52)
                     RI specifies signed integer data point representation. If BYT_Nr is 1:
           bottom of screen is -128, middle is 0, top of screen is 127.
                     RP specifies positive integer data point representation. If BYT_Nr is 1:
           bottom of screen is 0, top is 255.  
           DATA:ENCdg can accepts SRIbinary, same as RIBinary, except LSB is transferred first.
            Or, SRPBinary, same as RPBinary, except LSB transferred first. 
           start (optional) [int - 0 to record length] - data point to begin transfer from
           stop (optional) [int - start to recordLength] - data point to stop transferring at
           width (optional: 2) [int] - how many bytes per data point to transfer. 
        """
        self.scope.issueCommand(":DATA:SOUrce CH" + str(self.channel_num),
                          "Setting data source to channel " + str(self.channel_num),)
        if encoding == 'ASCII':
            self.scope.issueCommand(":DATA:ENCdg ASCIi",
                              "Setting data encoding to ASCII")
            self.encoding = 'ASCII'
        else:
            self.scope.issueCommand(":DATA:ENCdg RPBinary", 
                              "Setting data encoding to RPBinary")
            self.encoding = 'RPBinary'
        self.scope.issueCommand(":DATA:STARt " + str(start),
                          "Setting start data point to " + str(start))
        self.scope.issueCommand(":DATA:STOP " + str(stop),
                          "Setting stop data point to " + str(stop))
        self.scope.issueCommand(":DATA:WIDTH " + str(width),
                          "Setting bytes transferred per waveform point to " + str(width),)
        self.scope.checkComplete()

    def get_waveformParams(self):
    #does this all need leading colons ?
        print("Data source is " + self.scope.query("MEASUrement:IMMed:SOUrce?"))
        print("Starting data point is " + self.scope.query("DATA:STARt?"))
        print("Ending data point is " + self.scope.query("DATA:STOP?"))
        print("Data encoding is " + self.scope.query("DATA:ENCdg?"))
        print("Data width is " + self.scope.query("DATA:WIDTH?"))
    '''
    def get_transferTime(self):
        return scope.get_transferTime(self.encoding)
    '''
    def get_raw_waveform(self):
        
        #self.stop()
        #ime.sleep(.2)
        #self.run()
        time.sleep(.5)
        #needs provision to wait and also to be running!!
        #check if running, if not, start running. Otherwise you'll see an old waveform
        self.scope.issueCommand('TRIGger')
        self.curve_raw = self.scope.inst.query_binary_values("CURVe?", "B", container=np.array)
        self.curve_raw_mean = np.mean(self.curve_raw)
        self.curve_raw_min = np.min(self.curve_raw)
        self.curve_raw_max = np.max(self.curve_raw)
          
    def get_waveform(self, debug=False, wait=True):
        '''
        Downloads this channels waveform data. This function 
        will not make any adjustments to the V/div settings. If the parameter 
        wait is set to false, the most recent waveform will be
        transmitted. Otherwise the scope will wait for the next data acquisition
        to complete before downloading waveform data. The wait is only reliable
        if the number of acquisitions is starting at zero. 
        '''
        if wait:
            #If scope is in RUNStop mode... you need to hit stop and then run
            #for the number of acquisitions to be reset to 0
            #could check this in the function waitForAcquisitions
            self.scope.waitForAcquisitions(self.get_numAvg())
            

        self.scope.issueCommand(":DATA:SOUrce CH" + str(self.channel_num),
                          "Setting data source to channel " + str(self.channel_num))
                
        out = self.scope.query(":WFMOutpre?")
        '''
        dl is digitizer level
        value in YUNits =
        ((curve_in_dl - YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
        '''
        #watch out for header and verbose mode
        out = out.split(';')
        self.encoding = out[2] #ASC or BIN
        channelStats = out[5] #WFID: channel num, coupling, V/div, s/div, num points, Sample mode 
        parts = channelStats.split(', ')
        self.x_incr = float(out[10])
        self.x_num = int(out[6])
        self.y_mult = float(out[14])
        self.y_zero = float(out[16])
        self.y_offset = float(out[15])
        
        if debug:
            print("Requesting waveform setup information:")
            self.get_waveformParams()
            print("BYT_NR (equivalent to DATa:WIDth) is: " + out[0] )
            print("BIT_NR (number of bits per waveform point) is: " + out[1])
            print("changes to BIT_NR also changes WFMPRe:BYT_Nr and DATa:WIDth")
            print("BN_FMT (binary format, if used): " + out[3])
            print("RI specifies signed integer data-point representation.")
            print("RP specifies positive integer data-point representation.")
            print("BYT_OR (MSB or LSB) is: " + out[4])
            #difference between number of points and x_num is that x_num is the full
            #record of the waveform as captured by the scope, for MDO3014, could be up to 10*10^6
            #NR_PTs is the number transmitted
            print("NR_PT (number of points in transmitted waveform): " + str(self.x_num))
            print("Record Length is " + parts[4].replace(' points',''))
            print("NR_PT depends on DATa:STARt, DATa:STOP, and DATa:SOUrce is YT or FFT")
            print("PT_FMT (Y for normal waveform, ENV for peak detect): " + out[7])
            print("XINCR (interval between samples- sec for non-fft) is: {}.".format(self.x_incr))
            print("y_mult is " + str(self.y_mult))
            print("y_zero is " + str(self.y_zero))
            print("y_offset is " + str(self.y_offset))
            print("Acquire mode is: " + parts[5])
        
        print("Requesting waveform") 
        if self.encoding[:3] == 'BIN':
            stuff = self.scope.inst.query_binary_values("CURVe?", "B", container=np.array)
            '''
            format character for struct module, 'B' is unsigned char, which, 
            matches RP binary format from scope. Width is one so byte order 
            doesn't matter, but it could be specified (page 2-41 in scope manual) 
            '''
        elif self.encoding[:3] == 'ASC':
            stuff = self.scope.inst.query_ascii_values("CURVe?", separator=",")
        else:
            print("Error: Waveform encoding was not understood, exiting!")
            sys.exit()

        self.curve_raw = stuff
        self.curve_raw_mean = np.mean(stuff)
        self.curve_raw_min = np.min(stuff)
        self.curve_raw_max = np.max(stuff)
        data_y = np.empty(self.x_num)
        data_x = np.empty(self.x_num)
        for i in range(self.x_num - 1):
            data_y[i] = (int(stuff[i]) - self.y_offset) * self.y_mult + self.y_zero
            data_x[i] = i * self.x_incr
            
        if self.x_num != False and self.x_num != len(data_y):
            print()
            print("======================================================")
            print("WARNING: Data payload was stated as " + str(self.x_num) + " points")
            print("but " + str(len(data_x)) + " points were returned")
            print("======================================================")
            print()

            ''' 
            if self.did_clip() == True:
                print()
                print("=======================================================")
                print("WARNING: Data payload possibly contained clipped points")
                print("=======================================================")
                print()
            ''' 
        return data_x, data_y

