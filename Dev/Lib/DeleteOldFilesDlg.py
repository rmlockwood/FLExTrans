#
#   DeleteOldFilesDlg
#
#   Ron Lockwood
#   SIL International
#   10/13/26
#
#   Version 3.17.2 - 10/21/26 - Ron Lockwood
#    Updated the code description block to say the trigger count of 100 is a total across all groups.
#
#   Version 3.17.1 - 10/13/26 - Ron Lockwood
#    Initial version. Asks whether to delete old items (6, 12 or 24 months), always keeps the newest 50, and only asks when 100 are over a year old, at most every 3 months.
#
#   OVERVIEW (AI generated, then edited)
#
#   FLExTrans keeps things that pile up over the life of a project: a backup copy of the transfer rules file or the testbed file every time a tool changes one of them, and a result in the testbed
#   log every time the testbed is run. Clean Files offers to delete the old ones, and this is the window it asks with. It is used twice, once for the backup copies and once for the testbed results,
#   so the caller supplies the title, the message and how a count is worded; the window itself only knows about ages.
#
#   THE RULE
#
#   An item can be deleted when it is older than the age the user picks (6, 12 or 24 months) AND it is not one of the newest KEEP_NEWEST (50) items in its group. The second half is what protects a
#   project that has sat unused for a couple of years: every item in it is older than 24 months, and without the floor a single Yes would wipe out its whole history. Groups are the caller's
#   business - for the backup copies a group is all the copies of one file, so the testbed and each rules file keep 50 apiece; for the testbed results there is just the one group.
#
#   selectOldItems() is the rule, and countOldItems() runs it at each of the three ages so that the window can show how many items each choice would delete before the user commits to one. Both are
#   free of Qt so the rule can be tested on its own.
#
#   WHEN TO ASK
#
#   Clean Files is run often, so asking every time anything at all is old would nag. shouldAsk() holds two conditions, and both must be true:
#    - Enough has piled up: at least TRIGGER_MIN_COUNT (100) items that selectOldItems() would delete at TRIGGER_MONTHS (12). Without this, the day after a cleanup the user would be asked about
#      the one or two items that have just crossed the line. After a cleanup the count starts again from zero, so the next question comes only once another real batch has built up.
#      The 100 is a total across all the groups, not a count per group: each group first keeps its newest KEEP_NEWEST, and what is left over in every group is added up. So for the backup copies,
#      70 deletable testbed copies and 70 deletable rules copies make 140 and the user is asked, though neither file reaches 100 on its own. This is deliberate - the question is whether there
#      is a cleanup worth doing, wherever the items come from. A per-group trigger would never ask a project whose old items are spread over several files, however many there are in all.
#    - The user hasn't been asked recently: not within COOLDOWN_MONTHS (3) of the last time. The date is recorded whenever the window is shown, whether the answer was Yes or No - otherwise someone
#      who keeps saying No would be asked on every run, which is the most annoying case of all.
#   Once the window is open the user can still pick 6 or 24 months; the trigger only decides whether to ask.
#
#   THE LAST-ASKED FILE
#
#   The last-asked dates live in Config\OldFileCleanup.toml in the work project, one key per kind of item (the caller passes the key), so each project and each of the two cleanups has its own
#   cooldown. It is read with tomllib and written with tomli_w, read-modify-write so the two keys don't clobber each other. It deliberately isn't in FlexTrans.config, since saving the settings
#   window drops any key it doesn't know about. A missing, unreadable or corrupt file just means "never asked", and a failed write is ignored - the worst that can happen is one extra question.
#
#   THE WINDOW
#
#   The widgets are in Dev/Lib/Windows/DeleteOldFilesWindow.ui; the code adds the FLExTrans window icon, like every other FLExTrans dialog. An age that would delete nothing is disabled, and the
#   oldest age that would delete something is selected to begin with, since 24 months is the cautious default. No is the default button, so that Enter pressed out of habit deletes nothing.
#
#   CODE STRUCTURE
#
#   The constants come first, then monthsBefore() (date arithmetic by calendar month), selectOldItems() and countOldItems(), then readLastAsked(), saveLastAsked() and shouldAsk(), and finally the
#   DeleteOldFilesDlg class. Dev/Modules/CleanFiles.py is the only caller: it builds the dated groups, checks shouldAsk(), records the date with saveLastAsked(), opens the window with the counts
#   from countOldItems(), and on Yes calls selectOldItems() with the chosen age to get the items to delete.
#

