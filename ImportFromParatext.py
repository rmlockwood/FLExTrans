#
#   ImportFromParatext
#
#   Ron Lockwood
#   SIL International
#   10/30/21
#
#   Version 3.5.4 - 7/8/22 - Ron Lockwood
#    Set Window Icon to be the FLExTrans Icon
#
#   Version 3.5.3 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5.2 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.5.1 - 5/5/22 - Ron Lockwood
#    Various improvements.
#
#   Version 3.5 - 5/3/22 - Ron Lockwood
#    Initial version.
#
#   Import chapters from Paratext. The user is prompted which chapters and which
#   Paratext project.
#
#

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils
from flexlibs import FLExProject, AllProjectNames

import ReadConfig
import Utils
import ChapterSelection
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
from FTPaths import CONFIG_PATH

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Import Text From Paratext",
        FTM_Version    : "3.5.4",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Import chapters from Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
This module asks you which Paratext project, which book and which chapters should be 
imported. The book name should be given as a three-letter abbreviation just like in
Paratext. Those chapters are gathered and inserted into the current FLEx project as a 
new text. If you want to include the footnotes in the import, click the check box. 
If you want to use the English full name of the book in the text name, click the check box. 
If you want to make the newly imported text, the active text in FLExTrans click the check box.""" }
                 
#----------------------------------------------------------------
# The main processing function

# Tuple of 3 items
replaceList = [\
               #('Name', 'find_str', 'rpl_str'),\
              ]

PTXIMPORT_SETTINGS_FILE = 'ParatextImportSettings.json'

def setSourceNameInConfigFile(report, title):
        
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myConfig = os.path.join(os.path.dirname(CONFIG_PATH), ReadConfig.CONFIG_FILE)
        f = open(myConfig, encoding='utf-8')
        
    except:
        report.Error(f'Could not open the configuration file: {myConfig}') 
        return
    
    configLines = f.readlines()
    
    for i, line in enumerate(configLines):
        
        if re.search('SourceTextName', line):
        
            configLines[i] = f'SourceTextName={title}\n'
            break
                    
    f.close()

    # Make a copy of the original
    copyfile(myConfig, myConfig+'.copy')

    f = open(myConfig, 'w', encoding='utf-8')
    f.writelines(configLines)
    f.close()

def do_import(DB, report, chapSelectObj):
    
    copyUntilEnd = False
    
    # Create the text objects
    m_textFactory = DB.project.ServiceLocator.GetInstance(ITextFactory)
    m_stTextFactory = DB.project.ServiceLocator.GetInstance(IStTextFactory)
    m_stTxtParaFactory = DB.project.ServiceLocator.GetInstance(IStTxtParaFactory)

    # Create a text and add it to the project      
    text = m_textFactory.Create()           
    stText = m_stTextFactory.Create()
    
    # Set StText object as the Text contents
    text.ContentsOA = stText  
    
    # Open the Paratext file
    f = open(chapSelectObj.bookPath, encoding='utf-8')
    
    bookContents = f.read()
    
    # Find all the chapter #s
    chapList = re.findall(r'\\c (\d+)', bookContents, flags=re.DOTALL)
    
    if str(chapSelectObj.fromChap) not in chapList:
        
        report.Error('Starting chapter not found.')
        return
    
    if str(chapSelectObj.toChap+1) not in chapList:
        
        copyUntilEnd = True
        
        if len(chapList) > 0:
            chapSelectObj.toChap = int(chapList[-1])
    
    # Build the search regex
    reStr = fr'(\\c {str(chapSelectObj.fromChap)}\s.+?)'
    
    if copyUntilEnd:
        
        reStr += '$'
    else:
        reStr += fr'\\c {str(chapSelectObj.toChap+1)}\s'

    matchObj = re.search(reStr, bookContents, flags=re.DOTALL)
    
    importText = matchObj.group(1)
    
    # Remove newlines
    importText = re.sub(r'\n', '', importText)
        
    # Do some user defined replacements
    for _, findStr, replStr in replaceList:
        
        importText = re.sub(findStr, replStr, importText)
        
    # Remove footnotes if necessary
    if chapSelectObj.includeFootnotes == False:
        
        importText = re.sub(r'\\f.+?\\f\*', '', importText)
    
    segs = re.split(r'(\\\w+\*|\\f \+ |\\fr \d+:\d+|\\xo \d+:\d+|\\v \d+ |\\c \d+|\\\w+)', importText) # match footnotes, cros-refs,  or \v n or \c n or other sfms

    # Create 1st paragraph object
    stTxtPara = m_stTxtParaFactory.Create()
    
    # Add it to the stText object
    stText.ParagraphsOS.Add(stTxtPara)    

    bldr = TsStringUtils.MakeStrBldr()

    # SFMs to start a new paragraph in FLEx
    newPar = r'\\[cpsqm]'
    
    for _, seg in enumerate(segs):
        
        if re.search(newPar, seg): # or first segment if not blank
        
            # Save the built up string to the Contents member
            stTxtPara.Contents = bldr.GetString()
            
            # Create paragraph object
            stTxtPara = m_stTxtParaFactory.Create()
            
            # Add it to the stText object
            stText.ParagraphsOS.Add(stTxtPara)  
        
            bldr = TsStringUtils.MakeStrBldr()
        
        if len(seg) == 0:
            continue
        
        elif re.search(r'\\', seg):
            
            # add a space before the marker if we have content before it.
            if bldr.Length > 0:
                seg = ' ' + seg
            
            # make this in the Analysis WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultAnalWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
            
        else:
            # make this in the Vernacular WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultVernWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
        
    stTxtPara.Contents = bldr.GetString()

    # If the user wants full name, look it up
    if chapSelectObj.useFullBookName:
        
        bibleBook = ChapterSelection.bookMap[chapSelectObj.bookAbbrev]
    else:
        bibleBook = chapSelectObj.bookAbbrev

    # Build the title string from book abbreviation and chapter range. E.g. EXO 03 or EXO 03-04
    title = bibleBook + ' ' + str(chapSelectObj.fromChap).zfill(2)
    
    if chapSelectObj.fromChap < chapSelectObj.toChap:
        
        title += '-' + str(chapSelectObj.toChap).zfill(2)
        
    # Use new file name if the current one exists. E.g. PSA 01-03, PSA 01-03 - Copy, PSA 01-03 - Copy (2)
    title = Utils.createUniqueTitle(DB, title)
    
    # Set the title of the text
    tss = TsStringUtils.MakeString(title, DB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    report.Info('Text: "'+title+'" created.')
    
    # Make this new text the active text for FLExTrans if necessary
    if chapSelectObj.makeActive:
        
        setSourceNameInConfigFile(report, title)
    
class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.chapSel = None
        self.retVal = False
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon('FLExTransWindowIcon.ico'))
        
        self.ui.fromChapterSpinBox.valueChanged.connect(self.FromSpinChanged)
        self.ui.toChapterSpinBox.valueChanged.connect(self.ToSpinChanged)
        
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        
        # Load settings if available
        try:
            # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
            # Get the parent folder of flextools.ini, i.e. Config and add the settings file
            self.settingsPath = os.path.join(os.path.dirname(CONFIG_PATH), PTXIMPORT_SETTINGS_FILE)
            
            f = open(self.settingsPath, 'r')
            myMap = json.load(f)
            
            self.ui.ptxProjAbbrevLineEdit.setText(myMap['projectAbbrev'])
            self.ui.bookAbbrevLineEdit.setText(myMap['bookAbbrev'])
            self.ui.fromChapterSpinBox.setValue(myMap['fromChap'])
            self.ui.toChapterSpinBox.setValue(myMap['toChap'])
            self.ui.footnotesCheckBox.setChecked(myMap['includeFootnotes'])
            self.ui.makeActiveTextCheckBox.setChecked(myMap['makeActive'])
            self.ui.useFullBookNameForTitleCheckBox.setChecked(myMap['useFullBookName'])
            f.close()
        except:
            pass

    def CancelClicked(self):
        self.retVal = False
        self.close()
        
    def FromSpinChanged(self):
        
        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()

        # if from chapter is greater than the to chapter, change the to chapter to match
        if self.fromChap > self.toChap:
            
            self.ui.toChapterSpinBox.setValue(self.fromChap)
            self.toChap = self.fromChap
            
    def ToSpinChanged(self):
        
        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()

        # if to chapter is less than the from chapter, change the from chapter to match
        if self.toChap < self.fromChap:
            
            self.ui.fromChapterSpinBox.setValue(self.toChap)
            self.fromChap = self.toChap
            
    def OKClicked(self):

        # Get values from the 'dialog' window
        projectAbbrev = self.ui.ptxProjAbbrevLineEdit.text()
        bookAbbrev = self.ui.bookAbbrevLineEdit.text().upper()
        fromChap = self.ui.fromChapterSpinBox.value()        
        toChap = self.ui.toChapterSpinBox.value()
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

        # Check if the book is valid
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
        
        dumpMap = self.chapSel.dump()
        json.dump(dumpMap, f)
        
        f.close()
        
        self.retVal = True
        self.close()
            
def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Show the window
    app = QApplication(sys.argv)

    window = Main()
    
    window.show()
    
    app.exec_()
    
    if window.retVal == True:
        
        do_import(DB, report, window.chapSel)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
