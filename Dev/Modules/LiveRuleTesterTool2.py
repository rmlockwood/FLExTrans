#
#   LiveRuleTesterTool
#
#   Ron Lockwood
#   SIL International
#   7/2/16
#
#   Version 3.14.1 - 6/19/25 - Ron Lockwood
#    Don't allow synthesis if the target text is empty or no words are selected.
#
#   Version 3.14 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 6/2/25 - Ron Lockwood
#    Improved exception handling around use of the HermitCrab DLL.
# 
#   Version 3.13.2 - 4/9/25 - Ron Lockwood
#    Delete non-sentence-ending punctuation from the synthesis result before adding it to the testbed.
#    Also, apply Text Out rules to the sentence-ending punctuation if necessary.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.9 - 2/18/25 - Ron Lockwood
#    Fixes #892. Save check box states.
#
#   Version 3.12.8 - 2/17/25 - Ron Lockwood
#    Better handling of angle brackets. Improved escaping reserved Apertium characters
#    by making sure the character is not already escaped. This avoids double-escaping.
#
#   Version 3.12.7 - 2/11/25 - Ron Lockwood
#    Fixes #873. Prevent mismatches on LUs and synthesis result words when punctuation is there.
#    This is for when they want to add each word as its own test with the checkbox.
#
#   Version 3.12.6 - 1/10/25 - Ron Lockwood
#    Fixes #874. Use a system message box instead of a custom one.
#    Make it more readable for the user.
#
#   Version 3.12.5 - 1/10/25 - Ron Lockwood
#    Fixes #855. Don't clean up unknown words, if desired.
#    Make Apply Textout Rules invisible unless rules exist.
#
#   Version 3.12.4 - 1/10/25 - Ron Lockwood
#    Fixes #843. Fix bug of setting the HC dll's config file when it did not exist.
#
#   Version 3.12.3 - 1/6/25 - Ron Lockwood
#    Fixes #835. Don't crash when Apertium data is missing as Rule Assistant test data. Just don't show test data.
#
#   Version 3.12.2 - 12/4/24 - Ron Lockwood
#    Fixes #821. Escape reserved characters in the transfer rules generated for the LRT.
#
#   Version 3.12.1 - 11/27/24 - Ron Lockwood
#    Fixes #818. Call a dll for HC synthesis to speed up the process.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.6 - 10/26/24 - Ron Lockwood
#    Fixes #782. Change the Edit Replacement File button to launch the Replacement 
#    Dictionary Editor.
#
#   Version 3.11.5 - 10/26/24 - Ron Lockwood
#    Fixes #92. Run Apertium only on lexical units -- no punctuation.
#
#   Version 3.11.4 - 10/25/24 - Ron Lockwood
#    Fixes #737. Allow user to apply text out rules.
#    Fix bug where change to source text in top drop-down not being recognized.
#
#   Version 3.11.3 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.2 - 9/5/24 - Ron Lockwood
#    Escape Apertium lemmas when writing the data stream to a file.
#    Unescape Apertium lemmas when coming from a file for user display.
#
#   Version 3.11.1 - 8/30/24 - Ron Lockwood
#    apertium_transfer now gives additional info. in the trace -- namely the target lexical
#    unit. Remove this when outputting to the Rule Execution Information yellow box.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.12 - 5/3/24 - Ron Lockwood
#    Performance improvement. catalog target affixes was being called twice in many situations.
#
#   Version 3.10.11 - 4/22/24 - Ron Lockwood
#    Fixes #602. Rebuild of Biling. Lex. re-selects last sentence used.
#    Now it works more reliably regardless of the tab that was active.
#
#   Version 3.10.10 - 4/13/24 - Ron Lockwood
#    Fixes #399. Show **none** on the left size when the source language is in a RTL script.
#    Also make the tooltip size for all widgets the same as other widgets according to how much
#    the user has zoomed in or out.
#
#   Version 3.10.9 - 4/11/24 - Ron Lockwood
#    Bug fix for TreeTran use. Don't compare guid object to None.
#
#   Version 3.10.8 - 3/20/24 - Ron Lockwood
#    Refactoring to put changes to allow get interlinear parameter changes to all be in Utils
#
#   Version 3.10.7 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10.6 - 3/2/2024 - Ron Lockwood
#    Fixes #562 Fixes bug that says 'nothing selected' even though a sentence is selected.
#
#   Version 3.10.5 - 2/23/2024 - Ron Lockwood
#    Fixes #567 Fixes crash in Catalog Target Affixes when a lexeme form is null.
#
#   Version 3.10.4 - 1/27/2024 - Ron Lockwood
#    Include the LogInfo window in font increase/decrease.
#
#   Version 3.10.3 - 1/24/2024 - Ron Lockwood
#    Fixes #509. Catch all exceptions when reading the biling. lexion which now catches XML parse errors.
#
#   Version 3.10.2 - 1/21/2024 - Ron Lockwood
#    Fixes #549. Resize fonts in text boxes via zoom +/-. And save this info.
#
#   Version 3.10.1 - 1/6/2024 - Ron Lockwood
#    Fixes #533. Recheck the words that were checked on closing the tester.
#
#   Version 3.10 - 12/28/23 - Ron Lockwood
#    Fixes #518. Show the data stream for the checked boxes after rebuilding the
#    bilingual lexicon.
#
#   Version 3.9.1 - 6/3/23 - Ron Lockwood
#    Fixes #442. Force the rules to be renumbered when restoring checked rules.
#
#   Version 3.9 - 6/2/23 - Ron Lockwood
#    Support tracing of HermitCrab synthesis
#
#   Version 3.8.8 - 4/28/23 - Ron Lockwood
#    Don't give an error if the HermitCrab Synthesis flag (y/n) is not found in the config file.
#
#   Version 3.8.7 - 4/25/23 - Ron Lockwood
#    Handle blank HermitCrab config path in settings.
#
#   Version 3.8.6 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names. Removed fallback to use scripture text names.
#
#   Version 3.8.5 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.4 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#
#   Version 3.8.3 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8.2 - 4/15/23 - Ron Lockwood
#    Fixes #391. Save/restore which transfer rules were checked.
#
#   Version 3.8.1 - 4/14/23 - Ron Lockwood
#    Save/restore which words were checked on the Select Words tab when Rebuild Bil. Lex. button is pushed.
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.16 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   Version 3.7.15 - 2/7/23 - Ron Lockwood
#    Fixes #390. Words that are linked to **none** now get a blank mapping in the bilingual
#    dictionary. This allows them to be deleted by default, or they can be overridden by
#    replacement file entries.
#    Handle a target word that is now empty. We now show **none** on the tooltip.
#
#   Version 3.7.14 - 1/10/23 - Ron Lockwood
#    Show log file output in colored format. Also filter out unneeded information.
#    Fixes #162 and #320. Also widened yellow log output area.
#
#   Version 3.7.13 - 1/9/23 - Ron Lockwood
#    Fix to bug introduce in last version. Default last sentence # to -1 so no
#    indexes get set initially.
#
#   Version 3.7.12 - 1/7/23 - Ron Lockwood
#    Change the way we save the last sentence # selected. Use a class variable to
#    keep track of it. Fixes #370.
#
#   Earlier version history removed on 2/4/25.
#
#   Allow the user to test source language input live against transfer rules.
#
#   By default the transfer rules file, the bilingual lexicon file and the
#   source text file are loaded according to the configuration file. These
#   can be changed as desired.
#
#   The user can choose to select words from a sentence in the source text or
#   select a whole sentence or manually enter words in data stream format.
#   In the first two cases, the selection(s) are converted to data stream format.
#   The user can also choose which transfer rules to "turn on".
#   When Test button is pressed the selected transfer rules are run against the
#   source data stream and the target data stream is put into the target box.
#   Also the info. window will show errors and/or rules that have been matched.
#
#   Behind the scenes this tool is modifying a special source text file and
#   transfer rule file. It thens runs Apertium tools to get the results.
#
#   Synthesis is done with either STAMP or HermitCrab.
#

import os
import re
import regex
import unicodedata
import copy
import xml.etree.ElementTree as ET
import shutil
from subprocess import call

from SIL.LCModel import * # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr # type: ignore

from flextoolslib import *
from flexlibs import FLExProject

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QCheckBox, QDialogButtonBox, QToolTip, QSizePolicy

import Mixpanel
import InterlinData
import TextInOutUtils
from Testbed import *
import RunApertium
import Utils
import ReadConfig
import CatalogTargetAffixes
import ConvertTextToSTAMPformat
import DoStampSynthesis
import DoHermitCrabSynthesis
import ExtractBilingualLexicon
import TestbedLogViewer

from LiveRuleTester2 import Ui_LRTWindow
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'LiveRuleTesterTool'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'LiveRuleTester', 'TextClasses', 'InterlinData', 'TextInOutUtils', 'Testbed', 'CatalogTargetAffixes', 
                        'ConvertTextToSTAMPformat', 'DoStampSynthesis', 'DoHermitCrabSynthesis', 'ExtractBilingualLexicon', 'TestbedLogViewer'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Live Rule Tester Tool2",
        FTM_Version    : "3.14",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("LiveRuleTesterTool", "Test transfer rules and synthesis live against specific words."),
        FTM_Help       : "", 
        FTM_Description: _translate("LiveRuleTesterTool", 
"""The Live Rule Tester Tool is a tool that allows you to test source words or
sentences live against transfer rules. This tool is especially helpful for
finding out why transfer rules are not doing what you expect them to do.
You can zero in on the problem by selecting just one source word and applying
the pertinent transfer rule. In this way you don't have to run the whole system
against the whole text file and all transfer rules. You can also test that the
transfer results get synthesized correctly into target words. If you want, you
can add the source lexical items paired with the synthesis results to a testbed.
You can run the testbed to check that you are getting the results you expect.""")}

app.quit()
del app

