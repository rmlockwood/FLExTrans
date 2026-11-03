#
#   fttranslator/cli
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.6 - 11/3/26 - Ron Lockwood
#    Added the serve-offline command: the React front end translating from a bundle alone, for Linux hosts such as Railway.
#
#   Version 3.17.5 - 11/3/26 - Ron Lockwood
#    Added --synthesize and --hcsynth to offline-stream: HermitCrab synthesis without FieldWorks (synthesis.py).
#
#   Version 3.17.4 - 11/3/26 - Ron Lockwood
#    Added the export-bundle, golden and check-golden commands: the source lexicon data for an offline translator, test data for it, and the check.
#
#   Version 3.17.3 - 10/30/26 - Ron Lockwood
#    Added the serve command: a local web server for the React front end, with the projects kept open.
#
#   Version 3.17.2 - 10/27/26 - Ron Lockwood
#    Added the interactive command: type a sentence, get its translation, repeat until Ctrl+C, with the projects kept open.
#
#   Version 3.17.1 - 10/27/26 - Ron Lockwood
#    Added --timing to show each step's time and the total; -v shows them too.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The fttranslator command line: translate, steps, check and runs.
#
#   OVERVIEW (AI generated, then edited)
#
#   The command line for FTtranslator, run as python -m fttranslator. Each command takes a FLExTrans work project folder and builds a Translator for it. translate prints the target text on
#   stdout and everything else (FLExTrans' messages, the words that failed, OK or FAILED) on stderr, so the translation can be piped or redirected on its own.
#
#   KEEPING STDOUT CLEAN
#
#   Printing to sys.stderr isn't enough: the programs FLExTrans runs (make, STAMP) write straight to the console through file descriptor 1. stdoutToStderr() points descriptor 1 at stderr for the
#   length of a run and puts it back afterwards, so only the translation, printed after the run, reaches stdout.
#
#   INTERACTIVE
#
#   interactive is a read-translate loop: it prompts with "> ", translates each sentence as its own text when Enter is pressed, and shows only the answer and any failed words - the output of
#   make and STAMP goes nowhere instead of to the screen (silenceTools()), unless -v is given. One Translator serves the whole session, so the projects are opened once and each sentence after the first takes
#   about half a second (see KEEPING THE PROJECTS OPEN in translator.py). It ends on Ctrl+C, or Ctrl+Z then Enter. Ctrl+C at the prompt stops at once, but Ctrl+C during a translation only
#   asks to stop (CtrlCStopper): an interrupt in the middle of FieldWorks or the FLExTrans steps could leave a unit of work open, and the projects must still be saved and closed.
#
#   SERVE
#
#   serve is the same idea behind a web page: it starts the local web server in server.py, which keeps one Translator (and so the open projects) for its whole life, and opens the React front end
#   in the browser. It stops on Ctrl+C the same safe way, using CtrlCStopper.
#
#   EXPORT-BUNDLE
#
#   export-bundle opens the source project read-only and writes the offline translation bundle (see bundle.py) to <work project>\Output\ftt_bundle, or to --out. It translates nothing, but it does
#   read the target project (the bilingual lexicon and the synthesis data), so both projects must be closed in FLEx. golden does the same for the bundle's test data (see golden.py), writing to Output\ftt_golden; it runs Extract Source Text, so descriptor 1 goes to stderr as in
#   translate. Both resolve --out before making the Translator, because making one changes the working directory to the work project's Config folder. check-golden runs the FieldWorks-free
#   Extract Source Text (bundleextract.py) on those pairs and reports what differs; it makes no Translator at all, since it needs neither FieldWorks nor FLExTrans.
#
#   OFFLINE-STREAM
#
#   offline-stream runs the FieldWorks-free chain on a text from the bundle alone and prints the Apertium stream: tokenizer, hcparse, filing and guessing (analysisguess.py) and Extract Source
#   Text (bundleextract.py). --transfer goes on through the Apertium tools (transfer.py), and --synthesize (which implies --transfer) on through Convert Text to Synthesizer Format and HermitCrab
#   synthesis (synthesis.py), running HCSynthByGloss with the --hcsynth command and printing the synthesized text. --synth-dir keeps the master, parses and surface forms files for comparison.
#
#   SERVE-OFFLINE
#
#   serve-offline is serve without FieldWorks, FLExTrans or a work project: it runs the same chain as offline-stream --synthesize behind the React front end (offlineserver.py), from a bundle
#   folder alone. It is what the Docker image in deploy\Dockerfile runs on Railway, listening on 0.0.0.0 and Railway's $PORT. It stops on Ctrl+C or the host's stop signal; nothing needs saving.
#
#   ENCODINGS
#
#   main() switches stdout and stderr to UTF-8 so vernacular text survives a Windows console code page or a redirect, and reads stdin as UTF-8 with an optional byte-order mark. The command line
#   flags keep their dashes (--keep-approvals); argparse is given camelCase dest names so the code reads args.keepApprovals.
#
#   CODE STRUCTURE
#
#   _translator() builds the Translator for a command. Then cmdTranslate(), cmdInteractive() and cmdServe() with their helpers CtrlCStopper, stdoutToStderr(), silenceTools() (all three also used by
#   server.py), printTimings() (for --timing or -v), summarize() and _unique(), followed by cmdSteps(), cmdCheck(), cmdRuns(), cmdExportBundle(), cmdGolden() and cmdCheckGolden(). main() sets up argparse, runs the chosen command and shuts FieldWorks down with env.cleanup() however the command ends.
#

