#
#   test_WorkOnRulesWithAI
#
#   Unit tests for the non-Qt helper logic in the WorkOnRulesWithAI module. The module imports
#   PyQt, flextoolslib, and several FLEx-dependent helpers at module level, so net_stubs is
#   imported first to satisfy those imports; the function under test (buildProjectDataText) is
#   pure and operates on a plain StartData-shaped object, so a lightweight fake stands in for
#   the real FLEx-derived data.
#
import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL/Qt before the module loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Modules')))

import WorkOnRulesWithAI

class FakeDB:
    '''Stands in for one side (source or target) of the FLEx-derived StartData.'''

    def __init__(self):
        self.projectName = 'MyProject'
        self.categoryList = ['n', 'v', 'adj']
        self.featureList = [('gender', ['m', 'f']), ('number', ['sg', 'pl'])]
        self.categoryFeatures = {
            'n': {'gender': {'src', 'tgt'}, 'number': {'src'}},
            'v': {},  # empty - should be skipped
        }

class FakeStartData:

    def __init__(self):
        self.src = FakeDB()
        self.tgt = FakeDB()

class TestBuildProjectDataText(unittest.TestCase):

    def setUp(self):
        self.startData = FakeStartData()

    def test_includes_both_sides(self):

        text = WorkOnRulesWithAI.buildProjectDataText(self.startData, includeProjectNames=False)

        self.assertIn('SOURCE project:', text)
        self.assertIn('TARGET project:', text)

    def test_categories_and_features(self):

        text = WorkOnRulesWithAI.buildProjectDataText(self.startData, includeProjectNames=False)

        self.assertIn('Categories: n, v, adj', text)
        self.assertIn('gender: m, f', text)
        self.assertIn('number: sg, pl', text)

    def test_category_features_with_sides(self):

        text = WorkOnRulesWithAI.buildProjectDataText(self.startData, includeProjectNames=False)

        # 'n' lists its features with the sides (sorted) in brackets; the featureless 'v' is skipped.
        self.assertIn('n: gender[src|tgt], number[src]', text)
        self.assertNotIn('v:', text)

    def test_project_names_hidden_by_default(self):

        text = WorkOnRulesWithAI.buildProjectDataText(self.startData, includeProjectNames=False)

        self.assertNotIn('MyProject', text)
        self.assertIn('SOURCE project:', text)

    def test_project_names_included_when_opted_in(self):

        text = WorkOnRulesWithAI.buildProjectDataText(self.startData, includeProjectNames=True)

        self.assertIn('SOURCE project: MyProject', text)
        self.assertIn('TARGET project: MyProject', text)

if __name__ == '__main__':
    unittest.main()
