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

from Testbed import parseString

class TestParseString(unittest.TestCase):

    def test_basic_case(self):
        input_str = "abc<zx><uv>"
        expected_main_part = "abc"
        expected_symbols = ["zx", "uv"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_escaped_brackets(self):
        input_str = r"abc\<def\><zx>"
        expected_main_part = r"abc\<def\>"
        expected_symbols = ["zx"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_only_symbols(self):
        input_str = ">><sent>"
        expected_main_part = ">>"
        expected_symbols = ["sent"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_escaped_angle_brackets(self):
        input_str = r"\>\><sent>"
        expected_main_part = r"\>\>"
        expected_symbols = ["sent"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_mixed_content(self):
        input_str = r"d\>a<b>c<zx><uv>"
        expected_main_part = r"d\>a<b>c"
        expected_symbols = ["zx", "uv"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_multiple_symbols(self):
        input_str = "d<<c<zx><uv>"
        expected_main_part = "d<<c"
        expected_symbols = ["zx", "uv"]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols, expected_symbols)

    def test_trailing_space(self):
        input_str = "abc<zx><uv> "
        expected_main_part = "abc"
        expected_symbols = ["zx", "uv", " "]
        main_part, symbols = parseString(input_str)
        self.assertEqual(main_part, expected_main_part)
        self.assertEqual(symbols,expected_symbols)

if __name__ == "__main__":
    unittest.main()