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

bookMap = {\
'Genesis':'GEN',\
'Exodus':'EXO',\
'Leviticus':'LEV',\
'Numbers':'NUM',\
'Deuteronomy':'DEU',\
'Joshua':'JOS',\
'Judges':'JDG',\
'Ruth':'RUT',\
'1 Samuel':'1SA',\
'2 Samuel':'2SA',\
'1 Kings':'1KI',\
'2 Kings':'2KI',\
'1 Chronicles':'1CH',\
'2 Chronicles':'2CH',\
'Ezra':'EZR',\
'Nehemiah':'NEH',\
'Esther':'EST',\
'Job':'JOB',\
'Psalms':'PSA',\
'Proverbs':'PRO',\
'Ecclesiastes':'ECC',\
'Song of Solomon':'SNG',\
'Isaiah':'ISA',\
'Jeremiah':'JER',\
'Lamentations':'LAM',\
'Ezekiel':'EZK',\
'Daniel':'DAN',\
'Hosea':'HOS',\
'Joel':'JOL',\
'Amos':'AMO',\
'Obadiah':'OBA',\
'Jonah':'JON',\
'Micah':'MIC',\
'Nahum':'NAM',\
'Habakkuk':'HAB',\
'Zephaniah':'ZEP',\
'Haggai':'HAG',\
'Zechariah':'ZEC',\
'Malachi':'MAL',\
'Matthew':'MAT',\
'Mark':'MRK',\
'Luke':'LUK',\
'John':'JHN',\
'Acts':'ACT',\
'Romans':'ROM',\
'1 Corinthians':'1CO',\
'2 Corinthians':'2CO',\
'Galatians':'GAL',\
'Ephesians':'EPH',\
'Philippians':'PHP',\
'Colossians':'COL',\
'1 Thessalonians':'1TH',\
'2 Thessalonians':'2TH',\
'1 Timothy':'1TI',\
'2 Timothy':'2TI',\
'Titus':'TIT',\
'Philemon':'PHM',\
'Hebrews':'HEB',\
'James':'JAS',\
'1 Peter':'1PE',\
'2 Peter':'2PE',\
'1 John':'1JN',\
'2 John':'2JN',\
'3 John':'3JN',\
'Jude':'JUD',\
'Revelation':'REV',\
}

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
    
textNameList = []

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
    
    # TODO: remove footnotes if necessary
    
    segs = re.split(r'(\\f\*|\\f \+ |\\fr \d+:\d+|\\v \d+ |\\c \d+|\\\w+)', importText) # match footnotes or \v n or \c n or other sfms

    # Create 1st paragraph object
    stTxtPara = m_stTxtParaFactory.Create()
    
    # Add it to the stText object
    stText.ParagraphsOS.Add(stTxtPara)    

    bldr = TsStringUtils.MakeStrBldr()

    for _, seg in enumerate(segs):
        
        if re.search(r'\\p', seg): # or first segment if not blank
        
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
            
            # make this in the Analysis WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultAnalWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
            
        else:
            # make this in the Vernacular WS
            tss = TsStringUtils.MakeString(seg, DB.project.DefaultVernWs)
            bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
        
    stTxtPara.Contents = bldr.GetString()

    # TODO: use new file name if the current one exists.

    # Build the title string from book abbreviation and chapter range. E.g. EXO 3 or EXO 3-4
    title = chapSelectObj.bookAbbrev + ' ' + str(chapSelectObj.fromChap)
    
    if chapSelectObj.fromChap < chapSelectObj.toChap:
        
        title += '-' + str(chapSelectObj.toChap)
    
    # Set the title of the text
    tss = TsStringUtils.MakeString(title, DB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    report.Info('Text: "'+title+'" created.')

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
        bookAbbrev = self.ui.bookAbbrevLineEdit.text()
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
        if bookAbbrev not in bookMap.values():
            
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
