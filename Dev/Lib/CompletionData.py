#
#   CompletionData
#
#   Shared completion delegates and FLEx project completion-data gathering for
#   editors that offer lexical, category, feature, and affix suggestions.
#
#   Version 3.17.1 - 9/23/26 - Ron Lockwood
#    Added child-row filtering and styled item painting to completion delegates.
#
#   Version 3.17 - 9/23/26 - Ron Lockwood
#    First version.
#
#   OVERVIEW (AI generated, then edited)
#
#   This module contains the completion behavior shared by editors that offer FLEx lexical, category, feature, and affix data. It keeps the segmented period-list behavior and database traversal in one place so the editors cannot drift apart.
#
#   CODE STRUCTURE
#
#   SegmentedCompleter completes one period-separated tag at a time. CompleterDelegate attaches either it or a normal QCompleter to an editor. The gather functions build lemma, category, feature, and affix suggestion data from a FLEx database.
#

from unicodedata import normalize

from PyQt6.QtWidgets import QCompleter, QLineEdit, QStyledItemDelegate
from PyQt6.QtCore import Qt

from SIL.LCModel import IMoStemMsa                      # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore
from SIL.LCModel import IFsClosedFeatureRepository     # type: ignore

import Utils


class SegmentedCompleter(QCompleter):
    def _editor(self):
        editor = self.parent()
        assert isinstance(editor, QLineEdit)
        return editor

    def splitPath(self, path: str) -> list[str]:
        pos = self._editor().cursorPosition()
        left = path[:pos].split('.')[-1]
        right = path[pos:].split('.')[0]
        return [left + right]

    def pathFromIndex(self, index) -> str:
        editor = self._editor()
        pos = editor.cursorPosition()
        text = editor.text()
        left = text[:pos]
        right = text[pos:]
        oldMiddle = ''

        if '.' in left:
            splitPos = left.rfind('.') + 1
            oldMiddle = left[splitPos:]
            left = left[:splitPos]
        else:
            oldMiddle = left
            left = ''

        if '.' in right:
            splitPos = right.find('.')
            oldMiddle += right[:splitPos]
            right = right[splitPos:]
        else:
            oldMiddle += right
            right = ''

        middle = super().pathFromIndex(index)

        if not middle.lower().startswith(oldMiddle.lower()):
            return text

        self.posShouldBe = len(left + middle)
        return left + middle + right


class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, values, useSegmented, onlyChildren=False):
        super().__init__()
        self.values = values
        self.useSegmented = useSegmented
        self.onlyChildren = onlyChildren

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        assert isinstance(editor, QLineEdit)

        if self.onlyChildren and not index.parent().isValid():
            return editor

        if self.useSegmented:
            completer = SegmentedCompleter(self.values, editor)
        else:
            completer = QCompleter(self.values, editor)

        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        editor.setCompleter(completer)
        return editor


def gatherCompletionData(DB, report, composed, wsHandle=None):
    lemmas = {}
    affixes = set()
    affixClasses = ['MoInflAffMsa', 'MoDerivAffMsa', 'MoUnclassifiedAffixMsa']
    report.ProgressStart(DB.LexiconNumberOfEntries())

    for index, entry in enumerate(DB.LexiconAllEntries()):
        report.ProgressUpdate(index)

        if wsHandle is not None:
            headWord = Utils.getHeadwordStr(entry, wsHandle)
        else:
            headWord = ITsString(entry.HeadWord).Text

        headWord = Utils.add_one(headWord)
        if composed:
            headWord = normalize('NFC', headWord)
        clitic = Utils.isClitic(entry)

        for senseNumber, sense in enumerate(entry.SensesOS, 1):
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
                lemmas[f'{headWord}.{senseNumber}'] = (pos, '.'.join(tags))
            elif sense.MorphoSyntaxAnalysisRA.ClassName in affixClasses:
                affixes.add(Utils.underscores(Utils.as_string(sense.Gloss)))

    return lemmas, affixes


def gatherPOSTags(DB, report, additionalCategories=None):
    posMap = {}
    Utils.get_categories(DB, report, posMap, TargetDB=None,
                         numCatErrorsToShow=1, addInflectionClasses=False)
    posTags = set(posMap.keys())

    if additionalCategories:
        posTags.update(additionalCategories)

    return sorted(posTags)


def gatherTags(DB):
    tags = set()

    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):
        tags.update(Utils.as_tag(value) for value in feature.ValuesOC)

    return tags
