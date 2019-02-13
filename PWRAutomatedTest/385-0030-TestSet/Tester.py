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
class Tester():

    
    def __init__(self, myResources):
        self.currentDUTSerialNumber = None
        self.quantity_df = None
        self.myResources = myResources
        return
    
    def takeDUTSerialNumber(self, string):
        self.currentDUTSerialNumber = string
        return
    
    def takeConfigFilePath(self, string):
        self.ConfigFilePath = string
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
   
    def startTest(self):

        self.runtest0()
        self.runtest1()
        #self.runtest2()
        #self.runtest3()
        
        return
    
    def runtest0(self):
        close_rl5(self.myResources.daq)
        time.sleep(0.1)
        self.myResources.lv_supply.apply(0,.1)
        self.myResources.lv_supply.set_output('ON')
        for i in np.arange(20, 24, .01): #sweep voltage range
            break
            self.myResources.lv_supply.apply(i, 1) #(voltage, current)
            time.sleep(.1)
            output = self.quantities['24Vout'].measure(self.myResources.daq)
            _input = self.quantities['PSUA'].measure(self.myResources.daq)
            if .99*_input < output < 1.01*_input:
                pass
                #quantities['PSUA'].measure(daq)
                #tests[0].setMeasurement(quantities['PSUA'].getMeasurement())
                #break            
                #return
        return
    
    def runtest1(self):
        print("great job!")
        return
        
    
    