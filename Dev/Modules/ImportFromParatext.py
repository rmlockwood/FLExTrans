#
#   ImportFromParatext
#
#   Ron Lockwood
#   SIL International
#   10/30/21
#
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14 - 5/17/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.4 - 5/29/25 - Sara Mason
#   Fixes #997 Allows the user to choose if they want to overwrite all selected chapters, from the one message box.
#
#   Version 3.13.3 - 5/17/25 - Sara Mason
#   Fixes #973 Warns the user not to be in the Text & Words section when overwriting a text.
#
#   Version 3.13.2 - 4/25/25 - Ron Lockwood
#    Fixes #969. Convert \fig data to the new USFM 3.0 syntax. This helps make the vernacular part - the caption -
#    which the first thing in the new format easy to identify.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.9 - 2/20/25 - Ron Lockwood
#    Fixes #900. Prevent from chapter changing to single digit.
#    Don't do the logic of keeping the from chapter less than the to chapter until the user
#    finishes editing the to chapter box.
#
#   Version 3.12.8 - 1/23/25 - Ron Lockwood
#    Support import of Glossary book (GLO).
#
#   Version 3.12.7 - 1/13/25 - Ron Lockwood
#    Fixes crash on import with no cluster projects.
#
#   Version 3.12.6 - 12/31/24 - Ron Lockwood
#    Fixes #830. Validate project abbreviation only if we are not using cluster projects.
#    Revamp what we do before calling do_import and have do_import build the full path to the book.
#
#   Version 3.12.5 - 12/30/24 - Ron Lockwood
#    Fixes #742. Set the IsTranslated and Source metadata fields for the new text.
#
#   Version 3.12.4 - 12/30/24 - Ron Lockwood
#    Move dynamic widget creation and display to Cluster Utils.
#
#   Version 3.12.3 - 12/24/24 - Ron Lockwood
#    Support cluster project importing.
#
#   Version 3.12.2 - 12/4/24 - Ron Lockwood
#    Fixes #823. Use the same logic that's in the Import from Ptx module to mark sfms as analysis writing system.
#
#   Version 3.12.1 - 11/26/24 - Ron Lockwood
#    Allow intro. to be imported with chapter 1.
#    Fixed bug with excluding \r by using DOTALL
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.6 - 10/8/24 - Ron Lockwood
#    Treat attribute stuff from | to \xx* as analysis WS.
#
#   Version 3.11.5 - 10/4/24 - Ron Lockwood
#    Handle \+zz style markers, i.e. they start with a +.
#
#   Version 3.11.4 - 9/23/24 - Ron Lockwood
#    Fix to previous linefeed change to not delete trailing spaces.
#    Book names before references need to retain their spaces.
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
#   earlier version history removed on 1/13/25
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

from SIL.LCModel import ( # type: ignore
    ITextFactory,
    IStTextFactory,
    IStTxtParaFactory,
    ITextRepository,
)
from SIL.LCModel.Core.Text import TsStringUtils # type: ignore

from flextoolslib import *                                                 
from PyQt5 import QtGui
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QMessageBox, QCheckBox
from PyQt5.QtGui import QIcon

import ClusterUtils
import Mixpanel
import ReadConfig
import FTPaths
import Utils
from ParatextChapSelectionDlg import Ui_ParatextChapSelectionWindow
import ChapterSelection
import TextInOutUtils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'ImportFromParatext'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'ParatextChapSelectionDlg', 'ChapterSelection', 'TextInOutUtils'] 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : _translate("ImportFromParatext", "Import Text From Paratext"),
        FTM_Version    : "3.14.2",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("ImportFromParatext", "Import chapters from Paratext."),
        FTM_Help       : "",
        FTM_Description: _translate("ImportFromParatext", 
"""This module asks you which Paratext project, which book and which chapters should be 
imported. The book name should be given as a three-letter abbreviation just like in
Paratext. Those chapters are gathered and inserted into the current FLEx project as a 
new text. If you want to include various things, click the appropriate check box. 
If you want to use the full name of the book in the text name, instead of the abbreviation, click the check box. 
If you want to make the newly imported text, the active text in FLExTrans click the check box.
Importing into multiple FLEx projects from multiple Paratext projects is possible. First select your
cluster projects in the main FLExTrans Settings, then come back to this module.""")}

#app.quit()
#del app

#----------------------------------------------------------------
# The main processing function

# Tuple of 3 items
replaceList = [\
               #('Name', 'find_str', 'rpl_str'),\
              ]

