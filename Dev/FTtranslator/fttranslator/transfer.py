#
#   fttranslator/transfer
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17.1 - 11/6/26 - Ron Lockwood
#    Transfer through FTApertium (the C# port of the Apertium tools, loaded with pythonnet) by default; the Apertium tools are still used when asked for.
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. FLExTrans' Run Apertium step without FieldWorks or make: compiles the bundle's lexicon and rules and runs the Apertium tools on a stream.
#
#   OVERVIEW (AI generated, then edited)
#
#   The transfer step of the FieldWorks-free translator. FLExTrans' Run Apertium writes a batch file that runs make on the Build folder's Makefile (or Makefile.advanced), which compiles the
#   bilingual lexicon and rules when they have changed and pipes the source stream through the Apertium tools. Here the same work is done on the bundle's apertium folder (see
#   transferexport.py), which already holds the files as Run Apertium hands them to the tools, and transfer() then makes the change Run Apertium makes to the result
#   (unfixProblemCharsRuleFile(): a double newline becomes a single one).
#
#   THE TWO WAYS
#
#   FTApertium (the default): Dev\FTtranslator\apertium is a C# port of the four Apertium programs FLExTrans runs (lt-proc -b, apertium-transfer -b, apertium-interchunk, apertium-postchunk),
#   checked byte for byte, output and trace, against the Windows tools FLExTrans ships (see apertium\README.md). Its FTtranslator.Apertium.dll is loaded into this process with pythonnet, as
#   synthesis.py loads HCSynthByGloss.dll (both through dotnet.py), and its ApertiumTransfer object reads the lexicon and rules once; each text is one call. It needs no Apertium install, so the
#   same thing runs on Windows, in the Linux image and, later, on a phone. chooseApertiumDll() finds it: the path given (--apertium-dll), else the Release build in the repo.
#
#   The Apertium tools (--apertium-tools): the programs themselves, as before FTApertium. On Windows they are the ones in FlexTools\Tools (pass that folder as toolsDir), on Linux the apertium and
#   lttoolbox packages on PATH. Their arguments are the makefiles':
#     lt-comp lr bilingual.dix bilingual.bin
#     apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin           (and t2x, t3x)
#     lt-proc -b -N1 -L1 bilingual.bin
#     apertium-transfer -b -t tr.t1x transfer_rules.t1x.bin
#     apertium-interchunk -t tr.t2x transfer_rules.t2x.bin
#     apertium-postchunk -t tr.t3x transfer_rules.t3x.bin
#   They are compiled once into a folder of the Transfer's own (workDir); each text starts the programs again.
#
#   Either way, -t makes the rules stages trace the rules they apply, which FLExTrans keeps in apertium_log.txt; here it is kept in Transfer.log.
#
#   TRAPS
#
#    - Different builds of the Apertium tools (FLExTrans' Windows ones, a Linux distribution's) can differ; FTApertium follows the Windows ones FLExTrans ships.
#    - The streams are UTF-8 with \n line ends. On Windows FLExTrans' files have \r\n; compare after normalizing. (The Windows lt-proc also writes \n as \r\n; FTApertium keeps line ends as
#      they come in, as the Linux tools do.)
#    - Where an Apertium tool stops with an error (a rules file can be accepted by apertium-preprocess-transfer and still fail on a text), FTApertium stops with the same message; either way
#      transfer() raises RuntimeError.
#
#   CODE STRUCTURE
#
#   chooseApertiumDll() picks the way; loadApertiumTransfer() loads FTApertium. Transfer holds the loaded or compiled files: _tool() finds a tool, _run() runs one, _compile() compiles, and
#   transfer() runs a stream through.
#

import os
import re
import subprocess
import tempfile
from pathlib import Path

from .dotnet import startDotNet
from .transferexport import APERTIUM_DIR, BILINGUAL_FILE

# Run Apertium's bilingUnFixSymbProbData: the only change it makes to the transfer results
reDoubleNewline = re.compile(r'\n\n')

# Where dotnet build -c Release in Dev\FTtranslator\apertium puts the DLL
DEFAULT_APERTIUM_DLL = Path(__file__).resolve().parent.parent / "apertium" / "bin" / "Release" / "net8.0" / "FTtranslator.Apertium.dll"

