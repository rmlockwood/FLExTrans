#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Remove generated files to force each FLExTrans module to regenerate everything.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9.1 - 9/4/23 - Ron Lockwood
#    Fixes #487. Clean up synthesis test/generate files.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7 - 11/7/22 - Ron Lockwood
#    LiveRuleTester files weren't getting deleted. Delete advanced files.
#
#   Version 3.6 - 9/3/22 - Ron Lockwood
#    Fixes #235. Clean all STAMP files regardless of project name prefix.
#
#   Version 3.5 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.4.2 - 3/21/22 - Ron Lockwood
#    Handle when transfer rules file and testbed file locations are not set in
#    the configuration file. Issue #95. In fact always give no error when config file
#    entry is missing.
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
import re
from flextoolslib import *
import ReadConfig
import Utils
import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Remove generated files to force each FLExTrans module to regenerate everything. This typically removes most files in the Build and Output folders."
docs = {FTM_Name       : "Clean Files",
        FTM_Version    : "3.10",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Remove generated files to force each FLExTrans module to regenerate everything",
        FTM_Help  : "",  
        FTM_Description:    descr}     
#----------------------------------------------------------------

OUTPUT = "Output\\"

# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR
    buildFolder += '\\'
    
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report, giveError=False)
    try:
        os.remove(targetSynthesis)
    except:
        pass # ignore errors

    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report, giveError=False)
    try:
        os.remove(targetANA)
    except:
        pass # ignore errors

    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report, giveError=False)
    try:
        os.remove(transferResultsFile)
    except:
        pass # ignore errors

    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report, giveError=False)
    try:
        os.remove(outFileVal)
    except:
        pass # ignore errors
    
    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report, giveError=False)
    try:
        os.remove(bilingFile)
    except:
        pass # ignore errors
    
    # makefile uses this target so hard code it here
    try:
        os.remove(buildFolder+'bilingual.bin')
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
        os.remove(buildFolder+'tr.t1x')
        os.remove(buildFolder+'tr.t2x')
        os.remove(buildFolder+'tr.t3x')
    except:
        pass # ignore errors

    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False)
    try:
        os.remove(affixFile)
    except:
        pass # ignore errors
    
    # always delete transfer_rules.t1x.bin. This is what is in the Makefile
    try:
        os.remove(buildFolder+'transfer_rules.t1x.bin')
        os.remove(buildFolder+'transfer_rules.t2x.bin')
        os.remove(buildFolder+'transfer_rules.t3x.bin')
        os.remove(buildFolder+'target_text1.txt')
        os.remove(buildFolder+'target_text2.txt')
    except:
        pass # ignore errors
    
    # TODO: parameterize makefile for this
    try:
        os.remove(buildFolder+'apertium_log.txt')
    except:
        pass # ignore errors

    # old log file
    try:
        os.remove(buildFolder+'err_log')
    except:
        pass # ignore errors

    try:
        os.remove(buildFolder+Utils.APERTIUM_ERROR_FILE)
    except:
        pass # ignore errors

    # old error file
    try:
        os.remove(buildFolder+'err_out')
    except:
        pass # ignore errors

    try:
        os.remove(buildFolder+Utils.DO_MAKE_SCRIPT_FILE)
    except:
        pass # ignore errors
    
    tempPath = tempfile.gettempdir()
    
    # Remove target dictionary files
    stampFiles = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report, giveError=False)
    targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False)
    try:
        for p in Path(stampFiles).glob(targetProject+"*.*"):
            p.unlink()
    except:
        pass # ignore errors
    
    # Delete other dictionary files that could be there from copying and pasting a project folder
    try:
        for endStr in ['_ctrl_files.txt', '_outtx.ctl', '_sycd.chg', '_synt.chg', '_XXXtr.chg', \
                       '_if.dic', '_pf.dic', '_sf.dic', '_rt.dic', '_stamp.dec']:
            
            for p in Path(stampFiles).glob(f'*{endStr}'):
                p.unlink()
    except:
        pass # ignore errors
    

    try:
        for p in Path(stampFiles).glob(f"*{Utils.CONVERSION_TO_STAMP_CACHE_FILE}"):
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
        for p in Path(buildFolder+'LiveRuleTester').glob("*.*"):
            
            
            if re.search('Makefile', p.name):
                continue
            
            p.unlink()
    except:
        pass # ignore errors

    # Remove HermitCrab files
    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_CONFIG_FILE, report, giveError=False)
    try:
        os.remove(hcfile)
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_PARSES_FILE, report, giveError=False)
    try:
        os.remove(hcfile)
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_MASTER_FILE, report, giveError=False)
    try:
        os.remove(hcfile)
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE, report, giveError=False)
    try:
        os.remove(hcfile)
    except:
        pass # ignore errors

    # Remove Generate files
    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LOG_FILE, report, giveError=False)
    try:
        os.remove(genFile)
    except:
        pass # ignore errors

    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE, report, giveError=False)
    try:
        os.remove(genFile)
    except:
        pass # ignore errors

    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE, report, giveError=False)
    try:
        os.remove(genFile)
    except:
        pass # ignore errors



#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
