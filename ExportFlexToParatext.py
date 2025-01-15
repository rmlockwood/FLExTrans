#
#   ExportFlexToParatext
#
#   Ron Lockwood
#   SIL International
#   1/20/2025
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

import ReadConfig
import FTPaths
import Utils
from ParatextChapSelectionDlg import Ui_MainWindow
import ChapterSelection

#----------------------------------------------------------------
# Configurables:

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export FLEx Text to Paratext",
        FTM_Version    : "3.12.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Export one or more texts in FLEx that contains scripture to Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
Export one or more texts in FLEx that contains scripture to Paratext. The list of possible texts to choose
from will be filtered according to texts that have a scripture book name or abbreviation in the title plus
a chapter number or a range of chapter numbers.""" }
                 
#----------------------------------------------------------------
# The main processing function

class Main(QMainWindow):

    def __init__(self, clusterProjects, scriptureTitles):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.clusterProjects = clusterProjects
        self.scriptureTitles = scriptureTitles
        self.selectedTitles = []
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setWindowTitle("Export Chapters from FLEx to Paratext")

        header1TextStr = "FLEx project name"
        header2TextStr = "Paratext project abbrev."
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

def parseSourceTextName(report, sourceText, infoMap): 
    
    # Remove the - Copy ... so that a title like Ruth 01 - Copy (2) is still allowed
    sourceText = re.sub(r' - Copy.*', '', sourceText)
    
    stdError = f'The text name "{sourceText}" is invalid it should be of the form GEN 01 or Genesis 23-38'
    
    # should have two main elements, book name (which can have spaces) and chapter number
    myList = sourceText.split()
    
    # the book portion will be all except the last one
    bookAbbrev = book = ' '.join(myList[0:-1])
    
    chapters = myList[-1]
    
    # Check first if this is an abbreviation that is in the book map
    if book.upper() not in ChapterSelection.bookMap:
        
        # Now check if this is a full book name that is in the values part of the map (e.g. 'Genesis')
        if book not in ChapterSelection.bookMap.values():
            report.Error(f'The book name or abbreviation {book} is invalid. It should match a Paratext book.')
            return False
        else:
            for key, val in ChapterSelection.bookMap.items():
                
                if book == val:
                    bookAbbrev = key
                    break
    
    if re.search('-', chapters):
        
        bList = chapters.split('-')
        
        if len(bList) != 2:
            report.Error(stdError)
            return False
        
        (fromStr, toStr) = bList
            
        if not fromStr.isdigit() or not toStr.isdigit():
            report.Error(stdError)
            return False
        else:
            fromChap = int(fromStr)
            toChap = int(toStr)
            
            if toChap < fromChap or toChap == 0 or fromChap == 0:
                report.Error(stdError)
                return False
    else:
        if chapters.isdigit() == False:
            
            report.Error(stdError)
            return False
            
        fromChap = toChap = int(chapters)               
                    
    infoMap['bookAbbrev'] = bookAbbrev
    infoMap['fromChap'] = fromChap
    infoMap['toChap'] = toChap
    
    return True
               
def MainFunction(DB, report, modify):
    
    ## Read the SourceName from the config file
    
    # Read the configuration file 
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the cluster projects
    clusterProjects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report, giveError=False)
    if not clusterProjects:
        clusterProjects = []
    else:
        # Remove blank ones
        clusterProjects = [x for x in clusterProjects if x]
        
    

    # Get a list of the text titles
    textTitles = Utils.getSourceTextList(DB)

    # Filter these down to the ones that match a scripture book name or abbreviation and a chapter number
    scriptureTitles = ChapterSelection.getScriptureText(report, textTitles)
    
    # Show the window
    app = QApplication(sys.argv)

    window = Main(clusterProjects, scriptureTitles)
    
    window.show()
    
    app.exec_()
    
    if window.retVal == True:
        
        if window.chapSel.clusterProjects and len(window.chapSel.clusterProjects) > 0:

            for i, proj in enumerate(window.chapSel.clusterProjects):

                if window.chapSel.ptxProjList[i] == '...':
                    continue

                # Open the project (if it's not the main proj)
                if proj == DB.ProjectName():

                    myDB = DB
                else:
                    myDB = Utils.openProject(myDB, proj)

                report.Blank()
                report.Info(f'Exporting from the {proj} project...')
                exportAllSelectedTitles(myDB, report, window, proj, window.chapSel.ptxProjList[i])
                
                # Close the project (if not the main)
                if proj != DB.ProjectName():

                    myDB.CloseProject()
        else:
            exportAllSelectedTitles(DB, report, window, DB.ProjectName())

def exportAllSelectedTitles(myDB, report, window, proj, ptxAbbrev=None):

    matchingContentsObjList = []
    textTitles = Utils.getSourceTextList(myDB, matchingContentsObjList)

    for title in window.selectedTitles:

        try:
            contents = matchingContentsObjList[textTitles.index(title)]

        except ValueError:
            report.Error(f'{title} not found in the {proj} project.')
            continue

        textStr = makeTextStr(contents)

        if ptxAbbrev:

            window.chapSel.exportProjectAbbrev = ptxAbbrev

        if not ChapterSelection.doExport(textStr, report, window.chapSel, window):
           
           report.Error(f'There was a problem exporting {title} from the {proj} project to {window.chapSel.exportProjectAbbrev}.') 


def makeTextStr(contentsObj):

    paraList = []

    for p in contentsObj.ParagraphsOS:

        if para := ITsString(IStTxtPara(p).Contents).Text:

            paraList.append(para)

    return '\n'.join(paraList)
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
