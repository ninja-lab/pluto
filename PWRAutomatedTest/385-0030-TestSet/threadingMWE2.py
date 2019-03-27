# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:40:17 2019

@author: Erik
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QObject
from threading import Thread
import time
import sys

class master(QObject):
    StartSignal = pyqtSignal()
    StopSignal = pyqtSignal()
    
    def __init__(self):
        QObject.__init__(self)
        self.worker = worker()
        self.StartSignal.connect(self.worker.startLongFunction)
        self.StopSignal.connect(self.worker.stopThread.start)
    
        
class worker(QObject):
    def __init__(self):
        
        super().__init__()
        self.continueTest = True
        self.stopThread = Thread(target = self.listenForStop, name='stop')
        
    @pyqtSlot()    
    def listenForStop(self):
        print("Stopping!")
        self.continueTest = False
        
    def longFunction(self):
        for x in range(10):
            if self.continueTest:
                print("x: {}".format(x))
                time.sleep(1)
            else:
                return
        return
    @pyqtSlot()   
    def startLongFunction(self):
        self.testThread = Thread(target = self.longFunction, name='test')
        self.testThread.start()
        return
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    master = master() 
    master.StartSignal.emit()
    time.sleep(3)
    master.StopSignal.emit()
    
    
    