#
#   Settings GUI
#   Lærke Roager Christensen
#   3/28/22
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


from FTModuleClass import FlexToolsModuleClass
from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog

from ComboBox import CheckableComboBox
from flexlibs import FLExProject, AllProjectNames

import Utils
import ReadConfig
from FTPaths import CONFIG_PATH

# ----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name: "Settings Tool",
        FTM_Version: "3.5.3",
        FTM_ModifiesDB: False,
        FTM_Synopsis: "Change FLExTrans settings.",
        FTM_Help: "",
        FTM_Description:
            """
Change FLExTrans settings. If you want to change the filename for one of the settings,
type the new name in the text box.             
            """}

LABEL_OBJ_NAME = 0
LABEL_TEXT = 1
WIDGET1_OBJ_NAME = 2
WIDGET2_OBJ_NAME = 3
WIDGET_TYPE = 4
LABEL_OBJ = 5
WIDGET1_OBJ = 6
WIDGET2_OBJ = 7
LOAD_FUNC = 8
CONFIG_NAME = 9
DEFAULT_VALUE = 10
WIDGET_TOOLTIP = 11

COMBO_BOX = "combobox"
SIDE_BY_SIDE_COMBO_BOX = "side by side"
CHECK_COMBO_BOX = "checkable_combobox"
YES_NO = "yes no"
TEXT_BOX = "textbox"
FILE = "file"

targetComplexTypes = []
sourceComplexTypes = []
categoryList = []

def getCategoryList(wind):
    
    if len(categoryList) == 0:
        
        for pos in wind.DB.lp.AllPartsOfSpeech:
            
            catStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            categoryList.append(catStr)
            
    return categoryList
            
def getTargetComplexTypes(wind):
    
    if len(targetComplexTypes) == 0:
        
        for item in wind.targetDB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            
            targetComplexTypes.append(str(item))
            
    return targetComplexTypes
            
def getSourceComplexTypes(wind):
    
    if len(sourceComplexTypes) == 0:
        
        for item in wind.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
            
            sourceComplexTypes.append(str(item))
            
    return sourceComplexTypes
            
def loadSourceTextList(widget, wind, settingName):
    
    # Source Text name
    sourceList = []
    for item in wind.DB.ObjectsIn(ITextRepository):

        sourceList.append(str(item).strip())

    sortedSourceList = sorted(sourceList, key=str.casefold)
    
    # Get the source name from the config file
    configSource = wind.read(settingName)
    
    if configSource:

        # Add items and when we find the one that matches the config file. Set that one to be displayed.
        for i, itemStr in enumerate(sortedSourceList):
            
            widget.addItem(itemStr)
            
            if itemStr == configSource:
                
                widget.setCurrentIndex(i)

def loadCustomEntry(widget, wind, settingName):
    
    # Get the custom field to link to target entry
    customTarget = wind.read(settingName)
    
    if customTarget:

        # Add items and when we find the one that matches the config file. Set that one to be displayed.
        for i, item in enumerate(wind.DB.LexiconGetSenseCustomFields()):
    
            # item is a tuple, (id, name)
            widget.addItem(str(item[1]))           
    
            if item[1] == customTarget:
                
                widget.setCurrentIndex(i)

def loadTargetProjects(widget, wind, settingName):

    targetProject = wind.read(settingName)
    
    if targetProject:

        # TODO: Make this disable the other stuff that uses target??
        for i, item in enumerate(AllProjectNames()):
            
            widget.addItem(item)
            
            if item == targetProject:
                
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

        # Strip is because morpheme types come with symbols
        typesList.append(str(item).strip("-=~*"))
    
    widget.addItems(typesList)
    
    morphNames = wind.read(settingName)
    
    if morphNames:

        for morphName in morphNames:

            if morphName in typesList:
                
                widget.check(morphName)

def loadTargetMorphemeTypes(widget, wind, settingName):

    typesList = []
    for item in wind.targetDB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:

        # Strip is because morpheme types come with symbols
        typesList.append(str(item).strip("-=~*"))
    
    widget.addItems(typesList)
    
    morphNames = wind.read(settingName)
    
    if morphNames:

        for morphName in morphNames:

            if morphName in typesList:
                
                widget.check(morphName)

def loadSourceCategories(widget, wind, settingName):

    catList = getCategoryList(wind)
    
    widget.addItems(catList)
    
    disComplexTypes = wind.read(settingName)
    
    if disComplexTypes:

        for cat in disComplexTypes:

            if cat in catList:
                
                widget.check(cat)

def loadCategorySubLists(widget1, widget2, wind, settingName):

    catList = getCategoryList(wind)
    
    widget1.addItems(catList)
    widget2.addItems(catList)
    
    catPair = wind.read(settingName)
    
    if catPair:

        for i, cat in enumerate(catList):
            
            if cat == catPair[0]: # The first one in the config file
                
                widget1.setCurrentIndex(i+1) # ... is the first item

            if cat == catPair[1]: # The second one in the config file
                
                widget2.setCurrentIndex(i+1) # ... is the first item

def loadYesNo(widget, wind, settingName):            

    yesNo = wind.read(settingName)
    
    if yesNo == 'y':
        
        widget.setChecked(True)

def loadTextBox(widget, wind, settingName):            

    text = wind.read(settingName)
    
    if text:
        
        widget.setText(text)

def loadFile(widget, wind, settingName):            

    path = wind.read(settingName)
    
    if path:

        widget.setText(os.path.relpath(path).replace(os.sep, '/'))
        widget.setToolTip(os.path.abspath(path).replace(os.sep, '/'))

def make_open_file(wind, myWidgInfo):
    def open_file():
        do_browse(wind, myWidgInfo)
    return open_file
    
    do_browse(wind, myWidgInfo)
    
def do_browse(wind, myWidgInfo):

        filename, _ = QFileDialog.getOpenFileName(wind, "Open file", "", "(*.*)")
        if filename:
            myWidgInfo[WIDGET1_OBJ].setText(os.path.relpath(filename).replace(os.sep, '/'))
            myWidgInfo[WIDGET1_OBJ].setToolTip(os.path.abspath(filename).replace(os.sep, '/'))
    
