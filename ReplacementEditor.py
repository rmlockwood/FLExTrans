from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QItemDelegate, QCompleter

from ReplacementEditorWindow import Ui_MainWindow
from flextoolslib import (
    FlexToolsModuleClass,
    FTM_Name, FTM_Version, FTM_ModifiesDB,
    FTM_Synopsis, FTM_Help, FTM_Description,
)

import Utils

docs = {
    FTM_Name: "Edit Replacement Dictionary",
    FTM_Version: "3.12",
    FTM_ModifiesDB: False,
    FTM_Synopsis: "Builds an Apertium-style bilingual lexicon.",
    FTM_Help: "",
    FTM_Description:
"""
This module will build a bilingual
lexicon for two projects. The
database that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these link.

You can make custom changes to the bilingual lexicon by using a replacement file. See the help
document for more details.
"""
}


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

        self.table.setItem(self.rowNumber, 0, self.sourceLemma)
        self.table.setItem(self.rowNumber, 1, self.sourcePOS)
        self.table.setItem(self.rowNumber, 2, self.sourceInfl)
        self.table.setItem(self.rowNumber, 3, self.sourceAffixes)
        self.table.setItem(self.rowNumber, 4, self.arrow)
        self.table.setItem(self.rowNumber, 5, self.targetLemma)
        self.table.setItem(self.rowNumber, 6, self.targetPOS)
        self.table.setItem(self.rowNumber, 7, self.targetInfl)
        self.table.setItem(self.rowNumber, 8, self.targetAffixes)

        self.arrow.setText('⇒')

    def loadData(self, entry):
        llem = ''
        ltags = []
        rlem = ''
        rtags = []
        def read(node, side=None):
            nonlocal llem, ltags, rlem, rtags
            if node.tag == 'leftdata':
                llem += (node.text or '')
            elif node.tag == 'rightdata':
                rlem += (node.text or '')
            elif node.tag == 's':
                tag = node.attrib.get('n')
                if not tag:
                    return
                if side == 'left':
                    ltags.append(tag)
                elif side == 'right':
                    rtags.append(tag)
            elif node.tag == 'b':
                if side == 'left':
                    llem += ' '
                    if node.tail:
                        llem += node.tail
                elif side == 'right':
                    rlem += ' '
                    if node.tail:
                        rlem += node.tail
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
        read(entry)
        # get rid of excess whitespace
        llem = ' '.join(llem.strip().split())
        rlem = ' '.join(rlem.strip().split())
        self.sourceLemma.setText(llem)
        if len(ltags) > 0:
            self.sourcePOS.setText(ltags[0])
            infl, aff = self.splitTagList(ltags[1:], self.window.sourceTags)
            self.sourceInfl.setText(infl)
            self.sourceAffixes.setText(aff)
        self.targetLemma.setText(rlem)
        if len(rtags) > 0:
            self.targetPOS.setText(rtags[0])
            infl, aff = self.splitTagList(ltags[1:], self.window.targetTags)
            self.targetInfl.setText(infl)
            self.targetAffixes.setText(aff)

    def splitTagList(self, tags, features):
        infl, aff = [], []
        for tag in tags:
            if tag in features:
                infl.append(tag)
            else:
                aff.append(tag)
        return '.'.join(infl), '.'.join(aff)

    def getSource(self):
        return (self.sourceLemma.text(), self.sourcePOS.text(),
                self.sourceInfl.text(), self.sourceAffixes.text())

    def tagList(self, *widgets):
        ret = []
        for widget in widgets:
            if value := widget.text():
                for piece in value.split('.'):
                    if tag := piece.strip():
                        ret.append(tag)
        return ret

    def toXML(self):
        import xml.etree.ElementTree as ET
        llem = self.sourceLemma.text().split() or ['']
        ltags = self.tagList(self.sourcePOS, self.sourceInfl, self.sourceAffixes)
        rlem = self.targetLemma.text().split() or ['']
        rtags = self.tagList(self.targetPOS, self.targetInfl, self.targetAffixes)
        entry = ET.Element('e')
        p = ET.SubElement(entry, 'p')
        l = ET.SubElement(p, 'l')
        r = ET.SubElement(p, 'r')

        l.text = llem[0]
        for piece in llem[1:]:
            b = ET.SubElement(l, 'b')
            b.tail = piece
        for tag in ltags:
            ET.SubElement(l, 's', n=tag)

        r.text = rlem[0]
        for piece in rlem[1:]:
            b = ET.SubElement(r, 'b')
            b.tail = piece
        for tag in rtags:
            ET.SubElement(r, 's', n=tag)

        return entry

    def checkCellUpdate(self, column):
        if column == 0:
            lemma = self.sourceLemma.text()
            pos, infl = self.window.sourceLemmas.get(lemma, (None, None))
            if pos is not None:
                self.sourcePOS.setText(pos)
            if infl is not None:
                self.sourceInfl.setText(infl)
        elif column == 5:
            lemma = self.targetLemma.text()
            pos, infl = self.window.targetLemmas.get(lemma, (None, None))
            if pos is not None:
                self.targetPOS.setText(pos)
            if infl is not None:
                self.targetInfl.setText(infl)

