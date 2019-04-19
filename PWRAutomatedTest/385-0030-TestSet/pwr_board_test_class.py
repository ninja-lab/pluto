# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 13:27:08 2018

@author: Erik
"""


class quantity():
    '''
    These objects are populated with attributes described 
    in the config file, on the 'quantities' page. 
    It captures the signal name, the channel it is assigned to, 
    and the scale and offset to be applied to the measurement, if any. 
    '''
    def __init__(self, adict):
        self.mydict=adict
    def measure(self, daq):
        val = (daq.measure_DCV(self.mydict['CHANNEL']) - \
               self.mydict['OFFSET']) * \
               self.mydict['SCALE']
        #self.mydict['MEASURED'] = val
        return val
    def getScale(self):
        return self.mydict['SCALE']
    def getOffset(self):
        return self.mydict['OFFSET']
    def getStringName(self):
        return self.mydict['Quantity']
    def getChannel(self):
        return self.mydict['CHANNEL']  