import argparse
import contextlib
import json
import os
import shutil
import signal
import sys
from pathlib import Path

# Shown by --help
USAGE_TEXT = """
Command line for FTtranslator: end-to-end translation with FLEx and FLExTrans.

  translate WORKDIR [TEXT] [--file F]   translate a text, print the result
  interactive WORKDIR                   type sentences one at a time and get each translation
  serve     WORKDIR [--port N]          translate in the browser (the React front end)
  steps     WORKDIR                     list the pipeline that would run
  check     WORKDIR                     check projects, tools and configuration
  runs      WORKDIR                     list earlier runs and the words that failed
  export-bundle WORKDIR [--out DIR]     write the source lexicon data for an offline translator
  golden    WORKDIR [--text T] [--out DIR]  capture test data: texts' analyses + Extract Source Text's output
  check-golden WORKDIR                  run the bundle's Extract Source Text on the test data (no FieldWorks)
  offline-stream WORKDIR [TEXT] --hcparse C  translate from the bundle alone (no FieldWorks); see --help
  serve-offline --bundle DIR --hcparse C --hcsynth C  the browser front end, translating from a bundle alone (Linux, Railway)

WORKDIR is a FLExTrans work project folder (…\\WorkProjects\\<name>).
The FLEx projects must be closed in FieldWorks (or shared).
"""

def _translator(args):
    '''Return a Translator for the command's work project. Imported here because creating one sets up the whole process (env.bootstrap()).'''

    from .translator import Translator

    return Translator(args.workdir, args.modules, verbose=getattr(args, "verbose", False))

def cmdTranslate(args):

    from .pipeline import Options

    # The text comes from --file, the command line or stdin, in that order
    if args.file:

        text = Path(args.file).read_text(encoding="utf-8-sig")

    elif args.text:

        text = args.text
    else:
        text = sys.stdin.read()

    # Leaving the with block closes the projects the run opened
    with _translator(args) as translator, stdoutToStderr():

        result = translator.translate(text, Options(insert=args.insert, keepApprovals=args.keepApprovals, title=args.title))

    if args.json:

        Path(args.json).write_text(json.dumps(result.toDict(), ensure_ascii=False, indent=2), encoding="utf-8")

    if result.translation is not None:

        print(result.translation)

    # -v shows the step times too, since a verbose run is usually one being looked into
    if args.timing or args.verbose:

        printTimings(result, sys.stderr)

    summarize(result, sys.stderr)

    return 0 if result.ok else 1

