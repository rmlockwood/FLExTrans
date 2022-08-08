#
#   ExportToParatext
#
#   Ron Lockwood
#   SIL International
#   5/3/22
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

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils
from flexlibs import FLExProject, AllProjectNames
import ReadConfig
import os
import re
import sys
import glob
import winreg
import json
from shutil import copyfile

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication

from ParatextChapSelectionDlg import Ui_MainWindow
import ChapterSelection
from FTPaths import CONFIG_PATH

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Export Translated Text to Paratext",
        FTM_Version    : "3.5.3",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Export text that has been translated with FLExTrans to Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
After chapters have been translated with FLExTrans, this module will copy the chapters
into Paratext to the project specified.""" }
                 
#----------------------------------------------------------------
# The main processing function

PTXEXPORT_SETTINGS_FILE = 'ParatextExportSettings.txt'

def do_export(DB, report, chapSelectObj, configMap, parent):
    
    # Check that we have a synthesized file
    synFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not synFile:
        return
    
    # Read in the syn. file chapters
    f = open(synFile, 'r', encoding='utf-8')
    synFileContents = f.read()
    f.close()
    
    # Find all the chapter #s
    synChapList = re.findall(r'\\c (\d+)', synFileContents, flags=re.DOTALL)
    
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
    copyfile(chapSelectObj.bookPath, chapSelectObj.bookPath+'.bak')
    
    # Read the Paratext file
    f = open(chapSelectObj.bookPath, encoding='utf-8')
    
    bookContents = f.read()
    f.close()
    
    # Find all the chapter #s
    ptxChapList = re.findall(r'\\c (\d+)', bookContents, flags=re.DOTALL)
    
    # Split the synthesis contents into chapter chunks
    synContentsList = re.split(r'(\\c \d+)', synFileContents, flags=re.DOTALL) # gives us [\c 1, \s ..., \c 2, \s ..., ...]
    
    # Loop through each synthesis chapter and splice it into the paratext chapter contents
    for n in range(1, len(synContentsList), 2): # the zeroth one will be whatever is before the first \c, possibly the empty string
        
        wholeChStr = synContentsList[n] + synContentsList[n+1]
        
        # Check the corresponding chapter in the synthesis chapter list
        if synChapList[n//2] in ptxChapList:
            
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
        
        bookContents = re.sub(begRE + endRE, wholeChStr, bookContents, flags=re.DOTALL)
        
        # Unescape the backslashes
        #bookContents = re.sub(r'\\\\', r'\\', bookContents)
        
    # Write the ptx file
    f = open(chapSelectObj.bookPath, 'w', encoding='utf-8')
    f.write(bookContents)
    
    # Close files
    f.close()
    
    # Report how many chapters processed
    report.Info(f'{str(len(synChapList))} chapter(s) exported.')
    
class Main(QMainWindow):

    def __init__(self, bookAbbrev, fromChap, toChap):
        QMainWindow.__init__(self)

        self.chapSel = None
        self.retVal = False
        
        self.setWindowIcon(QtGui.QIcon('FLExTransWindowIcon.ico'))
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Set the interface according to what was passed in (from SourceName)
        self.ui.fromChapterSpinBox.setValue(fromChap)
        self.ui.fromChapterSpinBox.setEnabled(False)
        
        self.ui.toChapterSpinBox.setValue(toChap)
        self.ui.toChapterSpinBox.setEnabled(False)
        
        self.ui.bookAbbrevLineEdit.setText(bookAbbrev)
        self.ui.bookAbbrevLineEdit.setEnabled(False)
        
        # Hide the checkboxes
        self.ui.footnotesCheckBox.setVisible(False)
        self.ui.makeActiveTextCheckBox.setVisible(False)
        self.ui.useFullBookNameForTitleCheckBox.setVisible(False)

        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        self.setWindowTitle("Export Chapters to Paratext")
        # Load settings if available
        try:
            # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
            # Get the parent folder of flextools.ini, i.e. Config and add the settings file
            self.settingsPath = os.path.join(os.path.dirname(CONFIG_PATH), PTXEXPORT_SETTINGS_FILE)
            f = open(self.settingsPath, 'r')
            
            ptxProj = f.readline()
            
            self.ui.ptxProjAbbrevLineEdit.setText(ptxProj)
            f.close()
        except:
            pass

    def CancelClicked(self):
        self.retVal = False
        self.close()
        
    def OKClicked(self):

        # Get values from the 'dialog' window
        projectAbbrev = self.ui.ptxProjAbbrevLineEdit.text()
        bookAbbrev = self.ui.bookAbbrevLineEdit.text().upper()
        fromChap = self.ui.fromChapterSpinBox.value()        
        toChap = self.ui.toChapterSpinBox.value()
        
        # Unused, but pass them along
        includeFootnotes = self.ui.footnotesCheckBox.isChecked()
        makeActive = self.ui.makeActiveTextCheckBox.isChecked()
        useFullBookName = self.ui.useFullBookNameForTitleCheckBox.isChecked()
        
        ## Validate some stuff
        
        # Get the Paratext path from the registry
        aKey = r"SOFTWARE\Wow6432Node\Paratext\8"
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        aKey = winreg.OpenKey(aReg, aKey)
        paratextPathTuple = winreg.QueryValueEx(aKey, "Settings_Directory")
        paratextPath = paratextPathTuple[0]
        
        # Check if project path exists under Paratext
        projPath = os.path.join(paratextPath, projectAbbrev)
        if not os.path.exists(projPath):
            
            QMessageBox.warning(self, 'Not Found Error', f'Could not find that project at: {projPath}.')
            return

        # Check if the book is valid (book should already be validated)
        if bookAbbrev not in ChapterSelection.bookMap:
            
            QMessageBox.warning(self, 'Invalid Book Error', f'The book abbreviation: {bookAbbrev} is invalid.')
            return
        
        # Check if the book exists
        bookPath = os.path.join(projPath, '*' + bookAbbrev + projectAbbrev + '.SFM')
        
        parts = glob.glob(bookPath)
        
        if len(parts) < 1:
            
            QMessageBox.warning(self, 'Not Found Error', f'Could not find that book file at: {bookPath}.')
            return
    
        bookPath = parts[0]
        
        self.chapSel = ChapterSelection.ChapterSelection(projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, makeActive, useFullBookName)
        
        # Save the settings to a file so the same settings can be shown next time
        f = open(self.settingsPath, 'w')
        
        f.write(projectAbbrev)
        f.close()
        
        self.retVal = True
        self.close()

def parseSourceTextName(report, sourceText, infoMap): 
    
    stdError = f'The text name "{sourceText}" is invalid it should be of the form GEN 01 or GEN 23-38'
    
    # should have two main elements, book name (which can have spaces) and chapter number
    myList = sourceText.split()
    
    # the book portion will be all except the last one
    bookAbbrev = book = ' '.join(myList[0:-1])
    
    chapters = myList[-1]
    
    # Check first if this is an abbreviation that is in the book map
    if book.upper() not in ChapterSelection.bookMap:
        
        # Now check if this is a full book name that is in the values part of the map (e.g. 'Genesis')
        if book not in ChapterSelection.bookMap.values():
            report.Error('The book name or abbreviation is invalid. It should match a Paratext book.')
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

    # Find the desired text
    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceText:
        return
    
    infoMap = {'bookAbbrev': '', 'fromChap': 0, 'toChap': 0}
    
    # Parse it into book and chapters
    if parseSourceTextName(report, sourceText, infoMap) == False: # error occurred
        return 
    
    # Show the window
    app = QApplication(sys.argv)

    window = Main(infoMap['bookAbbrev'], infoMap['fromChap'], infoMap['toChap'])
    
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
