#
#   tests/test_synthesis
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Tests the FieldWorks-free Convert Text to Synthesizer Format and HermitCrab synthesis file handling on made-up data.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for synthesis.py that need neither FieldWorks nor HCSynthByGloss. The real proof of the port is comparing a whole run with the desktop's Build and Output files; these tests pin down
#   the parts a small test project doesn't reach - complex forms, irregularly inflected variants, circumfixes and the capitalization codes - so a change that breaks one shows up. The expected
#   strings are what FLExTrans' own convert_to_STAMP(), createHermitCrabParsesFile(), produceSynthesisFile() and fixUpText() gave on the same data when this file was written. Run them from
#   Dev\FTtranslator with python -m unittest discover -s tests.
#
#   THE DATA
#
#   CACHE is a ConversionData cache file with two complex forms (pomme de terre, inflection on the first component; irse, on the last, with a proclitic and an enclitic) and the variants of ser and
#   tener. AFFIXES is a target affix gloss list with each kind of affix.
#
#   CODE STRUCTURE
#
#   TestMasterFile covers convertToHermitCrab(); TestSynthesisFiles covers createHermitCrabParsesFile(), produceSynthesisFile() and fixUpText() with a made-up surface forms file.
#

import sys
import tempfile
import unittest
from pathlib import Path

# The package is one folder up from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import synthesis  # noqa: E402

CACHE = """COMPLEX FORMS
pomme de terre1
True
2
< n papa1.1 >
< adj frito1.1 >
irse1
False
2
REFL < v ir1.1 >
< adv ya1.1 > ENC
IRREGULARLY INFLECTED VARIANT FORMS
ser1
2
< _variant_ es1 >
2
number
sg
person
3
< _variant_ soy1 >
2
number
sg
person
1
tener1
1
< _variant_ tiene1 >
1
person
3
"""

AFFIXES = "PRS_3SG|suffix\nPL|suffix\nNEG|prefix\nCF|circumfix\nINFX|infix\nREFL|proclitic\nENC|enclitic\nPST|suffix\n"

