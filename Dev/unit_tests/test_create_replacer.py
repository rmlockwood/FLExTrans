import sys
import os
import unittest
import regex
from unittest.mock import MagicMock

# ── Mock Qt and project-specific dependencies before importing TextInOutUtils ──
def _qt_class(name):
    return type(name, (object,), {
        '__init__': lambda self, *a, **kw: None,
        '__init_subclass__': classmethod(lambda cls, **kw: None),
    })

_mock_widgets = MagicMock()
for _n in ('QMainWindow', 'QComboBox', 'QWidget', 'QVBoxLayout', 'QTextEdit', 'QPushButton'):
    setattr(_mock_widgets, _n, _qt_class(_n))

_mock_gui = MagicMock()
for _n in ('QStandardItem', 'QStandardItemModel'):
    setattr(_mock_gui, _n, _qt_class(_n))

_mock_textinout = MagicMock()
_mock_textinout.Ui_TextInOutMainWindow = _qt_class('Ui_TextInOutMainWindow')

sys.modules.update({
    'FTPaths':          MagicMock(),
    'ReadConfig':       MagicMock(),
    'ClusterUtils':     MagicMock(),
    'TextInOut':        _mock_textinout,
    'PyQt6':            MagicMock(),
    'PyQt6.QtCore':     MagicMock(),
    'PyQt6.QtGui':      _mock_gui,
    'PyQt6.QtWidgets':  _mock_widgets,
})

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Lib')))
from TextInOutUtils import create_replacer


def sub(search, repl, text):
    """Apply create_replacer replacement via regex.sub."""
    return regex.sub(search, create_replacer(repl), text)


# ── Plain literals ────────────────────────────────────────────────────────────

class TestPlainLiterals(unittest.TestCase):

    def test_empty_replacement(self):
        self.assertEqual(sub(r'\w+', '', 'hello'), '')

    def test_single_char(self):
        self.assertEqual(sub(r'x', 'z', 'x'), 'z')

    def test_word(self):
        self.assertEqual(sub(r'x', 'hello', 'x'), 'hello')

    def test_with_space(self):
        self.assertEqual(sub(r'x', 'hello world', 'x'), 'hello world')

    def test_digits_only(self):
        self.assertEqual(sub(r'x', '42', 'x'), '42')

    def test_hyphen(self):
        self.assertEqual(sub(r'x', 'a-b', 'x'), 'a-b')

    def test_underscore(self):
        self.assertEqual(sub(r'x', 'a_b', 'x'), 'a_b')

    def test_period(self):
        self.assertEqual(sub(r'x', 'a.b', 'x'), 'a.b')

    def test_alphanumeric_mixed(self):
        self.assertEqual(sub(r'x', 'abc123', 'x'), 'abc123')

    def test_long_phrase(self):
        self.assertEqual(sub(r'x', 'the quick brown fox', 'x'), 'the quick brown fox')


# ── Basic backreferences ──────────────────────────────────────────────────────

