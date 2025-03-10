#
#   RunApertium
#
#   Ron Lockwood
#   SIL International
#   1/1/17
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
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 5/1/23 - Ron Lockwood
#    Set the modified date of the internally used tr1.t1x file to be the same as
#    the transfer_rules.t1x (or whatever the user specified) so that the transfer rules are
#    only recompiled when the rules are out of date.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7.1 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   earlier version history removed on 3/5/25
#
#   Runs the makefile that calls Apertium 
#

import Utils
import ReadConfig
import os
from flextoolslib import *
import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:
descr = """This module executes lexical transfer based on links from source to target sense you have established and then executes structural transfer which
runs the transfer rules you have made to transform source morphemes into target morphemes.
"""
docs = {FTM_Name       : "Run Apertium",
        FTM_Version    : "3.13",
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
    buildFolder = FTPaths.BUILD_DIR

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return True

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the dictionary file
    dictionaryPath = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not dictionaryPath:
        return True
    
    # See if the dictionary file exists.
    if not os.path.exists(dictionaryPath):
        report.Error('The bilingual dictionary file does not exist. You may need to run the Build Bilingual Lexicon module. The file should be: ' + dictionaryPath)
        return True
    
    # Get the path to the analyzed text
    analyzedTextPath = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not analyzedTextPath:
        return True
    
    # See if the source text file exists.
    if not os.path.exists(analyzedTextPath):
        report.Error('The analyzed text file does not exist. You may need to run the Extract Source Text module. The file should be: ' + analyzedTextPath)
        return True
    
    # Get the path to the target apertium file
    transferResultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    if not transferResultsPath:
        return True
    
    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)
    if not tranferRulePath:
        return True

    # Get the modification date of the transfer rule file.
    statResult = os.stat(tranferRulePath)

    # Escape some characters and write as NFD unicode.
    if Utils.stripRulesFile(report, buildFolder, tranferRulePath, STRIPPED_RULES) == True:
        return True
    
    ## Advanced transfer files
    
    # Get the path to the 2nd transfer rules file (could be blank)
    tranferRulePath2 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE2, report, giveError=False)
    if tranferRulePath2:

        # Escape some characters and write as NFD unicode.
        if Utils.stripRulesFile(report, buildFolder, tranferRulePath2, STRIPPED_RULES2) == True:
            return True

    # Get the path to the 3rd transfer rules file (could be blank)
    tranferRulePath3 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE3, report, giveError=False)
    if tranferRulePath3:

        # Escape some characters and write as NFD unicode.
        if Utils.stripRulesFile(report, buildFolder, tranferRulePath3, STRIPPED_RULES3) == True:
            return True

    # Check if attributes are well-formed. Warnings will be reported in the function
    error_list = Utils.checkRuleAttributes(tranferRulePath)

    Utils.processErrorList(error_list, report)

    # Fix problem characters in symbols of the bilingual lexicon (making a backup copy of the original file)
    subPairs = Utils.fixProblemChars(dictionaryPath)
    
    # Substitute symbols with problem characters with fixed ones in the transfer file
    Utils.subProbSymbols(buildFolder, STRIPPED_RULES, subPairs)
    
    # Set the modification date to be the same as the original rules file so that the makefile that runs the Apertium tools
    # won't recompile the transfer_rules if they are not out of date.
    os.utime(os.path.join(buildFolder, STRIPPED_RULES), times=None, ns=(statResult.st_atime_ns, statResult.st_mtime_ns))

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
