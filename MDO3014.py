import time
import numpy as np
import Visa_Instrument
import pyvisa
import copy
import sys

class MDO3014(Visa_Instrument.Visa_Instrument):
    """ The class for the Tektronix TPS2024 oscilloscope
    This class is responsible for any functionality not specific to a
    particular channel, e.g. horizontal scale adjustment.
    
    TO DO 
    the status byte register MAV (message available) bit tells you
    if message is in the output queue
    """

    x_incr = False
    x_num = False
    numAvg = 0
    selectedChannel = 1
    debug = False

    available_tdivs = [50,
                       25,
                       10,
                       5,
                       2.5,
                       1,
                       0.5,
                       0.25,
                       0.1,
                       0.05,
                       0.025,
                       0.01,
                       0.005,
                       0.0025,
                       0.001,
                       0.0005,
                       0.00025,
                       0.0001,
                       0.00005,
                       0.000025,
                       0.00001,
                       0.000005,
                       0.0000025,
                       0.000001,
                       0.0000005,
                       0.00000025,
                       0.0000001,
                       0.00000005,
                       0.000000025,
                       0.00000001,
                       0.000000005,
                       0.0000000025]

    available_averageSettings = [128, 64, 16, 4]

    def __init__(self, rm, debug=False):
        
        for resource_id in rm.list_resources():
            try:
                super().__init__(resource_id, rm, debug)
                if self.query('*IDN?').strip() == 'TEKTRONIX,MDO3014,C030398,CF:91.1CT FV:v1.22':
                    print("Connected to: " + self.name.rstrip('\n'))
                    self.inst.timeout = 50000
                    break
            except pyvisa.errors.VisaIOError:
                print(resource_id + " is not Tektronix MDO3014, continuing...\n")
            

    def status(self):
        '''
        Read contents of the status byte register using Master Summary
        Status bit. SBR records whether output is available in the Output
        Queue, whether to oscope requests service, and whether Event Status
        Register (SESR) has recorded any events.
        '''
        return self.query("*STB?").strip()

    def wait(self):
        #self.write("BUSY?")
        #@tmp = self.read()
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

    def issueCommand(self, command, feedback=None, wait=True):
        self.write(command)
        if feedback:
            print(feedback)
        #if wait == True:
            #self.checkComplete()
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
        self.issueCommand('CURSor:FUNCtion HBArs', wait=False)
        self.issueCommand('CURSor:SELect:SOUrce CH'+ str(self.selectedChannel), wait=False)
        
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
        
        return self.query("MEASUrement:IMMed:VALue?")

    def trigger(self, coupling, channel, mode, level=0):
        #self.issueCommand("TRIGger:MAIn SETLevel")
        #self.issueCommand("TRIGger:MAIn SETLevel")
        #self.issueCommand("TRIGger:MAIn SETLevel")
        self.issueCommand("TRIGger:MAIn:EDGE:COUPling " + coupling)
        self.issueCommand("TRIGger:MAIn:EDGE:SOUrce {channel}".format(channel = channel))
        self.issueCommand("TRIGger:MAIn:MODe " + mode)
        self.issueCommand("ACQuire:STOPAfter SEQUENCE")
        if mode == 'NORMal':
            self.issueCommand("TRIGger:MAIn:LEVel " + str(level))
        
    def autoTrigger(self):
        self.issueCommand("TRIGger:MAIn:MODe AUTO")
    def normalTrigger(self):
        self.issueCommand("TRIGger:MAIn:MODe NORMal")
    def run(self):
        self.issueCommand("ACQuire:STATE RUN")
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
        #while num == False:
         #   num = self.read()
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
        done = self.get_numAcquisitions()
        while done < until:
            if done != last:
                print("Waiting for " + str(until - done) + " acquisitions")
                last = done
            done = self.get_numAcquisitions()
            time.sleep(0.1)

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

    def get_timeToCapture(self, frequency, cycles, averaging=1):
        """ Calculates and returns the time (in seconds) for a capture
        to complete based on the given frequency, cycles, and number
        of averages.
        """
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

    def get_transferTime(self, mode):
        if mode == 'ASCII':
            return 8.43393707275
        elif mode == 'RPBinary':
            return 4.0
        else:
            print("Error getting transfer time")

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
            


