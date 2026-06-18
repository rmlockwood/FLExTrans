#
#   RAutils.py
#
#   Matthew Lee, Ron Lockwood - original Java version by Andy Black
#   SIL International
#   September 2023
#
#   Version 3.16.9 - 6/17/26 - Ron Lockwood
#    Default new rules to no permutations and overwrite-rules to yes.
#
#   Version 3.16.8 - 6/17/26 - Ron Lockwood
#    Add preference storage for the horizontal rule-info/example-data splitter position.
#
#   Version 3.16.7 - 6/17/26 - Ron Lockwood
#    Add preference storage for the two main-window splitter positions.
#
#   Version 3.16.6 - 6/17/26 - Ron Lockwood
#    Store ApplicationPreferences in a TOML file (Config/RuleAssistantSettings.txt) instead of QSettings/registry.
#
#   Version 3.16.5 - 6/17/26 - Ron Lockwood
#    Hard code to 'number' for the co-feature and 'sg', 'pl' and 'many' for its values.
#
#   Version 3.16.4 - 6/17/26 - Ron Lockwood
#    Fix type-checker errors: broaden parent type, read head via getattr, narrow phrase with isinstance, Optional css-dir params.
#
#   Version 3.16.3 - 6/16/26 - Ron Lockwood
#    Apply coding conventions; camelCase naming.
#
#   Version 3.16.2 - 6/15/26 - Ron Lockwood
#    Refactored: widgets/layout now live in .ui files and logid separated to controler files.
#
#   Version 3.16.1 - 6/15/26 - Ron Lockwood
#    Fixes #1359. Get the target category for a word from its source if necessary.
#
#   Version 3.16 - 6/15/26 - Ron Lockwood
#    Fixed #1362. Start with correct word boxes for a new rule.
#
#  RuleAssistant utilities: combined model, flexmodel, and service classes.

# ---- External imports ----
import os
import xml.etree.ElementTree as ET
import io
import tomllib
import tomli_w
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PyQt6.QtCore import QObject, pyqtSlot, QCoreApplication

import FTPaths

_translate = QCoreApplication.translate

# ============================================================
# Constants
# ============================================================
VERSION_NUMBER = "1.6.0"
GREEK_VARIABLES = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "μ", "ν"]

# ============================================================
# Enums
# ============================================================
class AffixType(str, Enum):

    prefix = "prefix"
    suffix = "suffix"

class HeadValue(str, Enum):

    yes = "yes"
    no = "no"

class OverwriteRulesValue(str, Enum):

    yes = "yes"
    no = "no"

class PermutationsValue(str, Enum):

    no = "no"
    not_head = "not_head"
    with_head = "with_head"

class PhraseType(str, Enum):

    source = "source"
    target = "target"

class ValidFeatureType(str, Enum):

    prefix = "prefix"
    prefixstem = "prefixstem"
    prefixstemsuffix = "prefixstemsuffix"
    prefixsuffix = "prefixsuffix"
    stem = "stem"
    stemsuffix = "stemsuffix"
    suffix = "suffix"

# ============================================================
# FLEx metadata model
# ============================================================
@dataclass
class FLExFeatureValue:

    abbreviation: str = ""
    feature: Optional["FLExFeature"] = None

    # Return True if the given abbreviation is one of the Greek variable symbols.
    @staticmethod
    def isGreek(abbreviation: str) -> bool:

        return abbreviation in GREEK_VARIABLES

@dataclass
class FLExFeature:

    name: str = ""
    values: list[FLExFeatureValue] = field(default_factory=list)

    def __post_init__(self):

        # Back-link each value to this owning feature.
        for value in self.values:

            value.feature = self

    # Make a deep copy of this feature, including copies of all its values.
    def duplicate(self) -> "FLExFeature":

        newFeature = FLExFeature(name=self.name)
        newFeature.values = [FLExFeatureValue(abbreviation=v.abbreviation) for v in self.values]
        newFeature.__post_init__()
        return newFeature

@dataclass
class ValidFeature:

    name: str = ""
    validFeatureType: str = ""

@dataclass
class FLExCategory:

    abbreviation: str = ""
    validFeatures: list[ValidFeature] = field(default_factory=list)

@dataclass
class FLExDataBase:

    name: str = ""
    categories: list[FLExCategory] = field(default_factory=list)
    features: list[FLExFeature] = field(default_factory=list)
    featuresWithoutVariables: list[FLExFeature] = field(default_factory=list)
    maxVariables: int = 4

    def __post_init__(self):

        pass

    # Add Greek variable values to each feature, keeping an unmodified copy of the feature list.
    def addVariableValuesToFeatures(self) -> None:

        # Preserve the original (variable-free) features before appending variable values.
        self.featuresWithoutVariables = [f.duplicate() for f in self.features]

        for feature in self.features:

            for i in range(min(self.maxVariables, len(GREEK_VARIABLES))):

                feature.values.append(FLExFeatureValue(abbreviation=GREEK_VARIABLES[i]))

    def getFlexCategoriesForPhrase(self) -> list[FLExCategory]:

        return self.categories

    # Return the features valid for the given category abbreviation.
    def getFeaturesForCategory(self, categoryAbbr: str) -> list[FLExFeature]:

        for category in self.categories:

            if category.abbreviation == categoryAbbr:

                validNames = {vf.name for vf in category.validFeatures}
                return [f for f in self.features if f.name in validNames]

        return []

@dataclass
class SourceFLExData(FLExDataBase):

    pass

@dataclass
class TargetFLExData(FLExDataBase):

    pass

@dataclass
class FLExData:

    sourceData: SourceFLExData = field(default_factory=SourceFLExData)
    targetData: TargetFLExData = field(default_factory=TargetFLExData)

    # Return the categories for the requested phrase (source or target).
    def getFlexCategoriesForPhrase(self, phraseType) -> list[FLExCategory]:

        if phraseType == PhraseType.source:

            return self.sourceData.getFlexCategoriesForPhrase()

        return self.targetData.getFlexCategoriesForPhrase()

    # Return the features for a category within the requested phrase (source or target).
    def getFeaturesInPhraseForCategory(self, phraseType, categoryAbbr: str):

        if phraseType == PhraseType.source:

            return self.sourceData.getFeaturesForCategory(categoryAbbr)

        return self.targetData.getFeaturesForCategory(categoryAbbr)

# ============================================================
# Rule constituent base
# ============================================================
class RuleConstituent:

    def __init__(self):

        self.identifier: int = 0
        # parent is usually another RuleConstituent, but a rule's parent is the FLExTransRuleGenerator (the root container), so type it broadly.
        self.parent: Optional[object] = None

    # Produce the opening HTML span for this constituent, wired to call back into the app on click.
    def produceSpan(self, cssClass: str, typeCode: str) -> str:

        return (f'<span class="{cssClass}" id="{typeCode}.{self.identifier}" ' f'onmousedown="toApp(\'{typeCode}.{self.identifier}\',event)">')

    def produceToApp(self, typeCode: str) -> str:

        return f'"toApp(\'{typeCode}.{self.identifier}\',event)"'

    # Find a constituent by identifier; base implementation only matches itself.
    def findConstituent(self, identifier: int) -> Optional["RuleConstituent"]:

        if self.identifier == identifier:

            return self

        return None

