#
#   LinkSenseTool
#
#   Ron Lockwood
#   SIL International
#   7/18/15
#
#   Version 3.13.5 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.4 - 4/1/25 - Ron Lockwood
#    Refactor the process interlinear function to make it easier to read.
#
#   Version 3.13.3 - 3/24/25 - Ron Lockwood
#    Fixes #952. Don't try to make matches on glosses that are *** (missing in FLEx).
#
#   Version 3.13.2 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.7 - 3/2/25 - Ron Lockwood
#    Fixes #914. Set the morphtype to be from the analysis writing system instead of English.
#    This is needed now that we let non-English morphtype names be used in the settings.
#
#   Version 3.12.6 - 1/10/25 - Ron Lockwood
#    Fixes #840. Show the waitcursor for 3 seconds before closing the window if 
#    the users wants to rebuild the bilingual lexicon.
#
#   Version 3.12.5 - 1/3/25 - Ron Lockwood
#    Fixes #696. Scroll to the top of the table after filtering.
#
#   Version 3.12.4 - 12/30/24 - Ron Lockwood
#    Move New Entry Dialog to its own file. Support cluster projects.
#
#   Version 3.12.3 - 12/13/24 - Ron Lockwood
#    Suppress empty gloss warnings after a certain number. 
#
#   Version 3.12.2 - 11/28/24 - Ron Lockwood
#    New feature - Add a target entry from the Linker. 
#    Click a button to get an Add Entry dialog, fill out the info., the entry gets added to the db
#    and the new sense gets added to the target sense list and is selected.
#
#   Version 3.12.1 - 11/13/24 - Ron Lockwood
#    Fixes #806. Use proper placeholder text for the search box.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.2 - 10/12/24 - Ron Lockwood
#    Fixes #762. Allow target words with no gloss or blank POS to be in the target word
#    drop-down list.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.7 - 3/20/24 - Ron Lockwood
#    Refactoring to put changes to allow get interlinear parameter changes to all be in Utils
#
#   Version 3.10.6 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10.5 - 3/8/24 - Ron Lockwood
#    Fixes #578. If a change was made in the linking and the user clicks cancel or the 
#    red X, prompt them to see if they want to save the changes.
#
#   Version 3.10.4 - 2/29/24 - Ron Lockwood
#    Fixes #571. Setting to determine if filter by all fields is checked.
#
#   Version 3.10.3 - 1/18/24 - Ron Lockwood
#    Fixes #550. Handle a target word that doesn't have a category yet assigned.
#
#   Version 3.10.2 - 1/8/24 - Ron Lockwood
#    Fixes #537. Don't do gloss matching for a gloss that comes back from FLEx as ***.
#
#   Version 3.10.1 - 1/6/24 - Ron Lockwood
#    Fixes #499. Only rebuild the bilingual lexicon when OK is clicked.
#    Fixes #500. Sleep for 3 seconds before rebuilding the bilingual lexicon to let FLEx write data.
#
#   Version 3.10 - 1/6/24 - Ron Lockwood
#    Output the target DB name in the sense link text.
#
#   Version 3.9.8 - 12/26/23 - Ron Lockwood
#    Fixes #501. Fixed typo that returned source headword instead of source gloss.
#
#   Version 3.9.7 - 8/18/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.6 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.5 - 7/22/23 - Ron Lockwood
#    Writing **None** wasn't being handled.
#
#   Version 3.9.4 - 7/17/23 - Ron Lockwood
#    Fixes #470. Re-write entry urls as sense urls when loading the sense linker. 
#    Also clear the sense num field for such entries.
#
#   Version 3.9.3 - 7/17/23 - Ron Lockwood
#    Fixes #66. Use human-readable hyperlinks in the target equivalent custom field.
#
#   Version 3.9.2 - 7/4/23 - Ron Lockwood
#    Don't give an error if the sense custom field link setting is not there.
#
#   Version 3.9.1 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.9 - 6/19/23 - Ron Lockwood
#    Fixes #440. Don't capitalize source headwords if they aren't capitalized in the entry.
#
#   Version 3.8.5 - 5/5/23 - Ron Lockwood
#    Add a column to the table to show the verse number if it precedes a word. To do this a new class was added
#    which encapsulates the Link class and adds the verse number attribute.
#
#   Version 3.8.4 - 4/27/23 - Ron Lockwood
#    Fixes #363. Reworked the logic to get the interlinear text information first, then if there are
#    no senses to process, exit. Also do the progress indicator 3 times, once for getting interlinear data, once
#    for the gloss map and once for the building of the linking objects.
#
#   Version 3.8.3 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names.
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
#   earlier version history removed on 1/10/25
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
import time

from fuzzywuzzy import fuzz

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QFontDialog

from SIL.LCModel import ( # type: ignore
    IMoStemMsa,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore     
from flextoolslib import *                                                 
from flexlibs import FLExProject, AllProjectNames

import InterlinData
import FTPaths
import Mixpanel
import ReadConfig
import Utils
import ExtractBilingualLexicon
import NewEntryDlg

from Linker import Ui_SenseLinkerWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'LinkSenseTool'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'Linker', 'NewEntryDlg', 'NewEntry', 'ExtractBilingualLexicon', 'TextClasses', 'InterlinData'] 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Sense Linker Tool",
        FTM_Version    : "3.13.5",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("LinkSenseTool", "Link source and target senses."),
        FTM_Help       : "",
        FTM_Description: _translate("LinkSenseTool", 
"""This module will create links 
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
a sense-level custom field in your source project. It should be simple text field.
The purpose of the custom field is to hold the link to a sense in the target project.
Set which custom field is used for linking in the settings.""")}
                 
app.quit()
del app

#----------------------------------------------------------------
# Configurables:
UNLINKED_SENSE_FILENAME_PORTION = ' unlinked senses.html'

MAX_GLOSS_WARNINGS = 10

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
# Column numbers
COL_LINK_IT        = 0
COL_VERSE_NUM      = 1
COL_SRC_HEADWORD   = 2
COL_SRC_POS        = 3
COL_SRC_GLOSS      = 4
COL_TGT_HEADWORD   = 5
COL_TGT_POS        = 6
COL_TGT_GLOSS      = 7

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

