"""ValidityChecker service"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.flex_trans_rule import FLExTransRule


class ValidityChecker:
    """Validates rules before processing.

    Three validation checks:
    1. All source words must have categories
    2. Target must have at least one feature (on any word or affix)
    3. Target must have exactly one head word (when >1 word exists)
    """

    @staticmethod
    def check_source_words_have_categories(rule: "FLExTransRule") -> tuple[bool, str]:
        """Validate that all source words have categories.

        Args:
            rule: The rule to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        for word in rule.source.words:
            if not word.word_category:
                return False, f"Source word {word.word_id or '?'} is missing a category"
        return True, ""

    @staticmethod
    def check_target_has_feature(rule: "FLExTransRule") -> tuple[bool, str]:
        """Validate that target has at least one feature.

        Args:
            rule: The rule to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        for word in rule.target.words:
            if word.features:
                return True, ""
            for affix in word.affixes:
                if affix.features:
                    return True, ""
        return False, "Target phrase must have at least one feature"

    @staticmethod
    def check_target_word_marked_as_head(rule: "FLExTransRule") -> tuple[bool, str]:
        """Validate that target has exactly one head word (when >1 word).

        Args:
            rule: The rule to check

        Returns:
            Tuple of (is_valid, error_message)
        """
        from ..model.enums import HeadValue

        words = rule.target.words
        if len(words) <= 1:
            return True, ""

        head_count = sum(1 for w in words if w.head == HeadValue.yes)
        if head_count == 1:
            return True, ""
        elif head_count == 0:
            return False, "Target phrase must have one word marked as head"
        else:
            return False, f"Target phrase has {head_count} head words; only one allowed"

    @staticmethod
    def validate_rule(rule: "FLExTransRule") -> tuple[bool, str]:
        """Run all validation checks on a rule.

        Args:
            rule: The rule to validate

        Returns:
            Tuple of (is_valid, error_message). error_message is empty if valid.
        """
        checks = [
            ValidityChecker.check_source_words_have_categories,
            ValidityChecker.check_target_has_feature,
            ValidityChecker.check_target_word_marked_as_head,
        ]

        for check in checks:
            is_valid, error_msg = check(rule)
            if not is_valid:
                return False, error_msg

        return True, ""
