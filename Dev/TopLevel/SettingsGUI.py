#
#   Settings GUI
#   Lærke Roager Christensen 
#   3/28/22
#
#   Version 3.13.5 - 5/17/25 - Sara Mason
#   Fixes #981. Removes the ding sound when the Settings dialog is closed.
#
#   Version 3.13.4 - 4/9/25 - Sara Mason
#   Fixes #953. Sort proper nouns, changed proper nouns tooltip
#
#   Version 3.13.3 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13.2 - 3/18/25 - Ron Lockwood
#    Fixes #676. Let user know of implicit settings changes.
#
#   Version 3.13.1 - 3/11/25 - Ron Lockwood
#    Fixes #869. Better error on failure to open DB.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.6 - 3/2/25 - Ron Lockwood
#    Use a default list of morphnames also if there is no existing morphnames found in the list.
#    Also, use the default list for source morphnames.
#
#   Version 3.12.5 - 1/31/25 - Ron Lockwood
#    Fixes #868. Give different view modes so the user doesn't have to see all settings.
#
#   Version 3.12.4 - 1/6/25 - Ron Lockwood
#    Improved detection if a checked combo box changed. Before we were marking the settings as changed
#    just if the combo box was clicked. Now we only mark the setting as changed if an item gets checked or unchecked.
#
#   Version 3.12.3 - 1/6/25 - Ron Lockwood
#    Fixes #836. Crash when the target project doesn't exist. When fixing #819 below,
#    I didn't account for the case where the target project doesn't exist. This fixes that.
#
#   Version 3.12.2 - 12/13/24 - Ron Lockwood
#    Added projects to treat in a cluster.
#
#   Version 3.12.1 - 11/28/24 - Ron Lockwood
#    Fixes #819. Allow morphnames and gram. categories in other Analysis WSs.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.2 - 10/22/24 - Ron Lockwood
#    Fixes #730. Always default to a list of target morphtypes when they
#    are unavailable.
#
#   Version 3.11.1 - 9/6/24 - Ron Lockwood
#    Support mixpanel usage statistics.
#
#   Version 3.11 - 6/21/24 - Ron Lockwood
#    Use Setting for location and name of the Rule Assistant rules file.
#
#   Version 3.10.1 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10 - 2/29/24 - Ron Lockwood
#    Fixes #571. Setting to determine if filter by all fields is checked.
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
#   earlier version history removed on 1/31/25
#
#   To make it easier to change the configfile
#

import os
import sys
import json

from System import Guid # type: ignore
from System import String # type: ignore

from System.Windows.Forms import (MessageBox, MessageBoxButtons) # type: ignore

from flextoolslib import FlexToolsModuleClass
from flextoolslib import *

from SIL.LCModel import IMoMorphType, ICmObjectRepository, ICmPossibility # type: ignore

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QIcon

from ComboBox import CheckableComboBox
from flexlibs import FLExProject, AllProjectNames

import Utils
import ReadConfig
import FTPaths

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils'] 

tr = QtCore.QCoreApplication.translate

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
MINI_VIEW = 15
BASIC_VIEW = 10
FULL_VIEW = 5
HIDE_FROM_USER = 0

targetComplexTypes = []
sourceComplexTypes = []
categoryList = []
tgtCategoryList = []

defaultMorphNames = [
("d7f713e4-e8cf-11d3-9764-00c04f186933", "bound root"),
("d7f713e7-e8cf-11d3-9764-00c04f186933", "bound stem"),
("0cc8c35a-cee9-434d-be58-5d29130fba5b", "discontiguous phrase"),
("56db04bf-3d58-44cc-b292-4c8aa68538f4", "particle"),
("a23b6faa-1052-4f4d-984b-4b338bdaf95f", "phrase"),
("d7f713e5-e8cf-11d3-9764-00c04f186933", "root"),
("d7f713e8-e8cf-11d3-9764-00c04f186933", "stem")
]

def getSourceCategoryList(wind):
    
    if len(categoryList) == 0:
        
        for pos in wind.DB.lp.AllPartsOfSpeech:
            
            catStr = Utils.as_string(pos.Abbreviation)
            categoryList.append(catStr)
            
    return categoryList
            
def getTargetCategoryList(wind):
    
    if wind.targetDB and len(tgtCategoryList) == 0:
        
        for pos in wind.targetDB.lp.AllPartsOfSpeech:
            
            catStr = Utils.as_string(pos.Abbreviation)
            tgtCategoryList.append(catStr)
            
    return tgtCategoryList
            
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

def loadAllProjects(widget, wind, settingName):

    widget.addItems(AllProjectNames())

    projNames = wind.read(settingName)
    
    if projNames:

        for proj in projNames:

            widget.check(proj)