def cmdInteractive(args):
    '''Prompt for a sentence, translate it, show the answer, and repeat until Ctrl+C, keeping the projects open in between. See INTERACTIVE above.'''

    from .pipeline import Options

    options = Options(insert=args.insert, keepApprovals=args.keepApprovals)
    sentenceCount = 0
    ctrlC = CtrlCStopper()

    try:
        with _translator(args) as translator:

            print("Ready. Type a sentence and press Enter (the first one takes a few seconds). Ctrl+C to stop.", file=sys.stderr)

            while not ctrlC.requested:

                print("> ", end="", file=sys.stderr, flush=True)
                line = ctrlC.readline(sys.stdin)

                # End of input (Ctrl+Z then Enter), or Ctrl+C at the prompt
                if not line:

                    break

                text = line.strip()

                if not text:

                    continue

                # The output of make and STAMP goes nowhere, unless -v asks to see everything
                with stdoutToStderr() if args.verbose else silenceTools():

                    result = translator.translate(text, options)

                sentenceCount += 1

                if result.translation:

                    print(" ".join(result.translation.split()), flush=True)

                if args.timing or args.verbose:

                    printTimings(result, sys.stderr)

                summarize(result, sys.stderr, brief=True)

    finally:
        ctrlC.restore()

    print(f"\nTranslated {sentenceCount} sentence(s).", file=sys.stderr)

    return 0

def cmdServe(args):
    '''Run the local web server for the React front end until Ctrl+C, keeping the projects open in between. See SERVE above.'''

    from .server import serve

    # Leaving the with block saves and closes the projects
    with _translator(args) as translator:

        serve(translator, args.port, verbose=args.verbose, openBrowser=not args.noBrowser)

    return 0

class CtrlCStopper:
    '''Ctrl+C handling for the interactive and serve commands. At the prompt, Ctrl+C stops at once; during a translation it only asks to stop, so the run finishes and the projects are saved
       and closed. serve never sets waiting, so there Ctrl+C always just asks, and the server loop checks between requests.'''

    def __init__(self):

        self.requested = False
        self.waiting = False
        self.previous = signal.signal(signal.SIGINT, self._handle)

    def _handle(self, signum, frame):

        if self.waiting:

            raise KeyboardInterrupt

        if not self.requested:

            print("\nStopping...", file=sys.stderr, flush=True)

        self.requested = True

    def readline(self, stream):
        '''Read a line, returning "" (as at end of input) if Ctrl+C is pressed while waiting for it.'''

        self.waiting = True

        try:
            return stream.readline()

        except (KeyboardInterrupt, EOFError):

            self.requested = True
            return ""

        finally:
            self.waiting = False

    def restore(self):

        signal.signal(signal.SIGINT, self.previous)

@contextlib.contextmanager
def stdoutToStderr():
    '''Point file descriptor 1 at stderr for the length of the with block. See KEEPING STDOUT CLEAN above.'''

    sys.stdout.flush()
    savedStdout = os.dup(1)
    os.dup2(2, 1)

    try:
        yield
    finally:
        sys.stdout.flush()
        os.dup2(savedStdout, 1)
        os.close(savedStdout)

@contextlib.contextmanager
def silenceTools():
    '''For the length of the with block, send what the tools FLExTrans runs write (make to descriptor 1, STAMP to 2) nowhere, while Python's own sys.stderr - FTtranslator's warnings
       and errors - still reaches the screen through a saved copy of descriptor 2.'''

    sys.stdout.flush()
    sys.stderr.flush()
    savedStdout = os.dup(1)
    savedStderr = os.dup(2)
    devNull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devNull, 1)
    os.dup2(devNull, 2)
    originalStderr = sys.stderr
    sys.stderr = open(savedStderr, "w", encoding="utf-8", errors="replace", closefd=False)

    try:
        yield
    finally:
        sys.stderr.flush()
        sys.stderr = originalStderr
        os.dup2(savedStdout, 1)
        os.dup2(savedStderr, 2)

        for descriptor in (savedStdout, savedStderr, devNull):

            os.close(descriptor)