import calendar
import os
import tomllib
from datetime import datetime

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

import FTPaths
from DeleteOldFilesWindow import Ui_DeleteOldFilesWindow # type: ignore

# The ages offered, in months, youngest first. The window has one radio button per age, in this order.
AGE_CHOICES_MONTHS = (6, 12, 24)

# However old they are, this many of the newest items in each group are never deleted.
KEEP_NEWEST = 50

# The user is only asked when at least TRIGGER_MIN_COUNT items could be deleted at TRIGGER_MONTHS, and not within COOLDOWN_MONTHS of the last time they were asked. See WHEN TO ASK above.
TRIGGER_MONTHS = 12
TRIGGER_MIN_COUNT = 100
COOLDOWN_MONTHS = 3

# The file in the work project's Config folder that records when the user was last asked, and its keys, one per kind of item
LAST_ASKED_FILE = 'OldFileCleanup.toml'
LAST_ASKED_BACKUP_COPIES = 'backupCopiesLastAsked'
LAST_ASKED_TESTBED_RESULTS = 'testbedResultsLastAsked'

def monthsBefore(when, months):
    '''Return the date and time the given number of calendar months before when. The day is pulled back to the end of a shorter month, so six months before August 31 is February 28 (or 29).'''

    monthCount = when.year * 12 + (when.month - 1) - months
    year, monthIndex = divmod(monthCount, 12)
    month = monthIndex + 1
    day = min(when.day, calendar.monthrange(year, month)[1])

    return when.replace(year=year, month=month, day=day)

def selectOldItems(datedGroups, months, keepNewest=KEEP_NEWEST, now=None):
    '''Return the items that can be deleted at the given age. datedGroups is a list of groups, each a list of (datetime, item) pairs in any order. In each group the newest keepNewest items are kept
       no matter what, and of the rest only the ones dated before the cutoff are returned. now is only there so that a test can fix the date; it defaults to the current date and time.'''

    cutoff = monthsBefore(now or datetime.now(), months)
    oldItems = []

    for group in datedGroups:

        # Newest first, so that the ones to keep are simply the front of the list. Only the date is compared, since the items themselves may not be orderable.
        newestFirst = sorted(group, key=lambda datedItem: datedItem[0], reverse=True)

        for savedAt, item in newestFirst[keepNewest:]:

            if savedAt < cutoff:

                oldItems.append(item)

    return oldItems

def countOldItems(datedGroups, keepNewest=KEEP_NEWEST, now=None):
    '''Return a dictionary from each of the AGE_CHOICES_MONTHS to the number of items selectOldItems() would delete at that age. All zero means there is nothing to offer.'''

    return {months: len(selectOldItems(datedGroups, months, keepNewest, now)) for months in AGE_CHOICES_MONTHS}

def getLastAskedPath():
    '''Return the path of the last-asked file. A function rather than a constant so that FTPaths.CONFIG_DIR is read when it is used, which also lets a test point it at a temporary folder.'''

    return os.path.join(FTPaths.CONFIG_DIR, LAST_ASKED_FILE)

def readLastAsked(key):
    '''Return when the user was last asked about the kind of item named by key (one of the LAST_ASKED_ constants), or None if they never have been or the file can't be read.'''

    try:
        with open(getLastAskedPath(), 'rb') as lastAskedFile:

            lastAsked = tomllib.load(lastAskedFile).get(key)

    except (OSError, tomllib.TOMLDecodeError):

        return None

    # Anything other than a date and time (e.g. a hand-edited value) counts as never asked
    if not isinstance(lastAsked, datetime):

        return None

    return lastAsked