ZOOM_INCREASE_FACTOR = 1.15
SAMPLE_LOGIC = 'Sample logic'
MAX_CHECKBOXES = 80
LIVE_RULE_TESTER_FOLDER = 'LiveRuleTester'
TARGET_AFFIX_GLOSSES_FILE = 'target_affix_glosses.txt'
ANA_FILE = 'myText.ana'
SYNTHESIS_FILE = 'myText.txt'
WINDOWS_SETTINGS_FILE = 'window.settings.txt'
HC_PARSES_FILE = 'HermitCrabParses.txt'
HC_MASTER_FILE = 'HermitCrabMaster.txt'
HC_SURFACE_FORMS_FILE = 'HermitCrabSurfaceForms.txt'
ENVIR_VAR_FIELDWORKSDIR = 'FIELDWORKSDIR'

# These strings need to be identical with the Makefile in the LiveRuleTester folder
SOURCE_APERT = 'source_text.txt'
RULE_FILE1 = 'transfer_rules.t1x'
TARGET_FILE1 = 'target_text1.txt'
LOG_FILE = 'apertium_log.txt'
RULE_FILE2 = 'transfer_rules.t2x'
TARGET_FILE2 = 'target_text2.txt'
LOG_FILE2 = 'apertium_log2.txt'
RULE_FILE3 = 'transfer_rules.t3x'
TARGET_FILE = 'target_text.txt'
LOG_FILE3 = 'apertium_log3.txt'
BILING_FILE_IN_TESTER_FOLDER = 'bilingual.dix'
SENT_TAG = '<sent>'

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
        self.__RTL = False
    def getSent(self, sentNum):
        if sentNum not in range(0, len(self.__localData)):
            sentNum = 0
        return self.__localData[sentNum]
    def setRTL(self, val):
        self.__RTL = val
    def getRTL(self):
        return self.__RTL
    def rowCount(self, parent):
        return len(self.__localData)
    def data(self, index, role):
        mySent = self.__localData[index.row()]

        if role == QtCore.Qt.DisplayRole:
            value = self.joinTupParts(mySent, 0)

            if self.getRTL():
                value = '\u200F' + value + '\u200F'

            return value

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
    def joinTupParts(self, tupList, i):
        ret = ''

        for t in tupList:
            # don't put a space before sentence punctuation
            if len(t) > i+1 and re.search(SENT_TAG, t[i+1]):
                ret += t[i]
            else:
                ret += ' ' + t[i]

        return ret.lstrip()

