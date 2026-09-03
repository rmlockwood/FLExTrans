#
#   RuleFileHistory
#
#   Ron Lockwood
#   SIL International
#   9/2/26
#
#   Version 3.17.1 - 9/2/26 - Ron Lockwood
#    Initial version. The one place that knows where saved copies of the transfer rules file go and what they are named.
#
#   OVERVIEW
#
#   Every part of FLExTrans that is about to change the transfer rules file, or that wants a record of the rules that produced a given result, saves a timestamped copy of the file through this
#   module. All of those copies land in one folder, Output\rule-file-history, and each name carries a tag saying what saved it, so the whole history of a project's rules is one sorted listing
#   instead of a folder per producer plus a scattering of .bak files beside the rules file itself. Nothing in FLExTrans ever deletes these copies; they are small and the user can prune the folder
#   by hand whenever they like.
#
#   A name looks like <stem>_<YYYY-MM-DD_HH-MM-SS>_<tag><extension> - for example transfer_rules_2026-09-02_14-35-01_testbed_run.t1x. The date leads the tag so that the folder sorts
#   chronologically, and the original extension stays last so that a copy still opens in XMLmind XML Editor when it is double-clicked.
#
#   FLExTrans 3.17 used a different layout - Output\rule-history, with a subfolder per producer instead of a tag in each file name. Bringing one of those folders forward is the whole job of
#   Lib/OldRuleHistoryConversion.py, which is meant to be deleted once nobody is upgrading from that version any more. Nothing here knows about it.
#
#   This module is deliberately free of Qt, FLEx and flextoolslib imports so that AIRules.py - which is Qt-free by design so that it can be used and tested standalone - can call it.

import os
import shutil
from datetime import datetime

import FTPaths

# The folder every saved copy goes in.
HISTORY_DIR_NAME = 'rule-file-history'

# Tags saying what saved a copy. They go on the end of the file name, after the date and time. Keep them short, lower case and free of spaces - they end up in a file name.
TAG_TEST_ADDED        = 'test_added'
TAG_TESTBED_RUN       = 'testbed_run'
TAG_BEFORE_RA_CHANGES = 'before_RA_changes'
TAG_BEFORE_AI_CHANGES = 'before_AI_changes'
TAG_BEFORE_CAT_SETUP  = 'before_cat_setup'

# The date-time stamp every producer uses, so that one directory listing sorts chronologically no matter what saved each copy. Dashes, not colons, because a colon can't go in a Windows file name.
STAMP_FORMAT = '%Y-%m-%d_%H-%M-%S'

def getHistoryDir():
    '''Return the folder that saved copies of the transfer rules file go in. This is a function and not a module level constant so that FTPaths.OUTPUT_DIR is read when a copy is saved rather than
       when this module is imported, which is also what lets a unit test point the whole thing at a temporary folder.'''

    return os.path.join(FTPaths.OUTPUT_DIR, HISTORY_DIR_NAME)

def saveHistoryCopy(rulesFile, tag):
    '''Save a copy of the transfer rules file at rulesFile in the rule file history folder, named <stem>_<date>_<time>_<tag><extension>. tag says what is saving the copy; use one of the TAG_
       constants. Returns (path of the copy, error message). The path is None and the error message empty when there was nothing to copy, so a project with no transfer rules file yet is not an
       error. On failure the path is None and the error message says what went wrong. This never raises, so a caller can treat saving a copy as best effort.'''

    if not rulesFile or not os.path.isfile(rulesFile):

        return None, ''

    stem, extension = os.path.splitext(os.path.basename(rulesFile))
    destPath = os.path.join(getHistoryDir(), f'{stem}_{datetime.now().strftime(STAMP_FORMAT)}_{tag}{extension}')

    # Saving a copy is never the thing the user actually asked for, so a full disk or a locked folder gives the caller a message to report instead of ending the module part way through its work.
    try:
        os.makedirs(getHistoryDir(), exist_ok=True)
        shutil.copy2(rulesFile, destPath)

    except OSError as err:

        return None, str(err)

    return destPath, ''

def saveHistoryCopies(rulesFiles, tag):
    '''Save a copy of each of the transfer rules files in rulesFiles under the one tag, for the two producers that record every phase of an advanced (three phase) project rather than just the main
       rules file. Returns (list of the paths saved, error message), where the message is the first failure so that one bad copy is reported without abandoning the rest. All of the copies made by
       one call share a tag but not necessarily a stamp, since each is stamped as it is saved.'''

    destPaths = []
    firstError = ''

    for rulesFile in rulesFiles:

        destPath, errorMsg = saveHistoryCopy(rulesFile, tag)

        if destPath:

            destPaths.append(destPath)

        elif errorMsg and not firstError:

            firstError = errorMsg

    return destPaths, firstError
