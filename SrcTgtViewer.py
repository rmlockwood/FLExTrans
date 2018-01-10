# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SrcTgtViewer.ui'
#
# Created: Mon Jan 01 13:07:00 2018
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
        MainWindow.resize(891, 702)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.webView = QtWebKit.QWebView(self.centralwidget)
        self.webView.setGeometry(QtCore.QRect(10, 10, 871, 591))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.webView.setFont(font)
        self.webView.setZoomFactor(1.0)
        self.webView.setObjectName(_fromUtf8("webView"))
        self.OKButton = QtGui.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(790, 620, 90, 25))
        self.OKButton.setObjectName(_fromUtf8("OKButton"))
        self.FontButton = QtGui.QPushButton(self.centralwidget)
        self.FontButton.setGeometry(QtCore.QRect(10, 620, 90, 25))
        self.FontButton.setObjectName(_fromUtf8("FontButton"))
        self.SourceRadio = QtGui.QRadioButton(self.centralwidget)
        self.SourceRadio.setGeometry(QtCore.QRect(252, 622, 71, 20))
        self.SourceRadio.setChecked(True)
        self.SourceRadio.setObjectName(_fromUtf8("SourceRadio"))
        self.TargetRadio = QtGui.QRadioButton(self.centralwidget)
        self.TargetRadio.setGeometry(QtCore.QRect(325, 622, 71, 20))
        self.TargetRadio.setObjectName(_fromUtf8("TargetRadio"))
        self.RTL = QtGui.QCheckBox(self.centralwidget)
        self.RTL.setGeometry(QtCore.QRect(410, 622, 101, 20))
        self.RTL.setObjectName(_fromUtf8("RTL"))
        self.FontNameLabel = QtGui.QLabel(self.centralwidget)
        self.FontNameLabel.setGeometry(QtCore.QRect(114, 622, 110, 20))
        self.FontNameLabel.setObjectName(_fromUtf8("FontNameLabel"))
        self.ZoomIncrease = QtGui.QPushButton(self.centralwidget)
        self.ZoomIncrease.setGeometry(QtCore.QRect(580, 620, 21, 25))
        self.ZoomIncrease.setObjectName(_fromUtf8("ZoomIncrease"))
        self.ZoomDecrease = QtGui.QPushButton(self.centralwidget)
        self.ZoomDecrease.setGeometry(QtCore.QRect(610, 620, 21, 25))
        self.ZoomDecrease.setObjectName(_fromUtf8("ZoomDecrease"))
        self.ZoomLabel = QtGui.QLabel(self.centralwidget)
        self.ZoomLabel.setGeometry(QtCore.QRect(530, 622, 41, 20))
        self.ZoomLabel.setObjectName(_fromUtf8("ZoomLabel"))
        self.linkLabel = QtGui.QLabel(self.centralwidget)
        self.linkLabel.setGeometry(QtCore.QRect(660, 622, 101, 20))
        self.linkLabel.setTextFormat(QtCore.Qt.RichText)
        self.linkLabel.setOpenExternalLinks(True)
        self.linkLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.linkLabel.setObjectName(_fromUtf8("linkLabel"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 891, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Source/Target Viewer", None))
        self.OKButton.setText(_translate("MainWindow", "OK", None))
        self.FontButton.setText(_translate("MainWindow", "Font", None))
        self.SourceRadio.setText(_translate("MainWindow", "Source", None))
        self.TargetRadio.setText(_translate("MainWindow", "Target", None))
        self.RTL.setText(_translate("MainWindow", "Right to Left", None))
        self.FontNameLabel.setText(_translate("MainWindow", "Arial", None))
        self.ZoomIncrease.setText(_translate("MainWindow", "+", None))
        self.ZoomDecrease.setText(_translate("MainWindow", "–", None))
        self.ZoomLabel.setText(_translate("MainWindow", "Zoom:", None))
        self.linkLabel.setText(_translate("MainWindow", "<a href=\"file:///C:/Users/Ron/AppData/Local/Temp/FlexTransFileViewer.html\">Open in Browser</a>", None))

from PyQt4 import QtWebKit
