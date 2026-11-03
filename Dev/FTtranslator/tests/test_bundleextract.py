#
#   tests/test_bundleextract
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Tests the FieldWorks-free Extract Source Text on a small made-up lexicon.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for bundleextract.py that need neither FieldWorks nor a golden folder. The real proof of the port is check-golden, which compares it with Extract Source Text's own output on
#   whole projects; these tests pin down the main behaviors on a tiny lexicon so a change that breaks one shows up without a project at hand. The expected strings were worked out from the
#   original FLExTrans code, and check-golden agreed with the port on Mato-Uma, Toma-Zialo and FTT-Scratch when they were written. Run them from Dev\FTtranslator with
#   python -m unittest discover -s tests.
#
#   THE LEXICON
#
#   makeLexicon() builds a French-looking lexicon in bundle.py's format: maison (a noun with a stem feature) and its plural suffix -s, maisons (a sense-less irregularly inflected variant of
#   maison adding pl), and pomme and terre, the components of the complex form "pomme de terre". word() and punct() make occurrences in golden.py's format.
#
#   CODE STRUCTURE
#
#   makeLexicon(), word() and punct() are the fixtures. TestHelpers covers the copied Utils functions; TestExtractText covers whole texts: affixes and capitalization, sentence punctuation,
#   variants, complex forms, unknown words and paragraphs.
#

import sys
import unittest
from pathlib import Path

# The package is one folder up from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import bundleextract  # noqa: E402

def makeLexicon():
    '''The test lexicon. See THE LEXICON above.'''

    phrase = {"entry": "pommeDeTerre", "components": ["pomme", "terre"], "types": ["Phrase"]}
    entries = {
        "maison": {"headword": "maison", "clitic": None, "senses": ["maisonS"]},
        "-s": {"headword": "-s", "clitic": None, "senses": ["pluralS"]},
        "maisons": {"headword": "maisons", "clitic": None, "senses": [], "resolvesTo": {"entry": "maison", "inflFeatures": ["pl"]}},
        "pomme": {"headword": "pomme", "clitic": None, "senses": ["pommeS"], "complexForms": [phrase]},
        "terre": {"headword": "terre", "clitic": None, "senses": ["terreS"], "complexForms": [phrase]},
        "pommeDeTerre": {"headword": "pomme de terre", "clitic": None, "senses": ["pommeDeTerreS"]},
    }
    senses = {
        "maisonS": {"entry": "maison", "gloss": "house", "msa": "nounFem"},
        "pluralS": {"entry": "-s", "gloss": "PL", "msa": "suffix"},
        "pommeS": {"entry": "pomme", "gloss": "apple", "msa": "noun"},
        "terreS": {"entry": "terre", "gloss": "earth", "msa": "noun"},
        "pommeDeTerreS": {"entry": "pommeDeTerre", "gloss": "potato", "msa": "noun"},
    }
    msas = {
        "nounFem": {"stem": True, "pos": "n", "inflClass": None, "stemFeatures": ["fem"], "sense": "maisonS"},
        "noun": {"stem": True, "pos": "n", "inflClass": None, "stemFeatures": None, "sense": "pommeS"},
        "suffix": {"stem": False, "sense": "pluralS"},
    }
    config = {
        bundleextract.SENTENCE_PUNCTUATION: ".",
        bundleextract.SOURCE_FORMS_INFLECTION_1ST: [],
        bundleextract.SOURCE_COMPLEX_TYPES: ["Phrase"],
        bundleextract.SOURCE_DISCONTIG_TYPES: [],
        bundleextract.SOURCE_DISCONTIG_SKIPPED: [],
        bundleextract.NO_PROPER_NOUN_WARNING: False,
    }

    return bundleextract.Lexicon({"entries": entries, "senses": senses, "msas": msas}, config)