class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(899, 756)

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
        self.scrollArea.setMinimumSize(QtCore.QSize(900, 650))
        self.scrollArea.setMaximumSize(QtCore.QSize(900, 650))

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)

        self.scrollArea.setFont(font)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 847, 1046))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # Reset button, apply button and scroll area
        self.reset_button = QtWidgets.QPushButton(self.centralwidget)
        self.reset_button.setObjectName("reset_button")
        self.gridLayout.addWidget(self.reset_button, 0, 2, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 2, 1, 1)

        self.apply_button = QtWidgets.QPushButton(self.centralwidget)
        self.apply_button.setObjectName("apply_button")
        self.gridLayout.addWidget(self.apply_button, 2, 2, 1, 1)

        # Set up for the fields in the config file
        # They are placed in the order they are displayed when the program is opened
        # The addWidget function takes 5 parameters.
        # addWidget(Object, row, column, row-span, column-span)
        # In gridLayout_2 there are 26 rows (starting from 1), and 4 columns (starting from 0)
        # Both length and height is in "blocks"

        

        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            newObj = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            newObj.setObjectName(widgInfo[LABEL_OBJ_NAME])
            self.gridLayout_2.addWidget(newObj, i+1, 0, 1, 1)
            widgInfo[LABEL_OBJ] = newObj

            if widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                newObj = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                
                # Add a blank item
                newObj.addItem("")
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 1)
                widgInfo[WIDGET1_OBJ] = newObj
            
                newObj = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                
                # Add a blank item
                newObj.addItem("")
                self.gridLayout_2.addWidget(newObj, i+1, 2, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                # Yes radio button
                newObj = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 1)
                widgInfo[WIDGET1_OBJ] = newObj
            
                # No radio button - checked
                newObj = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])
                newObj.setChecked(True)
                self.gridLayout_2.addWidget(newObj, i+1, 2, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                newObj = CheckableComboBox()
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == FILE:
                
                # line edit part
                newObj = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setText("")
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 2)
                widgInfo[WIDGET1_OBJ] = newObj
                
                # browse button
                newObj = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])
                self.gridLayout_2.addWidget(newObj, i+1, 3, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
            
#         self.source_text_name = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.source_text_name.setObjectName("source_text_name")
#         self.gridLayout_2.addWidget(self.source_text_name, 1, 0, 1, 1)
# 
#         self.chose_sourc_text = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.chose_sourc_text.setObjectName("chose_sourc_text")
#         self.chose_sourc_text.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.gridLayout_2.addWidget(self.chose_sourc_text, 1, 1, 1, 3)

#         self.entry_link = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.entry_link.setObjectName("entry_link")
#         self.gridLayout_2.addWidget(self.entry_link, 2, 0, 1, 1)
# 
#         self.chose_entry_link = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.chose_entry_link.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_entry_link.setObjectName("chose_entry_link")
#         self.gridLayout_2.addWidget(self.chose_entry_link, 2, 1, 1, 3)

#         self.sense_number = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.sense_number.setObjectName("sense_number")
#         self.gridLayout_2.addWidget(self.sense_number, 3, 0, 1, 1)
# 
#         self.chose_sense_number = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.chose_sense_number.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_sense_number.setObjectName("chose_sense_number")
#         self.gridLayout_2.addWidget(self.chose_sense_number, 3, 1, 1, 3)

#         self.target_project = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.target_project.setObjectName("target_project")
#         self.gridLayout_2.addWidget(self.target_project, 4, 0, 1, 1)
# 
#         self.chose_target_project = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.chose_target_project.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_target_project.setObjectName("chose_target_project")
#         self.gridLayout_2.addWidget(self.chose_target_project, 4, 1, 1, 3)

#         self.analyzed_output = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.analyzed_output.setObjectName("analyzed_output")
#         self.gridLayout_2.addWidget(self.analyzed_output, 5, 0, 1, 1)
# 
#         self.output_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.output_filename.setText("")
#         self.output_filename.setObjectName("output_filename")
#         self.gridLayout_2.addWidget(self.output_filename, 5, 1, 1, 2)
# 
#         self.a_text_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.a_text_button.setObjectName("a_text_button")
#         self.gridLayout_2.addWidget(self.a_text_button, 5, 3, 1, 1)

#         self.output_ANA_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.output_ANA_file.setObjectName("output_ANA_file")
#         self.gridLayout_2.addWidget(self.output_ANA_file, 6, 0, 1, 1)
# 
#         self.output_ANA_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.output_ANA_filename.setText("")
#         self.output_ANA_filename.setObjectName("output_ANA_filename")
#         self.gridLayout_2.addWidget(self.output_ANA_filename, 6, 1, 1, 2)
# 
#         self.ana_file_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.ana_file_button.setObjectName("ana_file_button")
#         self.gridLayout_2.addWidget(self.ana_file_button, 6, 3, 1, 1)
# 
#         self.output_syn_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.output_syn_file.setObjectName("output_syn_file")
#         self.gridLayout_2.addWidget(self.output_syn_file, 7, 0, 1, 1)
# 
#         self.output_syn_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.output_syn_filename.setText("")
#         self.output_syn_filename.setObjectName("output_syn_filename")
#         self.gridLayout_2.addWidget(self.output_syn_filename, 7, 1, 1, 2)
# 
#         self.syn_file_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.syn_file_button.setObjectName("syn_file_button")
#         self.gridLayout_2.addWidget(self.syn_file_button, 7, 3, 1, 1)
# 
#         self.transfer_result_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.transfer_result_file.setObjectName("transfer_result_file")
#         self.gridLayout_2.addWidget(self.transfer_result_file, 8, 0, 1, 1)
# 
#         self.transfer_result_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.transfer_result_filename.setText("")
#         self.transfer_result_filename.setObjectName("transfer_result_filename")
#         self.gridLayout_2.addWidget(self.transfer_result_filename, 8, 1, 1, 2)
# 
#         self.transfer_result_file_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.transfer_result_file_button.setObjectName("transfer_result_file_button")
#         self.gridLayout_2.addWidget(self.transfer_result_file_button, 8, 3, 1, 1)

#         self.source_complex_types = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.source_complex_types.setObjectName("source_complex_types")
#         self.gridLayout_2.addWidget(self.source_complex_types, 9, 0, 1, 1)
# 
#         self.chose_source_compex_types = CheckableComboBox()
#         self.chose_source_compex_types.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_source_compex_types.setObjectName("chose_source_compex_types")
#         self.gridLayout_2.addWidget(self.chose_source_compex_types, 9, 1, 1, 3)

#         self.bilingual_dictionary_output_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.bilingual_dictionary_output_file.setObjectName("bilingual_dictionary_output_file")
#         self.gridLayout_2.addWidget(self.bilingual_dictionary_output_file, 10, 0, 1, 1)
# 
#         self.bilingual_dictionary_output_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.bilingual_dictionary_output_filename.setText("")
#         self.bilingual_dictionary_output_filename.setObjectName("bilingual_dictionary_output_filename")
#         self.gridLayout_2.addWidget(self.bilingual_dictionary_output_filename, 10, 1, 1, 2)
# 
#         self.bi_dictionary_uotfile_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.bi_dictionary_uotfile_button.setObjectName("bi_dictionary_uotfile_button")
#         self.gridLayout_2.addWidget(self.bi_dictionary_uotfile_button, 10, 3, 1, 1)
# 
#         self.bilingual_dictionary_repalce_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.bilingual_dictionary_repalce_file.setObjectName("bilingual_dictionary_repalce_file")
#         self.gridLayout_2.addWidget(self.bilingual_dictionary_repalce_file, 11, 0, 1, 1)
# 
#         self.bilingual_dictionary_repalce_file_2 = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.bilingual_dictionary_repalce_file_2.setText("")
#         self.bilingual_dictionary_repalce_file_2.setObjectName("bilingual_dictionary_repalce_file_2")
#         self.gridLayout_2.addWidget(self.bilingual_dictionary_repalce_file_2, 11, 1, 1, 2)
# 
#         self.bi_dictionary_replacefile_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.bi_dictionary_replacefile_button.setObjectName("bi_dictionary_replacefile_button")
#         self.gridLayout_2.addWidget(self.bi_dictionary_replacefile_button, 11, 3, 1, 1)
# 
#         self.taget_affix_gloss_list_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.taget_affix_gloss_list_file.setObjectName("taget_affix_gloss_list_file")
#         self.gridLayout_2.addWidget(self.taget_affix_gloss_list_file, 12, 0, 1, 1)
# 
#         self.taget_affix_gloss_list_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.taget_affix_gloss_list_filename.setText("")
#         self.taget_affix_gloss_list_filename.setObjectName("taget_affix_gloss_list_filename")
#         self.gridLayout_2.addWidget(self.taget_affix_gloss_list_filename, 12, 1, 1, 2)
# 
#         self.target_affix_list_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.target_affix_list_button.setObjectName("target_affix_list_button")
#         self.gridLayout_2.addWidget(self.target_affix_list_button, 12, 3, 1, 1)
# 
#         self.infelction_first_element = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.infelction_first_element.setObjectName("infelction_first_element")
#         self.gridLayout_2.addWidget(self.infelction_first_element, 13, 0, 1, 1)
# 
#         self.chose_infelction_first_element = CheckableComboBox()
#         self.chose_infelction_first_element.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_infelction_first_element.setObjectName("chose_infelction_first_element")
#         self.gridLayout_2.addWidget(self.chose_infelction_first_element, 13, 1, 1, 3)
# 
#         self.infelction_second_element = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.infelction_second_element.setObjectName("infelction_second_element")
#         self.gridLayout_2.addWidget(self.infelction_second_element, 14, 0, 1, 1)
# 
#         self.chose_infelction_second_element = CheckableComboBox()
#         self.chose_infelction_second_element.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_infelction_second_element.setObjectName("chose_infelction_second_element")
#         self.gridLayout_2.addWidget(self.chose_infelction_second_element, 14, 1, 1, 3)
# 
#         self.target_morpheme_types = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.target_morpheme_types.setObjectName("target_morpheme_types")
#         self.gridLayout_2.addWidget(self.target_morpheme_types, 15, 0, 1, 1)
# 
#         self.chose_target_morpheme_types = CheckableComboBox()
#         self.chose_target_morpheme_types.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_target_morpheme_types.setObjectName("chose_target_morpheme_types")
#         self.gridLayout_2.addWidget(self.chose_target_morpheme_types, 15, 1, 1, 3)
# 
#         self.source_morpheme_types = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.source_morpheme_types.setObjectName("source_morpheme_types")
#         self.gridLayout_2.addWidget(self.source_morpheme_types, 16, 0, 1, 1)
# 
#         self.chose_source_morpheme_types = CheckableComboBox()
#         self.chose_source_morpheme_types.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_source_morpheme_types.setObjectName("chose_source_morpheme_types")
#         self.gridLayout_2.addWidget(self.chose_source_morpheme_types, 16, 1, 1, 3)
# 
#         self.source_discountiguous_complex = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.source_discountiguous_complex.setObjectName("source_discountiguous_complex")
#         self.gridLayout_2.addWidget(self.source_discountiguous_complex, 17, 0, 1, 1)
# 
#         self.chose_source_discontiguous_compex = CheckableComboBox()
#         self.chose_source_discontiguous_compex.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_source_discontiguous_compex.setObjectName("chose_source_discontiguous_compex")
#         self.gridLayout_2.addWidget(self.chose_source_discontiguous_compex, 17, 1, 1, 3)
# 
#         self.skipped_source_words = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.skipped_source_words.setObjectName("skipped_source_words")
#         self.gridLayout_2.addWidget(self.skipped_source_words, 18, 0, 1, 1)
# 
#         self.chose_skipped_source_words = CheckableComboBox()
#         self.chose_skipped_source_words.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.chose_skipped_source_words.setObjectName("chose_skipped_source_words")
#         self.gridLayout_2.addWidget(self.chose_skipped_source_words, 18, 1, 1, 3)
# 
#         self.a_treetran_output_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.a_treetran_output_file.setObjectName("a_treetran_output_file")
#         self.gridLayout_2.addWidget(self.a_treetran_output_file, 19, 0, 1, 1)
# 
#         self.a_treetran_output_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.a_treetran_output_filename.setObjectName("a_treetran_output_filename")
#         self.gridLayout_2.addWidget(self.a_treetran_output_filename, 19, 1, 1, 2)
# 
#         self.a_tretran_outfile_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.a_tretran_outfile_button.setObjectName("a_tretran_outfile_button")
#         self.gridLayout_2.addWidget(self.a_tretran_outfile_button, 19, 3, 1, 1)
# 
#         self.treetran_insert_words_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.treetran_insert_words_file.setObjectName("treetran_insert_words_file")
#         self.gridLayout_2.addWidget(self.treetran_insert_words_file, 20, 0, 1, 1)
# 
#         self.treetran_insert_words_file_2 = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.treetran_insert_words_file_2.setObjectName("treetran_insert_words_file_2")
#         self.gridLayout_2.addWidget(self.treetran_insert_words_file_2, 20, 1, 1, 2)
# 
#         self.tretran_insert_words_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.tretran_insert_words_button.setObjectName("tretran_insert_words_button")
#         self.gridLayout_2.addWidget(self.tretran_insert_words_button, 20, 3, 1, 1)
# 
#         self.transfer_rules_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.transfer_rules_file.setObjectName("transfer_rules_file")
#         self.gridLayout_2.addWidget(self.transfer_rules_file, 21, 0, 1, 1)
# 
#         self.transfer_rules_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.transfer_rules_filename.setText("")
#         self.transfer_rules_filename.setObjectName("transfer_rules_filename")
#         self.gridLayout_2.addWidget(self.transfer_rules_filename, 21, 1, 1, 2)
# 
#         self.transfer_rules_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.transfer_rules_button.setObjectName("transfer_rules_button")
#         self.gridLayout_2.addWidget(self.transfer_rules_button, 21, 3, 1, 1)
# 
#         self.testbed_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.testbed_file.setObjectName("testbed_file")
#         self.gridLayout_2.addWidget(self.testbed_file, 22, 0, 1, 1)
# 
#         self.testbed_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.testbed_filename.setText("")
#         self.testbed_filename.setObjectName("testbed_filename")
#         self.gridLayout_2.addWidget(self.testbed_filename, 22, 1, 1, 2)
# 
#         self.testbed_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.testbed_button.setObjectName("testbed_button")
#         self.gridLayout_2.addWidget(self.testbed_button, 22, 3, 1, 1)
# 
#         self.testbed_result_file = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.testbed_result_file.setObjectName("testbed_result_file")
#         self.gridLayout_2.addWidget(self.testbed_result_file, 23, 0, 1, 1)
# 
#         self.testbed_result_filename = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.testbed_result_filename.setText("")
#         self.testbed_result_filename.setObjectName("testbed_result_filename")
#         self.gridLayout_2.addWidget(self.testbed_result_filename, 23, 1, 1, 2)
# 
#         self.testbed_result_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
#         self.testbed_result_button.setObjectName("testbed_result_button")
#         self.gridLayout_2.addWidget(self.testbed_result_button, 23, 3, 1, 1)




#         self.category_abbreviation_pairs = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.category_abbreviation_pairs.setObjectName("category_abbreviation_pairs")
#         self.gridLayout_2.addWidget(self.category_abbreviation_pairs, 24, 0, 1, 1)
# 
#         self.category_abbreviation_one = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.category_abbreviation_one.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.category_abbreviation_one.setObjectName("category_abbreviation_one")
#         self.category_abbreviation_one.addItem("")
#         self.gridLayout_2.addWidget(self.category_abbreviation_one, 24, 1, 1, 1)
# 
#         self.category_abbreviation_two = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
#         self.category_abbreviation_two.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
#         self.category_abbreviation_two.setObjectName("category_abbreviation_two")
#         self.category_abbreviation_two.addItem("")
#         self.gridLayout_2.addWidget(self.category_abbreviation_two, 24, 2, 1, 1)

#         self.cleanup_target_words = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.cleanup_target_words.setObjectName("cleanup_target_words")
#         self.gridLayout_2.addWidget(self.cleanup_target_words, 25, 0, 1, 1)
# 
#         self.cleanup_yes = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
#         self.cleanup_yes.setObjectName("cleanup_yes")
#         self.gridLayout_2.addWidget(self.cleanup_yes, 25, 1, 1, 1)
# 
#         self.cleanup_no = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
#         self.cleanup_no.setChecked(True)
#         self.cleanup_no.setObjectName("cleanup_no")
#         self.gridLayout_2.addWidget(self.cleanup_no, 25, 2, 1, 1)
# 
#         self.sentence_punctuation = QtWidgets.QLabel(self.scrollAreaWidgetContents)
#         self.sentence_punctuation.setObjectName("sentence_punctuation")
#         self.gridLayout_2.addWidget(self.sentence_punctuation, 26, 0, 1, 1)
# 
#         self.punctuation = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
#         self.punctuation.setText("")
#         self.punctuation.setObjectName("punctuation")
#         self.gridLayout_2.addWidget(self.punctuation, 26, 1, 1, 3)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FLExTrans Settings"))

        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            widgInfo[LABEL_OBJ].setText(_translate("MainWindow", widgInfo[LABEL_TEXT]))

            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].setText(_translate("MainWindow", "Browse file..."))
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

        # Setting texts, in same order as they appear on the tool
