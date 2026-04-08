"""FLExTransRuleGenerator root model class"""

from dataclasses import dataclass, field
from .flex_trans_rule import FLExTransRule
from .enums import OverwriteRulesValue


@dataclass
class FLExTransRuleGenerator:
    """Root object for the rule file (not a RuleConstituent).

    This is the root element when serialized to XML.

    Attributes:
        flex_trans_rules: List of all rules
        disjoint_features: List of disjoint feature sets
        overwrite_rules: Whether to overwrite rules on load
    """

    flex_trans_rules: list[FLExTransRule] = field(default_factory=list)
    disjoint_features: list["DisjointFeatureSet"] = field(default_factory=list)
    overwrite_rules: OverwriteRulesValue = OverwriteRulesValue.no

    def __post_init__(self):
        # Set parent pointers
        for rule in self.flex_trans_rules:
            rule.source.parent = rule
            rule.target.parent = rule
            for word in rule.source.words:
                word.parent = rule.source
                for feature in word.features:
                    feature.parent = word
                for affix in word.affixes:
                    affix.parent = word
                    for feature in affix.features:
                        feature.parent = affix
            for word in rule.target.words:
                word.parent = rule.target
                for feature in word.features:
                    feature.parent = word
                for affix in word.affixes:
                    affix.parent = word
                    for feature in affix.features:
                        feature.parent = affix

    def duplicate_rule(self, rule_index: int) -> None:
        """Duplicate a rule at the given index.

        Args:
            rule_index: Index of the rule to duplicate
        """
        if 0 <= rule_index < len(self.flex_trans_rules):
            duplicated = self.flex_trans_rules[rule_index].duplicate()
            self.flex_trans_rules.insert(rule_index, duplicated)
