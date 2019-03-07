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
from PyQt5.QtCore import  QObject, pyqtSignal, pyqtSlot
from threading import Thread

class Tester(QObject):
    #finished = pyqtSignal()
    resultReady = pyqtSignal(tuple)
    status = pyqtSignal(str)
    testDone = pyqtSignal()
    '''
    the result tuple is sent to the GUI for update. 
    The form is: (row, value)
    
    Each test the user wishes to execute is known to this class.
    One-value tests (thresholds and HV diode checks) are reported to
    this class a pandas series. 
    '''
    
    def __init__(self, myResources):
        super().__init__()
        self.myResources = myResources
        #self.testInfo = None
        self.quantity_df = None
        self.testInfo = None
        self.continueTest =True
        #the stopThread is only started when the stop button is pressed
        self.stopThread = Thread(target = self.listenForStop, name='stop')

        
        self.testFunctions = {1:self.runtest1, 2:self.runtest2, 3:self.runtest3,
                              4:self.runtest4, 5:self.runtest5, 6:self.runtest6,
                              7:self.runtest7, 8:self.runtest8, 9:self.runtest9,
                              10:self.runtest10, 11:self.runtest11, 12:self.runtest12,
                              13:self.runtest13, 14:self.runtest14}
        return
    
    @pyqtSlot()
    def listenForStop(self):
        self.continueTest= False
        self.status.emit('Stopping Test')
        #print('heard that stop request:'.format(self.continueTest))
        return
    
    def functionMapper(self, testNumber):
        return self.testFunctions.get(testNumber, self.runtest15)
    
    @pyqtSlot(list)
    def takeTestInfo(self, alist):
        #self.ConfigFilePath = string
        self.quantity_df = alist[-1]
        self.testInfo = alist[:-1]
        '''
        The quanitity objects allow a convenient way to capture a signal name, 
        a channel assignment, any scale or offset, and a measure() function. 
        '''
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
    
    def setUpForTest(self, test):
        
        if 'inputDiode' in test['NAME'].iloc[0]:
            self.status.emit('Setting up for HV Diode tests')
            self.myResources.hv_supply.set_rising_voltage_slew(50) #50V/sec
            self.myResources.hv_supply.set_output_mode(2) #slew rate priority (ramp slowly)
            self.myResources.hv_supply.apply(840, 10e-3)
            self.myResources.lv_supply.apply(0,0)
        elif 'Threshold' in test['NAME'].iloc[0]:
            self.status.emit('Setting up for threshold checks')
            load1_off(self.myResources.daq)
            load2_off(self.myResources.daq)
            load3_off(self.myResources.daq)
            flyback_off(self.myResources.daq)
            buck_off(self.myResources.daq)
            if 'PSUA' in test['TEST DESCRIPTION'].iloc[0]:
                close_rl5(self.myResources.daq)
            elif 'PSUB' in test['TEST DESCRIPTION'].iloc[0]:
                open_rl5(self.myResources.daq)
                self.myResources.hv_supply.apply(0,0)
                self.myResources.lv_supply.apply(0,0)
        else:
            self.myResources.hv_supply.apply(0,0)
            self.myResources.hv_supply.set_output_mode(0)
            
        return
    
    @pyqtSlot()
    def startTestThread(self):
        self.testThread = Thread(target=self.startTest, name='test')
        self.continueTest=True
        self.testThread.start()
        return
    
    
    def startTest(self):
        #loads 1-3 on 385-0046 Rev B are each 10 ohm. 24^2/10 = 57.6W
        #self.continueTest=True
        self.status.emit('Starting Test!')
        
        for test in self.testInfo:
            if self.continueTest:
                testNumber = test.iloc[0,0].astype(int)
                self.setUpForTest(test)
                #calling the test with the testNumber allows the 
                #resultReady() signal to know which row to use
                #get the test function first
                testFunction = self.functionMapper(testNumber)
                #call the testFunction with the starting row to write to
                #for static checks, there is only one row. 
                testFunction(test)
            else:
                return
        self.status.emit('Done the Test')
        self.testDone.emit()
       


        '''
        Dishcharge the caps using the beefy MOSFET on the interface board:
        '''
        self.status.emit('Discharging Caps')
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
    def getRow(self, test):
        return test['TEST #'].iloc[0].astype(int)-1
    def runtest1(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a Series. 
        '''
        self.status.emit('Running Test 1')
        row = self.getRow(test)
        self.myResources.lv_supply.apply(0,.1)
        self.myResources.lv_supply.set_output('ON')
        startVoltage = test['MIN'][0] #self.getMinimum(row)
        stopVoltage = test['MAX'][0]#self.getMaximum(row)
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
    
   
        
    def runtest2(self, test):
       
        return

    def runtest3(self, test):
      
        return
            
    def runtest4(self, test):
        return
    def runtest5(self, test):
        return
    def runtest6(self, test):
        return
    def runtest7(self, test):
        return
     
    def runtest8(self,test):
        return
    def runtest9(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        row = self.getRow(test)
        self.status.emit('Running Test 9!')
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        open_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 9: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest10(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 10!')
        row = self.getRow(test)
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        open_rl3(self.myResources.daq)
        close_rl4(self.myResources.daq)
        
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 10: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest11(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 11!')
        row = self.getRow(test)
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        close_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 11: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest12(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 12!')
        row = self.getRow(test)
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        close_rl3(self.myResources.daq)
        close_rl4(self.myResources.daq)
        
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 12: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest13(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 13!')
        row = self.getRow(test)
        close_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 13: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
    def runtest14(self, test):
        '''Impose 840 V on DC bus and read back current draw
        '''
        self.status.emit('Running Test 14!')
        row = self.getRow(test)
        close_rl1(self.myResources.daq)
        close_rl2(self.myResources.daq)
  
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            self.status.emit('Test 14: Voltage still climbing')
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Current Limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        return
                        
    def runtest15(self, test):
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
        
        
    
    