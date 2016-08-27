#
#   LinkSenseTool
#
#   Ron Lockwood
#   SIL International
#   7/18/15
#
#   Version 2.0.2 - 6/21/16 - Ron
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

from FTModuleClass import FlexToolsModuleClass
import ReadConfig
import os
import re
import tempfile
import sys
import unicodedata
from fuzzywuzzy import fuzz
import copy

#----------------------------------------------------------------
# Configurables:

# The minimum length a word should have before doing a fuzzy compare
# otherwise an exact comparision is used
MIN_GLOSS_LEN_FOR_FUZZ = 5
# The percentage or higher in similarity that two words must have in  
# order to be outputted as a possible match. 
FUZZ_THRESHOLD = 74


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Sense Linker Tool",
        'moduleVersion'    : "2.0.2",
        'moduleModifiesDB' : True,
        'moduleSynopsis'   : "Link source and target senses.",
        'moduleDescription'   :
u"""
The source database should be chosen for this module. This module will create links 
in the source project to senses in the target project. This module will show a window
with a list of all the senses in the text. White background rows indicate links that
already exist. blue background rows indicate suggested links based on an exact match
on gloss, light blue background rows indicate suggested links based on a close match on
gloss (currently 75% similar), pink background rows
have no link yet established. Double-click on the Target Head Word column for a row to copy
the currently selected target sense in the upper combo box into that row. Double-click on the first column of a
row in order to turn it from a 0 to a 1. All rows that have a 1 will have a link 
created when the OK button is clicked. Set the first column to 0 to cancel linking two senses. 
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
from Linker import Ui_MainWindow

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
        self.suggestion = False
        self.linkIt = False
        self.modified = False
        self.unlinked = True
        self.initiallyUnlinked = False
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
    def set_srcHPG(self, srcHPG):
        self.__srcHPG = srcHPG
    def set_tgtHPG(self, tgtHPG):
        self.__tgtHPG = tgtHPG
        if tgtHPG:
            self.unlinked = False
    def get_srcSense(self):
        return self.__srcHPG.getSense()
    def get_tgtSense(self):
        return self.__tgtHPG.getSense()
    def get_tgtGuid(self):
        return self.__tgtHPG.getSense().OwningEntry.Guid.ToString()
    def get_tgtSenseNum(self):
        return self.__tgtHPG.getSenseNum()
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
            # columns 4-6 need to be blank if there is no tgtHPG 
            if self.get_tgtHPG() == None:
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
                value = myHPG.getHeadword() + u' \u200F(' + myHPG.getPOS() + u')\u200F ' + myHPG.getGloss()
            else:
                value = myHPG.getHeadword() + u' (' + myHPG.getPOS() + u') ' + myHPG.getGloss()
            self.__currentHPG = myHPG    
            return QtCore.QString(value)
            
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
        
        if role == QtCore.Qt.EditRole:
            if col == 0:
                # make sure we have a target info.
                if self.__localData[row].get_tgtHPG() == None:
                    return 0
                else:
                    self.dataChanged.emit(index, index)
                    return 1 # default to 1 every time so the user can just double-click
            elif col == 4: # target headword column
                self.__localData[row].set_tgtHPG(self.__selectedHPG)
                self.__localData[row].linkIt = True
                self.__localData[row].modified = True
                self.dataChanged.emit(index, index)
                return self.__selectedHPG.getHeadword()
        
        # Set the foreground (font) color
        if role == QtCore.Qt.ForegroundRole:
            qColor = QtGui.QColor(QtCore.Qt.black)
            if row >= 0:
                if col == 1:
                    qColor = QtGui.QColor(QtCore.Qt.darkGreen)
                elif col == 4:
                    qColor = QtGui.QColor(QtCore.Qt.darkBlue)
                elif (col == 2 or col == 5) and self.__localData[row].suggestion == True: #gram cat.
                    # If there is a mismatch in grammatical category color it red
                    if self.__localData[row].get_srcPOS().lower() != self.__localData[row].get_tgtPOS().lower():
                        qColor = QtGui.QColor(QtCore.Qt.red)
                qBrush = QtGui.QBrush(qColor)
                return qBrush
        
        # Set the background color
        if role == QtCore.Qt.BackgroundRole:
            if row >= 0:
                # Mark in yellow the first column cells for the rows to be linked
                if col == 0 and self.__localData[row].linkIt == True:
                    qColor = QtGui.QColor(QtCore.Qt.yellow)
                # Modified rows get a color just for the target columns
                elif self.__localData[row].modified == True and col >= 4 and col <= 6:
                        qColor = QtGui.QColor(152, 251, 152) # pale green
                # Suggested links
                elif self.__localData[row].suggestion == True:
                    # Exact match
                    if self.__localData[row].get_srcGloss() == self.__localData[row].get_tgtGloss():
                        qColor = QtGui.QColor(176, 255, 255) # medium cyan?
                    else:
                        qColor = QtGui.QColor(224, 255, 255) # light cyan
                # No links
                elif self.__localData[row].unlinked == True or self.__localData[row].initiallyUnlinked == True:
                    self.__localData[row].initiallyUnlinked = True
                    qColor = QtGui.QColor(255, 192, 203) # pink
                else:
                    qColor = QtGui.QColor(QtCore.Qt.white)
                #qBrush = QtGui.QBrush(qColor) 
                return qColor
        
        if role == QtCore.Qt.DisplayRole:
            
            if col == 0:
                if self.__localData[row].linkIt == True:
                    value = 1
                else:
                    value = 0
            else:
                value = self.__localData[row].getDataByColumn(col)
                
            if type(value) == str:
                return QtCore.QString(value)
            else:
                return value
            
        elif role == QtCore.Qt.TextAlignmentRole:
            if col == 0:
                return QtCore.Qt.AlignCenter
            # Check if we have right to left data in a column, if so align it right
            if col > 0 and len(self.__localData[row].getDataByColumn(col)) > 0 and unicodedata.bidirectional(\
              self.__localData[row].getDataByColumn(col)[0]) in (u'R', u'AL'): # check first character of the given cell
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter
    def flags(self, index):
        # Allow the user to type in column 0
        val = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled 
        if index.column() == 0 or index.column() == 4:
            val = val | QtCore.Qt.ItemIsEditable 
        return val
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:
                myVal = value.toInt()
                # make sure we have a target info.
                if myVal[0] >= 1 and self.__localData[row].get_tgtHPG() is not None:
                    linkIt = True
                else:
                    linkIt = False
                self.__localData[row].linkIt = linkIt
        return True
            
class Main(QtGui.QMainWindow):

    def __init__(self, myData, headerData, comboData):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        self.__model = LinkerTable(myData, headerData)
        self.ui.tableView.setModel(self.__model)
        self.__combo_model = LinkerCombo(comboData)
        self.ui.targetLexCombo.setModel(self.__combo_model)
        self.ret_val = 0
        self.cols = 7
        self.ui.targetLexCombo.currentIndexChanged.connect(self.ComboClicked)
        self.ui.FilterCheckBox.clicked.connect(self.FilterClicked)
        self.ComboClicked()
        
        myHPG = self.__combo_model.getCurrentHPG()
        myHeadword = myHPG.getHeadword()
        # Check for right to left data and set the combobox direction if needed
        for i in range(0, len(myHeadword)):
            if unicodedata.bidirectional(myHeadword[i]) in (u'R', u'AL'):
                self.ui.targetLexCombo.setLayoutDirection(QtCore.Qt.RightToLeft)
                self.__combo_model.setRTL(True)
                break
        
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        
        # Stretch the table view to fit
        self.ui.tableView.setGeometry(10, 50, self.width() - 20, \
                                      self.height() - 80 - self.ui.OKButton.height() - 25)
        
        # Move the OK and Cancel buttons as the window gets resized.
        x = self.width()/2 - 10 - self.ui.OKButton.width()
        if x < 0:
            x = 0
        self.ui.OKButton.setGeometry(x, 50 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                     self.ui.OKButton.height())
        self.ui.CancelButton.setGeometry(x + self.ui.OKButton.width() + 10,  \
                                         50 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                         self.ui.OKButton.height())
        # Set the column widths
        colCount = self.cols # self.ui.tableView.columnCount()
        colWidth = (self.ui.tableView.width() / colCount) - 3
        if colWidth < 40:
            colWidth = 40
        for i in range(0, colCount):
            self.ui.tableView.setColumnWidth(i, colWidth)
    def ComboClicked(self):
        # Set the target HPG for the model  
        myHPG = self.__combo_model.getCurrentHPG()
        self.__model.setSelectedHPG(myHPG)
    def OKClicked(self):
        self.ret_val = 1
        self.close()
    def FilterClicked(self):
        if self.ui.FilterCheckBox.isChecked():
            self.filter()
        else:
            self.unfilter()
    def CancelClicked(self):
        self.ret_val = 0
        self.close()
    def filter(self):
        # Save the full list
        self.__fullData = self.__model.getInternalData()
        
        # Create a new filtered list
        filteredData = []
        for myLink in self.__model.getInternalData():
            if myLink.get_tgtHPG() is None or myLink.suggestion:
                filteredData.append(myLink)
        self.__model.setInternalData(filteredData)
        self.rows = len(self.__model.getInternalData())
        #self.__model.modelReset() # causes crash
        self.setGeometry(self.x()+10,self.y()+10,self.width(),self.height()+1)
        self.ui.tableView
        self.ui.tableView.update()
        self.__model.resetInternalData()
        return
    def unfilter(self):
        self.__model.setInternalData(self.__fullData)
        self.setGeometry(self.x()+1,self.y()+1,self.width(),self.height()+1)
        self.ui.tableView.update()
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

def get_gloss_map(TargetDB, report, gloss_map, targetMorphNames, tgtLexList, scale_factor):

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
                # Get headword, POS, gloss
                headword = ITsString(e.HeadWord).Text
                if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                    POS = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                    Abbreviation.BestAnalysisAlternative).Text
                else:
                    POS = 'UNK'
                gloss = ITsString(mySense.Gloss.AnalysisDefaultWritingSystem).Text
                
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
    repo = TargetDB.db.ServiceLocator.GetInstance(ILexEntryRepository)
    guid = Guid(String(myGuid))

    try:
        targetEntry = repo.GetObject(guid)
    except:
        report.Error('Invalid guid or guid not found in target database. Guid: '+myGuid)
        return ret
    
    if targetEntry:
        
        targetHeadWord = ITsString(targetEntry.HeadWord).Text
        
        # Get the POS abbreviation for the target sense, assuming we have a stem
        if senseNum <= len(targetEntry.SensesOS.ToArray()):
            
            targetSense = targetEntry.SensesOS.ToArray()[senseNum-1]
            if targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                # TODO: verify PartOfSpeechRA is valid
                # Get target pos abbreviation and gloss
                POS = ITsString(targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                Abbreviation.BestAnalysisAlternative).Text
         
                Gloss = ITsString(targetSense.Gloss.AnalysisDefaultWritingSystem).Text
                
                # Create an HPG (headword-POS-gloss) object
                myHPG = HPG(targetSense, targetHeadWord, POS, Gloss, senseNum)
                
                ret = myHPG
    
    return ret

# do check for exact match and sometimes fuzzy match to find suggested 
# target senses to be linked to
def getMatchesOnGloss(gloss, gloss_map, save_map):
    matchList = []
    
    # check for exact match
    if gloss in gloss_map:
        matchList = gloss_map[gloss]
    else:    
        # See if we have a candidate for a fuzzy compare
        if len(gloss) >= MIN_GLOSS_LEN_FOR_FUZZ:
            # Loop through all the glosses
            for mgloss in gloss_map.keys():
                # See if we have a match
                if gloss not in save_map:
                    # Look for a match TODO: - maybe skip the fuzzy match if there's a big difference in length
                    if fuzz.QRatio(mgloss.lower(), gloss.lower()) > FUZZ_THRESHOLD:
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

    TargetDB = FLExDBAccess()

    # Open the target database
    targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
    if not targetProj:
        return
    
    # See if the target project is a valid database name.
    if targetProj not in DB.GetDatabaseNames():
        report.Error('The Target Database does not exist. Please check the configuration file.')
        return

    report.Info('Opening: '+targetProj+' as the target database.')

    try:
        TargetDB.OpenDatabase(targetProj, modify, verbose = True)
    except FDA_DatabaseError, e:
        report.Error(e.message)
        print "FDO Cache Create failed!"
        print e.message
        return

    preGuidStr = 'silfw://localhost/link?app%3dflex%26database%3d'
    preGuidStr += re.sub('\s','+', targetProj)
    preGuidStr += '%26server%3d%26tool%3dlexiconEdit%26guid%3d'
     
    save_map = {}
    gloss_map = {}
    processed_map = {}
    myData = []
    updated_senses = {}
    tgtLexList = []

    TargetDB_tot = TargetDB.LexiconNumberOfEntries()
    
    # count the number of "bundles" we will process for progress bar
    bundle_tot = 0
    for par in interlinText.ContentsOA.ParagraphsOS:
        for seg in par.SegmentsOS:
            bundle_tot += seg.AnalysesRS.Count
    
    #tot = bundle_tot+TargetDB_tot
    
    # We will scale the progress indication according to the following
    # weighting factors
    report.ProgressStart(100)
    ENTRIES_SCALE_FACTOR = 66.3333
    BUNDLES_SCALE_FACTOR = 33.3333
    
    entries_scale = int(TargetDB_tot/ENTRIES_SCALE_FACTOR)
    bundles_scale = int(bundle_tot/BUNDLES_SCALE_FACTOR)
    if entries_scale == 0:
    	entries_scale = 1
    if bundles_scale == 0:
    	bundles_scale = 1

    # Create a map of glosses to target senses and their number
    if not get_gloss_map(TargetDB, report, gloss_map, targetMorphNames, tgtLexList, entries_scale):
        return

    warning_list = []
    ss = SegmentServices.StTextAnnotationNavigator(interlinText.ContentsOA)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(int(ENTRIES_SCALE_FACTOR)+int(prog_cnt/bundles_scale))

        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            continue
        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = analysisOccurance.Analysis
        # We get into this block if there are no analyses for the word or a analysis suggestion hasn't been accepted.
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
            outStr = ITsString(analysisOccurance.Analysis.Form.BestVernacularAlternative).Text
            if outStr not in warning_list:
                report.Warning('No analysis found for the word: "'+ outStr + '". Skipping.')
                warning_list.append(outStr)
            continue
        else:
            wfiAnalysis = None
            
        # Go through each morpheme in the word (i.e. bundle)
        for bundle in wfiAnalysis.MorphBundlesOS:
            if bundle.SenseRA and bundle.MsaRA and bundle.MorphRA and bundle.MorphRA.Owner:
                # Get the LexEntry object, set a sense variable
                e = bundle.MorphRA.Owner
                mySense = bundle.SenseRA
                    
                # For a stem we just want the headword and it's POS
                if bundle.MsaRA.ClassName == 'MoStemMsa' and bundle.MorphRA:
                    # Follow variants back to an entry with a sense
                    e = GetEntryWithSense(e)    
                    
                    if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
                        # If we have processed this sense already, we will just re-add it to the list
                        if mySense not in processed_map:
                            # Get gloss
                            srcGloss = ITsString(mySense.Gloss.AnalysisDefaultWritingSystem).Text
    
                            # Get headword and set homograph # if necessary
                            srcHeadWord = ITsString(e.HeadWord).Text
                            
                            # Get the POS
                            if bundle.MsaRA.PartOfSpeechRA:
                                srcPOS =  ITsString(bundle.MsaRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                            else:
                                srcPOS = 'UNK'
                            
                            # Create a headword-POS-gloss object and initialize a Link object with this
                            # as the source sense info.
                            myHPG = HPG(mySense, srcHeadWord, srcPOS, srcGloss)
                            myLink = Link(myHPG)
                            
                            equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
                            senseNum = DB.LexiconGetFieldText(mySense.Hvo, senseNumField)

                            # equiv now holds the url to the target, see if it is valid
                            if equiv:
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
                                processed_map[mySense] = myLink
                                
                            else: # no link url present
                                # Find matches for the current gloss using fuzzy compare if needed
                                matchedSenseList = getMatchesOnGloss(srcGloss, gloss_map, save_map)
                                
                                # Process all the matches
                                if len(matchedSenseList) > 0:
                                    
                                    for i, matchHPG in enumerate(matchedSenseList):
                                        
                                        if i == 0: # use the Link object already created
                                            myLink.set_tgtHPG(matchHPG)
                                            matchLink = myLink
                                        else:
                                            matchLink = Link(myHPG, matchHPG)
                                        matchLink.suggestion = True
                                        myData.append(matchLink)
                                        processed_map[mySense] = matchLink
                                # No matches
                                else:
                                    # add a Link object that has no target information
                                    myData.append(myLink)
                                    processed_map[mySense] = myLink
                        else: # we've processed this sense before, add it to the list again
                            myLink = processed_map[mySense]
                            myData.append(myLink)
                                    
    # Check to see if there is any data to link
    if len(myData) == 0:
                                        
        report.Warning('There were no senses found for linking.')
    else:
    
        # Show the window
        app = QtGui.QApplication(sys.argv)
        
        myHeaderData = ["Link it", 'Source Head Word', 'Source Cat.', 'Source Gloss',  
                        'Target Head Word',  'Target Cat.', 'Target Gloss']
        
        tgtLexList.sort(key=lambda HPG: (HPG.getHeadword().lower(), HPG.getPOS().lower(), HPG.getGloss()))
        window = Main(myData, myHeaderData, tgtLexList)
        
        window.show()
        app.exec_()
        
        cnt = 0
        # Update the source database with the correct links
        if window.ret_val: # True = make the changes
            
            # Loop through the data
            for currLink in myData:
                
                # See if we have already updated this sense
                currSense = currLink.get_srcSense()
                if currSense not in updated_senses:
                    # Create a link if the user marked it for linking
                    if currLink.linkIt == True:
                        cnt += 1
                        # Build target link from saved url path plus guid string for this target sense
                        text = preGuidStr + currLink.get_tgtGuid() + '%26tag%3d'
                        
                        # Set the target field
                        DB.LexiconSetFieldText(currSense, senseEquivField, text)
                    
                        # Set the sense number if necessary
                        if currLink.get_tgtSenseNum() > 1:
                            DB.LexiconSetFieldText(currSense, senseNumField, str(currLink.get_tgtSenseNum()))
                    
                        updated_senses[currSense] = 1
                    
        report.Info(str(cnt)+' links created.')
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
