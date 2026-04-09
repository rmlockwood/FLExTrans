"""FLEx feature and feature value classes"""

from dataclasses import dataclass, field
from typing import Optional
import constants


@dataclass
class FLExFeatureValue:
    """A value for a FLEx feature.

    Attributes:
        abbreviation: Value abbreviation (e.g., "sg", "pl", "α")
        feature: Back-reference to parent FLExFeature (set post-load)
    """

    abbreviation: str = ""
    feature: Optional["FLExFeature"] = None

    @staticmethod
    def is_greek(abbreviation: str) -> bool:
        """Check if a value is a Greek variable.

        Args:
            abbreviation: The abbreviation to check

        Returns:
            True if the abbreviation is a Greek letter variable
        """
        return abbreviation in constants.GREEK_VARIABLES


@dataclass
class FLExFeature:
    """A FLEx feature with its possible values.

    Attributes:
        name: Feature name (e.g., "gender", "number")
        values: List of FLExFeatureValue objects
    """

    name: str = ""
    values: list[FLExFeatureValue] = field(default_factory=list)

    def __post_init__(self):
        # Set back-references from values to this feature
        for value in self.values:
            value.feature = self

    def duplicate(self) -> "FLExFeature":
        """Create a copy of this feature with its values.

        Returns:
            A new FLExFeature
        """
        new_feature = FLExFeature(name=self.name)
        new_feature.values = [
            FLExFeatureValue(abbreviation=v.abbreviation) for v in self.values
        ]
        new_feature.__post_init__()
        return new_feature
