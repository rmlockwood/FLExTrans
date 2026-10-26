#
#   fttranslator/cli
#
#   Ron Lockwood
#   SIL International
#   10/26/26
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
#   ENCODINGS
#
#   main() switches stdout and stderr to UTF-8 so vernacular text survives a Windows console code page or a redirect, and reads stdin as UTF-8 with an optional byte-order mark. The command line
#   flags keep their dashes (--keep-approvals); argparse is given camelCase dest names so the code reads args.keepApprovals.
#
#   CODE STRUCTURE
#
#   _translator() builds the Translator for a command. Then cmdTranslate() with its helpers stdoutToStderr(), summarize() and _unique(), followed by cmdSteps(), cmdCheck() and cmdRuns(). main()
#   sets up argparse, runs the chosen command and shuts FieldWorks down with env.cleanup() however the command ends.
#

import argparse
import contextlib
import json
import os
import shutil
import sys
from pathlib import Path

# Shown by --help
USAGE_TEXT = """
Command line for FTtranslator: end-to-end translation with FLEx and FLExTrans.

  translate WORKDIR [TEXT] [--file F]   translate a text, print the result
  steps     WORKDIR                     list the pipeline that would run
  check     WORKDIR                     check projects, tools and configuration
  runs      WORKDIR                     list earlier runs and the words that failed

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

    translator = _translator(args)

    with stdoutToStderr():

        result = translator.translate(text, Options(insert=args.insert, keepApprovals=args.keepApprovals, title=args.title))

    if args.json:

        Path(args.json).write_text(json.dumps(result.toDict(), ensure_ascii=False, indent=2), encoding="utf-8")

    if result.translation is not None:

        print(result.translation)

    summarize(result, sys.stderr)

    return 0 if result.ok else 1

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

def summarize(result, out):
    '''Print the words that failed, grouped by why, then OK or FAILED.'''

    def printWords(label, words):

        if words:

            print(f"{label} ({len(words)}): {', '.join(words)}", file=out)

    print(file=out)
    printWords("No parse", result.unparsed)
    printWords("No analysis", _unique(result.unanalysed))
    printWords("Not linked to target lexicon", result.untranslated)
    printWords("Not synthesized", result.unsynthesized)

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
    subparser.add_argument("-v", "--verbose", action="store_true", help="show all FLExTrans messages")
    subparser.set_defaults(func=cmdTranslate)

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

    args = argParser.parse_args(argv)

    # Shut FieldWorks down however the command ends
    try:
        return args.func(args)
    finally:
        from . import env
        env.cleanup()
