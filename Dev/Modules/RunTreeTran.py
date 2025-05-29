#
#   RunTreeTran
#
#   Ron Lockwood
#   SIL International
#   6/10/19
#
#   Version 3.14 - 5/27/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
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
#   earlier version history removed on 3/10/25
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

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from flextoolslib import *                                                 

import Mixpanel
import Utils
import ReadConfig
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RunTreeTran'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Run TreeTran",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RunTreeTran", "Run the TreeTran Tool."),    
        FTM_Help   : "",
        FTM_Description: _translate("RunTreeTran",  
"""This module will run the TreeTran program to modify a syntax tree. The resulting
file is placed in the Output folder which is then used by the ExtractSourceText
module to modify the word order of the sentence according to the TreeTran rules
file. The TreeTran Rules file is in the Output folder also. This module assumes
that the invoker file Invoker.xml exists in the system temporary folder (%TEMP%). 
This file gets created by the PC-PATR with FLEx program when the tree toolbar
button is used. """)}

app.quit()
del app

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
        raise ValueError(_translate("RunTreeTran", 'The Tree Tran Result File has invalid XML content.') + ' (' + inputFilename + ')')
    
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
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if configMap is None:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Check if we are using TreeTran for sorting the text output
    # If TreeTran is not being used the config file will have AnalyzedTextTreeTranOutputFile=
    # i.e. set to nothing
    treeTranResultFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, report)
    if not treeTranResultFile:
        report.Error(_translate("RunTreeTran", 'You have not specified a value in the configuration file for {file}.').format(file=ReadConfig.ANALYZED_TREETRAN_TEXT_FILE))
        return 
    
    # Create a path to the temporary folder + invoker file
    invokerFile = os.path.join(tempfile.gettempdir(), INVOKER_FILE)
    
    # Filter the invoker file down to just the sentences that have a syntax parse
    filteredFile, sentCount = filterAndLogInvokerParses(invokerFile)
    
    # verify the filtered file exists
    if os.path.exists(filteredFile) == False:
        report.Error(_translate("RunTreeTran", 'There is a problem with the TreeTran input file: {filteredFile}. Has the PC-PATR with FLEx program been run correctly?').format(filteredFile=filteredFile))
        return
    
    # Get the TreeTran rules file path
    treeTranRules = ReadConfig.getConfigVal(configMap, ReadConfig.TREETRAN_RULES_FILE, report)
    if not treeTranRules:
        report.Error(_translate("RunTreeTran", 'You have not specified a value in the configuration file for {file}.').format(file=ReadConfig.TREETRAN_RULES_FILE))
        return 
    
    # Get parent folder of the folder flextools.ini (Config) is in. This should give us the working project folder. E.g. German-Swedish
    # Assume that the rules file is in the folder.
    rulesFilePath = os.path.join(FTPaths.WORK_DIR, treeTranRules)

    # verify the filtered file exists
    if os.path.exists(rulesFilePath) == False:
        report.Error(_translate("RunTreeTran", 'Can\'t find the TreeTran rules file: {rulesFilePath}.').format(rulesFilePath=rulesFilePath))
        return
    
    # run TreeTran
    call([FTPaths.TREETRAN_EXE, rulesFilePath, filteredFile, treeTranResultFile])
    
    report.Info(_translate("RunTreeTran", '{num} sentence(s) processed.').format(num=str(sentCount)))
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
