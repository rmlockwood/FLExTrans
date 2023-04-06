#
#   RunApertium
#
#   Ron Lockwood
#   SIL International
#   1/1/17
#
#   Version 3.7.1 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   Version 3.7 - 11/7/22 - Ron Lockwood
#   Move strip rules function to Utils
#
#   Version 3.6.3 - 10/25/22 - Ron Lockwood
#   Strip advanced rule files if they exist. Error handling if can't open file to strip.
#
#   Version 3.6.2 - 10/19/22 - Ron Lockwood
#    Fixes #244. Give a warning if an attribute matches a grammatical category.
#
#   Version 3.6.1 - 9/2/22 - Ron Lockwood
#    Fixes #255. Convert slashes in symbols before running Apertium
#
#   Version 3.6 - 8/11/22 - Ron Lockwood
#    Fixes #198. Warn the user for periods in attribute definitions.
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    Changes to support the Windows version of the Apertium tools. Fixes #143.
#    Run a function called stripRulesFile to remove DocType from the transfer 
#    rules file before applying aperitum tools.
#
#   Version 3.5 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.4.1 - 3/5/22 - Ron Lockwood
#    Use a config file setting for the transfer rules file. Make it an 
#    environment variable that the makefile can use.
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
#   Version 3.0 - 1/25/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.1.1 2/28/2018 - Ron Lockwood
#      Fixed typo. Use report.Error instead of report.error
#
#   Version 1.1 1/9/2018 - Ron Lockwood
#      Use absolute paths and moved most of the code into Utils.
#
#   Version 1.0 10/10/2017 - Marc Penner
#      Extracted call to run Apertium commands
#
#   Runs the makefile that calls Apertium 
#

import Utils
import ReadConfig
import os
import re
import unicodedata
from flextoolslib import *
from FTPaths import CONFIG_PATH

#----------------------------------------------------------------
# Documentation that the user sees:
descr = """This module executes lexical transfer based on links from source to target sense you have established and then executes structural transfer which
runs the transfer rules you have made to transform source morphemes into target morphemes.
"""
docs = {FTM_Name       : "Run Apertium",
        FTM_Version    : "3.7",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Run the Apertium transfer engine.",
        FTM_Help  : "",  
        FTM_Description:    descr}     

STRIPPED_RULES  = 'tr.t1x'
STRIPPED_RULES2 = 'tr.t2x'
STRIPPED_RULES3 = 'tr.t3x'

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = os.path.join(os.path.dirname(os.path.dirname(CONFIG_PATH)), Utils.BUILD_FOLDER)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return True

    # Get the path to the dictionary file
    dictionaryPath = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not dictionaryPath:
        return True
    
    # Get the path to the target apertium file
    transferResultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    if not transferResultsPath:
        return True
    
    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)
    if not tranferRulePath:
        return True

    # Create stripped down transfer rules file that doesn't have the DOCTYPE stuff
    if Utils.stripRulesFile(report, buildFolder, tranferRulePath, STRIPPED_RULES) == True:
        return True
    
    ## Advanced transfer files
    
    # Get the path to the 2nd transfer rules file (could be blank)
    tranferRulePath2 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE2, report, giveError=False)
    if tranferRulePath2:

        # Create stripped down transfer rules file that doesn't have the DOCTYPE stuff
        if Utils.stripRulesFile(report, buildFolder, tranferRulePath2, STRIPPED_RULES2) == True:
            return True

    # Get the path to the 3rd transfer rules file (could be blank)
    tranferRulePath3 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE3, report, giveError=False)
    if tranferRulePath3:

        # Create stripped down transfer rules file that doesn't have the DOCTYPE stuff
        if Utils.stripRulesFile(report, buildFolder, tranferRulePath3, STRIPPED_RULES3) == True:
            return True

    # Check if attributes are well-formed. Warnings will be reported in the function
    error_list = Utils.checkRuleAttributes(tranferRulePath)

    Utils.processErrorList(report, error_list)

    # Fix problem characters in symbols of the bilingual lexicon (making a backup copy of the original file)
    subPairs = Utils.fixProblemChars(dictionaryPath)
    
    # Substitute symbols with problem characters with fixed ones in the transfer file
    Utils.subProbSymbols(buildFolder, STRIPPED_RULES, subPairs)
    
    # Run the makefile to run Apertium tools to do the transfer component of FLExTrans. 
    ret = Utils.run_makefile(buildFolder, report)
    
    if ret:
        report.Error('An error happened when running the Apertium tools. The contents of apertium_error.txt is:')
        try:
            f = open(os.path.join(buildFolder, Utils.APERTIUM_ERROR_FILE), encoding='utf-8')
            lines = f.readlines()
            report.Error('\n'.join(lines))
        except:
            pass

    # Convert back the problem characters in the transfer results file back to what they were. Restore the backup biling. file
    Utils.unfixProblemCharsRuleFile(transferResultsPath)
    Utils.unfixProblemCharsDict(dictionaryPath)

    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
