#
#   OldRuleHistoryConversion
#
#   Ron Lockwood
#   SIL International
#   9/2/26
#
#   Version 3.16.1 - 9/2/26 - Ron Lockwood
#    Initial version. Brings a leftover rule-history folder from an earlier version into the rule file history folder.
#
#   TEMPORARY - THIS WHOLE MODULE IS MEANT TO BE DELETED
#
#   Earlier versions saved their copies of the transfer rules file in Output\\rule-history, with a 'created' subfolder for the Live Rule Tester's copies and a 'run' subfolder for Start Testbed's, instead
#   of one folder with a tag in each file name. This module exists only to bring such a folder forward, and is needed only for as long as people are still upgrading from one of those versions - a
#   few months, or a year at the outside. Nothing else depends on it, and none of its messages are translated, deliberately, so that it costs nothing to throw away.
#
#   TO REMOVE IT, delete this file and the two calls to it - one line each, both marked with the comment 'TEMPORARY (old rule history conversion)':
#    - Modules/StartTestbed.py     - the call in MainFunction and its import.
#    - Modules/LiveRuleTesterTool.py - the call in MainFunction and its import.
#   Also delete unit_tests/test_OldRuleHistoryConversion.py, and drop this file from the exclude_files list in Dev\\compile_transl.bat and the other four translation batch files.
#   Nothing in Lib/RuleFileHistory.py has to change - it knows nothing about the old layout.
#
#   WHAT IT DOES
#
#   Each file in the old folder is copied into the rule file history folder under the name the new scheme would have given it, and then the old folder is moved whole into
#   rule-file-history\\old with a note saying what happened. Nothing is deleted, so a user who is unhappy with the result still has everything they had, and can delete the 'old'
#   folder themselves once they are satisfied. Running it again after a successful conversion costs one look at the file system.
#
#   Deliberately free of Qt, FLEx and flextoolslib imports, both so that it can be unit tested on its own and so that removing it can't disturb anything else.

import os
import shutil
from datetime import datetime

import FTPaths
import RuleFileHistory

# The folder earlier versions used, where its contents go, and the note left with them.
OLD_HISTORY_DIR_NAME = 'rule-history'
OLD_FOLDER_NAME      = 'old'
CONVERSION_NOTE_NAME = 'README-old-rule-history.txt'
NOTE_TEXT            = 'rule-history and its contents are the old structure. Each file has been converted to an equivalent name and copied to the new structure.'

# The old date-time stamp, read so that it can be written out again in RuleFileHistory.STAMP_FORMAT.
OLD_STAMP_FORMAT = '%Y%m%d_%H%M%S'

# The copies the old 'created' subfolder held were saved every time Transfer was pressed in the Live Rule Tester, not when a test was added to the testbed, so relabelling them test_added would say
# something about them that isn't true. They get a tag of their own, which nothing new ever produces. The subfolder name is also the infix in the old file names.
TAG_RULE_TESTED    = 'rule_tested'
OLD_SUBFOLDER_TAGS = {'created': TAG_RULE_TESTED, 'run': RuleFileHistory.TAG_TESTBED_RUN}