# ============================================================
# Category
# ============================================================
@dataclass
class Category(RuleConstituent):

    name: str = ""

    def __post_init__(self):

        super().__init__()

    # Produce the editable, source-style HTML for this category.
    def produceHtml(self) -> str:

        cat = _translate("RuleAssistantLib", "cat")
        return f'{self.produceSpan("category", "c")}{cat}:{self.name}</span>'

    # Produce the read-only, target-style HTML for this category (tied to a word's identifier).
    def produceHtmlTarget(self, wordIdentifier: int) -> str:

        cat = _translate("RuleAssistantLib", "cat")
        return (f'<span class="categorytgt" id="w.{wordIdentifier}" ' f'onclick="toApp(\'w.{wordIdentifier}\',event)">{cat}:{self.name}</span>')

# ============================================================
# Feature
# ============================================================
@dataclass
class Feature(RuleConstituent):

    label: str = ""
    match: str = ""
    value: str = ""
    unmarked: str = ""
    ranking: int = 0

    def __post_init__(self):

        super().__init__()

    # Prefer the match string when present; otherwise fall back to the value.
    def getMatchOrValue(self) -> str:

        return self.match if self.match else self.value

    # Produce the HTML for this feature, optionally styled as a head feature.
    def produceHtml(self, isHead: bool = False) -> str:

        # Local translation helper that falls back to a default mapping when PyQt is unavailable.
        def _t(s: str) -> str:

            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)

            except ImportError:

                return {"FeatureX": "Feature"}.get(s, s)

        cssClass = "feature headfeature" if isHead else "feature"
        html = self.produceSpan(cssClass, "f")
        labelText = self.label if self.label else _t("FeatureX")
        html += f"{labelText}:{self.getMatchOrValue()}"

        # Show the ranking badge when this feature has been assigned a ranking.
        if self.ranking > 0:

            html += f'<span class="ranking feature">{self.ranking}</span>'

        # Show the unmarked-default badge when one is set.
        if self.unmarked:

            html += f'\n<span class="unmarked feature">unmarked:{self.unmarked}</span>'

        html += "</span>"
        return html

    # Make a copy of this feature with the same field values.
    def duplicate(self) -> "Feature":

        return Feature(label=self.label, match=self.match, value=self.value, unmarked=self.unmarked, ranking=self.ranking)

    # Assign sequential rankings to any sister features that do not yet have one.
    def assignRankingsToSisters(self, maxRankings: int) -> None:

        if not self.parent:

            return

        sisters = getattr(self.parent, "features", [])
        used = {s.ranking for s in sisters if hasattr(s, "ranking") and s.ranking > 0}
        n = 1

        for s in sisters:

            if hasattr(s, "ranking") and s.ranking == 0:

                # Find the next unused ranking number.
                while n in used:

                    n += 1

                s.ranking = n
                used.add(n)

    # Return True if any other sister feature already has a ranking.
    def sisterFeatureHasRanking(self) -> bool:

        if not self.parent:

            return False

        sisters = getattr(self.parent, "features", [])
        return any(hasattr(s, "ranking") and s.ranking > 0 for s in sisters if s is not self)

    # Swap this feature's ranking with the sister currently holding the new ranking.
    def swapRankingOfSisterWithRanking(self, newRanking: int, oldRanking: int) -> None:

        if not self.parent:

            return

        for s in getattr(self.parent, "features", []):

            if s is self:

                self.ranking = newRanking

            elif hasattr(s, "ranking") and s.ranking == newRanking:

                s.ranking = oldRanking

    # Clear the rankings on all sister features.
    def removeRankingsFromSisters(self) -> None:

        if not self.parent:

            return

        for s in getattr(self.parent, "features", []):

            if hasattr(s, "ranking"):

                s.ranking = 0

# ============================================================
# Affix
# ============================================================
@dataclass
class Affix(RuleConstituent):

    affixType: AffixType = AffixType.suffix
    features: list["Feature"] = field(default_factory=list)

    def __post_init__(self):

        super().__init__()

    # Produce the list-item HTML for this affix, including its features.
    def produceHtml(self, isHead: bool = False) -> str:

        if self.affixType == AffixType.prefix:

            affixTypeStr = _translate("RuleAssistantLib", "prefix")
        else:
            affixTypeStr = _translate("RuleAssistantLib", "suffix")

        html = "<li>"
        html += self.produceSpan("tf-nc affix", "a")
        html += affixTypeStr + "</span>"

        # Render the affix's features as a nested list when present.
        if self.features:

            html += "<ul>\n" + self._produceFeaturesHtml(isHead) + "</ul>"

        html += "</li>\n"
        return html

    # Produce the inner table HTML listing this affix's features.
    def _produceFeaturesHtml(self, isHead: bool = False) -> str:

        html = "<li><table class=\"tf-nc\">\n"

        for feature in self.features:

            html += "<tr>\n<td align=\"left\">" + feature.produceHtml(isHead) + "</td>\n</tr>\n"

        html += "</table>\n</li>\n"
        return html

    # Find a constituent by identifier within this affix or its features.
    def findConstituent(self, identifier: int) -> "RuleConstituent | None":

        if self.identifier == identifier:

            return self

        for feature in self.features:

            r = feature.findConstituent(identifier)

            if r:

                return r

        return None

    # Make a copy of this affix, including copies of its features (re-parented to the new affix).
    def duplicate(self) -> "Affix":

        newAffix = Affix(affixType=self.affixType)
        newAffix.features = [f.duplicate() for f in self.features]

        for f in newAffix.features:

            f.parent = newAffix

        return newAffix

    # Return True if this affix's parent word is marked as the head.
    def getIsHead(self) -> bool:

        if not self.parent:

            return False

        # parent is typed broadly (object), so read head via getattr; return a real bool.
        head = getattr(self.parent, "head", None)
        return bool(head) and str(head).lower() == "yes"

