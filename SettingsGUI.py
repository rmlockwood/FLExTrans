#
#   Settings GUI
#   Lærke Roager Christensen 
#   3/28/22
#
#   Version 3.9.4 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.3 - 7/19/23 - Ron Lockwood
#    Fixes #465. Strip whitespace characters when saving text, file or folder strings
#
#   Version 3.9.2 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.9.1 - 6/21/23 - Ron Lockwood
#    Added limit_pos setting to the things that get disabled when the Target DB changes.
#
#   Version 3.9 - 6/2/23 - Ron Lockwood
#    Fixes #443. Reorganized settings file in to sections with titles. Synthesis
#    test settings added. Added a parameter to hide a setting from the user. Hid some HC
#    settings. Category pairs now correctly uses target categories for 2nd item.
#
#   Version 3.8.4 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names.
#
#   Version 3.8.3 - 4/20/23 - Ron Lockwood
#    Corrected typo.
#
#   Version 3.8.2 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function. Also don't confirm changes if no settings were changed.
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Settings are now launched from the menu
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.6 - 1/30/23 - Ron Lockwood
#    Official support for creating a vocabulary list of unlinked senses. The tool creates an html file
#    with a table containing source headword, gloss and category plus blank cells for the target
#    language and a comment. Also below this info. is the sentence where the sense was found with the
#    word marked in bold type. A new setting for ProperNoun abbrev. added.
#
#   Version 3.7.5 - 12/7/22 - Ron Lockwood
#    Fixes #285. Allow some settings to be missing without giving an error.
#    The next time the settings are saved, the settings will be created. As part
#    of this fix, created a map from config setting name to widget.
#
#   Version 3.7.4 - 11/14/22 - Ron Lockwood
#    Shorter height for the window. Fixes #321
#
#   Version 3.7.3 - 11/7/22 - Ron Lockwood
#    Two new transfer rule file settings for advanced transfer.
#
#   Version 3.7.2 - 11/1/22 - Ron Lockwood
#    Fixes #154. Show user what settings changed.
#
#   Version 3.7.1 - 11/1/22 - Ron Lockwood
#    Fixes #174. Fixes #282. Fixes #298. Disable certain target settings if the 
#    target project is invalid or when the target project gets changed.
#
#   Version 3.7 - 11/1/22 - Ron Lockwood
#    Fixes #284. Load only analysis titles of interlinear texts.
#
#   Version 3.6.3 - 10/21/22 - Ron Lockwood
#    Fixes #236 Added Close and Apply/Close buttons. Detect Check Combo Box changes.
#
#   Version 3.6.2 - 9/7/22 - Ron Lockwood
#    Fixes #269 When target DB isn't found, allow the Window to open so it can be set.
#
#   Version 3.6.1 - 8/27/22 - Ron Lockwood
#    Fixes #215 Check morpheme type against guid in the object instead of
#    the analysis writing system so we aren't dependent on an English WS.
#    Also don't load types that aren't in the broad category of 'stem'.
#
#   Version 3.6 - 8/24/22 - Ron Lockwood
#    Added 'sense-level' to the tool tip for the custom fields
#
#   Version 3.5.9 - 8/10/22 - Ron Lockwood
#    Added new setting for composed characters.
#
#   Version 3.5.8 - 8/8/22 - Ron Lockwood
#    Fixes #188. Missing tooltip for checkable combos. Extra blank string in the
#    master list removed.
#
#   Version 3.5.7 - 7/30/22 - Ron Lockwood
#    Fixes #199. On certain settings allow the list box to load even if the
#    setting is blank.
#
#   Version 3.5.6 - 7/27/22 - Ron Lockwood
#    Use relative paths now. One thing this helps with, is if a project folder
#    gets copied from one place to another, the file paths will be to the new
#    files in the new folder since the paths are relative. Fixes #194.
#
#   Version 3.5.5 - 7/13/22 - Ron Lockwood
#    Give error if fail to open target DB.
#
#   Version 3.5.4 - 7/8/22 - Ron Lockwood
#    Rewrite of this module to have a master list of settings and associated
#    widgets. Loop through the widget list in various places to set up the window
#    and process data coming in and going out. Fixes #151. Fixes #153. Fixes #137.
#
#   Version 3.5.3 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.2 - 6/21/22 - Ron Lockwood
#    Fixes for #141 and #144. Alphabetize source text list. Correctly load
#    and save source complex types. Also change double loop code for multiple
#    select settings to use x in y instead of the outer loop. This is easier to
#    understand and is maybe more efficient.
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   To make it easier to change the configfile
#

import os
import sys

from System.Windows.Forms import (MessageBox, MessageBoxButtons)

from flextoolslib import FlexToolsModuleClass
from flextoolslib import *

from SIL.LCModel import IMoMorphType
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog

from ComboBox import CheckableComboBox
from flexlibs import FLExProject, AllProjectNames

import Utils
import ReadConfig
import FTPaths

# ----------------------------------------------------------------
# This won't be seen anymore by the user since it gets launced from the menu