#        self.source_text_name.setText(_translate("MainWindow", "Source Text Name"))

#        self.entry_link.setText(_translate("MainWindow", "Source Custom Field for Entry Link"))

#        self.sense_number.setText(_translate("MainWindow", "Source Custom Field for Sense Number"))

#         self.target_project.setText(_translate("MainWindow", "Target Project"))
# 
#         self.analyzed_output.setText(_translate("MainWindow", "Analyzed Text Output File"))
#         self.a_text_button.setText(_translate("MainWindow", "Browse file..."))

#         self.output_ANA_file.setText(_translate("MainWindow", "Target Output ANA File"))
#         self.ana_file_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.output_syn_file.setText(_translate("MainWindow", "Target Output Synthesis File"))
#         self.syn_file_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.transfer_result_file.setText(_translate("MainWindow", "Target Transfer Results File"))
#         self.transfer_result_file_button.setText(_translate("MainWindow", "Browse file..."))

#        self.source_complex_types.setText(_translate("MainWindow", "Source Complex Form Types"))

#         self.bilingual_dictionary_output_file.setText(_translate("MainWindow", "Bilingual Dictionary Output File"))
#         self.bi_dictionary_uotfile_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.bilingual_dictionary_repalce_file.setText(_translate("MainWindow", "Bilingual Dictionary Replacement File"))
#         self.bi_dictionary_replacefile_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.taget_affix_gloss_list_file.setText(_translate("MainWindow", "Target Affix Gloss List File"))
#         self.target_affix_list_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.infelction_first_element.setText(_translate("MainWindow", "Target Complex Form Types \n"
#                                                                        "with Inflection on 1st Element"))
#         self.chose_infelction_first_element.setItemText(0, _translate("MainWindow", "..."))
# 
#         self.infelction_second_element.setText(_translate("MainWindow", "Target Complex Form Types \n"
#                                                                         "with Inflection on 2nd Element"))
#         self.chose_infelction_second_element.setItemText(0, _translate("MainWindow", "..."))
# 
#         self.target_morpheme_types.setText(_translate("MainWindow", "Target Morpheme Types \n"
#                                                                     "Counted As Roots"))
# 
#         self.source_morpheme_types.setText(_translate("MainWindow", "Source Morpheme Types \n"
#                                                                     "Counted As Roots"))
# 
#         self.source_discountiguous_complex.setText(_translate("MainWindow", "Source Discontiguous Complex Form Types"))
# 
#         self.skipped_source_words.setText(_translate("MainWindow", "Source Skipped Word Grammatical \n"
#                                                                    "Categories for Discontigous Complex Forms"))
# 
#         self.a_treetran_output_file.setText(_translate("MainWindow", "Analyzed Text TreeTran Output File"))
#         self.a_tretran_outfile_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.treetran_insert_words_file.setText(_translate("MainWindow", "TreeTran Insert Words File"))
#         self.tretran_insert_words_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.transfer_rules_file.setText(_translate("MainWindow", "Transfer Rules File"))
#         self.transfer_rules_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.testbed_file.setText(_translate("MainWindow", "Testbed File"))
#         self.testbed_button.setText(_translate("MainWindow", "Browse file..."))
# 
#         self.testbed_result_file.setText(_translate("MainWindow", "Testbed Results File"))
#         self.testbed_result_button.setText(_translate("MainWindow", "Browse file..."))

