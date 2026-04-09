"""FLExData root class and subclasses"""

from dataclasses import dataclass, field
from flex_feature import FLExFeature, FLExFeatureValue
from flex_category import FLExCategory, ValidFeature
import constants


@dataclass
class FLExDataBase:
    """Base class for source and target FLEx data.

    Attributes:
        name: Language name
        categories: List of FLExCategory objects
        features: List of FLExFeature objects
        features_without_variables: Original features before Greek vars added
        max_variables: Maximum number of Greek variables to add (default 4)
    """

    name: str = ""
    categories: list[FLExCategory] = field(default_factory=list)
    features: list[FLExFeature] = field(default_factory=list)
    features_without_variables: list[FLExFeature] = field(default_factory=list)
    max_variables: int = 4

    def __post_init__(self):
        pass

    def add_variable_values_to_features(self) -> None:
        """Add Greek letter variables to each feature's value list.

        Creates a clone in features_without_variables first, then adds
        Greek variable values (α, β, γ, δ, etc.) to the original features.
        """
        # Save originals without variables
        self.features_without_variables = [f.duplicate() for f in self.features]

        # Add Greek variables to each feature
        for feature in self.features:
            # Add Greek letters up to max_variables
            for i in range(min(self.max_variables, len(constants.GREEK_VARIABLES))):
                greek_var = constants.GREEK_VARIABLES[i]
                feature.values.append(FLExFeatureValue(abbreviation=greek_var))

    def get_flex_categories_for_phrase(self) -> list[FLExCategory]:
        """Get all categories for this language.

        Returns:
            List of FLExCategory objects
        """
        return self.categories

    def get_features_for_category(self, category_abbr: str) -> list[FLExFeature]:
        """Get FLEx features valid for a category.

        Args:
            category_abbr: Category abbreviation to filter by

        Returns:
            List of FLExFeature objects valid for the category
        """
        # Find the category
        for category in self.categories:
            if category.abbreviation == category_abbr:
                # Get feature names from valid_features
                valid_names = {vf.name for vf in category.valid_features}
                # Return matching features
                return [f for f in self.features if f.name in valid_names]
        return []


@dataclass
class SourceFLExData(FLExDataBase):
    """FLEx data for the source language"""

    pass


@dataclass
class TargetFLExData(FLExDataBase):
    """FLEx data for the target language"""

    pass


@dataclass
class FLExData:
    """Root object for FLEx metadata (source and target languages).

    Attributes:
        source_data: SourceFLExData object
        target_data: TargetFLExData object
    """

    source_data: SourceFLExData = field(default_factory=SourceFLExData)
    target_data: TargetFLExData = field(default_factory=TargetFLExData)

    def get_flex_categories_for_phrase(self, phrase_type) -> list[FLExCategory]:
        """Get categories for a phrase type.

        Args:
            phrase_type: PhraseType.source or PhraseType.target

        Returns:
            List of FLExCategory objects
        """
        from enums import PhraseType

        if phrase_type == PhraseType.source:
            return self.source_data.get_flex_categories_for_phrase()
        else:
            return self.target_data.get_flex_categories_for_phrase()

    def get_features_in_phrase_for_category(self, phrase_type, category_abbr: str):
        """Get features valid for a category in a phrase.

        Args:
            phrase_type: PhraseType.source or PhraseType.target
            category_abbr: Category abbreviation

        Returns:
            List of FLExFeature objects
        """
        from enums import PhraseType

        if phrase_type == PhraseType.source:
            return self.source_data.get_features_for_category(category_abbr)
        else:
            return self.target_data.get_features_for_category(category_abbr)
