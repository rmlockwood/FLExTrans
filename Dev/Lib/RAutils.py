"""RuleAssistant utilities: combined model, flexmodel, and service classes."""

# ---- External imports ----
import xml.etree.ElementTree as ET
import io
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from PyQt6.QtCore import QSettings, QObject, pyqtSlot, QCoreApplication

_translate = QCoreApplication.translate


# ============================================================
# Constants
# ============================================================

VERSION_NUMBER = "1.6.0"
GREEK_VARIABLES = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "μ", "ν"]
DISJOINT_NUMBER = "number"
DISJOINT_PL = "pl"
DISJOINT_SG = "sg"


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

    @staticmethod
    def is_greek(abbreviation: str) -> bool:
        return abbreviation in GREEK_VARIABLES


@dataclass
class FLExFeature:
    name: str = ""
    values: list[FLExFeatureValue] = field(default_factory=list)

    def __post_init__(self):
        for value in self.values:
            value.feature = self

    def duplicate(self) -> "FLExFeature":
        new_feature = FLExFeature(name=self.name)
        new_feature.values = [FLExFeatureValue(abbreviation=v.abbreviation) for v in self.values]
        new_feature.__post_init__()
        return new_feature


@dataclass
class ValidFeature:
    name: str = ""
    valid_feature_type: str = ""


@dataclass
class FLExCategory:
    abbreviation: str = ""
    valid_features: list[ValidFeature] = field(default_factory=list)


@dataclass
class FLExDataBase:
    name: str = ""
    categories: list[FLExCategory] = field(default_factory=list)
    features: list[FLExFeature] = field(default_factory=list)
    features_without_variables: list[FLExFeature] = field(default_factory=list)
    max_variables: int = 4

    def __post_init__(self):
        pass

    def add_variable_values_to_features(self) -> None:
        self.features_without_variables = [f.duplicate() for f in self.features]
        for feature in self.features:
            for i in range(min(self.max_variables, len(GREEK_VARIABLES))):
                feature.values.append(FLExFeatureValue(abbreviation=GREEK_VARIABLES[i]))

    def get_flex_categories_for_phrase(self) -> list[FLExCategory]:
        return self.categories

    def get_features_for_category(self, category_abbr: str) -> list[FLExFeature]:
        for category in self.categories:
            if category.abbreviation == category_abbr:
                valid_names = {vf.name for vf in category.valid_features}
                return [f for f in self.features if f.name in valid_names]
        return []


@dataclass
class SourceFLExData(FLExDataBase):
    pass


@dataclass
class TargetFLExData(FLExDataBase):
    pass


@dataclass
class FLExData:
    source_data: SourceFLExData = field(default_factory=SourceFLExData)
    target_data: TargetFLExData = field(default_factory=TargetFLExData)

    def get_flex_categories_for_phrase(self, phrase_type) -> list[FLExCategory]:
        if phrase_type == PhraseType.source:
            return self.source_data.get_flex_categories_for_phrase()
        return self.target_data.get_flex_categories_for_phrase()

    def get_features_in_phrase_for_category(self, phrase_type, category_abbr: str):
        if phrase_type == PhraseType.source:
            return self.source_data.get_features_for_category(category_abbr)
        return self.target_data.get_features_for_category(category_abbr)


# ============================================================
# Rule constituent base
# ============================================================

