#
#   RunTreeTran
#
#   Ron Lockwood
#   SIL International
#   6/10/19
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 4/24/23 - Ron Lockwood
#    Constant for TreeTran.exe
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 9/3/22 - Ron Lockwood
#    Bump version number.
#
#   Version 3.5.1 - 7/9/22 - Ron Lockwood
#    Use a new config setting for the TreeTran rules path. Fixes #121.
#
#   Version 3.5 - 5/13/22 - Ron Lockwood
#    Look for the rules file in the project folder instead of Output
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Bump version number for FlexTools 3.2
#
#   Version 3.0.2 - 5/7/21 - Ron Lockwood
#    Give the user the # of sentences processed.
#
#   Version 3.0.1 - 2/24/21 - Ron Lockwood
#    Error message when config file not right.
#
#   Version 3.0 - 1/25/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0.1 - 1/22/20 - Ron Lockwood
#    Updated comments and documentation.
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.0 - 12/30/17 - Ron
#    Initial version.
#
# This module runs the TreeTran program which modifies a syntax tree. 
# See if we have a file for TreeTran output set in the configuration file. If not, 
# don't do anything. Then open Invoker.xml in the temp folder. It's possible that
# not all of the sentences were able to be parsed. So we need to filter out the
# sentences to just those that have a parse. Store the filtered file also in the
# temp folder.  Then run the treetran.exe program which lives in the FlexTools 
# folder giving it the rules file, the file with the sentences with valid parses
# and the output filename (from the config file) as parameters.


import os
import xml.etree.ElementTree as ET
import tempfile
from subprocess import call

from flextoolslib import *                                                 

import Utils
import ReadConfig
import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Run TreeTran",
        FTM_Version    : "3.9",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Run the TreeTran Tool.",    
        FTM_Help   : "",
        FTM_Description: 
"""
This module will run the TreeTran program to modify a syntax tree. The resulting
file is placed in the Output folder which is then used by the ExtractSourceText
module to modify the word order of the sentence according to the TreeTran rules
file. The TreeTran Rules file is in the Output folder also. This module assumes
that the invoker file Invoker.xml exists in the system temporary folder (%TEMP%). 
This file gets created by the PC-PATR with FLEx program when the tree toolbar
button is used. 
""" }
                 
INVOKER_FILE = 'Invoker.xml'   
VALID_PARSES_FILE = 'valid_parses_for_tree_tran.xml'

# Filter the invoker file down to just the sentences that have a syntax parse
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
    
    sentCount = 0
    
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
            sentCount += 1

    # Remove records if there's no analysis, i.e. no syntax parse
    for rec in deleteList:
        myRoot.remove(rec)
                
    f.close()
    
    # Get a path to the new file in the temp folder        
    filteredFileName = os.path.join(tempfile.gettempdir(), VALID_PARSES_FILE)
    
    # Write the new filter file
    myETree.write(filteredFileName, encoding='utf-8', xml_declaration=True)
        
    return filteredFileName, sentCount

#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if configMap is None:
        return

    # Check if we are using TreeTran for sorting the text output
    # If TreeTran is not being used the config file will have AnalyzedTextTreeTranOutputFile=
    # i.e. set to nothing
    treeTranResultFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, report)
    if not treeTranResultFile:
        report.Error(f'You have not specified a value in the configuration file for {ReadConfig.ANALYZED_TREETRAN_TEXT_FILE}.')
        return 
    
    # Create a path to the temporary folder + invoker file
    invokerFile = os.path.join(tempfile.gettempdir(), INVOKER_FILE)
    
    # Filter the invoker file down to just the sentences that have a syntax parse
    filteredFile, sentCount = filterAndLogInvokerParses(invokerFile)
    
    # verify the filtered file exists
    if os.path.exists(filteredFile) == False:
        report.Error('There is a problem with the TreeTran input file: '+filteredFile+'. Has the PC-PATR with FLEx program been run correctly?')
        return
    
    # Get the TreeTran rules file path
    treeTranRules = ReadConfig.getConfigVal(configMap, ReadConfig.TREETRAN_RULES_FILE, report)
    if not treeTranRules:
        report.Error(f'You have not specified a value in the configuration file for {ReadConfig.TREETRAN_RULES_FILE}.')
        return 
    
    # Get parent folder of the folder flextools.ini (Config) is in. This should give us the working project folder. E.g. German-Swedish
    # Assume that the rules file is in the folder.
    rulesFilePath = os.path.join(FTPaths.WORK_DIR, treeTranRules)

    # verify the filtered file exists
    if os.path.exists(rulesFilePath) == False:
        report.Error(f'Can\'t find the TreeTran rules file: {rulesFilePath}.')
        return
    
    # run TreeTran
    call([FTPaths.TREETRAN_EXE, rulesFilePath, filteredFile, treeTranResultFile])
    
    report.Info(str(sentCount) + ' sentence(s) processed.')
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
