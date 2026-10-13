import unittest
import sys
import os
import tempfile
import codecs

import net_stubs  # noqa: F401 — mock .NET/SIL/Qt before ChapterSelection loads

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import ChapterSelection
from ChapterSelection import getParatextBookNumStr, makeBookFileName, findBookFile, getNewBookFileName, getBookNotFoundMessage, markBookPresent, createBookFile, getBookChapterCount
from ChapterSelection import readVrsChapterCounts
from ChapterSelection import PARATEXT_BOOK_ORDER, ENGLISH_CHAPTER_COUNTS

# A cut-down Paratext Settings.xml, written the way Paratext writes it: a byte order mark, CRLF line endings, and a BooksPresent flag for GEN only
def settingsXml(postPart='ABC.SFM', bookNameForm='41MAT', booksPresent='1' + '0' * 122, versification='4'):

    return ('<ScriptureText>\r\n  <Versification>' + versification + '</Versification>\r\n  <BooksPresent>' + booksPresent + '</BooksPresent>\r\n'
            '  <Naming PrePart="" PostPart="' + postPart + '" BookNameForm="' + bookNameForm + '" />\r\n</ScriptureText>\r\n')

# Empty chapter markers for chapters fromCh through toCh, as a new book file has them
def placeholders(fromCh, toCh):

    return ''.join(f'\\c {ch}\n' for ch in range(fromCh, toCh + 1))

def writeFile(folder, fileName, contents='', bom=False):

    with open(os.path.join(folder, fileName), 'wb') as f:

        f.write((codecs.BOM_UTF8 if bom else b'') + contents.encode('utf-8'))

def readBytes(folder, fileName):

    with open(os.path.join(folder, fileName), 'rb') as f:

        return f.read()

class FakeReport:

    def __init__(self):

        self.errors = []
        self.infos = []

    def Error(self, msg):

        self.errors.append(msg)

    def Info(self, msg):

        self.infos.append(msg)

# Stands in for QMessageBox in askToCreateBookFile(), answering the question with whatever the test sets in answer
class FakeMessageBox:

    class StandardButton:

        Yes = 1
        No = 2

    class Icon:

        Question = 0

    answer = StandardButton.Yes
    timesShown = 0

    def __init__(self, *args):

        pass

    def __getattr__(self, name):

        return lambda *args: None

    def exec(self):

        FakeMessageBox.timesShown += 1
        return FakeMessageBox.answer