class SynthesisTestCase(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.folder = Path(self.tempDir.name)
        (self.folder / "cache.txt").write_text(CACHE, encoding="utf-8")
        (self.folder / "affixes.txt").write_text(AFFIXES, encoding="utf-8")
        self.convData = synthesis.ConversionData(self.folder / "cache.txt")
        self.masterFile = self.folder / "master.txt"

    def tearDown(self):

        self.tempDir.cleanup()

    def master(self, stream):
        '''Run convertToHermitCrab() on a stream and return (the master file's text or None, the errors).'''

        errors = synthesis.convertToHermitCrab(self.convData, str(self.folder / "affixes.txt"), stream, self.masterFile, ["Compound"], ["Phrasal"], ".?!")
        text = self.masterFile.read_text(encoding="utf-8") if self.masterFile.exists() else None

        return text, [message for message, code in errors if code == 2]

class TestMasterFile(SynthesisTestCase):

    def testVariants(self):

        # The tags matching a variant's features are removed, in any order; the capitalization code stays the original word's
        text, errors = self.master("^Ser1.1<cop><3><sg>$ ^ser1.1<cop><sg><1><PST>$ ^ser1.1<cop><PL>$^.<sent>$\n")
        self.assertEqual(errors, [])
        self.assertEqual(text, "^Ser1.1<cop><3><sg>$,es1.1_variant_<_variant_>;1\n^ser1.1<cop><sg><1><PST>$,soy1.1_variant_<_variant_><PST>;\n^ser1.1<cop><PL>$,ser1.1<cop><PL>;\n")

    def testComplexForms(self):

        # Inflection on the first or last component, capitalization codes 1, 2 and 3, clitics, and a variant keeping its sense number
        text, _ = self.master("^Pomme de terre1.1<n><PL>$, ^POMME DE TERRE1.1<n>$ ^Pomme De Terre1.1<n>$ «^irse1.1<v><PRS_3SG>$» ^tener1.2<v><NEG><3><PST>$\n")
        expected = ("^Pomme de terre1.1<n><PL>$,papa1.1<n><PL>;1|frito1.1<adj>;\n^POMME DE TERRE1.1<n>$,papa1.1<n>;2|frito1.1<adj>;\n^Pomme De Terre1.1<n>$,papa1.1<n>;3|frito1.1<adj>;\n"
                    "^irse1.1<v><PRS_3SG>$,<REFL>ir1.1<v>;|ya1.1<adv><PRS.3SG><ENC>;\n^tener1.2<v><NEG><3><PST>$,<NEG>tiene1.2_variant_<_variant_><PST>;\n")
        self.assertEqual(text, expected)

    def testAffixKinds(self):

        # A circumfix's prefix part stays as a prefix (without its tag) and its suffix part goes; an infix goes with the prefixes; each lexical unit is written once
        text, _ = self.master("^hablar1.1<v><NEG><CF><INFX><PRS_3SG><CF>$ ^@chat<UNK>$ ^Chat<UNK>$ ^El1.1<def>$ ^el1.1<def>$ ^El1.1<def>$\n")
        self.assertEqual(text, "^hablar1.1<v><NEG><CF><INFX><PRS_3SG><CF>$,<NEG><CF><INFX>hablar1.1<v><PRS.3SG>;\n^@chat<UNK>$,@chat<UNK>;\n^Chat<UNK>$,Chat<UNK>;1\n^El1.1<def>$,el1.1<def>;1\n^el1.1<def>$,el1.1<def>;\n")

    def testMissingCategory(self):

        text, errors = self.master("^solo1.1$ ^x1.1<n>$\n")
        self.assertIsNone(text)
        self.assertEqual(errors, ["Lemma or grammatical category missing for a target word near word 1. Found only: solo1.1. The preceding two words were: . The following two words were: x1.1<n>. Processing stopped."])

class TestSynthesisFiles(SynthesisTestCase):

    def testParsesAndSynthesis(self):

        stream = "^José1.1<nprop>$ ^@chat<UNK>$ ^ser1.1<cop><3><sg>$ \\[x\\] ^papa1.1<n><PL>$^.<sent>$\n"
        self.master(stream)

        # A capitalized lemma is restored from the config's map. An @ word is NOT skipped: the test looks at the parse's second character, and the @ is its first (see TRAPS in synthesis.py).
        luInfoList = []
        parsesFile = self.folder / "parses.txt"
        errors = synthesis.createHermitCrabParsesFile(self.masterFile, parsesFile, luInfoList, {"josé1.1nprop": "José1.1"})
        self.assertEqual(errors, [])
        self.assertEqual(parsesFile.read_text(encoding="utf-8"), "^José1.1<nprop>$\n^@chat<UNK>$\n^es1.1_variant_<_variant_>$\n^papa1.1<n><PL>$\n")
        self.assertEqual([lu for lu, _ in luInfoList], ["^José1.1<nprop>$", "^@chat<UNK>$", "^ser1.1<cop><3><sg>$", "^papa1.1<n><PL>$"])

        # HCSynthByGloss's output: a BOM, a failure for the @ word, an ambiguous word and a failure with a message
        surfaceFile = self.folder / "surface.txt"
        surfaceFile.write_text("﻿josé\n%0%^@chat<UNK>$%\n%2%es%está%\n%0%^papa1.1<n><PL>$% Duplicate gloss(es) found for 'PL'; synthesis may not work.\n", encoding="utf-8")
        errors, text = synthesis.produceSynthesisFile(luInfoList, surfaceFile, stream)
        self.assertEqual(errors, [("Synthesis failed. (%0%^@chat<UNK>$%)", 1), (" Duplicate gloss(es) found for 'PL'; synthesis may not work.", 1)])
        self.assertEqual(text, "José %0%^@chat<UNK>$% %2%es%está% \\[x\\] %0%^papa1.1<n><PL>$%.\n")

        # Cleaning up removes sense numbers, @ signs, tags and the failure markers; either way the Apertium escapes are undone
        self.assertEqual(synthesis.fixUpText(text, True), "José chat %2%es%está% [x] papa.\n")
        self.assertEqual(synthesis.fixUpText(text, False), "José %0%^@chat<UNK>$% %2%es%está% [x] %0%^papa1.1<n><PL>$%.\n")

if __name__ == "__main__":

    unittest.main()
