#
#   CleanFiles
#
#   Ron Lockwood
#   SIL International
#   11/25/2021
#
#   Version 3.17.2 - 10/13/26 - Ron Lockwood
#    Offer to delete old backup copies and old testbed results (6, 12 or 24 months, newest 50 kept) when 100 are over a year old, at most every 3 months.
#
#   Version 3.17.1 - 9/29/26 - Ron Lockwood
#    Fixes #1334. Glob on the bare target project name so dictionary files are cleaned when the target is a .fwdata path. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
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
#   It also does a second, separate job: housekeeping for the things that pile up over the life of a project. After the generated files are gone it offers - each in its own window, and only now and
#   then - to delete old backup copies of the transfer rules and testbed files, and then old runs from the testbed results file. See DELETING OLD ITEMS below.
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
#   DELETING OLD ITEMS
#
#   Every tool that changes the transfer rules file or the testbed file saves a dated copy first, in Output\rule-file-history and Output\testbed-file-history, and every testbed run adds a whole
#   copy of the testbed to the testbed results file. None of that is generated output that a rerun would recreate, so it is never deleted without asking. The user picks an age - 6, 12 or
#   24 months, with 24 selected to begin with - or says No. The rule, in Lib/DeleteOldFilesDlg.py, is that an item goes only if it is older than the chosen age AND is not one of the newest 50 in
#   its group, so a project that has sat untouched for two years still keeps its last 50. For the backup copies a group is all the copies of one file (the testbed, transfer_rules.t1x, and the
#   .t2x and .t3x of an advanced project), so each keeps 50; the results file is one group.
#
#    - A backup copy's date is read from its name (RuleFileHistory.parseHistoryFileName), not its modified time, which shutil.copy2 carried over from the original file. A file in those folders
#      whose name doesn't parse is not a copy FLExTrans made, so it is left alone.
#    - A testbed run's date is its startDateTime. A run whose date can't be read is left alone.
#    - Clean Files is run often, so the window only opens when at least 100 items are over a year old and the user wasn't asked in the last 3 months (DeleteOldFilesDlg.shouldAsk()). The
#      last-asked date is kept per project in Config\OldFileCleanup.toml, and is recorded when the window opens, so saying No starts the 3 months just as Yes does. The details are in WHEN TO ASK
#      in DeleteOldFilesDlg.py.
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
#   After the docs dictionary come the functions for deleting old items: copyCountText() and runCountText() word the counts beside each age, then offerToDeleteOldBackupCopies() and offerToDeleteOldTestbedResults(),
#   which each gather their dated items, open DeleteOldFilesDlg if there is anything to offer, and delete what the user agreed to. MainFunction(), which FlexTools calls, reads the settings, logs to
#   Mixpanel, and then deletes the files in this order: the setting-based and makefile files, the target dictionary files, the cache files, the LiveRuleTester folder, the HermitCrab files, the
#   Generate files and the Rule Assistant files. Last it calls the two offer functions. The FlexToolsModule declaration is at the bottom.
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
import RuleFileHistory
import Testbed
import DeleteOldFilesDlg

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
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'Testbed', 'DeleteOldFilesWindow']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("CleanFiles", "Clean Files"),
        FTM_Version    : "3.17.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("CleanFiles", "Remove generated files to force each FLExTrans module to regenerate everything"),
        FTM_Help       : "",  
        FTM_Description: _translate("CleanFiles",
"""Remove generated files to force each FLExTrans module to regenerate everything. This typically removes most files in the Build and Output folders. It also offers to delete old backup copies of the transfer rules and testbed files and old testbed results, always keeping the newest 50.""")}

#app.quit()
#del app

def copyCountText(count):
    '''The text shown beside an age in the window for backup copies: how many copies that age would delete.'''

    if count == 1:

        return _translate("CleanFiles", "1 copy")

    return _translate("CleanFiles", "{count} copies").format(count=count)

def runCountText(count):
    '''The text shown beside an age in the window for testbed results: how many runs that age would delete.'''

    if count == 1:

        return _translate("CleanFiles", "1 result")

    return _translate("CleanFiles", "{count} results").format(count=count)

