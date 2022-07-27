#
#   Settings GUI
#   Lærke Roager Christensen
#   3/28/22
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
        FTM_Version: "3.5.6",
        FTM_ModifiesDB: False,
        FTM_Synopsis: "Change FLExTrans settings.",
        FTM_Help: "",
        FTM_Description:
            """
Change FLExTrans settings. If you want to change the filename for one of the settings,
type the new name in the text box.             
            """}

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

COMBO_BOX = "combobox"
SIDE_BY_SIDE_COMBO_BOX = "side by side"
CHECK_COMBO_BOX = "checkable_combobox"
YES_NO = "yes no"
TEXT_BOX = "textbox"
FILE = "file"
FOLDER = "folder"

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

def loadYesNo(widget, widget2, wind, settingName):            

    yesNo = wind.read(settingName)
    
    if yesNo == 'y':
        
        widget.setChecked(True)
    else:
        widget2.setChecked(True)

def loadTextBox(widget, wind, settingName):            

    text = wind.read(settingName)
    
    if text:
        
        widget.setText(text)

def loadFile(widget, wind, settingName):            

    path = wind.read(settingName)
    
    if path:

        set_paths(widget, path)

def make_open_file(wind, myWidgInfo):
    
    # create a new function that will call do_browse with the given parameters
    def open_file():
        
        do_browse(wind, myWidgInfo)
        wind.set_modified_flag()
        
    return open_file
    
    do_browse(wind, myWidgInfo)
    
def make_open_folder(wind, myWidgInfo):
    
    # create a new function that will call do_browse with the given parameters
    def open_folder():
        
        do_folder_browse(wind, myWidgInfo)
        wind.set_modified_flag()
        
    return open_folder
    
    do_browse(wind, myWidgInfo)
    
def do_browse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = os.path.dirname(wind.read(myWidgInfo[CONFIG_NAME]))
    
    if not os.path.isdir(startDir):
        
        startDir = ""
                   
    filename, _ = QFileDialog.getOpenFileName(wind, "Select file", startDir, "(*.*)")
    
    if filename:
        
        set_paths(myWidgInfo[WIDGET1_OBJ], filename)

def do_folder_browse(wind, myWidgInfo):

    # if folder exists for the current setting, use it. set the starting directory for the open dialog 
    startDir = wind.read(myWidgInfo[CONFIG_NAME])
    
    if not os.path.isdir(startDir):
        
        startDir = ""
                   
    dirName = QFileDialog.getExistingDirectory(wind, "Select Folder", startDir, options=QFileDialog.ShowDirsOnly)
    
    if dirName:
        
        set_paths(myWidgInfo[WIDGET1_OBJ], dirName)

def set_paths(widget, path):
    
    # start the rel path relative to the project folder which is the parent of the config folder
    startPath = os.path.dirname(os.path.dirname(CONFIG_PATH))
    widget.setText(os.path.relpath(path, startPath))
    widget.setToolTip(os.path.relpath(path, startPath))
    
