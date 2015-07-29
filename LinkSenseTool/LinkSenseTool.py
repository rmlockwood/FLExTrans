#
#   LinkSenseTool
#
#   For a given text, see which senses have no link to a target sense. For 
#   those that don't have a link, propose possible target senses to link
#   to if the glosses for each match. Those chose for linking will have the
#   link custom field filled out.
#
#   Ron Lockwood
#   SIL International
#   7/18/15
#

from FTModuleClass import FlexToolsModuleClass
import ReadConfig
import os
import re
import tempfile
import sys

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Link Sense Tool",
        'moduleVersion'    : 1,
        'moduleModifiesDB' : True,
        'moduleSynopsis'   : "Link target and source senses.",
        'moduleDescription'   :
u"""
Link target and source senses.
""" }
                 
#----------------------------------------------------------------
# The main processing function

from SIL.FieldWorks.FDO import ILexPronunciation
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import ITextFactory, IStTextFactory, IStTxtParaFactory
from SIL.FieldWorks.FDO import ILexEntry, ILexSense
from SIL.FieldWorks.FDO import SpecialWritingSystemCodes
from SIL.FieldWorks.FDO.DomainServices import SegmentServices
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import IUndoStackManager
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
 
from PyQt4 import QtGui, QtCore
from Linker import Ui_MainWindow

