"""XML Backend Provider for loading/saving rules"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from ..model.flex_trans_rule_generator import FLExTransRuleGenerator
from ..model.flex_trans_rule import FLExTransRule
from ..model.source_target import Source, Target
from ..model.phrase import Phrase
from ..model.word import Word
from ..model.feature import Feature
from ..model.affix import Affix
from ..model.category import Category
from ..model.enums import AffixType, HeadValue, OverwriteRulesValue, PermutationsValue, PhraseType
from ..model.disjoint_feature_set import DisjointFeatureSet, DisjointFeatureValuePairing


class XMLBackEndProvider:
    """Loads and saves FLExTransRuleGenerator from/to XML files."""

    DOCTYPE = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE FLExTransRuleGenerator PUBLIC " -//XMLmind//DTD FLExTransRuleGenerator//EN"\n'
        '"FLExTransRuleGenerator.dtd">\n'
    )

    @staticmethod
    def load_data_from_file(filename: str) -> FLExTransRuleGenerator:
        """Load rules from an XML file.

        If file doesn't exist, creates default with one empty rule.

        Args:
            filename: Path to the rule XML file

        Returns:
            FLExTransRuleGenerator object
        """
        file_path = Path(filename)

        if not file_path.exists():
            # Create default
            generator = FLExTransRuleGenerator()
            rule = FLExTransRule(name="Rule 1")
            rule.source = Source()
            rule.target = Target()
            word_s = Word(word_id="1")
            word_t = Word(word_id="1")
            rule.source.words = [word_s]
            rule.target.words = [word_t]
            word_s.parent = rule.source
            word_t.parent = rule.target
            generator.flex_trans_rules = [rule]
            XMLBackEndProvider.save_data_to_file(generator, filename)
            return generator

        tree = ET.parse(filename)
        root = tree.getroot()

        generator = FLExTransRuleGenerator()
        generator.overwrite_rules = OverwriteRulesValue(
            root.get("overwrite_rules", "yes")
        )

        # Load disjoint feature sets
        disjoint_sets_el = root.find("DisjointFeatureSets")
        if disjoint_sets_el is not None:
            for ds_el in disjoint_sets_el.findall("DisjointFeatureSet"):
                ds = XMLBackEndProvider._parse_disjoint_feature_set(ds_el)
                generator.disjoint_features.append(ds)

        # Load rules
        rules_el = root.find("FLExTransRules")
        if rules_el is not None:
            for rule_el in rules_el.findall("FLExTransRule"):
                rule = XMLBackEndProvider._parse_rule(rule_el)
                generator.flex_trans_rules.append(rule)
                rule.parent = generator

        # Post-process: set phrase types and create category constituents
        for rule in generator.flex_trans_rules:
            rule.target.phrase_type = PhraseType.target
            rule.source.phrase_type = PhraseType.source
            XMLBackEndProvider._set_category_constituents_in_words(rule.source)
            XMLBackEndProvider._set_category_constituents_in_words(rule.target)

        return generator

    @staticmethod
    def save_data_to_file(generator: FLExTransRuleGenerator, filename: str) -> None:
        """Save rules to an XML file with proper DOCTYPE.

        Args:
            generator: The FLExTransRuleGenerator to save
            filename: Path to save to
        """
        root = ET.Element("FLExTransRuleGenerator")
        root.set("overwrite_rules", generator.overwrite_rules.value)

        # Disjoint feature sets
        if generator.disjoint_features:
            disjoint_sets_el = ET.SubElement(root, "DisjointFeatureSets")
            for ds in generator.disjoint_features:
                XMLBackEndProvider._create_disjoint_feature_set_element(ds, disjoint_sets_el)

        # Rules
        rules_el = ET.SubElement(root, "FLExTransRules")
        for rule in generator.flex_trans_rules:
            XMLBackEndProvider._create_rule_element(rule, rules_el)

        # Format and save
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")

        # Write to string, then prepend DOCTYPE
        import io
        buf = io.StringIO()
        tree.write(buf, encoding="unicode", xml_declaration=False)
        xml_body = buf.getvalue()

        with open(filename, "w", encoding="utf-8") as f:
            f.write(XMLBackEndProvider.DOCTYPE)
            f.write(xml_body)

    @staticmethod
    def _parse_rule(rule_el) -> FLExTransRule:
        """Parse a FLExTransRule from XML element.

        Args:
            rule_el: ElementTree Element for a rule

        Returns:
            Parsed FLExTransRule
        """
        desc_el = rule_el.find("Description")
        description = desc_el.text if desc_el is not None and desc_el.text else ""

        rule = FLExTransRule(
            name=rule_el.get("name", ""),
            description=description,
            create_permutations=PermutationsValue(rule_el.get("create_permutations", "with_head")),
        )

        # Source phrase
        source_el = rule_el.find("Source")
        if source_el is not None:
            phrase_el = source_el.find("Phrase")
            if phrase_el is not None:
                parsed_phrase = XMLBackEndProvider._parse_phrase(phrase_el, PhraseType.source)
                rule.source.words = parsed_phrase.words
                for word in rule.source.words:
                    word.parent = rule.source

        # Target phrase
        target_el = rule_el.find("Target")
        if target_el is not None:
            phrase_el = target_el.find("Phrase")
            if phrase_el is not None:
                parsed_phrase = XMLBackEndProvider._parse_phrase(phrase_el, PhraseType.target)
                rule.target.words = parsed_phrase.words
                for word in rule.target.words:
                    word.parent = rule.target

        return rule

    @staticmethod
    def _parse_phrase(phrase_el, phrase_type: PhraseType) -> Phrase:
        """Parse a Phrase from XML element.

        Args:
            phrase_el: ElementTree Element for a phrase
            phrase_type: PhraseType (source or target)

        Returns:
            Parsed Phrase
        """
        phrase = Phrase(phrase_type=phrase_type)

        words_el = phrase_el.find("Words")
        if words_el is not None:
            for word_el in words_el.findall("Word"):
                word = XMLBackEndProvider._parse_word(word_el)
                phrase.words.append(word)
                word.parent = phrase

        return phrase

    @staticmethod
    def _parse_word(word_el) -> Word:
        """Parse a Word from XML element.

        Args:
            word_el: ElementTree Element for a word

        Returns:
            Parsed Word
        """
        word = Word(
            word_id=word_el.get("id", ""),
            word_category=word_el.get("category", ""),
            head=HeadValue(word_el.get("head", "no")),
        )

        # Features
        features_el = word_el.find("Features")
        if features_el is not None:
            for feature_el in features_el.findall("Feature"):
                feature = XMLBackEndProvider._parse_feature(feature_el)
                word.features.append(feature)
                feature.parent = word

        # Affixes
        affixes_el = word_el.find("Affixes")
        if affixes_el is not None:
            for affix_el in affixes_el.findall("Affix"):
                affix = XMLBackEndProvider._parse_affix(affix_el)
                word.affixes.append(affix)
                affix.parent = word

        return word

    @staticmethod
    def _parse_feature(feature_el) -> Feature:
        """Parse a Feature from XML element.

        Args:
            feature_el: ElementTree Element for a feature

        Returns:
            Parsed Feature
        """
        return Feature(
            label=feature_el.get("label", ""),
            match=feature_el.get("match", ""),
            value=feature_el.get("value", ""),
            unmarked=feature_el.get("unmarked_default", ""),
            ranking=int(feature_el.get("ranking", "0")),
        )

    @staticmethod
    def _parse_affix(affix_el) -> Affix:
        """Parse an Affix from XML element.

        Args:
            affix_el: ElementTree Element for an affix

        Returns:
            Parsed Affix
        """
        affix = Affix(
            affix_type=AffixType(affix_el.get("type", "suffix"))
        )

        features_el = affix_el.find("Features")
        if features_el is not None:
            for feature_el in features_el.findall("Feature"):
                feature = XMLBackEndProvider._parse_feature(feature_el)
                affix.features.append(feature)
                feature.parent = affix

        return affix

    @staticmethod
    def _parse_disjoint_feature_set(ds_el) -> DisjointFeatureSet:
        """Parse a DisjointFeatureSet from XML element.

        Args:
            ds_el: ElementTree Element for a disjoint set

        Returns:
            Parsed DisjointFeatureSet
        """
        ds = DisjointFeatureSet(
            name=ds_el.get("disjoint_name", ""),
            co_feature_name=ds_el.get("co_feature_name", ""),
            language=PhraseType(ds_el.get("language", "target")),
        )

        pairings_el = ds_el.find("DisjointFeatureValuePairings")
        if pairings_el is not None:
            for pairing_el in pairings_el.findall("DisjointFeatureValuePairing"):
                pairing = DisjointFeatureValuePairing(
                    flex_feature_name=pairing_el.get("flex_feature_name", ""),
                    co_feature_value=pairing_el.get("co_feature_value", ""),
                )
                ds.pairings.append(pairing)

        return ds

    @staticmethod
    def _create_rule_element(rule: FLExTransRule, parent_el) -> None:
        """Create XML element for a rule.

        Args:
            rule: The FLExTransRule to serialize
            parent_el: Parent ElementTree Element
        """
        rule_el = ET.SubElement(parent_el, "FLExTransRule")
        rule_el.set("name", rule.name)
        rule_el.set("create_permutations", rule.create_permutations.value)

        desc_el = ET.SubElement(rule_el, "Description")
        desc_el.text = rule.description or ""

        source_el = ET.SubElement(rule_el, "Source")
        XMLBackEndProvider._create_phrase_element(rule.source, source_el)

        target_el = ET.SubElement(rule_el, "Target")
        XMLBackEndProvider._create_phrase_element(rule.target, target_el)

    @staticmethod
    def _create_phrase_element(phrase: Phrase, parent_el) -> None:
        """Create XML element for a phrase.

        Args:
            phrase: The Phrase to serialize
            parent_el: Parent ElementTree Element
        """
        phrase_el = ET.SubElement(parent_el, "Phrase")

        if phrase.words:
            words_el = ET.SubElement(phrase_el, "Words")
            for word in phrase.words:
                XMLBackEndProvider._create_word_element(word, words_el)

    @staticmethod
    def _create_word_element(word: Word, parent_el) -> None:
        """Create XML element for a word.

        Args:
            word: The Word to serialize
            parent_el: Parent ElementTree Element
        """
        word_el = ET.SubElement(parent_el, "Word")
        word_el.set("id", word.word_id)
        word_el.set("category", word.word_category)
        word_el.set("head", word.head.value)

        if word.features:
            features_el = ET.SubElement(word_el, "Features")
            for feature in word.features:
                XMLBackEndProvider._create_feature_element(feature, features_el)

        if word.affixes:
            affixes_el = ET.SubElement(word_el, "Affixes")
            for affix in word.affixes:
                XMLBackEndProvider._create_affix_element(affix, affixes_el)

    @staticmethod
    def _create_feature_element(feature: Feature, parent_el) -> None:
        """Create XML element for a feature.

        Args:
            feature: The Feature to serialize
            parent_el: Parent ElementTree Element
        """
        feature_el = ET.SubElement(parent_el, "Feature")
        feature_el.set("label", feature.label)
        feature_el.set("match", feature.match)
        feature_el.set("value", feature.value)
        feature_el.set("unmarked_default", feature.unmarked)
        feature_el.set("ranking", str(feature.ranking))

    @staticmethod
    def _create_affix_element(affix: Affix, parent_el) -> None:
        """Create XML element for an affix.

        Args:
            affix: The Affix to serialize
            parent_el: Parent ElementTree Element
        """
        affix_el = ET.SubElement(parent_el, "Affix")
        affix_el.set("type", affix.affix_type.value)

        if affix.features:
            features_el = ET.SubElement(affix_el, "Features")
            for feature in affix.features:
                XMLBackEndProvider._create_feature_element(feature, features_el)

    @staticmethod
    def _create_disjoint_feature_set_element(ds: DisjointFeatureSet, parent_el) -> None:
        """Create XML element for a disjoint feature set.

        Args:
            ds: The DisjointFeatureSet to serialize
            parent_el: Parent ElementTree Element
        """
        ds_el = ET.SubElement(parent_el, "DisjointFeatureSet")
        ds_el.set("language", ds.language.value)
        ds_el.set("disjoint_name", ds.name)
        ds_el.set("co_feature_name", ds.co_feature_name)

        if ds.pairings:
            pairings_el = ET.SubElement(ds_el, "DisjointFeatureValuePairings")
            for pairing in ds.pairings:
                pairing_el = ET.SubElement(pairings_el, "DisjointFeatureValuePairing")
                pairing_el.set("flex_feature_name", pairing.flex_feature_name)
                pairing_el.set("co_feature_value", pairing.co_feature_value)

    @staticmethod
    def _set_category_constituents_in_words(phrase: Phrase) -> None:
        """Create Category constituents from word category strings.

        Called after load to reconstruct runtime Category objects.

        Args:
            phrase: The Phrase to process
        """
        for word in phrase.words:
            word.category_constituent = Category(name=word.word_category)
            word.category_constituent.parent = word
