import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL before Utils loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import Utils

class TestescapeReservedApertChars(unittest.TestCase):

    def test_no_escapes(self):
        input_str = "abc"
        expected_result = "abc"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_right_brackets(self):
        input_str = ">>"
        expected_result = "\\>\\>"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_already_escaped(self):
        input_str = "abc\\<"
        expected_result = "abc\\<"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_asterisk(self):
        input_str = "*lupo1.1"
        expected_result = "\\*lupo1.1"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_slash(self):
        input_str = "1/3sg"
        expected_result = "1\\/3sg"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_backslash(self):
        input_str = "ge\\hen1.1"
        expected_result = "ge\\\\hen1.1"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_escaped_backslash(self):
        input_str = "ge\\\\hen1.1"
        expected_result = "ge\\\\hen1.1"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

    def test_all(self):
        input_str = "ge[]@/^${}<>*hen1.1"
        expected_result = "ge\\[\\]\\@\\/\\^\\$\\{\\}\\<\\>\\*hen1.1"
        result = Utils.escapeReservedApertChars(input_str)
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()