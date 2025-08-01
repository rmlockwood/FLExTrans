# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RuleCatsAndAttribs.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CatsAndAttribsWindow(object):
    def setupUi(self, CatsAndAttribsWindow):
        CatsAndAttribsWindow.setObjectName("CatsAndAttribsWindow")
        CatsAndAttribsWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        CatsAndAttribsWindow.resize(414, 262)
        CatsAndAttribsWindow.setWindowTitle("Set Up Transfer Rule Categories & Attributes")
        CatsAndAttribsWindow.setAnimated(False)
        self.centralwidget = QtWidgets.QWidget(CatsAndAttribsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.overrideFeaturesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.overrideFeaturesCheckbox.setEnabled(True)
        self.overrideFeaturesCheckbox.setGeometry(QtCore.QRect(80, 53, 331, 17))
        self.overrideFeaturesCheckbox.setToolTip("")
        self.overrideFeaturesCheckbox.setChecked(True)
        self.overrideFeaturesCheckbox.setObjectName("overrideFeaturesCheckbox")
        self.PopulateFeaturesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateFeaturesCheckbox.setGeometry(QtCore.QRect(60, 30, 351, 17))
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
        self.overrideClassesCheckbox.setGeometry(QtCore.QRect(80, 103, 331, 17))
        self.overrideClassesCheckbox.setToolTip("")
        self.overrideClassesCheckbox.setChecked(True)
        self.overrideClassesCheckbox.setObjectName("overrideClassesCheckbox")
        self.PopulateClassesCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateClassesCheckbox.setGeometry(QtCore.QRect(60, 80, 351, 17))
        self.PopulateClassesCheckbox.setChecked(True)
        self.PopulateClassesCheckbox.setObjectName("PopulateClassesCheckbox")
        self.PopulateSlotsCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.PopulateSlotsCheckbox.setGeometry(QtCore.QRect(60, 127, 351, 17))
        self.PopulateSlotsCheckbox.setObjectName("PopulateSlotsCheckbox")
        self.overrideSlotsCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.overrideSlotsCheckbox.setEnabled(False)
        self.overrideSlotsCheckbox.setGeometry(QtCore.QRect(80, 150, 331, 17))
        self.overrideSlotsCheckbox.setToolTip("")
        self.overrideSlotsCheckbox.setChecked(True)
        self.overrideSlotsCheckbox.setObjectName("overrideSlotsCheckbox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(60, 180, 311, 41))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        CatsAndAttribsWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(CatsAndAttribsWindow)
        QtCore.QMetaObject.connectSlotsByName(CatsAndAttribsWindow)
        CatsAndAttribsWindow.setTabOrder(self.PopulateFeaturesCheckbox, self.overrideFeaturesCheckbox)
        CatsAndAttribsWindow.setTabOrder(self.overrideFeaturesCheckbox, self.PopulateClassesCheckbox)
        CatsAndAttribsWindow.setTabOrder(self.PopulateClassesCheckbox, self.overrideClassesCheckbox)
        CatsAndAttribsWindow.setTabOrder(self.overrideClassesCheckbox, self.PopulateSlotsCheckbox)
        CatsAndAttribsWindow.setTabOrder(self.PopulateSlotsCheckbox, self.overrideSlotsCheckbox)
        CatsAndAttribsWindow.setTabOrder(self.overrideSlotsCheckbox, self.OKButton)
        CatsAndAttribsWindow.setTabOrder(self.OKButton, self.CancelButton)

    def retranslateUi(self, CatsAndAttribsWindow):
        _translate = QtCore.QCoreApplication.translate
        self.overrideFeaturesCheckbox.setText(_translate("CatsAndAttribsWindow", "Overwrite existing inflection feature attributes"))
        self.PopulateFeaturesCheckbox.setText(_translate("CatsAndAttribsWindow", "Populate inflection features as attributes"))
        self.OKButton.setText(_translate("CatsAndAttribsWindow", "OK"))
        self.CancelButton.setText(_translate("CatsAndAttribsWindow", "Cancel"))
        self.overrideClassesCheckbox.setText(_translate("CatsAndAttribsWindow", "Overwrite existing inflection class attributes"))
        self.PopulateClassesCheckbox.setText(_translate("CatsAndAttribsWindow", "Populate inflection classes as attributes"))
        self.PopulateSlotsCheckbox.setText(_translate("CatsAndAttribsWindow", "Populate template slots as attributes"))
        self.overrideSlotsCheckbox.setText(_translate("CatsAndAttribsWindow", "Overwrite existing template slot attributes"))
        self.label.setText(_translate("CatsAndAttribsWindow", "Source categories and the a_gram_cat attribute are populated automatically. Existing source categories are not overwritten."))
