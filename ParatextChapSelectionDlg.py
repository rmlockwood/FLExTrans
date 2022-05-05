# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ParatextChapSelection.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(316, 236)
        MainWindow.setAnimated(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.makeActiveTextCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.makeActiveTextCheckBox.setGeometry(QtCore.QRect(100, 130, 181, 17))
        self.makeActiveTextCheckBox.setChecked(True)
        self.makeActiveTextCheckBox.setObjectName("makeActiveTextCheckBox")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(50, 37, 151, 21))
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.fromChapterSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.fromChapterSpinBox.setGeometry(QtCore.QRect(120, 70, 42, 22))
        self.fromChapterSpinBox.setMinimum(1)
        self.fromChapterSpinBox.setMaximum(150)
        self.fromChapterSpinBox.setObjectName("fromChapterSpinBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 7, 151, 21))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(180, 70, 21, 21))
        self.label_3.setObjectName("label_3")
        self.useFullBookNameForTitleCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.useFullBookNameForTitleCheckBox.setGeometry(QtCore.QRect(100, 153, 191, 17))
        self.useFullBookNameForTitleCheckBox.setChecked(True)
        self.useFullBookNameForTitleCheckBox.setObjectName("useFullBookNameForTitleCheckBox")
        self.footnotesCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.footnotesCheckBox.setGeometry(QtCore.QRect(100, 107, 111, 17))
        self.footnotesCheckBox.setObjectName("footnotesCheckBox")
        self.ptxProjAbbrevLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.ptxProjAbbrevLineEdit.setGeometry(QtCore.QRect(210, 7, 51, 20))
        self.ptxProjAbbrevLineEdit.setObjectName("ptxProjAbbrevLineEdit")
        self.bookAbbrevLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.bookAbbrevLineEdit.setGeometry(QtCore.QRect(210, 37, 51, 20))
        self.bookAbbrevLineEdit.setObjectName("bookAbbrevLineEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(70, 70, 51, 21))
        self.label_2.setObjectName("label_2")
        self.toChapterSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.toChapterSpinBox.setGeometry(QtCore.QRect(200, 70, 42, 22))
        self.toChapterSpinBox.setMinimum(1)
        self.toChapterSpinBox.setMaximum(150)
        self.toChapterSpinBox.setObjectName("toChapterSpinBox")
        self.OKButton = QtWidgets.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(70, 190, 81, 23))
        self.OKButton.setObjectName("OKButton")
        self.CancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(160, 190, 81, 23))
        self.CancelButton.setObjectName("CancelButton")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.ptxProjAbbrevLineEdit, self.bookAbbrevLineEdit)
        MainWindow.setTabOrder(self.bookAbbrevLineEdit, self.fromChapterSpinBox)
        MainWindow.setTabOrder(self.fromChapterSpinBox, self.toChapterSpinBox)
        MainWindow.setTabOrder(self.toChapterSpinBox, self.footnotesCheckBox)
        MainWindow.setTabOrder(self.footnotesCheckBox, self.makeActiveTextCheckBox)
        MainWindow.setTabOrder(self.makeActiveTextCheckBox, self.useFullBookNameForTitleCheckBox)
        MainWindow.setTabOrder(self.useFullBookNameForTitleCheckBox, self.OKButton)
        MainWindow.setTabOrder(self.OKButton, self.CancelButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Choose Chapters"))
        self.makeActiveTextCheckBox.setToolTip(_translate("MainWindow", "We will change the source text name for FLExTrans to the newly created text."))
        self.makeActiveTextCheckBox.setText(_translate("MainWindow", "Make new text the active text"))
        self.label_4.setText(_translate("MainWindow", "Book Abbreviation"))
        self.label.setText(_translate("MainWindow", "Paratext Project Abbreviation"))
        self.label_3.setText(_translate("MainWindow", "to"))
        self.useFullBookNameForTitleCheckBox.setToolTip(_translate("MainWindow", "Otherwise we will just use the book abbreviation."))
        self.useFullBookNameForTitleCheckBox.setText(_translate("MainWindow", "Use full English book name for title"))
        self.footnotesCheckBox.setText(_translate("MainWindow", "Include footnotes"))
        self.label_2.setText(_translate("MainWindow", "Chapter"))
        self.OKButton.setText(_translate("MainWindow", "OK"))
        self.CancelButton.setText(_translate("MainWindow", "Cancel"))
