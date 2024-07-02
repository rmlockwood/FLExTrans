#
#   TextOutRules.py
#
#   Ron Lockwood
#   SIL International
#   6/29/24
#
#   Version 3.11 - 6/29/24 - Ron Lockwood
#    Initial version.
#
#   Define and test a set of search and replace operations to be used to fix up the text that comes out of 
#   synthesis. Regular expression can be used if desired.
#

import os
import shutil
import regex
import sys
import xml.etree.ElementTree as ET

from flextoolslib import *                                          

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QCheckBox, QDialog, QDialogButtonBox, QToolTip

import FTPaths
import ReadConfig
import TextInOutUtils

from TextInOut import Ui_MainWindow

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Text Out Rules",
        FTM_Version    : "3.11",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : 'Define and test a set of post-synthesis search and replace operations.' ,
        FTM_Help   : "",
        FTM_Description: 
"""
This module is used to define and test a set of search and replace operations to be used to fix up the text that comes out of 
synthesis. Regular expression can be used if desired.
"""}
        
class Main(QMainWindow):

    def __init__(self, searchReplacefile):

        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.searchReplacefile = searchReplacefile
        self.searchReplaceRulesElement = ""
        self.ruleFileXMLtree = ""
        self.rulesModel = None
        self.ruleIndex = None
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        # Reset icon images
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "UpArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.moveUpButton.setIcon(icon)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "DownArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.moveDownButton.setIcon(icon2)

        self.ui.errorLabel.setText('')
        
        self.ui.addButton.clicked.connect(self.AddClicked)
        self.ui.checkAllButton.clicked.connect(self.CheckAllClicked)
        self.ui.closeButton.clicked.connect(self.CloseClicked)
        self.ui.deleteButton.clicked.connect(self.DeleteClicked)
        self.ui.moveDownButton.clicked.connect(self.DownButtonClicked)
        self.ui.moveUpButton.clicked.connect(self.UpButtonClicked)
        self.ui.replaceTextBox.textChanged.connect(self.SearchOrReplaceChanged)
        self.ui.rulesList.clicked.connect(self.RulesListClicked)
        self.ui.searchTextBox.textChanged.connect(self.SearchOrReplaceChanged)
        self.ui.testButton.clicked.connect(self.TestClicked)
        self.ui.uncheckAllButton.clicked.connect(self.UncheckAllClicked)
        self.ui.updateButton.clicked.connect(self.UpdateClicked)

        # Load the rules
        self.loadRules()
    
    def AddClicked(self):
        
        # Build the rule string for the rule list
        ruleStr = TextInOutUtils.buildRuleString(self.ui.searchTextBox.text(), self.ui.replaceTextBox.text(), self.ui.regexCheckBox.checkState() == QtCore.Qt.Checked)

        # Get the row #
        if self.ruleIndex:

            rowNum = self.ruleIndex.row()
        else:
            rowNum = 0

        # Create an item object
        item = QStandardItem(ruleStr) 
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)

        # Insert it
        self.rulesModel.insertRow(rowNum, item)

        # Construct the etree elements
        newRuleEl = ET.Element(TextInOutUtils.SEARCH_REPL_RULE_ELEM)
        newSearchEl = ET.SubElement(newRuleEl, TextInOutUtils.SEARCH_STRING_ELEM)
        newReplEl = ET.SubElement(newRuleEl, TextInOutUtils.REPL_STRING_ELEM)
        newSearchEl.text = self.ui.searchTextBox.text()
        newReplEl.text = self.ui.replaceTextBox.text()

        if self.ui.regexCheckBox.checkState():
            isRegexStr = "yes"
        else:
            isRegexStr = "no"

        newRuleEl.attrib[TextInOutUtils.REGEX_ATTRIB] = isRegexStr

        # Add it to the element tree
        self.searchReplaceRulesElement.insert(rowNum, newRuleEl)

        # Select it
        qIndex = self.rulesModel.createIndex(rowNum, 0)
        self.ui.rulesList.setCurrentIndex(qIndex)

    def CheckAllClicked(self):

        # Loop through all the items in the rule list model
        for i in range(0, self.rulesModel.rowCount()):

            # Check each box
            self.rulesModel.item(i).setCheckState(QtCore.Qt.Checked)

    def CloseClicked(self):
        
        self.writeXMLfile()
        self.close()

    def DeleteClicked(self):

        if self.ruleIndex:

            # Remove the row
            self.rulesModel.removeRow(self.ruleIndex.row())

            # Remove this row from the etree
            self.searchReplaceRulesElement.remove(self.searchReplaceRulesElement[self.ruleIndex.row()])

            # If this was the last remaining row, disable the delete button
            if self.rulesModel.rowCount() < 1:

                self.ui.deleteButton.setEnabled(False)
                self.ui.updateButton.setEnabled(False)

    def DownButtonClicked(self):
        
        if self.ruleIndex and self.ruleIndex.row() < self.rulesModel.rowCount()-1:
            
            # move the XML sub-element
            elemToMove = self.searchReplaceRulesElement[self.ruleIndex.row()]
            self.searchReplaceRulesElement.remove(elemToMove)
            self.searchReplaceRulesElement.insert(self.ruleIndex.row()+1, elemToMove)

            # copy the check state from one row to the other
            currState = self.rulesModel.item(self.ruleIndex.row()).checkState()
            othState = self.rulesModel.item(self.ruleIndex.row()+1).checkState()
            self.rulesModel.item(self.ruleIndex.row()).setCheckState(othState)
            self.rulesModel.item(self.ruleIndex.row()+1).setCheckState(currState)
            
            # copy the rule string from one row to the other
            currStr = self.rulesModel.item(self.ruleIndex.row()).text()
            othStr = self.rulesModel.item(self.ruleIndex.row()+1).text()
            self.rulesModel.item(self.ruleIndex.row()).setText(othStr)
            self.rulesModel.item(self.ruleIndex.row()+1).setText(currStr)
            
            myIndex = self.rulesModel.index(self.ruleIndex.row()+1, self.ruleIndex.column())
            self.ui.rulesList.setCurrentIndex(myIndex)

            # redo the display
            self.RulesListClicked(myIndex)

    def RulesListClicked(self, index):
        
        self.ruleIndex = index
        
        # Get rule data for current index. Get it from the element tree object.
        searchReplaceRuleData = TextInOutUtils.getRuleFromElement(self.searchReplaceRulesElement[index.row()])
                        
        # Set the text boxes with what is in the rule.
        self.ui.searchTextBox.setText(searchReplaceRuleData.searchStr)
        self.ui.replaceTextBox.setText(searchReplaceRuleData.replStr)

        # Set the RegEx check box
        if searchReplaceRuleData.isRegEx:

            self.ui.regexCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.regexCheckBox.setCheckState(QtCore.Qt.Unchecked)

        # Enable controls
        self.enableControls()

    def SearchOrReplaceChanged(self):
        
        # if search is non-empty, enable stuff
        if self.ui.searchTextBox.text():

            self.ui.addButton.setEnabled(True)
            self.ui.regexCheckBox.setEnabled(True)

            # If a rule is selected, enable the update button
            if self.ruleIndex:

                self.ui.updateButton.setEnabled(True)

        # Otherwise disable stuff
        else:
            self.ui.addButton.setEnabled(False)
            self.ui.updateButton.setEnabled(False)
            self.ui.regexCheckBox.setEnabled(False)
                
    def TestClicked(self):

        self.ui.errorLabel.setText('')

        self.writeXMLfile()

        inStr = self.ui.inputText.toPlainText()
        newStr = inStr

        # Loop through the rules and apply each checked one in turn
        for ind, ruleEl in enumerate(self.searchReplaceRulesElement):

            # Process the rule if it is checked
            if self.rulesModel.item(ind).checkState():

                searchReplDataObj = TextInOutUtils.getRuleFromElement(ruleEl)

                try:
                    if searchReplDataObj.isRegEx:

                        newStr = regex.sub(searchReplDataObj.searchStr, searchReplDataObj.replStr, newStr)

                    else:
                        newStr = newStr.replace(searchReplDataObj.searchStr, searchReplDataObj.replStr)
                except:
                    self.ui.errorLabel.setText(f'Test stopped on failure of rule {str(ind+1)}: ' + TextInOutUtils.buildRuleStringFromElement(ruleEl)) # it might be more efficient to get this from the rule model
                    break

        self.ui.outputText.setText(newStr)
        return

    def UncheckAllClicked(self):

        # Loop through all the items in the rule list model
        for i in range(0, self.rulesModel.rowCount()):

            # Unheck each box
            self.rulesModel.item(i).setCheckState(QtCore.Qt.Unchecked)

    def UpButtonClicked(self):

        if self.ruleIndex and self.ruleIndex.row() > 0:
            
            # move the XML sub-element
            elemToMove = self.searchReplaceRulesElement[self.ruleIndex.row()]
            self.searchReplaceRulesElement.remove(elemToMove)
            self.searchReplaceRulesElement.insert(self.ruleIndex.row()-1, elemToMove)

            # copy the check state from one row to the other
            currState = self.rulesModel.item(self.ruleIndex.row()).checkState()
            othState = self.rulesModel.item(self.ruleIndex.row()-1).checkState()
            self.rulesModel.item(self.ruleIndex.row()).setCheckState(othState)
            self.rulesModel.item(self.ruleIndex.row()-1).setCheckState(currState)

            # copy the rule string from one row to the other
            currStr = self.rulesModel.item(self.ruleIndex.row()).text()
            othStr = self.rulesModel.item(self.ruleIndex.row()-1).text()
            self.rulesModel.item(self.ruleIndex.row()).setText(othStr)
            self.rulesModel.item(self.ruleIndex.row()-1).setText(currStr)
            
            myIndex = self.rulesModel.index(self.ruleIndex.row()-1, self.ruleIndex.column())
            self.ui.rulesList.setCurrentIndex(myIndex)

            # redo the display
            self.RulesListClicked(myIndex)
            
    def UpdateClicked(self):
        
        # Get the rule data at the current index selected
        myItem = self.rulesModel.itemFromIndex(self.ruleIndex)

        # Build the rule string for the rule list
        ruleStr = TextInOutUtils.buildRuleString(self.ui.searchTextBox.text(), self.ui.replaceTextBox.text(), self.ui.regexCheckBox.checkState() == QtCore.Qt.Checked)

        # Update the selected rule
        myItem.setText(ruleStr)
        myItem.setCheckState(QtCore.Qt.Checked)

        # Update the etree elements
        ruleEl = self.searchReplaceRulesElement[self.ruleIndex.row()]

        searchEl = ruleEl[0]
        replaceEl = ruleEl[1]

        searchEl.text = self.ui.searchTextBox.text()
        replaceEl.text = self.ui.replaceTextBox.text()

        if self.ui.regexCheckBox.checkState():
            isRegexStr = "yes"
        else:
            isRegexStr = "no"

        ruleEl.attrib[TextInOutUtils.REGEX_ATTRIB] = isRegexStr

        # Enable the delete button in case we were at 0 rows before.
        self.ui.deleteButton.setEnabled(True)

    def displayRules(self, rulesElement, rulesModel):
        
        # Loop through each rule
        for ruleEl in rulesElement:
                        
            searchReplObj = TextInOutUtils.getRuleFromElement(ruleEl)

            ruleStr = TextInOutUtils.buildRuleString(searchReplObj.searchStr, searchReplObj.replStr, searchReplObj.isRegEx)

            # Create an item object
            item = QStandardItem(ruleStr) 
            item.setCheckable(True)
            item.setCheckState(QtCore.Qt.Checked)

            # Append it
            rulesModel.appendRow(item)

    def enableControls(self):

        self.ui.addButton.setEnabled(True)
        self.ui.updateButton.setEnabled(True)
        self.ui.deleteButton.setEnabled(True)
        self.ui.regexCheckBox.setEnabled(True)

    def loadRules(self):
            
        # Verify we have a valid transfer file.
        try:
            testTree = ET.parse(self.searchReplacefile)
        except:
            QMessageBox.warning(self, 'Invalid File', 'The fix up synthesis text rules file you selected is invalid.')
            return False
        
        test_rt = testTree.getroot()
        self.searchReplaceRulesElement = test_rt.find(TextInOutUtils.SEARCH_REPLACE_RULES_ELEM)
        
        if self.searchReplaceRulesElement is not None:
            
            self.ruleFileXMLtree = testTree
            self.rulesModel = QStandardItemModel()
            self.displayRules(self.searchReplaceRulesElement, self.rulesModel)
            
            # Initialize the model for the rule list control
            self.ui.rulesList.setModel(self.rulesModel)
            
        else:
            QMessageBox.warning(self, 'Invalid Rules File', \
            'The fix up synthesis rule file has no SearchReplaceRules.')
            return False
        
    def writeXMLfile(self):

        ET.indent(self.ruleFileXMLtree)
        self.ruleFileXMLtree.write(self.searchReplacefile, encoding='utf-8', xml_declaration=True)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Get the path to the search-replace rules file
    textOutRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TEXT_OUT_RULES_FILE, report, giveError=True)

    if not textOutRulesFile:
        report.Error('No Fix Up Synthesis Text Rules File is defined. Check the Settings.')
        return
    
    try:
        # Check if the file exists, if not, create it.
        if os.path.exists(textOutRulesFile) == False:

            # Set a string for an empty rules list
            xmlString = f"<?xml version='1.0' encoding='utf-8'?><{TextInOutUtils.FT_SEARCH_REPLACE_ELEM}><{TextInOutUtils.SEARCH_REPLACE_RULES_ELEM}/></{TextInOutUtils.FT_SEARCH_REPLACE_ELEM}>"

            fOut = open(textOutRulesFile, 'w', encoding='utf-8')
            fOut.write(xmlString)
            fOut.close()
        else:
            # Make a backup copy of the search-replace rule file
            shutil.copy2(textOutRulesFile, textOutRulesFile+'.bak')
    except:
        report.Error('There was a problem creating or backing up the rules file. Check your configuration.')
        return

    # Show the window to get the options the user wants
    app = QApplication(sys.argv)
    window = Main(textOutRulesFile)
    window.show()
    app.exec_()
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
