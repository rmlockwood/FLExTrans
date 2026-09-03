#
#   test_OldRuleHistoryConversion
#
#   Unit tests for Dev/Lib/OldRuleHistoryConversion.py - bringing a leftover Output\rule-history folder
#   from version 3.17 or earlier into the rule file history folder.
#
#   TEMPORARY - delete this file when Lib/OldRuleHistoryConversion.py goes.
#
#   The module under test is Qt-free and FLEx-free, so these tests need no stubs; each one points
#   FTPaths.OUTPUT_DIR at its own temporary folder so nothing is read from or written to a real work
#   project.
#
import unittest
import sys
import os
import shutil
import tempfile
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import RuleFileHistory
import OldRuleHistoryConversion

class FakeReport:
    '''Stands in for the FlexTools report object, remembering what was said so the tests can check it.'''

    def __init__(self):

        self.infos = []
        self.warnings = []

    def Info(self, text):

        self.infos.append(text)

    def Warning(self, text):

        self.warnings.append(text)

class ConversionTestCase(unittest.TestCase):

    def setUp(self):

        self.workDir = tempfile.mkdtemp(prefix='oldrulehistory_test_')
        self.addCleanup(shutil.rmtree, self.workDir, True)

        self.outputDir = os.path.join(self.workDir, 'Output')
        os.makedirs(self.outputDir)

        patcher = mock.patch.object(RuleFileHistory.FTPaths, 'OUTPUT_DIR', self.outputDir)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.report = FakeReport()
        self.oldDir = os.path.join(self.outputDir, 'rule-history')

    def writeFile(self, path, text):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', encoding='utf-8') as fout:

            fout.write(text)

    def seedOldLayout(self):

        self.writeFile(os.path.join(self.oldDir, 'created', 'transfer_rules_created_20260810_101500.t1x'), 'created one')
        self.writeFile(os.path.join(self.oldDir, 'created', 'transfer_rules_created_20260812_143022.t1x'), 'created two')
        self.writeFile(os.path.join(self.oldDir, 'run', 'transfer_rules_run_20260810_102230.t1x'), 'run one')

    def historyNames(self):
        '''The file names sitting directly in the rule file history folder, sorted the way a directory listing would show them.'''

        historyDir = RuleFileHistory.getHistoryDir()

        if not os.path.isdir(historyDir):

            return []

        return sorted(name for name in os.listdir(historyDir) if os.path.isfile(os.path.join(historyDir, name)))

# ---------------------------------------------------------------------------
# convertOldFileName
# ---------------------------------------------------------------------------

class TestConvertOldFileName(unittest.TestCase):

    def test_created_becomes_rule_tested(self):

        newName = OldRuleHistoryConversion.convertOldFileName('transfer_rules_created_20260810_101500.t1x', 'created', OldRuleHistoryConversion.TAG_RULE_TESTED)
        self.assertEqual(newName, 'transfer_rules_2026-08-10_10-15-00_rule_tested.t1x')

    def test_run_becomes_testbed_run(self):

        newName = OldRuleHistoryConversion.convertOldFileName('transfer_rules_run_20260810_102230.t1x', 'run', RuleFileHistory.TAG_TESTBED_RUN)
        self.assertEqual(newName, 'transfer_rules_2026-08-10_10-22-30_testbed_run.t1x')

    def test_stem_with_the_infix_in_it_uses_the_last_one(self):
        '''A project whose rules file is called something like my_run_rules.t1x must not have its stem cut at the wrong place.'''

        newName = OldRuleHistoryConversion.convertOldFileName('my_run_rules_run_20260810_102230.t1x', 'run', RuleFileHistory.TAG_TESTBED_RUN)
        self.assertEqual(newName, 'my_run_rules_2026-08-10_10-22-30_testbed_run.t1x')

    def test_names_that_do_not_fit_are_refused(self):
        '''Anything the user dropped in the folder by hand is left alone rather than renamed on a guess.'''

        self.assertIsNone(OldRuleHistoryConversion.convertOldFileName('my_notes.t1x', 'run', RuleFileHistory.TAG_TESTBED_RUN))
        self.assertIsNone(OldRuleHistoryConversion.convertOldFileName('transfer_rules_run_not_a_date.t1x', 'run', RuleFileHistory.TAG_TESTBED_RUN))
        self.assertIsNone(OldRuleHistoryConversion.convertOldFileName('_run_20260810_102230.t1x', 'run', RuleFileHistory.TAG_TESTBED_RUN))

# ---------------------------------------------------------------------------
# convert
# ---------------------------------------------------------------------------

