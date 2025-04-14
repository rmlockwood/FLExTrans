#
#   ChapterSelection
#
#   Ron Lockwood
#   SIL International
#   5/3/22
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.8 - 3/4/25 - Ron Lockwood
#    Fixes #903. Don't show the 'Don't show message again' checkbox if there are no cluster projects.
#
#   Version 3.12.7 - 1/23/25 - Ron Lockwood
#    Support import of Glossary book (GLO).
#
#   Version 3.12.6 - 1/15/25 - Ron Lockwood
#    Export from the target DB as the default. Also recognize texts that have - Copy ...
#    at the end.
#
#   Version 3.12.5 - 1/15/25 - Ron Lockwood
#    Export from FLEx to Paratext, optionally across cluster projects.
#
#   Version 3.12.4 - 1/13/25 - Ron Lockwood
#    Fixes crash on import with no cluster projects.
#
#   Version 3.12.3 - 12/31/24 - Ron Lockwood
#    Fixes #830. Track the Paratext path instead of book path.
#
#   Version 3.12.2 - 12/30/24 - Ron Lockwood
#    Support for importing cluster projects.
#
#   Version 3.12.1 - 11/26/24 - Ron Lockwood
#    Allow intro. to be imported with chapter 1.
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
import re
from shutil import copyfile
import winreg
import glob
import json
from PyQt5.QtWidgets import QMessageBox, QCheckBox
import ClusterUtils
from ComboBox import CheckableComboBox
import FTPaths
from SIL.LCModel.Core.Text import TsStringUtils         # type: ignore

PTXIMPORT_SETTINGS_FILE = 'ParatextImportSettings.json'
EXP_SHRINK_WINDOW_PIXELS = 120
FROM_FLEX_EXP_PIXELS = 33

bookChapterPattern = re.compile(r'^(?P<book>.+?) (?P<chap1>\d{2})(?:-(?P<chap2>\d{2}))?(?: - Copy(?: \(\d{1,2}\))?)?$')

class ChapterSelection(object):
        
    def __init__(self, export, otherProj, projectAbbrev, bookAbbrev, paratextPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                 makeActive, useFullBookName, overwriteText, clusterProjects, ptxProjList, oneTextPerChapter=False, includeIntro=False):
    
        self.export = export
        self.dontShowWarning = False

        if self.export:
            self.exportProjectAbbrev = projectAbbrev  
            self.importProjectAbbrev = otherProj   
        else:
            self.importProjectAbbrev = projectAbbrev  
            self.exportProjectAbbrev = otherProj   

        self.bookAbbrev         = bookAbbrev  
        self.paratextPath       = paratextPath     
        self.fromChap           = fromChap        
        self.toChap             = toChap          
        self.includeFootnotes   = includeFootnotes
        self.includeCrossRefs   = includeCrossRefs
        self.makeActive         = makeActive      
        self.useFullBookName    = useFullBookName  
        self.overwriteText      = overwriteText
        self.clusterProjects    = clusterProjects   
        self.ptxProjList        = ptxProjList
        self.oneTextPerChapter  = oneTextPerChapter
        self.includeIntro       = includeIntro
        
    def dump(self):
        
        ret = {\
            'exportProjectAbbrev'    : self.exportProjectAbbrev,
            'importProjectAbbrev'    : self.importProjectAbbrev,
            'bookAbbrev'             : self.bookAbbrev,
            'fromChap'               : self.fromChap,
            'toChap'                 : self.toChap,
            'includeFootnotes'       : self.includeFootnotes,
            'includeCrossRefs'       : self.includeCrossRefs,
            'makeActive'             : self.makeActive,
            'useFullBookName'        : self.useFullBookName,
            'oneTextPerChapter'      : self.oneTextPerChapter,
            'includeIntro'           : self.includeIntro,
            'overwriteText'          : self.overwriteText,
            'clusterProjects'        : self.clusterProjects,
            'ptxProjList'            : self.ptxProjList,
            }
        return ret
    
    def getBookPath(self):
        
        if self.export:
            projectAbbrev = self.exportProjectAbbrev
        else:
            projectAbbrev = self.importProjectAbbrev  

        path = os.path.join(self.paratextPath, projectAbbrev, '*' + self.bookAbbrev + projectAbbrev + '.SFM')
        fileList = glob.glob(path)

        if len(fileList) < 1:
            return ''
        else:
            return fileList[0]