class TestBookNumbers(unittest.TestCase):

    # BOOKS must hold exactly Paratext's 123 books (the length of <BooksPresent>), each once
    def test_books_table(self):
        self.assertEqual(len(ChapterSelection.BOOKS), 123)
        self.assertEqual(len(set(PARATEXT_BOOK_ORDER)), 123)
        self.assertTrue(all(len(abbrev) == 3 for abbrev in PARATEXT_BOOK_ORDER))

    # Spot checks that the rows are in canonical order - a row out of place would give books the wrong file numbers and BooksPresent flags
    def test_books_table_anchors(self):
        self.assertEqual(PARATEXT_BOOK_ORDER.index('MAL'), 38)
        self.assertEqual(PARATEXT_BOOK_ORDER.index('MAT'), 39)
        self.assertEqual(PARATEXT_BOOK_ORDER.index('TOB'), 66)
        self.assertEqual(PARATEXT_BOOK_ORDER.index('FRT'), 99)
        self.assertEqual(PARATEXT_BOOK_ORDER[-1], 'LAO')

    # Every book has a name, and no two books share one (a text title can give its book by name); only books with chapters are in the chapter counts
    def test_derived_tables(self):
        self.assertEqual(len(ChapterSelection.bookMap), 123)
        self.assertEqual(len(set(ChapterSelection.bookMap.values())), 123)
        self.assertEqual(ChapterSelection.bookMap['RUT'], 'Ruth')
        self.assertEqual(ChapterSelection.bookMap['DNT'], 'Daniel (Greek, Theodotion)')
        self.assertEqual(ENGLISH_CHAPTER_COUNTS['PSA'], 150)
        self.assertNotIn('GLO', ENGLISH_CHAPTER_COUNTS)

    def test_old_testament(self):
        self.assertEqual(getParatextBookNumStr('GEN'), '01')
        self.assertEqual(getParatextBookNumStr('RUT'), '08')
        self.assertEqual(getParatextBookNumStr('MAL'), '39')

    # 40 is skipped, so the New Testament starts at 41
    def test_new_testament(self):
        self.assertEqual(getParatextBookNumStr('MAT'), '41')
        self.assertEqual(getParatextBookNumStr('1CO'), '47')
        self.assertEqual(getParatextBookNumStr('REV'), '67')

    def test_deuterocanon(self):
        self.assertEqual(getParatextBookNumStr('TOB'), '68')
        self.assertEqual(getParatextBookNumStr('MAN'), '84')
        self.assertEqual(getParatextBookNumStr('XXA'), '94')
        self.assertEqual(getParatextBookNumStr('XXG'), '100')

    def test_letter_numbers(self):
        self.assertEqual(getParatextBookNumStr('FRT'), 'A0')
        self.assertEqual(getParatextBookNumStr('INT'), 'A7')
        self.assertEqual(getParatextBookNumStr('GLO'), 'A9')
        self.assertEqual(getParatextBookNumStr('TDX'), 'B0')
        self.assertEqual(getParatextBookNumStr('DAG'), 'B2')
        self.assertEqual(getParatextBookNumStr('LAO'), 'C3')

    def test_unknown_book(self):
        self.assertEqual(getParatextBookNumStr('ZZZ'), '')

class TestMakeBookFileName(unittest.TestCase):

    def test_default_form(self):
        self.assertEqual(makeBookFileName(('', '41MAT', 'ABC.SFM'), 'RUT'), '08RUTABC.SFM')

    def test_no_number(self):
        self.assertEqual(makeBookFileName(('', 'MAT', 'ABC.SFM'), '1CO'), '1COABC.SFM')

    def test_number_only_with_prefix(self):
        self.assertEqual(makeBookFileName(('pre', '41', '.ptx'), 'FRT'), 'preA0.ptx')

class TestFindBookFile(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.folder = self.tempDir.name

    def tearDown(self):

        self.tempDir.cleanup()

    def test_numbered_sfm(self):
        writeFile(self.folder, '41MATABC.SFM')
        self.assertEqual(findBookFile(self.folder, 'MAT', 'ABC'), os.path.join(self.folder, '41MATABC.SFM'))

    def test_unnumbered_usfm(self):
        writeFile(self.folder, 'MATABC.usfm')
        self.assertEqual(os.path.basename(findBookFile(self.folder, 'MAT', 'ABC')), 'MATABC.usfm')

    def test_missing(self):
        writeFile(self.folder, '42MRKABC.SFM')
        self.assertEqual(findBookFile(self.folder, 'MAT', 'ABC'), '')

    # A project whose Settings.xml names its files with an extension the wildcard search wouldn't try
    def test_settings_naming(self):
        writeFile(self.folder, 'Settings.xml', settingsXml(postPart='ABC.PTX'), bom=True)
        writeFile(self.folder, '41MATABC.PTX')
        self.assertEqual(os.path.basename(findBookFile(self.folder, 'MAT', 'ABC')), '41MATABC.PTX')

class TestGetNewBookFileName(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.folder = self.tempDir.name

    def tearDown(self):

        self.tempDir.cleanup()

    def test_empty_folder_uses_paratext_default(self):
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), '41MATABC.SFM')

    def test_missing_folder_uses_paratext_default(self):
        self.assertEqual(getNewBookFileName(os.path.join(self.folder, 'nope'), 'MAT', 'ABC'), '41MATABC.SFM')

    def test_settings_naming(self):
        writeFile(self.folder, 'Settings.xml', settingsXml(postPart='ABC.SFM', bookNameForm='MAT'), bom=True)
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), 'MATABC.SFM')

    def test_follows_unnumbered_siblings(self):
        writeFile(self.folder, 'MRKABC.sfm')
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), 'MATABC.sfm')

    def test_follows_numbered_usfm_siblings(self):
        writeFile(self.folder, '42MRKABC.usfm')
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), '41MATABC.usfm')

    # A book whose abbreviation starts with a digit mustn't be mistaken for a number prefix
    def test_unnumbered_sibling_starting_with_digit(self):
        writeFile(self.folder, '1COABC.SFM')
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), 'MATABC.SFM')

    # Another project's files in the same folder don't count
    def test_ignores_other_projects(self):
        writeFile(self.folder, 'MRKXYZ.SFM')
        self.assertEqual(getNewBookFileName(self.folder, 'MAT', 'ABC'), '41MATABC.SFM')