class TestConvert(ConversionTestCase):

    def test_nothing_to_convert(self):

        OldRuleHistoryConversion.convert(self.report)

        self.assertEqual(self.historyNames(), [])
        self.assertEqual(self.report.infos, [])
        self.assertEqual(self.report.warnings, [])

    def test_no_report_is_allowed(self):

        self.seedOldLayout()
        OldRuleHistoryConversion.convert(None)

        self.assertEqual(len(self.historyNames()), 3)

    def test_files_are_converted_and_the_folder_moved(self):

        self.seedOldLayout()
        OldRuleHistoryConversion.convert(self.report)

        # The three converted names sit in one flat folder, in date order, with the tag saying which of the old subfolders each came out of.
        self.assertEqual(self.historyNames(), ['transfer_rules_2026-08-10_10-15-00_rule_tested.t1x',
                                               'transfer_rules_2026-08-10_10-22-30_testbed_run.t1x',
                                               'transfer_rules_2026-08-12_14-30-22_rule_tested.t1x'])

        # The old tree has moved whole, keeping its own name and its subfolders, and the content came across untouched.
        movedDir = os.path.join(RuleFileHistory.getHistoryDir(), 'old', 'rule-history')
        self.assertFalse(os.path.exists(self.oldDir))
        self.assertTrue(os.path.isfile(os.path.join(movedDir, 'created', 'transfer_rules_created_20260810_101500.t1x')))
        self.assertTrue(os.path.isfile(os.path.join(movedDir, 'run', 'transfer_rules_run_20260810_102230.t1x')))

        with open(os.path.join(RuleFileHistory.getHistoryDir(), 'transfer_rules_2026-08-10_10-22-30_testbed_run.t1x'), encoding='utf-8') as fin:

            self.assertEqual(fin.read(), 'run one')

        self.assertEqual(len(self.report.infos), 1)
        self.assertIn('3', self.report.infos[0])
        self.assertEqual(self.report.warnings, [])

    def test_the_note_is_written(self):

        self.seedOldLayout()
        OldRuleHistoryConversion.convert(self.report)

        with open(os.path.join(RuleFileHistory.getHistoryDir(), 'old', 'README-old-rule-history.txt'), encoding='utf-8') as fin:

            self.assertEqual(fin.read(), OldRuleHistoryConversion.NOTE_TEXT)

    def test_second_call_does_nothing(self):

        self.seedOldLayout()
        OldRuleHistoryConversion.convert(self.report)
        namesAfterFirst = self.historyNames()

        secondReport = FakeReport()
        OldRuleHistoryConversion.convert(secondReport)

        self.assertEqual(self.historyNames(), namesAfterFirst)
        self.assertEqual(secondReport.infos, [])
        self.assertEqual(secondReport.warnings, [])

    def test_an_old_folder_appearing_again_is_stamped(self):
        '''An older FLExTrans run in the project again, or a restored backup, must not nest inside or overwrite the folder already put aside.'''

        self.seedOldLayout()
        OldRuleHistoryConversion.convert(self.report)

        self.writeFile(os.path.join(self.oldDir, 'run', 'transfer_rules_run_20260901_090000.t1x'), 'later run')
        OldRuleHistoryConversion.convert(self.report)

        oldFolderDir = os.path.join(RuleFileHistory.getHistoryDir(), 'old')
        stampedDirs = [name for name in os.listdir(oldFolderDir) if name.startswith('rule-history_')]

        self.assertEqual(len(stampedDirs), 1)
        self.assertTrue(os.path.isfile(os.path.join(oldFolderDir, stampedDirs[0], 'run', 'transfer_rules_run_20260901_090000.t1x')))

        # The first folder put aside is still whole.
        self.assertTrue(os.path.isfile(os.path.join(oldFolderDir, 'rule-history', 'run', 'transfer_rules_run_20260810_102230.t1x')))

    def test_a_converted_name_already_there_is_not_copied_twice(self):
        '''A conversion interrupted after some of its copying has to be safe to run again.'''

        self.seedOldLayout()
        self.writeFile(os.path.join(RuleFileHistory.getHistoryDir(), 'transfer_rules_2026-08-10_10-22-30_testbed_run.t1x'), 'already here')
        OldRuleHistoryConversion.convert(self.report)

        self.assertIn('2', self.report.infos[0])

        with open(os.path.join(RuleFileHistory.getHistoryDir(), 'transfer_rules_2026-08-10_10-22-30_testbed_run.t1x'), encoding='utf-8') as fin:

            self.assertEqual(fin.read(), 'already here')

    def test_a_name_that_does_not_fit_stays_with_the_moved_folder(self):

        self.seedOldLayout()
        self.writeFile(os.path.join(self.oldDir, 'run', 'my_notes.t1x'), 'notes')
        OldRuleHistoryConversion.convert(self.report)

        self.assertNotIn('my_notes.t1x', self.historyNames())
        self.assertTrue(os.path.isfile(os.path.join(RuleFileHistory.getHistoryDir(), 'old', 'rule-history', 'run', 'my_notes.t1x')))

    def test_a_failure_leaves_the_old_folder_alone(self):
        '''If the folder can't be made, nothing has been moved, so the next run can try the whole thing again.'''

        self.seedOldLayout()
        self.writeFile(RuleFileHistory.getHistoryDir(), 'not a folder')
        OldRuleHistoryConversion.convert(self.report)

        self.assertEqual(len(self.report.warnings), 1)
        self.assertEqual(self.report.infos, [])
        self.assertTrue(os.path.isfile(os.path.join(self.oldDir, 'run', 'transfer_rules_run_20260810_102230.t1x')))

if __name__ == '__main__':
    unittest.main()
