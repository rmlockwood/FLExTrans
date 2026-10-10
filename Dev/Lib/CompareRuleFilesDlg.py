#
#   CompareRuleFilesDlg
#
#   Ron Lockwood
#   SIL International
#   10/10/26
#
#   Version 3.17.2 - 10/10/26 - Ron Lockwood
#    Added Collapse All / Expand All and Open Rules File buttons; the arrows now open a folded block to reach a change inside it. The change count has no direction text after it.
#
#   Version 3.17.1 - 10/10/26 - Ron Lockwood
#    Current rules file now on the right and the newest saved copy on the left, with Browse... in the left-hand list; "Change n of m" has no direction text after it.
#
#   Version 3.17 - 10/10/26 - Ron Lockwood
#    Initial version. A window that shows two versions of a transfer rules file side by side with their differences highlighted, for the Compare Rule Files tool and other callers.
#
#   OVERVIEW (AI generated, then edited)
#
#   The window behind the Compare Rule Files tool. Its purpose is to let the user see what has changed between two versions of their transfer rules - typically the rules file as it is now
#   against one of the copies FLExTrans saved before something changed it. Two combo boxes, one above each pane, pick the versions; the comparison itself is rendered as HTML by TransferPreview,
#   the same code that draws the AI Rule Studio's before/after view, so the colours mean the same thing in both places: red removed, green added, orange changed, with the changed parts of a
#   value picked out in darker orange. The two panes scroll as one with matching rows level, and the arrow buttons step through the changes.
#
#   It lives in Lib rather than in the module so that any tool can open it. Dev/Modules/CompareRuleFiles.py is only a thin wrapper that reads the settings and shows it; the Testbed Log Viewer is
#   meant to open it too, for a test's rules against the current ones. A caller that already runs a Qt event loop uses showRuleFileComparison (modal); the FlexTools module, which has no loop
#   running, shows the window and runs the application loop itself.
#
#   THE VERSION LISTS
#
#   Both combo boxes list the current rules file first and then every copy of it in the Output\rule-file-history folder, newest first (RuleFileHistory.listHistoryCopies; only copies of this
#   file, so the interchunk/postchunk copies of an advanced project don't appear). A copy is shown by when it was saved, in the user-interface language's date format, and what saved it - its tag,
#   turned into words by tagDescription. A copy holds the rules as they were at that moment: "before AI changes" is the file just before the AI Rule Studio wrote to it. The left-hand list has
#   one more entry, Browse..., second in the list, which opens any rules file; a file picked that way (or a path a caller passes that isn't in the lists) is added just below the fixed entries.
#   By default the left side is the newest saved copy and the right side the current file - older on the left, newer on the right - so opening the tool answers "what changed since the last
#   save?". Picking Browse... and then cancelling puts the left-hand list back on what it showed before.
#
#   WHICH WAY THE COLOURS READ
#
#   The colours describe the change from the older version to the newer one, whichever side each is on, because that is the question the user is asking: a rule added since a backup has to
#   come out green, not red, even if the user has put the backup on the right. isOlder decides by each file's modified time, which a saved copy carries over from the rules file it was copied
#   from, and TransferPreview is told to put the older version (its "before") in the right pane when that's where it is. The summary line at the top only
#   counts the changes ("3 changes.", "Change 2 of 3.") - no explanatory text alongside.
#
#   THE PAGE
#
#   The rendered page is written to a file in a temporary folder and loaded from there rather than handed to setHtml, because QWebEngineView.setHtml silently refuses content over 2 MB, and
#   a whole rules file's comparison can approach that. Each render gets a new file name so the view can't serve a stale page from its cache. The folder is removed when the window closes.
#   Once a page has loaded, diffSummary (in the page) is asked how many changes there are: none says so at the top and greys the arrow buttons; otherwise the arrows call diffNav and the
#   label says which change is showing. The zoom factor is kept on the dialog and re-applied after every load, since each new page would otherwise come up at the default size.
#
#   A change inside a folded block is still a stop for the arrows: the page counts it at the folded block's row and opens the block when the arrows reach it. Collapse All folds every block, the
#   sections included, so a rules file comes down to its six section lines; Expand All opens everything. Both ask the page for the new change count, because folding regroups the changes. Open Rules File opens
#   the current rules file in XXE; the comparison doesn't follow edits made there until the user picks the version again.
#
#   CODE STRUCTURE
#
#   tagDescription turns a history tag into words. CompareRuleFilesDlg builds the window from CompareRuleFilesWindow.ui (__init__), fills the lists (populateVersionLists, addVersionItem,
#   selectVersion, versionLabel), reacts to a pick (onLeftVersionChanged, onRightVersionChanged, browseForLeftVersion), renders (showComparison -> onLoadFinished -> onSummary), steps through
#   the changes (onPreviousChange, onNextChange -> onNavigated), folds (onCollapseAll, onExpandAll -> foldAll), opens the rules file in XXE (onOpenRulesFile), zooms, and cleans up its
#   temporary folder in done. showRuleFileComparison is the entry point for other modules.
#

