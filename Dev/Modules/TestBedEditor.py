#
#   TestBedEditor
#
#   Lærke Roager Jespersen
#
#   Version 3.17.28 - 10/7/26 - Ron Lockwood
#    Say in the module description that the category and features or classes are filled in when you leave the lemma cell.
#
#   Version 3.17.27 - 10/7/26 - Ron Lockwood
#    Save a backup copy of the testbed file to Output\testbed-file-history before the first save.
#
#   Version 3.17.26 - 10/7/26 - Ron Lockwood
#    Align the Gram. Cat., Features and Affixes cells by their own text direction too, e.g. Latin-script tags left-aligned in a right-to-left tree.
#
#   Version 3.17.25 - 10/7/26 - Ron Lockwood
#    Fit the Expected Result column to the window so the Comment column keeps at least its header width, and show cut-off cell text in a tooltip.
#
#   Version 3.17.24 - 10/7/26 - Ron Lockwood
#    Mirror the tree for a right-to-left source, and lay out each expected result and comment by its own text direction.
#
#   Version 3.17.23 - 10/7/26 - Ron Lockwood
#    Show invalid tests in the log viewer's invalid color with the reason in red across the lexical unit columns of the test row.
#
#   Version 3.17.22 - 10/7/26 - Ron Lockwood
#    Sort completion lists case-insensitively, refuse to save a blank lemma or grammatical category, and call the X1.1 value a lemma in the UI.
#
#   Version 3.17.21 - 10/6/26 - Ron Lockwood
#    Added an Edit Transfer Rules button that opens the transfer rules file in XMLmind, the same as the Live Rule Tester's button.
#
#   Version 3.17.20 - 10/6/26 - Ron Lockwood
#    Use the shared Utils.reportTestbedFileMissing message when the testbed file does not exist.
#
#   Version 3.17.19 - 10/5/26 - Ron Lockwood
#    Fixes #1601. Show the source text and comment in the delete test confirmation.
#
#   Version 3.17.18 - 9/28/26 - Ron Lockwood
#    Start the Add Test dialog at twice its natural width.
#
#   Version 3.17.17 - 9/28/26 - Ron Lockwood
#    Lint fixes.
#
#   Version 3.17.16 - 9/28/26 - Ron Lockwood
#    Size the header and columns to fit their bold header text, letting the comment column shrink to compensate.
#
#   Version 3.17.15 - 9/28/26 - Ron Lockwood
#    Wrote a full module description, including how to separate multiple features, classes or affixes with a period.
#
#   Version 3.17.14 - 9/28/26 - Ron Lockwood
#    Translate all UI strings and load the translations for this module, its window and the libraries it uses.
#
#   Version 3.17.13 - 9/25/26 - Ron Lockwood
#    Use a light-grey background for the selected tree item.
#
#   Version 3.17.12 - 9/25/26 - Ron Lockwood
#    Fix features and affixes not being reset for each lexical unit when loading the tree.
#
#   Version 3.17.11 - 9/24/26 - Ron Lockwood
#    Prevent editing lexical-unit fields on test rows.
#
#   Version 3.17.10 - 9/24/26 - Ron Lockwood
#    Prevent editing expected results and comments on lexical unit rows.
#
#   Version 3.17.9 - 9/25/26 - Ron Lockwood
#    New context menu for adding and deleting lexical unit lines.
#
#   Version 3.17.8 - 9/25/26 - Ron Lockwood
#    Add inflection classes to the completion data, not just features.
#
#   Version 3.17.7 - 9/24/26 - Ron Lockwood
#    Add a font-size control matching the testbed log viewer.
#
#   Version 3.17.6 - 9/23/26 - Ron Lockwood
#    Remove the opaque tree selection highlight so selected text remains readable.
#
#   Version 3.17.5 - 9/23/26 - Ron Lockwood
#    Auto-fill category and feature/class data after committing a lemma edit.
#
#   Version 3.17.4 - 9/23/26 - Ron Lockwood
#    Restrict completion delegates to lexical-unit child rows and use styled painting.
#
#   Version 3.17.3 - 9/23/26 - Ron Lockwood
#    Add ReplacementEditor-style completion data to lexical-unit child rows.
#
#   Version 3.17.2 - 9/23/26 - Ron Lockwood
#    Color lexical-unit child rows by lemma, grammatical category and feature/tag type.
#
#   Version 3.17.1 - 9/23/26 - Ron Lockwood
#    Connect Delete Test to remove the selected test after confirmation.
#
#   Version 3.17 - 9/23/26 - Ron Lockwood
#    Connect Add Test to create a new test and canned lexical unit.
#
#   Version 1.0 - 6/27/26 - Lærke Roager Jespersen
#    First version. Loads testbed tests into an editable tree view.
#    Double-click any cell to edit. Save writes changes back to the XML file.
#

