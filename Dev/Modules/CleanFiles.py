#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Version 3.17.1 - 9/29/26 - Ron Lockwood
#    Fixes #1334. Glob on the bare target project name so dictionary files are cleaned when the target is a .fwdata path. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.3 - 7/27/26 - Ron Lockwood
#    Don't delete a transfer changes file (_XXXtr.chg) that has content in it. The user may have put STAMP changes into it by hand.
#
#   Version 3.16.2 - 7/2/26 - Ron Lockwood
#    Silenced type-checker warnings on os.remove/glob calls and guarded the bilingual backup regex against a None path.
#
#   Version 3.16.1 - 6/28/26 - Ron Lockwood
#    Handle one project (two writing systems) mode - dictionary files are named after the source project.
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
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
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
#   OVERVIEW (AI generated, then edited)
#
#   This module deletes the files that the other FLExTrans modules generate, so that the next run of each module has to regenerate everything from scratch. Many steps in FLExTrans skip work when
#   their output looks current: the Apertium makefile rebuilds only targets older than their inputs, the STAMP and HermitCrab lexicon extraction reuse cached files when the FLEx project hasn't
#   changed, and the testbed and STAMP conversion keep cache files. When a setting changes, a project is swapped, or a project folder is copied, those timestamps can lie and stale output gets used.
#   Clean Files is the "start over" button for that. It never touches the FLEx projects and it doesn't delete anything the user authors (transfer rules, testbed, replacement dictionary, etc.).
#
#   WHAT IT DELETES
#
#    - Files whose paths come from settings: the synthesis output, target .ana file, transfer results, analyzed text, bilingual dictionary and its .dix.old backup, target affix gloss list, the four
#      HermitCrab files (config, parses, master, surface forms) and the three synthesis test (Generate) output files.
#    - Files with hard-coded names in the Build folder that the makefile or other modules use: bilingual.bin, tr.t1x-t3x, transfer_rules.t1x-t3x.bin, target_text1/2.txt, the Apertium log and error
#      files (plus the names used by older versions), the do-make script and the Rule Assistant GUI input and test/display data files.
#    - The target dictionary files in the Target Lexicon Files Folder: everything starting with the target project name, plus any file ending in one of the STAMP dictionary/control suffixes whatever
#      its prefix (these turn up when a project folder has been copied and pasted), plus the STAMP conversion cache.
#    - The testbed cache file in the system temp folder, and every file in Build/LiveRuleTester except the Makefile.
#
#   WHICH PROJECT NAME THE DICTIONARY FILES USE
#
#   The target dictionary files are named after a bare project name, so that is what gets globbed. In Two project mode the TargetProject setting may be a bare name or the full path of a .fwdata
#   file outside the standard FLEx Projects folder (#1334); Utils.targetProjectDisplayName() reduces a path to the bare name, since globbing on the path would match nothing. In One project mode
#   there is no target project and the dictionary files are named after the source project, so DB.ProjectName() is used instead.
#
#   TRAPS
#
#    - Every removal is wrapped in a try with a bare except that ignores the error, because a missing file is the normal case (a module that hasn't been run yet, a setting that isn't set).
#      That also means nothing is reported when a delete genuinely fails, e.g. because a file is open in another program.
#    - A few try blocks remove several files in a row (tr.t1x-t3x, and the transfer_rules.t?x.bin / target_text1/2.txt group). If an early file in the group is missing the rest of that group
#      is skipped too, so a project with no tr.t1x keeps its tr.t2x. Give each file its own try if this ever matters.
#    - A setting that isn't present comes back as None; os.remove(None) or None + "*.*" raises inside the try and is silently skipped, which is the intended behavior.
#
#   CODE STRUCTURE
#
#   After the docs dictionary there is only MainFunction(), which FlexTools calls. It reads the settings, logs to Mixpanel, and then deletes the files in this order: the setting-based and
#   makefile files, the target dictionary files, the cache files, the LiveRuleTester folder, the HermitCrab files, the Generate files and finally the Rule Assistant files. The FlexToolsModule
#   declaration is at the bottom.
#

import os
from pathlib import Path
import tempfile
import re

from flextoolslib import * # type: ignore

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QTranslator

