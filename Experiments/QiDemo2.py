# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 16:06:27 2021

@author: eriki
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QTimer

qtCreatorFile = "Qi.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow, Ui_MainWindow):
    
    temp_val = pyqtSignal(float)
    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setGeometry(50, 50, 400, 400)
        self.timer = QTimer()
        self.timer.setInterval(500) #mSec
        #self.timer.moveToThread(self)
        self.timer.timeout.connect(self.emit_temp_val)
        
        self.temp_val.connect(self.lcdNumber.display)
        #self.emit_temp_val()
        self.temp = 1
        self.timer.start()
    
    def emit_temp_val(self):
        self.temp += 1.1
        self.temp_val.emit(self.temp)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()
    sys.exit(app.exec_())