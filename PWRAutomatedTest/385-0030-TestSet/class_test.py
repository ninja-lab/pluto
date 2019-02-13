# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:18:29 2019

@author: Erik
"""

class parent():
    
    def __init__(self):
        self.x = 43
        self.y = 21
        
class child(parent):
    def __init__(self):
        super().__init__()
        self.z = 39

c = child()
print(c.x)        