# parent class to Link that adds verse number information
class LinkerRow(object):
    def __init__(self):
        self.__verseNum = ''
        self.__linkObj = None
    def setVerseNum(self, word):
        self.__verseNum = word.getVerseNum()
    def getVerseNum(self):
        return self.__verseNum
    def setLinkObject(self, myObj):
        self.__linkObj = myObj
    def getDataByColumn(self, col):
        ret =''
        if col > COL_LINK_IT and col <= COL_SRC_GLOSS:
            if col == COL_VERSE_NUM:
                ret = self.getVerseNum()
            if col == COL_SRC_HEADWORD:
                ret = self.getSrcHPG().getHeadword()
            elif col == COL_SRC_POS:
                ret = self.getSrcHPG().getPOS()
            elif col == COL_SRC_GLOSS:
                ret = self.getSrcHPG().getGloss()
                
        elif col >= COL_TGT_HEADWORD and col <= COL_TGT_GLOSS:
            # columns 4-6 need to be blank if there is no tgtHPG or we unchecked the linkIt box and we have a 
            # non-suggested link. This is just extra visual feedback that we will do nothing when OK is clicked.
            if self.getTgtHPG() == None or (self.getLinkIt() == False and not self.isSuggestion()):
                ret = ''   
            elif col == COL_TGT_HEADWORD:
                ret = self.getTgtHPG().getHeadword()
            elif col == COL_TGT_POS:
                ret = self.getTgtHPG().getPOS()
            elif col == COL_TGT_GLOSS:
                ret = self.getTgtHPG().getGloss()
        return ret

    # stubs for Link object calls
    def getModified(self):
        return self.__linkObj.getModified()
    def setModified(self, myBool):
        self.__linkObj.setModified(myBool)
    def getTgtModified(self):
        return self.__linkObj.getTgtModified()
    def setTgtModified(self, myBool):
        self.__linkObj.setTgtModified(myBool)
    def getLinkIt(self):
        return self.__linkObj.getLinkIt()
    def setLinkIt(self, myBool):
        self.__linkObj.setLinkIt(myBool)
    def getSrcHPG(self):
        return self.__linkObj.getSrcHPG()
    def getTgtHPG(self):
        return self.__linkObj.getTgtHPG()
    def getSrcPOS(self):
        return self.__linkObj.getSrcPOS()
    def getTgtPOS(self):
        return self.__linkObj.getTgtPOS()
    def getSrcGloss(self):
        return self.__linkObj.getSrcGloss()
    def getSrcHeadword(self):
        return self.__linkObj.getSrcHeadword()
    def getTgtGloss(self):
        return self.__linkObj.getTgtGloss()
    def getTgtHeadword(self):
        return self.__linkObj.getTgtHeadword()
    def getInitialStatus(self):
        return self.__linkObj.getInitialStatus()
    def setInitialStatus(self, myStatus):
        self.__linkObj.setInitialStatus(myStatus)
    def setSrcHPG(self, srcHPG):
        self.__linkObj.setSrcHPG(srcHPG)
    def setTgtHPG_only(self, tgtHPG):
        self.__linkObj.setTgtHPG_only(tgtHPG)
    def setTgtHPG(self, tgtHPG):
        self.__linkObj.setTgtHPG(tgtHPG)
    def getSrcSense(self):
        return self.__linkObj.getSrcSense()
    def getTgtSense(self):
        return self.__linkObj.getTgtSense()
    def getTgtGuid(self):
        return self.__linkObj.getTgtGuid()
    def getTgtSenseNum(self):
        return self.__linkObj.getTgtSenseNum()
    def isSuggestion(self):
        return self.__linkObj.isSuggestion()
    def isInitiallyLinkedAndTargetUnmodified(self):
        return self.__linkObj.isInitiallyLinkedAndTargetUnmodified()

# model the information having to do with a link from a source sense
# to a target sense
class Link(object):
    def __init__(self, srcHPG, tgtHPG=None):
        self.setSrcHPG(srcHPG)
        self.setTgtHPG(tgtHPG)
        self.initialStatus = INITIAL_STATUS_UNLINKED
        self.linkIt = False
        self.modified = False
        self.tgtModified = False
    def getModified(self):
        return self.modified
    def setModified(self, myBool):
        self.modified = myBool
    def getTgtModified(self):
        return self.tgtModified
    def setTgtModified(self, myBool):
        self.tgtModified = myBool
    def getLinkIt(self):
        return self.linkIt
    def setLinkIt(self, myBool):
        self.linkIt = myBool
    def getSrcHPG(self):
        return self.__srcHPG
    def getTgtHPG(self):
        return self.__tgtHPG
    def getSrcPOS(self):
        return self.__srcHPG.getPOS()
    def getTgtPOS(self):
        return self.__tgtHPG.getPOS()
    def getSrcGloss(self):
        return self.__srcHPG.getGloss()
    def getSrcHeadword(self):
        return self.__srcHPG.getHeadword()
    def getTgtGloss(self):
        return self.__tgtHPG.getGloss()
    def getTgtHeadword(self):
        return self.__tgtHPG.getHeadword()
    def getInitialStatus(self):
        return self.initialStatus
    def setInitialStatus(self, myStatus):
        self.initialStatus = myStatus
        if myStatus == INITIAL_STATUS_LINKED:
            self.setLinkIt(True) # this shows that this is a sense the user intends to keep linked
        else:
            self.setLinkIt(False)
    def setSrcHPG(self, srcHPG):
        self.__srcHPG = srcHPG
    def setTgtHPG_only(self, tgtHPG):
        self.__tgtHPG = tgtHPG
    def setTgtHPG(self, tgtHPG):
        self.__tgtHPG = tgtHPG
        if tgtHPG is not None:
            self.setInitialStatus(INITIAL_STATUS_LINKED)
            self.setLinkIt(True)
    def getSrcSense(self):
        return self.__srcHPG.getSense()
    def getTgtSense(self):
        return self.__tgtHPG.getSense()
    def getTgtGuid(self):
        return self.__tgtHPG.getSense().Guid.ToString()
    def getTgtSenseNum(self):
        return self.__tgtHPG.getSenseNum()
    def isSuggestion(self):
        if self.getInitialStatus() == INITIAL_STATUS_EXACT_SUGGESTION or self.getInitialStatus() == INITIAL_STATUS_FUZZY_SUGGESTION:
            return True
        return False
    def isInitiallyLinkedAndTargetUnmodified(self):
        return self.getInitialStatus() == INITIAL_STATUS_LINKED and self.tgtModified == False

