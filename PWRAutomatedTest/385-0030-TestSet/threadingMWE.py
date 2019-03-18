# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 16:01:00 2019

@author: Erik
"""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QObject
#import threading
import time
import sys

class master(QObject):
    StartSignal = pyqtSignal()
    StopSignal = pyqtSignal()
    
    def __init__(self):
        QObject.__init__(self)
        self.worker = worker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start() 
        self.StartSignal.connect(self.worker.longFunction)
        self.StopSignal.connect(self.worker.listenForStop)
    
        
class worker(QObject):
    def __init__(self):
        
        super().__init__()
        self.continueTest = True
        
    @pyqtSlot()    
    def listenForStop(self):
        print("Stopping!")
        self.continueTest = False
        
    @pyqtSlot()
    def longFunction(self):
        for x in range(10):
            if self.continueTest:
                print("x: {}".format(x))
                time.sleep(1)
            else:
                return
        return
            
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    master = master() 
    master.StartSignal.emit()
    time.sleep(3)
    master.StopSignal.emit()
    
    
    