#         self.category_abbreviation_pairs.setText(_translate("MainWindow", "Category Abbreviation Pairs"))
#         self.category_abbreviation_one.setItemText(0, _translate("MainWindow", "..."))
#         self.category_abbreviation_two.setItemText(0, _translate("MainWindow", "..."))

#         self.cleanup_target_words.setText(_translate("MainWindow", "Cleanup Unknown Target Words"))
#         self.cleanup_no.setText(_translate("MainWindow", "No"))
#         self.cleanup_yes.setText(_translate("MainWindow", "Yes"))
# 
#         self.sentence_punctuation.setText(_translate("MainWindow", "Sentence Punctuation"))

        self.apply_button.setText(_translate("MainWindow", "Apply"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))

        # ToolTip
#        self.chose_sourc_text.setToolTip("The name of the text (in the first analysis writing system)\n"+
#                                         "in the source FLEx project to be translated.")

#         self.a_text_button.setToolTip("The path and name of the file which holds\n"+
#                                       "the extracted source text.")

#         self.ana_file_button.setToolTip("The path and name of the file holding\n"+
#                                         "the intermediary text in STAMP format.")
# 
#         self.syn_file_button.setToolTip("The path and name of the file holding\n"+
#                                         "the intermediary synthesized file.")
# 
#         self.transfer_result_file_button.setToolTip("The path and name of the file which holds the text contents\n"+
#                                                     "after going through the transfer process.")

#         self.chose_source_compex_types.setToolTip("One or more complex types from the source FLEx project.\n"+
#                                                   "These types will be treated as a lexical unit in FLExTrans and whenever\n"+
#                                                   "the components that make up this type of complex form are found sequentially\n"+
#                                                   "in the source text, they will be converted to one lexical unit.")

#         self.chose_entry_link.setToolTip("The name of the custom field in the source FLEx project that\n"+
#                                          "holds the link information to entries in the target FLEx project.")
# 
#         self.chose_sense_number.setToolTip("The name of the custom field in the source FLEx project\n"+
#                                            "that holds the sense number of the target entry.")

#         self.bi_dictionary_uotfile_button.setToolTip("The path and name of the file which holds the bilingual lexicon.")
# 
#         self.bi_dictionary_replacefile_button.setToolTip("The path and name of the file which holds replacement\n"+
#                                                          "entry pairs for the bilingual lexicon.")
# 
# #        self.chose_target_project.setToolTip("The name of the target FLEx project.")
# 
#         self.target_affix_list_button.setToolTip("The ancillary file that hold a list of affix\n"+
#                                                  "glosses from the target FLEx project.")
# 
#         self.chose_infelction_first_element.setToolTip("One or more complex types from the target FLEx project.\n"+
#                                                        "These types, when occurring in the text file to be synthesized,\n"+
#                                                        "will be broken down into their constituent entries. Use this property\n"+
#                                                        "for the types that have inflection on the first element of the complex form.")
# 
#         self.chose_infelction_second_element.setToolTip("Same as above. Use this property for the types that have inflection\n"+
#                                                         "on the second element of the complex form.")
# 
#         self.chose_target_morpheme_types.setToolTip("Morpheme types in the target FLEx project that are to be considered\n"+
#                                                     "as some kind of root. In other words, non-affixes and non-clitics.")
# 
#         self.chose_source_morpheme_types.setToolTip("Morpheme types in the source FLEx project that are to be considered\n"+
#                                                     "as some kind of root. In other words, non-affixes and non-clitics.")
# 
#         self.chose_source_discontiguous_compex.setToolTip("One or more complex types from the source FLEx project.\n"+
#                                                           "These types will allow one intervening word between the first\n"+
#                                                           "and second words of the complex type, yet will still be treated\n"+
#                                                           "as a lexical unit.")
# 
#         self.chose_skipped_source_words.setToolTip("One or more grammatical categories that can intervene in the above complex types.")
# 
#         self.a_tretran_outfile_button.setToolTip("The path and name of the file that holds the output from TreeTran.")
# 
#         self.tretran_insert_words_button.setToolTip("The path and name of the file that has a list of\n"+
#                                                     "words that can be inserted with a TreeTran rule.")
# 
#         self.transfer_rules_button.setToolTip("The path and name of the file containing the transfer rules.")
# 
#         self.testbed_button.setToolTip("The path and name of the testbed file.")
# 
#         self.testbed_result_button.setToolTip("The path and name of the testbed results file.")



#         self.category_abbreviation_one.setToolTip("One or more pairs of grammatical categories where the first category\n"+
#                                                   "is the “from” category in the source FLEx project and the second category\n"+
#                                                   "is the “to” category in the target FLEx project. Use the abbreviations of\n"+
#                                                   "the FLEx categories. The substitution happens in the bilingual lexicon.")
# 
#         self.category_abbreviation_two.setToolTip("One or more pairs of grammatical categories where the first category\n" +
#                                                   "is the “from” category in the source FLEx project and the second category\n" +
#                                                   "is the “to” category in the target FLEx project. Use the abbreviations of\n" +
#                                                   "the FLEx categories. The substitution happens in the bilingual lexicon.")

#         self.cleanup_yes.setToolTip("Indicates if the system should remove preceding @ signs\n"+
#                                     "and numbers in the form N.N following words in the target text.")
# 
#         self.cleanup_no.setToolTip("Indicates if the system should remove preceding @ signs\n" +
#                                    "and numbers in the form N.N following words in the target text.")
# 
#         self.punctuation.setToolTip("A list of punctuation that ends a sentence.\n"+
#                                     "In transfer rules you can check for the end of a sentence.")