class LinkerCombo(QtCore.QAbstractListModel):
    
    def __init__(self, myData = [], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.__localData = myData
        self.__currentHPG = myData[0] # start out on the first one
        self.__RTL = False
    def appendDataItem(self, myHPG):
        self.__localData.append(myHPG)
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
        return len(self.__myHeaderData) 
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
            
            if col == COL_LINK_IT: # Checkbox column
                pass
            
            elif col == COL_TGT_HEADWORD: # target headword column
                
                locData.setTgtHPG_only(self.__selectedHPG)
                locData.setLinkIt(True)
                locData.setTgtModified(True)

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
                if col == COL_SRC_HEADWORD:
                    
                    qColor = QtGui.QColor(QtCore.Qt.darkGreen)
                
                # tgt headword    
                elif col == COL_TGT_HEADWORD:
                    
                    qColor = QtGui.QColor(QtCore.Qt.darkBlue)
                
                # gram. category    
                elif (col == COL_SRC_POS or col == COL_TGT_POS) and locData.isSuggestion() == True: 
                    
                    # If there is a mismatch in grammatical category color it red
                    if locData.getSrcPOS().lower() != locData.getTgtPOS().lower():
                        
                        qColor = QtGui.QColor(QtCore.Qt.red)
                        
                qBrush = QtGui.QBrush(qColor)
                
                return qBrush
        
        # Set the background color
        if role == QtCore.Qt.BackgroundRole:
            
            if row >= 0:
                
                initiallyLinkedUnmodifiedSense = locData.isInitiallyLinkedAndTargetUnmodified()
                
                # Mark in yellow the first column cells for the rows to be linked or unlinked (in the case of a previously linked row from the DB)
                if col == 0 and ((locData.getLinkIt() == True and not initiallyLinkedUnmodifiedSense) or (locData.getLinkIt() == False and initiallyLinkedUnmodifiedSense)):
                    
                    qColor = QtGui.QColor(QtCore.Qt.yellow)
                    
                # Modified rows get a color just for the target columns
                elif col >= COL_TGT_HEADWORD and col <= COL_TGT_GLOSS and (locData.getTgtModified() == True or \
                                                                           (locData.getInitialStatus() == INITIAL_STATUS_LINKED and locData.getLinkIt() == False)):
                    
                    qColor = QtGui.QColor(152, 251, 152) # pale green
                
                # Exact suggestion 
                elif locData.getInitialStatus() == INITIAL_STATUS_EXACT_SUGGESTION:
                    
                    qColor = QtGui.QColor(176, 255, 255) # medium cyan
                    
                # Fuzzy suggestion 
                elif locData.getInitialStatus() == INITIAL_STATUS_FUZZY_SUGGESTION:
                            
                    qColor = QtGui.QColor(224, 255, 255) # light cyan
                
                # No links
                elif locData.getInitialStatus() == INITIAL_STATUS_UNLINKED:
                    
                    qColor = QtGui.QColor(255, 192, 203) # pink
                    
                # Existing link in the DB    
                else: # INITIAL_STATUS_LINKED:
                    
                    qColor = QtGui.QColor(QtCore.Qt.white)

                # This causes continual repainting and high processor use, moved it to SetData()
                #self.dataChanged.emit(index, index)
                
                return qColor
        
        if role == QtCore.Qt.DisplayRole:
             
            if col != COL_LINK_IT:
                 
                return locData.getDataByColumn(col)
                 
        if role == QtCore.Qt.CheckStateRole:
             
            if col == COL_LINK_IT:
                 
                # If user said link it, check the box. Also if there is an existing link in the DB on 
                if locData.getLinkIt() == True or (locData.getInitialStatus() == INITIAL_STATUS_LINKED and locData.getModified() == False):
                     
                    val = QtCore.Qt.Checked
                else:
                    val = QtCore.Qt.Unchecked
                
                return val
             
        elif role == QtCore.Qt.TextAlignmentRole:
             
            if col == COL_LINK_IT:
                 
                # Doesn't have an effect
                return QtCore.Qt.AlignCenter
             
            # Check if we have right to left data in a column, if so align it right
            elif col > COL_LINK_IT and len(locData.getDataByColumn(col)) > 0:
                 
                # check first character of the given cell
                if unicodedata.bidirectional(locData.getDataByColumn(col)[0]) in ('R', 'AL'): 
                     
                    return QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter
                
    def flags(self, index):
        
        locData = self.__localData[index.row()]
        
        # Columns 0 and 4 are enabled and selectable
        val = QtCore.Qt.ItemIsSelectable
        
        # Add checkable for the 1st column
        if index.column() == COL_LINK_IT:

            # Don't allow the box to be checked if we have an unlinked row that hasn't had the target modified
            if not (locData.getInitialStatus() == INITIAL_STATUS_UNLINKED and locData.getTgtModified() == False):
            
                val =  val | QtCore.Qt.ItemIsEnabled
                
            val =  val | QtCore.Qt.ItemIsUserCheckable 
        
        # Add editable for the target headword column  
        elif index.column() == COL_TGT_HEADWORD:
            
            val = val | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable 
            
        return val
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        
        col = index.column()

        if role == QtCore.Qt.CheckStateRole and col == COL_LINK_IT:
            
            self.__linkingChanged = True
            
            row = index.row()
            
            if value == QtCore.Qt.Checked: 
                
                self.__localData[row].setLinkIt(True)
                self.__localData[row].setModified(True)
            else:
                self.__localData[row].setLinkIt(False)
                self.__localData[row].setModified(True)
            
            # Repaint columns link, target head-word, cat, gloss) when the checkbox is changed.
            # Do this for all rows to display rows that are linked to the link object
            for myCol in [COL_LINK_IT, COL_TGT_HEADWORD, COL_TGT_POS, COL_TGT_GLOSS]:
                
                for row in range(0,len(self.__localData)):
                    newindex = self.index(row, myCol)    
                    self.dataChanged.emit(newindex, newindex)
            
            # Recalculate the senses to link 
            self.__callbackFunc()
            
        return True

class Main(QMainWindow):

    def __init__(self, myData, headerData, comboData, sourceTextName, DB, report, configMap, properNounAbbr, sourceTextList, targetMorphNames, TargetDB):
        
        QMainWindow.__init__(self)
        self.showOnlyUnlinked = False
        self.hideProperNouns = False
        self.exportUnlinked = False
        self.ui = Ui_SenseLinkerWindow()
        self.ui.setupUi(self)
        myFont = self.ui.tableView.font()
        self.__model = LinkerTable(myData, headerData, myFont, self.calculateRemainingLinks)
        self.__fullData = myData
        self.headerData = headerData
        self.ui.tableView.setModel(self.__model)
        self.__comboData = comboData
        self.__comboModel = LinkerCombo(comboData)
        self.ui.targetLexCombo.setModel(self.__comboModel)
        self.DB = DB
        self.TargetDB = TargetDB
        self.__report = report
        self.__configMap = configMap
        self.retVal = 0
        self.cols = len(headerData)
        self.restartLinker = False
        self.properNounAbbr = properNounAbbr
        self.targetMorphNames = targetMorphNames
        
        # Set the combo box to the 2nd element, since the first one is **none**
        if len(comboData) > 1:
            
            self.ui.targetLexCombo.setCurrentIndex(1)
            
        # load the source text list
        Utils.loadSourceTextList(self.ui.SourceTextCombo, sourceTextName, sourceTextList)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.InitRebuildBilingCheckBox()
        self.InitSearchAllCheckBox()
        
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        self.ui.targetLexCombo.currentIndexChanged.connect(self.ComboClicked)
        self.ui.ShowOnlyUnlinkedCheckBox.clicked.connect(self.ShowOnlyUnlinkedClicked)
        self.ui.HideProperNounsCheckBox.clicked.connect(self.HideProperNounsClicked)
        self.ui.exportUnlinkedCheckBox.clicked.connect(self.exportUnlinkedClicked)
        self.ui.searchTargetEdit.textChanged.connect(self.SearchTargetChanged)
        self.ui.SourceTextCombo.activated.connect(self.sourceTextComboChanged)
        self.ui.FontButton.clicked.connect(self.FontClicked)
        self.ui.ZoomIncrease.clicked.connect(self.ZoomIncreaseClicked)
        self.ui.ZoomDecrease.clicked.connect(self.ZoomDecreaseClicked)
        self.ui.RebuildBilingCheckBox.clicked.connect(self.RebuildBilingChecked)
        self.ui.SearchAnythingCheckBox.clicked.connect(self.SearchAnythingChecked)
        self.ui.AddEntryButton.clicked.connect(self.AddTargetEntry)
        self.ComboClicked()
        
        myHPG = self.__comboModel.getCurrentHPG()
        myHeadword = myHPG.getHeadword()
        
        # Check for right to left data and set the combobox direction if needed
        for i in range(0, len(myHeadword)):

            if unicodedata.bidirectional(myHeadword[i]) in ('R', 'AL'):

                self.ui.targetLexCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.__comboModel.setRTL(True)
                break
    
        # Figure out how many senses are unlinked so we can show the user
        self.calculateRemainingLinks()
        
    def AddTargetEntry(self):

        # Get cluster projects from settings;
        clusterProjects = ReadConfig.getConfigVal(self.__configMap, ReadConfig.CLUSTER_PROJECTS, self.__report, giveError=False)

        if not clusterProjects:

            clusterProjects = []
        else:
            # Remove blank ones
            clusterProjects = [x for x in clusterProjects if x]

        dlg = NewEntryDlg.NewEntryDlg(self.TargetDB, self.__report, self.targetMorphNames, clusterProjects)
        dlg.exec_()

        if dlg.retVal == True:

            # Create a headword-POS-gloss object
            myHPG = HPG(dlg.sense, dlg.lexemeForm, dlg.POS, dlg.gloss, SenseNum=1)

            # Add the new sense to the end of the target sense list
            self.__comboModel.appendDataItem(myHPG)

            # Make the new sense the current item in the combo box.
            self.ui.targetLexCombo.setCurrentIndex(self.ui.targetLexCombo.count()-1)
            self.ui.targetLexCombo.setStyleSheet("QComboBox { background-color: yellow; }")

            # Set a timer to change the background color back after 2 seconds 
            QTimer.singleShot(2000, self.resetBackgroundColor)

    def resetBackgroundColor(self): 
            # Reset the background color of the edit box to default 
            self.ui.targetLexCombo.setStyleSheet("")
        
    def InitSearchAllCheckBox(self):
        
        self.ui.SearchAnythingCheckBox.setCheckState(QtCore.Qt.Unchecked)
        
        val = ReadConfig.getConfigVal(self.__configMap, ReadConfig.LINKER_SEARCH_ANYTHING_BY_DEFAULT, report=None, giveError=False)
        
        if val:
            if val == 'y':
                
                self.ui.SearchAnythingCheckBox.setCheckState(QtCore.Qt.Checked)
                
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
            
            mySrcHPG = linkObj.getSrcHPG()
            
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
        (font, ret) = QFontDialog.getFont(self.__model.getFont(), parent=self)
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
            if QMessageBox.question(self, _translate("LinkSenseTool", 'Save Changes'), _translate("LinkSenseTool", "Do you want to save your changes?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
        
                self.retVal = 1
        
        # Have FlexTools refresh the status bar
        refreshStatusbar()

        # Close the tool and it will restart
        self.close()
    
    def SearchAnythingChecked(self):
        
        if self.ui.SearchAnythingCheckBox.isChecked():
            
            self.__oldComboModel = self.__comboModel
            
        else:
            self.__comboModel = self.__oldComboModel
            self.ui.targetLexCombo.setModel(self.__comboModel)

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
                                    
                self.__comboModel = LinkerCombo(newList)
                self.ui.targetLexCombo.setModel(self.__comboModel)

    def findRow(self, searchText):
        
        found = False
        
        # Look for a match to the beginning of a headword
        for i in range(0, self.__comboModel.rowCount(None)):
            
            if re.match(unicodedata.normalize('NFD', re.escape(searchText)) + r'.*', self.__comboModel.getRowValue(i).getHeadword(), flags=re.RegexFlag.IGNORECASE):
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
            
    def positionControl(self, myControl, x, y):
        
        myControl.setGeometry(x, y, myControl.width(), myControl.height())
        
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        
        # Get the default font metrics
        font = self.ui.tableView.font()
        metrics = QtGui.QFontMetrics(font)
        expandedAmt = 0
        
        # LinkIt column width (first one)
        firstColWidth = 45
        headerText = self.headerData[COL_LINK_IT]
        textWidth = metrics.width(headerText) + 20  # Adding padding
        firstColWidth = textWidth
        self.ui.tableView.setColumnWidth(COL_LINK_IT, firstColWidth)
        
        # VerseNum column width (second one) - this is fixed width
        secondColWidth = 45
        self.ui.tableView.setColumnWidth(COL_VERSE_NUM, secondColWidth)

        colWidth = ((self.width() - 20 - firstColWidth - secondColWidth) // (self.cols - 2)) - 4 # don't include 1st 2 columns

        # Adjust column widths based on header text don't include 1st 2 columns
        for col in range(2, self.cols):

            headerText = self.headerData[col]
            textWidth = metrics.width(headerText) + 20  # Adding padding

            # See if our needed width for the text is less than our standard column width
            if textWidth < colWidth:

                # See if we should shrink a column
                if expandedAmt:

                    # Find out how much space is available
                    extraAvail = colWidth - textWidth

                    # If we have more shrink room than needed
                    if extraAvail > expandedAmt:

                        # Shrink the column and set the expandedAmt to 0 to show we don't need to do more shrinking
                        textWidth = colWidth - expandedAmt
                        expandedAmt = 0
                    
                    # Otherwise shrink as much as we can
                    else:
                        expandedAmt -= extraAvail
                
                # Otherwise use the standard column width
                else:
                    textWidth = colWidth
            else:
                expandedAmt += textWidth - colWidth

            self.ui.tableView.setColumnWidth(col, textWidth)

    def ComboClicked(self):
        # Set the target HPG for the model  
        myHPG = self.__comboModel.getCurrentHPG()
        self.__model.setSelectedHPG(myHPG)
        
    def OKClicked(self):
        self.retVal = 1
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
        
    def closeEvent(self, event):
        if self.retVal != 1:
            self.CancelClicked()
        elif self.rebuildBiling:
        
            # Show hourglass cursor 
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor) 

            # Pause for 3 seconds to let FLEx write out the links before the bilingual lexicon gets rebuilt
            time.sleep(3)

            # Revert back to the default cursor 
            QApplication.restoreOverrideCursor()       

    def CancelClicked(self):
        self.retVal = 0

        # Check if the user did some linking or unlinking
        if self.__model.didLinkingChange():
            
            # Check if the user wants to save changes
            if QMessageBox.question(self, _translate("LinkSenseTool", 'Save Changes'), _translate("LinkSenseTool", "Do you want to save your changes?"), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
        
                self.retVal = 1
        
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
                
                if myLink.getSrcHPG() not in srcHPGtoLinkItMap:
                    
                    srcHPGtoLinkItMap[myLink.getSrcHPG()] = myLink.getLinkIt() 
                else:
                    if myLink.getLinkIt():
                        
                        srcHPGtoLinkItMap[myLink.getSrcHPG()] = True
                
            for myLink in self.__fullData:
                
                keepIt = False
                
                if self.showOnlyUnlinked:
                    
                    # if none of possible identical srcHPGs has been linked, add this one
                    if not srcHPGtoLinkItMap[myLink.getSrcHPG()]:
                        
                        keepIt = True
                else:
                    keepIt = True
                        
                if self.hideProperNouns:
                    
                    if keepIt == True:
                    
                        if myLink.getSrcPOS() != self.properNounAbbr:
                            
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

        self.ui.tableView.scrollToTop()
        return
    
def getGlossMapAndTgtLexList(TargetDB, report, glossMap, targetMorphNames, tgtLexList, entriesTotal):

    report.ProgressStart(entriesTotal)
    glossWarnings = 0

    # Loop through all the target entries
    for entryIndex, entryObj in enumerate(TargetDB.LexiconAllEntries()):
    
        report.ProgressUpdate(entryIndex+1)
        
        # Don't process affixes, clitics
        if entryObj.LexemeFormOA and entryObj.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           entryObj.LexemeFormOA.MorphTypeRA and Utils.as_string(entryObj.LexemeFormOA.MorphTypeRA.Name) in targetMorphNames:
        
            # Loop through senses
            for senseNum, mySense in enumerate(entryObj.SensesOS):

                try:
                    msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                except:
                    # Skip an MSA that could not be casted.
                    continue

                # Skip empty MSAs
                if msa == None:
                    continue
                
                # Get headword, POS, gloss
                headword = ITsString(entryObj.HeadWord).Text
                
                # Make the lemma in the form x.x (but remove if 1.1)
                headword = Utils.fixupLemma(entryObj, senseNum+1, remove1dot1Bool=True)
                
                if msa.PartOfSpeechRA:

                    POS = ITsString(msa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                else:
                    POS = 'UNK'
                    report.Warning(_translate("LinkSenseTool", 'Empty grammatical category found for the target word: ')+ headword, TargetDB.BuildGotoURL(entryObj))
                    
                gloss = Utils.as_string(mySense.Gloss)
                
                # If we have a non-empty gloss, add it to the map (we will allow ***)
                if gloss and len(gloss) > 0:

                    # Create an HPG object
                    myHPG = HPG(mySense, headword, POS, gloss, senseNum+1)
                    
                    # Add this object to the list of all entry-senses for display
                    # in the combo box
                    tgtLexList.append(myHPG)
                    
                    if gloss not in glossMap:

                        glossMap[gloss] = [myHPG]

                    else: # multiple senses for this gloss

                        glossMap[gloss].append(myHPG)

                    if gloss == '***' and glossWarnings < MAX_GLOSS_WARNINGS:

                        report.Warning(_translate("LinkSenseTool", 'Empty gloss found for the target word: ')+ headword, TargetDB.BuildGotoURL(entryObj))
                        glossWarnings += 1

                    if glossWarnings == MAX_GLOSS_WARNINGS:

                        report.Warning(_translate("LinkSenseTool", 'More than {num_warnings} empty glosses found. Suppressing further warnings for empty target glosses.').format(num_warnings=MAX_GLOSS_WARNINGS))
                        glossWarnings += 1
    return True

# Given an entry guid and a sense #, look up the the sense info. Also convert an entry guid to a sense guid and re-write it.
def getHPGfromGuid(entry, DB, TargetDB, mySense, equiv, senseEquivField, senseNumField, report, preGuidStr):
                      
    retVal = None
          
    targetSense, lem, senseNum = Utils.getTargetSenseInfo(entry, DB, TargetDB, mySense, equiv, senseNumField, report, remove1dot1Bool=True, \
                                                          rewriteEntryLinkAsSense=True, preGuidStr=preGuidStr, senseEquivField=senseEquivField)
    if targetSense:

        if targetSense.MorphoSyntaxAnalysisRA:

            # Get the POS abbreviation for the target sense, assuming we have a stem
            if targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':

                targetMsa = IMoStemMsa(targetSense.MorphoSyntaxAnalysisRA)
                
                # verify PartOfSpeechRA is valid, if not, set the POS unknown
                if targetMsa.PartOfSpeechRA == None:

                    POS = 'UNK'
                else:
                    # Get target pos abbreviation and gloss
                    POS = ITsString(targetMsa.PartOfSpeechRA.\
                                    Abbreviation.BestAnalysisAlternative).Text
            
                Gloss = Utils.as_string(targetSense.Gloss)
                
                # Create an HPG (headword-POS-gloss) object
                myHPG = HPG(targetSense, lem, POS, Gloss, senseNum)
                
                retVal = myHPG
    return retVal

# do check for exact match and sometimes fuzzy match to find suggested 
# target senses to be linked to
def getMatchesOnGloss(gloss, glossMap, saveMap, doFuzzyCompare):

    matchList = []
    
    # Blank glosses in FLEx will be *** in the gloss field, so we will skip them. We don't want to
    # match a bunch of *** glosses in the target lexicon.
    if gloss == '***':

        return matchList
    
    # check for exact match
    if gloss in glossMap:

        matchList = glossMap[gloss]

    elif doFuzzyCompare:    

        # See if we've processed this gloss before
        if gloss not in saveMap:

            # See if we have a candidate for a fuzzy compare
            glossLen = len(gloss)

            if glossLen >= MIN_GLOSS_LEN_FOR_FUZZ:

                # Loop through all the target glosses
                for mgloss in list(glossMap.keys()):

                    mglossLen = len(mgloss)

                    # skip the fuzzy match if the target gloss is to small or there's a big difference in length
                    if mglossLen >= MIN_GLOSS_LEN_FOR_FUZZ and abs(mglossLen-glossLen) <= MIN_DIFF_GLOSS_LEN_FOR_FUZZ:
                        
                        # See if we have a match
                        if fuzz.QRatio(mgloss, gloss) > FUZZ_THRESHOLD:

                            matchList.extend(glossMap[mgloss])
                            saveMap[gloss] = matchList
        else: 
            # use saved list
            matchList = saveMap[gloss]
            
    return matchList

def getInterlinearText(DB, report, configMap, contents):
    
    # Get various bits of data for the get interlinear function
    interlinParams = InterlinData.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return

    # Get interlinear data. A complex text object is returned.
    myText = InterlinData.getInterlinData(DB, report, interlinParams)
    
    return myText

def processInterlinear(report, DB, senseEquivField, senseNumField, sourceMorphNames, TargetDB, glossMap, properNounAbbr, myText, preGuidStr):
        
    saveMap = {}
    processedMap = {}
    myData = []
    
    report.ProgressStart(myText.getWordCount())

    # Loop through the words
    for paragraph in myText.getParagraphs():
        
        for sentence in paragraph.getSentences():
            
            for wordIndex, word in enumerate(sentence.getWords()):
                
                report.ProgressUpdate(wordIndex)

                # Possible multiple entries if it's a compound
                for eNum, entry in enumerate(word.getEntries()):
                    
                    if not word.hasSenses():
                        continue
                    
                    # each entry should have a sense
                    mySense = word.getSense(eNum)
                    
                    if mySense is None:
                        continue
                        
                    myLinkerRow = LinkerRow()

                    # Add a possible verse number
                    myLinkerRow.setVerseNum(word)

                    # If we have not processed this sense already, initialize a new Link object
                    if mySense not in processedMap:
                        
                        # See if we have the right morph type
                        morphType = Utils.as_string(entry.LexemeFormOA.MorphTypeRA.Name)
    
                        if morphType not in sourceMorphNames:
                            continue
                            
                        # Get gloss
                        srcGloss = Utils.as_string(mySense.Gloss)    
                
                        # Get lemma & POS
                        srcHeadWord = Utils.remove1dot1(word.getLemma(eNum))
                        srcPOS = word.getPOS(eNum)

                        # Change the word to lower case if that's what the entry's headword is
                        srcHeadWord = word.matchCaseOfEntry(srcHeadWord, eNum)
                        
                        # Create a headword-POS-gloss (HPG) object and initialize a Link object with this as the source sense info.
                        srcHPG = HPG(mySense, srcHeadWord, srcPOS, srcGloss)
                        myLink = Link(srcHPG)
                        myLinkerRow.setLinkObject(myLink)
                        
                        # Get the url to the target sense (if present)
                        equivStr = Utils.getTargetEquivalentUrl(DB, mySense, senseEquivField)

                        if equivStr:

                            # handle sense mapped intentionally to nothing.
                            if equivStr == Utils.NONE_HEADWORD:
                                
                                tgtHPG = HPG(Sense=None, Headword=Utils.NONE_HEADWORD, POS=NA_STR, Gloss=NA_STR)
                            else:
                                # Get headword-POS-gloss (HPG) object for the guid, this returns None if not found
                                # This will also convert an entry guid to a sense guid and re-write it.
                                tgtHPG = getHPGfromGuid(entry, DB, TargetDB, mySense, equivStr, senseEquivField, senseNumField, report, preGuidStr)
                            
                            # Set the target part of the Link object and add it to the list
                            myLink.setTgtHPG(tgtHPG)
                            myData.append(myLinkerRow)
                            processedMap[mySense] = myLink, None, sentence
                            
                        else: # no link url present
                            
                            # Don't do a fuzzy compare if the source POS is a proper noun
                            doFuzzyCompare = False if srcPOS == properNounAbbr else True

                            # Find matches for the current gloss using fuzzy compare if needed
                            matchedSenseList = getMatchesOnGloss(srcGloss, glossMap, saveMap, doFuzzyCompare)
                            
                            # No matches
                            if len(matchedSenseList) == 0:

                                # add a Link object that has no target information
                                myData.append(myLinkerRow)
                                processedMap[mySense] = myLink, None, sentence
                                continue
                        
                            # Process all the matches
                            myMatchLinkList, matchLink = createMatchLinkList(matchedSenseList, myLink, srcHPG)

                            addLinkerRowsFromMatchLinkList(myMatchLinkList, myData, word)
                            processedMap[mySense] = matchLink, myMatchLinkList, sentence
                                    
                    else: # we've processed this sense before

                        myLink, myMatchLinkList, _ = processedMap[mySense] # _ for sent which we don't need
                        
                        # if there's no associated list, just append the link object
                        if myMatchLinkList == None:
                            
                            myLinkerRow.setLinkObject(myLink)
                            myData.append(myLinkerRow)
                        
                        # otherwise, we had multiple links associated with this sense, add them all to the list again
                        else:
                            addLinkerRowsFromMatchLinkList(myMatchLinkList, myData, word)
                # wordIndex += 1

    return myData, processedMap

def createMatchLinkList(matchedSenseList, myLink, srcHPG):

    # Process all the matches
    matchLinkList = []
    
    for i, matchHPG in enumerate(matchedSenseList):
        
        if i == 0: # use the Link object already created

            myLink.setTgtHPG(matchHPG)
            matchLink = myLink
        else:
            matchLink = Link(srcHPG, matchHPG)

        # See if we have an exact match
        if matchLink.getSrcGloss().lower() == matchLink.getTgtGloss().lower():
            
            matchLink.setInitialStatus(INITIAL_STATUS_EXACT_SUGGESTION)
        else:
            matchLink.setInitialStatus(INITIAL_STATUS_FUZZY_SUGGESTION)
            
        matchLinkList.append(matchLink)

    return matchLinkList, matchLink

def addLinkerRowsFromMatchLinkList(myMatchLinkList, myData, word):

    for curMatchLink in myMatchLinkList:

        myNewLinkerRow = LinkerRow()
        myNewLinkerRow.setLinkObject(curMatchLink)
        myNewLinkerRow.setVerseNum(word)
        myData.append(myNewLinkerRow)

def updateSourceDb(DB, TargetDB, report, myData, preGuidStr, senseEquivField, senseNumField):        
    
    updatedSenses = {}
    cnt = 0
    unlinkCount = 0
        
    # Loop through the data
    for currLink in myData:
        
        # See if we have already updated this sense
        currSense = currLink.getSrcSense()
        
        if currSense not in updatedSenses:
            
            # Create a link if the user marked it for linking and we have a valid target
            # and it's not an existing linked sense in the DB where the link hasn't been changed (these are 
            # marked linkIt=True, but we don't want to re-link them even though it wouldn't hurt).
            if (currLink.getLinkIt() == True and currLink.getTgtHPG() != None and currLink.getTgtHPG().getHeadword() != '') and \
               not currLink.isInitiallyLinkedAndTargetUnmodified():
                
                cnt += 1
                
                ## Set the target field

                # Get the FLEx style that is for hyperlinks (named hyperlink)
                myStyle = Utils.getHyperLinkStyle(DB)

                # Get the headword string
                headWord = currLink.getTgtHPG().getHeadword()
                
                # If the hyperlink style doesn't exist or we are doing a 'None' link, write a non-hyperlink value to the custom field
                if myStyle == None or headWord == Utils.NONE_HEADWORD: 

                    DB.LexiconSetFieldText(currSense, senseEquivField, Utils.NONE_HEADWORD)

                # Write a hyperlink to the custom field
                else:
                    # Build target link from saved url path plus guid string for this target sense
                    urlStr = preGuidStr + currLink.getTgtGuid() + '%26tag%3d'
                    
                    tgtSense = currLink.getTgtSense()
                    tgtEntry = ILexEntry(currLink.getTgtSense().Entry)
                    Utils.writeSenseHyperLink(DB, TargetDB, currSense, tgtEntry, tgtSense, senseEquivField, urlStr, myStyle)

                    # If the sense number field exists, set it to an empty string
                    if senseNumField:

                        DB.LexiconSetFieldText(currSense, senseNumField, '')

                updatedSenses[currSense] = 1
            
            # Unlink this sense
            elif currLink.getLinkIt() == False and currLink.isInitiallyLinkedAndTargetUnmodified():

                unlinkCount += 1
                
                # Clear the target field
                DB.LexiconSetFieldText(currSense, senseEquivField, '')

                # If the sense number field is None, we aren't using it
                if senseNumField:

                    DB.LexiconSetFieldText(currSense, senseNumField, '')

                updatedSenses[currSense] = 1

    # Give feedback            
    if cnt == 1:
       
        report.Info(_translate("LinkSenseTool", '1 link created.'))
    else:
        report.Info(_translate("LinkSenseTool", '{num} links created.').format(num=str(cnt)))

    if unlinkCount == 1:
       
        report.Info(_translate("LinkSenseTool", '1 link removed'))
       
    elif unlinkCount > 1:
       
        report.Info(_translate("LinkSenseTool", ' links removed').format(num=str(unlinkCount)))
                      
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
    ET.SubElement(row, 'th').text = _translate("LinkSenseTool", 'Gloss')
    ET.SubElement(row, 'th').text = _translate("LinkSenseTool", 'Category')
    ET.SubElement(row, 'th').text = tgtDBname
    ET.SubElement(row, 'th').text = _translate("LinkSenseTool", 'Comment')
    
    return row

def getFirstOccurringSent(myHPG, processedMap):

    mySense = myHPG.getSense()
    
    # The processed map from the process interlinear function already has the first sentence
    # where this sense occurred.
    if mySense in processedMap:
        
        # The 3rd part of the map is the sentence that goes to this sense
        return processedMap[mySense][2] 
    
    return None
        
def dumpVocab(myData, processedMap, srcDBname, tgtDBname, sourceTextName, report, hideProperNouns, properNounAbbr):
                
    doneMap = {}
    wordSentList = []
    cnt = 0
                
    # Loop through the data
    for currLink in myData:
        
        # See if we have already updated this sense
        srcHPG = currLink.getSrcHPG()
        
        if srcHPG not in doneMap:
            
            # This sense is not being linked so we'll be adding to the vocab document.
            if not currLink.getLinkIt():
                
                # Don't process a proper noun if the user had them hidden
                if not (hideProperNouns and srcHPG.getPOS() == properNounAbbr):
                
                    mySent = getFirstOccurringSent(currLink.getSrcHPG(), processedMap)
                    
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
        
        # add word to the sentence word list
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
            report.Error(_translate("LinkSenseTool", "Permission error writing {htmlFileName}. Perhaps the file is in use in another program?").format(htmlFileName=htmlFileName))
            return
        
        except:
            report.Error(_translate("LinkSenseTool", "Error writing {htmlFileName}.").format(htmlFileName=htmlFileName))
            return
        
        # Report how many words were dumped
        report.Info(_translate("LinkSenseTool", "{cnt} words written to the file: {htmlFileName}. You'll find it in the Output folder.").format(cnt=str(cnt), htmlFileName=os.path.basename(htmlFileName)))

    else:
        report.Info(_translate("LinkSenseTool", "No unlinked words. Nothing exported."))

def RunModule(DB, report, configMap, app):
        
    haveConfigError = False
    
    # Get need configuration file properties
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    linkField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    numField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, report, giveError=False)
    targetMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)

    if not sourceTextName:
        
        report.Error(_translate("LinkSenseTool", 'No Source Text Name has been set. Please go to Settings and fix this.'))
        haveConfigError = True
    
    if not linkField:
        
        report.Error(_translate("LinkSenseTool", 'No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.'))
        haveConfigError = True
    
    # Give an error if there are no morphnames
    if not sourceMorphNames or len(sourceMorphNames) < 1:
        
        report.Error(_translate("LinkSenseTool", 'No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.'))
        haveConfigError = True
    
    if not targetMorphNames or len(targetMorphNames) < 1:
        
        report.Error(_translate("LinkSenseTool", 'No Target Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.'))
        haveConfigError = True
    
    if haveConfigError:
        return ERROR_HAPPENED
    
    matchingContentsObjList = []

    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    
    if sourceTextName not in sourceTextList:
        
        report.Error(_translate("LinkSenseTool", 'The text named: {sourceTextName} not found.').format(sourceTextName=sourceTextName))
        return ERROR_HAPPENED
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceTextName)]
    
    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)

    # If there is no Sense Number custom field, that's ok, set this to null. Now we use sense guids.
    if not numField:

        senseNumField = None
    else:
        senseNumField = DB.LexiconGetSenseCustomFieldNamed(numField)
    
    if not (senseEquivField):

        report.Error(_translate("LinkSenseTool", "{linkField} field doesn't exist. Please read the instructions.").format(linkField=linkField))
        return ERROR_HAPPENED

    TargetDB = FLExProject()

    # Open the target database
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)

    if not targetProj:
        return ERROR_HAPPENED
    
    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():

        report.Error(_translate("LinkSenseTool", 'The Target Database does not exist. Please check the configuration file.'))
        return ERROR_HAPPENED

    report.Info(_translate("LinkSenseTool", 'Opening: {targetProj} as the target database.').format(targetProj=targetProj))

    try:
        TargetDB.OpenProject(targetProj, True)

    except: #FDA_DatabaseError, err:

        report.Error(_translate("LinkSenseTool", 'Failed to open the target database.'))
        raise

    report.Info(_translate("LinkSenseTool", "Starting {moduleName} for text: {sourceTextName}.").format(moduleName=docs[FTM_Name], sourceTextName=sourceTextName))

    preGuidStr = 'silfw://localhost/link?database%3d'
    preGuidStr += re.sub('\s','+', targetProj)
    preGuidStr += '%26tool%3dlexiconEdit%26guid%3d'
     
    glossMap = {}
    tgtLexList = []

    targetDBtotal = TargetDB.LexiconNumberOfEntries() 

    # Get the proper noun abbreviation
    properNounAbbr = ReadConfig.getConfigVal(configMap, ReadConfig.PROPER_NOUN_CATEGORY, report)
    
    if properNounAbbr is None:
        
        properNounAbbr = ''
    
    # Get the interlinear text object
    myText = getInterlinearText(DB, report, configMap, contents)

    if myText == None:
        TargetDB.CloseProject()
        return ERROR_HAPPENED 

    # Check to see if there is any data to link
    if myText.getSentCount() == 0:
                                        
        report.Error(_translate("LinkSenseTool", 'There were no senses found for linking. Please check your text and approve some words.'))
        TargetDB.CloseProject()
        return ERROR_HAPPENED

    # Create a map of glosses to target senses and their number and a list of target lexical senses
    if not getGlossMapAndTgtLexList(TargetDB, report, glossMap, targetMorphNames, tgtLexList, targetDBtotal):

        TargetDB.CloseProject()
        return ERROR_HAPPENED

    # Go through the interlinear words
    myData, processedMap = processInterlinear(report, DB, senseEquivField, senseNumField, sourceMorphNames, TargetDB, glossMap, properNounAbbr, myText, preGuidStr)

    # Check to see if there is any data to link
    if len(myData) == 0:
                                        
        report.Error(_translate("LinkSenseTool", 'There were no senses found for linking. Please check your text and approve some words.'))
    else:        
        myHeaderData = [_translate("LinkSenseTool", 'Link it!'), 
                                                    'V #', 
                        _translate("LinkSenseTool", 'Source Head Word'), 
                        _translate("LinkSenseTool", 'Source Category'), 
                        _translate("LinkSenseTool", 'Source Gloss'), 
                        _translate("LinkSenseTool", 'Target Head Word'), 
                        _translate("LinkSenseTool", 'Target Category'), 
                        _translate("LinkSenseTool", 'Target Gloss')]
        
        tgtLexList.sort(key=lambda HPG: (HPG.getHeadword().lower(), HPG.getPOS().lower(), HPG.getGloss()))
        
        # Create a special HPG for mapping to none, i.e. the sense will not be mapped to anything
        noneHPG = HPG(Sense=None, Headword=Utils.NONE_HEADWORD, POS=NA_STR, Gloss=NA_STR)
        tgtLexList.insert(0, noneHPG)
        
        window = Main(myData, myHeaderData, tgtLexList, sourceTextName, DB, report, configMap, properNounAbbr, sourceTextList, targetMorphNames, TargetDB)
        
        window.show()
        app.exec_()
        
        # Update the source database with the correct links
        if window.retVal: # True = make the changes        
            
            updateSourceDb(DB, TargetDB, report, myData, preGuidStr, senseEquivField, senseNumField)

            # Dump linked senses if the user wants to
            if window.exportUnlinked:
                
                dumpVocab(myData, processedMap, DB.ProjectName(), targetProj, sourceTextName, report, window.hideProperNouns, properNounAbbr)
    
        # If the user changed the source text combo, the restart member is set to True
        if window.restartLinker:
            
            TargetDB.CloseProject()
            return RESTART_MODULE
        
        elif window.rebuildBiling:
            
            # Only rebuild the bilingual lexicon if the user clicked OK
            if window.retVal:

                TargetDB.CloseProject()
                return REBUILD_BILING
    
    TargetDB.CloseProject()
    return NO_ERRORS