import Mixpanel
import ReadConfig
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'CleanFiles'

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
docs = {FTM_Name       : _translate("CleanFiles", "Clean Files"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("CleanFiles", "Remove generated files to force each FLExTrans module to regenerate everything"),
        FTM_Help       : "",  
        FTM_Description: _translate("CleanFiles",
"""Remove generated files to force each FLExTrans module to regenerate everything. This typically removes most files in the Build and Output folders.""")}

#app.quit()
#del app

# Return True if this is a transfer changes file (_XXXtr.chg) that has content in it. Such a file must not be deleted, because the user may have put STAMP changes
# into it by hand, e.g. changes that produce the ambiguities that the Disambiguate Synthesized Text module works with. An empty one is fine to delete since
# DoStampSynthesis recreates it blank as needed. If the file can't be read, play it safe and treat it as having content.
def isNonEmptyTransferChangesFile(path):

    if not path.name.endswith('_XXXtr.chg'):

        return False

    try:
        return path.read_text(encoding='utf-8').strip() != ''

    except OSError:
        return True

# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR
    buildFolder += '\\'
    
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report, giveError=False)
    try:
        os.remove(targetSynthesis)  # type: ignore
    except:
        pass # ignore errors

    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report, giveError=False)
    try:
        os.remove(targetANA)  # type: ignore
    except:
        pass # ignore errors

    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report, giveError=False)
    try:
        os.remove(transferResultsFile) # type: ignore
    except:
        pass # ignore errors

    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report, giveError=False)
    try:
        os.remove(outFileVal) # type: ignore
    except:
        pass # ignore errors
    
    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report, giveError=False)
    try:
        os.remove(bilingFile) # type: ignore
    except:
        pass # ignore errors
    
    # makefile uses this target so hard code it here
    try:
        os.remove(buildFolder+'bilingual.bin')
    except:
        pass # ignore errors
    
    # remove bilingual dictionary backup file
    bilingOldFile = re.sub(r'\.dix', '.dix.old', bilingFile) if bilingFile else ''
    try:
        os.remove(bilingOldFile) # type: ignore
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
        os.remove(affixFile) # type: ignore
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
        os.remove(buildFolder+Utils.APERTIUM_ERROR_FILE) # type: ignore
    except:
        pass # ignore errors

    # old error file
    try:
        os.remove(buildFolder+'err_out')
    except:
        pass # ignore errors

    try:
        os.remove(buildFolder+Utils.DO_MAKE_SCRIPT_FILE) # type: ignore
    except:
        pass # ignore errors
    
    tempPath = tempfile.gettempdir()
    
    # Remove target dictionary files
    stampFiles = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report, giveError=False)

    # In one project (two writing systems) mode the dictionary files are named after the source project (there is no separate target project), so glob on the source project name.
    oneProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) == 'n'

    if oneProjectMode:

        targetProject = DB.ProjectName()
    else:
        # The setting may be the full path of a .fwdata file; the dictionary files are named after the bare project name.
        targetProject = Utils.targetProjectDisplayName(ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False))
    try:

        for p in Path(stampFiles).glob(targetProject+"*.*"):  # type: ignore

            # Keep a transfer changes file that the user has put content into
            if isNonEmptyTransferChangesFile(p):
                continue

            p.unlink()

    except:
        pass # ignore errors
    
    # Delete other dictionary files that could be there from copying and pasting a project folder
    try:

        for endStr in ['_ctrl_files.txt', '_outtx.ctl', '_sycd.chg', '_synt.chg', '_XXXtr.chg', \
                       '_if.dic', '_pf.dic', '_sf.dic', '_rt.dic', '_stamp.dec']:

            for p in Path(stampFiles).glob(f'*{endStr}'):  # type: ignore

                # Keep a transfer changes file that the user has put content into
                if isNonEmptyTransferChangesFile(p):
                    continue

                p.unlink()

    except:
        pass # ignore errors
    

    try:
        for p in Path(stampFiles).glob(f"*{Utils.CONVERSION_TO_STAMP_CACHE_FILE}"):  # type: ignore
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
        os.remove(hcfile) # type: ignore
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_PARSES_FILE, report, giveError=False)
    try:
        os.remove(hcfile) # type: ignore
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_MASTER_FILE, report, giveError=False)
    try:
        os.remove(hcfile) # type: ignore
    except:
        pass # ignore errors

    hcfile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE, report, giveError=False)
    try:
        os.remove(hcfile) # type: ignore
    except:
        pass # ignore errors

    # Remove Generate files
    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_LOG_FILE, report, giveError=False)
    try:
        os.remove(genFile) # type: ignore
    except:
        pass # ignore errors

    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_PARSES_OUTPUT_FILE, report, giveError=False)
    try:
        os.remove(genFile) # type: ignore
    except:
        pass # ignore errors

    genFile = ReadConfig.getConfigVal(configMap, ReadConfig.SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE, report, giveError=False)
    try:
        os.remove(genFile) # type: ignore
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
