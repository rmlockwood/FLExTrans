"""FLExTransRule model class"""

from dataclasses import dataclass, field
from .rule_constituent import RuleConstituent
from .enums import PermutationsValue
from .source_target import Source, Target


@dataclass
class FLExTransRule(RuleConstituent):
    """A single transfer rule with source and target patterns.

    Attributes:
        name: Rule name (required)
        description: Rule description
        create_permutations: Whether to generate permutations
        source: Source phrase
        target: Target phrase
    """

    name: str = ""
    description: str = ""
    create_permutations: PermutationsValue = PermutationsValue.with_head
    source: Source = field(default_factory=Source)
    target: Target = field(default_factory=Target)

    def __post_init__(self):
        super().__init__()

    def find_constituent(self, identifier: int) -> "RuleConstituent | None":
        """Recursively search for a constituent by identifier.

        Args:
            identifier: The identifier to search for

        Returns:
            The matching RuleConstituent or None
        """
        if self.identifier == identifier:
            return self

        # Check source phrase
        result = self.source.find_constituent(identifier)
        if result:
            return result

        # Check target phrase
        result = self.target.find_constituent(identifier)
        if result:
            return result

        return None

    def duplicate(self) -> "FLExTransRule":
        """Create a deep copy of this rule.

        Returns:
            A new FLExTransRule with duplicate source and target
        """
        new_rule = FLExTransRule(
            name=self.name + " (duplicate)",
            description=self.description,
            create_permutations=self.create_permutations,
        )

        # Deep copy source phrase
        new_rule.source = Source()
        new_rule.source.phrase_type = self.source.phrase_type
        new_rule.source.words = [w.duplicate() for w in self.source.words]
        for word in new_rule.source.words:
            word.parent = new_rule.source
        new_rule.source.parent = new_rule

        # Deep copy target phrase
        new_rule.target = Target()
        new_rule.target.phrase_type = self.target.phrase_type
        new_rule.target.words = [w.duplicate() for w in self.target.words]
        for word in new_rule.target.words:
            word.parent = new_rule.target
        new_rule.target.parent = new_rule

        return new_rule
