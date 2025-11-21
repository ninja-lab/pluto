# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 19:03:47 2021

@author: eriki
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QTimer

qtCreatorFile = "Qi2.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow, Ui_MainWindow):
    
    RL_temp = pyqtSignal(float)
    RL_power = pyqtSignal(float)
    SS_temp = pyqtSignal(float)
    SS_power = pyqtSignal(float)
    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 400, 400)
        self.timer = QTimer()
        self.timer.setInterval(500) #mSec
       
        self.timer.timeout.connect(self.update_vals)
        
        self.RL_temp.connect(self.RL_TempLCD.display)
        self.RL_power.connect(self.RL_PowerLCD.display)
        self.SS_temp.connect(self.SS_TempLCD.display)
        self.SS_power.connect(self.SS_PowerLCD.display)
      
        self.RL_temp_val = 1
        self.RL_power_val = 2
        self.SS_power_val = 3
        self.SS_temp_val = 4
        
        self.myInstruments = InstrumentConnections(pyvisa.ResourceManager())
        
        self.timer.start()
    
    def update_vals(self):
        self.RL_power_val += 1.2
        self.RL_temp_val += 1.3
        self.SS_power_val += 1.1
        self.SS_temp_val += 1.5
        
        self.RL_temp.emit(self.RL_temp_val)
        self.RL_power.emit(self.RL_power_val)
        self.SS_temp.emit(self.SS_temp_val)
        self.SS_power.emit(self.SS_power_val)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()
    myCommLink = CommLink()
    #connect the signals to the slots
    myCommLink.new_RL_temp.connect(self.RL_TempLCD.display)
    sys.exit(app.exec_())