class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 756)

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
        self.scrollArea.setMinimumSize(QtCore.QSize(750, 650))
        self.scrollArea.setMaximumSize(QtCore.QSize(750, 650))

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
        self.gridLayout.addWidget(self.scrollArea, 0, 2, 1, 1)

        self.apply_button = QtWidgets.QPushButton(self.centralwidget)
        self.apply_button.setObjectName("apply_button")
        #self.apply_button.setMaximumWidth(60)
        self.gridLayout.addWidget(self.apply_button, 1, 2, 1, 1)

        # Set up for the fields in the config file
        # They are placed in the order according to the widgetList
        # AddWidget function takes 5 parameters.
        # addWidget(Object, row, column, row-span, column-span)
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            newObj = QtWidgets.QLabel(self.scrollAreaWidgetContents)
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
                
                # Create a button group so these two radio buttons can be distinct from any subsequent ones
                buttonGroup=QtWidgets.QButtonGroup(self.scrollAreaWidgetContents)
                
                # Add the button to the button group
                buttonGroup.addButton(newObj)
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 1)
                widgInfo[WIDGET1_OBJ] = newObj
            
                # No radio button - checked
                newObj = QtWidgets.QRadioButton(self.scrollAreaWidgetContents)
                newObj.setObjectName(widgInfo[WIDGET2_OBJ_NAME])

                # Add the button to the button group
                buttonGroup.addButton(newObj)
                self.gridLayout_2.addWidget(newObj, i+1, 2, 1, 1)
                widgInfo[WIDGET2_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                newObj = CheckableComboBox()
                newObj.setObjectName(widgInfo[WIDGET1_OBJ_NAME])
                newObj.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
                self.gridLayout_2.addWidget(newObj, i+1, 1, 1, 3)
                widgInfo[WIDGET1_OBJ] = newObj
            
            elif widgInfo[WIDGET_TYPE] in [FILE, FOLDER]:
                
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

class Main(QMainWindow):

    def __init__(self, configMap, report, targetDB, DB):
        QMainWindow.__init__(self)

        self.report = report
        self.configMap = configMap
        self.targetDB = targetDB
        self.DB = DB

        self.setWindowIcon(QtGui.QIcon('FLExTransWindowIcon.ico'))
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load the widgets with data        
        self.init_load()

        self.modified = False
        
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), ReadConfig.CONFIG_FILE)
        
        self.config = myPath
        
        # Get the project folder which is the parent of the config path
        myPath = os.path.dirname(os.path.dirname(CONFIG_PATH))
        
        self.projFolder = myPath
        
        # Loop through all settings
        for i in range(0, len(widgetList)):
            
            widgInfo = widgetList[i]
            
            # Connect browse buttons to functions
            if widgInfo[WIDGET_TYPE] == FILE:
                
                widgInfo[WIDGET2_OBJ].clicked.connect(make_open_file(self, widgInfo))
                widgInfo[WIDGET1_OBJ].textChanged.connect(self.set_modified_flag)

            elif widgInfo[WIDGET_TYPE] == FOLDER:
                
                widgInfo[WIDGET2_OBJ].clicked.connect(make_open_folder(self, widgInfo))
                widgInfo[WIDGET1_OBJ].textChanged.connect(self.set_modified_flag)

            # Connect all widgets to a function the sets the modified flag
            # This is so that any clicking on objects will prompt the user to save on exit
            elif widgInfo[WIDGET_TYPE] == COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(self.set_modified_flag)
                
            elif widgInfo[WIDGET_TYPE] == CHECK_COMBO_BOX:
                
                # TODO: this doesn't do anything. Need to figure out what signal we can connect to to see if this widget has changed data
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(self.set_modified_flag)
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                widgInfo[WIDGET1_OBJ].currentIndexChanged.connect(self.set_modified_flag)
                widgInfo[WIDGET2_OBJ].currentIndexChanged.connect(self.set_modified_flag)
                
            elif widgInfo[WIDGET_TYPE] == TEXT_BOX:
                
                widgInfo[WIDGET1_OBJ].textChanged.connect(self.set_modified_flag)
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                widgInfo[WIDGET1_OBJ].toggled.connect(self.set_modified_flag)
                
        # Apply button
        self.ui.apply_button.clicked.connect(self.save)

    def set_modified_flag(self):
        
        self.modified = True
        
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
            
            if widgInfo[WIDGET_TYPE] in [SIDE_BY_SIDE_COMBO_BOX, YES_NO]:
                
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
                
                outStr = widgInfo[CONFIG_NAME]+'='+self.optional_mul(widgInfo[WIDGET1_OBJ].currentData())
                
            elif widgInfo[WIDGET_TYPE] == SIDE_BY_SIDE_COMBO_BOX:
                
                valStr = widgInfo[WIDGET1_OBJ].currentText()+','+widgInfo[WIDGET2_OBJ].currentText()
                
                # If the user selected ..., set the value to blank
                if '...' in valStr:
                    
                    valStr = ''
                    
                outStr = widgInfo[CONFIG_NAME]+'='+valStr
                
            elif widgInfo[WIDGET_TYPE] in [FILE, FOLDER, TEXT_BOX]:
                
                outStr = widgInfo[CONFIG_NAME]+'='+widgInfo[WIDGET1_OBJ].text()
                
            elif widgInfo[WIDGET_TYPE] == YES_NO:
                
                if widgInfo[WIDGET1_OBJ].isChecked():
                    
                    selected='y'
                else:
                    selected='n'
            
                outStr = widgInfo[CONFIG_NAME]+'='+selected
                
            f.write(outStr+'\n')
            
        f.close()
        
        self.modified = False
        
        QMessageBox.information(self, 'Save Settings', 'Settings saved.')

    def optional_mul(self, array):
        write = ''
        if array:
            for text in array:
                write += text + ","
        return write

