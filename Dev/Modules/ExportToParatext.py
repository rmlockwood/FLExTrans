#
#   ExportToParatext
#
#   Ron Lockwood
#   SIL International
#   5/3/22
#
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Put the export logic in a separate function. So it can be called from other modules.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.6 - 3/5/25 - Ron Lockwood
#   Fixes #909. Error messages when files don't exist.
#
#   Version 3.12.5 - 3/4/25 - Ron Lockwood
#    New module name.
#
#   Version 3.12.4 - 1/15/25 - Ron Lockwood
#    Export from FLEx to Paratext, optionally across cluster projects.
#
#   Version 3.12.3 - 12/31/24 - Ron Lockwood
#    Fixes #830. Have do_export build the full path to the book.
#
#   Version 3.12.2 - 12/26/24 - Ron Lockwood
#    Move some widget initiation into Chap Selection file.
#
#   Version 3.12.1 - 11/27/24 - Ron Lockwood
#    Fixes #815. If an intro section exists above chapter 1, include it in the export.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.5 - 8/2/24 - Ron Lockwood
#    Don't need to remove paragraph marks anymore.
#
#   Version 3.10.1 - 3/19/24 - Ron Lockwood
#    Fixes #566. Allow the user to create one text per chapter when importing.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8 - 3/10/23 - Ron Lockwood
#    Handle when the synthesis file is missing.
#
#   Version 3.7.4 - 2/28/23 - Ron Lockwood
#    Remove section marks after verses and quote markers
#
#   Version 3.7.3 - 1/30/23 - Ron Lockwood
#    Restructured to put common init and exit code into ChapterSelection.py
#    Store export project and import project as separate settings.
#
#   Version 3.7.2 - 1/25/23 - Ron Lockwood
#    Fixes #173 and #190. Shorten window and move up OK and Cancel.
#    Also allow - Copy ... after the source text title.
#
#   earlier version history removed on 1/14/25
#
#   Export chapters from FLExTrans to Paratext. The user is prompted which Paratext 
#   project to use and the book, from and to chapter come from the current SourceName 
#   in the config file. The text from the TargetOutputSynthesisFile is used to populate
#   the Paratext book and chapter(s). 
#
#

import os
import re
import sys

from SIL.LCModel import * # type: ignore                                                  
from flextoolslib import *                                                 

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication

import ReadConfig
import FTPaths
from ParatextChapSelectionDlg import Ui_MainWindow
import ChapterSelection

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export FLExTrans Draft to Paratext",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Export the draft that has been translated with FLExTrans to Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
After chapters have been synthesized with the Synthesize Text module, the draft resides in the file specified
by the setting 'Target Output Synthesis File' (typically called 'target_text-syn.txt'). This module
takes the draft in this file and copies the chapters into Paratext to the project specified.""" }
                 
#----------------------------------------------------------------
# The main processing function

class Main(QMainWindow):

    def __init__(self, bookAbbrev, fromChap, toChap, clusterProjects):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.clusterProjects = clusterProjects
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.setWindowTitle("Export Chapters to Paratext")

        # Get stuff from a paratext import/export settings file and set dialog controls as appropriate
        ChapterSelection.InitControls(self, export=True)

        # Set the interface according to what was passed in 
        # This overrides values set in the init controls call above.
        self.ui.fromChapterSpinBox.setValue(fromChap)
        self.ui.fromChapterSpinBox.setEnabled(False)
        
        self.ui.toChapterSpinBox.setValue(toChap)
        self.ui.toChapterSpinBox.setEnabled(False)
        
        self.ui.bookAbbrevLineEdit.setText(bookAbbrev)
        self.ui.bookAbbrevLineEdit.setEnabled(False)
        
    def CancelClicked(self):
        self.retVal = False
        self.close()
        
    def OKClicked(self):

        ChapterSelection.doOKbuttonValidation(self, export=True)

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

def doExportToParatext(DB, configMap, report):

    # Find the desired text
    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceText:
        return None
    
    infoMap = {'bookAbbrev': '', 'fromChap': 0, 'toChap': 0}
    
    # Parse it into book and chapters
    if parseSourceTextName(report, sourceText, infoMap) == False: # error occurred
        return None 
    
    # Get the cluster projects
    clusterProjects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report, giveError=False)
    if not clusterProjects:
        clusterProjects = []
        
    # Show the window
    app = QApplication(sys.argv)

    window = Main(infoMap['bookAbbrev'], infoMap['fromChap'], infoMap['toChap'], clusterProjects)
    
    window.show()
    
    app.exec_()
    
    if window.retVal == True:
        
        # Check that we have a synthesized file
        synFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
        if not synFile:
            return None
        
        # Read in the syn. file chapters
        try:
            f = open(synFile, 'r', encoding='utf-8')
        except:
            report.Error(f'Could not find the synthesis file. Have you run the Synthesize Text module? Missing file: {synFile}.')
            return None
            
        synFileContents = f.read()
        f.close()
        
        ChapterSelection.doExport(synFileContents, report, window.chapSel, window)

        return 1
    else:
        report.Warning(f'Export cancelled.')
        return None

def MainFunction(DB, report, modify):
    
    # Read the configuration file 
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    doExportToParatext(DB, configMap, report)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
