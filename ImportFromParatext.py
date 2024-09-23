#
#   ImportFromParatext
#
#   Ron Lockwood
#   SIL International
#   10/30/21
#
#   Version 3.11.3 - 9/23/24 - Ron Lockwood
#    Make segments for every linefeed instead for certain sfms.
#
#   Version 3.11.2 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.1 - 8/16/24 - Ron Lockwood
#    Fix silently closing when TextIn/Out settings are missing.
#
#   Version 3.11 - 8/15/24 - Ron Lockwood
#    Support FLEx Alpha 9.2.2 which no longer supports Get Instance, use Get Service instead.
#
#   Version 3.10.7 - 8/2/24 - Ron Lockwood
#    Use new function num Rules to get the number of rules.
#
#   Version 3.10.6 - 8/2/24 - Ron Lockwood
#    Don't need to add paragraph marks anymore.
#
#   Version 3.10.5 - 7/8/24 - Ron Lockwood
#    Use new Text In search/replace rules.
#
#   Version 3.10.2 - 3/19/24 - Ron Lockwood
#    Fixes #566. Allow the user to create one text per chapter when importing.
#
#   Version 3.10.1 - 3/8/24 - Ron Lockwood
#    Don't add space before a marker.
#
#   Version 3.10 - 1/4/24 - Ron Lockwood
#    Fixes #536. support . for chapter verse separator. Make all between \xt and \x* the analysis WS.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.2 - 5/3/23 - Ron Lockwood
#    Refresh the status bar if they chose to use the new text as the active text.
#
#   Version 3.8.1 - 5/3/23 - Ron Lockwood
#    Put the paragraph mark after section markers and quote markes that have a number (e.g. q1)
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7.5 - 3/1/23 - Ron Lockwood
#    Determine uppercase for the section mark feature by looking for the first
#    non-blank vernacular segment.
#
#   Version 3.7.4 - 2/28/23 - Ron Lockwood
#    Put section marks after verses and quote markers
#
#   Version 3.7.3 - 1/30/23 - Ron Lockwood
#    Restructured to put common init and exit code into ChapterSelection.py
#    Store export project and import project as separate settings.
#
#   Version 3.7.2 - 1/25/23 - Ron Lockwood
#    Fixes #173 and #190. Give user choice to exclude \x..\x* and \r... Handle
#    verse bridges like \v 3-4. Handle \vp 3-4 or \vp 2
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

import os
import re
import sys
from shutil import copyfile
import xml.etree.ElementTree as ET

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils

from flextoolslib import *                                                 
from flexlibs import FLExProject, AllProjectNames

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication

import FTPaths
import ReadConfig
import Utils
import ChapterSelection
import TextInOutUtils
from ParatextChapSelectionDlg import Ui_MainWindow

#----------------------------------------------------------------
# Configurables:
PTXPATH = 'C:\\My Paratext 8 Projects'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Import Text From Paratext",
        FTM_Version    : "3.11.3",
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

class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.toChap = self.fromChap = 0
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.ui.fromChapterSpinBox.valueChanged.connect(self.FromSpinChanged)
        self.ui.toChapterSpinBox.valueChanged.connect(self.ToSpinChanged)
        
        self.setWindowTitle("Import Paratext Chapters")

        # Get stuff from a paratext import/export settings file and set dialog controls as appropriate
        ChapterSelection.InitControls(self, export=False)

        self.enableOneTextPerChapter()

    def CancelClicked(self):
        self.retVal = False
        self.close()

    # If more than 1 chapter, enable the one text per chapter checkbox
    def enableOneTextPerChapter(self):

        if self.toChap - self.fromChap > 0:
            self.ui.oneTextPerChapterCheckBox.setEnabled(True)
        else:
            self.ui.oneTextPerChapterCheckBox.setEnabled(False)
            self.ui.oneTextPerChapterCheckBox.setChecked(False)

    def FromSpinChanged(self):
        
        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()

        # if from chapter is greater than the to chapter, change the to chapter to match
        if self.fromChap > self.toChap:
            
            self.ui.toChapterSpinBox.setValue(self.fromChap)
            self.toChap = self.fromChap

        self.enableOneTextPerChapter()

    def ToSpinChanged(self):
        
        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()

        # if to chapter is less than the from chapter, change the from chapter to match
        if self.toChap < self.fromChap:
            
            self.ui.fromChapterSpinBox.setValue(self.toChap)
            self.fromChap = self.toChap
            
        self.enableOneTextPerChapter()

    def OKClicked(self):

        ChapterSelection.doOKbuttonValidation(self, export=False)
        