import os
import shutil
import tempfile
import xml.etree.ElementTree as ET

from PyQt6.QtCore import Qt, QCoreApplication, QDate, QTime, QLocale, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

import FTPaths
import RuleFileHistory
import TransferPreview
import UILanguages
from CompareRuleFilesWindow import Ui_CompareRuleFiles

_translate = QCoreApplication.translate

# The data stored on the Browse... entry of the left-hand list in place of a file path.
BROWSE_ITEM = '<browse>'

# Where the left-hand list's fixed entries end: the current file (0) and Browse... (1). A browsed file is inserted here, and the right-hand list, which has no Browse..., inserts at 1.
LEFT_INSERT_INDEX = 2
RIGHT_INSERT_INDEX = 1

ZOOM_FACTOR_STEP = 1.15
MIN_ZOOM = 0.25
MAX_ZOOM = 5.0

def tagDescription(tag: str) -> str:
    '''Words for the tag RuleFileHistory puts on each saved copy, saying what saved it. A tag this doesn't know (a newer producer, or a hand-made copy) is shown with its underscores as spaces.'''

    descriptions = {
        RuleFileHistory.TAG_TEST_ADDED:        _translate('CompareRuleFiles', 'test added to the testbed'),
        RuleFileHistory.TAG_TESTBED_RUN:       _translate('CompareRuleFiles', 'testbed run'),
        RuleFileHistory.TAG_BEFORE_RA_CHANGES: _translate('CompareRuleFiles', 'before Rule Assistant changes'),
        RuleFileHistory.TAG_BEFORE_AI_CHANGES: _translate('CompareRuleFiles', 'before AI Rule Studio changes'),
        RuleFileHistory.TAG_BEFORE_CAT_SETUP:  _translate('CompareRuleFiles', 'before category setup'),
        'rule_tested':                         _translate('CompareRuleFiles', 'rule tested in the Live Rule Tester'),
    }

    return descriptions.get(tag, tag.replace('_', ' '))

