# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 13:27:08 2018

@author: Erik
"""
import numpy as np

class pwr_board_test_class():

    def __init__(self, adict):
        '''
        Use the excel test report template as the source
        of all the attributes a test object needs to have.
        '''
        self.mydict=adict
      
    def setMeasurement(self, value):
        self.mydict['MEASURED'] = value
    
    def getMeasurement(self):
        return self.mydict['MEASURED']
    
    def isValid(self):

        return self.mydict['MIN'] <= self.getMeasurement() <= self.mydict['MAX']
    
    def getUnits(self):
        return self.mydict['UNITS']
    
    def report(self):
        return 'Test {} {}: Measured: {:.2f}{}, Status: {}'.format(
            self.mydict['TEST #'],self.mydict['NAME'], self.getMeasurement(), self.getUnits(), self.isValid())
        
class quantity():
    def __init__(self, adict):
        self.mydict=adict
  
    def measure(self, daq):
        val = (daq.measure_DCV(self.mydict['CHANNEL']) - \
               self.mydict['OFFSET']) * \
               self.mydict['SCALE']
        self.mydict['MEASURED'] = val
        return #self.mydict['MEASURED']
    
    def setMeasurement(self, value):
        self.mydict['MEASURED'] = value
    def getMin(self):
        return self.mydict['MIN']
    def getMax(self):
        return self.mydict['MAX']
    def getMeasurement(self):
        return self.mydict['MEASURED']
    def getNominal(self):
        return self.mydict['NOMINAL']
    def getScale(self):
        return self.mydict['SCALE']
    def getOffset(self):
        return self.mydict['OFFSET']
    def isValid(self):
        return self.mydict['MIN'] <= self.getMeasurement() <= self.mydict['MAX']    
    def getStringName(self):
        return self.mydict['Quantity']
    def getChannel(self):
        return self.mydict['CHANNEL']  
    
    def clearMeasurement(self):
        self.setMeasurement(np.NaN)