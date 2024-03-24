#
#   ChapterSelection
#
#   Ron Lockwood
#   SIL International
#   5/3/22
#
#   Version 3.10.1 - 3/19/24 - Ron Lockwood
#    Fixes #566. Allow the user to create one text per chapter when importing.
#
#   Version 3.10 - 3/13/24 - Ron Lockwood
#    Support Paratext lexicon import.
#
#   Version 3.9.1 - 12/21/23 - Ron Lockwood
#    Added apocryphal/deuterocanonical and extra books into the list.
#
#   Version 3.7.1 - 1/30/23 - Ron Lockwood
#    Restructured to put common init and exit code into ChapterSelection.py
#    Store export project and import project as separate settings.
#
#   Version 3.7 - 1/25/23 - Ron Lockwood
#    Added cross-references to the selection class.
#
#   Version 3.5 - 5/3/22 - Ron Lockwood
#    Initial version.
#
#   ChapterSelection Class which is for data associated with import and export
#   from and to Paratext. 
#

import os
import winreg
import glob
import json
from PyQt5.QtWidgets import QMessageBox

import FTPaths

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
'TOB':'Tobit',\
'JDT':'Judith',\
'ESG':'Esther Greek',\
'WIS':'Wisdom of Solomon',\
'SIR':'Sirach',\
'BAR':'Baruch',\
'LJE':'Letter of Jeremiah',\
'S3Y':'Song of the 3 Young Men',\
'SUS':'Susanna',\
'BEL':'Bel and the Dragon',\
'1MA':'1 Maccabees',\
'2MA':'2 Maccabees',\
'3MA':'3 Maccabees',\
'4MA':'4 Maccabees',\
'1ES':'1 Esdras (Greek)',\
'2ES':'2 Esdras (Latin)',\
'MAN':'Prayer of Manasseh',\
'PS2':'Psalm 151',\
'ODA':'Odae/Odes',\
'PSS':'Psalms of Solomon',\
'EZA':'Ezra Apocalypse',\
'5EZ':'5 Ezra',\
'6EZ':'6 Ezra',\
'DAG':'Daniel Greek',\
'PS3':'Psalms 152-155',\
'2BA':'2 Baruch (Apocalypse)',\
'LBA':'Letter of Baruch',\
'JUB':'Jubilees',\
'ENO':'Enoch',\
'1MQ':'1 Meqabyan/Mekabis',\
'REP':'Reproof',\
'4BA':'4 Baruch',\
'LAO':'Letter to the Laodiceans',\
'XXA':'Extra A',\
'XXB':'Extra B',\
'XXC':'Extra C',\
'XXD':'Extra D',\
'XXE':'Extra E',\
'XXF':'Extra F',\
'XXG':'Extra G',\
'INT':'Introduction',\
}

class ChapterSelection(object):
        
    def __init__(self, export, otherProj, projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                 makeActive, useFullBookName, oneTextPerChapter=False):
    
        if export:
            self.exportProjectAbbrev = projectAbbrev  
            self.importProjectAbbrev = otherProj   
        else:
            self.importProjectAbbrev = projectAbbrev  
            self.exportProjectAbbrev = otherProj   

        self.bookAbbrev         = bookAbbrev  
        self.bookPath           = bookPath     
        self.fromChap           = fromChap        
        self.toChap             = toChap          
        self.includeFootnotes   = includeFootnotes
        self.includeCrossRefs   = includeCrossRefs
        self.makeActive         = makeActive      
        self.useFullBookName    = useFullBookName     
        self.oneTextPerChapter  = oneTextPerChapter
        
    def dump(self):
        
        ret = {\
            'exportProjectAbbrev'    : self.exportProjectAbbrev,\
            'importProjectAbbrev'    : self.importProjectAbbrev,\
            'bookAbbrev'             : self.bookAbbrev         ,\
            'fromChap'               : self.fromChap           ,\
            'toChap'                 : self.toChap             ,\
            'includeFootnotes'       : self.includeFootnotes   ,\
            'includeCrossRefs'       : self.includeCrossRefs   ,\
            'makeActive'             : self.makeActive         ,\
            'useFullBookName'        : self.useFullBookName    ,\
            'oneTextPerChapter'      : self.oneTextPerChapter   \
            }
        return ret

