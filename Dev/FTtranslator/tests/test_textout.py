#
#   tests/test_textout
#
#   Ron Lockwood
#   SIL International
#   11/4/26
#
#   Version 3.17 - 11/4/26 - Ron Lockwood
#    Initial version. Tests the FieldWorks-free Text Out rules (textout.py), and compares them with FLExTrans' own TextInOutUtils.py.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for textout.py, the port of the rule-applying half of Dev\Lib\TextInOutUtils.py. Run them from Dev\FTtranslator with python -m unittest discover -s tests.
#
#   THE PARITY TEST
#
#   TextInOutUtils.py can't be imported outside FlexTools (it needs PyQt6 and, through Utils, FieldWorks' .NET assemblies), so TestParity reads its source with ast, takes out just the functions
#   and constants that apply rules, and runs them beside the port on the same rules and texts. Its Qt _translate is replaced by one that returns the English text, which is what the port
#   gives. The test is skipped where Dev\Lib isn't there (the Docker image holds only Dev\FTtranslator).
#
#   CODE STRUCTURE
#
#   rulesTree() builds a rules file from (search, replace, regex, inactive) tuples. TestRules covers the rules one kind at a time, TestTextOutRules the bundle loading and the messages, and
#   TestParity the comparison with the desktop.
#

import ast
import json
import tempfile
import unicodedata
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import regex

from fttranslator import textout

# The desktop's file, beside this package in the FLExTrans repo
DESKTOP_FILE = Path(__file__).resolve().parents[2] / "Lib" / "TextInOutUtils.py"

# What TestParity takes from the desktop's file
DESKTOP_NAMES = {"SearchReplaceRuleData", "getRuleFromElement", "buildRuleString", "buildRuleStringFromElement", "getPrintableString", "replacementsMap", "numRules", "create_replacer",
                 "applyRulesToString", "applySearchReplaceRules", "SEARCH_REPLACE_RULES_ELEM", "APPLY_WILDEBEEST_ATTRIB", "REGEX_ATTRIB", "INACTIVE_ATTRIB", "COMMENT_ATTRIB", "ARROW_CHAR"}

def rulesTree(rules):
    '''A rules file's tree from (search, replace, isRegEx, isInactive) tuples, laid out as the Text Out Rules editor writes it.'''

    root = ET.Element("FLExTransSearchReplace", ApplyWildebeest="no")
    rulesElement = ET.SubElement(root, "SearchReplaceRules")

    for search, replace, isRegEx, isInactive in rules:

        ruleElement = ET.SubElement(rulesElement, "SearchReplaceRule", RegEx="yes" if isRegEx else "no", Inactive="yes" if isInactive else "no", Comment="")
        ET.SubElement(ruleElement, "SearchString").text = search
        ET.SubElement(ruleElement, "ReplaceString").text = replace

    return ET.ElementTree(root)

def apply(rules, text):

    return textout.applySearchReplaceRules(text, rulesTree(rules))

class TestRules(unittest.TestCase):

    def testLiteral(self):

        self.assertEqual(apply([("Ebram", "Abram", False, False)], "Ebram dijo"), ("Abram dijo", ""))

    def testRulesApplyInOrder(self):

        self.assertEqual(apply([("ab", "x", False, False), ("xc", "y", False, False)], "abc")[0], "y")

    def testRegexBackreference(self):

        self.assertEqual(apply([(r"(\w+) (\w+)", r"\2 \1", True, False)], "hola mundo")[0], "mundo hola")

    def testCaseEscapes(self):

        self.assertEqual(apply([(r"^(\w+)", r"\u\1", True, False)], "hola mundo")[0], "Hola mundo")
        self.assertEqual(apply([(r"(\w+)$", r"\U\1\E!", True, False)], "hola mundo")[0], "hola MUNDO!")
        self.assertEqual(apply([(r"(\w+)", r"\u\L\1\E", True, False)], "HOLA")[0], "Hola")

    def testInactiveSkippedAndNotCounted(self):

        tree = rulesTree([("a", "b", False, True), ("c", "d", False, False)])
        self.assertEqual(textout.applySearchReplaceRules("ac", tree)[0], "ad")
        self.assertEqual(textout.numRules(tree), 1)

    def testFailingRuleNamesItAndStops(self):

        newText, errorMsg = apply([("a", "b", False, False), ("(", "x", True, False)], "abc")
        self.assertIsNone(newText)
        self.assertIn("rule 2", errorMsg)

    def testComposedSearchMatchesDecomposedText(self):

        # FieldWorks text is NFD; a rule typed with a composed é must still match it, and the result is NFD
        text = unicodedata.normalize("NFD", "café")
        self.assertEqual(apply([("é", "e", False, False)], text)[0], "cafe")
        self.assertEqual(apply([("caf", "kaf", False, False)], "café")[0], unicodedata.normalize("NFD", "kafé"))

