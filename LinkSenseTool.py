#
#   LinkSenseTool
#
#   Ron Lockwood
#   SIL International
#   7/18/15
#
#   Version 3.8.2 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#
#   Version 3.8 - 4/8/23 - Ron Lockwood
#    Fixed #397. Fixed crash when exporting 0 unlinked senses.
#
#   Version 3.7.10 - 2/24/23 - Ron Lockwood
#    Make the vocab headwords lowercase (unless they're proper nouns).
#
#   Version 3.7.9 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.8 - 1/30/23 - Ron Lockwood
#    Official support for creating a vocabulary list of unlinked senses. The tool creates an html file
#    with a table containing source headword, gloss and category plus blank cells for the target
#    language and a comment. Also below this info. is the sentence where the sense was found with the
#    word marked in bold type. A new setting for ProperNoun abbrev. added.
#
#   Version 3.7.7 - 1/18/23 - Ron Lockwood
#    Fixed bug where report was None in the do_replacements function and a warning was
#    attempted to be outputted. Have LinkSenseTool call extract_bilingual_lex with a report object.
#
#   Version 3.7.6 - 12/25/22 - Ron Lockwood
#    Added RegexFlag before re constants
#
#   Version 3.7.5 - 12/24/22 - Ron Lockwood
#    Removed defined function GetEntryWithSense which was unused.
#
#   Version 3.7.4 - 12/14/22 - Ron Lockwood
#    Don't count proper nouns as still to link if the Hide Proper Noun checkbox is checked.
#
#   Version 3.7.3 - 12/12/22 - Ron Lockwood
#    Re-read the config file before each new launch of the linker to ensure we have
#    the latest source text name. Also, put none-headword string in Utils.py
#
#   Version 3.7.2 - 12/10/22 - Ron Lockwood
#    Reworked interface to put new controls and some old on the bottom. OK & Cancel stay bottom right.
#    Fixed #308 - change font size and font family. Fixed #78 - Allow no link (called **none**) to be set.
#    Fixed #325 - allow searching by any part of the target combo box info. - headword, POS (with parens), gloss.
#    Fixed #185 - consistently hide linked rows, even those that aren't ticked, but have an identical srcHPG that is linked.
#    Fixed #335 - allow rebuilding of the bilingual lexicon after the linker closes.
#    Fixed #333 - show a status of how many senses still need to be linked.
#
#   Version 3.7.1 - 12/7/22 - Ron Lockwood
#    Fixes #91. Only make painting updates when a row's checkbox is changed.
#
#   Version 3.7 - 11/5/22 - Ron Lockwood
#    Fixes #252. The user can choose a different source text which triggers a restart
#    of the module. Added logic to detect if linking or unlinking was done. If a
#    change happened, prompt the user to save before restarting.
#
#   Version 3.6.2 - 9/3/22 - Ron Lockwood
#    Fixes #213. Show the source text name at the top of the window. 
#
#   Version 3.6.1 - 9/3/22 - Ron Lockwood
#    Fixes #233. Give errors if config file settings like source morpheme types are null.
#
#   Version 3.6 - 8/26/22 - Ron Lockwood
#    Fixes #215 Check morpheme type against guid in the object instead of
#    the analysis writing system so we aren't dependent on an English WS.
#
#   Version 3.5.4 - 7/13/22 - Ron Lockwood
#    More CloseProject() calls for FlexTools2.1.1
#
#   Version 3.5.3 - 7/8/22 - Ron Lockwood
#    Set Window Icon to be the FLExTrans Icon
#
#   Version 3.5.2 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5 - 4/2/22 - Ron Lockwood
#    Added a search box to select target words from the list box. Fixes #106.
#
#   Version 3.4.1 - 3/4/22 - Ron Lockwood
#    Give a better error than just showing the guid that wasn't found.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.1 - 3/3/22 - Ron Lockwood
#    Fixed crash when word was mapped to a target with POS not set. Bug 68.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
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
import os
import sys
import unicodedata
import xml.etree.ElementTree as ET

from fuzzywuzzy import fuzz

from System import Guid
from System import String

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFontDialog

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.DomainServices import SegmentServices

from flextoolslib import *                                                 

from flexlibs import FLExProject, AllProjectNames

import FTPaths
import ReadConfig
import Utils
import ExtractBilingualLexicon

from Linker import Ui_MainWindow

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Sense Linker Tool",
        FTM_Version    : "3.8.2",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Link source and target senses.",
        FTM_Help   : "",
        FTM_Description:  
