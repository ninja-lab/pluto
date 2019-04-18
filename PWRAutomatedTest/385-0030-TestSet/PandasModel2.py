# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 07:36:13 2019

@author: Erik
"""

#from PySide2 import QtCore, QtGui
from PyQt5 import QtCore, QtGui
import numpy as np
class PandasModel2(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe.
    This model is non-hierachical. 
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return
        if not (0 <= index.row() < self.rowCount() and 0 <= index.column() <= self.columnCount()):
            return
        value = self._data.iloc[index.row(), index.column()]
        if role == QtCore.Qt.DisplayRole:
            if index.column() != self.getColumnNumber('Check'): 
                if index.column() in [1,2,3]:
                    return '{:.3f}'.format(value)    
                if index.column() == 0:
                    return '{:.2f}'.format(value)
                return str(value)
        elif role == QtCore.Qt.CheckStateRole:  
            if index.column() == self.getColumnNumber('Check'):
                
                return QtCore.Qt.Checked if value else QtCore.Qt.Unchecked
        elif index.column() == self.getColumnNumber('MEASURED'):
            if role == QtCore.Qt.BackgroundRole:
                #print('value: {}, type: {}'.format(value, type(value)))
                if np.isnan(value):
                    return QtGui.QColor("red")
                elif (self.getMinimum(index.row()) > value) or (self.getMaximum(index.row()) < value):
                    #print('found failure')
                    return QtGui.QColor("red")
    
    def getMinimum(self, row):
        return self._data.iloc[row, self.getColumnNumber('MIN')]
    def getMaximum(self, row):
        return self._data.iloc[row, self.getColumnNumber('MAX')]
    
    def getColumnNumber(self, string):
        '''
        Given a string that identifies a label/column, 
        return the location of that label/column.
        This enables the config file columns to be moved around. 
        '''
        return self._data.columns.get_loc(string)

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
    def flags(self, index):
        '''
        The returned enums indicate which columns are editable, selectable, 
        checkable, etc. 
        The index is a QModelIndex. 
        '''
        if index.column() == self.getColumnNumber('Check'):
            #print(index.column())
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        #return QtCore.Qt.ItemIsEnabled
    
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        """Set the value to the index position depending on Qt::ItemDataRole and data type of the column
        Args:
            index (QtCore.QModelIndex): Index to define column and row.
            value (object): new value.
            role (Qt::ItemDataRole): Use this role to specify what you want to do.
        Raises:
            TypeError: If the value could not be converted to a known datatype.
        Returns:
            True if value is changed. Calls layoutChanged after update.
            False if value is not different from original value.
        """
        if not index.isValid(): 
            return False
        if role == QtCore.Qt.DisplayRole: #why not edit role?
            self._data.iat[index.row(),index.column()]= value
            self.layoutChanged.emit()
            return True
        elif role == (QtCore.Qt.CheckStateRole | QtCore.Qt.DisplayRole):
            #this block does get executed when toggling the check boxes, 
            #verified with debugger. Although the action is the same 
            #as the block above! 
            #coupled_rows = self.getCoupledRows(index.row())
            self._data.iat[index.row(),index.column()]= value
            #self._data.iat[index.row()+1,index.column()]= value
            for row in self.getCoupledRows(index.row()):
                self._data.iat[row, index.column()] = value
            self.layoutChanged.emit()
            #print(self.getCheckedTests())
            return True
        else:
            return False
    def getCoupledRows(self, row):
        #if row <= 2:
        #    return []
        #mask = self._data['TEST #'].values.astype(int) == int(self._data['TEST #'][row])
        #mask = self._data['TEST #'].values.astype(int) >= 4#int(self._data['TEST #'][row])
        test_num = 
        
        print('row: {}'.format(row))
        mask = self._data['TEST #'].values.astype(int) == row
        print('mask: ')
        print(mask)
        return self._data['TEST #'][mask].index
    def getCheckedTests(self):
        '''
        The GUI calls this method and sends the returned list
        to the Tester via TestCommand signal. 
        Return a list corresponding to the (consolidated) checked rows
        i.e. Tests 15.1 - 15.15 are consolidated as 15 
        '''
        mask = self._data['Check'].values == True
        tests = self._data['TEST #'][mask].values.astype(int) #a np array with duplicates
        myList = list(set(tests))
        myList.sort()                   
        return myList
    def getCheckedTests2(self):
        '''
        the GUI could call this method and all the checked info returned
        as either series or DataFrames, as appropriate. 
        The info is sent to the tester for use there:
            For threshold sweeps, the min and max are useful to save time. 
            The indexes are available so the Tester knows which rows to 
            write to using resultReady() signal. 
        '''
        mask = self._data['Check'].values == True
        checkedData = self._data[mask]
        alist = []            
        for i in self.getCheckedTests():
            alist.append(self._data.loc[self._data['TEST #'].astype(int) == i,:])
        return alist            