class Main(QMainWindow):

    def __init__(self, sentence_list, biling_file, sourceText, DB, configMap, report, sourceTextList, ruleCount=None, sentPunc=''):
        QMainWindow.__init__(self)
        self.ui = Ui_LRTWindow()
        self.ui.setupUi(self)

        self.__biling_file = biling_file
        self.__sourceText = sourceText
        self.__DB = DB
        Utils.loadSourceTextList(self.ui.SourceTextCombo, self.__sourceText, sourceTextList)
        self.__configMap = configMap
        self.__report = report
        self.__sentPunc = sentPunc
        self.__transfer_rules_file = None
        self.__replFile = None
        self.advancedTransfer = False
        self.__convertIt = True
        self.__extractIt = True
        self.__doCatalog = True
        self.rulesChanged = True
        self.fixBilingLex = True
        self.__bilingMap = {}
        self.nothingSelectedMsg = _translate('LiveRuleTesterTool', 'Nothing selected. Select at least one word or sentence.')

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

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
        self.wordsCheckedList = []
        self.interChunkRulesCheckedList = []
        self.postChunkRulesCheckedList = []
        self.restartTester = False
        self.lastSentNum = -1
        self.startTestbedLogViewer = False
        self.startRuleAssistant = False
        self.startReplacementEditor = False
        self.HCdllObj = None

        #policy = self.ui.TestButton.sizePolicy()
        #self.ui.TestButton.setSizePolicy(QSizePolicy.Minimum, policy.verticalPolicy())
        #self.ui.startRuleAssistant.hide()

        self.advancedWidgetsList = [
            self.ui.rebuildBilingLexButton,
            self.ui.startRuleAssistant,
            self.ui.viewBilingualLexiconButton,
            self.ui.editReplacementButton,
            self.ui.selectAllButton,
            self.ui.unselectAllButton,
            self.ui.upButton,
            self.ui.downButton,
            self.ui.editTransferRulesButton,
            self.ui.traceHermitCrabSynthesisCheckBox,
            self.ui.startRuleAssistant,
            self.ui.applyTextOutRulesCheckbox,
            self.ui.DoNotCleanupCheckbox,
            self.ui.addMultipleCheckBox,
            self.ui.editTestbedButton,
            self.ui.viewTestbedLogButton,
        ]

        # Reset icon images
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "UpArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.upButton.setIcon(icon)

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(FTPaths.TOOLS_DIR, "DownArrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.downButton.setIcon(icon2)

        # Tie controls to functions
        self.ui.TestButton.clicked.connect(self.TransferClicked)
        self.ui.listSentences.clicked.connect(self.listSentClicked)
        self.ui.listTransferRules.clicked.connect(self.rulesListClicked)
        self.ui.listInterChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.listPostChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.SentCombo.currentIndexChanged.connect(self.listSentComboClicked)
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
        self.ui.SourceTextCombo.activated.connect(self.sourceTextComboChanged)
        self.ui.ZoomIncreaseSource.clicked.connect(self.ZoomIncreaseSourceClicked)
        self.ui.ZoomDecreaseSource.clicked.connect(self.ZoomDecreaseSourceClicked)
        self.ui.ZoomIncreaseTarget.clicked.connect(self.ZoomIncreaseTargetClicked)
        self.ui.ZoomDecreaseTarget.clicked.connect(self.ZoomDecreaseTargetClicked)
        self.ui.startRuleAssistant.clicked.connect(self.OpenRuleAssistantClicked)
        # self.ui.advancedOptionsCheckbox.clicked.connect(self.AdvancedOptionsCheckboxClicked)

        # Set up paths to things.
        # Get parent folder of the folder flextools.ini is in and add \Build to it
        self.buildFolder = FTPaths.BUILD_DIR

        self.testerFolder = self.buildFolder + '\\' + LIVE_RULE_TESTER_FOLDER
        self.affixGlossPath = self.testerFolder + '\\' + TARGET_AFFIX_GLOSSES_FILE
        self.transferResultsPath = self.testerFolder + '\\' + TARGET_FILE
        self.targetAnaPath = self.testerFolder + '\\' + ANA_FILE
        self.synthesisFilePath = self.testerFolder + '\\' + SYNTHESIS_FILE
        self.windowsSettingsFile = self.testerFolder + '\\' + WINDOWS_SETTINGS_FILE
        self.parsesFile = self.testerFolder + '\\' + HC_PARSES_FILE
        self.HCmasterFile = self.testerFolder + '\\' + HC_MASTER_FILE
        self.surfaceFormsFile = self.testerFolder + '\\' + HC_SURFACE_FORMS_FILE

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
        selectWordsSentNum = 0
        savedSourceTextName = ''
        sourceFontSizeStr = ''
        targetFontSizeStr = ''

        # Clear text boxes and labels
        self.__ClearStuff()

        # Open a settings file to see which tabs were last used.
        # Put this in a try so that if the number of values in the users file are fewer than expected,
        # We won't crash and instead just ignore the saved values
        try:
            with open(self.windowsSettingsFile) as f:

                line = f.readline()

                ruleTab, sourceTab, selectWordsSentNum, savedSourceTextName = line.split('|')
                ruleTab = int(ruleTab)
                sourceTab = int(sourceTab)
                selectWordsSentNum = int(selectWordsSentNum)
                savedSourceTextName = savedSourceTextName.strip()

                # Read the 2nd line which is the state of the rule checkboxes
                checkBoxStateStr = f.readline().strip()
                self.rulesCheckedList = [int(char) for char in checkBoxStateStr]

                # Read the 3rd line which is the state of the word checkboxes
                checkBoxStateWordsStr = f.readline().strip()
                self.wordsCheckedList = [int(char) for char in checkBoxStateWordsStr]

                # Read the 4th line which is the source and target font size
                fontSizesStr = f.readline().strip()
                sourceFontSizeStr, targetFontSizeStr = fontSizesStr.split('|')

                # Read the 5th line which is the checkbox values for Apply Text Out rules and Do not clean up unknown words
                checkBoxStateStr = f.readline().strip()

                # Assuming checkBoxStateStr contains two characters, each either '1' or '0'
                if len(checkBoxStateStr) == 2:

                    # Set the checkboxes based on the values in the list
                    self.ui.applyTextOutRulesCheckbox.setChecked(checkBoxStateStr[0] == '1')
                    self.ui.DoNotCleanupCheckbox.setChecked(checkBoxStateStr[1] == '1')

                # Read the 6th line which is the state of the advanced options checkbox
                # advancedOptionsStr = f.readline().strip()

                # if len(advancedOptionsStr) > 0:

                #     self.ui.advancedOptionsCheckbox.setChecked(advancedOptionsStr[0] == '1')
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
            self.retVal = False
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
                if self.hasRTLdata(surface_form):
                    self.ui.listSentences.setLayoutDirection(QtCore.Qt.RightToLeft)
                    self.ui.SentCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                    self.__sent_model.setRTL(True)
                    found_rtl = True
                    break

        if found_rtl:
            # this doesn't seem to be working
            self.ui.TargetTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)

        # Read the bilingual lexicon into a map. this has to come before the combo box clicking for the first sentence
        if self.ReadBilingualLexicon() == False:
            self.retVal = False
            self.close()
            return

        # Set the source and target widget font sizes
        if targetFontSizeStr and sourceFontSizeStr:

            try:
                self.setSourceWidgetsFont(float(sourceFontSizeStr))
                self.setTargetWidgetsFont(float(targetFontSizeStr))
            except:
                pass

        self.ui.listSentences.setModel(self.__sent_model)
        self.ui.SentCombo.setModel(self.__sent_model)

        # Only use the sentence number from saved values if the text is the same one that was last saved
        if savedSourceTextName != sourceText:

            selectWordsSentNum = 0

        # Set the index of the combo box and sentence list to what was saved before
        self.ui.SentCombo.setCurrentIndex(selectWordsSentNum)
        qIndex = self.__sent_model.createIndex(selectWordsSentNum, 0)
        self.ui.listSentences.setCurrentIndex(qIndex)
        self.listSentClicked()

        if savedSourceTextName == sourceText and sourceTab == 0: # 0 means checkboxes with words

            # Check the saved words
            self.restoreCheckedWords()

        # Copy bilingual file to the tester folder
        try:
            # always name the local version bilingual.dix which is what the Makefile has
            shutil.copy(self.__biling_file, os.path.join(self.testerFolder, BILING_FILE_IN_TESTER_FOLDER))
        except:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Copy Error'), _translate('LiveRuleTesterTool', 'Could not copy the bilingual file to the folder: {0}. Please check that it exists.').format(self.testerFolder))
            self.retVal = False
            return

        # Get replacement file name.
        self.__replFile = ReadConfig.getConfigVal(self.__configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, self.__report)

        if not self.__replFile:
            self.retVal = False
            self.close()
            return

        ## Testbed preparation
        # Disable buttons as needed.
        self.ui.addToTestbedButton.setEnabled(False)
        self.ui.addMultipleCheckBox.setEnabled(False)

        # Get the path to the testbed file
        testbedPath = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TESTBED_FILE, self.__report, False)

        if not testbedPath:
            self.retVal = False
            self.close()

        self.__testbedPath = testbedPath

        # Disable the edit testbed button if the testbed doesn't exist.
        if os.path.exists(self.__testbedPath) == False:
            self.ui.editTestbedButton.setEnabled(False)

        # See if we loaded any info on which rules were checked.
        if len(self.rulesCheckedList) > 0:

            # recheck the rules that we had saved
            self.restoreChecked()
        else:
            # Start out with all rules checked.
            self.checkThemAll()

        # Number the rules
        self.rulesListClicked(self.TRIndex)

        # Disable the View Testbed Log button if the testbed log doesn't exist
        testbedLog = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TESTBED_RESULTS_FILE, self.__report)

        if not testbedLog:
            self.retVal = False
            self.close()
            return

        if os.path.exists(testbedLog) == False:
            self.ui.viewTestbedLogButton.setEnabled(False)

        # See if we are doing HermitCrab synthesis
        hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(self.__configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, self.__report, giveError=False)

        if hermitCrabSynthesisYesNo == 'y':

            self.doHermitCrabSynthesisBool = True

        else:

            # Set HermitCrab tracing checkbox to hidden if we are doing STAMP synthesis
            self.ui.traceHermitCrabSynthesisCheckBox.hide()

            self.doHermitCrabSynthesisBool = False

        self.textOutElemTree = None

        self.manualTabText = self.ui.tabSource.tabText(2)
        self.interChunkTabText = self.ui.tabRules.tabText(1)
        self.postChunkTabText = self.ui.tabRules.tabText(2)

        # Hide the advanced widgets if needed
        # self.AdvancedOptionsCheckboxClicked()

        self.retVal = True

    # def AdvancedOptionsCheckboxClicked(self):

    #     # Show or hide the advanced widgets and tabs
    #     if self.ui.advancedOptionsCheckbox.isChecked():

    #         for widget in self.advancedWidgetsList:

    #             widget.show()
            
    #         # Add advanced tabs
    #         self.ui.tabSource.insertTab(2, self.ui.tab_manual_entry, self.manualTabText)
    #         self.ui.tabRules.insertTab(1, self.ui.tab_interchunk_rules, self.interChunkTabText)
    #         self.ui.tabRules.insertTab(2, self.ui.tab_postchunk_rules, self.postChunkTabText)

    #         # If we are doing HermitCrab synthesis, show the checkbox
    #         if not self.doHermitCrabSynthesisBool:

    #             self.ui.traceHermitCrabSynthesisCheckBox.hide()

    #         # See if we have a Text Out Rules file so we know whether to show the text out checkbox
    #         self.ui.applyTextOutRulesCheckbox.hide()
    #         textOutRulesFile = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TEXT_OUT_RULES_FILE, self.__report, giveError=False)

    #         if textOutRulesFile:
                
    #             # Check if the file exists.
    #             if os.path.exists(textOutRulesFile):

    #                 try:
    #                     self.textOutElemTree = ET.parse(textOutRulesFile)
    #                     self.ui.applyTextOutRulesCheckbox.show() 
    #                 except:
    #                     pass 

    #         # Show the Do not clean up... checkbox if the applicable setting is not 'y'
    #         if not ReadConfig.getConfigVal(self.__configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, self.__report, giveError=False) == 'y':

    #             self.ui.DoNotCleanupCheckbox.hide()
        
    #     # Not advanced options, hide the widgets and tabs
    #     else:
    #         for widget in self.advancedWidgetsList:

    #             widget.hide()

    #         # Remove advanced tabs
    #         self.ui.tabSource.removeTab(2) # Remove Manual tab
    #         self.ui.tabRules.removeTab(2)  # Remove the PostChunk tab
    #         self.ui.tabRules.removeTab(1)  # Remove the InterChunk tab   

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     self.positionZoomWidgets()

    # def showEvent(self, event):
    #     super().showEvent(event)
    #     self.positionZoomWidgets()

    # def positionZoomWidgets(self):
    #     mainWidth = self.width()
    #     tabSourceGeom = self.ui.tabSource.geometry()
    #     x = mainWidth - 8 - self.ui.ZoomDecreaseSource.width()
    #     y = tabSourceGeom.y() + tabSourceGeom.height() - self.ui.ZoomDecreaseSource.height()
    #     self.ui.ZoomDecreaseSource.move(x, y)
    #     self.ui.ZoomIncreaseSource.move(x-23, y)
    #     self.ui.ZoomLabel_2.move(x-23-184, y)
    #     self.ui.selectWordsHintLabel.move(x-23-184-340-70, y)
        
    def sourceTextComboChanged(self):

        self.restartTester = True

        # Update the source text setting in the config file
        ReadConfig.writeConfigValue(self.__report, ReadConfig.SOURCE_TEXT_NAME, self.ui.SourceTextCombo.currentText())

        # Set the global variable
        FTPaths.CURRENT_SRC_TEXT = self.ui.SourceTextCombo.currentText()

        # Have FlexTools refresh the status bar
        refreshStatusbar()

        # Close the tool and it will restart
        self.closeEvent(None)
        self.close()

    # Read the bilingual lexicon and make a map from source entries to one or more target entries
    def ReadBilingualLexicon(self):

        # Clear the map
        self.__bilingMap.clear()

        # Read the XML file
        try:
            bilingEtree = ET.parse(self.__biling_file)

        except:

            # Try and build the bilingual lexicon
            if self.ExtractBilingLex() == False:
                return False

        # try to read the XML file again
        try:
            bilingEtree = ET.parse(self.__biling_file)

        except IOError:

            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Read Error'), _translate('LiveRuleTesterTool', 'Bilingual file: {0} could not be read.').format(self.__biling_file))
            return False

        # Get the root node
        bilingRoot = bilingEtree.getroot()

        def tagSequence(node):
            return [s.attrib['n'] for s in node.iter('s')]

        # Loop through all the bilingual entries
        for entry in bilingRoot.iter('e'):

            ## <e> (entry) should either have <p><l>abc</l><r>xyz</r></p>) or <i> (p = pair, l = left, r = right)

            # Get the left part
            left = entry.find('p/l')

            # If we can't find it, it must be an <i> (identity), skip it
            if left == None:
                continue

            # Get the right part
            right = entry.find('p/r')

            # Get just the text part of the left entry. Note: it's not as easy as left.text
            key = getXMLEntryText(left)

            # See if we have the source entry already
            if key not in self.__bilingMap:

                self.__bilingMap[key] = [(left, right)]
            else:
                if tagSequence(left) == tagSequence(self.__bilingMap[key][0][0]):
                    # The current entry has the same source language tags
                    # as the first entry with this lemma in the file,
                    # so it's a replacement, and we should use the later one.
                    self.__bilingMap[key][0] = (left, right)
                else:
                    self.__bilingMap[key].append((left, right))

        return True

    def ViewBilingualLexiconButtonClicked(self):

        if os.path.exists(self.__biling_file) == False:

            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Not Found Error'), _translate('LiveRuleTesterTool', 'Bilingual file: {0} does not exist.').format(self.__biling_file))
            return

        progFilesFolder = os.environ['ProgramFiles(x86)']

        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'

        call([xxe, self.__biling_file])

    def EditTransferRulesButtonClicked(self):

        if os.path.exists(self.__transfer_rules_file) == False:

            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Not Found Error'), _translate('LiveRuleTesterTool', 'Transfer rule file: {0} does not exist.').format(self.__transfer_rules_file))
            return

        progFilesFolder = os.environ['ProgramFiles(x86)']

        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'

        call([xxe, self.__transfer_rules_file])

    def EditReplacementButton(self):

        self.startReplacementEditor = True

        # Close the tool and it will restart
        self.closeEvent(None)
        self.close()

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
        lexParser = LexicalUnitParser(lexUnitStr)

        # Check for badly formed lexical units
        if lexParser.isWellFormed() == False:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Lexical unit error'), _translate('LiveRuleTesterTool', 'The lexical unit(s) is/are incorrectly formed.'))
            return None

        # Get the lexical units from the parser
        return lexParser.getLexicalUnits()

    def buildTestNodeFromInput(self, lexUnitList, synthesisResult):
        # Get the name of the text this lu came from
        origin = self.__sourceText

        # Initialize a Test XML object and fill out its data given a list of
        # lexical units and a result from the synthesis step
        myObj = TestbedTestXMLObject(lexUnitList, origin, synthesisResult)

        return myObj

    def ExtractBilingLex(self):

        # Extract the bilingual lexicon
        errorList = ExtractBilingualLexicon.extract_bilingual_lex(self.__DB, self.__configMap)

        # check for fatal errors
        fatal, msg = Utils.checkForFatalError(errorList, None)

        if fatal:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Extract Bilingual Lexicon Error'), _translate('LiveRuleTesterTool', '{0}\nRun the Extract Bilingual Lexicon module separately for more details.').format(msg))
            return False

        self.__report.Info(_translate('LiveRuleTesterTool', 'Built the bilingual lexicon.'))
        return True

    def RebuildBilingLexButtonClicked(self):

        self.setCursor(QtCore.Qt.WaitCursor)

        self.fixBilingLex = True

        # Save the last sentence number
        if self.ui.tabSource.currentIndex() == 0: # check boxes

            # Save the checked words state
            self.saveCheckedWords()
            self.lastSentNum = self.ui.SentCombo.currentIndex()

        elif self.ui.tabSource.currentIndex() == 1: # sentence list

            self.lastSentNum = self.ui.listSentences.currentIndex().row()

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

        # Try and build the bilingual lexicon
        if self.ExtractBilingLex() == False:
            return

        # Reload the bilingual map for showing tooltips
        if self.ReadBilingualLexicon() == False:
            return

        # Copy bilingual file to the tester folder
        try:
            # always name the local version bilingual.dix which is what the Makefile has
            shutil.copy(self.__biling_file, os.path.join(self.testerFolder, 'bilingual.dix'))
        except:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Copy Error'), _translate('LiveRuleTesterTool', 'Could not copy the bilingual file to the folder: {0}. Please check that it exists.').format(self.testerFolder))
            self.retVal = False
            return

        # Make sure the last sentence used gets selected.
        self.sourceTabClicked()

        # Re-check the words that had been checked, if we were on Select Words view.
        if self.ui.tabSource.currentIndex() == 0:

            self.restoreCheckedWords()

        self.__ClearStuff()

        self.unsetCursor()

    def ViewTestbedLogButtonClicked(self):

        self.startTestbedLogViewer = True

        # Close the tool and it will restart
        self.closeEvent(None)
        self.close()

    def OpenRuleAssistantClicked(self):
        self.startRuleAssistant = True
        self.closeEvent(None)
        self.close()

    def EditTestbedLogButtonClicked(self):

        if os.path.exists(self.__testbedPath) == False:

            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Not Found Error'), _translate('LiveRuleTesterTool', 'Testbed file: {0} does not exist.').format(self.__testbedPath))
            return

        progFilesFolder = os.environ['ProgramFiles(x86)']

        xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'

        call([xxe, self.__testbedPath])

    def ShowOverwritePrompt(self, luStr, showAllButtons=True):

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(_translate('LiveRuleTesterTool', 'Test Exists'))
        msgBox.setText(_translate('LiveRuleTesterTool', 'There is a test that already exists in the testbed that matches the lexical unit:\n\n{0}\n\nDo you want to overwrite it?').format(luStr))
        
        # Add custom buttons based on the parameter
        if showAllButtons:

            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.NoToAll)
        else:
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        msgBox.setDefaultButton(QMessageBox.Yes)
        
        # Show the dialog and get the user's response
        result = msgBox.exec_()
        return result
        
    def removeSentLUs(self, luObjList):

        # Go throught the list in reverse and remove <sent> LU objects.
        for i in range(len(luObjList) - 1, -1, -1):

            if luObjList[i].getGramCat() == 'sent':

                luObjList.pop(i)
        return
    
    def removeNonSentencePunctuation(self, inputStr, sentencePunctuation):

        errMsg = ''

        # Extract all punctuation characters 
        allPunctuation = set(regex.findall(r'\p{P}', inputStr))

        # If the user is applying text out rules, we need to convert the sentence-ending punctuation with the same rules before we filter them out.
        if self.ui.applyTextOutRulesCheckbox.isChecked() and self.textOutElemTree and inputStr:
            
            sentencePunctuation, errMsg = TextInOutUtils.applySearchReplaceRules(sentencePunctuation, self.textOutElemTree)

            if errMsg:

                return "", errMsg
        
        # Filter out sentence-ending punctuation
        nonSentencePunctuation = allPunctuation - set(sentencePunctuation)
        
        if nonSentencePunctuation:

            # Create a regex pattern to match non-sentence-ending punctuation
            pattern = f"[{regex.escape(''.join(nonSentencePunctuation))}]"
            
            # Remove non-sentence-ending punctuation from the inputStr
            resultStr = regex.sub(pattern, "", inputStr)
            
            return resultStr, errMsg
        
        else:
            # If no non-sentence-ending punctuation was found, return the original string
            return inputStr, errMsg

    def AddTestbedButtonClicked(self):
        
        self.ui.TestsAddedLabel.setText('')
        activeLexicalUnitsStr = self.getActiveLexicalUnits()

        # If there are no lexical units, warn the user and return
        if not activeLexicalUnitsStr.strip():

            self.ui.SynthTextEdit.setPlainText(self.nothingSelectedMsg)
            return

        # Set the direction attribute
        if self.__sent_model.getRTL():
            direction = RTL
        else:
            direction = LTR

        try:
            fileObj = FlexTransTestbedFile(direction, self.__report)
        except:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Not Found Error'), _translate('LiveRuleTesterTool', 'Problem with the testbedfile. Check that you have TestbedFile set to a value in your configuration file. Normally it is set to ..\\testbed.xml'))
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

        # Remove non-sentence-ending punctuation
        synResult, errMsg = self.removeNonSentencePunctuation(synResult, self.__sentPunc)

        if errMsg:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Testbed Error'), errMsg)
            return
        
        cnt = 0

        # Check if add-multiple was selected
        if self.ui.addMultipleCheckBox.isChecked():

            luObjList = self.getLexUnitObjsFromString(activeLexicalUnitsStr)
            if luObjList == None:
                return

            # Remove any <sent> LUs. It doesn't make sense to add a test of just a sentence punctuation mark mapped to it's result.
            # If that's really needed it can be added without checking the Add multiple words checkbox.
            self.removeSentLUs(luObjList)

            # Remove all punctuation from the result.
            synResult = regex.sub(r'\p{P}', '', synResult)
            resultList = synResult.split(' ') 

            # Check for an equal amount of lexical units as synthesis results
            if len(luObjList) != len(resultList):
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Testbed Error'), _translate('LiveRuleTesterTool', 'There is not an equal number of synthesis results for the lexical units you have. Cannot add to the testbed.'))
                return

            retVal = None

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
                        if retVal != QDialogButtonBox.YesToAll:
                            retVal = self.ShowOverwritePrompt(myTestXMLObj.getLUString())

                        # See if we should overwrite
                        if retVal == QDialogButtonBox.Yes or retVal == QDialogButtonBox.YesToAll:
                            testbedObj.overwriteInTestbed(existingTestXMLObj, myTestXMLObj)
                            cnt += 1

                        # Break out of the loop if the user said no to all
                        elif retVal == QDialogButtonBox.NoToAll:
                            break
                    else:
                        testbedObj.addToTestbed(myTestXMLObj)
                        cnt += 1

        else:
            luObjList = self.getLexUnitObjsFromString(activeLexicalUnitsStr)

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

                    # Get confirmation from the user. Only display Yes and No buttons.
                    retVal = self.ShowOverwritePrompt(myTestXMLObj.getLUString(), showAllButtons=False)

                    # See if we should overwrite
                    if retVal == QMessageBox.Yes:

                        testbedObj.overwriteInTestbed(existingTestXMLObj, myTestXMLObj)
                        cnt += 1
                else:
                    testbedObj.addToTestbed(myTestXMLObj)
                    cnt += 1

        # Tell the user how many tests were added.
        if cnt == 1:

            feedbackStr = _translate('LiveRuleTesterTool', '{0} test added.').format(str(cnt))
        else:
            feedbackStr = _translate('LiveRuleTesterTool', '{0} tests added.').format(str(cnt))

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

    def hasRTLdata(self, word1):
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
        errorList = []

        # Check if the target text is empty give a warning
        if not self.ui.TargetTextEdit.toPlainText().strip() or self.ui.TargetTextEdit.toPlainText() == self.nothingSelectedMsg:

            self.ui.SynthTextEdit.setPlainText(_translate('LiveRuleTesterTool', 'There are no target text morphemes. Click the Transfer button first.'))
            return

        # If there are no lexical units, warn the user and return
        if not self.getActiveLexicalUnits().strip():

            self.ui.SynthTextEdit.setPlainText(self.nothingSelectedMsg)
            return        

        self.setCursor(QtCore.Qt.WaitCursor)

        # Make the text box blank to start out.
        self.ui.SynthTextEdit.setPlainText('')

        if self.doHermitCrabSynthesisBool:

            HCconfigPath = ReadConfig.getConfigVal(self.__configMap, ReadConfig.HERMIT_CRAB_CONFIG_FILE, self.__report)

            if not HCconfigPath:

                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Configuration Error'), _translate('LiveRuleTesterTool', 'HermitCrab settings not found.'))
                self.unsetCursor()
                return
            
            useHCsynthDll = True
            if useHCsynthDll and self.HCdllObj is None:

                # Change to the Fieldworks folder for doing the dll operations
                fieldworksDir = os.getenv(ENVIR_VAR_FIELDWORKSDIR)

                try:
                    os.chdir(fieldworksDir)

                except OSError as e:

                    QMessageBox.warning(self, _translate("LiveRuleTesterTool", 'Directory Error'), _translate("LiveRuleTesterTool", 'Could not change to the Fieldworks directory: {fieldworksDir}. Error: {e}').format)
                    self.unsetCursor()
                    return

                # Import the clr module from pythonnet
                import clr 

                # Load the DLL 
                clr.AddReference('HCSynthByGlossDll')
                from SIL.HCSynthByGloss2 import HCSynthByGlossDll # type: ignore

                # Initialize the object with the output file name
                try:
                    self.HCdllObj = HCSynthByGlossDll(self.surfaceFormsFile)

                except Exception as e:

                    QMessageBox.warning(self, _translate("LiveRuleTesterTool", 'DLL Error'), _translate("LiveRuleTesterTool", 'An exception occurred. Could not initialize the HermitCrab synthesis DLL. Error: {e}').format(e=e))
                    self.unsetCursor()
                    return

        ## CATALOG
        # Catalog all the target affixes
        # We only need to do this once, until the user requests to refresh the lexicon
        if self.__doCatalog:

            try:
                errorList = CatalogTargetAffixes.catalog_affixes(self.__DB, self.__configMap, self.affixGlossPath)
            except:
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Locked DB?'), _translate('LiveRuleTesterTool', 'The project could be locked. Check if sharing is checked for the target project. \
                                    If it is, run the Clean Files module and then the Catalog Target Affixes module and report any errors to the developers.'))
                self.unsetCursor()
                return

            # check for fatal errors
            fatal, msg = Utils.checkForFatalError(errorList, None)

            if fatal:
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Catalog Prefix Error'), _translate('LiveRuleTesterTool', '{0}\nRun the {1} module separately for more details.').format(msg, CatalogTargetAffixes.docs[FTM_Name]))
                self.unsetCursor()
                return

            self.__doCatalog = False

        ## CONVERT
        # if the target text has changed, we need to do the affixes and convert the target text to STAMP format
        if self.__convertIt == True:

            # Convert the target text to .ana format (for STAMP)
            errorList = ConvertTextToSTAMPformat.convert_to_STAMP(self.__DB, self.__configMap, self.targetAnaPath, self.affixGlossPath, self.transferResultsPath,
                                                                   self.doHermitCrabSynthesisBool, self.HCmasterFile)
            # check for fatal errors
            fatal, msg = Utils.checkForFatalError(errorList, None)

            if fatal:
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Convert to STAMP Error'), _translate('LiveRuleTesterTool', '{0}\nRun the Convert to {1} module separately for more details.').format(msg, ConvertTextToSTAMPformat.docs[FTM_Name]))
                self.unsetCursor()
                return

            self.__convertIt = False

        ## EXTRACT
        # if the refresh lexicon button was pressed or this is the first run, extract the target lexicon
        if self.__extractIt == True:

            # We have two possible extracts, one for STAMP and one for HermitCrab
            if self.doHermitCrabSynthesisBool:

                # Extract the lexicon, HermitCrab style. (The whole HC configuration file, actually)
                errorList = DoHermitCrabSynthesis.extractHermitCrabConfig(self.__DB, self.__configMap, HCconfigPath, self.__report, useCacheIfAvailable=True, DLLobj=self.HCdllObj)

                # check for fatal errors
                fatal, msg = Utils.checkForFatalError(errorList, None)

                if fatal:
                    errorStr = msg
                    if not self.HCdllObj:
                        errorStr += _translate('LiveRuleTesterTool', '\nRun the {0} module separately for more details.').format(DoHermitCrabSynthesis.docs[FTM_Name])
                    QMessageBox.warning(self, _translate('LiveRuleTesterTool', '{0} Error').format(DoHermitCrabSynthesis.docs[FTM_Name]), errorStr)
                    self.unsetCursor()
                    return
            else:
                # Redo the catalog of prefixes in case the user changed an affix
                if self.__doCatalog:

                    errorList = CatalogTargetAffixes.catalog_affixes(self.__DB, self.__configMap, self.affixGlossPath)

                    # check for fatal errors
                    fatal, msg = Utils.checkForFatalError(errorList, None)

                    if fatal:
                        QMessageBox.warning(self, _translate('LiveRuleTesterTool', '{0} Error').format(CatalogTargetAffixes.docs[FTM_Name]), _translate('LiveRuleTesterTool', '{0}\nRun the {1} module separately for more details.').format(msg, CatalogTargetAffixes.docs[FTM_Name]))
                        self.unsetCursor()
                        return

                # Extract the lexicon, STAMP style
                errorList = DoStampSynthesis.extract_target_lex(self.__DB, self.__configMap)

                # check for fatal errors
                fatal, msg = Utils.checkForFatalError(errorList, None)

                if fatal:
                    QMessageBox.warning(self, _translate('LiveRuleTesterTool', '{0} Error').format(DoStampSynthesis.docs[FTM_Name]), _translate('LiveRuleTesterTool', '{0}\nRun the {1} module separately for more details.').format(msg, DoStampSynthesis.docs[FTM_Name]))
                    self.unsetCursor()
                    return

        ## SYNTHESIZE
        # We have two possible syntheses, one for STAMP and one for HermitCrab
        if self.doHermitCrabSynthesisBool:

            # Check if the user wants to do a trace which will bring up a web page.
            traceIt = self.ui.traceHermitCrabSynthesisCheckBox.isChecked()

            errorList = DoHermitCrabSynthesis.synthesizeWithHermitCrab(self.__configMap, HCconfigPath, self.synthesisFilePath, self.parsesFile, self.HCmasterFile, self.surfaceFormsFile, self.transferResultsPath,\
                                                                       report=None, trace=traceIt, DLLobj=self.HCdllObj, overrideClean=self.ui.DoNotCleanupCheckbox.isChecked())

            # check for fatal errors
            fatal, msg = Utils.checkForFatalError(errorList, None)

            if fatal:
                errorStr = msg
                if not self.HCdllObj:
                    errorStr += _translate('LiveRuleTesterTool', '\nRun the {0} module separately for more details.').format(DoHermitCrabSynthesis.docs[FTM_Name])
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', '{0} Error').format(DoHermitCrabSynthesis.docs[FTM_Name]), errorStr)
                self.unsetCursor()
                return
        else:
            errorList = DoStampSynthesis.synthesize(self.__configMap, self.targetAnaPath, self.synthesisFilePath, report=None, overrideClean=self.ui.DoNotCleanupCheckbox.isChecked())

            # check for fatal errors
            fatal, msg = Utils.checkForFatalError(errorList, None)

            if fatal:
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', '{moduleName} Error').format(moduleName=DoStampSynthesis.docs[FTM_Name]), 
                     _translate('LiveRuleTesterTool', f'{msg}\n' + 'Run the {moduleName} module separately for more details.').format(moduleName=DoStampSynthesis.docs[FTM_Name]))
                self.unsetCursor()
                return

        # Load the synthesized result into the text box
        synf = open(self.synthesisFilePath, encoding='utf-8')
        synthText = synf.read()

        # Apply Text Out Rules if desired
        if self.ui.applyTextOutRulesCheckbox.isChecked() and self.textOutElemTree and len(synthText) > 0:

            synthText, errMsg = TextInOutUtils.applySearchReplaceRules(synthText, self.textOutElemTree)

            if synthText is None:

                synthText = errMsg

        # if RTL text, prepend the RTL mark
        if self.hasRTLdata(synthText[:len(synthText)//2]): # just check the 1st half of the string.
            
            synthText = '\u200F' + synthText
            self.ui.SynthTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.ui.SynthTextEdit.setLayoutDirection(QtCore.Qt.LeftToRight)

        # If we got no output, give a string to the user to indicate it.
        if len(synthText) == 0:
            
            synthText = 'Synthesis produced no output.'

        self.ui.SynthTextEdit.setPlainText(synthText)

        synf.close()

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

        # Redo the numbering
        self.rulesListClicked(self.TRIndex)

    def collectChecks(self, myList, myModel):

        # Loop through all the items in the rule list model
        for i in range(0, myModel.rowCount()):

            # Save the state of each check box
            if myModel.item(i).checkState():
                myList.append(QtCore.Qt.Checked)
            else:
                myList.append(QtCore.Qt.Unchecked)

    def collectWordChecks(self, myList, checkBoxList):

        # Loop through all the items in the rule list model
        for i in range(0, len(checkBoxList)):

            # We only need to check the first x that are visible to the user.
            if checkBoxList[i].isVisible() == False:
                break

            # Save the state of each check box
            if checkBoxList[i].checkState():
                myList.append(QtCore.Qt.Checked)
            else:
                myList.append(QtCore.Qt.Unchecked)

    def saveCheckedWords(self):

        self.wordsCheckedList.clear()

        self.collectWordChecks(self.wordsCheckedList, self.__checkBoxList)

    def saveChecked(self):

        self.rulesCheckedList.clear()

        self.collectChecks(self.rulesCheckedList, self.__transferModel)

        if self.advancedTransfer:

            self.interChunkRulesCheckedList.clear()
            self.collectChecks(self.interChunkRulesCheckedList, self.__interChunkModel)

            self.postChunkRulesCheckedList.clear()
            self.collectChecks(self.postChunkRulesCheckedList, self.__postChunkModel)

    def recheck(self, myList, myModel):

        # Loop through all the items in the rule list model
        for i in range(0, myModel.rowCount()):

            if i < len(myList):

                # Set the state of each check box
                myModel.item(i).setCheckState(myList[i])

    def recheckWords(self, myList, checkBoxList):

        # Loop through all the items in the rule list model
        for i in range(0, len(checkBoxList)):

            if i < len(myList):

                # Set the state of each check box
                checkBoxList[i].setCheckState(myList[i])
            else:
                break

    def restoreCheckedWords(self):

        self.recheckWords(self.wordsCheckedList, self.__checkBoxList)
        self.SourceCheckBoxClicked()

    def restoreChecked(self):

        self.recheck(self.rulesCheckedList, self.__transferModel)

        if self.advancedTransfer:

            self.recheck(self.interChunkRulesCheckedList, self.__interChunkModel)
            self.recheck(self.postChunkRulesCheckedList, self.__postChunkModel)

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
        for j in range(0, len(tokens)-1,2):

            # Save the lexical unit in the saved string

            # if we have <sent> remove the space currently at the end of lexicalUnits
            if re.search(SENT_TAG, tokens[j+1]):
                self.__lexicalUnits = self.__lexicalUnits[:-1]

            # Preserve whitespace that may be between compound elements by adding the j+2 item
            self.__lexicalUnits += '^' + tokens[j+1] + '$' + tokens[j+2]

            # Turn the lexical unit into color-coded html.
            processLexicalUnit(tokens[j+1]+' ', paragraph_element, self.__sent_model.getRTL(), True) # last parameter: show UNK categories

        # Add a space at the end
        self.__lexicalUnits += ' '

    def SourceCheckBoxClicked(self):
        self.ui.TestsAddedLabel.setText('')

        mySent = self.__sent_model.getSent(self.lastSentNum)
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

        self.lastSentNum = self.ui.listSentences.currentIndex().row()
        mySent = self.__sent_model.getSent(self.lastSentNum)
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

    def __ClearStuff(self):

        self.ui.TestsAddedLabel.setText('')
        self.ui.TargetTextEdit.setPlainText('')
        self.ui.LogEdit.setText('')
        self.ui.SynthTextEdit.setPlainText('')
        self.ui.warningLabel.setText('')

    def sourceTabClicked(self):

        if self.ui.tabSource.currentIndex() == 0: # check boxes

            # if no selection (-1), don't set the current index
            if self.lastSentNum != -1:

                self.ui.SentCombo.setCurrentIndex(self.lastSentNum)
                self.ui.SentCombo.update()
                self.listSentComboClicked()

            # self.ui.selectWordsHintLabel.setVisible(True)

        elif self.ui.tabSource.currentIndex() == 1: # sentence list

            # if no selection (-1), don't set the current index
            if self.lastSentNum != -1:

                qIndex = self.__sent_model.createIndex(self.lastSentNum, 0)
                self.ui.listSentences.setCurrentIndex(qIndex)
                self.listSentClicked()

            # self.ui.selectWordsHintLabel.setVisible(False)

        else: # manual entry
            pass
            # self.ui.selectWordsHintLabel.setVisible(False)

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

                self.rulesListClicked(self.TRIndex)
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

                self.rulesListClicked(self.TRIndex)
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

                self.rulesListClicked(self.TRIndex)
                self.__ClearStuff()

            self.__prevTab = self.ui.tabRules.currentIndex()

    def listSentComboClicked(self):

        self.lastSentNum = self.ui.SentCombo.currentIndex()
        mySent = self.__sent_model.getSent(self.lastSentNum)
        space_val = 10
        y_spacing = 30
        x_margin = 2
        x = x_margin
        y = 2

        # Clear stuff
        self.ui.SelectedWordsEdit.setPlainText('')
        self.__ClearAllChecks()
        self.__lexicalUnits = ''
        self.ui.ManualEdit.setPlainText('')

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

            arrowStr = '⭠'
        else:
            arrowStr = '⭢'

        # Go through all pairs and add them to the tool tip
        for source, target in srcTrgtPairsList:

            # Combine source and target into one paragraph html string
            tipStr += convertXMLEntryToColoredString(source, isRtl)[:-4] # remove </p> at end
            tipStr += f'&nbsp;{arrowStr}&nbsp;'

            # If the target is mapped to nothing (which happens if the user chose **None** in the linker),
            # set the right side of the tooltip to **None**
            if target.text is None:

                # If we have RTL orientation, prepend the RTL marker character
                if isRtl:
                    tipStr += '\u200F' + Utils.NONE_HEADWORD
                else:
                    tipStr += Utils.NONE_HEADWORD
            else:
                tipStr += convertXMLEntryToColoredString(target, isRtl)[3:] # remove <p> at beginning

        return tipStr.strip()

    def closeEvent(self, event):

        rulesTab = self.ui.tabRules.currentIndex()
        sourceTab = self.ui.tabSource.currentIndex()

        # Save which rules were checked.
        self.saveChecked()
        checkedStateStr = ''.join(map(str, self.rulesCheckedList))

        # Save which words were checked.
        self.saveCheckedWords()
        checkedWordsState = ''.join(map(str, self.wordsCheckedList))

        # Get the font sizes of source and target widgets
        myFont = self.ui.SelectedSentencesEdit.font()
        sourceFontSizeStr = str(myFont.pointSizeF())
        myFont = self.ui.SynthTextEdit.font()
        targetFontSizeStr = str(myFont.pointSizeF())

        # Get checkbox values
        checkboxStr1 = '1' if self.ui.applyTextOutRulesCheckbox.isChecked() else '0'
        checkboxStr2 = '1' if self.ui.DoNotCleanupCheckbox.isChecked() else '0'
        # checkboxStr3 = '1' if self.ui.advancedOptionsCheckbox.isChecked() else '0'

        with open(self.windowsSettingsFile, 'w') as f:

            # Save current rules tab, current source tab, last sentence # selected and the last source text
            f.write(f'{str(rulesTab)}|{str(sourceTab)}|{str(self.lastSentNum)}|{self.__sourceText}\n')
            f.write(f'{checkedStateStr}\n')
            f.write(f'{checkedWordsState}\n')
            f.write(f'{sourceFontSizeStr}|{targetFontSizeStr}\n')
            f.write(f'{checkboxStr1}{checkboxStr2}\n')
            # f.write(f'{checkboxStr3}\n')

        if self.HCdllObj:

            # Return back to the directory we were in orginally before doing the dll operations
            os.chdir(os.path.dirname(FTPaths.CONFIG_PATH))

    def removeSampleLogicRule(self, rulesElement):

        for rule in rulesElement:

            if re.search(SAMPLE_LOGIC, rule.attrib['comment']):

                rulesElement.remove(rule)
                break

    def loadTransferRules(self):

        # Escape some characters and write as NFD unicode.
        if RunApertium.stripRulesFile(self.__report, self.testerFolder, self.__transfer_rules_file, RULE_FILE1) == True:
            return True
        
        test_tree = ET.parse(self.__transfer_rules_file)
        test_rt = test_tree.getroot()
        self.__transferRulesElement = test_rt.find('section-rules')

        if self.__transferRulesElement is not None:

            # Remove the Sample logic rule if present
            self.removeSampleLogicRule(self.__transferRulesElement)

            self.__transferRuleFileXMLtree = test_tree
            self.__transferModel = QStandardItemModel ()
            self.displayRules(self.__transferRulesElement, self.__transferModel)

            # Initialize the model for the rule list control
            self.ui.listTransferRules.setModel(self.__transferModel)

        else:
            QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Invalid Rules File'), \
            _translate('LiveRuleTesterTool', 'The transfer file has no transfer element or no section-rules element'))
            return False

        # Check if the interchunk file exists. If it does, we assume we have advanced transfer going on
        interchunk_rules_file = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TRANSFER_RULES_FILE2, self.__report, giveError=False)

        if interchunk_rules_file and os.path.isfile(interchunk_rules_file):

            # Escape some characters and write as NFD unicode.
            if RunApertium.stripRulesFile(self.__report, self.testerFolder, interchunk_rules_file, RULE_FILE2) == True:
                return True

            interchunk_tree = ET.parse(interchunk_rules_file)
            interchunk_rt = interchunk_tree.getroot()
            self.__interchunkRulesElement = interchunk_rt.find('section-rules')

            if self.__interchunkRulesElement is not None:
                self.__interChunkRuleFileXMLtree = interchunk_tree
                self.__interChunkModel = QStandardItemModel()
                self.displayRules(self.__interchunkRulesElement, self.__interChunkModel)
                # Initialize the model for the rule list control
                self.ui.listInterChunkRules.setModel(self.__interChunkModel)
            else:
                QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Invalid Interchunk Rules File'), \
                _translate('LiveRuleTesterTool', 'The interchunk transfer file has no transfer element or no section-rules element'))
                return False

            postchunk_rules_file = ReadConfig.getConfigVal(self.__configMap, ReadConfig.TRANSFER_RULES_FILE3, self.__report, giveError=False)

            # Check if the file exists. If it does, we assume we have advanced transfer going on
            if postchunk_rules_file and os.path.isfile(postchunk_rules_file):

                # Escape some characters and write as NFD unicode.
                if RunApertium.stripRulesFile(self.__report, self.testerFolder, postchunk_rules_file, RULE_FILE3) == True:
                    return True

                postchunk_tree = ET.parse(postchunk_rules_file)
                postchunk_rt = postchunk_tree.getroot()
                self.__postchunkRulesElement = postchunk_rt.find('section-rules')

                if self.__postchunkRulesElement is not None:
                    self.__postChunkRuleFileXMLtree = postchunk_tree
                    self.__postChunkModel = QStandardItemModel()
                    self.displayRules(self.__postchunkRulesElement, self.__postChunkModel)
                    # Initialize the model for the rule list control
                    self.ui.listPostChunkRules.setModel(self.__postChunkModel)
                else:
                    QMessageBox.warning(self, _translate('LiveRuleTesterTool', 'Invalid postchunk Rules File'), \
                    _translate('LiveRuleTesterTool', 'The postchunk transfer file has no transfer element or no section-rules element'))
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

        self.rulesChanged = True

        for i, el in enumerate(self.__rulesElement):
            ruleText = el.get('comment')

            if ruleText == None:
                ruleText = _translate('LiveRuleTesterTool', 'missing comment')

            # If active add text with the active rule #
            if self.__ruleModel.item(i).checkState():
                self.__ruleModel.item(i).setText(ruleText + _translate('LiveRuleTesterTool', ' - Active Rule ') + str(active_rules))
                active_rules += 1
            else:
                self.__ruleModel.item(i).setText(ruleText)

    def displayRules(self, rules_element, ruleModel):

        # Loop through each rule
        for rule_el in rules_element:

            # Get the comment for the rule
            comment = rule_el.get('comment')

            if comment == None:
                comment = _translate('LiveRuleTesterTool', 'missing comment')

            # Create an item object
            item = QStandardItem(comment)
            item.setCheckable(True)
            item.setCheckState(False)
            ruleModel.appendRow(item)

    def escapeDataStreamsLemmas(self, inputString):

        # Define the substitution function
        def escapeMatch(match):

            initialCaret = match.group(1)
            toEscape = match.group(2)
            escaped = Utils.escapeReservedApertChars(toEscape)
            return initialCaret + escaped + match.group(3)

        # Perform the substitution using the compiled pattern. The pattern looks like this: r'(\^)(.*?)(?<!\\)(<)'
        escapedString = Utils.reBetweenCaretAndFirstAngleBracket.sub(escapeMatch, inputString)

        return escapedString

    def TransferClicked(self):

        self.setCursor(QtCore.Qt.WaitCursor)

        if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules'
            self.__interchunkHtmlResult = ''
            self.__interchunkLexicalUnitsResult = ''

        self.__convertIt = True

        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                source_file = os.path.join(self.testerFolder, SOURCE_APERT)
                tr_file = os.path.join(self.testerFolder, RULE_FILE1)
                tgt_file = os.path.join(self.testerFolder, TARGET_FILE1)
                log_file = os.path.join(self.testerFolder, LOG_FILE)

                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
                ruleFileRoot = self.__transferRuleFileXMLtree.getroot()

            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                source_file = os.path.join(self.testerFolder, TARGET_FILE1)
                tr_file = os.path.join(self.testerFolder, RULE_FILE2)
                tgt_file = os.path.join(self.testerFolder, TARGET_FILE2)
                log_file = os.path.join(self.testerFolder, LOG_FILE2)

                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__interChunkRuleFileXMLtree)
                ruleFileRoot = self.__interChunkRuleFileXMLtree.getroot()

            else: # postchunk
                source_file = os.path.join(self.testerFolder, TARGET_FILE2)
                tr_file = os.path.join(self.testerFolder, RULE_FILE3)
                tgt_file = os.path.join(self.testerFolder, TARGET_FILE)
                log_file = os.path.join(self.testerFolder, LOG_FILE3)

                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__postChunkRuleFileXMLtree)
                ruleFileRoot = self.__postChunkRuleFileXMLtree.getroot()

        else:
            source_file = os.path.join(self.testerFolder, SOURCE_APERT)
            tr_file = os.path.join(self.testerFolder, RULE_FILE1)
            tgt_file = os.path.join(self.testerFolder, TARGET_FILE)
            log_file = os.path.join(self.testerFolder, LOG_FILE)

            # Copy the xml structure to a new object
            myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
            ruleFileRoot = self.__transferRuleFileXMLtree.getroot()

        # Save the source text to the tester folder
        sf = open(source_file, 'w', encoding='utf-8')
        myStr = self.getActiveLexicalUnits()

        if len(myStr) < 1:

            self.ui.TargetTextEdit.setPlainText(self.nothingSelectedMsg)
            self.unsetCursor()
            return

        # Break into punctuation and LUs
        tokens = re.split(r'\^(.+?)\$', myStr)
        myStr = ""

        # Loop through just the lexical units. We will ignore writing punctuation (stuff between LUs). Sentence punctuation is still put out.
        for tok in tokens[1::2]:

            if re.search(SENT_TAG, tok):

                myStr += f'^{tok}$'
            else:
                myStr += f' ^{tok}$'

        # When writing to the source text file, insert slashes before reserved Apertium characters
        sf.write(self.escapeDataStreamsLemmas(myStr.strip()))
        sf.close()

        # Only rewrite the transfer rules file if there was a change
        if self.rulesChanged or self.fixBilingLex:

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

            # If no rules were selected, create a dummy rule
            if len(list(new_sr_element)) < 1:

                # Create a dummy rule that does nothing
                ruleElement = ET.SubElement(new_sr_element, 'rule')
                patternElement = ET.SubElement(ruleElement, 'pattern')
                patternItemElement = ET.SubElement(patternElement, 'pattern-item')
                patternItemElement.attrib['n'] = 'c_dummy'
                ET.SubElement(ruleElement, 'action')

                # Create a dummy category to go with the rule
                sectionDefCatsElement = myRoot.find('section-def-cats')
                defCatElement = ET.SubElement(sectionDefCatsElement, 'def-cat')
                defCatElement.attrib['n'] = 'c_dummy'
                catItemElement = ET.SubElement(defCatElement, 'cat-item')
                catItemElement.attrib['tags'] = 'dummy'

            # Write out the file
            myTree.write(tr_file, encoding='UTF-8', xml_declaration=True) #, pretty_print=True)

            # Convert the file to be decomposed unicode
            Utils.decompose(tr_file)

        if self.fixBilingLex:

            # Fix problem characters in symbols of the bilingual lexicon (making a backup copy of the original file)
            subPairs = RunApertium.fixProblemChars(os.path.join(self.testerFolder, BILING_FILE_IN_TESTER_FOLDER))

            # Substitute symbols with problem characters with fixed ones in the transfer file
            RunApertium.subProbSymbols('.', tr_file, subPairs)

            self.fixBilingLex = False

        ## Display the results

        # Clear the results box
        self.ui.TargetTextEdit.setText('')

        # Check if attributes are well-formed. Warnings will be reported in the function
        if not self.advancedTransfer:

            errorList = RunApertium.checkRuleAttributesXML(ruleFileRoot)

            for i, triplet in enumerate(errorList):
                if i == 0:
                    self.ui.warningLabel.setText(triplet[0])
                else:
                    self.ui.warningLabel.setText(self.ui.warningLabel.text()+'\n'+triplet[0])

        # Run the makefile to run Apertium tools to do the transfer
        # component of FLExTrans. Pass in the folder of the bash
        # file to run. The current directory is FlexTools
        ret = RunApertium.run_makefile(self.buildFolder+'\\LiveRuleTester', self.__report)

        if ret:
            self.ui.TargetTextEdit.setPlainText(_translate('LiveRuleTesterTool', 'An error happened when running the Apertium tools.'))
            self.unsetCursor()
            return

        # Only rewrite the transfer rules file if there was a change
        if self.rulesChanged:

            # Convert back the problem characters in the transfer results file back to what they were. Restore the backup biling. file
            RunApertium.unfixProblemCharsRuleFile(os.path.join(tr_file))

        # Load the target text contents into the results edit box
        try:
            tgtf = open(tgt_file, encoding='utf-8')

        except FileNotFoundError: # if file doesn't exist try .aper (old name) insted of .txt

            tgt_file = re.sub('\.txt', '.aper', tgt_file)
            err_msg = _translate('LiveRuleTesterTool', 'Cannot find file: {tgt_file}.').format(tgt_file=tgt_file)

            try:
                tgtf = open(tgt_file, encoding='utf-8')

                # Set this for use in Convert2Stamp
                self.transferResultsPath = self.testerFolder + '\\' + os.path.basename(tgt_file)

            except FileNotFoundError:
                self.ui.TargetTextEdit.setPlainText(err_msg)
                self.unsetCursor()
                return
        except:
            self.ui.TargetTextEdit.setPlainText(err_msg)
            self.unsetCursor()
            return

        targetOutput = tgtf.read()

        # Create a <p> html element
        pElem = ET.Element('p')

        RTLflag = self.hasRTLdata(targetOutput[:len(targetOutput)//2])

        # Process advanced results differently (which doesn't apply to post chunk, because we get normal data stream in that case)
        if self.advancedTransfer and self.ui.tabRules.currentIndex() != 2: # 'tab_postchunk_rules'

            # Testbed.py function
            processAdvancedResults(targetOutput, pElem, RTLflag, dummy=True, punctuationPresent=True)

        else:
            # parse the lexical units. This will give us tokens before, between
            # and after each lu. E.g. ^hi1.1<n>$ ^there2.3<dem><pl>$ gives
            #                         ['', 'hi1.1<n>', ' ', 'there2.3<dem><pl>', '']
            tokens = re.split('\^|\$', targetOutput)

            # process pairs of tokens (punctuation and lexical unit)
            # ignore the punctuation (spaces)
            for i in range(0, len(tokens)-1, 2):

                # Turn the lexical units into color-coded html.
                processLexicalUnit(tokens[i+1]+' ', pElem, self.hasRTLdata(targetOutput[:len(targetOutput)//2]), True) # last parameter: show UNK categories

        # The p element now has one or more <span> children, turn them into an html string
        htmlVal = ET.tostring(pElem, encoding='unicode')

        # If we only have a paragraph element, we got no output.
        if htmlVal == '<p />':

            htmlVal = _translate('LiveRuleTesterTool', 'The rules produced no output.')

        self.ui.TargetTextEdit.setText(htmlVal)

        tgtf.close()

        # Store the actual data stream in __lexicalUnits for use elsewhere when in advanced mode
        # Store the html in another member
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                self.__transferHtmlResult = htmlVal
                self.__transferLexicalUnitsResult = targetOutput
                self.__tranferPrevSourceHtml = self.getActiveSrcTextEditVal()
                self.__tranferPrevSourceLUs = self.getActiveLexicalUnits()
            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                self.__interchunkHtmlResult = htmlVal
                self.__interchunkLexicalUnitsResult = targetOutput
                self.__interchunkPrevSource = self.getActiveSrcTextEditVal()
                self.__interchunkPrevSourceLUs = self.getActiveLexicalUnits()
            else: # 'tab_postchunk_rules':
                self.__postchunkPrevSource = self.getActiveSrcTextEditVal()
                self.__postchunkPrevSourceLUs = self.getActiveLexicalUnits()

        # Load the log file
        lf = open(log_file, encoding='utf-8')

        # fix up the output of the log file to colorize it and remove unneeded stuff
        myLines = lf.readlines()
        newText = self.processLogLines(myLines)
        self.ui.LogEdit.setText(newText)

        lf.close()
        self.rulesChanged = False
        self.unsetCursor()

    def processLogLines(self, inputLines):

        retStr = ''

        # Process advanced (chunk) data differently. Interchunk and Postchunk phases have the chunk format
        if self.advancedTransfer and self.ui.tabRules.currentIndex() != 0: # transfer tab

            delimeter = '} '
            processFunc = processAdvancedResults
        else:
            delimeter = '> '
            processFunc = processLexicalUnit

        for line in inputLines:

            # A typical line may look like this:
            # apertium-transfer: Rule 19 line 2 cat1.1<n><m><ez_pl> my1.1<nprop><m>

            # If we have Rule N, process it
            if re.search(r'Rule \d+', line):

                # Extract the rule # and the lexical units
                matchObj = re.search(r'(.+)(Rule )(\d+)( line \d+ )(.+)', line)
                ruleStr = matchObj.group(2) + matchObj.group(3).zfill(2)
                lexUnitsStr = matchObj.group(5).strip()

                # Translate the word 'Rule' to the localized version
                ruleStr = re.sub('Rule ', _translate('LiveRuleTesterTool', 'Rule '), ruleStr)

                # Put a delimeter between multiple lexical units
                lexUnitsStr = re.sub(delimeter, f'{delimeter}\t ', lexUnitsStr)

                # Split into lexical units
                lexUnitList = lexUnitsStr.split('\t')

                # Each lexical unit also has / plus the target lexical unit. Remove these.
                lexUnitList = [myLU.split('/')[0] for myLU in lexUnitList]

                # Create a <p> html element
                paragraphEl = ET.Element('p')

                # Start the span with 'Rule' + #
                outputLUSpan(paragraphEl, CHUNK_GRAM_CAT_COLOR, f'{ruleStr}: ', self.__sent_model.getRTL())

                # process all the lexical units
                for lexUnit in lexUnitList:

                    # Mark up the lexical unit with color, etc.
                    processFunc(lexUnit, paragraphEl, self.__sent_model.getRTL(), True)

                # Convert the ET element to an html string
                coloredLUStr = ET.tostring(paragraphEl, encoding='unicode')

                # add the html for this line to the reest
                retStr += coloredLUStr

        return retStr

    def ZoomIncreaseTargetClicked(self):
        myFont = self.ui.SynthTextEdit.font()
        self.setTargetWidgetsFont(myFont.pointSizeF() * ZOOM_INCREASE_FACTOR)

    def ZoomDecreaseTargetClicked(self):
        myFont = self.ui.SynthTextEdit.font()
        self.setTargetWidgetsFont(myFont.pointSizeF() * 1/ZOOM_INCREASE_FACTOR)

    def ZoomIncreaseSourceClicked(self):
        myFont = self.ui.SelectedSentencesEdit.font()
        self.setSourceWidgetsFont(myFont.pointSizeF() * ZOOM_INCREASE_FACTOR)

    def ZoomDecreaseSourceClicked(self):
        myFont = self.ui.SelectedSentencesEdit.font()
        self.setSourceWidgetsFont(myFont.pointSizeF() * 1/ZOOM_INCREASE_FACTOR)

    def setTargetWidgetsFont(self, fontSize):
        myFont = self.ui.SynthTextEdit.font()
        myFont.setPointSizeF(fontSize)

        self.ui.SynthTextEdit.setFont(myFont)
        self.ui.TargetTextEdit.setFont(myFont)

    def setSourceWidgetsFont(self, fontSize):
        myFont = self.ui.SelectedSentencesEdit.font()
        myFont.setPointSizeF(fontSize)

        self.ui.SelectedSentencesEdit.setFont(myFont)
        self.ui.SelectedWordsEdit.setFont(myFont)
        self.ui.listSentences.setFont(myFont)
        self.ui.SentCombo.setFont(myFont)
        self.ui.LogEdit.setFont(myFont)

        # Set the font size of all the check boxes.
        # This may cause a label to not fit, but on reload or click on another sentence, the check box label gets resized.
        for check in self.__checkBoxList:

            check.setFont(myFont)

        # Set the tooltip size globally
        QToolTip.setFont(myFont)

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

RESTART_MODULE = 0
ERROR_HAPPENED = 1
NO_ERRORS = 2
START_LOG_VIEWER = 3
START_RULE_ASSISTANT = 4
START_REPLACEMENT_EDITOR = 5

def RunModule(DB, report, configMap, ruleCount=None, app=None):

    # Get needed configuration file properties
    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    sentPunc = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)

    # check for errors
    if not (sourceText and bilingFile and sentPunc):
        return ERROR_HAPPENED

    matchingContentsObjList = []

    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)

    if sourceText not in sourceTextList:

        report.Error(_translate('LiveRuleTesterTool', 'The text named: {name} not found.').format(name=sourceText))
        return ERROR_HAPPENED
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceText)]

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

        insertWordsList = InterlinData.getInsertedWordsList(treeTranInsertWordsFile, report, DB)

        if insertWordsList == None:
            return ERROR_HAPPENED # error already reported

    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile, encoding='utf-8')
            f_treeTranResultFile.close()
        except:
            report.Error(_translate('LiveRuleTesterTool', 'There is a problem with the Tree Tran Result File path: {file}. Please check the configuration file setting.').format(file=treeTranResultFile))
            return ERROR_HAPPENED

        # get the list of guids from the TreeTran results file
        treeSentList = InterlinData.getTreeSents(treeTranResultFile, report)

        if treeSentList == None:
            return ERROR_HAPPENED # error already reported

        # get log info. that tells us which sentences have a syntax parse and # words per sent
        logInfo = Utils.importGoodParsesLog()

    # Get various bits of data for the get interlinear function
    interlinParams = InterlinData.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return

    # Get interlinear data. A complex text object is returned.
    myText = InterlinData.getInterlinData(DB, report, interlinParams)

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
                    report.Error(_translate('LiveRuleTesterTool', 'Sentence {sentNum} from TreeTran not found').format(sentNum=sentNum))
                    return ERROR_HAPPENED

                # Output any punctuation preceding the sentence.
                prePuncTupList = myFLExSent.getSurfaceAndDataPrecedingSentPunc()
                tupList.extend(prePuncTupList)

                # Loop through each word in the sentence and get the Guids
                for wrdNum in range(0, myTreeSent.getLength()):
                    myGuid = myTreeSent.getNextGuidAndIncrement()

                    if not myGuid:
                        report.Error(_translate('LiveRuleTesterTool', 'Null Guid in sentence ') + str(sentNum+1) + ', word ' + str(wrdNum+1))
                        break

                    # If we couldn't find the guid, see if there's a reason
                    if myFLExSent.haveGuid(myGuid) == False:
                        # Check if the reason we didn't have a guid found is that it got replaced as part of a complex form replacement
                        nextGuid = myTreeSent.getNextGuid()
                        if nextGuid is None or myFLExSent.notPartOfAdjacentComplexForm(myGuid, nextGuid) == True:
                            report.Warning(_translate('LiveRuleTesterTool', 'Could not find the desired Guid in sentence ') + str(sentNum+1) + ', word ' + str(wrdNum+1))
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

                    report.Error(_translate('LiveRuleTesterTool', 'Sentence: {sentNum} not found. Check that the right parses are present.').format(sentNum=sentNum))
                    continue

                myFLExSent.getSurfaceAndDataTupleList(tupList)

            segment_list.append(tupList)

        report.Info(_translate('LiveRuleTesterTool', "Exported: {num} sentence(s) using TreeTran results.").format(num=str(len(logInfo))))

        if noParseSentCount > 0:
            report.Warning(_translate('LiveRuleTesterTool', 'No parses found for {num} sentence(s).')).format(num=str(noParseSentCount))

    else:
        # Normal, non-TreeTran processing
        if myText.haveData() == True:
            segment_list = myText.getSurfaceAndDataTupleListBySent()

    if len(segment_list) > 0:

        # if the bilingual file path is relative, add on the current directory
        if re.search(':', bilingFile):
            pass
        else:
            pwd = os.getcwd()
            bilingFile = os.path.join(pwd, bilingFile)

        # Supply the segment list to the main windowed program
        window = Main(segment_list, bilingFile, sourceText, DB, configMap, report, sourceTextList, ruleCount=ruleCount, sentPunc=sentPunc)

        if window.retVal == False:
            report.Error(_translate('LiveRuleTesterTool', 'An error occurred getting things initialized.'))
            return ERROR_HAPPENED

        window.show()
        app.exec_()

        # If the user changed the source text combo, the restart member is set to True
        if window.restartTester:

            return RESTART_MODULE

        elif window.startTestbedLogViewer:

            return START_LOG_VIEWER

        elif window.startRuleAssistant:

            return START_RULE_ASSISTANT
        
        elif window.startReplacementEditor:

            return START_REPLACEMENT_EDITOR
    else:
        report.Error(_translate('LiveRuleTesterTool', 'This text has no data.'))
        return ERROR_HAPPENED

    return NO_ERRORS