"""
This module will create links 
in the source project to senses in the target project. It will show a window
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
is to indicate you may not want to link the two sense even though the glosses match. 
This module requires
two sense-level custom fields in your source project. They should be simple text fields.
One is to link to an entry in the target project and the other is to indicate a sense
number number in that entry. Set these in the Settings tool. 
Created links will appear in the custom field set in your settings. If the sense number
being linked to is not sense number one, the custom field for sense number set in your Settings
will be set to the corresponding sense number, otherwise it will be blank.
""" }
                 
#----------------------------------------------------------------
# Configurables:
UNLINKED_SENSE_FILENAME_PORTION = ' unlinked senses.html'

# The minimum length a word should have before doing a fuzzy compare
# otherwise an exact comparision is used
MIN_GLOSS_LEN_FOR_FUZZ = 5
# Only do a fuzzy compare if the difference in the lengths of the strings
# is less than this number
MIN_DIFF_GLOSS_LEN_FOR_FUZZ = 3
# The percentage or higher in similarity that two words must have in  
# order to be outputted as a possible match. 
FUZZ_THRESHOLD = 74

SEARCH_HERE = 'Search here'
INITIAL_STATUS_UNLINKED = 0
INITIAL_STATUS_LINKED = 1    
INITIAL_STATUS_EXACT_SUGGESTION = 2
INITIAL_STATUS_FUZZY_SUGGESTION = 3

NA_STR = 'n/a'

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
    def getLinkIt(self):
        return self.linkIt
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
    def isInitiallyLinkedAndTargetUnmodified(self):
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
    def getRowValue(self, row):
        return self.__localData[row]
    def rowCount(self, parent):
        return len(self.__localData)
    def data(self, index, role):
        row = index.row()
        myHPG = self.__localData[row]
        
        if role == QtCore.Qt.DisplayRole:
            if self.getRTL():
                value = myHPG.getHeadword() + ' (' + myHPG.getPOS() + ') ' + myHPG.getGloss()
            else:
                value = myHPG.getHeadword() + ' (' + myHPG.getPOS() + ') ' + myHPG.getGloss()
            self.__currentHPG = myHPG    
            return value
            
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        return True
            