class Main(QMainWindow):

    def __init__(self, configMap, report, targetDB, DB):
        QMainWindow.__init__(self)
        # RL code review 23Jun22: I think it is good practice to put assigning of parameter values at the top of the method
        self.report = report
        self.configMap = configMap
        self.targetDB = targetDB
        self.DB = DB

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), ReadConfig.CONFIG_FILE)
        
        self.config = myPath

        # connect buttons to functions
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].clicked.connect(make_open_file(self, widgInfo))
             
        #Buttons
        self.ui.apply_button.clicked.connect(self.save)
#        self.ui.reset_button.clicked.connect(self.reset)

#        self.ui.a_text_button.clicked.connect(self.open_a_text)
#         self.ui.ana_file_button.clicked.connect(self.open_ana_file)
#         self.ui.syn_file_button.clicked.connect(self.open_syn_file)
#         self.ui.transfer_result_file_button.clicked.connect(self.open_tranfer_result)


#         self.ui.bi_dictionary_uotfile_button.clicked.connect(self.open_bi_dic_file)
#         self.ui.bi_dictionary_replacefile_button.clicked.connect(self.open_bi_dic_replacefile)
#         self.ui.target_affix_list_button.clicked.connect(self.open_affix_list)
#         self.ui.a_tretran_outfile_button.clicked.connect(self.open_a_treetran)
#         self.ui.tretran_insert_words_button.clicked.connect(self.open_insert_words)
#         self.ui.transfer_rules_button.clicked.connect(self.open_transfer_rules)
#         self.ui.testbed_button.clicked.connect(self.open_testbed)
#         self.ui.testbed_result_button.clicked.connect(self.open_testbed_result)

        self.init_load()

    # RL code review 23Jun22: Could connect() calls above call browse() directly?
#     def do_browse(self, myWidgInfo):
#         
#         self.browse(myWidgInfo[WIDGET1_OBJ], "(*.*)")
#         
#    def open_a_text(self):
#        self.browse(self.ui.output_filename, "(*.*)")

#     def open_ana_file(self):
#         self.browse(self.ui.output_ANA_filename, "(*.*)")
# 
#     def open_syn_file(self):
#         self.browse(self.ui.output_syn_filename, "(*.*)")
# 
#     def open_tranfer_result(self):
#         self.browse(self.ui.transfer_result_filename, "(*.*)")

#     def open_bi_dic_file(self):
#         self.browse(self.ui.bilingual_dictionary_output_filename, "(*.*)")
# 
#     def open_bi_dic_replacefile(self):
#         self.browse(self.ui.bilingual_dictionary_repalce_file_2, "(*.*)")
# 
#     def open_affix_list(self):
#         self.browse(self.ui.taget_affix_gloss_list_filename, "(*.*)")
# 
#     def open_a_treetran(self):
#         self.browse(self.ui.a_treetran_output_filename, "(*.*)")
# 
#     def open_insert_words(self):
#         self.browse(self.ui.treetran_insert_words_file_2, "(*.*)")
# 
#     def open_transfer_rules(self):
#         self.browse(self.ui.transfer_rules_filename, "(*.*)")
# 
#     def open_testbed(self):
#         self.browse(self.ui.testbed_filename, "(*.*)")
# 
#     def open_testbed_result(self):
#         self.browse(self.ui.testbed_result_filename, "(*.*)")

#     def browse(self, name, end):
#         filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", end)
#         if filename:
#             name.setText(os.path.relpath(filename).replace(os.sep, '/'))
#             name.setToolTip(os.path.abspath(filename).replace(os.sep, '/'))

    def read(self, key):
        return ReadConfig.getConfigVal(self.configMap, key, self.report)

    def init_load(self):
        
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
            
#        self.ui.chose_sourc_text.clear()
#         self.ui.chose_entry_link.clear()
#         self.ui.chose_sense_number.clear()
#         self.ui.chose_target_project.clear()
#        self.ui.chose_source_compex_types.clear()
#         self.ui.chose_infelction_first_element.clear()
#         self.ui.chose_infelction_second_element.clear()
#         self.ui.chose_target_morpheme_types.clear()
#         self.ui.chose_source_morpheme_types.clear()
#         self.ui.chose_source_discontiguous_compex.clear()
#         self.ui.chose_skipped_source_words.clear()
#         self.ui.category_abbreviation_one.clear()
#         self.ui.category_abbreviation_one.addItem("...")
#         self.ui.category_abbreviation_two.clear()
#         self.ui.category_abbreviation_two.addItem("...")

        # load all the widgets, calling the applicable load function
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                # pass two widgets
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], widgInfo[WIDGET2_OBJ], self, widgInfo[CONFIG_NAME])

            else:
                
                # Call the load function for this widget, pass in the widget object and this window object
                # Also pass the config file setting name
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], self, widgInfo[CONFIG_NAME])

#         # Source Text name
#         sourceList = []
#         for item in self.DB.ObjectsIn(ITextRepository):
# 
#             source_list.append(str(item).strip())
# 
#         sorted_source_list = sorted(source_list, key=str.casefold)
#         
#         # RL code review 23Jun22: below is how I might add whitespace, not a must, but it could help other people who are reading the code
#         config_source = self.read(ReadConfig.SOURCE_TEXT_NAME)
#         
#         for i, item_str in enumerate(sorted_source_list):
#             
#             widgetList[0][len(widgetList[0])-1].addItem(item_str)
#             
#             if item_str == config_source:
#                 
#                 widgetList[0][len(widgetList[0])-1].setCurrentIndex(i)
        
        # RL code review 23Jun22: in Python you can also do: 
        # for i, item in enumerate(self.DB.LexiconGetSenseCustomFields()):  - this way you don't have to initialize i or increment i
#         # Source Custom field for Entry Link and Sense number
#         for i, item in enumerate(self.DB.LexiconGetSenseCustomFields()):
# 
#             # Add the element to the comboBox, item[1] is because item is some sort of tuple value
#             self.ui.chose_entry_link.addItem(str(item[1]))            # RL code review 23Jun22: why item[1]? maybe explain
#             self.ui.chose_sense_number.addItem(str(item[1]))          # RL code review 23Jun22: why convert to a str, but not in the next line?
# 
#             # Check the currently selected value
#             if item[1] == self.read(ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY):
#                 self.ui.chose_entry_link.setCurrentIndex(i)
# 
#             if item[1] == self.read(ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM):
#                 self.ui.chose_sense_number.setCurrentIndex(i)

#         # Target Projects
#         #TODO Make this disable the other stuff that uses target??
#         for i, item in enumerate(AllProjectNames()):
#             self.ui.chose_target_project.addItem(item)
#             if item == self.read('TargetProject'):
#                 self.ui.chose_target_project.setCurrentIndex(i)
        
        # RL code review 23Jun22: for easier maintenance of the code, it would be better have something like x = self.read('AnalyzedTextOutputFile')
        # and then use x twice in the next two lines. This way if the 'AnalyzedTextOutputFile' changes, you only have to change it once.
        # Also, it's nice if we could use constants for all these strings, in fact you will find most of them in ReadConfig.py so you could use ReadConfig.ANALYZED_TEXT_FILE, etc.
        # Analyzed Text file
#         analyzedText = self.read(ReadConfig.ANALYZED_TEXT_FILE)
#         self.ui.output_filename.setText(os.path.relpath(analyzedText).replace(os.sep, '/'))
#         self.ui.output_filename.setToolTip(os.path.abspath(analyzedText).replace(os.sep, '/'))

        # Output ANA file