# ============================================================
# Phrase
# ============================================================
@dataclass
class Phrase(RuleConstituent):

    words: list["Word"] = field(default_factory=list)
    phraseType: PhraseType = PhraseType.source

    def __post_init__(self):

        super().__init__()

    # Produce the HTML for this phrase and all its words.
    def produceHtml(self) -> str:

        # Local translation helper that falls back to a default mapping when PyQt is unavailable.
        def _t(s: str) -> str:

            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)

            except ImportError:

                return {"phrase": "phrase", "src": "src", "tgt": "tgt"}.get(s, s)

        lang = _t("src") if self.phraseType == PhraseType.source else _t("tgt")
        html = "<li>" + self.produceSpan("tf-nc", "p") + _t("phrase")
        html += f'<span class="language">{lang}</span></span>\n'
        html += "<ul>"

        for word in self.words:

            html += word.produceHtml()

        html += "</ul></li>"
        return html

    # Find a constituent by identifier within this phrase or its words.
    def findConstituent(self, identifier: int) -> "RuleConstituent | None":

        if self.identifier == identifier:

            return self

        for word in self.words:

            r = word.findConstituent(identifier)

            if r:

                return r

        return None

    # Insert a brand-new word at the given index, assigning it a unique id and parenting it.
    def insertNewWordAt(self, index: int) -> "Word":

        newWord = Word()
        newWord.wordId = newWord.getIdOfNewlyAddedWord(self.words)
        self.words.insert(index, newWord)
        newWord.parent = self
        return newWord

    # Compute the next unused numeric id (as a string) for a newly added word.
    def getIdOfNewlyAddedWord(self) -> str:

        usedIds = {int(w.wordId) for w in self.words if w.wordId.isdigit()}
        nextId = 1

        while nextId in usedIds:

            nextId += 1

        return str(nextId)

    # Swap the positions of the two words at the given indexes (when both are valid).
    def swapPositionOfWords(self, i: int, j: int) -> None:

        if 0 <= i < len(self.words) and 0 <= j < len(self.words):

            self.words[i], self.words[j] = self.words[j], self.words[i]

    # Change a word's id, swapping ids with any other word that already holds the new id.
    def changeIdOfWord(self, wordIndex: int, oldId: str, newId: str) -> None:

        if not (0 <= wordIndex < len(self.words)):

            return

        # If another word already uses the new id, give it the old id to avoid collisions.
        for otherWord in self.words:

            if otherWord.wordId == newId:

                otherWord.wordId = oldId
                break

        self.words[wordIndex].wordId = newId

    # Mark the given word as the head and all others as non-head.
    def markWordAsHead(self, word: "Word") -> None:

        for w in self.words:

            w.head = HeadValue.yes if w is word else HeadValue.no

    # Return the category of the word with the given id, or empty string if not found.
    def getCategoryOfWordWithId(self, wordId: str) -> str:

        for word in self.words:

            if word.wordId == wordId:

                return word.wordCategory

        return ""

    def getFeaturesInUse(self) -> list:

        return []

    # Return the FLEx features in use for the given category, based on feature labels found in the phrase.
    def getFeaturesInUseForCategory(self, allFlexFeatures, categoryAbbr: str) -> list:

        phraseFeatureLabels = set()

        for word in self.words:

            if word.wordCategory == categoryAbbr:

                for feature in word.getAllFeaturesInWord():

                    if feature.label:

                        phraseFeatureLabels.add(feature.label)

        return [f for f in allFlexFeatures if f.name in phraseFeatureLabels]

# ============================================================
# Source / Target
# ============================================================
@dataclass
class Source(Phrase):

    def __post_init__(self):

        super().__post_init__()
        self.phraseType = PhraseType.source

@dataclass
class Target(Phrase):

    def __post_init__(self):

        super().__post_init__()
        self.phraseType = PhraseType.target

# ============================================================
# Word
# ============================================================
@dataclass
class Word(RuleConstituent):

    wordId: str = ""
    wordCategory: str = ""
    head: HeadValue = HeadValue.no
    features: list["Feature"] = field(default_factory=list)
    affixes: list["Affix"] = field(default_factory=list)
    categoryConstituent: Optional[Category] = None

    def __post_init__(self):

        super().__init__()

        # Ensure the word always has a category constituent for rendering.
        if self.categoryConstituent is None:

            self.categoryConstituent = Category(name=self.wordCategory)

    # Produce the HTML for this word, including its category, features, and affixes.
    def produceHtml(self) -> str:

        # Local translation helper that falls back to a default mapping when PyQt is unavailable.
        def _t(s: str) -> str:

            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)

            except ImportError:

                return {"word": "word", "head": "head"}.get(s, s)

        headClass = "headword" if self.head == HeadValue.yes else ""
        html = "<li><table class=\"tf-nc\">\n<tr>\n<td align=\"center\">"
        html += self.produceSpan(headClass, "w") + _t("word")

        # Add a "(head)" annotation when this word is the head.
        if self.head == HeadValue.yes:

            html += ('(<span style="font-style:italic; font-size:smaller">' + _t("head") + "</span>)")

        # Show the word's index when it has an id.
        if self.wordId:

            html += f'<span class="index">{self.wordId}</span>\n'

        html += "</span>\n</td>\n</tr>\n"

        # Render the category row when there is category HTML to show.
        categoryHtml = self._produceCategoryHtml()

        if categoryHtml:

            html += "<tr>\n<td align=\"center\">" + categoryHtml + "</td>\n</tr>\n"

        html += "</table>\n"

        # Render prefixes, then features, then suffixes inside a nested list.
        if self.affixes or self.features:

            html += "<ul>\n"

            for affix in (a for a in self.affixes if a.affixType == AffixType.prefix):

                html += affix.produceHtml(self.head == HeadValue.yes)

            if self.features:

                html += self._produceFeaturesHtml()

            for affix in (a for a in self.affixes if a.affixType == AffixType.suffix):

                html += affix.produceHtml(self.head == HeadValue.yes)

            html += "</ul>\n"

        html += "</li>"
        return html

    # Produce the category HTML for this word, falling back to the source word's category if needed.
    def _produceCategoryHtml(self) -> str:

        if self.wordCategory:

            # The word has its own category: editable, source-style span.
            if self.categoryConstituent:

                return self.categoryConstituent.produceHtml()

            return ""

        # No category of its own: fall back to the corresponding source word's
        # category, shown read-only under the (target) word box. Matches the Java
        # version, which derives a target word's category from the source word.
        cat = self.getCategoryOfWordOrCorrespondingSourceWord()

        if cat and cat.name:

            return cat.produceHtmlTarget(self.identifier)

        return ""

    # Produce the inner table HTML listing this word's own features.
    def _produceFeaturesHtml(self) -> str:

        html = "<li><table class=\"tf-nc\">\n"

        for feature in self.features:

            html += "<tr>\n<td align=\"left\">" + feature.produceHtml(self.head == HeadValue.yes) + "</td>\n</tr>\n"

        html += "</table>\n</li>\n"
        return html

    # Find a constituent by identifier within this word, its category, features, or affixes.
    def findConstituent(self, identifier: int) -> "RuleConstituent | None":

        if self.identifier == identifier:

            return self

        if self.categoryConstituent and self.categoryConstituent.findConstituent(identifier):

            return self.categoryConstituent.findConstituent(identifier)

        for feature in self.features:

            r = feature.findConstituent(identifier)

            if r:

                return r

        for affix in self.affixes:

            r = affix.findConstituent(identifier)

            if r:

                return r

        return None

    # Compute the next unused numeric id (as a string) given the existing phrase words.
    def getIdOfNewlyAddedWord(self, phraseWords: list) -> str:

        usedIds = {int(w.wordId) for w in phraseWords if w.wordId.isdigit()}
        nextId = 1

        while nextId in usedIds:

            nextId += 1

        return str(nextId)

    # Make a deep copy of this word, including copies of its features and affixes (all re-parented).
    def duplicate(self) -> "Word":

        newWord = Word(wordId=self.wordId, wordCategory=self.wordCategory, head=self.head)
        newWord.categoryConstituent = Category(name=self.wordCategory)
        newWord.features = [f.duplicate() for f in self.features]

        for f in newWord.features:

            f.parent = newWord

        newWord.affixes = [a.duplicate() for a in self.affixes]

        for a in newWord.affixes:

            a.parent = newWord

        return newWord

    # Return this word's own category, or fall back to the matching source word's category for a target word.
    def getCategoryOfWordOrCorrespondingSourceWord(self) -> Optional[Category]:

        if self.categoryConstituent and self.categoryConstituent.name:

            return self.categoryConstituent

        if not self.parent:

            return None

        phrase = self.parent

        if not isinstance(phrase, Phrase):

            return None

        rule = phrase.parent

        if not rule:

            return None

        # Only target words derive their category from a corresponding source word.
        if phrase.phraseType == PhraseType.target:

            sourcePhrase = getattr(rule, "source", None)
        else:
            return None

        if not sourcePhrase:

            return None

        # Find the source word with the same id and use its category constituent.
        for sourceWord in getattr(sourcePhrase, "words", []):

            if sourceWord.wordId == self.wordId:

                return sourceWord.categoryConstituent

        return None

    # Return all features belonging to this word, including those on its affixes.
    def getAllFeaturesInWord(self) -> list:

        features = list(self.features)

        for affix in self.affixes:

            features.extend(affix.features)

        return features