class LinkerTable(QtCore.QAbstractTableModel):
    
    def __init__(self, myData = [[]], headerData = [], font = None, changeCallback = None, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__localData = myData
        self.__myHeaderData = headerData
        self.__selectedHPG = None
        self.__linkingChanged = False
        self.__font = font
        self.__callbackFunc = changeCallback
    def getFont(self):
        return self.__font
    def setFont(self, myFont):
        self.__font = myFont
    def didLinkingChange(self):
        return self.__linkingChanged
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

                self.__linkingChanged = True
                
                # Recalculate the senses to link 
                self.__callbackFunc()
                
                return self.__selectedHPG.getHeadword()
        
        if role == QtCore.Qt.FontRole:
            
            return self.__font
        
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
                
                initiallyLinkedUnmodifiedSense = locData.isInitiallyLinkedAndTargetUnmodified()
                
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

                # This causes continual repainting and high processor use, moved it to SetData()
                #self.dataChanged.emit(index, index)
                
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
            
            self.__linkingChanged = True
            
            row = index.row()
            
            if value == QtCore.Qt.Checked: 
                
                self.__localData[row].linkIt = True
                self.__localData[row].modified = True
            else:
                self.__localData[row].linkIt = False
                self.__localData[row].modified = True
            
            # Repaint columns 0,4-6 (link, target head-word, cat, gloss) when the checkbox is changed.
            # Do this for all rows to display rows that are linked to the link object
            for myCol in [0,4,5,6]:
                
                for row in range(0,len(self.__localData)):
                    newindex = self.index(row, myCol)    
                    self.dataChanged.emit(newindex, newindex)
            
            # Recalculate the senses to link 
            self.__callbackFunc()
            
        return True
            
class Main(QMainWindow):

    def __init__(self, myData, headerData, comboData, sourceTextName, DB, report, configMap, properNounAbbr):
        
        QMainWindow.__init__(self)
        self.showOnlyUnlinked = False
        self.hideProperNouns = False
        self.exportUnlinked = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        myFont = self.ui.tableView.font()
        self.__model = LinkerTable(myData, headerData, myFont, self.calculateRemainingLinks)
        self.__fullData = myData
        self.ui.tableView.setModel(self.__model)
        self.__comboData = comboData
        self.__combo_model = LinkerCombo(comboData)
        self.ui.targetLexCombo.setModel(self.__combo_model)
        self.__report = report
        self.__configMap = configMap
        self.ret_val = 0
        self.cols = 7
        self.restartLinker = False
        self.properNounAbbr = properNounAbbr
        
        # Set the combo box to the 2nd element, since the first one is **none**
        if len(comboData) > 1:
            
            self.ui.targetLexCombo.setCurrentIndex(1)
            
        # load the source text list
        Utils.loadSourceTextList(self.ui.SourceTextCombo, DB, sourceTextName)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.InitRebuildBilingCheckBox()
        
        self.ui.searchTargetEdit.setText(SEARCH_HERE)
        
        self.ui.targetLexCombo.currentIndexChanged.connect(self.ComboClicked)
        self.ui.ShowOnlyUnlinkedCheckBox.clicked.connect(self.ShowOnlyUnlinkedClicked)
        self.ui.HideProperNounsCheckBox.clicked.connect(self.HideProperNounsClicked)
        self.ui.exportUnlinkedCheckBox.clicked.connect(self.exportUnlinkedClicked)
        self.ui.searchTargetEdit.textChanged.connect(self.SearchTargetChanged)
        self.ui.searchTargetEdit.cursorPositionChanged.connect(self.SearchTargetClicked)
        self.ui.SourceTextCombo.activated.connect(self.sourceTextComboChanged)
        self.ui.FontButton.clicked.connect(self.FontClicked)
        self.ui.ZoomIncrease.clicked.connect(self.ZoomIncreaseClicked)
        self.ui.ZoomDecrease.clicked.connect(self.ZoomDecreaseClicked)
        self.ui.RebuildBilingCheckBox.clicked.connect(self.RebuildBilingChecked)
        self.ui.SearchAnythingCheckBox.clicked.connect(self.SearchAnythingChecked)
        self.ComboClicked()
        
        myHPG = self.__combo_model.getCurrentHPG()
        myHeadword = myHPG.getHeadword()
        
        # Check for right to left data and set the combobox direction if needed
        for i in range(0, len(myHeadword)):
            if unicodedata.bidirectional(myHeadword[i]) in ('R', 'AL'):
                self.ui.targetLexCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                #self.ui.searchTargetEdit.setAlignment(QtCore.Qt.AlignRight)
                self.__combo_model.setRTL(True)
                break
    
        # Figure out how many senses are unlinked so we can show the user
        self.calculateRemainingLinks()
        
    def InitRebuildBilingCheckBox(self):
        
        self.ui.RebuildBilingCheckBox.setCheckState(QtCore.Qt.Checked)
        
        val = ReadConfig.getConfigVal(self.__configMap, ReadConfig.REBUILD_BILING_LEX_BY_DEFAULT, report=None, giveError=False)
        
        if val:
            if val == 'n':
                
                self.ui.RebuildBilingCheckBox.setCheckState(QtCore.Qt.Unchecked)
                
        self.rebuildBiling = self.ui.RebuildBilingCheckBox.isChecked()
        
    def RebuildBilingChecked(self):
        
        self.rebuildBiling = self.ui.RebuildBilingCheckBox.isChecked()
        
    def calculateRemainingLinks(self):
        
        count = 0
        uniqueSrcHPGMap = {}
        
        # Build a map that just has unique senses
        for linkObj in self.__fullData:
            
            mySrcHPG = linkObj.get_srcHPG()
            
            if mySrcHPG not in uniqueSrcHPGMap:
                
                # For each key add a list of one or more True or False values that indicate if it's been linked
                uniqueSrcHPGMap[mySrcHPG] = [linkObj.getLinkIt()]
            else:
                uniqueSrcHPGMap[mySrcHPG].append(linkObj.getLinkIt())
                
        # Now go through the unique senses and if we have no True's for a sense, increment the to link count
        for mySrcHPG, boolList in uniqueSrcHPGMap.items():
            
            if self.hideProperNouns:
                    
                if mySrcHPG.getPOS() == self.properNounAbbr:
                    continue
                        
            for myBool in boolList:
                
                if myBool:
                    break
                
            if not myBool:
                count += 1
                    
        self.ui.SensesRemainingLabel.setText(str(count))
        
    def causeRepaint(self):
        # crude way to cause a repaint
        tv = self.ui.tableView
        tv.setGeometry(tv.x()+1,tv.y()+1,tv.width(),tv.height()+1)
        tv.setGeometry(tv.x()-1,tv.y()-1,tv.width(),tv.height()-1)

    def FontClicked(self):
        (font, ret) = QFontDialog.getFont()
        if ret:
            myFont = self.__model.getFont()
            myFont.setFamily(font.family())
            self.ui.FontNameLabel.setText(font.family())

    def ZoomIncreaseClicked(self):
        myFont = self.__model.getFont()
        mySize = myFont.pointSizeF()
        mySize = mySize * 1.125
        myFont.setPointSizeF(mySize)
        self.__model.setFont(myFont)
        self.causeRepaint()
        
    def ZoomDecreaseClicked(self):
        myFont = self.__model.getFont()
        mySize = myFont.pointSizeF()
        mySize = mySize * .889
        myFont.setPointSizeF(mySize)
        self.__model.setFont(myFont)
        self.causeRepaint()
        
    def sourceTextComboChanged(self):
        
        self.restartLinker = True
        
        # Update the source text setting in the config file
        ReadConfig.writeConfigValue(self.__report, ReadConfig.SOURCE_TEXT_NAME, self.ui.SourceTextCombo.currentText())
        
        # Set the global variable
        FTPaths.CURRENT_SRC_TEXT = self.ui.SourceTextCombo.currentText()
        
        # Check if the user did some linking or unlinking
        if self.__model.didLinkingChange():
            
            # Check if the user wants to save changes
            if QMessageBox.question(self, 'Save Changes', "Do you want to save your changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
        
                self.ret_val = 1
        
        # Have FlexTools refresh the status bar
        refreshStatusbar()

        # Close the tool and it will restart
        self.close()
    
    def SearchAnythingChecked(self):
        
        if self.ui.SearchAnythingCheckBox.isChecked():
            
            self.__old_combo_model = self.__combo_model
            
        else:
            self.__combo_model = self.__old_combo_model
            self.ui.targetLexCombo.setModel(self.__combo_model)

            # Set the combo box to the 2nd element, since the first one is **none**
            if len(self.__comboData) > 1:
                
                self.ui.targetLexCombo.setCurrentIndex(1)


    def buildSearchResults(self, searchText):
        
        newList = []
        
        if searchText:
            
            myREobj = re.compile(unicodedata.normalize('NFD', re.escape(searchText)))
            
            for hpg in self.__comboData[1:]: # skip the **none** target
                
                # Search for match in headword, POS including parens, or gloss
                if myREobj.search(hpg.getHeadword()) or myREobj.search('('+hpg.getPOS()+')') or myREobj.search(hpg.getGloss()):
                    
                    newList.append(hpg)
                    
            if len(newList) > 0:
                                    
                self.__combo_model = LinkerCombo(newList)
                self.ui.targetLexCombo.setModel(self.__combo_model)

    def findRow(self, searchText):
        
        found = False
        
        # Look for a match to the beginning of a headword
        for i in range(0, self.__combo_model.rowCount(None)):
            
            if re.match(unicodedata.normalize('NFD', re.escape(searchText)) + r'.*', self.__combo_model.getRowValue(i).getHeadword(), flags=re.RegexFlag.IGNORECASE):
                found = True
                break
        
        if found:
            return i
        
        return -1
        
    def SearchTargetChanged(self):
        
        # Do a filter based on what was typed which can match anything
        if self.ui.SearchAnythingCheckBox.isChecked():
            
            self.buildSearchResults(self.ui.searchTargetEdit.text())
            
        else:
            
            foundRow = self.findRow(self.ui.searchTargetEdit.text())
            
            if foundRow > 0:
                self.ui.targetLexCombo.setCurrentIndex(foundRow)
            
    def SearchTargetClicked(self):
        
        # Blank out the search text box if the user hasn't typed anything yet
        if self.ui.searchTargetEdit.text() == SEARCH_HERE:
            
            self.ui.searchTargetEdit.setText('')
    
    def positionControl(self, myControl, x, y):
        
        myControl.setGeometry(x, y, myControl.width(), myControl.height())
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        
        # Stretch the table view to fit
        self.ui.tableView.setGeometry(10, 50, self.width() - 20, self.height() - self.ui.OKButton.height() - 85)
        
        # Move the OK and Cancel buttons up and down as the window gets resized
        x = 10
        if x < 0:
            x = 0
        
        self.positionControl(self.ui.OKButton, x, self.ui.tableView.height() + 60)
        self.positionControl(self.ui.CancelButton, x + self.ui.OKButton.width() + 10, self.ui.tableView.height() + 60)
        
        # Set position of other controls all the same height and 10 pixels between each other
        startX = self.ui.CancelButton.x() + self.ui.CancelButton.width() + 10
        
        # Make a list of all the controls that need to move up or down
        controlList = [self.ui.ShowOnlyUnlinkedCheckBox, self.ui.HideProperNounsCheckBox, self.ui.ZoomLabel, self.ui.ZoomIncrease, self.ui.ZoomDecrease, 
                       self.ui.FontButton, self.ui.FontNameLabel, self.ui.RebuildBilingCheckBox, self.ui.exportUnlinkedCheckBox]

        for myControl in controlList:
            
            self.positionControl(myControl, startX, self.ui.OKButton.y())
            startX += myControl.width() + 10
        
        self.positionControl(self.ui.SensesToLinkLabel, 10, self.ui.OKButton.y() + 27)
        self.positionControl(self.ui.SensesRemainingLabel, self.ui.SensesToLinkLabel.x() + self.ui.SensesToLinkLabel.width() + 5, self.ui.OKButton.y() + 27)
        
        
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
        
    def exportUnlinkedClicked(self):
        if self.ui.exportUnlinkedCheckBox.isChecked():
            self.exportUnlinked = True
        else:
            self.exportUnlinked = False
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
            srcHPGtoLinkItMap = {}
            
            # Create a map of unique srcHPGs to LinkIt, we override the map if a LinkIt is true
            # for any of the identical srcHPGs. This helps below to see if any identical srcHPGs have been linked
            for myLink in self.__fullData:
                
                if myLink.get_srcHPG() not in srcHPGtoLinkItMap:
                    
                    srcHPGtoLinkItMap[myLink.get_srcHPG()] = myLink.getLinkIt() 
                else:
                    if myLink.getLinkIt():
                        
                        srcHPGtoLinkItMap[myLink.get_srcHPG()] = True
                
            for myLink in self.__fullData:
                
                keepIt = False
                
                if self.showOnlyUnlinked:
                    
                    # if none of possible identical srcHPGs has been linked, add this one
                    if not srcHPGtoLinkItMap[myLink.get_srcHPG()]:
                        
                        keepIt = True
                else:
                    keepIt = True
                        
                if self.hideProperNouns:
                    
                    if keepIt == True:
                    
                        if myLink.get_srcPOS() != self.properNounAbbr:
                            
                            keepIt = True
                        else:
                            keepIt = False
                if keepIt:
                        
                    filteredData.append(myLink)
                    
            self.__model.setInternalData(filteredData)
            
        self.__model.endResetModel();
        self.rows = len(self.__model.getInternalData())

        self.causeRepaint()
        
        self.ui.tableView.update()
        self.__model.resetInternalData()
        
        # Recalculate links since we won't count prop nouns if the Hide prop nouns checkboxe is checked.
        self.calculateRemainingLinks()
        
        return
    
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
        if e.LexemeFormOA and e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and Utils.morphTypeMap[e.LexemeFormOA.MorphTypeRA.Guid.ToString()] in targetMorphNames:
        
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
        report.Error(f'Invalid guid or guid not found in target database. Guid: {myGuid}. You can filter for ' +
                       'this value in your target equivalent custom field to find the source entry with the problem.')
        return ret
    
    if targetEntry:
        
        lem = ITsString(targetEntry.HeadWord).Text

        # Make the lemma in the form x.x (but remove it 1.1)
        lem = fixupLemma(lem, targetEntry, senseNum)
        
        # Get the POS abbreviation for the target sense, assuming we have a stem
        if senseNum <= len(targetEntry.SensesOS.ToArray()):
            
            targetSense = targetEntry.SensesOS.ToArray()[senseNum-1]
            if targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                
                # verify PartOfSpeechRA is valid, if not, set the POS unknown
                if targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA == None:
                    POS = 'UNK'
                else:
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

def process_interlinear(report, DB, configMap, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText, properNounAbbr):
        
    save_map = {}
    processed_map = {}
    myData = []

    # Get punctuation string
    sent_punct = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)
    
    if not sent_punct:
        return False, myData, processed_map
    
    typesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report):
        return False, myData, processed_map

    discontigTypesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report)
    if not discontigTypesList:
        discontigTypesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report):
        return False, myData, processed_map

    discontigPOSList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report)
    if not discontigPOSList:
        discontigPOSList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report):
        return False, myData, processed_map

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
                                
                                # Lookup the morphType via hard-coded guid
                                morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
                                morphType = Utils.morphTypeMap[morphGuidStr]
            
                                if morphType in sourceMorphNames:
                                    
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
                                        
                                        # handle sense mapped intentionally to nothing.
                                        if equiv == Utils.NONE_HEADWORD:
                                            
                                            tgtHPG = HPG(Sense=None, Headword=Utils.NONE_HEADWORD, POS=NA_STR, Gloss=NA_STR)
                                            
                                        else:
                                        
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
                                        processed_map[mySense] = myLink, None, sentence
                                        
                                    else: # no link url present
                                      
                                        if srcPOS == properNounAbbr:
                                            
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
                                                
                                            processed_map[mySense] = matchLink, matchLinkList, sentence
                                                
                                        # No matches
                                        else:
                                            # add a Link object that has no target information
                                            myData.append(myLink)
                                            processed_map[mySense] = myLink, None, sentence
                                            
                            else: # we've processed this sense before
                                myLink, myMatchLinkList, _ = processed_map[mySense] # _ for sent which we don't need
                                
                                # if there's no associated list, just append the link object
                                if myMatchLinkList == None:
                                    
                                    myData.append(myLink)
                                
                                # otherwise, we had multiple links associated with this sense, add them all to the list again
                                else:
                                    myData.extend(myMatchLinkList)
    
    return True, myData, processed_map

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
               not currLink.isInitiallyLinkedAndTargetUnmodified():
                
                cnt += 1
                
                # Handle mapping to none
                headWord = currLink.get_tgtHPG().getHeadword()
                
                if headWord == Utils.NONE_HEADWORD:
                    
                    text = headWord
                else:
                    # Build target link from saved url path plus guid string for this target sense
                    text = preGuidStr + currLink.get_tgtGuid() + '%26tag%3d'
                
                # Set the target field
                DB.LexiconSetFieldText(currSense, senseEquivField, text)
            
                # Set the sense number if necessary
                if currLink.get_tgtSenseNum() > 1:
                    numStr = str(currLink.get_tgtSenseNum())
                    DB.LexiconSetFieldText(currSense, senseNumField, numStr)
            
                updated_senses[currSense] = 1
            
            # Unlink this sense
            elif currLink.linkIt == False and currLink.isInitiallyLinkedAndTargetUnmodified():

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

