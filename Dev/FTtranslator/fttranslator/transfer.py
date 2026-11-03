#
#   fttranslator/transfer
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. FLExTrans' Run Apertium step without FieldWorks or make: compiles the bundle's lexicon and rules and runs the Apertium tools on a stream.
#
#   OVERVIEW (AI generated, then edited)
#
#   The transfer step of the FieldWorks-free translator. FLExTrans' Run Apertium writes a batch file that runs make on the Build folder's Makefile (or Makefile.advanced), which compiles the
#   bilingual lexicon and rules when they have changed and pipes the source stream through the tools. Here the same tools run with the same arguments, without make: Transfer compiles the
#   bundle's apertium folder (see transferexport.py) once, into a folder of its own, and transfer() pipes a stream through lt-proc and apertium-transfer, then apertium-interchunk and
#   apertium-postchunk for advanced transfer, and makes the change Run Apertium makes to the result (unfixProblemCharsRuleFile(): a double newline becomes a single one).
#
#   THE TOOLS
#
#   On Linux the tools come from the apertium and lttoolbox packages and are found on PATH. On Windows they are the ones in FlexTools\Tools; pass that folder as toolsDir. Their arguments are the
#   makefiles':
#     lt-comp lr bilingual.dix bilingual.bin
#     apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin           (and t2x, t3x)
#     lt-proc -b -N1 -L1 bilingual.bin
#     apertium-transfer -b -t tr.t1x transfer_rules.t1x.bin
#     apertium-interchunk -t tr.t2x transfer_rules.t2x.bin
#     apertium-postchunk -t tr.t3x transfer_rules.t3x.bin
#   -t makes the transfer tools trace the rules they apply on standard error, which FLExTrans keeps in apertium_log.txt; here it is kept in Transfer.log.
#
#   TRAPS
#
#    - Different builds of the Apertium tools (FLExTrans' Windows ones, a Linux distribution's) can differ, so the Linux output has to be checked against the desktop's, not assumed.
#    - The streams are UTF-8 with \n line ends. On Windows FLExTrans' files have \r\n; compare after normalizing.
#
#   CODE STRUCTURE
#
#   Transfer holds the compiled files: _tool() finds a tool, _compile() compiles, and transfer() runs a stream through.
#

import os
import re
import subprocess
import tempfile
from pathlib import Path

from .transferexport import APERTIUM_DIR, BILINGUAL_FILE

# Run Apertium's bilingUnFixSymbProbData: the only change it makes to the transfer results
reDoubleNewline = re.compile(r'\n\n')

class Transfer:
    '''The bundle's lexicon and rules, compiled, ready to run streams through. See the overview above.'''

    def __init__(self, bundleDir, rulesFiles, toolsDir=None, workDir=None):

        self.sourceDir = Path(bundleDir) / APERTIUM_DIR
        self.rulesFiles = list(rulesFiles)
        self.toolsDir = Path(toolsDir) if toolsDir else None
        self.workDir = Path(workDir) if workDir else Path(tempfile.mkdtemp(prefix="ftt_transfer_"))
        self.log = ""
        self._compile()

    def _tool(self, name):

        if self.toolsDir is None:

            return name

        return str(self.toolsDir / (name + (".exe" if os.name == "nt" else "")))

    def _run(self, args, inputText=None):

        result = subprocess.run(args, input=inputText, capture_output=True, encoding="utf-8", cwd=self.workDir)

        if result.returncode != 0:

            raise RuntimeError(f"{Path(args[0]).name} failed ({result.returncode}): {result.stderr.strip()}")

        return result

    def _compile(self):

        self._run([self._tool("lt-comp"), "lr", str(self.sourceDir / BILINGUAL_FILE), str(self.workDir / "bilingual.bin")])

        for rulesFile in self.rulesFiles:

            self._run([self._tool("apertium-preprocess-transfer"), str(self.sourceDir / rulesFile), str(self.workDir / f"transfer_rules{Path(rulesFile).suffix}.bin")])

    def transfer(self, stream):
        '''Run a source stream (Extract Source Text's output) through the tools and return the target stream, as Run Apertium leaves it in the transfer results file.'''

        result = self._run([self._tool("lt-proc"), "-b", "-N1", "-L1", str(self.workDir / "bilingual.bin")], stream)
        stages = [("apertium-transfer", ["-b", "-t"], ".t1x"), ("apertium-interchunk", ["-t"], ".t2x"), ("apertium-postchunk", ["-t"], ".t3x")]
        output = result.stdout
        self.log = ""

        for (tool, flags, suffix), rulesFile in zip(stages, self.rulesFiles):

            result = self._run([self._tool(tool)] + flags + [str(self.sourceDir / rulesFile), str(self.workDir / f"transfer_rules{suffix}.bin")], output)
            output = result.stdout
            self.log += result.stderr

        return reDoubleNewline.sub("\n", output)
