import sys
import time

import numpy as np
np.set_printoptions(precision=5)
import scipy.optimize as sopt

from PyQt5 import QtGui, QtCore, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
import PyQt5.QtCore as qtcore

Ui_MainWindow, QMainWindow = uic.loadUiType("pycfitgui.ui")

import inspect

import warnings
warnings.simplefilter('always', sopt.OptimizeWarning)

import datamanager as dm

class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


class ApplicationWindow(QMainWindow, Ui_MainWindow):
    dataUpdated = QtCore.pyqtSignal(np.ndarray,np.ndarray)
    def __init__(self):
        super(ApplicationWindow,self).__init__()
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.dataManager = dm.DataManager()
        self.DataTable.setDataManager(self.dataManager);
        self.MPLWidget.setDataManager(self.dataManager);
        # self.VarGuesses.setDataManager(self.dataManager);
        self.dataManager.attach(self.dataUpdated);
        # sys.stderr = Stream(newText=self.onUpdateText)
        # sys.stdout = Stream(newText=self.onUpdateText)

    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def onUpdateText(self, text):
        self.LogTextView.insertPlainText(text)
        self.LogTextView.ensureCursorVisible()

    def dataUpdated(self,sender,name=None):
        self.EqnValidBox.setChecked(sender.fitfuncIsValid)
        currSetting = self.VariableSelector.currentText();
        self.VariableSelector.clear()
        if (self.dataManager.fitfuncIsValid):
            self.VariableSelector.addItems(self.dataManager.fitfuncVariables['args'][1:])
            if (self.VariableSelector.findText(currSetting) != -1):
                self.VariableSelector.setCurrentText(currSetting)
        if (name=="FitStarted"):
            self.LogTextView.clear();


    def EnablePointsClicked(self,other):
        if (self.dataManager.dataIsValid is False): # Just a catch so we don't try to select points when there's none to select
            return;
        self.MPLWidget.maskSelect(False);

    def DisablePointsClicked(self,other):
        if (self.dataManager.dataIsValid is False): # Just a catch so we don't try to select points when there's none to select
            return;
        self.MPLWidget.maskSelect(True);

    def fitfuncChanged(self,str):
        self.dataManager.setFitFunc(str);

    def FitParamsChanged(self,str):
        try:
            newGuess = float(self.InitGuessBox.text());
            newLower = float(self.LowerBoundBox.text());
            newUpper = float(self.UpperBoundBox.text());
            varName = self.VariableSelector.currentText();
            print("Varname: "+varName);
            self.dataManager.updateParams(varName,[newGuess,newLower,newUpper])
        except Exception as e:
            print("Something went wrong converting fit parameters to floats")
            print(e)

    def VariableSelectorChanged(self,newStr):
        if not newStr: # We need to catch if the selector changed to blank
            return;
        try:
            values = self.dataManager.fitfuncVariables[newStr]
            self.InitGuessBox.setText(str(values[0]))
            self.LowerBoundBox.setText(str(values[1]))
            self.UpperBoundBox.setText(str(values[2]))
            self.FitValueBox.setText(str(values[3]))
            self.LowerConfBox.setText(str(values[4]))
            self.UpperConfBox.setText(str(values[5]))
        except Exception as e:
            print("Something went wrong setting the fields")
            print(e)

    def dragEnterEvent(self,e):
        if (e.mimeData().hasUrls() and len(e.mimeData().urls()) < 2): # A drag-and-dropped file will appear as a URL with the file path
            e.accept()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self,e):
        if (e.mimeData().hasUrls() and len(e.mimeData().urls()) < 2): # A drag-and-dropped file will appear as a URL with the file path
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self,e):
        if (e.mimeData().hasUrls() and len(e.mimeData().urls()) < 2): # A drag-and-dropped file will appear as a URL with the file path
            e.setDropAction(QtCore.Qt.CopyAction)
            url = e.mimeData().urls()[0]
            try:
                dat = np.loadtxt(url.toLocalFile()) # Need to add some additional logic to handle parsing the data in to the right format
            except:
                super().dropEvent(e);
                return;
            self.dataManager.setData(dat)
            e.accept()
        else:
            super().dropEvent(e)

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()