def printTimings(result, out):
    '''Print how long each step took, the time outside the steps (opening the source project on the first run, and saving), and the total.'''

    print(file=out)
    print("Step times:", file=out)

    for timing in result.timings:

        print(f"  {timing['step']:38s} {timing['seconds']:8.2f} s", file=out)

    # totalSeconds is None only if translate() stopped with an exception before it was set
    if result.totalSeconds is not None:

        stepSeconds = sum(timing["seconds"] for timing in result.timings)
        print(f"  {'Outside the steps (open, save)':38s} {result.totalSeconds - stepSeconds:8.2f} s", file=out)
        print(f"  {'Total':38s} {result.totalSeconds:8.2f} s", file=out)

def summarize(result, out, brief=False):
    '''Print the words that failed, grouped by why, then OK or FAILED. brief (the interactive command) leaves out the blank line before and the OK line, so a good answer is just the answer.'''

    def printWords(label, words):

        if words:

            print(f"{label} ({len(words)}): {', '.join(words)}", file=out)

    if not brief:

        print(file=out)

    printWords("No parse", result.unparsed)
    printWords("No analysis", _unique(result.unanalysed))
    printWords("Not linked to target lexicon", result.untranslated)
    printWords("Not synthesized", result.unsynthesized)

    if result.ok and brief:

        return

    if result.ok:

        status = "OK"

    elif result.steps:

        status = f"FAILED after '{result.steps[-1]}'"
    else:
        status = "FAILED"

    where = f"; source text '{result.title}'" if result.title else ""
    print(f"{status}{where}", file=out)

def _unique(words):
    '''The words without repeats, in their first-seen order.'''

    return list(dict.fromkeys(words))

def cmdSteps(args):

    translator = _translator(args)
    print(f"Source project: {translator.profile.sourceProject}")
    print(f"Collection:     {translator.profile.collectionFile}")

    for number, step in enumerate(translator.steps(), 1):

        print(f"{number:3d}. {step.describe()}")

    return 0

def cmdCheck(args):

    translator = _translator(args)

    # Imported here: they need env.bootstrap(), which creating the Translator has just done
    from .report import makeReporter
    import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()
    from flexlibs import AllProjectNames
    from parse_priority import fw

    report = makeReporter(verbose=False)
    configMap = translator.readConfig(report)
    problems = []

    def check(ok, what):

        print(f"  [{'ok' if ok else 'XX'}] {what}")

        if not ok:

            problems.append(what)

    # The projects
    projectNames = set(AllProjectNames())
    targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False)
    twoProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) != "n"
    check(translator.profile.sourceProject in projectNames, f"source project '{translator.profile.sourceProject}' exists")

    if twoProjectMode:

        check(targetProject in projectNames, f"target project '{targetProject}' exists")

    # The tools FLExTrans runs: from FlexTools\Tools, except the HermitCrab synthesis ones, which have to be on PATH
    tools = ["make.exe", "lt-comp.exe", "lt-proc.exe", "apertium-preprocess-transfer.exe", "apertium-transfer.exe"]
    hermitCrabSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False) == "y"

    if not hermitCrabSynthesis:

        tools.append("stamp64.exe")

    for exe in tools:

        check((translator.env.toolsDir / exe).exists(), f"{exe} in {translator.env.toolsDir}")

    if hermitCrabSynthesis:

        for exe in ("GenerateHCConfigForFLExTrans.exe", "HCSynthByGloss.exe"):

            check(shutil.which(exe) is not None, f"{exe} on PATH")

    # The pipeline: building it also imports any custom modules in the collection
    try:
        steps = translator.steps()
        check(True, f"pipeline resolves ({len(steps)} steps)")

    except SystemExit as err:

        check(False, f"pipeline: {err}")

    # The source project's active parser, which the guesser's parser approvals depend on
    try:
        project = fw.openProject(translator.profile.sourceProject)

        try:
            activeParser = project.project.LangProject.MorphologicalDataOA.ActiveParser
            check(activeParser == "HC", f"source project's active parser is HermitCrab (it is {activeParser})")
        finally:
            project.CloseProject()

    except SystemExit as err:

        check(False, str(err))

    print("\nAll checks passed." if not problems else f"\n{len(problems)} problem(s).")

    return 0 if not problems else 1

