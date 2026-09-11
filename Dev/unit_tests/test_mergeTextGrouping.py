import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL before FLExTrans modules load

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

from MergeTextsUtils import (parseTextName, chapterPadWidth, naturalSortKey, textNameSortKey, groupTextNames, mergedTextName, chapterCoverage)

class TestParseTextName(unittest.TestCase):

    def test_zero_padded_chapter(self):
        self.assertEqual(parseTextName('Matthew 01'), ('Matthew', 1, None, ''))

    def test_unpadded_chapter(self):
        self.assertEqual(parseTextName('Matthew 7'), ('Matthew', 7, None, ''))

    def test_zero_padded_span(self):
        self.assertEqual(parseTextName('Matthew 03-04'), ('Matthew', 3, 4, ''))

    def test_unpadded_span(self):
        self.assertEqual(parseTextName('Matthew 3-4'), ('Matthew', 3, 4, ''))

    def test_span_with_spaces_around_the_hyphen(self):
        self.assertEqual(parseTextName('Matthew 03 - 04'), ('Matthew', 3, 4, ''))

    # This is the case that depends on the base of CHAPTER_TOKEN_RE being lazy (.*?) rather than greedy (.*). A greedy base would stretch to 'Matthew 03' and report chapter 4 of a book that does
    # not exist, losing the span. If this test starts failing, check whether somebody removed the '?' from the base.
    def test_span_needs_a_lazy_base(self):
        baseName, chapFrom, chapTo, _suffix = parseTextName('Matthew 03-04')
        self.assertEqual(baseName, 'Matthew')
        self.assertEqual((chapFrom, chapTo), (3, 4))

    # A numbered book name and a span at once - both halves of the pattern under load together.
    def test_numbered_book_with_a_span(self):
        self.assertEqual(parseTextName('1 Kings 05-06'), ('1 Kings', 5, 6, ''))

    # A book whose own name starts with a number must not be split on that number. What protects this is that the separator has to be followed by digits, so 'Kings' cannot end the base.
    def test_book_name_starting_with_a_number(self):
        self.assertEqual(parseTextName('1 Kings 05'), ('1 Kings', 5, None, ''))

    def test_underscore_separator(self):
        self.assertEqual(parseTextName('MAT_01'), ('MAT', 1, None, ''))

    def test_three_digit_chapter(self):
        self.assertEqual(parseTextName('Psalm 119'), ('Psalm', 119, None, ''))

    def test_no_chapter_at_all(self):
        self.assertEqual(parseTextName('Matthew'), ('Matthew', None, None, ''))

    # A four digit run is not a chapter. Without the three digit cap this would come back as book 'Field notes 2' chapter 202, and the text would be grouped with real chapters.
    def test_four_digit_run_is_not_a_chapter(self):
        self.assertEqual(parseTextName('Field notes 2024'), ('Field notes 2024', None, None, ''))

    def test_copy_suffix(self):
        self.assertEqual(parseTextName('Matthew 01 - Copy'), ('Matthew', 1, None, ' - Copy'))

    def test_numbered_copy_suffix(self):
        self.assertEqual(parseTextName('Matthew 01 - Copy (2)'), ('Matthew', 1, None, ' - Copy (2)'))

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(parseTextName('  Matthew 01  '), ('Matthew', 1, None, ''))

class TestChapterPadWidth(unittest.TestCase):

    def test_padded(self):
        self.assertEqual(chapterPadWidth('Matthew 01'), 2)

    def test_unpadded(self):
        self.assertEqual(chapterPadWidth('Matthew 7'), 1)

    def test_span_takes_the_wider_side(self):
        self.assertEqual(chapterPadWidth('Matthew 9-10'), 2)

    def test_three_digits(self):
        self.assertEqual(chapterPadWidth('Psalm 119'), 3)

    def test_no_chapter(self):
        self.assertEqual(chapterPadWidth('Field notes'), 0)

class TestNaturalSortKey(unittest.TestCase):

    def test_digits_compare_as_numbers(self):
        self.assertEqual(sorted(['Text 10', 'Text 9', 'Text 2'], key=naturalSortKey), ['Text 2', 'Text 9', 'Text 10'])

    def test_case_insensitive(self):
        self.assertEqual(sorted(['beta', 'Alpha'], key=naturalSortKey), ['Alpha', 'beta'])

    # Mixed digit and text pieces must never be compared against each other, which would raise a TypeError.
    def test_mixed_shapes_do_not_raise(self):
        self.assertEqual(sorted(['Text', 'Text 1', '5 Text'], key=naturalSortKey), ['5 Text', 'Text', 'Text 1'])

class TestTextNameSortKey(unittest.TestCase):

    # The headline case: a span sorts by the chapter it starts at, so 'Matthew 03-04' lands between 02 and 05.
    def test_span_sorts_between_its_neighbours(self):
        shuffled = ['Matthew 05', 'Matthew 02', 'Matthew 03-04', 'Matthew 01']
        expected = ['Matthew 01', 'Matthew 02', 'Matthew 03-04', 'Matthew 05']
        self.assertEqual(sorted(shuffled, key=textNameSortKey), expected)

    def test_full_book_in_reading_order(self):
        names = ['Matthew %02d' % chapNum for chapNum in range(1, 29)]
        shuffled = list(reversed(names))
        self.assertEqual(sorted(shuffled, key=textNameSortKey), names)

    # Zero padded names would sort correctly as plain strings; unpadded ones only sort correctly because the key is numeric.
    def test_unpadded_chapters_sort_numerically(self):
        self.assertEqual(sorted(['Matthew 10', 'Matthew 9', 'Matthew 2'], key=textNameSortKey), ['Matthew 2', 'Matthew 9', 'Matthew 10'])

    def test_copy_sorts_after_its_original(self):
        self.assertEqual(sorted(['Matthew 01 - Copy', 'Matthew 01'], key=textNameSortKey), ['Matthew 01', 'Matthew 01 - Copy'])

    def test_name_without_a_chapter_sorts_last(self):
        self.assertEqual(sorted(['Matthew 02', 'Matthew', 'Matthew 01'], key=textNameSortKey), ['Matthew 01', 'Matthew 02', 'Matthew'])

    def test_books_group_before_chapters_are_considered(self):
        self.assertEqual(sorted(['Mark 01', 'Matthew 02', 'Matthew 01'], key=textNameSortKey), ['Mark 01', 'Matthew 01', 'Matthew 02'])