class TestBookNotFoundMessage(unittest.TestCase):

    def test_no_wildcard(self):

        with tempfile.TemporaryDirectory() as folder:

            msg = getBookNotFoundMessage(folder, 'MAT', 'ABC')

        self.assertIn('Matthew', msg)
        self.assertIn('ABC', msg)
        self.assertIn('41MATABC.SFM', msg)
        self.assertNotIn('*', msg)

class TestCreateBookFile(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.folder = self.tempDir.name

    def tearDown(self):

        self.tempDir.cleanup()

    def readBook(self, fileName):

        with open(os.path.join(self.folder, fileName), encoding='utf-8') as f:

            return f.read()

    # With no Settings.xml the English versification is used: Matthew has 28 chapters
    def test_creates_id_line_and_chapter_placeholders(self):

        createBookFile(os.path.join(self.folder, '41MATABC.SFM'), 'MAT', self.folder)
        self.assertEqual(self.readBook('41MATABC.SFM'), '\\id MAT\n' + placeholders(1, 28))

    # A book with no chapters (front matter) gets just the \id line
    def test_book_without_chapters(self):

        createBookFile(os.path.join(self.folder, 'A0FRTABC.SFM'), 'FRT', self.folder)
        self.assertEqual(self.readBook('A0FRTABC.SFM'), '\\id FRT\n')

    # Chapters in the text past the versification's last chapter still get placeholders, so they land in order
    def test_export_chapters_past_the_end(self):

        createBookFile(os.path.join(self.folder, '08RUTABC.SFM'), 'RUT', self.folder, ['5', '6'])
        self.assertEqual(self.readBook('08RUTABC.SFM'), '\\id RUT\n' + placeholders(1, 6))

    # The project's versification comes from Settings.xml and the .vrs file in the projects folder (the project folder's parent)
    def test_project_versification(self):

        projFolder = os.path.join(self.folder, 'ABC')
        os.mkdir(projFolder)
        writeFile(projFolder, 'Settings.xml', settingsXml(versification='1'), bom=True)
        writeFile(self.folder, 'org.vrs', '# Versification  "Original"\r\nJOL 1:20 2:27 3:5 4:21\r\nMAL 1:14 2:17 3:24\r\nJOL 3:1-5 = JOL 2:28-32\r\n')
        self.assertEqual(getBookChapterCount(projFolder, 'JOL'), 4)
        self.assertEqual(getBookChapterCount(projFolder, 'MAL'), 3)

        # A book the .vrs file doesn't list has no known chapters
        self.assertEqual(getBookChapterCount(projFolder, 'MAT'), 0)

    # A versification file that isn't there falls back to English
    def test_missing_versification_file(self):

        writeFile(self.folder, 'Settings.xml', settingsXml(versification='1'), bom=True)
        self.assertEqual(getBookChapterCount(self.folder, 'MAL'), 4)

    # Mapping lines (including one for a book the file also defines), excluded verse lines, END-terminated book lines (as some custom.vrs files have) and trailing comments
    def test_vrs_line_kinds(self):

        writeFile(self.folder, 'test.vrs', '# comment\r\nGEN 1:31 2:25 3:24\r\nGEN 31:55 = GEN 32:1\r\n-GEN 1:31\r\nJOL 1:20 2:32 3:21 END\r\nRUT 1:22 2:23 # two chapters\r\n'
                                           'MAT 1:25 2:23 END # with both\r\n')
        self.assertEqual(readVrsChapterCounts(os.path.join(self.folder, 'test.vrs')), {'GEN': 3, 'JOL': 3, 'RUT': 2, 'MAT': 2})

    # A custom.vrs with END-terminated lines still overrides the standard versification
    def test_custom_vrs_with_end(self):

        writeFile(self.folder, 'custom.vrs', 'JOL 1:20 2:32 3:21 END\r\n')
        self.assertEqual(getBookChapterCount(self.folder, 'JOL'), 3)

    # A file is parsed once and then served from the cache, even if it changes afterwards
    def test_vrs_cache(self):

        vrsPath = os.path.join(self.folder, 'test.vrs')
        writeFile(self.folder, 'test.vrs', 'RUT 1:22 2:23\r\n')
        first = readVrsChapterCounts(vrsPath)
        self.assertIs(readVrsChapterCounts(vrsPath), first)

        writeFile(self.folder, 'test.vrs', 'RUT 1:22 2:23 3:18 4:22\r\n')
        self.assertEqual(readVrsChapterCounts(vrsPath), {'RUT': 2})

    # A missing file comes back empty
    def test_missing_vrs(self):
        self.assertEqual(readVrsChapterCounts(os.path.join(self.folder, 'nope.vrs')), {})

    # Looking up a book mustn't change the cached counts (custom.vrs used to be merged into them)
    def test_custom_vrs_does_not_change_cache(self):

        projFolder = os.path.join(self.folder, 'ABC')
        os.mkdir(projFolder)
        writeFile(projFolder, 'Settings.xml', settingsXml(versification='4'), bom=True)
        writeFile(self.folder, 'eng.vrs', 'MAL 1:14 2:17 3:18 4:6\r\n')
        writeFile(projFolder, 'custom.vrs', 'MAL 1:14 2:17 3:24\r\n')
        self.assertEqual(getBookChapterCount(projFolder, 'MAL'), 3)
        self.assertEqual(readVrsChapterCounts(os.path.join(self.folder, 'eng.vrs')), {'MAL': 4})
        self.assertEqual(ENGLISH_CHAPTER_COUNTS['MAL'], 4)

    def test_custom_vrs_overrides(self):

        writeFile(self.folder, 'custom.vrs', '# custom\r\nMAL 1:14 2:17 3:24\r\n')
        self.assertEqual(getBookChapterCount(self.folder, 'MAL'), 3)
        self.assertEqual(getBookChapterCount(self.folder, 'MAT'), 28)

    def test_marks_book_present_and_keeps_the_rest(self):

        writeFile(self.folder, 'Settings.xml', settingsXml(), bom=True)
        markBookPresent(self.folder, 'MAT')

        expectedFlags = '1' + '0' * 38 + '1' + '0' * 83
        self.assertEqual(readBytes(self.folder, 'Settings.xml'), codecs.BOM_UTF8 + settingsXml(booksPresent=expectedFlags).encode('utf-8'))

    # For now createBookFile() leaves Paratext's Settings.xml alone (its markBookPresent() call is commented out)
    def test_create_leaves_settings_alone(self):

        writeFile(self.folder, 'Settings.xml', settingsXml(), bom=True)
        createBookFile(os.path.join(self.folder, '41MATABC.SFM'), 'MAT', self.folder)
        self.assertEqual(readBytes(self.folder, 'Settings.xml'), codecs.BOM_UTF8 + settingsXml().encode('utf-8'))

    def test_marks_book_present_without_bom(self):

        writeFile(self.folder, 'Settings.xml', settingsXml())
        markBookPresent(self.folder, 'GEN')
        self.assertEqual(readBytes(self.folder, 'Settings.xml'), settingsXml().encode('utf-8'))

    # An old Settings.xml with a short BooksPresent string is padded out to the book's position
    def test_short_books_present(self):

        writeFile(self.folder, 'Settings.xml', settingsXml(booksPresent='1'))
        markBookPresent(self.folder, 'MAT')
        self.assertIn('<BooksPresent>' + '1' + '0' * 38 + '1' + '0' * 83 + '</BooksPresent>', readBytes(self.folder, 'Settings.xml').decode('utf-8'))

    def test_no_settings_file(self):

        markBookPresent(self.folder, 'MAT')
        self.assertEqual(os.listdir(self.folder), [])

class TestExportToMissingBook(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.paratextPath = self.tempDir.name
        self.folder = os.path.join(self.paratextPath, 'ABC')
        os.mkdir(self.folder)
        self.savedMessageBox = ChapterSelection.QMessageBox
        ChapterSelection.QMessageBox = FakeMessageBox
        FakeMessageBox.answer = FakeMessageBox.StandardButton.Yes
        FakeMessageBox.timesShown = 0

    def tearDown(self):

        ChapterSelection.QMessageBox = self.savedMessageBox
        self.tempDir.cleanup()

    def makeChapSel(self, projectAbbrev='ABC', bookAbbrev='RUT'):

        return ChapterSelection.ChapterSelection(True, '', projectAbbrev, bookAbbrev, self.paratextPath, 1, 2, False, False, False, False, False, [], [])

    def readBook(self):

        with open(os.path.join(self.folder, '08RUTABC.SFM'), encoding='utf-8') as f:

            return f.read()

    def test_creates_book_and_exports_chapters(self):

        report = FakeReport()
        text = '\\id RUT - draft\n\\c 1\n\\v 1 one\n\\c 2\n\\v 1 two\n'
        self.assertEqual(ChapterSelection.doExport(text, report, self.makeChapSel(), None), 1)

        # Only the create question is asked, not the overwrite one, and no backup is made of the new file
        self.assertEqual(FakeMessageBox.timesShown, 1)
        self.assertEqual(sorted(os.listdir(self.folder)), ['08RUTABC.SFM'])

        # The exported chapters replace their placeholders; the rest of Ruth's chapters stay as placeholders
        self.assertEqual(self.readBook(), '\\id RUT - draft\n\\c 1\n\\v 1 one\n\\c 2\n\\v 1 two\n\\c 3\n\\c 4\n')
        self.assertEqual(report.errors, [])

    # Without an \id line in the text, the new book keeps its own
    def test_new_book_middle_chapter_without_id(self):

        ChapterSelection.doExport('\\c 3\n\\v 1 three', FakeReport(), self.makeChapSel(), None)
        self.assertEqual(self.readBook(), '\\id RUT\n\\c 1\n\\c 2\n\\c 3\n\\v 1 three\n\\c 4\n')

    def test_new_book_last_chapter(self):

        ChapterSelection.doExport('\\c 4\n\\v 1 four\n', FakeReport(), self.makeChapSel(), None)
        self.assertEqual(self.readBook(), '\\id RUT\n\\c 1\n\\c 2\n\\c 3\n\\c 4\n\\v 1 four\n')

    # The intro that comes with chapter 1 carries the text's \id line; the new file must end up with only one
    def test_new_book_with_intro_has_one_id_line(self):

        text = '\\id RUT - draft\n\\ip Intro\n\\c 1\n\\v 1 one\n'
        ChapterSelection.doExport(text, FakeReport(), self.makeChapSel(), None)
        self.assertEqual(self.readBook(), '\\id RUT - draft\n\\ip Intro\n\\c 1\n\\v 1 one\n\\c 2\n\\c 3\n\\c 4\n')

    def test_user_declines(self):

        FakeMessageBox.answer = FakeMessageBox.StandardButton.No
        report = FakeReport()
        self.assertIsNone(ChapterSelection.doExport('\\c 1\n\\v 1 one\n', report, self.makeChapSel(), None))
        self.assertEqual(os.listdir(self.folder), [])

    # A missing project folder is an error - we create books, not projects
    def test_missing_project(self):

        report = FakeReport()
        self.assertIsNone(ChapterSelection.doExport('\\c 1\n\\v 1 one\n', report, self.makeChapSel('XYZ'), None))
        self.assertEqual(FakeMessageBox.timesShown, 0)
        self.assertEqual(len(report.errors), 1)

# Splicing chapters into a book that already exists, especially one with empty chapters like the placeholders of a new book
class TestSpliceIntoExistingBook(unittest.TestCase):

    def setUp(self):

        self.tempDir = tempfile.TemporaryDirectory()
        self.paratextPath = self.tempDir.name
        self.folder = os.path.join(self.paratextPath, 'ABC')
        os.mkdir(self.folder)
        self.savedMessageBox = ChapterSelection.QMessageBox
        ChapterSelection.QMessageBox = FakeMessageBox
        FakeMessageBox.answer = FakeMessageBox.StandardButton.Yes

    def tearDown(self):

        ChapterSelection.QMessageBox = self.savedMessageBox
        self.tempDir.cleanup()

    def export(self, bookContents, text):

        writeFile(self.folder, '41MATABC.SFM', bookContents)
        chapSel = ChapterSelection.ChapterSelection(True, '', 'ABC', 'MAT', self.paratextPath, 1, 1, False, False, False, False, False, [], [])
        self.assertEqual(ChapterSelection.doExport(text, FakeReport(), chapSel, None), 1)

        with open(os.path.join(self.folder, '41MATABC.SFM'), encoding='utf-8') as f:

            return f.read()

    # An empty chapter used to swallow the next chapter's marker
    def test_empty_middle_chapter(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\c 2\n\\c 3\n', '\\c 2\n\\v 1 two\n'), '\\id MAT\n\\c 1\n\\c 2\n\\v 1 two\n\\c 3\n')

    # An empty last chapter used not to match at all, so nothing was exported into it
    def test_empty_last_chapter(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\c 2', '\\c 2\n\\v 1 two\n'), '\\id MAT\n\\c 1\n\\c 2\n\\v 1 two\n')

    def test_replace_chapter_with_content(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\v 1 old one\n\\c 2\n\\v 1 old two\n', '\\c 1\n\\v 1 new one\n'), '\\id MAT\n\\c 1\n\\v 1 new one\n\\c 2\n\\v 1 old two\n')

    # Replacing chapter 1 mustn't stop at a \cp or \cl marker that starts with \c
    def test_chapter_marker_lookalikes(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\cp A\n\\v 1 old\n\\c 2\n\\v 1 two\n', '\\c 1\n\\v 1 new\n'), '\\id MAT\n\\c 1\n\\v 1 new\n\\c 2\n\\v 1 two\n')

    # Inserting chapter 2 ahead of chapter 3 mustn't also match \c 30 (or \c 2 match \c 20)
    def test_insert_does_not_match_longer_chapter_numbers(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\c 3\n\\v 1 three\n\\c 30\n', '\\c 2\n\\v 1 two'), '\\id MAT\n\\c 1\n\\c 2\n\\v 1 two\n\\c 3\n\\v 1 three\n\\c 30\n')

    # A text whose last chapter has no final line break still gets one before the next chapter marker
    def test_no_final_line_break(self):
        self.assertEqual(self.export('\\id MAT\n\\c 1\n\\c 2\n', '\\c 1\n\\v 1 one'), '\\id MAT\n\\c 1\n\\v 1 one\n\\c 2\n')

if __name__ == '__main__':
    unittest.main()
