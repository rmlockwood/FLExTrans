#
#   ExportFlexToParatext
#
#   Ron Lockwood
#   SIL International
#   1/20/2025
#
#   Version 3.13.2 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 4/25/25 - Ron Lockwood
#    Fixes #971. Change the window title based on which projects are selected for export.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.3 - 3/4/25 - Ron Lockwood
#    New module name.
#
#   Version 3.12.2 - 1/15/25 - Ron Lockwood
#    Export from the target DB as the default. Also recognize texts that have - Copy ...
#    at the end.
#
#   Version 3.12.1 - 1/15/25 - Ron Lockwood
#    Export from FLEx to Paratext, optionally across cluster projects.
#
#   Version 3.12 - 1/10/25 - Ron Lockwood
#    Initial version.
#
#   Export texts that represent on or more scripture chapters from FLEx to Paratext. 
#   The text comes from the baseline text. The user is prompted which Paratext 
#   project to use. The book, from and to chapter come from the text(s) selected. 
#
#

import os
import re
import sys

import ClusterUtils
from SIL.LCModel import * # type: ignore                                                  
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore        

from flextoolslib import *                                                 
from SIL.LCModel import ( # type: ignore
    IStTxtPara, 
)

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox
from PyQt5.QtCore import QCoreApplication, QTranslator

import Mixpanel
import ReadConfig
import FTPaths
import Utils
from ParatextChapSelectionDlg import Ui_ParatextChapSelectionWindow
import ChapterSelection

# Define _translate for convenience
_translate = QCoreApplication.translate

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['ExportFlexToParatext'], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Testbed', 'TestbedValidator', 'Mixpanel', 'ParatextChapSelectionDlg'] 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export Text from Target FLEx to Paratext",
        FTM_Version    : "3.13.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("ExportFlexToParatext", "Export one or more texts that contain scripture from the target FLEx project to Paratext."),
        FTM_Help       : "",
        FTM_Description: _translate("ExportFlexToParatext",
"""Export one or more texts that contain scripture from the target FLEx project to Paratext. The list of possible texts to choose
from will be filtered according to texts that have a scripture book name or abbreviation in the title plus
a chapter number or a range of chapter numbers.""")}

app.quit()
del app

#----------------------------------------------------------------
# The main processing function

class Main(QMainWindow):

    def __init__(self, targetDB, clusterProjects, scriptureTitles):
        QMainWindow.__init__(self)

        self.ui = Ui_ParatextChapSelectionWindow()
        self.targetDB = targetDB
        self.clusterProjects = clusterProjects
        self.scriptureTitles = scriptureTitles
        self.selectedTitles = []
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setWindowTitle(_translate("ExportFlexToParatext", "Export from {projectName} to Paratext").format(projectName=targetDB.ProjectName()))

        header1TextStr = _translate("ExportFlexToParatext", "FLEx project name")
        header2TextStr = _translate("ExportFlexToParatext", "Paratext project abbrev.")
        self.ptxProjs = ChapterSelection.getParatextProjects()

        # Set the top two widgets that need to be disabled
        self.topWidget1 = self.ui.ptxProjAbbrevLineEdit
        self.topWidget2 = self.ui.label

        # Create all the possible widgets we need for all the cluster projects
        ClusterUtils.initClusterWidgets(self, QComboBox, self.ui.centralwidget, header1TextStr, header2TextStr, 100, self.fillPtxCombo)

        reduction = ChapterSelection.EXP_SHRINK_WINDOW_PIXELS - ChapterSelection.FROM_FLEX_EXP_PIXELS
        self.originalMainWinHeight = ClusterUtils.IMP_EXP_WINDOW_HEIGHT - reduction
        self.originalOKyPos = self.ui.OKButton.y() - reduction

        # Get stuff from a paratext import/export settings file and set dialog controls as appropriate
        ChapterSelection.InitControls(self, export=True, fromFLEx=True)
        
    def fillPtxCombo(self, comboWidget):

        # Fill the combo box
        comboWidget.addItems(['...'] + self.ptxProjs)
    
    def clusterSelectionChanged(self):

        # Set the window title based on the selected project(s)
        if len(selProjs := self.ui.clusterProjectsComboBox.currentData()) == 1:

            self.setWindowTitle(f"Export from {selProjs[0]} to Paratext")

        elif len(selProjs) > 1:

            self.setWindowTitle(f"Export from multiple FLEx projects to Paratext")
        
        # Otherwise, use the default title
        else:
            self.setWindowTitle(f"Export from {self.targetDB.ProjectName()} to Paratext")

        ClusterUtils.showClusterWidgets(self)

    def CancelClicked(self):
        self.retVal = False
        self.close()
        
    def OKClicked(self):

        ChapterSelection.doOKbuttonValidation(self, export=True, checkBookAbbrev=False, checkBookPath=True, fromFLEx=True)

        self.selectedTitles = self.ui.scriptureTextsComboBox.currentData()

    def titlesSelectionChanged(self, index):
        
        # If the user chooses, select whole books at a time (all chapters that match the book)
        if self.ui.selectAllChaptersCheckbox.isChecked():

            title = self.ui.scriptureTextsComboBox.itemText(index)

            # If the click on a checkbox made in checked, it will now be part of the current data
            if title in self.ui.scriptureTextsComboBox.currentData():

                checkFunc = self.ui.scriptureTextsComboBox.check
            else:
                checkFunc = self.ui.scriptureTextsComboBox.unCheck
            
            match = ChapterSelection.bookChapterPattern.match(title)

            if not match:
                return
            
            book = match.group('book')

            # select/unselect all titles that match this book
            for index in range(self.ui.scriptureTextsComboBox.count()): 
                
                if re.match(book, title := self.ui.scriptureTextsComboBox.itemText(index)):

                    checkFunc(title)

