#
#   LinkSenseTool
#
#   Ron Lockwood
#   SIL International
#   7/18/15
#
#   Version 3.1 - 11/30/21 - Ron Lockwood
#    Rewrite of the MainFunction. Use the Utils.getInterlinData function to get
#    the words in the interlinear text. The advantage is that the Utils function
#    puts together the phrasal verbs and the like. Also modularized the MainFunction.
#    Also added the feature of filtering the list to not show proper nouns. Also
#    show X.X form of the headword, but only if it isn't 1.1. Also only don't do
#    the fuzzy compare for proper nouns. Also trimmed down the url link to the 
#    target DB. It matches what FLEx 9.1 uses. Fixed bug where the 2nd time an
#    entry with exact or fuzzy match wasn't getting all the matching rows that
#    were there the first time. Now I save the matching rows and add them again.
#    
#   Version 3.0 - 1/29/21 - Ron Lockwood
#    Changes for python 3 conversion. This included removing the code for a
#    delegate widget and a custom TableView. Instead the IsCheckable signal is
#    used.
#    Also overhauled the TableView user interface to support unlinking of senses
#    currently linked in the DB. This required changes in the Link object as
#    well as the code for loading the link list and processing the link list
#    after the user presses OK.
#
#   Version 2.2.2 - 2/27/19 - Ron Lockwood
#    Skip empty MSAs
#
#   Version 2.2.1 - 1/15/18 - Marc Penner
#    Wrapped calls to resetInternalData with beginResetModel and end.. so that 
#    blank lines get removed.
#
#   Version 2.2 - 1/18/17 - Ron
#    Use BestAnalysisAlternative instead of AnalysisDefault.
#    Fixed bug where only one fuzzy match was getting processed.
#    To improve performance, only find fuzzy matches when the difference in 
#    the length of the glosses is less than or equal to a constant -- 
#    currently set at 3.
#    If no POS found, return unicode string UNK instead of normal string -- 
#    Fixes bug when checking for RTL text in a cell.
#    Change the way FlexTools Update status bar gets calculated. Weighted by 
#    lexicon total now.
#
#   Version 2.1 - 10/27/16 - Ron
#    Converted the Link It column to checkboxes.
#
#   Version 2.0.2 - 8/27/16 - Ron
#    Change scale numbers to 1 if they come out 0 initially.
#
#   Version 2.0.1 - 6/21/16 - Ron
#    Don't allow Link It column to change to 1 if there is no target information.
#    Force resizing a bit for filter/unfilter to force a refresh of the table.
#
#   Version 2.0 - 6/16/16 - Ron
#    Major overhaul. Use class objects to model the link information.
#    Allow the user to link any sense in the text not just the unlinked ones
#    matched a gloss as before. Also use a fuzzy compare logic for near matches 
#    on gloss to give more suggestions. Now a list of target senses is provided
#    which can be used as the sense to link to for any source sense.
#    Also, handle variants of senses.
#
#   Version 1.0.1 - 5/7/16 - Ron
#    Give a more helpful message when the target database is not found.
#
#   For a given text, display all the senses and if there is link data present
#   show it. Otherwise do a fuzzy compare on gloss to suggest a possible link
#   for the source sense. Senses where no suggestion could be made are also
#   shown. The user can select a target sense from the combo box and then
#   double-click on the target column to have that data inserted. Only rows
#   that have a 1 showing in the first column will get changed in the source
#   database. If the user clicks on the checkbox at the top, the list will be
#   filtered down to just the senses that don't currently have a corresponding
#   link to a target sense.
#
#   Note that the user can change existing senses to be linked to something new.
#   The fuzzy search is attempted as quick as possible by caching seen glosses
#   and by not trying fuzzy searches if we get an exact match or if the gloss
#   is short.
#
#   The table display will have duplicate senses since the same sense may occur 
#   multiple times in a text. The object that goes with those senses will be
#   the same and when it gets updated duplicates senses throughout the table
#   will be updated.
#

import re
import sys
import unicodedata
from fuzzywuzzy import fuzz

from System import Guid
from System import String

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication

from FTModuleClass import *                                                 
from FTModuleClass import FlexToolsModuleClass

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.DomainServices import SegmentServices
from flexlibs.FLExProject import FLExProject, GetProjectNames

import ReadConfig
import Utils

from Linker import Ui_MainWindow

#----------------------------------------------------------------
# Configurables:
PROPER_NOUN_ABBREV = 'nprop'
DUMP_VOCAB_WORDS = True


# The minimum length a word should have before doing a fuzzy compare
# otherwise an exact comparision is used
MIN_GLOSS_LEN_FOR_FUZZ = 5
# Only do a fuzzy compare if the difference in the lengths of the strings
# is less than this number
MIN_DIFF_GLOSS_LEN_FOR_FUZZ = 3
# The percentage or higher in similarity that two words must have in  
# order to be outputted as a possible match. 
FUZZ_THRESHOLD = 74

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Sense Linker Tool",
        FTM_Version    : "3.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Link source and target senses.",
        FTM_Help   : "",
        FTM_Description:  