docs = {FTM_Name: "",
        FTM_Version: "",
        FTM_ModifiesDB: False,
        FTM_Synopsis: "",
        FTM_Help: "",
        FTM_Description:""}

### See widget list at the bottom and instructions for adding a new setting ###

LABEL_TEXT = 0
WIDGET1_OBJ_NAME = 1
WIDGET2_OBJ_NAME = 2
WIDGET_TYPE = 3
LABEL_OBJ = 4
WIDGET1_OBJ = 5
WIDGET2_OBJ = 6
LOAD_FUNC = 7
CONFIG_NAME = 8
WIDGET_TOOLTIP = 9
GIVE_ERROR_IF_NOT_PRESENT = 10
HIDE_SETTING = 11

COMBO_BOX = "combobox"
SIDE_BY_SIDE_COMBO_BOX = "side by side"
CHECK_COMBO_BOX = "checkable_combobox"
YES_NO = "yes no"
TEXT_BOX = "textbox"
FILE = "file"
FOLDER = "folder"
SECTION_TITLE = "section_title"
GIVE_ERROR = True
DONT_GIVE_ERROR = False
DONT_HIDE = False
HIDE_FROM_USER = True

targetComplexTypes = []
sourceComplexTypes = []
categoryList = []

def getSourceCategoryList(wind):
    
    if len(categoryList) == 0:
        
        for pos in wind.DB.lp.AllPartsOfSpeech:
            
            catStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            categoryList.append(catStr)
            
    return categoryList
            
def getTargetCategoryList(wind):
    
    if len(categoryList) == 0:
        
        for pos in wind.targetDB.lp.AllPartsOfSpeech:
            
            catStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            categoryList.append(catStr)
            
    return categoryList
            
def getTargetComplexTypes(wind):
    
    if len(targetComplexTypes) == 0:
        
        if wind.targetDB:
        
            for item in wind.targetDB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
                
                targetComplexTypes.append(str(item))
            
    return targetComplexTypes
            
def getSourceComplexTypes(wind):
    
    if len(sourceComplexTypes) == 0:
        
        for item in wind.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            
            sourceComplexTypes.append(str(item))
            
    return sourceComplexTypes
            
def loadSourceTextListForSettings(widget, wind, settingName):
    
    # Create a list of source text names
    sourceList = Utils.getSourceTextList(wind.DB)

    sortedSourceList = sorted(sourceList, key=str.casefold)
    
    # Get the source name from the config file
    configSource = wind.read(settingName)
    
    if configSource is not None:

        # Add items and when we find the one that matches the config file. Set that one to be displayed.
        for i, itemStr in enumerate(sortedSourceList):
            
            widget.addItem(itemStr)
            
            if itemStr == configSource:
                
                widget.setCurrentIndex(i)

def loadCustomEntry(widget, wind, settingName):
    
    # Get the custom field to link to target entry
    customTarget = wind.read(settingName)
    
    if customTarget is not None:

        # Add items and when we find the one that matches the config file. Set that one to be displayed.
        for i, item in enumerate(wind.DB.LexiconGetSenseCustomFields()):
    
            # item is a tuple, (id, name)
            widget.addItem(str(item[1]))           
    
            if item[1] == customTarget:
                
                widget.setCurrentIndex(i)

def loadTargetProjects(widget, wind, settingName):

    targetProject = wind.read(settingName)
    
    # TODO: Make this disable the other stuff that uses target??
    for i, item in enumerate(AllProjectNames()):
        
        widget.addItem(item)
        
        if targetProject and item == targetProject:
            
            widget.setCurrentIndex(i)
            
def loadSourceComplexFormTypes(widget, wind, settingName):

    typesList = getSourceComplexTypes(wind)

    widget.addItems(typesList)
    
    complexType = wind.read(settingName)
    
    if complexType:

        for comType in complexType:

            if comType in typesList:
                
                widget.check(comType)
                
def loadTargetComplexFormTypes(widget, wind, settingName):

    typesList = getTargetComplexTypes(wind)

    widget.addItems(typesList)
    
    complexType = wind.read(settingName)
    
    if complexType:

        for comType in complexType:

            if comType in typesList:
                
                widget.check(comType)

def loadSourceMorphemeTypes(widget, wind, settingName):

    typesList = []
    
    for item in wind.DB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
        
        item = IMoMorphType(item)
        
        # Only load things that can be stems
        if item.IsStemType == True:
            
            # convert this item's id to a string
            myGuid = item.Guid.ToString()
            morphTypeStr = Utils.morphTypeMap[myGuid]
            
            typesList.append(morphTypeStr)
    
    widget.addItems(typesList)
    
    morphNames = wind.read(settingName)
    
    if morphNames:

        for morphName in morphNames:

            if morphName in typesList:
                
                widget.check(morphName)

