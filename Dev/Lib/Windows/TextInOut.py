# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TextInOut.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TextInOutMainWindow(object):
    def setupUi(self, TextInOutMainWindow):
        TextInOutMainWindow.setObjectName("TextInOutMainWindow")
        TextInOutMainWindow.resize(540, 581)
        self.centralwidget = QtWidgets.QWidget(TextInOutMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 40, 521, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.layoutWidget.setFont(font)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.replaceLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.replaceLabel.setFont(font)
        self.replaceLabel.setObjectName("replaceLabel")
        self.horizontalLayout.addWidget(self.replaceLabel)
        self.replaceTextBox = QtWidgets.QLineEdit(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.replaceTextBox.setFont(font)
        self.replaceTextBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.replaceTextBox.setObjectName("replaceTextBox")
        self.horizontalLayout.addWidget(self.replaceTextBox)
        self.layoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 110, 231, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.layoutWidget_2.setFont(font)
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.buttonLayout = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.buttonLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setObjectName("buttonLayout")
        self.addButton = QtWidgets.QPushButton(self.layoutWidget_2)
        self.addButton.setEnabled(False)
        self.addButton.setMinimumSize(QtCore.QSize(40, 23))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.addButton.setFont(font)
        self.addButton.setObjectName("addButton")
        self.buttonLayout.addWidget(self.addButton)
        self.updateButton = QtWidgets.QPushButton(self.layoutWidget_2)
        self.updateButton.setEnabled(False)
        self.updateButton.setMinimumSize(QtCore.QSize(40, 23))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.updateButton.setFont(font)
        self.updateButton.setObjectName("updateButton")
        self.buttonLayout.addWidget(self.updateButton)
        self.deleteButton = QtWidgets.QPushButton(self.layoutWidget_2)
        self.deleteButton.setEnabled(False)
        self.deleteButton.setMinimumSize(QtCore.QSize(40, 23))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName("deleteButton")
        self.buttonLayout.addWidget(self.deleteButton)
        self.inputText = QtWidgets.QTextEdit(self.centralwidget)
        self.inputText.setGeometry(QtCore.QRect(10, 350, 521, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.inputText.setFont(font)
        self.inputText.setStyleSheet("background-color: rgb(225, 255, 255);")
        self.inputText.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>")
        self.inputText.setObjectName("inputText")
        self.outputText = QtWidgets.QTextEdit(self.centralwidget)
        self.outputText.setGeometry(QtCore.QRect(10, 470, 521, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.outputText.setFont(font)
        self.outputText.setStyleSheet("background-color: rgb(229, 255, 236);")
        self.outputText.setReadOnly(True)
        self.outputText.setMarkdown("")
        self.outputText.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8.25pt;\"><br /></p></body></html>")
        self.outputText.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.outputText.setPlaceholderText("")
        self.outputText.setObjectName("outputText")
        self.testButton = QtWidgets.QPushButton(self.centralwidget)
        self.testButton.setGeometry(QtCore.QRect(91, 436, 101, 23))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.testButton.setFont(font)
        self.testButton.setObjectName("testButton")
        self.layoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_3.setGeometry(QtCore.QRect(10, 280, 190, 42))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.layoutWidget_3.setFont(font)
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.buttonLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.buttonLayout_2.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout_2.setObjectName("buttonLayout_2")
        self.checkAllButton = QtWidgets.QPushButton(self.layoutWidget_3)
        self.checkAllButton.setMinimumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.checkAllButton.setFont(font)
        self.checkAllButton.setText("☑")
        self.checkAllButton.setObjectName("checkAllButton")
        self.buttonLayout_2.addWidget(self.checkAllButton)
        self.uncheckAllButton = QtWidgets.QPushButton(self.layoutWidget_3)
        self.uncheckAllButton.setMinimumSize(QtCore.QSize(40, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.uncheckAllButton.setFont(font)
        self.uncheckAllButton.setText("☐")
        self.uncheckAllButton.setObjectName("uncheckAllButton")
        self.buttonLayout_2.addWidget(self.uncheckAllButton)
        self.moveUpButton = QtWidgets.QPushButton(self.layoutWidget_3)
        self.moveUpButton.setMinimumSize(QtCore.QSize(40, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.moveUpButton.setFont(font)
        self.moveUpButton.setText("")
        self.moveUpButton.setObjectName("moveUpButton")
        self.buttonLayout_2.addWidget(self.moveUpButton)
        self.moveDownButton = QtWidgets.QPushButton(self.layoutWidget_3)
        self.moveDownButton.setMinimumSize(QtCore.QSize(40, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.moveDownButton.setFont(font)
        self.moveDownButton.setText("")
        self.moveDownButton.setObjectName("moveDownButton")
        self.buttonLayout_2.addWidget(self.moveDownButton)
        self.closeButton = QtWidgets.QPushButton(self.centralwidget)
        self.closeButton.setGeometry(QtCore.QRect(10, 550, 71, 23))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.closeButton.setFont(font)
        self.closeButton.setAutoDefault(False)
        self.closeButton.setDefault(True)
        self.closeButton.setObjectName("closeButton")
        self.testInputLabel = QtWidgets.QLabel(self.centralwidget)
        self.testInputLabel.setGeometry(QtCore.QRect(10, 330, 211, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.testInputLabel.setFont(font)
        self.testInputLabel.setObjectName("testInputLabel")
        self.testInputLabel_2 = QtWidgets.QLabel(self.centralwidget)
        self.testInputLabel_2.setGeometry(QtCore.QRect(10, 450, 221, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.testInputLabel_2.setFont(font)
        self.testInputLabel_2.setObjectName("testInputLabel_2")
        self.errorLabel = QtWidgets.QLabel(self.centralwidget)
        self.errorLabel.setGeometry(QtCore.QRect(100, 550, 431, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.errorLabel.setFont(font)
        self.errorLabel.setObjectName("errorLabel")
        self.rulesList = QtWidgets.QListView(self.centralwidget)
        self.rulesList.setGeometry(QtCore.QRect(10, 150, 521, 121))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rulesList.setFont(font)
        self.rulesList.setStyleSheet("background-color: rgb(240, 221, 255);")
        self.rulesList.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.rulesList.setObjectName("rulesList")
        self.wildebeestCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.wildebeestCheckBox.setEnabled(True)
        self.wildebeestCheckBox.setGeometry(QtCore.QRect(210, 280, 241, 17))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.wildebeestCheckBox.setFont(font)
        self.wildebeestCheckBox.setText("Run the Wildebeest cleanup tool")
        self.wildebeestCheckBox.setObjectName("wildebeestCheckBox")
        self.layoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_4.setGeometry(QtCore.QRect(10, 10, 521, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.layoutWidget_4.setFont(font)
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_4)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.searchLabel = QtWidgets.QLabel(self.layoutWidget_4)
        self.searchLabel.setMinimumSize(QtCore.QSize(65, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.searchLabel.setFont(font)
        self.searchLabel.setObjectName("searchLabel")
        self.horizontalLayout_2.addWidget(self.searchLabel)
        self.searchTextBox = QtWidgets.QLineEdit(self.layoutWidget_4)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchTextBox.setFont(font)
        self.searchTextBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.searchTextBox.setObjectName("searchTextBox")
        self.horizontalLayout_2.addWidget(self.searchTextBox)
        self.layoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget_5.setGeometry(QtCore.QRect(10, 70, 521, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.layoutWidget_5.setFont(font)
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget_5)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.commentLabel = QtWidgets.QLabel(self.layoutWidget_5)
        self.commentLabel.setMinimumSize(QtCore.QSize(65, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.commentLabel.setFont(font)
        self.commentLabel.setObjectName("commentLabel")
        self.horizontalLayout_3.addWidget(self.commentLabel)
        self.commentTextBox = QtWidgets.QLineEdit(self.layoutWidget_5)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.commentTextBox.setFont(font)
        self.commentTextBox.setObjectName("commentTextBox")
        self.horizontalLayout_3.addWidget(self.commentTextBox)
        self.regexCheckBox = QtWidgets.QCheckBox(self.layoutWidget_5)
        self.regexCheckBox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.regexCheckBox.setFont(font)
        self.regexCheckBox.setObjectName("regexCheckBox")
        self.horizontalLayout_3.addWidget(self.regexCheckBox)
        self.inactiveCheckBox = QtWidgets.QCheckBox(self.layoutWidget_5)
        self.inactiveCheckBox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.inactiveCheckBox.setFont(font)
        self.inactiveCheckBox.setToolTip("")
        self.inactiveCheckBox.setObjectName("inactiveCheckBox")
        self.horizontalLayout_3.addWidget(self.inactiveCheckBox)
        self.WBlinkLabel = QtWidgets.QLabel(self.centralwidget)
        self.WBlinkLabel.setGeometry(QtCore.QRect(440, 279, 91, 20))
        self.WBlinkLabel.setText("<html><head/><body><p><a href=\"https://github.com/uhermjakob/wildebeest\"><span style=\" text-decoration: underline; color:#0000ff;\">wildebeest help</span></a></p></body></html>")
        self.WBlinkLabel.setTextFormat(QtCore.Qt.RichText)
        self.WBlinkLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.WBlinkLabel.setOpenExternalLinks(True)
        self.WBlinkLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.WBlinkLabel.setObjectName("WBlinkLabel")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(250, 298, 281, 24))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.WBstepsDefaultRadio = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.WBstepsDefaultRadio.setMaximumSize(QtCore.QSize(16777215, 15))
        self.WBstepsDefaultRadio.setToolTip("")
        self.WBstepsDefaultRadio.setChecked(True)
        self.WBstepsDefaultRadio.setObjectName("WBstepsDefaultRadio")
        self.horizontalLayout_4.addWidget(self.WBstepsDefaultRadio)
        self.WBstepsAllRadio = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.WBstepsAllRadio.setMaximumSize(QtCore.QSize(16777215, 15))
        self.WBstepsAllRadio.setObjectName("WBstepsAllRadio")
        self.horizontalLayout_4.addWidget(self.WBstepsAllRadio)
        self.WBstepsNoneRadio = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.WBstepsNoneRadio.setMaximumSize(QtCore.QSize(16777215, 15))
        self.WBstepsNoneRadio.setObjectName("WBstepsNoneRadio")
        self.horizontalLayout_4.addWidget(self.WBstepsNoneRadio)
        self.WBlangLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.WBlangLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.WBlangLabel.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.WBlangLabel.setFont(font)
        self.WBlangLabel.setObjectName("WBlangLabel")
        self.horizontalLayout_4.addWidget(self.WBlangLabel)
        self.WBlangCodeTextBox = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.WBlangCodeTextBox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.WBlangCodeTextBox.setFont(font)
        self.WBlangCodeTextBox.setObjectName("WBlangCodeTextBox")
        self.horizontalLayout_4.addWidget(self.WBlangCodeTextBox)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(250, 320, 281, 24))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.WBaddLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.WBaddLabel.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.WBaddLabel.setFont(font)
        self.WBaddLabel.setObjectName("WBaddLabel")
        self.horizontalLayout_5.addWidget(self.WBaddLabel)
        self.WBaddStepsTextBox = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.WBaddStepsTextBox.setFont(font)
        self.WBaddStepsTextBox.setObjectName("WBaddStepsTextBox")
        self.horizontalLayout_5.addWidget(self.WBaddStepsTextBox)
        self.WBskipLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.WBskipLabel.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.WBskipLabel.setFont(font)
        self.WBskipLabel.setObjectName("WBskipLabel")
        self.horizontalLayout_5.addWidget(self.WBskipLabel)
        self.WBskipStepsTextBox = QtWidgets.QLineEdit(self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.WBskipStepsTextBox.setFont(font)
        self.WBskipStepsTextBox.setObjectName("WBskipStepsTextBox")
        self.horizontalLayout_5.addWidget(self.WBskipStepsTextBox)
        self.WBstepsLabel = QtWidgets.QLabel(self.centralwidget)
        self.WBstepsLabel.setGeometry(QtCore.QRect(210, 302, 36, 31))
        self.WBstepsLabel.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.WBstepsLabel.setFont(font)
        self.WBstepsLabel.setObjectName("WBstepsLabel")
        TextInOutMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(TextInOutMainWindow)
        QtCore.QMetaObject.connectSlotsByName(TextInOutMainWindow)
        TextInOutMainWindow.setTabOrder(self.searchTextBox, self.replaceTextBox)
        TextInOutMainWindow.setTabOrder(self.replaceTextBox, self.commentTextBox)
        TextInOutMainWindow.setTabOrder(self.commentTextBox, self.regexCheckBox)
        TextInOutMainWindow.setTabOrder(self.regexCheckBox, self.inactiveCheckBox)
        TextInOutMainWindow.setTabOrder(self.inactiveCheckBox, self.addButton)
        TextInOutMainWindow.setTabOrder(self.addButton, self.updateButton)
        TextInOutMainWindow.setTabOrder(self.updateButton, self.deleteButton)
        TextInOutMainWindow.setTabOrder(self.deleteButton, self.rulesList)
        TextInOutMainWindow.setTabOrder(self.rulesList, self.moveUpButton)
        TextInOutMainWindow.setTabOrder(self.moveUpButton, self.moveDownButton)
        TextInOutMainWindow.setTabOrder(self.moveDownButton, self.wildebeestCheckBox)
        TextInOutMainWindow.setTabOrder(self.wildebeestCheckBox, self.WBstepsDefaultRadio)
        TextInOutMainWindow.setTabOrder(self.WBstepsDefaultRadio, self.WBstepsAllRadio)
        TextInOutMainWindow.setTabOrder(self.WBstepsAllRadio, self.WBstepsNoneRadio)
        TextInOutMainWindow.setTabOrder(self.WBstepsNoneRadio, self.WBlangCodeTextBox)
        TextInOutMainWindow.setTabOrder(self.WBlangCodeTextBox, self.WBaddStepsTextBox)
        TextInOutMainWindow.setTabOrder(self.WBaddStepsTextBox, self.WBskipStepsTextBox)
        TextInOutMainWindow.setTabOrder(self.WBskipStepsTextBox, self.inputText)
        TextInOutMainWindow.setTabOrder(self.inputText, self.testButton)
        TextInOutMainWindow.setTabOrder(self.testButton, self.outputText)
        TextInOutMainWindow.setTabOrder(self.outputText, self.closeButton)

    def retranslateUi(self, TextInOutMainWindow):
        _translate = QtCore.QCoreApplication.translate
        TextInOutMainWindow.setWindowTitle(_translate("TextInOutMainWindow", "Text Out Rules"))
        self.replaceLabel.setText(_translate("TextInOutMainWindow", "Replace with:"))
        self.addButton.setToolTip(_translate("TextInOutMainWindow", "Add search and replace text as a new rule."))
        self.addButton.setText(_translate("TextInOutMainWindow", "Add"))
        self.updateButton.setToolTip(_translate("TextInOutMainWindow", "Update the rule selected below with the above search and replace text."))
        self.updateButton.setText(_translate("TextInOutMainWindow", "Update"))
        self.deleteButton.setToolTip(_translate("TextInOutMainWindow", "Delete the below selected rule."))
        self.deleteButton.setText(_translate("TextInOutMainWindow", "Delete"))
        self.testButton.setToolTip(_translate("TextInOutMainWindow", "Test the checked rules above with the input text."))
        self.testButton.setText(_translate("TextInOutMainWindow", "Test"))
        self.checkAllButton.setToolTip(_translate("TextInOutMainWindow", "Check all rules."))
        self.uncheckAllButton.setToolTip(_translate("TextInOutMainWindow", "Uncheck all rules."))
        self.moveUpButton.setToolTip(_translate("TextInOutMainWindow", "Move the selected rule up."))
        self.moveDownButton.setToolTip(_translate("TextInOutMainWindow", "Move the selected rule down."))
        self.closeButton.setText(_translate("TextInOutMainWindow", "Close"))
        self.testInputLabel.setText(_translate("TextInOutMainWindow", "Test input"))
        self.testInputLabel_2.setText(_translate("TextInOutMainWindow", "Test output"))
        self.errorLabel.setText(_translate("TextInOutMainWindow", "Error Msg here"))
        self.wildebeestCheckBox.setToolTip(_translate("TextInOutMainWindow", "This tool will run before other rules."))
        self.searchLabel.setText(_translate("TextInOutMainWindow", "Search for:"))
        self.commentLabel.setText(_translate("TextInOutMainWindow", "Comment:"))
        self.regexCheckBox.setToolTip(_translate("TextInOutMainWindow", "Treat the search and replace text as regular expressions."))
        self.regexCheckBox.setText(_translate("TextInOutMainWindow", "Regular Expression"))
        self.inactiveCheckBox.setText(_translate("TextInOutMainWindow", "Inactive"))
        self.WBstepsDefaultRadio.setText(_translate("TextInOutMainWindow", "Default"))
        self.WBstepsAllRadio.setText(_translate("TextInOutMainWindow", "All"))
        self.WBstepsNoneRadio.setText(_translate("TextInOutMainWindow", "None"))
        self.WBlangLabel.setText(_translate("TextInOutMainWindow", "Lang:"))
        self.WBlangCodeTextBox.setToolTip(_translate("TextInOutMainWindow", "3-letter ISO 639-3 code"))
        self.WBlangCodeTextBox.setPlaceholderText(_translate("TextInOutMainWindow", "code"))
        self.WBaddLabel.setText(_translate("TextInOutMainWindow", "Add:"))
        self.WBaddStepsTextBox.setToolTip(_translate("TextInOutMainWindow", "Steps to add to the base number of steps selected above.\n"
"Separate steps with spaces or commas."))
        self.WBskipLabel.setText(_translate("TextInOutMainWindow", "Skip:"))
        self.WBskipStepsTextBox.setToolTip(_translate("TextInOutMainWindow", "Steps to skip from the base number of steps selected above.\n"
"Separate steps with spaces or commas."))
        self.WBstepsLabel.setText(_translate("TextInOutMainWindow", "Steps:"))
