#
#   TextInOutUtils.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
#
#   Version 3.12.1 - 11/12/24 - Ron Lockwood
#    Use default path if settings has no path to the xml file.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.2 - 10/7/24 - Ron Lockwood
#    Convert search and to be searched strings to decomposed.
#
#   Version 3.11.1 - 9/19/24 - Ron Lockwood
#    Display the comment in the list
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    See the beginning of the comment text.
#
#   Version 3.10.6 - 8/2/24 - Ron Lockwood
#    Use new function num Rules to get the number of rules.
#
#   Version 3.10.5 - 7/12/24 - Ron Lockwood
#    Added Wildebeest support.
#
#   Version 3.10.4 - 7/9/24 - Ron Lockwood
#    Added comment and inactive properties to rules.
#
#   Version 3.10.3 - 7/8/24 - Ron Lockwood
#    Added Text In module putting common window code in InOutUtils.
#
#   Version 3.10.2 - 7/1/24 - Ron Lockwood
#    Initial version.
#
#   Shared functions, classes and constants for text in and out processing.
#

import unicodedata
import FTPaths
import ReadConfig
import regex
import os
import xml.etree.ElementTree as ET
from wildebeest.wb_normalize import Wildebeest

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow

from TextInOut import Ui_MainWindow

FT_SEARCH_REPLACE_ELEM = 'FLExTransSearchReplace' 
SEARCH_REPLACE_RULES_ELEM = 'SearchReplaceRules' 
SEARCH_REPL_RULE_ELEM = 'SearchReplaceRule' 
SEARCH_STRING_ELEM = 'SearchString'
REPL_STRING_ELEM = 'ReplaceString'
WB_SETTINGS_ELEM = 'WildebeestSettings'
WB_ADD_STEPS_ELEM = 'AddSteps'
WB_SKIP_STEPS_ELEM = 'SkipSteps'
REGEX_ATTRIB = 'RegEx'
INACTIVE_ATTRIB = 'Inactive'
COMMENT_ATTRIB = 'Comment'
APPLY_WILDEBEEST_ATTRIB = 'ApplyWildebeest'
WB_BASE_ATTRIB = 'Base'
WB_BASE_DEFAULT = 'DEFAULT'
WB_BASE_ALL = 'ALL'
WB_BASE_NONE = 'NONE'
WB_LANG_CODE_ATTRIB = 'LangCode'
WB_ADD_STEP_ATTRIB = 'AddStep'
WB_SKIP_STEP_ATTRIB = 'SkipStep'

ARROW_CHAR = '⭢'

class SearchReplaceRuleData():

    def __init__(self, searchStr, replStr, isRegEx, isInactive, comment):

        self.searchStr = "" if searchStr is None else searchStr
        self.replStr = "" if replStr is None else replStr
        self.isRegEx = isRegEx
        self.isInactive = isInactive
        self.comment = "" if comment is None else comment

def getPath(report, configMap, settingName, defaultRelPath):

    rulesFile = ReadConfig.getConfigVal(configMap, settingName, report, giveError=False)

    if not rulesFile:

        rulesFile = os.path.join(FTPaths.WORK_DIR, defaultRelPath)
        ReadConfig.writeConfigValue(report, settingName, defaultRelPath, createIfMissing=True)

    return rulesFile

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

    # Get the inactive flag
    inactiveVal = element.get(INACTIVE_ATTRIB)

    if inactiveVal == 'yes':
        isInactive = True
    else:
        isInactive = False

    # Get the comment
    comment = element.get(COMMENT_ATTRIB)

    searchReplaceRuleData = SearchReplaceRuleData(searchEl.text, replaceEl.text, isRegEx, isInactive, comment)

    return searchReplaceRuleData

def buildRuleString(searchRplObj):

    # Create a regex indicator string if reg ex is checked
    if searchRplObj.isRegEx:

        regExStr = (' (✓ RegEx)')
    else:
        regExStr = ""

    # Create an inactive indicator string if reg ex is checked
    if searchRplObj.isInactive:

        inactiveStr = ('🚫')
    else:
        inactiveStr = ""

    # Build rule display string including codes for invisible chars.
    searchStr = getPrintableString(searchRplObj.searchStr)
    replStr = getPrintableString(searchRplObj.replStr)

    # Comment string
    commentStr = ''
    if searchRplObj.comment:

        commentStr = ' - ' + searchRplObj.comment

    return f'{searchStr} {ARROW_CHAR} {replStr}{regExStr}{inactiveStr}{commentStr}'

