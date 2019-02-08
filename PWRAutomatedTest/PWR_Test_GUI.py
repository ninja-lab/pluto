# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:11:55 2019

@author: Erik
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
import pandas as pd
import numpy as np
from PandasModel import PandasModel
qtCreatorFile = "385-0030-RevD-GUI.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QMainWindow, Ui_MainWindow):
       
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.InstrumentsPageButton.pressed.connect(self.showInstrumentsPage)
        self.TestingPageButton.pressed.connect(self.showTestingPage)
        self.instrumentsConnected = False
        self.validDUTSerialNumber = False
        self.StartTestButton.setEnabled(False)
        
        self.data =  pd.DataFrame(np.random.randn(6, 6))
        self.data[0][1] = 'hello'
        self.model = PandasModel(self.data)
        self.model.setData(self.model.index(3,3),999)
        self.tableView.setModel(self.model)
        
    def showTestingPage(self):
        self.stackedWidget.setCurrentIndex(0)
        self.InstrumentsPageButton.setChecked(False)

    def showInstrumentsPage(self):
        self.stackedWidget.setCurrentIndex(1)
        self.TestingPageButton.setChecked(False)
        
    def checkDUTSerialNumber(self):
        DUTSerialNumber = self.DUTSerialNumberLineEdit.text()
        if DUTSerialNumber is not None:
            self.validDUTSerialNumber = True
        self.checkStartConditions()
        
    def takeConnectResult(self, result):
        self.instrumentsConnected = result
        self.checkStartConditions()
        
    def checkStartConditions(self):
        #probably need more robust checking on form of serial number
        if self.instrumentsConnected and self.validDUTSerialNumber:
            self.StartTestButton.setEnabled(True)
            self.TestInfoLineEdit.setText('You can start the test!')
        else: 
            self.StartTestButton.setEnabled(False)
            if not self.instrumentsConnected:
                self.TestInfoLineEdit.setText('Instruments are not connected!')
            elif not self.validDUTSerialNumber:
                self.TestInfoLineEdit.setText('Enter DUT Serial Number!')
        
    '''
    This class controls whether the StartTestButton is enabled or not. 
    It is enabled if the operator has entered a valid DUT serial number, 
    and all the instruments are connected. 
    '''
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())