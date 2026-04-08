"""ConstituentFinder service"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..model.rule_constituent import RuleConstituent
    from ..model.flex_trans_rule import FLExTransRule


class ConstituentFinder:
    """Finds a RuleConstituent by its identifier in a rule.

    Uses the fact that source phrase IDs are always < target phrase ID
    to efficiently route the search to the correct half of the tree.
    """

    def find_constituent(self, rule: "FLExTransRule", identifier: int) -> Optional["RuleConstituent"]:
        """Find a constituent by identifier.

        Args:
            rule: The FLExTransRule to search in
            identifier: The identifier to find

        Returns:
            The RuleConstituent with the given identifier, or None
        """
        # Use target phrase's identifier as the split point
        target_phrase_id = rule.target.identifier

        if identifier < target_phrase_id:
            # Search in source phrase
            return rule.source.find_constituent(identifier)
        else:
            # Search in target phrase
            return rule.target.find_constituent(identifier)
