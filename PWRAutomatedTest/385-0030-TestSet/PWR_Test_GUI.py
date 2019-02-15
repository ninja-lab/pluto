# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:11:55 2019

@author: Erik
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, qApp#, QLabel, QAction
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5 import uic
import pandas as pd
from PandasModel import PandasModel
import PWRTestResources_rc
qtCreatorFile = "385-0030-RevD-GUI.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
pd.set_option('precision', 1)
class MyApp(QMainWindow, Ui_MainWindow):
    '''
    This signal tells the Tester object that it can read the Quantities tab
    of the Config File
    This class inherits from QThread because it needs a signal that passes 
    the config file path out. The Tester object needs the path so it can 
    read the 'quantities' sheet. 
    '''
  
    
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.InstrumentsPageButton.pressed.connect(self.showInstrumentsPage)
        self.TestingPageButton.pressed.connect(self.showTestingPage)
        self.ConfigFileSelectButton.pressed.connect(self.openFileNameDialog)
        self.instrumentsConnected = False
        self.validDUTSerialNumber = False
        self.StartTestButton.setEnabled(False)
        self.ConfigFileLineEdit.editingFinished.connect(self.loadTableData)
        self.data = None
        self.ConfigFilePath = None       
        self.actionQuit.triggered.connect(qApp.closeAllWindows)
        self.setGeometry(100, 100, 400, 400)
        self.DUTSerialNumber = None
 
    def takeResult(self, testNumber, result):
        return 
    def findTestNumber(self, state, quantityName):
        return
    
    def loadTableData(self):
        '''
        This is called after a path to the config file is obtained. 
        The config file is effectively the test matrix. 
        It is also where the information regarding channel assignments in
        the DAQ is kept. 
        '''
        self.data = pd.read_excel(self.ConfigFilePath, 'Report')
        #otherwise the TIMESTAMP column is loaded as NaN which is float
        self.data['TIMESTAMP'] = pd.to_datetime(self.data['TIMESTAMP'])
        self.model = PandasModel(self.data)
        self.tableView.setModel(self.model)

    def showTestingPage(self):
        self.stackedWidget.setCurrentIndex(0)
        self.InstrumentsPageButton.setChecked(False)

    def showInstrumentsPage(self):
        self.stackedWidget.setCurrentIndex(1)
        self.TestingPageButton.setChecked(False)
        
    def checkDUTSerialNumber(self):
        self.DUTSerialNumber = self.DUTSerialNumberLineEdit.text()
        if self.DUTSerialNumber is not None:
            self.validDUTSerialNumber = True
        self.checkStartConditions()
        
    def takeConnectResult(self, result):
        self.instrumentsConnected = result
        self.checkStartConditions()
    '''
    This class controls whether the StartTestButton is enabled or not. 
    It is enabled if the operator has entered a valid DUT serial number, 
    and all the instruments are connected. 
    '''   
    def checkStartConditions(self):
        #probably need more robust checking on form of serial number
    
        if self.instrumentsConnected and self.validDUTSerialNumber and (self.ConfigFilePath is not None):
            self.StartTestButton.setEnabled(True)
            self.TestInfoLineEdit.setText('You can start the test!')
        else: 
            self.StartTestButton.setEnabled(False)
            if not self.instrumentsConnected:
                self.TestInfoLineEdit.setText('Instruments are not connected!')
            elif not self.validDUTSerialNumber:
                self.TestInfoLineEdit.setText('Enter DUT Serial Number!')
            elif self.ConfigFilePath is None:
                self.TestInfoLineEdit.setText('Find the Config file!')
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.ConfigFileLineEdit.setText(fileName)
            self.ConfigFilePath = fileName
            self.ConfigFileLineEdit.editingFinished.emit()
            self.checkStartConditions()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())