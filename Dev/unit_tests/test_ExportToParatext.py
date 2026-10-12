import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL/Qt before ExportToParatext loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib/Windows')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Modules')))

from ExportToParatext import findBookAbbrev, parseSourceTextName

# Pieces of the three error messages parseSourceTextName() can give, used to check which one came out
MISSING_CHAPTERS = 'is missing chapter number(s)'
BAD_TEXT_NAME = 'is invalid it should be of the form'
BAD_BOOK = 'The book name or abbreviation'

class FakeReport:

    def __init__(self):

        self.errors = []

    def Error(self, msg):

        self.errors.append(msg)

def parse(sourceText):

    report = FakeReport()
    infoMap = {'bookAbbrev': '', 'fromChap': 0, 'toChap': 0}
    ok = parseSourceTextName(report, sourceText, infoMap)
    return ok, infoMap, report.errors

class TestFindBookAbbrev(unittest.TestCase):

    def test_abbreviation(self):
        self.assertEqual(findBookAbbrev('GEN'), 'GEN')

    # A lowercase abbreviation is accepted and given back as typed, not uppercased
    def test_lowercase_abbreviation(self):
        self.assertEqual(findBookAbbrev('gen'), 'gen')

    def test_book_name(self):
        self.assertEqual(findBookAbbrev('Genesis'), 'GEN')

    def test_numbered_book_name(self):
        self.assertEqual(findBookAbbrev('1 Samuel'), '1SA')

    def test_multi_word_book_name(self):
        self.assertEqual(findBookAbbrev('Song of Solomon'), 'SNG')

    def test_unknown_book(self):
        self.assertIsNone(findBookAbbrev('Foo'))

    def test_misspelled_book(self):
        self.assertIsNone(findBookAbbrev('Mathew'))

    def test_empty_string(self):
        self.assertIsNone(findBookAbbrev(''))

class TestParseValidNames(unittest.TestCase):

    def assertParses(self, sourceText, bookAbbrev, fromChap, toChap):

        ok, infoMap, errors = parse(sourceText)
        self.assertTrue(ok, errors)
        self.assertEqual(errors, [])
        self.assertEqual(infoMap, {'bookAbbrev': bookAbbrev, 'fromChap': fromChap, 'toChap': toChap})

    def test_abbreviation_and_chapter(self):
        self.assertParses('GEN 01', 'GEN', 1, 1)

    def test_unpadded_chapter(self):
        self.assertParses('GEN 1', 'GEN', 1, 1)

    def test_lowercase_abbreviation(self):
        self.assertParses('Mat 01', 'Mat', 1, 1)

    def test_book_name_and_range(self):
        self.assertParses('Genesis 23-38', 'GEN', 23, 38)

    def test_range_of_one_chapter(self):
        self.assertParses('Matthew 5-5', 'MAT', 5, 5)

    def test_numbered_book_name(self):
        self.assertParses('1 Samuel 3', '1SA', 3, 3)

    def test_multi_word_book_name(self):
        self.assertParses('Song of Solomon 2', 'SNG', 2, 2)

    def test_three_digit_chapter(self):
        self.assertParses('Psalms 119', 'PSA', 119, 119)

    def test_extra_spaces(self):
        self.assertParses('Matthew   05', 'MAT', 5, 5)

    # A text the user duplicated in FLEx gets " - Copy" or " - Copy (2)" added to its name, which is ignored
    def test_copy_suffix(self):
        self.assertParses('Ruth 01 - Copy', 'RUT', 1, 1)

    def test_numbered_copy_suffix(self):
        self.assertParses('Ruth 01 - Copy (2)', 'RUT', 1, 1)

class TestParseMissingChapters(unittest.TestCase):

    # Issue #1622: a valid book with no chapter number used to be reported as an invalid book name, because the last word was taken as the chapter
    def assertMissingChapters(self, sourceText):

        ok, _infoMap, errors = parse(sourceText)
        self.assertFalse(ok)
        self.assertEqual(len(errors), 1)
        self.assertIn(MISSING_CHAPTERS, errors[0])
        self.assertIn(f'"{sourceText.replace(" - Copy", "")}"', errors[0])

    def test_book_name(self):
        self.assertMissingChapters('Matthew')

    def test_abbreviation(self):
        self.assertMissingChapters('MAT')

    def test_numbered_book_name(self):
        self.assertMissingChapters('1 Samuel')

    def test_multi_word_book_name(self):
        self.assertMissingChapters('Song of Solomon')

    def test_copy_suffix(self):
        self.assertMissingChapters('Matthew - Copy')

class TestParseInvalidNames(unittest.TestCase):

    def assertError(self, sourceText, expectedPiece):

        ok, infoMap, errors = parse(sourceText)
        self.assertFalse(ok)
        self.assertEqual(len(errors), 1)
        self.assertIn(expectedPiece, errors[0])

        # Nothing is filled in when the name is rejected
        self.assertEqual(infoMap, {'bookAbbrev': '', 'fromChap': 0, 'toChap': 0})

    # Without digits at the end and without a book name, it's the general message, not the missing chapters one
    def test_unknown_word(self):
        self.assertError('Foo', BAD_TEXT_NAME)

    def test_book_then_word(self):
        self.assertError('Matthew x', BAD_TEXT_NAME)

    def test_unknown_book_with_chapter(self):
        self.assertError('Foo 3', BAD_BOOK)

    def test_misspelled_book_with_chapter(self):
        self.assertError('Mathew 5', BAD_BOOK)

    def test_chapter_only(self):
        self.assertError('5', BAD_BOOK)

    def test_chapter_with_letter(self):
        self.assertError('Matthew 5a', BAD_TEXT_NAME)

    def test_backwards_range(self):
        self.assertError('Matthew 7-5', BAD_TEXT_NAME)

    def test_range_starting_at_zero(self):
        self.assertError('Matthew 0-3', BAD_TEXT_NAME)

    def test_range_with_three_parts(self):
        self.assertError('Matthew 1-2-3', BAD_TEXT_NAME)

    def test_range_missing_start(self):
        self.assertError('Matthew -3', BAD_TEXT_NAME)

    def test_range_missing_end(self):
        self.assertError('Matthew 3-', BAD_TEXT_NAME)

    def test_range_with_letters(self):
        self.assertError('Matthew 3-b', BAD_TEXT_NAME)

if __name__ == '__main__':
    unittest.main()