def convert(report):
    '''Bring a leftover Output\\rule-history folder forward and tell the user what happened. Cheap and safe to call at the start of any module: a project that never used the old layout, or that has
       already been converted, costs one look at the file system. Nothing is ever deleted and nothing raises, so a failure leaves the user exactly where they were and is reported as a warning.'''

    oldDir = os.path.join(FTPaths.OUTPUT_DIR, OLD_HISTORY_DIR_NAME)

    # The normal case, and the only one left once everybody has upgraded.
    if not os.path.isdir(oldDir):

        return

    holdingDir = os.path.join(RuleFileHistory.getHistoryDir(), OLD_FOLDER_NAME)
    destDir = os.path.join(holdingDir, OLD_HISTORY_DIR_NAME)

    # An old layout folder has appeared again after a conversion - an older FLExTrans was run in this project, or a backup was restored over it. Stamp the destination so that the move can't land
    # inside the folder that is already there, which is what shutil.move does when its destination is an existing directory, and so that it can't overwrite it either.
    if os.path.exists(destDir):

        destDir = f'{destDir}_{datetime.now().strftime(RuleFileHistory.STAMP_FORMAT)}'

    # Copy the files across before moving the old folder aside. If the move then fails, the converted copies are already in place and the old folder is exactly where it was, so the next run picks
    # up where this one left off: the copying skips the names it already made and the move is tried again.
    try:
        os.makedirs(RuleFileHistory.getHistoryDir(), exist_ok=True)
        count = copyOldFilesToNewNames(oldDir)
        os.makedirs(holdingDir, exist_ok=True)
        shutil.move(oldDir, destDir)

    except OSError as err:

        if report is not None:

            report.Warning(f'The old {OLD_HISTORY_DIR_NAME} folder of saved transfer rule copies could not be converted, so it has been left as it is. The error was: {err}')

        return

    writeConversionNote(holdingDir)

    if report is not None:

        movedTo = os.path.join(os.path.basename(FTPaths.OUTPUT_DIR), RuleFileHistory.HISTORY_DIR_NAME, OLD_FOLDER_NAME, os.path.basename(destDir))
        report.Info(f'Converted {count} saved copies of the transfer rules file to the new naming. The old {OLD_HISTORY_DIR_NAME} folder itself was moved to {movedTo} and nothing in it was deleted.')

def copyOldFilesToNewNames(oldDir):
    '''Copy every file in the old layout's created and run subfolders into the rule file history folder under its converted name, and return how many were copied. A file whose name doesn't fit the
       old scheme is left where it is rather than given an invented name; it still travels with the folder when that is moved aside. A name that is already in the history folder is not copied a
       second time, so a conversion that was interrupted part way through its copying can be run again safely.'''

    count = 0

    for subFolderName, tag in OLD_SUBFOLDER_TAGS.items():

        subFolderPath = os.path.join(oldDir, subFolderName)

        if not os.path.isdir(subFolderPath):

            continue

        for fileName in sorted(os.listdir(subFolderPath)):

            sourcePath = os.path.join(subFolderPath, fileName)
            newName = convertOldFileName(fileName, subFolderName, tag)

            if not os.path.isfile(sourcePath) or not newName:

                continue

            destPath = os.path.join(RuleFileHistory.getHistoryDir(), newName)

            if os.path.exists(destPath):

                continue

            shutil.copy2(sourcePath, destPath)
            count += 1

    return count

def convertOldFileName(fileName, oldInfix, tag):
    '''Turn one old layout file name - <stem>_<infix>_<YYYYMMDD_HHMMSS><extension>, where the infix is the name of the subfolder the file was in - into the new <stem>_<date>_<time>_<tag><extension>.
       Returns None for a name that doesn't fit that scheme, so that a file somebody put in the folder by hand is never renamed on a guess.'''

    base, extension = os.path.splitext(fileName)
    stem, separator, oldStamp = base.rpartition(f'_{oldInfix}_')

    if not separator or not stem:

        return None

    # A stamp that won't parse means this isn't one of the copies FLExTrans saved, whatever the rest of the name looks like.
    try:
        stampDate = datetime.strptime(oldStamp, OLD_STAMP_FORMAT)

    except ValueError:

        return None

    return f'{stem}_{stampDate.strftime(RuleFileHistory.STAMP_FORMAT)}_{tag}{extension}'

def writeConversionNote(holdingDir):
    '''Write the note that explains the folder layout change into holdingDir. An existing note is left alone, since a second conversion into the same folder has nothing new to say, and a failure
       writing it is ignored, since the note is a courtesy for whoever finds the folder later and the conversion it describes has already succeeded.'''

    notePath = os.path.join(holdingDir, CONVERSION_NOTE_NAME)

    if os.path.isfile(notePath):

        return

    try:
        with open(notePath, 'w', encoding='utf-8') as noteFile:

            noteFile.write(NOTE_TEXT)

    except OSError:

        pass
