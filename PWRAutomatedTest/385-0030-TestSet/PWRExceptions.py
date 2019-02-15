# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 11:35:43 2019

@author: Erik
"""

class Error(Exception):
    pass

class TestFailure(Error):
    ''' Exception raised when a test result fails to fall
    within the allowable range '''
    def __init__(self, val, message):
        self.val = val
        self.message = message
        
        