class TestTextOutRules(unittest.TestCase):

    def testNoRulesInManifest(self):

        self.assertIsNone(textout.TextOutRules.load("nowhere", {"files": {}}))
        self.assertIsNone(textout.TextOutRules.load("nowhere", {"files": {"textOutRules": None}}))

    def testLoadAndApply(self):

        with tempfile.TemporaryDirectory() as folder:

            rulesTree([("a", "b", False, False), ("x", "y", False, True)]).write(Path(folder) / textout.RULES_FILE, encoding="utf-8", xml_declaration=True)
            manifest = json.loads(json.dumps({"files": {"textOutRules": textout.RULES_FILE}}))
            rules = textout.TextOutRules.load(folder, manifest)
            assert rules is not None  # the file was just written
            self.assertEqual(rules.apply("ax"), ("bx", [("info", "1 Text Out rules applied.")]))

    def testFailureMessage(self):

        rules = textout.TextOutRules(rulesTree([("[", "x", True, False)]))
        newText, messages = rules.apply("abc")
        self.assertIsNone(newText)
        self.assertEqual(messages[0][0], "error")

@unittest.skipUnless(DESKTOP_FILE.exists(), "FLExTrans' Dev\\Lib isn't here")
class TestParity(unittest.TestCase):

    # Rules and texts chosen to reach every branch: literal and regex rules, inactive rules, case escapes, an unknown escape, an empty group, NFD text and a failing rule
    RULES = [("Ebram", "Abram", False, False), ("x", "IGNORED", False, True), (r"\b(\w)(\w*) (telo)\b", r"\u\1\2 \U\3\E", True, False), (r"(o)(z)?", r"\1[\2]\n", True, False),
             ("é", "é́", False, False), (r"(\p{Lu})", r"\l\1", True, False)]
    TEXTS = ["Ebram nalin telo xoz", unicodedata.normalize("NFD", "Café Ébram"), "", "ZZZ telo"]

    @classmethod
    def setUpClass(cls):

        # The desktop's rule-applying functions, taken out of its source and run with an English _translate. See THE PARITY TEST above.
        tree = ast.parse(DESKTOP_FILE.read_text(encoding="utf-8"))
        keep: list[ast.stmt] = [node for node in tree.body if (isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in DESKTOP_NAMES)
                or (isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in DESKTOP_NAMES for target in node.targets))]
        namespace = {"regex": regex, "unicodedata": unicodedata, "_translate": lambda context, text: text}
        exec(compile(ast.Module(body=keep, type_ignores=[]), str(DESKTOP_FILE), "exec"), namespace)
        cls.desktop = namespace

    def testSameResults(self):

        for count in range(1, len(self.RULES) + 1):

            for text in self.TEXTS:

                with self.subTest(rules=count, text=text):

                    tree = rulesTree(self.RULES[:count])
                    self.assertEqual(textout.applySearchReplaceRules(text, tree), self.desktop["applySearchReplaceRules"](text, tree))
                    self.assertEqual(textout.numRules(tree), self.desktop["numRules"](tree))

    def testSameFailure(self):

        tree = rulesTree([("a", "b", False, False), ("(​", "x", True, False)])
        self.assertEqual(textout.applySearchReplaceRules("abc", tree), self.desktop["applySearchReplaceRules"]("abc", tree))

if __name__ == "__main__":

    unittest.main()