class channel(MDO3014):
    """ Channel class that implements the functionality related to one of
    the oscilloscope's physical channels.
    """
    channel = False  # Channel num
    y_offset = False
    y_mult = False
    y_zero = False
    curve_raw = False
    curve_raw_mean = False
    curve_raw_max = False
    curve_raw_min = False

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

    def __init__(self, inst, channel, yunit='V', atten=10):
        self.inst = inst
        self.channel = channel
        self.issueCommand('CH'+str(self.channel) + ':PRObe ' + str(atten))
        self.issueCommand('CH'+str(self.channel) + ':YUNit ' + '"' + yunit + '"')

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

        self.issueCommand("CH" + str(self.channel)
                          + ":SCAle " + str(setVdiv),
                          "Setting channel "
                          + str(self.channel)
                          + " scale to "
                          + str(setVdiv) + " V/div")
        self.y_mult = setVdiv

    def set_Position(self, level):
        self.issueCommand("CH" + str(self.channel) + ":POSition " + str(level))
        
    def did_clip(self, debug=False):
        """ Checks to see if the last acquisition contained clipped data points.
        This would indicate that the V/div is set too high. Limits make sense for RPBinary only
        with 1 byte width. 
        It is found by experiment that the digitizing levels do extend beyond the top and 
        bottom of the screen! So waveforms clip on the screen before the digitizer level is 255
        A waveform centered in the middle with peaks +/- 2 division has max 180 and min 77,
        approx +/- 50 out of 127
        """
        count = 0
        #if self.curve_raw != False:
        for point in self.curve_raw:
            #these values from experiment
            if point > 230 or point < 25:
                count += 1
            else:
                count = 0

            if count > 1:
                return True
        return False
    
    def get_Position(self):
        return round(float(self.query("CH{}:POSition?".format(self.channel))),2)
        
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
            temp2 = 'Zooming in channel '+str(self.channel)+' to '
            temp2 += str(temp1)
            temp2 += ' V/div'
            #print(temp2)
            self.set_vScale(temp1)
            
        
        
    def zoom_out(self):
        set_vdiv = self.get_yScale() #current V/div setting
        if self.available_vdivs.index(set_vdiv) > 0:
            #if you can zoom out, find the next largest V/div
            temp_index = self.available_vdivs.index(set_vdiv) - 1
            temp1 = self.available_vdivs[temp_index]
            temp2 = 'Zooming out channel '+str(self.channel)+' to '
            temp2 += str(temp1)
            temp2 += ' V/div'
            #print(temp2)
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
        self.get_raw_waveform()
        if self.curve_raw_mean < 75 or self.curve_raw_mean > 175:
            #print("Mean is {}".format(self.curve_raw_mean))
            self.zoom_out() 
            self.set_Position(-1*self.curve_raw_mean*5.0/255.0) #10 divisions (before zooming out), 5 after
            self.center()
        elif (self.curve_raw_max - self.curve_raw_min) < 40:
            #print("Max is {}".format(self.curve_raw_max))
            #print("Min is {}".format(self.curve_raw_min)) 
            #zoom in to get a bigger waveform
            self.zoom_in() #AND adjust position... 
            self.set_Position(-1*self.curve_raw_mean*5.0/255.0)
            self.center()
        else:
            print("there ya go")
            
    def get_yScale(self):
        """ Ask the instrument for this channels V/div setting.
        """
        tmp = self.query('CH' + str(self.channel) + ':SCAle?')
        return float(tmp)

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
                        temp += str(self.channel) + ' to '
                        temp += str(best_div)
                        temp += ' V/div'

                    self.set_vScale(best_div)
                    self.waitForAcquisitions(self.numAvg)
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
                self.set_averaging(False)
                time.sleep(1)
                print(('Enabling averaging, setting to ' + str(averages)))
                self.set_averaging(averages)
                time.sleep(1)
                return self.get_waveform_autoRange(averages=averages)
        return [xs, ys]
  
    def set_waveformParams(self,
                           encoding='RPBinary',
                           start=0,
                           stop=20000,
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
           start (optional: 0) [int - 0-2499] - data point to begin transfer from
           stop (optional: 2500) [int - 1-2500] - data point to stop transferring at
           width (optional: 2) [int] - how many bytes per data point to transfer. Does this imply
           resolution? Because top and bottom of screen are limits in both cases I think. 
        """
        self.issueCommand(":DATA:SOUrce CH" + str(self.channel),
                          "Setting data source to channel " + str(self.channel),
                          False)
        if encoding == 'ASCII':
            self.issueCommand(":DATA:ENCdg ASCIi",
                              "Setting data encoding to ASCII", False)
            self.encoding = 'ASCII'
        else:
            self.issueCommand(":DATA:ENCdg RPBinary", 
                              "Setting data encoding to RPBinary", False)
            self.encoding = 'RPBinary'
        self.issueCommand(":DATA:STARt " + str(start),
                          "Setting start data point to " + str(start), False)
        self.issueCommand(":DATA:STOP " + str(stop),
                          "Setting stop data point to " + str(stop), False)
        self.issueCommand(":DATA:WIDTH " + str(width),
                          "Setting of bytes to transfer per waveform point to " + str(width),
                          False)
        self.checkComplete()

    def get_waveformParams(self):
    #does this all need leading colons:???/"
            print("Data source is " + self.inst.query("MEASUrement:IMMed:SOUrce?"))
            print("Starting data point is " + self.inst.query("DATA:STARt?"))
            print("Ending data point is " + self.inst.query("DATA:STOP?"))
            print("Data encoding is " + self.inst.query("DATA:ENCdg?"))
            print("Data width is " + self.inst.query("DATA:WIDTH?"))

    def get_transferTime(self):
        return self.inst.get_transferTime(self.encoding)

    def get_raw_waveform(self):
        time.sleep(2)
        self.curve_raw = self.inst.inst.query_binary_values("CURVe?", "B")
        self.curve_raw_mean = np.mean(self.curve_raw)
        self.curve_raw_min = np.min(self.curve_raw)
        self.curve_raw_max = np.max(self.curve_raw)
        
    

    
    def get_waveform(self, debug=False, wait=True):
        '''
        Downloads this channels waveform data.This function 
        will not make any adjustments to the V/div settings.If the parameter 
        wait is set to false, the most recent waveform will be
        captured. Otherwise the scope will wait for the next data acquisition
        to complete before downloading waveform data. The wait is only reliable
        if the number of acquisitions is starting at zero. 
        '''
        if wait:
            self.waitForAcquisitions()

        self.issueCommand(":DATA:SOUrce CH" + str(self.channel),
                          "Setting data source to channel " + str(self.channel))
                
        out = self.query(":WFMOutpre?")
        y_offset = False
        y_mult = False
        x_incr = False
        y_zero = False
        x_num = False
        '''
	dl is digitizer level
	value in YUNits =
	((curve_in_dl - YOFF_in_dl) * YMUlt) + YZERO_in_YUNits
	'''
#watch out for header and verbose mode
        out = out.split(';')
        encoding = out[2] #ASC or BIN
        channelStats = out[5] #WFID: channel num, coupling, V/div, s/div, num points, Sample mode 
        parts = channelStats.split(', ')
        x_incr = float(out[10])
        x_num = int(parts[4].replace(' points',''))
        y_mult = float(out[14])
        y_zero = float(out[16])
        y_offset = float(out[15])
        
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
            print("NR_PT (number of points in transmitted waveform): " + out[6])
            print("x_num is " + str(x_num))
            print("NR_PT depends on DATa:STARt, DATa:STOP, and DATa:SOUrce is YT or FFT")
            print("PT_FMT (Y for normal waveform, ENV for peak detect): " + out[7])
            print("XINCR (interval between samples- sec for non-fft) is: {}.".format(x_incr))
            print("y_mult is " + str(y_mult))
            print("y_zero is " + str(y_zero))
            print("y_offset is " + str(y_offset))
            print("Acquire mode is: " + parts[5])
            
       
        
        print("Requesting waveform") 
        if encoding[:3] == 'BIN':
            stuff = self.inst.inst.query_binary_values("CURVe?", "B")
            '''
            format character for struct module, 'B' is unsigned char, which, 
            matches RP binary format from scope. Width is one so byte order 
            doesn't matter, but it could be specified (page 2-41 in scope manual) 
            '''
        elif encoding[:3] == 'ASC':
            stuff = self.inst.inst.query_ascii_values("CURVe?", separator=",", container=list)
        else:
            print("Error: Waveform encoding was not understood, exiting!")
            sys.exit()

        self.curve_raw = stuff
        data_y = [((int(x) - y_offset) * y_mult) + y_zero for x in stuff]
        data_x = [x * x_incr for x in range(len(data_y))]

        if self.x_num != False and x_num != len(data_y):
            print()
            print("======================================================")
            print("WARNING: Data payload was stated as " + str(self.x_num) + " points")
            print("but " + str(len(data_x)) + " points were returned")
            print("======================================================")
            print()

        self.y_offset = y_offset
        self.y_mult = y_mult
        self.x_incr = x_incr
        self.y_zero = y_zero

        if self.did_clip() == True:
            print()
            print("=======================================================")
            print("WARNING: Data payload possibly contained clipped points")
            print("=======================================================")
            print()

        return data_x, data_y

