#
#   TextInOutUtils.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
#
#   Version 3.14.1 - 8/8/25 - Ron Lockwood
#   Fixes #1017. Support cluster projects.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
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
import shutil
import json
import xml.etree.ElementTree as ET
from wildebeest.wb_normalize import Wildebeest

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QComboBox, QWidget, QVBoxLayout, QTextEdit, QPushButton

from TextInOut import Ui_TextInOutMainWindow

import ClusterUtils

# Define _translate for convenience
_translate = QCoreApplication.translate

TEXT_IN_SETTINGS_FILE = 'TextInSettings.json'
TEXT_OUT_SETTINGS_FILE = 'TextOutSettings.json'
SELECTED_CLUSTER_PROJECTS = 'selectedClusterProjects'
WORK_PROJECTS = 'workProjects'
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

TEXTOUT_MODULENAME = "Text Out Rules"

ARROW_CHAR = '⭢'

class SearchReplaceRuleData():

    def __init__(self, searchStr, replStr, isRegEx, isInactive, comment):

        self.searchStr = "" if searchStr is None else searchStr
        self.replStr = "" if replStr is None else replStr
        self.isRegEx = isRegEx
        self.isInactive = isInactive
        self.comment = "" if comment is None else comment

class RulesPopup(QWidget):

    def __init__(self, rules_text, parent=None):

        super().__init__(parent, QtCore.Qt.Window | QtCore.Qt.ToolTip)
        self.setWindowTitle("Rules for WorkProject")
        layout = QVBoxLayout(self)

        # Create a QTextEdit to display the rules
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(rules_text)
        self.textEdit.setWordWrapMode(QtGui.QTextOption.NoWrap)

        # Add the QTextEdit to the layout
        layout.addWidget(self.textEdit)

        # Add a close button
        closeBtn = QPushButton("Close", self)
        closeBtn.clicked.connect(self.close)
        layout.addWidget(closeBtn)

        self.setLayout(layout)

        # Add a thin black border
        self.setStyleSheet("border: 1px solid black;")

        self.resize(450, 140)

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

