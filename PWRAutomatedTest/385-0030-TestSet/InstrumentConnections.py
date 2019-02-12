# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 07:34:02 2019

@author: Erik

The two instek power supplies are Serial Intruments, and it 
is impossible to tell them apart until one queries their *IDN?. 
The Keysight DAQ is a USBTMC. 

"""

import pyvisa
from PyQt5.QtCore import pyqtSignal, QThread
import InstekPSW
import Keysight34972A
import re
    
class InstrumentConnections(QThread):
    #this is where user defined signals need to get defined
    KeysightConnectResult = pyqtSignal(str)
    PSW80ConnectResult = pyqtSignal(str)
    PSW800ConnectResult = pyqtSignal(str)
    ConnectResult = pyqtSignal(bool)

    
    def __init__(self, rm):
        #I think classes that define new signals need to inherit from QThread
        QThread.__init__(self)

        self.ResourceManager = rm
        self.lv_supply = None
        self.hv_supply = None
        self.daq = None
        
        self.KeysightPattern = re.compile('Agilent Technologies,34972A')
        self.PSW80Pattern = re.compile('GW-INSTEK,PSW80-13.5')
        self.PSW800Pattern = re.compile('GW-INSTEK,PSW800-1.44')
        
        return
    
    

    def Connect(self):
    
        tup =  self.ResourceManager.list_resources()
        #print(tup)
        for resource_id in tup :
            try:
                
                inst = self.ResourceManager.open_resource(resource_id, send_end=True )
                name_str = inst.query('*IDN?').strip()
                #print(name_str)
                #print('resource_id: {}'.format(resource_id))
                if self.PSW80Pattern.match(name_str) is not None:
                    self.lv_supply = InstekPSW.InstekPSW(inst)
                    self.PSW80ConnectResult.emit('Connected to: {}'.format(name_str))
                elif self.PSW800Pattern.match(name_str) is not None:
                    self.hv_supply = InstekPSW.InstekPSW(inst)
                    self.PSW800ConnectResult.emit('Connected to: {}'.format(name_str))
                elif self.KeysightPattern.match(name_str) is not None:
                    self.daq = Keysight34972A.Keysight34972A(inst)
                    self.KeysightConnectResult.emit('Connected to: {}'.format(name_str))
            except pyvisa.errors.VisaIOError:
                pass
        if self.lv_supply is not None and self.hv_supply is not None and self.daq is not None:
            self.ConnectResult.emit(True)
        else:
            if self.lv_supply is None:
                self.PSW80ConnectResult.emit('Could not connect!')
            if self.hv_supply is None:
                self.PSW800ConnectResult.emit('Could not connect!')
            if self.daq is None:
                self.KeysightConnectResult.emit('Could not connect!')
            self.ConnectResult.emit(False)
    def Refresh(self):
        if self.lv_supply is not None:
            self.lv_supply.close()
        if self.hv_supply is not None:
            self.hv_supply.close()
        if self.daq is not None:
            self.daq.close()
        self.ResourceManager.close()
        self.ResourceManager = pyvisa.ResourceManager()
        self.lv_supply = None
        self.hv_supply = None
        self.daq = None
        self.PSW80ConnectResult.emit('Refreshed')
        self.PSW800ConnectResult.emit('Refreshed')
        self.KeysightConnectResult.emit('Refreshed')
        return
            
                    
                    
                        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
             