import pyvisa
import datetime
import time
import re
import csv
from math import floor, log10
import Visa_Instrument
import pandas as pd
import numpy as np
from math import ceil 

class rigol_ds1054z(Visa_Instrument.Visa_Instrument):
    
    # Constructor
    def __init__(self,resource, debug=False):
        super().__init__(resource, debug)
        self.inst.timeout = 5000
        #self.inst.read_termination = '\n'
        #self.sendReset()
        self.debug = debug

    class measurement:
        def __init__(self, name='', description='', command='', unit='', return_type=''):
            self.name        = name
            self.description = description
            self.command     = command
            self.unit        = unit
            self.return_type = return_type
    
    max_voltage           = measurement(name='max_voltage',          command='VMAX', unit='Volts',         return_type='float', description='voltage value from the highest point of the waveform to the GND')
    min_voltage           = measurement(name='min_voltage',          command='VMIN', unit='Volts',         return_type='float', description='voltage value from the lowest point of the waveform to the GND')
    peak_to_peak_voltage  = measurement(name='peak_to_peak_voltage', command='VPP',  unit='Volts',         return_type='float', description='voltage value from the highest point to the lowest point of the waveform')
    top_voltage           = measurement(name='top_voltage',          command='VTOP', unit='Volts',         return_type='float', description='voltage value from the flat top of the waveform to the GND')
    base_voltage          = measurement(name='base_voltage',         command='VBAS', unit='Volts',         return_type='float', description='voltage value from the flat base of the waveform to the GND')
    top_to_base_voltage   = measurement(name='top_to_base_voltage',  command='VAMP', unit='Volts',         return_type='float', description='voltage value from the top of the waveform to the base of the waveform')
    average_voltage       = measurement(name='average_voltage',      command='VAVG', unit='Volts',         return_type='float', description='arithmetic average value on the whole waveform or on the gating area')
    rms_voltage           = measurement(name='rms_voltage',          command='VRMS', unit='Volts',         return_type='float', description='root mean square value on the whole waveform or the gating area')
    upper_voltage         = measurement(name='upper_voltage',        command='VUP',  unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold maximum value')
    mid_voltage           = measurement(name='mid_voltage',          command='VMID', unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold middle value')
    lower_voltage         = measurement(name='lower_voltage',        command='VLOW', unit='Volts',         return_type='float', description='actual voltage value corresponding to the threshold minimum value')
    overshoot_voltage     = measurement(name='overshoot_percent',    command='OVER', unit='%%',            return_type='float', description='ratio of the difference of the maximum value and top value of the waveform to the amplitude value')
    preshoot_voltage      = measurement(name='preshoot_percent',     command='PRES', unit='%%',            return_type='float', description='ratio of the difference of the minimum value and base value of the waveform to the amplitude value')
    variance_voltage      = measurement(name='variance_voltage',     command='VARI', unit='Volts',         return_type='float', description='average of the sum of the squares for the difference between the amplitude value of each waveform point and the waveform average value on the whole waveform or on the gating area')
    period_rms_voltage    = measurement(name='period_rms_voltage',   command='PVRMS',unit='Volts',         return_type='float', description='root mean square value within a period of the waveform')
    period_time           = measurement(name='period_time',          command='PER',  unit='Seconds',       return_type='float', description='time between the middle threshold points of two consecutive, like-polarity edges')
    frequency             = measurement(name='frequency',            command='FREQ', unit='Hz',            return_type='float', description='reciprocal of period')
    rise_time             = measurement(name='rise_time',            command='RTIM', unit='Seconds',       return_type='string',description='time for the signal amplitude to rise from the threshold lower limit to the threshold upper limit')
    fall_time             = measurement(name='fall_time',            command='FTIM', unit='Seconds',       return_type='string',description='time for the signal amplitude to fall from the threshold upper limit to the threshold lower limit')
    positive_width_time   = measurement(name='positive_width_time',  command='PWID', unit='Seconds',       return_type='float', description='time difference between the threshold middle value of a rising edge and the threshold middle value of the next falling edge of the pulse')
    negative_width_time   = measurement(name='negative_width_time',  command='NWID', unit='Seconds',       return_type='float', description='time difference between the threshold middle value of a falling edge and the threshold middle value of the next rising edge of the pulse')
    positive_duty_percent = measurement(name='positive_duty_ratio',  command='PDUT', unit='%%',            return_type='float', description='ratio of the positive pulse width to the period')
    negative_duty_percent = measurement(name='negative_duty_ratio',  command='NDUT', unit='%%',            return_type='float', description='ratio of the negative pulse width to the period')
    max_voltage_time      = measurement(name='max_voltage_time',     command='TVMAX',unit='Seconds',       return_type='float', description='time corresponding to the waveform maximum value')
    min_voltage_time      = measurement(name='min_voltage_time',     command='TVMIN',unit='Seconds',       return_type='float', description='time corresponding to the waveform minimum value')
    positive_pulse_number = measurement(name='positive_pulse_number',command='PPUL', unit='Occurances',    return_type='int',   description='number of positive pulses that rise from below the threshold lower limit to above the threshold upper limit')
    negative_pulse_number = measurement(name='negative_pulse_number',command='NPUL', unit='Occurances',    return_type='int',   description='number of negative pulses that fall from above the threshold upper limit to below the threshold lower limit')
    positive_edges_number = measurement(name='positive_edges_number',command='PEDG', unit='Occurances',    return_type='int',   description='number of rising edges that rise from below the threshold lower limit to above the threshold upper limit')
    negative_edges_number = measurement(name='negative_edges_number',command='NEDG', unit='Occurances',    return_type='int',   description='number of falling edges that fall from above the threshold upper limit to below the threshold lower limit')
    rising_delay_time     = measurement(name='rising_delay_time',    command='RDEL', unit='Seconds',       return_type='string',description='time difference between the falling edges of source 1 and source 2. Negative delay indicates that the selected falling edge of source 1 occurred after that of source 2')
    falling_delay_time    = measurement(name='falling_delay_time',   command='FDEL', unit='Seconds',       return_type='string',description='time difference between the falling edges of source 1 and source 2. Negative delay indicates that the selected falling edge of source 1 occurred after that of source 2')
    rising_phase_ratio    = measurement(name='rising_phase_ratio',   command='RPH',  unit='Degrees',       return_type='float', description='rising_delay_time / period_time x 360 degrees')
    falling_phase_ratio   = measurement(name='falling_phase_ratio',  command='FPH',  unit='Degrees',       return_type='float', description='falling_delay_time / period_time x 360 degrees')
    positive_slew_rate    = measurement(name='positive_slew_rate',   command='PSLEW',unit='Volts / Second',return_type='float', description='divide the difference of the upper value and lower value on the rising edge by the corresponding time')
    negative_slew_rate    = measurement(name='negative_slew_rate',   command='NSLEW',unit='Volts / Second',return_type='float', description='divide the difference of the lower value and upper value on the falling edge by the corresponding time')
    waveform_area         = measurement(name='waveform_area',        command='MAR',  unit='Volt Seconds',  return_type='float', description='algebraic sum of the area of the whole waveform within the screen. area of the waveform above the zero reference is positive and the area of the waveform below the zero reference is negative')
    first_period_area     = measurement(name='first_period_area',    command='MPAR', unit='Volt Seconds',  return_type='float', description='algebraic sum of the area of the first period of the waveform on the screen. area of the waveform above the zero reference is positive and the area of the waveform below the zero reference is negative')

    single_measurement_list = [max_voltage,         min_voltage,           peak_to_peak_voltage,  top_voltage,           base_voltage,          top_to_base_voltage,
                               average_voltage,     rms_voltage,           upper_voltage,         mid_voltage,           lower_voltage,         overshoot_voltage,
                               preshoot_voltage,    variance_voltage,      period_rms_voltage,    period_time,           frequency,             rise_time,
                               fall_time,           positive_width_time,   negative_width_time,   positive_duty_percent, negative_duty_percent, max_voltage_time,
                               min_voltage_time,    positive_pulse_number, negative_pulse_number, positive_edges_number, negative_edges_number, positive_slew_rate,
                               negative_slew_rate,  waveform_area,         first_period_area]

    double_measurement_list = [rising_phase_ratio, falling_phase_ratio, rising_delay_time, falling_delay_time]

    def powerise10(self, x):
        """ Returns x as a*10**b with 0 <= a < 10"""
        if x == 0: return 0,0
        Neg = x < 0
        if Neg: x = -x
        a = 1.0 * x / 10**(floor(log10(x)))
        b = int(floor(log10(x)))
        if Neg: a = -a
        return a,b
    
    def eng_notation(self, x):
        """Return a string representing x in an engineer friendly notation"""
        a,b = self.powerise10(x)
        if -3 < b < 3: return "%.4g" % x
        a = a * 10**(b % 3)
        b = b - b % 3
        return "%.4gE%s" % (a,b)

    def get_measurement(self, channel=1, meas_type=max_voltage):
        self.inst.write(':MEAS:ITEM? ' + meas_type.command + ',CHAN' + str(channel))
        fullreading = self.inst.read_raw()
        readinglines = fullreading.splitlines()
        if (meas_type.return_type == 'float'):
            reading = float(readinglines[0])
            if (meas_type.unit == '%%'):
                percentage_reading = reading*100
                #print ("Channel " + str(channel) + " " + meas_type.name + " value is %0.2F " + meas_type.unit) % percentage_reading
                #print('Channel {0} {1} value is {2} {3}'.format(channel, meas_type.name, meas_type.unit, percentage_reading))
            else:
                eng_reading = self.eng_notation(reading)
                #print ("Channel " + str(channel) + " " + meas_type.name + " value is " + eng_reading + " " + meas_type.unit)
        elif (meas_type.return_type == 'int'):
            reading = int(float(readinglines[0]))
            #print ("Channel " + str(channel) + " " + meas_type.name + " value is %d " + meas_type.unit) % reading
            #print('Channel {} {} value is {:d} {}'.format(channel, meas_type.name, reading, meas_type.unit))
        else:
            reading = str(readinglines[0])
            #print ("Channel " + str(channel) + " " + meas_type.name + " value is " + reading + " " + meas_type.unit)
        return reading
    
    # if no filename is provided, the timestamp will be the filename
    def write_screen_capture(self, filename=''):
        self.inst.write(':DISP:DATA? ON,OFF,PNG')
        raw_data = self.inst.read_raw()[2+9:]
        # save image file
        if (filename == ''):
            filename = "rigol_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +".png"
        fid = open(filename, 'wb')
        fid.write(raw_data)
        fid.close()
        print ("Wrote screen capture to filename " + '\"' + filename + '\"')
        #time.sleep(5)
        
    def getImage(self):
        self.inst.write(':DISP:DATA? ON,OFF,PNG')
        return self.inst.read_raw()[2+9:]
    # probe should either be 10.0 or 1.0, per the setting on the physical probe
    def setup_channel(self, channel=1, on=1, offset_divs=0.0, volts_per_div=1.0, probe=10.0):
        if (on == 1):
            self.inst.write(':CHAN' + str(channel) + ':DISP ' + 'ON')
            self.inst.write(':CHAN' + str(channel) + ':SCAL ' + str(volts_per_div))
            self.inst.write(':CHAN' + str(channel) + ':OFFS ' + str(offset_divs*volts_per_div))
            self.inst.write(':CHAN' + str(channel) + ':PROB ' + str(probe))
            print ("Turned on CH" + str(channel) + ", position is " + str(offset_divs) + " divisions from center, " + str(volts_per_div) + " volts/div, scope is " + str(probe) + "x")
        else:
            self.inst.write(':CHAN' + str(channel) + ':DISP OFF')
            print ("Turned off channel " + str(channel))
    
    def val_and_unit_to_real_val(self, val_with_unit='1s'):
        number = int(re.search(r"([0-9]+)",val_with_unit).group(0))
        unit = re.search(r"([a-z]+)",val_with_unit).group(0).lower()
        if (unit == 's' or unit == 'v'):
            real_val_no_units = number
        elif (unit == 'ms' or unit == 'mv'):
            real_val_no_units = number * 0.001
        elif (unit == 'us' or unit == 'uv'):
            real_val_no_units = number * 0.000001
        elif (unit == 'ns' or unit == 'nv'):
            real_val_no_units = number * 0.000000001
        else:
            real_val_no_units = number
        return real_val_no_units

    # remember to always use lowercase time_per_div units, the regex look for lowercase
    def setup_timebase(self, time_per_div='1ms', delay='1ms'):
        time_per_div_real = self.val_and_unit_to_real_val(time_per_div)
        self.inst.write(':TIM:MAIN:SCAL ' + str(time_per_div_real))
        print ("Timebase was set to " + time_per_div + " per division")
        delay_real = self.val_and_unit_to_real_val(delay)
        self.inst.write(':TIM:MAIN:OFFS ' + str(delay_real))
    
    # remember to always use lowercase level units, the regex look for lowercase
    def setup_trigger(self, channel=1, slope_pos=1, level='100mv'):
        level_real = self.val_and_unit_to_real_val(level)
        self.inst.write(':TRIG:EDG:SOUR CHAN' + str(channel))
        if (slope_pos == 0):
            self.inst.write(':TRIG:EDG:SLOP NEG')
        else:
            self.inst.write(':TRIG:EDG:SLOP POS')
        self.inst.write(':TRIG:EDG:LEV ' + str(level_real))
        if (slope_pos == 1):
            print ("Triggering on CH" + str(channel) + " positive edge with level of " + level)
        else:
            print ("Triggering on CH" + str(channel) + " negative edge with level of " + level)
    
    # decode channel is either 1 or 2, only two decodes can be present at any time
    # use uppercase for encoding, valid choices are HEX, ASC, DEC, BIN, LINE
    # position_divs is the number of division (from bottom) to position the decode
    def setup_i2c_decode(self, decode_channel=1, on=1, sda_channel=1, scl_channel=2, encoding='HEX', position_divs=1.0):
        if (on == 0):
            self.inst.write(':DEC' + str(decode_channel) + ':CONF:LINE OFF')
        else:
            self.inst.write(':DEC' + str(decode_channel) + ':MODE IIC')
            self.inst.write(':DEC' + str(decode_channel) + ':DISP ON')
            self.inst.write(':DEC' + str(decode_channel) + ':FORM ' + encoding)
            self.inst.write(':DEC' + str(decode_channel) + ':POS ' + str(400-position_divs*50))
            self.inst.write(':DEC' + str(decode_channel) + ':THRE AUTO')
            self.inst.write(':DEC' + str(decode_channel) + ':CONF:LINE ON')
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:CLK CHAN' + str(scl_channel))
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:DATA CHAN' + str(sda_channel))
            self.inst.write(':DEC' + str(decode_channel) + ':IIC:ADDR RW')

    def single_trigger(self):
        self.inst.write(':TRIG:SWE SING')
        #time.sleep(5)
        
    def repeat_trigger(self):
        self.inst.write(':TRIG:SWE NORM')
        
    # only allowed values are 6e3, 6e4, 6e5, 6e6, 12e6 for single channels
    # only allowed values are 6e3, 6e4, 6e5, 6e6, 12e6 for   dual channels
    # only allowed values are 3e3, 3e4, 3e5, 3e6, 6e6  for 3 or 4 channels
    # the int conversion is needed for scientific notation values
    def setup_mem_depth(self, memory_depth=12e6):
        self.inst.write(':ACQ:MDEP ' + str(int(memory_depth)))
        print ("Acquire memory depth set to %d samples" % memory_depth)

    def write_waveform_data(self, channel=1, filename=''):
        self.inst.write(':WAV:SOUR: CHAN' + str(channel))
        time.sleep(1)
        self.inst.write(':WAV:MODE NORM')
        self.inst.write(':WAV:FORM ASC')
        self.inst.write(':ACQ:MDEP?')
        fullreading = self.inst.read_raw()
        readinglines = fullreading.splitlines()
        mdepth = int(readinglines[0])
        num_reads = int((mdepth / 15625) +1)
        if (filename == ''):
            filename = "rigol_waveform_data_channel_" + str(channel) + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") +".csv"
        #fid = open(filename, 'wb')
        fid = open(filename, 'w')
        print ("Started saving waveform data for channel " + str(channel) + " " + str(mdepth) + " samples to filename " + '\"' + filename + '\"')
        for read_loop in range(0,num_reads):
            self.inst.write(':WAV:DATA?')
            fullreading = self.inst.read_raw()
            readinglines = fullreading.splitlines()
            reading = str(readinglines[0])
            reading = reading.replace(",", "\n")
            fid.write(reading)
        fid.close()
    

    def capture(self):
        '''
        same thing more or less as write_waveform_data, but doesn't write to disk. 
        Returns a dataframe. 
        '''
        chanList = self.getActiveChannels()  
        self.write('WAV:MODE NORM')
        self.write('WAV:FORM BYTE')
        
        
        #memdepth = int(self.query('ACQuire:MDepth?'))
        memdepth = int(1200)
        
        max_read = 250000
        num_reads = ceil(memdepth / max_read)
        data = pd.DataFrame(data=np.zeros((memdepth,len(chanList))),columns = chanList)
        for channel in chanList:
            self.write('WAV:SOUR {}'.format(channel))
            params = self.query('WAV:PRE?').split(',')
            form = params[0]
            typ = params[1]
            x_num = int(params[2])
            x_incr = float(params[4])
            x_origin = float(params[5])
            y_increment = float(params[7])
            y_origin = float(params[8])
            y_ref = float(params[9])
            ser = pd.Series()
            for i in range(num_reads):
                start = max_read*i + 1 #1, 250,001, 500,001, ...
                if i == num_reads - 1:
                    stop = memdepth
                else:
                    stop = start + max_read - 1 #250,000, 500,000, 750,000, ...
                self.write('WAVeform:STARt {}'.format(start))
                self.write('WAVeform:STOP {}'.format(stop))
                chunk = self.inst.query_binary_values(':WAV:DATA?', datatype='B')
                scaled_data_y = [(y-y_origin-y_ref)*y_increment for y in chunk]
                ser = ser.append(pd.Series(scaled_data_y))
            data[channel][:] = ser[:]
        data['time'] = [x * x_incr for x in range(x_num)] #x_num same as memdepth? 
        return data
    
    def getActiveChannels(self):
        chanList = []
        for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH"]:
            response = self.query(channel + ":DISP?")
            # If channel is active
            if response == '1':
                chanList += [channel]
        return chanList
    def fullCapture(self):
        chanList = self.getActiveChannels()  
        self.write('WAV:MODE MAX')
        self.write('WAV:FORM BYTE')
        val = self.query('ACQuire:MDepth?')
        try:
            memdepth = int(val)
        except ValueError:
            srate = float(self.query('ACQuire:SRATe?'))
            tscale= float(self.query('TIMebase:SCALe?'))
            memdepth = int(srate*12*tscale)
        max_read = 250000
        num_reads = ceil(memdepth / max_read)
        data = pd.DataFrame(data=np.zeros((memdepth,len(chanList))),columns = chanList)
        self.write('STOP')
        for channel in chanList:
            
            self.write('WAV:SOUR {}'.format(channel))
            params = self.query('WAV:PRE?').split(',')
            form = params[0]
            typ = params[1]
            x_num = int(params[2])
            x_incr = float(params[4])
            x_origin = float(params[5])
            y_increment = float(params[7])
            y_origin = float(params[8])
            y_ref = float(params[9])
            ser = pd.Series()
            for i in range(num_reads):
                start = max_read*i + 1 #1, 250,001, 500,001, ...
                if i == num_reads - 1:
                    stop = memdepth
                else:
                    stop = start + max_read - 1 #250,000, 500,000, 750,000, ...
                self.write('WAVeform:STARt {}'.format(start))
                self.write('WAVeform:STOP {}'.format(stop))
                chunk = self.inst.query_binary_values(':WAV:DATA?', datatype='B')
                scaled_data_y = [(y-y_origin-y_ref)*y_increment for y in chunk]
                ser = ser.append(pd.Series(scaled_data_y))
            data[channel][:] = ser[:]
        data['time'] = [x * x_incr for x in range(x_num)] #x_num same as memdepth? 
        
        return data

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    tup =  rm.list_resources()
    ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z')

    for resource_id in tup :
        try:
            
            inst = rm.open_resource(resource_id, send_end=True )
            name_str = inst.query('*IDN?').strip()
            #print(name_str)
            #print('resource_id: {}'.format(resource_id))
            if ScopePattern.match(name_str) is not None:
                scope = rigol_ds1054z(inst)
                print(name_str)
        except pyvisa.errors.VisaIOError:
            pass