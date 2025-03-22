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

from Utils import splitSFMs

class TestSplitSFMs(unittest.TestCase):

    def test_split_chap_sec_par_ver(self):
        input_str = "\\c 22\n\\s Tayta Diosta Abraham cäsukunqan\n\\p\n\\v 1 Chaypita "
        expected_output = ['', '\\c 22', '', '\n', '', '\\s', ' Tayta Diosta Abraham cäsukunqan', '\n', '', '\\p', '', '\n', '', '\\v 1 ', 'Chaypita ']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_basic_split(self):
        input_str = "\\v 1 In the beginning God created the heaven and the earth."
        expected_output = ['', '\\v 1 ', 'In the beginning God created the heaven and the earth.']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_verse_dash(self):
        input_str = "\\v 11-12 In the beginning God created the heaven and the earth."
        expected_output = ['', '\\v 11-12 ', 'In the beginning God created the heaven and the earth.']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_newline(self):
        input_str = "\\v 1 In the beginning\n\\v 2 And the earth was without form"
        expected_output = ['', '\\v 1 ', 'In the beginning', '\n', '', '\\v 2 ', 'And the earth was without form']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_fig_over_two_lines(self):
        input_str = '\\p Chawrasqa \\fig Isaacta Abraham|alt="Abraham about" src="LB00291B.\nTIF" size="col" loc="GEN 22.9-12" copy="LB" ref="22.9-12"\\fig*'
        expected_output = ['', '\\p', ' Chawrasqa ', '\\fig', ' Isaacta Abraham', '|alt="Abraham about" src="LB00291B.\nTIF" size="col" loc="GEN 22.9-12" copy="LB" ref="22.9-12"\\fig*', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_attributes(self):
        input_str = "\\fig |x=123 \\fig* In the beginning"
        expected_output = ['', '\\fig', ' ', '|x=123 \\fig*', ' In the beginning']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_footnote(self):
        input_str = "\\v 1 In the beginning\\f + \\fr 1:1 \\ft footnote text\\f*"
        expected_output = ['', '\\v 1 ', 'In the beginning', '\\f + ', '', '\\fr 1:1', ' ', '\\ft', ' footnote text', '\\f*', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_cross_reference(self):
        input_str = "\\v 1 In the beginning\\x + \\xo 1:1 \\xt cross reference\\x*"
        expected_output = ['', '\\v 1 ', 'In the beginning', '\\x + ', '', '\\xo 1:1', ' ', '\\xt cross reference\\x*', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_chapter_and_verse(self):
        input_str = "\\c 1\\v 1 In the beginning"
        expected_output = ['', '\\c 1', '', '\\v 1 ', 'In the beginning']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_remark(self):
        input_str = "\\rem This is a remark\n\\v 1 In the beginning"
        expected_output = ['', '\\rem This is a remark\n', '', '\\v 1 ', 'In the beginning']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_verse_reference(self):
        input_str = "\\r Mark 1:1-2"
        expected_output = ['', '\\r', ' Mark ', '1:1-2', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_verse_reference1(self):
        input_str = "\\r Mark 1:12"
        expected_output = ['', '\\r', ' Mark ', '1:12', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_verse_reference2(self):
        input_str = "\\v 1 In the beginning 1:1-2"
        expected_output = ['', '\\v 1 ', 'In the beginning ', '1:1-2', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_marker_preceded_by_plus(self):
        input_str = "\\v 1 In the beginning\\+add additional text"
        expected_output = ['', '\\v 1 ', 'In the beginning', '\\+add', ' additional text']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_glossary_term(self):
        input_str = "the beginning \\w God|Yahweh\w* created"
        expected_output = ['the beginning ', '\\w', ' God', '|', 'Yahweh', '\\w*', ' created']
        self.assertEqual(splitSFMs(input_str), expected_output)

if __name__ == "__main__":
    unittest.main()