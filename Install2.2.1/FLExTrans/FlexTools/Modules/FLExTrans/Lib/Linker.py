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
        MainWindow.resize(1156, 490)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(10, 50, 1131, 351))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.tableView.setFont(font)
        self.tableView.setObjectName("tableView")
        self.OKButton = QtWidgets.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(10, 410, 90, 25))
        self.OKButton.setObjectName("OKButton")
        self.CancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(110, 410, 90, 25))
        self.CancelButton.setObjectName("CancelButton")
        self.targetLexCombo = QtWidgets.QComboBox(self.centralwidget)
        self.targetLexCombo.setGeometry(QtCore.QRect(100, 10, 271, 29))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.targetLexCombo.setFont(font)
        self.targetLexCombo.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.targetLexCombo.setObjectName("targetLexCombo")
        self.ShowOnlyUnlinkedCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.ShowOnlyUnlinkedCheckBox.setGeometry(QtCore.QRect(210, 410, 121, 27))
        self.ShowOnlyUnlinkedCheckBox.setObjectName("ShowOnlyUnlinkedCheckBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 16, 151, 20))
        self.label.setObjectName("label")
        self.HideProperNounsCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.HideProperNounsCheckBox.setGeometry(QtCore.QRect(340, 410, 115, 27))
        self.HideProperNounsCheckBox.setObjectName("HideProperNounsCheckBox")
        self.searchTargetEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.searchTargetEdit.setGeometry(QtCore.QRect(384, 10, 191, 29))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchTargetEdit.setFont(font)
        self.searchTargetEdit.setObjectName("searchTargetEdit")
        self.SourceTextCombo = QtWidgets.QComboBox(self.centralwidget)
        self.SourceTextCombo.setGeometry(QtCore.QRect(800, 10, 341, 29))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.SourceTextCombo.setFont(font)
        self.SourceTextCombo.setMaxVisibleItems(30)
        self.SourceTextCombo.setObjectName("SourceTextCombo")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(730, 16, 65, 23))
        self.label_4.setObjectName("label_4")
        self.SearchAnythingCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.SearchAnythingCheckBox.setGeometry(QtCore.QRect(600, 13, 121, 27))
        self.SearchAnythingCheckBox.setObjectName("SearchAnythingCheckBox")
        self.ZoomDecrease = QtWidgets.QPushButton(self.centralwidget)
        self.ZoomDecrease.setGeometry(QtCore.QRect(540, 412, 21, 25))
        self.ZoomDecrease.setObjectName("ZoomDecrease")
        self.ZoomIncrease = QtWidgets.QPushButton(self.centralwidget)
        self.ZoomIncrease.setGeometry(QtCore.QRect(510, 412, 21, 25))
        self.ZoomIncrease.setObjectName("ZoomIncrease")
        self.ZoomLabel = QtWidgets.QLabel(self.centralwidget)
        self.ZoomLabel.setGeometry(QtCore.QRect(470, 414, 32, 20))
        self.ZoomLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.ZoomLabel.setObjectName("ZoomLabel")
        self.FontNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.FontNameLabel.setGeometry(QtCore.QRect(674, 414, 91, 20))
        self.FontNameLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.FontNameLabel.setObjectName("FontNameLabel")
        self.FontButton = QtWidgets.QPushButton(self.centralwidget)
        self.FontButton.setGeometry(QtCore.QRect(570, 410, 90, 25))
        self.FontButton.setObjectName("FontButton")
        self.RebuildBilingCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.RebuildBilingCheckBox.setGeometry(QtCore.QRect(790, 410, 151, 27))
        self.RebuildBilingCheckBox.setChecked(True)
        self.RebuildBilingCheckBox.setObjectName("RebuildBilingCheckBox")
        self.SensesToLinkLabel = QtWidgets.QLabel(self.centralwidget)
        self.SensesToLinkLabel.setGeometry(QtCore.QRect(10, 442, 71, 20))
        self.SensesToLinkLabel.setObjectName("SensesToLinkLabel")
        self.SensesRemainingLabel = QtWidgets.QLabel(self.centralwidget)
        self.SensesRemainingLabel.setGeometry(QtCore.QRect(82, 442, 31, 20))
        self.SensesRemainingLabel.setObjectName("SensesRemainingLabel")
        self.exportUnlinkedCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.exportUnlinkedCheckBox.setGeometry(QtCore.QRect(980, 410, 151, 27))
        self.exportUnlinkedCheckBox.setChecked(False)
        self.exportUnlinkedCheckBox.setObjectName("exportUnlinkedCheckBox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1156, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

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
        self.searchTargetEdit.setToolTip(_translate("MainWindow", "Type the beginning of an entry or any text (if \'search all fields\' is checked), \n"
"then double-click in the Target Head Word column for the desired row to link to it."))
        self.label_4.setText(_translate("MainWindow", "Source Text:"))
        self.SearchAnythingCheckBox.setText(_translate("MainWindow", "Search all fields"))
        self.ZoomDecrease.setText(_translate("MainWindow", "–"))
        self.ZoomIncrease.setText(_translate("MainWindow", "+"))
        self.ZoomLabel.setText(_translate("MainWindow", "Zoom:"))
        self.FontNameLabel.setText(_translate("MainWindow", "Arial"))
        self.FontButton.setText(_translate("MainWindow", "Font"))
        self.RebuildBilingCheckBox.setText(_translate("MainWindow", "Rebuild Bilingual Lexicon"))
        self.SensesToLinkLabel.setText(_translate("MainWindow", "Senses to link:"))
        self.SensesRemainingLabel.setText(_translate("MainWindow", "888"))
        self.exportUnlinkedCheckBox.setToolTip(_translate("MainWindow", "Export a list of unlinked senses to a file. If Hide Proper Nouns \n"
"is checked, Proper Nouns will not be exported."))
        self.exportUnlinkedCheckBox.setText(_translate("MainWindow", "Export Unlinked Senses"))