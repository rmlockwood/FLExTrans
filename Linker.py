# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Linker.ui'
#
# Created: Thu Jun 16 09:53:04 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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
        self.tableView = QtGui.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(10, 50, 835, 351))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.OKButton = QtGui.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(260, 400, 90, 25))
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.CancelButton = QtGui.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(390, 400, 90, 25))
        self.CancelButton.setObjectName(_fromUtf8("CancelButton"))
        self.targetLexCombo = QtGui.QComboBox(self.centralwidget)
        self.targetLexCombo.setGeometry(QtCore.QRect(160, 10, 361, 29))
        self.targetLexCombo.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.targetLexCombo.setObjectName(_fromUtf8("targetLexCombo"))
        self.FilterCheckBox = QtGui.QCheckBox(self.centralwidget)
        self.FilterCheckBox.setGeometry(QtCore.QRect(550, 10, 221, 27))
        self.FilterCheckBox.setObjectName(_fromUtf8("FilterCheckBox"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 23))
        self.label.setObjectName(_fromUtf8("label"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1372, 36))
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
        self.targetLexCombo.setToolTip(_translate("MainWindow", "After selecting the desired sense here, double-click in the target head word column for the desired row to copy it.", None))
        self.FilterCheckBox.setText(_translate("MainWindow", "Show Only Unlinked", None))
        self.label.setText(_translate("MainWindow", "All Target Senses:", None))