def buildRuleStringFromElement(element):

    SRobj = getRuleFromElement(element)

    return buildRuleString(SRobj)

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

def numRules(tree):
    
    # Get the parent element where the rules are listed.
    root = tree.getroot()
    searchReplaceRulesElement = root.find(SEARCH_REPLACE_RULES_ELEM)

    if searchReplaceRulesElement:

        return sum(1 for i, ruleEl in enumerate(searchReplaceRulesElement) if getRuleFromElement(ruleEl).isInactive == False)
    else:
        return 0

def applySearchReplaceRules(inputStr, tree):
    
    errorMsg = ""
    newStr = inputStr

    # Get the parent element where the rules are listed.
    root = tree.getroot()
    searchReplaceRulesElement = root.find(SEARCH_REPLACE_RULES_ELEM)

    # See if we have Wildebeest to run, if so run it
    wildebeestStr = root.get(APPLY_WILDEBEEST_ATTRIB)

    if wildebeestStr == 'yes':

       newStr = runWildebeest(root, newStr)

    # Loop through each rule
    for ruleEl in searchReplaceRulesElement:

        searchReplObj = getRuleFromElement(ruleEl)

        # Skip a rule if it is marked inactive
        if searchReplObj.isInactive == False:

            # Convert the search string and the string to replace to decomposed unicode. 
            # FLEx stores things as decomposed, but the user may not be inputting decomposed unicode.
            newStr = unicodedata.normalize('NFD', newStr)
            newSearch = unicodedata.normalize('NFD', searchReplObj.searchStr)

            try:
                if searchReplObj.isRegEx:

                    newStr = regex.sub(newSearch, searchReplObj.replStr, newStr)
                else:
                    newStr = newStr.replace(newSearch, searchReplObj.replStr)
            except:
                newStr = None
                errorMsg = f'Test stopped on failure of rule: ' + buildRuleStringFromElement(ruleEl)
                break

    return newStr, errorMsg