def InitControls(self, export=True):
    
    self.chapSel = None
    self.retVal = False
    
    self.ui.OKButton.clicked.connect(self.OKClicked)
    self.ui.CancelButton.clicked.connect(self.CancelClicked)

    self.otherProj = ''
    
    # Load settings if available
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add the settings file
        self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), PTXIMPORT_SETTINGS_FILE)
        
        f = open(self.settingsPath, 'r')
        myMap = json.load(f)
        
        # Set the project edit box to either the export or import project.
        # Save the other one as otherProj so we can write it out again to the settings file.
        if export:
            self.ui.ptxProjAbbrevLineEdit.setText(myMap['exportProjectAbbrev'])
            self.otherProj = myMap['importProjectAbbrev']
        else:
            self.ui.ptxProjAbbrevLineEdit.setText(myMap['importProjectAbbrev'])
            self.otherProj = myMap['exportProjectAbbrev']
            
        self.ui.bookAbbrevLineEdit.setText(myMap['bookAbbrev'])
        self.ui.fromChapterSpinBox.setValue(myMap['fromChap'])
        self.ui.toChapterSpinBox.setValue(myMap['toChap'])
        self.ui.footnotesCheckBox.setChecked(myMap['includeFootnotes'])
        self.ui.crossrefsCheckBox.setChecked(myMap['includeCrossRefs'])
        self.ui.makeActiveTextCheckBox.setChecked(myMap['makeActive'])
        self.ui.useFullBookNameForTitleCheckBox.setChecked(myMap['useFullBookName'])
        self.ui.oneTextPerChapterCheckBox.setChecked(myMap['oneTextPerChapter'])
        f.close()
    except:
        pass

def doOKbuttonValidation(self, export=True, checkBookAbbrev=True, checkBookPath=True):
    
    # Get values from the 'dialog' window
    projectAbbrev = self.ui.ptxProjAbbrevLineEdit.text()
    bookAbbrev = self.ui.bookAbbrevLineEdit.text().upper()
    fromChap = self.ui.fromChapterSpinBox.value()        
    toChap = self.ui.toChapterSpinBox.value()
    includeFootnotes = self.ui.footnotesCheckBox.isChecked()
    includeCrossRefs = self.ui.crossrefsCheckBox.isChecked()
    makeActive = self.ui.makeActiveTextCheckBox.isChecked()
    useFullBookName = self.ui.useFullBookNameForTitleCheckBox.isChecked()
    oneTextPerChapter = self.ui.oneTextPerChapterCheckBox.isChecked()
    
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
    if checkBookAbbrev and bookAbbrev not in bookMap:
        
        QMessageBox.warning(self, 'Invalid Book Error', f'The book abbreviation: {bookAbbrev} is invalid.')
        return
    
    # Check if the book exists
    bookPath = os.path.join(projPath, '*' + bookAbbrev + projectAbbrev + '.SFM')
    
    parts = glob.glob(bookPath)
    
    if checkBookPath and len(parts) < 1:
        
        QMessageBox.warning(self, 'Not Found Error', f'Could not find that book file at: {bookPath}.')
        return

    bookPath = parts[0]
    
    self.chapSel = ChapterSelection(export, self.otherProj, projectAbbrev, bookAbbrev, bookPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                                    makeActive, useFullBookName, oneTextPerChapter)
    
    # Save the settings to a file so the same settings can be shown next time
    f = open(self.settingsPath, 'w')
    
    dumpMap = self.chapSel.dump()
    json.dump(dumpMap, f)
    
    f.close()
    
    self.retVal = True
    self.close()