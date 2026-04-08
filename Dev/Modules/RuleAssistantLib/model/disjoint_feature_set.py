"""Disjoint feature set model classes"""

from dataclasses import dataclass, field
from .enums import PhraseType


@dataclass
class DisjointFeatureValuePairing:
    """A pairing of feature name to co-feature value.

    Example: gender feature paired with "sg" value.

    Attributes:
        flex_feature_name: FLEx feature name (e.g., "gender")
        co_feature_value: Co-feature value (e.g., "sg", "pl")
    """

    flex_feature_name: str = ""
    co_feature_value: str = ""

    def duplicate(self) -> "DisjointFeatureValuePairing":
        """Create a copy of this pairing.

        Returns:
            A new DisjointFeatureValuePairing
        """
        return DisjointFeatureValuePairing(
            flex_feature_name=self.flex_feature_name,
            co_feature_value=self.co_feature_value,
        )


@dataclass
class DisjointFeatureSet:
    """A set of disjoint (mutually exclusive) feature-value pairings.

    Example: number feature where "sg" and "pl" are disjoint and coupled
    with gender values.

    Attributes:
        name: Name of the disjoint set (e.g., "number")
        co_feature_name: Co-feature name (e.g., "gender")
        language: PhraseType.source or PhraseType.target
        pairings: List of DisjointFeatureValuePairing objects (2-6 pairings)
    """

    name: str = ""
    co_feature_name: str = ""
    language: PhraseType = PhraseType.target
    pairings: list[DisjointFeatureValuePairing] = field(default_factory=list)

    def remove_pairings_from(self, index: int) -> None:
        """Remove pairings starting from index (only if 3-6).

        Java code has hardcoded constraint: only allows 3-6 pairings total.
        This method only removes if index is in valid range.

        Args:
            index: Index to remove from (only 3-6 allowed)
        """
        # Hardcoded constraint from Java: can only have 3-6 total pairings
        if 3 <= index <= 6 and index < len(self.pairings):
            self.pairings = self.pairings[:index]

    def has_flex_feature_in_list(self, flex_features: list) -> bool:
        """Check if all pairings' features exist in given feature list.

        Args:
            flex_features: List of FLExFeature objects to check against

        Returns:
            True if all pairing features are found in the list
        """
        feature_names = {f.name for f in flex_features if hasattr(f, "name")}
        for pairing in self.pairings:
            if pairing.flex_feature_name not in feature_names:
                return False
        return True

    def duplicate(self) -> "DisjointFeatureSet":
        """Create a copy of this disjoint feature set.

        Returns:
            A new DisjointFeatureSet
        """
        new_set = DisjointFeatureSet(
            name=self.name,
            co_feature_name=self.co_feature_name,
            language=self.language,
        )
        new_set.pairings = [p.duplicate() for p in self.pairings]
        return new_set
