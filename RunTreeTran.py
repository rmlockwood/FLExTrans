#
#   RunTreeTran
#
#   Ron Lockwood
#   SIL International
#   6/10/19
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.0 - 12/30/17 - Ron
#    Initial version.
#
# This module runs the TreeTran program which modifies a syntax tree. 


import Utils
import ReadConfig
import os
import re
import xml.etree.ElementTree as ET
import tempfile
import sys
import shutil
import unicodedata
from subprocess import call
from FTModuleClass import FlexToolsModuleClass
from FTModuleClass import *                                                 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Run TreeTran",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Run the TreeTran Tool.",    
        FTM_Help   : "",
        FTM_Description: 
u"""
This module will run the TreeTran program to modify a syntax tree. The resulting
file is placed in the Output folder which is then used by the ExtractSourceText
module to modify the word order of the sentence according to the TreeTran rules
file. The TreeTran Rules file is in the Output folder also.
""" }
                 
TREE_TRAN_RULES = 'tree_tran_rules.xml'
INVOKER_FILE = 'Invoker.xml'   
VALID_PARSES_FILE = 'valid_parses_for_tree_tran.xml'

def filterAndLogInvokerParses(inputFilename):
    
    recsInSent = []
    deleteList = []
    wordCount = 0
    f = open(os.path.join(tempfile.gettempdir(), Utils.GOOD_PARSES_LOG), 'w')
    
    try:
        myETree = ET.parse(inputFilename)
    except:
        raise ValueError('The Tree Tran Result File has invalid XML content.' + ' (' + inputFilename + ')')
    
    myRoot = myETree.getroot()
    
    # Loop through the anaRec's 
    for anaRec in myRoot:
        
        wordCount += 1
        
        recsInSent.append(anaRec)

        # get the analysis node if it exists
        analysisNode = anaRec.find('Analysis')
        if analysisNode != None:
            # Set parsed flag.
            if analysisNode.attrib['count'] == '0':
                # add this list of records (the whole sentence) to the deletion list
                deleteList.extend(recsInSent)
                
                parsedFlag = '0'
            else:
                parsedFlag = '1'
                
            # Log the # words and whether it parsed
            f.write(str(wordCount)+','+parsedFlag+'\n')
                
            # reset the sentence list
            recsInSent = []
            wordCount = 0

    # Remove records if there's no analysis, i.e. no syntax parse
    for rec in deleteList:
        myRoot.remove(rec)
                
    f.close()
    
    # Get a path to the new file in the temp folder        
    filteredFileName = os.path.join(tempfile.gettempdir(), VALID_PARSES_FILE)
    
    # Write the new filter file
    myETree.write(filteredFileName, encoding='utf-8', xml_declaration=True)
        
    return filteredFileName

#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Check if we are using TreeTran for sorting the text output
    treeTranResultFile = unicode(ReadConfig.getConfigVal(configMap, 'AnalyzedTextTreeTranOutputFile', report), "utf-8")
    if not treeTranResultFile:
        return 
    
    # Create a path to the temporary folder + invoker file
    invokerFile = os.path.join(tempfile.gettempdir(), INVOKER_FILE)
    
    # Filter the invoker file down to just the sentences that have a syntax parse
    filteredFile = filterAndLogInvokerParses(invokerFile)
    
    # verify the invoker file exists
    if os.path.exists(filteredFile) == False:
        report.Error('There is a problem with the TreeTran input file: '+filteredFile+'. Has the PC-PATR with FLEx program been run correctly?')
        return

    # run TreeTran
    call(['treetran.exe', Utils.OUTPUT_FOLDER+'\\'+TREE_TRAN_RULES, filteredFile, treeTranResultFile])
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
