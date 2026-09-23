#
#   ReplacementEditor
#
#   Daniel Swanson
#   SIL International
#   8/7/24
#
#   Version 3.17.2 - 9/23/26 - Ron Lockwood
#    Use the shared styled completion delegate.
#
#   Version 3.17.1 - 9/23/26 - Ron Lockwood
#    Use shared completion delegates and data gathering.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.1 - 6/28/26 - Ron Lockwood
#    Handle one project (two writing systems) mode - target data is in the source project, read in the target WS.
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
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 11/21/24 - Ron Lockwood
#    We do need to convert problem characters for the POS. Partially undid the 3.11.2 change.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.3 - 10/30/24 - Ron Lockwood
#    Add Mixpanel logging.
#
#   Version 3.11.2 - 9/19/24 - Ron Lockwood
#    Don't need to convert problem characters on the headword anymore.
#
#   Version 3.11.1 - 8/17/24 - Ron Lockwood
#    UI improvements.
#
#   Version 3.11 - 8/7/24 - Daniel Swanson
#    First version

import xml.etree.ElementTree as ET
import os
from collections import defaultdict

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QApplication, QMessageBox
from PyQt6.QtGui import QFontMetrics, QIcon
from PyQt6.QtCore import QCoreApplication, Qt

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
from LinkSenseTool import docs as LinkSenseToolDocs

from ReplacementEditorWindow import Ui_ReplacementEditorWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'ReplacementEditor'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'ReplacementEditorWindow'] 

docs = {FTM_Name:        _translate("ReplacementEditor", "Replacement Dictionary Editor"),
        FTM_Version:     "3.17",
        FTM_ModifiesDB:  False,
        FTM_Synopsis:    _translate("ReplacementEditor", "Edit manual overrides for the bilingual dictionary."),
        FTM_Help:        "",
        FTM_Description: _translate("ReplacementEditor", 
"""This module provides an interface for editing the replacement dictionary
which allows you to override the links created by the {linkSenseToolModule}
in the presence of particular affixes. For example, if you have a noun that
is generally translated one way, but has a different translation in the
vocative singular, you can specify that here.""").format(linkSenseToolModule=LinkSenseToolDocs[FTM_Name])}

#app.quit()
#del app