class Main(QMainWindow):

    def __init__(self, clusterProjects):
        QMainWindow.__init__(self)

        self.ui = Ui_ParatextChapSelectionWindow()
        self.clusterProjects = clusterProjects
        self.ui.setupUi(self)
        self.toChap = 0
        self.fromChap = 0
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setWindowTitle("Import Paratext Chapters")

        header1TextStr = "FLEx project name"
        header2TextStr = "Paratext project abbrev."
        self.ptxProjs = ChapterSelection.getParatextProjects()

        # Set the top two widgets that need to be disabled
        self.topWidget1 = self.ui.ptxProjAbbrevLineEdit
        self.topWidget2 = self.ui.label

        # Create all the possible widgets we need for all the cluster projects
        ClusterUtils.initClusterWidgets(self, QComboBox, self.ui.horizontalLayout_7, header1TextStr, header2TextStr, 100, self.fillPtxCombo)

        # Get stuff from a paratext import/export settings file and set dialog controls as appropriate
        ChapterSelection.InitControls(self, export=False)

        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()
        self.enableOneTextPerChapter()
        self.enableIncludeIntro()

        self.ui.fromChapterSpinBox.valueChanged.connect(self.FromSpinChanged)
        self.ui.toChapterSpinBox.valueChanged.connect(self.ToSpinChanged)
        self.ui.toChapterSpinBox.editingFinished.connect(self.ToSpinEditFinish)

    def fillPtxCombo(self, comboWidget):

        # Fill the combo box
        comboWidget.addItems(['...'] + self.ptxProjs)
    
    def clusterSelectionChanged(self):

        ClusterUtils.showClusterWidgets(self)

    def CancelClicked(self):
        self.retVal = False
        self.close()

    def enableIncludeIntro(self):

        if self.fromChap == 1:
            self.ui.includeIntroCheckBox.setEnabled(True)
        else:
            self.ui.includeIntroCheckBox.setEnabled(False)
            self.ui.includeIntroCheckBox.setChecked(False)

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
        self.enableIncludeIntro()

    def ToSpinEditFinish(self):

        # if to chapter is less than the from chapter, change the from chapter to match
        if self.toChap < self.fromChap:
            
            self.ui.fromChapterSpinBox.setValue(self.toChap)
            self.fromChap = self.toChap
            
    def ToSpinChanged(self):
        
        self.fromChap = self.ui.fromChapterSpinBox.value()
        self.toChap = self.ui.toChapterSpinBox.value()

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
        report.Error(_translate("ImportFromParatext", "Could not open the configuration file: {myConfig}").format(myConfig=myConfig)) 
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

    bookPath = chapSelectObj.getBookPath()

    if not bookPath:

        report.Error(_translate("ImportFromParatext", "Could not find the book file: {bookPath}").format(bookPath=bookPath))
        return
    
    # Open the Paratext file and read the contents
    with open(bookPath, encoding='utf-8') as f:

        bookContents = f.read()
    
    # Find all the chapter #s
    chapList = re.findall(r'\\c (\d+)', bookContents, flags=re.RegexFlag.DOTALL)
    
    # Give error if we can't find the starting chapter
    if str(chapSelectObj.fromChap) not in chapList:
        
        report.Error(_translate("ImportFromParatext", "Starting chapter not found."))
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
    
    # See if we should include intro material
    if chapSelectObj.includeIntro:

        # Build the search regex. It starts the search at \mt. This will work if the first title is \mt2 or \mt1, etc.
        reStr = fr'(\\mt.+?)'

        if not re.search(reStr, bookContents):

            report.Error(_translate("ImportFromParatext", "Cannot find main title (\\mt or \\mtN). This is needed for importing introductory material."))
            return
    else:
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

    # Check for nothing found
    if not matchObj:

        report.Error(_translate("ImportFromParatext", "Cannot find the range of chapters specified."))
        return

    importText = matchObj.group(1)
    
    # Do user-defined search/replace rules if needed
    if tree:

        importText, errMsg = TextInOutUtils.applySearchReplaceRules(importText, tree)

        if importText is None:

            report.Error(errMsg)
            return
        else:
            report.Info(_translate("ImportFromParatext", "{numRules} 'Text In' rules applied.").format(numRules=str(TextInOutUtils.numRules(tree))))
            
    # Convert old USFM 1.0 or 2.0 \fig syntax to 3.0
    # old format: \fig DESC|FILE|SIZE|LOC|COPY|CAP|REF\fig*
    # new format: \\fig CAP|alt="DESC" src="FILE" size="SIZE" loc="LOC" copy="COPY" ref="REF"\\fig*
    importText = re.sub(r'\\fig ([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\\fig\*', r'\\fig \6|alt="\1" src="\2" size="\3" loc="\4" copy="\5" ref="\7"\\fig*', importText)

    # Remove footnotes if necessary
    if chapSelectObj.includeFootnotes == False:
        
        importText = re.sub(r'\\f.+?\\f\*', '', importText)
    
    # Remove \x & \r cross references if desired by the user
    if chapSelectObj.includeCrossRefs == False:
        
        importText = re.sub(r'\\x.+?\\x\*', '', importText)
        importText = re.sub(r'\\r\s.+?\\p', r'\\p', importText, flags=re.DOTALL) # assume a \p directly follows a \r

    # If the user wants one text per chapter, split the text on chapters
    if chapSelectObj.oneTextPerChapter == True:
    
        # This gives us something like: ['', '\\c 3', ' blah blah. ', '\\c 4', ' \\v 1 bkbk end.']
        tempChapterList = re.split(r'(\\c \d+)', importText)

        # Put the \\c list elements back together with their respective contents
        for i in range(1, len(tempChapterList), 2):

            # If including intro and we have chapter 1, add intro portion before chapter 1 marker and text
            if chapSelectObj.includeIntro and i == 1 and tempChapterList[i] == '\\c 1':

                byChapterList.append(tempChapterList[0] + tempChapterList[i] + tempChapterList[i+1])
            else:
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
    
        ChapterSelection.insertParagraphs(DB, chapterContent, m_stTxtParaFactory, stText)

        # Build the title string from book abbreviation and chapter.
        title = "{bibleBook} {chapter}".format(bibleBook=bibleBook, chapter=str(titleChapNum).zfill(2))
        title += "-{toChap}".format(toChap=str(chapSelectObj.toChap).zfill(2)) if chapSelectObj.oneTextPerChapter == False and chapSelectObj.fromChap < chapSelectObj.toChap else ""

        # If the user wants to overwrite the existing text, remind them not to be in the Text and Words section. 
        if chapSelectObj.overwriteText and not chapSelectObj.overwriteAllChapters:
            
            # Create a QMessageBox instance 
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
            msgBox.setText(_translate("ImportFromParatext",
            'The option to overwrite the text in FLEx was chosen. If FLEx is open, make sure you are NOT in the Text & Words section of FLEx.\n\nAre you sure you want to continue with overwriting the text in FLEx?'))
            msgBox.setWindowTitle(_translate("ImportFromParatext", "Overwriting FLEx text"))
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            checkbox = QCheckBox(_translate("ImportFromParatext", "Overwrite all selected chapters"))
            msgBox.setCheckBox(checkbox)

            # Display the message box and wait for user interaction
            ret = msgBox.exec_()
            if ret == QMessageBox.Yes:
                    chapSelectObj.confirmContinueOverwrite = True

            # Check if the user wants to overwrite all chapters
            if checkbox.isChecked():
                chapSelectObj.overwriteAllChapters = True

        #check if overwriteText is true, and the confirmation from the messagebox is also true
        if chapSelectObj.overwriteText and chapSelectObj.confirmContinueOverwrite:

            # Find the text
            for interlinText in DB.ObjectsIn(ITextRepository):

                if title == Utils.as_string(interlinText.Name).strip():
                    
                    # Delete it
                    interlinText.Delete()
                    break
        else:
            # Use new file name if the current one exists. E.g. PSA 01-03, PSA 01-03 - Copy, PSA 01-03 - Copy (2)
            title = Utils.createUniqueTitle(DB, title)
        
        if firstTitle == None:

            firstTitle = title
            
        # Set the title of the text
        tss = TsStringUtils.MakeString(title, DB.project.DefaultAnalWs)
        text.Name.AnalysisDefaultWritingSystem = tss

        # Set metadata for the text
        ChapterSelection.setTextMetaData(DB, text)

        report.Info(_translate("ImportFromParatext", "Text: \"{title}\" created in the {projectName} project.").format(title=title, projectName=DB.ProjectName()))

        titleChapNum += 1
        
    # Make this new text (or the first of the series) the active text for FLExTrans if necessary
    if chapSelectObj.makeActive:
        
        setSourceNameInConfigFile(report, firstTitle)
        FTPaths.CURRENT_SRC_TEXT = firstTitle

        # Have FlexTools refresh the status bar
        refreshStatusbar()
    
def MainFunction(DB, report, modify=True):
    
    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)
    tree = None

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
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
                report.Error(_translate("ImportFromParatext", "The rules file: {textInRulesFile} has invalid XML data.").format(textInRulesFile=textInRulesFile))
                return

    # Get the cluster projects
    clusterProjects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report, giveError=False)
    if not clusterProjects:
        clusterProjects = []
    else:
        # Remove blank ones
        clusterProjects = [x for x in clusterProjects if x]
        
    window = Main(clusterProjects)
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
                    myDB = Utils.openProject(report, proj)

                # Set the import project member to the right ptx project and import it
                window.chapSel.importProjectAbbrev = window.chapSel.ptxProjList[i]
                do_import(myDB, report, window.chapSel, tree)

                # Close the project (if not the main)
                if proj != DB.ProjectName():

                    myDB.CloseProject()
        else:
            do_import(DB, report, window.chapSel, tree)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
