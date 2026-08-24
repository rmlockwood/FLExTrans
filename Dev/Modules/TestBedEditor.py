#
#   TestBedEditor
#
#   Lærke Roager Jespersen
#
#   Version 1.0 - 6/27/26
#    First version. Loads testbed tests into an editable tree view.
#    Double-click any cell to edit. Save writes changes back to the XML file.
#

import os
import xml.etree.ElementTree as ET

from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QMessageBox
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QFont, QBrush, QColor, QIcon

from flextoolslib import (
    FlexToolsModuleClass,
    FTM_Name, FTM_Version, FTM_ModifiesDB,
    FTM_Synopsis, FTM_Help, FTM_Description,
)

import ReadConfig
import FTPaths
import Mixpanel
import Utils
from Testbed import (FlexTransTestbedFile, SENT,
                     HEAD_WORD, SENSE_NUM, GRAM_CAT, OTHER_TAGS, TAG,
                     SOURCE_INPUT, LEXICAL_UNITS, LEXICAL_UNIT,
                     TARGET_OUTPUT, EXPECTED_RESULT)

from TestBedEditorWindow import Ui_TestBedEditorWindow

_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TestBedEditor'

docs = {
    FTM_Name:        "Testbed Editor",
    FTM_Version:     "1.0",
    FTM_ModifiesDB:  False,
    FTM_Synopsis:    "View and edit tests in the testbed.",
    FTM_Help:        "",
    FTM_Description: "View and edit tests in the testbed.",
}

# Column indices
COL_SOURCE   = 0  # test: origin (read-only);  LU: headword.sense#
COL_GRAMCAT  = 1  # LU: grammatical category
COL_FEATURES = 2  # LU: features/classes
COL_AFFIXES  = 3  # LU: affixes
COL_EXPECTED = 4  # test: expected result
COL_COMMENT  = 5  # test: comment

TEST_BG_COLOR = QColor('#D6E4F0')

EDITABLE   = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |
              Qt.ItemFlag.ItemIsEditable)
READ_ONLY  = (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)


class Main(QMainWindow):

    def __init__(self, testObjList, testbedFileObj, report):
        super().__init__()
        self.testObjList    = testObjList
        self.testbedFileObj = testbedFileObj
        self.report         = report
        self.unsaved        = False

        self.ui = Ui_TestBedEditorWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR,
                                              'FLExTransWindowIcon.ico')))

        self._loadTree()

        self.ui.treeWidget.itemChanged.connect(self._onItemChanged)
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.closeButton.clicked.connect(self.close)

    # ------------------------------------------------------------------
    # Tree loading
    # ------------------------------------------------------------------

    def _loadTree(self):
        tree = self.ui.treeWidget
        tree.blockSignals(True)
        tree.clear()

        boldFont = QFont()
        boldFont.setBold(True)
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
                luItem = QTreeWidgetItem(testItem)
                luItem.setFlags(EDITABLE)

                if lu.getGramCat() == SENT:
                    luItem.setText(COL_SOURCE, lu.getHeadWord())
                else:
                    luItem.setText(COL_SOURCE,
                                   lu.getHeadWord() + '.' + (lu.getSenseNum() or ''))

                luItem.setText(COL_GRAMCAT, lu.getGramCat() or '')

                # All other tags go into Features/Classes for now;
                # Affixes split comes when autocomplete is added
                otherTags = lu.getOtherTags()
                luItem.setText(COL_FEATURES, '.'.join(otherTags) if otherTags else '')
                luItem.setText(COL_AFFIXES,  '')

            testItem.setExpanded(True)

        for col in range(tree.columnCount()):
            tree.resizeColumnToContents(col)

        tree.blockSignals(False)

    # ------------------------------------------------------------------
    # Change tracking
    # ------------------------------------------------------------------

    def _onItemChanged(self, item, column):
        self.unsaved = True
        self.ui.saveLabel.setText('There are unsaved changes.')

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self):
        tree = self.ui.treeWidget

        for i in range(tree.topLevelItemCount()):
            testItem = tree.topLevelItem(i)
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
            lexUnitsNode    = sourceInputNode.find(LEXICAL_UNITS)

            for child in list(lexUnitsNode):
                lexUnitsNode.remove(child)

            for j in range(testItem.childCount()):
                luItem  = testItem.child(j)
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
        self.ui.saveLabel.setText('Testbed file saved.')

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        if self.unsaved:
            confirm = QMessageBox.question(
                self, 'Unsaved Changes', 'Save changes before exiting?',
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

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    try:
        testbedFileObj = FlexTransTestbedFile(None, report)
    except ValueError:
        return

    if not testbedFileObj.exists():
        report.Error('Testbed file does not exist. Please add tests to the testbed first.')
        return

    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
    testObjList   = testbedXMLObj.getTestXMLObjectList()

    window = Main(testObjList, testbedFileObj, report)
    window.show()
    app.exec()


FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
