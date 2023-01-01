# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RuleCatsAndAttribs.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(414, 262)
        MainWindow.setAnimated(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.overrideFeaturesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.overrideFeaturesCheckbox.setEnabled(True)
        self.overrideFeaturesCheckbox.setGeometry(QtCore.QRect(80, 53, 241, 17))
        self.overrideFeaturesCheckbox.setToolTip("")
        self.overrideFeaturesCheckbox.setChecked(True)
        self.overrideFeaturesCheckbox.setObjectName("overrideFeaturesCheckbox")
        self.PopulateFeaturesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateFeaturesCheckbox.setGeometry(QtCore.QRect(60, 30, 231, 17))
        self.PopulateFeaturesCheckbox.setChecked(True)
        self.PopulateFeaturesCheckbox.setObjectName("PopulateFeaturesCheckbox")
        self.OKButton = QtWidgets.QPushButton(self.centralwidget)
        self.OKButton.setGeometry(QtCore.QRect(120, 230, 81, 23))
        self.OKButton.setObjectName("OKButton")
        self.CancelButton = QtWidgets.QPushButton(self.centralwidget)
        self.CancelButton.setGeometry(QtCore.QRect(210, 230, 81, 23))
        self.CancelButton.setObjectName("CancelButton")
        self.overrideClassesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.overrideClassesCheckbox.setEnabled(True)
        self.overrideClassesCheckbox.setGeometry(QtCore.QRect(80, 103, 241, 17))
        self.overrideClassesCheckbox.setToolTip("")
        self.overrideClassesCheckbox.setChecked(True)
        self.overrideClassesCheckbox.setObjectName("overrideClassesCheckbox")
        self.PopulateClassesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateClassesCheckbox.setGeometry(QtCore.QRect(60, 80, 231, 17))
        self.PopulateClassesCheckbox.setChecked(True)
        self.PopulateClassesCheckbox.setObjectName("PopulateClassesCheckbox")
        self.PopulateSlotsCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateSlotsCheckbox.setGeometry(QtCore.QRect(60, 127, 231, 17))
        self.PopulateSlotsCheckbox.setObjectName("PopulateSlotsCheckbox")
        self.overrideSlotsCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.overrideSlotsCheckbox.setEnabled(False)
        self.overrideSlotsCheckbox.setGeometry(QtCore.QRect(80, 150, 241, 17))
        self.overrideSlotsCheckbox.setToolTip("")
        self.overrideSlotsCheckbox.setChecked(False)
        self.overrideSlotsCheckbox.setObjectName("overrideSlotsCheckbox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 180, 311, 41))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.PopulateFeaturesCheckbox, self.overrideFeaturesCheckbox)
        MainWindow.setTabOrder(self.overrideFeaturesCheckbox, self.PopulateClassesCheckbox)
        MainWindow.setTabOrder(self.PopulateClassesCheckbox, self.overrideClassesCheckbox)
        MainWindow.setTabOrder(self.overrideClassesCheckbox, self.PopulateSlotsCheckbox)
        MainWindow.setTabOrder(self.PopulateSlotsCheckbox, self.overrideSlotsCheckbox)
        MainWindow.setTabOrder(self.overrideSlotsCheckbox, self.OKButton)
        MainWindow.setTabOrder(self.OKButton, self.CancelButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Set Up Transfer Rule Categories & Attributes"))
        self.overrideFeaturesCheckbox.setText(_translate("MainWindow", "Override existing inflection feature attributes"))
        self.PopulateFeaturesCheckbox.setText(_translate("MainWindow", "Populate inflection features as attributes"))
        self.OKButton.setText(_translate("MainWindow", "OK"))
        self.CancelButton.setText(_translate("MainWindow", "Cancel"))
        self.overrideClassesCheckbox.setText(_translate("MainWindow", "Override existing inflection class attributes"))
        self.PopulateClassesCheckbox.setText(_translate("MainWindow", "Populate inflection classes as attributes"))
        self.PopulateSlotsCheckbox.setText(_translate("MainWindow", "Populate template slots as attributes"))
        self.overrideSlotsCheckbox.setText(_translate("MainWindow", "Override existing template slot attributes"))
        self.label.setText(_translate("MainWindow", "Source categories and the a_gram_cat attribute are populated automatically. Existing values for these are not overridden."))