def cmdRuns(args):

    translator = _translator(args)
    records = translator.runs()

    if not records:

        print("No runs yet.")

    # The record keys are RunResult's field names
    for record in records[-args.last:]:

        print(f"{record['title']}  {'OK' if record['ok'] else 'FAILED'}")
        print(f"    source     : {record['source'].strip()[:70]}")

        if record.get("translation"):

            print(f"    translation: {record['translation'][:70]}")

        for label, key in (("no parse", "unparsed"), ("no analysis", "unanalysed"), ("not linked to target", "untranslated"), ("not synthesized", "unsynthesized")):

            if record.get(key):

                print(f"    {label:24s}: {', '.join(_unique(record[key]))}")

    return 0

def cmdExportBundle(args):
    '''Write the offline translation bundle for the work project. See EXPORT-BUNDLE above.'''

    # Resolved before the Translator is made, since that changes the working directory to the work project's Config folder
    outDir = Path(args.out).resolve() if args.out else None
    translator = _translator(args)

    # Imported here: they need env.bootstrap(), which creating the Translator has just done
    from . import bundle
    from .report import makeReporter
    from parse_priority import fw

    report = makeReporter(verbose=args.verbose)
    configMap = translator.readConfig(report)
    outDir = outDir or translator.env.workDir / "Output" / "ftt_bundle"
    project = fw.openProject(translator.profile.sourceProject)

    try:
        ok = bundle.exportBundle(project, configMap, outDir, report, translator.profile.sourceProject, translator.env.workDir.name)
    finally:
        project.CloseProject()

    if ok:

        print(f"Bundle written to {outDir}")

    return 0 if ok else 1