"""
The source database should be chosen for this module. This module will create links 
in the source project to senses in the target project. This module will show a window
with a list of all the senses in the text. White background rows indicate links that
already exist. blue background rows indicate suggested links based on an exact match
on gloss, light blue background rows indicate suggested links based on a close match on
gloss (currently 75% similar), red background rows
have no link yet established. Double-click on the Target Head Word column for a row to copy
the currently selected target sense in the upper combo box into that row. Click the checkbox
to create a link for that row. I.e. the source sense will be linked to the target sense.
Unchecking a checkbox for white row will unlink the specified sense from its target sense.
Close matches are only attempted for words with five letters or longer.
For suggested sense pairs where
there is a mismatch in the grammatical category, both categories are colored red. This
is to indicate you may not want to link the two sense even though the glosses match. The
database that FlexTools should be set to is your source project. Set the TargetProject
property in the FlexTrans.config file to the name of your target project.
FlexTrans.config should be in the FlexTools folder. This module requires
two sense-level custom fields in your source project. They should be simple text fields.
One is to link to an entry in the target project and the other is to indicate a sense
number number in that entry. Set the FlexTrans.config file properties 
SourceCustomFieldForEntryLink
and SourceCustomFieldForSenseNum to the corresponding custom field names. Created links
will appear in the field named in SourceCustomFieldForEntryLink. If the sense number
being linked to is not sense number one, the field named in SourceCustomFieldForSenseNum
will be set to the corresponding sense number. 
""" }
                 
#----------------------------------------------------------------

# model the information having to do with basic sense information, namely
# headword, part of speech (POS) and gloss thus the name HPG
class HPG(object):
    def __init__(self, Sense, Headword, POS, Gloss, SenseNum=1):
        self.__sense = Sense
        self.__headword = Headword
        self.__POS = POS
        self.__gloss = Gloss
        self.__senseNum = SenseNum
    def getSense(self):
        return self.__sense 
    def getHeadword(self):
        return self.__headword
    def getPOS(self):
        return self.__POS
    def getGloss(self):
        return self.__gloss
    def getSenseNum(self):
        return self.__senseNum

INITIAL_STATUS_UNLINKED = 0
INITIAL_STATUS_LINKED = 1    
INITIAL_STATUS_EXACT_SUGGESTION = 2
INITIAL_STATUS_FUZZY_SUGGESTION = 3

# model the information having to do with a link from a source sense
# to a target sense
class Link(object):
    def __init__(self, srcHPG, tgtHPG=None):
        self.set_srcHPG(srcHPG)
        self.set_tgtHPG(tgtHPG)
        self.initial_status = INITIAL_STATUS_UNLINKED
        self.linkIt = False
        self.modified = False
        self.tgtModified = False
    def get_srcHPG(self):
        return self.__srcHPG
    def get_tgtHPG(self):
        return self.__tgtHPG
    def get_srcPOS(self):
        return self.__srcHPG.getPOS()
    def get_tgtPOS(self):
        return self.__tgtHPG.getPOS()
    def get_srcGloss(self):
        return self.__srcHPG.getGloss()
    def get_tgtGloss(self):
        return self.__tgtHPG.getGloss()
    def get_initial_status(self):
        return self.initial_status
    def set_initial_status(self, myStatus):
        self.initial_status = myStatus
        if myStatus == INITIAL_STATUS_LINKED:
            self.linkIt = True # this shows that this is a sense the user intends to keep linked
        else:
            self.linkIt = False
    def set_srcHPG(self, srcHPG):
        self.__srcHPG = srcHPG
    def set_tgtHPG_only(self, tgtHPG):
        self.__tgtHPG = tgtHPG
    def set_tgtHPG(self, tgtHPG):
        self.__tgtHPG = tgtHPG
        if tgtHPG is not None:
            self.set_initial_status(INITIAL_STATUS_LINKED)
            self.linkIt = True
    def get_srcSense(self):
        return self.__srcHPG.getSense()
    def get_tgtSense(self):
        return self.__tgtHPG.getSense()
    def get_tgtGuid(self):
        return self.__tgtHPG.getSense().OwningEntry.Guid.ToString()
    def get_tgtSenseNum(self):
        return self.__tgtHPG.getSenseNum()
    def is_suggestion(self):
        if self.get_initial_status() == INITIAL_STATUS_EXACT_SUGGESTION or self.get_initial_status() == INITIAL_STATUS_FUZZY_SUGGESTION:
            return True
        return False
    def isInitiallyUnlinkedAndTargetUnmodified(self):
        return self.get_initial_status() == INITIAL_STATUS_LINKED and self.tgtModified == False
    def getDataByColumn(self, col):
        ret =''
        if col > 0 and col < 4:
            if col == 1:
                ret = self.get_srcHPG().getHeadword()
            elif col == 2:
                ret = self.get_srcHPG().getPOS()
            elif col == 3:
                ret = self.get_srcHPG().getGloss()
                
        elif col > 3 and col < 7:
            # columns 4-6 need to be blank if there is no tgtHPG or we unchecked the linkIt box and we have a 
            # non-suggested link. This is just extra visual feedback that we will do nothing when OK is clicked.
            if self.get_tgtHPG() == None or (self.linkIt == False and not self.is_suggestion()):
                ret = ''   
            elif col == 4:
                ret = self.get_tgtHPG().getHeadword()
            elif col == 5:
                ret = self.get_tgtHPG().getPOS()
            elif col == 6:
                ret = self.get_tgtHPG().getGloss()
        return ret
    
