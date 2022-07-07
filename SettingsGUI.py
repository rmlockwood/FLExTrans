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
        # They are placed in the order according to the widgetList
        # AddWidget function takes 5 parameters.
        # addWidget(Object, row, column, row-span, column-span)
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

        self.apply_button.setText(_translate("MainWindow", "Apply"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))

class Main(QMainWindow):

    def __init__(self, configMap, report, targetDB, DB):
        QMainWindow.__init__(self)

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
             
        # Apply button
        self.ui.apply_button.clicked.connect(self.save)
#        self.ui.reset_button.clicked.connect(self.reset)

        self.init_load()

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
            
        # load all the widgets, calling the applicable load function defined widgetList
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            if widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                # pass two widgets
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], widgInfo[WIDGET2_OBJ], self, widgInfo[CONFIG_NAME])

            else:
                
                # Call the load function for this widget, pass in the widget object and this window object
                # Also pass the config file setting name
                widgInfo[LOAD_FUNC](widgInfo[WIDGET1_OBJ], self, widgInfo[CONFIG_NAME])

    def save(self):

        f = open(self.config, "w", encoding='utf-8')
        
        # Write out the config file according to each type
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
