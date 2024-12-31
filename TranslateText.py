#
#   TranslateText
#
#   Ron Lockwood
#   SIL International
#   12/31/24
#
#   Version 3.12 - 12/31/24 - Ron Lockwood
#    Initial version.
#
#
# This module does everything in the Drafting collection in one go. 


import os
import re
import sys
from unicodedata import normalize

from System import Int32 # type: ignore
from flextoolslib import *                                                 
from flexlibs import AllProjectNames
from SIL.LCModel import ( # type: ignore
    IMoAdhocProhibGrRepository, 
    IMoStemMsa, 
    IMoUnclassifiedAffixMsa, 
    IMoDerivAffMsa, 
    IMoInflAffMsa,
    IMoAlloAdhocProhibFactory,
    IMoMorphAdhocProhibFactory,
    IMoAdhocProhibGrFactory,
    IMoMorphSynAnalysis,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QCompleter

from ClusterAdHoc import Ui_AdHocMainWindow
from ComboBox import CheckableComboBox
import FTPaths
import ReadConfig
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Translate Text",
        FTM_Version    : "3.12",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Translate the current source text.",    
        FTM_Help   : "",
        FTM_Description: 
"""
Translate the current source text.
""" }

def extractSourcText(DB, configMap, report):

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not outFileVal:
        return
    
    fullPathTextOutputFile = outFileVal
    
    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: '+fullPathTextOutputFile+'. Please check the configuration file setting.')
        return
    
    # Find the desired text
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceTextName:
        return
    
    matchingContentsObjList = []

    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    
    if sourceTextName not in sourceTextList:
        
        report.Error('The text named: '+sourceTextName+' not found.')
        return
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceTextName)]
    
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
            f_treeTranResultFile = open(treeTranResultFile)
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
            
    # Process the text
    report.Info("Exporting analyses...")

    # Get various bits of data for the get interlinear function
    interlinParams = Utils.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return

    # Get interlinear data. A complex text object is returned.
    myText = Utils.getInterlinData(DB, report, interlinParams)
        
    # Write out all the words
    myText.write(f_out)
    
    report.Info("Exported: " + str(myText.getSentCount()) + " sentence(s).")
        
    f_out.close()

    report.Info("Export of " + sourceTextName + " complete.")


#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])





    # Get the cluster projects
    projects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report)
    if not projects:
        return
        
    composed = ReadConfig.getConfigVal(configMap, ReadConfig.COMPOSED_CHARACTERS, report)
    composed = (composed == 'y')

    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