def runWildebeest(root, inputStr):

    newStr = inputStr
    addList = []
    skipList = []

    WBelem = root.find(WB_SETTINGS_ELEM)

    if WBelem:

        # Get base string
        baseStr = WBelem.get(WB_BASE_ATTRIB)

        # Get add and skip steps
        addStepsElem = WBelem.find(WB_ADD_STEPS_ELEM)
        skipStepsElem = WBelem.find(WB_SKIP_STEPS_ELEM)

        if addStepsElem is not None and addStepsElem.text:

            addStr = addStepsElem.text
            addList = addStr.split()

        if skipStepsElem is not None and skipStepsElem.text:

            skipStr = skipStepsElem.text
            skipList = skipStr.split()

        # Get language code
        langCode = WBelem.get(WB_LANG_CODE_ATTRIB)

        # clean the string with Wildebeest
        wb = Wildebeest()
        ht = wb.build_norm_step_dict(base=baseStr, skip=skipList, add=addList)
        newStr = wb.norm_clean_string(newStr, ht, lang_code=langCode)

    return newStr

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

        self.WBcontrols = [
            self.ui.WBlangCodeTextBox,
            self.ui.WBstepsDefaultRadio,
            self.ui.WBstepsAllRadio,
            self.ui.WBstepsNoneRadio,
            self.ui.WBaddStepsTextBox,
            self.ui.WBskipStepsTextBox,
            self.ui.WBlangLabel,
            self.ui.WBstepsLabel,
            self.ui.WBaddLabel,
            self.ui.WBskipLabel         
        ]
        
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

            # If we are doing text out, don't show the wildebeest checkbox
            self.hideWildebeestStuff()

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
        self.ui.wildebeestCheckBox.clicked.connect(self.WildebeestClicked)

        # Load the rules
        self.loadRules()
    
    def AddClicked(self):
        
        # Build the rule string for the rule list
        ruleStr = buildRuleString(self.initDataObj())

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
        ET.SubElement(newRuleEl, SEARCH_STRING_ELEM)
        ET.SubElement(newRuleEl, REPL_STRING_ELEM)

        # Set element text and attributes
        self.setElementInfo(newRuleEl)

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

        # Set the Inactive check box
        if searchReplaceRuleData.isInactive:

            self.ui.inactiveCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.ui.inactiveCheckBox.setCheckState(QtCore.Qt.Unchecked)

        # Set comment
        self.ui.commentTextBox.setText(searchReplaceRuleData.comment)
        
        # See the beginning of the comment box.
        self.ui.commentTextBox.setCursorPosition(0)

        # Enable controls
        self.enableControls()

    def SearchOrReplaceChanged(self):
        
        # if search is non-empty, enable stuff
        if self.ui.searchTextBox.text():

            self.ui.addButton.setEnabled(True)
            self.ui.regexCheckBox.setEnabled(True)
            self.ui.inactiveCheckBox.setEnabled(True)

            # If a rule is selected, enable the update button
            if self.ruleIndex:

                self.ui.updateButton.setEnabled(True)

        # Otherwise disable stuff
        else:
            self.ui.addButton.setEnabled(False)
            self.ui.updateButton.setEnabled(False)
            self.ui.regexCheckBox.setEnabled(False)
            self.ui.inactiveCheckBox.setEnabled(False)
                
    def TestClicked(self):

        self.ui.errorLabel.setText('')

        self.writeXMLfile()

        inStr = self.ui.inputText.toPlainText()
        newStr = inStr

        # Run Wildebeest if needed
        if self.ui.wildebeestCheckBox.isChecked():

            newStr = runWildebeest(self.root, newStr)

        # Loop through the rules and apply each checked one in turn
        for ind, ruleEl in enumerate(self.searchReplaceRulesElement):

            # Process the rule if it is checked
            if self.rulesModel.item(ind).checkState():

                searchReplDataObj = getRuleFromElement(ruleEl)

                if searchReplDataObj.isInactive == False:

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
        ruleStr = buildRuleString(self.initDataObj())

        # Update the selected rule
        myItem.setText(ruleStr)
        myItem.setCheckState(QtCore.Qt.Checked)

        # Update the etree elements
        ruleEl = self.searchReplaceRulesElement[self.ruleIndex.row()]

        # Set element text and attributes
        self.setElementInfo(ruleEl)

        # Enable the delete button in case we were at 0 rows before.
        self.ui.deleteButton.setEnabled(True)

    def WildebeestClicked(self):

        if self.ui.wildebeestCheckBox.isChecked():

            self.setWildebeestVisibility(True)
        else:
            self.setWildebeestVisibility(False)

    def displayRules(self, rulesElement, rulesModel):
        
        # Loop through each rule
        for ruleEl in rulesElement:
                        
            searchReplObj = getRuleFromElement(ruleEl)

            ruleStr = buildRuleString(searchReplObj)

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
        self.ui.inactiveCheckBox.setEnabled(True)

    def hideWildebeestStuff(self):

        self.ui.wildebeestCheckBox.setVisible(False)
        self.ui.WBlinkLabel.setVisible(False)

        # Hide the rest of the wildebeest controls
        self.setWildebeestVisibility(False)

    def initDataObj(self):

        searchRplObj = SearchReplaceRuleData(self.ui.searchTextBox.text(), self.ui.replaceTextBox.text(), self.ui.regexCheckBox.isChecked(), 
                                        self.ui.inactiveCheckBox.isChecked(), self.ui.commentTextBox.text())
        return searchRplObj

    def initWBcontrols(self, testRoot):
                
        # Get the Wildebeest attribute
        wildebeest = testRoot.get(APPLY_WILDEBEEST_ATTRIB)

        if wildebeest and wildebeest == 'yes':

            self.ui.wildebeestCheckBox.setCheckState(QtCore.Qt.Checked)
            self.setWildebeestVisibility(True)
        else:
            self.setWildebeestVisibility(False)
        
        # Find the Wildebeest section
        self.WBelem = testRoot.find(WB_SETTINGS_ELEM)

        if self.WBelem:

            # Set the base radio buttons
            if self.WBelem.get(WB_BASE_ATTRIB) == WB_BASE_DEFAULT:

                self.ui.WBstepsDefaultRadio.setChecked(True)
                self.ui.WBstepsAllRadio.setChecked(False)
                self.ui.WBstepsNoneRadio.setChecked(False)
        
            elif self.WBelem.get(WB_BASE_ATTRIB) == WB_BASE_ALL:

                self.ui.WBstepsDefaultRadio.setChecked(False)
                self.ui.WBstepsAllRadio.setChecked(True)
                self.ui.WBstepsNoneRadio.setChecked(False)
        
            else:
                self.ui.WBstepsDefaultRadio.setChecked(False)
                self.ui.WBstepsAllRadio.setChecked(False)
                self.ui.WBstepsNoneRadio.setChecked(True)

            # Set the language code text box
            self.ui.WBlangCodeTextBox.setText(self.WBelem.get(WB_LANG_CODE_ATTRIB))

            # Set the add and skip steps text boxes
            addStepsElem = self.WBelem.find(WB_ADD_STEPS_ELEM)
            skipStepsElem = self.WBelem.find(WB_SKIP_STEPS_ELEM)

            if addStepsElem is not None and addStepsElem.text:

                self.ui.WBaddStepsTextBox.setText(addStepsElem.text)
        
            if skipStepsElem is not None and skipStepsElem.text:

                self.ui.WBskipStepsTextBox.setText(skipStepsElem.text)

    def loadRules(self):
            
        # Verify we have a valid transfer file.
        try:
            testTree = ET.parse(self.searchReplacefile)
        except:
            QMessageBox.warning(self, 'Invalid File', 'The fix up synthesis text rules file you selected is invalid.')
            return False
        
        self.root = testTree.getroot()

        # Find the Rules section
        self.searchReplaceRulesElement = self.root.find(SEARCH_REPLACE_RULES_ELEM)
        
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
        
        # Set Wildebeest controls
        self.initWBcontrols(self.root)
        
    def saveWBinfo(self):

        # Set root wildebeest boolean
        if not self.ui.wildebeestCheckBox.isChecked():

            self.root.attrib[APPLY_WILDEBEEST_ATTRIB] = "no"

        else:
            self.root.attrib[APPLY_WILDEBEEST_ATTRIB] = "yes"
        
        # Find the Wildebeest section
        self.WBelem = self.root.find(WB_SETTINGS_ELEM)

        # Delete an existing wildebeest subelement if needed
        if self.WBelem:

            self.root.remove(self.WBelem)

        ## Now rebuild the wildebeest subelement
        self.WBelem = ET.SubElement(self.root, WB_SETTINGS_ELEM)

        # Set the base value
        if self.ui.WBstepsDefaultRadio.isChecked():

            self.WBelem.attrib[WB_BASE_ATTRIB] = WB_BASE_DEFAULT

        elif self.ui.WBstepsAllRadio.isChecked():

            self.WBelem.attrib[WB_BASE_ATTRIB] = WB_BASE_ALL
        else:
            self.WBelem.attrib[WB_BASE_ATTRIB] = WB_BASE_NONE
        
        # Set the language code
        self.WBelem.attrib[WB_LANG_CODE_ATTRIB] = self.ui.WBlangCodeTextBox.text()

        # Create the add and skip sub-elements
        addStepsElem = ET.SubElement(self.WBelem, WB_ADD_STEPS_ELEM)
        skipStepsElem = ET.SubElement(self.WBelem, WB_SKIP_STEPS_ELEM)

        # Remove commas, semicolons spaces or bars and put together again with spaces
        temp = self.ui.WBaddStepsTextBox.text()
        temp = " ".join(regex.split('[\s,;|]+', temp))
        addStepsElem.text = temp

        temp = self.ui.WBskipStepsTextBox.text()
        temp = " ".join(regex.split('[\s,;|]+', temp))
        skipStepsElem.text = temp

    def setWildebeestVisibility(self, makeVisible):

        for widget in self.WBcontrols:

            widget.setVisible(makeVisible)

    def setElementInfo(self, ruleEl):

        searchEl = ruleEl[0]
        replaceEl = ruleEl[1]
        searchEl.text = self.ui.searchTextBox.text()
        replaceEl.text = self.ui.replaceTextBox.text()

        # Set regex attribute
        if self.ui.regexCheckBox.isChecked():
            isRegexStr = "yes"
        else:
            isRegexStr = "no"

        ruleEl.attrib[REGEX_ATTRIB] = isRegexStr

        # Set inactive attribute
        if self.ui.inactiveCheckBox.isChecked():
            isInactiveStr = "yes"
        else:
            isInactiveStr = "no"

        ruleEl.attrib[INACTIVE_ATTRIB] = isInactiveStr

        # Set comment attribute
        ruleEl.attrib[COMMENT_ATTRIB] = self.ui.commentTextBox.text()

    def writeXMLfile(self):

        # Get all the wildebeest info. and save it in the element tree
        self.saveWBinfo()

        # Indent the xml to make it pretty then write it to a file.
        ET.indent(self.ruleFileXMLtree)
        self.ruleFileXMLtree.write(self.searchReplacefile, encoding='utf-8', xml_declaration=True)