# OVERVIEW (AI generated, then edited)
#
# This module provides the editable tree view for the FLExTrans testbed. Each top-level row represents a test and its child rows represent the lexical units that make up the source input. The tree is loaded 
# from the XML model, and Save writes edits back through the model before serializing the testbed file.
#
# ADDING TESTS
#
# Add Test collects the three text fields needed by a test, creates a model object with one canned lexical unit, and appends both the model object and its tree row. Keeping the model object attached to the row 
# is important because Save uses that object to find the new XML node.
#
# INVALID TESTS
#
# When the testbed is run, each test is validated against the source FLEx project, and a test with a lemma, category or tag that no longer exists is marked is_valid="no" with an invalidReason
# attribute. _loadTree shows such a test, and its lexical units, in the log viewer's invalid color (PUNC_COLOR) and puts the reason on the test row's Gram. Cat. cell under INVALID_REASON_ROLE.
# A QTreeWidget can't span just some columns, so LexicalUnitColumnDelegate paints the reason, in red, across the Gram. Cat., Features and Affixes cells. It draws it while painting the last of
# them in visual order, because the view paints cells in that order and the later cells' backgrounds would otherwise cover it. The reason is never item text, so Save ignores it and resizing the
# columns to their contents doesn't widen them to fit it. The editor doesn't revalidate: the reason stays until the testbed is next run, even if the user fixes the test here.
#
# TEXT DIRECTION
#
# The testbed's source_direction attribute says whether the source language is right to left. If it is, the whole tree is mirrored, as in the testbed log viewer: the Source column is on the right
# and text is right-aligned. But not every cell runs the same way as the source: the expected result is in the target language, a comment can be in any language, and categories, features and
# affixes are often Latin script. So both delegates call setDirectionFromText, which lays out each of those cells by its own text (Utils.hasRtl), using AlignAbsolute so a mirrored tree doesn't
# flip the alignment back. The Source/Lemma column alone follows the tree, keeping its text next to the expand arrows. The invalid reason is in the UI language and is aligned the same way.
#
# COLUMN WIDTHS
#
# Columns are fitted to their contents when the tree loads, except Expected Result. A testbed with sentence-length tests would make that column as wide as its longest sentence, even one far
# down the list, and push the Comment column off the edge. So _fitExpectedColumn gives it its content width but no more than leaves Comment the width of its header text, and runs again whenever
# the tree's viewport changes width (an event filter on the viewport, not the tree: the viewport is resized after the tree's own resize event). Once the user drags the column themselves it is left
# alone; autoSizingColumns is what lets _onSectionResized tell their drag from our own resizes. Any cell too narrow for its text shows the full text as a tooltip (showToolTipIfCutOff).
#
# CODE STRUCTURE
#
# setDirectionFromText and showToolTipIfCutOff are helpers both delegates call, from initStyleOption and helpEvent respectively. LexicalUnitColumnDelegate is the completion delegate for
# the lexical unit columns, plus per-cell text direction (except Source/Lemma) and the invalid reason painting. ChildRowReadOnlyDelegate keeps the Expected Result and Comment columns
# read-only on lexical unit rows and sets each cell's text direction. Main.__init__ mirrors the tree for a right-to-left source, loads the tree and connects controls. _loadTree creates rows from the model and fits the columns to their contents. _fitHeaderText makes the header tall enough, and each column wide
# enough, for its bold header text, then re-fits Expected Result. _fitExpectedColumn, _onSectionResized and eventFilter handle the Expected Result width (see COLUMN WIDTHS). _addTest creates and
# appends a new test. _deleteTest removes the selected test after confirmation. _onItemChanged tracks edits and re-fits Expected Result when one changes. save first calls _findBlankLexicalUnit
# and refuses to write if any lexical unit row has a blank lemma or grammatical category; otherwise it writes all rows. closeEvent handles unsaved changes and keeps the window open if that save
# is refused. _editTransferRules opens the transfer rules file (Transfer Rules File setting, read in MainFunction) in XMLmind XML Editor, just as the Live Rule Tester's Edit Transfer Rules button does.
#
# TRANSLATION
#
# The docs dictionary is translated at import time, so the module-level code loads just this module's .qm before docs is built. MainFunction then loads the .qm files for the libraries and the window
# (librariesToTranslate) plus Qt's base translations for the standard buttons in the message boxes. Strings in the window itself come from TestBedEditorWindow.ui and live in TestBedEditorWindow_xx.ts.
#

import html
import os
from subprocess import call
from typing import Optional
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                             QFormLayout, QLineEdit, QMainWindow, QMenu,
                             QStyle, QStyledItemDelegate, QToolTip, QTreeWidgetItem,
                             QMessageBox)
from PyQt6.QtCore import QCoreApplication, QEvent, QRect, Qt
from PyQt6.QtGui import QAction, QCloseEvent, QFont, QFontMetrics, QBrush, QColor, QIcon, QPalette

from flextoolslib import (
    FlexToolsModuleClass,
    FTM_Name, FTM_Version, FTM_ModifiesDB,
    FTM_Synopsis, FTM_Help, FTM_Description,
)

import ReadConfig
import FTPaths
import Mixpanel
import Utils
from CompletionData import (CompleterDelegate, gatherCompletionData,
                            gatherPOSTags, gatherTags)
from Testbed import (FlexTransTestbedFile, SENT,
                     HEAD_WORD, SENSE_NUM, GRAM_CAT, OTHER_TAGS, TAG,
                     SOURCE_INPUT, LEXICAL_UNITS, LEXICAL_UNIT,
                     TARGET_OUTPUT, EXPECTED_RESULT, LexicalUnit,
                     TestbedTestXMLObject, LEMMA_COLOR, GRAM_CAT_COLOR,
                     AFFIX_COLOR, PUNC_COLOR, NOT_FOUND_COLOR,
                     TAG_BEFORE_EDITOR_SAVE)

from TestBedEditorWindow import Ui_TestBedEditorWindow

_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TestBedEditor'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# Libraries (and the window) whose translations we load in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'Testbed', 'TestBedEditorWindow']

docs = {
    FTM_Name:        _translate("TestBedEditor", "Testbed Editor"),
    FTM_Version:     "3.17.28",
    FTM_ModifiesDB:  False,
    FTM_Synopsis:    _translate("TestBedEditor", "View and edit tests in the testbed."),
    FTM_Help:        "",
    FTM_Description: _translate("TestBedEditor",
"""View and edit the tests in the testbed. Each test is a row showing its source text, expected result and comment, with a row under it for each lexical unit in the test's source input. Double-click a cell to edit it. For a lexical unit, enter the lemma (the headword with its homograph and sense numbers, e.g. house1.1), the grammatical category, any features or classes, and any affixes. As you type, suggestions from the source FLEx project are offered. After you choose a lemma, its category and features or classes are filled in when you leave the cell. Separate multiple features, classes or affixes with a period, e.g. sg.pst. Right-click a row to add or delete a lexical unit. Use Add Test and Delete Test to add or remove whole tests, and click Save to write your changes to the testbed file."""),
}