# ============================================================
# DisjointFeatureSet
# ============================================================
@dataclass
class DisjointFeatureValuePairing:

    flexFeatureName: str = ""
    coFeatureValue: str = ""

    # Make a copy of this pairing.
    def duplicate(self) -> "DisjointFeatureValuePairing":

        return DisjointFeatureValuePairing(flexFeatureName=self.flexFeatureName, coFeatureValue=self.coFeatureValue)

@dataclass
class DisjointFeatureSet:

    name: str = ""
    coFeatureName: str = ""
    language: PhraseType = PhraseType.target
    pairings: list[DisjointFeatureValuePairing] = field(default_factory=list)

    # Truncate the pairings list at the given index (only for indexes in the 3..6 range).
    def removePairingsFrom(self, index: int) -> None:

        if 3 <= index <= 6 and index < len(self.pairings):

            self.pairings = self.pairings[:index]

    # Return True if every pairing's FLEx feature name is present in the given feature list.
    def hasFlexFeatureInList(self, flexFeatures: list) -> bool:

        featureNames = {f.name for f in flexFeatures if hasattr(f, "name")}
        return all(p.flexFeatureName in featureNames for p in self.pairings)

    # Make a copy of this disjoint feature set, including copies of its pairings.
    def duplicate(self) -> "DisjointFeatureSet":

        newSet = DisjointFeatureSet(name=self.name, coFeatureName=self.coFeatureName, language=self.language)
        newSet.pairings = [p.duplicate() for p in self.pairings]
        return newSet

# ============================================================
# FLExTransRule + Generator
# ============================================================
@dataclass
class FLExTransRule(RuleConstituent):

    name: str = ""
    description: str = ""
    createPermutations: PermutationsValue = PermutationsValue.no
    source: Source = field(default_factory=Source)
    target: Target = field(default_factory=Target)

    def __post_init__(self):

        super().__init__()

    # Find a constituent by identifier within this rule's source or target phrase.
    def findConstituent(self, identifier: int) -> "RuleConstituent | None":

        if self.identifier == identifier:

            return self

        r = self.source.findConstituent(identifier)

        if r:

            return r

        return self.target.findConstituent(identifier)

    @staticmethod
    def newWithWordBoxes(name: str) -> "FLExTransRule":
        """Create a new rule that already has one source word and one target word
        (each parented) so the tree view shows editable word boxes, matching the
        Java version. Without this a new rule renders empty and can't be edited."""

        rule = FLExTransRule(name=name)
        rule.source = Source()
        rule.target = Target()
        wordS = Word(wordId="1")
        wordT = Word(wordId="1")
        rule.source.words = [wordS]
        rule.target.words = [wordT]
        wordS.parent = rule.source
        wordT.parent = rule.target
        rule.source.parent = rule
        rule.target.parent = rule
        return rule

    # Make a deep copy of this rule, re-parenting all the duplicated phrases and words.
    def duplicate(self) -> "FLExTransRule":

        newRule = FLExTransRule(name=self.name + " (duplicate)", description=self.description, createPermutations=self.createPermutations)
        newRule.source = Source()
        newRule.source.phraseType = self.source.phraseType
        newRule.source.words = [w.duplicate() for w in self.source.words]

        for w in newRule.source.words:

            w.parent = newRule.source

        newRule.source.parent = newRule
        newRule.target = Target()
        newRule.target.phraseType = self.target.phraseType
        newRule.target.words = [w.duplicate() for w in self.target.words]

        for w in newRule.target.words:

            w.parent = newRule.target

        newRule.target.parent = newRule
        return newRule

@dataclass
class FLExTransRuleGenerator:

    flexTransRules: list[FLExTransRule] = field(default_factory=list)
    disjointFeatures: list[DisjointFeatureSet] = field(default_factory=list)
    overwriteRules: OverwriteRulesValue = OverwriteRulesValue.yes

    def __post_init__(self):

        # Re-establish parent back-links throughout the whole rule tree after loading.
        for rule in self.flexTransRules:

            rule.source.parent = rule
            rule.target.parent = rule

            for word in rule.source.words:

                word.parent = rule.source

                for f in word.features:

                    f.parent = word

                for a in word.affixes:

                    a.parent = word

                    for f in a.features:

                        f.parent = a

            for word in rule.target.words:

                word.parent = rule.target

                for f in word.features:

                    f.parent = word

                for a in word.affixes:

                    a.parent = word

                    for f in a.features:

                        f.parent = a

    # Insert a duplicate of the rule at the given index (when the index is valid).
    def duplicateRule(self, ruleIndex: int) -> None:

        if 0 <= ruleIndex < len(self.flexTransRules):

            self.flexTransRules.insert(ruleIndex, self.flexTransRules[ruleIndex].duplicate())

    # Create a new editable rule (with word boxes) and insert it at index.
    def insertNewRule(self, index: int, name: str) -> "FLExTransRule":
        """Create a new editable rule (with word boxes) and insert it at index."""

        rule = FLExTransRule.newWithWordBoxes(name)
        rule.parent = self
        self.flexTransRules.insert(index, rule)
        return rule

