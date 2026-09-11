#
#   MergeTextsDlg
#
#   Ron Lockwood
#   SIL International
#   9/9/26
#
#   Version 3.17.1 - 9/11/26 - Ron Lockwood
#    Fixes #1561. Word the coverage sentence in the singular for one chapter.
#
#   Version 3.17 - 9/9/26 - Ron Lockwood
#    Initial version.
#
#   OVERVIEW (AI generated, then edited)
#
#   The window for the Merge Texts module: it works out which texts the user wants merged, in what order, and what the merged text should be called, and it is the place where every warning about
#   what a merge costs gets said. It does no merging itself - it hands a MergeInfo back to Dev/Modules/MergeTexts.py, which does the database work. All of the widgets live in
#   Dev/Lib/Windows/MergeTextsWindow.ui and are reached through self.ui.
#
#   THE TWO LISTS
#
#   The group combo offers the books MergeTextsUtils.groupTextNames found by looking at the text names, plus a "(manual selection)" entry for everything its name heuristic cannot see. Picking a
#   group fills the right hand list with that book's chapters in reading order and leaves every other text on the left. From there the two lists are just moved between, so a user whose texts are
#   named in some way the heuristic misses can still build any selection by hand - which is what the manual entry exists for.
#
#   Any hand edit flips the combo to "(manual selection)", because a combo still naming a book after the user has removed half its chapters would be lying about what is going to happen. The
#   loadingLists flag is what stops that flip from firing while the code is itself repopulating the lists.
#
#   THE SUGGESTED NAME
#
#   The name box is filled in from MergeTextsUtils.mergedTextName every time the selection changes, so it always describes the range actually selected - remove chapters 25 to 28 and the suggestion
#   goes from "Matthew 01-28" to "Matthew 01-24". That stops the moment the user types in the box: nameEditedByUser latches and the suggestion never overwrites a hand-typed name again. Without
#   that latch, adding one more chapter would silently throw away the name the user had chosen.
#
#   WHY EACH ROW CARRIES ITS OBJECT
#
#   Each row holds the (name, IText, IStText) triple under UserRole rather than being looked up later by its display string. Two reasons, both real: the row for the configured source text has a
#   marker appended to it so its display string is not the text's name, and FLEx allows two texts to have the same name, so a name is not an identifier. The same reasoning is in DeleteTexts.py.
#
#   THE HAZARDS
#
#   checkHazards is the honest part of the window. A paragraph move carries the paragraphs and everything they own - segments, and therefore each word's analysis, gloss, free translation and notes.
#   It does not carry what belongs to the TEXT, and the user has to be told which of those they are about to lose:
#
#     - Text tags are owned by the StText. The moveTagsCheck option re-attaches them to the merged text; unticked, they die with the source text. Since tags are unusual, the checkbox is only
#       shown when some selected text actually has one - see refreshSummary.
#     - A discourse chart that has words in it would be stranded. See THE CHARTS below, which is the whole of that story.
#     - Media files and a notebook record belong to the source IText, so deleting it destroys them. Texts with media are reported and excluded from deletion rather than quietly discarded.
#     - Mixed vernacular writing systems across the selection are legal but almost always a mistake, so they warn.
#
#   Hazards come back in two buckets. A fatal one (a text with no contents object at all) disables Merge outright, because there is nothing sensible to do with it. A warning one only requires the
#   user to tick proceedAnywayCheck, which stays hidden until there is actually something to acknowledge.
#
#   THE CHARTS
#
#   A discourse chart names the text it charts through BasedOnRA, and that text is about to be deleted, so a merge would leave the chart pointing at nothing. Warning about every chart found would
#   be crying wolf, though: FLEx creates a chart shell the moment somebody opens the Discourse view on a text, so in practice most charts on a chapter have no words placed in them at all and mean
#   nothing to whoever built them. chartLists therefore splits the charts in two. The empty ones are handed to the module in MergeInfo and quietly deleted along with their texts. Only a chart that
#   really has words in it - one with a ConstChartWordGroup somewhere in its rows - represents work that would be lost, and only those get named in a warning the user has to acknowledge.
#
#   CODE STRUCTURE
#
#   MergeInfo - the plain carrier handed back to the module: the ordered IText list, the target name, the Move-tags answer, and the empty charts to delete.
#   ConfirmMergeDlg / confirmMerge() - the point-of-no-return dialog, a fixed-size window wrapped around one scrollable list of the texts about to be merged away. Fixed size and scrolling for the
#   same reason DeleteTexts.py gives: a message box grows to fit its text and would run off the screen somewhere past fifty names, and No is made the default so a reflexive Enter cancels.
#   MergeTextsDlg - the window itself. loadTexts() reads the project once, loadGroups() fills the combo, onGroupChanged()/loadGroupSelection() populate the lists, the on*Clicked handlers move rows
#   around (double-clicking a row moves just that one), refreshSummary() keeps the name box, the summary line, the Move-tags checkbox and the Merge button in step, chartHasWords()/chartLists()
#   sort the discourse charts out, checkHazards() produces the warnings, and onMergeClicked() validates, confirms and accepts.
#