class RuleConstituent:
    def __init__(self):
        self.identifier: int = 0
        self.parent: Optional["RuleConstituent"] = None

    def produce_span(self, css_class: str, type_code: str) -> str:
        return (
            f'<span class="{css_class}" id="{type_code}.{self.identifier}" '
            f'onmousedown="toApp(\'{type_code}.{self.identifier}\',event)">'
        )

    def produce_to_app(self, type_code: str) -> str:
        return f'"toApp(\'{type_code}.{self.identifier}\',event)"'

    def find_constituent(self, identifier: int) -> Optional["RuleConstituent"]:
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

    def produce_html(self) -> str:
        return f'{self.produce_span("category", "c")}cat:{self.name}</span>'

    def produce_html_target(self, word_identifier: int) -> str:
        return (
            f'<span class="categorytgt" id="w.{word_identifier}" '
            f'onclick="toApp(\'w.{word_identifier}\',event)">cat:{self.name}</span>'
        )


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

    def get_match_or_value(self) -> str:
        return self.match if self.match else self.value

    def produce_html(self, is_head: bool = False) -> str:
        def _t(s: str) -> str:
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)
            except ImportError:
                return {"FeatureX": "Feature"}.get(s, s)

        css_class = "feature headfeature" if is_head else "feature"
        html = self.produce_span(css_class, "f")
        label_text = self.label if self.label else _t("FeatureX")
        html += f"{label_text}:{self.get_match_or_value()}"
        if self.ranking > 0:
            html += f'<span class="ranking feature">{self.ranking}</span>'
        if self.unmarked:
            html += f'\n<span class="unmarked feature">unmarked:{self.unmarked}</span>'
        html += "</span>"
        return html

    def duplicate(self) -> "Feature":
        return Feature(label=self.label, match=self.match, value=self.value,
                       unmarked=self.unmarked, ranking=self.ranking)

    def assign_rankings_to_sisters(self, max_rankings: int) -> None:
        if not self.parent:
            return
        sisters = getattr(self.parent, "features", [])
        used = {s.ranking for s in sisters if hasattr(s, "ranking") and s.ranking > 0}
        n = 1
        for s in sisters:
            if hasattr(s, "ranking") and s.ranking == 0:
                while n in used:
                    n += 1
                s.ranking = n
                used.add(n)

    def sister_feature_has_ranking(self) -> bool:
        if not self.parent:
            return False
        sisters = getattr(self.parent, "features", [])
        return any(hasattr(s, "ranking") and s.ranking > 0 for s in sisters if s is not self)

    def swap_ranking_of_sister_with_ranking(self, new_ranking: int, old_ranking: int) -> None:
        if not self.parent:
            return
        for s in getattr(self.parent, "features", []):
            if s is self:
                self.ranking = new_ranking
            elif hasattr(s, "ranking") and s.ranking == new_ranking:
                s.ranking = old_ranking

    def remove_rankings_from_sisters(self) -> None:
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
    affix_type: AffixType = AffixType.suffix
    features: list["Feature"] = field(default_factory=list)

    def __post_init__(self):
        super().__init__()

    def produce_html(self, is_head: bool = False) -> str:
        affix_type_str = "prefix" if self.affix_type == AffixType.prefix else "suffix"
        html = "<li>"
        html += self.produce_span("tf-nc affix", "a")
        html += affix_type_str + "</span>"
        if self.features:
            html += "<ul>\n" + self._produce_features_html(is_head) + "</ul>"
        html += "</li>\n"
        return html

    def _produce_features_html(self, is_head: bool = False) -> str:
        html = "<li><table class=\"tf-nc\">\n"
        for feature in self.features:
            html += "<tr>\n<td align=\"left\">" + feature.produce_html(is_head) + "</td>\n</tr>\n"
        html += "</table>\n</li>\n"
        return html

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        if self.identifier == identifier:
            return self
        for feature in self.features:
            r = feature.find_constituent(identifier)
            if r:
                return r
        return None

    def duplicate(self) -> "Affix":
        new_affix = Affix(affix_type=self.affix_type)
        new_affix.features = [f.duplicate() for f in self.features]
        for f in new_affix.features:
            f.parent = new_affix
        return new_affix

    def get_is_head(self) -> bool:
        if not self.parent:
            return False
        return getattr(self.parent, "head", None) and str(self.parent.head).lower() == "yes"


# ============================================================
# Phrase
# ============================================================

@dataclass
class Phrase(RuleConstituent):
    words: list["Word"] = field(default_factory=list)
    phrase_type: PhraseType = PhraseType.source

    def __post_init__(self):
        super().__init__()

    def produce_html(self) -> str:
        def _t(s: str) -> str:
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)
            except ImportError:
                return {"phrase": "phrase", "src": "src", "tgt": "tgt"}.get(s, s)

        lang = _t("src") if self.phrase_type == PhraseType.source else _t("tgt")
        html = "<li>" + self.produce_span("tf-nc", "p") + _t("phrase")
        html += f'<span class="language">{lang}</span></span>\n'
        html += "<ul>"
        for word in self.words:
            html += word.produce_html()
        html += "</ul></li>"
        return html

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        if self.identifier == identifier:
            return self
        for word in self.words:
            r = word.find_constituent(identifier)
            if r:
                return r
        return None

    def insert_new_word_at(self, index: int) -> "Word":
        new_word = Word()
        new_word.word_id = new_word.get_id_of_newly_added_word(self.words)
        self.words.insert(index, new_word)
        new_word.parent = self
        return new_word

    def get_id_of_newly_added_word(self) -> str:
        used_ids = {int(w.word_id) for w in self.words if w.word_id.isdigit()}
        next_id = 1
        while next_id in used_ids:
            next_id += 1
        return str(next_id)

    def swap_position_of_words(self, i: int, j: int) -> None:
        if 0 <= i < len(self.words) and 0 <= j < len(self.words):
            self.words[i], self.words[j] = self.words[j], self.words[i]

    def change_id_of_word(self, word_index: int, old_id: str, new_id: str) -> None:
        if not (0 <= word_index < len(self.words)):
            return
        for other_word in self.words:
            if other_word.word_id == new_id:
                other_word.word_id = old_id
                break
        self.words[word_index].word_id = new_id

    def mark_word_as_head(self, word: "Word") -> None:
        for w in self.words:
            w.head = HeadValue.yes if w is word else HeadValue.no

    def get_category_of_word_with_id(self, word_id: str) -> str:
        for word in self.words:
            if word.word_id == word_id:
                return word.word_category
        return ""

    def get_features_in_use(self) -> list:
        return []

    def get_features_in_use_for_category(self, all_flex_features, category_abbr: str) -> list:
        phrase_feature_labels = set()
        for word in self.words:
            if word.word_category == category_abbr:
                for feature in word.get_all_features_in_word():
                    if feature.label:
                        phrase_feature_labels.add(feature.label)
        return [f for f in all_flex_features if f.name in phrase_feature_labels]