def loadTargetMorphemeTypes(widget, wind, settingName):

    typesList = []
    
    if wind.targetDB:
        
        for item in wind.targetDB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:

            item = IMoMorphType(item)

            # Only load things that can be stems
            if item.IsStemType == True:
                
                # convert this item's id to a string
                myGuid = item.Guid.ToString()
                morphTypeStr = Utils.morphTypeMap[myGuid]
                
                typesList.append(morphTypeStr)
        
        widget.addItems(typesList)
        
        morphNames = wind.read(settingName)
        
        if morphNames:
    
            for morphName in morphNames:
    
                if morphName in typesList:
                    
                    widget.check(morphName)

def loadSourceCategories(widget, wind, settingName):

    catList = getSourceCategoryList(wind)
    
    widget.addItems(catList)
    
    disCategories = wind.read(settingName)
    
    if disCategories:

        for cat in disCategories:

            if cat in catList:
                
                widget.check(cat)

def loadTargetCategories(widget, wind, settingName):

    catList = getTargetCategoryList(wind)
    
    widget.addItems(catList)
    
    disCategories = wind.read(settingName)
    
    if disCategories:

        for cat in disCategories:

            if cat in catList:
                
                widget.check(cat)

def loadSourceCategoriesNormalListBox(widget, wind, settingName):

    catList = getSourceCategoryList(wind)
    
    catProperNoun = wind.read(settingName)
    
    for i, cat in enumerate(catList):

        widget.addItem(cat)
        
        if catProperNoun and cat == catProperNoun:
            
            widget.setCurrentIndex(i)

def loadCategorySubLists(widget1, widget2, wind, settingName):

    catList = getSourceCategoryList(wind)
    
    widget1.addItems(catList)

    tgtCatList = getTargetCategoryList(wind)

    widget2.addItems(tgtCatList)
    
    catPair = wind.read(settingName)
    
    if catPair:

        for i, cat in enumerate(catList):
            
            if cat == catPair[0]: # The first one in the config file
                
                widget1.setCurrentIndex(i+1) # ... is the first item

        for i, cat in enumerate(tgtCatList):
            
            if cat == catPair[1]: # The second one in the config file
                
                widget2.setCurrentIndex(i+1) # ... is the first item

def loadYesNo(widget, widget2, wind, settingName):            

    yesNo = wind.read(settingName)
    
    if yesNo == 'y':
        
        widget.setChecked(True)
    else:
        widget2.setChecked(True)

def loadTextBox(widget, wind, settingName):            

    text = wind.read(settingName)
    
    if text is not None:
        
        widget.setText(text)

def loadFile(widget, wind, settingName):            

    path = wind.read(settingName)
    
    if path:

        setPaths(widget, path)

def reportChange(wind, mySet, myWidgInfo):
    
    # create a new function that will call doBrowse with the given parameters
    def report_it():
        
        doReport(mySet, myWidgInfo)
        wind.setModifiedFlag()
        
    return report_it

def reportChangeAndDisable(wind, mySet, myWidgInfo):
    
    # create a new function that will call doBrowse with the given parameters
    def report_it():
        
        doReport(mySet, myWidgInfo)
        wind.setModifiedFlag()
        wind.disableTargetWidgets()
        
    return report_it

def doReport(mySet, myWidgInfo):
    
    mySet.add(myWidgInfo[LABEL_TEXT])
    
def makeOpenFile(wind, myWidgInfo):
    
    # create a new function that will call doBrowse with the given parameters
    def open_file():
        
        doBrowse(wind, myWidgInfo)
        wind.setModifiedFlag()
        
    return open_file
    
    doBrowse(wind, myWidgInfo)
    
def makeOpenFolder(wind, myWidgInfo):
    
    # create a new function that will call doBrowse with the given parameters
    def open_folder():
        
        doFolderBrowse(wind, myWidgInfo)
        wind.setModifiedFlag()
        
    return open_folder
    
    doBrowse(wind, myWidgInfo)
    
def doBrowse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = os.path.dirname(wind.read(myWidgInfo[CONFIG_NAME]))
    
    if not os.path.isdir(startDir):
        
        startDir = ""
                   
    filename, _ = QFileDialog.getOpenFileName(wind, "Select file", startDir, "(*.*)")
    
    if filename:
        
        setPaths(myWidgInfo[WIDGET1_OBJ], filename)

def doFolderBrowse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = wind.read(myWidgInfo[CONFIG_NAME])
    
    if not os.path.isdir(startDir):
        
        startDir = ""
                   
    dirName = QFileDialog.getExistingDirectory(wind, "Select Folder", startDir, options=QFileDialog.ShowDirsOnly)
    
    if dirName:
        
        setPaths(myWidgInfo[WIDGET1_OBJ], dirName)

def setPaths(widget, myPath):
    
    # start the rel path relative to the project folder which is the parent of the config folder
    startPath = FTPaths.WORK_DIR
    widget.setText(os.path.relpath(myPath, startPath))
    widget.setToolTip(os.path.relpath(myPath, startPath))
    
class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 630)
        MainWindow.setMaximumSize(QtCore.QSize(910, 1000))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())

        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(750, 200))
        self.scrollArea.setMaximumSize(QtCore.QSize(900, 1000))

        font = QtGui.QFont()
