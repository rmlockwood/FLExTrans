# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SrcTgtViewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(891, 670)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.webView = QWebEngineView(self.centralwidget)
        self.webView.setGeometry(QtCore.QRect(10, 10, 871, 591))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.webView.setFont(font)
#        self.webView.setProperty("zoomFactor", 1.0)
        self.webView.setObjectName("webView")
        self.OKButton = QtWidgets.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(790, 620, 90, 25))
        self.OKButton.setObjectName("OKButton")
        self.FontButton = QtWidgets.QPushButton(self.centralwidget)
        self.FontButton.setGeometry(QtCore.QRect(10, 620, 90, 25))
        self.FontButton.setObjectName("FontButton")
        self.SourceRadio = QtWidgets.QRadioButton(self.centralwidget)
        self.SourceRadio.setGeometry(QtCore.QRect(242, 622, 71, 20))
        self.SourceRadio.setChecked(True)
        self.SourceRadio.setObjectName("SourceRadio")
        self.TargetRadio = QtWidgets.QRadioButton(self.centralwidget)
        self.TargetRadio.setGeometry(QtCore.QRect(315, 622, 61, 20))
        self.TargetRadio.setObjectName("TargetRadio")
        self.RTL = QtWidgets.QCheckBox(self.centralwidget)
        self.RTL.setGeometry(QtCore.QRect(430, 622, 101, 20))
        self.RTL.setObjectName("RTL")
        self.FontNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.FontNameLabel.setGeometry(QtCore.QRect(114, 622, 110, 20))
        self.FontNameLabel.setObjectName("FontNameLabel")
        self.ZoomIncrease = QtWidgets.QPushButton(self.centralwidget)
        self.ZoomIncrease.setGeometry(QtCore.QRect(590, 620, 21, 25))
        self.ZoomIncrease.setObjectName("ZoomIncrease")
        self.ZoomDecrease = QtWidgets.QPushButton(self.centralwidget)
        self.ZoomDecrease.setGeometry(QtCore.QRect(620, 620, 21, 25))
        self.ZoomDecrease.setObjectName("ZoomDecrease")
        self.ZoomLabel = QtWidgets.QLabel(self.centralwidget)
        self.ZoomLabel.setGeometry(QtCore.QRect(540, 622, 41, 20))
        self.ZoomLabel.setObjectName("ZoomLabel")
        self.linkLabel = QtWidgets.QLabel(self.centralwidget)
        self.linkLabel.setGeometry(QtCore.QRect(660, 622, 101, 20))
        self.linkLabel.setTextFormat(QtCore.Qt.RichText)
        self.linkLabel.setOpenExternalLinks(True)
        self.linkLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.linkLabel.setObjectName("linkLabel")
        self.targetRadio1 = QtWidgets.QRadioButton(self.centralwidget)
        self.targetRadio1.setGeometry(QtCore.QRect(380, 602, 31, 20))
        self.targetRadio1.setObjectName("targetRadio1")
        self.targetRadio2 = QtWidgets.QRadioButton(self.centralwidget)
        self.targetRadio2.setGeometry(QtCore.QRect(380, 622, 31, 20))
        self.targetRadio2.setObjectName("targetRadio2")
        self.targetRadio3 = QtWidgets.QRadioButton(self.centralwidget)
        self.targetRadio3.setGeometry(QtCore.QRect(380, 642, 31, 20))
        self.targetRadio3.setObjectName("targetRadio3")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Source/Target Viewer"))
        self.OKButton.setText(_translate("MainWindow", "OK"))
        self.FontButton.setText(_translate("MainWindow", "Font"))
        self.SourceRadio.setText(_translate("MainWindow", "Source"))
        self.TargetRadio.setText(_translate("MainWindow", "Target"))
        self.RTL.setText(_translate("MainWindow", "Right to Left"))
        self.FontNameLabel.setText(_translate("MainWindow", "Arial"))
        self.ZoomIncrease.setText(_translate("MainWindow", "+"))
        self.ZoomDecrease.setText(_translate("MainWindow", "–"))
        self.ZoomLabel.setText(_translate("MainWindow", "Zoom:"))
        self.linkLabel.setText(_translate("MainWindow", "<a href=\"file:///C:/Users/Ron/AppData/Local/Temp/FlexTransFileViewer.html\">Open in Browser</a>"))
        self.targetRadio1.setText(_translate("MainWindow", "1"))
        self.targetRadio2.setText(_translate("MainWindow", "2"))
        self.targetRadio3.setText(_translate("MainWindow", "3"))