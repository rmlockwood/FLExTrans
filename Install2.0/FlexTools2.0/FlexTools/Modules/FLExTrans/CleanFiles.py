#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Remove generated files to force each FLExTrans module to regenerate everything.
#
#   Version 3.4.1 - 3/5/22 - Ron Lockwood
#    Makefile paramaterized to use setting in the config file. But many things
#    to delete are in the Makefile as outputs, so just hard code them here.
#    Remove nearly all files from the LiveRuleTester folder
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use the config file to find file names to clean up.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 11/25/2021 - Ron Lockwood
#

import os
from pathlib import Path
import tempfile
from FTModuleClass import *
import ReadConfig
import Utils
import re

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Remove generated files to force each FLExTrans module to regenerate everything."
docs = {FTM_Name       : "Clean Files",
        FTM_Version    : "3.4.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : descr,
        FTM_Help  : "Remove generated files to force each FLExTrans module to regenerate everything.",  
        FTM_Description:    descr}     
#----------------------------------------------------------------

OUTPUT = "Output\\"

# The main processing function
def MainFunction(DB, report, modify=True):
    
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    try:
        os.remove(targetSynthesis)
    except:
        pass # ignore errors

    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    try:
        os.remove(targetANA)
    except:
        pass # ignore errors

    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    try:
        os.remove(transferResultsFile)
    except:
        pass # ignore errors

    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    try:
        os.remove(outFileVal)
    except:
        pass # ignore errors
    
    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    try:
        os.remove(bilingFile)
    except:
        pass # ignore errors
    
    # makefile uses this target so hard code it here
    try:
        os.remove(OUTPUT+'bilingual.bin')
    except:
        pass # ignore errors
    
    # remove bilingual dictionary backup file
    bilingOldFile = re.sub('.dix', '.dix.old', bilingFile)
    try:
        os.remove(bilingOldFile)
    except:
        pass # ignore errors
    
    # makefile uses this target so hard code it here
    try:
        os.remove(OUTPUT+'tr.t1x')
    except:
        pass # ignore errors

    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report)
    try:
        os.remove(affixFile)
    except:
        pass # ignore errors
    
    # always delete transfer_rules.t1x.bin. This is what is in the Makefile
    try:
        os.remove(OUTPUT+'transfer_rules.t1x.bin')
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    try:
        os.remove(OUTPUT+'apertium_log.txt')
    except:
        pass # ignore errors

    # old log file
    try:
        os.remove(OUTPUT+'err_log')
    except:
        pass # ignore errors

    try:
        os.remove(OUTPUT+Utils.APERTIUM_ERROR_FILE)
    except:
        pass # ignore errors

    # old error file
    try:
        os.remove(OUTPUT+'err_out')
    except:
        pass # ignore errors

    try:
        os.remove(OUTPUT+Utils.DO_MAKE_SCRIPT_FILE)
    except:
        pass # ignore errors
    
    tempPath = tempfile.gettempdir()
    
    # Remove target dictionary files
    try:
        for p in Path(tempPath).glob("*_rt.dic"):
            p.unlink()
    except:
        pass # ignore errors
    
    try:
        for p in Path(tempPath).glob(f"*{Utils.CONVERSION_TO_STAMP_CACHE_FILE}"):
            p.unlink()
    except:
        pass # ignore errors
    
    try:
        for p in Path(tempPath).glob(f"*{Utils.TESTBED_CACHE_FILE}"):
            p.unlink()
    except:
        pass # ignore errors
    
    # Remove files in the LiveRuleTester folder
    try:
        for p in Path('.').glob(f"{OUTPUT}LiveRuleTester\\*"):
            
            
            if re.search('fix.py', p.name) or re.search('Makefile', p.name):
                continue
            
            p.unlink()
    except:
        pass # ignore errors
    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
