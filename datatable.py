from PyQt5 import QtWidgets,QtCore
import numpy as np

class DataTable(QtWidgets.QTableWidget):
    def __init__(self,parent):
        super().__init__();
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def setDataManager(self,dataManager):
        self.datamanager = dataManager;
        dataManager.attach(self.dataUpdated)

    def dataUpdated(self,sender,name=None):
        if (sender.dataIsValid is False):
            return;
        data = sender.data;
        datashp = data.shape
        self.setRowCount(datashp[0])
        self.setColumnCount(2)
        for i in range(0,datashp[0]):
            for j in range(0,datashp[1]):
                item = QtWidgets.QTableWidgetItem(str(data[i,j]))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.setItem(i,j,item)