import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import (QAbstractItemView, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QStyle, QVBoxLayout)
from PyQt6.QtCore import QCoreApplication, Qt

from SIL.LCModel import IDsConstChartRepository # type: ignore

import FTPaths
import MergeTextsUtils
import Utils
from MergeTextsWindow import Ui_MergeTextsWindow # type: ignore

# Define _translate for convenience
_translate = QCoreApplication.translate

class MergeInfo(object):

    """What the window hands back to the module. Holds the IText objects themselves, not their names, since a name is not an identifier in FLEx."""

    def __init__(self, sourceTextList, targetName, moveTags, emptyChartList):

        self.sourceTextList = sourceTextList
        self.targetName = targetName
        self.moveTags = moveTags

        # The word-less charts on the texts being merged. The dialog worked out which charts are empty in order to decide what to warn about, so it hands the list over rather than making the
        # module scan for them a second time. See THE CHARTS below.
        self.emptyChartList = emptyChartList

class ConfirmMergeDlg(QDialog):

    def __init__(self, textNameList, targetName, parent=None):

        super().__init__(parent)

        self.setWindowTitle(_translate("MergeTextsDlg", "Merging FLEx Texts"))
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setModal(True)

        # A fixed size is the point of this dialog: the list scrolls instead of the window growing, so confirming three texts and confirming a whole Gospel look the same. A plain message box would
        # have grown to fit its text and run off the bottom of the screen somewhere past fifty names.
        self.resize(500, 430)

        layout = QVBoxLayout(self)

        # Warning triangle beside the question, so this still reads as destructive at a glance the way the standard warning message box does.
        headerLayout = QHBoxLayout()
        iconLabel = QLabel()
        style = self.style()

        # style() is typed as Optional; a realized widget always has one, but fall back to simply not showing the icon rather than crashing the confirmation.
        if style is not None:

            iconLabel.setPixmap(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning).pixmap(32, 32))

        iconLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        headerLayout.addWidget(iconLabel)

        headerLabel = QLabel(_translate("MergeTextsDlg", 'Merge these {count} text(s) into a new text called "{targetName}"?').format(count=len(textNameList), targetName=targetName))
        headerLabel.setWordWrap(True)
        headerLayout.addWidget(headerLabel, 1)
        layout.addLayout(headerLayout)

        # Every text about to be merged away, in merge order, in one scrollable list. Selection and focus are switched off so it reads as a read-only display of what is about to happen.
        nameListWidget = QListWidget()
        nameListWidget.addItems(textNameList)
        nameListWidget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        nameListWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nameListWidget.setAlternatingRowColors(True)
        layout.addWidget(nameListWidget, 1)

        # Spell out the consequence that is easiest to miss: the texts listed above do not merely lose their content, they are removed from the project.
        consequenceLabel = QLabel(_translate("MergeTextsDlg", "Their paragraphs will be moved into the new text and the texts above will then be DELETED."))
        consequenceLabel.setWordWrap(True)
        layout.addWidget(consequenceLabel)

        warningLabel = QLabel(_translate("MergeTextsDlg", "This CANNOT be undone. If FLEx is open, make sure you are NOT in the Texts & Words section of FLEx."))
        warningLabel.setWordWrap(True)
        layout.addWidget(warningLabel)

        # Yes/No rather than OK/Cancel, and their captions come from Qt's own translations. Yes carries AcceptRole and No RejectRole, which is what accepted/rejected below hang off.
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        yesButton = buttonBox.button(QDialogButtonBox.StandardButton.Yes)
        noButton = buttonBox.button(QDialogButtonBox.StandardButton.No)

        # Make No the default and give it focus, so pressing Enter or Space out of habit cancels rather than merging. This has to happen after the box is in the layout and it has to demote Yes
        # explicitly: a QDialogButtonBox hands the default to its accept-role button as it is laid out, which silently undoes a setDefault() made any earlier.
        if yesButton is not None:

            yesButton.setAutoDefault(False)
            yesButton.setDefault(False)

        if noButton is not None:

            noButton.setAutoDefault(True)
            noButton.setDefault(True)
            noButton.setFocus()

