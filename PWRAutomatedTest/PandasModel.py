# -*- coding: utf-8 -*-
"""
Created on Thu Feb  7 07:36:13 2019

@author: Erik
"""

import PyQt5.QtCore as QtCore

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled
    
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
        self._data.iat[index.row(),index.column()]= value
        self.layoutChanged.emit()
        return True


