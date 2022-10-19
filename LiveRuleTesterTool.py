#
#   LiveRuleTesterTool
#
#   Ron Lockwood
#   SIL International
#   7/2/16
#
#   Version 3.6.8 - 10/19/22 - Ron Lockwood
#    Fixes #244. Give a warning if an attribute matches a grammatical category.
#
#   Version 3.6.7 - 9/2/22 - Ron Lockwood
#    Fixes #263. Force reload of word tooltips when Reload bilingual button clicked.
#
#   Version 3.6.6 - 9/2/22 - Ron Lockwood
#    Fixes #255. Convert slashes in symbols before running Apertium
#
#   Version 3.6.5 - 8/27/22 - Ron Lockwood
#    If the tooltip word is Title case and not found in the bilingual map, try
#    lowercasing the first letter to find it.
#
#   Version 3.6.4 - 8/19/22 - Ron Lockwood
#    Fixed bugs in last feature added. Now entries with spaces work as well as
#    entries that have sfm markers or other stuff before the lexical unit.
#    Use the new function getXMLEntryText.
#
#   Version 3.6.3 - 8/18/22 - Ron Lockwood
#    Fixes #223. Show a tooltip for each word in the Select Words (checkbox) view.
#    The tooltip display the entry or entries for the word that are found in the
#    bilingual lexicon. To do this the bilingual lexicon has to be converted to a map
#    on initialization and whenever the bilingual lexicon is rebuilt.
#
#   Version 3.6.2 - 8/11/22 - Ron Lockwood
#    Fixes #198. Warn the user for periods in attribute definitions.
#
#   Version 3.6.1 - 8/11/22 - Ron Lockwood
#    Save transfer rule file in decomposed unicode.
#
#   Version 3.6 - 8/8/22 - Ron Lockwood
#    New buttons to view/edit the bilingual lexicon, the transfer rule file and
#    the replacement file. Fixes #196
#
#   Version 3.5.10 - 7/8/22 - Ron Lockwood
#    Set Window Icon to be the FLExTrans Icon
#
#   Version 3.5.9 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.8 - 5/19/22 - Ron Lockwood
#    Close FLEx project and reopen on Rebuild Bilingual Lexicon button.
#    This clears the cache in LCM and allows the rebuild function to use the
#    latest FLEx data. Fixes #122.
#
#   Version 3.5.7 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.5.6 - 4/14/22 - Ron Lockwood
#    Give error message when no words are suggested. Fixes #109
#
#   Version 3.5.5 - 4/14/22 - Ron Lockwood
#    Turn on and off wait cursor for certain operations. Fixes #103
#
#   Version 3.5.4 - 4/1/22 - Ron Lockwood
#    Program a button to rebuild the bilingual lexicon. Fixes #37
#
#   Version 3.5.3 - 4/1/22 - Ron Lockwood
#    Save checked rules on refresh. Fixes #29
#
#   Version 3.5.2 - 4/1/22 - Ron Lockwood
#    Fixed crash on up or down button. I was incorrectly using _children for
#    ElementTree which no longer works in Python 3. Also got selecting a row
#    working. Fixes #104
#
#   Version 3.5.1 - 4/1/22 - Ron Lockwood
#    If no rule is checked, give a specific error. Instead of letting Apertium 
#    fail. Fixes #28.
#
#   Version 3.5 - 3/24/22 - Ron Lockwood
#    Save selected tabs on close to a file and rest to those on open. Bug #2.
#
#   Version 3.4.5 - 3/21/22 - Ron Lockwood
#    Handle when transfer rules file and testbed file locations are not set in
#    the configuration file. Issue #95
#
#   Version 3.4.4 - 3/17/22 - Ron Lockwood
#    Allow for a user configurable Testbed location. Issue #70.
#
#   Version 3.4.3 - 3/10/22 - Ron Lockwood
#    Get the transfer rules path from the config file
#
#   Version 3.4.2 - 3/5/22 - Ron Lockwood
#    New parameter for run_makefile for a config file setting for transfer rules.
#    Also rename err_log to apertium_log.txt and always use bilingual.dix for the
#    filename in the tester folder.
#
#   Version 3.4.1 - 3/3/22 - Ron Lockwood
#    Get the transfer_rules.t1x file from the top level
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2.5 - 3/8/21 - Ron Lockwood
#    Error checking for missing guid in XML files
#
#   Version 3.2.4 - 3/4/21 - Ron Lockwood
#    Support for discontiguous complex forms
#
#   Version 3.2.3 - 3/4/21 - Ron Lockwood
#    Support for testbed editing in the XML Editor XXE
#
#   Version 3.2.2 - 2/25/21 - Ron Lockwood
#    Support an insert word list file for extraction purposes. Get new item:
#    TreeTranInsertWordsFile from the config file. call getInsertedWordsList
#    and addInseredWordsList. Bug fix: check if we get None for the sent. object
#    for the number given. Give an error if needed.
#
#   Version 3.2.1 - 2/19/21 - Ron Lockwood
#    remove multiple spaces from synthesis result
#
#   Version 3.2 - 1/29/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 3.1.7 - 3/27/20 - Ron Lockwood
#    Handle adding sentence punctuation when using TreeTran.
#    
#   Version 3.1.6 - 3/26/20 - Ron Lockwood
#    Added the same logic as ExtractSourceText to process words in TreeTran-
#    outputted order, if TreeTran is being used.
#
#   Version 3.1.5 - 3/20/20 - Ron Lockwood
#    Use new getInterlinData function.
#
#   Version 3.1.4 - 1/30/20 - Ron Lockwood
#    On Synthesize catch if the Target DB is locked. 
# 
#   Version 3.1.3 - 4/22/19 - Ron Lockwood
#    Look at first half of text box strings to determine rtl. This prevents the
#    whole thing from being right aligned when there is just an rtl punctuation
#    mark at the end.
#
#   Version 3.1.2 - 4/5/19 - Ron Lockwood
#    Make the synthesis text box RTL only if the text going in there is RTL.
#
#   Version 3.1.1 - 3/27/19 - Ron Lockwood
#    Handle errors coming from various calls as coming in triplets instead of twos.
#    The last is a url that gets ignored. RTL fixes.
#
#   Version 3.1 - 3/30/18 - Ron Lockwood
#    Add lexical units and synthesis results to the testbed. There is an option
#    to add multiple lexical units and synthesis results if they match in number
#    this could be useful for adding a whole paradigm to the testbed. Also added
#    buttons to let the user edit the testbed or view the testbed log.
#
#   Version 3.0 - 3/30/18 - Ron Lockwood
#    Added the capability of doing a test synthesis on the results of the test
#    rules that were run. This involves running the last 4 of the main FLExTrans
#    modules from this module. Each of these 4 modules was modified to give a
#    function that this module could call. New interface elements were added.
#    most of the new capability get run when the synthesize button is pushed.
#
#   Version 2.2.1 - 2/28/18 - Ron Lockwood
#    More gracefully handle when the LiveRuleTester folder doesn't exist. Added
#    missing module description.
#
#   Version 2.2 - 1/10/18 - Ron Lockwood
#    Added the direct call to Apertium through bash. This uses the same
#    code that the RunApertium module has. Handle splitting of compounds into parts
#    just as ExtractSourceText does.
#
#   Version 2.1 - 1/2/18 - Ron
#    Display the lexical units in a more readable manner using the same style
#    as in the View Source-Target module. Fixed bug where RTL text wasn't detected
#    properly because there was sfm markers at the beginning. Now we check the 
#    first 5 sentences to find RTL text.
#
#   Version 2.0 - 1/18/17 - Ron
#    The tool now supports advanced transfer processing. When the .t2x and .t3x
#    files are present, advanced mode is enabled and the Interchunk and Postchunk
#    tabs can be used. The output from one gets copied to the input of the other
#    when the tab is changed.
#    Don't prompt the user for the transfer rules file anymore, just use the one
#    defined in the configuration file by default.
#    Copy the bilingual dictionary file and the Makefile once upon startup to the
#    LiveRuleTester folder. If the biling. dictionary changes. The tool will have
#    to be restarted or you can browse to find the file again.
#    Removed unused RuleList class.
#
#   Version 1.0.2 - 12/12/16 - Ron
#    Use contentsOA for the call to get_interlin_data just like the ExtractSourceText 
#    module.
#    Handle scripture texts.
#
#   Version 1.0.1 - 11/8/16 - Ron
#    Smaller interface.
#
#   Version 1.0 - 8/27/16 - Ron
#    Initial version.
#
#   Allow the user to test source language input live against transfer rules.
#
#   By default the transfer rules file, the bilingual lexicon file and the
#   source text file are loaded according to the configuration file. These
#   can be changed as desired.
#   The user can choose to select words from a sentence in the source text or
#   select a whole sentence or manually enter words in data stream format. 
#   In the first two cases, the selection(s) are converted to data stream format. 
#   The user can also choose which transfer rules to "turn on".
#   When Test button is pressed the selected transfer rules are run against the
#   source data stream and the target data stream is put into the target box.
#   Also the info. window will show errors and/or rules that have been matched.
#
#   Behind the scenes this tool is modifying a special source text file and 
#   transfer rule file. There is the assumption that an Apertium virtual machine
#   has been set up and that under the FLExTools folder there is LiveRuleTester
#   folder which serves as a share folder for the Linux VM. A cronjob runs the 
#   Makefile in the LiveRuleTester folder every 3 seconds. The Makefile builds
#   the necessary files to create the target text file.
#

from System import Guid
from System import String

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from flexlibs import FLExProject

import os
import re
import sys
import unicodedata
import copy
import xml.etree.ElementTree as ET
import shutil
from subprocess import call

#import win32gui

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QApplication, QCheckBox, QDialog, QDialogButtonBox

