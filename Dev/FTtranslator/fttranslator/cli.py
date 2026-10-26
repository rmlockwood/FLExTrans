"""
Command line for FTtranslator: end-to-end translation with FLEx and FLExTrans.

  translate WORKDIR [TEXT] [--file F]   translate a text, print the result
  steps     WORKDIR                     list the pipeline that would run
  check     WORKDIR                     check projects, tools and configuration
  runs      WORKDIR                     list earlier runs and the words that failed

WORKDIR is a FLExTrans work project folder (…\\WorkProjects\\<name>).
The FLEx projects must be closed in FieldWorks (or shared).
"""

import argparse
import contextlib
import json
import os
import shutil
import sys
from pathlib import Path


def _translator(args):
    from .translator import Translator
    return Translator(args.workdir, args.modules, verbose=getattr(args, "verbose", False))


def cmd_translate(args):
    from .pipeline import Options
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8-sig")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    t = _translator(args)
    with stdout_to_stderr():
        result = t.translate(text, Options(insert=args.insert, keep_approvals=args.keep_approvals,
                                           title=args.title))
    if args.json:
        Path(args.json).write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    if result.translation is not None:
        print(result.translation)
    summarize(result, sys.stderr)
    return 0 if result.ok else 1


@contextlib.contextmanager
def stdout_to_stderr():
    """Keep stdout for the translation: the tools FLExTrans runs (make, STAMP)
    write to the console, so point file descriptor 1 at stderr meanwhile."""
    sys.stdout.flush()
    saved = os.dup(1)
    os.dup2(2, 1)
    try:
        yield
    finally:
        sys.stdout.flush()
        os.dup2(saved, 1)
        os.close(saved)


def summarize(result, out):
    def line(label, words):
        if words:
            print(f"{label} ({len(words)}): {', '.join(words)}", file=out)
    print(file=out)
    line("No parse", result.unparsed)
    line("No analysis", _unique(result.unanalysed))
    line("Not linked to target lexicon", result.untranslated)
    line("Not synthesized", result.unsynthesized)
    status = "OK" if result.ok else f"FAILED after '{result.steps[-1]}'" if result.steps else "FAILED"
    where = f"; source text '{result.title}'" if result.title else ""
    print(f"{status}{where}", file=out)


def _unique(words):
    return list(dict.fromkeys(words))


def cmd_steps(args):
    t = _translator(args)
    print(f"Source project: {t.profile.source_project}")
    print(f"Collection:     {t.profile.collection_file}")
    for n, step in enumerate(t.steps(), 1):
        print(f"{n:3d}. {step.describe()}")
    return 0


def cmd_check(args):
    t = _translator(args)
    from .report import make_reporter
    report = make_reporter(verbose=False)
    cfg = t.read_config(report)
    import ReadConfig
    from flexlibs import AllProjectNames
    problems = []

    def check(ok, what):
        print(f"  [{'ok' if ok else 'XX'}] {what}")
        if not ok:
            problems.append(what)

    names = set(AllProjectNames())
    target = ReadConfig.getConfigVal(cfg, ReadConfig.TARGET_PROJECT, report, giveError=False)
    two = ReadConfig.getConfigVal(cfg, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) != "n"
    check(t.profile.source_project in names, f"source project '{t.profile.source_project}' exists")
    if two:
        check(target in names, f"target project '{target}' exists")
    tools = ["make.exe", "lt-comp.exe", "lt-proc.exe", "apertium-preprocess-transfer.exe",
             "apertium-transfer.exe"]
    hc = ReadConfig.getConfigVal(cfg, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False) == "y"
    if not hc:
        tools.append("stamp64.exe")
    for exe in tools:
        check((t.env.tools_dir / exe).exists(), f"{exe} in {t.env.tools_dir}")
    if hc:
        for exe in ("GenerateHCConfigForFLExTrans.exe", "HCSynthByGloss.exe"):
            check(shutil.which(exe) is not None, f"{exe} on PATH")
    try:
        steps = t.steps()
        check(True, f"pipeline resolves ({len(steps)} steps)")
    except SystemExit as e:
        check(False, f"pipeline: {e}")

    from parse_priority import fw
    try:
        p = fw.open_project(t.profile.source_project)
        try:
            active = p.project.LangProject.MorphologicalDataOA.ActiveParser
            check(active == "HC", f"source project's active parser is HermitCrab (it is {active})")
        finally:
            p.CloseProject()
    except SystemExit as e:
        check(False, str(e))
    print("\nAll checks passed." if not problems else f"\n{len(problems)} problem(s).")
    return 0 if not problems else 1


def cmd_runs(args):
    t = _translator(args)
    runs = t.runs()
    if not runs:
        print("No runs yet.")
    for r in runs[-args.last:]:
        print(f"{r['title']}  {'OK' if r['ok'] else 'FAILED'}")
        print(f"    source     : {r['source'].strip()[:70]}")
        if r.get("translation"):
            print(f"    translation: {r['translation'][:70]}")
        for label, key in (("no parse", "unparsed"), ("no analysis", "unanalysed"),
                           ("not linked to target", "untranslated"),
                           ("not synthesized", "unsynthesized")):
            if r.get(key):
                print(f"    {label:24s}: {', '.join(_unique(r[key]))}")
    return 0


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8-sig")
    ap = argparse.ArgumentParser(prog="fttranslator", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("workdir", help="FLExTrans work project folder")
        p.add_argument("--modules", help="FLExTrans modules folder (default: the installed one next "
                                         "to the work project); 'dev' means this repo's Dev\\Modules")

    p = sub.add_parser("translate", help="translate a text and print the result")
    common(p)
    p.add_argument("text", nargs="?", help="the source text (default: --file or stdin)")
    p.add_argument("--file", help="read the source text from a UTF-8 file")
    p.add_argument("--title", help="title for the new text in the source project")
    p.add_argument("--insert", action="store_true",
                   help="also insert the translation into the target project (Insert Target Text)")
    p.add_argument("--keep-approvals", action="store_true",
                   help="leave the guessed analyses approved in the source text (they then count "
                        "for future guesses); default: release them for review in FLEx")
    p.add_argument("--json", help="also write the run record (approvals, failures, messages) here")
    p.add_argument("-v", "--verbose", action="store_true", help="show all FLExTrans messages")
    p.set_defaults(func=cmd_translate)

    p = sub.add_parser("steps", help="list the pipeline steps")
    common(p)
    p.set_defaults(func=cmd_steps)

    p = sub.add_parser("check", help="check projects, tools and configuration")
    common(p)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("runs", help="list earlier runs and their failed words")
    common(p)
    p.add_argument("--last", type=int, default=10)
    p.set_defaults(func=cmd_runs)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    finally:
        from . import env
        env.cleanup()