# ============================================================
# ApplicationPreferences
# ============================================================
class ApplicationPreferences:

    LAST_LOCALE_LANGUAGE = "lastLocaleLanguage"
    LAST_SELECTED_RULE = "lastSelectedRule"
    LAST_SELECTED_DISJOINT_FEATURE_SET = "lastSelectedDisjointFeatureSet"
    LAST_WINDOW = "lastWindow"
    POSITION_X = "PositionX"
    POSITION_Y = "PositionY"
    WIDTH = "Width"
    HEIGHT = "Height"
    MAXIMIZED = "Maximized"
    LAST_SPLIT_PANE_POSITION = "lastSplitPanePosition"
    MAIN_SPLITTER_SIZES = "mainSplitterSizes"
    V_SPLITTER_SIZES = "vSplitterSizes"
    H_SPLITTER_SIZES = "hSplitterSizes"

    # Settings live in this TOML-formatted file in the project's Config folder (replacing the old QSettings/registry storage).
    SETTINGS_FILENAME = "RuleAssistantSettings.txt"

    def __init__(self):

        self._filePath = os.path.join(FTPaths.CONFIG_DIR, self.SETTINGS_FILENAME)
        self._data = self._load()

    # Read the TOML settings file into a flat dict; a missing or unreadable file just means "use defaults".
    def _load(self) -> dict:

        try:
            with open(self._filePath, "rb") as f:

                return tomllib.load(f)

        except (FileNotFoundError, OSError, tomllib.TOMLDecodeError):

            return {}

    def getLastLocaleLanguage(self, default: str = "en") -> str:

        return str(self._data.get(self.LAST_LOCALE_LANGUAGE, default))

    def setLastLocaleLanguage(self, langCode: str) -> None:

        self._data[self.LAST_LOCALE_LANGUAGE] = langCode

    def getLastSelectedRule(self, default: int = 0) -> int:

        return int(self._data.get(self.LAST_SELECTED_RULE, default))

    def setLastSelectedRule(self, index: int) -> None:

        self._data[self.LAST_SELECTED_RULE] = index

    def getLastSelectedDisjointFeatureSet(self, default: int = 0) -> int:

        return int(self._data.get(self.LAST_SELECTED_DISJOINT_FEATURE_SET, default))

    def setLastSelectedDisjointFeatureSet(self, index: int) -> None:

        self._data[self.LAST_SELECTED_DISJOINT_FEATURE_SET] = index

    def getWindowPositionX(self, default: int = 100) -> int:

        return int(self._data.get(f"{self.LAST_WINDOW}{self.POSITION_X}", default))

    def setWindowPositionX(self, x: int) -> None:

        self._data[f"{self.LAST_WINDOW}{self.POSITION_X}"] = x

    def getWindowPositionY(self, default: int = 100) -> int:

        return int(self._data.get(f"{self.LAST_WINDOW}{self.POSITION_Y}", default))

    def setWindowPositionY(self, y: int) -> None:

        self._data[f"{self.LAST_WINDOW}{self.POSITION_Y}"] = y

    def getWindowWidth(self, default: int = 660) -> int:

        return int(self._data.get(f"{self.LAST_WINDOW}{self.WIDTH}", default))

    def setWindowWidth(self, width: int) -> None:

        self._data[f"{self.LAST_WINDOW}{self.WIDTH}"] = width

    def getWindowHeight(self, default: int = 1000) -> int:

        return int(self._data.get(f"{self.LAST_WINDOW}{self.HEIGHT}", default))

    def setWindowHeight(self, height: int) -> None:

        self._data[f"{self.LAST_WINDOW}{self.HEIGHT}"] = height

    def getWindowMaximized(self, default: bool = False) -> bool:

        return bool(self._data.get(f"{self.LAST_WINDOW}{self.MAXIMIZED}", default))

    def setWindowMaximized(self, maximized: bool) -> None:

        self._data[f"{self.LAST_WINDOW}{self.MAXIMIZED}"] = bool(maximized)

    def getSplitPanePosition(self, default: float = 0.3) -> float:

        return float(self._data.get(self.LAST_SPLIT_PANE_POSITION, default))

    def setSplitPanePosition(self, position: float) -> None:

        self._data[self.LAST_SPLIT_PANE_POSITION] = position

    # Splitter sizes are stored as a list of pixel widths/heights (one per pane); an empty list means "not saved yet".
    def getMainSplitterSizes(self) -> list:

        return [int(s) for s in self._data.get(self.MAIN_SPLITTER_SIZES, [])]

    def setMainSplitterSizes(self, sizes) -> None:

        self._data[self.MAIN_SPLITTER_SIZES] = [int(s) for s in sizes]

    def getVSplitterSizes(self) -> list:

        return [int(s) for s in self._data.get(self.V_SPLITTER_SIZES, [])]

    def setVSplitterSizes(self, sizes) -> None:

        self._data[self.V_SPLITTER_SIZES] = [int(s) for s in sizes]

    def getHSplitterSizes(self) -> list:

        return [int(s) for s in self._data.get(self.H_SPLITTER_SIZES, [])]

    def setHSplitterSizes(self, sizes) -> None:

        self._data[self.H_SPLITTER_SIZES] = [int(s) for s in sizes]

    # Persist the current settings to the TOML file, creating the Config folder if it doesn't exist yet.
    def sync(self) -> None:

        os.makedirs(os.path.dirname(self._filePath), exist_ok=True)

        with open(self._filePath, "wb") as f:

            tomli_w.dump(self._data, f)

# ============================================================
# ConstituentFinder
# ============================================================
class ConstituentFinder:

    # Find a constituent by identifier, choosing the source or target phrase based on the identifier value.
    def findConstituent(self, rule: FLExTransRule, identifier: int) -> Optional[RuleConstituent]:

        targetPhraseId = rule.target.identifier

        if identifier < targetPhraseId:

            return rule.source.findConstituent(identifier)

        return rule.target.findConstituent(identifier)

