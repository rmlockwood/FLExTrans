#
#   RunTreeTran
#
#   Ron Lockwood
#   SIL International
#   6/10/19
#
#   Version 3.17.1 - 10/20/26 - Ron Lockwood
#    Fixes #1639. Run TreeTran with CREATE_NO_WINDOW so no console window flashes when FLExTrans runs under pyw. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.1 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
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
#   OVERVIEW (AI generated, then edited)
#
#   This module runs the external TreeTran program, which rewrites syntax trees according to a rules file so that ExtractSourceText can reorder the words of each sentence to match the
#   target language. It is the bridge between PC-PATR with FLEx (which produces the parses) and the rest of the FLExTrans pipeline (which consumes TreeTran's reordered result).
#
#   THE FILES
#
#   Input: Invoker.xml in the system temp folder (%TEMP%). PC-PATR with FLEx writes it when the user clicks its tree toolbar button; this module does not create it, so it must exist
#   before the module runs. Rules: the TreeTran rules file named by the TreeTranRulesFile setting, looked up relative to the work project folder (FTPaths.WORK_DIR).
#   Output: the file named by the AnalyzedTextTreeTranOutputFile setting, which ExtractSourceText reads next. If that setting is empty the module reports an error and stops.
#
#   FILTERING
#
#   Not every sentence in Invoker.xml necessarily got a syntax parse, and TreeTran can only work on parsed sentences. filterAndLogInvokerParses() therefore removes every sentence
#   whose closing anaRec has an Analysis with count="0" and writes the rest to valid_parses_for_tree_tran.xml in the temp folder. A sentence is the run of anaRecs up to and including
#   the one carrying an Analysis element, so all of its records are dropped together. As it goes, it logs one "word count,parsed flag" line per sentence to Utils.GOOD_PARSES_LOG
#   in the temp folder.
#
#   RUNNING TREETRAN
#
#   TreeTran is a console program. FLExTrans normally runs under pyw, which has no console, so the call passes CREATE_NO_WINDOW; without it Windows would open a console window
#   for TreeTran that can flash on screen (issue #1639). The module doesn't check TreeTran's exit code; it reports the number of parsed sentences it handed over.
#
#   CODE STRUCTURE
#
#   docs (the FlexTools module description) and the module-level translation loading come first, then filterAndLogInvokerParses() (the filtering above), then MainFunction(), which
#   reads the settings, calls filterAndLogInvokerParses(), checks the rules file exists, runs TreeTran and reports the sentence count. FlexToolsModule wires MainFunction into FlexTools.
#

import os
import xml.etree.ElementTree as ET
import tempfile
from subprocess import call, CREATE_NO_WINDOW

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from flextoolslib import * # type: ignore

import Mixpanel
import Utils
import ReadConfig
import FTPaths
from ExtractSourceText import docs as ExtractSourceTextDocs

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RunTreeTran'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("RunTreeTran", "Run TreeTran"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RunTreeTran", "Run the TreeTran Tool."),
        FTM_Help       : "",
        FTM_Description: _translate("RunTreeTran",
"""This module will run the TreeTran program to modify a syntax tree. The resulting
file is placed in the Output folder which is then used by the {extractSourceTextModule}
module to modify the word order of the sentence according to the TreeTran rules
file. The TreeTran Rules file is in the Output folder also. This module assumes
that the invoker file Invoker.xml exists in the system temporary folder (%TEMP%). 
This file gets created by the PC-PATR with FLEx program when the tree toolbar
button is used. """).format(extractSourceTextModule=ExtractSourceTextDocs[FTM_Name])}

#app.quit()
#del app

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
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

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
        report.Error(_translate("RunTreeTran", 'There is a problem with the TreeTran input file: {filteredFile}. Has the PC-PATR with FLEx program been run correctly?').format(filteredFile=Utils.shortenPathForDisplay(filteredFile)))
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
        report.Error(_translate("RunTreeTran", 'Can\'t find the TreeTran rules file: {rulesFilePath}.').format(rulesFilePath=Utils.shortenPathForDisplay(rulesFilePath)))
        return
    
    # Run TreeTran. CREATE_NO_WINDOW because FLExTrans runs under pyw, which has no console, so Windows would otherwise open a console window for TreeTran that can flash on screen.
    call([FTPaths.TREETRAN_EXE, rulesFilePath, filteredFile, treeTranResultFile], creationflags=CREATE_NO_WINDOW)
    
    report.Info(_translate("RunTreeTran", '{num} sentence(s) processed.').format(num=str(sentCount)))
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
