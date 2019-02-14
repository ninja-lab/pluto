# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:17:04 2019

@author: Erik
This is the main file. 
"""
import sys

from PyQt5.QtWidgets import QApplication#, QMainWindow
from Tester import Tester
from InstrumentConnections import InstrumentConnections
import pyvisa
myResources = InstrumentConnections(pyvisa.ResourceManager()) 

app = QApplication(sys.argv)

myTester = Tester(myResources)
myTester.show()
'''
To start a test, all the instruments have to be connected, 
and the user has to enter a valid serial number. 
Only then is the StartTestButton enabled. 
'''

myTester.PSW80ConnectButton.pressed.connect(myResources.Connect)
myTester.RefreshButton.pressed.connect(myResources.Refresh)
myTester.DUTSerialNumberLineEdit.editingFinished.connect(myTester.checkDUTSerialNumber)
'''window.checkDUTSerialNumber will call window.checkStartConditions() if the serial number is valid (based on some
potential requirements of form)
'''
myResources.PSW80ConnectResult.connect(myTester.PSW80LineEdit.setText)
myResources.PSW800ConnectResult.connect(myTester.PSW800LineEdit.setText)
myResources.KeysightConnectResult.connect(myTester.KeysightLineEdit.setText)
myResources.ConnectResult.connect(myTester.takeConnectResult)
'''window.takeConnectResult() will also call window.checkStartConditions(), which enables the 
StartTestButton() if both the DUT serial number is valid, and the instruments are connected. 
'''
myTester.StartTestButton.clicked.connect(myTester.startTest)

sys.exit(app.exec_())

