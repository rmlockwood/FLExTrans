# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Linker.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1372, 701)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(10, 50, 835, 351))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.tableView.setFont(font)
        self.tableView.setObjectName("tableView")
        self.OKButton = QtWidgets.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(260, 400, 90, 25))
        self.OKButton.setObjectName("OKButton")
        self.CancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(390, 400, 90, 25))
        self.CancelButton.setObjectName("CancelButton")
        self.targetLexCombo = QtWidgets.QComboBox(self.centralwidget)
        self.targetLexCombo.setGeometry(QtCore.QRect(100, 10, 271, 29))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.targetLexCombo.setFont(font)
        self.targetLexCombo.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.targetLexCombo.setObjectName("targetLexCombo")
        self.ShowOnlyUnlinkedCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.ShowOnlyUnlinkedCheckBox.setGeometry(QtCore.QRect(590, 13, 121, 27))
        self.ShowOnlyUnlinkedCheckBox.setObjectName("ShowOnlyUnlinkedCheckBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 16, 151, 20))
        self.label.setObjectName("label")
        self.HideProperNounsCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.HideProperNounsCheckBox.setGeometry(QtCore.QRect(720, 13, 121, 27))
        self.HideProperNounsCheckBox.setObjectName("HideProperNounsCheckBox")
        self.searchTargetEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.searchTargetEdit.setGeometry(QtCore.QRect(384, 10, 191, 29))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchTargetEdit.setFont(font)
        self.searchTargetEdit.setObjectName("searchTargetEdit")
        self.sourceTextNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.sourceTextNameLabel.setGeometry(QtCore.QRect(860, 16, 501, 20))
        self.sourceTextNameLabel.setObjectName("sourceTextNameLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1372, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FLExTrans Sense Linker Tool"))
        self.OKButton.setText(_translate("MainWindow", "OK"))
        self.CancelButton.setText(_translate("MainWindow", "Cancel"))
        self.targetLexCombo.setToolTip(_translate("MainWindow", "After selecting the desired sense here, double-click in the Target Head Word column for the desired row to link to it."))
        self.ShowOnlyUnlinkedCheckBox.setText(_translate("MainWindow", "Show Only Unlinked"))
        self.label.setText(_translate("MainWindow", "All Target Senses:"))
        self.HideProperNounsCheckBox.setText(_translate("MainWindow", "Hide Proper Nouns"))
        self.searchTargetEdit.setToolTip(_translate("MainWindow", "Type the beginning of an entry, then double-click in the Target Head Word column for the desired row to link to it."))
        self.sourceTextNameLabel.setText(_translate("MainWindow", "Source Textname: XYZ"))