def offerToDeleteOldBackupCopies(report):
    '''Ask whether to delete old backup copies of the transfer rules and testbed files, and delete the ones the user agrees to. Does nothing, and asks nothing, unless DeleteOldFilesDlg.shouldAsk()
       says it is time to ask.'''

    # Gather the copies in both history folders, grouped by the file each is a copy of. The folder is part of the key so that a rules file and a testbed file that happen to share a stem stay apart.
    groups = {}

    for historyDir in [RuleFileHistory.getHistoryDir(), Testbed.getTestbedHistoryDir()]:

        try:
            fileNames = os.listdir(historyDir)

        except OSError:

            # No folder yet just means nothing has been saved there
            continue

        for fileName in fileNames:

            parsed = RuleFileHistory.parseHistoryFileName(fileName)
            path = os.path.join(historyDir, fileName)

            # Leave alone anything FLExTrans didn't name, and any sub-folder
            if not parsed or not os.path.isfile(path):

                continue

            stem, savedAt, _tag, extension = parsed
            groups.setdefault((historyDir, stem.lower(), extension.lower()), []).append((savedAt, path))

    datedGroups = list(groups.values())

    # Only ask when a real batch is over a year old and the user wasn't asked recently
    if not DeleteOldFilesDlg.shouldAsk(datedGroups, DeleteOldFilesDlg.readLastAsked(DeleteOldFilesDlg.LAST_ASKED_BACKUP_COPIES)):

        return

    # Record the date before asking, so that a No starts the cooldown just as a Yes does
    DeleteOldFilesDlg.saveLastAsked(DeleteOldFilesDlg.LAST_ASKED_BACKUP_COPIES)

    ageCounts = DeleteOldFilesDlg.countOldItems(datedGroups)
    totalCount = sum(len(group) for group in datedGroups)
    message = _translate("CleanFiles", "FLExTrans saves a backup copy of the transfer rules file or the testbed file each time it changes one of them. There are {total} of these copies in the Output folder, and some of them are old.\n\nDo you want to delete the old copies? The newest {keep} copies of each file are always kept, however old they are.").format(total=totalCount, keep=DeleteOldFilesDlg.KEEP_NEWEST)

    dlg = DeleteOldFilesDlg.DeleteOldFilesDlg(_translate("CleanFiles", "Delete Old Backup Copies"), message, ageCounts, copyCountText)
    dlg.exec()

    if dlg.chosenMonths is None:

        report.Info(_translate("CleanFiles", "No backup copies were deleted."))
        return

    deletedCount = 0
    failedCount = 0
    firstError = ''

    # Keep going past a copy that can't be deleted (open in another program, say), and report the failures together at the end
    for path in DeleteOldFilesDlg.selectOldItems(datedGroups, dlg.chosenMonths):

        try:
            os.remove(path)
            deletedCount += 1

        except OSError as err:

            failedCount += 1
            firstError = firstError or str(err)

    report.Info(_translate("CleanFiles", "Old backup copies deleted: {count}.").format(count=deletedCount))

    if failedCount:

        report.Warning(_translate("CleanFiles", "Old backup copies that could not be deleted: {count}. The first error was: {errorText}").format(count=failedCount, errorText=firstError))

def offerToDeleteOldTestbedResults(configMap, report):
    '''Ask whether to delete old runs from the testbed results file, and delete the ones the user agrees to. Does nothing, and asks nothing, unless DeleteOldFilesDlg.shouldAsk() says
       it is time to ask.'''

    resultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TESTBED_RESULTS_FILE, report, giveError=False)

    try:
        resultsTree, datedResults = Testbed.loadDatedTestbedResults(resultsPath)

    except ValueError as err:

        report.Warning(str(err))
        return

    if resultsTree is None:

        return

    # Only ask when a real batch is over a year old and the user wasn't asked recently
    if not DeleteOldFilesDlg.shouldAsk([datedResults], DeleteOldFilesDlg.readLastAsked(DeleteOldFilesDlg.LAST_ASKED_TESTBED_RESULTS)):

        return

    # Record the date before asking, so that a No starts the cooldown just as a Yes does
    DeleteOldFilesDlg.saveLastAsked(DeleteOldFilesDlg.LAST_ASKED_TESTBED_RESULTS)

    ageCounts = DeleteOldFilesDlg.countOldItems([datedResults])
    message = _translate("CleanFiles", "The testbed log holds the results of {total} testbed runs, and some of them are old.\n\nDo you want to delete the old results? The newest {keep} results are always kept, however old they are.").format(total=len(datedResults), keep=DeleteOldFilesDlg.KEEP_NEWEST)

    dlg = DeleteOldFilesDlg.DeleteOldFilesDlg(_translate("CleanFiles", "Delete Old Testbed Results"), message, ageCounts, runCountText)
    dlg.exec()

    if dlg.chosenMonths is None:

        report.Info(_translate("CleanFiles", "No testbed results were deleted."))
        return

    oldResults = DeleteOldFilesDlg.selectOldItems([datedResults], dlg.chosenMonths)

    # resultsPath is set, since loadDatedTestbedResults() returns no tree without it
    assert resultsPath is not None

    try:
        Testbed.removeTestbedResults(resultsTree, oldResults, resultsPath)

    except OSError as err:

        report.Error(_translate("CleanFiles", "The old testbed results could not be deleted. The error was: {errorText}").format(errorText=str(err)))
        return

    report.Info(_translate("CleanFiles", "Old testbed results deleted: {count}.").format(count=len(oldResults)))

# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR
    buildFolder += '\\'
    
    # Load the translations for the libraries this module uses, which includes the window that offers to delete old items
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True)

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
            p.unlink()
    except:
        pass # ignore errors
    
    # Delete other dictionary files that could be there from copying and pasting a project folder
    try:
        for endStr in ['_ctrl_files.txt', '_outtx.ctl', '_sycd.chg', '_synt.chg', '_XXXtr.chg', \
                       '_if.dic', '_pf.dic', '_sf.dic', '_rt.dic', '_stamp.dec']:
            
            for p in Path(stampFiles).glob(f'*{endStr}'):  # type: ignore
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

    # Housekeeping for things that pile up rather than get regenerated. Each asks first, and only now and then (see DeleteOldFilesDlg.shouldAsk()).
    offerToDeleteOldBackupCopies(report)
    offerToDeleteOldTestbedResults(configMap, report)

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