# ============================================================
# Source / Target
# ============================================================

@dataclass
class Source(Phrase):
    def __post_init__(self):
        super().__post_init__()
        self.phrase_type = PhraseType.source


@dataclass
class Target(Phrase):
    def __post_init__(self):
        super().__post_init__()
        self.phrase_type = PhraseType.target


# ============================================================
# Word
# ============================================================

@dataclass
class Word(RuleConstituent):
    word_id: str = ""
    word_category: str = ""
    head: HeadValue = HeadValue.no
    features: list["Feature"] = field(default_factory=list)
    affixes: list["Affix"] = field(default_factory=list)
    category_constituent: Optional[Category] = None

    def __post_init__(self):
        super().__init__()
        if self.category_constituent is None:
            self.category_constituent = Category(name=self.word_category)

    def produce_html(self) -> str:
        def _t(s: str) -> str:
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistantLib", s)
            except ImportError:
                return {"word": "word", "head": "head"}.get(s, s)

        head_class = "headword" if self.head == HeadValue.yes else ""
        html = "<li><table class=\"tf-nc\">\n<tr>\n<td align=\"center\">"
        html += self.produce_span(head_class, "w") + _t("word")
        if self.head == HeadValue.yes:
            html += ('(<span style="font-style:italic; font-size:smaller">'
                     + _t("head") + "</span>)")
        if self.word_id:
            html += f'<span class="index">{self.word_id}</span>\n'
        html += "</span>\n</td>\n</tr>\n"
        category_html = self._produce_category_html()
        if category_html:
            html += "<tr>\n<td align=\"center\">" + category_html + "</td>\n</tr>\n"
        html += "</table>\n"
        if self.affixes or self.features:
            html += "<ul>\n"
            for affix in (a for a in self.affixes if a.affix_type == AffixType.prefix):
                html += affix.produce_html(self.head == HeadValue.yes)
            if self.features:
                html += self._produce_features_html()
            for affix in (a for a in self.affixes if a.affix_type == AffixType.suffix):
                html += affix.produce_html(self.head == HeadValue.yes)
            html += "</ul>\n"
        html += "</li>"
        return html

    def _produce_category_html(self) -> str:
        if not self.category_constituent or not self.category_constituent.name:
            return ""
        return self.category_constituent.produce_html()

    def _produce_features_html(self) -> str:
        html = "<li><table class=\"tf-nc\">\n"
        for feature in self.features:
            html += "<tr>\n<td align=\"left\">" + feature.produce_html(self.head == HeadValue.yes) + "</td>\n</tr>\n"
        html += "</table>\n</li>\n"
        return html

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        if self.identifier == identifier:
            return self
        if self.category_constituent and self.category_constituent.find_constituent(identifier):
            return self.category_constituent.find_constituent(identifier)
        for feature in self.features:
            r = feature.find_constituent(identifier)
            if r:
                return r
        for affix in self.affixes:
            r = affix.find_constituent(identifier)
            if r:
                return r
        return None

    def get_id_of_newly_added_word(self, phrase_words: list) -> str:
        used_ids = {int(w.word_id) for w in phrase_words if w.word_id.isdigit()}
        next_id = 1
        while next_id in used_ids:
            next_id += 1
        return str(next_id)

    def duplicate(self) -> "Word":
        new_word = Word(word_id=self.word_id, word_category=self.word_category, head=self.head)
        new_word.category_constituent = Category(name=self.word_category)
        new_word.features = [f.duplicate() for f in self.features]
        for f in new_word.features:
            f.parent = new_word
        new_word.affixes = [a.duplicate() for a in self.affixes]
        for a in new_word.affixes:
            a.parent = new_word
        return new_word

    def get_category_of_word_or_corresponding_source_word(self) -> Optional[Category]:
        if self.category_constituent and self.category_constituent.name:
            return self.category_constituent
        if not self.parent:
            return None
        phrase = self.parent
        if not hasattr(phrase, "phrase_type"):
            return None
        rule = phrase.parent
        if not rule:
            return None
        if phrase.phrase_type == PhraseType.target:
            source_phrase = getattr(rule, "source", None)
        else:
            return None
        if not source_phrase:
            return None
        for source_word in getattr(source_phrase, "words", []):
            if source_word.word_id == self.word_id:
                return source_word.category_constituent
        return None

    def get_all_features_in_word(self) -> list:
        features = list(self.features)
        for affix in self.affixes:
            features.extend(affix.features)
        return features


