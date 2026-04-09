"""FLEx category classes"""

from dataclasses import dataclass, field
from flex_feature import FLExFeature


@dataclass
class ValidFeature:
    """A feature valid for a category.

    Attributes:
        name: Feature name (e.g., "gender")
        valid_feature_type: Type string indicating positions (e.g., "prefix|stem|suffix")
    """

    name: str = ""
    valid_feature_type: str = ""


@dataclass
class FLExCategory:
    """A FLEx grammatical category (e.g., noun, verb).

    Attributes:
        abbreviation: Category abbreviation (e.g., "n", "v", "def")
        valid_features: List of ValidFeature objects for this category
    """

    abbreviation: str = ""
    valid_features: list[ValidFeature] = field(default_factory=list)
