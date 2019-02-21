# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 10:16:36 2019

@author: Erik
"""
import time
from PWRTestIO import *
import numpy as np
from pwr_board_test_class import quantity
import pandas as pd
from datetime import datetime
#from PWR_Test_GUI import MyApp
from PyQt5.QtCore import  QObject, pyqtSignal, pyqtSlot
class Tester(QObject):
    #finished = pyqtSignal()
    resultReady = pyqtSignal(tuple)
    status = pyqtSignal(str)
    
    '''
    the result tuple is sent to the GUI for update. 
    The form is: (row, value)
    '''
    
    def __init__(self, myResources):
        super().__init__()
        self.currentDUTSerialNumber = None
        self.myResources = myResources
        self.currentTest = 0
        self.data = None
        return
    
    @pyqtSlot(str)
    def takeConfigFilePath(self, string):
        self.ConfigFilePath = string
        
        '''
        The quanitity objects allow a convenient way to capture a signal name, 
        a channel assignment, any scale or offset, and a measure() function. 
        '''

        self.data = pd.read_excel(self.ConfigFilePath, 'Report')
        self.quantity_df = pd.read_excel(self.ConfigFilePath, 'Quantities')
        self.quantities = {}
        for row in self.quantity_df.iterrows():
            ser = row[1] #(index, Series) comes from iterrows()
            column_names = ser.index.tolist()
            my_dict = {}
            for column_name in column_names:
                my_dict[column_name] = ser[column_name]
            new_quantity = quantity(my_dict)
            self.quantities[new_quantity.getStringName()] = new_quantity
        return
    @pyqtSlot()
    def stopTest(self):
        
        return
    
    @pyqtSlot()
    def startTest(self):
        #loads 1-3 on 385-0046 Rev B are each 10 ohm. 24^2/10 = 57.6W
        load1_off(self.myResources.daq)
        load2_off(self.myResources.daq)
        load3_off(self.myResources.daq)
        flyback_off(self.myResources.daq)
        buck_off(self.myResources.daq)
        self.status.emit('Starting Test!')
        
        self.currentRow = 0
        #try:
            
        #self.runtest1()
        self.status.emit('Test 2 underway!')
        self.runtest2()
        self.runtest3()
        self.runtest4()
        self.runtest5()
        self.runtest6()
        self.runtest7()
        
        self.runtest8()
       
        '''tests 9-14 test HV Diodes, so do some set up common to all'''
        self.status.emit('Setting up for HV Diode tests')
        self.myResources.hv_supply.set_rising_voltage_slew(50) #50V/sec
        self.myResources.hv_supply.set_output_mode(2) #slew rate priority (ramp slowly)
        self.myResources.hv_supply.apply(840, 10e-3)
        
        #self.runtest9() #HV diode test
        self.runtest10()#HV diode test
        self.runtest11()#HV diode test
        self.runtest12()#HV diode test
        self.runtest13()#HV diode test
        self.runtest14()#HV diode test
        '''
        Undo the setup from HV Diode checks:
        (the power supply is already off)
        '''
        self.myResources.hv_supply.apply(0,0)
        self.myResources.hv_supply.set_output_mode(0) #high speed priority on Vout
     
        
        self.runtest15()
        self.runtest16()
        self.runtest17()
        self.runtest18()
        '''
        Dishcharge the caps using the beefy MOSFET on the interface board:
        '''
        self.status.emit('Discharging Caps')
        discharge_caps(2.3, self.quantities['HVCAP'], self.quantities['BuckCurrent'],
                       self.myResources.daq)
        cap_voltage = self.quantities['HVCAP'].measure(self.myResources.daq)
        self.status.emit('Cap Voltage: {:.2f}V'.format(cap_voltage))
        time.sleep(2)
        self.runtest19()
        self.runtest20()
        self.runtest21()
         
        '''
        Dishcharge the caps using the beefy MOSFET on the interface board:
        '''
        self.status.emit('Discharging Caps')
        time.sleep(3)
        discharge_caps(2.3, self.quantities['HVCAP'], self.quantities['BuckCurrent'],
                       self.myResources.daq)
        cap_voltage = self.quantities['HVCAP'].measure(self.myResources.daq)
        self.status.emit('Cap Voltage: {:.2f}V'.format(cap_voltage))
        time.sleep(3)
        self.status.emit('Done all the tests!')
        return

    '''
    For the threshold tests, it is useful to know the min and max acceptable values,
    because the test can be slow if sweeping a large range and stepping small. 
    Unfortunately, the data exists in two places, but is only read from for convienence 
    here. 
    '''
    def getMinimum(self, row):
        return self.data.iloc[row, self.getColumnNumber('MIN')]
    def getMaximum(self, row):
        return self.data.iloc[row, self.getColumnNumber('MAX')]
    def getColumnNumber(self, string):
        '''
        Given a string that identifies a label/column, 
        return the location of that label/column.
        This enables the config file columns to be moved around. 
        '''
        return self.data.columns.get_loc(string)
    def runtest1(self):
        row = 0
        close_rl5(self.myResources.daq)
        time.sleep(0.1)
        self.myResources.lv_supply.apply(0,.1)
        self.myResources.lv_supply.set_output('ON')
        startVoltage = self.getMinimum(row)
        stopVoltage = self.getMaximum(row)
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if .99*_input < output < 1.01*_input:
                #self.updateModel(row, _input)
                self.resultReady.emit((row, output))
                return
        self.resultReady.emit((row, np.nan))
        return
    
   
        
    def runtest2(self):
        self.resultReady.emit((1, 123234))
        return

    def runtest3(self):
        self.resultReady.emit((2,55545))
        return
            
    def runtest4(self):
        return
    def runtest5(self):
        return
    def runtest6(self):
        return
    def runtest7(self):
        return
     
    def runtest8(self):
        return
    def runtest9(self):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 9!')
        row = 8
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        open_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 9: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                print('current_limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest10(self):
        return
    def runtest11(self):
        return
    def runtest12(self):
        return
    def runtest13(self):
        return
    def runtest14(self):
        return
                        
    def runtest15(self):
        '''
        Read all channels to verify no power state.
        The setup is already done with SetupNoPowerState()
        Perform the scan and read all channels. 
        
        '''
        load1_on(self.myResources.daq)
        self.status.emit('Running Test 15')
        time.sleep(1)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        start_row = 14
        end_row = 27
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)
        self.status.emit('Test 15 Complete')
            
        return
    
   
    def runtest16(self):
        '''
        Test the HV Cap charging time. Scan list is:
            24Vout - the Flyback Vin
            HVCap  - the Flyback Vout
            TP2B   - Isolated 24V that powers buck circuitry
        Passing criteria for HVCap looks at dV/dt = 2V/sec
        Test 17 checks final charge level, not this test. 
        Load1 is ON still. 
        For now, I happen to know that 
        row 29 - 24Vout
        row 30 - HVCap
        row 31 - TP2B
        '''
        #row = 29
        running_values = np.arange(0,20,1, dtype=float)
        flyback_on(self.myResources.daq)
        buck_off(self.myResources.daq)
        self.myResources.lv_supply.apply(24, 3)
        alist = [self.quantities['24Vout'], self.quantities['HVCAP'], self.quantities['TP2B']]
        self.myResources.daq.setQuantityScan(alist)
        self.myResources.daq.format_reading() 
        
        start = datetime.now()
        self.myResources.lv_supply.set_output('ON')
        
        while True:
            data = self.myResources.daq.read()
            TP2B = data[2]
            Vin = data[0]
            #some time saving checks:
            if Vin < self.getMinimum(29):
                self.status.emit('Flyback Vin is out of spec!')
                self.resultReady.emit((29, Vin))
                break
            if TP2B < self.getMinimum(31):
                self.status.emit('HV Buck Bootstrap out of spec!')
                self.resultReady.emit((31, TP2B))
                break
            if (datetime.now() - start).seconds > 170:
                self.status.emit('Timeout condition on cap charging')
                break
            #update the running values of HV Cap voltages
            running_values[:-1] = running_values[1:]
            running_values[-1] = data[1]
            settled = (np.diff(running_values) < .5).all()
            if settled:
                self.status.emit('HV Cap has settled')
                stop = datetime.now()
                time.sleep(2)
                self.resultReady.emit((29, Vin))
                self.resultReady.emit((30, data[1]/(stop-start).seconds))
                self.resultReady.emit((31, TP2B))
                break
            else:
                self.status.emit('HV Cap still charging: {:.1f}V'.format(data[1]))
                time.sleep(2)
        self.status.emit('Test 16 Complete')
        time.sleep(1)
        return
    def runtest17(self):
        '''
        A single scan to check the normal operation state. 
        Rows 32-45 inclusive. 
        PSUA is still on. 
        Load1 is ON Still, turn on the other loads too.
        Turn on the DC Bus, and allow the buck to be on, even though
        it should be off in normal operation state. 
        '''
        self.status.emit('Test 17 Commencing')
        load2_on(self.myResources.daq)
        load3_on(self.myResources.daq)
        buck_on(self.myResources.daq)
        self.myResources.hv_supply.apply(800, 1)
        self.myResources.hv_supply.set_output('ON')
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        start_row = 32
        end_row = 45
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)
        self.status.emit('Test 17 Complete')
        time.sleep(1)
        return
    
    def runtest18(self):
        '''
        Test SPM mode from Normal Operation State. 
        PSUA goes off, and the DUT transitions to SPM state. 
        A single scan on all channels, plus a calculation for
        the HV Buck efficiency. 
        Rows 46-60 inclusive.
        The scan list does not need to be changed from before.
        The buck is still allowed to be ON. 
        All 3 loads are still ON. 
        '''
        start_row = 46
        end_row = 60
        self.status.emit('Test 18: SPM Mode Starting')
        self.myResources.lv_supply.set_output('OFF')
        time.sleep(5)
        data = self.myResources.daq.read()
        #calculate buck efficiency:
        Vin = self.myResources.hv_supply.get_voltage()
        Vout = data[10]
        Iin = self.myResources.hv_supply.get_current()
        Iout = data[13]
        try:
            data.append((Vout*Iout)/(Vin*Iin))
        except ZeroDivisionError:#DivisionByZero:
            data.append(0)
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)   
        self.status.emit('Test 18 Complete')
        self.myResources.hv_supply.set_output('OFF')
        return
    
    def runtest19(self):
        '''
        Another NoPowerState check
        '''
        load1_off(self.myResources.daq)
        load2_on(self.myResources.daq)
        load3_on(self.myResources.daq)
        self.status.emit('Running Test 19')
        time.sleep(1)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        start_row = 61
        end_row = 74
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)
        self.status.emit('Test 19 Complete')
        return
    def runtest20(self):
        '''
        Test the bootstrap function of the HV Buck. 
        row 75: HVCAP dV/dt
        row 76: TP5B, HVBuck dV/dt (the results in rows 75,76 wil be the same
        since the HV buck output is pinned to the caps via diode)
        row 77: TP1B, DCBus
        row 78: TP6B, 16V
        row 79: TP2B, Bootstrap
        '''
        self.myResources.hv_supply.apply(290, 1.44)
        alist = [self.quantities['HVCAP'], self.quantities['TP5B'],
                 self.quantities['TP1B'], self.quantities['TP6B'],
                 self.quantities['TP2B']]
        self.myResources.daq.setQuantityScan(alist)
        start = datetime.now()
        self.myResources.hv_supply.set_output('ON')
        while True:
            data = self.myResources.daq.read()
            TP2B = data[4]
            TP6B = data[3]
            
            #some time saving checks:
            if self.getMaximum(78) < TP6B < self.getMinimum(78):
                self.status.emit('16V rail is out of spec!')
                self.resultReady.emit((78, TP6B))
                break
            if TP2B < self.getMinimum(79):
                self.status.emit('HV Buck Bootstrap out of spec!')
                self.resultReady.emit((79, TP2B))
                break
            if (datetime.now() - start).seconds > 20:
                self.status.emit('Timeout condition on cap charging')
                break
            #update the running values of Buck output voltages
            running_values[:-1] = running_values[1:]
            running_values[-1] = data[1]
            settled = (np.diff(running_values) < .5).all()
            if settled:
                self.status.emit('Buck has charged the caps')
                stop = datetime.now()
                self.resultReady.emit((75, data[0]/(stop-start).seconds))
                self.resultReady.emit((76, data[1]/(stop-start).seconds))
                self.resultReady.emit((77, data[2]))
                self.resultReady.emit((78, TP6B))
                self.resultReady.emit((79, TP2B))
                break
            else:
                self.status.emit('HV Cap still charging: {:.1f}V'.format(data[0]))
                time.sleep(.3)
        return
    
    def runtest21(self):
        '''
        Test SPM mode from Bootstrap state. 
        PSUA is already OFF, and the DUT is in SPM mode already. 
        A single scan on all channels, plus a calculation for
        the HV Buck efficiency. 
        Rows 80-94 inclusive.
        The scan list does not need to be changed from before.
        The buck is still allowed to be ON. 
        All 3 loads are still ON. 
        '''
        start_row = 80
        end_row = 93
        self.status.emit('Test 21: SPM Mode from Bootstrap state')
        #self.myResources.lv_supply.set_output('OFF')
        #time.sleep(5)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        data = self.myResources.daq.read()
        #calculate buck efficiency:
        Vin = self.myResources.hv_supply.get_voltage()
        Vout = data[10]
        Iin = self.myResources.hv_supply.get_current()
        Iout = data[13]
        try:
            data.append((Vout*Iout)/(Vin*Iin))
        except ZeroDivisionError:
            data.append(0)
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)   
        self.status.emit('Test 21 Complete')
        self.myResources.hv_supply.set_output('OFF')
        return
        
        
    
    