#         ANAFile = self.read(ReadConfig.TARGET_ANA_FILE)
#         self.ui.output_ANA_filename.setText(os.path.relpath(ANAFile).replace(os.sep, '/'))
#         self.ui.output_ANA_filename.setToolTip(os.path.abspath(ANAFile).replace(os.sep, '/'))
# 
#         # Output Synthesis file
#         synFile = self.read(ReadConfig.TARGET_SYNTHESIS_FILE)
#         self.ui.output_syn_filename.setText(os.path.relpath(synFile).replace(os.sep, '/'))
#         self.ui.output_syn_filename.setToolTip(os.path.abspath(synFile).replace(os.sep, '/'))
# 
#         # Transfer result file
#         transferFile = self.read(ReadConfig.TRANSFER_RESULTS_FILE)
#         self.ui.transfer_result_filename.setText(os.path.relpath(transferFile).replace(os.sep, '/'))
#         self.ui.transfer_result_filename.setToolTip(os.path.abspath(transferFile).replace(os.sep, '/'))

        # RL code review 23Jun22: It would be nice to explain in a comment which setting is being loaded as well as
        # what you have here saying the data comes from the Complex Form Types list
        # From the Complex Form Types list
#         array = []
#         for item in self.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
# 
#             array.append(str(item))
# 
#         self.ui.chose_source_compex_types.addItems(array)
#         
#         # RL code review 23Jun22: Again for maintenance it would be better to have something like settingStr = self.read('SourceComplexTypes') then use settingStr twice
#         # Source Complex Types
#         complexType = self.read(ReadConfig.SOURCE_COMPLEX_TYPES)
#         if complexType:
# 
#             for test in complexType:
# 
#                 if test in array:
#                     self.ui.chose_source_compex_types.check(test)

#         # Bilingual Dictionary output file
#         biDictFile = self.read(ReadConfig.BILINGUAL_DICTIONARY_FILE)
#         self.ui.bilingual_dictionary_output_filename.setText(os.path.relpath(biDictFile).replace(os.sep, '/'))
#         self.ui.bilingual_dictionary_output_filename.setToolTip(os.path.abspath(biDictFile).replace(os.sep, '/'))
# 
#         # Bilingual Dictionary replace file
#         biDictReplaceFile = self.read(ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE)
#         self.ui.bilingual_dictionary_repalce_file_2.setText(os.path.relpath(biDictReplaceFile).replace(os.sep, '/'))
#         self.ui.bilingual_dictionary_repalce_file_2.setToolTip(os.path.abspath(biDictReplaceFile).replace(os.sep, '/'))
# 
#         # Affix Gloss list file
#         affixGlossFile = self.read(ReadConfig.TARGET_AFFIX_GLOSS_FILE)
#         self.ui.taget_affix_gloss_list_filename.setText(os.path.relpath(affixGlossFile).replace(os.sep, '/'))
#         self.ui.taget_affix_gloss_list_filename.setToolTip(os.path.abspath(affixGlossFile).replace(os.sep, '/'))

        #From the Complex Form Types list
#         array = []
#         for item in self.targetDB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
# 
#             array.append(str(item))
# 
#         # Forms for inflection
#         # Add items to both first and second element
#         self.ui.chose_infelction_first_element.addItems(array)
#         self.ui.chose_infelction_second_element.addItems(array)
# 
#         # Check the elements on first element
#         firstElm = self.read(ReadConfig.TARGET_FORMS_INFLECTION_1ST)
#         if firstElm:
# 
#             for test in firstElm:
# 
#                 if test in array:
#                     self.ui.chose_infelction_first_element.check(test)
# 
#         # Check the elements on second element
#         secondElm = self.read(ReadConfig.TARGET_FORMS_INFLECTION_2ND)
#         if secondElm:
# 
#             for test in secondElm:
# 
#                 if test in array:
#                     self.ui.chose_infelction_second_element.check(test)

#         # From the Morpheme Types list
#         # Target Morpheme Names Counted As Roots
#         array = []
#         for item in self.targetDB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
# 
#             # Strip is because morpheme types come with some add-ons that are not necessary for the user in this case
#             array.append(str(item).strip("-=~*")) # RL code review 23Jun22: explain the strip()
# 
#         self.ui.chose_target_morpheme_types.addItems(array)
# 
#         for test in self.read(ReadConfig.TARGET_MORPHNAMES):
# 
#             if test in array:
# 
#                 self.ui.chose_target_morpheme_types.check(test)
# 
#         # Source Morpheme Names Counted As Roots
#         array = []
#         for item in self.DB.lp.LexDbOA.MorphTypesOA.PossibilitiesOS:
# 
#             # Strip is because morpheme types come with some add-ons that are not necessary for the user in this case
#             array.append(str(item).strip("-=~*"))
# 
#         self.ui.chose_source_morpheme_types.addItems(array)
# 
#         for test in self.read(ReadConfig.SOURCE_MORPHNAMES):
# 
#             if test in array:
# 
#                 self.ui.chose_source_morpheme_types.check(test)


#         # From the Complex Form Types list.
#         # Source Discontigous Complex Types
#         array = []
#         for item in self.DB.lp.LexDbOA.ComplexEntryTypesOA.PossibilitiesOS:
# 
#             array.append(str(item))
# 
#         self.ui.chose_source_discontiguous_compex.addItems(array)
# 
#         disComplexTypes = self.read(ReadConfig.SOURCE_DISCONTIG_TYPES)
#         if disComplexTypes:
#             for test in disComplexTypes:
# 
#                 if test in array:
# 
#                     self.ui.chose_source_discontiguous_compex.check(test)
# 
#         # From the category abbreviation list.
#         # Source Discontigous Complex Form Skipped Word Grammatical Categories
#         array = []
#         for pos in self.DB.lp.AllPartsOfSpeech:
# 
#             posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
#             array.append(posAbbrStr)
# 
#         self.ui.chose_skipped_source_words.addItems(array)
# 
#         disSkipped = self.read(ReadConfig.SOURCE_DISCONTIG_SKIPPED)
#         if disSkipped:
#             for test in disSkipped:
# 
#                 if test in array:
# 
#                     self.ui.chose_skipped_source_words.check(test)
# 
#         # Analyzed text treeTran output file, if there are any
#         analyzedTreeTran = self.read(ReadConfig.ANALYZED_TREETRAN_TEXT_FILE)
#         if analyzedTreeTran:
#             self.ui.a_treetran_output_filename.setText(os.path.relpath(analyzedTreeTran).replace(os.sep, '/'))
#             self.ui.a_treetran_output_filename.setToolTip(os.path.abspath(analyzedTreeTran).replace(os.sep, '/'))
# 
#         # TreeTran insert words file, if there are any
#         treeTranFile = self.read(ReadConfig.TREETRAN_INSERT_WORDS_FILE)
#         if treeTranFile:
#             self.ui.treetran_insert_words_file_2.setText(os.path.relpath(treeTranFile).replace(os.sep, '/'))
#             self.ui.treetran_insert_words_file_2.setToolTip(os.path.abspath(treeTranFile).replace(os.sep, '/'))
# 
#         # Transfer Rules file
#         transferRulesFile = self.read(ReadConfig.TRANSFER_RULES_FILE)
#         self.ui.transfer_rules_filename.setText(os.path.relpath(transferRulesFile).replace(os.sep, '/'))
#         self.ui.transfer_rules_filename.setToolTip(os.path.abspath(transferRulesFile).replace(os.sep, '/'))
# 
#         # Testbed File
#         testbedFile = self.read(ReadConfig.TESTBED_FILE)
#         self.ui.testbed_filename.setText(os.path.relpath(testbedFile).replace(os.sep, '/'))
#         self.ui.testbed_filename.setToolTip(os.path.abspath(testbedFile).replace(os.sep, '/'))
# 
#         # Testbed Result file
#         testbedResultFile = self.read(ReadConfig.TESTBED_RESULTS_FILE)
#         self.ui.testbed_result_filename.setText(os.path.relpath(testbedResultFile).replace(os.sep, '/'))
#         self.ui.testbed_result_filename.setToolTip(os.path.abspath(testbedResultFile).replace(os.sep, '/'))

        # From the category abbreviation list.
        # Category Abbreviation Substitution List, check if chosen
