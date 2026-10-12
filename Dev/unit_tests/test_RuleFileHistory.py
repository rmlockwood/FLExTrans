#
#   test_RuleFileHistory
#
#   Unit tests for Dev/Lib/RuleFileHistory.py - the one place that knows where saved copies of the
#   transfer rules file go and what they are named, plus the conversion of the Output\rule-history
#   folder that version 3.17 and earlier used. The module is Qt-free and FLEx-free, so these tests
#   need no stubs; every test points FTPaths.OUTPUT_DIR at its own temporary folder so nothing is
#   read from or written to a real work project.
#
import unittest
import sys
import os
import shutil
import tempfile
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import RuleFileHistory

class RuleFileHistoryTestCase(unittest.TestCase):
    '''Base class giving each test its own Output folder and a transfer rules file to copy.'''

    def setUp(self):

        self.workDir = tempfile.mkdtemp(prefix='rulefilehistory_test_')
        self.addCleanup(shutil.rmtree, self.workDir, True)

        self.outputDir = os.path.join(self.workDir, 'Output')
        os.makedirs(self.outputDir)

        patcher = mock.patch.object(RuleFileHistory.FTPaths, 'OUTPUT_DIR', self.outputDir)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.rulesPath = os.path.join(self.workDir, 'transfer_rules.t1x')
        self.writeFile(self.rulesPath, '<transfer/>')

    def writeFile(self, path, text):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as fout:

            fout.write(text)

    def historyNames(self):
        '''The file names sitting directly in the rule file history folder, sorted the way a directory listing would show them.'''

        historyDir = RuleFileHistory.getHistoryDir()

        if not os.path.isdir(historyDir):

            return []

        return sorted(name for name in os.listdir(historyDir) if os.path.isfile(os.path.join(historyDir, name)))

# ---------------------------------------------------------------------------
# saveHistoryCopy and saveHistoryCopies
# ---------------------------------------------------------------------------

class TestSaveHistoryCopy(RuleFileHistoryTestCase):

    def test_name_and_location(self):

        destPath, errorMsg = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_TESTBED_RUN)

        self.assertEqual(errorMsg, '')
        self.assertEqual(os.path.dirname(destPath), os.path.join(self.outputDir, 'rule-file-history'))

        # The stamp is dash separated and sits between the stem and the tag, and the original extension stays last so the copy still opens in XMLmind by association.
        name = os.path.basename(destPath)
        self.assertTrue(name.startswith('transfer_rules_'))
        self.assertTrue(name.endswith('_testbed_run.t1x'))

        stamp = name[len('transfer_rules_'):-len('_testbed_run.t1x')]
        self.assertRegex(stamp, r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$')

    def test_content_is_copied(self):

        self.writeFile(self.rulesPath, '<transfer>the real rules</transfer>')
        destPath, _ = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_TEST_ADDED)

        with open(destPath, encoding='utf-8') as fin:

            self.assertEqual(fin.read(), '<transfer>the real rules</transfer>')

    def test_names_sort_chronologically(self):
        '''A copy saved a second later has to sort after the earlier one, since a plain directory listing is how the history is meant to be read.'''

        earlier = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_TESTBED_RUN)[0]

        # Move the clock on a second rather than sleeping. Only the stamp differs, which is exactly what the sort depends on.
        realDatetime = RuleFileHistory.datetime

        with mock.patch.object(RuleFileHistory, 'datetime') as fakeDatetime:

            fakeDatetime.now.return_value = realDatetime.now().replace(microsecond=0) + realDatetime.resolution * 1000000
            later = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_TESTBED_RUN)[0]

        self.assertLess(os.path.basename(earlier), os.path.basename(later))

    def test_no_file_is_not_an_error(self):
        '''A project with no transfer rules file yet, or a setting that is still empty, is normal rather than something to report.'''

        self.assertEqual(RuleFileHistory.saveHistoryCopy(os.path.join(self.workDir, 'not_there.t1x'), RuleFileHistory.TAG_TESTBED_RUN), (None, ''))
        self.assertEqual(RuleFileHistory.saveHistoryCopy('', RuleFileHistory.TAG_TESTBED_RUN), (None, ''))
        self.assertEqual(RuleFileHistory.saveHistoryCopy(None, RuleFileHistory.TAG_TESTBED_RUN), (None, ''))

    def test_unwritable_folder_gives_a_message(self):
        '''A file sitting where the history folder should be stands in for a full disk or a locked folder: the caller gets a message instead of an exception.'''

        self.writeFile(RuleFileHistory.getHistoryDir(), 'not a folder')
        destPath, errorMsg = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_TESTBED_RUN)

        self.assertIsNone(destPath)
        self.assertTrue(errorMsg)