class TestBackreferences(unittest.TestCase):

    def test_group1_identity(self):
        self.assertEqual(sub(r'(\w+)', r'\1', 'hello'), 'hello')

    def test_group2_only(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\2', 'hello world'), 'world')

    def test_both_groups_concatenated(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1\2', 'hello world'), 'helloworld')

    def test_literal_prefix_and_group(self):
        self.assertEqual(sub(r'(\w+)', r'pre\1', 'foo'), 'prefoo')

    def test_group_and_literal_suffix(self):
        self.assertEqual(sub(r'(\w+)', r'\1suf', 'foo'), 'foosuf')

    def test_surrounded_by_literals(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'pre\1mid\2end', 'hello world'), 'prehellomidworldend')

    def test_separator_between_groups(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1-\2', 'hello world'), 'hello-world')

    def test_same_group_twice(self):
        self.assertEqual(sub(r'(\w+)', r'\1\1', 'hi'), 'hihi')

    def test_third_group(self):
        self.assertEqual(sub(r'(\w+) (\w+) (\w+)', r'\3', 'a b c'), 'c')

    def test_group_with_digits(self):
        self.assertEqual(sub(r'(\d+)', r'[\1]', '123'), '[123]')

    def test_swap_two_words(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\2 \1', 'hello world'), 'world hello')

    def test_group0_whole_match(self):
        self.assertEqual(sub(r'\w+', r'\0', 'hello'), 'hello')

    def test_multiple_matches_in_input(self):
        self.assertEqual(sub(r'(\w+)', r'[\1]', 'foo bar'), '[foo] [bar]')

    def test_optional_group_not_matched(self):
        # Optional group that didn't participate returns empty string
        self.assertEqual(sub(r'(\w+)(X)?', r'\1\2', 'hello'), 'hello')

    def test_five_groups_reversed(self):
        self.assertEqual(sub(r'(\w) (\w) (\w) (\w) (\w)', r'\5\4\3\2\1', 'a b c d e'), 'edcba')


# ── \l — lowercase NEXT CHARACTER only (first char of group or literal char) ──

class TestLowercaseBackref(unittest.TestCase):

    def test_lowercase_first_char_of_uppercase_group(self):
        # \l only lowercases the first character; the rest is unchanged
        self.assertEqual(sub(r'([A-Z]+)', r'\l\1', 'HELLO'), 'hELLO')

    def test_already_lowercase_unchanged(self):
        self.assertEqual(sub(r'([a-z]+)', r'\l\1', 'hello'), 'hello')

    def test_lowercase_first_char_of_mixed_group(self):
        # Only the leading H is lowercased
        self.assertEqual(sub(r'(\w+)', r'\l\1', 'HeLLo'), 'heLLo')

    def test_lowercase_second_group(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1 \l\2', 'foo BAR'), 'foo bAR')

    def test_literal_char_uppercase_A(self):
        self.assertEqual(sub(r'x', r'\lA', 'x'), 'a')

    def test_literal_char_already_lowercase(self):
        self.assertEqual(sub(r'x', r'\la', 'x'), 'a')

    def test_literal_char_Z(self):
        self.assertEqual(sub(r'x', r'\lZ', 'x'), 'z')

    def test_digits_group_no_case_change(self):
        self.assertEqual(sub(r'(\d+)', r'\l\1', '123'), '123')

    def test_with_literal_prefix(self):
        self.assertEqual(sub(r'(\w+)', r'word:\l\1', 'HELLO'), 'word:hELLO')

    def test_with_literal_suffix(self):
        self.assertEqual(sub(r'(\w+)', r'\l\1.end', 'HELLO'), 'hELLO.end')

    def test_two_groups_first_char_lowercased(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\l\1 \l\2', 'FOO BAR'), 'fOO bAR')

    def test_single_char_uppercase_group(self):
        self.assertEqual(sub(r'(\w+)', r'\l\1', 'A'), 'a')

    def test_optional_group_empty_lowercased(self):
        # Optional group not matched → empty; group1 first char only is lowercased
        self.assertEqual(sub(r'(\w+)(X)?', r'\l\1\l\2', 'HELLO'), 'hELLO')

    def test_unicode_uppercase(self):
        # Only the leading C is lowercased
        self.assertEqual(sub(r'(\w+)', r'\l\1', 'CAFÉ'), 'cAFÉ')

    def test_three_groups_first_char_lowercased(self):
        self.assertEqual(sub(r'(\w+) (\w+) (\w+)', r'\l\1 \l\2 \l\3', 'FOO BAR BAZ'), 'fOO bAR bAZ')


# ── \u — uppercase NEXT CHARACTER only (first char of group or literal char) ──

class TestUppercaseBackref(unittest.TestCase):

    def test_uppercase_first_char_of_lowercase_group(self):
        # \u only uppercases the first character; the rest is unchanged
        self.assertEqual(sub(r'([a-z]+)', r'\u\1', 'hello'), 'Hello')

    def test_already_uppercase_unchanged(self):
        self.assertEqual(sub(r'([A-Z]+)', r'\u\1', 'HELLO'), 'HELLO')

    def test_uppercase_first_char_of_mixed_group(self):
        # Only the leading h is uppercased
        self.assertEqual(sub(r'(\w+)', r'\u\1', 'hElLo'), 'HElLo')

    def test_uppercase_second_group(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1 \u\2', 'foo bar'), 'foo Bar')

    def test_literal_char_lowercase_a(self):
        self.assertEqual(sub(r'x', r'\ua', 'x'), 'A')

    def test_literal_char_already_uppercase(self):
        self.assertEqual(sub(r'x', r'\uA', 'x'), 'A')

    def test_literal_char_z(self):
        self.assertEqual(sub(r'x', r'\uz', 'x'), 'Z')

    def test_digits_group_no_case_change(self):
        self.assertEqual(sub(r'(\d+)', r'\u\1', '123'), '123')

    def test_with_literal_prefix(self):
        self.assertEqual(sub(r'(\w+)', r'word:\u\1', 'hello'), 'word:Hello')

    def test_with_literal_suffix(self):
        self.assertEqual(sub(r'(\w+)', r'\u\1.end', 'hello'), 'Hello.end')

    def test_two_groups_first_char_uppercased(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\u\1 \u\2', 'foo bar'), 'Foo Bar')

    def test_single_char_lowercase_group(self):
        self.assertEqual(sub(r'(\w+)', r'\u\1', 'a'), 'A')

    def test_optional_group_empty_uppercased(self):
        # Optional group not matched → empty; group1 first char only is uppercased
        self.assertEqual(sub(r'(\w+)(X)?', r'\u\1\u\2', 'hello'), 'Hello')

    def test_unicode_lowercase(self):
        # Only the leading c is uppercased
        self.assertEqual(sub(r'(\w+)', r'\u\1', 'café'), 'Café')

    def test_three_groups_first_char_uppercased(self):
        self.assertEqual(sub(r'(\w+) (\w+) (\w+)', r'\u\1 \u\2 \u\3', 'foo bar baz'), 'Foo Bar Baz')


# ── \L...\E — lowercase literal section ──────────────────────────────────────

class TestLowercaseSection(unittest.TestCase):

    def test_uppercase_text_lowercased(self):
        self.assertEqual(sub(r'x', r'\LABC\E', 'x'), 'abc')

    def test_already_lowercase_unchanged(self):
        self.assertEqual(sub(r'x', r'\Labc\E', 'x'), 'abc')

    def test_mixed_with_space(self):
        self.assertEqual(sub(r'x', r'\LHello World\E', 'x'), 'hello world')

    def test_digits_unchanged(self):
        self.assertEqual(sub(r'x', r'\L123\E', 'x'), '123')

    def test_empty_section(self):
        self.assertEqual(sub(r'x', r'\L\E', 'x'), '')

    def test_literal_prefix_before_section(self):
        self.assertEqual(sub(r'x', r'text\LABC\E', 'x'), 'textabc')

    def test_literal_suffix_after_section(self):
        self.assertEqual(sub(r'x', r'\LABC\Etext', 'x'), 'abctext')

    def test_surrounded_by_literals(self):
        self.assertEqual(sub(r'x', r'before\LAFTER\Eend', 'x'), 'beforeafterend')

    def test_two_sections(self):
        self.assertEqual(sub(r'x', r'\LFOO\E-\LBAR\E', 'x'), 'foo-bar')

    def test_backref_inside_not_processed(self):
        # \1 inside \L...\E is NOT expanded; its chars are lowercased literally (\→\, 1→1)
        self.assertEqual(sub(r'(\w+)', r'\L\1\E', 'HELLO'), '\\1')


# ── \U...\E — uppercase literal section ──────────────────────────────────────

class TestUppercaseSection(unittest.TestCase):

    def test_lowercase_text_uppercased(self):
        self.assertEqual(sub(r'x', r'\Uabc\E', 'x'), 'ABC')

    def test_already_uppercase_unchanged(self):
        self.assertEqual(sub(r'x', r'\UABC\E', 'x'), 'ABC')

    def test_mixed_with_space(self):
        self.assertEqual(sub(r'x', r'\UHello World\E', 'x'), 'HELLO WORLD')

    def test_digits_unchanged(self):
        self.assertEqual(sub(r'x', r'\U123\E', 'x'), '123')

    def test_empty_section(self):
        self.assertEqual(sub(r'x', r'\U\E', 'x'), '')

    def test_literal_prefix_before_section(self):
        self.assertEqual(sub(r'x', r'text\Uabc\E', 'x'), 'textABC')

    def test_literal_suffix_after_section(self):
        self.assertEqual(sub(r'x', r'\Uabc\Etext', 'x'), 'ABCtext')

    def test_surrounded_by_literals(self):
        self.assertEqual(sub(r'x', r'before\Uafter\Eend', 'x'), 'beforeAFTERend')

    def test_two_sections(self):
        self.assertEqual(sub(r'x', r'\Ufoo\E-\Ubar\E', 'x'), 'FOO-BAR')

    def test_backref_inside_not_processed(self):
        # \1 inside \U...\E is NOT expanded; its chars are uppercased literally (\→\, 1→1)
        self.assertEqual(sub(r'(\w+)', r'\U\1\E', 'hello'), '\\1')


# ── Mixed / complex patterns ──────────────────────────────────────────────────

class TestMixedPatterns(unittest.TestCase):

    def test_uppercase_first_char_first_group_lowercase_first_char_second(self):
        # \u and \l each affect only the first character of their respective group
        self.assertEqual(sub(r'(\w+) (\w+)', r'\u\1 \l\2', 'hello WORLD'), 'Hello wORLD')

    def test_lowercase_first_char_first_group_uppercase_first_char_second(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\l\1 \u\2', 'HELLO world'), 'hELLO World')

    def test_L_section_backref_U_section(self):
        # \LABC\E gives 'abc', \1 gives group, \UDEF\E gives 'DEF'
        self.assertEqual(sub(r'(\w+)', r'\LABC\E\1\UDEF\E', 'x'), 'abcxDEF')

    def test_possessive_form(self):
        # \u capitalizes only the first character of the group
        self.assertEqual(sub(r'(\w+)', r"\u\1's", 'dog'), "Dog's")

    def test_swap_and_capitalize_first_char(self):
        # \u on each group capitalizes only the first character after swapping
        self.assertEqual(sub(r'(\w+) (\w+)', r'\u\2 \u\1', 'hello world'), 'World Hello')

    def test_three_groups_first_char_lowercased(self):
        self.assertEqual(sub(r'(\w+) (\w+) (\w+)', r'\l\1 \l\2 \l\3', 'FOO BAR BAZ'), 'fOO bAR bAZ')

    def test_three_groups_first_char_uppercased(self):
        self.assertEqual(sub(r'(\w+) (\w+) (\w+)', r'\u\1 \u\2 \u\3', 'foo bar baz'), 'Foo Bar Baz')

    def test_multiple_matches_first_char_lowercased(self):
        # Each match: only first character lowercased
        self.assertEqual(sub(r'([A-Z]+)', r'\l\1', 'FOO BAR'), 'fOO bAR')

    def test_u_on_single_char_group_then_l_on_rest(self):
        # \u\1 uppercases single-char group1; \l\2 lowercases first char of group2
        self.assertEqual(sub(r'(\w)(\w+)', r'\u\1\l\2', 'hELLO'), 'HeLLO')

    def test_upper_lower_separator(self):
        # \u capitalizes first char of group1; \l lowercases first char of group2
        self.assertEqual(sub(r'(\w+)-(\w+)', r'\u\1_\l\2', 'hello-WORLD'), 'Hello_wORLD')

    def test_five_groups_reversed(self):
        self.assertEqual(sub(r'(\w) (\w) (\w) (\w) (\w)', r'\5\4\3\2\1', 'a b c d e'), 'edcba')

    def test_u_and_l_on_single_char_groups_capitalize(self):
        # When groups are single chars, \u\1\l\2 capitalizes each word correctly
        self.assertEqual(sub(r'(\w)(\w*)', r'\u\1\l\2', 'hELLO wORLD fOO'), 'HeLLO WoRLD FoO')

    def test_L_section_then_group_then_U_section(self):
        self.assertEqual(sub(r'(\w+)', r'\lf\u\1\LEND\E', 'TEST'), 'fTEST' + 'end')

    def test_u_on_every_match_capitalizes_first_char(self):
        # Each word: first char uppercased, rest unchanged
        self.assertEqual(sub(r'(\w+)', r'\u\1', 'foo bar baz'), 'Foo Bar Baz')

    def test_literal_l_uppercase_A_then_u_uppercase_Z(self):
        # \lA → 'a', \uZ → 'Z'
        self.assertEqual(sub(r'x', r'\lA\uZ', 'x'), 'aZ')


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases(unittest.TestCase):

    def test_trailing_backslash_l(self):
        # Pattern ends with \l (no following char to process): outputs literal \l
        self.assertEqual(sub(r'x', r'\l', 'x'), '\\l')

    def test_trailing_backslash_u(self):
        # Pattern ends with \u (no following char to process): outputs literal \u
        self.assertEqual(sub(r'x', r'\u', 'x'), '\\u')

    def test_l_with_literal_non_backslash_char(self):
        # \lM → 'm' (M is not a backref, just lowercased)
        self.assertEqual(sub(r'x', r'\lM', 'x'), 'm')

    def test_u_with_literal_non_backslash_char(self):
        # \um → 'M'
        self.assertEqual(sub(r'x', r'\um', 'x'), 'M')

    def test_optional_group_none_returns_empty(self):
        # \1 where group didn't match → '' (None or "")
        self.assertEqual(sub(r'(\w+)(X)?', r'\1[\2]', 'hello'), 'hello[]')

    def test_L_section_ends_at_first_E(self):
        # \L processes until first \E; text after \E is literal
        self.assertEqual(sub(r'x', r'\LABC\EDEF', 'x'), 'abcDEF')

    def test_U_section_ends_at_first_E(self):
        self.assertEqual(sub(r'x', r'\Uabc\EDEF', 'x'), 'ABCDEF')

    def test_group_with_punctuation_no_case_change(self):
        # Punctuation has no case; lower() leaves it unchanged
        self.assertEqual(sub(r'([!?]+)', r'\l\1', '!?!'), '!?!')

    def test_multiple_consecutive_backrefs(self):
        self.assertEqual(sub(r'(\w)(\w)(\w)', r'\3\2\1', 'abc'), 'cba')

    def test_u_and_l_on_split_word_groups(self):
        # \u uppercases first char of single-char group; \l lowercases first char of rest.
        # Words already starting correctly are unchanged; mixed-case tails are only
        # partially corrected (first char of tail lowercased, rest unchanged).
        self.assertEqual(sub(r'(\w)(\w*)', r'\u\1\l\2', 'the QUICK brown FOX'), 'The QuICK Brown FoX')


# ── Passthrough: other \ sequences must not be altered ───────────────────────
#
# Sequences not in {0-9, l, u, L, U} fall through to the else branch, which
# outputs the backslash and then the next character separately.  The resulting
# 2-char string is passed verbatim to regex.sub (callable API, no re-escaping).
#
# This class guards against future edits accidentally hijacking any of these.

class TestPassthroughEscapes(unittest.TestCase):

    # ── regex character-class shorthands ─────────────────────────────────────

    def test_backslash_s_passes_through(self):
        self.assertEqual(sub(r'x', r'\s', 'x'), '\\s')

    def test_backslash_w_passes_through(self):
        self.assertEqual(sub(r'x', r'\w', 'x'), '\\w')

    def test_backslash_d_passes_through(self):
        self.assertEqual(sub(r'x', r'\d', 'x'), '\\d')

    def test_backslash_b_passes_through(self):
        self.assertEqual(sub(r'x', r'\b', 'x'), '\\b')

    def test_backslash_S_passes_through(self):
        self.assertEqual(sub(r'x', r'\S', 'x'), '\\S')

    def test_backslash_W_passes_through(self):
        self.assertEqual(sub(r'x', r'\W', 'x'), '\\W')

    def test_backslash_D_passes_through(self):
        self.assertEqual(sub(r'x', r'\D', 'x'), '\\D')

    def test_backslash_B_passes_through(self):
        self.assertEqual(sub(r'x', r'\B', 'x'), '\\B')

    # ── regex anchors ─────────────────────────────────────────────────────────

    def test_backslash_A_passes_through(self):
        self.assertEqual(sub(r'x', r'\A', 'x'), '\\A')

    def test_backslash_Z_passes_through(self):
        self.assertEqual(sub(r'x', r'\Z', 'x'), '\\Z')

    def test_backslash_z_passes_through(self):
        self.assertEqual(sub(r'x', r'\z', 'x'), '\\z')

    def test_backslash_G_passes_through(self):
        self.assertEqual(sub(r'x', r'\G', 'x'), '\\G')

    # ── common string escapes ─────────────────────────────────────────────────

    def test_backslash_n_passes_through_as_literal(self):
        # \n is NOT converted to a newline; it passes through as the 2-char string
        result = sub(r'x', r'\n', 'x')
        self.assertEqual(result, '\\n')
        self.assertNotEqual(result, '\n')   # not a real newline

    def test_backslash_t_passes_through_as_literal(self):
        result = sub(r'x', r'\t', 'x')
        self.assertEqual(result, '\\t')
        self.assertNotEqual(result, '\t')

    def test_backslash_r_passes_through(self):
        self.assertEqual(sub(r'x', r'\r', 'x'), '\\r')

    def test_backslash_f_passes_through(self):
        self.assertEqual(sub(r'x', r'\f', 'x'), '\\f')

    def test_backslash_v_passes_through(self):
        self.assertEqual(sub(r'x', r'\v', 'x'), '\\v')

    def test_backslash_a_passes_through(self):
        self.assertEqual(sub(r'x', r'\a', 'x'), '\\a')

    # ── other letters not used by create_replacer ─────────────────────────────

    def test_backslash_e_passes_through(self):
        self.assertEqual(sub(r'x', r'\e', 'x'), '\\e')

    def test_backslash_p_passes_through(self):
        # \p{...} is used for Unicode properties in some engines; literal here
        self.assertEqual(sub(r'x', r'\p', 'x'), '\\p')

    def test_backslash_g_passes_through(self):
        # \g<name> named-group syntax; literal here
        self.assertEqual(sub(r'x', r'\g', 'x'), '\\g')

    def test_backslash_x_passes_through(self):
        self.assertEqual(sub(r'x', r'\x', 'x'), '\\x')

    def test_backslash_E_outside_section_passes_through(self):
        # \E only has meaning as a terminator inside \L...\E or \U...\E
        self.assertEqual(sub(r'x', r'\E', 'x'), '\\E')

    def test_backslash_c_passes_through(self):
        self.assertEqual(sub(r'x', r'\c', 'x'), '\\c')

    def test_backslash_i_passes_through(self):
        self.assertEqual(sub(r'x', r'\i', 'x'), '\\i')

    def test_backslash_k_passes_through(self):
        # \k<name> backreference syntax in some engines; literal here
        self.assertEqual(sub(r'x', r'\k', 'x'), '\\k')

    def test_backslash_q_passes_through(self):
        self.assertEqual(sub(r'x', r'\q', 'x'), '\\q')

    # ── double backslash ──────────────────────────────────────────────────────

    def test_double_backslash_passes_through(self):
        # \\ → \\ (two backslashes in, two backslashes out)
        self.assertEqual(sub(r'x', '\\\\', 'x'), '\\\\')

    # ── passthrough mixed with valid sequences ─────────────────────────────────

    def test_backref_then_backslash_n(self):
        # \1 is expanded; the following \n passes through literally
        self.assertEqual(sub(r'(\w+)', r'\1\n', 'hello'), 'hello\\n')

    def test_backslash_n_between_backrefs(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1\n\2', 'hello world'), 'hello\\nworld')

    def test_backslash_t_between_backrefs(self):
        self.assertEqual(sub(r'(\w+) (\w+)', r'\1\t\2', 'foo bar'), 'foo\\tbar')

    def test_backslash_s_after_backref(self):
        self.assertEqual(sub(r'(\w+)', r'\1\s', 'foo'), 'foo\\s')

    def test_backslash_w_before_backref(self):
        self.assertEqual(sub(r'(\w+)', r'\w\1', 'foo'), '\\wfoo')

    def test_backslash_d_adjacent_to_l_sequence(self):
        # \l\1 lowercases first char of group only; \d after it passes through
        self.assertEqual(sub(r'(\w+)', r'\l\1\d', 'HELLO'), 'hELLO\\d')

    def test_backslash_s_adjacent_to_u_sequence(self):
        # \u\1 uppercases first char of group only; \s before it passes through
        self.assertEqual(sub(r'(\w+)', r'\s\u\1', 'hello'), '\\sHello')

    def test_backslash_n_inside_L_section_lowercased_literally(self):
        # Inside \L...\E the chars of the pattern are lowercased; \n → \n (no change)
        self.assertEqual(sub(r'x', r'\L\n\E', 'x'), '\\n')

    def test_multiple_passthrough_escapes_in_sequence(self):
        self.assertEqual(sub(r'x', r'\s\w\d', 'x'), '\\s\\w\\d')


if __name__ == '__main__':
    unittest.main()
