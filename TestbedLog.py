# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TestbedLog.ui'
#
# Created: Fri Jul 06 21:21:03 2018
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
        MainWindow.resize(900, 546)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.logTreeView = QtGui.QTreeView(self.centralwidget)
        self.logTreeView.setObjectName(_fromUtf8("logTreeView"))
        self.verticalLayout.addWidget(self.logTreeView)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.OKButton = QtGui.QPushButton(self.centralwidget)
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.horizontalLayout_2.addWidget(self.OKButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.editTestbedButton = QtGui.QPushButton(self.centralwidget)
        self.editTestbedButton.setObjectName(_fromUtf8("editTestbedButton"))
        self.horizontalLayout_2.addWidget(self.editTestbedButton)
        spacerItem2 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.ZoomLabel = QtGui.QLabel(self.centralwidget)
        self.ZoomLabel.setObjectName(_fromUtf8("ZoomLabel"))
        self.horizontalLayout_2.addWidget(self.ZoomLabel)
        self.fontSizeSpinBox = QtGui.QSpinBox(self.centralwidget)
        self.fontSizeSpinBox.setObjectName(_fromUtf8("fontSizeSpinBox"))
        self.horizontalLayout_2.addWidget(self.fontSizeSpinBox)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Testbed Log", None))
        self.OKButton.setText(_translate("MainWindow", "OK", None))
        self.editTestbedButton.setText(_translate("MainWindow", "Edit Testbed", None))
        self.ZoomLabel.setText(_translate("MainWindow", "Font Size:", None))