def chooseApertiumDll(apertiumDll=None, useTools=False):
    '''The FTApertium DLL to transfer with, or None to use the Apertium tools (useTools). Without apertiumDll, the Release build in the repo. Raises RuntimeError if there is none. See THE TWO
       WAYS above.'''

    if useTools:

        return None

    if apertiumDll:

        return Path(apertiumDll)

    if DEFAULT_APERTIUM_DLL.is_file():

        return DEFAULT_APERTIUM_DLL

    raise RuntimeError(f"FTApertium isn't built (no {DEFAULT_APERTIUM_DLL}). Build it with 'dotnet build -c Release' in Dev\\FTtranslator\\apertium, give the DLL's path with --apertium-dll, or "
                       "use the Apertium tools with --apertium-tools.")

def loadApertiumTransfer(dllPath, apertiumDir, rulesFiles):
    '''Load FTtranslator.Apertium.dll and return (an ApertiumTransfer for the files in apertiumDir, the TransferException class). Raises RuntimeError saying what went wrong.'''

    # .NET 8 in this process, shared with the synthesis DLL (see dotnet.py)
    dllPath = startDotNet(dllPath, "the FTApertium DLL")

    try:
        import clr

        clr.AddReference(str(dllPath))  # type: ignore  # pythonnet adds AddReference to clr at run time, so the checker can't see it
        from FTtranslator.Apertium import ApertiumTransfer, TransferException  # type: ignore  # a .NET namespace that pythonnet provides at run time

    except Exception as e:

        raise RuntimeError(f"Could not load the FTApertium DLL ({dllPath}). Error: {e}")

    # Reading the lexicon and rules can fail on a bad file, as the Apertium compilers can
    try:
        engine = ApertiumTransfer(str(apertiumDir), *[str(rulesFile) for rulesFile in rulesFiles])

    except Exception as e:

        raise RuntimeError(f"FTApertium could not read the transfer files in {apertiumDir}. Error: {e}")

    return engine, TransferException

class Transfer:
    '''The bundle's lexicon and rules, loaded (FTApertium, when apertiumDll is given) or compiled (the Apertium tools), ready to run streams through. See the overview above.'''

    def __init__(self, bundleDir, rulesFiles, toolsDir=None, workDir=None, apertiumDll=None):

        self.sourceDir = Path(bundleDir) / APERTIUM_DIR
        self.rulesFiles = list(rulesFiles)
        self.toolsDir = Path(toolsDir) if toolsDir else None
        self.log = ""
        self.engine = None
        self.engineError = None

        # FTApertium needs no folder of its own; the tools compile into one
        if apertiumDll:

            self.workDir = None
            self.engine, self.engineError = loadApertiumTransfer(apertiumDll, self.sourceDir, self.rulesFiles)
        else:
            self.workDir = Path(workDir) if workDir else Path(tempfile.mkdtemp(prefix="ftt_transfer_"))
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

        assert self.workDir is not None  # only the tools compile, and they always have a workDir
        self._run([self._tool("lt-comp"), "lr", str(self.sourceDir / BILINGUAL_FILE), str(self.workDir / "bilingual.bin")])

        for rulesFile in self.rulesFiles:

            self._run([self._tool("apertium-preprocess-transfer"), str(self.sourceDir / rulesFile), str(self.workDir / f"transfer_rules{Path(rulesFile).suffix}.bin")])

    def transfer(self, stream):
        '''Run a source stream (Extract Source Text's output) through the lookup and rules stages and return the target stream, as Run Apertium leaves it in the transfer results file.'''

        if self.engine is not None:

            return reDoubleNewline.sub("\n", self._transferWithEngine(stream))

        assert self.workDir is not None  # set whenever there is no engine
        result = self._run([self._tool("lt-proc"), "-b", "-N1", "-L1", str(self.workDir / "bilingual.bin")], stream)
        stages = [("apertium-transfer", ["-b", "-t"], ".t1x"), ("apertium-interchunk", ["-t"], ".t2x"), ("apertium-postchunk", ["-t"], ".t3x")]
        output = result.stdout
        self.log = ""

        for (tool, flags, suffix), rulesFile in zip(stages, self.rulesFiles):

            result = self._run([self._tool(tool)] + flags + [str(self.sourceDir / rulesFile), str(self.workDir / f"transfer_rules{suffix}.bin")], output)
            output = result.stdout
            self.log += result.stderr

        return reDoubleNewline.sub("\n", output)

    def _transferWithEngine(self, stream):
        '''FTApertium's ApertiumTransfer.Transfer(), with its error as the RuntimeError the tools give. See TRAPS above.'''

        assert self.engine is not None and self.engineError is not None  # only called when the engine is loaded

        try:
            output = str(self.engine.Transfer(stream))

        except self.engineError as e:

            raise RuntimeError(f"FTApertium transfer failed: {e.Message}")
        finally:
            self.log = str(self.engine.Log)

        return output
