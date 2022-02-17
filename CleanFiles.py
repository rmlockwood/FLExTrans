#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Remove generated files to force each FLExTrans module to regenerate everything.
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
        FTM_Version    : "3.4",
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
    
    # TODO: parameterize makefile for this
    bilingBinFile = re.sub('.dix', '.bin', bilingFile)
    try:
        os.remove(bilingBinFile)
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    bilingOldFile = re.sub('.dix', '.dix.old', bilingFile)
    try:
        os.remove(bilingOldFile)
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    try:
        os.remove(OUTPUT+'tr.t1x')
    except:
        pass # ignore errors

    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report)
    try:
        os.remove(affixFile)
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    try:
        os.remove(OUTPUT+f'{Utils.TRANSFER_RULE_FILE_PATH}.bin')
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    try:
        os.remove(OUTPUT+'apertium_log.txt')
    except:
        pass # ignore errors

    try:
        os.remove(Utils.APERTIUM_ERROR_FILE)
    except:
        pass # ignore errors

    try:
        os.remove(Utils.DO_MAKE_SCRIPT_FILE)
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
    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
