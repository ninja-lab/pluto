# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:17:04 2019

@author: Erik
This is the main file. 
"""
import sys

from PyQt5.QtWidgets import QApplication#, QMainWindow
from PWR_Test_GUI import MyApp
from Tester import Tester
from InstrumentConnections import InstrumentConnections
import pyvisa
myInstruments = InstrumentConnections(rm=pyvisa.ResourceManager()) 

app = QApplication(sys.argv)
window = MyApp()
window.show()


myTester = Tester()
'''
To start a test, all the instruments have to be connected, 
and the user has to enter a valid serial number. 
Only then is the StartTestButton enabled. 
'''

window.PSW80ConnectButton.pressed.connect(myInstruments.Connect)
window.RefreshButton.pressed.connect(myInstruments.Refresh)
window.DUTSerialNumberLineEdit.textChanged.connect(myTester.takeDUTSerialNumber)
window.DUTSerialNumberLineEdit.editingFinished.connect(window.checkDUTSerialNumber)
myInstruments.PSW80ConnectResult.connect(window.PSW80LineEdit.setText)
myInstruments.PSW800ConnectResult.connect(window.PSW800LineEdit.setText)
myInstruments.KeysightConnectResult.connect(window.KeysightLineEdit.setText)
myInstruments.ConnectResult.connect(window.takeConnectResult)

sys.exit(app.exec_())

