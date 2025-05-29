#
#   ReplacementEditor
#
#   Daniel Swanson
#   SIL International
#   8/7/24
#
#   Version 3.13.2 - 5/21/25 - Ron Lockwood
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
from unicodedata import normalize
from collections import defaultdict

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QItemDelegate, QCompleter, QApplication, QMessageBox
from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtCore import QCoreApplication, Qt

from SIL.LCModel import IMoStemMsa                      # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore
from SIL.LCModel import IFsClosedFeatureRepository # type: ignore

from flextoolslib import (
    FlexToolsModuleClass,
    FTM_Name, FTM_Version, FTM_ModifiesDB,
    FTM_Synopsis, FTM_Help, FTM_Description,
)

import ReadConfig
import FTPaths
import Mixpanel
import Utils

from ReplacementEditorWindow import Ui_ReplacementEditorWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'ReplacementEditor'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'ReplacementEditorWindow'] 

docs = {
    FTM_Name:        "Replacement Dictionary Editor",
    FTM_Version:     "3.13.2",
    FTM_ModifiesDB:  False,
    FTM_Synopsis:    _translate("ReplacementEditor", "Edit manual overrides for the bilingual dictionary."),
    FTM_Help:        "",
    FTM_Description: _translate("ReplacementEditor", 
"""This module provides an interface for editing the replacement dictionary
which allows you to override the links created by the Sense Linker Tool
in the presence of particular affixes. For example, if you have a noun that
is generally translated one way, but has a different translation in the
vocative singular, you can specify that here.""")}

app.quit()
del app

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

class SegmentedCompleter(QCompleter):
    '''Override the Qt autocomplete class to each tag in a period-separated
    list rather than the field value as a whole'''

    def splitPath(self, path: str) -> list[str]:
        '''Pretend the field value is solely the tag which currently
        contains the cursor'''

        pos = self.parent().cursorPosition()
        left = path[:pos].split('.')[-1]
        right = path[pos:].split('.')[0]
        return [left+right]

    def pathFromIndex(self, index) -> str:
        '''A selection has been chosen, so generate the actual field value
        from it'''

        pos = self.parent().cursorPosition()
        text = self.parent().text()
        oldMiddle = ''

        # get the tags to the left of the cursor
        left = text[:pos]
        if '.' in left:
            splitPos = left.rfind('.') + 1
            oldMiddle += left[splitPos:]
            left = left[:splitPos]
        else:
            oldMiddle += left
            left = ''

        # get the tags to the right of the cursor
        right = text[pos:]
        if '.' in right:
            splitPos = right.find('.')
            oldMiddle += right[:splitPos]
            right = right[splitPos:]
        else:
            oldMiddle += right
            right = ''

        # get the autocompleted tag
        middle = super().pathFromIndex(index)

        # If we we're completing a tag in the middle and we select an option,
        # then we sometimes apply the completion twice and also replace the
        # last tag in the input, hence this check.
        if not middle.lower().startswith(oldMiddle.lower()):
            return text

        # I'm not quite sure where in the process to use this value,
        # but ideally after completing we'd be able to set the user's cursor
        # to be at the end of the tag they just completed.
        # Unfortunately, for now I think we're stuck with the cursor jumping
        # to the end of the input. -DGS 2024-08-09
        self.posShouldBe = len(left + middle)

        # return the final value
        return left + middle + right

class CompleterDelegate(QItemDelegate):
    '''Intermediary between the table and the fields to ensure that when the
    fields turn into input boxes they have autocompleters attached'''

    def __init__(self, values, use_segmented):
        super().__init__()
        self.values = values
        self.use_segmented = use_segmented

    def createEditor(self, *args, **kwargs):
        '''Turn a label into an input box and attach an autocompleter'''

        ret = super().createEditor(*args, **kwargs)
        if self.use_segmented:
            comp = SegmentedCompleter(self.values, ret)
        else:
            comp = QCompleter(self.values)
        comp.setCaseSensitivity(Qt.CaseInsensitive)
        ret.setCompleter(comp)
        return ret

class Main(QMainWindow):
    def __init__(self, replaceFile, sourceDB, targetDB, report, composed):
        super().__init__()
        self.replaceFile = replaceFile
        self.sourceDB = sourceDB
        self.targetDB = targetDB
        self.report = report

        self.unsaved = False
        self.ui = Ui_ReplacementEditorWindow()
        self.ui.setupUi(self)
        self.setWindowIcon()
        self.rows = []

        self.sourceLemmas, self.sourceAffixes = self.gatherCompletionData(sourceDB, composed)
        self.targetLemmas, self.targetAffixes = self.gatherCompletionData(targetDB, composed)
        self.sourcePOS = self.gatherPOSTags(sourceDB)
        self.targetPOS = self.gatherPOSTags(targetDB)
        self.sourceTags = self.gatherTags(sourceDB)
        self.targetTags = self.gatherTags(targetDB)

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
            textWidth = metrics.width(headerText) + 20  # Adding padding

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

    def gatherCompletionData(self, DB, composed):
        if composed:
            def norm(s): return normalize('NFC', s)
        else:
            def norm(s): return s
        lemmas = {}
        affixes = set()
        affixClasses = ['MoInflAffMsa', 'MoDerivAffMsa', 'MoUnclassifiedAffixMsa']
        self.report.ProgressStart(DB.LexiconNumberOfEntries())
        for index, entry in enumerate(DB.LexiconAllEntries()):
            self.report.ProgressUpdate(index)
            headWord = ITsString(entry.HeadWord).Text
            headWord = Utils.add_one(headWord)
            #headWord = Utils.convertProblemChars(headWord, Utils.lemmaProbData)
            headWord = norm(headWord)
            clitic = Utils.isClitic(entry)
            for i, sense in enumerate(entry.SensesOS, 1):
                if clitic:
                    affixes.add(Utils.underscores(Utils.as_string(sense.Gloss)))
                if not sense.MorphoSyntaxAnalysisRA:
                    continue
                if sense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                    msa = IMoStemMsa(sense.MorphoSyntaxAnalysisRA)
                    if not msa.PartOfSpeechRA:
                        continue
                    pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                    pos = Utils.convertProblemChars(pos, Utils.catProbData)
                    tags = Utils.getInflectionTags(msa)
                    lemmas[f'{headWord}.{i}'] = (pos, '.'.join(tags))
                elif sense.MorphoSyntaxAnalysisRA.ClassName in affixClasses:
                    affixes.add(Utils.underscores(Utils.as_string(sense.Gloss)))
        return lemmas, affixes

    def gatherPOSTags(self, DB):
        posMap = {}
        Utils.get_categories(DB, self.report, posMap, TargetDB=None,
                       numCatErrorsToShow=1, addInflectionClasses=False)
        return sorted(posMap.keys())

    def gatherTags(self, DB):
        tags = set()
        for feature in DB.ObjectsIn(IFsClosedFeatureRepository):
            tags.update(Utils.as_tag(val) for val in feature.ValuesOC)
        return tags

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
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if confirm == QMessageBox.Save:
                self.save()
            elif confirm == QMessageBox.Cancel:
                event.ignore()

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication([])
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

    targetDB = Utils.openTargetProject(configMap, report)

    composed = ReadConfig.getConfigVal(configMap, ReadConfig.COMPOSED_CHARACTERS,
                                       report)
    composed = (composed == 'y')

    window = Main(replaceFile, DB, targetDB, report, composed)
    window.show()
    app.exec_()

    targetDB.CloseProject()

FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs = docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