# Split the text into sfm marker (or ref) and non-sfm marker (or ref), i.e. text content. The sfm marker or reference will later get marked as analysis lang. so it doesn't
# have to be interlinearized. Always put the marker + ref with dash before the plain marker + ref. \\w+* catches all end markers and \\w+ catches everything else (it needs to be at the end)
# We have the \d+:\d+-\d+ and \d+:\d+ as their own expressions to catch places in the text that have a verse reference like after a \r or \xt. It's nice if these get marked as analysis WS.
# Attributes are of the form |x=123 ... \s*
# You can't have parens inside of the split expression since the whole thing is already in parens, unless you mark it as non-capturing parens with ?:. Otherwise it will mess up the output.
def splitSFMs(inputStr):

    segs = re.split(r'(\n|'                 # newline
                    r'\|\w+?=(?:.|\n)+?\*|' # attributes (|xyz=...) ending in * but possibly across lines
                    r'\||'                  # verticle bar
                    r'\\\w+\*|'             # end marker
                    r'\\f \+ |'             # footnote with plus
                    r'\\fr \d+[:.]\d+-\d+|' # footnote reference with dash (either colon or dot separating chapter and verse)
                    r'\\fr \d+[:.]\d+|'     # footnote reference
                    r'\\xt .+?\\x\*|'       # cross reference with end marker
                    r'\\x \+ |'             # cross reference with plus
                    r'\\xo \d+[:.]\d+-\d+|' # cross reference original with dash
                    r'\\xo \d+[:.]\d+|'     # cross reference original
                    r'\\v \d+-\d+ |'        # verse with dash
                    r'\\v \d+ |'            # verse
                    r'\\vp \S+ |'           # publication verse
                    r'\\c \d+|'             # chapter
                    r'\\rem.+?\n|'          # remark
                    r'\d+[:.]\d+-\d+|'      # verse reference with dash
                    r'\d+[:.]\d+|'          # verse reference
                    r'\\\+\w+|'             # marker preceded by plus
                    r'\\\w+)',              # any other marker
                    inputStr) 
    return segs

def insertParagraphs(DB, inputStr, m_stTxtParaFactory, stText):

    # Fix any sfms that are split across two lines. E.g. kanqa>>.\[newline]x + \xo ...
    # put the \ after the newline
    inputStr = re.sub(r'\\\n', r'\n\\', inputStr)

    segs = splitSFMs(inputStr)

    # Create 1st paragraph object
    stTxtPara = m_stTxtParaFactory.Create()
    
    # Add it to the stText object
    stText.ParagraphsOS.Add(stTxtPara)    
    bldr = TsStringUtils.MakeStrBldr()

    # Start a new paragraph at every line feed
    newPar = r'\n' 
    
    for _, seg in enumerate(segs):
        
        if not (seg is None or len(seg) == 0 or seg == '\n'):
            
            # Either an sfm marker or a verse ref should get marked as Analysis WS
            if re.search(r'\\|\d+[.:]\d+', seg):
                
                # make this in the Analysis WS
                tss = TsStringUtils.MakeString(re.sub(r'\n','', seg), DB.project.DefaultAnalWs)
                bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
                
            else:
                # make this in the Vernacular WS
                tss = TsStringUtils.MakeString(re.sub(r'\n','', seg), DB.project.DefaultVernWs)
                bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
        
        if seg and re.search(newPar, seg): # or first segment if not blank
        
            # Save the built up string to the Contents member
            stTxtPara.Contents = bldr.GetString()
            
            # Create paragraph object
            stTxtPara = m_stTxtParaFactory.Create()
            
            # Add it to the stText object
            stText.ParagraphsOS.Add(stTxtPara)  
        
            bldr = TsStringUtils.MakeStrBldr()
        
    stTxtPara.Contents = bldr.GetString()

def setTextMetaData(DB, text):

    # Set the Source field
    tss = TsStringUtils.MakeString('FLExTrans', DB.project.DefaultAnalWs)
    text.Source.AnalysisDefaultWritingSystem = tss

    # Set the IsTranslated field
    text.IsTranslated = True

