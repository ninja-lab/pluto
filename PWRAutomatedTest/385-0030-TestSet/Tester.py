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
#from datetime import datetime
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
        
        self.runtest9() #HV diode test
        self.runtest10()#HV diode test
        self.runtest11()#HV diode test
        self.runtest12()#HV diode test
        self.runtest13()#HV diode test
        self.runtest14()#HV diode test
        '''
        Undo the setup from HV Diode checks:
        '''
        self.myResources.hv_supply.apply(0,0)
    
        self.SetupNoPowerState()
        
        self.runtest15()
        self.runtest16()
        self.runtest17()
        self.runtest18()
        self.runtest19()
        self.runtest20()
        self.runtest21()
         
        #except Exception:
        self.status.emit('Done all the tests!')
        return

    '''
    For the threshold tests, it is useful to know the min and max acceptable values,
    because the test can be slow if sweeping a large range and stepping small. 
    Unfortunately, 
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
    def SetupNoPowerState(self):
        self.status.emit('Setting up for No Power State checks!')
        self.myResources.daq.configure_DCV_channels('(@201:208,210:215)')
        self.myResources.daq.format_reading(time=0, channel=0)
        #self.myResources.daq.format_time_type(time_type='ABS')        
        for my_quantity in self.quantities.values():
            self.myResources.daq.setScale(my_quantity.getScale(), my_quantity.getChannel())
            self.myResources.daq.setOffset(my_quantity.getOffset(), my_quantity.getChannel())
        self.myResources.daq.useScaling()
        
                          
    def runtest15(self):
        '''
        Read all channels to verify no power state.
        The setup is already done with SetupNoPowerState()
        Perform the scan and read all channels. 
        
        '''
        self.status.emit('Running Test 15')
        start_row = 14
        end_row = 27
        data = self.myResources.daq.read()
        combined = zip(np.arange(start_row, end_row+1), data)
        for pair in combined:
            #self.updateModel(pair[0],pair[1])
            self.resultReady.emit(pair)
        return
    
    def runtest16(self):
        row = 29
        return
    def runtest17(self):
        return  
    def runtest18(self):
        return
    def runtest19(self):
        return
    def runtest20(self):
        return
    
    def runtest21(self):
        return
        
        
    
    