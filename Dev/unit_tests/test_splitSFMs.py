import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL before ChapterSelection loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

from ChapterSelection import splitSFMs

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
        input_str = r"the beginning \w God|Yahweh\w* created"
        expected_output = ['the beginning ', '\\w', ' God', '|', 'Yahweh', '\\w*', ' created']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_with_target_ref_embedded_in_footnote(self): # from qvm Exo. 1:5
        input_str = "chayarqan.\\f + \\fr 1.5 \\ft Septuaginta \\xt Hech. 7.14\\xt* niykan.\\f* Tsurin \\x + \\xo 1.1-5 \\xt Gén. 46.8-27.\\x*"
        expected_output = ['chayarqan.', '\\f + ', '', '\\fr 1.5', ' ', '\\ft', ' Septuaginta ', '\\xt Hech. 7.14\\xt*', ' niykan.', '\\f*', ' Tsurin ', '\\x + ', '', '\\xo 1.1-5', ' ', '\\xt Gén. 46.8-27.\\x*', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_split_dashes_variants_between_digits(self): 
                                   #m-dash,                  en-dash,                        wave dash,        figure dash
        input_str = "z\\f + \\fr 1.5—6 \\ft z \\xt Hech. 7.14–15\\xt* z.\\f* z \\x + \\xo 1.1〜5 \\xt Gén. 46.8‒27.\\x*"
        expected_output = ['z', '\\f + ', '', '\\fr 1.5—6', ' ', '\\ft', ' z ', '\\xt Hech. 7.14–15\\xt*', ' z.', '\\f*', ' z ', '\\x + ', '', '\\xo 1.1〜5', ' ', '\\xt Gén. 46.8‒27.\\x*', '']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_parallel_reference_with_additional_verses(self): 
        input_str = "\\r (Maleke 13:32-37; // Luke 17:26-30, 34-36)"
        expected_output = ['', '\\r', ' (Maleke ', '13:32-37', '; // Luke ', '17:26-30, 34-36', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_parallel_reference_with_several_additional_ranges(self): 
        input_str = "\\r (Luke 17:26-30, 34-36, 39-40)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30, 34-36, 39-40', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_parallel_reference_ending_in_a_single_verse(self): 
        input_str = "\\r (Luke 17:26-30, 34-36, 41)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30, 34-36, 41', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # A comma followed by a new chapter:verse reference is not part of the verse list, so it gets split off on its own.
    def test_parallel_reference_followed_by_new_chapter_verse(self): 
        input_str = "\\r (Luke 17:26-30, 18:1)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30', ', ', '18:1', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # A range that crosses a chapter boundary has to stay whole. Before, it broke after 1:2-3 and the leftover :4 was treated as vernacular text.
    def test_reference_range_crossing_a_chapter_boundary(self): 
        input_str = "\\r (Mat 1:2-3:4)"
        expected_output = ['', '\\r', ' (Mat ', '1:2-3:4', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_reference_range_crossing_a_chapter_boundary_with_dots(self): 
        input_str = "\\r (Mat 1.2-3.4)"
        expected_output = ['', '\\r', ' (Mat ', '1.2-3.4', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # Two cross-chapter ranges in a row each get matched on their own; the comma between them is ordinary text.
    def test_two_reference_ranges_crossing_chapter_boundaries(self): 
        input_str = "\\r (Mat 1:2-3:4, 5:6-7)"
        expected_output = ['', '\\r', ' (Mat ', '1:2-3:4', ', ', '5:6-7', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # Verse lists can be separated by commas other than the ASCII one. The commas are written as \u escapes because several of them look identical on screen.
    def test_verse_list_with_arabic_comma(self): # right-to-left scripts use U+060C, not U+002C
        input_str = "\\r (Luke 17:26-30\u060C 34-36\u060C 41)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30\u060C 34-36\u060C 41', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_verse_list_with_ethiopic_comma(self): 
        input_str = "\\r (Luke 17:26-30\u1363 34-36)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30\u1363 34-36', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    def test_verse_list_with_fullwidth_comma(self): 
        input_str = "\\r (Luke 17:26-30\uFF0C 34-36)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30\uFF0C 34-36', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # A comma needn't be followed by a space.
    def test_verse_list_with_arabic_comma_and_no_space(self): 
        input_str = "\\r (Luke 17:26-30\u060C34-36)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30\u060C34-36', ')']
        self.assertEqual(splitSFMs(input_str), expected_output)

    # U+066B is the Arabic decimal separator, not a comma, so it must not continue the verse list.
    def test_arabic_decimal_separator_does_not_continue_the_list(self): 
        input_str = "\\r (Luke 17:26-30\u066B 34)"
        expected_output = ['', '\\r', ' (Luke ', '17:26-30', '\u066B 34)']
        self.assertEqual(splitSFMs(input_str), expected_output)

if __name__ == "__main__":
    unittest.main()