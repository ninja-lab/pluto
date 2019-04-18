# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 13:26:01 2019

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
from PyQt5.QtWidgets import QWidget, QApplication, QTableView, QVBoxLayout, QMessageBox, QPushButton

'''
Imported from PWR_Test_GUI
import pyvisa
from InstrumentConnections import InstrumentConnections
'''
class SelfTester2(QObject):
    resultReady = pyqtSignal(tuple)
    status = pyqtSignal(str)
    testDone = pyqtSignal()
    

    
    def __init__(self, myResources):
        super().__init__()
        self.myResources = myResources
        self.myResources.Connect()
        self.daq = self.myResources.get_daq()
        
        '''
        self.mystr = 'Test {}: Readback: {:.2f}, Input: {:.2f}, Result: {}'
        self.quantity_df = pd.read_excel('C:\\Users\\Erik\\git\\pluto\\PWRAutomatedTest\\385-0030-TestSet\\PWR_Board_TestReportTemplate2.xlsx', 'Quantities')          
        self.testInfo = None
        self.quantities = {}
        for row in self.quantity_df.iterrows():
            ser = row[1] #(index, Series) comes from iterrows()
            column_names = ser.index.tolist()
            my_dict = {}
            for column_name in column_names:
                my_dict[column_name] = ser[column_name]
            new_quantity = quantity(my_dict)
            self.quantities[new_quantity.getStringName()] = new_quantity
        '''
        #start
        #self.testInfo = None
        self.quantity_df = None
        self.testHWInfo = None
        self.continueHWTest =True
        #the stopThread is only started when the stop button is pressed
        self.stopHWThread = Thread(target = self.listenForHWStop, name='stop')


        #self.HWtestFunctions = {1:self.checkPSUAm, 2:self.checkPSUBm}#{1:self.HWdebugtest}
        
        self.HWtestFunctions = {1:self.checkPSUAm, 2:self.checkPSUBm, 3:self.checkTP5B,
                              4:self.checkTP1B, 5:self.testLoads, 
                              6:self.testRibbon, 7:self.LEDcheck}
        
        
    @pyqtSlot()
    def window(self, title, message, result):
        self.title = 'PyQt5 messagebox - pythonspot.com'
        #self.setWindowTitle(self.title)
        self.setGeometry(10, 10, 320, 200)
 
        buttonReply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            print('Yes clicked.')
            self.failresult = True
        else:
            print('No clicked.')
            self.failresult = False
        #self.show()
        return   
    
    def listenForHWStop(self):
        self.continueHWTest= False
        self.status.emit('Stopping Test')
        #print('heard that stop request:'.format(self.continueTest))
        return
    
    def functionMapper(self, testNumber):
        return self.HWtestFunctions.get(testNumber, self.runtestError)
    
    @pyqtSlot(list)
    def takeHWTestInfo(self, alist):
        #self.ConfigFilePath = string
        self.quantity_df = alist[-1]
        self.testHWInfo = alist[:-1]
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
    
    def setUpForHWTest(self, test):
        load1_off(self.myResources.daq)
        load2_off(self.myResources.daq)
        load3_off(self.myResources.daq)
        
        self.lv_supply = self.myResources.get_lv_supply()
        self.lv_supply.set_output_mode(0)
        self.lv_supply.set_rising_voltage_slew('MAX')
        
        self.hv_supply = self.myResources.get_hv_supply()
        self.hv_supply.set_output_mode(0)
        
        '''
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
        elif 'Caps Charging' in test['TEST DESCRIPTION'].iloc[0]: 
            load1_off(self.myResources.daq)
            load2_off(self.myResources.daq)
            load3_off(self.myResources.daq)
            close_rl5(self.myResources.daq)
        '''
        return
    
    @pyqtSlot()
    def startHWTestThread(self):
        self.testHWThread = Thread(target=self.startHWTest, name='test')
        self.continueHWTest=True
        self.testHWThread.start()
        return
    

    def startHWTest(self):
        #loads 1-3 on 385-0046 Rev B are each 10 ohm. 24^2/10 = 57.6W
        #self.continueTest=True
        self.continueHWTest=True
        self.status.emit('Starting Test!')
        
        for test in self.testHWInfo:
            if self.continueHWTest:
                testNumber = test.iloc[0,0].astype(int)
                self.setUpForHWTest(test)
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
        
        self.status.emit('Discharging Caps')
        self.dischargeCaps()
        self.status.emit('Done all the tests!')
        '''
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
    '''
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
    '''
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

    def checkPSUAm(self, test):
        '''
        Feed the 80V instek to PSUAm with SelfTest Cable __
        Adjust a few times and verify the readback matches
        '''
        self.status.emit('Setting up for PSUA Check')
        
        
        close_rl5(self.daq)
        time.sleep(1)
        self.lv_supply.apply(0,1)
        self.lv_supply.set_output('ON')
        row = self.getRow(test) - 1
        i = 0
        for voltage in np.arange(5,30,5,dtype=float):
            self.lv_supply.apply(voltage, 5)
            i += 1
            row += 1
            time.sleep(1)
            readback = self.quantities['PSUA'].measure(self.daq) 
            '''
            stimulus = self.lv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(voltage)
            print(readback)
            print(stimulus)
            print(result)
            print('!!!DONE!!!!')
            '''
            self.resultReady.emit((row, readback)) #read the input
            #self.resultReady.emit((row, readback)) #read the input
        self.lv_supply.apply(0,.2)
        self.lv_supply.set_output('OFF')     
        return 
        '''
        #debug function to see how to input rows
        
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
        self.resultReady.emit((row, np.nan))
        time.sleep(2)
        self.continueTest= False
        self.dischargeCaps() #if fails, discharges caps
        return
        '''
    def checkPSUBm(self, test):
        '''
        Feed the 80V instek to PSUAm with SelfTest Cable __
        Adjust a few times and verify the readback matches
        '''
        open_rl5(self.daq)
        time.sleep(1)
        self.lv_supply.apply(0,1)
        self.lv_supply.set_output('ON')
        #row = self.getRow(test) - 1
        row = 4
        i = 0
        for voltage in np.arange(5,30,5,dtype=float):
            self.lv_supply.apply(voltage, 5)
            time.sleep(1)
            i += 1
            row += 1
            readbackB = self.quantities['PSUB'].measure(self.daq) 
            readbackC = self.quantities['PSUC'].measure(self.daq) 
            '''
            stimulus = self.lv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(voltage)
            print(readback)
            print(stimulus)
            print(result)
            print('!!!DONE!!!!')
            '''
            self.resultReady.emit((row, readbackB)) #read the input
            self.resultReady.emit((row+5, readbackC)) #read the input
            
        self.lv_supply.apply(0,.2)
        self.lv_supply.set_output('OFF')
        return
    
    def checkTP5B(self, test):
        '''
        Output HV supply to PBUS/NBUS 
        '''
        close_rl1(self.daq)
        open_rl2(self.daq)
        self.hv_supply.apply(0, .2)
        self.hv_supply.set_output('ON')
        #row = self.getRow(test) - 1
        row = 14
        
        for voltage in np.arange(6,36,6,dtype=float):
            self.hv_supply.apply(voltage, 1)
            time.sleep(1)
            
            row += 1
            readback5b = self.quantities['TP5B'].measure(self.daq) 
            readback6b = self.quantities['TP6B'].measure(self.daq) 
            readbackhv = self.quantities['HVCAP'].measure(self.daq)
            '''
            stimulus = self.lv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(voltage)
            print(readback)
            print(stimulus)
            print(result)
            print('!!!DONE!!!!')
            '''
            self.resultReady.emit((row, readback5b)) #read the TP5B input
            self.resultReady.emit((row+5, readback6b)) #read the TP6B input
            self.resultReady.emit((row+10, readbackhv)) #read the TP6B input
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return
            
    def checkTP1B(self, test):
        '''
        Output HV supply to PBUS/NBUS 
        '''
        close_rl1(self.daq)
        close_rl2(self.daq)
        self.hv_supply.apply(0, .2)
        self.hv_supply.set_output('ON')
        #row = self.getRow(test) - 1
        row = 29
        
        for voltage in np.arange(6,36,6,dtype=float):
            #print('programmed: {}'.format(voltage))
            self.hv_supply.apply(voltage, 1)
            time.sleep(5)
            readback1b = self.quantities['TP1B'].measure(self.daq) 
            readback2b = self.quantities['TP2B'].measure(self.daq) 
            
            row += 1
            '''
            stimulus = self.hv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(3, readback, stimulus, result ))
            '''
            self.resultReady.emit((row, readback1b)) #read the TP5B input
            self.resultReady.emit((row+5, readback2b)) #read the TP6B input
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return        
    
    def checkHVCAP(self, test):
        '''
        Output HV supply to PBUS/NBUS 
        
        NOTE: removed. to be included in TP 5 test
        
        open_rl1(self.daq)
        open_rl2(self.daq)
        close_rl3(self.daq)
        close_rl4(self.daq)
        '''
        close_rl1(self.daq)
        open_rl2(self.daq) #because R11 connects to HVCAP
        
        self.hv_supply.apply(0, 1)
        self.hv_supply.set_output('ON')
        #row = self.getRow(test) - 1
        row = 39
        
        for voltage in np.arange(3.2,16.2,3.2,dtype=float):
            self.hv_supply.apply(voltage, .2)
            time.sleep(1)
            row +=1
            readback = self.quantities['HVCAP'].measure(self.daq)
            '''
            stimulus = self.hv_supply.get_voltage()
            result = .99*readback < stimulus < 1.01*readback
            print(self.mystr.format(4, readback, stimulus, result ))
            '''
            #time.sleep(2)
            self.resultReady.emit((row, readback)) #read the input
        self.hv_supply.apply(0,.2)
        self.hv_supply.set_output('OFF')
        return

    def exercise_relays(self):
        
        for i in range(5):
            close_rl1(self.daq)
            time.sleep(.2)
            close_rl2(self.daq)
            time.sleep(.2)
            close_rl3(self.daq)
            time.sleep(.2)
            close_rl4(self.daq)
            time.sleep(.2)
            close_rl5(self.daq)
            time.sleep(2)
            open_rl1(self.daq)
            time.sleep(.2)
            open_rl2(self.daq)
            time.sleep(.2)
            open_rl3(self.daq)
            time.sleep(.2)
            open_rl4(self.daq)
            time.sleep(.2)
            open_rl5(self.daq)
            time.sleep(2)
        return 
    
    def testLoads(self, test):
        load1_off(self.daq)
        load2_off(self.daq)
        load3_off(self.daq)
        #row = self.getRow(test)
        row = 40
        time.sleep(1)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        #result = load > 1e6
        #print(self.mystr.format(5, load, 1e9, result))
        if load > 9999999:
            load = 999999 #log as generic pass
        elif load == 9999:
            load = -9999
        self.resultReady.emit((row, load)) #read the input
        
        
        load1_on(self.daq)
        time.sleep(1)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        #result = .9*10 < load < 1.1*10
        #print(self.mystr.format(5, load, 10, result))
        load1_off(self.daq)
        self.resultReady.emit((row+1, load)) #read the input
        
        load2_on(self.daq)
        time.sleep(1)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        #result = .9*10 < load < 1.1*10
        #print(self.mystr.format(5, load, 10, result))
        load2_off(self.daq)
        self.resultReady.emit((row+2, load)) #read the input
        
        load3_on(self.daq)
        time.sleep(1)
        load = self.daq.measure_Resistance(self.quantities['24Vout'].getChannel())
        #result = .9*10 < load < 1.1*10
        #print(self.mystr.format(5, load, 10, result))
        load3_off(self.daq)
        self.resultReady.emit((row+3, load)) #read the input
        time.sleep(1)
        return
    def testRibbon(self, test):
        buck_off(self.daq)
        time.sleep(1)
        row = 44
        readback = self.quantities['PSU_FLT'].measure(self.daq)
        #result = readback < .2
        #print(self.mystr.format(6, readback, 0, result))
        self.resultReady.emit((row, readback))
       
        row +=1
        buck_on(self.daq)
        time.sleep(1)
        readback = self.quantities['PSU_FLT'].measure(self.daq)
        #result = readback > 4
        #print(self.mystr.format(6, readback, 5, result))
        self.resultReady.emit((row, readback))
        buck_off(self.daq)
        
        row +=1
        flyback_on(self.daq)
        time.sleep(1)
        readback = self.quantities['SPM'].measure(self.daq)
        #result = readback > 4
        #print(self.mystr.format(7, readback, 5, result))
        self.resultReady.emit((row, readback))
        
        row +=1
        readback = self.quantities['TEMP'].measure(self.daq)
        #print(feedback)
        self.resultReady.emit((row, readback))
        
        row +=1
        flyback_off(self.daq)
        time.sleep(1)
        readback = self.quantities['SPM'].measure(self.daq)
        #result = readback < .2
        #print(self.mystr.format(7, readback, 0, result))
        self.resultReady.emit((row, readback))
        
        row +=1
        readback = self.quantities['TEMP'].measure(self.daq)
        self.resultReady.emit((row, readback))
        
        flyback_off(self.daq)
        
        
        row +=1
        readback = self.quantities['FLT_OUT'].measure(self.daq)
        self.resultReady.emit((row, readback))
        #result = 3.8 < readback < 4.2
        #print(self.mystr.format(8, readback, 4, result))
        return
    def LEDcheck(self, test):
        
        #row = self.getRow(test)
        row = 49
        self.failresult = False
        #self.setWindowTitle("QTableView")
        '''
        Va Vb visual check/RL3, RL4 check
        '''
        self.failtitle = 'DS1 Diode check'
        self.failmessage = "Is DS1 lit up?"
        self.failresult = False
        
        
        open_rl1(self.myResources.daq)
        close_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        time.sleep(1)
        
        self.myResources.hv_supply.apply(4,0.1)
        self.myResources.hv_supply.set_output('ON')
        time.sleep(.2)
        self.window(self.failtitle,self.failmessage,self.failresult)
        self.resultReady.emit((row, self.failresult)) #read the input
        self.myResources.hv_supply.set_output('OFF')
        
        
        '''
        Va Vc visual check/RL3, RL4 check
        '''
        self.failtitle = 'DS2 Diode check'
        self.failmessage = "Is DS2 lit up?"
        self.failresult = False
        row += 1
        
        #open_rl1(self.myResources.daq)
        close_rl3(self.myResources.daq)
        close_rl4(self.myResources.daq)
        time.sleep(1)
        
        #self.myResources.hv_supply.apply(4,0.1)
        self.myResources.hv_supply.set_output('ON')
        time.sleep(.2)
        self.window(self.failtitle,self.failmessage,self.failresult)
        self.resultReady.emit((row, self.failresult)) #read the input
        self.myResources.hv_supply.set_output('OFF')
        
        '''
        Vb Va visual check/RL3, RL4 check
        '''
        self.failtitle = 'DS3 Diode check'
        self.failmessage = "Is DS3 lit up?"
        self.failresult = False
        row += 1
        
        #open_rl1(self.myResources.daq)
        open_rl3(self.myResources.daq)
        close_rl4(self.myResources.daq)
        time.sleep(1)
        
        #self.myResources.hv_supply.apply(4,0.1)
        self.myResources.hv_supply.set_output('ON')
        time.sleep(.2)
        self.window(self.failtitle,self.failmessage,self.failresult)
        self.resultReady.emit((row, self.failresult)) #read the input
        self.myResources.hv_supply.set_output('OFF')
        
        '''
        Vc Va visual check/RL3, RL4 check
        '''
        self.failtitle = 'DS4 Diode check'
        self.failmessage = "Is DS4 lit up?"
        self.failresult = False
        row += 1
        
        #open_rl1(self.myResources.daq)
        open_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        time.sleep(1)
        
        #self.myResources.hv_supply.apply(4,0.1)
        self.myResources.hv_supply.set_output('ON')
        time.sleep(.2)
        self.window(self.failtitle,self.failmessage,self.failresult)
        self.resultReady.emit((row, self.failresult)) #read the input
        self.myResources.hv_supply.set_output('OFF')
        self.myResources.hv_supply.apply(0,0.1)
        return
    def HWdebugtest(self, test):
        _input = 5555
        row = self.getRow(test)
        self.resultReady.emit((row, _input))
        return
    
        
#selfTester = SelfTester(InstrumentConnections(pyvisa.ResourceManager()))
#selfTester.checkPSUAm()
#selfTester.checkPSUBm()
#selfTester.checkTP1B()
#selfTester.checkTP5B()
#selfTester.checkHVCAP()
#selfTester.testLoads()
#selfTester.testRibbon()