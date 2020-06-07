import requests
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from gui import *
from scipy import interpolate
from PyQt5.QtWidgets import *
import sys
import os


class Gui(Ui_MainWindow):
    days = []
    highList = []
    lowlist = []
    option = 0

    def __init__(self, window):
        super(Gui, self).__init__()
        self.setupUi(window)
        self.setCurrency()
        self.DayRange.valueChanged.connect(lambda: self.slider())
        self.ChooseCurrency.currentIndexChanged.connect(lambda: self.setCurrency())
        self.SearchButton.clicked.connect(lambda: self.catchdata())
        self.DayRange.sliderReleased.connect(lambda: self.sliderSet())
        self.ChooseGraph.currentIndexChanged.connect(lambda: self.setGraph())

    def execDraw(self):
        draw = Window()
        draw.exec_()

    def slider(self):
        self.LimitInfo.setText(str(self.DayRange.value()))
        limit = str(self.DayRange.value())

    def sliderSet(self):
        lambda: self.catchdata()
        self.tableWidget.setRowCount((self.DayRange.value()) + 1)

    def setGraph(self):
        self.option = self.ChooseGraph.currentIndex()
        self.catchdata()

    def setCurrency(self):
        currency = self.ChooseCurrency.currentText()
        self.catchdata()

    def catchdata(self):
        # wyszukiwanie danych
        limit = str(self.DayRange.value())
        currency = str(self.ChooseCurrency.currentText())
        cryptoName = str(self.CryptoInput.toPlainText())
        url = (
                "https://min-api.cryptocompare.com/data/v2/histoday?fsym=" + cryptoName + "&tsym=" + currency + "&limit=" + limit)

        try:
            request = requests.get(url).json()
            request = request['Data']['Data']
        except Exception:
            self.msg.show()
            self.CryptoInput.setText("BTC")
            self.CryptoInput.setAlignment(QtCore.Qt.AlignCenter)
            cryptoName = "BTC"
            url = (
                    "https://min-api.cryptocompare.com/data/v2/histoday?fsym=" + cryptoName + "&tsym=" + currency + "&limit=" + limit)
            request = requests.get(url).json()
            request = request['Data']['Data']
        dateList = []
        highList = []
        lowlist = []
        for t in request:
            dateList.append(t['time'])

        for t in request:
            highList.append(t['high'])

        for t in request:
            lowlist.append(t['low'])

        volume = t['volumeto']

        days = []
        i = 0
        for t in dateList:
            dt_object = datetime.fromtimestamp(t)
            dt_object = dt_object.date()
            dt_object = dt_object.strftime("%d/%m")
            days.append(dt_object)
            i = i + 1
        self.VolumeIn.setText(str(volume) + " " + currency)
        self.tableWidget.setRowCount((self.DayRange.value()) + 1)
        for row in range((self.DayRange.value()) + 1):
            self.tableWidget.setItem(row, 0,
                                     QTableWidgetItem(str(datetime.fromtimestamp(dateList[row]).strftime("%d.%m.%Y"))))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(highList[row]) + " " + currency))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(lowlist[row]) + " " + currency))

        self.days = days
        self.highList = highList
        self.lowlist = lowlist

        if self.option == 2:
            self.interpol(lowlist)
        elif self.option == 1:
            self.interpol(highList)
        else:
            self.approximate()

        self.pic.setPixmap(QtGui.QPixmap(os.getcwd() + "/temp.png"))

    def interpol(self, selList):
        x = np.arange(0, len(self.days))
        f = interpolate.interp1d(x, selList)
        ynew = f(x)
        plt.plot(self.days, selList, 'o', self.days, ynew, '-')
        plt.xticks(x, self.days, rotation='vertical')
        plt.savefig('temp.png', dpi=67)
        plt.clf()

    def approximate(self):
        xy = []
        xy.append(np.arange(0, len(self.days)))
        xy.append(self.highList)
        xy.append(self.lowlist)

        hold = np.polyfit(xy[0], xy[1], len(self.days) / 2)
        xinterp = np.arange(0, len(self.days))
        yinterp = np.polyval(hold, xinterp)
        plt.plot(self.days, yinterp, '-', self.days, self.highList, 'o', self.days, self.lowlist, '.')
        plt.xticks(xinterp, self.days, rotation='vertical')
        plt.savefig('temp.png', dpi=67)
        plt.clf()


app = QApplication(sys.argv)
MainWindow = QMainWindow()

ui = Gui(MainWindow)
MainWindow.show()
app.exec_()
