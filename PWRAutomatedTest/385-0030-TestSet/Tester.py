# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 10:16:36 2019

@author: Erik
@updates by Ivan
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
                              13:self.runtest13, 14:self.runtest14, 15:self.runtest15,
                              16:self.runtest16, 17:self.runtest17, 18:self.runtest18,
                              19:self.runtest19, 20:self.runtest20, 21:self.runtest21}
        return
    
    @pyqtSlot()
    def listenForStop(self):
        self.continueTest= False
        self.status.emit('Stopping Test')
        #print('heard that stop request:'.format(self.continueTest))
        return
    
    def functionMapper(self, testNumber):
        return self.testFunctions.get(testNumber, self.runtestError)
    
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
            close_rl5(self.myResources.daq)#need to enable PSUA so not to turn on SPM mode
            
            load1_off(self.myResources.daq)
            load2_off(self.myResources.daq)
            load3_off(self.myResources.daq)
            buck_off(self.myResources.daq)
            flyback_off(self.myResources.daq)
            self.myResources.hv_supply.set_rising_voltage_slew(100) #50V/sec
            self.myResources.hv_supply.set_output_mode(2) #slew rate priority (ramp slowly)
            self.myResources.hv_supply.apply(840, 100e-3)
            self.myResources.lv_supply.apply(24.0, 1)#turn on PSUA
            self.myResources.lv_supply.set_output('ON')
            time.sleep(3)

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
                #self.myResources.lv_supply.apply(0,0.2) #discharge PSUA caps (still work in progress), trying to prevent issue where PSUA and PSUB LEDs ON at same time
                self.myResources.hv_supply.apply(0,0)
                self.myResources.lv_supply.apply(0,0)                
                open_rl5(self.myResources.daq)
                time.sleep(3)
        elif 'Caps Charging' in test['TEST DESCRIPTION'].iloc[0]: 
            load1_off(self.myResources.daq)
            load2_off(self.myResources.daq)
            load3_off(self.myResources.daq)
            close_rl5(self.myResources.daq)
           
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
        self.continueTest=True
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
        #IM 3/21/19 - Setting HV/LV supplies down to 0V as a safety precaution
        self.myResources.hv_supply.apply(0,0)
        self.myResources.hv_supply.set_output_mode(0)
        self.myResources.lv_supply.apply(0,0)

        '''
        Discharge the caps using the beefy MOSFET on the interface board:
        '''
        self.status.emit('Discharging Caps')
        self.dischargeCaps()
        self.status.emit('Done all the tests!')
        
        return

    '''
    For the threshold tests, it is useful to know the min and max acceptable values,
    because the test can be slow if sweeping a large range and stepping small. 
    Unfortunately, the data exists in two places, but is only read from for convienence 
    here.  NOTE: IM 3/26/2019 data dataframe produces error, found better method test[test['NAME']== thing ['MIN'].iloc[0]
    '''
    #def getMinimum(self, row):
        #return self.data.iloc[row, self.getColumnNumber('MIN')]
    #def getMaximum(self, row):
        #return self.data.iloc[row, self.getColumnNumber('MAX')]
    
    def dischargeCaps(self): #IM 3/26/19 - Adding fail state power down event
        #self.continueTest= False # for fail state powerdown events
        self.myResources.hv_supply.apply(0,0)
        self.myResources.lv_supply.apply(0,0)
        self.status.emit('Discharging Caps')
        discharge_caps(2.3, self.quantities['HVCAP'], self.quantities['BuckCurrent'],
                       self.myResources.daq)
        cap_voltage = self.quantities['HVCAP'].measure(self.myResources.daq)
        self.status.emit('Cap Voltage: {:.2f}V'.format(cap_voltage))
        time.sleep(3)
        return
    
    def getColumnNumber(self, string):
        '''
        Given a string that identifies a label/column, 
        return the location of that label/column.
        This enables the config file columns to be moved around. 
        '''
        return self.data.columns.get_loc(string)
    def getRow(self, test):
        return test['TEST #'].iloc[0].astype(int)-1
    def runtestError(self, test):
        '''
        Catch all failure test
        '''
        self.status.emit('Invalid Tests selected')
        time.sleep(3) 
        
        return  
    def runtest1(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUA UVLO Rising
        '''
        self.status.emit('Running Test 1: PSUA UVLO Rising')
        row = self.getRow(test)
        self.myResources.lv_supply.apply(10,1)
        self.myResources.lv_supply.set_output('ON')
        #first check at 10V to see if there is a shorted inner diode
        output = self.quantities['24Vout'].measure(self.myResources.daq)
        _input = self.quantities['PSUA'].measure(self.myResources.daq)
        if .99*_input < output < 1.01*_input:
            self.resultReady.emit((row, output))
            self.status.emit('Failed Test 1: Shorted Inner Diode-PMOS')
            self.myResources.lv_supply.set_output('OFF') 
            time.sleep(2)
            self.continueTest= False
            self.resultReady.emit((row, -99))
            self.dischargeCaps() #if fails, discharges caps
            return        
        startVoltage = test['MIN'].iloc[0]-.3 #self.getMinimum(row)
        stopVoltage = test['MAX'].iloc[0]#self.getMaximum(row)
        self.status.emit('Running Test 1: Voltage Ramp')
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1) 
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if .99*_input < output < 1.01*_input:
                #self.updateModel(row, _input)
                self.resultReady.emit((row, output))
                self.myResources.lv_supply.set_output('OFF') #added to turn off PS after test has completed
                self.status.emit('Test 1: PSUA UVLO Rising - PASS')                
                return 
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 1: PSUA UVLO Rising - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
        #in the future, will need to make a way to read flags
        #to see if test 2 is enable to stop need from turning off PS for safety.
        #This would help with reducing Test Time
    def runtest2(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUA UVLO Falling
        '''
        self.status.emit('Running Test 2: PSUA UVLO Falling')
        row = self.getRow(test)

        stopVoltage = test['MIN'].iloc[0] 
        startVoltage = test['MAX'].iloc[0]
        self.myResources.lv_supply.apply(startVoltage+.3, 1)
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 2: Voltage Ramp')
        for i in np.arange(startVoltage+.3, stopVoltage, -.01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if  not (.99*_input < output < 1.01*_input): #checks if PMOS is OFF
                #self.updateModel(row, _input)
                self.resultReady.emit((row, _input)) #read the input after PMOS is OFF
                self.myResources.lv_supply.set_output('OFF')
                self.status.emit('Test 2: PSUA UVLO Falling - PASS')
                return
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 2: PSUA UVLO Falling - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return

    def runtest3(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe.  
        
        Test PSUA OVLO Rising
        '''
        self.status.emit('Running Test 3: PSUA OVLO Rising')
        row = self.getRow(test)
        self.myResources.lv_supply.apply(10,1)
        self.myResources.lv_supply.set_output('ON')
        
        #first check at 10V to see if there is a shorted inner diode (sanity check)
        output = self.quantities['24Vout'].measure(self.myResources.daq)
        _input = self.quantities['PSUA'].measure(self.myResources.daq)
        if .99*_input < output < 1.01*_input:
            self.resultReady.emit((row, output))
            self.status.emit('Failed Test 3: Shorted Inner Diode-PMOS')
            self.myResources.lv_supply.set_output('OFF') 
            time.sleep(2)
            self.resultReady.emit((row, -99))
            self.continueTest= False
            self.dischargeCaps() #if fails, discharges caps
            return

        startVoltage = test['MIN'].iloc[0]-.3 #self.getMinimum(row)
        stopVoltage = test['MAX'].iloc[0]#self.getMaximum(row)

        self.myResources.lv_supply.apply(startVoltage, 1) #boot up to allow PMOS to be ON
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 3: Voltage Ramp')
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1) 
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if not(.99*_input < output < 1.01*_input): #we want to see PMOS turn off
                #self.updateModel(row, _input)
                self.resultReady.emit((row, _input))
                self.myResources.lv_supply.set_output('OFF') 
                self.status.emit('Test 3: PSUA OVLO Rising - PASS')
                return 
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 3: PSUA OVLO Rising - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
            
    def runtest4(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUA OVLO Falling
        '''
        self.status.emit('Running Test 4: PSUA OVLO Falling')
        row = self.getRow(test)

        stopVoltage = test['MIN'].iloc[0] 
        startVoltage = test['MAX'].iloc[0]
        self.myResources.lv_supply.apply(startVoltage+.3, 1)
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 4: Voltage Ramp down')
        for i in np.arange(startVoltage+.3, stopVoltage, -.01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if  .99*_input < output < 1.01*_input: #checks if PMOS is ON
                #self.updateModel(row, _input)
                self.resultReady.emit((row, output)) 
                self.myResources.lv_supply.set_output('OFF')
                self.status.emit('Test 4: PSUA OVLO Falling - PASS')
                
                time.sleep(1)
                return
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 4: PSUA OVLO Falling - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
    def runtest5(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUB UVLO Rising
        '''
        self.status.emit('Running Test 5: PSUB UVLO Rising')
        row = self.getRow(test)
        self.myResources.lv_supply.apply(10,1)
        self.myResources.lv_supply.set_output('ON')
        time.sleep(5)
        #first check at 10V to see if there is a shorted inner diode
        output = self.quantities['24Vout'].measure(self.myResources.daq)
        _input = self.quantities['PSUB'].measure(self.myResources.daq)
        if .99*_input < output < 1.01*_input:
            self.resultReady.emit((row, output))
            self.status.emit('Failed Test 5: Shorted Inner Diode-PMOS')
            self.myResources.lv_supply.set_output('OFF') 
            time.sleep(2)
            self.continueTest= False
            self.resultReady.emit((row, -99))
            self.dischargeCaps() #if fails, discharges caps
            time.sleep(1)
            return        
        startVoltage = test['MIN'].iloc[0]-.3 #self.getMinimum(row)
        stopVoltage = test['MAX'].iloc[0]#self.getMaximum(row)
        self.status.emit('Running Test 5: Voltage Ramp')
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1) 
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUB'].measure(self.myResources.daq)
            if .99*_input < output < 1.01*_input:
                #self.updateModel(row, _input)
                self.resultReady.emit((row, output))
                self.myResources.lv_supply.set_output('OFF') #added to turn off PS after test has completed
                self.status.emit('Test 5: PSUB UVLO Rising - PASS')
                return 
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 5: PSUB UVLO Rising - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
    def runtest6(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUB UVLO Falling
        '''
        self.status.emit('Running Test 6: PSUB UVLO Falling')
        row = self.getRow(test)

        stopVoltage = test['MIN'].iloc[0] 
        startVoltage = test['MAX'].iloc[0]
        self.myResources.lv_supply.apply(startVoltage+.3, 1)
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 6: Voltage Ramp')
        for i in np.arange(startVoltage+.3, stopVoltage, -.01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUB'].measure(self.myResources.daq)
            if  not (.99*_input < output < 1.01*_input): #checks if PMOS is OFF
                #self.updateModel(row, _input)
                self.resultReady.emit((row, _input)) #read the input after PMOS is OFF
                self.myResources.lv_supply.set_output('OFF')
                self.status.emit('Test 6: PSUB UVLO Falling - PASS')
                return
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 6: PSUB UVLO Falling - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
    def runtest7(self, test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe.  
        
        Test PSUB OVLO Rising
        '''
        self.status.emit('Running Test 7: PSUB OVLO Rising')
        row = self.getRow(test)
        self.myResources.lv_supply.apply(10,1)
        self.myResources.lv_supply.set_output('ON')
        
        #first check at 10V to see if there is a shorted inner diode (sanity check)
        output = self.quantities['24Vout'].measure(self.myResources.daq)
        _input = self.quantities['PSUB'].measure(self.myResources.daq)
        if .99*_input < output < 1.01*_input:
            self.resultReady.emit((row, output))
            self.status.emit('Failed Test 7: Shorted Inner Diode-PMOS')
            self.myResources.lv_supply.set_output('OFF') 
            time.sleep(2)
            self.resultReady.emit((row, -99))
            self.continueTest= False
            self.dischargeCaps() #if fails, discharges caps
            return

        startVoltage = test['MIN'].iloc[0]-.3 #self.getMinimum(row)
        stopVoltage = test['MAX'].iloc[0]#self.getMaximum(row)

        self.myResources.lv_supply.apply(startVoltage, 1) #boot up to allow PMOS to be ON
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 7: Voltage Ramp')
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1) 
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUB'].measure(self.myResources.daq)
            if not(.99*_input < output < 1.01*_input): #we want to see PMOS turn off
                #self.updateModel(row, _input)
                self.resultReady.emit((row, _input))
                self.myResources.lv_supply.set_output('OFF') 
                self.status.emit('Test 7: PSUA OVLO Rising - PASS')
                return 
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 7: PSUA OVLO Rising - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
     
    def runtest8(self,test):
        '''
        For a threshold check, the test passed in is known
        to be a 1 row dataframe. 
        
        Test PSUB OVLO Falling
        '''
        self.status.emit('Running Test 8: PSUB OVLO Falling')
        row = self.getRow(test)

        stopVoltage = test['MIN'].iloc[0] 
        startVoltage = test['MAX'].iloc[0]
        self.myResources.lv_supply.apply(startVoltage+.3, 1)
        self.myResources.lv_supply.set_output('ON')

        time.sleep(5)
        self.status.emit('Running Test 8: Voltage Ramp down')
        for i in np.arange(startVoltage+.3, stopVoltage, -.01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUB'].measure(self.myResources.daq)
            if  .99*_input < output < 1.01*_input: #checks if PMOS is ON
                #self.updateModel(row, _input)
                self.resultReady.emit((row, output)) 
                self.myResources.lv_supply.set_output('OFF')
                self.status.emit('Test 8: PSUB OVLO Falling - PASS')
                return
        self.myResources.lv_supply.set_output('OFF')
        self.status.emit('Failed Test 8: PSUB OVLO Falling - FAIL')
        self.resultReady.emit((row, -88))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Failed Test 9: Current Limit!')
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                time.sleep(3)
                self.continueTest = False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 9: Voltage still falling')
            time.sleep(.3)
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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Failed Test 10: Current Limit!')
                time.sleep(3)
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                self.continueTest= False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 10: Voltage still falling')
            time.sleep(.3)
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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Failed Test 11: Current Limit!')
                time.sleep(3)
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                self.continueTest= False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 11: Voltage still falling')
            time.sleep(.3)
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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('Failed Test 12: Current Limit!')
                time.sleep(3)
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                self.continueTest= False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 12: Voltage still falling')
            time.sleep(.3)        

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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('FAIL Test 13: Current Limit!')
                time.sleep(3)
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                self.continueTest= False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 13: Voltage still falling')
            time.sleep(.3)
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
            if self.myResources.hv_supply.get_current_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                self.status.emit('FAIL Test 14: Current Limit!')
                time.sleep(3)
                self.resultReady.emit((row, -999)) #generic fail flag for current limit
                self.continueTest= False
                #self.dischargeCaps() #if fails, discharges caps
                break
            time.sleep(.3)
        if self.continueTest == True:
            current = self.myResources.hv_supply.get_current()
            self.resultReady.emit((row, current))
        self.myResources.hv_supply.set_output('OFF')
        while self.myResources.hv_supply.get_voltage() > 5:
            self.status.emit('Test 14: Voltage still falling')
            time.sleep(.3)  

        return     
    
    #def runtestStateMachine(self, test):
        #'''
        #Runs tests 15-21 when called upon functionMapper. Allows you to run through these tests all in one sequence rather than 
        #running each individually
        #'''
        #self.runtest15(test)
        #self.runtest19(test)
        
        #return  
                 
    def runtest15(self, test):
        '''
        Read all channels to verify no power state.
        The setup is already done with SetupNoPowerState()
        Perform the scan and read all channels. 
        
        '''     
        self.dischargeCaps() #required for discharge after test 14
        load1_on(self.myResources.daq)
        self.status.emit('Running Test 15')
        time.sleep(5)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        #start_row = 14
        #start_row = test['TEST #'].iloc[0].index
        #end_row = 27
        #end_row = test['TEST #'].iloc[-1]
        start_row=test.index[0]
        end_row=test.index[-1]
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair) 
        self.status.emit('Test 15 Complete')
        return
    
   
    def runtest16(self, test):
        '''
        Test the HV Cap charging time. Scan list is:
            24Vout - the Flyback Vin
            HVCap  - the Flyback Vout
            TP2B   - Isolated 24V that powers buck circuitry
        Passing criteria for HVCap looks at dV/dt = 2V/sec
        Test 17 checks final charge level, not this test. 
        Load1 removed #Load1 is ON still. 
        For now, I happen to know that 
        row 29 - 24Vout
        row 30 - HVCap
        row 31 - TP2B
        '''
        row = test.index[0]
        #row = 29
        running_values = np.arange(0,10,1, dtype=float)
        flyback_on(self.myResources.daq)
        buck_off(self.myResources.daq)
        self.myResources.lv_supply.apply(24, 9)
        alist = [self.quantities['24Vout'], self.quantities['HVCAP'], self.quantities['TP2B']]
        self.myResources.daq.setQuantityScan(alist)
        self.myResources.daq.format_reading() 
        
        start = datetime.now()
        self.myResources.lv_supply.set_output('ON')
        time.sleep(3)
        while True:
            data = self.myResources.daq.read()
            #TP2B = self.quantities['TP2B'].measure(self.myResources.daq)
            TP2B = data[2]
            #Vin = self.quantities['24Vout'].measure(self.myResources.daq)
            Vin = data[0]
            #some time saving checks:
            if Vin < test[test['NAME']=='24Vout']['MIN'].iloc[0]:
            #if Vin < self.getMinimum(29):
                self.status.emit('FAIL Test 16: Flyback Vin is out of spec!')
                self.resultReady.emit((row, Vin))
                #self.resultReady.emit((29, Vin))
                time.sleep(2)
                self.continueTest= False
                self.dischargeCaps() #if fails, discharges caps
                break
            if TP2B < test[test['NAME']=='TP2B']['MIN'].iloc[0]:
            #if TP2B < self.getMinimum(31):
                self.status.emit('FAIL Test 16: HV Buck Bootstrap out of spec!')
                self.resultReady.emit((row+2, TP2B))
                #self.resultReady.emit((31, TP2B))
                time.sleep(2)
                self.continueTest= False
                self.dischargeCaps() #if fails, discharges caps
                break
            if (datetime.now() - start).seconds > 300:#170:
                self.status.emit('FAIL Test 16: Timeout condition on cap charging')
                time.sleep(2)

                self.resultReady.emit((row, Vin)) #grabbing Vin, TP2B data even though fault condition occurred              
                self.resultReady.emit((row+1, -999)) #fault condition
                self.resultReady.emit((row+2, TP2B))
                self.continueTest= False
                self.dischargeCaps() #if fails, discharges caps

                break
            #update the running values of HV Cap voltages
            running_values[:-1] = running_values[1:]
            running_values[-1] = data[1]
            settled = (np.diff(running_values) < .5).all()
            if settled:
                stop = datetime.now()
                self.status.emit('Test 16: HV Cap has settled')
                self.resultReady.emit((row, Vin))
                #self.resultReady.emit((29, Vin))                
                self.resultReady.emit((row+1, data[1]/(stop-start).seconds))
                #self.resultReady.emit((30, data[1]/(stop-start).seconds))
                self.resultReady.emit((row+2, TP2B))
                #self.resultReady.emit((31, TP2B))
                break
            else:
                self.status.emit('Running Test 16: HV Cap still charging: {:.1f}V'.format(data[1]))
                time.sleep(2)
        self.status.emit('Test 16 Complete')
        time.sleep(1)
        return
    def runtest17(self, test):
        '''
        A single scan to check the normal operation state. 
        Rows 32-45 inclusive. 
        PSUA is still on. 
        Load1 is ON Still, turn on the other loads too.
        Turn on the DC Bus, and allow the buck to be on, even though
        it should be off in normal operation state. 
        '''
        self.status.emit('Test 17 Commencing')
        load1_on(self.myResources.daq)
        load2_on(self.myResources.daq)
        load3_on(self.myResources.daq)
        buck_off(self.myResources.daq) #sets up buck for SPM mode
        self.myResources.hv_supply.apply(800, 1)
        self.myResources.hv_supply.set_output('ON')
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        #start_row = 32
        #end_row = 45
        start_row=test.index[0]
        end_row=test.index[-1]
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        #for i in combined:
        #    print(i)
        #print('sleeping for 10')
        #time.sleep(10)
        for pair in combined:
            self.resultReady.emit(pair)
        self.status.emit('Test 17 Complete')
        time.sleep(1)
        return
    
    def runtest18(self, test):
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
        #start_row = 46
        #end_row = 60
        start_row=test.index[0]
        end_row=test.index[-1]
        self.status.emit('Test 18: SPM Mode Starting')
        self.myResources.lv_supply.set_output('OFF') #turns off low voltage
        time.sleep(5)
        data = self.myResources.daq.read()
        #calculate buck efficiency:
        Vin = self.myResources.hv_supply.get_voltage()
        #print('test 18:')
        #print('vin:{}'.format(Vin))
        
        Vout = data[9]
        Iin = self.myResources.hv_supply.get_current()
        Iout = data[13]
        #print('vout:{}'.format(Vout))
        #print('Iin:{}'.format(Iin))
        #print('Iout:{}'.format(Iout))
        try:
            data.append((Vout*Iout)*100/(Vin*Iin))
        except ZeroDivisionError:#DivisionByZero:
            data.append(0)
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)   
        self.status.emit('Test 18 Complete')
        self.myResources.hv_supply.set_output('OFF')
        return
    
    def runtest19(self, test):#):
        '''
        Another NoPowerState check
        '''
        self.dischargeCaps()
        load1_off(self.myResources.daq)
        load2_on(self.myResources.daq)
        load3_on(self.myResources.daq)
        
        self.status.emit('Running Test 19')
        time.sleep(10)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        #start_row = 60
        #end_row = 73
        start_row=test.index[0]
        end_row=test.index[-1]
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)
        self.status.emit('Test 19 Complete')
        return
    def runtest20(self, test):
        '''
        Test the bootstrap function of the HV Buck. 
        row 75: HVCAP dV/dt
        row 76: TP5B, HVBuck dV/dt (the results in rows 75,76 wil be the same
        since the HV buck output is pinned to the caps via diode)
        row 77: TP1B, DCBus
        row 78: TP6B, 16V
        row 79: TP2B, Bootstrap
        '''
        self.status.emit('Starting Test 20!')
        load1_off(self.myResources.daq)
        load2_off(self.myResources.daq)
        load3_off(self.myResources.daq)
        row=test.index[0]
        
        running_values = np.arange(0,10,1, dtype=float)
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
            '''
            if test[test['NAME']=='TP6B']['MAX'].iloc[0] < TP6B < test[test['NAME']=='TP6B']['MIN'].iloc[0]:
            #if self.getMaximum(78) < TP6B < self.getMinimum(78):
                self.status.emit('FAIL Test 20: 16V rail is out of spec!')
                self.resultReady.emit((row+3, TP6B))
                time.sleep(2)
                self.continueTest= False
                self.dischargeCaps()#if fails, discharges caps
                #self.resultReady.emit((78, TP6B))
                break
            
            if TP2B < test[test['NAME']=='TP2B']['MIN'].iloc[0]:
            #if TP2B < self.getMinimum(79):
                self.status.emit('FAIL Test 20: HV Buck Bootstrap out of spec!')
                self.resultReady.emit((row+4, TP2B))
                #self.resultReady.emit((79, TP2B))
                time.sleep(2)
                self.continueTest= False
                self.dischargeCaps()#if fails, discharges caps
                break
            '''
            if (datetime.now() - start).seconds > 25:
                self.status.emit('FAIL Test 20: Timeout condition on cap charging')
                time.sleep(2)
                self.continueTest= False
                self.dischargeCaps()#if fails, discharges caps
                break
            #update the running values of Buck output voltages
            running_values[:-1] = running_values[1:]
            running_values[-1] = data[1]
            settled = (np.diff(running_values) < .5).all()
            if settled:
                self.status.emit('Test 20: Buck has charged the caps')
                stop = datetime.now()
                self.resultReady.emit((row, data[0]/(stop-start).seconds))
                self.resultReady.emit((row+1, data[1]/(stop-start).seconds))
                self.resultReady.emit((row+2, data[2]))
                self.resultReady.emit((row+3, TP6B))
                self.resultReady.emit((row+4, TP2B))
                break
            else:
                self.status.emit('Running Test 20: HV Cap still charging: {:.1f}V'.format(data[0]))
                time.sleep(.3)
        return
    
    def runtest21(self, test):
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
        #start_row = 80
        #end_row = 93
        load1_on(self.myResources.daq)
        load2_on(self.myResources.daq)
        load3_on(self.myResources.daq)
        start_row=test.index[0]
        end_row=test.index[-1]
        self.status.emit('Test 21: SPM Mode from Bootstrap state')
        #self.myResources.lv_supply.set_output('OFF')
        #time.sleep(5)
        quantity_list = list(self.quantities.values())
        self.myResources.daq.setQuantityScan(quantity_list)
        time.sleep(3)
        data = self.myResources.daq.read()
        #calculate buck efficiency:
        Vin = self.myResources.hv_supply.get_voltage()
        Vout = data[9]
        Iin = self.myResources.hv_supply.get_current()
        Iout = data[13]
        try:
            data.append((Vout*Iout)*100/(Vin*Iin))
        except ZeroDivisionError:
            data.append(0)
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            self.resultReady.emit(pair)   
        self.status.emit('Test 21 Complete')
        self.myResources.hv_supply.set_output('OFF')
        return
        
        
    
    