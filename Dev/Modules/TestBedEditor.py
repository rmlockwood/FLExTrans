#
#   TestBedEditor
#
#   Lærke Roager Jespersen
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
# CODE STRUCTURE
#
# Main.__init__ loads the tree and connects controls. _loadTree creates rows from the model. _fitHeaderText makes the header tall enough, and each column wide enough, for its bold header text.
# _addTest creates and appends a new test. _deleteTest removes the selected test after confirmation. _onItemChanged tracks edits, save writes all rows, and closeEvent handles unsaved changes.
#
# TRANSLATION
#
# The docs dictionary is translated at import time, so the module-level code loads just this module's .qm before docs is built. MainFunction then loads the .qm files for the libraries and the window
# (librariesToTranslate) plus Qt's base translations for the standard buttons in the message boxes. Strings in the window itself come from TestBedEditorWindow.ui and live in TestBedEditorWindow_xx.ts.
#

import html
import os
from typing import Optional
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                             QFormLayout, QLineEdit, QMainWindow, QMenu,
                             QStyle, QStyledItemDelegate, QTreeWidgetItem,
                             QMessageBox)
from PyQt6.QtCore import QCoreApplication, Qt
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
                     AFFIX_COLOR)

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
    FTM_Version:     "3.17.19",
    FTM_ModifiesDB:  False,
    FTM_Synopsis:    _translate("TestBedEditor", "View and edit tests in the testbed."),
    FTM_Help:        "",
    FTM_Description: _translate("TestBedEditor",
"""View and edit the tests in the testbed. Each test is a row showing its source text, expected result and comment, with a row under it for each lexical unit in the test's source input. Double-click a cell to edit it. For a lexical unit, enter the headword with its homograph and sense numbers (e.g. house1.1), the grammatical category, any features or classes, and any affixes. As you type, suggestions from the source FLEx project are offered, and choosing a headword fills in its category and features. Separate multiple features, classes or affixes with a period, e.g. sg.pst. Right-click a row to add or delete a lexical unit. Use Add Test and Delete Test to add or remove whole tests, and click Save to write your changes to the testbed file."""),
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

EDITABLE   = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |
              Qt.ItemFlag.ItemIsEditable)
READ_ONLY  = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)


class ChildRowReadOnlyDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        if index.parent().isValid():
            return None

        return super().createEditor(parent, option, index)


class Main(QMainWindow):

    def __init__(self, testObjList, testbedFileObj, report, DB):
        super().__init__()
        self.testObjList    = testObjList
        self.testbedFileObj = testbedFileObj
        self.report         = report
        self.unsaved        = False
        self.sourceLemmas, self.sourceAffixes = gatherCompletionData(DB, report, testbedFileObj.composed)
        self.sourcePOS = gatherPOSTags(DB, report, [SENT])
        self.sourceTags = gatherTags(DB, report, self.sourcePOS)

        self.ui = Ui_TestBedEditorWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        treePalette = self.ui.treeWidget.palette()
        treePalette.setColor(QPalette.ColorRole.Highlight, TEST_HIGHLIGHT_COLOR)
        treePalette.setColor(QPalette.ColorRole.HighlightedText, treePalette.color(QPalette.ColorRole.Text))
        self.ui.treeWidget.setPalette(treePalette)
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
        self.ui.deleteButton.setEnabled(False)

        delegateData = [
            (sorted(self.sourceLemmas.keys()), False, True, False),
            (self.sourcePOS, False, True, True),
            (sorted(self.sourceTags), True, True, True),
            (sorted(self.sourceAffixes), True, True, True),
        ]
        self.delegates = [CompleterDelegate(*args) for args in delegateData]
        for index, delegate in enumerate(self.delegates):
            self.ui.treeWidget.setItemDelegateForColumn(index, delegate)

        childRowReadOnlyDelegate = ChildRowReadOnlyDelegate(self.ui.treeWidget)
        self.ui.treeWidget.setItemDelegateForColumn(COL_EXPECTED, childRowReadOnlyDelegate)
        self.ui.treeWidget.setItemDelegateForColumn(COL_COMMENT, childRowReadOnlyDelegate)

    def _fontSizeChanged(self):
        treeFont = self.ui.treeWidget.font()
        treeFont.setPointSize(self.ui.fontSizeSpinBox.value())
        self.ui.treeWidget.setFont(treeFont)

        # The header text grows with the font size, so resize the header and columns again to keep it from being clipped.
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

            testItem.setExpanded(True)

        for col in range(tree.columnCount()):
            tree.resizeColumnToContents(col)

        self._fitHeaderText()
        tree.blockSignals(False)

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

        for col in range(tree.columnCount()):

            # Measure the header text in its bold form. The .ui font only sets bold, so the size comes from the header view, which inherits the tree's font size.
            # Resolve against the header's font to get the size actually drawn; the .ui makes the headers bold, but force it here in case that changes.
            boldFont = headerItem.font(col).resolve(header.font())
            boldFont.setBold(True)
            boldMetrics = QFontMetrics(boldFont)
            headerWidth = boldMetrics.horizontalAdvance(headerItem.text(col)) + padding
            headerHeight = max(headerHeight, boldMetrics.height() + padding)

            # The comment column is last, so the header stretches it into whatever room the other columns leave. Setting it to just its header width
            # lets it give up space to the other columns rather than pushing the table into a horizontal scroll.
            if col == COL_COMMENT:

                tree.setColumnWidth(col, headerWidth)

            elif tree.columnWidth(col) < headerWidth:

                tree.setColumnWidth(col, headerWidth)

        # Qt sizes the header's height from the smaller unresolved font too, so make it at least tall enough for the tallest bold header text.
        header.setMinimumHeight(headerHeight)

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

        self.unsaved = True
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'There are unsaved changes.'))

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self):
        tree = self.ui.treeWidget

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

        self.testbedFileObj.write()
        self.unsaved = False
        self.ui.saveLabel.setText(_translate("TestBedEditor", 'Testbed file saved.'))

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
                self.save()
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
        report.Error(_translate("TestBedEditor", 'Testbed file does not exist. Please add tests to the testbed first.'))
        return

    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
    testObjList   = testbedXMLObj.getTestXMLObjectList()

    window = Main(testObjList, testbedFileObj, report, DB)
    window.show()
    app.exec()


FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
