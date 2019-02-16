# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:17:04 2019

@author: Erik
This is the main file. 
"""
import sys

from PyQt5.QtWidgets import QApplication#, QMainWindow
#from Tester import Tester
#from InstrumentConnections import InstrumentConnections
#import pyvisa
#myResources = InstrumentConnections(pyvisa.ResourceManager()) 
from PWR_Test_GUI import MyApp

app = QApplication(sys.argv)
window = MyApp()
window.show()

#myTester = Tester(myResources)

'''
To start a test, all the instruments have to be connected, 
and the user has to enter a valid serial number. 
Only then is the StartTestButton enabled. 
'''

#window.PSW80ConnectButton.pressed.connect(myResources.Connect)
#window.RefreshButton.pressed.connect(myResources.Refresh)
#window.DUTSerialNumberLineEdit.editingFinished.connect(window.checkDUTSerialNumber)
'''window.checkDUTSerialNumber will call window.checkStartConditions() if the serial number is valid (based on some
potential requirements of form)
'''
#myResources.PSW80ConnectResult.connect(window.PSW80LineEdit.setText)
#myResources.PSW800ConnectResult.connect(window.PSW800LineEdit.setText)
#myResources.KeysightConnectResult.connect(window.KeysightLineEdit.setText)
#myResources.ConnectResult.connect(window.takeConnectResult)
'''window.takeConnectResult() will also call window.checkStartConditions(), which enables the 
StartTestButton() if both the DUT serial number is valid, and the instruments are connected. 
'''
#window.StartTestButton.clicked.connect(myTester.startTest)

sys.exit(app.exec_())