def confirmMerge(textNameList, targetName, parent=None):

    dlg = ConfirmMergeDlg(textNameList, targetName, parent)

    return dlg.exec() == QDialog.DialogCode.Accepted

# The combo entry that means "I am choosing the texts myself". Kept as a module constant so loadGroups and the handlers cannot drift apart on its wording.
MANUAL_SELECTION_KEY = '<manual>'

# The LCM class name of a discourse-chart cell that holds words of the text, as ICmObject.ClassName reports it. Cells are polymorphic and this is the only kind that means the chart is really in use.
CONST_CHART_WORD_GROUP = 'ConstChartWordGroup'

def rowTriple(listWidget, row):

    # The (name, IText, IStText) triple carried by one row. The Qt stubs type item() as Optional, but every row index here comes from the widget's own count or from its own selectedItems(), so the
    # row cannot be absent; assert rather than guard, since a None here would mean the list changed underneath us and returning a fallback would silently drop a text from the merge.
    item = listWidget.item(row)
    assert item is not None, f'row {row} is missing from the list'

    return item.data(Qt.ItemDataRole.UserRole)

def takeRow(listWidget, row):

    # Same reasoning as rowTriple: takeItem() is typed Optional but is only ever called here with a row the widget just reported.
    item = listWidget.takeItem(row)
    assert item is not None, f'row {row} could not be taken from the list'

    return item