def containsWord(sentHPGlist, word):
    
    found = False
    
    for sentHPG in sentHPGlist:
        
        if sentHPG.getSense() == word.getSense(0): # TODO: compounds with mult. senses?
            
            found = True
            break
        
    return found

def outputHtmlSentRow(tableObj, outSent, sentHPGlist, headerRow):
    
    fullSent = '<td>'
    
    for word in outSent.getWords():
        
        surfaceForm = word.getSurfaceForm()
        
        # If this is one of the key words going into the table, make it bold
        if containsWord(sentHPGlist, word):
            
            surfaceForm = '<b>' + surfaceForm + '</b>'
            
        fullSent += word.getInitialPunc() + surfaceForm + word.getFinalPunc()
        
    fullSent += '</td>'
    
    # Make a row, add it to the table    
    row = ET.SubElement(tableObj, 'tr')
    
    # Convert the full sentence html to a td element
    sentCell = ET.fromstring(fullSent, ET.XMLParser(encoding='utf-8'))
    
    # Make the sentence cell span all the rest of the columns
    sentCell.attrib['colspan'] = str(len(headerRow))

    # Add the sentence cell to the row.
    row.append(sentCell)
    
def outputHtmlWordRow(tableObj, srcHPG, properNounAbbr):
    
    # Make a row, add it to the table and add various pieces of data for the cells
    row = ET.SubElement(tableObj, 'tr')
    
    # Remove the X.X from the word
    headWord = re.sub(r'\d+\.\d+', '', srcHPG.getHeadword(), flags=re.RegexFlag.A)
    
    # Make it lowercase if not a proper noun
    if srcHPG.getPOS() != properNounAbbr:
        
        headWord = headWord.lower()
        
    ET.SubElement(row, 'td').text = headWord
    ET.SubElement(row, 'td').text = srcHPG.getGloss()
    ET.SubElement(row, 'td').text = srcHPG.getPOS()
    ET.SubElement(row, 'td').text = '' # target
    ET.SubElement(row, 'td').text = '' # Comment