class TestGroupTextNames(unittest.TestCase):

    def test_two_books_and_a_loose_text(self):
        names = ['Matthew 01', 'Matthew 03-04', 'Matthew 02', 'Field notes', 'Mark 1', 'Mark 2']
        groupList = groupTextNames(names)
        self.assertEqual([base for base, _members in groupList], ['Mark', 'Matthew'])
        self.assertEqual(dict(groupList)['Matthew'], ['Matthew 01', 'Matthew 02', 'Matthew 03-04'])
        self.assertEqual(dict(groupList)['Mark'], ['Mark 1', 'Mark 2'])

    # One text is not a merge, so a base with a single member is dropped rather than offered.
    def test_single_member_group_is_dropped(self):
        self.assertEqual(groupTextNames(['Lone 01', 'Matthew 01', 'Matthew 02']), [('Matthew', ['Matthew 01', 'Matthew 02'])])

    def test_texts_without_chapters_are_left_out(self):
        self.assertEqual(groupTextNames(['Field notes', 'Interview', 'Story']), [])

    def test_grouping_is_case_insensitive_and_keeps_the_first_spelling(self):
        groupList = groupTextNames(['Matthew 04', 'matthew 05'])
        self.assertEqual(groupList, [('Matthew', ['Matthew 04', 'matthew 05'])])

    def test_empty_input(self):
        self.assertEqual(groupTextNames([]), [])

class TestMergedTextName(unittest.TestCase):

    def test_whole_book(self):
        names = ['Matthew %02d' % chapNum for chapNum in range(1, 29)]
        self.assertEqual(mergedTextName('Matthew', names), 'Matthew 01-28')

    # The high end comes from the last member's TO chapter, so a trailing span ends the name at 24 rather than 23.
    def test_range_ending_in_a_span(self):
        self.assertEqual(mergedTextName('Matthew', ['Matthew 03', 'Matthew 23-24']), 'Matthew 03-24')

    def test_partial_range(self):
        self.assertEqual(mergedTextName('Matthew', ['Matthew 03', 'Matthew 04', 'Matthew 05']), 'Matthew 03-05')

    def test_padding_follows_the_widest_member(self):
        self.assertEqual(mergedTextName('Matthew', ['Matthew 9', 'Matthew 10']), 'Matthew 09-10')

    def test_unpadded_throughout(self):
        self.assertEqual(mergedTextName('Matthew', ['Matthew 1', 'Matthew 2']), 'Matthew 1-2')

    def test_single_chapter_covered(self):
        self.assertEqual(mergedTextName('Matthew', ['Matthew 01', 'Matthew 01 - Copy']), 'Matthew 01')

    def test_no_parseable_chapter_falls_back_to_the_base(self):
        self.assertEqual(mergedTextName('Field notes', ['Field notes', 'Interview']), 'Field notes')

class TestChapterCoverage(unittest.TestCase):

    # chapterCoverage returns (lowChap, highChap, missingList, overlapList) rather than a sentence, so that MergeTextsDlg can word it in the interface language.
    def test_contiguous(self):
        self.assertEqual(chapterCoverage(['Matthew 01', 'Matthew 02', 'Matthew 03-04']), (1, 4, [], []))

    def test_gap(self):
        self.assertEqual(chapterCoverage(['Matthew 01', 'Matthew 03']), (1, 3, [2], []))

    def test_several_gaps(self):
        self.assertEqual(chapterCoverage(['Matthew 01', 'Matthew 04']), (1, 4, [2, 3], []))

    def test_overlap(self):
        self.assertEqual(chapterCoverage(['Matthew 03-04', 'Matthew 04']), (3, 4, [], [4]))

    def test_gap_and_overlap_together(self):
        self.assertEqual(chapterCoverage(['Matthew 01', 'Matthew 01', 'Matthew 03']), (1, 3, [2], [1]))

    def test_no_chapters_gives_none(self):
        self.assertIsNone(chapterCoverage(['Field notes', 'Interview']))

    # Issue #1561: a chapter picked alongside an ordinary text is not a chapter run, so there is nothing to say about its coverage.
    def test_only_some_names_have_chapters_gives_none(self):
        self.assertIsNone(chapterCoverage(['Examples from Chapter 8', 'Words']))

    def test_one_chapter_plus_several_plain_names_gives_none(self):
        self.assertIsNone(chapterCoverage(['Matthew 01', 'Field notes', 'Interview']))

    def test_single_text(self):
        self.assertEqual(chapterCoverage(['Matthew 01']), (1, 1, [], []))

    def test_empty_selection_gives_none(self):
        self.assertIsNone(chapterCoverage([]))

if __name__ == "__main__":
    unittest.main()
