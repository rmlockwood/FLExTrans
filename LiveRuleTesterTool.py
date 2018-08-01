#
#   LiveRuleTesterTool
#
#   Ron Lockwood
#   SIL International
#   7/2/16
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
import Utils

#----------------------------------------------------------------
# Configurables:
TESTER_FOLDER = Utils.OUTPUT_FOLDER+'\\LiveRuleTester'
AFFIX_GLOSS_PATH = TESTER_FOLDER + '\\target_pfx_glosses.txt'
TRANFER_RESULTS_PATH = TESTER_FOLDER + '\\target_text.aper'
TARGET_ANA_PATH = TESTER_FOLDER + '\\myText.ana'
SYNTHESIS_FILE_PATH = TESTER_FOLDER + '\\myText.syn'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Live Rule Tester Tool",
        'moduleVersion'    : "3.1",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Test transfer rules and synthesis live against specific words.",
        'moduleDescription'   :
u"""
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
                 
#----------------------------------------------------------------
# The main processing function

from FTModuleClass import FlexToolsModuleClass
from SIL.FieldWorks.FDO import ILexPronunciation
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import IScrSectionRepository
from SIL.FieldWorks.FDO import ITextFactory, IStTextFactory, IStTxtParaFactory
from SIL.FieldWorks.FDO import ILexEntryRepository
from SIL.FieldWorks.FDO import ILexEntry, ILexSense
from SIL.FieldWorks.FDO import SpecialWritingSystemCodes
from SIL.FieldWorks.FDO.DomainServices import SegmentServices
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import IUndoStackManager
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
from System import Guid
from System import String
 
import ReadConfig
import CatalogTargetPrefixes
import ConvertTextToSTAMPformat
import ExtractTargetLexicon
#import TestbedLogViewer 
import os
import re
import sys
import unicodedata
import copy
import time
import platform
import subprocess
import xml.etree.ElementTree as ET
import shutil
import uuid

from PyQt4.QtGui import QFileDialog, QMessageBox
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QCursor
from LiveRuleTester import Ui_MainWindow
from OverWriteTestDlg import Ui_OverWriteTest
    
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
                #value = myHPG.getHeadword() + u' \u200F(' + myHPG.getPOS() + u')\u200F ' + myHPG.getGloss()
            #else:
            value = self.joinTupParts(mySent, 0)
            self.__currentSent = mySent    
            return QtCore.QString(value)
            
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
    
class OverWriteDlg(QtGui.QDialog):
    def __init__(self, luStr):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_OverWriteTest()
        self.ui.setupUi(self)
        
        # Default to NoToAll. 
        self.retValue = QtGui.QDialogButtonBox.NoToAll
        
        # Add the lexical unit to the label
        labelStr = str(self.ui.label.text())
        labelStr = re.sub('XX', '"' + luStr + '"', labelStr)
        self.ui.label.setText(labelStr)
        
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.YesToAll).clicked.connect(self.yesToAllClicked)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.NoToAll).clicked.connect(self.noToAllClicked)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).clicked.connect(self.yesClicked)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.No).clicked.connect(self.noClicked)
    def yesToAllClicked(self):
        self.retValue = QtGui.QDialogButtonBox.YesToAll
    def noToAllClicked(self):
        self.retValue = QtGui.QDialogButtonBox.NoToAll
    def yesClicked(self):
        self.retValue = QtGui.QDialogButtonBox.Yes
    def noClicked(self):
        self.retValue = QtGui.QDialogButtonBox.No
    def getRetValue(self):
        return self.retValue
        
class Main(QtGui.QMainWindow):

    def __init__(self, sentence_list, biling_file, source_text, DB, configMap, report):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__biling_file = biling_file
        self.ui.BilingFileEdit.setText(biling_file)
        self.__source_text = source_text
        self.ui.SourceFileEdit.setText(source_text)
        self.__DB = DB
        self.__configMap = configMap
        self.__report = report
        self.__transfer_rules_file = None
        self.advancedTransfer = False
        self.__convertIt = True
        self.__extractIt = True
        self.__doCatalog = True
        
        self.__ruleModel = self.__transferModel = None
        self.__interChunkModel = None
        self.__postChunkModel = None
        self.__transferRulesElement = None
        self.__interchunkRulesElement = None
        self.__postchunkRulesElement = None
        self.TRIndex = None
        self.setStatusBar(None)
        self.__lexicalUnits = ''
        
        # Make sure we are on the 1st tabs
        self.ui.tabRules.setCurrentIndex(0)
        self.ui.tabSource.setCurrentIndex(0)
        
        # Tie controls to functions
        self.ui.TestButton.clicked.connect(self.TestClicked)
        #self.ui.CloseButton.clicked.connect(self.CloseClicked)
        self.ui.listSentences.clicked.connect(self.listSentClicked)
        self.ui.listTransferRules.clicked.connect(self.rulesListClicked)
        self.ui.listInterChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.listPostChunkRules.clicked.connect(self.rulesListClicked)
        self.ui.SentCombo.currentIndexChanged.connect(self.listSentComboClicked)
        self.ui.TransferFileBrowseButton.clicked.connect(self.TransferBrowseClicked)
        self.ui.BilingFileBrowseButton.clicked.connect(self.BilingBrowseClicked)
        self.ui.tabRules.currentChanged.connect(self.TabClicked)
        self.ui.refreshButton.clicked.connect(self.RefreshClicked)
        self.ui.selectAllButton.clicked.connect(self.SelectAllClicked)
        self.ui.unselectAllButton.clicked.connect(self.UnselectAllClicked)
        self.ui.upButton.clicked.connect(self.UpButtonClicked)
        self.ui.downButton.clicked.connect(self.DownButtonClicked)
        self.ui.synthesizeButton.clicked.connect(self.SynthesizeButtonClicked)
        self.ui.refreshLexButton.clicked.connect(self.RefreshLexButtonClicked)
        self.ui.addToTestbedButton.clicked.connect(self.AddTestbedButtonClicked)
        self.ui.viewTestbedLogButton.clicked.connect(self.ViewTestbedLogButtonClicked)
        
        # Blank out the tests added feedback label
        self.ui.TestsAddedLabel.setText('')
        
        # Right align some text boxes
        self.ui.SourceFileEdit.home(False)
        
        # Create a bunch of check boxes to be arranged later
        self.__checkBoxList = []
        for i in range(0,50):
            myCheck = QtGui.QCheckBox(self.ui.scrollArea)
            myCheck.setVisible(False)
            myCheck.setProperty("myIndex", i)
            myCheck.setGeometry(QtCore.QRect(0,0, 35, 35)) # default position
            
            # connect to a function
            myCheck.clicked.connect(self.SourceCheckBoxClicked)
            
            # add it to the list
            self.__checkBoxList.append(myCheck)

        # Load the transfer rules
        pwd = os.getcwd()
        self.__transfer_rules_file= os.path.join(pwd, Utils.OUTPUT_FOLDER, 'transfer_rules.t1x')
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
            self.ui.SynthTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.ui.TargetTextEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
            
        self.ui.listSentences.setModel(self.__sent_model)
        self.ui.SentCombo.setModel(self.__sent_model)
        
        # Simulate a click on the sentence list box
        self.listSentComboClicked()
        
        # Copy bilingual file to the tester folder
        try:
            shutil.copy(self.__biling_file, os.path.join(TESTER_FOLDER, os.path.basename(self.__biling_file)))
        except:
            QMessageBox.warning(self, 'Copy Error', 'Could not copy the bilingual file to the folder: '+TESTER_FOLDER+'. Please check that it exists.')
            self.ret_val = False
            return 

        # Copy makefile file to the tester folder. We do this because it could be an advanced transfer makefile
        try:
            shutil.copy(os.path.join(Utils.OUTPUT_FOLDER, 'Makefile'), TESTER_FOLDER)
            m_path = os.path.join(Utils.OUTPUT_FOLDER, 'Makefile')
        except:
            QMessageBox.warning(self, 'Copy Error', 'Could not copy '+m_path+' to the folder: '+TESTER_FOLDER+'. Please check that it exists.')
            self.ret_val = False
            return 
        
        ## Testbed preparation
        # Disable buttons as needed.
        self.ui.addToTestbedButton.setEnabled(False)
        self.ui.addMultipleCheckBox.setEnabled(False)
        
        if os.path.exists(Utils.TESTBED_FILE_PATH) == False:
            self.ui.viewTestbedLogButton.setEnabled(False)

        self.ret_val = True

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
        origin = unicode(self.ui.SourceFileEdit.text())
        
        # Initialize a Test XML object and fill out its data given a list of
        # lexical units and a result from the synthesis step
        myObj = Utils.TestbedTestXMLObject(lexUnitList, origin, synthesisResult)
        
        return myObj
    
    def ViewTestbedLogButtonClicked(self):
        pass
        
    def AddTestbedButtonClicked(self):
        self.ui.TestsAddedLabel.setText('')
        
        # Set the direction attribute
        if self.__sent_model.getRTL():
            direction = Utils.RTL
        else:
            direction = Utils.LTR

        fileObj = Utils.FlexTransTestbedFile(direction)
        testbedObj = fileObj.getFLExTransTestbedXMLObject()
        
        if fileObj.isNew():
            self.ui.editTestbedButton.setEnabled(True)
         
        # Get the current list of tests in the XML testbed    
        testXMLObjList = testbedObj.getTestXMLObjectList()
        
        # Get the synthesis result text
        synResult = unicode(self.ui.SynthTextEdit.toPlainText()).strip()
        
        # Remove the RTL marker
        synResult = re.sub(ur'\u200F','', synResult)
        
        cnt = 0
        
        # Check if add-multiple was selected
        if self.ui.addMultipleCheckBox.isChecked():
            
            luObjList = self.getLexUnitObjsFromString(self.getActiveTextEditVal())
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
                        if ret_val != QtGui.QDialogButtonBox.YesToAll:
                            dlg = OverWriteDlg(myTestXMLObj.getLUString())
                            dlg.exec_()
                            ret_val = dlg.getRetValue()
                        
                        # See if we should overwrite    
                        if ret_val == QtGui.QDialogButtonBox.Yes or ret_val == QtGui.QDialogButtonBox.YesToAll:
                            testbedObj.overwriteInTestbed(existingTestXMLObj, myTestXMLObj)
                            cnt += 1
                        
                        # Break out of the loop if the user said no to all    
                        elif ret_val == QtGui.QDialogButtonBox.NoToAll:
                            break
                    else:
                        testbedObj.addToTestbed(myTestXMLObj)
                        cnt += 1
                    
        else:
            luObjList = self.getLexUnitObjsFromString(self.getActiveTextEditVal())
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
                    dlg.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.No|QtGui.QDialogButtonBox.Yes)

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
            if unicodedata.bidirectional(word1[i]) in (u'R', u'AL'):
                return True
        return False

    def RefreshLexButtonClicked(self):
        self.ui.SynthTextEdit.setPlainText('')
        self.__extractIt = True
        self.__doCatalog = True
        
    def SynthesizeButtonClicked(self):
        self.ui.TestsAddedLabel.setText('')
        error_list = []
        
        # Make the text box blank to start out.
        self.ui.SynthTextEdit.setPlainText('')
        
        ## CATALOG
        # Catalog all the target affixes
        # We only need to do this once, until the user requests to refresh the lexicon
        if self.__doCatalog:
            
            error_list = CatalogTargetPrefixes.catalog_affixes(self.__DB, self.__configMap, AFFIX_GLOSS_PATH)
            for msg, code in error_list:
                if code == 2:
                    QMessageBox.warning(self, 'Catalog Prefix Error', msg + '\nRun the Catalog Target Prefixes module separately for more details.')
                    return
                
            self.__doCatalog = False
                    
        ## CONVERT
        # if the target text has changed, we need to do the affixes and convert the target text to STAMP format
        if self.__convertIt == True:
            
            # Convert the target text to .ana format (for STAMP)
            error_list = ConvertTextToSTAMPformat.convert_to_STAMP(self.__DB, self.__configMap, TARGET_ANA_PATH, AFFIX_GLOSS_PATH, TRANFER_RESULTS_PATH)
            for msg, code in error_list:
                if code == 2:
                    QMessageBox.warning(self, 'Convert to STAMP Error', msg + '\nRun the Convert to STAMP module separately for more details.')
                    return
            
            self.__convertIt = False
                    
        ## EXTRACT
        # if the refresh lexicon button was pressed or this is the first run, extract the target lexicon
        if self.__extractIt == True:
            
            # Redo the catalog of prefixes in case the user changed an affix
            error_list = CatalogTargetPrefixes.catalog_affixes(self.__DB, self.__configMap, AFFIX_GLOSS_PATH)
            for msg, code in error_list:
                if code == 2:
                    QMessageBox.warning(self, 'Catalog Prefix Error', msg + '\nRun the Catalog Target Prefixes module separately for more details.')
                    return
            
            # Extract the lexicon        
            error_list = ExtractTargetLexicon.extract_target_lex(self.__DB, self.__configMap)
            for msg, code in error_list:
                    if code == 2:
                        QMessageBox.warning(self, 'Extract Target Lexicon Error', msg + '\nRun the Extract Target Lexicon module separately for more details.')
                        return
        
        ## SYNTHESIZE
        error_list = ExtractTargetLexicon.synthesize(self.__configMap, TARGET_ANA_PATH, SYNTHESIS_FILE_PATH) 
        for msg, code in error_list:
            if code == 2:
                QMessageBox.warning(self, 'Extract Target Lexicon Error', msg + '\nRun the Extract Target Lexicon module separately for more details.')
                return
                    
        # Load the synthesized result into the text box
        lf = open(SYNTHESIS_FILE_PATH)
        synthText = unicode(lf.read(),'utf-8')
        
        # if RTL text, prepend the RTL mark
        if self.__sent_model.getRTL():
            synthText = ur'\u200F' + synthText
            
        self.ui.SynthTextEdit.setPlainText(synthText)
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
        
        return
                
    def UpButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() > 0:
            # pop current list item and insert it one above
            self.__rulesElement._children.insert(self.TRIndex.row()-1,\
                                                self.__rulesElement._children.pop(self.TRIndex.row()))
            
            # copy the selection
            cur_state = self.__ruleModel.item(self.TRIndex.row()).checkState()
            oth_state = self.__ruleModel.item(self.TRIndex.row()-1).checkState()
            self.__ruleModel.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__ruleModel.item(self.TRIndex.row()-1).setCheckState(cur_state)
            
            # redo the display
            self.rulesListClicked(self.TRIndex)
            
    def DownButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() < len(self.__rulesElement._children)-1:
            # pop current list item and insert it one above
            self.__rulesElement._children.insert(self.TRIndex.row()+1,\
                                                self.__rulesElement._children.pop(self.TRIndex.row()))
            
            # copy the selection
            cur_state = self.__ruleModel.item(self.TRIndex.row()).checkState()
            oth_state = self.__ruleModel.item(self.TRIndex.row()+1).checkState()
            self.__ruleModel.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__ruleModel.item(self.TRIndex.row()+1).setCheckState(cur_state)
            
            # redo the display
            self.rulesListClicked(self.TRIndex)
    
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
        self.loadTransferRules()
        self.ui.SynthTextEdit.setPlainText('')
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
        val = ET.tostring(paragraph_element)
        
        # The text box will turn the html into rich text    
        self.ui.SelectedWordsEdit.setText(val)    
                    
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
        val = ET.tostring(paragraph_element)
            
        # The text box will turn the html into rich text    
        self.ui.SelectedSentencesEdit.setText(val)
        
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
    def getActiveTextEditVal(self):
        if self.ui.tabSource.currentIndex() == 0:
            #ret = self.ui.SelectedWordsEdit.toPlainText()
            ret = self.__lexicalUnits
        elif self.ui.tabSource.currentIndex() == 1:
            #ret = self.ui.SelectedSentencesEdit.toPlainText()
            ret = self.__lexicalUnits
        else:
            ret = unicode(self.ui.ManualEdit.toPlainText())
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
        self.ui.SelectedWordsEdit.setPlainText(self.ui.TargetTextEdit.toPlainText())
        self.ui.SelectedSentencesEdit.setPlainText(self.ui.TargetTextEdit.toPlainText())
        self.ui.ManualEdit.setPlainText(self.ui.TargetTextEdit.toPlainText())
        self.__ClearStuff()
    def __ClearStuff(self):
        self.ui.TargetTextEdit.setPlainText('')
        self.ui.LogEdit.setPlainText('')
    def TabClicked(self):
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                self.__ruleModel = self.__transferModel
                self.__rulesElement = self.__transferRulesElement
                
                # unhide stuff
                self.__MakeVisible(True)
                
                # re-write the check boxes
                self.SourceCheckBoxClicked()
                
                # blank the other two source boxes
                self.ui.SelectedSentencesEdit.setPlainText('')
                self.ui.ManualEdit.setPlainText('')
    
                self.__ClearStuff()
                
            elif self.ui.tabRules.currentIndex() == 1: #'tab_interchunk_rules':
                self.__ruleModel = self.__interChunkModel
                self.__rulesElement = self.__interchunkRulesElement
                
                # hide stuff
                self.__MakeVisible(False)
                
                # copy stuff
                self.__CopyStuff()
                
            else: # postchunk
                self.__ruleModel = self.__postChunkModel
                self.__rulesElement = self.__postchunkRulesElement
    
                # hide stuff
                self.__MakeVisible(False)
    
                # copy stuff
                self.__CopyStuff()
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
        for i,wrdTup in enumerate(mySent):
            # Get the ith checkbox
            myCheck = self.__checkBoxList[i]
                        
            # Make it visible
            myCheck.setVisible(True)
            
            # set the text of the check box from the first tuple element
            # this will be the surface form
            myCheck.setText(wrdTup[0])
            
            # get the width of the box and text (maybe have to add icon size)
            width = myCheck.fontMetrics().boundingRect(wrdTup[0]).width() + 28 + 5 #\
                    #myCheck.getIconSize().width()
            
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
            
        # Make the rest of the unused check boxes invisible
        for j in range(i+1,len(self.__checkBoxList)):
            self.__checkBoxList[j].setVisible(False)
             
    def CloseClicked(self):
        self.ret_val = 0
        self.close()
    def BilingBrowseClicked(self):
        # Bring up file select dialog
        biling_file_tup = \
         QFileDialog.getOpenFileNameAndFilter(self, 'Choose Bilingual Dictionary File',\
            'Output', 'Dictionary Files (bilingual.dix)')
         
        self.__biling_file = biling_file_tup[0]
        self.ui.BilingFileEdit.setText(self.__biling_file)
        
        # Copy bilingual file to the tester folder
        shutil.copy(self.__biling_file, os.path.join(TESTER_FOLDER, os.path.basename(self.__biling_file)))
        
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
            self.__transferModel = QtGui.QStandardItemModel()
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
                self.__interChunkModel = QtGui.QStandardItemModel()
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
                    self.__postChunkModel = QtGui.QStandardItemModel()
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
                self.__ruleModel = self.__transferModel
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
            item = QtGui.QStandardItem(comment) 
            item.setCheckable(True)
            item.setCheckState(False)
            ruleModel.appendRow(item)
            
    def TestClicked(self):
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        
        self.__convertIt = True
        
        # TODO: allow editable rule file edit box?
        # Make sure we have a transfer file
        if self.ui.TransferFileEdit.text() == '':
            return
        
        # Create the tester folder if it doesn't exist
        #if not os.path.exists(TESTER_FOLDER):
        #    os.makedirs(TESTER_FOLDER)
            
        if self.advancedTransfer:
            if self.ui.tabRules.currentIndex() == 0: # 'tab_transfer_rules':
                source_file = os.path.join(TESTER_FOLDER, 'source_text.aper')
                tr_file = os.path.join(TESTER_FOLDER, 'transfer_rules.t1x')
                tgt_file = os.path.join(TESTER_FOLDER, 'target_text1.aper')
                log_file = os.path.join(TESTER_FOLDER, 'err_log')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
                rule_file = self.__transferRuleFileXMLtree.getroot()
                
            elif self.ui.tabRules.currentIndex() == 1: # 'tab_interchunk_rules':
                source_file = os.path.join(TESTER_FOLDER, 'target_text1.aper')
                tr_file = os.path.join(TESTER_FOLDER, 'transfer_rules.t2x')
                tgt_file = os.path.join(TESTER_FOLDER, 'target_text2.aper')
                log_file = os.path.join(TESTER_FOLDER, 'err_log2')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__interChunkRuleFileXMLtree)
                rule_file = self.__interChunkRuleFileXMLtree.getroot()

            else: # postchunk
                source_file = os.path.join(TESTER_FOLDER, 'target_text2.aper')
                tr_file = os.path.join(TESTER_FOLDER, 'transfer_rules.t3x')
                tgt_file = os.path.join(TESTER_FOLDER, 'target_text.aper')
                log_file = os.path.join(TESTER_FOLDER, 'err_log3')
                
                # Copy the xml structure to a new object
                myTree = copy.deepcopy(self.__postChunkRuleFileXMLtree)
                rule_file = self.__postChunkRuleFileXMLtree.getroot()

        else:
            source_file = os.path.join(TESTER_FOLDER, 'source_text.aper')
            tr_file = os.path.join(TESTER_FOLDER, 'transfer_rules.t1x')
            tgt_file = os.path.join(TESTER_FOLDER, 'target_text.aper')
            log_file = os.path.join(TESTER_FOLDER, 'err_log')
            
            # Copy the xml structure to a new object
            myTree = copy.deepcopy(self.__transferRuleFileXMLtree)
            rule_file = self.__transferRuleFileXMLtree.getroot()
            
        # Save the source text to the tester folder
        sf = open(source_file, 'w')
        myStr = unicode(self.getActiveTextEditVal())
        
        sf.write(myStr.encode('utf-8'))
        sf.close()
        
        # Save the transfer rules file with the selected rules present
        rf = open(tr_file, 'w')
        
        # Copy the xml structure to a new object
        myRoot = myTree.getroot()
        
        sr_element = myRoot.find('section-rules')
        
        # Remove the section-rules element
        myRoot.remove(sr_element)
        
        # Recreate the section-rules element
        new_sr_element = ET.SubElement(myRoot, 'section-rules')
        
        rules_element = rule_file.find('section-rules')

        # Put a space in the rules section so we get a closing element </section-rules>
        #makrules_element.text = ' '
        
        # Loop through all the selected rules
        for i, rule_el in enumerate(rules_element):
        
            # Add to the xml structure if it is a selected rule
            if self.__ruleModel.item(i).checkState():
                new_sr_element.append(rule_el) 
            
        # Write out the file
        myTree.write(rf, encoding='UTF-8', xml_declaration=True) #, pretty_print=True)
        rf.close()
        
        ## Display the results
        
        # Clear the results box
        self.ui.TargetTextEdit.setText('') 

        # Run the makefile to run Apertium tools to do the transfer
        # component of FLExTrans. Pass in the folder of the bash
        # file to run. The current directory is FlexTools
        ret = Utils.run_makefile('Output\\LiveRuleTester')
        
        if ret:
            self.ui.TargetTextEdit.setPlainText('An error happened when running the Apertium tools.')
            QApplication.restoreOverrideCursor()
            return
        
        # Load the target text contents into the results edit box
        tgtf = open(tgt_file)
        target_output = unicode(tgtf.read(),'utf-8')
        
        # Create a <p> html element
        p = ET.Element('p')

        # parse the lexical units. This will give us tokens before, between 
        # and after each lu. E.g. ^hi1.1<n>$ ^there2.3<dem><pl>$ gives
        #                         ['', 'hi1.1<n>', ' ', 'there2.3<dem><pl>', '']
        tokens = re.split('\^|\$', target_output)
        
        # process pairs of tokens (punctuation and lexical unit)
        # ignore the punctuation (spaces)
        for i in range(0,len(tokens)-1,2):
            # Turn the lexical units into color-coded html.            
            Utils.process_lexical_unit(tokens[i+1]+' ', p, self.has_RTL_data(target_output), True) # last parameter: show UNK categories
        
        # The p element now has one or more <span> children, turn them into an html string        
        val = ET.tostring(p)

        self.ui.TargetTextEdit.setText(val)
        
        tgtf.close()
        
        # Load the log file
        lf = open(log_file)
        self.ui.LogEdit.setPlainText(unicode(lf.read(),'utf-8'))
        lf.close()
        
        QApplication.restoreOverrideCursor()

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
    text_desired_eng = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    bilingFile = ReadConfig.getConfigVal(configMap, 'BilingualDictOutputFile', report)

    # check for errors
    if not (text_desired_eng and bilingFile):
        return
    
    # Get punctuation string
    sent_punct = unicode(ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report), "utf-8")
    
    if not sent_punct:
        return
    
    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
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

    getSurfaceForm = True
    segment_list = Utils.get_interlin_data(DB, report, sent_punct, contents, typesList, getSurfaceForm)
    
    # See if we have any data to show
    if len(segment_list) > 0:
                
        # Create the qt app
        app = QtGui.QApplication(sys.argv)
        
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
        
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
