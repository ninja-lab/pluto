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
from PyQt5.QtWidgets import QWidget, QApplication, QTableView,QVBoxLayout
import sys
from PandasModel2 import  PandasModel2
import numpy as np
import pandas as pd

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle("QTableView")
        self.initData()
        self.initUI()
        
    def initData(self):
        data = pd.DataFrame(np.random.randint(1,10, size=(6,4)), columns=['TEST #','MIN', 'MAX','MEASURED'])
        data['MEASURED'][2] = np.nan
        data['TEST #'] = [1,2,3,4.1,4.2,4.3]   
        data['MIN'] = [1, 2, 3, 4, 5, 6]
        data['MAX'] = [5,4, 4, 9, 9, 9]                
        #add the checkable column to the DataFrame
        data['Check'] = True
        self.model = PandasModel2(data)
        for df in self.model.getCheckedTests2():
            print(df)

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
