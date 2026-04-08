"""Word model class"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from .rule_constituent import RuleConstituent
from .category import Category
from .enums import AffixType, HeadValue

if TYPE_CHECKING:
    from .feature import Feature
    from .affix import Affix
    from .phrase import Phrase


@dataclass
class Word(RuleConstituent):
    """A word slot in a phrase.

    Attributes:
        word_id: User-visible word number (string: "1", "2", etc.)
        word_category: Category abbreviation (e.g., "n", "v")
        head: HeadValue.yes if marked as head, else HeadValue.no
        features: List of Feature objects directly on the word
        affixes: List of Affix objects (prefix or suffix)
        category_constituent: Runtime Category object (created post-load)
    """

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
        """Generate HTML for this word in the tree.

        Returns:
            HTML <li> element with word table and optional children
        """
        def _t(s: str) -> str:
            """Translate string with fallback for testing."""
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistant", s)
            except ImportError:
                return {"word": "word", "head": "head"}.get(s, s)

        head_class = "headword" if self.head == HeadValue.yes else ""

        html = "<li>"
        html += '<table class="tf-nc">\n'

        # Row 1: word label with optional (head) marker and index
        html += "<tr>\n<td align=\"center\">"
        html += self.produce_span(head_class, "w")
        html += _t("word")

        if self.head == HeadValue.yes:
            html += (
                '(<span style="font-style:italic; font-size:smaller">'
                + _t("head")
                + "</span>)"
            )

        if self.word_id:
            html += f'<span class="index">{self.word_id}</span>\n'

        html += "</span>\n</td>\n</tr>\n"

        # Row 2: category (conditional)
        category_html = self._produce_category_html()
        if category_html:
            html += "<tr>\n<td align=\"center\">" + category_html + "</td>\n</tr>\n"

        html += "</table>\n"

        # Children: prefix affixes, features, suffix affixes
        if self.affixes or self.features:
            html += "<ul>\n"

            # Prefix affixes
            for affix in (a for a in self.affixes if a.affix_type == AffixType.prefix):
                html += affix.produce_html(self.head == HeadValue.yes)

            # Features
            if self.features:
                html += self._produce_features_html()

            # Suffix affixes
            for affix in (a for a in self.affixes if a.affix_type == AffixType.suffix):
                html += affix.produce_html(self.head == HeadValue.yes)

            html += "</ul>\n"

        html += "</li>"
        return html

    def _produce_category_html(self) -> str:
        """Generate HTML for this word's category.

        Returns:
            HTML for category span or empty string if no category
        """
        if not self.category_constituent or not self.category_constituent.name:
            return ""
        return self.category_constituent.produce_html()

    def _produce_features_html(self) -> str:
        """Generate HTML for all features on this word.

        Features are rendered as a single <li><table> with one row per feature.

        Returns:
            HTML <li><table>...<tr>...<feature>...</tr></table></li>
        """
        html = "<li><table class=\"tf-nc\">\n"
        for feature in self.features:
            html += "<tr>\n<td align=\"left\">"
            html += feature.produce_html(self.head == HeadValue.yes)
            html += "</td>\n</tr>\n"
        html += "</table>\n</li>\n"
        return html

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        """Recursively search for a constituent by identifier.

        Args:
            identifier: The identifier to search for

        Returns:
            The matching RuleConstituent or None
        """
        if self.identifier == identifier:
            return self

        # Check category
        if self.category_constituent and self.category_constituent.find_constituent(identifier):
            return self.category_constituent.find_constituent(identifier)

        # Check features
        for feature in self.features:
            result = feature.find_constituent(identifier)
            if result:
                return result

        # Check affixes and their features
        for affix in self.affixes:
            result = affix.find_constituent(identifier)
            if result:
                return result

        return None

    def get_id_of_newly_added_word(self, phrase_words: list["Word"]) -> str:
        """Find the lowest positive integer string not already in use.

        Returns:
            A word ID string (e.g., "1", "2", "3")
        """
        used_ids = {int(w.word_id) for w in phrase_words if w.word_id.isdigit()}
        next_id = 1
        while next_id in used_ids:
            next_id += 1
        return str(next_id)

    def duplicate(self) -> "Word":
        """Create a deep copy of this word with all features and affixes.

        Returns:
            A new Word with duplicate content
        """
        new_word = Word(
            word_id=self.word_id,
            word_category=self.word_category,
            head=self.head,
        )
        new_word.category_constituent = Category(name=self.word_category)
        new_word.features = [f.duplicate() for f in self.features]
        for feature in new_word.features:
            feature.parent = new_word
        new_word.affixes = [a.duplicate() for a in self.affixes]
        for affix in new_word.affixes:
            affix.parent = new_word
        return new_word

    def get_category_of_word_or_corresponding_source_word(self) -> Optional[Category]:
        """Get category, trying parent source word if own is empty.

        Used for target words that inherit source word's category display.

        Returns:
            A Category object or None
        """
        if self.category_constituent and self.category_constituent.name:
            return self.category_constituent

        # Try to find corresponding source word
        if not self.parent:
            return None

        phrase = self.parent
        if not hasattr(phrase, "phrase_type"):
            return None

        # Find the rule
        rule = phrase.parent
        if not rule:
            return None

        # Get corresponding source phrase
        from .enums import PhraseType

        if hasattr(phrase, "phrase_type") and phrase.phrase_type == PhraseType.target:
            source_phrase = getattr(rule, "source", None)
            if source_phrase:
                source_phrase = getattr(source_phrase, "phrase", None)
        else:
            return None

        if not source_phrase:
            return None

        # Find source word with same ID
        for source_word in getattr(source_phrase, "words", []):
            if source_word.word_id == self.word_id:
                return source_word.category_constituent

        return None

    def get_all_features_in_word(self) -> list["Feature"]:
        """Get all features on this word and all its affixes.

        Returns:
            Combined list of Feature objects
        """
        features = list(self.features)
        for affix in self.affixes:
            features.extend(affix.features)
        return features