class LinkerTable(QtCore.QAbstractTableModel):
    
    def __init__(self, myData = [[]], headerData = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__localData = myData
        self.__myHeaderData = headerData
        
    def rowCount(self, parent):
        return len(self.__localData)
    
    def columnCount(self, parent):
        return len(self.__localData[0]) 
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.__myHeaderData[section]
            else:
                return
                #return QtCore.QString("Row %1").arg(section)
            
    def data(self, index, role):
        row = index.row()
        col = index.column()
        
        if role == QtCore.Qt.EditRole:
            if col == 0:
                #return self.__localData[row][col][0]
                return 1 # default to 1 every time so the user can just double-click
        
        if role == QtCore.Qt.ForegroundRole:
            qColor = QtGui.QColor(QtCore.Qt.black)
            if row >= 0:
                if col == 1:
                    qColor = QtGui.QColor(QtCore.Qt.darkGreen)
                elif col == 4:
                    qColor = QtGui.QColor(QtCore.Qt.darkBlue)
                elif col == 3 or col == 6: #gram cat.
                    if self.__localData[row][3] != self.__localData[row][6]:
                        qColor = QtGui.QColor(QtCore.Qt.red)
                qBrush = QtGui.QBrush(qColor)
                return qBrush
        
        if role == QtCore.Qt.DisplayRole:
            #if row == 0 and col == 0:
                #self.__localData[col][row].setChecked()
                #self.__localData[col][row].setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
                #return
            
            if col == 0:
                value = self.__localData[row][col][0] # first part of the tuple
            else:
                value = self.__localData[row][col]
                
            if type(value) == str:
                return QtCore.QString(value)
            else:
                return value
        
    def flags(self, index):
        val = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled 
        if index.column() == 0:
            val = val | QtCore.Qt.ItemIsEditable 
        return val
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == 0:
                myVal = value.toInt()
                if myVal[0] >= 1:
                    newVal = 1
                elif myVal[0] <= 0:
                    newVal = 0
                ld = self.__localData[row][col]
                self.__localData[row][col] = (newVal, ld[1], ld[2], ld[3]) # link-it, sense #, sense, tgt guid
            else:
                self.__localData[row][col] = value
        return True
            
class Main(QtGui.QMainWindow):

    def __init__(self, myData, headerData):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        #self.ui.pushButton.clicked.connect(self.ButtonClicked)
        #myData = [[QtCore.QString("a"),QtCore.QString("b"),QtCore.QString("c")],[QtCore.QString("d"),QtCore.QString("e"),QtCore.QString("f")]]
        model = LinkerTable(myData, headerData)
        self.ui.tableView.setModel(model)
        self.ret_val = 0
        self.cols = len(myData[0])
        
    def resizeEvent(self, event):
        QtGui.QMainWindow.resizeEvent(self, event)
        
        # Stretch the table view to fit
        self.ui.tableView.setGeometry(10, 10, self.width() - 20, \
                                      self.height() - 20 - self.ui.OKButton.height() - 25)
        
        # Move the OK and Cancel buttons as the window gets resized.
        x = self.width()/2 - 10 - self.ui.OKButton.width()
        if x < 0:
            x = 0
        self.ui.OKButton.setGeometry(x, 10 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                     self.ui.OKButton.height())
        self.ui.CancelButton.setGeometry(x + self.ui.OKButton.width() + 10,  \
                                         10 + self.ui.tableView.height() + 10, self.ui.OKButton.width(),
                                         self.ui.OKButton.height())
        # Set the column widths
        colCount = self.cols # self.ui.tableView.columnCount()
        colWidth = (self.ui.tableView.width() / colCount) - 1
        if colWidth < 10:
            colWidth = 10
        for i in range(0, colCount):
            self.ui.tableView.setColumnWidth(i, colWidth)
        
    def OKClicked(self):
        self.ret_val = 1
        self.close()
      
    def CancelClicked(self):
        self.ret_val = 0
        self.close()
      
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
                    e = entryRef.ComponentLexemesRS.ToArray()[0]
                    continue
        notDoneWithVariants = False
    return e

def get_sense_map(DB, report, sense_map, sourceMorphNames, senseEquivField, preGuidStrList):
    
    got_url = False
    
    # Loop through all the entries
    for entry_cnt,e in enumerate(DB.LexiconAllEntries()):
    
        report.ProgressUpdate(entry_cnt)
        
        # Don't process affixes, clitics
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and ITsString(e.LexemeFormOA.\
           MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
        
            # Loop through senses
            for mySense in e.SensesOS:
                
                # Check if there is a value in the link field
                equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
                if equiv != None:
                    sense_map[mySense] = 1
                    
                    # Do a one time parse of a link to get the url
                    if not got_url:
                        u = equiv.index('guid')
                        preGuidStrList.append(equiv[:u+7])
                        got_url = True
                else:
                    sense_map[mySense] = 0
    
    if got_url:        
        return True
    else:
        report.Error('You need to have at least one sense linked already so this tool can get the link path.')
        return False

def get_gloss_map(DB, report, gloss_map, targetMorphNames, first_tot):

    # Loop through all the target entries
    for entry_cnt,e in enumerate(DB.LexiconAllEntries()):
    
        report.ProgressUpdate(entry_cnt+first_tot)
        
        # Don't process affixes, clitics
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and ITsString(e.LexemeFormOA.\
           MorphTypeRA.Name.BestAnalysisAlternative).Text in targetMorphNames:
        
            # Loop through senses
            for senseNum, mySense in enumerate(e.SensesOS):
                
                gloss = ITsString(mySense.Gloss.AnalysisDefaultWritingSystem).Text
                
                if len(gloss) > 0:
                    if gloss not in gloss_map:
                        gloss_map[gloss] = [(mySense, senseNum+1)]
                    else:
                        gloss_map[gloss].append((mySense, senseNum+1))
                        
    return True
                        
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

    if not text_desired_eng and linkField and numField and text_desired_eng and sourceMorphNames:
        return
    
    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    senseNumField = DB.LexiconGetSenseCustomFieldNamed(numField)
    
    # Find the desired text
    foundText = False
    for text in DB.ObjectsIn(ITextRepository):
        if text_desired_eng == ITsString(text.Name.BestAnalysisAlternative).Text:
            foundText = True
            break;
        
    if not foundText:
        report.Error('The text named: '+text_desired_eng+' not found.')
        return

    TargetDB = FLExDBAccess()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenDatabase(targetProj, modify, verbose = True)
    except FDA_DatabaseError, e:
        report.Error(e.message)
        print "FDO Cache Create failed!"
        print e.message
        return

    report.Info('Using: '+targetProj+' as the target database.')

    sense_map = {}
    gloss_map = {}
    processed_map = {}
    myData = []
    preGuidStrList = []

    DB_tot = DB.LexiconNumberOfEntries()
    TargetDB_tot = TargetDB.LexiconNumberOfEntries()
    tot = DB_tot+TargetDB_tot
    DB_pct = float(DB_tot)/tot
    TargetDB_pct = float(TargetDB_tot)/tot
    report.ProgressStart(tot)
    
    # Create a map of senses and whether they have a target link
    if not get_sense_map(DB, report, sense_map, sourceMorphNames, senseEquivField, preGuidStrList):
        return
    
    # Create a map of glosses to target senses and their number
    if not get_gloss_map(TargetDB, report, gloss_map, targetMorphNames, DB_tot):
        return

    warning_list = []
    ss = SegmentServices.StTextAnnotationNavigator(text.ContentsOA)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
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
            if bundle.SenseRA:
                if bundle.MsaRA:
                    # Get the LexEntry object
                    e = bundle.MorphRA.Owner
                        
                    # For a stem we just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':
                        
                        if bundle.MorphRA:
                            
                            # Follow variants back to an entry with a sense
                            e = GetEntryWithSense(e)    
                            
                            # Go through each sense and identify which sense number we have
                            foundSense = False
                            for mySense in e.SensesOS:
                                if mySense.Guid == bundle.SenseRA.Guid:
                                    foundSense = True
                                    break
                            if not foundSense:
                                report.Warning("Couldn't find the sense for headword: "+ITsString(e.HeadWord).Text)    

                            if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
                            
                                # Get gloss
                                srcGloss = ITsString(mySense.Gloss.AnalysisDefaultWritingSystem).Text

                                # Get headword and set homograph # if necessary
                                srcHeadWord = ITsString(e.HeadWord).Text
                                #srcHeadWord = add_one(srcHeadWord)
                                
                                # Get the POS
                                if bundle.MsaRA.PartOfSpeechRA:
                                    srcPOS =  ITsString(bundle.MsaRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                                else:
                                    srcPOS = 'UNK'
                                
                                if not sense_map[mySense] and srcGloss in gloss_map and mySense not in processed_map:
                                
                                    for (tgtSense, tgtSenseNum) in gloss_map[srcGloss]:
                                        
                                        # Get target gloss
                                        tgtGloss = ITsString(tgtSense.Gloss.AnalysisDefaultWritingSystem).Text
                                        
                                        # Get target POS
                                        if tgtSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                                            tgtPOS = ITsString(tgtSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                               Abbreviation.AnalysisDefaultWritingSystem).Text
                                        else:
                                            tgtPOS = 'UNK'
                                            
                                        # Get target headword
                                        tgtHeadword = ITsString(tgtSense.OwningEntry.HeadWord).Text
                                        #tgtHeadword = add_one(tgtHeadword)
                                            
                                        # Add to the data table
                                        myData.append([(0, tgtSenseNum, mySense, tgtSense.Guid), srcHeadWord, 
                                                      srcGloss, srcPOS, tgtHeadword, tgtGloss, tgtPOS])
                                    
                                processed_map[mySense] = 1 

    # Check to see if there is any data to link
    if len(myData) == 0:
                                        
        report.Warning('There were no senses found for linking.')
    else:
    
        # Show the window
        app = QtGui.QApplication(sys.argv)
        
        myHeaderData = ["Link it", 'Source Head Word', 'Source Gloss', 'Source Cat.', 
                        'Target Head Word', 'Target Gloss', 'Target Cat.']
        window = Main(myData, myHeaderData)
        
        window.show()
        app.exec_()
        
        cnt = 0
        # Update the source database with the correct links
        if window.ret_val: # True = make the changes
            
            # Loop through the data
            for row in myData:
                
                # See if the user wanted to create a link for this row
                if row[0][0]: # 1st tuple element
                    cnt += 1
                    # Build target link from saved url path plus guid string for this target sense
                    text = preGuidStrList[0] + row[0][3].ToString() + '%26tag%3d'
                    # Set the target field
                    DB.LexiconSetFieldText(row[0][2], senseEquivField, text)
                    
                    # Set the sense number
                    if row[0][1] > 1:
                        DB.LexiconSetFieldText(row[0][2], senseNumField, str(row[0][1]))
            
            
        report.Info(str(cnt)+' links created.')
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