import Utils
import ReadConfig
import CatalogTargetAffixes
import ConvertTextToSTAMPformat
import DoStampSynthesis
import ExtractBilingualLexicon

from LiveRuleTester import Ui_MainWindow
from OverWriteTestDlg import Ui_OverWriteTest
from FTPaths import CONFIG_PATH

#----------------------------------------------------------------
# Configurables:

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Live Rule Tester Tool",
        FTM_Version    : "3.6.8",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Test transfer rules and synthesis live against specific words.",
        FTM_Help   : "",
        FTM_Description:
"""
The Live Rule Tester Tool is a tool that allows you to test source words or 
sentences live against transfer rules. This tool is especially helpful for 
finding out why transfer rules are not doing what you expect them to do. 
You can zero in on the problem by selecting just one source word and applying 
the pertinent transfer rule. In this way you don't have to run the whole system 
against the whole text file and all transfer rules. You can also test that the 
transfer results get synthesized correctly into target words. If you want, you
can add the source lexical items paired with the synthesis results to a testbed. 
You can run the testbed to check that you are getting the results you expect.
""" }

MAX_CHECKBOXES = 80
BILING_FILE_IN_TESTER_FOLDER = 'bilingual.dix'

def firstLower(myStr):
    
    if myStr:
        return myStr[0].lower() + myStr[1:]
    else:
        return myStr
    
