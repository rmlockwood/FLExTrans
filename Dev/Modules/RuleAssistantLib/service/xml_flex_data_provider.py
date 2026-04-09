"""XML FLEx Data Provider for loading FLEx metadata"""

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from flex_data import FLExData, SourceFLExData, TargetFLExData
from flex_feature import FLExFeature, FLExFeatureValue
from flex_category import FLExCategory, ValidFeature


class XMLFLExDataBackEndProvider:
    """Loads FLEx metadata from XML files."""

    @staticmethod
    def load_data_from_file(filename: str) -> FLExData:
        """Load FLEx data from an XML file.

        After loading, adds Greek variable values to features.

        Args:
            filename: Path to the FLEx data XML file

        Returns:
            FLExData object with source and target data
        """
        tree = ET.parse(filename)
        root = tree.getroot()

        flex_data = FLExData()

        # Load source data
        source_el = root.find("SourceData")
        if source_el is not None:
            flex_data.source_data = XMLFLExDataBackEndProvider._parse_language_data(
                source_el, SourceFLExData
            )

        # Load target data
        target_el = root.find("TargetData")
        if target_el is not None:
            flex_data.target_data = XMLFLExDataBackEndProvider._parse_language_data(
                target_el, TargetFLExData
            )

        # Post-process: add Greek variables to features
        flex_data.source_data.add_variable_values_to_features()
        flex_data.target_data.add_variable_values_to_features()

        return flex_data

    @staticmethod
    def _parse_language_data(lang_el, lang_class) -> "SourceFLExData | TargetFLExData":
        """Parse language data (source or target).

        Args:
            lang_el: ElementTree Element for language data
            lang_class: Class to instantiate (SourceFLExData or TargetFLExData)

        Returns:
            Parsed language data object
        """
        lang_data = lang_class()
        lang_data.name = lang_el.get("name", "")

        # Categories
        categories_el = lang_el.find("Categories")
        if categories_el is not None:
            for cat_el in categories_el.findall("FLExCategory"):
                cat = XMLFLExDataBackEndProvider._parse_category(cat_el)
                lang_data.categories.append(cat)

        # Features
        features_el = lang_el.find("Features")
        if features_el is not None:
            for feat_el in features_el.findall("FLExFeature"):
                feat = XMLFLExDataBackEndProvider._parse_feature(feat_el)
                lang_data.features.append(feat)

        return lang_data

    @staticmethod
    def _parse_category(cat_el) -> FLExCategory:
        """Parse a FLExCategory from XML element.

        Args:
            cat_el: ElementTree Element for a category

        Returns:
            Parsed FLExCategory
        """
        cat = FLExCategory(abbreviation=cat_el.get("abbr", ""))

        valid_features_el = cat_el.find("ValidFeatures")
        if valid_features_el is not None:
            for vf_el in valid_features_el.findall("ValidFeature"):
                vf = ValidFeature(
                    name=vf_el.get("name", ""),
                    valid_feature_type=vf_el.get("type", ""),
                )
                cat.valid_features.append(vf)

        return cat

    @staticmethod
    def _parse_feature(feat_el) -> FLExFeature:
        """Parse a FLExFeature from XML element.

        Args:
            feat_el: ElementTree Element for a feature

        Returns:
            Parsed FLExFeature
        """
        feat = FLExFeature(name=feat_el.get("name", ""))

        values_el = feat_el.find("Values")
        if values_el is not None:
            for val_el in values_el.findall("FLExFeatureValue"):
                val = FLExFeatureValue(abbreviation=val_el.get("abbr", ""))
                feat.values.append(val)

        feat.__post_init__()  # Set back-references
        return feat
