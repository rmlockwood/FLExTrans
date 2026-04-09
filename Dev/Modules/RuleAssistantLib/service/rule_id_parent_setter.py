"""RuleIdentifierAndParentSetter service"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flex_trans_rule import FLExTransRule


class RuleIdentifierAndParentSetter:
    """Assigns sequential identifiers and parent back-pointers to all constituents.

    CRITICAL: Identifiers are assigned in depth-first order:
    - Source phrase and all its children first
    - Then target phrase and all its children
    - This ensures source phrase IDs are always < target phrase ID (used by ConstituentFinder)

    The identifier sequence for a rule is:
    1. Source phrase
    2. Source word 1, category, features, affixes+features
    3. Source word 2, category, features, affixes+features
    4. ...
    5. Target phrase
    6. Target word 1, category, features, affixes+features
    7. ...
    """

    def set_identifiers_and_parents(self, rule: "FLExTransRule") -> None:
        """Assign identifiers and parent pointers to all nodes in the rule.

        Args:
            rule: The FLExTransRule to process
        """
        self.counter = 0

        # Set source phrase and all its children
        self._set_phrase_identifiers(rule.source, rule)

        # Set target phrase and all its children
        self._set_phrase_identifiers(rule.target, rule)

        # Set phrase parents
        rule.source.parent = rule
        rule.target.parent = rule

    def _set_phrase_identifiers(self, phrase, rule) -> None:
        """Recursively assign identifiers to a phrase and all children.

        Args:
            phrase: The Phrase to process
            rule: The parent FLExTransRule
        """
        # Assign phrase identifier
        self.counter += 1
        phrase.identifier = self.counter
        phrase.parent = rule

        # Assign identifiers to words and their content
        for word in phrase.words:
            self.counter += 1
            word.identifier = self.counter
            word.parent = phrase

            # Category constituent
            if word.category_constituent:
                self.counter += 1
                word.category_constituent.identifier = self.counter
                word.category_constituent.parent = word

            # Features directly on word
            for feature in word.features:
                self.counter += 1
                feature.identifier = self.counter
                feature.parent = word

            # Affixes and their features
            for affix in word.affixes:
                self.counter += 1
                affix.identifier = self.counter
                affix.parent = word

                for feature in affix.features:
                    self.counter += 1
                    feature.identifier = self.counter
                    feature.parent = affix