#         font.setFamily("Arial")
        font.setPointSize(9)

        self.scrollArea.setFont(font)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 847, 1046))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # Set up scroll area
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 6) # span 6 columns

        self.apply_button = QtWidgets.QPushButton(self.centralwidget)
        self.apply_button.setObjectName("apply_button")
        self.gridLayout.addWidget(self.apply_button, 1, 3, 1, 1) # put the buttons at columns 3-5 so they are on the right side

        self.applyClose_button = QtWidgets.QPushButton(self.centralwidget)
        self.applyClose_button.setObjectName("applyClose_button")
        self.gridLayout.addWidget(self.applyClose_button, 1, 4, 1, 1)

        self.Close_button = QtWidgets.QPushButton(self.centralwidget)
        self.Close_button.setObjectName("Close_button")
        self.gridLayout.addWidget(self.Close_button, 1, 5, 1, 1)

        # Set up for the fields in the config file
        # They are placed in the order according to the widgetList
        # AddWidget function takes 5 parameters.
        # addWidget(Object, row, column, row-span, column-span)
        j = 1
        for i in range(0, len(widgetList)):

            widgInfo = widgetList[i]
            
            newObj = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.gridLayout_2.addWidget(newObj, i+j, 0, 1, 1)
            widgInfo[LABEL_OBJ] = newObj

            # Hide the widget if necessary
            if widgInfo[HIDE_SETTING] == HIDE_FROM_USER:

                newObj.hide()
                j -= 1

            # Process section title
            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:

                # Make the section header bold
                font = QtGui.QFont()
                font.setBold(True)
                newObj.setFont(font)

                # Add a horizontal line
                line = QtWidgets.QFrame(self.scrollAreaWidgetContents)
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Sunken)
                line.setObjectName("line")
                j += 1
                self.gridLayout_2.addWidget(line, i+j, 0, 1, 4)
                continue

            elif widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
            elif widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                newObj = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                
                # Add a blank item
                newObj.addItem("")
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 1)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                
                # Add a blank item
                newObj.addItem("")
                self.gridLayout_2.addWidget(newObj, i+j, 2, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                # Yes radio button
                newObj = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                
                # Create a button group so these two radio buttons can be distinct from any subsequent ones
                buttonGroup=QtWidgets.QButtonGroup(self.scrollAreaWidgetContents)
                
                # Add the button to the button group
                buttonGroup.addButton(newObj)
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 1)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
                # No radio button - checked
                newObj = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])

                # Add the button to the button group
                buttonGroup.addButton(newObj)
                self.gridLayout_2.addWidget(newObj, i+j, 2, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                newObj = CheckableComboBox()
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
            
            elif widgInfo[WIDGET_TYPE] in [FILE, FOLDER]:
                
                # line edit part
                newObj = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setText("")
                self.gridLayout_2.addWidget(newObj, i+j, 1, 1, 2)
                widgInfo[WIDGET1_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)

                # browse button
                newObj = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])
                self.gridLayout_2.addWidget(newObj, i+j, 3, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
                self.hideWidgetIfNeeded(widgInfo, newObj)
                    
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def hideWidgetIfNeeded(self, widgInfo, newObj):

        # Hide the widget if necessary
        if widgInfo[HIDE_SETTING] == HIDE_FROM_USER:

            newObj.hide()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FLExTrans Settings"))

        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]

            # Skip the widget if we are hiding it from the user
            if widgInfo[HIDE_SETTING] == HIDE_FROM_USER:
                continue

            widgInfo[LABEL_OBJ].setText(_translate("MainWindow", widgInfo[LABEL_TEXT]))

            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:
                continue

            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].setText(_translate("MainWindow", "Browse file..."))
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                
            if widgInfo[WIDGET_TYPE] == FOLDER:
                
                widgInfo[WIDGET2_OBJ].setText(_translate("MainWindow", "Browse folder..."))
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].setItemText(0, _translate("MainWindow", "..."))
                widgInfo[WIDGET2_OBJ].setItemText(0, _translate("MainWindow", "..."))
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                widgInfo[WIDGET1_OBJ].setText(_translate("MainWindow", "Yes"))
                widgInfo[WIDGET2_OBJ].setText(_translate("MainWindow", "No"))
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

            else:
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

        self.apply_button.setText(_translate("MainWindow", "Apply"))
        self.applyClose_button.setText(_translate("MainWindow", "Apply and Close"))
        self.Close_button.setText(_translate("MainWindow", "Close"))