def word(surface, beg, bundles=None, seg=0, para=0):
    '''An occurrence of a word. bundles is a list of (entry, sense, msa); None makes it an unanalyzed wordform.'''

    occurrence = {"para": para, "seg": seg, "beg": beg, "end": beg + len(surface), "surface": surface, "baseline": surface}

    if bundles is None:

        occurrence["kind"] = bundleextract.WFI_WORD_FORM
    else:
        occurrence.update({"kind": bundleextract.WFI_GLOSS, "wordform": surface, "bundles": [{"morphEntry": e, "sense": s, "msa": m} for e, s, m in bundles]})

    return occurrence

def punct(text, beg, seg=0, para=0):

    return {"para": para, "seg": seg, "beg": beg, "end": beg + len(text), "punct": text}

def extract(*occurrences):

    return bundleextract.extractText({"occurrences": list(occurrences)}, makeLexicon())

class TestHelpers(unittest.TestCase):

    def testEscapeReservedApertChars(self):

        self.assertEqual(bundleextract.escapeReservedApertChars("a[b"), "a\\[b")

        # Already escaped characters are left alone
        self.assertEqual(bundleextract.escapeReservedApertChars("a\\[b"), "a\\[b")

    def testSplitCompounds(self):

        self.assertEqual(bundleextract.splitCompounds("^a1.1<n>b1.1<n>$"), "^a1.1<n>$^b1.1<n>$")
        self.assertEqual(bundleextract.splitCompounds("^.<sent>$"), "^.<sent>$")

    def testAddOne(self):

        self.assertEqual(bundleextract.addOne("maison"), "maison1")
        self.assertEqual(bundleextract.addOne("maison2"), "maison2")

    def testDoCapitalization(self):

        self.assertEqual(bundleextract.doCapitalization("maison", "Maisons"), "Maison")
        self.assertEqual(bundleextract.doCapitalization("maison", "MAISONS"), "MAISON")

class TestExtractText(unittest.TestCase):

    def testAffixCapitalizationAndSentencePunctuation(self):

        # The lemma takes the occurrence's capitalization; the stem feature comes before the suffix's gloss
        output, messages = extract(word("Maisons", 0, [("maison", "maisonS", "nounFem"), ("-s", "pluralS", "suffix")]), punct(".", 7))
        self.assertEqual(output, "^Maison1.1<n><fem><PL>$^.<sent>$\n")
        self.assertEqual(messages, [])

    def testVariantAddsItsInflectionFeatures(self):

        output, _ = extract(word("maisons", 0, [("maisons", "maisonS", "nounFem")]))
        self.assertEqual(output, "^maison1.1<n><fem><pl>$\n")

    def testComplexFormReplacesItsComponents(self):

        # The second component's leading space goes with it; the complex form takes the first component's
        output, _ = extract(word("pomme", 0, [("pomme", "pommeS", "noun")]), word("terre", 6, [("terre", "terreS", "noun")]))
        self.assertEqual(output, "^pomme de terre1.1<n>$\n")

    def testUnknownWordsWarnOnce(self):

        output, messages = extract(word("xyz", 0), word("xyz", 4))
        self.assertEqual(output, "^xyz<UNK>$ ^xyz<UNK>$\n")
        self.assertEqual(messages, [("warning", "No analysis found for the word: xyz Treating this as an unknown word."), ("warning", "One or more unknown words occurred multiple times.")])

    def testNewParagraphWhenOffsetsGoBack(self):

        output, _ = extract(word("abc", 0), word("de", 0, seg=1, para=1))
        self.assertEqual(output, "^abc<UNK>$\n^de<UNK>$\n")

    def testMissingSenseFallsBackToTheWordform(self):

        output, messages = extract(word("maison", 0, [("maison", None, "nounFem")]))
        self.assertEqual(output, "^maison<UNK>$\n")
        self.assertEqual(messages[0], ("warning", "No sense found for some part of the source word: maison"))

if __name__ == "__main__":

    unittest.main()