def InitControls(self, export=True, fromFLEx=False):
    
    self.chapSel = None
    self.retVal = False
    
    self.ui.OKButton.clicked.connect(self.OKClicked)
    self.ui.CancelButton.clicked.connect(self.CancelClicked)

    # Set initial window size. Import doesn't change it (but in ClusterUtils height is saved), but export to ptx and export from flex do.
    self.otherProj = ''
    self.resize(ClusterUtils.IMP_EXP_WINDOW_WIDTH, ClusterUtils.IMP_EXP_WINDOW_HEIGHT)
    
    # Load settings if available
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add the settings file
        self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), PTXIMPORT_SETTINGS_FILE)
        
        f = open(self.settingsPath, 'r')
        myMap = json.load(f)
        f.close()
    except:
        myMap = {}
        
    # Set the project edit box to either the export or import project.
    # Save the other one as otherProj so we can write it out again to the settings file.
    if export:
        self.ui.ptxProjAbbrevLineEdit.setText(myMap.get('exportProjectAbbrev',''))
        self.otherProj = myMap.get('importProjectAbbrev','')
    else:
        self.ui.ptxProjAbbrevLineEdit.setText(myMap.get('importProjectAbbrev',''))
        self.otherProj = myMap.get('exportProjectAbbrev','')
        
    self.ui.bookAbbrevLineEdit.setText(myMap.get('bookAbbrev',''))
    self.ui.fromChapterSpinBox.setValue(myMap.get('fromChap',1))
    self.ui.toChapterSpinBox.setValue(myMap.get('toChap',1))
    self.ui.footnotesCheckBox.setChecked(myMap.get('includeFootnotes',False))
    self.ui.crossrefsCheckBox.setChecked(myMap.get('includeCrossRefs',False))
    self.ui.makeActiveTextCheckBox.setChecked(myMap.get('makeActive',True))
    self.ui.useFullBookNameForTitleCheckBox.setChecked(myMap.get('useFullBookName',True))
    self.ui.oneTextPerChapterCheckBox.setChecked(myMap.get('oneTextPerChapter',False))
    self.ui.includeIntroCheckBox.setChecked(myMap.get('includeIntro',False))
    self.ui.overwriteExistingTextCheckBox.setChecked(myMap.get('overwriteText',False)) 

    # Change widgets if we are doing export
    if export:

        # Hide the checkboxes
        self.ui.footnotesCheckBox.setVisible(False)
        self.ui.crossrefsCheckBox.setVisible(False)
        self.ui.makeActiveTextCheckBox.setVisible(False)
        self.ui.useFullBookNameForTitleCheckBox.setVisible(False)
        self.ui.oneTextPerChapterCheckBox.setVisible(False)
        self.ui.includeIntroCheckBox.setVisible(False)
        self.ui.overwriteExistingTextCheckBox.setVisible(False)
        
        pixels = EXP_SHRINK_WINDOW_PIXELS

        if fromFLEx:

            self.ui.bookAbbrevLineEdit.setVisible(False)
            self.ui.bookAbbrevLabel.setVisible(False)
            self.ui.fromChapterSpinBox.setVisible(False)
            self.ui.toChapterSpinBox.setVisible(False)
            self.ui.chapterLabel.setVisible(False)
            self.ui.toLabel.setVisible(False)

            pixels -= FROM_FLEX_EXP_PIXELS

        # Resize the main window 
        self.resize(self.width(), self.height()-pixels)

        # Move controls up by pixels
        widgetsToMove = [
            self.ui.clusterProjectsLabel,
            self.ui.clusterProjectsComboBox,
            self.ui.OKButton,
            self.ui.CancelButton,
        ]
        for wid in widgetsToMove:

            wid.setGeometry(wid.x(), wid.y()-pixels, wid.width(), wid.height())

    if not fromFLEx:

        # Hide a checkbox
        self.ui.selectAllChaptersCheckbox.setVisible(False)
        self.ui.scriptureTextsComboBox.setVisible(False)
        self.ui.scriptureTextsLabel.setVisible(False)

    # Initialize cluster projects (for import and from FLEx export)
    if (export == False or (export == True and fromFLEx == True)) and len(self.clusterProjects) > 0:

        ClusterUtils.initClusterProjects(self, self.clusterProjects, myMap.get('clusterProjects', []), self.ui.centralwidget)

        # Make ptx project selections in all visible combo boxes
        ptxProjList = myMap.get('ptxProjList', [])

        for i, ptxProj in enumerate(ptxProjList):

            if i < len(self.keyWidgetList):
                self.keyWidgetList[i].setCurrentText(ptxProj)
    else:
        # Hide cluster project widgets
        widgetsToHide = [
            self.ui.clusterProjectsLabel,
            self.ui.clusterProjectsComboBox,
        ]
        for wid in widgetsToHide:

            wid.setVisible(False)

    if fromFLEx:

        # Setup the checkable combo box for scripture text. ***Replace*** the one from the designer tool.
        geom = self.ui.scriptureTextsComboBox.geometry() # same as old control
        self.ui.scriptureTextsComboBox.hide()
        self.ui.scriptureTextsComboBox = CheckableComboBox(self.ui.centralwidget)
        geom.moveTo(geom.x(), self.ui.clusterProjectsComboBox.geometry().y()-30)  # move above cluster projects
        self.ui.scriptureTextsComboBox.setGeometry(geom)
        self.ui.scriptureTextsComboBox.setObjectName("scriptureTextsComboBox")
        self.ui.scriptureTextsComboBox.addItems([title for title in self.scriptureTitles if title])

        wid = self.ui.scriptureTextsLabel
        wid.setGeometry(wid.x(), self.ui.clusterProjectsComboBox.geometry().y()-30, wid.width(), wid.height())

        geom = self.ui.selectAllChaptersCheckbox.geometry()
        geom.moveTo(geom.x(), self.ui.clusterProjectsComboBox.geometry().y()-60)
        self.ui.selectAllChaptersCheckbox.setGeometry(geom)

        # Connect a custom signal to a function
        self.ui.scriptureTextsComboBox.itemCheckedStateChanged.connect(self.titlesSelectionChanged)