class CompareRuleFilesDlg(QDialog):
    '''The comparison window. rulesFile is the project's transfer rules file - the "current" entry, and the file whose saved copies are listed. leftPath and rightPath, when given, choose
    the starting versions instead of the defaults (newest saved copy on the left, current on the right); a path that isn't in the lists is added to them.'''

    def __init__(self, rulesFile: str, leftPath=None, rightPath=None, parent=None):

        super().__init__(parent)

        self.ui = Ui_CompareRuleFiles()
        self.ui.setupUi(self)

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.rulesFile = rulesFile
        self.langCode = self.interfaceLangCode()
        self.dateLocale = QLocale(UILanguages.localeNameForCode(self.langCode) or QLocale.system().name())
        self.zoomFactor = 1.0
        self.tempDir = tempfile.mkdtemp(prefix='FLExTransRuleCompare_')
        self.renderCount = 0
        self.lastLeftIndex = 0
        self.olderOnRight = False

        self.populateVersionLists()

        # Starting versions: what the caller asked for, else the newest saved copy (if there is one) on the left and the current file on the right - older on the left, newer on the right.
        if leftPath:

            self.selectVersion(self.ui.leftVersionCombo, leftPath, LEFT_INSERT_INDEX)

        elif self.ui.leftVersionCombo.count() > LEFT_INSERT_INDEX:

            self.ui.leftVersionCombo.setCurrentIndex(LEFT_INSERT_INDEX)

        self.selectVersion(self.ui.rightVersionCombo, rightPath or rulesFile, RIGHT_INSERT_INDEX)
        self.lastLeftIndex = self.ui.leftVersionCombo.currentIndex()

        # Connect only now, so filling and pre-selecting the lists above doesn't render the comparison several times over.
        self.ui.leftVersionCombo.currentIndexChanged.connect(self.onLeftVersionChanged)
        self.ui.rightVersionCombo.currentIndexChanged.connect(self.onRightVersionChanged)
        self.ui.previousChangeButton.clicked.connect(self.onPreviousChange)
        self.ui.nextChangeButton.clicked.connect(self.onNextChange)
        self.ui.zoomIncreaseButton.clicked.connect(self.onZoomIncrease)
        self.ui.zoomDecreaseButton.clicked.connect(self.onZoomDecrease)
        self.ui.collapseAllButton.clicked.connect(self.onCollapseAll)
        self.ui.expandAllButton.clicked.connect(self.onExpandAll)
        self.ui.openRulesFileButton.clicked.connect(self.onOpenRulesFile)
        self.ui.closeButton.clicked.connect(self.reject)
        self.ui.comparisonView.loadFinished.connect(self.onLoadFinished)
        self.ui.comparisonView.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.showComparison()

    def interfaceLangCode(self) -> str:
        '''The FLExTrans interface-language code, which picks the rule labels in the comparison and the date format in the lists. English when Utils can't be loaded (a standalone run).'''

        try:
            import Utils
            return Utils.getInterfaceLangCode() or 'en'

        except Exception:

            return 'en'

    # --- the version lists ------------------------------------------------

    def populateVersionLists(self):
        '''Fill both lists: the current rules file, then (left-hand list only) Browse..., then every saved copy of the rules file, newest first.'''

        currentLabel = _translate('CompareRuleFiles', 'Current rules file ({name})').format(name=os.path.basename(self.rulesFile))

        for combo in (self.ui.leftVersionCombo, self.ui.rightVersionCombo):

            self.addVersionItem(combo, currentLabel, self.rulesFile)

        self.ui.leftVersionCombo.addItem(_translate('CompareRuleFiles', 'Browse...'), BROWSE_ITEM)

        for path, savedAt, tag in RuleFileHistory.listHistoryCopies(self.rulesFile):

            label = self.versionLabel(savedAt, tag)

            for combo in (self.ui.leftVersionCombo, self.ui.rightVersionCombo):

                self.addVersionItem(combo, label, path)

    def addVersionItem(self, combo, label: str, path: str, index=None):
        '''Add (or, with index, insert) a version to a list, with its file path as the item data and as the tooltip so the actual file can always be seen.'''

        if index is None:

            index = combo.count()

        combo.insertItem(index, label, path)
        combo.setItemData(index, path, Qt.ItemDataRole.ToolTipRole)

    def versionLabel(self, savedAt, tag: str) -> str:
        '''How a saved copy appears in the lists: when it was saved, in the interface language's long date and short time formats, and what saved it.'''

        date = QDate(savedAt.year, savedAt.month, savedAt.day)
        time = QTime(savedAt.hour, savedAt.minute, savedAt.second)
        whenText = self.dateLocale.toString(date, QLocale.FormatType.LongFormat) + ' ' + self.dateLocale.toString(time, QLocale.FormatType.ShortFormat)

        return _translate('CompareRuleFiles', '{when} - {what}').format(when=whenText, what=tagDescription(tag))

    def selectVersion(self, combo, path: str, insertIndex: int):
        '''Select the entry for path in a list, adding it (labelled with its file name) at insertIndex when it isn't already there - e.g. a file a caller names that isn't the current file or a
        saved copy. Signals are blocked so this doesn't itself trigger a render.'''

        wanted = os.path.normcase(os.path.abspath(path))
        combo.blockSignals(True)

        try:
            for index in range(combo.count()):

                data = combo.itemData(index)

                if data and data != BROWSE_ITEM and os.path.normcase(os.path.abspath(data)) == wanted:

                    combo.setCurrentIndex(index)
                    return

            self.addVersionItem(combo, os.path.basename(path), path, insertIndex)
            combo.setCurrentIndex(insertIndex)

        finally:
            combo.blockSignals(False)

    def onLeftVersionChanged(self, index):
        '''A new left-hand version was picked. Browse... opens a file chooser instead of being a version itself; anything else is remembered (so a cancelled Browse can go back to it) and shown.'''

        if self.ui.leftVersionCombo.itemData(index) == BROWSE_ITEM:

            self.browseForLeftVersion()
            return

        self.lastLeftIndex = index
        self.showComparison()

    def onRightVersionChanged(self, index):

        self.showComparison()

    def browseForLeftVersion(self):
        '''Let the user pick any rules file for the left-hand side. It is added to the list and shown; cancelling puts the list back on the version it showed before.'''

        startDir = RuleFileHistory.getHistoryDir()

        if not os.path.isdir(startDir):

            startDir = os.path.dirname(self.rulesFile)

        path, _ = QFileDialog.getOpenFileName(self, _translate('CompareRuleFiles', 'Choose a transfer rules file to compare'), startDir,
                                              _translate('CompareRuleFiles', 'Transfer rules files (*.t1x *.t2x *.t3x);;All files (*.*)'))

        if not path:

            self.ui.leftVersionCombo.blockSignals(True)
            self.ui.leftVersionCombo.setCurrentIndex(self.lastLeftIndex)
            self.ui.leftVersionCombo.blockSignals(False)
            return

        self.selectVersion(self.ui.leftVersionCombo, path, LEFT_INSERT_INDEX)
        self.lastLeftIndex = self.ui.leftVersionCombo.currentIndex()
        self.showComparison()

    # --- rendering ----------------------------------------------------------

    def showComparison(self):
        '''Render the two selected versions side by side and load the page. The change count and arrow buttons are set once the page has loaded (onLoadFinished), since it's the page that
        knows how the changes group together.'''

        leftPath = self.ui.leftVersionCombo.currentData()
        rightPath = self.ui.rightVersionCombo.currentData()

        self.ui.previousChangeButton.setEnabled(False)
        self.ui.nextChangeButton.setEnabled(False)

        # The colours read as the change from the older version to the newer one - a rule added since a backup is green, not red - whichever side each was picked on. With the default
        # backup-left, current-file-right layout the older one is on the left, the usual case.
        self.olderOnRight = self.isOlder(rightPath, leftPath)
        beforePath, afterPath = (rightPath, leftPath) if self.olderOnRight else (leftPath, rightPath)

        try:
            pageHtml = TransferPreview.renderFileComparisonHtml(beforePath, afterPath, self.langCode, beforeOnRight=self.olderOnRight)

        except (OSError, ET.ParseError) as err:

            self.ui.summaryLabel.setText(_translate('CompareRuleFiles', 'These files could not be compared: {err}').format(err=err))
            self.ui.comparisonView.setHtml('')
            return

        # A new file name for every render, so the view can't show a cached copy of an earlier comparison; the previous page's file is no longer needed.
        self.renderCount += 1
        pagePath = os.path.join(self.tempDir, 'comparison{n}.html'.format(n=self.renderCount))

        with open(pagePath, 'w', encoding='utf-8') as pageFile:
            pageFile.write(pageHtml)

        previousPath = os.path.join(self.tempDir, 'comparison{n}.html'.format(n=self.renderCount - 1))

        if os.path.isfile(previousPath):

            try:
                os.remove(previousPath)

            except OSError:

                pass

        self.ui.summaryLabel.setText(_translate('CompareRuleFiles', 'Comparing...'))
        self.ui.comparisonView.load(QUrl.fromLocalFile(pagePath))

    def isOlder(self, path: str, otherPath: str) -> bool:
        '''Whether the file at path is an older version than the one at otherPath, by when each was last modified. A saved copy keeps the modified time the rules file had when it was copied
        (RuleFileHistory copies with copy2), so this is the age of that version of the rules, not of the copy. A tie, or a file that can't be looked at, counts as not older.'''

        try:
            return os.path.getmtime(path) < os.path.getmtime(otherPath)

        except OSError:

            return False

    def onLoadFinished(self, ok):
        '''The page is in: restore the zoom and ask the page how many changes it found.'''

        if not ok:

            return

        self.ui.comparisonView.setZoomFactor(self.zoomFactor)

        page = self.ui.comparisonView.page()

        # page() is typed Optional, but a view always has a page once one has finished loading in it.
        if page is not None:

            page.runJavaScript('diffSummary()', self.onSummary)

    def onSummary(self, count):
        '''Say how many changes there are - or that there are none, with the arrow buttons greyed - at the top of the window.'''

        count = int(count or 0)

        self.ui.previousChangeButton.setEnabled(count > 0)
        self.ui.nextChangeButton.setEnabled(count > 0)
        self.ui.summaryLabel.setText(self.countText(count))

    def countText(self, count: int) -> str:
        '''The summary line for a comparison with count changes.'''

        if count == 0:

            return _translate('CompareRuleFiles', 'No differences: the two versions are the same.')

        if count == 1:

            return _translate('CompareRuleFiles', '1 change.')

        return _translate('CompareRuleFiles', '{count} changes.').format(count=count)

    # --- stepping through the changes ------------------------------------

    def onPreviousChange(self):

        self.navigate(-1)

    def onNextChange(self):

        self.navigate(1)

    def navigate(self, direction: int):
        '''Ask the page to scroll to the next (1) or previous (-1) change; it answers with [the change's number, how many there are].'''

        page = self.ui.comparisonView.page()

        if page is not None:

            page.runJavaScript('diffNav({d})'.format(d=direction), self.onNavigated)

    def onNavigated(self, result):
        '''Show which change is on screen. A number of 0 means there was no change that way, so the summary is left as it was.'''

        if not result or len(result) != 2:

            return

        number, count = int(result[0]), int(result[1])

        if number > 0:

            self.ui.summaryLabel.setText(_translate('CompareRuleFiles', 'Change {number} of {count}.').format(number=number, count=count))

    # --- folding -------------------------------------------------------------

    def onCollapseAll(self):

        self.foldAll(True)

    def onExpandAll(self):

        self.foldAll(False)

    def foldAll(self, folded: bool):
        '''Fold every block, sections included (Collapse All), or open everything (Expand All) - see foldAll in TransferPreview's page script. Folding regroups the changes (all the changes
        inside a folded block count as one stop), so the summary is refreshed from the count the page returns.'''

        page = self.ui.comparisonView.page()

        if page is not None:

            page.runJavaScript('foldAll({f})'.format(f='true' if folded else 'false'), self.onSummary)

    # --- opening the rules file --------------------------------------------

    def onOpenRulesFile(self):
        '''Open the current transfer rules file in the XML editor. os.startfile hands it to whatever is registered for .t1x (XXE), like AI Rule Studio's Open Rule File, and keeps this window
        responsive while the editor is open.'''

        try:
            os.startfile(self.rulesFile)

        except OSError as err:

            QMessageBox.warning(self, _translate('CompareRuleFiles', 'Could not open the editor'),
                                _translate('CompareRuleFiles', 'The transfer rules file could not be opened ({err}). Open it yourself from: {path}').format(err=err, path=self.rulesFile))

    # --- zoom ---------------------------------------------------------------

    def onZoomIncrease(self):

        self.setZoom(self.zoomFactor * ZOOM_FACTOR_STEP)

    def onZoomDecrease(self):

        self.setZoom(self.zoomFactor / ZOOM_FACTOR_STEP)

    def setZoom(self, factor: float):
        '''Clamp and remember the zoom, and apply it. The page re-aligns its panes itself, since a zoom change reaches it as a resize.'''

        self.zoomFactor = max(MIN_ZOOM, min(MAX_ZOOM, factor))
        self.ui.comparisonView.setZoomFactor(self.zoomFactor)

    # --- closing ------------------------------------------------------------

    def done(self, a0):
        '''Remove the temporary folder the rendered pages were written to, however the window is closed (Close button, the title-bar X, or Esc all come through here). The parameter - the
        dialog's result code - is named a0 to match the PyQt6 stubs, which otherwise flag the override as incompatible.'''

        shutil.rmtree(self.tempDir, ignore_errors=True)
        super().done(a0)

def showRuleFileComparison(rulesFile: str, leftPath=None, rightPath=None, parent=None):
    '''Open the comparison window modally - the entry point for a module that already runs a Qt event loop, such as the Testbed Log Viewer. rulesFile is the project's transfer rules file;
    leftPath and rightPath optionally choose the two versions to start with (by default the current file and its newest saved copy).'''

    dlg = CompareRuleFilesDlg(rulesFile, leftPath, rightPath, parent)
    dlg.exec()