class Main(QMainWindow):

    def __init__(self, configMap, targetDB, DB):
        QMainWindow.__init__(self)

        self.configMap = configMap
        self.targetDB = targetDB
        self.DB = DB
        self.giveConfirmation = True
        self.changedSettingsSet = set()
        self.nameToWidgetMap = {}
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Loop through all settings 
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            # Populate a map from config name string to widget info.
            self.nameToWidgetMap[widgInfo[CONFIG_NAME]] = widgInfo
            
        # Load the widgets with data        
        self.initLoad()

        self.modified = False
        
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), ReadConfig.CONFIG_FILE)
        
        self.config = myPath
        
        # Get the project folder which is the parent of the config path
        myPath = os.path.dirname(os.path.dirname(FTPaths.CONFIG_PATH))
        
        self.projFolder = myPath
        
        # If there's an invalid target DB, the member will be None, in this case disable certain target widgets.
        if self.targetDB == None:
            
            self.disableTargetWidgets()
            
        # Loop through all settings and connect widgets to functions
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            # Connect browse buttons to functions
            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].clicked.connect(makeOpenFile(self, widgInfo))
                widgInfo[WIDGET1_OBJ].textChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))

            elif widgInfo[WIDGET_TYPE] == FOLDER:
                
                widgInfo[WIDGET2_OBJ].clicked.connect(makeOpenFolder(self, widgInfo))
                widgInfo[WIDGET1_OBJ].textChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))

            # Connect all widgets to a function the sets the modified flag
            # This is so that any clicking on objects will prompt the user to save on exit
            elif widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                if widgInfo[WIDGET1_OBJ_NAME] == 'choose_target_project':

                    widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(reportChangeAndDisable(self, self.changedSettingsSet, widgInfo))
                    
                else:
                    widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))

                                    
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                # TODO: this doesn't do anything. Need to figure out what signal we can connect to to see if this widget has changed data
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                widgInfo[WIDGET2_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                widgInfo[WIDGET1_OBJ].textChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                widgInfo[WIDGET1_OBJ].toggled.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
        self.clearCheckComboBoxModifiedFlags()
        
        # Apply button
        self.ui.apply_button.clicked.connect(self.save)
        self.ui.applyClose_button.clicked.connect(self.saveAndClose)
        self.ui.Close_button.clicked.connect(self.closeMyWindow)

    def disableTargetWidgets(self):
        
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET1_OBJ_NAME] in ["choose_target_morpheme_types", "choose_inflection_first_element", "choose_inflection_second_element", "limit_pos"]:
                
                widgInfo[WIDGET1_OBJ].setEnabled(False)
                
    def setModifiedFlag(self):
        
        self.modified = True
        
    def read(self, key):
        
        widgeInfo = self.nameToWidgetMap[key]
        
        return ReadConfig.getConfigVal(self.configMap, key, report=None, giveError=widgeInfo[GIVE_ERROR_IF_NOT_PRESENT])

    def initLoad(self):
        
        # Clear combo boxes
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] in [COMBO_BOX, CHECK_COMBO_BOX]:
                
                widgInfo[WIDGET1_OBJ].clear()
            
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].clear()
                widgInfo[WIDGET2_OBJ].clear()

                widgInfo[WIDGET1_OBJ].addItem("...")
                widgInfo[WIDGET2_OBJ].addItem("...")
            
        # load all the widgets, calling the applicable load function defined widgetList
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:
                continue

            if widgInfo[WIDGET_TYPE] in [SIDE_BY_SIDE_COMBO_BOX, YES_NO]:
                
                # pass two widgets
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], widgInfo[WIDGET2_OBJ], self, widgInfo[CONFIG_NAME])

            else:
                
                # Call the load function for this widget, pass in the widget object and this window object
                # Also pass the config file setting name
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], self, widgInfo[CONFIG_NAME])

    def closeEvent(self, event):
        
        self.closeMyWindow()
        
    def closeMyWindow(self):
        
        if self.giveConfirmation:
            
            self.checkIfCheckComboChanged()
            
        self.close()
        
    def clearCheckComboBoxModifiedFlags(self):
        
        # If a check combo box was modified, set the modified flag for this main class so 
        # we can prompt the user to save
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].modified = False
        
    def checkIfCheckComboChanged(self):
        
        # If a check combo box was modified, set the modified flag for this main class so 
        # we can prompt the user to save
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                if widgInfo[WIDGET1_OBJ].modified:
                    
                    self.changedSettingsSet.add(widgInfo[LABEL_TEXT])
                    self.modified = True
                    
                    # Reset them all back to False
                    widgInfo[WIDGET1_OBJ].modified = False
        
    def saveAndClose(self):
        
        self.giveConfirmation = False
        self.save()
        self.close()
        
    def reportChangedSettings(self):
        
        refreshStatusbar()

        if len(self.changedSettingsSet) > 0:
        
            msgList = [myStr +' setting changed.' for myStr in list(self.changedSettingsSet)]
            msgStr = '\n'.join(msgList)    
            QMessageBox.information(self, 'FLExTrans Settings', msgStr)
        
    def save(self):

        f = open(self.config, "w", encoding='utf-8')
        
        # Write out the config file according to each type
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]

            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:
                continue
            
            if widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].currentText()
                
                if widgInfo[CONFIG_NAME] == ReadConfig.SOURCE_TEXT_NAME:
                    
                    # Set the global variable
                    FTPaths.CURRENT_SRC_TEXT = widgInfo[WIDGET1_OBJ].currentText()
 
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+self.addCommas(widgInfo[WIDGET1_OBJ].currentData())
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                valStr = widgInfo[WIDGET1_OBJ].currentText()+','+widgInfo[WIDGET2_OBJ].currentText()
                
                # If the user selected ..., set the value to blank
                if '...' in valStr:
                    
                    valStr = ''
                    
                outStr = widgInfo[CONFIG_NAME]+'='+valStr
                
            elif widgInfo[WIDGET_TYPE] in [FILE, FOLDER, TEXT_BOX]:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].text().strip()
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                if widgInfo[WIDGET1_OBJ].isChecked():
                    
                    selected='y'
                else:
                    selected='n'
            
                outStr = widgInfo[CONFIG_NAME]+'='+selected
                
            f.write(outStr+'\n')
            
        f.close()
        
        self.checkIfCheckComboChanged()
        
        self.reportChangedSettings()

        self.modified = False
        self.changedSettingsSet.clear()
        
        # Mark the combo boxes as not having changed
        self.clearCheckComboBoxModifiedFlags()
        
        if self.giveConfirmation:
            
            pass
            #QMessageBox.information(self, 'Save Settings', 'Changes saved.')

    def addCommas(self, array):
        retStr = ''
        if array:
            for text in array:
                retStr += text + ","
        return retStr