def MainFunction(DB, report, modify=False, ruleCount=None):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    retVal = RESTART_MODULE
    loggedStart = False

    # Have a loop of re-running this module so that when the user changes to a different text, the window restarts with the new info. loaded
    while retVal == RESTART_MODULE:

        configMap = ReadConfig.readConfig(report)
        if not configMap:
            retVal = ERROR_HAPPENED
            break

        if not loggedStart:

            # Log the start of this module on the analytics server if the user allows logging.
            Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])
            loggedStart = True

        retVal = RunModule(DB, report, configMap, ruleCount, app)

        if retVal == START_RULE_ASSISTANT:

            from RuleAssistant import MainFunction as RA
            from RuleAssistant import docs as RA_docs
            report.Info(_translate('LiveRuleTesterTool', 'Running {name} (version {version})...').format(name=RA_docs[FTM_Name], version=RA_docs[FTM_Version]))
            ruleCount = RA(DB, report, modify, fromLRT=True)

            # Show we are re-running the LRT
            report.Info(_translate('LiveRuleTesterTool', 'Running {name} (version {version})...').format(name=docs[FTM_Name], version=docs[FTM_Version]))
            retVal = RESTART_MODULE
        else:
            ruleCount = None

    # Start the log viewer
    if retVal == START_LOG_VIEWER:

        TestbedLogViewer.RunTestbedLogViewer(report)

    # Start the replacement dictionary editor
    elif retVal == START_REPLACEMENT_EDITOR:

        from ReplacementEditor import MainFunction as RE
        RE(DB, report, modify)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
