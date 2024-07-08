#
#   TextInOutUtils.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
#
#   Version 3.11.1 - 7/8/24 - Ron Lockwood
#    Added Text In module putting common window code in InOutUtils.
#
#   Version 3.11 - 7/1/24 - Ron Lockwood
#    Initial version.
#
#   Shared functions, classes and constants for text in and out processing.
#

import FTPaths
import regex
import os
import xml.etree.ElementTree as ET

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow

from TextInOut import Ui_MainWindow

FT_SEARCH_REPLACE_ELEM = 'FLExTransSearchReplace' 
SEARCH_REPLACE_RULES_ELEM = 'SearchReplaceRules' 
SEARCH_REPL_RULE_ELEM = 'SearchReplaceRule' 
SEARCH_STRING_ELEM = 'SearchString'
REPL_STRING_ELEM = 'ReplaceString'
REGEX_ATTRIB = 'RegEx'
ARROW_CHAR = '⭢'

class SearchReplaceRuleData():

    def __init__(self, searchStr, replStr, isRegEx):

        self.searchStr = "" if searchStr is None else searchStr
        self.replStr = "" if replStr is None else replStr
        self.isRegEx = isRegEx

def getRuleFromElement(element):

    # Get the search and replace string elements
    searchEl = element[0]
    replaceEl = element[1]

    # Get the regex yes/no attribute
    regExVal = element.get(REGEX_ATTRIB)

    if regExVal == 'yes':
        isRegEx = True
    else:
        isRegEx = False

    searchReplaceRuleData = SearchReplaceRuleData(searchEl.text, replaceEl.text, isRegEx)

    return searchReplaceRuleData

def buildRuleString(searchStr, replStr, isRegExChecked):

    # Create a regex indicator string if reg ex is checked
    if isRegExChecked:

        regExStr = (' (✓ RegEx)')
    else:
        regExStr = ""

    # Build rule display string including codes for invisible chars.
    searchStr = getPrintableString(searchStr)
    replStr = getPrintableString(replStr)

    return f'{searchStr} {ARROW_CHAR} {replStr}{regExStr}'

def buildRuleStringFromElement(element):

    SRobj = getRuleFromElement(element)

    return buildRuleString(SRobj.searchStr, SRobj.replStr, SRobj.isRegEx)

def getPrintableString(myStr):
    
    # If we have a special char, return the equivalent alias str, otherwise return the char.
    return ''.join(replacementsMap.get(char, char) for char in myStr)

replacementsMap = {
'\u0000': '[NUL]','\u0001': '[SOH]','\u0002': '[STX]','\u0003': '[ETX]','\u0004': '[EOT]','\u0005': '[ENQ]','\u0006': '[ACK]','\u0007': '[BEL]','\u0008': '[BS]',
'\u0009': '[HT]', '\u0009': '[TAB]','\u000A': '[EOL]','\u000A': '[LF]', '\u000A': '[NL]', '\u000B': '[VT]', '\u000C': '[FF]', '\u000D': '[CR]', '\u000E': '[SO]','\u000F': '[SI]',
'\u0010': '[DLE]','\u0011': '[DC1]','\u0012': '[DC2]','\u0013': '[DC3]','\u0014': '[DC4]','\u0015': '[NAK]','\u0016': '[SYN]','\u0017': '[ETB]','\u0018': '[CAN]',
'\u0019': '[EM]', '\u0019': '[EOM]','\u001A': '[SUB]','\u001B': '[ESC]','\u001C': '[FS]', '\u001D': '[GS]', '\u001E': '[RS]', '\u001F': '[US]', '\u0020': '[SP]','\u007F': '[DEL]',
'\u0080': '[PAD]','\u0081': '[HOP]','\u0082': '[BPH]','\u0083': '[NBH]','\u0084': '[IND]','\u0085': '[NEL]','\u0086': '[SSA]','\u0087': '[ESA]','\u0088': '[HTS]',
'\u0089': '[HTJ]','\u008A': '[VTS]','\u008B': '[PLD]','\u008C': '[PLU]','\u008D': '[RI]', '\u008E': '[SS2]','\u008F': '[SS3]','\u0090': '[DCS]','\u0091': '[PU1]',
'\u0092': '[PU2]','\u0093': '[STS]','\u0094': '[CCH]','\u0095': '[MW]', '\u0096': '[SPA]','\u0097': '[EPA]','\u0098': '[SOS]','\u200B': '[ZWSP]','\u200C':'[ZWNJ]',
'\u200D': '[ZWJ]','\u200E': '[LRM]','\u200F': '[RLM]','\u202A': '[LRE]','\u202B': '[RLE]','\u202C': '[PDF]','\u202D': '[LRO]','\u202E': '[RLO]','\u202F': '[NNBSP]',
'\u205F': '[MMSP]','\u2060':'[WJ]', '\u2066': '[LRI]','\u2067': '[RLI]','\u2068': '[FSI]','\u2069': '[PDI]'
}

