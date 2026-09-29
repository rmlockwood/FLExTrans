import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL before ChapterSelection loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

from ChapterSelection import splitNumbers

# splitNumbers() returns re.split output with one capturing group, so the list alternates text, number, text, ... and the odd-numbered items are the numbers that
# insertParagraphs() puts in the analysis WS. Most tests check the whole list; numbersIn() pulls out just the numbers for the tests where that's all that matters.
def numbersIn(pieces):

    return pieces[1::2]

class TestSplitNumbers(unittest.TestCase):

    def assertSplit(self, inputStr, numberSeparators, expectedOutput):

        result = splitNumbers(inputStr, numberSeparators)
        self.assertEqual(result, expectedOutput)

        # Splitting must never lose or change text: joined back together the pieces are the input again.
        self.assertEqual(''.join(result), inputStr)

    # Basics

    def test_empty_string(self):
        self.assertSplit('', ',', [''])

    def test_no_numbers(self):
        self.assertSplit('In the beginning God created', ',', ['In the beginning God created'])

    def test_single_digit(self):
        self.assertSplit('there were 7 angels', ',', ['there were ', '7', ' angels'])

    def test_number_alone(self):
        self.assertSplit('42', ',', ['', '42', ''])

    def test_number_at_start(self):
        self.assertSplit('12 tribes', ',', ['', '12', ' tribes'])

    def test_number_at_end(self):
        self.assertSplit('the tribes were 12', ',', ['the tribes were ', '12', ''])

    def test_several_numbers(self):
        self.assertSplit('5 loaves and 2 fish fed 5000', ',', ['', '5', ' loaves and ', '2', ' fish fed ', '5000', ''])

    def test_number_in_parentheses(self):
        self.assertSplit('the rest (12) remained', ',', ['the rest (', '12', ') remained'])

    # Thousands separators

    def test_comma_thousands(self):
        self.assertSplit('I heard 144,000 sealed', ',', ['I heard ', '144,000', ' sealed'])

    def test_comma_millions(self):
        self.assertSplit('about 1,000,000 people', ',', ['about ', '1,000,000', ' people'])

    def test_period_thousands(self):
        self.assertSplit('about 1.000.000 people', '.', ['about ', '1.000.000', ' people'])

    def test_space_thousands(self):
        self.assertSplit('3 000 sheep', ' ', ['', '3 000', ' sheep'])

    def test_no_break_space_thousands(self):
        self.assertSplit('3 000 sheep', ' ', ['', '3 000', ' sheep'])

    def test_narrow_no_break_space_thousands(self):
        self.assertSplit('3 000 sheep', ' ', ['', '3 000', ' sheep'])

    def test_apostrophe_thousands(self):
        self.assertSplit("3'000 sheep", "'", ['', "3'000", ' sheep'])

    # Thousands plus decimal

    def test_thousands_and_decimal_both_given(self):
        self.assertSplit('it cost 3,000.25 denarii', ',.', ['it cost ', '3,000.25', ' denarii'])

    def test_thousands_and_decimal_given_in_other_order(self):
        self.assertSplit('it cost 3,000.25 denarii', '.,', ['it cost ', '3,000.25', ' denarii'])

    def test_european_thousands_and_decimal(self):
        self.assertSplit('it cost 3.000,25 denarii', '.,', ['it cost ', '3.000,25', ' denarii'])

    def test_thousands_and_decimal_only_comma_given(self):

        # The period isn't a separator, so the number stops at it; the 25 after it is then a number of its own because a period isn't a word character.
        self.assertSplit('it cost 3,000.25 denarii', ',', ['it cost ', '3,000', '.', '25', ' denarii'])

    def test_thousands_and_decimal_only_period_given(self):
        self.assertSplit('it cost 3,000.25 denarii', '.', ['it cost ', '3', ',', '000.25', ' denarii'])

    def test_decimal_only(self):
        self.assertSplit('about 0.5 of it', ',.', ['about ', '0.5', ' of it'])

    def test_space_thousands_and_comma_decimal(self):
        self.assertSplit('3 000,25 denarii', ' ,', ['', '3 000,25', ' denarii'])

    # A separator only counts when a digit follows it

    def test_trailing_comma_stays_text(self):
        self.assertSplit('he gave 7, and more', ',', ['he gave ', '7', ', and more'])

    def test_sentence_end_period_stays_text(self):
        self.assertSplit('in the year 1990.', '.', ['in the year ', '1990', '.'])

    def test_number_then_comma_then_number_with_space(self):

        # "7, 8" is a list of two numbers, not one number, because a space follows the comma.
        self.assertSplit('verses 7, 8 and 9', ',', ['verses ', '7', ', ', '8', ' and ', '9', ''])

    def test_comma_list_without_spaces_is_one_number(self):

        # Without spaces there's no way to tell "1,2,3" from a grouped number, so it's taken as one. Either way it all ends up in the analysis WS.
        self.assertSplit('items 1,2,3 here', ',', ['items ', '1,2,3', ' here'])

    def test_leading_separator_stays_text(self):
        self.assertSplit('about ,5 of it', ',', ['about ,', '5', ' of it'])

    def test_double_separator_breaks_number(self):
        self.assertSplit('1,,000', ',', ['', '1', ',,', '000', ''])

    def test_space_separator_at_end_of_number(self):
        self.assertSplit('7 angels', ' ', ['', '7', ' angels'])

    def test_space_separator_joins_adjacent_numbers(self):

        # With a space as the separator, two numbers with a single space between them look like one grouped number. That's the trade-off of choosing a space.
        self.assertSplit('chapter 3 4 men', ' ', ['chapter ', '3 4', ' men'])

    # Empty separator box

    def test_no_separators_splits_at_comma(self):
        self.assertSplit('I heard 144,000 sealed', '', ['I heard ', '144', ',', '000', ' sealed'])

    def test_no_separators_plain_number(self):
        self.assertSplit('there were 7 angels', '', ['there were ', '7', ' angels'])

    def test_no_separators_word_attached(self):
        self.assertSplit('the 7th day', '', ['the 7th day'])

    # Digits touching word characters stay part of the word

    def test_ordinal_suffix(self):
        self.assertSplit('the 7th day', ',', ['the 7th day'])

    def test_letters_before_digits(self):
        self.assertSplit('abc123 here', ',', ['abc123 here'])

    def test_digits_inside_word(self):
        self.assertSplit('x2y', ',', ['x2y'])

    def test_underscore_before_digits(self):
        self.assertSplit('_5 here', ',', ['_5 here'])

    def test_non_ascii_letter_before_digits(self):
        self.assertSplit('ñ5 here', ',', ['ñ5 here'])

    def test_combining_mark_after_digits(self):

        # A combining mark is a word character, so the digit it sits on stays with the text.
        self.assertSplit('5́ here', ',', ['5́ here'])

    def test_grouped_number_touching_letters(self):
        self.assertSplit('144,000th time', ',', ['144,000th time'])

    def test_no_partial_match_by_backtracking(self):

        # The possessive quantifiers stop the engine from backing off to "12,3" or "12" to get a match, so the whole token stays text, the same as 7th does.
        self.assertSplit('12,34abc', ',', ['12,34abc'])

    def test_no_partial_match_by_backtracking_without_separators(self):
        self.assertSplit('123abc', '', ['123abc'])

    def test_number_after_hyphen(self):
        self.assertSplit('minus -5 here', ',', ['minus -', '5', ' here'])

    # Non-ASCII digits and separators

    def test_arabic_indic_digits(self):
        self.assertSplit('x ٣٤٥ y', ',', ['x ', '٣٤٥', ' y'])

    def test_devanagari_digits(self):
        self.assertSplit('x १२३ y', ',', ['x ', '१२३', ' y'])

    def test_arabic_thousands_separator(self):
        self.assertSplit('x ١٬٠٠٠ y', '٬', ['x ', '١٬٠٠٠', ' y'])

    def test_arabic_thousands_and_decimal_separators(self):
        self.assertSplit('x ٣٬٠٠٠٫٢٥ y', '٬٫', ['x ', '٣٬٠٠٠٫٢٥', ' y'])

    def test_arabic_letter_before_digits(self):
        self.assertSplit('ب٣ y', ',', ['ب٣ y'])

    # Separators that mean something in a regex character class must be taken literally

    def test_close_bracket_separator(self):
        self.assertSplit('a 1]2 b', ']', ['a ', '1]2', ' b'])

    def test_hyphen_separator(self):
        self.assertSplit('a 3-4 b', '-', ['a ', '3-4', ' b'])

    def test_caret_separator(self):
        self.assertSplit('a 5^6 b', '^', ['a ', '5^6', ' b'])

    def test_backslash_separator(self):
        self.assertSplit('a 7\\8 b', '\\', ['a ', '7\\8', ' b'])

    def test_hyphen_between_separators_is_not_a_range(self):

        # Unescaped, "+-/" would be the range + to / in a character class, which includes the comma and the period.
        self.assertSplit('a 1,2 and 3.4 b', '+-/', ['a ', '1', ',', '2', ' and ', '3', '.', '4', ' b'])

    def test_hyphen_between_separators_still_matches_each(self):
        self.assertSplit('a 1+2-3/4 b', '+-/', ['a ', '1+2-3/4', ' b'])

    def test_dot_separator_is_literal(self):

        # Unescaped outside a class, . would match anything; here it must only match a period.
        self.assertSplit('a 1x2 and 3.4 b', '.', ['a 1x2 and ', '3.4', ' b'])

    # The numbers themselves

    def test_numbers_in_mixed_text(self):
        result = splitNumbers('Of the 12 tribes, 144,000 were sealed; 3,000.25 was paid on day 7.', ',.')
        self.assertEqual(numbersIn(result), ['12', '144,000', '3,000.25', '7'])

if __name__ == '__main__':
    unittest.main()
