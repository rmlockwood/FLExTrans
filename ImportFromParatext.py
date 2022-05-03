#
#   ImportFromParatext
#
#   Ron Lockwood
#   SIL International
#   10/30/21
#
#   Version 3.1 - 2/4/22 - Ron Lockwood
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
from flexlibs.FLExProject import FLExProject, GetProjectNames
import ReadConfig
import os
import re
import sys
import glob
import winreg
import json
from shutil import copyfile

from PyQt5 import QtCore
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication

from ParatextChapSelection import Ui_MainWindow

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Import Text From Paratext",
        FTM_Version    : "3.2",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Import chapters from Paratext.",
        FTM_Help       : "",
        FTM_Description:
"""
Copy chapters of a given book from a given Paratext project import it into the source FLEx project.
The copied chapters will show up as a new text in the FLEx project. If the text already exists, a
new text will get created with a similar name. By checking the Include footnotes checkbox, the sfm
markers and associated text will be imported with the verse text. By checking the Make a new text the active text
checkbox, FLExTrans will make the newly created text, the source text for subsequent FLExTrans work.
By checking the Use full English book name for title checkbox, the title will have the full book name
in the title. For example, Genesis 1-2. Otherwise the title will use the book abbreviation. For example,
GEN 1-2. You have to have at least an Observer role on the project to use this module.""" }
                 
#----------------------------------------------------------------
# The main processing function

PTXIMPORT_SETTINGS_FILE = 'ParatextImportSettings.json'

bookMap = {\
'GEN':'Genesis',\
'EXO':'Exodus',\
'LEV':'Leviticus',\
'NUM':'Numbers',\
'DEU':'Deuteronomy',\
'JOS':'Joshua',\
'JDG':'Judges',\
'RUT':'Ruth',\
'1SA':'1 Samuel',\
'2SA':'2 Samuel',\
'1KI':'1 Kings',\
'2KI':'2 Kings',\
'1CH':'1 Chronicles',\
'2CH':'2 Chronicles',\
'EZR':'Ezra',\
'NEH':'Nehemiah',\
'EST':'Esther',\
'JOB':'Job',\
'PSA':'Psalms',\
'PRO':'Proverbs',\
'ECC':'Ecclesiastes',\
'SNG':'Song of Solomon',\
'ISA':'Isaiah',\
'JER':'Jeremiah',\
'LAM':'Lamentations',\
'EZK':'Ezekiel',\
'DAN':'Daniel',\
'HOS':'Hosea',\
'JOL':'Joel',\
'AMO':'Amos',\
'OBA':'Obadiah',\
'JON':'Jonah',\
'MIC':'Micah',\
'NAM':'Nahum',\
'HAB':'Habakkuk',\
'ZEP':'Zephaniah',\
'HAG':'Haggai',\
'ZEC':'Zechariah',\
'MAL':'Malachi',\
'MAT':'Matthew',\
'MRK':'Mark',\
'LUK':'Luke',\
'JHN':'John',\
'ACT':'Acts',\
'ROM':'Romans',\
'1CO':'1 Corinthians',\
'2CO':'2 Corinthians',\
'GAL':'Galatians',\
'EPH':'Ephesians',\
'PHP':'Philippians',\
'COL':'Colossians',\
'1TH':'1 Thessalonians',\
'2TH':'2 Thessalonians',\
'1TI':'1 Timothy',\
'2TI':'2 Timothy',\
'TIT':'Titus',\
'PHM':'Philemon',\
'HEB':'Hebrews',\
'JAS':'James',\
'1PE':'1 Peter',\
'2PE':'2 Peter',\
'1JN':'1 John',\
'2JN':'2 John',\
'3JN':'3 John',\
'JUD':'Jude',\
'REV':'Revelation',\
}

textNameList = []

class ChapterSelection(object):
        
    def __init__(self, projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, makeActive, useFullBookName):
    
        self.projectAbbrev      = projectAbbrev    
        self.bookAbbrev         = bookAbbrev  
        self.bookPath           = bookPath     
        self.fromChap           = fromChap        
        self.toChap             = toChap          
        self.includeFootnotes   = includeFootnotes
        self.makeActive         = makeActive      
        self.useFullBookName    = useFullBookName     
        
    def dump(self):
        
        ret = {\
            'projectAbbrev'    : self.projectAbbrev      ,\
            'bookAbbrev'       : self.bookAbbrev         ,\
            'fromChap'         : self.fromChap           ,\
            'toChap'           : self.toChap             ,\
            'includeFootnotes' : self.includeFootnotes   ,\
            'makeActive'       : self.makeActive         ,\
            'useFullBookName'  : self.useFullBookName     \
            }
        return ret
    