def addIntroHtmlStuff(tableObj, srcDBname, tgtDBname):
    
    # Make a row, add it to the table and add header cells
    row = ET.SubElement(tableObj, 'tr')
    ET.SubElement(row, 'th').text = srcDBname
    ET.SubElement(row, 'th').text = 'Gloss'
    ET.SubElement(row, 'th').text = 'Cat.'
    ET.SubElement(row, 'th').text = tgtDBname
    ET.SubElement(row, 'th').text = 'Comment'
    
    return row

def getFirstOccurringSent(myHPG, processed_map):

    mySense = myHPG.getSense()
    
    # The processed map from the process_interlinear function already has the first sentence
    # where this sense occurred.
    if mySense in processed_map:
        
        # The 3rd part of the map is the sentence that goes to this sense
        return processed_map[mySense][2] 
    
    return None
        
def dumpVocab(myData, processed_map, srcDBname, tgtDBname, sourceTextName, report, hideProperNouns, properNounAbbr):
                
    doneMap = {}
    wordSentList = []
    cnt = 0
                
    # Loop through the data
    for currLink in myData:
        
        # See if we have already updated this sense
        srcHPG = currLink.get_srcHPG()
        
        if srcHPG not in doneMap:
            
            # This sense is not being linked so we'll be adding to the vocab document.
            if not currLink.linkIt:
                
                # Don't process a proper noun if the user had them hidden
                if not (hideProperNouns and srcHPG.getPOS() == properNounAbbr):
                
                    mySent = getFirstOccurringSent(currLink.get_srcHPG(), processed_map)
                    
                    if mySent == None:
                        
                        continue
                    
                    wordSentList.append((srcHPG, mySent))
                    doneMap[srcHPG] = 1
                    cnt += 1
                
    missingWordsForSentList = []
    prevSent = None
    
    tableObj = ET.Element("table")
    
    # Check if we have RTL data, if so, make the table RTL
    if Utils.hasRtl(srcHPG.getHeadword()):
        
        tableObj.attrib['dir'] = 'rtl'
    
    headerRow = addIntroHtmlStuff(tableObj, srcDBname, tgtDBname)
    
    # Loop through unlinked words
    for i, (srcHPG, mySent) in enumerate(wordSentList):
        
        # if we are on a different sentence, put out the sentence row of the table
        if mySent != prevSent and i != 0:
        
            outputHtmlSentRow(tableObj, prevSent, missingWordsForSentList, headerRow)
            
            missingWordsForSentList = []
        
        # Output the word row of the table
        outputHtmlWordRow(tableObj, srcHPG, properNounAbbr) 
        
        # add word to sent_word_list
        missingWordsForSentList.append(srcHPG)
        
        prevSent = mySent
        
    # Put out the last sentence row
    if prevSent:
    
        outputHtmlSentRow(tableObj, prevSent, missingWordsForSentList, headerRow)

        # Get the output folder (parent of the config path folder + output)
        outputFolder = FTPaths.OUTPUT_DIR
        
        # Convert source text name to valid file name characters (by substituting _ for invalid ones)
        htmlFileName = "".join([x if (x.isalnum() or x in "._- ") else "_" for x in sourceTextName])
        #htmlFileName = "".join(x for x in sourceTextName if (x.isalnum() or x in "._- ") else '_')
        
        # Build the path with the source text name
        htmlFileName = os.path.join(outputFolder, htmlFileName + UNLINKED_SENSE_FILENAME_PORTION)
        
        # Write the html file
        etObj = ET.ElementTree(tableObj)
        
        try:
            etObj.write(htmlFileName)
            
        except PermissionError:
            report.Error(f"Permission error writing {htmlFileName}. Perhaps the file is in use in another program?")
            return
        
        except:
            report.Error(f"Error writing {htmlFileName}.")
            return
        
        # Report how many words were dumped
        report.Info(f"{str(cnt)} words written to the file: {os.path.basename(htmlFileName)}. You'll find it in the Output folder.")

    else:
        report.Info(f"No unlinked words. Nothing exported.")

