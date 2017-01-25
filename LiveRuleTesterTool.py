#
#   LiveRuleTesterTool.py
#
#   Ron Lockwood
#   SIL International
#   7/2/16
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

from FTModuleClass import FlexToolsModuleClass
import ReadConfig
import Utils
import os
import re
import sys
import unicodedata
import copy
import time
from PyQt4.QtGui import QFileDialog, QMessageBox

#----------------------------------------------------------------
# Configurables:
TESTER_FOLDER = 'Output\\LiveRuleTester'
OUTPUT_FOLDER = 'Output'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Live Rule Tester Tool",
        'moduleVersion'    : "2.0",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Test transfer rules live.",
        'moduleDescription'   :
u"""
TODO
""" }
                 
#----------------------------------------------------------------
# The main processing function

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
 
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QCursor
from LiveRuleTester import Ui_MainWindow
import xml.etree.ElementTree as ET
import shutil


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
            ret += ' ' + t[i]
        return ret.lstrip()

class Main(QtGui.QMainWindow):

    def __init__(self, sentence_list, biling_file, source_text):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__biling_file = biling_file
        self.ui.BilingFileEdit.setText(biling_file)
        self.__source_text = source_text
        self.ui.SourceFileEdit.setText(source_text)
        self.__transfer_rules_file = None
        self.advancedTransfer = False
        
        self.__ruleModel = self.__transferModel = None
        self.__interChunkModel = None
        self.__postChunkModel = None
        self.__transferRulesElement = None
        self.__interchunkRulesElement = None
        self.__postchunkRulesElement = None
        self.TRIndex = None
        self.setStatusBar(None)
        
        # Tie controls to functions
        self.ui.TestButton.clicked.connect(self.TestClicked)
        self.ui.CloseButton.clicked.connect(self.CloseClicked)
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

        pwd = os.getcwd()
        self.__transfer_rules_file= os.path.join(pwd, OUTPUT_FOLDER, 'transfer_rules.t1x')
        if not self.loadTransferRules():
            self.ret_val = 0
            self.close()
            return False
        
        # Simulate a click on the transfer browse button to get the user
        # to select a transfer file
        #if self.TransferBrowseClicked() == False:
        #    self.ret_val = 0
        #    self.close()
        
        # Set the models
        self.__sent_model = SentenceList(sentence_list)

        # Check for right to left data and set the sentence list direction if needed
        # Just check the first surface form for the first word, i.e. word 0, tuple index 0
        currSent = self.__sent_model.getCurrentSent()
        
        # make sure we have some data
        if len(currSent) > 0:
            word1 = currSent[0][0]
            if self.has_RTL_data(word1):
                self.ui.listSentences.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.ui.SentCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.__sent_model.setRTL(True)
        
        self.ui.listSentences.setModel(self.__sent_model)
        self.ui.SentCombo.setModel(self.__sent_model)
        
        # Simulate a click on the sentence list box
        self.listSentComboClicked()
        
        self.ret_val = 0
        
        # Copy bilingual file to the tester folder
        shutil.copy(self.__biling_file, os.path.join(TESTER_FOLDER, os.path.basename(self.__biling_file)))
        
        # Copy makefile file to the tester folder. We do this because it could be an advanced transfer makefile
        shutil.copy(os.path.join(OUTPUT_FOLDER, 'Makefile'), TESTER_FOLDER)

    def has_RTL_data(self, word1):
        for i in range(0, len(word1)):
            if unicodedata.bidirectional(word1[i]) in (u'R', u'AL'):
                return True
        return False
        
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
    
    def SourceCheckBoxClicked(self):
        mySent = self.__sent_model.getCurrentSent()
        val = ''
        
        # Loop through all the check boxes 
        for i in range(0, len(mySent)):
            
            # If the check box is checked, put the data stream form into the source box
            if self.__checkBoxList[i].isChecked():
                
                # The 2nd part of the tuple has the data stream info.
                val += mySent[i][1] + ' '
        
        # Add a LTR marker if our text language is RTL
        if self.__sent_model.getRTL():
            val = u'\u200E' + val        
            
        self.ui.SelectedWordsEdit.setPlainText(val)                
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
    def getActiveTextEditVal(self):
        if self.ui.tabSource.currentIndex() == 0:
            ret = self.ui.SelectedWordsEdit.toPlainText()
        elif self.ui.tabSource.currentIndex() == 1:
            ret = self.ui.SelectedSentencesEdit.toPlainText()
        else:
            ret = self.ui.ManualEdit.toPlainText()
        return ret
    def listSentClicked(self):
        mySent = self.__sent_model.getCurrentSent()
        
        # Populate the data stream box with the values from each word in the sentence
        # tup is (surface_form, datastream_form)
        val = self.__sent_model.joinTupParts(mySent, 1) # 1 for the 2nd tuple element

        # Add a LTR marker if our text language is RTL
        if self.__sent_model.getRTL():
            val = u'\u200E' + val        
            
        self.ui.SelectedSentencesEdit.setPlainText(val)
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
        
        # Remove any LTR markers
        myStr = re.sub(u'\u200E', '', myStr)
        
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
        self.ui.TargetTextEdit.setPlainText('') 
        
        changed = False
        elapsed_secs = 0
        start_secs = time.time()
        
        # Wait for the modification time of the target text file to be different
        # It could take up to 3+ seconds for the target file to get created 
        while not changed and elapsed_secs < 5:
            
            # See if target file is changed in the last 4 seconds
            try:
                modified_time_in_secs = os.path.getmtime(tgt_file)
            except:
                elapsed_secs = 99
                break
            
            current_time_in_secs = time.time()
            if current_time_in_secs - modified_time_in_secs < 4:
                changed = True
                
            # Calculate elapsed seconds
            elapsed_secs = current_time_in_secs - start_secs
            
        # If it takes more than 5 seconds give an error
        if elapsed_secs == 99:
            self.ui.TargetTextEdit.setPlainText('Target file not found!')
            QApplication.restoreOverrideCursor()
            return
        elif elapsed_secs >= 5:
            self.ui.TargetTextEdit.setPlainText('No results!')
            QApplication.restoreOverrideCursor()
            return
        
        # Pause to allow the target file to be written
        time.sleep(1)
        
        # Load the target text contents into the results edit box
        tgtf = open(tgt_file)
        target_output = unicode(tgtf.read(),'utf-8')
        
        # If we have RTL chars, put in some LTR markers
        if self.has_RTL_data(target_output):
            target_output = u'\u200E' + re.sub(u'<', u'\u200E<', target_output)
        self.ui.TargetTextEdit.setPlainText(target_output)
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

    # Get need configuration file properties
    text_desired_eng = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, 'SourceMorphNamesCountedAsRoots', report)
    targetMorphNames = ReadConfig.getConfigVal(configMap, 'TargetMorphNamesCountedAsRoots', report)
    bilingFile = ReadConfig.getConfigVal(configMap, 'BilingualDictOutputFile', report)

    # check for errors
    if not (text_desired_eng and targetMorphNames and sourceMorphNames and bilingFile):
        return
    
    # Get punctuation string
    sent_punct = ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report)
    
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
        window = Main(segment_list, bilingFile, text_desired_eng)
        
        window.show()
        app.exec_()
        
        cnt = 0
        
        # Update the source database with the correct links
        if window.ret_val: # True = make the changes
            pass



                    
    #report.Info(str(cnt)+' links created.')
     
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
