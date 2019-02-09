# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 10:11:55 2019

@author: Erik
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QAction, qApp
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt
from PyQt5 import uic
import pandas as pd
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
        self.ConfigFileSelectButton.pressed.connect(self.openFileNameDialog)
        self.instrumentsConnected = False
        self.validDUTSerialNumber = False
        self.StartTestButton.setEnabled(False)
        self.ConfigFileLineEdit.editingFinished.connect(self.loadTableData)
        self.data = None
        self.ConfigFilePath = None
        #self.AKlogo = QPixmap('AK_Horizontal_FullColor_RBG.png').scaled(QSize(200,75),Qt.KeepAspectRatio)
        #self.AKlabel = QLabel()
        #self.AKlabel.setPixmap(self.AKlogo)
        #self.AKlabel.setFixedSize(200,75)

        exitAct = QAction(QIcon('exit2.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.centralWidget().close)
        exitAct.triggered.connect(qApp.closeAllWindows)        
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        #self.statusBar().showMessage('Ready')
        self.setWindowTitle('Amber Kinetics Power Board GUI')  
        self.setWindowIcon(QIcon('A.png'))
        self.setGeometry(200, 200, 1400, 700)
 
    def updateModelData(self):
        return 
    
    def loadTableData(self):
        '''
        This is called after a path to the config file is obtained. 
        The config file is a csv.
        '''
        self.data = pd.read_excel(self.ConfigFilePath, 'Report')
        self.model = PandasModel(self.data)
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
    '''
    This class controls whether the StartTestButton is enabled or not. 
    It is enabled if the operator has entered a valid DUT serial number, 
    and all the instruments are connected. 
    '''   
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
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            #print(fileName)
            self.ConfigFileLineEdit.setText(fileName)
            self.ConfigFilePath = fileName
            self.ConfigFileLineEdit.editingFinished.emit()

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())