#
#   LiveRuleTesterTool.py
#
#   Ron Lockwood
#   SIL International
#   7/2/16
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

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Live Rule Tester Tool",
        'moduleVersion'    : "1.0",
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
            if self.getRTL():
                pass
                #value = myHPG.getHeadword() + u' \u200F(' + myHPG.getPOS() + u')\u200F ' + myHPG.getGloss()
            else:
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

            
# Model class for list of rules.
class RuleList(QtCore.QAbstractListModel):
    
    def __init__(self, myData = [], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.__localData = myData
        self.__currentRule = myData[0] # start out on the first one
    def getCurrentRule(self):
        return self.__currentRule
    def rowCount(self, parent):
        return len(self.__localData)
    def data(self, index, role):
        row = index.row()
        myRule = self.__localData[row]
        
        if role == QtCore.Qt.DisplayRole:
            self.__currentRule = myRule
            
            # Show the rule comment and the count of active rules
            selected = myRule[0]
            value = myRule[1]
            if selected: 
                value += ' Active rule ' + str(self.__getActiveRuleNum(row))
            return QtCore.QString(value)
            
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
    def __getActiveRuleNum(self, rowNum):
        # Add up all the rules that are selected to this row number
        ret = 0
        for x in range(0, rowNum+1):
            if self.__localData[x][0]: # True value for selected
                ret += 1
        return ret

class Main(QtGui.QMainWindow):

    def __init__(self, sentence_list, biling_file, source_text):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.__biling_file = biling_file
        self.ui.BilingFileEdit.setText(biling_file)
        self.__source_text = source_text
        self.ui.SourceFileEdit.setText(source_text)
        
        self.__rule_model = None
        self.transfer_rules_file = None
        self.TRIndex = None
        self.setStatusBar(None)
        # Tie controls to functions
        self.ui.TestButton.clicked.connect(self.TestClicked)
        self.ui.CloseButton.clicked.connect(self.CloseClicked)
        self.ui.listSentences.clicked.connect(self.listSentClicked)
        #self.ui.listTransferRules.currentChanged.connect(self.listTransferRulesClicked)
        #self.ui.listTransferRules.dataChanged.connect(self.listTransferRulesClicked)
        self.ui.listTransferRules.clicked.connect(self.listTransferRulesClicked)
        #self.ui.listTransferRules.selectionChanged.connect(self.TRSelectionChanged)
        self.ui.SentCombo.currentIndexChanged.connect(self.listSentComboClicked)
        self.ui.TransferFileBrowseButton.clicked.connect(self.TransferBrowseClicked)
        self.ui.BilingFileBrowseButton.clicked.connect(self.BilingBrowseClicked)
        self.ui.tabSource.currentChanged.connect(self.TabClicked)
        self.ui.refreshButton.clicked.connect(self.RefreshClicked)
        self.ui.selectAllButton.clicked.connect(self.SelectAllClicked)
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
            myCheck.setGeometry(QtCore.QRect(0,0, 27, 27)) # default position
            
            # connect to a function
            myCheck.clicked.connect(self.CheckClicked)
            
            # add it to the list
            self.__checkBoxList.append(myCheck)

        # Simulate a click on the transfer browse button to get the user
        # to select a transfer file
        if self.TransferBrowseClicked() == False:
            self.ret_val = 0
            self.close()
        
        # Set the models
        self.__sent_model = SentenceList(sentence_list)
        self.ui.listSentences.setModel(self.__sent_model)
        self.ui.SentCombo.setModel(self.__sent_model)
        
        # Simulate a click on the sentence list box
        self.listSentComboClicked()
        
        self.ret_val = 0
        
        # Check for right to left data and set the sentence list direction if needed
        # Just check the first surface form for the first word, i.e. word 0, tuple index 0
        currSent = self.__sent_model.getCurrentSent()
        word1 = currSent[0][0]
        for i in range(0, len(word1)):
            if unicodedata.bidirectional(word1[i]) in (u'R', u'AL'):
                self.ui.listSentences.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.ui.SentCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.__sent_model.setRTL(True)
                break
    
    def TRSelectionChanged(self):
        self.TRIndex = index.row() # currentIndex
    
    def UpButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() > 0:
            # pop current list item and insert it one above
            self.rules_element._children.insert(self.TRIndex.row()-1,\
                                                self.rules_element._children.pop(self.TRIndex.row()))
            
            # copy the selection
            cur_state = self.__rule_model.item(self.TRIndex.row()).checkState()
            oth_state = self.__rule_model.item(self.TRIndex.row()-1).checkState()
            self.__rule_model.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__rule_model.item(self.TRIndex.row()-1).setCheckState(cur_state)
            
            # redo the display
            self.listTransferRulesClicked(self.TRIndex)
            
            # change the selection to the one just moved
            #self.__rule_model.item(self.TRIndex.row()-1).setSelected(True)
            
    def DownButtonClicked(self):
        if self.TRIndex and self.TRIndex.row() < len(self.rules_element._children)-1:
            # pop current list item and insert it one above
            self.rules_element._children.insert(self.TRIndex.row()+1,\
                                                self.rules_element._children.pop(self.TRIndex.row()))
            
            # copy the selection
            cur_state = self.__rule_model.item(self.TRIndex.row()).checkState()
            oth_state = self.__rule_model.item(self.TRIndex.row()+1).checkState()
            self.__rule_model.item(self.TRIndex.row()).setCheckState(oth_state)
            self.__rule_model.item(self.TRIndex.row()+1).setCheckState(cur_state)
            
            # redo the display
            self.listTransferRulesClicked(self.TRIndex)
    
            # change the selection to the one just moved
            #self.__rule_model.item(self.TRIndex.row()+1).setSelected(True)
            
    def SelectAllClicked(self):
        # Loop through all the items in the rule list model
        for i in range(0, self.__rule_model.rowCount()):
            # Check each box
            self.__rule_model.item(i).setCheckState(QtCore.Qt.Checked)
        
        # Redo the numbering
        self.listTransferRulesClicked(self.TRIndex)
            
    def RefreshClicked(self):
        self.loadTransferRules()
    
    def CheckClicked(self):
        mySent = self.__sent_model.getCurrentSent()
        val = ''
        
        # Loop through all the check boxes 
        for i in range(0, len(mySent)):
            
            # If the check box is checked, put the data stream form into the source box
            if self.__checkBoxList[i].isChecked():
                
                # The 2nd part of the tuple has the data stream info.
                val += mySent[i][1] + ' '
                
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
        self.ui.SelectedSentencesEdit.setPlainText(val)
    def __ClearAllChecks(self):
        for check in self.__checkBoxList:
            check.setVisible(False)
            check.setChecked(False)
    def TabClicked(self):
        pass
        #if self.ui.tabSource.currentIndex() != 0:
        #    self.__ClearAllChecks()
        #else:
        #    self.listSentComboClicked()
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
        
    def TransferBrowseClicked(self):
        # Bring up file select dialog
        transfer_rules_file_tup = \
         QFileDialog.getOpenFileNameAndFilter(self, 'Choose Transfer File',\
            'Output', 'Transfer Rules (transfer_rules.t1x)')
        
        self.transfer_rules_file = transfer_rules_file_tup[0]
        
        if not self.loadTransferRules():
            self.ret_val = 0
            self.close()
            return False
        
        return True
        
    def loadTransferRules(self):
            
        # Verify we have a valid transfer file.
        try:
            test_tree = ET.parse(self.transfer_rules_file)
        except:
            QMessageBox.warning(self, 'Invalid File', 'The transfer file you selected is invalid.')
            return False
        
        test_rt = test_tree.getroot()
        self.rules_element = test_rt.find('section-rules')
        
        if self.rules_element:
            self.ui.TransferFileEdit.setText(self.transfer_rules_file)
            self.__ruleFileXMLtree = test_tree
            self.displayRules(self.rules_element)
        else:
            QMessageBox.warning(self, 'Invalid Rules File', \
            'The transfer file has no transfer element or no section-rules element')
            self.ui.TransferFileEdit.setText('')
        
        return True

    def listTransferRulesClicked(self, index):
        self.TRIndex = index
        active_rules = 1
        for i, el in enumerate(self.rules_element):
            ruleText = el.get('comment')
            
            # If active add text with the active rule #
            if self.__rule_model.item(i).checkState():
                self.__rule_model.item(i).setText(ruleText + ' - Active Rule ' + str(active_rules))
                active_rules += 1
            else:
                self.__rule_model.item(i).setText(ruleText)
    
    def displayRules(self, rules_element):
        self.__rule_model = QtGui.QStandardItemModel()
        self.__rule_comment_list = []
        
        # Loop through each rule
        for rule_el in rules_element:
            
            # Get the comment for the rule
            comment = rule_el.get('comment')
            
            # Create an item object
            item = QtGui.QStandardItem(comment) 
            item.setCheckable(True)
            item.setCheckState(False)
            self.__rule_model.appendRow(item)
            #self.__rule_comment_list.append(comment)
            
        # Initialize the model for the rule list control
        self.ui.listTransferRules.setModel(self.__rule_model)
        
    def TestClicked(self):
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        
        # TODO: allow editable rule file edit box?
        # Make sure we have a transfer file
        if self.ui.TransferFileEdit.text() == '':
            return
        
        # Create the tester folder if it doesn't exist
        #if not os.path.exists(TESTER_FOLDER):
        #    os.makedirs(TESTER_FOLDER)
            
        # Copy bilingual file to the tester folder
        shutil.copy(self.__biling_file, os.path.join(TESTER_FOLDER, os.path.basename(self.__biling_file)))
        
        # Save the source text to the tester folder
        source_file = os.path.join(TESTER_FOLDER, 'source_text.aper')
        sf = open(source_file, 'w')
        myStr = unicode(self.getActiveTextEditVal())
        sf.write(myStr.encode('utf-8'))
        sf.close()
        
        # Save the transfer rules file with the selected rules present

        tr_file = os.path.join(TESTER_FOLDER, 'transfer_rules.t1x')
        rf = open(tr_file, 'w')
        
        # Copy the xml structure to a new object
        myTree = copy.deepcopy(self.__ruleFileXMLtree)
        myRoot = myTree.getroot()
        
        sr_element = myRoot.find('section-rules')
        
        # Remove the section-rules element
        myRoot.remove(sr_element)
        
        # Recreate the section-rules element
        new_sr_element = ET.SubElement(myRoot, 'section-rules')
        
        rule_file = self.__ruleFileXMLtree.getroot()
        rules_element = rule_file.find('section-rules')

        # Loop through all the selected rules
        for i, rule_el in enumerate(rules_element):
        
            # Add to the xml structure if it is a selected rule
            if self.__rule_model.item(i).checkState():
                new_sr_element.append(rule_el) 
            
        # Write out the file
        myTree.write(rf, encoding='UTF-8', xml_declaration=True) #, pretty_print=True)
        rf.close()
        
        ## Display the results
        
        # Clear the results box
        self.ui.TargetTextEdit.setPlainText('') 
        
        tgt_file = os.path.join(TESTER_FOLDER, 'target_text.aper')

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
        target_output = tgtf.read()
        self.ui.TargetTextEdit.setPlainText(target_output)
        tgtf.close()
        
        # Load the log file
        log_file = os.path.join(TESTER_FOLDER, 'err_log')
        lf = open(log_file)
        self.ui.LogEdit.setPlainText(lf.read())
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
            text = interlinText
        text_list.append(text_desired_eng)
        
    if not foundText:
        report.Error('The text named: '+text_desired_eng+' not found.')
        return

    getSurfaceForm = True
    segment_list = Utils.get_interlin_data(DB, report, sent_punct, text, typesList, getSurfaceForm)
    
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
