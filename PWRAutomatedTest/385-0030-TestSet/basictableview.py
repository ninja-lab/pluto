#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
ZetCode Advanced PyQt5 tutorial 

This is a basic QTableView example.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
'''

#from PySide2.QtWidgets import (QWidget, QApplication, QTableView,
#        QVBoxLayout)
#from PySide2.QtGui import QStandardItemModel, QStandardItem
#import PySide2.QtCore as QtCore

from PyQt5.QtWidgets import QWidget, QApplication, QTableView, QVBoxLayout
#from PySide2.QtCore import QtCore

import sys
from PandasModel import  PandasModel
#import numpy as np
import pandas as pd

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setGeometry(300, 300, 1200, 300)
        self.setWindowTitle("QTableView")
        self.initData()
        self.initUI()
        
    def initData(self):
        data = pd.read_excel('PWR_Board_TestReportTemplate2.xlsx', 'Report')
        #otherwise the TIMESTAMP column is loaded as NaN which is float
        data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'])
        data['PASS/FAIL'] = data['PASS/FAIL'].astype(str)
        #add the checkable column to the DataFrame
        data['Check'] = True
        self.model = PandasModel(data)
        #self.model.setData(self.model.index(1,5),999)
    def initUI(self):
             
        self.tv = QTableView(self)
        #self.tv.setSelectionMode(QAbstractItemView.SingleSelection)
        #self.tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        #delegate = myDelegate(None)
        #self.tv.setItemDelegateForColumn(10, delegate)
        self.tv.setModel(self.model)
        #self.model.setData(self.model.index(2,2),QtGui.QBrush(
        #       QtCore.Qt.red), QtCore.Qt.BackgroundRole)
        vbox = QVBoxLayout()
        vbox.addWidget(self.tv) 
        self.setLayout(vbox)  

app = QApplication([])
ex = Example()
ex.show()
sys.exit(app.exec_())
