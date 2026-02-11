import unittest
import sys
import os

# Add the path to the modules directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib/Windows')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Modules')))
sys.path.append('C:\\Program Files\\SIL\\FieldWorks 9\\')
sys.path.append('C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\')

# Import and initialize pythonnet
import clr
clr.AddReference("System")
clr.AddReference("SIL.LCModel")
clr.AddReference("SIL.LCModel.Core")

import Utils
from DoHermitCrabSynthesis import extractRootAndFirstTag as extract_root_and_first_tag_func

class extractRootAndFirstTag(unittest.TestCase):
    # Alias the function so test methods can use it
    _func = staticmethod(extract_root_and_first_tag_func)

    def test_prefix_and_suffix(self):
        input_str = "<2s.S2>tang1.1<v><3sg><obj>"
        expected_result = ('tang1.1', 'v')
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_prefix_only(self):
        input_str = "<2s.S2>tang1.1<v>"
        expected_result = ('tang1.1', 'v')
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_suffix_only(self):
        input_str = "tang1.1<v><3sg>"
        expected_result = ('tang1.1', 'v')
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_suffix_longer_cat(self):
        input_str = "tang1.1<v_intr><3sg>"
        expected_result = ('tang1.1', 'v_intr')
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_no_tag(self):
        input_str = "tang1.1"
        expected_result = ('tang1.1', None)
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_no_last_tag(self):
        input_str = "<impv>tang1.1"
        expected_result = ('tang1.1', None)
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

    def test_no_root(self):
        input_str = "<impv><v><obj>"
        expected_result = (None, None)
        result = self._func(input_str)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()