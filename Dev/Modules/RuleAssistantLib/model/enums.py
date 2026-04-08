"""Enums for FLExTrans Rule Assistant model"""

from enum import Enum


class AffixType(str, Enum):
    """Type of affix: prefix or suffix"""
    prefix = "prefix"
    suffix = "suffix"


class HeadValue(str, Enum):
    """Whether a word is marked as head"""
    yes = "yes"
    no = "no"


class OverwriteRulesValue(str, Enum):
    """Whether to overwrite existing rules on load"""
    yes = "yes"
    no = "no"


class PermutationsValue(str, Enum):
    """Whether to create permutations of the rule"""
    no = "no"
    not_head = "not_head"
    with_head = "with_head"


class PhraseType(str, Enum):
    """Source or target phrase"""
    source = "source"
    target = "target"


class ValidFeatureType(str, Enum):
    """Where a feature can appear (prefix, stem, suffix positions)"""
    prefix = "prefix"
    prefixstem = "prefixstem"
    prefixstemsuffix = "prefixstemsuffix"
    prefixsuffix = "prefixsuffix"
    stem = "stem"
    stemsuffix = "stemsuffix"
    suffix = "suffix"