def saveLastAsked(key, when=None):
    '''Record that the user was asked about the kind of item named by key, at when (default now). The other keys in the file are kept. A failure to write is ignored, since the only cost is that
       the user may be asked again sooner than COOLDOWN_MONTHS.'''

    # Import here (not at module load) so this module can still be imported without tomli_w present, e.g. by unit tests that only exercise the rule
    import tomli_w

    lastAskedPath = getLastAskedPath()
    data = {}

    try:
        with open(lastAskedPath, 'rb') as lastAskedFile:

            data = tomllib.load(lastAskedFile)

    except (OSError, tomllib.TOMLDecodeError):

        # No file yet, or a corrupt one that is simply replaced
        data = {}

    # Whole seconds, so the file reads cleanly
    data[key] = (when or datetime.now()).replace(microsecond=0)

    try:
        with open(lastAskedPath, 'wb') as lastAskedFile:

            tomli_w.dump(data, lastAskedFile)

    except OSError:

        pass

def shouldAsk(datedGroups, lastAsked, now=None):
    '''Return True when the user should be asked about these items: enough of them are old (TRIGGER_MIN_COUNT at TRIGGER_MONTHS) and they weren't asked within COOLDOWN_MONTHS of lastAsked,
       which is what readLastAsked() returned. now is only there so that a test can fix the date.'''

    now = now or datetime.now()

    if lastAsked is not None and lastAsked > monthsBefore(now, COOLDOWN_MONTHS):

        return False

    return len(selectOldItems(datedGroups, TRIGGER_MONTHS, now=now)) >= TRIGGER_MIN_COUNT

class DeleteOldFilesDlg(QDialog):
    '''Ask whether to delete old items and how old. title and message are the window title and the explanation above the choices. ageCounts is what countOldItems() returned, and countText is a
       function turning a count into the text shown beside each age (e.g. "12 copies"). After exec(), chosenMonths is the age picked if the user said Yes, or None if they said No.'''

    def __init__(self, title, message, ageCounts, countText, parent=None):

        super().__init__(parent)

        self.chosenMonths = None

        self.ui = Ui_DeleteOldFilesWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setWindowTitle(title)
        self.ui.messageLabel.setText(message)

        # Pair each age with its radio button and count label, in the same order as AGE_CHOICES_MONTHS
        self.radioForMonths = {6: self.ui.sixMonthsRadio, 12: self.ui.twelveMonthsRadio, 24: self.ui.twentyFourMonthsRadio}
        countLabelForMonths = {6: self.ui.sixMonthsCountLabel, 12: self.ui.twelveMonthsCountLabel, 24: self.ui.twentyFourMonthsCountLabel}

        # Show how many each age would delete, and disable an age that would delete nothing so the user can't pick a choice that does nothing
        for months in AGE_CHOICES_MONTHS:

            count = ageCounts.get(months, 0)
            countLabelForMonths[months].setText(countText(count))
            self.radioForMonths[months].setEnabled(count > 0)
            countLabelForMonths[months].setEnabled(count > 0)

        # Start on the oldest age that would delete something, which deletes the least
        for months in reversed(AGE_CHOICES_MONTHS):

            if ageCounts.get(months, 0) > 0:

                self.radioForMonths[months].setChecked(True)
                break

        self.ui.buttonBox.accepted.connect(self.onYes)
        self.ui.buttonBox.rejected.connect(self.reject)

        yesButton = self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Yes)
        noButton = self.ui.buttonBox.button(QDialogButtonBox.StandardButton.No)

        # Make No the default, so pressing Enter out of habit deletes nothing. Yes has to be demoted explicitly: a QDialogButtonBox hands the default to its accept-role button as it is laid out,
        # which would undo a setDefault() made on No alone.
        if yesButton is not None:

            yesButton.setAutoDefault(False)
            yesButton.setDefault(False)

        if noButton is not None:

            noButton.setAutoDefault(True)
            noButton.setDefault(True)
            noButton.setFocus()

    def onYes(self):

        for months, radio in self.radioForMonths.items():

            if radio.isChecked():

                self.chosenMonths = months

        self.accept()
