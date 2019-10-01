from PyQt5 import QtWidgets,QtCore
import numpy as np

class VarTable(QtWidgets.QTableWidget):
    def __init__(self,parent):
        super().__init__();
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def setDataManager(self,dataManager):
        self.datamanager = dataManager;
        dataManager.attach(self.dataUpdated)

    def dataUpdated(self,sender,name=None):
        if (sender.fitfuncIsValid is False):
            while (self.rowCount() > 0):
                self.removeRow(0)
            return;
        vars = sender.fitfuncVariables;
        nvars = len(vars)
        self.setRowCount(6)
        self.setColumnCount(nvars-1)
        self.setHorizontalHeaderLabels(vars[1:])
        self.setVerticalHeaderLabels(['Initial Guess','Lower Bound','Upper Bound','Fit Value','Lower 95%','Upper 95%'])
        for i in range(0,nvars-1):
            varName = vars[i+1]
            varData = self.datamanager.fitfuncVarParams[varName];
            for j in range(0,len(varData)):
                item = QtWidgets.QTableWidgetItem(str(varData[j]))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.setItem(j,i,item)

    def cellValueChanged(self,i,j):
        newValue = float(self.item(i,j).text());
        varName = self.horizontalHeaderItem(j).text()
        self.datamanager.updateParams(varName,i,newValue)
