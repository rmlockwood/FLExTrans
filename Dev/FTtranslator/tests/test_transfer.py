#
#   tests/test_transfer
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Tests the transfer step (transfer.py) through FTApertium, on FTApertium's own test fixtures.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for transfer.py's FTApertium way (see THE TWO WAYS there). Run them from Dev\FTtranslator with python -m unittest discover -s tests. FTApertium itself is tested in C#
#   (apertium\tests) against output made with the Windows Apertium tools; these tests check the Python side: that Transfer loads FTtranslator.Apertium.dll with pythonnet, runs one-stage and
#   advanced transfer from a bundle's apertium folder, keeps the trace in Transfer.log, and turns a rules error into a RuntimeError as the tools' errors are.
#
#   WHAT THEY USE
#
#   The fixtures in apertium\tests\fixtures, copied into a temporary bundle folder (bundle\apertium\...), and the Release build of the DLL. The tests are skipped when the DLL isn't built or
#   pythonnet isn't installed, as on a machine without the .NET SDK. The expected results are the fixtures' files with Run Apertium's double newline made single, as transfer() does.
#
#   CODE STRUCTURE
#
#   read() reads a fixture file, readTrace() a trace with its line ends made \n, and makeBundle() copies a fixture into a bundle's layout. TestTransferWithFTApertium holds the tests.
#

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

from fttranslator import transfer
from fttranslator.transferexport import APERTIUM_DIR

FIXTURES = Path(__file__).resolve().parents[1] / "apertium" / "tests" / "fixtures"

def read(fixture, name):

    # newline="" keeps the line ends as they are, as the streams are passed to Transfer
    return (FIXTURES / fixture / name).read_text(encoding="utf-8", newline="")

def readTrace(fixture, name):

    # The Windows tools write their trace (standard error) with \r\n line ends; FTApertium writes \n, as ReferenceCheck.cs compares them
    return read(fixture, name).replace("\r\n", "\n")

def makeBundle(fixture, folder):
    '''Copy a fixture's lexicon and rules files into folder\\apertium, as a bundle holds them, and return folder.'''

    apertiumDir = Path(folder) / APERTIUM_DIR
    apertiumDir.mkdir(parents=True)

    for path in (FIXTURES / fixture).iterdir():

        if path.name == "bilingual.dix" or path.suffix in (".t1x", ".t2x", ".t3x"):

            shutil.copy(path, apertiumDir / path.name)

    return Path(folder)

@unittest.skipUnless(transfer.DEFAULT_APERTIUM_DLL.is_file() and importlib.util.find_spec("pythonnet"), "FTApertium isn't built (dotnet build -c Release in apertium) or pythonnet isn't installed")
class TestTransferWithFTApertium(unittest.TestCase):

    def setUp(self):

        self.folder = tempfile.mkdtemp(prefix="ftt_test_transfer_")

    def tearDown(self):

        shutil.rmtree(self.folder, ignore_errors=True)

    def test_one_stage(self):

        bundle = makeBundle("rules", self.folder)
        engine = transfer.Transfer(bundle, ["tr.t1x"], apertiumDll=transfer.chooseApertiumDll())

        self.assertIsNone(engine.workDir)
        self.assertEqual(engine.transfer(read("rules", "001.source.txt")), transfer.reDoubleNewline.sub("\n", read("rules", "001.transfer.txt")))
        self.assertEqual(engine.log, readTrace("rules", "001.trace.txt"))

    def test_advanced(self):

        bundle = makeBundle("advanced", self.folder)
        engine = transfer.Transfer(bundle, ["tr.t1x", "tr.t2x", "tr.t3x"], apertiumDll=transfer.chooseApertiumDll())

        self.assertEqual(engine.transfer(read("advanced", "001.source.txt")), transfer.reDoubleNewline.sub("\n", read("advanced", "001.postchunk.txt")))
        self.assertEqual(engine.log, readTrace("advanced", "001.trace.txt") + readTrace("advanced", "001.interchunk-trace.txt") + readTrace("advanced", "001.postchunk-trace.txt"))

    def test_rules_error(self):

        bundle = makeBundle("error", self.folder)
        engine = transfer.Transfer(bundle, ["tr.t1x"], apertiumDll=transfer.chooseApertiumDll())

        with self.assertRaises(RuntimeError) as caught:

            engine.transfer(read("error", "001.source.txt"))

        self.assertIn("unexpected expression: 'with-param'", str(caught.exception))

        # The same Transfer goes on working after an error
        self.assertEqual(engine.transfer(read("error", "002.source.txt")), read("error", "002.transfer.txt"))

    def test_choose(self):

        self.assertIsNone(transfer.chooseApertiumDll(useTools=True))
        self.assertEqual(transfer.chooseApertiumDll("x.dll"), Path("x.dll"))
        self.assertEqual(transfer.chooseApertiumDll(), transfer.DEFAULT_APERTIUM_DLL)

if __name__ == "__main__":

    unittest.main()