class LinkerCombo(QtCore.QAbstractListModel):
    
    def __init__(self, myData = [], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.__localData = myData
        self.__currentHPG = myData[0] # start out on the first one
        self.__RTL = False
    def setRTL(self, val):
        self.__RTL = val
    def getRTL(self):
        return self.__RTL
    def getCurrentHPG(self):
        return self.__currentHPG
    def rowCount(self, parent):
        return len(self.__localData)
    def data(self, index, role):
        row = index.row()
        myHPG = self.__localData[row]
        
        if role == QtCore.Qt.DisplayRole:
            if self.getRTL():
                value = myHPG.getHeadword() + ' \u200F(' + myHPG.getPOS() + ')\u200F ' + myHPG.getGloss()
            else:
                value = myHPG.getHeadword() + ' (' + myHPG.getPOS() + ') ' + myHPG.getGloss()
            self.__currentHPG = myHPG    
            return value
            
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
            
class LinkerTable(QtCore.QAbstractTableModel):
    
    def __init__(self, myData = [[]], headerData = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__localData = myData
        self.__myHeaderData = headerData
        self.__selectedHPG = None
    def getInternalData(self):
        return self.__localData
    def setInternalData(self, Data):
        self.__localData = Data
    def setSelectedHPG(self, selHPG):    
        self.__selectedHPG = selHPG
    def rowCount(self, parent):
        return len(self.__localData)
    def columnCount(self, parent):
        return 7 
    def headerData(self, section, orientation, role):
        
        # Set the background color
        if role == QtCore.Qt.BackgroundRole:
            
            qColor = QtGui.QColor(QtCore.Qt.gray)
            return qColor
        
        if role == QtCore.Qt.DisplayRole:
            
            if orientation == QtCore.Qt.Horizontal:
                
                return self.__myHeaderData[section]
            else:
                return
            
    def data(self, index, role):
        
        row = index.row()
        col = index.column()
        locData = self.__localData[row]
        
        if role == QtCore.Qt.EditRole:
            
            if col == 0: # Checkbox column
                pass
            
            elif col == 4: # target headword column
                
                locData.set_tgtHPG_only(self.__selectedHPG)
                locData.linkIt = True
                locData.tgtModified = True
                #self.dataChanged.emit(index, index)
                
                return self.__selectedHPG.getHeadword()
        
        # Set the foreground (font) color
        if role == QtCore.Qt.ForegroundRole:
            
            qColor = QtGui.QColor(QtCore.Qt.black)
            
            if row >= 0:
                
                # src headword
                if col == 1:
                    
                    qColor = QtGui.QColor(QtCore.Qt.darkGreen)
                
                # tgt headword    
                elif col == 4:
                    
                    qColor = QtGui.QColor(QtCore.Qt.darkBlue)
                
                # gram. category    
                elif (col == 2 or col == 5) and locData.is_suggestion() == True: 
                    
                    # If there is a mismatch in grammatical category color it red
                    if locData.get_srcPOS().lower() != locData.get_tgtPOS().lower():
                        
                        qColor = QtGui.QColor(QtCore.Qt.red)
                        
                qBrush = QtGui.QBrush(qColor)
                
                return qBrush
        
        # Set the background color
        if role == QtCore.Qt.BackgroundRole:
            
            if row >= 0:
                
                initiallyLinkedUnmodifiedSense = locData.isInitiallyUnlinkedAndTargetUnmodified()
                
                # Mark in yellow the first column cells for the rows to be linked or unlinked (in the case of a previously linked row from the DB)
                if col == 0 and ((locData.linkIt == True and not initiallyLinkedUnmodifiedSense) or (locData.linkIt == False and initiallyLinkedUnmodifiedSense)):
                    
                    qColor = QtGui.QColor(QtCore.Qt.yellow)
                
                # Modified rows get a color just for the target columns
                elif col >= 4 and col <= 6 and (locData.tgtModified == True or (locData.get_initial_status() == INITIAL_STATUS_LINKED and locData.linkIt == False)):
                    
                    qColor = QtGui.QColor(152, 251, 152) # pale green
                
                # Exact suggestion 
                elif locData.get_initial_status() == INITIAL_STATUS_EXACT_SUGGESTION:
                    
                    qColor = QtGui.QColor(176, 255, 255) # medium cyan
                    
                # Fuzzy suggestion 
                elif locData.get_initial_status() == INITIAL_STATUS_FUZZY_SUGGESTION:
                            
                    qColor = QtGui.QColor(224, 255, 255) # light cyan
                
                # No links
                elif locData.get_initial_status() == INITIAL_STATUS_UNLINKED:
                    
                    qColor = QtGui.QColor(255, 192, 203) # pink
                    
                # Existing link in the DB    
                else: # INITIAL_STATUS_LINKED:
                    
                    qColor = QtGui.QColor(QtCore.Qt.white)

                self.dataChanged.emit(index, index)

                return qColor
        
        if role == QtCore.Qt.DisplayRole:
             
            if col != 0:
                 
                return locData.getDataByColumn(col)
                 
        if role == QtCore.Qt.CheckStateRole:
             
            if col == 0:
                 
                # If user said link it, check the box. Also if there is an existing link in the DB on 
                if locData.linkIt == True or (locData.get_initial_status() == INITIAL_STATUS_LINKED and locData.modified == False):
                     
                    val = QtCore.Qt.Checked
                else:
                    val = QtCore.Qt.Unchecked
                
                # force an update so we get colors changing as needed
                #self.dataChanged.emit(index, index)
                
                return val
             
        elif role == QtCore.Qt.TextAlignmentRole:
             
            if col == 0:
                 
                # Doesn't have an effect
                return QtCore.Qt.AlignCenter
             
            # Check if we have right to left data in a column, if so align it right
            elif col > 0 and len(locData.getDataByColumn(col)) > 0:
                 
                # check first character of the given cell
                if unicodedata.bidirectional(locData.getDataByColumn(col)[0]) in ('R', 'AL'): 
                     
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter
                
    def flags(self, index):
        
        locData = self.__localData[index.row()]
        
        # Columns 0 and 4 are enabled and selectable
        val = QtCore.Qt.ItemIsSelectable
        
        # Add checkable for the 1st column
        if index.column() == 0:

            # Don't allow the box to be checked if we have an unlinked row that hasn't had the target modified
            if not (locData.get_initial_status() == INITIAL_STATUS_UNLINKED and locData.tgtModified == False):
            
                val =  val | QtCore.Qt.ItemIsEnabled
                
            val =  val | QtCore.Qt.ItemIsUserCheckable 
        
        # Add editable for the target headword column  
        elif index.column() == 4:
            
            val = val | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable 
            
        return val
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        
        col = index.column()

        if role == QtCore.Qt.CheckStateRole and col == 0:
            
            row = index.row()
            
            if value == QtCore.Qt.Checked: 
                
                self.__localData[row].linkIt = True
                self.__localData[row].modified = True
            else:
                self.__localData[row].linkIt = False
                self.__localData[row].modified = True
                
        return True
            
class Main(QMainWindow):

    def __init__(self, myData, headerData, comboData):
        QMainWindow.__init__(self)
        self.showOnlyUnlinked = False
        self.hideProperNouns = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        self.__model = LinkerTable(myData, headerData)
        self.__fullData = myData
        self.ui.tableView.setModel(self.__model)
        self.__combo_model = LinkerCombo(comboData)
        self.ui.targetLexCombo.setModel(self.__combo_model)
        self.ret_val = 0
        self.cols = 7
        self.ui.targetLexCombo.currentIndexChanged.connect(self.ComboClicked)
        self.ui.ShowOnlyUnlinkedCheckBox.clicked.connect(self.ShowOnlyUnlinkedClicked)
        self.ui.HideProperNounsCheckBox.clicked.connect(self.HideProperNounsClicked)
        self.ComboClicked()
        
        myHPG = self.__combo_model.getCurrentHPG()
        myHeadword = myHPG.getHeadword()
        
        # Check for right to left data and set the combobox direction if needed
        for i in range(0, len(myHeadword)):
            if unicodedata.bidirectional(myHeadword[i]) in ('R', 'AL'):
                self.ui.targetLexCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.__combo_model.setRTL(True)
                break
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        
        # Stretch the table view to fit
        self.ui.tableView.setGeometry(10, 50, self.width() - 20, \
                                      self.height() - 80 - self.ui.OKButton.height() - 25)
        
        # Move the OK and Cancel buttons as the window gets resized.
        x = self.width()//2 - 10 - self.ui.OKButton.width()
        if x < 0:
            x = 0
        self.ui.OKButton.setGeometry(x, 50 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                     self.ui.OKButton.height())
        self.ui.CancelButton.setGeometry(x + self.ui.OKButton.width() + 10,  \
                                         50 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                         self.ui.OKButton.height())
        firstColWidth = 45
        
        # Set the column widths
        colCount = self.cols # self.ui.tableView.columnCount()
        colWidth = ((self.ui.tableView.width() - firstColWidth) // (colCount - 1)) - 4 #don't include 1st column
        if colWidth < 40:
            colWidth = 40

        self.ui.tableView.setColumnWidth(0, firstColWidth)
        for i in range(1, colCount):
            self.ui.tableView.setColumnWidth(i, colWidth)
    def ComboClicked(self):
        # Set the target HPG for the model  
        myHPG = self.__combo_model.getCurrentHPG()
        self.__model.setSelectedHPG(myHPG)
    def OKClicked(self):
        self.ret_val = 1
        self.close()
    def ShowOnlyUnlinkedClicked(self):
        if self.ui.ShowOnlyUnlinkedCheckBox.isChecked():
            self.showOnlyUnlinked = True
        else:
            self.showOnlyUnlinked = False
        self.filter()
    def HideProperNounsClicked(self):
        if self.ui.HideProperNounsCheckBox.isChecked():
            self.hideProperNouns = True
        else:
            self.hideProperNouns = False
        self.filter()
    def CancelClicked(self):
        self.ret_val = 0
        self.close()
    def filter(self):
        
        self.__model.beginResetModel();

        # If both are unchecked, use the full list
        if self.showOnlyUnlinked == False and self.hideProperNouns == False:
            
            self.__model.setInternalData(self.__fullData)
        else:
            # Create a new filtered list
            filteredData = []
            
            for myLink in self.__fullData:
                
                keepIt = False
                
                if self.showOnlyUnlinked:
                    
                    if myLink.get_tgtHPG() is None or myLink.is_suggestion():
                        
                        keepIt = True
                else:
                    keepIt = True
                        
                if self.hideProperNouns:
                    
                    if keepIt == True:
                    
                        if myLink.get_srcPOS() != PROPER_NOUN_ABBREV:
                            
                            keepIt = True
                        else:
                            keepIt = False
                if keepIt:
                        
                    filteredData.append(myLink)
                    
            self.__model.setInternalData(filteredData)
            
        self.__model.endResetModel();
        self.rows = len(self.__model.getInternalData())

        # crude way to cause a repaint
        tv = self.ui.tableView
        tv.setGeometry(tv.x()+1,tv.y()+1,tv.width(),tv.height()+1)
        tv.setGeometry(tv.x()-1,tv.y()-1,tv.width(),tv.height()-1)
        
        self.ui.tableView.update()
        self.__model.resetInternalData()
        
        return
    
def GetEntryWithSense(e):
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

def remove1dot1(lem):
    return re.sub('1\.1', '', lem)
    
def fixupLemma(lem, entry, senseNum):
    
    lem = ITsString(entry.HeadWord).Text
    lem = Utils.add_one(lem)
    lem = lem + '.' + str(senseNum) # add sense number
    
    # If the lemma ends with 1.1, remove it (for optics)
    return remove1dot1(lem)

def get_gloss_map_and_tgtLexList(TargetDB, report, gloss_map, targetMorphNames, tgtLexList, scale_factor):

    # Loop through all the target entries
    for entry_cnt,e in enumerate(TargetDB.LexiconAllEntries()):
    
        report.ProgressUpdate(int(entry_cnt/scale_factor))
        
        # Don't process affixes, clitics
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and ITsString(e.LexemeFormOA.\
           MorphTypeRA.Name.BestAnalysisAlternative).Text in targetMorphNames:
        
            # Loop through senses
            for senseNum, mySense in enumerate(e.SensesOS):
                # Skip empty MSAs
                if mySense.MorphoSyntaxAnalysisRA == None:
                    continue
                
                # Get headword, POS, gloss
                headword = ITsString(e.HeadWord).Text
                
                # Make the lemma in the form x.x (but remove if 1.1)
                headword = fixupLemma(headword, e, senseNum+1)
                
                if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                    POS = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                    Abbreviation.BestAnalysisAlternative).Text
                else:
                    POS = 'UNK'
                    
                gloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
                
                # If we have a valid gloss, add it to the map
                if gloss and len(gloss) > 0:
                    # Create an HPG object
                    myHPG = HPG(mySense, headword, POS, gloss, senseNum+1)
                    
                    # Add this object to the list of all entry-senses for display
                    # in the combo box
                    tgtLexList.append(myHPG)
                    
                    if gloss not in gloss_map:
                        gloss_map[gloss] = [myHPG]
                    else: # multiple senses for this gloss
                        gloss_map[gloss].append(myHPG)
                        
    return True

# Given an entry guid and a sense #, look up the the sense info. 
def get_HPG_from_guid(TargetDB, myGuid, senseNum, report):
                      
    ret = None
          
    # Look up the entry in the trgt project by guid
    repo = TargetDB.project.ServiceLocator.GetInstance(ILexEntryRepository)
    guid = Guid(String(myGuid))

    try:
        targetEntry = repo.GetObject(guid)
    except:
        report.Error('Invalid guid or guid not found in target database. Guid: '+myGuid)
        return ret
    
    if targetEntry:
        
        lem = ITsString(targetEntry.HeadWord).Text

        # Make the lemma in the form x.x (but remove it 1.1)
        lem = fixupLemma(lem, targetEntry, senseNum)
        
        # Get the POS abbreviation for the target sense, assuming we have a stem
        if senseNum <= len(targetEntry.SensesOS.ToArray()):
            
            targetSense = targetEntry.SensesOS.ToArray()[senseNum-1]
            if targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                # TODO: verify PartOfSpeechRA is valid
                # Get target pos abbreviation and gloss
                POS = ITsString(targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                Abbreviation.BestAnalysisAlternative).Text
         
                Gloss = ITsString(targetSense.Gloss.BestAnalysisAlternative).Text
                
                # Create an HPG (headword-POS-gloss) object
                myHPG = HPG(targetSense, lem, POS, Gloss, senseNum)
                
                ret = myHPG
    
    return ret

# do check for exact match and sometimes fuzzy match to find suggested 
# target senses to be linked to
def getMatchesOnGloss(gloss, gloss_map, save_map, doFuzzyCompare):
    matchList = []
    
    # check for exact match
    if gloss in gloss_map:
        matchList = gloss_map[gloss]
    elif doFuzzyCompare:    
        # See if we've processed this gloss before
        if gloss not in save_map:
            # See if we have a candidate for a fuzzy compare
            gloss_len = len(gloss)
            if gloss_len >= MIN_GLOSS_LEN_FOR_FUZZ:
                # Loop through all the target glosses
                for mgloss in list(gloss_map.keys()):
                    mgloss_len = len(mgloss)
                    # skip the fuzzy match if the target gloss is to small or there's a big difference in length
                    if mgloss_len >= MIN_GLOSS_LEN_FOR_FUZZ and \
                       abs(mgloss_len-gloss_len) <= MIN_DIFF_GLOSS_LEN_FOR_FUZZ:
                        # See if we have a match
                        if fuzz.QRatio(mgloss, gloss) > FUZZ_THRESHOLD:
                            matchList.extend(gloss_map[mgloss])
                            save_map[gloss] = matchList
        else: 
            # use saved list
            matchList = save_map[gloss]
    return matchList

def MainFunction(DB, report, modify=True):
        
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get need configuration file properties
    text_desired_eng = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, 'SourceMorphNamesCountedAsRoots', report)
    linkField = ReadConfig.getConfigVal(configMap, 'SourceCustomFieldForEntryLink', report)
    numField = ReadConfig.getConfigVal(configMap, 'SourceCustomFieldForSenseNum', report)
    targetMorphNames = ReadConfig.getConfigVal(configMap, 'TargetMorphNamesCountedAsRoots', report)

    if not (text_desired_eng and linkField and numField and text_desired_eng and sourceMorphNames):
        return
    
    # Find the desired text
    foundText = False
    for interlinText in DB.ObjectsIn(ITextRepository):
        if text_desired_eng == ITsString(interlinText.Name.BestAnalysisAlternative).Text:
            foundText = True
            break;
        
    if not foundText:
        report.Error('The text named: '+text_desired_eng+' not found.')
        return

    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    senseNumField = DB.LexiconGetSenseCustomFieldNamed(numField)
    
    if not (senseEquivField):
        report.Error(linkField + " field doesn't exist. Please read the instructions.")

    if not (senseNumField):
        report.Error(numField + " field doesn't exist. Please read the instructions.")

    if not (senseEquivField and senseNumField):
        return

    TargetDB = FLExProject()

    # Open the target database
    targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
    if not targetProj:
        return
    
    # See if the target project is a valid database name.
    if targetProj not in GetProjectNames():
        report.Error('The Target Database does not exist. Please check the configuration file.')
        return

    report.Info('Opening: '+targetProj+' as the target database.')

    try:
        TargetDB.OpenProject(targetProj, True)
    except: #FDA_DatabaseError, e:
        raise

    report.Info("Starting " + docs[FTM_Name] + " for text: " + text_desired_eng + ".")

    preGuidStr = 'silfw://localhost/link?database%3d'
    preGuidStr += re.sub('\s','+', targetProj)
    preGuidStr += '%26tool%3dlexiconEdit%26guid%3d'
     
    gloss_map = {}
    tgtLexList = []

    TargetDB_tot = TargetDB.LexiconNumberOfEntries() 

    # TODO: rework how we do the progress indicator since we now use the Utils.getInterlinData function
    ENTRIES_SCALE_FACTOR, bundles_scale, entries_scale = calculate_progress_stats(report, interlinText, TargetDB_tot)

    # Create a map of glosses to target senses and their number and a list of target lexical senses
    if not get_gloss_map_and_tgtLexList(TargetDB, report, gloss_map, targetMorphNames, tgtLexList, entries_scale):
        return

    # Go through the interlinear words
    #myData = process_interlinear(report, DB, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText, ENTRIES_SCALE_FACTOR, bundles_scale)

    retVal, myData = process_interlinear_new(report, DB, configMap, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText)

    if retVal == False:
        return 

    # Check to see if there is any data to link
    if len(myData) == 0:
                                        
        report.Warning('There were no senses found for linking.')
    else:
    
        if DUMP_VOCAB_WORDS:
            
            dump_vocab(myData)

        # Show the window
        app = QApplication(sys.argv)
        
        myHeaderData = ["Link It!", 'Source Head Word', 'Source Cat.', 'Source Gloss',  
                        'Target Head Word', 'Target Cat.', 'Target Gloss']
        
        tgtLexList.sort(key=lambda HPG: (HPG.getHeadword().lower(), HPG.getPOS().lower(), HPG.getGloss()))
        window = Main(myData, myHeaderData, tgtLexList)
        
        window.show()
        app.exec_()
        
        # Update the source database with the correct links
        if window.ret_val: # True = make the changes        
            
            update_source_db(DB, report, myData, preGuidStr, senseEquivField, senseNumField)

def process_interlinear_new(report, DB, configMap, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText):
        
    save_map = {}
    processed_map = {}
    myData = []

    # Get punctuation string
    sent_punct = ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report)
    
    if not sent_punct:
        return False, myData
    
    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
        return False, myData

    discontigTypesList = ReadConfig.getConfigVal(configMap, 'SourceDiscontigousComplexTypes', report)
    if not discontigTypesList:
        discontigTypesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceDiscontigousComplexTypes', report):
        return False, myData

    discontigPOSList = ReadConfig.getConfigVal(configMap, 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories', report)
    if not discontigPOSList:
        discontigPOSList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories', report):
        return False, myData

    # Get interlinear data. A complex text object is returned.
    myText = Utils.getInterlinData(DB, report, sent_punct, interlinText.ContentsOA, typesList, discontigTypesList, discontigPOSList)
    
    # Loop through the words
    for paragraph in myText.getParagraphs():
        
        for sentence in paragraph.getSentences():
            
            for word in sentence.getWords():
                
                # Possible multiple entries if it's a compound, I think
                for eNum, entry in enumerate(word.getEntries()):
                    
                    if word.hasSenses():
                    
                        # each entry should have a sense
                        mySense = word.getSense(eNum)
                        
                        if mySense is not None:
                            
                            # If we have processed this sense already, we will just re-add it to the list
                            if mySense not in processed_map:
                                
                                if ITsString(entry.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
                                    
                                    # Get gloss
                                    srcGloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text    
                            
                                    # Get lemma & POS
                                    srcHeadWord = remove1dot1(word.getLemma(eNum))
                                    srcPOS = word.getPOS(eNum)
                                    
                                    # Create a headword-POS-gloss object and initialize a Link object with this
                                    # as the source sense info.
                                    myHPG = HPG(mySense, srcHeadWord, srcPOS, srcGloss)
                                    myLink = Link(myHPG)
                                    
                                    equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
        
                                    # equiv now holds the url to the target, see if it is valid
                                    if equiv:

                                        senseNum = DB.LexiconGetFieldText(mySense.Hvo, senseNumField)
                                        
                                        # If no sense number, assume it is 1
                                        if senseNum == None or not senseNum.isdigit():
                                            senseNum = '1'
                                        
                                        # Get the guid from the url
                                        u = equiv.index('guid')
                                        guid = equiv[u+7:u+7+36]
                                    
                                        # Get sense information for the guid, this returns None if not found
                                        tgtHPG = get_HPG_from_guid(TargetDB, guid, int(senseNum), report)
                                        
                                        # Set the target part of the Link object and add it to the list
                                        myLink.set_tgtHPG(tgtHPG)
                                        myData.append(myLink)
                                        processed_map[mySense] = myLink, None
                                        
                                    else: # no link url present
                                      
                                        if srcPOS == PROPER_NOUN_ABBREV:
                                            
                                            doFuzzyCompare = False
                                        else:
                                            doFuzzyCompare = True
                                            
                                        # Find matches for the current gloss using fuzzy compare if needed
                                        matchedSenseList = getMatchesOnGloss(srcGloss, gloss_map, save_map, doFuzzyCompare)
                                        
                                        # Process all the matches
                                        if len(matchedSenseList) > 0:
                                            
                                            matchLinkList = []
                                            
                                            for i, matchHPG in enumerate(matchedSenseList):
                                                
                                                if i == 0: # use the Link object already created
                                                    myLink.set_tgtHPG(matchHPG)
                                                    matchLink = myLink
                                                else:
                                                    matchLink = Link(myHPG, matchHPG)
                                                
                                                # See if we have an exact match
                                                if matchLink.get_srcGloss().lower() == matchLink.get_tgtGloss().lower():
                                                    
                                                    matchLink.set_initial_status(INITIAL_STATUS_EXACT_SUGGESTION)
                                                else:
                                                    matchLink.set_initial_status(INITIAL_STATUS_FUZZY_SUGGESTION)
                                                    
                                                matchLinkList.append(matchLink)
        
                                            myData.extend(matchLinkList)
                                                
                                            processed_map[mySense] = matchLink, matchLinkList
                                                
                                        # No matches
                                        else:
                                            # add a Link object that has no target information
                                            myData.append(myLink)
                                            processed_map[mySense] = myLink, None
                                            
                            else: # we've processed this sense before
                                myLink, myMatchLinkList = processed_map[mySense]
                                
                                # if there's no associated list, just append the link object
                                if myMatchLinkList == None:
                                    
                                    myData.append(myLink)
                                
                                # otherwise, we had multiple links associated with this sense, add them all to the list again
                                else:
                                    myData.extend(myMatchLinkList)
    
    return True, myData

# def process_interlinear(report, DB, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText, ENTRIES_SCALE_FACTOR, bundles_scale):
#         
#     save_map = {}
#     processed_map = {}
#     myData = []
#     warning_list = []
# 
#     ss = SegmentServices.StTextAnnotationNavigator(interlinText.ContentsOA)
#     for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
#        
#         report.ProgressUpdate(int(ENTRIES_SCALE_FACTOR)+int(prog_cnt/bundles_scale))
# 
#         if analysisOccurance.Analysis.ClassName == "PunctuationForm":
#             continue
#         if analysisOccurance.Analysis.ClassName == "WfiGloss":
#             wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
#         elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
#             wfiAnalysis = analysisOccurance.Analysis
#         # We get into this block if there are no analyses for the word or a analysis suggestion hasn't been accepted.
#         elif analysisOccurance.Analysis.ClassName == "WfiWordform":
#             outStr = ITsString(analysisOccurance.Analysis.Form.BestVernacularAlternative).Text
#             if outStr not in warning_list:
#                 report.Warning('No analysis found for the word: "'+ outStr + '". Skipping.')
#                 warning_list.append(outStr)
#             continue
#         else:
#             wfiAnalysis = None
#             
#         # Go through each morpheme in the word (i.e. bundle)
#         for bundle in wfiAnalysis.MorphBundlesOS:
#             if bundle.SenseRA and bundle.MsaRA and bundle.MorphRA and bundle.MorphRA.Owner:
#                 # Get the LexEntry object, set a sense variable
#                 e = bundle.MorphRA.Owner
#                 mySense = bundle.SenseRA
#                     
#                 # For a stem we just want the headword and it's POS
#                 if bundle.MsaRA.ClassName == 'MoStemMsa' and bundle.MorphRA:
#                     # Follow variants back to an entry with a sense
#                     e = GetEntryWithSense(e)    
#                     
#                     if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
#                         # If we have processed this sense already, we will just re-add it to the list
#                         if mySense not in processed_map:
#                             # Get gloss
#                             srcGloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
#     
#                             # Get headword and set homograph # if necessary
#                             srcHeadWord = ITsString(e.HeadWord).Text
#                             
#                             # Get the POS
#                             if bundle.MsaRA.PartOfSpeechRA:
#                                 srcPOS =  ITsString(bundle.MsaRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
#                             else:
#                                 srcPOS = 'UNK'
#                             
#                             # Create a headword-POS-gloss object and initialize a Link object with this
#                             # as the source sense info.
#                             myHPG = HPG(mySense, srcHeadWord, srcPOS, srcGloss)
#                             myLink = Link(myHPG)
#                             
#                             equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
#                             senseNum = DB.LexiconGetFieldText(mySense.Hvo, senseNumField)
# 
#                             # equiv now holds the url to the target, see if it is valid
#                             if equiv:
#                                 # If no sense number, assume it is 1
#                                 if senseNum == None or not senseNum.isdigit():
#                                     senseNum = '1'
#                                 
#                                 # Get the guid from the url
#                                 u = equiv.index('guid')
#                                 guid = equiv[u+7:u+7+36]
#                             
#                                 # Get sense information for the guid, this returns None if not found
#                                 tgtHPG = get_HPG_from_guid(TargetDB, guid, int(senseNum), report)
#                                 
#                                 # Set the target part of the Link object and add it to the list
#                                 myLink.set_tgtHPG(tgtHPG)
#                                 myData.append(myLink)
#                                 processed_map[mySense] = myLink
#                                 
#                             else: # no link url present
#                               
#                                 if myHPG.getPOS() == 'nprop':
#                                     continue
#                                   
#                                 # Find matches for the current gloss using fuzzy compare if needed
#                                 matchedSenseList = getMatchesOnGloss(srcGloss, gloss_map, save_map)
#                                 
#                                 # Process all the matches
#                                 if len(matchedSenseList) > 0:
#                                     
#                                     for i, matchHPG in enumerate(matchedSenseList):
#                                         
#                                         if i == 0: # use the Link object already created
#                                             myLink.set_tgtHPG(matchHPG)
#                                             matchLink = myLink
#                                         else:
#                                             matchLink = Link(myHPG, matchHPG)
#                                         
#                                         # See if we have an exact match
#                                         if matchLink.get_srcGloss().lower() == matchLink.get_tgtGloss().lower():
#                                             
#                                             matchLink.set_initial_status(INITIAL_STATUS_EXACT_SUGGESTION)
#                                         else:
#                                             matchLink.set_initial_status(INITIAL_STATUS_FUZZY_SUGGESTION)
# 
#                                         myData.append(matchLink)
#                                         processed_map[mySense] = matchLink
#                                         
#                                 # No matches
#                                 else:
#                                     # add a Link object that has no target information
#                                     myData.append(myLink)
#                                     processed_map[mySense] = myLink
#                                     
#                         else: # we've processed this sense before, add it to the list again
#                             myLink = processed_map[mySense]
#                             myData.append(myLink)
#     return myData

def update_source_db(DB, report, myData, preGuidStr, senseEquivField, senseNumField):        
    
    updated_senses = {}
    cnt = 0
    unlinkCount = 0
        
    # Loop through the data
    for currLink in myData:
        
        # See if we have already updated this sense
        currSense = currLink.get_srcSense()
        
        if currSense not in updated_senses:
            
            # Create a link if the user marked it for linking and we have a valid target
            # and it's not an existing linked sense in the DB where the link hasn't been changed (these are 
            # marked linkIt=True, but we don't want to re-link them even though it wouldn't hurt).
            if (currLink.linkIt == True and currLink.get_tgtHPG() != None and currLink.get_tgtHPG().getHeadword() != '') and \
               not currLink.isInitiallyUnlinkedAndTargetUnmodified():
                
                cnt += 1
                
                # Build target link from saved url path plus guid string for this target sense
                text = preGuidStr + currLink.get_tgtGuid() + '%26tag%3d'
                
                # Set the target field
                DB.LexiconSetFieldText(currSense, senseEquivField, text)
            
                # Set the sense number if necessary
                if currLink.get_tgtSenseNum() > 1:
                    numStr = str(currLink.get_tgtSenseNum())
                    DB.LexiconSetFieldText(currSense, senseNumField, numStr)
            
                updated_senses[currSense] = 1
            
            
            elif currLink.linkIt == False and currLink.isInitiallyUnlinkedAndTargetUnmodified():

                unlinkCount += 1
                
                # Clear the target field
                DB.LexiconSetFieldText(currSense, senseEquivField, '')
                DB.LexiconSetFieldText(currSense, senseNumField, '')

                updated_senses[currSense] = 1

    # Give feedback            
    if cnt == 1:
       
        report.Info('1 link created.')
    else:
        report.Info(str(cnt)+' links created.')

    if unlinkCount == 1:
       
        report.Info('1 link removed')
       
    elif unlinkCount > 1:
       
        report.Info(str(unlinkCount) + ' links removed')  
                      
def calculate_progress_stats(report, interlinText, TargetDB_tot):
            
    # count the number of "bundles" we will process for progress bar
    bundle_tot = 0
    for par in interlinText.ContentsOA.ParagraphsOS:
        for seg in par.SegmentsOS:
            bundle_tot += seg.AnalysesRS.Count
    
    # We will scale the progress indication according to the following
    # weighting factors
    # 385 units for an entry to process in the get_gloss_map function
    TIME_RATIO = 385
    # 1 unit for each fuzzy compare
    
    report.ProgressStart(100)
    
    # The time to process a bundle depends on the number of glosses (roughly total entries). 
    # This is because a fuzzy compare gets done on each target gloss for each unique bundle
    ENTRIES_SCALE_FACTOR = float(TargetDB_tot*TIME_RATIO) / float(TargetDB_tot*TIME_RATIO+bundle_tot*TargetDB_tot*1) * 100.0
    BUNDLES_SCALE_FACTOR = 100.0 - ENTRIES_SCALE_FACTOR
    
    entries_scale = int(TargetDB_tot/ENTRIES_SCALE_FACTOR)
    bundles_scale = int(bundle_tot/BUNDLES_SCALE_FACTOR)
    if entries_scale == 0:
        entries_scale = 1
    if bundles_scale == 0:
        bundles_scale = 1

    return ENTRIES_SCALE_FACTOR, bundles_scale, entries_scale

def dump_vocab(myData):
                
    # dump words with no link
    processed = {}
    fz = open("vocab_dump.txt", encoding='utf-8')
     
    # read in existing data in the file
    for i,line in enumerate(fz):
        processed[line.strip()] = 0
     
    fz.close()
     
    fz = open("vocab_dump.txt", 'w', encoding='utf-8')
     
    # print out existing words in the same order they were in the file
    for key, _ in sorted(processed.items(), key=lambda item: item[1]):
         
        fz.write(key+'\n')
    
    for link in myData:
        hpg = link.get_srcHPG()
        myHeadword = hpg.getHeadword()
        myHeadword = re.sub('\d','',myHeadword,re.A)
         
        if myHeadword not in processed and hpg.getPOS() != PROPER_NOUN_ABBREV:
    
            if link.initial_status != INITIAL_STATUS_LINKED:
                fz.write(myHeadword+'\n')
                  
            processed[myHeadword] = 1
    fz.close()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