# TODO: this function is a duplicate of what is in InsertTargetText.py, move it to Utils and have both modules call it    
def findTextName(TargetDB, myTextName):
    foundText = False
    
    if len(textNameList) == 0:
        
        for text in TargetDB.ObjectsIn(ITextRepository):
            
            tName = ITsString(text.Name.BestVernacularAnalysisAlternative).Text
            textNameList.append(tName)
            
            if myTextName == tName:
                
                foundText = True
    else:
        if myTextName in textNameList:
            
            foundText = True
            
    return foundText

def  createUniqueTitle(DB, title):
      
    if findTextName(DB, title):
        
        title += ' - Copy'
        if findTextName(DB, title): 
            
            done = False
            i = 2
            
            while not done: 
                
                tryName = title + ' (' + str(i) + ')'
                
                if not findTextName(DB, tryName): 
                    
                    title = tryName
                    done = True 
                    
                i += 1
    return title

def setSourceNameInConfigFile(report, title):
        
    try:
        # Edit the FLExTrans config file to use the current text/folder name
        myConfig = '../' + ReadConfig.CONFIG_FILE
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
    

    # Open the file
    f = open(chapSelectObj.bookPath, encoding='utf-8')
    
    bookContents = f.read()
    
    # Find all the chapter #s
    chapList = re.findall(r'\\c (\d+)', bookContents, re.DOTALL)
    
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

    matchObj = re.search(reStr, bookContents, re.DOTALL)
    
    importText = matchObj.group(1)
    
    # Remove newlines
    importText = re.sub(r'\n', '', importText)
        
    # Replace new line with space if it's before a marker
    #outStr = re.sub(r'\n\\', r' \\', savedTxt)
    
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
        
        bibleBook = bookMap[chapSelectObj.bookAbbrev]
    else:
        bibleBook = chapSelectObj.bookAbbrev

    # Build the title string from book abbreviation and chapter range. E.g. EXO 03 or EXO 03-04
    title = bibleBook + ' ' + str(chapSelectObj.fromChap).zfill(2)
    
    if chapSelectObj.fromChap < chapSelectObj.toChap:
        
        title += '-' + str(chapSelectObj.toChap).zfill(2)

    # Use new file name if the current one exists. E.g. PSA 01-03, PSA 01-03 - Copy, PSA 01-03 - Copy (2)
    title = createUniqueTitle(DB, title)
    
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
        
        self.ui.fromChapterSpinBox.valueChanged.connect(self.FromSpinChanged)
        self.ui.toChapterSpinBox.valueChanged.connect(self.ToSpinChanged)
        
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        #self.ui.CancelButton.clicked.connect(self.CancelClicked)
        
        # Load settings if available
        try:
            f = open(PTXIMPORT_SETTINGS_FILE, 'r')
            myMap = json.load(f)
            
            self.ui.ptxProjAbbrevLineEdit.setText(myMap['projectAbbrev'])
            self.ui.bookAbbrevLineEdit.setText(myMap['bookAbbrev'])
            self.ui.fromChapterSpinBox.setValue(myMap['fromChap'])
            self.ui.toChapterSpinBox.setValue(myMap['toChap'])
            self.ui.footnotesCheckBox.setChecked(myMap['includeFootnotes'])
            self.ui.makeActiveTextCheckBox.setChecked(myMap['makeActive'])
            self.ui.useFullBookNameForTitleCheckBox.setChecked(myMap['useFullBookName'])
            
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
        if bookAbbrev not in bookMap:
            
            QMessageBox.warning(self, 'Invalid Book Error', f'The book abbreviation: {bookAbbrev} is invalid.')
            return
        
        # Check if the book exists
        bookPath = os.path.join(projPath, '*' + bookAbbrev + projectAbbrev + '.SFM')
        
        parts = glob.glob(bookPath)
        
        if len(parts) < 1:
            
            QMessageBox.warning(self, 'Not Found Error', f'Could not find that book file at: {bookPath}.')
            return
    
        bookPath = parts[0]
        
        self.chapSel = ChapterSelection(projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, makeActive, useFullBookName)
        
        # Save the settings to a file so the same settings can be shown next time
        f = open(PTXIMPORT_SETTINGS_FILE, 'w')
        
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