# ============================================================
# RuleIdentifierAndParentSetter
# ============================================================
class RuleIdentifierAndParentSetter:

    # Assign sequential identifiers and set parent links across the whole rule tree.
    def setIdentifiersAndParents(self, rule: FLExTransRule) -> None:

        self.counter = 0
        self._setPhraseIdentifiers(rule.source, rule)
        self._setPhraseIdentifiers(rule.target, rule)
        rule.source.parent = rule
        rule.target.parent = rule

    # Assign identifiers and parents within a single phrase (words, categories, features, affixes).
    def _setPhraseIdentifiers(self, phrase, rule) -> None:

        self.counter += 1
        phrase.identifier = self.counter
        phrase.parent = rule

        for word in phrase.words:

            self.counter += 1
            word.identifier = self.counter
            word.parent = phrase

            if word.categoryConstituent:

                self.counter += 1
                word.categoryConstituent.identifier = self.counter
                word.categoryConstituent.parent = word

            for feature in word.features:

                self.counter += 1
                feature.identifier = self.counter
                feature.parent = word

            for affix in word.affixes:

                self.counter += 1
                affix.identifier = self.counter
                affix.parent = word

                for feature in affix.features:

                    self.counter += 1
                    feature.identifier = self.counter
                    feature.parent = affix

# ============================================================
# ValidityChecker
# ============================================================
class ValidityChecker:

    # Verify every source word has a category.
    @staticmethod
    def checkSourceWordsHaveCategories(rule: FLExTransRule) -> tuple[bool, str]:

        for word in rule.source.words:

            if not word.wordCategory:

                return False, _translate("RuleAssistantLib", "One or more source words do not have a category.  Please insert a category for every source word.")

        return True, ""

    # Verify at least one target word or affix has a feature.
    @staticmethod
    def checkTargetHasFeature(rule: FLExTransRule) -> tuple[bool, str]:

        for word in rule.target.words:

            if word.features:

                return True, ""

            for affix in word.affixes:

                if affix.features:

                    return True, ""

        return False, _translate("RuleAssistantLib", "No word or affix in the target has a feature.  Please insert at least one feature.")

    # Verify exactly one target word is marked as head when there is more than one word.
    @staticmethod
    def checkTargetWordMarkedAsHead(rule: FLExTransRule) -> tuple[bool, str]:

        words = rule.target.words

        if len(words) <= 1:

            return True, ""

        headCount = sum(1 for w in words if w.head == HeadValue.yes)

        if headCount == 1:

            return True, ""

        elif headCount == 0:

            return False, _translate("RuleAssistantLib", "No word has been marked as the head in the target phrase.  Please mark one word as the head.")

        return False, _translate("RuleAssistantLib", "Target phrase has {0} head words; only one allowed").format(headCount)

    # Run all validity checks and return the first failure, or success if all pass.
    @staticmethod
    def validateRule(rule: FLExTransRule) -> tuple[bool, str]:

        for check in [
            ValidityChecker.checkSourceWordsHaveCategories,
            ValidityChecker.checkTargetHasFeature,
            ValidityChecker.checkTargetWordMarkedAsHead,
        ]:

            isValid, errorMsg = check(rule)

            if not isValid:

                return False, errorMsg

        return True, ""

# ============================================================
# WebPageInteractor
# ============================================================
class WebPageInteractor(QObject):

    def __init__(self, controller):

        super().__init__()
        self._controller = controller
        self._xCoord = 0
        self._yCoord = 0

    # JS bridge slot: record the screen X coordinate of the last click.
    @pyqtSlot(int)
    def setXCoord(self, x: int) -> None:

        self._xCoord = x

    # JS bridge slot: record the screen Y coordinate of the last click.
    @pyqtSlot(int)
    def setYCoord(self, y: int) -> None:

        self._yCoord = y

    # JS bridge slot: notify the controller which item was clicked, with the recorded coordinates.
    @pyqtSlot(str)
    def setItemClickedOn(self, item: str) -> None:

        if self._controller:

            self._controller.processItemClickedOn(item, self._xCoord, self._yCoord)

    @property
    def xCoord(self) -> int:

        return self._xCoord

    @property
    def yCoord(self) -> int:

        return self._yCoord

# ============================================================
# WebPageProducer
# ============================================================
class WebPageProducer:

    def __init__(self, cssAssetsDir: Optional[str] = None):

        self._treeflexCss = ""
        self._rulegenCss = ""
        self._loadCssFiles(cssAssetsDir)

    # Load the treeflex and rulegen CSS files from the assets directory (or this file's directory).
    def _loadCssFiles(self, cssAssetsDir: Optional[str] = None) -> None:

        baseDir = Path(cssAssetsDir) if cssAssetsDir else Path(__file__).resolve().parent

        for attr, name in [("_treeflexCss", "treeflex.css"), ("_rulegenCss", "rulegen.css")]:

            f = baseDir / name

            try:
                if f.exists():

                    setattr(self, attr, f.read_text(encoding="utf-8"))
                else:
                    # Without the CSS the tree renders as unstyled text, so make
                    # a missing file loud rather than failing silently.
                    print(f"Warning: Rule Assistant CSS not found: {f}")

            except Exception as e:

                print(f"Warning: Could not load {name}: {e}")

    # Produce the full HTML web page for the given rule.
    def produceWebPage(self, rule: FLExTransRule) -> str:

        RuleIdentifierAndParentSetter().setIdentifiersAndParents(rule)
        html = self._htmlHead(rule.name)
        html += self._htmlBody(rule)
        html += "</body>\n</html>"
        return html

    # Produce the HTML head (title, CSS, and JavaScript) for the page.
    def _htmlHead(self, title: str) -> str:

        return (
            '<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>'
            f"<title>{title}</title>\n"
            '<meta charset="utf-8"/>\n<style>\n'
            f"{self._treeflexCss}\n{self._rulegenCss}\n</style>\n"
            f"{self._javascript()}\n</head>\n<body>\n"
        )

    # Produce the HTML body holding the source phrase, an arrow, and the target phrase.
    def _htmlBody(self, rule: FLExTransRule) -> str:

        return ("<table>\n<tr>\n" + self._phraseTd(rule.source) + '<td>\n<span class="arrow"/>\n</td>\n' + self._phraseTd(rule.target) + "</tr>\n</table>\n")

    # Produce a table cell wrapping a phrase's tree HTML.
    def _phraseTd(self, phrase) -> str:

        return ('<td valign="top">\n<span class="tf-tree tf-gap-sm">\n<ul>\n' + phrase.produceHtml() + "\n</ul>\n</span>\n</td>\n")

    # Produce the JavaScript that wires up the Qt web channel and the toApp click bridge.
    def _javascript(self) -> str:

        return (
            '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>\n'
            "<script>\n"
            "document.addEventListener('DOMContentLoaded', function() {\n"
            "    new QWebChannel(qt.webChannelTransport, function(channel) {\n"
            "        window.ftRuleGenApp = channel.objects.ftRuleGenApp;\n"
            "    });\n"
            "});\n\n"
            "function toApp(msg, event) {\n"
            "    if (window.ftRuleGenApp) {\n"
            "        ftRuleGenApp.setXCoord(event.screenX);\n"
            "        ftRuleGenApp.setYCoord(event.screenY);\n"
            "        ftRuleGenApp.setItemClickedOn(msg);\n"
            "    }\n    return false;\n}\n</script>\n"
        )