RESTART_MODULE = 0
ERROR_HAPPENED = 1
NO_ERRORS = 2
REBUILD_BILING = 3

def MainFunction(DB, report, modify=False):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)
    if not modify:
        report.Error(_translate("LinkSenseTool", 'You need to run this module in "modify mode."'))
        return
    
    retVal = RESTART_MODULE
    loggedStart = False

    # Have a loop of re-running this module so that when the user changes to a different text, the window restarts with the new info. loaded
    while retVal == RESTART_MODULE:
        
        # Read the configuration file which we assume is in the current directory.
        configMap = ReadConfig.readConfig(report)
        if not configMap:
            return
    
        if not loggedStart:

            # Log the start of this module on the analytics server if the user allows logging.
            Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])
            loggedStart = True

        retVal = RunModule(DB, report, configMap, app)
        
    if retVal == REBUILD_BILING:
        
        # Extract the bilingual lexicon. Force a complete rebuild instead of using the cache.        
        errorList = ExtractBilingualLexicon.extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=False)
        
        # output info, warnings, errors
        for msg in errorList:
            
            # msg is a pair -- string & code
            if msg[1] == 0:
                report.Info(msg[0])
            elif msg[1] == 1:
                report.Warning(msg[0])
            else: # error=2
                report.Error(msg[0])
        
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