def loadTargetProjects(widget, wind, settingName):

    targetProject = wind.read(settingName)
    
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
    repo = wind.DB.project.ServiceLocator.GetService(ICmObjectRepository)
    
    for item in wind.DB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
        
        item = IMoMorphType(item)
        
        # Only load things that can be stems
        if item.IsStemType == True:
            
            # convert this item's id to a string
            morphType = repo.GetObject(item.Guid)
            morphType = ICmPossibility(morphType)
            morphTypeStr = Utils.as_string(morphType.Name)
            
            typesList.append(morphTypeStr)
    
    widget.addItems(typesList)
    
    morphNames = wind.read(settingName)
    
    # Use a default list if we have nothing set or no morphNames found in the typesList
    if not morphNames or set(morphNames).isdisjoint(set(typesList)):

        for guidStr in defaultMorphNames:

            # Go from guid to to morphname string in the analysis lang.
            morphType = repo.GetObject(Guid(String(guidStr[0])))
            morphType = ICmPossibility(morphType)
            morphTypeStr = Utils.as_string(morphType.Name)

            if morphTypeStr in typesList:
                
                widget.check(morphTypeStr)
    else:
        if morphNames:

            for morphName in morphNames:

                if morphName in typesList:
                    
                    widget.check(morphName)

def loadTargetMorphemeTypes(widget, wind, settingName):

    typesList = []

    if wind.targetDB:
        
        repo = wind.targetDB.project.ServiceLocator.GetService(ICmObjectRepository)
        
        for item in wind.targetDB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:

            item = IMoMorphType(item)

            # Only load things that can be stems
            if item.IsStemType == True:
                
                # convert this item's id to a string
                morphType = repo.GetObject(item.Guid)
                morphType = ICmPossibility(morphType)
                morphTypeStr = Utils.as_string(morphType.Name)
                
                typesList.append(morphTypeStr)
        
        widget.addItems(typesList)
        
        morphNames = wind.read(settingName)
        
        # Use a default list if we have nothing set or no morphNames found in the typesList
        if not morphNames or set(morphNames).isdisjoint(set(typesList)):

            for guidStr in defaultMorphNames:

                # Go from guid to to morphname string in the analysis lang.
                morphType = repo.GetObject(Guid(String(guidStr[0])))
                morphType = ICmPossibility(morphType)
                morphTypeStr = Utils.as_string(morphType.Name)

                if morphTypeStr in typesList:
                    
                    widget.check(morphTypeStr)
        else:
    
            for morphName in morphNames:

                if morphName in typesList:
                    
                    widget.check(morphName)
    else:
        # Use a default list if the targetDB doesn't exist
        widget.addItems(engList := [eng[1] for eng in defaultMorphNames])

        for morphName in engList:

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
    
    # Sort the category list
    catList.sort()
    
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
    
    # create a new function that will call doReport with the given parameters
    def report_it():
        
        doReport(mySet, myWidgInfo)
        wind.setModifiedFlag()
        
    return report_it

def reportChangeAndDisable(wind, mySet, myWidgInfo):
    
    # create a new function that will call doReport with the given parameters
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
    
def makeOpenFolder(wind, myWidgInfo):
    
    # create a new function that will call doFolderBrowse with the given parameters
    def open_folder():
        
        doFolderBrowse(wind, myWidgInfo)
        wind.setModifiedFlag()
        
    return open_folder
    
def doBrowse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = os.path.dirname(wind.read(myWidgInfo[CONFIG_NAME]))
    
    if not os.path.isdir(startDir):
        
        startDir = ""

    # TODO: bring up language specific file dialog               
    filename, _ = QFileDialog.getOpenFileName(wind, "Select file", startDir, "(*.*)")
    
    if filename:
        
        setPaths(myWidgInfo[WIDGET1_OBJ], filename)

