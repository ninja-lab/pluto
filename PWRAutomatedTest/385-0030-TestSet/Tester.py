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
from PWR_Test_GUI import MyApp
class Tester(MyApp):

    def __init__(self, myResources):
        MyApp.__init__(self)
        self.currentDUTSerialNumber = None
        self.myResources = myResources
        self.currentTest = 0
    
    def startTest(self):
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
        self.measurement_column = self.model.getColumnNumber('MEASURED')
        self.time_column = self.model.getColumnNumber('TIMESTAMP') 

        
        
        self.currentRow = 0
        #try:
            
        #self.runtest1()
        self.runtest2()
        self.runtest3()
        self.runtest4()
        self.runtest5()
        self.runtest6()
        self.runtest7()
        
        self.runtest8()
        '''tests 9-14 test HV Diodes, so do some set up common to all'''
        self.myResources.hv_supply.set_rising_voltage_slew(50) #50V/sec
        self.myResources.hv_supply.set_output_mode(2) #slew rate priority (ramp slowly)
        self.myResources.hv_supply.apply(840, 10e-3)
        
        self.runtest9()
        self.runtest10()
        self.runtest11()
        self.runtest12()
        self.runtest13()
        self.runtest14()
        
        self.myResources.hv_supply.apply(0,0)
        
        self.runtest15()
        self.runtest16()
        self.runtest17()
        self.runtest18()
        self.runtest19()
        self.runtest20()
        self.runtest21()
            
        #except Exception:
            
            
        return
        
    def updateModel(self, row, val):
        self.model.setData(self.model.index(row, self.measurement_column), val)
        self.model.setData(self.model.index(row, self.time_column), datetime.now())
        
    def runtest1(self):
        row = 1
        close_rl5(self.myResources.daq)
        time.sleep(0.1)
        self.myResources.lv_supply.apply(0,.1)
        self.myResources.lv_supply.set_output('ON')
        startVoltage = self.model.getMinimum(row)
        stopVoltage = self.model.getMaximum(row)
        for i in np.arange(startVoltage, stopVoltage, .01): #sweep voltage range
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if .99*_input < output < 1.01*_input:
                self.updateModel(row, _input)
                
        return
    
   
        
    def runtest2(self):
        print("great job!")
        return

    def runtest3(self):
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
        open_rl1(self.myResources.daq)
        open_rl2(self.myResources.daq)
        open_rl3(self.myResources.daq)
        open_rl4(self.myResources.daq)
        
        self.myResources.hv_supply.set_output('ON')
        while self.myResources.hv_supply.get_voltage() < 830:
            if self.myResources.hv_supply.get_protection_state():
                self.myResources.hv_supply.set_output('OFF')
                print('current_limit!')
                break
            time.sleep(.3)
        current = self.myResources.hv_supply.get_current()
        self.updateModel(9, current)
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
        return
    
    def runtest16(self):
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
        
        
    
    