class SegmentedCompleter(QCompleter):
    def splitPath(self, path):
        pos = self.parent().cursorPosition()
        left = path[:pos].split('.')[-1]
        right = path[pos:].split('.')[0]
        return [left+right]

    def pathFromIndex(self, index):
        pos = self.parent().cursorPosition()
        text = self.parent().text()
        oldMiddle = ''
        left = text[:pos]
        if '.' in left:
            splitPos = left.rfind('.') + 1
            oldMiddle += left[splitPos:]
            left = left[:splitPos]
        else:
            oldMiddle += left
            left = ''
        right = text[pos:]
        print(right)
        if '.' in right:
            splitPos = right.find('.')
            oldMiddle += right[:splitPos]
            right = right[splitPos:]
        else:
            oldMiddle += right
            right = ''
        middle = super().pathFromIndex(index)
        # If we we're completing a tag in the middle and we select an option,
        # then we sometimes apply the completion twice and also replace the
        # last tag in the input, hence this check.
        if not middle.startswith(oldMiddle):
            return text
        self.posShouldBe = len(left + middle)
        return left + middle + right

    def complete(self, *args, **kwargs):
        print('complete!')
        super().complete(*args, **kwargs)

class CompleterDelegate(QItemDelegate):
    def __init__(self, values, use_segmented):
        super().__init__()
        self.values = values
        self.use_segmented = use_segmented

    def createEditor(self, *args, **kwargs):
        ret = super().createEditor(*args, **kwargs)
        if self.use_segmented:
            comp = SegmentedCompleter(self.values, ret)
        else:
            comp = QCompleter(self.values)
        ret.setCompleter(comp)
        return ret

class Main(QMainWindow):
    def __init__(self, replaceFile, sourceDB, targetDB, report):
        super().__init__()
        self.replaceFile = replaceFile
        self.sourceDB = sourceDB
        self.targetDB = targetDB
        self.report = report

        self.unsaved = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon()
        self.rows = []

        self.sourceLemmas, self.sourceAffixes = self.gatherCompletionData(sourceDB)
        self.targetLemmas, self.targetAffixes = self.gatherCompletionData(targetDB)
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

    def setWindowIcon(self):
        import QtGui
        import os
        import FTPaths
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

    def loadEntries(self):
        from xml.etree import ElementTree as ET

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

    def gatherCompletionData(self, DB):
        from SIL.LCModel import IMoStemMsa, IMoInflAffMsa
        from SIL.LCModel.Core.KernelInterfaces import ITsString
        lemmas = {}
        affixes = set()
        for entry in DB.LexiconAllEntries():
            headWord = ITsString(entry.HeadWord).Text
            headWord = Utils.add_one(headWord)
            headWord = Utils.convertProblemChars(headWord, Utils.lemmaProbData)
            for i, sense in enumerate(entry.SensesOS, 1):
                if not sense.MorphoSyntaxAnalysisRA:
                    continue
                if sense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                    msa = IMoStemMsa(sense.MorphoSyntaxAnalysisRA)
                    if not msa.PartOfSpeechRA:
                        continue
                    pos = ITsString(msa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                    pos = Utils.convertProblemChars(pos, Utils.catProbData)
                    tags = Utils.getInflectionTags(msa)
                    lemmas[f'{headWord}.{i}'] = (pos, '.'.join(tags))
                elif sense.MorphoSyntaxAnalysisRA.ClassName == 'MoInflAffMsa':
                    affixes.add(Utils.underscores(Utils.as_string(sense.Gloss)))
        return lemmas, affixes

    def gatherPOSTags(self, DB):
        from Utils import get_categories
        posMap = {}
        get_categories(DB, self.report, posMap, TargetDB=None,
                       numCatErrorsToShow=1, addInflectionClasses=False)
        return sorted(posMap.keys())

    def gatherTags(self, DB):
        from SIL.LCModel import IFsClosedFeatureRepository
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
        self.saveLabel.text('There are unsaved changes')
        self.rows[row].checkCellUpdate(column)

    def checkTable(self):
        from collections import defaultdict
        duplicateSource = defaultdict(list)
        noAffixes = []
        for rowNumber, row in enumerate(self.rows, 1):
            src = row.getSource()
            duplicateSource[src] = rowNumber
            if not src[3]:
                noAffixes.append(rowNumber)

        dupPairs = [val for val in duplicateSource.values() if len(val) > 1]
        message = []
        if dupPairs:
            message.append(f'The following sets of rows are identical on the source side and only the first one will have any effect:\n' + '\n'.join(f'- ' + ', '.join(map(str(pair)) for pair in dupPairs)))
        if noAffixes:
            message.append(f'The following rows have no affixes and thus are redundant with the links created by Link Senses: ' + ', '.join(map(str(noAffixes))))

        if message:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Useless Lines', '\n\n'.join(message))

    def save(self):
        self.checkTable()
        from xml.etree import ElementTree as ET
        dix = ET.Element('repldictionary')
        section = ET.SubElement(dix, 'section', id='append', type='standard')
        for row in self.rows:
            section.append(row.toXML())
        ET.indent(dix)
        with open(self.replaceFile, 'wb') as fout:
            fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            fout.write(b'<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "repldix.dtd">\n')
            fout.write(ET.tostring(dix, encoding='utf-8'))
        self.ui.saveLabel.text('Replacement file saved')
        self.unsaved = False

    def closeEvent(self, event):
        from PyQt5.QtWidgets import QMessageBox

        if self.unsaved:
            confirm = QMessageBox.question(
                self, 'Unsaved Changes', 'Save changes before exiting?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if confirm == QMessageBox.Save:
                self.save()
            elif confirm == QMessageBox.Cancel:
                event.ignore()

def MainFunction(DB, report, modifyAllowed):
    import ReadConfig
    import sys
    from PyQt5.QtWidgets import QApplication

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    replaceFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
    if not replaceFile:
        report.Error(f'A value for {ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE} not found in the configuration file.')
        return

    targetDB = Utils.openTargetProject(configMap, report)

    app = QApplication(sys.argv)
    window = Main(replaceFile, DB, targetDB, report)
    window.show()
    app.exec_()

    targetDB.CloseProject()

FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction,
                                       docs = docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
