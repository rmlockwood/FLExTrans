#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Remove generated files to force each FLExTrans module to regenerate everything.
#
#   Version 3.13.1 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 1/6/25 - Ron Lockwood
#    Clean up more Rule Assistant files.
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
#   earlier version history removed on 3/10/25
#

import os
from pathlib import Path
import tempfile
import re

from flextoolslib import *

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

import ReadConfig
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate

app = QApplication([])
translatorForGlobals = QTranslator()

if translatorForGlobals.load(f"CleanFiles_{Utils.getInterfaceLangCode()}.qm", FTPaths.TRANSL_DIR):

    QCoreApplication.installTranslator(translatorForGlobals)

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Clean Files",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("CleanFiles", "Remove generated files to force each FLExTrans module to regenerate everything"),
        FTM_Help  : "",  
        FTM_Description: _translate("CleanFiles",
"""Remove generated files to force each FLExTrans module to regenerate everything. This typically removes most files in the Build and Output folders.""")}

app.quit()
del app

# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR
    buildFolder += '\\'
    
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

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

    # GUI input file for Rule Assistant
    try:
        os.remove(os.path.join(buildFolder, Utils.RA_GUI_INPUT_FILE))
    except:
        pass # ignore errors
    try:
        os.remove(os.path.join(buildFolder, Utils.RULE_ASSISTANT_SOURCE_TEST_DATA_FILE))
    except:
        pass # ignore errors
    try:
        os.remove(os.path.join(buildFolder, Utils.RULE_ASSISTANT_TARGET_TEST_DATA_FILE))
    except:
        pass # ignore errors
    try:
        os.remove(os.path.join(buildFolder, Utils.RULE_ASSISTANT_DISPLAY_DATA_FILE))
    except:
        pass # ignore errors

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