def cmdGolden(args):
    '''Capture golden pairs for testing a bundle runtime: each text's analyses next to Extract Source Text's real output. See EXPORT-BUNDLE above.'''

    # Resolved before the Translator is made, since that changes the working directory to the work project's Config folder
    outDir = Path(args.out).resolve() if args.out else None
    tokensFile = Path(args.tokens).resolve() if args.tokens else None
    translator = _translator(args)

    # Imported here: they need env.bootstrap(), which creating the Translator has just done
    from . import golden
    from .report import makeReporter
    from .translator import flexlibsView
    from parse_priority import fw

    report = makeReporter(verbose=args.verbose)
    configMap = translator.readConfig(report)
    outDir = outDir or translator.env.workDir / "Output" / "ftt_golden"

    # --tokens: only the tokenizer pairs, which need the project open for writing (everything is undone). See TOKENIZER PAIRS in golden.py.
    if tokensFile:

        paragraphs = [line.strip() for line in tokensFile.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        project = fw.openProject(translator.profile.sourceProject, write=True)

        try:
            outDir.mkdir(parents=True, exist_ok=True)
            count = golden.captureTokens(project, paragraphs, outDir / "tokens.json")
        finally:
            project.CloseProject()

        print(f"Tokenizer pairs: {len(paragraphs)} paragraph(s), {count} occurrence(s), written to {outDir / 'tokens.json'}")
        return 0

    project = fw.openProject(translator.profile.sourceProject)

    # Extract Source Text is written against flexlibs, so it gets a flexlibs view of the open project, as in a translation run. The parser pairs use flexicon's parser on the project itself.
    try:
        with stdoutToStderr():

            ok = golden.captureGolden(flexlibsView(project), configMap, outDir, report, textNames=args.text, verbose=args.verbose)

            if ok and not args.text:

                golden.captureParserGolden(project, outDir, report)

    finally:
        project.CloseProject()

    if ok:

        print(f"Golden pairs written to {outDir}")

    return 0 if ok else 1

def cmdCheckGolden(args):
    '''Run the bundle's Extract Source Text (bundleextract.py) on every golden pair and report what differs. Needs no FieldWorks, so no Translator is made. See EXPORT-BUNDLE above.'''

    from . import bundleextract

    outputDir = Path(args.workdir).resolve() / "Output"
    bundleDir = Path(args.bundle).resolve() if args.bundle else outputDir / "ftt_bundle"
    goldenDir = Path(args.golden).resolve() if args.golden else outputDir / "ftt_golden"
    differing = bundleextract.compareGolden(bundleDir, goldenDir, sys.stdout, showDiffs=args.show) if (goldenDir / "index.json").exists() else 0

    # The tokenizer pairs, if golden --tokens made some
    if (goldenDir / "tokens.json").exists():

        from .tokenizer import Tokenizer

        print(file=sys.stdout)
        differing += Tokenizer.load(bundleDir).compareTokens(goldenDir / "tokens.json", sys.stdout, showDiffs=args.show)

    return 0 if differing == 0 else 1

def cmdOfflineStream(args):
    '''Run the FieldWorks-free chain (tokenize, parse, file, guess, Extract Source Text) on a text and print the Apertium stream. Needs no FieldWorks. See analysisguess.py.'''

    import shlex

    from . import analysisguess

    bundleDir = Path(args.bundle).resolve() if args.bundle else Path(args.workdir).resolve() / "Output" / "ftt_bundle"
    text = Path(args.file).read_text(encoding="utf-8-sig") if args.file else args.text
    parser = analysisguess.HCParseProcess(shlex.split(args.hcparse, posix=False), bundleDir)

    try:
        stream, messages, _, unparsed = analysisguess.translateToStream(text, bundleDir, parser)
    finally:
        parser.close()

    # --transfer: on through the Apertium tools, as Run Apertium does (see transfer.py). --synthesize needs the target stream, so it implies --transfer.
    if args.transfer or args.synthesize:

        from .transfer import Transfer

        manifest = json.loads((bundleDir / "manifest.json").read_text(encoding="utf-8"))
        stream = Transfer(bundleDir, manifest["files"]["apertium"]["rules"], toolsDir=args.tools).transfer(stream)

    # --synthesize: on through Convert Text to Synthesizer Format and HermitCrab synthesis (see synthesis.py); its messages go with the others
    if args.synthesize:

        from .synthesis import Synthesizer

        if not args.hcsynth:

            raise SystemExit("--synthesize needs --hcsynth, the command that runs HCSynthByGloss")

        synthesizer = Synthesizer(bundleDir, shlex.split(args.hcsynth, posix=False), workDir=Path(args.synthDir).resolve() if args.synthDir else None)
        text, synthMessages = synthesizer.synthesize(stream)
        messages = list(messages) + synthMessages

        if text is None:

            for level, message in messages:

                print(f"{level.upper()}: {message}", file=sys.stderr)

            return 1

        stream = text

    print(stream, end="")

    for level, message in messages:

        print(f"{level.upper()}: {message}", file=sys.stderr)

    if unparsed:

        print(f"No parse ({len(unparsed)}): {', '.join(unparsed)}", file=sys.stderr)

    return 0

def cmdServeOffline(args):
    '''Serve the React front end, translating from a bundle with no FieldWorks or FLExTrans. See SERVE-OFFLINE above and offlineserver.py.'''

    from . import offlineserver

    offlineserver.serve(Path(args.bundle).resolve(), args.hcparse, args.hcsynth, args.host, args.port, toolsDir=args.tools, verbose=args.verbose)

    return 0

def main(argv=None):

    # Vernacular text must survive the console code page and redirection. The streams are typed as TextIO, which has no reconfigure(), but they are TextIOWrappers here.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.stdin.reconfigure(encoding="utf-8-sig")  # type: ignore

    argParser = argparse.ArgumentParser(prog="fttranslator", description=USAGE_TEXT, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = argParser.add_subparsers(dest="cmd", required=True)

    # Every command takes the work project and optionally a modules folder
    def addCommon(subparser):

        subparser.add_argument("workdir", help="FLExTrans work project folder")
        subparser.add_argument("--modules", help="FLExTrans modules folder (default: the installed one next to the work project); 'dev' means this repo's Dev\\Modules")

    subparser = subparsers.add_parser("translate", help="translate a text and print the result")
    addCommon(subparser)
    subparser.add_argument("text", nargs="?", help="the source text (default: --file or stdin)")
    subparser.add_argument("--file", help="read the source text from a UTF-8 file")
    subparser.add_argument("--title", help="title for the new text in the source project")
    subparser.add_argument("--insert", action="store_true", help="also insert the translation into the target project (Insert Target Text)")
    subparser.add_argument("--keep-approvals", dest="keepApprovals", action="store_true", help="leave the guessed analyses approved in the source text (they then count for future guesses); default: release them for review in FLEx")
    subparser.add_argument("--json", help="also write the run record (approvals, failures, messages) here")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all FLExTrans messages, and the step times")
    subparser.add_argument("--timing", action="store_true", help="show how long each step took and the total time")
    subparser.set_defaults(func=cmdTranslate)

    subparser = subparsers.add_parser("interactive", help="type sentences one at a time and get each translation, until Ctrl+C")
    addCommon(subparser)
    subparser.add_argument("--insert", action="store_true", help="also insert each translation into the target project (Insert Target Text)")
    subparser.add_argument("--keep-approvals", dest="keepApprovals", action="store_true", help="leave the guessed analyses approved in the source texts; default: release them for review in FLEx")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all FLExTrans messages and tool output, and the step times")
    subparser.add_argument("--timing", action="store_true", help="show how long each step took and the total time, for each sentence")
    subparser.set_defaults(func=cmdInteractive)

    subparser = subparsers.add_parser("serve", help="translate in the browser: a local web server for the React front end, until Ctrl+C")
    addCommon(subparser)
    subparser.add_argument("--port", type=int, default=8765, help="the port to listen on (default 8765); 0 picks a free one")
    subparser.add_argument("--no-browser", dest="noBrowser", action="store_true", help="don't open the page in the browser")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all FLExTrans messages, tool output and requests in the console")
    subparser.set_defaults(func=cmdServe)

    subparser = subparsers.add_parser("steps", help="list the pipeline steps")
    addCommon(subparser)
    subparser.set_defaults(func=cmdSteps)

    subparser = subparsers.add_parser("check", help="check projects, tools and configuration")
    addCommon(subparser)
    subparser.set_defaults(func=cmdCheck)

    subparser = subparsers.add_parser("runs", help="list earlier runs and their failed words")
    addCommon(subparser)
    subparser.add_argument("--last", type=int, default=10)
    subparser.set_defaults(func=cmdRuns)

    subparser = subparsers.add_parser("export-bundle", help="write the source lexicon data for an offline translator")
    addCommon(subparser)
    subparser.add_argument("--out", help="the folder to write to (default: <work project>\\Output\\ftt_bundle)")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all messages")
    subparser.set_defaults(func=cmdExportBundle)

    subparser = subparsers.add_parser("golden", help="capture test data for a bundle runtime: each text's analyses and Extract Source Text's real output")
    addCommon(subparser)
    subparser.add_argument("--text", action="append", help="capture only the text with this title (can be given more than once; default: every text)")
    subparser.add_argument("--out", help="the folder to write to (default: <work project>\\Output\\ftt_golden)")
    subparser.add_argument("--tokens", help="instead, capture tokenizer pairs: have FLEx parse each line of this UTF-8 file as a new paragraph (the project is opened for writing; all is undone)")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all messages")
    subparser.set_defaults(func=cmdGolden)

    subparser = subparsers.add_parser("check-golden", help="run the bundle's Extract Source Text on the golden pairs and report what differs (no FieldWorks needed)")
    subparser.add_argument("workdir", help="FLExTrans work project folder, whose Output folder holds ftt_bundle and ftt_golden")
    subparser.add_argument("--bundle", help="the bundle folder (default: <work project>\\Output\\ftt_bundle)")
    subparser.add_argument("--golden", help="the golden pairs folder (default: <work project>\\Output\\ftt_golden)")
    subparser.add_argument("--show", type=int, default=5, help="how many differing texts to show (default 5)")
    subparser.set_defaults(func=cmdCheckGolden)

    subparser = subparsers.add_parser("offline-stream", help="without FieldWorks: tokenize, parse, guess and Extract Source Text, and print the Apertium stream")
    subparser.add_argument("workdir", help="FLExTrans work project folder, whose Output folder holds ftt_bundle")
    subparser.add_argument("text", nargs="?", help="the source text (or --file)")
    subparser.add_argument("--file", help="read the source text from a UTF-8 file")
    subparser.add_argument("--bundle", help="the bundle folder (default: <work project>\\Output\\ftt_bundle)")
    subparser.add_argument("--hcparse", required=True, help='the command that runs hcparse, without its file arguments, e.g. "dotnet /opt/hcparse/HCParse.dll"')
    subparser.add_argument("--transfer", action="store_true", help="also run the Apertium transfer and print the target stream")
    subparser.add_argument("--tools", help="the folder with the Apertium tools (FlexTools\\Tools on Windows; default: on PATH)")
    subparser.add_argument("--synthesize", action="store_true", help="also synthesize the target text with HermitCrab and print it (implies --transfer)")
    subparser.add_argument("--hcsynth", help='the command that runs HCSynthByGloss, without its arguments, e.g. "dotnet /opt/hcsynth/HCSynthByGloss.dll"')
    subparser.add_argument("--synth-dir", dest="synthDir", help="the folder for the synthesis files (master, parses, surface forms); default: a new temporary folder")
    subparser.set_defaults(func=cmdOfflineStream)

    subparser = subparsers.add_parser("serve-offline", help="without FieldWorks: the browser front end, translating from a bundle alone (for Linux hosts such as Railway)")
    subparser.add_argument("--bundle", required=True, help="the bundle folder (a copy of <work project>\\Output\\ftt_bundle)")
    subparser.add_argument("--hcparse", required=True, help='the command that runs hcparse, without its file arguments, e.g. "dotnet /opt/hcparse/HCParse.dll"')
    subparser.add_argument("--hcsynth", required=True, help='the command that runs HCSynthByGloss, without its arguments, e.g. "dotnet /opt/hcsynth/HCSynthByGloss.dll"')
    subparser.add_argument("--tools", help="the folder with the Apertium tools (FlexTools\\Tools on Windows; default: on PATH)")
    subparser.add_argument("--host", default="127.0.0.1", help="the address to listen on (default 127.0.0.1; 0.0.0.0 for every interface, as on a server)")
    subparser.add_argument("--port", type=int, default=8765, help="the port to listen on (default 8765)")
    subparser.add_argument("-v", "--verbose", action="store_true", help="show each request in the console")
    subparser.set_defaults(func=cmdServeOffline)

    args = argParser.parse_args(argv)

    # Shut FieldWorks down however the command ends
    try:
        return args.func(args)
    finally:
        from . import env
        env.cleanup()