def MainFunction(DB, report, modify=True): 
    
    # DB and report will be None

    # Read the configuration file
    configMap = ReadConfig.readConfig(report=None)
    if not configMap:
        MessageBox.Show("Error reading configuration file.", "FLExTrans", MessageBoxButtons.OK)
        return

    # Open the source database
    sourceDB = FLExProject()

    try:
        sourceDB.OpenProject(FTConfig.currentProject, False)
    except:
        MessageBox.Show("Failed to open the source database.", "FLExTrans", MessageBoxButtons.OK)
        sourceDB = None
        return

    # Open the source database
    TargetDB = FLExProject()

    try:
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report=None)
        
        if not targetProj:
            
            TargetDB = None
        else:
            TargetDB.OpenProject(targetProj, False)
    except:
        MessageBox.Show("Failed to open the target database.", "FLExTrans", MessageBoxButtons.OK)
        TargetDB = None
    
    # Show the window
    app = QApplication(sys.argv)

    window = Main(configMap, TargetDB, sourceDB)

    window.show()

    app.exec_()
    
    # Prompt the user to save changes, if needed
    if window.modified == True:
        
        if QMessageBox.question(window, 'Save Changes', "Do you want to save your changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:

            window.giveConfirmation = False
            window.save()
            #window.reportChangedSettings()
    
    if TargetDB:
        
        TargetDB.CloseProject()
        
    sourceDB.CloseProject()


# ----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs=docs)

#### Instructions for adding a new setting ####
#
# Copy and paste an existing line that has the same type as the new setting you want.
# Give new names for the various text strings.
# If necessary write a new load function at the top of this file.
# Set the config key name to a value from the ReadConfig.py file.
# If a new type of widget is needed, more work is needed to add to each part of the code where the widgetList is iterated

widgetList = [

   ["Project Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   # label text          obj1 name       obj2 name  type     label   obj1    obj2    load function       config key name            
   ["Source Text Name", "choose_source_text", "", COMBO_BOX, object, object, object, loadSourceTextListForSettings, ReadConfig.SOURCE_TEXT_NAME,\
    # tooltip text                                                                                               Give an error if missing
    "The name of the text (in the first analysis writing system)\nin the source FLEx project to be translated.", GIVE_ERROR, DONT_HIDE],\
   
   ["Target Project", "choose_target_project", "", COMBO_BOX, object, object, object, loadTargetProjects, ReadConfig.TARGET_PROJECT,\
    "The name of the target FLEx project.", GIVE_ERROR, DONT_HIDE],\

   ["Source Custom Field for Entry Link", "choose_entry_link", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY,\
    "The name of the sense-level custom field in the source FLEx project that\nholds the link information to entries in the target FLEx project.", GIVE_ERROR, DONT_HIDE],\
   
#    ["Source Custom Field for Sense Number", "chose_sense_number", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM,\
#     "The name of the sense-level custom field in the source FLEx project\nthat holds the sense number of the target entry.", GIVE_ERROR, DONT_HIDE],\

   ["Category that Represents Proper Noun", "choose_proper_noun", "", COMBO_BOX, object, object, object, loadSourceCategoriesNormalListBox, ReadConfig.PROPER_NOUN_CATEGORY,\
    "The name of the category that you use for proper nouns in your source FLEx project.", DONT_GIVE_ERROR, DONT_HIDE],\
   
   ["Cache data for faster processing?", "cache_yes", "cache_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CACHE_DATA, \
    "Indicates if the system should avoid regenerating data that hasn't changed.\nUse the CleanFiles module to force the regeneration of data.", GIVE_ERROR, DONT_HIDE],\

   ["Use composed characters in editing?", "composed_yes", "composed_no", YES_NO, object, object, object, loadYesNo, ReadConfig.COMPOSED_CHARACTERS, \
    "When editing the transfer rules file or the testbed, if Yes, characters with \ndiacritics will be composed (NFC) to single characters (where possible). If No, characters will be decomposed (NFD).", GIVE_ERROR, DONT_HIDE],\

   ["Sentence Punctuation", "punctuation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SENTENCE_PUNCTUATION, \
    "A list of punctuation that ends a sentence.\nIn transfer rules you can check for the end of a sentence.", GIVE_ERROR, DONT_HIDE],\

   ["Source Morpheme Types Counted As Roots", "choose_source_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceMorphemeTypes, ReadConfig.SOURCE_MORPHNAMES,\
    "Morpheme types in the source FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics.", GIVE_ERROR, DONT_HIDE],\

   ["Target Morpheme Types Counted As Roots", "choose_target_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadTargetMorphemeTypes, ReadConfig.TARGET_MORPHNAMES,\
    "Morpheme types in the target FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics.", GIVE_ERROR, DONT_HIDE],\



   ["Complex Forms", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   ["Source Complex Form Types", "choose_source_compex_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_COMPLEX_TYPES,\
    "One or more complex types from the source FLEx project.\nThese types will be treated as a lexical unit in FLExTrans and whenever\nthe components that make up this type of complex form are found sequentially\nin the source text, they will be converted to one lexical unit.", GIVE_ERROR, DONT_HIDE],\

   ["Source Discontiguous Complex Form Types", "choose_source_discontiguous_compex", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_DISCONTIG_TYPES,\
    "One or more complex types from the source FLEx project.\nThese types will allow one intervening word between the first\nand second words of the complex type, yet will still be treated\nas a lexical unit.", GIVE_ERROR, DONT_HIDE],\

   ["Source Skipped Word Grammatical\nCategories for Discontiguous Complex Forms", "choose_skipped_source_words", "", CHECK_COMBO_BOX, object, object, object, loadSourceCategories, ReadConfig.SOURCE_DISCONTIG_SKIPPED,\
    "One or more grammatical categories that can intervene in the above complex types.", GIVE_ERROR, DONT_HIDE],\

   ["Target Complex Form Types\nwith inflection on 1st Element", "choose_inflection_first_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_1ST,\
    "One or more complex types from the target FLEx project.\nThese types, when occurring in the text file to be synthesized,\nwill be broken down into their constituent entries. Use this property\nfor the types that have inflection on the first element of the complex form.", GIVE_ERROR, DONT_HIDE],\

   ["Target Complex Form Types\nwith inflection on 2nd Element", "choose_inflection_second_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_2ND,\
    "Same as above. Use this property for the types that have inflection\non the second element of the complex form.", GIVE_ERROR, DONT_HIDE],\



   ["Transfer Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   ["Default to rebuilding the bilingual\nlexicon after linking senses?", "rebuild_bl_yes", "rebuild_bl_no", YES_NO, object, object, object, loadYesNo, ReadConfig.REBUILD_BILING_LEX_BY_DEFAULT, \
    "In the Sense Linker tool by default check the checkbox for rebuilding the bilingual lexicon.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Transfer Rules File", "transfer_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE, \
    "The path and name of the file containing the transfer rules.", GIVE_ERROR, DONT_HIDE],\

   ["Transfer Rules File 2 (Advanced Transfer)", "transfer_rules_filename2", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE2, \
    "The path and name of the file containing the 2nd transfer rules for use in advanced transfer.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Transfer Rules File 3 (Advanced Transfer)", "transfer_rules_filename3", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE3, \
    "The path and name of the file containing the 3rd transfer rules for use in advanced transfer.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Category Abbreviation Pairs", "category_abbreviation_one", "category_abbreviation_two", SIDE_BY_SIDE_COMBO_BOX, object, object, object, loadCategorySubLists, ReadConfig.CATEGORY_ABBREV_SUB_LIST,\
    "One or more pairs of grammatical categories where the first category\nis the “from” category in the source FLEx project and the second category\nis the “to” category in the target FLEx project. Use the abbreviations of\nthe FLEx categories. The substitution happens in the bilingual lexicon.", GIVE_ERROR, DONT_HIDE],\
   
   ["Analyzed Text Output File", "output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TEXT_FILE,\
    "The path and name of the file which holds\nthe extracted source text.", GIVE_ERROR, DONT_HIDE],\

   ["Bilingual Dictionary Output File", "bilingual_dictionary_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICTIONARY_FILE,\
    "The path and name of the file which holds the bilingual lexicon.", GIVE_ERROR, DONT_HIDE],\

   ["Bilingual Dictionary Replacement File", "bilingual_dictionary_replace_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, \
    "The path and name of the file which holds replacement\nentry pairs for the bilingual lexicon.", GIVE_ERROR, DONT_HIDE],\

   ["Target Transfer Results File", "transfer_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RESULTS_FILE, \
    "The path and name of the file which holds the text contents\nafter going through the transfer process.", GIVE_ERROR, DONT_HIDE],\



   ["Synthesis Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   ["Use HermitCrab synthesis?", "hc_synthesis_yes", "hc_synthesis_no", YES_NO, object, object, object, loadYesNo, ReadConfig.HERMIT_CRAB_SYNTHESIS, \
    "Use the HermitCrab phonological synthesizer. This applies if you have\nHermitCrab parsing set up for your target project. You also need to have the\nSynthesize Text with HermitCrab module in your AllSteps collection.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Clean Up Unknown Target Words?", "cleanup_yes", "cleanup_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CLEANUP_UNKNOWN_WORDS, \
    "Indicates if the system should remove preceding @ signs\nand numbers in the form N.N following words in the target text.", GIVE_ERROR, DONT_HIDE],\

   ["Target Lexicon Files Folder", "lexicon_files_folder", "", FOLDER, object, object, object, loadFile, ReadConfig.TARGET_LEXICON_FILES_FOLDER, \
    "The path where lexicon files and other STAMP files are created", GIVE_ERROR, DONT_HIDE],\

   ["Target Output ANA File", "output_ANA_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_ANA_FILE,\
    "The path and name of the file holding\nthe intermediary text in STAMP format.", GIVE_ERROR, DONT_HIDE],\

   ["Hermit Crab Master File", "hermit_crab_master_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_MASTER_FILE,\
    "The path and name of the HermitCrab master file. \nThis is only needed if you are using HermitCrab Synthesis.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Target Output Synthesis File", "output_syn_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_SYNTHESIS_FILE,\
    "The path and name of the file holding\nthe intermediary synthesized file.", GIVE_ERROR, DONT_HIDE],\

   ["Target Affix Gloss List File", "taget_affix_gloss_list_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_AFFIX_GLOSS_FILE, \
    "The ancillary file that hold a list of affix\nglosses from the target FLEx project.", GIVE_ERROR, DONT_HIDE],\



   ["Synthesis Test Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\
    
   ["Limit to specific POS values", "limit_pos", "", CHECK_COMBO_BOX, object, object, object, loadTargetCategories, ReadConfig.SYNTHESIS_TEST_LIMIT_POS,\
    "One or more grammatical categories. The synthesis test will be limited to using only these categories.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Limit number of stems", "stem_num", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SYNTHESIS_TEST_LIMIT_STEM_COUNT, \
    "Limit the generation to a specified number of stems.\nStems chosen may seem random.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Limit to specific Citation Form", "limit_citation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SYNTHESIS_TEST_LIMIT_LEXEME, \
    "Limit the generation to one or more specified Citation Form(s).", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Parses Output File", "output_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE,\
    "The path and name of the file for the generated parse forms in human readable\nform, with glosses of roots and affixes.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["SIGMORPHON Output File", "sigmorphon_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE,\
    "The path and name of the file for the generated parse forms in SIGMORPHON\nformat, with no roots, and affixes separated by semicolons.", DONT_GIVE_ERROR, HIDE_FROM_USER],\

   ["Synthesis test log file", "log_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_LOG_FILE,\
    "The path and name of the file for the log output\nof the synthesis test.", DONT_GIVE_ERROR, DONT_HIDE],\



   ["Testbed Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   ["Testbed File", "testbed_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_FILE, \
    "The path and name of the testbed file.", GIVE_ERROR, DONT_HIDE],\

   ["Testbed Results Log File", "testbed_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_RESULTS_FILE, \
    "The path and name of the testbed results log file", GIVE_ERROR, DONT_HIDE],\



   ["TreeTran Settings", "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, DONT_HIDE],\

   ["TreeTran Insert Words File", "treetran_insert_words_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_INSERT_WORDS_FILE, \
    "The path and name of the file that has a list of\nwords that can be inserted with a TreeTran rule.", DONT_GIVE_ERROR, DONT_HIDE],\

   ["TreeTran Rules File", "treetran_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_RULES_FILE, \
    "The path and name of the TreeTran rules file", DONT_GIVE_ERROR, DONT_HIDE],\

   ["Analyzed Text TreeTran Output File", "treetran_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, \
    "The path and name of the file that holds the output from TreeTran.", DONT_GIVE_ERROR, DONT_HIDE],\


# Hidden settings
   ["Hermit Crab Configuration File", "hermit_crab_config_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_CONFIG_FILE,\
    "The path and name of the HermitCrab configuration file. \nThis is only needed if you are using HermitCrab Synthesis.", DONT_GIVE_ERROR, HIDE_FROM_USER],\

   ["Hermit Crab Parses File", "hermit_crab_parses_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_PARSES_FILE,\
    "The path and name of the HermitCrab parses file. \nThis is only needed if you are using HermitCrab Synthesis.", DONT_GIVE_ERROR, HIDE_FROM_USER],\

   ["Hermit Crab Surface Forms File", "hermit_crab_surface_forms_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE,\
    "The path and name of the HermitCrab surface forms file. \nThis is only needed if you are using HermitCrab Synthesis.", DONT_GIVE_ERROR, HIDE_FROM_USER]

              ]

# ----------------------------------------------------------------
# The main processing function
if __name__ == '__main__':
    FlexToolsModule.Help()