def doFolderBrowse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = wind.read(myWidgInfo[CONFIG_NAME])
    
    if not os.path.isdir(startDir):
        
        startDir = ""
                   
    # TODO: bring up language specific file dialog               
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
        
        self.MW = MainWindow

        MainWindow.setObjectName("SettingsWindow")
        MainWindow.resize(800, 630)
        MainWindow.setMaximumSize(QtCore.QSize(910, 1000))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Create a group box for the radio buttons
        self.radioGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.radioGroupBox.setObjectName("radioGroupBox")
        self.radioGroupBox.setTitle(tr("SettingsWindow", "View Mode"))
        self.radioGroupBox.setFixedHeight(47)  # Set a fixed height for the group box

        # Create a horizontal layout for the radio buttons
        self.radioLayout = QtWidgets.QHBoxLayout(self.radioGroupBox)
        self.radioLayout.setObjectName("radioLayout")

        # Create the radio buttons
        self.miniRadioButton = QtWidgets.QRadioButton(self.radioGroupBox)
        self.miniRadioButton.setObjectName("miniRadioButton")
        self.miniRadioButton.setText(tr("SettingsWindow", "Mini"))
        self.miniRadioButton.setChecked(True)  # Set the default mode to Mini
        self.radioLayout.addWidget(self.miniRadioButton)

        self.basicRadioButton = QtWidgets.QRadioButton(self.radioGroupBox)
        self.basicRadioButton.setObjectName("basicRadioButton")
        self.basicRadioButton.setText(tr("SettingsWindow", "Basic"))
        self.radioLayout.addWidget(self.basicRadioButton)

        self.fullRadioButton = QtWidgets.QRadioButton(self.radioGroupBox)
        self.fullRadioButton.setObjectName("fullRadioButton")
        self.fullRadioButton.setText(tr("SettingsWindow", "Full"))
        self.radioLayout.addWidget(self.fullRadioButton)

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())

        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(750, 200))
        self.scrollArea.setMaximumSize(QtCore.QSize(900, 1000))

        font = QtGui.QFont()
        font.setPointSize(9)

        self.scrollArea.setFont(font)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # Add the group box to the main layout above the scroll area
        self.gridLayout.addWidget(self.radioGroupBox, 2, 0, 1, 3)  # span 6 columns

        # Set up scroll area
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 6)  # span 6 columns

        self.apply_button = QtWidgets.QPushButton(self.centralwidget)
        self.apply_button.setObjectName("apply_button")
        self.apply_button.setText(tr("SettingsWindow", "Apply"))
        self.gridLayout.addWidget(self.apply_button, 2, 3, 1, 1)  # put the buttons at columns 3-5 so they are on the right side

        self.applyClose_button = QtWidgets.QPushButton(self.centralwidget)
        self.applyClose_button.setObjectName("applyClose_button")
        self.applyClose_button.setText(tr("SettingsWindow", "Apply and Close"))
        self.gridLayout.addWidget(self.applyClose_button, 2, 4, 1, 1)

        self.Close_button = QtWidgets.QPushButton(self.centralwidget)
        self.Close_button.setObjectName("Close_button")
        self.Close_button.setText(tr("SettingsWindow", "Close"))
        self.gridLayout.addWidget(self.Close_button, 2, 5, 1, 1)
        
        # Set the radio button based on the loaded view setting
        if MainWindow.viewSetting == MINI_VIEW:

            self.miniRadioButton.setChecked(True)

        elif MainWindow.viewSetting == BASIC_VIEW:

            self.basicRadioButton.setChecked(True)
        else:
            self.fullRadioButton.setChecked(True)

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

            # Hide the widget if necessary depending on the view mode value
            if widgInfo[HIDE_SETTING] < MainWindow.viewSetting:

                newObj.hide()

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
                widgInfo[WIDGET1_OBJ] = line
                j += 1
                self.gridLayout_2.addWidget(line, i+j, 0, 1, 4)

                if widgInfo[HIDE_SETTING] < MainWindow.viewSetting:

                    line.hide()

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

        # Add a link widget at the bottom
        newObj = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        newObj.setText('<html><head/><body><p><a href="https://software.sil.org/language-software-privacy-policy"><span style=" text-decoration: underline; color:#0000ff;">software.sil.org/language-software-privacy-policy</span></a></p></body></html>')
        newObj.setOpenExternalLinks(True)
        self.gridLayout_2.addWidget(newObj, i+j+1, 0, 1, 1)
                    
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def hideWidgetIfNeeded(self, widgInfo, newObj):

        # Hide the widget if necessary
        if widgInfo[HIDE_SETTING] < self.MW.viewSetting:

            newObj.hide()

    def retranslateUi(self, MainWindow):

        MainWindow.setWindowTitle("FLExTrans Settings")

        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]

            # Skip the widget if we are hiding it from the user
            if widgInfo[HIDE_SETTING] == HIDE_FROM_USER:
                continue

            widgInfo[LABEL_OBJ].setText(widgInfo[LABEL_TEXT])
            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:
                continue

            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].setText(tr("SettingsWindow", "Browse file..."))
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                
            if widgInfo[WIDGET_TYPE] == FOLDER:
                
                widgInfo[WIDGET2_OBJ].setText(tr("SettingsWindow", "Browse folder..."))
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].setItemText(0, "...")
                widgInfo[WIDGET2_OBJ].setItemText(0, "...")
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                widgInfo[WIDGET1_OBJ].setText(tr("SettingsWindow", "Yes"))
                widgInfo[WIDGET2_OBJ].setText(tr("SettingsWindow", "No"))
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])
                widgInfo[WIDGET2_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

            else:
                widgInfo[WIDGET1_OBJ].setToolTip(widgInfo[WIDGET_TOOLTIP])

class Main(QMainWindow):

    def __init__(self, configMap, targetDB, DB):
        QMainWindow.__init__(self)

        self.configMap = configMap
        self.targetDB = targetDB
        self.DB = DB
        self.changedSettingsSet = set()
        self.nameToWidgetMap = {}
        self.nameToLabelMap = {}
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        # Load the view setting from the JSON file
        self.loadViewSetting()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect the toggled signal to the slot method
        self.ui.miniRadioButton.toggled.connect(self.hideUnhide)
        self.ui.basicRadioButton.toggled.connect(self.hideUnhide)
        self.ui.fullRadioButton.toggled.connect(self.hideUnhide)

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
                widgInfo[WIDGET1_OBJ].itemCheckedStateChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                widgInfo[WIDGET2_OBJ].currentIndexChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                widgInfo[WIDGET1_OBJ].textChanged.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                widgInfo[WIDGET1_OBJ].toggled.connect(reportChange(self, self.changedSettingsSet, widgInfo))
                
        # Apply button
        self.ui.apply_button.clicked.connect(self.save)
        self.ui.applyClose_button.clicked.connect(self.saveAndClose)
        self.ui.Close_button.clicked.connect(self.closeEvent)

        self.hideUnhide()
        
    def calcViewSetting(self):

        if self.ui.miniRadioButton.isChecked():

            self.viewSetting = MINI_VIEW

        elif self.ui.basicRadioButton.isChecked():

            self.viewSetting = BASIC_VIEW
        else:
            self.viewSetting = FULL_VIEW

    def loadViewSetting(self):

        # Determine the path to the JSON file
        jsonPath = os.path.join(os.getcwd(), 'SettingsViewMode.json')

        # Load the view setting from the JSON file
        if os.path.exists(jsonPath):
            
            with open(jsonPath, 'r') as file:

                data = json.load(file)
                self.viewSetting = data.get('viewSetting', MINI_VIEW)
        else:
            self.viewSetting = MINI_VIEW

    def saveViewSetting(self):

        # Determine the path to the JSON file
        jsonPath = os.path.join(os.getcwd(), 'SettingsViewMode.json')

        # Save the view setting to the JSON file
        with open(jsonPath, 'w') as file:

            json.dump({'viewSetting': self.viewSetting}, file)

    def centerWindow(self):

        # Get the screen geometry
        screen = QtWidgets.QDesktopWidget().screenGeometry()

        # Get the window geometry
        size = self.geometry()
        
        # Calculate the center position
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2

        # Check if the window is already centered
        if self.x() != x or self.y() != y:

            # Move the window to the center position
            self.move(x, y)

    def hideUnhide(self):

        self.calcViewSetting()
        
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[HIDE_SETTING] < self.viewSetting:

                widgInfo[LABEL_OBJ].hide()
                widgInfo[WIDGET1_OBJ].hide()

                if type(widgInfo[WIDGET2_OBJ]) != type:

                    widgInfo[WIDGET2_OBJ].hide()
            else:
                widgInfo[LABEL_OBJ].show()
                widgInfo[WIDGET1_OBJ].show()

                if type(widgInfo[WIDGET2_OBJ]) != type:

                    widgInfo[WIDGET2_OBJ].show()
        
        if self.viewSetting == MINI_VIEW:
        
            # Adjust the size of the main window to fit the reduced amount of content
            self.ui.centralwidget.adjustSize()
            self.adjustSize()
        else:
            self.resize(800, 630)

        self.centerWindow()

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
        
        # Save the view setting to the JSON file
        self.saveViewSetting()
        self.close()
        
    def saveAndClose(self):
        
        self.save()
        self.closeEvent(None)
        
    def getLabelForName(self, name):
        
        # See if we filled out the map already once
        if not self.nameToLabelMap:

            for i in range(0, len(widgetList)):
                
                widgInfo = widgetList[i]
                self.nameToLabelMap[widgInfo[CONFIG_NAME]] = widgInfo[LABEL_TEXT]

        return self.nameToLabelMap.get(name, '')
    
    def userChangedThisSetting(self, nameStr):
        
        # If the user changed the setting, the label will be in the set
        return self.getLabelForName(nameStr) in self.changedSettingsSet
    
    def reportChangedSettings(self, updatedConfigMap):

        labelsList = []
        msgStr = ''

        refreshStatusbar()

        if len(self.changedSettingsSet) > 0:

            msgList = [tr("SettingsWindow", "{} setting changed.").format(myStr) for myStr in list(self.changedSettingsSet)]
            msgStr = '\n'.join(msgList)

        # See if we changed anything that wasn't a user change
        for key in updatedConfigMap:

            if key in self.configMap:

                if self.configMap[key] != updatedConfigMap[key] and not self.userChangedThisSetting(key):
                    
                    labelsList.append(self.getLabelForName(key))
            else:
                labelsList.append(self.getLabelForName(key))

        if labelsList:
            flexTransChanges = tr("SettingsWindow", "FLExTrans made these changes for you:\n") + '\n'.join(labelsList)

            if msgStr:
                msgStr += '\n\n'

            msgStr += flexTransChanges

        if msgStr:
            # QMessageBox.information(self, 'FLExTrans Settings', msgStr)
            msg = QMessageBox()
            msg.setWindowTitle("FLExTrans Settings")
            msg.setText(msgStr)
            msg.setIcon(QMessageBox.NoIcon)  # <- Suppresses the sound
            msg.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
            msg.exec_()
        
    def save(self):

        updatedConfigMap = {}

        f = open(self.config, "w", encoding='utf-8')
        
        # Write out the config file according to each type
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]

            if widgInfo[WIDGET_TYPE] == SECTION_TITLE:
                continue
            
            if widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].currentText()
                updatedConfigMap[widgInfo[CONFIG_NAME]] = widgInfo[WIDGET1_OBJ].currentText()
                
                if widgInfo[CONFIG_NAME] == ReadConfig.SOURCE_TEXT_NAME:
                    
                    # Set the global variable
                    FTPaths.CURRENT_SRC_TEXT = widgInfo[WIDGET1_OBJ].currentText()
 
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+self.addCommas(widgInfo[WIDGET1_OBJ].currentData())
                myList = widgInfo[WIDGET1_OBJ].currentData()
                updatedConfigMap[widgInfo[CONFIG_NAME]] =  myList + [''] if myList else '' # just need the list, but always with a blank at the end. For an empty list make it the null string

            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                valStr = widgInfo[WIDGET1_OBJ].currentText()+','+widgInfo[WIDGET2_OBJ].currentText()
                
                # If the user selected ..., set the value to blank
                if '...' in valStr:
                    
                    valStr = ''
                    
                outStr = widgInfo[CONFIG_NAME]+'='+valStr
                updatedConfigMap[widgInfo[CONFIG_NAME]] = valStr
                
            elif widgInfo[WIDGET_TYPE] in [FILE, FOLDER, TEXT_BOX]:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].text().strip()
                updatedConfigMap[widgInfo[CONFIG_NAME]] = widgInfo[WIDGET1_OBJ].text().strip()
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                if widgInfo[WIDGET1_OBJ].isChecked():
                    
                    selected='y'
                else:
                    selected='n'
            
                outStr = widgInfo[CONFIG_NAME]+'='+selected
                updatedConfigMap[widgInfo[CONFIG_NAME]] = selected
                
            f.write(outStr+'\n')
            
        f.close()
        
        self.reportChangedSettings(updatedConfigMap)

        self.modified = False
        self.changedSettingsSet.clear()
        
    def addCommas(self, array):
        retStr = ''
        if array:
            for text in array:
                retStr += text + ","
        return retStr

