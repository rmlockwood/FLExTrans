# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OverWriteTestDlg.ui'
#
# Created: Sat Jun 02 10:00:44 2018
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

class Ui_OverWriteTest(object):
    def setupUi(self, OverWriteTest):
        OverWriteTest.setObjectName(_fromUtf8("OverWriteTest"))
        OverWriteTest.setWindowModality(QtCore.Qt.ApplicationModal)
        OverWriteTest.resize(539, 196)
        OverWriteTest.setWhatsThis(_fromUtf8(""))
        OverWriteTest.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(OverWriteTest)
        self.buttonBox.setGeometry(QtCore.QRect(30, 140, 481, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.NoToAll|QtGui.QDialogButtonBox.Yes|QtGui.QDialogButtonBox.YesToAll)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(OverWriteTest)
        self.label.setGeometry(QtCore.QRect(70, 30, 451, 81))
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(OverWriteTest)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OverWriteTest.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OverWriteTest.reject)
        QtCore.QMetaObject.connectSlotsByName(OverWriteTest)

    def retranslateUi(self, OverWriteTest):
        OverWriteTest.setWindowTitle(_translate("OverWriteTest", "Test Exists", None))
        self.label.setText(_translate("OverWriteTest", "There is a test that already exists in the testbed that matches the lexical unit XX. Do you want to overwrite it?", None))