# ============================================================
# XMLBackEndProvider
# ============================================================
class XMLBackEndProvider:

    DOCTYPE = ('<?xml version="1.0" encoding="utf-8"?>\n' '<!DOCTYPE FLExTransRuleGenerator PUBLIC " -//XMLmind//DTD FLExTransRuleGenerator//EN"\n' '"FLExTransRuleGenerator.dtd">\n')

    # Load a rule generator from an XML file, creating a default file if none exists.
    @staticmethod
    def loadDataFromFile(filename: str) -> FLExTransRuleGenerator:

        filePath = Path(filename)

        # No file yet: create a generator with a single default rule and persist it.
        if not filePath.exists():

            generator = FLExTransRuleGenerator()
            rule = FLExTransRule.newWithWordBoxes("Rule 1")
            rule.parent = generator
            generator.flexTransRules = [rule]
            XMLBackEndProvider.saveDataToFile(generator, filename)
            return generator

        tree = ET.parse(filename)
        root = tree.getroot()
        generator = FLExTransRuleGenerator()
        generator.overwriteRules = OverwriteRulesValue(root.get("overwrite_rules", "yes"))

        # Parse the disjoint feature sets, if present.
        disjointSetsEl = root.find("DisjointFeatureSets")

        if disjointSetsEl is not None:

            for dsEl in disjointSetsEl.findall("DisjointFeatureSet"):

                generator.disjointFeatures.append(XMLBackEndProvider._parseDisjointFeatureSet(dsEl))

        # Parse the rules, if present, parenting each to the generator.
        rulesEl = root.find("FLExTransRules")

        if rulesEl is not None:

            for ruleEl in rulesEl.findall("FLExTransRule"):

                rule = XMLBackEndProvider._parseRule(ruleEl)
                generator.flexTransRules.append(rule)
                rule.parent = generator

        # Finalize each rule's phrase types and category constituents.
        for rule in generator.flexTransRules:

            rule.target.phraseType = PhraseType.target
            rule.source.phraseType = PhraseType.source
            XMLBackEndProvider._setCategoryConstituentsInWords(rule.source)
            XMLBackEndProvider._setCategoryConstituentsInWords(rule.target)

        return generator

    # Serialize a rule generator to an XML file (with the FLExTrans DOCTYPE header).
    @staticmethod
    def saveDataToFile(generator: FLExTransRuleGenerator, filename: str) -> None:

        root = ET.Element("FLExTransRuleGenerator")
        root.set("overwrite_rules", generator.overwriteRules.value)

        # Write the disjoint feature sets, if any.
        if generator.disjointFeatures:

            disjointSetsEl = ET.SubElement(root, "DisjointFeatureSets")

            for ds in generator.disjointFeatures:

                XMLBackEndProvider._createDisjointFeatureSetElement(ds, disjointSetsEl)

        rulesEl = ET.SubElement(root, "FLExTransRules")

        for rule in generator.flexTransRules:

            XMLBackEndProvider._createRuleElement(rule, rulesEl)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        buf = io.StringIO()
        tree.write(buf, encoding="unicode", xml_declaration=False)

        with open(filename, "w", encoding="utf-8") as f:

            f.write(XMLBackEndProvider.DOCTYPE)
            f.write(buf.getvalue())

    # Parse a single FLExTransRule element into a rule object.
    @staticmethod
    def _parseRule(ruleEl) -> FLExTransRule:

        descEl = ruleEl.find("Description")
        description = descEl.text if descEl is not None and descEl.text else ""
        rule = FLExTransRule(name=ruleEl.get("name", ""), description=description, createPermutations=PermutationsValue(ruleEl.get("create_permutations", "with_head")))

        # Parse the source phrase's words, if present.
        sourceEl = ruleEl.find("Source")

        if sourceEl is not None:

            phraseEl = sourceEl.find("Phrase")

            if phraseEl is not None:

                parsed = XMLBackEndProvider._parsePhrase(phraseEl, PhraseType.source)
                rule.source.words = parsed.words

                for w in rule.source.words:

                    w.parent = rule.source

        # Parse the target phrase's words, if present.
        targetEl = ruleEl.find("Target")

        if targetEl is not None:

            phraseEl = targetEl.find("Phrase")

            if phraseEl is not None:

                parsed = XMLBackEndProvider._parsePhrase(phraseEl, PhraseType.target)
                rule.target.words = parsed.words

                for w in rule.target.words:

                    w.parent = rule.target

        return rule

    # Parse a Phrase element (and its words) for the given phrase type.
    @staticmethod
    def _parsePhrase(phraseEl, phraseType: PhraseType) -> Phrase:

        phrase = Phrase(phraseType=phraseType)
        wordsEl = phraseEl.find("Words")

        if wordsEl is not None:

            for wordEl in wordsEl.findall("Word"):

                word = XMLBackEndProvider._parseWord(wordEl)
                phrase.words.append(word)
                word.parent = phrase

        return phrase

    # Parse a Word element, including its features and affixes.
    @staticmethod
    def _parseWord(wordEl) -> Word:

        word = Word(wordId=wordEl.get("id", ""), wordCategory=wordEl.get("category", ""), head=HeadValue(wordEl.get("head", "no")))

        # Parse the word's own features.
        featuresEl = wordEl.find("Features")

        if featuresEl is not None:

            for featureEl in featuresEl.findall("Feature"):

                feature = XMLBackEndProvider._parseFeature(featureEl)
                word.features.append(feature)
                feature.parent = word

        # Parse the word's affixes.
        affixesEl = wordEl.find("Affixes")

        if affixesEl is not None:

            for affixEl in affixesEl.findall("Affix"):

                affix = XMLBackEndProvider._parseAffix(affixEl)
                word.affixes.append(affix)
                affix.parent = word

        return word

    # Parse a Feature element into a Feature object.
    @staticmethod
    def _parseFeature(featureEl) -> Feature:

        return Feature(
            label=featureEl.get("label", ""),
            match=featureEl.get("match", ""),
            value=featureEl.get("value", ""),
            unmarked=featureEl.get("unmarked_default", ""),
            ranking=int(featureEl.get("ranking", "0")),
        )

    # Parse an Affix element, including its features.
    @staticmethod
    def _parseAffix(affixEl) -> Affix:

        affix = Affix(affixType=AffixType(affixEl.get("type", "suffix")))
        featuresEl = affixEl.find("Features")

        if featuresEl is not None:

            for featureEl in featuresEl.findall("Feature"):

                feature = XMLBackEndProvider._parseFeature(featureEl)
                affix.features.append(feature)
                feature.parent = affix

        return affix

    # Parse a DisjointFeatureSet element, including its value pairings.
    @staticmethod
    def _parseDisjointFeatureSet(dsEl) -> DisjointFeatureSet:

        ds = DisjointFeatureSet(name=dsEl.get("disjoint_name", ""), coFeatureName=dsEl.get("co_feature_name", ""), language=PhraseType(dsEl.get("language", "target")))
        pairingsEl = dsEl.find("DisjointFeatureValuePairings")

        if pairingsEl is not None:

            for pairingEl in pairingsEl.findall("DisjointFeatureValuePairing"):

                ds.pairings.append(DisjointFeatureValuePairing(flexFeatureName=pairingEl.get("flex_feature_name", ""), coFeatureValue=pairingEl.get("co_feature_value", "")))

        return ds

    # Build the XML element for a single rule and append it to the parent element.
    @staticmethod
    def _createRuleElement(rule: FLExTransRule, parentEl) -> None:

        ruleEl = ET.SubElement(parentEl, "FLExTransRule")
        ruleEl.set("name", rule.name)
        ruleEl.set("create_permutations", rule.createPermutations.value)
        ET.SubElement(ruleEl, "Description").text = rule.description or ""
        XMLBackEndProvider._createPhraseElement(rule.source, ET.SubElement(ruleEl, "Source"))
        XMLBackEndProvider._createPhraseElement(rule.target, ET.SubElement(ruleEl, "Target"))

    # Build the XML element for a phrase (and its words) and append it to the parent element.
    @staticmethod
    def _createPhraseElement(phrase: Phrase, parentEl) -> None:

        phraseEl = ET.SubElement(parentEl, "Phrase")

        if phrase.words:

            wordsEl = ET.SubElement(phraseEl, "Words")

            for word in phrase.words:

                XMLBackEndProvider._createWordElement(word, wordsEl)

    # Build the XML element for a word, including its features and affixes.
    @staticmethod
    def _createWordElement(word: Word, parentEl) -> None:

        wordEl = ET.SubElement(parentEl, "Word")
        wordEl.set("id", word.wordId)
        wordEl.set("category", word.wordCategory)
        wordEl.set("head", word.head.value)

        # Write the word's own features.
        if word.features:

            featuresEl = ET.SubElement(wordEl, "Features")

            for f in word.features:

                XMLBackEndProvider._createFeatureElement(f, featuresEl)

        # Write the word's affixes.
        if word.affixes:

            affixesEl = ET.SubElement(wordEl, "Affixes")

            for a in word.affixes:

                XMLBackEndProvider._createAffixElement(a, affixesEl)

    # Build the XML element for a single feature.
    @staticmethod
    def _createFeatureElement(feature: Feature, parentEl) -> None:

        el = ET.SubElement(parentEl, "Feature")
        el.set("label", feature.label)
        el.set("match", feature.match)
        el.set("value", feature.value)
        el.set("unmarked_default", feature.unmarked)
        el.set("ranking", str(feature.ranking))

    # Build the XML element for an affix, including its features.
    @staticmethod
    def _createAffixElement(affix: Affix, parentEl) -> None:

        affixEl = ET.SubElement(parentEl, "Affix")
        affixEl.set("type", affix.affixType.value)

        if affix.features:

            featuresEl = ET.SubElement(affixEl, "Features")

            for f in affix.features:

                XMLBackEndProvider._createFeatureElement(f, featuresEl)

    # Build the XML element for a disjoint feature set, including its value pairings.
    @staticmethod
    def _createDisjointFeatureSetElement(ds: DisjointFeatureSet, parentEl) -> None:

        dsEl = ET.SubElement(parentEl, "DisjointFeatureSet")
        dsEl.set("language", ds.language.value)
        dsEl.set("disjoint_name", ds.name)
        dsEl.set("co_feature_name", ds.coFeatureName)

        if ds.pairings:

            pairingsEl = ET.SubElement(dsEl, "DisjointFeatureValuePairings")

            for p in ds.pairings:

                pairingEl = ET.SubElement(pairingsEl, "DisjointFeatureValuePairing")
                pairingEl.set("flex_feature_name", p.flexFeatureName)
                pairingEl.set("co_feature_value", p.coFeatureValue)

    # Rebuild each word's category constituent from its category and parent the constituent to the word.
    @staticmethod
    def _setCategoryConstituentsInWords(phrase: Phrase) -> None:

        for word in phrase.words:

            word.categoryConstituent = Category(name=word.wordCategory)
            word.categoryConstituent.parent = word