def applySearchReplaceRules(inputStr, tree):
    
    # Get the parent element where the rules are listed.
    root = tree.getroot()
    searchReplaceRulesElement = root.find(SEARCH_REPLACE_RULES_ELEM)

    # Loop through each rule
    for ruleEl in searchReplaceRulesElement:

        searchReplObj = getRuleFromElement(ruleEl)

        try:
            if searchReplObj.isRegEx:

                newStr = regex.sub(searchReplObj.searchStr, searchReplObj.replStr, inputStr)
            else:
                newStr = inputStr.replace(searchReplObj.searchStr, searchReplObj.replStr)
        except:
            newStr = None
            errorMsg = f'Test stopped on failure of rule: ' + buildRuleStringFromElement(ruleEl)
            break

    return newStr, errorMsg

class TextInOutRulesWindow(QMainWindow):

    def __init__(self, searchReplacefile, textIn):

        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.searchReplacefile = searchReplacefile
        self.textIn = textIn
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

        # See if we are doing text in or out
        if not self.textIn:

            # If we are doing text out, don't show the wildebeast checkbox
            self.ui.wildebeastCheckBox.setVisible(False)

            self.setWindowTitle('Text Out Rules')
        else:
             self.setWindowTitle('Text In Rules')
           
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
        ruleStr = buildRuleString(self.ui.searchTextBox.text(), self.ui.replaceTextBox.text(), self.ui.regexCheckBox.checkState() == QtCore.Qt.Checked)

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
        newRuleEl = ET.Element(SEARCH_REPL_RULE_ELEM)
        newSearchEl = ET.SubElement(newRuleEl, SEARCH_STRING_ELEM)
        newReplEl = ET.SubElement(newRuleEl, REPL_STRING_ELEM)
        newSearchEl.text = self.ui.searchTextBox.text()
        newReplEl.text = self.ui.replaceTextBox.text()

        if self.ui.regexCheckBox.checkState():
            isRegexStr = "yes"
        else:
            isRegexStr = "no"

        newRuleEl.attrib[REGEX_ATTRIB] = isRegexStr

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
        searchReplaceRuleData = getRuleFromElement(self.searchReplaceRulesElement[index.row()])
                        
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

                searchReplDataObj = getRuleFromElement(ruleEl)

                try:
                    if searchReplDataObj.isRegEx:

                        newStr = regex.sub(searchReplDataObj.searchStr, searchReplDataObj.replStr, newStr)

                    else:
                        newStr = newStr.replace(searchReplDataObj.searchStr, searchReplDataObj.replStr)
                except:
                    self.ui.errorLabel.setText(f'Test stopped on failure of rule {str(ind+1)}: ' + buildRuleStringFromElement(ruleEl)) # it might be more efficient to get this from the rule model
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
        ruleStr = buildRuleString(self.ui.searchTextBox.text(), self.ui.replaceTextBox.text(), self.ui.regexCheckBox.checkState() == QtCore.Qt.Checked)

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

        ruleEl.attrib[REGEX_ATTRIB] = isRegexStr

        # Enable the delete button in case we were at 0 rows before.
        self.ui.deleteButton.setEnabled(True)

    def displayRules(self, rulesElement, rulesModel):
        
        # Loop through each rule
        for ruleEl in rulesElement:
                        
            searchReplObj = getRuleFromElement(ruleEl)

            ruleStr = buildRuleString(searchReplObj.searchStr, searchReplObj.replStr, searchReplObj.isRegEx)

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
        self.searchReplaceRulesElement = test_rt.find(SEARCH_REPLACE_RULES_ELEM)
        
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
