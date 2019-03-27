# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 11:05:13 2019

@author: Erik
"""
import re
import pyvisa

ScopePattern = re.compile('RIGOL TECHNOLOGIES,DS1104Z,')
tup =  self.ResourceManager.list_resources()
#print(tup)
for resource_id in tup :
    try:
        
        inst = self.ResourceManager.open_resource(resource_id, send_end=True )
        name_str = inst.query('*IDN?').strip()
        if self.ScopePattern.match(name_str) is not None:
            scope = RigolDS1104.Rigol(inst)
            self.PSW80ConnectResult.emit('Connected to: {}'.format(name_str))

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