def giveDBErrorMessageBox(myProj):
    
    errMsg = tr("SettingsWindow",
        "Failed to open the '{projectName}' database. This could be because you have the project open ".format(projectName=myProj)+\
        "and you have not turned on the sharing option in the Sharing tab of the Fieldworks Project Properties dialog. "
        "This is found under File > Project Management > Fieldworks Project Properties on the menu."
    )
    MessageBox.Show(errMsg, "FLExTrans", MessageBoxButtons.OK)

def MainFunction(DB, report, modify=True): 
    
    # DB and report will be None

    # Read the configuration file
    configMap = ReadConfig.readConfig(report=None)
    if not configMap:
        MessageBox.Show(tr("SettingsWindow","Error reading configuration file."), "FLExTrans", MessageBoxButtons.OK)
        return

    # Open the source database
    sourceDB = FLExProject()

    try:
        sourceDB.OpenProject(FTConfig.currentProject, False)
    except:
        giveDBErrorMessageBox(FTConfig.currentProject)
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
        giveDBErrorMessageBox(targetProj)
        TargetDB = None
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + ['SettingsGUI'], 
                           translators, loadBase=True)

    window = Main(configMap, TargetDB, sourceDB)
    window.show()
    app.exec_()
    
    # Prompt the user to save changes, if needed
    if window.modified == True:
        
        if QMessageBox.question(window, tr("SettingsWindow", 'Save Changes'), tr("SettingsWindow", "Do you want to save your changes?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:

            window.save()
    
    if TargetDB:
        
        TargetDB.CloseProject()
        
    sourceDB.CloseProject()


# ----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs=docs)

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['SettingsGUI'], translators)

#### Instructions for adding a new setting ####
#
# Copy and paste an existing line that has the same type as the new setting you want.
# Give new names for the various text strings.
# If necessary write a new load function at the top of this file.
# Set the config key name to a value from the ReadConfig.py file.
# If a new type of widget is needed, more work is needed to add to each part of the code where the widgetList is iterated
widgetList = [

   [tr("SettingsWindow", "Project Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, MINI_VIEW],\

   # label text          obj1 name       obj2 name  type     label   obj1    obj2    load function       config key name            
   [tr("SettingsWindow", "Source Text Name"), "choose_source_text", "", COMBO_BOX, object, object, object, loadSourceTextListForSettings, ReadConfig.SOURCE_TEXT_NAME,\
   # tooltip text 
    tr("SettingsWindow", "The name of the text (in the first analysis writing system)\nin the source FLEx project to be translated."), GIVE_ERROR, MINI_VIEW],\
   
   [tr("SettingsWindow", "Target Project"), "choose_target_project", "", COMBO_BOX, object, object, object, loadTargetProjects, ReadConfig.TARGET_PROJECT,\
    tr("SettingsWindow", "The name of the target FLEx project."), GIVE_ERROR, MINI_VIEW],\

   [tr("SettingsWindow", "Source Custom Field for Entry Link"), "choose_entry_link", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY,\
    tr("SettingsWindow", "The name of the sense-level custom field in the source FLEx project that\nholds the link information to entries in the target FLEx project."), GIVE_ERROR, BASIC_VIEW],\
   
   [tr("SettingsWindow", "Category that Represents Proper Noun"), "choose_proper_noun", "", COMBO_BOX, object, object, object, loadSourceCategoriesNormalListBox, ReadConfig.PROPER_NOUN_CATEGORY,\
    tr("SettingsWindow", "The name of the grammatical category that you use for proper nouns in your\nsource FLEx project. It is possible to choose not to translate proper nouns."), DONT_GIVE_ERROR, BASIC_VIEW],\
   
   [tr("SettingsWindow", "Hide warnings for unanalyzed Proper Nouns"), "unanalyzed_proper_noun_yes", "unanalyzed_proper_noun_no", YES_NO, object, object, object, loadYesNo, ReadConfig.NO_PROPER_NOUN_WARNING,\
    tr("SettingsWindow", "Don't show warnings for capitalized words (Proper Nouns) that are left unanalyzed. Except at the beginning of a sentence."), DONT_GIVE_ERROR, BASIC_VIEW],\
   
   [tr("SettingsWindow", "Cache data for faster processing?"), "cache_yes", "cache_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CACHE_DATA, \
    tr("SettingsWindow", "Indicates if the system should avoid regenerating data that hasn't changed.\nUse the CleanFiles module to force the regeneration of data."), GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Use composed characters in editing?"), "composed_yes", "composed_no", YES_NO, object, object, object, loadYesNo, ReadConfig.COMPOSED_CHARACTERS, \
    tr("SettingsWindow", "When editing the transfer rules file or the testbed, if Yes, characters with \ndiacritics will be composed (NFC) to single characters (where possible). If No, characters will be decomposed (NFD)."),\
          GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Sentence Punctuation"), "punctuation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SENTENCE_PUNCTUATION, \
    tr("SettingsWindow", "A list of punctuation that ends a sentence.\nIn transfer rules you can check for the end of a sentence."), GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Source Morpheme Types Counted As Roots"), "choose_source_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceMorphemeTypes, ReadConfig.SOURCE_MORPHNAMES,\
    tr("SettingsWindow", "Morpheme types in the source FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Morpheme Types Counted As Roots"), "choose_target_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadTargetMorphemeTypes, ReadConfig.TARGET_MORPHNAMES,\
    tr("SettingsWindow", "Morpheme types in the target FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."), GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Complex Forms"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Source Complex Form Types"), "choose_source_compex_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_COMPLEX_TYPES,\
    tr("SettingsWindow", "One or more complex types from the source FLEx project.\nThese types will be treated as a lexical unit in FLExTrans and whenever\nthe components that make up this type of complex form are found sequentially\nin the source text, they will be converted to one lexical unit."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Source Discontiguous Complex Form Types"), "choose_source_discontiguous_compex", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_DISCONTIG_TYPES,\
    tr("SettingsWindow", "One or more complex types from the source FLEx project.\nThese types will allow one intervening word between the first\nand second words of the complex type, yet will still be treated\nas a lexical unit."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Source Skipped Word Grammatical\nCategories for Discontiguous Complex Forms"), "choose_skipped_source_words", "", CHECK_COMBO_BOX, object, object, object, loadSourceCategories, ReadConfig.SOURCE_DISCONTIG_SKIPPED,\
    tr("SettingsWindow", "One or more grammatical categories that can intervene in the above complex types."), GIVE_ERROR, FULL_VIEW],\
    
   [tr("SettingsWindow", "Target Complex Form Types\nwith inflection on 1st Element"), "choose_inflection_first_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_1ST,\
    tr("SettingsWindow", "One or more complex types from the target FLEx project.\nThese types, when occurring in the text file to be synthesized,\nwill be broken down into their constituent entries. Use this property\nfor the types that have inflection on the first element of the complex form."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Complex Form Types\nwith inflection on 2nd Element"), "choose_inflection_second_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_2ND,\
    tr("SettingsWindow", "Same as above. Use this property for the types that have inflection\non the second element of the complex form."), GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Linker Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, BASIC_VIEW],\
    
   [tr("SettingsWindow", "Default to rebuilding the bilingual\nlexicon after linking senses?"), "rebuild_bl_yes", "rebuild_bl_no", YES_NO, object, object, object, loadYesNo, ReadConfig.REBUILD_BILING_LEX_BY_DEFAULT, \
    tr("SettingsWindow", "In the Sense Linker tool by default check the checkbox for rebuilding the bilingual lexicon."), DONT_GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Default to filtering on all fields?"), "filter_all_yes", "filter_all_yno", YES_NO, object, object, object, loadYesNo, ReadConfig.LINKER_SEARCH_ANYTHING_BY_DEFAULT, \
    tr("SettingsWindow", "In the Sense Linker tool by default check the checkbox for filtering on all fields."), DONT_GIVE_ERROR, BASIC_VIEW],\



   [tr("SettingsWindow", "Transfer Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Transfer Rules File"), "transfer_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE, \
    tr("SettingsWindow", "The path and name of the file containing the transfer rules."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Transfer Rules File 2 (Advanced Transfer)"), "transfer_rules_filename2", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE2, \
    tr("SettingsWindow", "The path and name of the file containing the 2nd transfer rules for use in advanced transfer."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Transfer Rules File 3 (Advanced Transfer)"), "transfer_rules_filename3", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE3, \
    tr("SettingsWindow", "The path and name of the file containing the 3rd transfer rules for use in advanced transfer."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Category Abbreviation Pairs"), "category_abbreviation_one", "category_abbreviation_two", SIDE_BY_SIDE_COMBO_BOX, object, object, object, loadCategorySubLists, ReadConfig.CATEGORY_ABBREV_SUB_LIST,\
    tr("SettingsWindow", "One or more pairs of grammatical categories where the first category\nis the “from” category in the source FLEx project and the second category\nis the “to” category in the target FLEx project. Use the abbreviations of\nthe FLEx categories. The substitution happens in the bilingual lexicon."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Analyzed Text Output File"), "output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TEXT_FILE,\
    tr("SettingsWindow", "The path and name of the file which holds\nthe extracted source text."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Bilingual Dictionary Output File"), "bilingual_dictionary_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICTIONARY_FILE,\
    tr("SettingsWindow", "The path and name of the file which holds the bilingual lexicon."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Bilingual Dictionary Replacement File"), "bilingual_dictionary_replace_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, \
    tr("SettingsWindow", "The path and name of the file which holds replacement\nentry pairs for the bilingual lexicon."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Transfer Results File"), "transfer_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RESULTS_FILE, \
    tr("SettingsWindow", "The path and name of the file which holds the text contents\nafter going through the transfer process."), GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Synthesis Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Use HermitCrab synthesis?"), "hc_synthesis_yes", "hc_synthesis_no", YES_NO, object, object, object, loadYesNo, ReadConfig.HERMIT_CRAB_SYNTHESIS, \
    tr("SettingsWindow", "Use the HermitCrab phonological synthesizer. This applies if you have\nHermitCrab parsing set up for your target project. You also need to have the\nSynthesize Text with HermitCrab module in your AllSteps collection."), DONT_GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Clean Up Unknown Target Words?"), "cleanup_yes", "cleanup_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CLEANUP_UNKNOWN_WORDS, \
    tr("SettingsWindow", "Indicates if the system should remove preceding @ signs\nand numbers in the form N.N following words in the target text."), GIVE_ERROR, BASIC_VIEW],\

   [tr("SettingsWindow", "Target Lexicon Files Folder"), "lexicon_files_folder", "", FOLDER, object, object, object, loadFile, ReadConfig.TARGET_LEXICON_FILES_FOLDER, \
    tr("SettingsWindow", "The path where lexicon files and other STAMP files are created"), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Output ANA File"), "output_ANA_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_ANA_FILE,\
    tr("SettingsWindow", "The path and name of the file holding\nthe intermediary text in STAMP format."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Hermit Crab Master File"), "hermit_crab_master_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_MASTER_FILE,\
    tr("SettingsWindow", "The path and name of the HermitCrab master file. \nThis is only needed if you are using HermitCrab Synthesis."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Hermit Crab Configuration File"), "hermit_crab_config_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_CONFIG_FILE,\
    tr("SettingsWindow", "The path and name of the HermitCrab configuration file. \nThis is only needed if you are using HermitCrab Synthesis."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Hermit Crab Parses File"), "hermit_crab_parses_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_PARSES_FILE,\
    tr("SettingsWindow", "The path and name of the HermitCrab parses file. \nThis is only needed if you are using HermitCrab Synthesis."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Hermit Crab Surface Forms File"), "hermit_crab_surface_forms_filename", "", FILE, object, object, object, loadFile, ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE,\
    tr("SettingsWindow", "The path and name of the HermitCrab surface forms file. \nThis is only needed if you are using HermitCrab Synthesis."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Output Synthesis File"), "output_syn_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_SYNTHESIS_FILE,\
    tr("SettingsWindow", "The path and name of the file holding\nthe intermediary synthesized file."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Target Affix Gloss List File"), "target_affix_gloss_list_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_AFFIX_GLOSS_FILE, \
    tr("SettingsWindow", "The ancillary file that hold a list of affix\nglosses from the target FLEx project."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Text Out Rules File"), "fixup_synth_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TEXT_OUT_RULES_FILE, \
    tr("SettingsWindow", "The file that holds the search/replace rules to fix up the synthesis result text."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Text In Rules File"), "fixup_ptx_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TEXT_IN_RULES_FILE, \
    tr("SettingsWindow", "The file that holds the search/replace rules to fix up the Paratext import text."), DONT_GIVE_ERROR, FULL_VIEW],\


   [tr("SettingsWindow", "Synthesis Test Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Limit to specific POS values"), "limit_pos", "", CHECK_COMBO_BOX, object, object, object, loadTargetCategories, ReadConfig.SYNTHESIS_TEST_LIMIT_POS,\
    tr("SettingsWindow", "One or more grammatical categories. The synthesis test will be limited to using only these categories."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Limit number of stems"), "stem_num", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SYNTHESIS_TEST_LIMIT_STEM_COUNT, \
    tr("SettingsWindow", "Limit the generation to a specified number of stems.\nStems chosen may seem random."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Limit to specific Citation Form"), "limit_citation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SYNTHESIS_TEST_LIMIT_LEXEME, \
    tr("SettingsWindow", "Limit the generation to one or more specified Citation Form(s)."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Parses Output File"), "output_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE,\
    tr("SettingsWindow", "The path and name of the file for the generated parse forms in human readable\nform, with glosses of roots and affixes."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "SIGMORPHON Output File"), "sigmorphon_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE,\
    tr("SettingsWindow", "The path and name of the file for the generated parse forms in SIGMORPHON\nformat, with no roots, and affixes separated by semicolons."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Synthesis test log file"), "log_syn_test", "", FILE, object, object, object, loadFile, ReadConfig.SYNTHESIS_TEST_LOG_FILE,\
    tr("SettingsWindow", "The path and name of the file for the log output\nof the synthesis test."), DONT_GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Testbed Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Testbed File"), "testbed_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_FILE, \
    tr("SettingsWindow", "The path and name of the testbed file."), GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Testbed Results Log File"), "testbed_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_RESULTS_FILE, \
    tr("SettingsWindow", "The path and name of the testbed results log file."), GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Rule Assistant"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Rule Assistant Rule File"), "rule_assistant_filename", "", FILE, object, object, object, loadFile, ReadConfig.RULE_ASSISTANT_FILE, \
    tr("SettingsWindow", "The path and name of the rule assistant rule definition file."), DONT_GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "TreeTran Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "TreeTran Insert Words File"), "treetran_insert_words_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_INSERT_WORDS_FILE, \
    tr("SettingsWindow", "The path and name of the file that has a list of\nwords that can be inserted with a TreeTran rule."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "TreeTran Rules File"), "treetran_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_RULES_FILE, \
    tr("SettingsWindow", "The path and name of the TreeTran rules file"), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Analyzed Text TreeTran Output File"), "treetran_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, \
    tr("SettingsWindow", "The path and name of the file that holds the output from TreeTran."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Cluster Settings"), "sec_title", "", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Projects to treat together as a cluster"), "cluster_projects", "", CHECK_COMBO_BOX, object, object, object, loadAllProjects, ReadConfig.CLUSTER_PROJECTS, \
    tr("SettingsWindow", "Indicate the cluster projects you would like to run some modules on together."), DONT_GIVE_ERROR, FULL_VIEW],\



   [tr("SettingsWindow", "Privacy"), "sec_title", "link_str", SECTION_TITLE, object, object, object, None, None,\
    "", GIVE_ERROR, MINI_VIEW],\

   [tr("SettingsWindow", "Send usage statistics to FLExTrans developers"), "log_stats_yes", "log_stats_no", YES_NO, object, object, object, loadYesNo, ReadConfig.LOG_STATISTICS, \
    tr("SettingsWindow", "No personally identifiable information is sent. These anonymous statistics will help with future development."), DONT_GIVE_ERROR, MINI_VIEW],\

   [tr("SettingsWindow", "Mixpanel User ID"), "mixpanel_id", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.LOG_STATISTICS_USER_ID, \
    tr("SettingsWindow", "The (probably) unique ID for this project which gets logged to Mixpanel."), DONT_GIVE_ERROR, FULL_VIEW],\

   [tr("SettingsWindow", "Usage Statistics Opt Out Question Asked"), "opt_out_id_yes", "opt_out_id_no", YES_NO, object, object, object, loadYesNo, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION, \
    tr("SettingsWindow", "Opt out of sending usage statistics."), DONT_GIVE_ERROR, FULL_VIEW],
]

app.quit()
del app

# ----------------------------------------------------------------
# The main processing function
if __name__ == '__main__':
    FlexToolsModule.Help()


