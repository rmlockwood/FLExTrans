#
#   FixUpSynthText.py
#
#   Ron Lockwood
#   SIL International
#   7/1/24
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
import regex
import xml.etree.ElementTree as ET

from flextoolslib import *                                          

import ReadConfig
import TextInOutUtils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Fix Up Synthesis Text",
        FTM_Version    : "3.11.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : 'Run a set of post-synthesis search and replace operations.' ,
        FTM_Help   : "",
        FTM_Description: 
"""
This module will run a set of search and replace operations to fix up the text that comes out of 
synthesis. The operations are defined with the Text Out Rules module. The rules are stored in the
Fix Up Synthesis Text Rules File as specified in the Settings.
"""}

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the search-replace rules file
    textOutRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TEXT_OUT_RULES_FILE, report, giveError=True)

    if not textOutRulesFile:
        return
    
    # Check if the file exists.
    if os.path.exists(textOutRulesFile) == False:

        report.Error(f'The rules file: {textOutRulesFile} could not be found. Use the Text Out Rules module to define the rules.')
        return
    
    # Get the path to the synthesis file.
    synthFile = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)

    if not synthFile:
        return 

    # Verify we have a valid transfer file.
    try:
        tree = ET.parse(textOutRulesFile)
    except:
        report.Error(f'The rules file: {textOutRulesFile} has invalid XML data.')
        return 

    f = open(synthFile, encoding='utf-8')
    lines = f.readlines()
    f.close()
    
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
        report.Info(f"The synthesis file was fixed using {str(TextInOutUtils.numRules(tree))} 'Text Out' rules.")

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