def exportAllSelectedTitles(myDB, report, window, proj, ptxAbbrev=None):

    matchingContentsObjList = []
    textTitles = Utils.getSourceTextList(myDB, matchingContentsObjList)

    for title in window.selectedTitles:

        try:
            contents = matchingContentsObjList[textTitles.index(title)]

        except ValueError:
            report.Error(_translate("ExportFlexToParatext", "{title} not found in the {proj} project.").format(title=title, proj=proj))
            continue

        textStr = makeTextStr(contents)

        ## Get the book abbreviation
        # First get the book string at the start of the title. It could be full name or abbrev.
        matchObj = ChapterSelection.bookChapterPattern.match(title)
        bookStr = matchObj.group('book')
        bookAbbrev = ''

        # if we have an abbrev. already, done
        if bookStr in ChapterSelection.bookMap:
                    
            bookAbbrev = bookStr 

        # Otherwise find the abbreviation for the full name
        else:
            for key, val in ChapterSelection.bookMap.items():
                
                if bookStr == val:
                    bookAbbrev = key
                    break
        
        window.chapSel.bookAbbrev = bookAbbrev
        
        if ptxAbbrev:

            window.chapSel.exportProjectAbbrev = ptxAbbrev

        if not ChapterSelection.doExport(textStr, report, window.chapSel, window):
           
            report.Error(_translate("ExportFlexToParatext", "There was a problem exporting {title} from the {proj} project to {exportProjectAbbrev}.").format(
                title=title, proj=proj, exportProjectAbbrev=window.chapSel.exportProjectAbbrev)) 
            break

def makeTextStr(contentsObj):

    paraList = []

    for p in contentsObj.ParagraphsOS:

        if para := ITsString(IStTxtPara(p).Contents).Text:

            paraList.append(para)

    return '\n'.join(paraList)

def MainFunction(DB, report, modify):
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + ['ExportFlexToParatext'], 
                           translators, loadBase=True)

    # Read the configuration file 
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the cluster projects
    clusterProjects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report, giveError=False)
    if not clusterProjects:
        clusterProjects = []
    else:
        # Remove blank ones
        clusterProjects = [x for x in clusterProjects if x]

    # Open the Target DB
    targetDB = Utils.openTargetProject(configMap, report)

    # Get a list of the text titles
    textTitles = Utils.getSourceTextList(targetDB)

    # Filter these down to the ones that match a scripture book name or abbreviation and a chapter number
    scriptureTitles = ChapterSelection.getScriptureText(report, textTitles)
    
    window = Main(targetDB, clusterProjects, scriptureTitles)
    window.show()
    app.exec_()
    
    if window.retVal == True:
        
        if window.chapSel.clusterProjects and len(window.chapSel.clusterProjects) > 0:

            for i, proj in enumerate(window.chapSel.clusterProjects):

                if window.chapSel.ptxProjList[i] == '...':
                    continue

                # Open the project (if it's not the main project or the target project)
                if proj == DB.ProjectName():

                    myDB = DB

                elif proj == targetDB.ProjectName():

                    myDB = targetDB
                else:
                    myDB = Utils.openProject(report, proj)

                report.Blank()
                report.Info(_translate("ExportFlexToParatext", "Exporting from the {proj} project...").format(proj=proj))

                exportAllSelectedTitles(myDB, report, window, proj, window.chapSel.ptxProjList[i])
                
                # Close the project (if not the main)
                if proj != DB.ProjectName() and proj != targetDB.ProjectName():

                    myDB.CloseProject()
        else:
            exportAllSelectedTitles(targetDB, report, window, targetDB.ProjectName())

    targetDB.CloseProject()

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