def setSourceNameInConfigFile(report, title):
        
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myConfig = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), ReadConfig.CONFIG_FILE)
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

def do_import(DB, report, chapSelectObj, tree):
    
    copyUntilEnd = False
    firstTitle = None
    byChapterList = []

    # Open the Paratext file and read the contents
    f = open(chapSelectObj.bookPath, encoding='utf-8')
    bookContents = f.read()
    
    # Find all the chapter #s
    chapList = re.findall(r'\\c (\d+)', bookContents, flags=re.RegexFlag.DOTALL)
    
    # Give error if we can't find the starting chapter
    if str(chapSelectObj.fromChap) not in chapList:
        
        report.Error('Starting chapter not found.')
        return
    
    # If the user wants full name, look it up
    if chapSelectObj.useFullBookName:
        
        bibleBook = ChapterSelection.bookMap[chapSelectObj.bookAbbrev]
    else:
        bibleBook = chapSelectObj.bookAbbrev

    # Create the text object factories
    m_textFactory = DB.project.ServiceLocator.GetService(ITextFactory)
    m_stTextFactory = DB.project.ServiceLocator.GetService(IStTextFactory)
    m_stTxtParaFactory = DB.project.ServiceLocator.GetService(IStTxtParaFactory)

    # Check if the toChapter is there. If not set the end chapter and set a flag.
    if str(chapSelectObj.toChap+1) not in chapList:
        
        copyUntilEnd = True
        
        if len(chapList) > 0:
            chapSelectObj.toChap = int(chapList[-1])
    
    # Build the search regex. It starts the search at the fromChapter
    reStr = fr'(\\c {str(chapSelectObj.fromChap)}\s.+?)'
    
    # The expression ends with the end of the book contents if we need to
    if copyUntilEnd:
        
        reStr += '$'

    # Otherwise the expression ends at the toChapter
    else:
        reStr += fr'\\c {str(chapSelectObj.toChap+1)}\s'

    # Get the results
    matchObj = re.search(reStr, bookContents, flags=re.RegexFlag.DOTALL)
    importText = matchObj.group(1)
    
    # Remove newlines
    #importText = re.sub(r'\n', '', importText)
        
    # Do user-defined search/replace rules if needed
    if tree:

        importText, errMsg = TextInOutUtils.applySearchReplaceRules(importText, tree)

        if importText is None:

            report.Error(errMsg)
            return
        else:
            report.Info(f"{str(TextInOutUtils.numRules(tree))} 'Text In' rules applied.")
            
    # Remove footnotes if necessary
    if chapSelectObj.includeFootnotes == False:
        
        importText = re.sub(r'\\f.+?\\f\*', '', importText)
    
    # Remove \x & \r cross references if desired by the user
    if chapSelectObj.includeCrossRefs == False:
        
        importText = re.sub(r'\\x.+?\\x\*', '', importText)
        importText = re.sub(r'\\r.+?\\p', r'\\p', importText) # assume a \p directly follows a \r

    # If the user wants one text per chapter, split the text on chapters
    if chapSelectObj.oneTextPerChapter == True:
    
        # This gives us something like: ['', '\\c 3', ' blah blah. ', '\\c 4', ' \\v 1 bkbk end.']
        tempChapterList = re.split(r'(\\c \d+)', importText)

        # Put the \\c list elements back together with their respective contents
        for i in range(1, len(tempChapterList), 2):

            byChapterList.append(tempChapterList[i] + tempChapterList[i+1])

    # Otherwise treat as one chapter (going to one text)
    else:
        byChapterList = [importText]

    # Set the starting chapter number for the title which may get incremented
    titleChapNum = chapSelectObj.fromChap

    # Loop through each 'chapter'
    for chapterContent in byChapterList:

        # Create a text and add it to the project      
        text = m_textFactory.Create()           
        stText = m_stTextFactory.Create()
        
        # Set StText object as the Text contents
        text.ContentsOA = stText  
    
        # Split the text into sfm marker (or ref) and non-sfm marker (or ref), i.e. text contenct. The sfm marker or reference will later get marked as analysis lang. so it doesn't
        # have to be interlinearized. Always put the marker + ref with dash before the plain marker + ref. \\w+* catches all end markers and \\w+ catches everything else (it needs to be at the end)
        # We have the \d+:\d+-\d+ and \d+:\d+ as their own expressions to catch places in the text that have a verse reference like after a \r or \xt. It's nice if these get marked as analysis WS.
        # You can't have parens inside of the split expression since it is already in parens. It will mess up the output.

        #                  end mrk footnt  footnt ref+dash     footnt ref      cr ref note   cr ref  cr ref orig+dash    cr ref orig     verse+dash   verse    pub verse chap    ref+dash       ref     any marker
        segs = re.split(r'(\\\w+\*|\\f \+ |\\fr \d+[:.]\d+-\d+|\\fr \d+[:.]\d+|\\xt .+?\\x\*|\\x \+ |\\xo \d+[:.]\d+-\d+|\\xo \d+[:.]\d+|\\v \d+-\d+ |\\v \d+ |\\vp \S+ |\\c \d+|\d+[:.]\d+-\d+|\d+[:.]\d+|\\\w+)', chapterContent) 

        # Create 1st paragraph object
        stTxtPara = m_stTxtParaFactory.Create()
        
        # Add it to the stText object
        stText.ParagraphsOS.Add(stTxtPara)    

        bldr = TsStringUtils.MakeStrBldr()

        # See if we have a script that has both upper and lower case. 
        if len(segs) >= 2:
            
            # Find a non-zero segment vernacular string (an even numbered index)
            for i in range(2, len(segs), 2):
                
                if len(segs[i]) > 0:
                
                    # if the lower case is equal to the upper case, assume this script has no upper case
                    if segs[i].lower() == segs[i].upper():
                        
                        upperCase = False
                    else:
                        upperCase = True
                        
                    break
        
        # SFMs to start a new paragraph in FLEx
        #newPar = r'\\[cpsqm]'
        newPar = r'\n' # just start a new paragraph at every line feed
        
        for _, seg in enumerate(segs):
            
            if not (seg is None or len(seg) == 0 or seg == '\n'):
                
                # Either an sfm marker or a verse ref should get marked as Analysis WS
                if re.search(r'\\|\d+[.:]\d+', seg):
                    
                    # make this in the Analysis WS
                    tss = TsStringUtils.MakeString(re.sub(r'\n','', seg), DB.project.DefaultAnalWs)
                    bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)
                    
                else:
                    # make this in the Vernacular WS
                    tss = TsStringUtils.MakeString(seg.rstrip(), DB.project.DefaultVernWs)
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

        # Build the title string from book abbreviation and chapter.
        title = bibleBook + ' ' + str(titleChapNum).zfill(2)
        
        # Possibly add to the title if we are putting multiple chapters into one text
        if chapSelectObj.oneTextPerChapter == False:

            if chapSelectObj.fromChap < chapSelectObj.toChap:
                
                #  E.g. EXO 03-04
                title += '-' + str(chapSelectObj.toChap).zfill(2)

        # Use new file name if the current one exists. E.g. PSA 01-03, PSA 01-03 - Copy, PSA 01-03 - Copy (2)
        title = Utils.createUniqueTitle(DB, title)
        
        if firstTitle == None:

            firstTitle = title
            
        # Set the title of the text
        tss = TsStringUtils.MakeString(title, DB.project.DefaultAnalWs)
        text.Name.AnalysisDefaultWritingSystem = tss
        
        report.Info('Text: "'+title+'" created.')

        titleChapNum += 1
        
    # Make this new text (or the first of the series) the active text for FLExTrans if necessary
    if chapSelectObj.makeActive:
        
        setSourceNameInConfigFile(report, firstTitle)
        FTPaths.CURRENT_SRC_TEXT = firstTitle

        # Have FlexTools refresh the status bar
        refreshStatusbar()
    
def MainFunction(DB, report, modify=True):
    
    tree = None

    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

   # Get the path to the search-replace rules file
    textInRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TEXT_IN_RULES_FILE, report, giveError=False)

    if textInRulesFile is not None:
    
        # Check if the file exists.
        if os.path.exists(textInRulesFile) == True:

            # Verify we have a valid transfer file.
            try:
                tree = ET.parse(textInRulesFile)
            except:
                report.Error(f'The rules file: {textInRulesFile} has invalid XML data.')
                return

    # Show the window
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()
    
    if window.retVal == True:
        
        do_import(DB, report, window.chapSel, tree)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