# ============================================================
# DisjointFeatureSet
# ============================================================

@dataclass
class DisjointFeatureValuePairing:
    flex_feature_name: str = ""
    co_feature_value: str = ""

    def duplicate(self) -> "DisjointFeatureValuePairing":
        return DisjointFeatureValuePairing(
            flex_feature_name=self.flex_feature_name,
            co_feature_value=self.co_feature_value,
        )


@dataclass
class DisjointFeatureSet:
    name: str = ""
    co_feature_name: str = ""
    language: PhraseType = PhraseType.target
    pairings: list[DisjointFeatureValuePairing] = field(default_factory=list)

    def remove_pairings_from(self, index: int) -> None:
        if 3 <= index <= 6 and index < len(self.pairings):
            self.pairings = self.pairings[:index]

    def has_flex_feature_in_list(self, flex_features: list) -> bool:
        feature_names = {f.name for f in flex_features if hasattr(f, "name")}
        return all(p.flex_feature_name in feature_names for p in self.pairings)

    def duplicate(self) -> "DisjointFeatureSet":
        new_set = DisjointFeatureSet(
            name=self.name, co_feature_name=self.co_feature_name, language=self.language
        )
        new_set.pairings = [p.duplicate() for p in self.pairings]
        return new_set


# ============================================================
# FLExTransRule + Generator
# ============================================================

@dataclass
class FLExTransRule(RuleConstituent):
    name: str = ""
    description: str = ""
    create_permutations: PermutationsValue = PermutationsValue.with_head
    source: Source = field(default_factory=Source)
    target: Target = field(default_factory=Target)

    def __post_init__(self):
        super().__init__()

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        if self.identifier == identifier:
            return self
        r = self.source.find_constituent(identifier)
        if r:
            return r
        return self.target.find_constituent(identifier)

    def duplicate(self) -> "FLExTransRule":
        new_rule = FLExTransRule(
            name=self.name + " (duplicate)",
            description=self.description,
            create_permutations=self.create_permutations,
        )
        new_rule.source = Source()
        new_rule.source.phrase_type = self.source.phrase_type
        new_rule.source.words = [w.duplicate() for w in self.source.words]
        for w in new_rule.source.words:
            w.parent = new_rule.source
        new_rule.source.parent = new_rule
        new_rule.target = Target()
        new_rule.target.phrase_type = self.target.phrase_type
        new_rule.target.words = [w.duplicate() for w in self.target.words]
        for w in new_rule.target.words:
            w.parent = new_rule.target
        new_rule.target.parent = new_rule
        return new_rule


@dataclass
class FLExTransRuleGenerator:
    flex_trans_rules: list[FLExTransRule] = field(default_factory=list)
    disjoint_features: list[DisjointFeatureSet] = field(default_factory=list)
    overwrite_rules: OverwriteRulesValue = OverwriteRulesValue.no

    def __post_init__(self):
        for rule in self.flex_trans_rules:
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

    def duplicate_rule(self, rule_index: int) -> None:
        if 0 <= rule_index < len(self.flex_trans_rules):
            self.flex_trans_rules.insert(rule_index, self.flex_trans_rules[rule_index].duplicate())




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

    def __init__(self):
        self._settings = QSettings("SIL", "FLExTransRuleGenerator")

    def get_last_locale_language(self, default: str = "en") -> str:
        return self._settings.value(self.LAST_LOCALE_LANGUAGE, default)

    def set_last_locale_language(self, lang_code: str) -> None:
        self._settings.setValue(self.LAST_LOCALE_LANGUAGE, lang_code)

    def get_last_selected_rule(self, default: int = 0) -> int:
        return int(self._settings.value(self.LAST_SELECTED_RULE, default))

    def set_last_selected_rule(self, index: int) -> None:
        self._settings.setValue(self.LAST_SELECTED_RULE, index)

    def get_last_selected_disjoint_feature_set(self, default: int = 0) -> int:
        return int(self._settings.value(self.LAST_SELECTED_DISJOINT_FEATURE_SET, default))

    def set_last_selected_disjoint_feature_set(self, index: int) -> None:
        self._settings.setValue(self.LAST_SELECTED_DISJOINT_FEATURE_SET, index)

    def get_window_position_x(self, default: int = 100) -> int:
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.POSITION_X}", default))

    def set_window_position_x(self, x: int) -> None:
        self._settings.setValue(f"{self.LAST_WINDOW}{self.POSITION_X}", x)

    def get_window_position_y(self, default: int = 100) -> int:
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.POSITION_Y}", default))

    def set_window_position_y(self, y: int) -> None:
        self._settings.setValue(f"{self.LAST_WINDOW}{self.POSITION_Y}", y)

    def get_window_width(self, default: int = 660) -> int:
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.WIDTH}", default))

    def set_window_width(self, width: int) -> None:
        self._settings.setValue(f"{self.LAST_WINDOW}{self.WIDTH}", width)

    def get_window_height(self, default: int = 1000) -> int:
        return int(self._settings.value(f"{self.LAST_WINDOW}{self.HEIGHT}", default))

    def set_window_height(self, height: int) -> None:
        self._settings.setValue(f"{self.LAST_WINDOW}{self.HEIGHT}", height)

    def get_window_maximized(self, default: bool = False) -> bool:
        return self._settings.value(f"{self.LAST_WINDOW}{self.MAXIMIZED}", default, type=bool)

    def set_window_maximized(self, maximized: bool) -> None:
        self._settings.setValue(f"{self.LAST_WINDOW}{self.MAXIMIZED}", maximized)

    def get_split_pane_position(self, default: float = 0.3) -> float:
        return float(self._settings.value(self.LAST_SPLIT_PANE_POSITION, default))

    def set_split_pane_position(self, position: float) -> None:
        self._settings.setValue(self.LAST_SPLIT_PANE_POSITION, position)

    def sync(self) -> None:
        self._settings.sync()