#         catAbbrevList = self.read(ReadConfig.CATEGORY_ABBREV_SUB_LIST)
#         for i, pos in enumerate(self.DB.lp.AllPartsOfSpeech):
# 
#             posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
#             self.ui.category_abbreviation_one.addItem(posAbbrStr)
# 
#             if catAbbrevList:
#                 if posAbbrStr == catAbbrevList[0]: # The first one in the config file
# 
#                     self.ui.category_abbreviation_one.setCurrentIndex(i)
# 
#         for i, pos in enumerate(self.targetDB.lp.AllPartsOfSpeech):
# 
#             posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
#             self.ui.category_abbreviation_two.addItem(posAbbrStr)
# 
#             if catAbbrevList:
#                 if posAbbrStr == catAbbrevList[1]: # The second one in the config file
# 
#                     self.ui.category_abbreviation_two.setCurrentIndex(i)

        # Clean Up Unknown target Words
#         if self.read(ReadConfig.CLEANUP_UNKNOWN_WORDS) == 'y':
# 
#             self.ui.cleanup_yes.setChecked(True)
# 
#         # Punctuation
#         self.ui.punctuation.setText(self.read(ReadConfig.SENTENCE_PUNCTUATION))
#         # Align left as default
#         self.ui.punctuation.setAlignment(Qt.AlignLeft)

    def save(self):
        # RL code review 23Jun22: maybe a better variable name
        punctSelected='n'
        if self.ui.cleanup_yes.isChecked():
            punctSelected='y'
        f = open(self.config, "w", encoding='utf-8')
        
        # RL code review 23Jun22: I personally would prefer each line to have f.write(...), but this is ok
        # this is going to hard to maintain since we don't know which setting is connected to which ui element and what kind of data will be coming from that ui element
        # The only solution might be too much work, but somehow have a list with the setting string, the ui element, and a type and then use a loop to put out the appropriate 
        # string based on it's type. In theory it might make it easier to add new settings just at the top and the rest of the code does loops over the master list.
        # Just an idea.
        
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].currentText()
                
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].currentData()
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                valStr = widgInfo[WIDGET1_OBJ].currentText()+','+widgInfo[WIDGET2_OBJ].currentText()
                
                # If the user selected ..., set the value to blank
                if '...' in valStr:
                    
                    valStr = ''
                    
                outStr = widgInfo[CONFIG_NAME]+'='+valStr
                
            elif widgInfo[WIDGET_TYPE] == FILE or widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].text()
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                if widgInfo[WIDGET1_OBJ].isChecked():
                    
                    selected='y'
                else:
                    selected='n'
            
                outStr = widgInfo[CONFIG_NAME]+'='+selected
                
            f.write(outStr+'\n')
            
        #f.write("SourceTextName="+widgetList[0][len(widgetList[0])-1].currentText()+"\n"+
                #"AnalyzedTextOutputFile="+self.ui.output_filename.text()+"\n"+
                #"TargetOutputANAFile="+self.ui.output_ANA_filename.text()+"\n"+
                #"TargetOutputSynthesisFile="+self.ui.output_syn_filename.text()+"\n"+
                #"TargetTranferResultsFile="+self.ui.transfer_result_filename.text()+"\n"+
        f.write("SourceComplexTypes="+self.optional_mul(self.ui.chose_source_compex_types.currentData())+"\n"+
#                "SourceCustomFieldForEntryLink="+self.ui.chose_entry_link.currentText()+"\n"+
#                "SourceCustomFieldForSenseNum="+self.ui.chose_sense_number.currentText()+"\n"+
                "TargetAffixGlossListFile="+self.ui.taget_affix_gloss_list_filename.text()+"\n"+
                "BilingualDictOutputFile="+self.ui.bilingual_dictionary_output_filename.text()+"\n"+
                "BilingualDictReplacementFile="+self.ui.bilingual_dictionary_repalce_file_2.text()+"\n"+
#                "TargetProject="+self.ui.chose_target_project.currentText()+"\n"+
                "TargetComplexFormsWithInflectionOn1stElement="+self.optional_mul(self.ui.chose_infelction_first_element.currentData())+"\n"+
                "TargetComplexFormsWithInflectionOn2ndElement="+self.optional_mul(self.ui.chose_infelction_second_element.currentData())+"\n"+
                "TargetMorphNamesCountedAsRoots="+self.optional_mul(self.ui.chose_target_morpheme_types.currentData())+"\n"+ #stem,bound stem,root,bound root,phrase
                "SourceMorphNamesCountedAsRoots="+self.optional_mul(self.ui.chose_source_morpheme_types.currentData())+"\n"+#stem,bound stem,root,bound root,phrase
                "SourceDiscontigousComplexTypes="+self.optional_mul(self.ui.chose_source_discontiguous_compex.currentData())+"\n"+
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories="+self.optional_mul(self.ui.chose_skipped_source_words.currentData())+"\n"+
                "AnalyzedTextTreeTranOutputFile="+self.ui.a_treetran_output_filename.text()+"\n"+
                "TreeTranInsertWordsFile="+self.ui.treetran_insert_words_file_2.text()+"\n"+
                "TransferRulesFile="+self.ui.transfer_rules_filename.text()+"\n"+
                "TestbedFile="+self.ui.testbed_filename.text()+"\n"+
                "TestbedResultsFile="+self.ui.testbed_result_filename.text()+"\n"+
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n"+
                "CategoryAbbrevSubstitutionList="+self.optional(self.ui.category_abbreviation_one)+","+self.optional(self.ui.category_abbreviation_two)+"\n"+
                "CleanUpUnknownTargetWords="+punctSelected+"\n"+
                "SentencePunctuation="+self.ui.punctuation.text()+"\n")
        f.close()
        msgBox = QMessageBox()
        msgBox.setText("Your file has been successfully saved.")
        msgBox.setWindowTitle("Successful save")
        msgBox.exec()

    def optional(self, string):
        write = ''
        if string.currentText() != '...':
            write = string.currentText()
        return write

    def optional_mul(self, array):
        write = ''
        if array:
            for text in array:
                write += text + ","
        return write

    def reset(self):
        f = open(self.config, "w", encoding='utf-8') # TODO change here when new standard
        
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            f.write(widgInfo[CONFIG_NAME]+'='+widgInfo[DEFAULT_VALUE]+'\n')
         
        #f.write("SourceTextName=Text1\n" +
#                 "SourceCustomFieldForEntryLink=Target Equivalent\n" +
#                 "SourceCustomFieldForSenseNum=Target Sense Number\n" +
        f.write("AnalyzedTextOutputFile=Output\\source_text.aper\n" +
                "TargetOutputANAFile=Build\\myText.ana\n" +
                "TargetOutputSynthesisFile=Output\\myText.syn\n" +
                "TargetTranferResultsFile=Output\\target_text.aper\n" +
                "SourceComplexTypes=\n" +
                "BilingualDictOutputFile=Output\\bilingual.dix\n" +
                "BilingualDictReplacementFile=replace.dix\n" +
                "TargetProject=Swedish-FLExTrans-Sample\n" +
                "TargetAffixGlossListFile=Build\\target_affix_glosses.txt\n" +
                "TargetComplexFormsWithInflectionOn1stElement=\n" +
                "TargetComplexFormsWithInflectionOn2ndElement=\n" +
                "TargetMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase,\n" +
                "SourceMorphNamesCountedAsRoots=stem,bound stem,root,bound root,phrase,\n" +
                "SourceDiscontigousComplexTypes=\n" +
                "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories=\n" +
                "AnalyzedTextTreeTranOutputFile=\n" +
                "TreeTranInsertWordsFile=\n" +
                "TransferRulesFile=transfer_rules.t1x\n" +
                "TestbedFile=testbed.xml\n" +
                "TestbedResultsFile=Output\\testbed_results.xml\n" +
                "# This property is in the form source_cat,target_cat. Multiple pairs can be defined\n" +
                "CategoryAbbrevSubstitutionList=\n" +
                "CleanUpUnknownTargetWords=n\n" +
                "SentencePunctuation=.?;:!\"\'\n")
        f.close()
        self.init_load()

