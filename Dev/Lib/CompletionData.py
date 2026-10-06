#
#   CompletionData
#
#   Shared completion delegates and FLEx project completion-data gathering for
#   editors that offer lexical, category, feature, and affix suggestions.
#
#   Version 3.17.5 - 10/5/26 - Ron Lockwood
#    Fixes #1603. Widen the completion popup to fit its longest suggestion instead of limiting it to the cell width.
#
#   Version 3.17.3 - 9/25/26 - Ron Lockwood
#    Convert dots to underscores in inflection classes when gathering tags.
#
#   Version 3.17.4 - 9/24/26 - Ron Lockwood
#    Match completion popup font size to the editing control.
#
#   Version 3.17.2 - 9/25/26 - Ron Lockwood
#    Add inflection classes to the completion data, not just features.
#
#   Version 3.17.3 - 9/23/26 - Ron Lockwood
#    Added child-row filtering and styled item painting to completion delegates.
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
#   SegmentedCompleter completes one period-separated tag at a time. PopupWidthFitter widens a completer's popup so long suggestions aren't cut off; Qt otherwise makes the popup exactly as
#   wide as the editor, which in a narrow table or tree cell hides most of a long lemma. CompleterDelegate attaches either kind of completer, plus a fitter, to an editor. The gather functions
#   build lemma, category, feature, and affix suggestion data from a FLEx database.
#

from unicodedata import normalize

from PyQt6.QtWidgets import QCompleter, QLineEdit, QStyledItemDelegate
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6 import sip

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

class PopupWidthFitter(QObject):
    '''Keep a completer's popup at least as wide as its longest current suggestion.'''

    # Extra room for the item margins so the last character isn't clipped.
    PADDING = 16

    def __init__(self, completer):

        super().__init__(completer)
        self.completer = completer
        popup = completer.popup()

        if popup is None:

            return

        # Qt sets the popup's geometry to the editor's width each time it shows or refilters it, but it honors the minimum width, so keep the minimum width in step with the suggestions.
        popup.installEventFilter(self)
        model = completer.completionModel()

        # The completion model is reset every time the typed prefix changes the filtered list.
        if model is not None:

            model.modelReset.connect(self.fitWidth)

    # The parameters keep PyQt's a0/a1 names so the override matches the stub's signature.
    def eventFilter(self, a0: QObject | None, a1: QEvent | None) -> bool:

        if a1 is not None and a1.type() == QEvent.Type.Show:

            self.fitWidth()

        return False

    def fitWidth(self):

        # When the cell editor closes, the completer is destroyed and its completion model is reset one last time on the way out. That reset still reaches us, so skip it.
        if sip.isdeleted(self.completer):

            return

        popup = self.completer.popup()
        model = self.completer.completionModel()

        if popup is None or model is None:

            return

        # Measure every suggestion, not just the visible ones, so scrolling doesn't reveal a clipped item.
        metrics = popup.fontMetrics()
        textWidth = 0

        for row in range(model.rowCount()):

            text = model.index(row, 0).data(Qt.ItemDataRole.DisplayRole)

            if text:

                textWidth = max(textWidth, metrics.horizontalAdvance(str(text)))

        scrollBar = popup.verticalScrollBar()
        scrollBarWidth = scrollBar.sizeHint().width() if scrollBar is not None else 0
        neededWidth = textWidth + scrollBarWidth + 2 * popup.frameWidth() + self.PADDING

        # Don't let a very long suggestion push the popup wider than the screen.
        screen = popup.screen()

        if screen is not None:

            neededWidth = min(neededWidth, screen.availableGeometry().width())

        popup.setMinimumWidth(neededWidth)

class CompleterDelegate(QStyledItemDelegate):
    def __init__(self, values, useSegmented, onlyChildren=False, editableOnlyChildren=False):
        super().__init__()
        self.values = values
        self.useSegmented = useSegmented
        self.onlyChildren = onlyChildren
        self.editableOnlyChildren = editableOnlyChildren

    def createEditor(self, parent, option, index):
        if self.editableOnlyChildren and not index.parent().isValid():
            return None

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
        popup = completer.popup()
        if popup is not None:
            popup.setFont(editor.font())

        # Let the popup grow past the cell width so long suggestions can be read in full. The completer owns the fitter, so it goes away with the editor.
        PopupWidthFitter(completer)
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
    Utils.get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)
    posTags = set(posMap.keys())

    if additionalCategories:

        posTags.update(additionalCategories)

    return sorted(posTags)


def gatherTags(DB, report, posTags):
    '''Gather inflection features and classes.'''

    posMap = {}
    tags = set()

    # First features
    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        tags.update(Utils.as_tag(value) for value in feature.ValuesOC)

    # Get classes which are a per POS thing. Get categories including inflection classes and the ones that are in this list but not the original POS list, are the classes.
    Utils.get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=True)
    classTags = set(posMap.keys()) - set(posTags)

    # Now add the classes to the tags set after converting dots to underscores.
    tags.update({Utils.underscores(tag) for tag in classTags})

    return tags
