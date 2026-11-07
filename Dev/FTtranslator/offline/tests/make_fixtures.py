#
#   offline/tests/make_fixtures
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Makes the expected output of FTOffline's unit-test fixtures with the Python offline translator.
#
#   OVERVIEW (AI generated, then edited)
#
#   The unit tests (FixtureTests.cs) check the C# port against the Python translator on small fixtures that can be committed, since they use only FTT-Scratch, the test pair whose bundle is
#   already in the repo (deploy/bundle). Two kinds:
#
#    - fixtures/ftt-scratch/texts/*.txt are translated by the Python offline translator from deploy/bundle, and every step is saved in fixtures/ftt-scratch/stages (make_stages.py's format),
#      which the test compares step by step, as ftoffline check does.
#    - fixtures/textout holds a Text Out rules file written to exercise what TextOutRules.cs has to get right (\w with a ZWNJ, \b, \Z, full case mapping, Greek final sigma, an inactive
#      rule, a rule that fails), and an input. textout.py's result goes in expected.txt and its message in expected-message.txt, and error.xml's in error-message.txt.
#
#   Run it again after changing a fixture, or deploy/bundle, or the Python translator, and commit what it writes with the change.
#
#   TRAPS
#
#    - The expected files are written as bytes, with \n line ends, and fixtures/.gitattributes stops git from changing them, since the comparison is exact.
#    - The stages are made with hcparse, FTApertium and HCSynthByGloss.dll from their Release builds in this repo (build them first), as make_stages.py says.
#
#   CODE STRUCTURE
#
#   makeTextOut() writes the Text Out expectations; main() does those and runs make_stages.py for FTT-Scratch.
#

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TESTS = Path(__file__).resolve().parent
FTT = TESTS.parents[1]
FIXTURES = TESTS / "fixtures"

sys.path.insert(0, str(FTT))

from fttranslator.textout import TextOutRules

def makeTextOut():
    '''textout.py's results for fixtures/textout. See the OVERVIEW above.'''

    folder = FIXTURES / "textout"
    text = (folder / "input.txt").read_bytes().decode("utf-8")
    output, messages = TextOutRules(ET.parse(folder / "rules.xml")).apply(text)

    # rules.xml must apply cleanly (error.xml is the fixture for a failure); a rule that fails here is a mistake in the fixture
    if output is None:

        raise SystemExit(f"fixtures/textout/rules.xml failed in textout.py: {messages[0][1]}")

    (folder / "expected.txt").write_bytes(output.encode("utf-8"))
    (folder / "expected-message.txt").write_bytes(messages[0][1].encode("utf-8"))
    output, messages = TextOutRules(ET.parse(folder / "error.xml")).apply(text)
    assert output is None
    (folder / "error-message.txt").write_bytes(messages[0][1].encode("utf-8"))

def main():

    makeTextOut()
    stagesDir = FIXTURES / "ftt-scratch" / "stages"
    texts = sorted(str(path) for path in (FIXTURES / "ftt-scratch" / "texts").glob("*.txt"))
    subprocess.run([sys.executable, str(TESTS / "make_stages.py"), str(FTT / "deploy" / "bundle"), str(stagesDir)] + texts, check=True)
    print("Fixtures written. Run dotnet test in tests/.")

if __name__ == "__main__":

    main()