def MainFunction(DB, report, modify=True):
    # Read the configuration file which we assume is in the current directory.

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        report.error('Error reading configuration file.')
        return

    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenProject(targetProj, False)
    except:
        raise

    # Show the window
    app = QApplication(sys.argv)

    window = Main(configMap, report, TargetDB, DB,) #sourceDB

    window.show()

    app.exec_()
    msgBox = QMessageBox()
    if QMessageBox().question(msgBox, 'Save?', "Do you want to save before you leave?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
        window.save()

    TargetDB.CloseProject()


# ----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs=docs)

widgetList = [
   # label obj name      label text          obj1 name        obj2 name type     label   obj1    obj2     load function       config key name              default value
   ["source_text_name", "Source Text Name", "choose_source_text", "", COMBO_BOX, object, object, object, loadSourceTextList, ReadConfig.SOURCE_TEXT_NAME, 'Text1',\
   # tooltip text
    "The name of the text (in the first analysis writing system)\nin the source FLEx project to be translated."],\
   
   ["entry_link", "Source Custom Field for Entry Link", "choose_entry_link", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, 'Target Equivalent',\
    "The name of the custom field in the source FLEx project that\nholds the link information to entries in the target FLEx project."],\
   
   ["sense_number", "Source Custom Field for Sense Number", "chose_sense_number", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, 'Target Sense Number',\
    "The name of the custom field in the source FLEx project\nthat holds the sense number of the target entry."],\

   ["target_project", "Target Project", "chose_target_project", "", COMBO_BOX, object, object, object, loadTargetProjects, ReadConfig.TARGET_PROJECT, 'Swedish-FLExTrans-Sample',\
    "The name of the target FLEx project."],\

   ["analyzed_output", "Analyzed Text Output File", "output_filename", "a_text_button", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TEXT_FILE, 'Output\\source_text.txt',\
    "The path and name of the file which holds\nthe extracted source text."],\

   ["output_ANA_file", "Target Output ANA File", "output_ANA_filename", "ana_file_button", FILE, object, object, object, loadFile, ReadConfig.TARGET_ANA_FILE, 'Build\\myText.ana',\
    "The path and name of the file holding\nthe intermediary text in STAMP format."],\

   ["output_syn_file", "Target Output Synthesis File", "output_syn_filename", "syn_file_button", FILE, object, object, object, loadFile, ReadConfig.TARGET_SYNTHESIS_FILE, 'Output\\myText.syn',\
    "The path and name of the file holding\nthe intermediary synthesized file."],\

   ["transfer_result_file", "Target Transfer Results File", "transfer_result_filename", "transfer_result_file_button", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RESULTS_FILE, 'Output\\target_text.aper', \
    "The path and name of the file which holds the text contents\nafter going through the transfer process."],\

   ["source_complex_types", "Source Complex Form Types", "choose_source_compex_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_COMPLEX_TYPES, '',\
    "One or more complex types from the source FLEx project.\nThese types will be treated as a lexical unit in FLExTrans and whenever\nthe components that make up this type of complex form are found sequentially\nin the source text, they will be converted to one lexical unit."],\

   ["bilingual_dictionary_output_file", "Bilingual Dictionary Output File", "bilingual_dictionary_output_filename", "bi_dictionary_outfile_button", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICTIONARY_FILE, 'Output\\target_text.aper',\
    "The path and name of the file which holds the bilingual lexicon."],\

   ["bilingual_dictionary_replace_file", "Bilingual Dictionary Replacement File", "bilingual_dictionary_replace_filename", "bi_dictionary_replacefile_button", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, 'Output\\target_text.aper', \
    "The path and name of the file which holds replacement\nentry pairs for the bilingual lexicon."],\

   ["taget_affix_gloss_list_file", "The path and name of the file which holds the text contents\nafter going through the transfer process.", "taget_affix_gloss_list_filename", "target_affix_list_button", FILE, object, object, object, loadFile, ReadConfig.TARGET_AFFIX_GLOSS_FILE, 'Output\\target_text.aper', \
    "The ancillary file that hold a list of affix\nglosses from the target FLEx project."],\

   ["inflection_first_element", "Target Complex Form Types\nwith inflection on 1st Element", "choose_inflection_first_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_1ST, '',\
    "One or more complex types from the target FLEx project.\nThese types, when occurring in the text file to be synthesized,\nwill be broken down into their constituent entries. Use this property\nfor the types that have inflection on the first element of the complex form."],\

   ["inflection_second_element", "Target Complex Form Types\nwith inflection on 2nd Element", "choose_inflection_second_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_2ND, '',\
    "Same as above. Use this property for the types that have inflection\non the second element of the complex form."],\

   ["target_morpheme_types", "Target Morpheme Types\nCounted As Roots", "choose_source_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadTargetMorphemeTypes, ReadConfig.TARGET_MORPHNAMES, '',\
    "Morpheme types in the target FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."],\

   ["source_morpheme_types", "Source Morpheme Types\nCounted As Roots", "choose_target_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceMorphemeTypes, ReadConfig.SOURCE_MORPHNAMES, '',\
    "Morpheme types in the source FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."],\

   ["source_discontiguous_complex", "Source Discontiguous Complex Form Types", "choose_source_discontiguous_compex", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_DISCONTIG_TYPES, '',\
    "One or more complex types from the source FLEx project.\nThese types will allow one intervening word between the first\nand second words of the complex type, yet will still be treated\nas a lexical unit."],\

   ["skipped_source_words", "Source Skipped Word Grammatical\nCategories for Discontigous Complex Forms", "choose_skipped_source_words", "", CHECK_COMBO_BOX, object, object, object, loadSourceCategories, ReadConfig.SOURCE_DISCONTIG_SKIPPED, '',\
    "One or more grammatical categories that can intervene in the above complex types."],\

   ["treetran_output_file", "Analyzed Text TreeTran Output File", "treetran_output_filename", "a_treetran_outfile_button", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, 'Output\\target_text.aper', \
    "The path and name of the file that holds the output from TreeTran."],\

   ["treetran_insert_words_file", "Target Transfer Results File", "treetran_insert_words_filename", "treetran_insert_words_button", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_INSERT_WORDS_FILE, 'Output\\target_text.aper', \
    "The path and name of the file that has a list of\nwords that can be inserted with a TreeTran rule."],\

   ["transfer_rules_file", "Transfer Rules File", "transfer_rules_filename", "transfer_rules_button", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE, 'Output\\target_text.aper', \
    "The path and name of the file containing the transfer rules."],\

   ["testbed_file", "Testbed File", "testbed_filename", "testbed_button", FILE, object, object, object, loadFile, ReadConfig.TESTBED_FILE, 'Output\\target_text.aper', \
    "The path and name of the testbed file."],\

   ["testbed_result_file", "Testbed Results File", "testbed_result_filename", "testbed_result_button", FILE, object, object, object, loadFile, ReadConfig.TESTBED_RESULTS_FILE, 'Output\\target_text.aper', \
    "The path and name of the testbed results file"],\

   ["category_abbreviation_pairs", "Category Abbreviation Pairs", "category_abbreviation_one", "category_abbreviation_two", SIDE_BY_SIDE_COMBO_BOX, object, object, object, loadCategorySubLists, ReadConfig.CATEGORY_ABBREV_SUB_LIST, 'Target Equivalent',\
    "One or more pairs of grammatical categories where the first category\nis the “from” category in the source FLEx project and the second category\nis the “to” category in the target FLEx project. Use the abbreviations of\nthe FLEx categories. The substitution happens in the bilingual lexicon."],\
   
   ["cleanup_target_words", "Cleanup Unknown Target Words", "cleanup_yes", "cleanup_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CLEANUP_UNKNOWN_WORDS, 'Output\\target_text.aper', \
    "Indicates if the system should remove preceding @ signs\nand numbers in the form N.N following words in the target text."],\

   ["sentence_punctuation", "Sentence Punctuation", "punctuation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SENTENCE_PUNCTUATION, 'Output\\target_text.aper', \
    "A list of punctuation that ends a sentence.\nIn transfer rules you can check for the end of a sentence."]

              ]

# ----------------------------------------------------------------
# The main processing function
if __name__ == '__main__':
    FlexToolsModule.Help()
