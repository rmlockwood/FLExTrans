"""Phrase model class"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .rule_constituent import RuleConstituent
from .enums import PhraseType

if TYPE_CHECKING:
    from .word import Word
    from flexmodel.flex_feature import FLExFeature


@dataclass
class Phrase(RuleConstituent):
    """A phrase (source or target) containing words.

    Attributes:
        words: List of Word objects in this phrase
        phrase_type: PhraseType.source or PhraseType.target (runtime-only)
    """

    words: list["Word"] = field(default_factory=list)
    phrase_type: PhraseType = PhraseType.source

    def __post_init__(self):
        super().__init__()

    def produce_html(self) -> str:
        """Generate HTML for this phrase.

        Returns:
            HTML <li> element with phrase label and child words
        """

        def _t(s: str) -> str:
            """Translate string with fallback for testing."""
            try:
                from PyQt6.QtCore import QCoreApplication
                return QCoreApplication.translate("RuleAssistant", s)
            except ImportError:
                return {"phrase": "phrase", "src": "src", "tgt": "tgt"}.get(s, s)

        lang = _t("src") if self.phrase_type == PhraseType.source else _t("tgt")

        html = "<li>"
        html += self.produce_span("tf-nc", "p")
        html += _t("phrase")
        html += f'<span class="language">{lang}</span></span>\n'

        html += "<ul>"
        for word in self.words:
            html += word.produce_html()
        html += "</ul></li>"

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

        for word in self.words:
            result = word.find_constituent(identifier)
            if result:
                return result

        return None

    def insert_new_word_at(self, index: int) -> "Word":
        """Insert a new blank word at the given index.

        Args:
            index: Position to insert at

        Returns:
            The newly created Word
        """
        from .word import Word

        new_word = Word()
        new_word.word_id = new_word.get_id_of_newly_added_word(self.words)
        self.words.insert(index, new_word)
        new_word.parent = self
        return new_word

    def get_id_of_newly_added_word(self) -> str:
        """Find the lowest positive integer string not already in use.

        Returns:
            A word ID string (e.g., "1", "2", "3")
        """
        used_ids = {int(w.word_id) for w in self.words if w.word_id.isdigit()}
        next_id = 1
        while next_id in used_ids:
            next_id += 1
        return str(next_id)

    def swap_position_of_words(self, i: int, j: int) -> None:
        """Swap the positions of two words.

        Args:
            i: Index of first word
            j: Index of second word
        """
        if 0 <= i < len(self.words) and 0 <= j < len(self.words):
            self.words[i], self.words[j] = self.words[j], self.words[i]

    def change_id_of_word(self, word_index: int, old_id: str, new_id: str) -> None:
        """Change a word's ID, swapping if new ID is already in use.

        Args:
            word_index: Index of word to change
            old_id: The old ID (for reference)
            new_id: The new ID to assign
        """
        if not (0 <= word_index < len(self.words)):
            return

        # Find if new_id is already in use
        for other_word in self.words:
            if other_word.word_id == new_id:
                other_word.word_id = old_id
                break

        self.words[word_index].word_id = new_id

    def mark_word_as_head(self, word: "Word") -> None:
        """Mark a word as head, unmark all others in this phrase.

        Args:
            word: The word to mark as head
        """
        from .enums import HeadValue

        for w in self.words:
            w.head = HeadValue.yes if w is word else HeadValue.no

    def get_category_of_word_with_id(self, word_id: str) -> str:
        """Find a word's category by word ID.

        Used to look up a corresponding source word's category.

        Args:
            word_id: The word ID to search for

        Returns:
            Category abbreviation or empty string
        """
        for word in self.words:
            if word.word_id == word_id:
                return word.word_category
        return ""

    def get_features_in_use(self) -> list["FLExFeature"]:
        """Get deduplicated list of FLEx features used in this phrase.

        Returns:
            List of FLExFeature objects
        """
        feature_names = set()
        features = []

        for word in self.words:
            for feature in word.get_all_features_in_word():
                # Skip empty/blank features
                if not feature.label or (not feature.match and not feature.value):
                    continue
                if feature.label not in feature_names:
                    feature_names.add(feature.label)

        # This method is used by the UI to get FLEx feature metadata
        # The actual FLEx features are retrieved separately
        return []

    def get_features_in_use_for_category(
        self, all_flex_features: list["FLExFeature"], category_abbr: str
    ) -> list["FLExFeature"]:
        """Get FLEx features valid for a category and used in this phrase.

        Args:
            all_flex_features: All available FLEx features
            category_abbr: Category abbreviation to filter by

        Returns:
            List of FLExFeature objects valid for the category
        """
        # Get features used in this phrase
        phrase_feature_labels = set()
        for word in self.words:
            if word.word_category == category_abbr:
                for feature in word.get_all_features_in_word():
                    if feature.label:
                        phrase_feature_labels.add(feature.label)

        # Filter FLEx features to those used
        matching_features = [
            f for f in all_flex_features if f.name in phrase_feature_labels
        ]
        return matching_features