# Column indices
COL_SOURCE   = 0  # test: origin (read-only);  LU: headword.sense#
COL_GRAMCAT  = 1  # LU: grammatical category
COL_FEATURES = 2  # LU: features/classes
COL_AFFIXES  = 3  # LU: affixes
COL_EXPECTED = 4  # test: expected result
COL_COMMENT  = 5  # test: comment

TEST_BG_COLOR = QColor('#D6E4F0')
TEST_HIGHLIGHT_COLOR = QColor('#D3D3D3')

# Text color for a test the testbed marked invalid - the same color the testbed log viewer recolors an invalid test's lexical units to. Its reason is red so it stands out.
INVALID_TEXT_COLOR = QColor('#' + PUNC_COLOR)
INVALID_REASON_COLOR = QColor('#' + NOT_FOUND_COLOR)

# The columns of a test row that the invalid reason is drawn across.
REASON_SPAN_COLUMNS = (COL_GRAMCAT, COL_FEATURES, COL_AFFIXES)

# Item data role holding an invalid test's reason, stored on the test row's grammatical category cell.
INVALID_REASON_ROLE = Qt.ItemDataRole.UserRole + 1

EDITABLE   = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |
              Qt.ItemFlag.ItemIsEditable)
READ_ONLY  = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

def setDirectionFromText(option, index):

    # Lay out and align a cell by the direction of its own text rather than the tree's. The tree follows the source direction, but a cell can hold text that runs the other way: a target-language
    # expected result, a comment in any language, or Latin-script categories and tags in a right-to-left tree. AlignAbsolute keeps left meaning left in a right-to-left tree, where Qt would otherwise
    # flip it. The stubs type option as Optional, but Qt always passes one.
    if option is None:

        return

    text = index.data(Qt.ItemDataRole.DisplayRole)

    if not text:

        return

    if Utils.hasRtl(text):

        option.direction = Qt.LayoutDirection.RightToLeft
        option.displayAlignment = Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    else:
        option.direction = Qt.LayoutDirection.LeftToRight
        option.displayAlignment = Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

def showToolTipIfCutOff(delegate, event, view, option, index):

    # Show a cell's full text as its tooltip when the cell is too narrow to show all of it, and no tooltip when it all fits. Returns False when the cell should get the normal tooltip handling instead:
    # it isn't a tooltip event, the cell is empty, or the item has a tooltip of its own (e.g. an invalid test's reason).
    if event is None or view is None or event.type() != QEvent.Type.ToolTip or index.data(Qt.ItemDataRole.ToolTipRole):

        return False

    text = index.data(Qt.ItemDataRole.DisplayRole)

    if not text:

        return False

    # The delegate's size hint is the width the whole text needs, margins included; option.rect is the width the cell actually has.
    if delegate.sizeHint(option, index).width() > option.rect.width():

        QToolTip.showText(event.globalPos(), text, view)
    else:
        QToolTip.hideText()

    return True

class LexicalUnitColumnDelegate(CompleterDelegate):

    # A CompleterDelegate for the lexical unit columns that also draws an invalid test's reason across the Gram. Cat., Features and Affixes cells of the test row. A QTreeWidget can only span
    # a whole row, so the reason isn't item text: it is painted here, which also keeps it from widening the columns when they are resized to their contents.
    def __init__(self, tree, *args):

        super().__init__(*args)
        self.tree = tree

    def helpEvent(self, event, view, option, index):

        if showToolTipIfCutOff(self, event, view, option, index):

            return True

        return super().helpEvent(event, view, option, index)

    def initStyleOption(self, option, index):

        super().initStyleOption(option, index)

        # Categories, features and affixes are often Latin script even when the source language is right to left, so align those cells by their own text. The Source/Lemma column keeps
        # following the tree: in a mirrored tree its expand arrows are on the right, and left-aligned text there would sit far from its arrow.
        if index.column() != COL_SOURCE:

            setDirectionFromText(option, index)

    def paint(self, painter, option, index):

        super().paint(painter, option, index)

        # Only test (top-level) rows carry a reason.
        if painter is None or index.parent().isValid():

            return

        reason = index.siblingAtColumn(COL_GRAMCAT).data(INVALID_REASON_ROLE)

        if not reason:

            return

        header = self.tree.header()

        # The stubs type header() as Optional, but a QTreeWidget always has a header view.
        assert header is not None
        visualIndexes = sorted(header.visualIndex(col) for col in REASON_SPAN_COLUMNS)

        # The view paints a row's cells in visual order, so draw the reason when painting the last of the spanned cells; drawn any earlier, the next cell's background would paint over it.
        # The user can drag the columns around, so if they are no longer side by side just draw the reason in the Gram. Cat. cell.
        if visualIndexes[-1] - visualIndexes[0] == len(REASON_SPAN_COLUMNS) - 1:

            if header.visualIndex(index.column()) != visualIndexes[-1]:

                return

            # Span the union of the three sections. In a right-to-left tree the visual order runs right to left on screen, so take the outer edges rather than assuming which cell is leftmost.
            sectionLefts = [header.sectionViewportPosition(col) for col in REASON_SPAN_COLUMNS]
            sectionRights = [header.sectionViewportPosition(col) + header.sectionSize(col) for col in REASON_SPAN_COLUMNS]
            textRect = QRect(min(sectionLefts), option.rect.top(), max(sectionRights) - min(sectionLefts), option.rect.height())

        elif index.column() == COL_GRAMCAT:

            textRect = QRect(option.rect)
        else:
            return

        # Inset the text the way the style insets ordinary cell text, and elide a reason too long for the space (the full reason is in the tooltip).
        style = self.tree.style()
        margin = style.pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin, None, self.tree) + 1 if style is not None else 4
        textRect.adjust(margin, 0, -margin, 0)

        reasonFont = QFont(option.font)
        reasonFont.setItalic(True)
        elidedReason = QFontMetrics(reasonFont).elidedText(reason, Qt.TextElideMode.ElideRight, textRect.width())

        # The reason is in the UI language, not the source language, so align it by its own direction. AlignAbsolute keeps a right-to-left tree from flipping the alignment.
        if Utils.hasRtl(reason):

            reasonAlignment = Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        else:
            reasonAlignment = Qt.AlignmentFlag.AlignAbsolute | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        painter.save()
        painter.setFont(reasonFont)
        painter.setPen(INVALID_REASON_COLOR)
        painter.drawText(textRect, reasonAlignment, elidedReason)
        painter.restore()


