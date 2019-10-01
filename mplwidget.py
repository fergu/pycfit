from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib

class MPLWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi()
        self.maskingSetting = False;
        self.rectSelect = RectangleSelector(self.ax, self.maskSelected,
                                       drawtype='box', useblit=True,
                                       interactive=False)
        self.rectSelect.set_active(False);
        self.dataArtist = matplotlib.lines.Line2D([],[],linestyle='',marker='.',markerfacecolor='b');
        self.ax.add_line(self.dataArtist)
        self.maskArtist = matplotlib.lines.Line2D([],[],linestyle='',marker='x',markerfacecolor='r',markeredgecolor='r');
        self.ax.add_line(self.maskArtist)
        self.fitArtist = matplotlib.lines.Line2D([],[],linestyle='--',color='k');
        self.ax.add_line(self.fitArtist)

    def setupUi(self):
        layout = QtWidgets.QVBoxLayout(self);
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()
        self.show()

    def setDataManager(self,dm):
        self.dataManager = dm;
        self.dataManager.attach(self.dataUpdated)

    def maskSelect(self,setting):
        self.maskingSetting = setting;
        self.rectSelect.set_active(True);

    # FIXME: This won't work yet
    def maskSelected(self,click,release): # This function starts the rectangle selection on the figure and returns an array of whether or not the n-th point was in the selection
        self.rectSelect.set_active(False);
        lowerLeft = [min(click.xdata,release.xdata), min(click.ydata,release.ydata)]
        upperRight = [max(click.xdata,release.xdata), max(click.ydata,release.ydata)]
        data = self.dataManager.data;
        dataX = data[:,0]
        dataY = data[:,1]
        mask = (dataX > lowerLeft[0]) & (dataX < upperRight[0]) & (dataY > lowerLeft[1]) & (dataY < upperRight[1])
        self.dataManager.updateMask(mask, self.maskingSetting)

    def dataUpdated(self,sender,name=None):
        if(name=="FitStarted"):
            return;
        if (self.dataManager.dataIsValid is True):
            data = sender.data
            # mask = sender.mask
            # This may need to include the mask usage. I'm not sure.
            self.dataArtist.set_xdata(data[~data.mask[:,0],0].data); self.dataArtist.set_ydata(data[~data.mask[:,1],1].data)
            self.maskArtist.set_xdata(data[data.mask[:,0],0].data); self.maskArtist.set_ydata(data[data.mask[:,1],1].data)
            self.ax.relim();
            self.ax.autoscale()
        if (self.dataManager.fitfuncIsValid is True and self.dataManager.fit is not None):
            self.fitArtist.set_xdata(sender.fit[:,0]); self.fitArtist.set_ydata(sender.fit[:,1])
        else:
            self.fitArtist.set_xdata([]); self.fitArtist.set_ydata([])
        self.canvas.draw()