# Model class for list of sentences.
class SentenceList(QtCore.QAbstractListModel):
    
    def __init__(self, myData = [], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.__localData = myData
        self.__currentSent = myData[0] # start out on the first one
        self.__RTL = False
    def getCurrentSent(self):
        return self.__currentSent
    def setRTL(self, val):
        self.__RTL = val
    def getRTL(self):
        return self.__RTL
    def rowCount(self, parent):
        return len(self.__localData)
    def data(self, index, role):
        row = index.row()
        mySent = self.__localData[row]
        
        if role == QtCore.Qt.DisplayRole:
            #if self.getRTL():
            #    pass
                #value = myHPG.getHeadword() + ' \u200F(' + myHPG.getPOS() + ')\u200F ' + myHPG.getGloss()
            #else:
            value = self.joinTupParts(mySent, 0)
            self.__currentSent = mySent    
            return value
            
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
    def joinTupParts(self, tupList, i):
        ret = ''
        for t in tupList: 
            # don't put a space before sentence punctuation
            if len(t) > i+1 and re.search(Utils.SENT_TAG, t[i+1]):
                ret += t[i]
            else:
                ret += ' ' + t[i]
             
        return ret.lstrip()
    
class OverWriteDlg(QDialog):
    def __init__(self, luStr):
        QDialog.__init__(self)
        self.ui = Ui_OverWriteTest()
        self.ui.setupUi(self)
        
        # Default to NoToAll. 
        self.retValue = QDialogButtonBox.NoToAll
        
        # Add the lexical unit to the label
        labelStr = str(self.ui.label.text())
        labelStr = re.sub('XX', '"' + luStr + '"', labelStr)
        self.ui.label.setText(labelStr)
        
        self.ui.buttonBox.button(QDialogButtonBox.YesToAll).clicked.connect(self.yesToAllClicked)
        self.ui.buttonBox.button(QDialogButtonBox.NoToAll).clicked.connect(self.noToAllClicked)
        self.ui.buttonBox.button(QDialogButtonBox.Yes).clicked.connect(self.yesClicked)
        self.ui.buttonBox.button(QDialogButtonBox.No).clicked.connect(self.noClicked)
    def yesToAllClicked(self):
        self.retValue = QDialogButtonBox.YesToAll
    def noToAllClicked(self):
        self.retValue = QDialogButtonBox.NoToAll
    def yesClicked(self):
        self.retValue = QDialogButtonBox.Yes
    def noClicked(self):
        self.retValue = QDialogButtonBox.No
    def getRetValue(self):
        return self.retValue
        
class Main(QMainWindow):

    def __init__(self, sentence_list, biling_file, source_text, DB, configMap, report):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.myWinId = int(self.winId())

        self.__biling_file = biling_file
        self.ui.BilingFileEdit.setText(biling_file)
        self.__source_text = source_text
        self.ui.SourceFileEdit.setText(source_text)
        self.__DB = DB
        self.__configMap = configMap
        self.__report = report
        self.__transfer_rules_file = None
        self.__replFile = None
        self.advancedTransfer = False
        self.__convertIt = True
        self.__extractIt = True
        self.__doCatalog = True
        self.__bilingMap = {}
        
        self.setWindowIcon(QtGui.QIcon('FLExTransWindowIcon.ico'))
        
        self.__ruleModel = self.__transferModel = None
        self.__interChunkModel = None
        self.__postChunkModel = None
        self.__transferRulesElement = None
        self.__interchunkRulesElement = None
        self.__postchunkRulesElement = None
        self.TRIndex = None
        self.setStatusBar(None)
        self.__lexicalUnits = ''
        self.__transferHtmlResult = ''
        self.__transferLexicalUnitsResult = ''
        self.__tranferPrevSourceHtml = ''
        self.__tranferPrevSourceLUs = ''
        self.__interchunkHtmlResult = ''
        self.__interchunkLexicalUnitsResult = ''
        self.__interchunkPrevSource = ''
        self.__interchunkPrevSourceLUs = ''
        self.__postchunkPrevSource = ''
        self.__postchunkPrevSourceLUs = ''
        self.__prevTab = 0
        self.rulesCheckedList = []
        
        # Tie controls to functions
        self.ui.TestButton.clicked.connect(self.TransferClicked)
        self.ui.listSentences.clicked.connect(self.listSentClicked)
        self.ui.listTransferRules.clicked.connect(self.rulesListClicked)
        self.ui.listInterChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.listPostChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.SentCombo.currentIndexChanged.connect(self.listSentComboClicked)
        self.ui.TransferFileBrowseButton.clicked.connect(self.TransferBrowseClicked)
        self.ui.BilingFileBrowseButton.clicked.connect(self.BilingBrowseClicked)
        self.ui.tabRules.currentChanged.connect(self.rulesTabClicked)
        self.ui.tabSource.currentChanged.connect(self.sourceTabClicked)
        self.ui.refreshButton.clicked.connect(self.RefreshClicked)
        self.ui.selectAllButton.clicked.connect(self.SelectAllClicked)
        self.ui.unselectAllButton.clicked.connect(self.UnselectAllClicked)
        self.ui.upButton.clicked.connect(self.UpButtonClicked)
        self.ui.downButton.clicked.connect(self.DownButtonClicked)
        self.ui.synthesizeButton.clicked.connect(self.SynthesizeButtonClicked)
        self.ui.refreshTargetLexiconButton.clicked.connect(self.RefreshTargetLexiconButtonClicked)
        self.ui.addToTestbedButton.clicked.connect(self.AddTestbedButtonClicked)
        self.ui.viewTestbedLogButton.clicked.connect(self.ViewTestbedLogButtonClicked)
        self.ui.editTestbedButton.clicked.connect(self.EditTestbedLogButtonClicked)
        self.ui.rebuildBilingLexButton.clicked.connect(self.RebuildBilingLexButtonClicked)
        self.ui.viewBilingualLexiconButton.clicked.connect(self.ViewBilingualLexiconButtonClicked)
        self.ui.editTransferRulesButton.clicked.connect(self.EditTransferRulesButtonClicked)
        self.ui.editReplacementButton.clicked.connect(self.EditReplacementButton)
        
        # Set up paths to things.
        # Get parent folder of the folder flextools.ini is in and add \Build to it
        self.buildFolder = os.path.join(os.path.dirname(os.path.dirname(CONFIG_PATH)), Utils.BUILD_FOLDER)

        self.testerFolder = self.buildFolder+'\\LiveRuleTester'
        self.affixGlossPath = self.testerFolder + '\\target_pfx_glosses.txt'
        self.transferResultsPath = self.testerFolder + '\\target_text.aper'
        self.targetAnaPath = self.testerFolder + '\\myText.ana'
        self.synthesisFilePath = self.testerFolder + '\\myText.syn'
        self.windowsSettingsFile = self.testerFolder+'\\window.settings.txt'
        
        # Right align some text boxes
        self.ui.SourceFileEdit.home(False)
        
        # Create a bunch of check boxes to be arranged later
        self.__checkBoxList = []
        for i in range(0, MAX_CHECKBOXES):
            myCheck = QCheckBox(self.ui.scrollArea)
            myCheck.setVisible(False)
            myCheck.setProperty("myIndex", i)
            myCheck.setGeometry(QtCore.QRect(0,0, 35, 35)) # default position
            
            # connect to a function
            myCheck.clicked.connect(self.SourceCheckBoxClicked)
            
            # add it to the list
            self.__checkBoxList.append(myCheck)

        # Make sure we are on right tabs
        ruleTab = 0
        sourceTab = 0
        
        # Clear text boxes and labels
        self.__ClearStuff()
        
        # Open a settings file to see which tabs were last used.
        try:
            f = open(self.windowsSettingsFile)
            
            line = f.readline()
            
            ruleTab, sourceTab = line.split(',')
            ruleTab = int(ruleTab)
            sourceTab = int(sourceTab)
            
            f.close()
        except:
            pass
        
        # Set which tab is shown        
        self.ui.tabRules.setCurrentIndex(ruleTab)
        self.ui.tabSource.setCurrentIndex(sourceTab)
        
        # Get the path to the transfer rules file
        self.__transfer_rules_file = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TRANSFER_RULES_FILE, self.__report, giveError=False)

        # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the top proj. folder.
        if not self.__transfer_rules_file:
            self.__transfer_rules_file = self.buildFolder + '\\..\\transfer_rules.t1x'
            
        # Parse the xml rules file and load the rules
        if not self.loadTransferRules():
            self.ret_val = False
            self.close()
            return 
        
        # Set the models
        self.__sent_model = SentenceList(sentence_list)

        # Check within the first 5 sentences if we have any RTL data and set the sentence list direction if needed
        found_rtl = False
        for i,mySent in enumerate(sentence_list):
            if found_rtl == True or i >= 5:
                break
            for myWordBundle in mySent:
                surface_form = myWordBundle[0]
                if self.has_RTL_data(surface_form):
                    self.ui.listSentences.setLayoutDirection(QtCore.Qt.RightToLeft)
                    self.ui.SentCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                    self.__sent_model.setRTL(True)
                    found_rtl = True
                    break
        
        if found_rtl:
            # this doesn't seem to be working
            self.ui.TargetTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
            
        # Read the bilingual lexicon into a map. this has to come before the combo box clicking for the first sentence
        self.ReadBilingualLexicon()
        
        self.ui.listSentences.setModel(self.__sent_model)
        self.ui.SentCombo.setModel(self.__sent_model)
        
        # Copy bilingual file to the tester folder
        try:
            # always name the local version bilingual.dix which is what the Makefile has
            shutil.copy(self.__biling_file, os.path.join(self.testerFolder, BILING_FILE_IN_TESTER_FOLDER))
        except:
            QMessageBox.warning(self, 'Copy Error', 'Could not copy the bilingual file to the folder: '+self.testerFolder+'. Please check that it exists.')
            self.ret_val = False
            return 
        
        # Get replacement file name.
        self.__replFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
        if not self.__replFile:
            self.ret_val = False
            self.close()
            return 
        
        ## Testbed preparation
        # Disable buttons as needed.
        self.ui.addToTestbedButton.setEnabled(False)
        self.ui.addMultipleCheckBox.setEnabled(False)
        
        # Get the path to the testbed file, if it's not in the config file (perhaps an older version of FLExTrans) set it to the proj. folder
        testbedPath = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TESTBED_FILE, self.__report, False)
        if not testbedPath:
            
            testbedPath = self.buildFolder + '\\..\\testbed.xml'

        self.__testbedPath = testbedPath
        
        # Disable the edit testbed button if the testbed doesn't exist.
        if os.path.exists(self.__testbedPath) == False:
            self.ui.editTestbedButton.setEnabled(False)

        # Start out with all rules checked. 
        self.checkThemAll()
        
        self.ret_val = True

    # Read the bilingual lexicon and make a map from source entries to one or more target entries
    def ReadBilingualLexicon(self):
        
        # Clear the map
        self.__bilingMap.clear()
        
        # Read the XML file
        try:
            bilingEtree = ET.parse(self.__biling_file)
            
        except IOError:
            
            QMessageBox.warning(self, 'Read Error', f'Bilingual file: {self.__biling_file} could not be read.')
            return        
        
        # Get the root node
        bilingRoot = bilingEtree.getroot()
            
        # Get the section element
        biling_section = bilingRoot.find('section')
        
        # Loop through all the bilingual entries
        for entry in biling_section:
            
            ## <e> (entry) should either have <p><l>abc</l><r>xyz</r></p>) or <i> (p = pair, l = left, r = right)
            
            # Get the left part 
            left = entry.find('p/l')
        
            # If we can't find it, it must be an <i> (identity), skip it
            if left == None:
                continue
            
            # Get the right part
            right = entry.find('p/r')
            
            # Get just the text part of the left entry. Note: it's not as easy as left.text
            key = Utils.getXMLEntryText(left)
            
            # See if we have the source entry already
            if key not in self.__bilingMap:
                
                self.__bilingMap[key] = [(left, right)]
            else:
                self.__bilingMap[key].append((left, right))
        
    def ViewBilingualLexiconButtonClicked(self):
        
        if os.path.exists(self.__biling_file) == False:

            QMessageBox.warning(self, 'Not Found Error', f'Bilingual file: {self.__biling_file} does not exist.')
            return 
        
        progFilesFolder = os.environ['ProgramFiles(x86)']
        
        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
        
        call([xxe, self.__biling_file])
            
    def EditTransferRulesButtonClicked(self):
        
        if os.path.exists(self.__transfer_rules_file) == False:

            QMessageBox.warning(self, 'Not Found Error', f'Transfer rule file: {self.__transfer_rules_file} does not exist.')
            return 
        
        progFilesFolder = os.environ['ProgramFiles(x86)']
        
        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
        
        call([xxe, self.__transfer_rules_file])
            
    def EditReplacementButton(self):
        
        if os.path.exists(self.__replFile) == False:

            QMessageBox.warning(self, 'Not Found Error', f'Transfer rule file: {self.__replFile} does not exist.')
            return 
        
        progFilesFolder = os.environ['ProgramFiles(x86)']
        
        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
        
        call([xxe, self.__replFile])
            
    def checkThemAll(self):
            
            if self.advancedTransfer:
                self.__ruleModel = self.__interChunkModel
                self.__rulesElement = self.__interchunkRulesElement
                self.SelectAllClicked()
                self.__ruleModel = self.__postChunkModel
                self.__rulesElement = self.__postchunkRulesElement
                self.SelectAllClicked()
                self.__ruleModel = self.__transferModel
                self.__rulesElement = self.__transferRulesElement
                self.SelectAllClicked()
            else:
                self.SelectAllClicked()

    def getLexUnitObjsFromString(self, lexUnitStr):
        # Initialize a Parser object
        lexParser = Utils.LexicalUnitParser(lexUnitStr)
        
        # Check for badly formed lexical units
        if lexParser.isWellFormed() == False:
            QMessageBox.warning(self, 'Lexical unit error', 'The lexical unit(s) is/are incorrectly formed.')
            return None
            
        # Get the lexical units from the parser
        return lexParser.getLexicalUnits()
        
    def buildTestNodeFromInput(self, lexUnitList, synthesisResult):
        # Get the name of the text this lu came from
        origin = self.ui.SourceFileEdit.text()
        
        # Initialize a Test XML object and fill out its data given a list of
        # lexical units and a result from the synthesis step
        myObj = Utils.TestbedTestXMLObject(lexUnitList, origin, synthesisResult)
        
        return myObj
    
    def RebuildBilingLexButtonClicked(self):
        
        self.setCursor(QtCore.Qt.WaitCursor)
        
        # Open the project fresh
        projname = self.__DB.ProjectName()
        
        try:
            # Delete the old project (i.e. close it)
            self.__DB.CloseProject()
            
            # Open the database
            self.__DB = FLExProject()
            self.__DB.OpenProject(projname, writeEnabled=False)
        except: 
            raise
        
        # Extract the bilingual lexicon        
        error_list = ExtractBilingualLexicon.extract_bilingual_lex(self.__DB, self.__configMap)
        
        for triplet in error_list:
            if triplet[1] == 2: # error code
                msg = triplet[0]
                QMessageBox.warning(self, 'Extract Bilingual Lexicon Error', msg + '\nRun the Extract Bilingual Lexicon module separately for more details.')
                return

        # Copy bilingual file to the tester folder
        try:
            # always name the local version bilingual.dix which is what the Makefile has
            shutil.copy(self.__biling_file, os.path.join(self.testerFolder, 'bilingual.dix'))
        except:
            QMessageBox.warning(self, 'Copy Error', 'Could not copy the bilingual file to the folder: '+self.testerFolder+'. Please check that it exists.')
            self.ret_val = False
            return 
        
        # Reload the bilingual map for showing tooltips
        self.ReadBilingualLexicon()
        
        # Force reload of the tooltips
        self.listSentComboClicked()
        
        self.__ClearStuff()
        
        self.unsetCursor()

    def ViewTestbedLogButtonClicked(self):
        resultsFileObj = Utils.FlexTransTestbedResultsFile(self.__report)
    
        # Get previous results
        resultsXMLObj = resultsFileObj.getResultsXMLObj()
    
        window = TestbedLogViewer.LogViewerMain(resultsXMLObj)
        
        window.show()
        window.myResize()
        firstIndex = window.getModel().rootItem.children[0].index
        window.ui.logTreeView.expand(firstIndex)
        #exec_val = app.exec_()

    def EditTestbedLogButtonClicked(self):
        
        if os.path.exists(self.__testbedPath) == False:

            QMessageBox.warning(self, 'Not Found Error', f'Testbed file: {self.__testbedPath} does not exist.')
            return 
        
        progFilesFolder = os.environ['ProgramFiles(x86)']
        
        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
        
        call([xxe, self.__testbedPath])
            
    def AddTestbedButtonClicked(self):
        self.ui.TestsAddedLabel.setText('')
        
        # Set the direction attribute
        if self.__sent_model.getRTL():
            direction = Utils.RTL
        else:
            direction = Utils.LTR

        try:
            fileObj = Utils.FlexTransTestbedFile(direction, self.__report)
        except:
            QMessageBox.warning(self, 'Not Found Error', f'Problem with the testbedfile. Check that you have TestbedFile set to a value in your configuration file. Normally it is set to ..\\testbed.xml')
            return 
        
        testbedObj = fileObj.getFLExTransTestbedXMLObject()
        
        if fileObj.isNew():
            self.ui.editTestbedButton.setEnabled(True)
         
        # Get the current list of tests in the XML testbed    
        testXMLObjList = testbedObj.getTestXMLObjectList()
        
        # Get the synthesis result text
        synResult = self.ui.SynthTextEdit.toPlainText().strip()
        
        # Remove the RTL marker
        synResult = re.sub('\u200F','', synResult)
        
        # Remove multiple spaces
        synResult = re.sub('\s{2,}', ' ', synResult)
        
        # For now remove non-sentence ending punctuation
        synResult = re.sub(r'[,،]', '', synResult)
        
        cnt = 0
        
        # Check if add-multiple was selected
        if self.ui.addMultipleCheckBox.isChecked():
            
            luObjList = self.getLexUnitObjsFromString(self.getActiveLexicalUnits())
            if luObjList == None:
                return

            resultList = synResult.split(' ') # split on space
            
            # Check for an equal amount of lexical units as synthesis results
            if len(luObjList) != len(resultList):
                QMessageBox.warning(self, 'Testbed Error', 'There is not an equal number of synthesis results for the lexical units you have. Cannot add to the testbed.')
                return
            
            ret_val = None
            
            # Loop through all the lexical units and results
            for i in range (0, len(luObjList)):
                luObj = luObjList[i]
                result = resultList[i]
                
                # take the lexical unit and result and build a Test XML node
                myTestXMLObj = self.buildTestNodeFromInput([luObj], result) # first parameter is a list
                
                # We'll get None if there was an error
                if myTestXMLObj == None:
                    return
                
                # If we created a new testbed, just add the new test
                if fileObj.isNew():
                    testbedObj.addToTestbed(myTestXMLObj)
                    cnt += 1
                else:    
                    # Check if the lexical unit already exists for a test in the testbed
                    # None gets returned if it wasn't found
                    existingTestXMLObj = self.getExistingTest(testXMLObjList, myTestXMLObj)
                    
                    if existingTestXMLObj:
                        # Get confirmation from the user if necessary.
                        if ret_val != QDialogButtonBox.YesToAll:
                            dlg = OverWriteDlg(myTestXMLObj.getLUString())
                            dlg.exec_()
                            ret_val = dlg.getRetValue()
                        
                        # See if we should overwrite    
                        if ret_val == QDialogButtonBox.Yes or ret_val == QDialogButtonBox.YesToAll:
                            testbedObj.overwriteInTestbed(existingTestXMLObj, myTestXMLObj)
                            cnt += 1
                        
                        # Break out of the loop if the user said no to all    
                        elif ret_val == QDialogButtonBox.NoToAll:
                            break
                    else:
                        testbedObj.addToTestbed(myTestXMLObj)
                        cnt += 1
                    
        else:
            # TODO: This leaves out the punctuation that may be between lexical units. The synthesis result will have punctuation in it.
            # so this creates a mismatch.
            luObjList = self.getLexUnitObjsFromString(self.getActiveLexicalUnits())
            if luObjList == None:
                return

            # take the lexical unit(s) and result and build a Test XML node
            myTestXMLObj = self.buildTestNodeFromInput(luObjList, synResult)
            
            # We'll get None if there was an error
            if myTestXMLObj == None:
                return
            
            # If we created a new testbed, just add the new test
            if fileObj.isNew():
                testbedObj.addToTestbed(myTestXMLObj)
                cnt += 1
            else:
                # Check if the lexical unit already exists for a test in the testbed
                # None gets returned if it wasn't found
                existingTestXMLObj = self.getExistingTest(testXMLObjList, myTestXMLObj)
                if existingTestXMLObj:
                    # Get confirmation from the user.
                    dlg = OverWriteDlg(myTestXMLObj.getLUString())
                    
                    # Only show the Yes and No buttons
                    dlg.ui.buttonBox.setStandardButtons(QDialogButtonBox.No|QDialogButtonBox.Yes)

                    # Show the dialog
                    ret_val = dlg.exec_()
                    
                    # See if we should overwrite    
                    if ret_val == 1: # Yes
                        testbedObj.overwriteInTestbed(existingTestXMLObj, myTestXMLObj)
                        cnt += 1
                else:
                    testbedObj.addToTestbed(myTestXMLObj)
                    cnt += 1
        
        # Tell the user how many tests were added.
        if cnt == 1:
            feedbackStr = str(cnt) + ' test added.'
        else:
            feedbackStr = str(cnt) + ' tests added.'
        self.ui.TestsAddedLabel.setText(feedbackStr)
        
        # Write the XML file
        if cnt > 0:
            fileObj.write()

    def getExistingTest(self, testXMLObjList, myTestXMLObj):
        
        for testXMLObj in testXMLObjList:
            if testXMLObj.equalLexUnits(myTestXMLObj):
                return testXMLObj
        
        return None
    
    def loadTestbed(self):
        pass
    
    def has_RTL_data(self, word1):
        for i in range(0, len(word1)):
            if unicodedata.bidirectional(word1[i]) in ('R', 'AL'):
                return True
        return False

    def RefreshTargetLexiconButtonClicked(self):
        self.ui.SynthTextEdit.setPlainText('')
        self.__extractIt = True
        self.__doCatalog = True
        
    def SynthesizeButtonClicked(self):
        self.ui.TestsAddedLabel.setText('')
        error_list = []
        
        self.setCursor(QtCore.Qt.WaitCursor)

        # Make the text box blank to start out.
        self.ui.SynthTextEdit.setPlainText('')
        
        ## CATALOG
        # Catalog all the target affixes
        # We only need to do this once, until the user requests to refresh the lexicon
        if self.__doCatalog:
            
            try:
                error_list = CatalogTargetAffixes.catalog_affixes(self.__DB, self.__configMap, self.affixGlossPath)
            except:
                QMessageBox.warning(self, 'Locked DB', 'The database appears to be locked.')
                self.unsetCursor()
                return

            for triplet in error_list:
                if triplet[1] == 2: # error code
                    msg = triplet[0]
                    QMessageBox.warning(self, 'Catalog Prefix Error', msg + '\nRun the Catalog Target Prefixes module separately for more details.')
                    self.unsetCursor()
                    return
                
            self.__doCatalog = False
                    
        ## CONVERT
        # if the target text has changed, we need to do the affixes and convert the target text to STAMP format
        if self.__convertIt == True:
            
            # Convert the target text to .ana format (for STAMP)
            error_list = ConvertTextToSTAMPformat.convert_to_STAMP(self.__DB, self.__configMap, self.targetAnaPath, self.affixGlossPath, self.transferResultsPath)
            for triplet in error_list:
                if triplet[1] == 2: # error code
                    msg = triplet[0]
                    QMessageBox.warning(self, 'Convert to STAMP Error', msg + '\nRun the Convert to STAMP module separately for more details.')
                    self.unsetCursor()
                    return
            
            self.__convertIt = False
                    
        ## EXTRACT
        # if the refresh lexicon button was pressed or this is the first run, extract the target lexicon
        if self.__extractIt == True:
            
            # Redo the catalog of prefixes in case the user changed an affix
            error_list = CatalogTargetAffixes.catalog_affixes(self.__DB, self.__configMap, self.affixGlossPath)
            if triplet[1] == 2: # error code
                msg = triplet[0]
                QMessageBox.warning(self, 'Catalog Prefix Error', msg + '\nRun the Catalog Target Prefixes module separately for more details.')
                self.unsetCursor()
                return
            
            # Extract the lexicon        
            error_list = DoStampSynthesis.extract_target_lex(self.__DB, self.__configMap)
            for triplet in error_list:
                if triplet[1] == 2: # error code
                    msg = triplet[0]
                    QMessageBox.warning(self, 'Extract Target Lexicon Error', msg + '\nRun the Extract Target Lexicon module separately for more details.')
                    self.unsetCursor()
                    return
        
        ## SYNTHESIZE
        error_list = DoStampSynthesis.synthesize(self.__configMap, self.targetAnaPath, self.synthesisFilePath) 
        for triplet in error_list:
            if triplet[1] == 2: # error code
                msg = triplet[0]
                QMessageBox.warning(self, 'Extract Target Lexicon Error', msg + '\nRun the Extract Target Lexicon module separately for more details.')
                self.unsetCursor()
                return
                    
        # Load the synthesized result into the text box
        lf = open(self.synthesisFilePath, encoding='utf-8')
        synthText = lf.read()
        
        # if RTL text, prepend the RTL mark
        if self.has_RTL_data(synthText[:len(synthText)//2]): # just check the 1st half of the string.
            synthText = '\u200F' + synthText
            
        self.ui.SynthTextEdit.setPlainText(synthText)
        
        if self.has_RTL_data(synthText[:len(synthText)//2]):
            self.ui.SynthTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.ui.SynthTextEdit.setLayoutDirection(QtCore.Qt.LeftToRight)

        lf.close()

        # Set a flag so that we don't extract the dictionary next time
        self.__extractIt = False
        
        # See if we have synthesis text without @'s. If so, enable the Add to Testbed button
        if len(synthText) > 0 and re.search('@', synthText) == None:
        
            self.ui.addToTestbedButton.setEnabled(True)

            # See if we have multiple words, If so, enable the Add Multiple... checkbox
            if re.search('\S+\s+\S+', synthText):
                self.ui.addMultipleCheckBox.setEnabled(True)
            else:
                self.ui.addMultipleCheckBox.setEnabled(False)
        else:
            self.ui.addToTestbedButton.setEnabled(False)
            self.ui.addMultipleCheckBox.setEnabled(False)
        
        self.unsetCursor()
        return
                
    def UpButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() > 0:
            
            # get current list item and insert it one above and remove it from its old position
            elemToMove = self.__rulesElement[self.TRIndex.row()]
            self.__rulesElement.remove(elemToMove)
            self.__rulesElement.insert(self.TRIndex.row()-1, elemToMove)
            
            # copy the selection
            cur_state = self.__ruleModel.item(self.TRIndex.row()).checkState()
            oth_state = self.__ruleModel.item(self.TRIndex.row()-1).checkState()
            self.__ruleModel.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__ruleModel.item(self.TRIndex.row()-1).setCheckState(cur_state)
            
            myIndex = self.__ruleModel.index(self.TRIndex.row()-1, self.TRIndex.column())
            self.ui.listTransferRules.setCurrentIndex(myIndex)

            # redo the display
            self.rulesListClicked(myIndex)
            
    def DownButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() < len(list(self.__rulesElement))-1:
            
            # get current list item and insert it one above and remove it from its old position
            elemToMove = self.__rulesElement[self.TRIndex.row()]
            self.__rulesElement.remove(elemToMove)
            self.__rulesElement.insert(self.TRIndex.row()+1, elemToMove)

            # copy the selection
            cur_state = self.__ruleModel.item(self.TRIndex.row()).checkState()
            oth_state = self.__ruleModel.item(self.TRIndex.row()+1).checkState()
            self.__ruleModel.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__ruleModel.item(self.TRIndex.row()+1).setCheckState(cur_state)
            
            myIndex = self.__ruleModel.index(self.TRIndex.row()+1, self.TRIndex.column())
            self.ui.listTransferRules.setCurrentIndex(myIndex)

            # redo the display
            self.rulesListClicked(myIndex)
    
    def SelectAllClicked(self):
        # Loop through all the items in the rule list model
        for i in range(0, self.__ruleModel.rowCount()):
            # Check each box
            self.__ruleModel.item(i).setCheckState(QtCore.Qt.Checked)
        
        # Redo the numbering
        self.rulesListClicked(self.TRIndex)
            
    def UnselectAllClicked(self):
        # Loop through all the items in the rule list model
        for i in range(0, self.__ruleModel.rowCount()):
            # Check each box
            self.__ruleModel.item(i).setCheckState(QtCore.Qt.Unchecked)
        
        # Redo the numbering
        self.rulesListClicked(self.TRIndex)
            
    def RefreshClicked(self):
        self.saveChecked()
        self.loadTransferRules()
        self.ui.SynthTextEdit.setPlainText('')
        self.__ClearStuff()
        self.restoreChecked()
        #self.checkThemAll()
        
        # Redo the numbering
        self.rulesListClicked(self.TRIndex)
            
    def saveChecked(self):
        
        self.rulesCheckedList = []
        
        # Loop through all the items in the rule list model
        for i in range(0, self.__ruleModel.rowCount()):
            
            # Save the state of each check box 
            if self.__ruleModel.item(i).checkState():
                self.rulesCheckedList.append(QtCore.Qt.Checked)
            else:
                self.rulesCheckedList.append(QtCore.Qt.Unchecked)
                
    def restoreChecked(self):
        
        # Loop through all the items in the rule list model
        for i in range(0, self.__ruleModel.rowCount()):
            
            if i < len(self.rulesCheckedList):
                
                # Set the state of each check box
                self.__ruleModel.item(i).setCheckState(self.rulesCheckedList[i])
                
    def doLexicalUnitProcessing(self, mySent, i, paragraph_element):
        # Split compounds
        # The 2nd part of the tuple has the data stream info.
        luStr = Utils.split_compounds(mySent[i][1])
        
        # parse the lexical units. This will give us tokens before, between 
        # and after each lu. E.g. ^hi1.1<n>$, ^there2.3<dem><pl>$ gives
        #                         ['', 'hi1.1<n>', ', ', 'there2.3<dem><pl>', '']
        # in this case we won't have punctuation
        tokens = re.split('\^|\$', luStr)
            
        # process pairs of tokens (white space and lexical unit)
        # we only care about the 2nd item in the pair, the lexical unit
        for j in range(0,len(tokens)-1,2):
    
            # Save the lexical unit in the saved string
            
            # if we have <sent> remove the space currently at the end of lexicalUnits
            if re.search(Utils.SENT_TAG, tokens[j+1]):
                self.__lexicalUnits = self.__lexicalUnits[:-1]
                
            # Preserve whitespace that may be between compound elements by adding the j+2 item 
            self.__lexicalUnits += '^' + tokens[j+1] + '$' + tokens[j+2]
            
            # Turn the lexical unit into color-coded html. 
            Utils.process_lexical_unit(tokens[j+1]+' ', paragraph_element, self.__sent_model.getRTL(), True) # last parameter: show UNK categories
        
        # Add a space at the end
        self.__lexicalUnits += ' '
        
    def SourceCheckBoxClicked(self):
        self.ui.TestsAddedLabel.setText('')
        mySent = self.__sent_model.getCurrentSent()
        self.__lexicalUnits = ''
        
        # Create a <p> html element
        paragraph_element = ET.Element('p')
        
        # Loop through all the check boxes 
        for i in range(0, len(mySent)):
            
            # If the check box is checked, put the data stream form into the source box
            if self.__checkBoxList[i].isChecked():
                
                # process this lexical unit to set both the lexicalUnits variable
                # and get an color-coded html element (<p>)
                self.doLexicalUnitProcessing(mySent, i, paragraph_element)
        
        # The paragraph_element now has one or more <span> children, turn it into a string        
        val = ET.tostring(paragraph_element, encoding='unicode')
        
        # The text box will turn the html into rich text    
        self.ui.SelectedWordsEdit.setText(val)    
                    
        # Put the same thing into the manual edit, but in data stream format.
        self.ui.ManualEdit.setPlainText(self.__lexicalUnits)

    def listSentClicked(self):
        mySent = self.__sent_model.getCurrentSent()
        self.__lexicalUnits = ''
        
        # Create a <p> html element
        paragraph_element = ET.Element('p')

        for i in range(0, len(mySent)):

            # process this lexical unit to set both the lexicalUnits variable
            # and get an color-coded html element (<p>)
            self.doLexicalUnitProcessing(mySent, i, paragraph_element)
        
        # The paragraph_element now has one or more <span> children, turn them into a string        
        val = ET.tostring(paragraph_element, encoding='unicode')
            
        # The text box will turn the html into rich text    
        self.ui.SelectedSentencesEdit.setText(val)
        
        # Put the same thing into the manual edit, but in data stream format.
        self.ui.ManualEdit.setPlainText(self.__lexicalUnits)
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
    def getActiveLexicalUnits(self):
        if self.ui.tabSource.currentIndex() == 0:
            ret = self.__lexicalUnits
        elif self.ui.tabSource.currentIndex() == 1:
            ret = self.__lexicalUnits
        else:
            ret = (self.ui.ManualEdit.toPlainText())
        return ret
    def getActiveSrcTextEditVal(self):
        if self.ui.tabSource.currentIndex() == 0:
            ret = self.ui.SelectedWordsEdit.toHtml()
        elif self.ui.tabSource.currentIndex() == 1:
            ret = self.ui.SelectedSentencesEdit.toHtml()
        else:
            ret = self.ui.ManualEdit.toPlainText()
        return ret
    def __ClearAllChecks(self):
        
        for check in self.__checkBoxList:
            check.setVisible(False)
            check.setChecked(False)
            
    # set global variables to the appropriate list variables
    # change interface as needed.
    def __MakeVisible(self, isVisible):
        
        # hide or unhide the sentence drop-down box, list box, check box area
        self.ui.SentCombo.setVisible(isVisible)
        self.ui.scrollArea.setVisible(isVisible)
        self.ui.listSentences.setVisible(isVisible)
        
    def __CopyStuff(self):
        
        # copy text from results to the source boxes
        self.ui.SelectedWordsEdit.setText(self.ui.TargetTextEdit.toHtml())
        self.ui.SelectedSentencesEdit.setText(self.ui.TargetTextEdit.toHtml())
        self.ui.ManualEdit.setPlainText(self.__lexicalUnits)
        self.__ClearStuff()
        
    def __ClearStuff(self):
        
        self.ui.TestsAddedLabel.setText('')
        self.ui.TargetTextEdit.setPlainText('')
        self.ui.LogEdit.setPlainText('')
        self.ui.SynthTextEdit.setPlainText('')
        self.ui.warningLabel.setText('')
        
    def sourceTabClicked(self):
        
        if self.ui.tabSource.currentIndex() == 0: # check boxes
            
            self.ui.selectWordsHintLabel.setVisible(True)
            
        else: # sentences or manual
            
            self.ui.selectWordsHintLabel.setVisible(False)
            
    def rulesTabClicked(self):
        
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                self.__ruleModel = self.__transferModel
                self.__rulesElement = self.__transferRulesElement
                
                # unhide stuff
                self.__MakeVisible(True)
                
                # re-write the check boxes
                self.SourceCheckBoxClicked()
                
                if self.ui.tabSource.currentIndex() == 0: # checkboxes with words
                    self.ui.SelectedWordsEdit.setText(self.__tranferPrevSourceHtml)
                elif self.ui.tabSource.currentIndex() == 1: # sentences
                    self.ui.SelectedSentencesEdit.setText(self.__tranferPrevSourceHtml)

                self.__lexicalUnits = self.__tranferPrevSourceLUs
                    
                self.ui.ManualEdit.setPlainText(self.__tranferPrevSourceLUs)
    
                self.__ClearStuff()
                
            elif self.ui.tabRules.currentIndex() == 1: #'tab_interchunk_rules':
                self.__ruleModel = self.__interChunkModel
                self.__rulesElement = self.__interchunkRulesElement
                
                # hide stuff
                self.__MakeVisible(False)
                
                if self.__prevTab == 0: # transfer
                    self.ui.SelectedWordsEdit.setText(self.__transferHtmlResult)
                    self.ui.SelectedSentencesEdit.setText(self.__transferHtmlResult)
                    self.ui.ManualEdit.setPlainText(self.__transferLexicalUnitsResult)
                    self.__lexicalUnits = self.__transferLexicalUnitsResult
                elif self.__prevTab == 2: # postchunk
                    self.ui.SelectedWordsEdit.setText(self.__interchunkPrevSource)
                    self.ui.SelectedSentencesEdit.setText(self.__interchunkPrevSource)
                    self.ui.ManualEdit.setPlainText(self.__interchunkPrevSourceLUs)
                    self.__lexicalUnits = self.__interchunkPrevSourceLUs
                
                self.__ClearStuff()

            else: # postchunk
                self.__ruleModel = self.__postChunkModel
                self.__rulesElement = self.__postchunkRulesElement
    
                # hide stuff
                self.__MakeVisible(False)
    
                self.ui.SelectedWordsEdit.setText(self.__interchunkHtmlResult)
                self.ui.SelectedSentencesEdit.setText(self.__interchunkHtmlResult)
                self.ui.ManualEdit.setPlainText(self.__interchunkLexicalUnitsResult)
                self.__lexicalUnits = self.__interchunkLexicalUnitsResult
                
                self.__ClearStuff()

            self.__prevTab = self.ui.tabRules.currentIndex()

    def listSentComboClicked(self):
        
        mySent = self.__sent_model.getCurrentSent()
        space_val = 10
        y_spacing = 30
        x_margin = 2
        x = x_margin
        y = 2

        # Clear the source text area
        self.ui.SelectedWordsEdit.setPlainText('')
        self.__ClearAllChecks()
        
        i=0
        # Position a check box for each "word" in the sentence
        for i, wrdTup in enumerate(mySent):
            
            # Bail out if we have more words than available check boxes
            if i >= len(self.__checkBoxList):
                break
            
            # Get the ith checkbox
            myCheck = self.__checkBoxList[i]
                        
            # Make it visible
            myCheck.setVisible(True)
            
            # set the text of the check box from the first tuple element
            # this will be the surface form
            myCheck.setText(wrdTup[0])
            
            # get the width of the box and text (maybe have to add icon size)
            width = myCheck.fontMetrics().boundingRect(wrdTup[0]).width() + 28 + 5 
            
            # set the position, if it's too wide to fit make a new row
            if width + x > self.ui.scrollArea.width():
                
                y += y_spacing
                x = x_margin
            
            if self.__sent_model.getRTL():
                
                xval = self.ui.scrollArea.width() - x - width
                myCheck.setLayoutDirection(QtCore.Qt.RightToLeft)
                
            else:
                xval = x
                
            myCheck.setGeometry(QtCore.QRect(xval, y, width, 27))
            x += width + space_val
            
            # If this word has a target(s) in the bilingual lexicon, show as a tooltip
            srcTrgPairsList = self.getTargetsInBilingMap(wrdTup)
            
            if srcTrgPairsList:
                
                tipText = self.formatTextForToolTip(srcTrgPairsList)
            else:
                tipText = '---'
            
            self.__checkBoxList[i].setToolTip(tipText)
            
        # Make the rest of the unused check boxes invisible
        for j in range(i+1,len(self.__checkBoxList)):
            
            self.__checkBoxList[j].setVisible(False)

    def getTargetsInBilingMap(self, wrdTup):
        
        dataStreamStr = wrdTup[1].strip() # of the form (\\v 1) ^word1.2<v><3sg>$
        
        # Find the lexical unit. There should only be one, but there might be non-lexical unit stuff like format markers
        aper_toks = re.split('\^|\$', dataStreamStr) 

        # one of the tokens will have the lexical unit
        for aper_tok in aper_toks:
            
            # A valid lexical unit will have <x> in it
            if re.search('<.+>', aper_tok):
                
                # Split off the lemma part, it's the first token
                toks = re.split('<', aper_tok)
                lemma = toks[0]
            
                if lemma in self.__bilingMap:
                    
                    return self.__bilingMap[lemma]
                
                # try lowercasing the first letter if we don't find it at first
                else:
                    lowerLemma = firstLower(lemma)
                    
                    if lowerLemma in self.__bilingMap:
                    
                        return self.__bilingMap[lowerLemma]
                
                # If we found <>, stop looking
                break
            
        return None
                
    def formatTextForToolTip(self, srcTrgtPairsList):
        
        tipStr = ''
        isRtl = self.__sent_model.getRTL()
        
        # Between the source and target we want an arrow, choose left or right arrows depending on the text direction
        if isRtl:
            
            arrowStr = '\u2B60'
        else:
            arrowStr = '\u2B62'
            
        # Go through all pairs and add them to the tool tip
        for source, target in srcTrgtPairsList:
            
            # Combine source and target into one paragraph html string
            tipStr += Utils.convertXMLEntryToColoredString(source, isRtl)[:-4] # remove </p> at end
            tipStr += f'&nbsp;{arrowStr}&nbsp;' # right arrow
            tipStr += Utils.convertXMLEntryToColoredString(target, isRtl)[3:] # remove <p> at beginning
            
        return tipStr.strip()
    
    def closeEvent(self, event):
        
        rulesTab = self.ui.tabRules.currentIndex()
        sourceTab = self.ui.tabSource.currentIndex()
        
        f = open(self.windowsSettingsFile, 'w')
        
        f.write(f'{str(rulesTab)},{str(sourceTab)}\n')
        f.close()
        
        self.__DB.CloseProject()
        
    def BilingBrowseClicked(self):
        # Bring up file select dialog
        biling_file_tup = \
         QFileDialog.getOpenFileNameAndFilter(self, 'Choose Bilingual Dictionary File',\
            'Output', 'Dictionary Files (bilingual.dix)')
         
        self.__biling_file = biling_file_tup[0]
        self.ui.BilingFileEdit.setText(self.__biling_file)
        
        # Copy bilingual file to the tester folder
        shutil.copy(self.__biling_file, os.path.join(self.testerFolder, os.path.basename(self.__biling_file)))
        
    def TransferBrowseClicked(self):
        # Bring up file select dialog
        __transfer_rules_file_tup = \
         QFileDialog.getOpenFileNameAndFilter(self, 'Choose Transfer File',\
            'Output', 'Transfer Rules (transfer_rules.t1x)')
        
        self.__transfer_rules_file = __transfer_rules_file_tup[0]
        
        if not self.loadTransferRules():
            self.ret_val = 0
            self.close()
            return False
        
        return True
        
    def loadTransferRules(self):
            
        # Verify we have a valid transfer file.
        try:
            test_tree = ET.parse(self.__transfer_rules_file)
        except:
            QMessageBox.warning(self, 'Invalid File', 'The transfer file you selected is invalid.')
            return False
        
        test_rt = test_tree.getroot()
        self.__transferRulesElement = test_rt.find('section-rules')
        
        if self.__transferRulesElement is not None:
            self.ui.TransferFileEdit.setText(self.__transfer_rules_file)
            self.__transferRuleFileXMLtree = test_tree
            self.__transferModel = QStandardItemModel ()
            self.displayRules(self.__transferRulesElement, self.__transferModel)
            # Initialize the model for the rule list control
            self.ui.listTransferRules.setModel(self.__transferModel)
            
        else:
            QMessageBox.warning(self, 'Invalid Rules File', \
            'The transfer file has no transfer element or no section-rules element')
            self.ui.TransferFileEdit.setText('')
            return False
        
        # Check if we have an interchunk rules file (.t2x)
        
        # build the interchunk rules file name
        rest = self.__transfer_rules_file[0:-4] #os.path.splitext(self.__transfer_rules_file.toStdString())
        interchunk_rules_file = rest + '.t2x'
        
        # Check if the file exists. If it does, we assume we have advanced transfer going on
        if os.path.isfile(interchunk_rules_file):
            
            # Verify we have a valid transfer file.
            try:
                interchunk_tree = ET.parse(interchunk_rules_file)
            except:
                QMessageBox.warning(self, 'Invalid File', 'The interchunk transfer file you selected is invalid.')
                return False
            
            interchunk_rt = interchunk_tree.getroot()
            self.__interchunkRulesElement = interchunk_rt.find('section-rules')
            
            if self.__interchunkRulesElement is not None:
                self.__interChunkRuleFileXMLtree = interchunk_tree
                self.__interChunkModel = QStandardItemModel()
                self.displayRules(self.__interchunkRulesElement, self.__interChunkModel)
                # Initialize the model for the rule list control
                self.ui.listInterChunkRules.setModel(self.__interChunkModel)
            else:
                QMessageBox.warning(self, 'Invalid Interchunk Rules File', \
                'The interchunk transfer file has no transfer element or no section-rules element')
                return False
            
            # build the postchunk rules file name
            postchunk_rules_file = rest + '.t3x'
            
            # Check if the file exists. If it does, we assume we have advanced transfer going on
            if os.path.isfile(postchunk_rules_file):
                
                # Verify we have a valid transfer file.
                try:
                    postchunk_tree = ET.parse(postchunk_rules_file)
                except:
                    QMessageBox.warning(self, 'Invalid File', 'The postchunk transfer file you selected is invalid.')
                    return False
                
                postchunk_rt = postchunk_tree.getroot()
                self.__postchunkRulesElement = postchunk_rt.find('section-rules')
                
                if self.__postchunkRulesElement is not None:
                    self.__postChunkRuleFileXMLtree = postchunk_tree
                    self.__postChunkModel = QStandardItemModel()
                    self.displayRules(self.__postchunkRulesElement, self.__postChunkModel)
                    # Initialize the model for the rule list control
                    self.ui.listPostChunkRules.setModel(self.__postChunkModel)
                else:
                    QMessageBox.warning(self, 'Invalid postchunk Rules File', \
                    'The postchunk transfer file has no transfer element or no section-rules element')
                    return False
    
                # if we have interchunk and postchunk transfer rules files we are in advanced mode
                self.advancedTransfer = True
         
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                # Set these global variables to the transfer ones
                self.__ruleModel = self.__transferModel
                self.__rulesElement = self.__transferRulesElement
                
            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                # Set these global variables to the interchunk ones
                self.__ruleModel = self.__interChunkModel
                self.__rulesElement = self.__interchunkRulesElement

            else: # postchunk
                # Set these global variables to the postchunk ones
                self.__ruleModel = self.__postChunkModel
                self.__rulesElement = self.__postchunkRulesElement

        else:
            # Set these global variables to the transfer ones
            self.__ruleModel = self.__transferModel
            self.__rulesElement = self.__transferRulesElement
 
            
        return True

    def rulesListClicked(self, index):
        self.TRIndex = index
        active_rules = 1
        for i, el in enumerate(self.__rulesElement):
            ruleText = el.get('comment')
            
            if ruleText == None:
                ruleText = 'missing comment'
                
            # If active add text with the active rule #
            if self.__ruleModel.item(i).checkState():
                self.__ruleModel.item(i).setText(ruleText + ' - Active Rule ' + str(active_rules))
                active_rules += 1
            else:
                self.__ruleModel.item(i).setText(ruleText)
    
    def displayRules(self, rules_element, ruleModel):
        
        # Loop through each rule
        for rule_el in rules_element:
            
            # Get the comment for the rule
            comment = rule_el.get('comment')
            
            if comment == None:
                comment = 'missing comment'
                
            # Create an item object
            item = QStandardItem(comment) 
            item.setCheckable(True)
            item.setCheckState(False)
            ruleModel.appendRow(item)
            
    def TransferClicked(self):
        
        self.setCursor(QtCore.Qt.WaitCursor)
        
        if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules'
            self.__interchunkHtmlResult = ''
            self.__interchunkLexicalUnitsResult = ''
        
        self.__convertIt = True
        
        # TODO: allow editable rule file edit box?
        # Make sure we have a transfer file
        if self.ui.TransferFileEdit.text() == '':
            self.unsetCursor()
            return
        
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                source_file = os.path.join(self.testerFolder, 'source_text.aper')
                tr_file = os.path.join(self.testerFolder, 'transfer_rules.t1x')
                tgt_file = os.path.join(self.testerFolder, 'target_text1.aper')
                log_file = os.path.join(self.testerFolder, 'apertium_log.txt')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
                ruleFileRoot = self.__transferRuleFileXMLtree.getroot()
                
            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                source_file = os.path.join(self.testerFolder, 'target_text1.aper')
                tr_file = os.path.join(self.testerFolder, 'transfer_rules.t2x')
                tgt_file = os.path.join(self.testerFolder, 'target_text2.aper')
                log_file = os.path.join(self.testerFolder, 'apertium_log2.txt')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__interChunkRuleFileXMLtree)
                ruleFileRoot = self.__interChunkRuleFileXMLtree.getroot()

            else: # postchunk
                source_file = os.path.join(self.testerFolder, 'target_text2.aper')
                tr_file = os.path.join(self.testerFolder, 'transfer_rules.t3x')
                tgt_file = os.path.join(self.testerFolder, 'target_text.aper')
                log_file = os.path.join(self.testerFolder, 'apertium_log3.txt')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__postChunkRuleFileXMLtree)
                ruleFileRoot = self.__postChunkRuleFileXMLtree.getroot()

        else:
            source_file = os.path.join(self.testerFolder, 'source_text.aper')
            tr_file = os.path.join(self.testerFolder, 'transfer_rules.t1x')
            tgt_file = os.path.join(self.testerFolder, 'target_text.aper')
            log_file = os.path.join(self.testerFolder, 'apertium_log.txt')
            
            # Copy the xml structure to a new object
            myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
            ruleFileRoot = self.__transferRuleFileXMLtree.getroot()
            
        # Save the source text to the tester folder
        sf = open(source_file, 'w', encoding='utf-8')
        myStr = self.getActiveLexicalUnits()
        
        if len(myStr) < 1:
            
            self.ui.TargetTextEdit.setPlainText('Nothing selected. Select at least one word or sentence.')
            self.unsetCursor()
            return
            
        sf.write(myStr)
        sf.close()
        
        # Copy the xml structure to a new object
        myRoot = myTree.getroot()
        
        sr_element = myRoot.find('section-rules')
        
        # Remove the section-rules element
        myRoot.remove(sr_element)
        
        # Recreate the section-rules element
        new_sr_element = ET.SubElement(myRoot, 'section-rules')
        
        rules_element = ruleFileRoot.find('section-rules')

        # Loop through all the selected rules
        for i, rule_el in enumerate(rules_element):
        
            # Add to the xml structure if it is a selected rule
            if self.__ruleModel.item(i).checkState():
                new_sr_element.append(rule_el) 
            
        # Give an error if no rules were selected
        if len(list(new_sr_element)) < 1:
            
            self.ui.TargetTextEdit.setPlainText('At least one rule must be selected.')
            self.unsetCursor()
            return
        
        # Write out the file
        myTree.write(tr_file, encoding='UTF-8', xml_declaration=True) #, pretty_print=True)
        
        # Convert the file to be decomposed unicode
        Utils.decompose(tr_file)
        
        ## Display the results
        
        # Clear the results box
        self.ui.TargetTextEdit.setText('') 

        # Fix problem characters in symbols of the bilingual lexicon (making a backup copy of the original file)
        subPairs = Utils.fixProblemChars(os.path.join(self.testerFolder,BILING_FILE_IN_TESTER_FOLDER))
        
        # Substitute symbols with problem characters with fixed ones in the transfer file
        Utils.subProbSymbols('.', tr_file, subPairs)
        
        # Check if attributes are well-formed. Warnings will be reported in the function
        if not self.advancedTransfer:
        
            error_list = Utils.checkRuleAttributesXML(ruleFileRoot)
    
#            for triplet in error_list:
#                self.ui.warningLabel.SetText('hi ron')
                #self.ui.warningLabel.SetText(self.ui.TestsAddedLabel.GetText()+triplet[0]+'\n')

        # Run the makefile to run Apertium tools to do the transfer
        # component of FLExTrans. Pass in the folder of the bash
        # file to run. The current directory is FlexTools
        ret = Utils.run_makefile(self.buildFolder+'\\LiveRuleTester', self.__report)
        
        if ret:
            self.ui.TargetTextEdit.setPlainText('An error happened when running the Apertium tools.')
            self.unsetCursor()
            return
        
        # Convert back the problem characters in the transfer results file back to what they were. Restore the backup biling. file
        Utils.unfixProblemChars(os.path.join(self.testerFolder,BILING_FILE_IN_TESTER_FOLDER), tgt_file)

        # Load the target text contents into the results edit box
        tgtf = open(tgt_file, encoding='utf-8')
        target_output = tgtf.read()
        
        # Create a <p> html element
        pElem = ET.Element('p')

        rtl_flag = self.has_RTL_data(target_output[:len(target_output)//2])
        
        # Process advanced results differently (which doesn't apply to post chunk, because we get normal data stream in that case)
        if self.advancedTransfer and self.ui.tabRules.currentIndex() != 2: # 'tab_postchunk_rules'
            
            # Split off the advanced stuff that precedes the brace {
            # parsing: '--^ch_xx<ABC>{^hello1.1<excl>$ ^Ron1.1<Prop>$}$~~ ^ch_yy<Z>{^yo1.1<n>$}$++'
            # gives: ['--^ch_xx<ABC>', '^hello1.1<excl>$ ^Ron1.1<Prop>$', '$~~ ^ch_yy<Z>', '^yo1.1<n>$', '$++']
            tokens = re.split('{|}', target_output)
            
            # process pairs of tokens
            for i in range(0,len(tokens)-1): # skip the last one for now
                
                tok = tokens[i]
            
                # the even # elements are the advanced stuff
                if i%2 == 0:
                    
                    # remove the $ from the advanced part
                    tok = re.sub('\$', '', tok)
                    
                    # split on ^ and output any punctuation
                    [punc, chunk] = re.split('\^', tok)
                    
                    # don't put out anything when it's a default chunk
                    if re.search('^default', chunk):
                        continue
                    
                    # TODO: not sure if we have punctuation in the the live rule tester. Might not need a lot of this code
                    # First, put out the punctuation. If the punctuation is null, put
                    # out a space. Except if it's the first punctuation and it null.
                    if len(punc) > 0:
                        Utils.output_span(pElem, Utils.PUNC_COLOR, punc, rtl_flag)
                    elif i > 0:
                        Utils.output_span(pElem, Utils.PUNC_COLOR, ' ', rtl_flag)
                    
                    # Now put out the chunk part
                    Utils.process_chunk_lexical_unit(chunk, pElem, rtl_flag)
                    
                    # Put out a [ to surround the normal lex. unit
                    Utils.output_span(pElem, Utils.CHUNK_LEMMA_COLOR, ' [', rtl_flag)

                # process odd # elements -- the normal stuff (that was within the braces)
                else:
                    
                    # parse the lexical units. This will give us tokens before, between 
                    # and after each lu. E.g. ^hi1.1<n>$, ^there2.3<dem><pl>$ gives
                    #                         ['', 'hi1.1<n>', ', ', 'there2.3<dem><pl>', '']
                    subTokens = re.split('\^|\$', tok)
                    
                    # process pairs of tokens (punctuation and lexical unit)
                    for j in range(0,len(subTokens)-1,2):
                        # First, put out the punctuation. If the punctuation is null, put
                        # out a space. Except if it's the first punctuation and it null.
                        if len(subTokens[j]) > 0:
                            Utils.output_span(pElem, Utils.PUNC_COLOR, subTokens[j], rtl_flag)
                        else:
                            # we need a preceding space if we are not within brackets
                            if re.search('^default', chunk) is None:
                                myStr = ''
                            else:
                                myStr = ' '
                            Utils.output_span(pElem, Utils.PUNC_COLOR, myStr, rtl_flag)
                        
                        # parse the lexical unit and add the elements needed to the list item element
                        Utils.process_lexical_unit(subTokens[j+1], pElem, rtl_flag, True)
                        
                    # process last subtoken for the stuff inside the {}
                    if len(subTokens[-1]) > 0:
                        Utils.output_span(pElem, Utils.PUNC_COLOR, subTokens[-1], rtl_flag)
                    
                    # Put out a closing ] if it wasn't a default chunk
                    if re.search('^default', chunk) is None:
                        Utils.output_span(pElem, Utils.CHUNK_LEMMA_COLOR, ']', rtl_flag)
            
        else:
            # parse the lexical units. This will give us tokens before, between 
            # and after each lu. E.g. ^hi1.1<n>$ ^there2.3<dem><pl>$ gives
            #                         ['', 'hi1.1<n>', ' ', 'there2.3<dem><pl>', '']
            tokens = re.split('\^|\$', target_output)
            
            # process pairs of tokens (punctuation and lexical unit)
            # ignore the punctuation (spaces)
            for i in range(0,len(tokens)-1,2):
                # Turn the lexical units into color-coded html.            
                Utils.process_lexical_unit(tokens[i+1]+' ', pElem, self.has_RTL_data(target_output[:len(target_output)//2]), True) # last parameter: show UNK categories
            
        # The p element now has one or more <span> children, turn them into an html string        
        htmlVal = ET.tostring(pElem, encoding='unicode')

        self.ui.TargetTextEdit.setText(htmlVal)
        
        tgtf.close()
        
        # Store the actual data stream in __lexicalUnits for use elsewhere when in advanced mode
        # Store the html in another member
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                self.__transferHtmlResult = htmlVal
                self.__transferLexicalUnitsResult = target_output
                self.__tranferPrevSourceHtml = self.getActiveSrcTextEditVal()
                self.__tranferPrevSourceLUs = self.getActiveLexicalUnits()
            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                self.__interchunkHtmlResult = htmlVal
                self.__interchunkLexicalUnitsResult = target_output
                self.__interchunkPrevSource = self.getActiveSrcTextEditVal()
                self.__interchunkPrevSourceLUs = self.getActiveLexicalUnits()
            else: # 'tab_postchunk_rules':
                self.__postchunkPrevSource = self.getActiveSrcTextEditVal()
                self.__postchunkPrevSourceLUs = self.getActiveLexicalUnits()
        
        # Load the log file
        lf = open(log_file, encoding='utf-8')
        self.ui.LogEdit.setPlainText(lf.read())
        lf.close()
        
        self.unsetCursor()

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            myList = get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return

def get_component_count(e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            return entryRef.ComponentLexemesRS.Count
        
def get_position_in_component_list(e, complex_e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in complex_e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            # loop through components
            for i, my_e in enumerate(entryRef.ComponentLexemesRS):
                if e == my_e:
                    return i

def GetEntryWithSense(e, inflFeatAbbrevs):
    # If the entry is a variant and it has no senses, loop through its references 
    # until we get to an entry that has a sense
    notDoneWithVariants = True
    while notDoneWithVariants:
        if e.SensesOS.Count == 0:
            if e.EntryRefsOS:
                foundVariant = False
                for entryRef in e.EntryRefsOS:
                    if entryRef.RefType == 0: # we have a variant
                        foundVariant = True
                        
                        # Collect any inflection features that are assigned to the special
                        # variant types called Irregularly Inflected Form
                        for varType in entryRef.VariantEntryTypesRS:
                            if varType.ClassName == "LexEntryInflType" and varType.InflFeatsOA:
                                my_feat_abbr_list = []
                                # The features might be complex, make a recursive function call to find all features
                                get_feat_abbr_list(varType.InflFeatsOA.FeatureSpecsOC, my_feat_abbr_list)
                                inflFeatAbbrevs.extend(my_feat_abbr_list)
                        break
                if foundVariant and entryRef.ComponentLexemesRS.Count > 0:
                    # if the variant we found is a variant of sense, we are done. Use the owning entry.
                    if entryRef.ComponentLexemesRS.ToArray()[0].ClassName == 'LexSense':
                        e = entryRef.ComponentLexemesRS.ToArray()[0].OwningEntry
                        break
                    else: # normal variant of entry
                        e = entryRef.ComponentLexemesRS.ToArray()[0]
                        continue
        notDoneWithVariants = False
    return e

def MainFunction(DB, report, modify=False):
        
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get needed configuration file properties
    text_desired_eng = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)

    # check for errors
    if not (text_desired_eng and bilingFile):
        return
    
    # Get punctuation string
    sent_punct = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)
    
    if not sent_punct:
        return
    
    typesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report):
        return

    discontigTypesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report)
    if not discontigTypesList:
        discontigTypesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report):
        return

    discontigPOSList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report)
    if not discontigPOSList:
        discontigPOSList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report):
        return

    # Find the desired text
    text_list = []
    foundText = False
    for interlinText in DB.ObjectsIn(ITextRepository):
        if text_desired_eng == ITsString(interlinText.Name.BestAnalysisAlternative).Text:
            foundText = True
            contents = interlinText.ContentsOA
        text_list.append(text_desired_eng)
    
    if not foundText:
        # check if it's scripture text
        for section in DB.ObjectsIn(IScrSectionRepository):
            if text_desired_eng == ITsString(section.ContentOA.Title.BestAnalysisAlternative).Text:
                contents = section.ContentOA
                foundText = True
                break
            
        if not foundText:    
            report.Error('The text named: '+text_desired_eng+' not found.')
            return

    # Check if we are using TreeTran for sorting the text output
    treeTranResultFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, report)
    
    if not treeTranResultFile:
        TreeTranSort = False
    else:
        TreeTranSort = True
    
    # Check if we are using an Insert Words File for TreeTran 
    treeTranInsertWordsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TREETRAN_INSERT_WORDS_FILE, report)
    
    if not treeTranInsertWordsFile:
        insertWordsFile = False
    else:
        insertWordsFile = True
        
        insertWordsList = Utils.getInsertedWordsList(treeTranInsertWordsFile, report, DB)

        if insertWordsList == None: 
            return # error already reported
        
    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile, encoding='utf-8')
            f_treeTranResultFile.close()
        except:
            report.Error('There is a problem with the Tree Tran Result File path: '+treeTranResultFile+'. Please check the configuration file setting.')
            return
        
        # get the list of guids from the TreeTran results file
        treeSentList = Utils.getTreeSents(treeTranResultFile, report)
        
        if treeSentList == None: 
            return # error already reported
        
        # get log info. that tells us which sentences have a syntax parse and # words per sent
        logInfo = Utils.importGoodParsesLog()
            
    # Get the interlinear data. It's stored in a complex object.
    myText = Utils.getInterlinData(DB, report, sent_punct, contents, typesList, discontigTypesList, discontigPOSList)

    if TreeTranSort:
        
        segment_list = []
        
        # If we are using an Insert Words file, add the words to the text object
        if insertWordsFile == True:
            myText.addInsertedWordsList(insertWordsList)
        
        # create a map of bundle guids to word objects. This gets used when the TreeTran module is used.
        myText.createGuidMaps()
        
        p = 0
        noParseSentCount = 0
        
        # Loop through each sent
        for sentNum, (_, parsed) in enumerate(logInfo):
            
            tupList = []
            
            # If we have a parse for a sentence, TreeTran may have rearranged the words.
            # We need to put them out in the new TreeTran order.
            if parsed == True:
                myTreeSent = treeSentList[p]
                
                myFLExSent = myText.getSent(sentNum)
                if myFLExSent is None:
                    report.Error('Sentence ' + str(sentNum) + ' from TreeTran not found')
                    return
                    
                # Output any punctuation preceding the sentence.
                prePuncTupList = myFLExSent.getSurfaceAndDataPrecedingSentPunc()
                tupList.extend(prePuncTupList)
                
                # Loop through each word in the sentence and get the Guids
                for wrdNum in range(0, myTreeSent.getLength()):
                    myGuid = myTreeSent.getNextGuidAndIncrement()
                    
                    if myGuid == None:
                        report.Error('Null Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                        break
                    
                    # If we couldn't find the guid, see if there's a reason
                    if myFLExSent.haveGuid(myGuid) == False:
                        # Check if the reason we didn't have a guid found is that it got replaced as part of a complex form replacement
                        nextGuid = myTreeSent.getNextGuid()
                        if nextGuid is None or myFLExSent.notPartOfAdjacentComplexForm(myGuid, nextGuid) == True:
                            report.Warning('Could not find the desired Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                    else:
                        surface, data = myFLExSent.getSurfaceAndDataForGuid(myGuid)
                        tupList.append((surface,data))
                    
                # Output any punctuation at the of the sentence.
                postPuncTupList = myFLExSent.getSurfaceAndDataFinalSentPunc()
                tupList.extend(postPuncTupList)
                
                p += 1
                
            # No syntax parse from PC-PATR. Put words out in their default order since TreeTran didn't rearrange anything.                        
            else:
                noParseSentCount += 1
                
                # Get the sentence in question
                myFLExSent = myText.getSent(sentNum)

                if myFLExSent == None:
                    
                    report.Error('Sentence: ' + str(sentNum) + ' not found. Check that the right parses are present.')
                    continue 

                myFLExSent.getSurfaceAndDataTupleList(tupList)
            
            segment_list.append(tupList)
                
        report.Info("Exported: " + str(len(logInfo)) + " sentence(s) using TreeTran results.")
        
        if noParseSentCount > 0:
            report.Warning('No parses found for ' + str(noParseSentCount) + ' sentence(s).')

    else:
        # Normal, non-TreeTran processing
        if myText.haveData() == True:
            segment_list = myText.getSurfaceAndDataTupleListBySent()
        
    if len(segment_list) > 0:    
        # Create the qt app
        app = QApplication(sys.argv)
        
        # if the bilingual file path is relative, add on the current directory
        if re.search(':', bilingFile):
            pass
        else:
            pwd = os.getcwd()
            bilingFile = os.path.join(pwd, bilingFile)
            
        # Supply the segment list to the main windowed program
        window = Main(segment_list, bilingFile, text_desired_eng, DB, configMap, report)
        
        if window.ret_val == False:
            report.Error('An error occurred getting things initialized.')
            return
        
        window.show()
        app.exec_()
    else:
        report.Error('This text has no data.')

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