# ============================================================
# ConstituentFinder
# ============================================================

class ConstituentFinder:
    def find_constituent(self, rule: FLExTransRule, identifier: int) -> Optional[RuleConstituent]:
        target_phrase_id = rule.target.identifier
        if identifier < target_phrase_id:
            return rule.source.find_constituent(identifier)
        return rule.target.find_constituent(identifier)


# ============================================================
# RuleIdentifierAndParentSetter
# ============================================================

class RuleIdentifierAndParentSetter:
    def set_identifiers_and_parents(self, rule: FLExTransRule) -> None:
        self.counter = 0
        self._set_phrase_identifiers(rule.source, rule)
        self._set_phrase_identifiers(rule.target, rule)
        rule.source.parent = rule
        rule.target.parent = rule

    def _set_phrase_identifiers(self, phrase, rule) -> None:
        self.counter += 1
        phrase.identifier = self.counter
        phrase.parent = rule
        for word in phrase.words:
            self.counter += 1
            word.identifier = self.counter
            word.parent = phrase
            if word.category_constituent:
                self.counter += 1
                word.category_constituent.identifier = self.counter
                word.category_constituent.parent = word
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
    @staticmethod
    def check_source_words_have_categories(rule: FLExTransRule) -> tuple[bool, str]:
        for word in rule.source.words:
            if not word.word_category:
                return False, _translate("RuleAssistantLib", "One or more source words do not have a category.  Please insert a category for every source word.")
        return True, ""

    @staticmethod
    def check_target_has_feature(rule: FLExTransRule) -> tuple[bool, str]:
        for word in rule.target.words:
            if word.features:
                return True, ""
            for affix in word.affixes:
                if affix.features:
                    return True, ""
        return False, _translate("RuleAssistantLib", "No word or affix in the target has a feature.  Please insert at least one feature.")

    @staticmethod
    def check_target_word_marked_as_head(rule: FLExTransRule) -> tuple[bool, str]:
        words = rule.target.words
        if len(words) <= 1:
            return True, ""
        head_count = sum(1 for w in words if w.head == HeadValue.yes)
        if head_count == 1:
            return True, ""
        elif head_count == 0:
            return False, _translate("RuleAssistantLib", "No word has been marked as the head in the target phrase.  Please mark one word as the head.")
        return False, _translate("RuleAssistantLib", "Target phrase has {0} head words; only one allowed").format(head_count)

    @staticmethod
    def validate_rule(rule: FLExTransRule) -> tuple[bool, str]:
        for check in [
            ValidityChecker.check_source_words_have_categories,
            ValidityChecker.check_target_has_feature,
            ValidityChecker.check_target_word_marked_as_head,
        ]:
            is_valid, error_msg = check(rule)
            if not is_valid:
                return False, error_msg
        return True, ""


# ============================================================
# WebPageInteractor
# ============================================================

class WebPageInteractor(QObject):
    def __init__(self, controller):
        super().__init__()
        self._controller = controller
        self._x_coord = 0
        self._y_coord = 0

    @pyqtSlot(int)
    def setXCoord(self, x: int) -> None:
        self._x_coord = x

    @pyqtSlot(int)
    def setYCoord(self, y: int) -> None:
        self._y_coord = y

    @pyqtSlot(str)
    def setItemClickedOn(self, item: str) -> None:
        if self._controller:
            self._controller.process_item_clicked_on(item, self._x_coord, self._y_coord)

    @property
    def x_coord(self) -> int:
        return self._x_coord

    @property
    def y_coord(self) -> int:
        return self._y_coord


