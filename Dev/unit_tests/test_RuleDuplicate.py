#
#   test_RuleDuplicate
#
#   Unit tests for FLExTransRule.duplicate() / FLExTransRuleGenerator.duplicateRule() - the Rule
#   Assistant's rule copy. Locks in the issue #1446 behavior: a duplicated rule gets no
#   permutations, so it doesn't generate redundant permutation rules for the same phrase head.
#
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

from RAutils import FLExTransRule, FLExTransRuleGenerator, PermutationsValue

# Build a rule carrying a given permutations setting.
def makeRule(name, permutations):

    return FLExTransRule(name=name, description="desc", createPermutations=permutations)

class TestRuleDuplicate(unittest.TestCase):

    # Duplicating a rule that generates permutations must produce a copy with no permutations.
    def test_duplicate_drops_permutations(self):

        original = makeRule("N Num", PermutationsValue.with_head)
        copy = original.duplicate()

        self.assertEqual(PermutationsValue.no, copy.createPermutations)

    # The copy keeps the original's name and description (the caller renames it separately).
    def test_duplicate_keeps_name_and_description(self):

        original = makeRule("N Num", PermutationsValue.not_head)
        copy = original.duplicate()

        self.assertEqual("N Num", copy.name)
        self.assertEqual("desc", copy.description)

    # duplicateRule inserts the new rule and returns it; its permutations are cleared too.
    def test_duplicateRule_inserts_and_returns_copy(self):

        gen = FLExTransRuleGenerator(flexTransRules=[makeRule("N Num", PermutationsValue.with_head)])
        newRule = gen.duplicateRule(0)

        self.assertIsNotNone(newRule)
        self.assertEqual(2, len(gen.flexTransRules))
        self.assertEqual(PermutationsValue.no, newRule.createPermutations)

if __name__ == '__main__':

    unittest.main()