RESTART_MODULE = 0
ERROR_HAPPENED = 1
NO_ERRORS = 2
REBUILD_BILING = 3

def MainFunction(DB, report, modify=False):

    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    retVal = RESTART_MODULE
    
    # Have a loop of re-running this module so that when the user changes to a different text, the window restarts with the new info. loaded
    while retVal == RESTART_MODULE:
        
        # Read the configuration file which we assume is in the current directory.
        configMap = ReadConfig.readConfig(report)
        if not configMap:
            return
    
        retVal = RunModule(DB, report, configMap)
        
    if retVal == REBUILD_BILING:
        
        # Extract the bilingual lexicon. Force a complete rebuild instead of using the cache.        
        error_list = ExtractBilingualLexicon.extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=False)
        
        # output info, warnings, errors
        for msg in error_list:
            
            # msg is a pair -- string & code
            if msg[1] == 0:
                report.Info(msg[0])
            elif msg[1] == 1:
                report.Warning(msg[0])
            else: # error=2
                report.Error(msg[0])
        
        
def RunModule(DB, report, configMap):
        
    haveConfigError = False
    
    # Get need configuration file properties
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    linkField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    numField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, report)
    targetMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)

    if not sourceTextName:
        
        report.Error('No Source Text Name has been set. Please go to Settings and fix this.')
        haveConfigError = True
    
    if not linkField:
        
        report.Error('No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.')
        haveConfigError = True
    
    if not numField:
        
        report.Error('No Source Custom Field for Sense Number has been set. Please go to Settings and fix this.')
        haveConfigError = True
    
    # Give an error if there are no morphnames
    if not sourceMorphNames or len(sourceMorphNames) < 1:
        
        report.Error('No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.')
        haveConfigError = True
    
    if not targetMorphNames or len(targetMorphNames) < 1:
        
        report.Error('No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.')
        haveConfigError = True
    
    if haveConfigError:
        return ERROR_HAPPENED
    
    # Find the desired text
    foundText = False
    for interlinText in DB.ObjectsIn(ITextRepository):
        if sourceTextName == ITsString(interlinText.Name.BestAnalysisAlternative).Text:
            foundText = True
            break;
        
    if not foundText:
        report.Error('The text named: '+sourceTextName+' not found.')
        return ERROR_HAPPENED

    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    senseNumField = DB.LexiconGetSenseCustomFieldNamed(numField)
    
    if not (senseEquivField):
        report.Error(linkField + " field doesn't exist. Please read the instructions.")

    if not (senseNumField):
        report.Error(numField + " field doesn't exist. Please read the instructions.")

    if not (senseEquivField and senseNumField):
        return ERROR_HAPPENED

    TargetDB = FLExProject()

    # Open the target database
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
    if not targetProj:
        return ERROR_HAPPENED
    
    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():
        report.Error('The Target Database does not exist. Please check the configuration file.')
        return ERROR_HAPPENED

    report.Info('Opening: '+targetProj+' as the target database.')

    try:
        TargetDB.OpenProject(targetProj, True)
    except: #FDA_DatabaseError, e:
        report.Error('Failed to open the target database.')
        raise

    report.Info("Starting " + docs[FTM_Name] + " for text: " + sourceTextName + ".")

    preGuidStr = 'silfw://localhost/link?database%3d'
    preGuidStr += re.sub('\s','+', targetProj)
    preGuidStr += '%26tool%3dlexiconEdit%26guid%3d'
     
    gloss_map = {}
    tgtLexList = []

    TargetDB_tot = TargetDB.LexiconNumberOfEntries() 

    # Get the proper noun abbreviation
    properNounAbbr = ReadConfig.getConfigVal(configMap, ReadConfig.PROPER_NOUN_CATEGORY, report)
    
    if properNounAbbr is None:
        
        properNounAbbr = ''
    
    # TODO: rework how we do the progress indicator since we now use the Utils.getInterlinData function
    ENTRIES_SCALE_FACTOR, bundles_scale, entries_scale = calculate_progress_stats(report, interlinText, TargetDB_tot)

    # Create a map of glosses to target senses and their number and a list of target lexical senses
    if not get_gloss_map_and_tgtLexList(TargetDB, report, gloss_map, targetMorphNames, tgtLexList, entries_scale):
        TargetDB.CloseProject()
        return ERROR_HAPPENED

    # Go through the interlinear words
    retVal, myData, processed_map = process_interlinear(report, DB, configMap, senseEquivField, senseNumField, sourceMorphNames, TargetDB, gloss_map, interlinText, properNounAbbr)

    if retVal == False:
        return ERROR_HAPPENED 

    # Check to see if there is any data to link
    if len(myData) == 0:
                                        
        report.Warning('There were no senses found for linking.')
    else:
    
        # Show the window
        app = QApplication(sys.argv)
        
        myHeaderData = ["Link It!", 'Source Head Word', 'Source Cat.', 'Source Gloss',  
                        'Target Head Word', 'Target Cat.', 'Target Gloss']
        
        tgtLexList.sort(key=lambda HPG: (HPG.getHeadword().lower(), HPG.getPOS().lower(), HPG.getGloss()))
        
        # Create a special HPG for mapping to none, i.e. the sense will not be mapped to anything
        noneHPG = HPG(Sense=None, Headword=Utils.NONE_HEADWORD, POS=NA_STR, Gloss=NA_STR)
        tgtLexList.insert(0, noneHPG)
        
        window = Main(myData, myHeaderData, tgtLexList, sourceTextName, DB, report, configMap, properNounAbbr)
        
        window.show()
        app.exec_()
        
        # Update the source database with the correct links
        if window.ret_val: # True = make the changes        
            
            update_source_db(DB, report, myData, preGuidStr, senseEquivField, senseNumField)

            # Dump linked senses if the user wants to
            if window.exportUnlinked:
                
                dumpVocab(myData, processed_map, DB.ProjectName(), targetProj, sourceTextName, report, window.hideProperNouns, properNounAbbr)
    
        # If the user changed the source text combo, the restart member is set to True
        if window.restartLinker:
            
            TargetDB.CloseProject()
            return RESTART_MODULE
        
        elif window.rebuildBiling:
            
            TargetDB.CloseProject()
            return REBUILD_BILING
    
    TargetDB.CloseProject()
    
    return NO_ERRORS

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
