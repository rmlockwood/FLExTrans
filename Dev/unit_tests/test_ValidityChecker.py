#
#   test_ValidityChecker
#
#   Unit tests for RAutils.ValidityChecker - the Rule Assistant's rule validation. These lock in
#   the issue #1451 behavior: validateRule reports every problem with a rule at once (not one at a
#   time), and a target with any words must have a head marked (matching what CreateApertiumRules
#   requires before it will write a rule).
#
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

from RAutils import FLExTransRule, Source, Target, Word, Feature, HeadValue, ValidityChecker

# Build a rule from lists of source/target Word objects, wiring the phrases the way the rest of the code expects.
def makeRule(sourceWords, targetWords):

    rule = FLExTransRule(name="r")
    rule.source = Source(words=list(sourceWords))
    rule.target = Target(words=list(targetWords))

    return rule

class TestValidityChecker(unittest.TestCase):

    # A completely unworked rule (no source category, no target feature, no head) should report all three problems together in a single message.
    def test_all_problems_reported_together(self):

        rule = makeRule([Word(wordId="1")], [Word(wordId="1")])
        isValid, message = ValidityChecker.validateRule(rule)

        self.assertFalse(isValid)
        self.assertIn("category", message)
        self.assertIn("feature", message)
        self.assertIn("head", message)

    # A single target word with no head marked is invalid, because CreateApertiumRules won't write a headless target even when there's only one word.
    def test_single_target_word_needs_head(self):

        rule = makeRule([Word(wordId="1", wordCategory="n")],
                        [Word(wordId="1", wordCategory="n", features=[Feature(label="number", value="pl")])])
        isValid, message = ValidityChecker.checkTargetWordMarkedAsHead(rule)

        self.assertFalse(isValid)
        self.assertIn("head", message)

    # A fully specified rule (source category, target feature, one head) passes with an empty message.
    def test_valid_rule_passes(self):

        rule = makeRule([Word(wordId="1", wordCategory="n")],
                        [Word(wordId="1", wordCategory="n", head=HeadValue.yes, features=[Feature(label="number", value="pl")])])
        isValid, message = ValidityChecker.validateRule(rule)

        self.assertTrue(isValid)
        self.assertEqual("", message)

if __name__ == '__main__':

    unittest.main()
