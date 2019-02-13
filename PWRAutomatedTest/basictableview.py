#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
ZetCode Advanced PyQt5 tutorial 

This is a basic QTableView example.

Author: Jan Bodnar
Website: zetcode.com 
Last edited: August 2017
'''

from PyQt5.QtWidgets import (QWidget, QApplication, QTableView, 
        QVBoxLayout)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import sys
from .\PandasModel import  PandasModel
#import yaml
#myFile = open('config.yaml')
#data = yaml.load(myFile)
import numpy as np
import pandas as pd

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle("QTableView")
        self.initData()
        self.initUI()
        
    def initData(self):
    

        data =  pd.DataFrame(np.random.randn(6, 6))
        data[0][1] = 'hello'
        self.model = PandasModel(data)
        self.model.setData(self.model.index(1,5),999)
    def initUI(self):
             
        self.tv = QTableView(self)
        self.tv.setModel(self.model)
        vbox = QVBoxLayout()
        vbox.addWidget(self.tv) 
        self.setLayout(vbox)  

app = QApplication([])
ex = Example()
ex.show()
sys.exit(app.exec_())
