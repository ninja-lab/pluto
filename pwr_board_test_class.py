# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 13:27:08 2018

@author: Erik
"""

class pwr_board_test_class():

    def __init__(self, series):
        '''
        Use the excel test report template as the source
        of all the attributes a test object needs to have.
        
        '''
        column_names = series.index.tolist()
        self.mydict={}
        for column_name in column_names:
            self.mydict[str(column_name)] = series[column_name]
      
    def setMeasurement(self, value):
        self.mydict['MEASURED'] = value
    
    def getMeasurement(self):
        return self.mydict['MEASURED']
    
    def isValid(self):
        if self.getMeasurement is np.NaN:
            return false
        else:
            return self.mydict['MIN'] <= self.getMeasurement() <= self.mydict['MAX']
        
class quantity():
    def __init__(self, series):
        self.mydict={}
        column_names = series.index.tolist()
        
        for column_name in column_names:
            self.mydict[str(column_name)] = series[column_name]
     
    def measure(self, daq):
        val = (daq.measure_DCV(self.mydict['CHANNEL']) - \
               self.mydict['OFFSET']) * \
               self.mydict['SCALE']
        self.mydict['MEASURED'] = val
        
    
    def isValid(self, correct_value):
        if self.getMeasurement is np.NaN:
            return false
        else:
            return self.mydict['MIN'] <= self.getMeasurement() <= self.mydict['MAX']
        
    
        