def getParatextPath():

    # Get the Paratext path from the registry
    aKey = r"SOFTWARE\Wow6432Node\Paratext\8"
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    aKey = winreg.OpenKey(aReg, aKey)
    paratextPathTuple = winreg.QueryValueEx(aKey, "Settings_Directory")
    return paratextPathTuple[0]
    
    
def doOKbuttonValidation(self, export=True, checkBookAbbrev=True, checkBookPath=True, fromFLEx=False):
    
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
    includeIntro = self.ui.includeIntroCheckBox.isChecked()
    overwriteText = self.ui.overwriteExistingTextCheckBox.isChecked()
   
    ptxProjList = []

    if export == False or (export == True and fromFLEx == True):

        # Go through each visible Paratext combobox and get the value
        for myCombo in self.keyWidgetList:

            ptxProjList.append(myCombo.currentText())

    ## Validate some stuff
    
    # Check if the book is valid
    if checkBookAbbrev and bookAbbrev not in bookMap:
        
        QMessageBox.warning(self, 'Invalid Book Error', f'The book abbreviation: {bookAbbrev} is invalid.')
        return
    
    # Get the Paratext path
    paratextPath = getParatextPath()

    # Check if Paratext path exists
    if not os.path.exists(paratextPath):
        
        QMessageBox.warning(self, 'Not Found Error', f'Could not find the Paratext path: {paratextPath}.')
        return

    # If we have cluster projects, we don't check a couple of these things, error checking will have to be done for each project
    if export or self.ui.clusterProjectsComboBox.isHidden() or len(self.ui.clusterProjectsComboBox.currentData()) == 0:

        # Check if project path exists under Paratext
        projPath = os.path.join(paratextPath, projectAbbrev)
        if not os.path.exists(projPath):
            
            QMessageBox.warning(self, 'Not Found Error', f'Could not find that project at: {projPath}.')
            return

        if not fromFLEx:

            # Check if the book exists
            bookPath = os.path.join(projPath, '*' + bookAbbrev + projectAbbrev + '.SFM')
            
            fileList = glob.glob(bookPath)
            
            if checkBookPath and len(fileList) < 1:
                
                QMessageBox.warning(self, 'Not Found Error', f'Could not find that book file at: {bookPath}.')
                return

    if self.ui.clusterProjectsComboBox.isHidden():
        clustProjs = []
    else:
        clustProjs = self.ui.clusterProjectsComboBox.currentData()

    self.chapSel = ChapterSelection(export, self.otherProj, projectAbbrev, bookAbbrev, paratextPath, fromChap, toChap, includeFootnotes, includeCrossRefs, \
                                    makeActive, useFullBookName, overwriteText, clustProjs, ptxProjList, oneTextPerChapter, includeIntro)
    
    # Save the settings to a file so the same settings can be shown next time
    f = open(self.settingsPath, 'w')
    
    dumpMap = self.chapSel.dump()
    json.dump(dumpMap, f, indent=4)
    
    f.close()
    
    self.retVal = True
    self.close()

def getFilteredSubdirectories(rootDir, excludeList):
    """
    Get a list of first-level subdirectories in rootDir, excluding those in excludeList or
    those that start with '_' or 'UserSettings'.
    """
    subdirectories = []
    
    for dirname in os.listdir(rootDir):

        dirpath = os.path.join(rootDir, dirname)

        if os.path.isdir(dirpath):

            if (dirname not in excludeList and not dirname.startswith('_') and not dirname.startswith('UserSettings')):
                
                subdirectories.append(dirname)

    return subdirectories