class TableRow:
    def __init__(self, window, table):
        self.window = window
        self.table = table
        self.rowNumber = self.table.rowCount()
        self.table.insertRow(self.rowNumber)

        self.sourceLemma = QTableWidgetItem()
        self.sourcePOS = QTableWidgetItem()
        self.sourceInfl = QTableWidgetItem()
        self.sourceAffixes = QTableWidgetItem()
        self.arrow = QTableWidgetItem()
        self.targetLemma = QTableWidgetItem()
        self.targetPOS = QTableWidgetItem()
        self.targetInfl = QTableWidgetItem()
        self.targetAffixes = QTableWidgetItem()
        self.comment = QTableWidgetItem()

        self.table.setItem(self.rowNumber, 0, self.sourceLemma)
        self.table.setItem(self.rowNumber, 1, self.sourcePOS)
        self.table.setItem(self.rowNumber, 2, self.sourceInfl)
        self.table.setItem(self.rowNumber, 3, self.sourceAffixes)
        self.table.setItem(self.rowNumber, 4, self.arrow)
        self.table.setItem(self.rowNumber, 5, self.targetLemma)
        self.table.setItem(self.rowNumber, 6, self.targetPOS)
        self.table.setItem(self.rowNumber, 7, self.targetInfl)
        self.table.setItem(self.rowNumber, 8, self.targetAffixes)
        self.table.setItem(self.rowNumber, 9, self.comment)

        self.arrow.setText('⇒')

    def loadData(self, entry: ET.Element):
        '''Iterate through the descendants of `entry` and extract the values
        for this row of the table'''

        llem = ''
        ltags = []
        rlem = ''
        rtags = []
        def read(node, side=None):
            '''Recursively examine the children of `node`'''

            nonlocal llem, ltags, rlem, rtags

            # old style lemmas (which have literal spaces)
            if node.tag == 'leftdata':
                llem += (node.text or '')
            elif node.tag == 'rightdata':
                rlem += (node.text or '')

            # tags
            elif node.tag == 's':
                tag = node.attrib.get('n')
                if not tag:
                    return
                if side == 'left':
                    ltags.append(tag)
                elif side == 'right':
                    rtags.append(tag)

            # spaces
            elif node.tag == 'b':
                if side == 'left':
                    llem += ' '
                    if node.tail:
                        llem += node.tail
                elif side == 'right':
                    rlem += ' '
                    if node.tail:
                        rlem += node.tail

            # other containers
            else:
                nextSide = side
                if node.tag == 'l':
                    nextSide = 'left'
                    if node.text:
                        llem += node.text
                elif node.tag == 'r':
                    nextSide = 'right'
                    if node.text:
                        rlem += node.text
                for ch in node:
                    read(ch, nextSide)

        # recurse through the entry
        read(entry)

        # get rid of excess whitespace
        llem = ' '.join(llem.strip().split())
        rlem = ' '.join(rlem.strip().split())

        # put the lemmas and tags in the table cells
        self.sourceLemma.setText(llem)
        if len(ltags) > 0:
            self.sourcePOS.setText(ltags[0])
            infl, aff = self.splitTagList(ltags[1:], self.window.sourceTags,
                                          self.window.sourceAffixes)
            self.sourceInfl.setText(infl)
            self.sourceAffixes.setText(aff)
        self.targetLemma.setText(rlem)
        if len(rtags) > 0:
            self.targetPOS.setText(rtags[0])
            infl, aff = self.splitTagList(rtags[1:], self.window.targetTags,
                                          self.window.targetAffixes)
            self.targetInfl.setText(infl)
            self.targetAffixes.setText(aff)
        self.comment.setText(entry.attrib.get('c', ''))

    def splitTagList(self, tags: list[str], features, affixes) -> tuple[str, str]:
        '''Attempt to distinguish inflectional features from affixes'''

        # if everything can be an affix, then everything is an affix
        if set(tags) <= affixes:
            return '', '.'.join(tags)
        # default to making everything a feature
        split = len(tags)
        # iterate backwards
        for i in range(len(tags)-1, -1, -1):
            # find the rightmost tag that can't be an affix
            if tags[i] in features and tags[i] not in affixes:
                split = i + 1
                break
        return '.'.join(tags[:split]), '.'.join(tags[split:])

    def getSource(self) -> tuple[str, str, str, str]:
        '''Return the source fields as a tuple'''

        return (self.sourceLemma.text(), self.sourcePOS.text(),
                self.sourceInfl.text(), self.sourceAffixes.text())

    def getTarget(self) -> tuple[str, str, str, str]:
        '''Return the target fields as a tuple'''

        return (self.targetLemma.text(), self.targetPOS.text(),
                self.targetInfl.text(), self.targetAffixes.text())

    def tagList(self, *widgets) -> list[str]:
        '''Given a collection of widgets, extract their values and return
        the tags in them as a list'''

        ret = []
        for widget in widgets:
            if value := widget.text():
                for piece in value.split('.'):
                    if tag := piece.strip():
                        ret.append(tag)
        return ret

    def toXML(self) -> ET.Element:
        '''Generate an XML entry from the cell values'''

        # get the data
        llem = self.sourceLemma.text().split() or ['']
        ltags = self.tagList(self.sourcePOS, self.sourceInfl, self.sourceAffixes)
        rlem = self.targetLemma.text().split() or ['']
        rtags = self.tagList(self.targetPOS, self.targetInfl, self.targetAffixes)

        # build the structure
        entry = ET.Element('e')
        # we can't use indent() because that would end up
        # inserting spaces between tags
        entry.tail = '\n    '
        c = self.comment.text().strip()
        if c:
            entry.attrib['c'] = c
        p = ET.SubElement(entry, 'p')
        l = ET.SubElement(p, 'l')
        r = ET.SubElement(p, 'r')

        # insert the left
        l.text = llem[0]
        for piece in llem[1:]:
            b = ET.SubElement(l, 'b')
            b.tail = piece
        for tag in ltags:
            ET.SubElement(l, 's', n=tag)

        # insert the right
        r.text = rlem[0]
        for piece in rlem[1:]:
            b = ET.SubElement(r, 'b')
            b.tail = piece
        for tag in rtags:
            ET.SubElement(r, 's', n=tag)

        return entry

    def checkCellUpdate(self, column):
        '''Check if a lemma has changed, and autofill the other columns
        as needed'''

        if column == 0:
            # source lemma
            lemma = self.sourceLemma.text()
            pos, infl = self.window.sourceLemmas.get(lemma, (None, None))
            if pos is not None:
                self.sourcePOS.setText(pos)
            if infl is not None:
                self.sourceInfl.setText(infl)

        elif column == 5:
            # target lemma
            lemma = self.targetLemma.text()
            pos, infl = self.window.targetLemmas.get(lemma, (None, None))
            if pos is not None:
                self.targetPOS.setText(pos)
            if infl is not None:
                self.targetInfl.setText(infl)