class TestSaveHistoryCopies(RuleFileHistoryTestCase):

    def setUp(self):

        super().setUp()

        self.interchunkPath = os.path.join(self.workDir, 'transfer_rules.t2x')
        self.postchunkPath = os.path.join(self.workDir, 'transfer_rules.t3x')
        self.writeFile(self.interchunkPath, '<transfer/>')
        self.writeFile(self.postchunkPath, '<transfer/>')

    def test_every_phase_is_saved_under_one_tag(self):

        destPaths, errorMsg = RuleFileHistory.saveHistoryCopies([self.rulesPath, self.interchunkPath, self.postchunkPath], RuleFileHistory.TAG_TEST_ADDED)

        self.assertEqual(errorMsg, '')
        self.assertEqual(len(destPaths), 3)
        self.assertEqual([os.path.splitext(path)[1] for path in destPaths], ['.t1x', '.t2x', '.t3x'])

        for path in destPaths:

            self.assertIn('_test_added', os.path.basename(path))

    def test_missing_phases_are_skipped(self):
        '''A project that isn't using advanced transfer hands over one path, and that is not a partial result to complain about.'''

        destPaths, errorMsg = RuleFileHistory.saveHistoryCopies([self.rulesPath], RuleFileHistory.TAG_TESTBED_RUN)

        self.assertEqual(errorMsg, '')
        self.assertEqual(len(destPaths), 1)

    def test_first_error_is_returned(self):

        self.writeFile(RuleFileHistory.getHistoryDir(), 'not a folder')
        destPaths, errorMsg = RuleFileHistory.saveHistoryCopies([self.rulesPath, self.interchunkPath], RuleFileHistory.TAG_TESTBED_RUN)

        self.assertEqual(destPaths, [])
        self.assertTrue(errorMsg)

# ---------------------------------------------------------------------------
# listHistoryCopies
# ---------------------------------------------------------------------------

class TestListHistoryCopies(RuleFileHistoryTestCase):

    def historyFile(self, name):
        '''Put a file with the given name in the history folder and return its path.'''

        path = os.path.join(RuleFileHistory.getHistoryDir(), name)
        self.writeFile(path, '<transfer/>')
        return path

    def test_newest_first_with_date_and_tag(self):

        older = self.historyFile('transfer_rules_2026-09-02_14-35-01_testbed_run.t1x')
        newer = self.historyFile('transfer_rules_2026-10-10_09-11-00_before_AI_changes.t1x')

        copies = RuleFileHistory.listHistoryCopies(self.rulesPath)

        self.assertEqual([path for path, _, _ in copies], [newer, older])
        self.assertEqual(copies[0][1], RuleFileHistory.datetime(2026, 10, 10, 9, 11, 0))
        self.assertEqual(copies[0][2], RuleFileHistory.TAG_BEFORE_AI_CHANGES)
        self.assertEqual(copies[1][2], RuleFileHistory.TAG_TESTBED_RUN)

    def test_only_copies_of_this_file(self):
        '''The interchunk and postchunk copies of an advanced project, and copies of a differently named rules file, share the folder but aren't copies of this file.'''

        mine = self.historyFile('transfer_rules_2026-09-02_14-35-01_testbed_run.t1x')
        self.historyFile('transfer_rules_2026-09-02_14-35-01_testbed_run.t2x')
        self.historyFile('other_rules_2026-09-02_14-35-01_testbed_run.t1x')

        self.assertEqual([path for path, _, _ in RuleFileHistory.listHistoryCopies(self.rulesPath)], [mine])

    def test_round_trip_with_saveHistoryCopy(self):
        '''Whatever saveHistoryCopy writes, listHistoryCopies has to be able to read back - the two halves of the name format live in this one module.'''

        destPath, _ = RuleFileHistory.saveHistoryCopy(self.rulesPath, RuleFileHistory.TAG_BEFORE_CAT_SETUP)
        copies = RuleFileHistory.listHistoryCopies(self.rulesPath)

        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0][0], destPath)
        self.assertEqual(copies[0][2], RuleFileHistory.TAG_BEFORE_CAT_SETUP)

    def test_unparseable_names_are_skipped(self):

        self.historyFile('transfer_rules_notes.t1x')
        self.historyFile('transfer_rules_2026-13-45_99-99-99_testbed_run.t1x')

        self.assertEqual(RuleFileHistory.listHistoryCopies(self.rulesPath), [])

    def test_no_history_folder(self):

        self.assertEqual(RuleFileHistory.listHistoryCopies(self.rulesPath), [])
        self.assertEqual(RuleFileHistory.listHistoryCopies(''), [])

if __name__ == '__main__':
    unittest.main()
