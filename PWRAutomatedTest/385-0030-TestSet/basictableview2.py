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
from PyQt5.QtWidgets import QWidget, QApplication, QTableView,QVBoxLayout, QLabel
import sys
from PandasModel2 import  PandasModel2
import numpy as np
import pandas as pd
import os

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle("QTableView")
        self.initData()
        self.initUI()
        
    def initData(self):
        '''
        data = pd.DataFrame(np.random.randint(1,10, size=(12,4)), columns=['TEST #','MIN', 'MAX','MEASURED'])
        data['MEASURED'][2] = np.nan
        data['NAME'] = ['a','b','c','d','e','f','g','h','i','j','k','l']
        data['TEST #'] = [1,2,3,4.1,4.2,4.3,5.1,5.2,5.3,6.1,6.2,6.3]   
        data['MIN'] = list(range(len(data['TEST #']))) #[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        data['MAX'] = list(range(len(data['TEST #'])))#[5,4, 4, 9, 9, 9 ,17, 18, 19, 20, 21, 22]                
        #add the checkable column to the DataFrame
        data['Check'] = True
        self.model = PandasModel2(data)
        print(data)
        for df in self.model.getCheckedTests2():
            print(df)
            print(df[df['NAME']=='a']['MEASURED'])
            
        
        w=QtWidgets.QWidget()
        l1 = QtWidgets.QLabel(w)
        l1.setText('This is a test error prompt')
        w.setWindowTitle('Test Error')
        w.show()
        '''
        data = pd.DataFrame(np.random.randint(1,10, size=(12,4)), columns=['TEST #','MIN', 'MAX','MEASURED'])
        data['MEASURED'][2] = np.nan
        data['NAME'] = ['a','b','c','a','b','c','a','b','c','a','b','c']
        data['TEST #'] = [3.1,3.2,3.3,4.1,4.2,4.3,5.1,5.2,5.3,6.1,6.2,6.3]   
        data['MIN'] = list(range(len(data['TEST #']))) #[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        data['MAX'] = list(range(len(data['TEST #'])))#[5,4, 4, 9, 9, 9 ,17, 18, 19, 20, 21, 22]                
        #add the checkable column to the DataFrame
        data['Check'] = True
        self.model = PandasModel2(data)
        print(data)
        #flag = False
        '''
        for df in self.model.getCheckedTests2():
            print(df)
            print(df[df['NAME']=='b']['MEASURED'].iloc[0])
            if 9 == df['MAX'].iloc[0]:
                flag = True
            elif 18 == df['MAX'].iloc[0] and flag:
                print('Test 1')
                flag = False
        
        self.SaveFilePath = 'C:\\Users\\Ivan Moon\\Documents\\AK M32 Documents\\Power Board Test csv files\\_TEST_CSV_.csv'
        data.to_csv(self.SaveFilePath)
        '''
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