def MainFunction(DB, report, modify=True): 
    # Read the configuration file which we assume is in the current directory.

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        report.Error('Error reading configuration file.')
        return

    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenProject(targetProj, False)
    except:
        report.Error('Failed to open the target database.')
        raise

    # Show the window
    app = QApplication(sys.argv)

    window = Main(configMap, report, TargetDB, DB,) #sourceDB

    window.show()

    app.exec_()
    
    # Prompt the user to save changes, if needed
    if window.modified == True:
        
        if QMessageBox.question(window, 'Save Changes', "Do you want to save your changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:

            window.save()
    
    TargetDB.CloseProject()


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
# If a new type of widget is needed, more work needed to add to each part of the code where the widgetList is iterated

widgetList = [
   # label text          obj1 name       obj2 name  type     label   obj1    obj2    load function       config key name            
   ["Source Text Name", "choose_source_text", "", COMBO_BOX, object, object, object, loadSourceTextList, ReadConfig.SOURCE_TEXT_NAME,\
    # tooltip text
    "The name of the text (in the first analysis writing system)\nin the source FLEx project to be translated."],\
   
   ["Source Custom Field for Entry Link", "choose_entry_link", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY,\
    "The name of the custom field in the source FLEx project that\nholds the link information to entries in the target FLEx project."],\
   
   ["Source Custom Field for Sense Number", "chose_sense_number", "", COMBO_BOX, object, object, object, loadCustomEntry, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM,\
    "The name of the custom field in the source FLEx project\nthat holds the sense number of the target entry."],\

   ["Target Project", "chose_target_project", "", COMBO_BOX, object, object, object, loadTargetProjects, ReadConfig.TARGET_PROJECT,\
    "The name of the target FLEx project."],\

   ["Source Morpheme Types\nCounted As Roots", "choose_target_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceMorphemeTypes, ReadConfig.SOURCE_MORPHNAMES, '',\
    "Morpheme types in the source FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."],\

   ["Target Morpheme Types\nCounted As Roots", "choose_source_morpheme_types", "", CHECK_COMBO_BOX, object, object, object, loadTargetMorphemeTypes, ReadConfig.TARGET_MORPHNAMES, '',\
    "Morpheme types in the target FLEx project that are to be considered\nas some kind of root. In other words, non-affixes and non-clitics."],\

   ["Source Complex Form Types", "choose_source_compex_types", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_COMPLEX_TYPES, '',\
    "One or more complex types from the source FLEx project.\nThese types will be treated as a lexical unit in FLExTrans and whenever\nthe components that make up this type of complex form are found sequentially\nin the source text, they will be converted to one lexical unit."],\

   ["Target Complex Form Types\nwith inflection on 1st Element", "choose_inflection_first_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_1ST, '',\
    "One or more complex types from the target FLEx project.\nThese types, when occurring in the text file to be synthesized,\nwill be broken down into their constituent entries. Use this property\nfor the types that have inflection on the first element of the complex form."],\

   ["Target Complex Form Types\nwith inflection on 2nd Element", "choose_inflection_second_element", "", CHECK_COMBO_BOX, object, object, object, loadTargetComplexFormTypes, ReadConfig.TARGET_FORMS_INFLECTION_2ND, '',\
    "Same as above. Use this property for the types that have inflection\non the second element of the complex form."],\

   ["Sentence Punctuation", "punctuation", "", TEXT_BOX, object, object, object, loadTextBox, ReadConfig.SENTENCE_PUNCTUATION, \
    "A list of punctuation that ends a sentence.\nIn transfer rules you can check for the end of a sentence."],\

   ["Source Discontiguous Complex Form Types", "choose_source_discontiguous_compex", "", CHECK_COMBO_BOX, object, object, object, loadSourceComplexFormTypes, ReadConfig.SOURCE_DISCONTIG_TYPES, '',\
    "One or more complex types from the source FLEx project.\nThese types will allow one intervening word between the first\nand second words of the complex type, yet will still be treated\nas a lexical unit."],\

   ["Source Skipped Word Grammatical\nCategories for Discontiguous Complex Forms", "choose_skipped_source_words", "", CHECK_COMBO_BOX, object, object, object, loadSourceCategories, ReadConfig.SOURCE_DISCONTIG_SKIPPED, '',\
    "One or more grammatical categories that can intervene in the above complex types."],\

   ["Cleanup Unknown Target Words?", "cleanup_yes", "cleanup_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CLEANUP_UNKNOWN_WORDS, \
    "Indicates if the system should remove preceding @ signs\nand numbers in the form N.N following words in the target text."],\

   ["Cache data for faster processing?", "cache_yes", "cache_no", YES_NO, object, object, object, loadYesNo, ReadConfig.CACHE_DATA, \
    "Indicates if the system should avoid regenerating data that hasn't changed.\nUse the CleanFiles module to force the regeneration of data."],\

   ["Category Abbreviation Pairs", "category_abbreviation_one", "category_abbreviation_two", SIDE_BY_SIDE_COMBO_BOX, object, object, object, loadCategorySubLists, ReadConfig.CATEGORY_ABBREV_SUB_LIST,\
    "One or more pairs of grammatical categories where the first category\nis the “from” category in the source FLEx project and the second category\nis the “to” category in the target FLEx project. Use the abbreviations of\nthe FLEx categories. The substitution happens in the bilingual lexicon."],\
   
   ["Transfer Rules File", "transfer_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RULES_FILE, \
    "The path and name of the file containing the transfer rules."],\

   ["Analyzed Text Output File", "output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TEXT_FILE,\
    "The path and name of the file which holds\nthe extracted source text."],\

   ["Bilingual Dictionary Output File", "bilingual_dictionary_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICTIONARY_FILE,\
    "The path and name of the file which holds the bilingual lexicon."],\

   ["Bilingual Dictionary Replacement File", "bilingual_dictionary_replace_filename", "", FILE, object, object, object, loadFile, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, \
    "The path and name of the file which holds replacement\nentry pairs for the bilingual lexicon."],\

   ["Target Transfer Results File", "transfer_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TRANSFER_RESULTS_FILE, \
    "The path and name of the file which holds the text contents\nafter going through the transfer process."],\

   ["Target Affix Gloss List File", "taget_affix_gloss_list_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_AFFIX_GLOSS_FILE, \
    "The ancillary file that hold a list of affix\nglosses from the target FLEx project."],\

   ["Target Output ANA File", "output_ANA_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_ANA_FILE,\
    "The path and name of the file holding\nthe intermediary text in STAMP format."],\

   ["Target Lexicon Files Folder", "lexicon_files_folder", "", FOLDER, object, object, object, loadFile, ReadConfig.TARGET_LEXICON_FILES_FOLDER, \
    "The path where lexicon files and other STAMP files are created"],\

   ["Target Output Synthesis File", "output_syn_filename", "", FILE, object, object, object, loadFile, ReadConfig.TARGET_SYNTHESIS_FILE,\
    "The path and name of the file holding\nthe intermediary synthesized file."],\

   ["Testbed File", "testbed_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_FILE, \
    "The path and name of the testbed file."],\

   ["Testbed Results File", "testbed_result_filename", "", FILE, object, object, object, loadFile, ReadConfig.TESTBED_RESULTS_FILE, \
    "The path and name of the testbed results file"],\

   ["TreeTran Rules File", "treetran_rules_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_RULES_FILE, \
    "The path and name of the TreeTran rules file"],\

   ["Analyzed Text TreeTran Output File", "treetran_output_filename", "", FILE, object, object, object, loadFile, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, \
    "The path and name of the file that holds the output from TreeTran."],\

   ["TreeTran Insert Words File", "treetran_insert_words_filename", "", FILE, object, object, object, loadFile, ReadConfig.TREETRAN_INSERT_WORDS_FILE, \
    "The path and name of the file that has a list of\nwords that can be inserted with a TreeTran rule."]
              ]

# ----------------------------------------------------------------
# The main processing function
if __name__ == '__main__':
    FlexToolsModule.Help()
