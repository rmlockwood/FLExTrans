#
#   ExportToParatext
#
#   Ron Lockwood
#   SIL International
#   5/3/22
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
#   Version 3.7.1 - 12/25/22 - Ron Lockwood
#    Added RegexFlag before re constants
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 9/3/22 - Ron Lockwood
#    Bump version number.
#
#   Version 3.5.3 - 7/8/22 - Ron Lockwood
#    Set Window Icon to be the FLExTrans Icon
#
#   Version 3.5.2 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5.1 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.5 - 5/3/22 - Ron Lockwood
#    Initial version.
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
from shutil import copyfile

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils

from flextoolslib import *                                                 

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication

import ReadConfig
import FTPaths
from ParatextChapSelectionDlg import Ui_MainWindow
import ChapterSelection

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export Translated Text to Paratext",
        FTM_Version    : "3.12.3",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Export text that has been translated with FLExTrans to Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
After chapters have been translated with FLExTrans, this module will copy the chapters
into Paratext to the project specified.""" }
                 
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
               
def do_export(DB, report, chapSelectObj, configMap, parent):
    
    # Check that we have a synthesized file
    synFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not synFile:
        return
    
    # Read in the syn. file chapters
    try:
        f = open(synFile, 'r', encoding='utf-8')
    except:
        report.Error(f'Could not find the synthesis file. Have you run the Synthesis Module? Missing file: {synFile}.')
        return
        
    synFileContents = f.read()
    f.close()
    
    # Find all the chapter #s
    synChapList = re.findall(r'\\c (\d+)', synFileContents, flags=re.RegexFlag.DOTALL)
    
    # Check that we have chapters in the syn. file
    if len(synChapList) < 1:
        report.Error('No chapters found in the synthesis file.')
        return
    
    # Prompt the user to be sure they want to replace these chapters, preview?
    ret = QMessageBox.question(parent, 'Overwrite chapters', f'Are you sure you want to overwrite {str(len(synChapList))} chapter(s)?', QMessageBox.Yes | QMessageBox.No)
    
    if ret == QMessageBox.No:
        report.Info('Export cancelled.')
        return 
    
    # Create a backup of the paratext file
    bookPath = os.path.join(chapSelectObj.paratextPath, chapSelectObj.projectAbbrev, chapSelectObj.bookAbbrev)
    copyfile(bookPath, bookPath+'.bak')
    
    # Read the Paratext file
    with open(bookPath, encoding='utf-8') as f:
    
        bookContents = f.read()
    
    # Find all the chapter #s
    ptxChapList = re.findall(r'\\c (\d+)', bookContents, flags=re.RegexFlag.DOTALL)
    
    # Split the synthesis contents into chapter chunks
    synContentsList = re.split(r'(\\c \d+)', synFileContents, flags=re.RegexFlag.DOTALL) # gives us [\c 1, \s ..., \c 2, \s ..., ...]
    haveIntro = False

    # Loop through each synthesis chapter and splice it into the paratext chapter contents
    for n in range(1, len(synContentsList), 2): # the zeroth one will be whatever is before the first \c, possibly the empty string
        
        # If we have chapter 1, and before chapter 1 is some intro stuff, add intro portion before chapter 1 marker and text
        if n == 1 and synContentsList[n] == '\\c 1' and re.search(r'\\ip', synContentsList[0]):

            haveIntro = True
            wholeChStr = synContentsList[0] + synContentsList[n] + synContentsList[n+1]
        else:
            wholeChStr = synContentsList[n] + synContentsList[n+1]
        
        # Check the corresponding chapter in the synthesis chapter list
        if synChapList[n//2] in ptxChapList:
            
            # If we have intro stuff to put in chapter 1, start the regex at \mt if it exists.
            if n == 1 and haveIntro:

                begRE = r'(\\mt.+\\c 1|\\c 1)'
            else:
                begRE = r'\\c ' + synChapList[n//2]
            
            # See if this is the last paratext chapter
            if synChapList[n//2] == ptxChapList[-1]:
                
                endRE = r'\s.+'
                replExtra = ''
            else:
                endRE = r'\s.+?\\c' # non-greedy match
                replExtra = '\\c'
        else:
            found = False
            
            # Find the next chapter # in the list
            for i, ptxCh in enumerate(ptxChapList):
                
                if int(synChapList[n//2]) < int(ptxCh):
                    
                    found = True
                    break
            if found:
                
                begRE = r'\\c ' + ptxCh
                replExtra = '\\c ' + ptxCh
                endRE = ''
                
            # No next chapter found, just append
            else: 
                
                bookContents += wholeChStr
                continue
        
        # Escape each backslash
        wholeChStr = re.sub(r'\\', r'\\\\', wholeChStr + replExtra)    
        
        bookContents = re.sub(begRE + endRE, wholeChStr, bookContents, flags=re.RegexFlag.DOTALL)
        
    # Write the ptx file
    f = open(bookPath, 'w', encoding='utf-8')
    f.write(bookContents)
    
    # Close files
    f.close()
    
    # Report how many chapters processed
    report.Info(f'{str(len(synChapList))} chapter(s) exported.')
    
def MainFunction(DB, report, modify):
    
    ## Read the SourceName from the config file
    
    # Read the configuration file 
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Find the desired text
    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceText:
        return
    
    infoMap = {'bookAbbrev': '', 'fromChap': 0, 'toChap': 0}
    
    # Parse it into book and chapters
    if parseSourceTextName(report, sourceText, infoMap) == False: # error occurred
        return 
    
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
        
        do_export(DB, report, window.chapSel, configMap, window)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