class ChildRowReadOnlyDelegate(QStyledItemDelegate):

    # The delegate for the Expected Result and Comment columns. It stops these cells being edited on lexical unit rows, and lays out each cell's text in its own direction.
    def createEditor(self, parent, option, index):
        if index.parent().isValid():
            return None

        return super().createEditor(parent, option, index)

    def helpEvent(self, event, view, option, index):

        if showToolTipIfCutOff(self, event, view, option, index):

            return True

        return super().helpEvent(event, view, option, index)

    def initStyleOption(self, option, index):

        super().initStyleOption(option, index)

        # The expected result is in the target language and the comment can be in any language, so like the log viewer's labels, lay out and align each cell by its own text.
        setDirectionFromText(option, index)


class Main(QMainWindow):

    def __init__(self, testObjList, testbedFileObj, report, DB, transferRulesFile):
        super().__init__()
        self.testObjList    = testObjList
        self.testbedFileObj = testbedFileObj
        self.transferRulesFile = transferRulesFile
        self.report         = report
        self.unsaved        = False
        self.sourceLemmas, self.sourceAffixes = gatherCompletionData(DB, report, testbedFileObj.composed)
        self.sourcePOS = gatherPOSTags(DB, report, [SENT])
        self.sourceTags = gatherTags(DB, report, self.sourcePOS)

        # State for fitting the Expected Result column (see _fitExpectedColumn). These must exist before _fontSizeChanged below first calls _fitHeaderText.
        self.headerWidths = {}               # column -> width of its bold header text, filled in by _fitHeaderText
        self.expectedContentWidth = None     # width the Expected Result contents need; None until measured or after they change
        self.autoSizingColumns = False       # True while we're resizing columns ourselves, so _onSectionResized can tell our resizes from the user's
        self.userSizedExpected = False       # set once the user drags the Expected Result column; we stop fitting it then

        self.ui = Ui_TestBedEditorWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        # When the source language is right to left, mirror the whole tree (columns and text) the way the testbed log viewer does. The expected result and comment cells still follow
        # their own text's direction (see ChildRowReadOnlyDelegate).
        if testbedFileObj.getFLExTransTestbedXMLObject().isRTL():

            self.ui.treeWidget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        treePalette = self.ui.treeWidget.palette()
        treePalette.setColor(QPalette.ColorRole.Highlight, TEST_HIGHLIGHT_COLOR)
        treePalette.setColor(QPalette.ColorRole.HighlightedText, treePalette.color(QPalette.ColorRole.Text))
        self.ui.treeWidget.setPalette(treePalette)

        # Watch for the user resizing the Expected Result column, and for the visible part of the tree changing width, so that column can be re-fitted (see _fitExpectedColumn).
        treeHeader = self.ui.treeWidget.header()
        treeViewport = self.ui.treeWidget.viewport()

        # The stubs type these as Optional, but a QTreeWidget always has a header view and a viewport.
        assert treeHeader is not None and treeViewport is not None
        treeHeader.sectionResized.connect(self._onSectionResized)
        treeViewport.installEventFilter(self)

        self.ui.fontSizeSpinBox.valueChanged.connect(self._fontSizeChanged)
        self.ui.fontSizeSpinBox.setValue(12)
        self._fontSizeChanged()

        self._loadTree()

        self.ui.treeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.treeWidget.customContextMenuRequested.connect(self._onTreeContextMenu)
        self.ui.treeWidget.itemChanged.connect(self._onItemChanged)
        self.ui.treeWidget.currentItemChanged.connect(self._onCurrentItemChanged)
        self.ui.addButton.clicked.connect(self._addTest)
        self.ui.deleteButton.clicked.connect(self._deleteTest)
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.editTransferRulesButton.clicked.connect(self._editTransferRules)
        self.ui.deleteButton.setEnabled(False)

        # Sort the completion lists case-insensitively so e.g. zu1.1 sits right after Zu1.1 instead of after every capitalized word. The second key element breaks ties so the
        # capitalized form consistently comes first.
        caseInsensitiveKey = lambda value: (value.casefold(), value)

        delegateData = [
            (sorted(self.sourceLemmas.keys(), key=caseInsensitiveKey), False, True, False),
            (sorted(self.sourcePOS, key=caseInsensitiveKey), False, True, True),
            (sorted(self.sourceTags, key=caseInsensitiveKey), True, True, True),
            (sorted(self.sourceAffixes, key=caseInsensitiveKey), True, True, True),
        ]
        self.delegates = [LexicalUnitColumnDelegate(self.ui.treeWidget, *args) for args in delegateData]
        for index, delegate in enumerate(self.delegates):
            self.ui.treeWidget.setItemDelegateForColumn(index, delegate)

        childRowReadOnlyDelegate = ChildRowReadOnlyDelegate(self.ui.treeWidget)
        self.ui.treeWidget.setItemDelegateForColumn(COL_EXPECTED, childRowReadOnlyDelegate)
        self.ui.treeWidget.setItemDelegateForColumn(COL_COMMENT, childRowReadOnlyDelegate)

    def _fontSizeChanged(self):
        treeFont = self.ui.treeWidget.font()
        treeFont.setPointSize(self.ui.fontSizeSpinBox.value())
        self.ui.treeWidget.setFont(treeFont)

        # The header text grows with the font size, so resize the header and columns again to keep it from being clipped. The Expected Result contents grow too, so measure them again.
        self.expectedContentWidth = None
        self._fitHeaderText()

    def _createDefaultLexicalUnitItem(self, parentItem, insertBefore=None):

        luItem = QTreeWidgetItem(parentItem) # At this point the item is added as the last child of parentItem

        if insertBefore is not None:

            oldIndex = parentItem.indexOfChild(luItem)
            newIndex = parentItem.indexOfChild(insertBefore)

            # Cut the item from where it is at the end.
            parentItem.takeChild(oldIndex)

            # Insert the item before the specified item that was right-clicked on.
            parentItem.insertChild(newIndex, luItem)

        luItem.setFlags(EDITABLE)
        luItem.setText(COL_SOURCE, 'word1.1')
        luItem.setText(COL_GRAMCAT, 'n')
        self._colorLexicalUnitItem(luItem)
        return luItem

    def _addLexicalUnitForItem(self, item):
        if item is None:
            return

        if item.parent() is None:
            parentItem = item
            insertBefore = None
        else:
            parentItem = item.parent()
            insertBefore = item

        luItem = self._createDefaultLexicalUnitItem(parentItem, insertBefore)
        self.ui.treeWidget.setCurrentItem(luItem)
        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'There are unsaved changes.'))

    def _deleteLexicalUnitForItem(self, item):
        if item is None or item.parent() is None:
            return

        parentItem = item.parent()
        parentItem.takeChild(parentItem.indexOfChild(item))
        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'There are unsaved changes.'))

    def _onTreeContextMenu(self, pos):
        item = self.ui.treeWidget.itemAt(pos)
        if item is None:
            return

        self.ui.treeWidget.setCurrentItem(item)
        menu = QMenu(self)

        addAction = QAction(_translate("TestBedEditor", 'Add Lexical Unit'), self)
        addAction.triggered.connect(lambda: self._addLexicalUnitForItem(item))
        menu.addAction(addAction)

        deleteAction = QAction(_translate("TestBedEditor", 'Delete this Lexical Unit'), self)
        deleteAction.setEnabled(item.parent() is not None)
        deleteAction.triggered.connect(lambda: self._deleteLexicalUnitForItem(item))
        menu.addAction(deleteAction)

        # The stubs type viewport() as Optional, but a QTreeWidget always has a viewport; guard anyway so the menu is simply skipped rather than crashing.
        viewport = self.ui.treeWidget.viewport()

        if viewport is None:

            return

        menu.exec(viewport.mapToGlobal(pos))

    # ------------------------------------------------------------------
    # Tree loading
    # ------------------------------------------------------------------

    def _loadTree(self):

        tree = self.ui.treeWidget
        tree.blockSignals(True)
        tree.clear()

        boldFont = QFont()
        boldFont.setBold(False)
        testBg = QBrush(TEST_BG_COLOR)

        for testObj in self.testObjList:

            # Test (parent) row — origin is read-only, expected + comment editable
            testItem = QTreeWidgetItem(tree)
            testItem.setFlags(EDITABLE)
            testItem.setText(COL_SOURCE,   testObj.getOrigin())
            testItem.setText(COL_EXPECTED, testObj.getExpectedResult() or '')
            testItem.setText(COL_COMMENT,  testObj.getComment() or '')

            for col in range(tree.columnCount()):
                testItem.setFont(col, boldFont)
                testItem.setBackground(col, testBg)

            # Store the test object for Save
            testItem.setData(COL_SOURCE, Qt.ItemDataRole.UserRole, testObj)

            # A test the testbed marked invalid (e.g. a lemma or tag no longer in the source project) is shown in the log viewer's invalid color, with the reason drawn in red across the lexical unit columns by
            # LexicalUnitColumnDelegate. The reason is also the tooltip, in case it's too long to show in full.
            if not testObj.isValid():

                invalidReason = testObj.getInvalidReason()

                for col in range(tree.columnCount()):

                    testItem.setForeground(col, QBrush(INVALID_TEXT_COLOR))

                testItem.setData(COL_GRAMCAT, INVALID_REASON_ROLE, invalidReason)

                for col in REASON_SPAN_COLUMNS:

                    testItem.setToolTip(col, invalidReason)

            # LU (child) rows — headword, gramm cat, features, affixes editable
            for lu in testObj.getLexicalUnitList():

                myAffixes = myFeatures = ''

                luItem = QTreeWidgetItem(testItem)
                luItem.setFlags(EDITABLE)

                if lu.getGramCat() == SENT:

                    luItem.setText(COL_SOURCE, lu.getHeadWord())
                else:
                    luItem.setText(COL_SOURCE,
                                   lu.getHeadWord() + '.' + (lu.getSenseNum() or ''))

                luItem.setText(COL_GRAMCAT, lu.getGramCat() or '')

                # All other tags go into either Features/Classes or affixes
                otherTags = lu.getOtherTags()

                # Attempt to distinguish inflectional features from affixes

                # if everything is a subset of the affix list, then everything is an affix
                if set(otherTags) <= self.sourceAffixes:

                    myAffixes = '.'.join(otherTags)

                else:
                    # default to making everything a feature
                    split = len(otherTags)

                    # iterate backwards
                    for i in range(len(otherTags)-1, -1, -1):

                        # find the rightmost tag that can't be an affix
                        if otherTags[i] in self.sourceTags and otherTags[i] not in self.sourceAffixes:

                            split = i + 1
                            break

                    myFeatures = '.'.join(otherTags[:split])
                    myAffixes = '.'.join(otherTags[split:])

                luItem.setText(COL_FEATURES, myFeatures)
                luItem.setText(COL_AFFIXES,  myAffixes)
                self._colorLexicalUnitItem(luItem)

                # The lexical units of an invalid test get the invalid color too, overriding the usual lemma, category and affix colors.
                if not testObj.isValid():

                    for col in range(tree.columnCount()):

                        luItem.setForeground(col, QBrush(INVALID_TEXT_COLOR))

            testItem.setExpanded(True)

        # Fit each column to its contents. The Expected Result column is then trimmed by _fitExpectedColumn (called from _fitHeaderText) so it doesn't push the Comment column off the edge.
        self.autoSizingColumns = True

        for col in range(tree.columnCount()):

            tree.resizeColumnToContents(col)

        self.autoSizingColumns = False
        self.expectedContentWidth = None
        self._fitHeaderText()
        tree.blockSignals(False)

    def _fitExpectedColumn(self):

        # A testbed with sentence-length tests would make the Expected Result column as wide as its longest sentence, even one far down the list, and squeeze the Comment column off the edge.
        # So give it the width its contents need, but no more than leaves the Comment column the width of its header text. Cut-off text shows in a tooltip (see showToolTipIfCutOff).
        # Once the user has dragged the column to a width of their own, leave it alone.
        if self.userSizedExpected or not self.headerWidths:

            return

        tree = self.ui.treeWidget
        viewport = tree.viewport()

        # The stubs type viewport() as Optional, but a QTreeWidget always has a viewport.
        if viewport is None:

            return

        # Measuring every row is the slow part, so remember the result until the contents or font change.
        if self.expectedContentWidth is None:

            self.expectedContentWidth = tree.sizeHintForColumn(COL_EXPECTED)

        otherColumnsWidth = sum(tree.columnWidth(col) for col in range(tree.columnCount()) if col not in (COL_EXPECTED, COL_COMMENT))
        availableWidth = viewport.width() - otherColumnsWidth - self.headerWidths[COL_COMMENT]

        # Never go narrower than the column's own header text, even if that means the window needs a horizontal scroll.
        newWidth = max(self.headerWidths[COL_EXPECTED], min(self.expectedContentWidth, availableWidth))

        self.autoSizingColumns = True
        tree.setColumnWidth(COL_EXPECTED, newWidth)
        self.autoSizingColumns = False

    def _onSectionResized(self, logicalIndex, oldSize, newSize):

        # A resize we didn't make ourselves is the user dragging the column border, so stop fitting the Expected Result column automatically.
        if logicalIndex == COL_EXPECTED and not self.autoSizingColumns:

            self.userSizedExpected = True

    def eventFilter(self, a0, a1):

        # Re-fit the Expected Result column whenever the visible part of the tree changes width: when the window is first shown, resized or maximized, or a scroll bar comes or goes. This watches
        # the viewport rather than the tree itself because the viewport is resized after the tree's own resize event, so only then is its new width known.
        if a0 is self.ui.treeWidget.viewport() and a1 is not None and a1.type() == QEvent.Type.Resize:

            self._fitExpectedColumn()

        return super().eventFilter(a0, a1)

    def _fitHeaderText(self):

        tree = self.ui.treeWidget
        header = tree.header()
        headerItem = tree.headerItem()

        # The stubs type these as Optional, but a QTreeWidget always has a header view and a header item.
        assert header is not None and headerItem is not None
        style = header.style()

        # Allow for the header's left and right margins around the text, plus a little slack so the bold text never gets elided.
        margin = style.pixelMetric(QStyle.PixelMetric.PM_HeaderMargin, None, header) if style is not None else 4
        padding = 4 * margin
        headerHeight = 0
        self.autoSizingColumns = True

        for col in range(tree.columnCount()):

            # Measure the header text in its bold form. The .ui font only sets bold, so the size comes from the header view, which inherits the tree's font size.
            # Resolve against the header's font to get the size actually drawn; the .ui makes the headers bold, but force it here in case that changes.
            boldFont = headerItem.font(col).resolve(header.font())
            boldFont.setBold(True)
            boldMetrics = QFontMetrics(boldFont)
            headerWidth = boldMetrics.horizontalAdvance(headerItem.text(col)) + padding
            headerHeight = max(headerHeight, boldMetrics.height() + padding)

            # Remember it for _fitExpectedColumn, which keeps the Comment column at least this wide.
            self.headerWidths[col] = headerWidth

            # The comment column is last, so the header stretches it into whatever room the other columns leave. Setting it to just its header width
            # lets it give up space to the other columns rather than pushing the table into a horizontal scroll.
            if col == COL_COMMENT:

                tree.setColumnWidth(col, headerWidth)

            elif tree.columnWidth(col) < headerWidth:

                tree.setColumnWidth(col, headerWidth)

        self.autoSizingColumns = False

        # Qt sizes the header's height from the smaller unresolved font too, so make it at least tall enough for the tallest bold header text.
        header.setMinimumHeight(headerHeight)

        # Setting the Comment column to its header width above may have left room for the Expected Result column, or the header widths may have changed with the font size.
        self._fitExpectedColumn()

    def _addTest(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(_translate("TestBedEditor", 'Add Test'))
        layout = QFormLayout(dialog)

        sourceEdit = QLineEdit(dialog)
        expectedEdit = QLineEdit(dialog)
        commentEdit = QLineEdit(dialog)
        layout.addRow(_translate("TestBedEditor", 'Source Text:'), sourceEdit)
        layout.addRow(_translate("TestBedEditor", 'Expected Result:'), expectedEdit)
        layout.addRow(_translate("TestBedEditor", 'Comment:'), commentEdit)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        layout.addRow(buttonBox)

        # Start the dialog at twice its natural width so longer source text and expected results fit without scrolling in the line edits.
        startSize = dialog.sizeHint()
        dialog.resize(startSize.width() * 2, startSize.height())

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        sourceText = sourceEdit.text()
        expectedResult = expectedEdit.text()
        comment = commentEdit.text()
        newTestObj = TestbedTestXMLObject([LexicalUnit('word1.1 n')], sourceText, expectedResult, comment=comment)
        self.testObjList.append(newTestObj)
        self.testbedFileObj.getFLExTransTestbedXMLObject().addToTestbed(newTestObj)

        tree = self.ui.treeWidget
        testItem = QTreeWidgetItem(tree)
        testItem.setFlags(EDITABLE)
        testItem.setText(COL_SOURCE, sourceText)
        testItem.setText(COL_EXPECTED, expectedResult)
        testItem.setText(COL_COMMENT, comment)
        testItem.setData(COL_SOURCE, Qt.ItemDataRole.UserRole, newTestObj)

        boldFont = QFont()
        boldFont.setBold(False)
        testBg = QBrush(TEST_BG_COLOR)

        for col in range(tree.columnCount()):
            testItem.setFont(col, boldFont)
            testItem.setBackground(col, testBg)

        luItem = self._createDefaultLexicalUnitItem(testItem)
        testItem.setExpanded(True)
        tree.resizeColumnToContents(COL_SOURCE)
        tree.resizeColumnToContents(COL_GRAMCAT)

        # The new test's expected result may be the longest yet, so have _fitHeaderText's re-fit measure the Expected Result column again.
        self.expectedContentWidth = None
        self._fitHeaderText()

        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'There are unsaved changes.'))

    def _colorLexicalUnitItem(self, luItem):
        luItem.setForeground(COL_SOURCE, QBrush(QColor('#' + LEMMA_COLOR)))
        luItem.setForeground(COL_GRAMCAT, QBrush(QColor('#' + GRAM_CAT_COLOR)))
        luItem.setForeground(COL_FEATURES, QBrush(QColor('#' + AFFIX_COLOR)))
        luItem.setForeground(COL_AFFIXES, QBrush(QColor('#' + AFFIX_COLOR)))

    def _onCurrentItemChanged(self, currentItem, previousItem):
        self.ui.deleteButton.setEnabled(currentItem is not None)

    def _getSelectedTestItem(self):
        testItem = self.ui.treeWidget.currentItem()

        if testItem is None:
            return None

        parentItem = testItem.parent()

        while parentItem is not None:
            testItem = parentItem
            parentItem = testItem.parent()

        return testItem

    def _deleteTest(self):
        testItem = self._getSelectedTestItem()

        if testItem is None:
            return

        testObj = testItem.data(COL_SOURCE, Qt.ItemDataRole.UserRole)
        sourceText = html.escape(testItem.text(COL_SOURCE))
        lexicalUnits = testObj.getFormattedLUString()
        expectedResult = html.escape(testItem.text(COL_EXPECTED))
        comment = html.escape(testItem.text(COL_COMMENT))

        # Show everything that identifies the test (source text, lexical units, expected result and comment), since two tests can share the same lexical units or expected result.
        # The message is rich text; the lexical units string is already HTML (colored spans) and the other values were escaped above.
        message = _translate("TestBedEditor", 
         'Are you sure you want to delete this test?<br><br><b>Source Text:</b> {sourceText}<br><b>Lexical Units:</b> {lexicalUnits}<br><b>Expected Result:</b> {expectedResult}<br><b>Comment:</b> {comment}').format(
             sourceText=sourceText, lexicalUnits=lexicalUnits, expectedResult=expectedResult, comment=comment)

        confirm = QMessageBox(self)
        confirm.setWindowTitle(_translate("TestBedEditor", 'Delete Test'))
        confirm.setIcon(QMessageBox.Icon.Question)
        confirm.setTextFormat(Qt.TextFormat.RichText)
        confirm.setText(message)
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm.setDefaultButton(QMessageBox.StandardButton.No)

        if confirm.exec() != QMessageBox.StandardButton.Yes:
            return

        self.testbedFileObj.getFLExTransTestbedXMLObject().removeFromTestbed(testObj)
        self.ui.treeWidget.takeTopLevelItem(self.ui.treeWidget.indexOfTopLevelItem(testItem))
        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'Test deleted. There are unsaved changes.'))

    def _editTransferRules(self):

        # Warn and bail if the transfer rules file isn't there.
        if not self.transferRulesFile or not os.path.exists(self.transferRulesFile):

            QMessageBox.warning(self, _translate("TestBedEditor", 'Not Found Error'), _translate("TestBedEditor", 'Transfer rule file: {transferRulesFile} does not exist.').format(transferRulesFile=Utils.shortenPathForDisplay(self.transferRulesFile or '')))
            return

        # Launch the XMLmind XML Editor (xxe) on the file, the same way the Live Rule Tester's Edit Transfer Rules button does.
        xxe = os.path.join(os.environ['ProgramFiles(x86)'], 'XMLmind_XML_Editor', 'bin', 'xxe.exe')
        call([xxe, self.transferRulesFile])

    # ------------------------------------------------------------------
    # Change tracking
    # ------------------------------------------------------------------

    def _onItemChanged(self, item, column):
        if column == COL_SOURCE and item.parent() is not None:
            gramCat, features = self.sourceLemmas.get(item.text(COL_SOURCE), (None, None))

            if gramCat is not None:
                item.setText(COL_GRAMCAT, gramCat)

            if features is not None:
                item.setText(COL_FEATURES, features)

        # An edited expected result may be longer or shorter than before, so measure the column's contents again and re-fit it.
        if column == COL_EXPECTED:

            self.expectedContentWidth = None
            self._fitExpectedColumn()

        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'There are unsaved changes.'))

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _findBlankLexicalUnit(self):

        tree = self.ui.treeWidget

        # Return the first lexical unit row whose headword or grammatical category is blank, or None if all are filled in.
        for i in range(tree.topLevelItemCount()):

            testItem = tree.topLevelItem(i)

            # The stubs type topLevelItem() as Optional; it can't be None for an index within topLevelItemCount(), but skip it if it ever is.
            if testItem is None:

                continue

            for j in range(testItem.childCount()):

                luItem = testItem.child(j)

                # The stubs type child() as Optional; it can't be None for an index within childCount(), but skip it if it ever is.
                if luItem is None:

                    continue

                if not luItem.text(COL_SOURCE).strip() or not luItem.text(COL_GRAMCAT).strip():

                    return luItem

        return None

    def save(self):

        tree = self.ui.treeWidget

        # A lexical unit with no headword or no grammatical category would be written as an invalid testbed entry, so refuse to save and take the user to the row to fix it.
        blankLuItem = self._findBlankLexicalUnit()

        if blankLuItem is not None:

            tree.setCurrentItem(blankLuItem)
            tree.scrollToItem(blankLuItem)
            # A test's source text isn't unique (it's often just where the test came from), so identify the test by its source text, expected result and comment together, as the
            # delete confirmation does. The message is rich text, so escape the values.
            parentItem = blankLuItem.parent()
            sourceText = expectedResult = comment = ''

            if parentItem is not None:

                sourceText = html.escape(parentItem.text(COL_SOURCE))
                expectedResult = html.escape(parentItem.text(COL_EXPECTED))
                comment = html.escape(parentItem.text(COL_COMMENT))

            message = _translate("TestBedEditor",
             'A lemma or its grammatical category is blank in this test. Fill it in before saving.<br><br><b>Source Text:</b> {sourceText}<br><b>Expected Result:</b> {expectedResult}<br><b>Comment:</b> {comment}').format(
                 sourceText=sourceText, expectedResult=expectedResult, comment=comment)

            errorBox = QMessageBox(self)
            errorBox.setWindowTitle(_translate("TestBedEditor", 'Save Error'))
            errorBox.setIcon(QMessageBox.Icon.Critical)
            errorBox.setTextFormat(Qt.TextFormat.RichText)
            errorBox.setText(message)
            errorBox.exec()
            return False

        for i in range(tree.topLevelItemCount()):
            testItem = tree.topLevelItem(i)

            # The stubs type topLevelItem() as Optional; it can't be None for an index within topLevelItemCount(), but skip it if it ever is.
            if testItem is None:

                continue

            testObj  = testItem.data(COL_SOURCE, Qt.ItemDataRole.UserRole)
            testNode = testObj.getTestNode()

            # Update expected result
            expNode = testNode.find(TARGET_OUTPUT + '/' + EXPECTED_RESULT)
            if expNode is not None:
                expNode.text = testItem.text(COL_EXPECTED)

            # Update comment
            testObj.setComment(testItem.text(COL_COMMENT))

            # Rebuild lexical units from child rows
            sourceInputNode = testNode.find(SOURCE_INPUT)

            # A well-formed test always has these nodes (the tree was loaded from them). If one is missing, leave that test's lexical units untouched rather than crash.
            if sourceInputNode is None:

                continue

            lexUnitsNode = sourceInputNode.find(LEXICAL_UNITS)

            if lexUnitsNode is None:

                continue


            for child in list(lexUnitsNode):
                lexUnitsNode.remove(child)

            for j in range(testItem.childCount()):
                luItem  = testItem.child(j)

                # The stubs type child() as Optional; it can't be None for an index within childCount(), but skip it if it ever is.
                if luItem is None:

                    continue

                hwSense = luItem.text(COL_SOURCE).strip()
                gramCat = luItem.text(COL_GRAMCAT).strip()
                features = luItem.text(COL_FEATURES).strip()
                affixes  = luItem.text(COL_AFFIXES).strip()

                luElem = ET.SubElement(lexUnitsNode, LEXICAL_UNIT)

                if gramCat == SENT:
                    ET.SubElement(luElem, HEAD_WORD).text = hwSense
                    ET.SubElement(luElem, SENSE_NUM).text = 'n/a'
                else:
                    # Split on last dot to separate headword from sense number
                    if '.' in hwSense:
                        hw, sn = hwSense.rsplit('.', 1)
                    else:
                        hw, sn = hwSense, '1'
                    ET.SubElement(luElem, HEAD_WORD).text = hw
                    ET.SubElement(luElem, SENSE_NUM).text = sn

                ET.SubElement(luElem, GRAM_CAT).text = gramCat

                otherTagsElem = ET.SubElement(luElem, OTHER_TAGS)
                allTags = []
                if features:
                    allTags.extend(t.strip() for t in features.split('.'))
                if affixes:
                    allTags.extend(t.strip() for t in affixes.split('.'))
                for tag in allTags:
                    if tag:
                        ET.SubElement(otherTagsElem, TAG).text = tag

        # The first save of the session saves a copy of the file as it was to Output\testbed-file-history before overwriting it
        self.testbedFileObj.write(TAG_BEFORE_EDITOR_SAVE)
        self.unsaved = False
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'Testbed file saved.'))
        return True

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        """Handle window close event. The parameter name/type match QWidget.closeEvent."""

        # Qt always passes an event here; the stubs just type it as Optional.
        if a0 is None:

            return

        event = a0

        if self.unsaved:
            confirm = QMessageBox.question(
                self, _translate("TestBedEditor", 'Unsaved Changes'), _translate("TestBedEditor", 'Save changes before exiting?'),
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if confirm == QMessageBox.StandardButton.Save:

                # Keep the window open if the save was refused (e.g. a blank lexical unit) so the user can fix it rather than lose their changes.
                if not self.save():

                    event.ignore()
                    return

            elif confirm == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        event.accept()

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    try:
        testbedFileObj = FlexTransTestbedFile(None, report)
    except ValueError:
        return

    if not testbedFileObj.exists():
        Utils.reportTestbedFileMissing(report)
        return

    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
    testObjList   = testbedXMLObj.getTestXMLObjectList()

    # Get the path to the transfer rules file for the Edit Transfer Rules button. Don't give an error here; the button reports a missing file when it's clicked.
    transferRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)

    window = Main(testObjList, testbedFileObj, report, DB, transferRulesFile)
    window.show()
    app.exec()


FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
