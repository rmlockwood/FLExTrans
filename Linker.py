# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Linker.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import MyTableView

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1372, 701)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tableView = MyTableView.MyTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(10, 50, 835, 351))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        self.tableView.setFont(font)
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.OKButton = QtGui.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(260, 400, 90, 25))
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.CancelButton = QtGui.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(390, 400, 90, 25))
        self.CancelButton.setObjectName(_fromUtf8("CancelButton"))
        self.FilterCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.FilterCheckBox.setGeometry(QtCore.QRect(550, 10, 221, 27))
        self.FilterCheckBox.setObjectName(_fromUtf8("FilterCheckBox"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1372, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "FLExTrans Sense Linker Tool", None))
        self.OKButton.setText(_translate("MainWindow", "OK", None))
        self.CancelButton.setText(_translate("MainWindow", "Cancel", None))
        self.FilterCheckBox.setText(_translate("MainWindow", "Show Only Unlinked", None))