def buildRuleString(searchRplObj, basicInfo=True):

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

    if basicInfo:
        return f'{searchStr} {ARROW_CHAR} {replStr}{regExStr}'

    # If not basic info, include all details
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
                errorMsg = _translate("TextInOutUtils", "Test stopped on failure of rule: {ruleString}").format(ruleString=buildRuleStringFromElement(ruleEl))
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

    def __init__(self, DB, report, configMap, settingName, textIn, winTitle):

        QMainWindow.__init__(self)
        self.ui = Ui_TextInOutMainWindow()
        self.ui.setupUi(self)

        self.DB = DB
        self.report = report
        self.configMap = configMap
        self.settingName = settingName
        self.textIn = textIn
        self.rulesModel = None
        self.ruleIndex = None
        self.settingsMap = {}
        self.xmlTreeList = []
        self.xmlParentObjList = []
        self.xmlRootList = []
        self.filePathList = []
        self.workProjectFoldersList = []
        self.selectedWorkProjects = []
        self.validFolders = False
        self.lastSelectAllState = QtCore.Qt.Checked
        self.retVal = True
        self.keyWidgetList = []

        # Wildebeest widgets
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

        # Get cluster projects from settings;
        self.clusterProjects = ReadConfig.getConfigVal(self.configMap, ReadConfig.CLUSTER_PROJECTS, report=None, giveError=False)

        if not self.clusterProjects:

            self.clusterProjects = []
        else:
            # Remove blank ones
            self.clusterProjects = [x for x in self.clusterProjects if x]

        currDBname = DB.ProjectName()

        if self.clusterProjects:
            
            if currDBname not in self.clusterProjects:

                self.report.Error(_translate("TextInOutUtils", "Current Project not in Cluster Projects list, exiting."))
                self.retVal = False
                self.close()
                return
            
            # Remove the current project from the cluster projects list, we will always use it
            self.clusterProjects.remove(currDBname)

        if textIn:
            self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), TEXT_IN_SETTINGS_FILE)
        else:
            self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), TEXT_OUT_SETTINGS_FILE)

        # Get the work project folders
        workProjPath = FTPaths.WORK_PROJECTS_DIR
        self.workProjectFoldersList.append("...")

        try:
            for foldName in os.listdir(workProjPath):

                foldPath = os.path.join(workProjPath, foldName)

                if os.path.isdir(foldPath):

                    self.workProjectFoldersList.append(foldName)
        except:
            self.report.Error(_translate("TextInOutUtils", "Error accessing work project folders."))


        header1TextStr = _translate("TextInOutUtils", "FLEx project name")
        header2TextStr = _translate("TextInOutUtils", "WorkProject folder")

        # Set the top two widgets that need to be disabled. For this window, use dummy widgets since we don't have something to be disabled.
        self.topWidget1 = self.ui.dummyLabel
        self.topWidget2 = self.ui.dummyLabel

        # Load saved settings
        try:
            with open(self.settingsPath, 'r', encoding='utf-8') as f:

                self.settingsMap = json.load(f)
        except:
            pass

        selectedClusterProjects = self.settingsMap.get(SELECTED_CLUSTER_PROJECTS, [])

        # Create all the possible widgets we need for all the cluster projects
        ClusterUtils.initClusterWidgets(self, QComboBox, self.ui.horizontalLayout_7, header1TextStr, header2TextStr, comboWidth=130, specialProcessFunc=self.setWorkProjectComboBox, 
                                        originalWinHeight=self.height(), noCancelButton=True, containerWidgetToMove=self.ui.widgetContainer)

        # Load cluster projects
        if len(self.clusterProjects) > 0:

            ClusterUtils.initClusterProjects(self, self.clusterProjects, selectedClusterProjects, self.ui.horizontalLayout_7) # load last used cluster projects here

            # Make work project selections in all visible combo boxes
            savedWorkProjList = self.settingsMap.get(WORK_PROJECTS, [])

            for i, wrkProj in enumerate(savedWorkProjList):

                if i < len(self.keyWidgetList):

                    self.keyWidgetList[i].setCurrentText(wrkProj)
        else:
            # Hide cluster project widgets
            widgetsToHide = [
                self.ui.clusterProjectsLabel,
                self.ui.clusterProjectsComboBox,
                self.ui.clusterInfoLabel,
            ]
            for wid in widgetsToHide:

                wid.setVisible(False)

        # Reset icon images
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "UpArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.moveUpButton.setIcon(icon)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "DownArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.moveDownButton.setIcon(icon2)

        self.ui.errorTextBox.setText('')

        self.setWindowTitle(winTitle)

        # See if we are doing text in or out
        if not self.textIn:

            # If we are doing text out, don't show the wildebeest checkbox
            self.hideWildebeestStuff()
        else:
             # Translate the Wildebeest checkbox and help link
             self.ui.wildebeestCheckBox.setText(_translate("TextInOutUtils", "Run the {wildebeest} cleanup tool").format(wildebeest="Wildebeest"))
             helpText = _translate("TextInOutUtils", "help")
             self.ui.WBlinkLabel.setText(f"<html><head/><body><p><a href=\"https://github.com/uhermjakob/wildebeest\"><span style=\" text-decoration: underline; color:#0000ff;\">wildebeest {helpText}</span></a></p></body></html>")

        self.ui.addButton.clicked.connect(self.AddClicked)
        self.ui.selectAllCheckBox.clicked.connect(self.CheckAllClicked)
        self.ui.OKButton.clicked.connect(self.CloseClicked)
        self.ui.deleteButton.clicked.connect(self.DeleteClicked)
        self.ui.moveDownButton.clicked.connect(self.DownButtonClicked)
        self.ui.moveUpButton.clicked.connect(self.UpButtonClicked)
        self.ui.replaceTextBox.textChanged.connect(self.SearchOrReplaceChanged)
        self.ui.rulesList.clicked.connect(self.RulesListClicked)
        self.ui.searchTextBox.textChanged.connect(self.SearchOrReplaceChanged)
        self.ui.testButton.clicked.connect(self.TestClicked)
        self.ui.updateButton.clicked.connect(self.UpdateClicked)
        self.ui.wildebeestCheckBox.clicked.connect(self.WildebeestClicked)

        self.ui.dummyLabel.setVisible(False)
        self.ui.dummyLabel.setText('')

        # Load the rules
        self.checkForValidFolders()
        self.loadRules()
    
    def setWorkProjectComboBox(self, comboWidget):

        # Fill the combo box
        comboWidget.addItems(self.workProjectFoldersList)
    
    def getPath(self, folder):

        if folder == None: # default folder

            config = ReadConfig.readConfig(None)
            rulesRelPath = ReadConfig.getConfigVal(config, self.settingName, report=None, giveError=True)

        # Read the config file in that work project
        else:
            configpath = os.path.join(FTPaths.WORK_PROJECTS_DIR, folder, "Config", ReadConfig.CONFIG_FILE)

            try:
                with open(configpath, 'r', encoding='utf-8') as f:

                    config = ReadConfig.getConfigMap(f, report=None)
            except:
                # Put an error in the error widget
                self.appendError(_translate("TextInOutUtils", "There was a problem reading the configuration file for folder {folderName}. Check your configuration.").format(folderName=folder))
                return None

            rulesRelPath = ReadConfig.getConfigVal(config, self.settingName, report=None, giveError=True, basePath=os.path.join(FTPaths.WORK_PROJECTS_DIR, folder))

        if not rulesRelPath:
            # If no rules file is specified, use a default name
            if self.textIn:
                rulesRelPath = os.path.join("Output", "fixup_paratext_rules.xml")
            else:
                rulesRelPath = os.path.join("Output", "fixup_synthesis_rules.xml")

        if folder == None: # default folder

            rulesPath = os.path.join(FTPaths.WORK_DIR, rulesRelPath)
        else:
            rulesPath = os.path.join(FTPaths.WORK_PROJECTS_DIR, folder, rulesRelPath)

        try:
            # Check if the file exists, if not, create it.
            if os.path.exists(rulesPath) == False:

                # Set a string for an empty rules list
                xmlString = f"<?xml version='1.0' encoding='utf-8'?><{FT_SEARCH_REPLACE_ELEM}><{SEARCH_REPLACE_RULES_ELEM}/></{FT_SEARCH_REPLACE_ELEM}>"

                with open(rulesPath, 'w', encoding='utf-8') as fOut:

                    fOut.write(xmlString)

                # We are going to ignore updating the config file for each project, that get's too complicated. It will get update the next time the user runs the module for that project.
            else:
                # Make a backup copy of the search-replace rule file
                shutil.copy2(rulesPath, rulesPath+'.bak')
        except:
            self.appendError(_translate("TextInOutUtils", 'There was a problem creating or backing up the rules file. Check your configuration.'))
            return None

        return rulesPath

    def eventFilter(self, obj, event):

        # Show popup when mouse enters key widget
        if event.type() == QtCore.QEvent.Enter and obj in self.keyWidgetList:

            # Always close any existing popup before opening a new one
            if hasattr(self, 'rulesPopup') and self.rulesPopup:

                self.rulesPopup.close()
                self.rulesPopup = None
                self._popupActive = False

            idx = 0

            # Get the index of the first non- '...' folder
            for widget in self.keyWidgetList:

                if widget.currentText() != "...":

                    if widget == obj:
                        break

                    idx += 1

            # Check if the folder is ... and if so, don't show rules
            if obj.currentText() == "...":
                return super().eventFilter(obj, event)
            
            # Get the rules text for the folder
            rules_text = self.getRulesTextForFolder(idx)

            # Initialize the popup with the rules text
            self.rulesPopup = RulesPopup(rules_text, self)

            # Install event filter to track mouse events on the popup
            self.rulesPopup.installEventFilter(self)  # Track mouse events on popup

            # Set the popup size and position based on the widget
            pos = obj.mapToGlobal(obj.rect().bottomLeft())

            # Set the popup size to fit the text and show it
            self.rulesPopup.move(pos)
            self.rulesPopup.show()
            self._popupActive = True

        # Hide popup only if mouse leaves both widget and popup
        elif event.type() == QtCore.QEvent.Leave and obj in self.keyWidgetList:

            QtCore.QTimer.singleShot(100, self._maybeClosePopup)

        elif event.type() == QtCore.QEvent.Leave and hasattr(self, 'rulesPopup') and obj == self.rulesPopup:

            QtCore.QTimer.singleShot(100, self._maybeClosePopup)

        elif event.type() == QtCore.QEvent.Enter and hasattr(self, 'rulesPopup') and obj == self.rulesPopup:

            self._popupActive = True

        return super().eventFilter(obj, event)

    def _maybeClosePopup(self):

        # Check if mouse is over popup or any key widget
        if hasattr(self, 'rulesPopup') and self.rulesPopup:

            mouse_pos = QtGui.QCursor.pos()

            # Check popup
            over_popup = self.rulesPopup.geometry().contains(mouse_pos)

            # Check all key widgets (map global mouse pos to widget's local coordinates)
            over_widget = any(w.rect().contains(w.mapFromGlobal(mouse_pos)) for w in self.keyWidgetList)

            # If mouse is not over popup and not over any key widget, close the popup
            if not over_popup and not over_widget:

                self.rulesPopup.close()
                self.rulesPopup = None
                self._popupActive = False

    def getRulesTextForFolder(self, idx):

        # idx: index in self.keyWidgetList, matches self.xmlParentObjList[1:] (default is [0])
        if idx+1 < len(self.xmlParentObjList):

            rulesElem = self.xmlParentObjList[idx+1]
            rules = []

            # Loop through the rules in the element and build a string
            for ruleEl in rulesElem:

                rules.append(buildRuleString(getRuleFromElement(ruleEl)))

            return "\n".join(rules) if rules else "No rules found."
        else:
            return "No rules found."

    def clusterSelectionChanged(self):

        # Write the XML files if we have xml data
        if self.xmlParentObjList:
            
            self.writeXMLfile()

        # Create needed widgets and position them
        ClusterUtils.showClusterWidgets(self)

        # Connect folder combo boxes to a function
        for widget in self.keyWidgetList:

            widget.currentIndexChanged.connect(self.checkForValidFolders)
            widget.installEventFilter(self)
        
        self.checkForValidFolders()
        
    def AddClicked(self):
        
        # Clear the error message widget
        self.ui.errorTextBox.setText('')

        myDataObj = self.initDataObj()

        # Build the rule string for the rule list
        ruleStr = buildRuleString(myDataObj)

        # Get the row #
        if self.ruleIndex:

            rowNum = self.ruleIndex.row()
        else:
            rowNum = 0

        defaultProjRowNum = rowNum

        # Create an item object
        item = QStandardItem(ruleStr) 
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.Checked)

        # Insert it
        self.rulesModel.insertRow(rowNum, item)

        # Select it
        qIndex = self.rulesModel.createIndex(rowNum, 0)
        self.ui.rulesList.setCurrentIndex(qIndex)

        # Add it to the element tree
        for i in range(len(self.selectedWorkProjects)+1):

            if i > 0: # We have the default project row number already

                # Find the rule in the current folder's rule list
                rowNum = self.findMatch(self.xmlParentObjList[i], myDataObj)

                if rowNum == -1: # not found

                    # Put into the same row as the default project
                    if defaultProjRowNum < len(self.xmlParentObjList[i]):
                        rowNum = defaultProjRowNum
                    else:
                        # If the default project row number is out of range, put it at the end
                        rowNum = len(self.xmlParentObjList[i])
                else:
                    self.appendError(_translate("TextInOutUtils", "For folder {foldName}, the rule: {ruleID} already exists.").format(foldName=self.selectedWorkProjects[i-1], 
                                                                                                                                      ruleID=buildRuleString(myDataObj, basicInfo=True)))
                    continue

            # Construct the etree elements
            newRuleEl = ET.Element(SEARCH_REPL_RULE_ELEM)
            ET.SubElement(newRuleEl, SEARCH_STRING_ELEM)
            ET.SubElement(newRuleEl, REPL_STRING_ELEM)

            # Set element text and attributes
            self.setElementInfo(newRuleEl)

            # Add the rule, possibly at the beginning if row number is 0
            self.xmlParentObjList[i].insert(rowNum, newRuleEl)

            if defaultProjRowNum == 0:

                # Build the currentIndex with this row number
                self.ruleIndex = self.rulesModel.index(defaultProjRowNum, 0)

            self.RulesListClicked(self.ruleIndex)

    def UpdateClicked(self):
        
        # Clear the error message widget
        self.ui.errorTextBox.setText('')

        # Get the rule data at the current index selected
        myItem = self.rulesModel.itemFromIndex(self.ruleIndex)
        rowNum = self.ruleIndex.row()

        # Get the current info for doing the find match
        oldDataObj = getRuleFromElement(self.xmlParentObjList[0][rowNum])
        oldRuleStr = buildRuleString(oldDataObj, basicInfo=True)

        # Build the rule string for the rule list
        myDataObj = self.initDataObj()
        ruleStr = buildRuleString(myDataObj)

        # Update the selected rule
        myItem.setText(ruleStr)
        myItem.setCheckState(QtCore.Qt.Checked)

        # Update the etree elements
        for i in range(len(self.selectedWorkProjects)+1):

            if i > 0: # We have the default project row number already

                # Find the rule in the current folder's rule list
                rowNum = self.findMatch(self.xmlParentObjList[i], oldDataObj)

                if rowNum == -1:

                    self.appendError(_translate("TextInOutUtils", "For folder {foldName}, the rule: {ruleID} was not found.").format(foldName=self.selectedWorkProjects[i-1], 
                                                                                                                                     ruleID=oldRuleStr))
                    continue

            # Get the rule element
            ruleEl = self.xmlParentObjList[i][rowNum]
            
            # Set element text and attributes
            self.setElementInfo(ruleEl)

        # Enable the delete button in case we were at 0 rows before.
        self.ui.deleteButton.setEnabled(True)

    def DeleteClicked(self):

        # Clear the error message widget
        self.ui.errorTextBox.setText('')

        if self.ruleIndex:

            rowCount = self.rulesModel.rowCount()

            # Remove the row
            rowNum = defaultRow = self.ruleIndex.row()
            self.rulesModel.removeRow(rowNum)

            # Get the current info for doing the find match
            oldDataObj = getRuleFromElement(self.xmlParentObjList[0][rowNum])
            oldRuleStr = buildRuleString(oldDataObj, basicInfo=True)

            # Update the etree elements
            for i in range(len(self.selectedWorkProjects)+1):

                if i > 0: # We have the default project row number already

                    # Find the rule in the current folder's rule list
                    rowNum = self.findMatch(self.xmlParentObjList[i], oldDataObj)

                    if rowNum == -1:

                        self.appendError(_translate("TextInOutUtils", "For folder {foldName}, the rule: {ruleID} was not found.").format(foldName=self.selectedWorkProjects[i-1], 
                                                                                                                                         ruleID=oldRuleStr))
                        continue

                # Remove this row from the etree
                self.xmlParentObjList[i].remove(self.xmlParentObjList[i][rowNum])

            # If this was the last remaining row, disable the delete button
            if self.rulesModel.rowCount() < 1:

                self.ui.deleteButton.setEnabled(False)
                self.ui.updateButton.setEnabled(False)
                self.ui.searchTextBox.setText('')
                self.ui.replaceTextBox.setText('')
                self.ui.commentTextBox.setText('')
                self.ui.regexCheckBox.setChecked(False)
                self.ui.inactiveCheckBox.setChecked(False)
        
            # If we are deleting the first and last row, set index to None.
            if defaultRow == 0 and rowCount == 1:

                # If we are deleting the first row, set the ruleIndex to None
                self.ruleIndex = None  
                return
            
            # If we are deleting the last row in the list, set the ruleIndex to the previous row
            elif defaultRow == rowCount-1:

                self.ruleIndex = self.rulesModel.index(defaultRow - 1, 0)

            # Update the text in the search and replace text boxes
            self.RulesListClicked(self.ruleIndex)

    def findMatch(self, xmlObj, myDataObj):

        # Loop through the rules in the xmlObj
        for i, ruleEl in enumerate(xmlObj):

            searchReplDataObj = getRuleFromElement(ruleEl)

            # If we find a match, return the row number
            if (searchReplDataObj.searchStr == myDataObj.searchStr and
                searchReplDataObj.replStr == myDataObj.replStr and
                searchReplDataObj.isRegEx == myDataObj.isRegEx):

                return i

        # If we didn't find a match, return -1
        return -1
    
    def CheckAllClicked(self):

        state = self.ui.selectAllCheckBox.checkState()

        if state == QtCore.Qt.Checked:

            newState = state

        elif state == QtCore.Qt.Unchecked:

            newState = QtCore.Qt.Unchecked

        else: #state == QtCore.Qt.PartiallyChecked:
            
            newState = QtCore.Qt.Checked
            self.ui.selectAllCheckBox.setCheckState(QtCore.Qt.Checked)

        if self.lastSelectAllState == QtCore.Qt.PartiallyChecked:

            newState = QtCore.Qt.Unchecked
            self.ui.selectAllCheckBox.setCheckState(QtCore.Qt.Unchecked)

        # Loop through all the items in the rule list model
        for i in range(0, self.rulesModel.rowCount()):

            # change each box
            self.rulesModel.item(i).setCheckState(newState)

        self.RulesListClicked(self.ui.rulesList.currentIndex())

    def CloseClicked(self):
        
        self.writeXMLfile()
        self.close()

    def closeEvent(self, event):

        self.CloseClicked()

    def UpButtonClicked(self):

        # Clear the error message widget
        self.ui.errorTextBox.setText('')
        
        if self.ruleIndex and self.ruleIndex.row() > 0:
            
            rowNum = defaultRowNum = self.ruleIndex.row()

            # Get the current info for doing the find match
            oldDataObj = getRuleFromElement(self.xmlParentObjList[0][rowNum])
            oldRuleStr = buildRuleString(oldDataObj, basicInfo=True)

            # Add it to the element tree
            for i in range(len(self.selectedWorkProjects)+1):

                if i > 0: # We have the default project row number already

                    # Find the rule in the current folder's rule list
                    rowNum = self.findMatch(self.xmlParentObjList[i], oldDataObj)

                    if rowNum == -1: # not found

                        self.appendError(_translate("TextInOutUtils", "For folder {foldName}, the rule: {ruleID} not found.").format(foldName=self.selectedWorkProjects[i-1], 
                                                                                                                                     ruleID=oldRuleStr))
                        continue

                # If the row number found was zero, we skip moving it.
                if rowNum > 0:

                    # move the XML sub-element
                    elemToMove = self.xmlParentObjList[i][rowNum]
                    self.xmlParentObjList[i].remove(elemToMove)
                    self.xmlParentObjList[i].insert(rowNum-1, elemToMove)

            # copy the check state from one row to the other
            currState = self.rulesModel.item(defaultRowNum).checkState()
            othState = self.rulesModel.item(defaultRowNum-1).checkState()
            self.rulesModel.item(defaultRowNum).setCheckState(othState)
            self.rulesModel.item(defaultRowNum-1).setCheckState(currState)

            # copy the rule string from one row to the other
            currStr = self.rulesModel.item(defaultRowNum).text()
            othStr = self.rulesModel.item(defaultRowNum-1).text()
            self.rulesModel.item(defaultRowNum).setText(othStr)
            self.rulesModel.item(defaultRowNum-1).setText(currStr)
            
            myIndex = self.rulesModel.index(defaultRowNum-1, self.ruleIndex.column())
            self.ui.rulesList.setCurrentIndex(myIndex)

            # redo the display
            self.RulesListClicked(myIndex)
            
    def DownButtonClicked(self):
        
        # Clear the error message widget
        self.ui.errorTextBox.setText('')

        if self.ruleIndex and self.ruleIndex.row() < self.rulesModel.rowCount()-1:
            
            rowNum = defaultRowNum = self.ruleIndex.row()

            # Get the current info for doing the find match
            oldDataObj = getRuleFromElement(self.xmlParentObjList[0][rowNum])
            oldRuleStr = buildRuleString(oldDataObj, basicInfo=True)

            # Add it to the element tree
            for i in range(len(self.selectedWorkProjects)+1):

                if i > 0: # We have the default project row number already

                    # Find the rule in the current folder's rule list
                    rowNum = self.findMatch(self.xmlParentObjList[i], oldDataObj)

                    if rowNum == -1: # not found

                        self.appendError(_translate("TextInOutUtils", "For folder {foldName}, the rule: {ruleID} not found.").format(foldName=self.selectedWorkProjects[i-1], 
                                                                                                                                     ruleID=oldRuleStr))
                        continue

                # If the row number is at the end of the list, we skip moving it.
                if rowNum < len(self.xmlParentObjList[i])-1:

                    # move the XML sub-element
                    elemToMove = self.xmlParentObjList[i][rowNum]
                    self.xmlParentObjList[i].remove(elemToMove)
                    self.xmlParentObjList[i].insert(rowNum+1, elemToMove)

            # copy the check state from one row to the other
            currState = self.rulesModel.item(defaultRowNum).checkState()
            othState = self.rulesModel.item(defaultRowNum+1).checkState()
            self.rulesModel.item(defaultRowNum).setCheckState(othState)
            self.rulesModel.item(defaultRowNum+1).setCheckState(currState)
            
            # copy the rule string from one row to the other
            currStr = self.rulesModel.item(defaultRowNum).text()
            othStr = self.rulesModel.item(defaultRowNum+1).text()
            self.rulesModel.item(defaultRowNum).setText(othStr)
            self.rulesModel.item(defaultRowNum+1).setText(currStr)
            
            myIndex = self.rulesModel.index(defaultRowNum+1, self.ruleIndex.column())
            self.ui.rulesList.setCurrentIndex(myIndex)

            # redo the display
            self.RulesListClicked(myIndex)

    def RulesListClicked(self, index):
        
        self.ruleIndex = index
        
        # Get rule data for current index. Get it from the element tree object.
        searchReplaceRuleData = getRuleFromElement(self.xmlParentObjList[0][index.row()])
                        
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
        if self.validFolders:

            self.enableControls(True)

        # Figure out last checked state
        oneBoxChecked = False
        oneBoxUnchecked = False
        
        self.rulesChanged = True

        for i in range(0, self.rulesModel.rowCount()):

            # If active add text with the active rule #
            if self.rulesModel.item(i).checkState():

                oneBoxChecked = True
            else:
                oneBoxUnchecked = True

        # If we have a mix of checked and unchecked boxes, set the select All CheckBox to partially checked
        if oneBoxChecked and oneBoxUnchecked:

            self.ui.selectAllCheckBox.setCheckState(QtCore.Qt.PartiallyChecked)
            self.lastSelectAllState = QtCore.Qt.PartiallyChecked

        elif oneBoxChecked:

            self.ui.selectAllCheckBox.setCheckState(QtCore.Qt.Checked)
            self.lastSelectAllState = QtCore.Qt.Checked
        else:
            self.ui.selectAllCheckBox.setCheckState(QtCore.Qt.Unchecked)
            self.lastSelectAllState = QtCore.Qt.Unchecked

    def SearchOrReplaceChanged(self):
        
        # if search is non-empty, and either we have no cluster projects, or we have cluster projects and valid folders, then enable the buttons
        if self.ui.searchTextBox.text() and (not self.clusterProjects or (self.clusterProjects and self.validFolders)):

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
            self.ui.deleteButton.setEnabled(False)
            self.ui.regexCheckBox.setEnabled(False)
            self.ui.inactiveCheckBox.setEnabled(False)
                
    def TestClicked(self):

        self.ui.errorTextBox.setText('')

        self.writeXMLfile()

        inStr = self.ui.inputText.toPlainText()
        newStr = inStr

        # Run Wildebeest if needed
        if self.ui.wildebeestCheckBox.isChecked():

            newStr = runWildebeest(self.defaultRoot, newStr)

        # Loop through the rules and apply each checked one in turn
        for ind, ruleEl in enumerate(self.xmlParentObjList[0]):

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
                        self.ui.errorTextBox.setText(_translate(
                                "TextInOutUtils",
                                "Test stopped on failure of rule {ruleNumber}: {ruleString}"
                            ).format(ruleNumber=str(ind + 1), ruleString=buildRuleStringFromElement(ruleEl))
                        )
                        break

        self.ui.outputText.setText(newStr)
        return

    def appendError(self, errorStr):

        # Append the error to the error text box
        currentText = self.ui.errorTextBox.toPlainText()

        if currentText:

            currentText += '\n'

        currentText += errorStr
        self.ui.errorTextBox.setText(currentText)

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

    def enableControls(self, enabled: bool):

        self.ui.addButton.setEnabled(enabled)
        self.ui.updateButton.setEnabled(enabled)
        self.ui.deleteButton.setEnabled(enabled)
        self.ui.regexCheckBox.setEnabled(enabled)
        self.ui.inactiveCheckBox.setEnabled(enabled)

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

    def checkForValidFolders(self) -> bool:

        self.validFolders = True

        self.initLists()

        # If we have a ..., we have an invalid folder.
        for widget in self.keyWidgetList:

            if widget.currentText() == '...':

                self.validFolders = False
                break

        # If we don't have valid folders, disable the controls, give an error.
        if not self.validFolders:

            self.ui.errorTextBox.setText('Please select a valid folder for each project.')
        else:
            self.ui.errorTextBox.setText('')

        # Enable or disable controls based on valid folders
        self.SearchOrReplaceChanged()

        return self.validFolders
    
    def loadRules(self):
        
        self.rulesModel = QStandardItemModel()
        parentElement = self.xmlParentObjList[0]
        self.displayRules(parentElement, self.rulesModel)
        
        # Initialize the model for the rule list control
        self.ui.rulesList.setModel(self.rulesModel)

        # Set Wildebeest controls
        self.defaultRoot = self.xmlRootList[0]
        self.initWBcontrols(self.defaultRoot)

    def enumerateWorkProjects(self):

        return [myCombo.currentText() for myCombo in self.keyWidgetList if myCombo.currentText() != '...']

    def initLists(self):

        self.xmlTreeList.clear()
        self.xmlParentObjList.clear()
        self.xmlRootList.clear()
        self.filePathList.clear()

        # The default project is always the first one in the list.
        path = self.getPath(None)
        try:
            tree = ET.parse(path)
        except:
            self.report.Error(_translate("TextInOutUtils", "Error loading XML file."))
            raise

        self.xmlTreeList = [tree]

        self.defaultRoot = tree.getroot()
        self.xmlRootList = [self.defaultRoot]
        searchReplaceRulesElement = self.defaultRoot.find(SEARCH_REPLACE_RULES_ELEM)
        self.xmlParentObjList = [searchReplaceRulesElement]
        self.filePathList = [path]

        if len(self.clusterProjects) > 0:

            self.selectedWorkProjects = self.enumerateWorkProjects()

            for folder in self.selectedWorkProjects:

                # Get the path to the rules file and parse it
                path = self.getPath(folder)

                if not path:
                    continue

                try:
                    tree = ET.parse(path)
                except:
                    self.report.Error(_translate("TextInOutUtils", "Error loading XML file."))
                    raise

                self.xmlTreeList.append(tree)

                # Get the parent element of the rule elements
                root = tree.getroot()
                self.xmlRootList.append(root)
                searchReplaceRulesElement = root.find(SEARCH_REPLACE_RULES_ELEM)
                self.xmlParentObjList.append(searchReplaceRulesElement)
                self.filePathList.append(path)

    def saveWBinfo(self, xmlRoot):

        # Set root wildebeest boolean
        if not self.ui.wildebeestCheckBox.isChecked():

            xmlRoot.attrib[APPLY_WILDEBEEST_ATTRIB] = "no"

        else:
            xmlRoot.attrib[APPLY_WILDEBEEST_ATTRIB] = "yes"
        
        # Find the Wildebeest section
        self.WBelem = xmlRoot.find(WB_SETTINGS_ELEM)

        # Delete an existing wildebeest subelement if needed
        if self.WBelem:

            xmlRoot.remove(self.WBelem)

        ## Now rebuild the wildebeest subelement
        self.WBelem = ET.SubElement(xmlRoot, WB_SETTINGS_ELEM)

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

        # Save last used settings to a json file
        self.settingsMap = {}
        self.settingsMap[WORK_PROJECTS] = [myCombo.currentText() for myCombo in self.keyWidgetList]
        self.settingsMap[SELECTED_CLUSTER_PROJECTS] = self.ui.clusterProjectsComboBox.currentData()

        try:
            with open(self.settingsPath, 'w', encoding='utf-8') as f:
                
                json.dump(self.settingsMap, f, indent=4)
        except:
            self.report.Error(_translate("TextInOutUtils", "Error saving settings."))

        if len(self.selectedWorkProjects) > 0:

            for i in range(len(self.selectedWorkProjects)+1): # +1 for the default project

                # Get all the wildebeest info. and save it in the element tree
                self.saveWBinfo(self.xmlRootList[i])

                # Indent the xml to make it pretty then write it to a file.
                ET.indent(self.xmlTreeList[i])
                self.xmlTreeList[i].write(self.filePathList[i], encoding='utf-8', xml_declaration=True)

                # We are done after the 0th project, if it is the default project so break out of the loop
                if len(self.clusterProjects) == 0:
                    break