# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:11:55 2019

@author: Erik
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, qApp#, QLabel, QAction
from PyQt5.QtCore import pyqtSignal, QThread, QObject
import pyvisa
from datetime import datetime
from InstrumentConnections import InstrumentConnections
from PyQt5 import uic
import pandas as pd
from PandasModel import PandasModel
import Tester
import style_strings
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
  
    ConfigFilePathObtained = pyqtSignal(str)
    DisplayMessage = pyqtSignal(str)
    
    def __init__(self,):
        QMainWindow.__init__(self,)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        #connect some signals to slots
        self.InstrumentsPageButton.pressed.connect(self.showInstrumentsPage)
        self.TestingPageButton.pressed.connect(self.showTestingPage)
        self.ConfigFileSelectButton.pressed.connect(self.openFileNameDialog)
        self.actionQuit.triggered.connect(qApp.closeAllWindows)
        #self.actionFunky.triggered.connect(self.setFunkyStyleSheet)
        #self.actionRetro.triggered.connect(self.setRetroStyleSheet)
        #self.actionNone.triggered.connect(self.setNoneStyleSheet)
        
        self.ConfigFileLineEdit.editingFinished.connect(self.loadTableData)
        
        self.DUTSerialNumberLineEdit.editingFinished.connect(self.checkDUTSerialNumber)
        
        #intialize some fields to be used
        self.instrumentsConnected = False
        self.validDUTSerialNumber = False
        self.StartTestButton.setEnabled(False)
        self.data = None
        self.ConfigFilePath = None       
        self.DUTSerialNumber = None
        self.setGeometry(100, 100, 800, 800)
        
        #this setup found to be necessary for the a long running test to run in the background
        self.obj = Tester.Tester(InstrumentConnections(pyvisa.ResourceManager()))
        
        self.thread = QThread()
        self.obj.resultReady.connect(self.onResultReady)
        self.obj.status.connect(self.TestInfoLineEdit.setText)
        self.obj.moveToThread(self.thread)
        self.thread.start()

        self.StopTestButton.pressed.connect(self.thread.quit)
        self.StartTestButton.pressed.connect(self.thread.start)
        self.StartTestButton.pressed.connect(self.obj.startTest)
  
        self.ConfigFilePathObtained.connect(self.obj.takeConfigFilePath)
        self.PSW80ConnectButton.pressed.connect(self.obj.myResources.Connect)
        self.RefreshButton.pressed.connect(self.obj.myResources.Refresh)
        self.obj.myResources.PSW80ConnectResult.connect(self.PSW80LineEdit.setText)
        self.obj.myResources.PSW800ConnectResult.connect(self.PSW800LineEdit.setText)
        self.obj.myResources.KeysightConnectResult.connect(self.KeysightLineEdit.setText)
        self.obj.myResources.ConnectResult.connect(self.takeConnectResult)
    '''    
    def setFunkyStyleSheet(self):
        qApp.setStyleSheet(style_strings.funky)
        #self.centralWidget.setStyleSheet(style_strings.funky)
    def setRetroStyleSheet(self):
        qApp.setStyleSheet(style_strings.retro)
    def setNoneStyleSheet(self):
        qApp.setStyleSheet('')
        #self.centralWidget.setStyleSheet('')
        self.scrollAreaWidgetContents.setStyleSheet('')
   '''
    def onResultReady(self, tup):
        row = tup[0]
        passfail_column = self.model.getColumnNumber('PASS/FAIL')
        self.model.setData(self.model.index(row,self.measurement_column),tup[1])
        self.model.setData(self.model.index(row,self.time_column),datetime.now())
        if self.model.getMinimum(row) < tup[1] < self.model.getMaximum(row):
            self.model.setData(self.model.index(row, passfail_column), 'pass')
        else:
            self.model.setData(self.model.index(row, passfail_column), 'FAIL!')

    def loadTableData(self):
        '''
        This is called after a path to the config file is obtained. 
        The config file is effectively the test matrix. 
        It is also where the information regarding channel assignments in
        the DAQ is kept. 
        For now, the Tester class also reads from the config file, to know about min
        and max when it is useful, and to create the quantity objects. 
        '''
        try:
            self.data = pd.read_excel(self.ConfigFilePath, 'Report')
            #otherwise the TIMESTAMP column is loaded as NaN which is float
            self.data['TIMESTAMP'] = pd.to_datetime(self.data['TIMESTAMP'])
            self.data['PASS/FAIL'] = self.data['PASS/FAIL'].astype(str) 
            self.model = PandasModel(self.data)
            self.tableView.setModel(self.model)
        
            self.measurement_column = self.model.getColumnNumber('MEASURED')
            self.time_column = self.model.getColumnNumber('TIMESTAMP') 
        except ValueError:
            self.ConfigFileLineEdit.setText('That is not the config file!')
       
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
            self.ConfigFilePathObtained.emit(self.ConfigFilePath)
            self.checkStartConditions()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)#sys.argv
    window = MyApp()
    window.show()
    sys.exit(app.exec_())