# ============================================================
# XMLFLExDataBackEndProvider
# ============================================================
class XMLFLExDataBackEndProvider:

    # Load FLEx metadata (source and target language data) from an XML file.
    @staticmethod
    def loadDataFromFile(filename: str) -> FLExData:

        tree = ET.parse(filename)
        root = tree.getroot()
        flexData = FLExData()

        # Parse the source language data, if present.
        sourceEl = root.find("SourceData")

        if sourceEl is not None:

            flexData.sourceData = XMLFLExDataBackEndProvider._parseLanguageData(sourceEl, SourceFLExData)

        # Parse the target language data, if present.
        targetEl = root.find("TargetData")

        if targetEl is not None:

            flexData.targetData = XMLFLExDataBackEndProvider._parseLanguageData(targetEl, TargetFLExData)

        # Append the Greek variable values to both languages' features.
        flexData.sourceData.addVariableValuesToFeatures()
        flexData.targetData.addVariableValuesToFeatures()
        return flexData

    # Parse a language data element (categories and features) into the given data class.
    @staticmethod
    def _parseLanguageData(langEl, langClass):

        langData = langClass()
        langData.name = langEl.get("name", "")

        # Parse the categories, if present.
        categoriesEl = langEl.find("Categories")

        if categoriesEl is not None:

            for catEl in categoriesEl.findall("FLExCategory"):

                langData.categories.append(XMLFLExDataBackEndProvider._parseCategory(catEl))

        # Parse the features, if present.
        featuresEl = langEl.find("Features")

        if featuresEl is not None:

            for featEl in featuresEl.findall("FLExFeature"):

                langData.features.append(XMLFLExDataBackEndProvider._parseFeature(featEl))

        return langData

    # Parse a FLExCategory element, including its valid features.
    @staticmethod
    def _parseCategory(catEl) -> FLExCategory:

        cat = FLExCategory(abbreviation=catEl.get("abbr", ""))
        validFeaturesEl = catEl.find("ValidFeatures")

        if validFeaturesEl is not None:

            for vfEl in validFeaturesEl.findall("ValidFeature"):

                cat.validFeatures.append(ValidFeature(name=vfEl.get("name", ""), validFeatureType=vfEl.get("type", "")))

        return cat

    # Parse a FLExFeature element, including its values.
    @staticmethod
    def _parseFeature(featEl) -> FLExFeature:

        feat = FLExFeature(name=featEl.get("name", ""))
        valuesEl = featEl.find("Values")

        if valuesEl is not None:

            for valEl in valuesEl.findall("FLExFeatureValue"):

                feat.values.append(FLExFeatureValue(abbreviation=valEl.get("abbr", "")))

        feat.__post_init__()
        return feat