# ============================================================
# WebPageProducer
# ============================================================

class WebPageProducer:
    def __init__(self, css_assets_dir: str = None):
        self._treeflex_css = ""
        self._rulegen_css = ""
        self._load_css_files(css_assets_dir)

    def _load_css_files(self, css_assets_dir: str = None) -> None:
        base_dir = Path(css_assets_dir) if css_assets_dir else Path(__file__).resolve().parent
        for attr, name in [("_treeflex_css", "treeflex.css"), ("_rulegen_css", "rulegen.css")]:
            f = base_dir / name
            try:
                if f.exists():
                    setattr(self, attr, f.read_text(encoding="utf-8"))
                else:
                    # Without the CSS the tree renders as unstyled text, so make
                    # a missing file loud rather than failing silently.
                    print(f"Warning: Rule Assistant CSS not found: {f}")
            except Exception as e:
                print(f"Warning: Could not load {name}: {e}")

    def produce_web_page(self, rule: FLExTransRule) -> str:
        RuleIdentifierAndParentSetter().set_identifiers_and_parents(rule)
        html = self._html_head(rule.name)
        html += self._html_body(rule)
        html += "</body>\n</html>"
        return html

    def _html_head(self, title: str) -> str:
        return (
            '<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">\n<head>'
            f"<title>{title}</title>\n"
            '<meta charset="utf-8"/>\n<style>\n'
            f"{self._treeflex_css}\n{self._rulegen_css}\n</style>\n"
            f"{self._javascript()}\n</head>\n<body>\n"
        )

    def _html_body(self, rule: FLExTransRule) -> str:
        return (
            "<table>\n<tr>\n"
            + self._phrase_td(rule.source)
            + '<td>\n<span class="arrow"/>\n</td>\n'
            + self._phrase_td(rule.target)
            + "</tr>\n</table>\n"
        )

    def _phrase_td(self, phrase) -> str:
        return (
            '<td valign="top">\n<span class="tf-tree tf-gap-sm">\n<ul>\n'
            + phrase.produce_html()
            + "\n</ul>\n</span>\n</td>\n"
        )

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
    DOCTYPE = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE FLExTransRuleGenerator PUBLIC " -//XMLmind//DTD FLExTransRuleGenerator//EN"\n'
        '"FLExTransRuleGenerator.dtd">\n'
    )

    @staticmethod
    def load_data_from_file(filename: str) -> FLExTransRuleGenerator:
        file_path = Path(filename)
        if not file_path.exists():
            generator = FLExTransRuleGenerator()
            rule = FLExTransRule(name="Rule 1")
            rule.source = Source()
            rule.target = Target()
            word_s = Word(word_id="1")
            word_t = Word(word_id="1")
            rule.source.words = [word_s]
            rule.target.words = [word_t]
            word_s.parent = rule.source
            word_t.parent = rule.target
            generator.flex_trans_rules = [rule]
            XMLBackEndProvider.save_data_to_file(generator, filename)
            return generator

        tree = ET.parse(filename)
        root = tree.getroot()
        generator = FLExTransRuleGenerator()
        generator.overwrite_rules = OverwriteRulesValue(root.get("overwrite_rules", "yes"))

        disjoint_sets_el = root.find("DisjointFeatureSets")
        if disjoint_sets_el is not None:
            for ds_el in disjoint_sets_el.findall("DisjointFeatureSet"):
                generator.disjoint_features.append(XMLBackEndProvider._parse_disjoint_feature_set(ds_el))

        rules_el = root.find("FLExTransRules")
        if rules_el is not None:
            for rule_el in rules_el.findall("FLExTransRule"):
                rule = XMLBackEndProvider._parse_rule(rule_el)
                generator.flex_trans_rules.append(rule)
                rule.parent = generator

        for rule in generator.flex_trans_rules:
            rule.target.phrase_type = PhraseType.target
            rule.source.phrase_type = PhraseType.source
            XMLBackEndProvider._set_category_constituents_in_words(rule.source)
            XMLBackEndProvider._set_category_constituents_in_words(rule.target)

        return generator

    @staticmethod
    def save_data_to_file(generator: FLExTransRuleGenerator, filename: str) -> None:
        root = ET.Element("FLExTransRuleGenerator")
        root.set("overwrite_rules", generator.overwrite_rules.value)
        if generator.disjoint_features:
            disjoint_sets_el = ET.SubElement(root, "DisjointFeatureSets")
            for ds in generator.disjoint_features:
                XMLBackEndProvider._create_disjoint_feature_set_element(ds, disjoint_sets_el)
        rules_el = ET.SubElement(root, "FLExTransRules")
        for rule in generator.flex_trans_rules:
            XMLBackEndProvider._create_rule_element(rule, rules_el)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        buf = io.StringIO()
        tree.write(buf, encoding="unicode", xml_declaration=False)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(XMLBackEndProvider.DOCTYPE)
            f.write(buf.getvalue())

    @staticmethod
    def _parse_rule(rule_el) -> FLExTransRule:
        desc_el = rule_el.find("Description")
        description = desc_el.text if desc_el is not None and desc_el.text else ""
        rule = FLExTransRule(
            name=rule_el.get("name", ""),
            description=description,
            create_permutations=PermutationsValue(rule_el.get("create_permutations", "with_head")),
        )
        source_el = rule_el.find("Source")
        if source_el is not None:
            phrase_el = source_el.find("Phrase")
            if phrase_el is not None:
                parsed = XMLBackEndProvider._parse_phrase(phrase_el, PhraseType.source)
                rule.source.words = parsed.words
                for w in rule.source.words:
                    w.parent = rule.source
        target_el = rule_el.find("Target")
        if target_el is not None:
            phrase_el = target_el.find("Phrase")
            if phrase_el is not None:
                parsed = XMLBackEndProvider._parse_phrase(phrase_el, PhraseType.target)
                rule.target.words = parsed.words
                for w in rule.target.words:
                    w.parent = rule.target
        return rule

    @staticmethod
    def _parse_phrase(phrase_el, phrase_type: PhraseType) -> Phrase:
        phrase = Phrase(phrase_type=phrase_type)
        words_el = phrase_el.find("Words")
        if words_el is not None:
            for word_el in words_el.findall("Word"):
                word = XMLBackEndProvider._parse_word(word_el)
                phrase.words.append(word)
                word.parent = phrase
        return phrase

    @staticmethod
    def _parse_word(word_el) -> Word:
        word = Word(
            word_id=word_el.get("id", ""),
            word_category=word_el.get("category", ""),
            head=HeadValue(word_el.get("head", "no")),
        )
        features_el = word_el.find("Features")
        if features_el is not None:
            for feature_el in features_el.findall("Feature"):
                feature = XMLBackEndProvider._parse_feature(feature_el)
                word.features.append(feature)
                feature.parent = word
        affixes_el = word_el.find("Affixes")
        if affixes_el is not None:
            for affix_el in affixes_el.findall("Affix"):
                affix = XMLBackEndProvider._parse_affix(affix_el)
                word.affixes.append(affix)
                affix.parent = word
        return word

    @staticmethod
    def _parse_feature(feature_el) -> Feature:
        return Feature(
            label=feature_el.get("label", ""),
            match=feature_el.get("match", ""),
            value=feature_el.get("value", ""),
            unmarked=feature_el.get("unmarked_default", ""),
            ranking=int(feature_el.get("ranking", "0")),
        )

    @staticmethod
    def _parse_affix(affix_el) -> Affix:
        affix = Affix(affix_type=AffixType(affix_el.get("type", "suffix")))
        features_el = affix_el.find("Features")
        if features_el is not None:
            for feature_el in features_el.findall("Feature"):
                feature = XMLBackEndProvider._parse_feature(feature_el)
                affix.features.append(feature)
                feature.parent = affix
        return affix

    @staticmethod
    def _parse_disjoint_feature_set(ds_el) -> DisjointFeatureSet:
        ds = DisjointFeatureSet(
            name=ds_el.get("disjoint_name", ""),
            co_feature_name=ds_el.get("co_feature_name", ""),
            language=PhraseType(ds_el.get("language", "target")),
        )
        pairings_el = ds_el.find("DisjointFeatureValuePairings")
        if pairings_el is not None:
            for pairing_el in pairings_el.findall("DisjointFeatureValuePairing"):
                ds.pairings.append(DisjointFeatureValuePairing(
                    flex_feature_name=pairing_el.get("flex_feature_name", ""),
                    co_feature_value=pairing_el.get("co_feature_value", ""),
                ))
        return ds

    @staticmethod
    def _create_rule_element(rule: FLExTransRule, parent_el) -> None:
        rule_el = ET.SubElement(parent_el, "FLExTransRule")
        rule_el.set("name", rule.name)
        rule_el.set("create_permutations", rule.create_permutations.value)
        ET.SubElement(rule_el, "Description").text = rule.description or ""
        XMLBackEndProvider._create_phrase_element(rule.source, ET.SubElement(rule_el, "Source"))
        XMLBackEndProvider._create_phrase_element(rule.target, ET.SubElement(rule_el, "Target"))

    @staticmethod
    def _create_phrase_element(phrase: Phrase, parent_el) -> None:
        phrase_el = ET.SubElement(parent_el, "Phrase")
        if phrase.words:
            words_el = ET.SubElement(phrase_el, "Words")
            for word in phrase.words:
                XMLBackEndProvider._create_word_element(word, words_el)

    @staticmethod
    def _create_word_element(word: Word, parent_el) -> None:
        word_el = ET.SubElement(parent_el, "Word")
        word_el.set("id", word.word_id)
        word_el.set("category", word.word_category)
        word_el.set("head", word.head.value)
        if word.features:
            features_el = ET.SubElement(word_el, "Features")
            for f in word.features:
                XMLBackEndProvider._create_feature_element(f, features_el)
        if word.affixes:
            affixes_el = ET.SubElement(word_el, "Affixes")
            for a in word.affixes:
                XMLBackEndProvider._create_affix_element(a, affixes_el)

    @staticmethod
    def _create_feature_element(feature: Feature, parent_el) -> None:
        el = ET.SubElement(parent_el, "Feature")
        el.set("label", feature.label)
        el.set("match", feature.match)
        el.set("value", feature.value)
        el.set("unmarked_default", feature.unmarked)
        el.set("ranking", str(feature.ranking))

    @staticmethod
    def _create_affix_element(affix: Affix, parent_el) -> None:
        affix_el = ET.SubElement(parent_el, "Affix")
        affix_el.set("type", affix.affix_type.value)
        if affix.features:
            features_el = ET.SubElement(affix_el, "Features")
            for f in affix.features:
                XMLBackEndProvider._create_feature_element(f, features_el)

    @staticmethod
    def _create_disjoint_feature_set_element(ds: DisjointFeatureSet, parent_el) -> None:
        ds_el = ET.SubElement(parent_el, "DisjointFeatureSet")
        ds_el.set("language", ds.language.value)
        ds_el.set("disjoint_name", ds.name)
        ds_el.set("co_feature_name", ds.co_feature_name)
        if ds.pairings:
            pairings_el = ET.SubElement(ds_el, "DisjointFeatureValuePairings")
            for p in ds.pairings:
                pairing_el = ET.SubElement(pairings_el, "DisjointFeatureValuePairing")
                pairing_el.set("flex_feature_name", p.flex_feature_name)
                pairing_el.set("co_feature_value", p.co_feature_value)

    @staticmethod
    def _set_category_constituents_in_words(phrase: Phrase) -> None:
        for word in phrase.words:
            word.category_constituent = Category(name=word.word_category)
            word.category_constituent.parent = word