class MergeTextsDlg(QDialog):

    def __init__(self, DB, report, activeTextName, parent=None):

        super().__init__(parent)

        self.DB = DB
        self.report = report
        self.activeTextName = activeTextName

        self.retVal = False
        self.mergeInfo = None

        # Latches once the user types in the name box, after which the suggested name never overwrites what they typed. See THE SUGGESTED NAME above.
        self.nameEditedByUser = False

        # Set while the code itself is repopulating the lists, so the handlers that would flip the combo to "(manual selection)" stay quiet.
        self.loadingLists = False

        self.ui = Ui_MergeTextsWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.textTripleList = []
        self.groupList = []

        # The two hazard buckets checkHazards fills in. Initialized here so refreshButtons can read them before the first refresh has run.
        self.fatalList = []
        self.warnList = []

        self.loadTexts()
        self.loadGroups()
        self.connectSignals()

        # Fill the lists from whichever group the combo landed on, then bring the name box, the summary and the buttons into line with it.
        self.onGroupChanged(self.ui.groupCombo.currentIndex())

    def loadTexts(self):

        """Read every text in the project once, into (name, IText, IStText) triples.

        Done up front, before anything is moved, because walking the repository while modifying it would invalidate the iterator part way through - the same reasoning DeleteTexts.py gives.
        """

        contentsObjList = []
        textObjList = []
        nameList = Utils.getSourceTextList(self.DB, matchingContentsObjList=contentsObjList, textObjList=textObjList)

        tripleList = list(zip(nameList, textObjList, contentsObjList))

        # Sort by name, case-insensitively, the way source text lists are sorted elsewhere in FLExTrans.
        self.textTripleList = sorted(tripleList, key=lambda textTriple: textTriple[0].casefold())

    def loadGroups(self):

        """Fill the group combo from the text names, plus the manual entry. Each row carries the group's base name under UserRole so the handler needn't parse the display string back apart."""

        self.groupList = MergeTextsUtils.groupTextNames([textName for textName, _textObj, _contentsObj in self.textTripleList])

        self.loadingLists = True

        for displayBase, memberList in self.groupList:

            self.ui.groupCombo.addItem(_translate("MergeTextsDlg", "{displayBase}  ({count} texts)").format(displayBase=displayBase, count=len(memberList)), displayBase)

        self.ui.groupCombo.addItem(_translate("MergeTextsDlg", "(choose the texts myself)"), MANUAL_SELECTION_KEY)

        self.loadingLists = False

    def connectSignals(self):

        self.ui.groupCombo.currentIndexChanged.connect(self.onGroupChanged)
        self.ui.addButton.clicked.connect(self.onAddClicked)
        self.ui.removeButton.clicked.connect(self.onRemoveClicked)
        self.ui.moveUpButton.clicked.connect(self.onMoveUpClicked)
        self.ui.moveDownButton.clicked.connect(self.onMoveDownClicked)
        self.ui.sortByNameButton.clicked.connect(self.onSortByNameClicked)
        self.ui.targetNameEdit.textEdited.connect(self.onTargetNameEdited)
        self.ui.moveTagsCheck.toggled.connect(self.refreshSummary)
        self.ui.proceedAnywayCheck.toggled.connect(self.refreshButtons)
        self.ui.availableList.itemSelectionChanged.connect(self.refreshButtons)
        self.ui.selectedList.itemSelectionChanged.connect(self.refreshButtons)

        # Double-clicking a row moves just that one across, which is the quickest way to build a selection by hand and the gesture people try first in a two-list chooser.
        self.ui.availableList.itemDoubleClicked.connect(self.onAvailableDoubleClicked)
        self.ui.selectedList.itemDoubleClicked.connect(self.onSelectedDoubleClicked)
        self.ui.mergeButton.clicked.connect(self.onMergeClicked)
        self.ui.cancelButton.clicked.connect(self.onCancelClicked)

    def makeItem(self, textTriple):

        """A list row for one text: it displays the name but carries the whole (name, IText, IStText) triple. See WHY EACH ROW CARRIES ITS OBJECT above."""

        textName = textTriple[0]

        # Mark the text FLExTrans is currently set up to translate, so the user can see which one it is before merging it away.
        if self.activeTextName and textName == self.activeTextName:

            displayName = _translate("MergeTextsDlg", "{textName}  [current FLExTrans source text]").format(textName=textName)

        else:
            displayName = textName

        item = QListWidgetItem(displayName)
        item.setData(Qt.ItemDataRole.UserRole, textTriple)

        return item

    def selectedTriples(self):

        """The (name, IText, IStText) triples in the merge list, in merge order."""

        return [rowTriple(self.ui.selectedList, row) for row in range(self.ui.selectedList.count())]

    def onGroupChanged(self, _index):

        # Repopulating the lists is not a hand edit, so don't let it flip the combo back to manual.
        if self.loadingLists:

            return

        groupKey = self.ui.groupCombo.currentData()

        # A fresh group means the previously suggested name no longer applies, so let the suggestion take over the box again.
        self.nameEditedByUser = False

        if groupKey == MANUAL_SELECTION_KEY:

            self.loadGroupSelection([])

        else:
            memberNameSet = set()

            for displayBase, memberList in self.groupList:

                if displayBase == groupKey:

                    memberNameSet = set(memberList)
                    break

            # Keep the group's own reading order rather than the alphabetical order of textTripleList, so 'Matthew 9' still precedes 'Matthew 10'.
            memberTripleList = [textTriple for textTriple in self.textTripleList if textTriple[0] in memberNameSet]
            memberTripleList.sort(key=lambda textTriple: MergeTextsUtils.textNameSortKey(textTriple[0]))

            self.loadGroupSelection(memberTripleList)

    def loadGroupSelection(self, selectedTripleList):

        """Put selectedTripleList in the merge list and everything else in the available list."""

        self.loadingLists = True

        self.ui.selectedList.clear()
        self.ui.availableList.clear()

        for textTriple in selectedTripleList:

            self.ui.selectedList.addItem(self.makeItem(textTriple))

        # Compare on identity of the IText object rather than on the name, since two texts can legitimately share a name.
        selectedHvoSet = {textTriple[1].Hvo for textTriple in selectedTripleList}

        for textTriple in self.textTripleList:

            if textTriple[1].Hvo in selectedHvoSet:

                continue

            self.ui.availableList.addItem(self.makeItem(textTriple))

        self.loadingLists = False

        self.refreshSummary()

    def switchToManualSelection(self):

        """Flip the combo to the manual entry without reloading the lists, which is what a hand edit means."""

        manualIndex = self.ui.groupCombo.findData(MANUAL_SELECTION_KEY)

        if manualIndex < 0 or self.ui.groupCombo.currentIndex() == manualIndex:

            return

        self.loadingLists = True
        self.ui.groupCombo.setCurrentIndex(manualIndex)
        self.loadingLists = False

    def onAddClicked(self):

        # Take the rows in list order rather than in the order they were Ctrl-clicked, so adding a block of chapters appends them in chapter order.
        rowList = sorted([self.ui.availableList.row(item) for item in self.ui.availableList.selectedItems()])

        if not rowList:

            return

        addTripleList = [rowTriple(self.ui.availableList, row) for row in rowList]

        # Remove from the bottom up, so each takeItem does not shift the rows still to be removed.
        for row in reversed(rowList):

            self.ui.availableList.takeItem(row)

        for textTriple in addTripleList:

            self.ui.selectedList.addItem(self.makeItem(textTriple))

        self.switchToManualSelection()
        self.refreshSummary()

    def onRemoveClicked(self):

        rowList = sorted([self.ui.selectedList.row(item) for item in self.ui.selectedList.selectedItems()])

        if not rowList:

            return

        for row in reversed(rowList):

            item = takeRow(self.ui.selectedList, row)
            self.ui.availableList.addItem(self.makeItem(item.data(Qt.ItemDataRole.UserRole)))

        # The available list is a plain pool rather than an ordering, so keep it alphabetical the way it started.
        self.sortAvailableList()

        self.switchToManualSelection()
        self.refreshSummary()

    def onAvailableDoubleClicked(self, item):

        # Narrow the selection to the row that was double-clicked, then reuse the Add path so that the flip to manual selection and the refresh all happen in one place rather than being repeated here.
        self.ui.availableList.setCurrentItem(item)

        self.onAddClicked()

    def onSelectedDoubleClicked(self, item):

        self.ui.selectedList.setCurrentItem(item)

        self.onRemoveClicked()

    def sortAvailableList(self):

        tripleList = [rowTriple(self.ui.availableList, row) for row in range(self.ui.availableList.count())]
        tripleList.sort(key=lambda textTriple: textTriple[0].casefold())

        self.loadingLists = True
        self.ui.availableList.clear()

        for textTriple in tripleList:

            self.ui.availableList.addItem(self.makeItem(textTriple))

        self.loadingLists = False

    def moveSelectedRows(self, offset):

        """Move the selected merge-list rows one place up (offset -1) or down (offset +1), keeping them selected."""

        rowList = sorted([self.ui.selectedList.row(item) for item in self.ui.selectedList.selectedItems()])

        if not rowList:

            return

        # Walk the rows in the direction of travel, so a block of rows moves as a block instead of the first one blocking the rest.
        if offset > 0:

            rowList = list(reversed(rowList))

        # Refuse the whole move if the leading row is already at the end it is heading for, which is what keeps a block from collapsing onto itself.
        for row in rowList:

            if row + offset < 0 or row + offset >= self.ui.selectedList.count():

                return

        for row in rowList:

            item = takeRow(self.ui.selectedList, row)
            self.ui.selectedList.insertItem(row + offset, item)
            item.setSelected(True)

        self.switchToManualSelection()
        self.refreshSummary()

    def onMoveUpClicked(self):

        self.moveSelectedRows(-1)

    def onMoveDownClicked(self):

        self.moveSelectedRows(1)

    def onSortByNameClicked(self):

        tripleList = self.selectedTriples()
        tripleList.sort(key=lambda textTriple: MergeTextsUtils.textNameSortKey(textTriple[0]))

        self.loadingLists = True
        self.ui.selectedList.clear()

        for textTriple in tripleList:

            self.ui.selectedList.addItem(self.makeItem(textTriple))

        self.loadingLists = False

        self.refreshSummary()

    def onTargetNameEdited(self, _text):

        # textEdited fires only for typing, not for our own setText, so this is a reliable signal that the name is now the user's. See THE SUGGESTED NAME above.
        self.nameEditedByUser = True

        self.refreshButtons()

    def refreshSummary(self):

        """Bring the suggested name, the summary line and the warnings into line with the current selection. Called after every change to the lists or the checkboxes."""

        tripleList = self.selectedTriples()
        nameList = [textName for textName, _textObj, _contentsObj in tripleList]

        # Only ever suggest; never overwrite a name the user typed.
        if not self.nameEditedByUser:

            self.ui.targetNameEdit.setText(self.suggestedName(nameList))

        summaryStr = _translate("MergeTextsDlg", "{textCount} text(s) selected.").format(textCount=len(tripleList))

        # The chapter coverage is worth saying because a gap or a doubled chapter is usually a mistake in the selection. A paragraph count is not - it tells the user nothing they can act on.
        coverageStr = self.coverageDescription(nameList)

        if coverageStr:

            summaryStr += '  ' + coverageStr

        self.ui.summaryLabel.setText(summaryStr)

        # The Move-text-tags option only means something when some selected text actually has tags, which is unusual, so the checkbox stays out of the way until it applies.
        self.ui.moveTagsCheck.setVisible(self.taggedTextCount(tripleList) > 0)

        self.refreshHazards(tripleList)
        self.refreshButtons()

    def coverageDescription(self, nameList):

        """A sentence saying which chapters the selection covers and whether any are missing or doubled. Empty unless every text in the selection carries a chapter number.

        MergeTextsUtils.chapterCoverage deliberately hands back plain numbers rather than a ready-made sentence, because that file has no .ts of its own. The wording is assembled here so that it
        goes through _translate and appears in the interface language.
        """

        coverage = MergeTextsUtils.chapterCoverage(nameList)

        if coverage is None:

            return ''

        lowChap, highChap, missingList, overlapList = coverage

        # "Covers chapters 8 to 8." reads like a mistake, so a selection that lands on one chapter gets the singular wording instead of a range with the same number at both ends.
        if lowChap == highChap:

            descriptionStr = _translate("MergeTextsDlg", "Covers chapter {chapNum}.").format(chapNum=lowChap)

        else:
            descriptionStr = _translate("MergeTextsDlg", "Covers chapters {lowChap} to {highChap}.").format(lowChap=lowChap, highChap=highChap)

        if missingList:

            descriptionStr += ' ' + _translate("MergeTextsDlg", "Missing: {chapterList}.").format(chapterList=', '.join([str(chapNum) for chapNum in missingList]))

        if overlapList:

            descriptionStr += ' ' + _translate("MergeTextsDlg", "Covered twice: {chapterList}.").format(chapterList=', '.join([str(chapNum) for chapNum in overlapList]))

        # A single chapter cannot have a gap in it, so the reassurance would be noise there. It is only worth saying when the selection spans a range that could have had one.
        if not missingList and not overlapList and lowChap != highChap:

            descriptionStr += ' ' + _translate("MergeTextsDlg", "No gaps.")

        return descriptionStr

    def suggestedName(self, nameList):

        """The name to offer for the merged text, given the names currently selected."""

        if not nameList:

            return ''

        groupKey = self.ui.groupCombo.currentData()

        # In manual mode there is no group base to build on, so derive one from what is actually selected.
        if groupKey == MANUAL_SELECTION_KEY or groupKey is None:

            displayBase = MergeTextsUtils.parseTextName(nameList[0])[0]

        else:
            displayBase = groupKey

        return MergeTextsUtils.mergedTextName(displayBase, nameList)

    def chartHasWords(self, chart):

        """Whether a discourse chart actually has any words placed in it."""

        for row in chart.RowsOS:

            for cellPart in row.CellsOS:

                # CellsOS is polymorphic: a cell can be a word group, a chart tag, a moved-text marker or a clause marker, and only a word group holds actual words of the text. ClassName is the
                # way to tell LCM subtypes apart from Python - the C# kclsid* class-id constants are not projected through pythonnet and raise AttributeError if you reach for them.
                if cellPart.ClassName == CONST_CHART_WORD_GROUP:

                    return True

        return False

    def chartLists(self, tripleList):

        """The discourse charts based on the selected texts, split into (chartsWithWords, emptyChartList).

        The split matters because the two cases deserve opposite treatment. FLEx creates a chart shell as soon as the Discourse view is opened on a text, so most charts found here have no words in
        them at all and mean nothing to the user - those are deleted as part of the merge and never mentioned. A chart that does have words represents real work that a merge would strand, since a
        chart names its text through BasedOnRA and that text is about to be deleted, so those are named in a warning the user has to acknowledge.
        """

        stTextHvoSet = {contentsObj.Hvo for _textName, _textObj, contentsObj in tripleList if contentsObj is not None}

        chartsWithWords = []
        emptyChartList = []

        for chart in self.DB.ObjectsIn(IDsConstChartRepository):

            if chart.BasedOnRA is None or chart.BasedOnRA.Hvo not in stTextHvoSet:

                continue

            if self.chartHasWords(chart):

                chartsWithWords.append(chart)

            else:
                emptyChartList.append(chart)

        return chartsWithWords, emptyChartList

    def taggedTextCount(self, tripleList):

        """How many text tags the selected texts carry between them. Nothing to say - and no checkbox to show - when this is zero."""

        return sum([contentsObj.TagsOC.Count for _textName, _textObj, contentsObj in tripleList if contentsObj is not None])

    def writingSystemLabel(self, wsHandle):

        """A human name for a writing system handle, falling back to the handle itself so a warning never fails to be shown."""

        try:
            return self.DB.project.ServiceLocator.WritingSystemManager.Get(wsHandle).DisplayLabel

        except Exception:
            return str(wsHandle)

    def checkHazards(self, tripleList):

        """The warnings for the current selection, as (fatalList, warnList). A fatal hazard disables Merge; a warning only needs proceedAnywayCheck ticked. See THE HAZARDS above."""

        fatalList = []
        warnList = []

        if len(tripleList) < 2:

            return fatalList, warnList

        emptyNameList = []
        mediaNameList = []
        wsMap = {}

        # Only charts that actually have words in them are a problem; the empty shells FLEx leaves behind are deleted during the merge without troubling the user. See chartLists().
        chartsWithWords, _emptyChartList = self.chartLists(tripleList)
        chartedHvoSet = {chart.BasedOnRA.Hvo for chart in chartsWithWords}

        chartedNameList = []

        for textName, textObj, contentsObj in tripleList:

            # No contents object at all means there are no paragraphs to move and nothing to do with this text. Nothing sensible can be done automatically, so it blocks the merge.
            if contentsObj is None:

                fatalList.append(_translate("MergeTextsDlg", 'The text "{textName}" has no contents and cannot be merged. Remove it from the list.').format(textName=textName))
                continue

            if contentsObj.ParagraphsOS.Count == 0:

                emptyNameList.append(textName)

            if contentsObj.Hvo in chartedHvoSet:

                chartedNameList.append(textName)

            # Media files and a notebook record belong to the IText, so deleting it destroys them. The source texts are always deleted, so this is always worth saying.
            if textObj.MediaFilesOA is not None:

                mediaNameList.append(textName)

            wsMap.setdefault(contentsObj.MainWritingSystem, []).append(textName)

        if emptyNameList:

            warnList.append(_translate("MergeTextsDlg", "These texts have no paragraphs and will be skipped: {nameList}.").format(nameList=', '.join(emptyNameList)))

        # More than one vernacular writing system in the selection is legal, and the paragraphs keep their own writing systems either way.
        # But the merged text would then have mixed content, which is nearly always a mistake rather than something the user meant.
        if len(wsMap) > 1:

            labelList = [self.writingSystemLabel(wsHandle) for wsHandle in wsMap]
            warnList.append(_translate("MergeTextsDlg", "The selected texts use more than one writing system ({wsList}), so the merged text would have mixed content.").format(wsList=', '.join(labelList)))

        if chartedNameList:

            warnList.append(_translate("MergeTextsDlg", "A discourse chart is based on these texts and will be left pointing at nothing: {nameList}. Delete those charts in the FLEx Discourse area first, then merge, then chart the merged text.").format(nameList=', '.join(chartedNameList)))

        if mediaNameList:

            warnList.append(_translate("MergeTextsDlg", "These texts have media files, which belong to the text and not to its paragraphs. They will not be deleted, so their media survives: {nameList}.").format(nameList=', '.join(mediaNameList)))

        if not self.ui.moveTagsCheck.isChecked():

            taggedCount = self.taggedTextCount(tripleList)

            if taggedCount:

                warnList.append(_translate("MergeTextsDlg", "{count} text tag(s) will be lost, because moving text tags to the merged text is turned off.").format(count=taggedCount))

        return fatalList, warnList

    def refreshHazards(self, tripleList):

        self.fatalList, self.warnList = self.checkHazards(tripleList)

        messageList = self.fatalList + self.warnList

        if not messageList:

            self.ui.hazardLabel.setText('')
            self.ui.hazardLabel.setVisible(False)
            self.ui.proceedAnywayCheck.setVisible(False)
            self.ui.proceedAnywayCheck.setChecked(False)
            return

        self.ui.hazardLabel.setText('<b>' + _translate("MergeTextsDlg", "Please read:") + '</b><ul><li>' + '</li><li>'.join(messageList) + '</li></ul>')
        self.ui.hazardLabel.setVisible(True)

        # Only ask for an acknowledgement when there is something the user can actually proceed past. A fatal hazard has to be fixed instead.
        showProceed = bool(self.warnList)

        if not showProceed:

            self.ui.proceedAnywayCheck.setChecked(False)

        self.ui.proceedAnywayCheck.setVisible(showProceed)

    def refreshButtons(self):

        selectedCount = self.ui.selectedList.count()

        self.ui.addButton.setEnabled(len(self.ui.availableList.selectedItems()) > 0)
        self.ui.removeButton.setEnabled(len(self.ui.selectedList.selectedItems()) > 0)
        self.ui.moveUpButton.setEnabled(len(self.ui.selectedList.selectedItems()) > 0)
        self.ui.moveDownButton.setEnabled(len(self.ui.selectedList.selectedItems()) > 0)
        self.ui.sortByNameButton.setEnabled(selectedCount > 1)

        canMerge = selectedCount > 1 and bool(self.ui.targetNameEdit.text().strip()) and not self.fatalList

        # A warning has to be acknowledged before Merge comes alive, which is what the proceed checkbox is for.
        if self.warnList and not self.ui.proceedAnywayCheck.isChecked():

            canMerge = False

        self.ui.mergeButton.setEnabled(canMerge)

    def nameIsAcceptable(self, tripleList, targetName):

        """Check the merged name against the names already in the project, offering a unique one when it is taken. Returns the name to use, or None to stay in the dialog."""

        selectedHvoSet = {textObj.Hvo for _textName, textObj, _contentsObj in tripleList}

        # A name that matches one of the texts being merged is refused rather than resolved. The clash would disappear when that text is deleted, but only if deletion is even switched on, and
        # relying on FLEx tolerating two texts of the same name in between is not worth finding out.
        for textName, textObj, _contentsObj in self.textTripleList:

            if textObj.Hvo in selectedHvoSet and textName == targetName:

                QMessageBox.warning(self, _translate("MergeTextsDlg", "Name Already Used"),
                                    _translate("MergeTextsDlg", 'The name "{targetName}" belongs to one of the texts you are merging. Choose a different name for the merged text, or take that text out of the list.').format(targetName=targetName))
                return None

        clashNameList = [textName for textName, textObj, _contentsObj in self.textTripleList if textObj.Hvo not in selectedHvoSet and textName == targetName]

        if not clashNameList:

            return targetName

        # The name is taken by a text that is staying put. Offer the same ' - Copy' style name FLExTrans uses elsewhere rather than silently renaming.
        uniqueName = Utils.createUniqueTitle(self.DB, targetName)

        answer = QMessageBox.question(self, _translate("MergeTextsDlg", "Name Already Used"),
                                      _translate("MergeTextsDlg", 'The {projectName} project already has a text called "{targetName}". Use the name "{uniqueName}" instead?').format(projectName=self.DB.ProjectName(), targetName=targetName, uniqueName=uniqueName),
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

        if answer != QMessageBox.StandardButton.Yes:

            return None

        self.ui.targetNameEdit.setText(uniqueName)
        self.nameEditedByUser = True

        return uniqueName

    def onMergeClicked(self):

        tripleList = self.selectedTriples()

        if len(tripleList) < 2:

            QMessageBox.warning(self, _translate("MergeTextsDlg", "Nothing to Merge"), _translate("MergeTextsDlg", "Choose at least two texts to merge."))
            return

        targetName = self.ui.targetNameEdit.text().strip()

        if not targetName:

            QMessageBox.warning(self, _translate("MergeTextsDlg", "No Name"), _translate("MergeTextsDlg", "Type a name for the merged text."))
            return

        targetName = self.nameIsAcceptable(tripleList, targetName)

        if targetName is None:

            return

        nameList = [textName for textName, _textObj, _contentsObj in tripleList]

        if not confirmMerge(nameList, targetName, self):

            return

        # Recompute the chart split against the selection actually being merged, rather than trusting whatever the last refresh happened to see.
        _chartsWithWords, emptyChartList = self.chartLists(tripleList)

        self.mergeInfo = MergeInfo([textObj for _textName, textObj, _contentsObj in tripleList], targetName, self.ui.moveTagsCheck.isChecked(), emptyChartList)
        self.retVal = True

        self.accept()

    def onCancelClicked(self):

        self.retVal = False
        self.mergeInfo = None

        self.reject()
