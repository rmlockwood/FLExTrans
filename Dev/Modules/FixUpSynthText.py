#
#   FixUpSynthText.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
#
#   Version 3.14 - 5/20/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 3/5/25 - Ron Lockwood
#   Fixes #909. Error messages when files don't exist.
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
#   Version 3.10.6 - 8/2/24 - Ron Lockwood
#    Use new function num Rules to get the number of rules.
#
#   Version 3.10.5 - 7/8/24 - Ron Lockwood
#    Use common code in InOutUtils for replacing text.
#
#   Version 3.10.2 - 7/1/24 - Ron Lockwood
#    Initial version.
#
#   Run a set of search and replace operations to fix up the text that comes out of 
#   synthesis. Regular expression can be used if desired.
#

import os
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

from flextoolslib import *                                          

import TextInOutUtils
import Mixpanel
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'FixUpSynthText'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'TextInOut', 'TextInOutUtils']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Fix Up Synthesis Text",
        FTM_Version    : "3.14",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("FixUpSynthText", 'Run a set of post-synthesis search and replace operations.') ,
        FTM_Help   : "",
        FTM_Description: _translate("FixUpSynthText", 
"""This module will run a set of search and replace operations to fix up the text that comes out of 
synthesis. The operations are defined with the Text Out Rules module. The rules are stored in the
Fix Up Synthesis Text Rules File as specified in the Settings.""")}

app.quit()
del app

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the search-replace rules file
    textOutRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TEXT_OUT_RULES_FILE, report, giveError=True)

    if not textOutRulesFile:
        return
    
    # Check if the file exists.
    if os.path.exists(textOutRulesFile) == False:

        report.Error(_translate("FixUpSynthText", "The rules file: {textOutRulesFile} could not be found. Use the Text Out Rules module to define the rules.").format(textOutRulesFile=textOutRulesFile))
        return
    
    # Get the path to the synthesis file.
    synthFile = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)

    if not synthFile:
        return 

    # Verify we have a valid text out rules file.
    try:
        tree = ET.parse(textOutRulesFile)
    except:
        report.Error(_translate("FixUpSynthText", "The rules file: {textOutRulesFile} has invalid XML data.").format(textOutRulesFile=textOutRulesFile))
        return 

    try:
        with open(synthFile, encoding='utf-8') as f:
        
            lines = f.readlines()
    except:
        report.Error(_translate("FixUpSynthText", "The Synthesize Text module must be run before this one. Could not open the synthesis file: '{synthFile}'.").format(synthFile=synthFile))
        return
    
    newLines = []

    newStr = ""
    
    for line in lines:

        # Do user-defined search/replace rules
        newStr, errMsg = TextInOutUtils.applySearchReplaceRules(line, tree)

        if newStr is None:

            report.Error(errMsg)
            break            

        newLines.append(newStr)

    f = open(synthFile, 'w', encoding='utf-8')
    f.writelines(newLines)
    f.close()
    
    if newStr:
        report.Info(_translate("FixUpSynthText", "The synthesis file was fixed using {numRules} 'Text Out' rules.").format(numRules=str(TextInOutUtils.numRules(tree))))

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