# ============================================================
# XMLFLExDataBackEndProvider
# ============================================================

class XMLFLExDataBackEndProvider:
    @staticmethod
    def load_data_from_file(filename: str) -> FLExData:
        tree = ET.parse(filename)
        root = tree.getroot()
        flex_data = FLExData()
        source_el = root.find("SourceData")
        if source_el is not None:
            flex_data.source_data = XMLFLExDataBackEndProvider._parse_language_data(source_el, SourceFLExData)
        target_el = root.find("TargetData")
        if target_el is not None:
            flex_data.target_data = XMLFLExDataBackEndProvider._parse_language_data(target_el, TargetFLExData)
        flex_data.source_data.add_variable_values_to_features()
        flex_data.target_data.add_variable_values_to_features()
        return flex_data

    @staticmethod
    def _parse_language_data(lang_el, lang_class):
        lang_data = lang_class()
        lang_data.name = lang_el.get("name", "")
        categories_el = lang_el.find("Categories")
        if categories_el is not None:
            for cat_el in categories_el.findall("FLExCategory"):
                lang_data.categories.append(XMLFLExDataBackEndProvider._parse_category(cat_el))
        features_el = lang_el.find("Features")
        if features_el is not None:
            for feat_el in features_el.findall("FLExFeature"):
                lang_data.features.append(XMLFLExDataBackEndProvider._parse_feature(feat_el))
        return lang_data

    @staticmethod
    def _parse_category(cat_el) -> FLExCategory:
        cat = FLExCategory(abbreviation=cat_el.get("abbr", ""))
        valid_features_el = cat_el.find("ValidFeatures")
        if valid_features_el is not None:
            for vf_el in valid_features_el.findall("ValidFeature"):
                cat.valid_features.append(ValidFeature(
                    name=vf_el.get("name", ""),
                    valid_feature_type=vf_el.get("type", ""),
                ))
        return cat

    @staticmethod
    def _parse_feature(feat_el) -> FLExFeature:
        feat = FLExFeature(name=feat_el.get("name", ""))
        values_el = feat_el.find("Values")
        if values_el is not None:
            for val_el in values_el.findall("FLExFeatureValue"):
                feat.values.append(FLExFeatureValue(abbreviation=val_el.get("abbr", "")))
        feat.__post_init__()
        return feat
