import unittest
import sys
import os

# Add the path to the lib directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
sys.path.append('C:\\Program Files\\SIL\\FieldWorks 9\\')
sys.path.append('C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\')

# Import and initialize pythonnet
import clr
clr.AddReference("System")
clr.AddReference("SIL.LCModel")
clr.AddReference("SIL.LCModel.Core")

import Utils

class TestescapeReservedApertChars(unittest.TestCase):

    def test_no_escapes(self):
        expected_result = "abc"
        input_str = "abc"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_right_brackets(self):
        expected_result = ">>"
        input_str = "\\>\\>"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_already_escaped(self):
        expected_result = "abc<"
        input_str = "abc\\<"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_asterisk(self):
        expected_result = "*lupo1.1"
        input_str = "\\*lupo1.1"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_slash(self):
        expected_result = "1/3sg"
        input_str = "1\\/3sg"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_backslash(self):
        expected_result = "ge\\hen1.1"
        input_str = "ge\\\\hen1.1"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_all(self):
        expected_result = "ge[]@/^${}<>*hen1.1"
        input_str = "ge\\[\\]\\@\\/\\^\\$\\{\\}\\<\\>\\*hen1.1"
        result = Utils.unescapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()