def getParatextProjects():

    excludeList = [
        'cms',
        'Temp Files',
    ]
    ptxProjs = getFilteredSubdirectories(getParatextPath(), excludeList)

    return ptxProjs

def getScriptureText(report, textTitles):
    """
    Filters textTitles to match the criteria:
    - The book has to start with either an abbreviation or name that matches the dictionary bookMap.
    - The title will have a space and a two-digit chapter number and optionally a '-' and another two-digit chapter number.

    Parameters:
    - report: The report object for reporting.
    - textTitles: List of text titles to filter.

    Returns:
    - A list of filtered text titles.
    """
    filteredTitles = []

    for title in textTitles:

        match = bookChapterPattern.match(title)

        if match:

            book = match.group('book')
            chap1 = match.group('chap1')
            chap2 = match.group('chap2')

            if book in bookMap or book in bookMap.values():
                
                filteredTitles.append(title)

    return sorted(filteredTitles)

def doExport(textContents, report, chapSelectObj, parent):
    
    # Find all the chapter #s
    myChapList = re.findall(r'\\c (\d+)', textContents, flags=re.RegexFlag.DOTALL)
    
    # Check that we have chapters in the syn. file
    if len(myChapList) < 1:

        report.Error(f'No chapters found in the text.')
        return None
    
    elif len(myChapList) > 1:
    
        chapStr = 'chapters'
        digitsStr = myChapList[0]+'-'+myChapList[-1]
    else:
        chapStr = 'chapter'
        digitsStr = myChapList[0]

    # Prompt the user to be sure they want to replace these chapters.
    if not chapSelectObj.dontShowWarning:

        # Create a QMessageBox instance
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(f'Are you sure you want to overwrite {chapStr} {digitsStr} of {bookMap[chapSelectObj.bookAbbrev]} in the {chapSelectObj.exportProjectAbbrev} project?')
        msgBox.setWindowTitle("Overwrite chapters")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        # Add checkbox to the QMessageBox if we have multiple projects
        if len(chapSelectObj.clusterProjects) > 0:

            checkBox = QCheckBox("Do not show this message again.")
            msgBox.setCheckBox(checkBox)
        
        # Display the message box and wait for user interaction
        ret = msgBox.exec_()
        
        # Check if the checkbox was checked
        if len(chapSelectObj.clusterProjects) > 0 and checkBox.isChecked():

            chapSelectObj.dontShowWarning = True

        if ret == QMessageBox.No:

            report.Info('Export cancelled.')
            return None
        
    bookPath = chapSelectObj.getBookPath()

    if not bookPath:

        report.Error(f'Could not find the book file: {bookPath}')
        return None
    
    # Create a backup of the paratext file
    copyfile(bookPath, bookPath+'.bak')
    
    # Read the Paratext file
    with open(bookPath, encoding='utf-8') as f:
    
        bookContents = f.read()
    
    # Find all the chapter #s
    ptxChapList = re.findall(r'\\c (\d+)', bookContents, flags=re.RegexFlag.DOTALL)
    
    # Split the synthesis contents into chapter chunks
    synContentsList = re.split(r'(\\c \d+)', textContents, flags=re.RegexFlag.DOTALL) # gives us [\c 1, \s ..., \c 2, \s ..., ...]
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
        if myChapList[n//2] in ptxChapList:
            
            # If we have intro stuff to put in chapter 1, start the regex at \mt if it exists.
            if n == 1 and haveIntro:

                begRE = r'(\\mt.+\\c 1|\\c 1)'
            else:
                begRE = r'\\c ' + myChapList[n//2]
            
            # See if this is the last paratext chapter
            if myChapList[n//2] == ptxChapList[-1]:
                
                endRE = r'\s.+'
                replExtra = ''
            else:
                endRE = r'\s.+?\\c' # non-greedy match
                replExtra = '\\c'
        else:
            found = False
            
            # Find the next chapter # in the list
            for i, ptxCh in enumerate(ptxChapList):
                
                if int(myChapList[n//2]) < int(ptxCh):
                    
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

    # Report what got exported
    report.Info(f'{chapStr.capitalize()} {digitsStr} of {bookMap[chapSelectObj.bookAbbrev]} exported to the {chapSelectObj.exportProjectAbbrev} project.')

    return 1
    
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
'GLO':'Glossary',\
}