class Main(QMainWindow):
    def __init__(self, replaceFile, sourceDB, targetDB, report, composed, targetWSHandle=None):
        super().__init__()
        self.replaceFile = replaceFile
        self.sourceDB = sourceDB
        self.targetDB = targetDB
        self.report = report

        # In one project mode the target lemmas come from the source project read in the target writing system; this handle selects it (None = default vernacular).
        self.targetWSHandle = targetWSHandle

        self.unsaved = False
        self.ui = Ui_ReplacementEditorWindow()
        self.ui.setupUi(self)
        self.setWindowIcon()
        self.rows = []

        self.sourceLemmas, self.sourceAffixes = gatherCompletionData(sourceDB, report, composed)
        self.targetLemmas, self.targetAffixes = gatherCompletionData(targetDB, report, composed, self.targetWSHandle)
        self.sourcePOS = gatherPOSTags(sourceDB, report)
        self.targetPOS = gatherPOSTags(targetDB, report)
        self.sourceTags = gatherTags(sourceDB)
        self.targetTags = gatherTags(targetDB)

        delegate_data = [
            (sorted(self.sourceLemmas.keys()), False),
            (self.sourcePOS, False),
            (sorted(self.sourceTags), True),
            (sorted(self.sourceAffixes), True),
            ([], False),
            (sorted(self.targetLemmas.keys()), False),
            (self.targetPOS, False),
            (sorted(self.targetTags), True),
            (sorted(self.targetAffixes), True),
            ([], False),
        ]
        self.delegates = [CompleterDelegate(*args) for args in delegate_data]
        for index, delegate in enumerate(self.delegates):
            self.ui.tableWidget.setItemDelegateForColumn(index, delegate)

        self.loadEntries()

        self.ui.tableWidget.cellChanged.connect(self.cellChanged)
        self.ui.addButton.clicked.connect(self.addRow)
        self.ui.deleteButton.clicked.connect(self.deleteSelectedRows)
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.closeButton.clicked.connect(self.close)

    def positionControl(self, myControl, x, y):

        myControl.setGeometry(x, y, myControl.width(), myControl.height())

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)

        # Stretch the table view to fit
        self.ui.tableWidget.setGeometry(10, 10, self.width() - 20, self.height() - self.ui.addButton.height() - 45)

        # Get the default font metrics
        font = self.ui.tableWidget.font()
        metrics = QFontMetrics(font)

        # Adjust column widths based on header text
        for col in range(self.ui.tableWidget.columnCount()):

            headerText = self.ui.tableWidget.horizontalHeaderItem(col).text()
            textWidth = metrics.horizontalAdvance(headerText) + 20  # Adding padding

            if col == 9:  # Comment column:

                textWidth = textWidth * 3  # Wider column for comments

            self.ui.tableWidget.setColumnWidth(col, textWidth)

    def setWindowIcon(self):
        super().setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

    def loadEntries(self):

        entries = []
        try:
            tree = ET.parse(self.replaceFile)
            entries = tree.getroot().findall('.//e')
        except:
            pass

        lastRow = -1
        for ent in entries:
            if lastRow == -1:
                lastRow = len(self.rows)
                self.addRow()
            try:
                self.rows[lastRow].loadData(ent)
                lastRow = -1
            except:
                pass
        if lastRow != -1:
            self.deleteRow(lastRow)

    def addRow(self):
        row = TableRow(self, self.ui.tableWidget)
        self.rows.append(row)

    def deleteSelectedRows(self):
        delRows = set(i.row() for i in self.ui.tableWidget.selectedIndexes())
        i = 0
        newRows = []
        for row in self.rows:
            if row.rowNumber in delRows:
                self.ui.tableWidget.removeRow(i)
                del row
            else:
                row.rowNumber = i
                i += 1
                newRows.append(row)
        self.rows = newRows

    def cellChanged(self, row, column):
        if row >= len(self.rows):
            return
        self.unsaved = True
        self.ui.saveLabel.setText(_translate("ReplacementEditor", 'There are unsaved changes.'))
        self.rows[row].checkCellUpdate(column)

    def checkTable(self):
        duplicateSource = defaultdict(list)
        noAffixes = []
        for rowNumber, row in enumerate(self.rows, 1):
            src = row.getSource()
            duplicateSource[src].append(rowNumber)
            if not src[3] and not row.getTarget()[3]:
                noAffixes.append(rowNumber)

        dupPairs = [val for val in duplicateSource.values() if len(val) > 1]
        message = []
        if dupPairs:
            message.append(_translate("ReplacementEditor", 'The following sets of rows are identical on the source side and only the first one will have any effect:\n') + '\n'.join(f'- ' + ', '.join(map(str, pair)) for pair in dupPairs))
        if noAffixes:
            message.append(_translate("ReplacementEditor", 'The following rows have no affixes and thus are redundant with the links created by Sense Linker Tool: ') + ', '.join(map(str, noAffixes)))

        if message:
            QMessageBox.warning(self, _translate("ReplacementEditor", 'Useless Lines:'), '\n\n'.join(message))

    def save(self):
        self.checkTable()
        dix = ET.Element('dictionary')
        section = ET.SubElement(dix, 'section', id='append', type='standard')
        for row in self.rows:
            section.append(row.toXML())
        with open(self.replaceFile, 'wb') as fout:
            fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            fout.write(b'<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
            fout.write(ET.tostring(dix, encoding='utf-8'))
        self.ui.saveLabel.setText(_translate("ReplacementEditor", 'Replacement dictionary file saved.'))
        self.unsaved = False

    def closeEvent(self, event):

        if self.unsaved:
            confirm = QMessageBox.question(
                self, _translate("ReplacementEditor", 'Unsaved Changes'), _translate("ReplacementEditor", 'Save changes before exiting?'),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            )
            if confirm == QMessageBox.StandardButton.Save:
                self.save()
            elif confirm == QMessageBox.StandardButton.Cancel:
                event.ignore()

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    replaceFile = ReadConfig.getConfigVal(
        configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
    if not replaceFile:
        report.Error(_translate("ReplacementEditor", 'A value for {configValue} not found in the configuration file.').format(configValue=ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE))
        return

    # In one project (two writing systems) mode there is no separate target project: the target data is in the source project,
    # read in the target writing system. So reuse the source DB and resolve the target WS handle for the completion lemmas.
    oneProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) == 'n'
    targetWSHandle = None

    if oneProjectMode:

        targetDB = DB
        targetWSTag = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_WRITING_SYSTEM, report, giveError=False)

        if targetWSTag:

            targetWSHandle = DB.WSHandle(targetWSTag)
    else:
        targetDB = Utils.openTargetProject(configMap, report)

    composed = ReadConfig.getConfigVal(configMap, ReadConfig.COMPOSED_CHARACTERS,
                                       report)
    composed = (composed == 'y')

    window = Main(replaceFile, DB, targetDB, report, composed, targetWSHandle)
    window.show()
    app.exec()

    # Only close the target project if it's a separate project (not in one project mode where target == source).
    if targetDB is not DB:

        targetDB.CloseProject()

FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs = docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
