"""
Command line for experimenting with FieldWorks' parse guesser.

Read-only:   analyses, rank
Writing:     assign, add, demo   (rolled back unless --commit)
Utility:     copy
"""

import argparse
import sys

from . import fw
from .guesser import (Ranker, find_occurrences, find_wordform, sorted_analyses,
                      pick_analysis, describe, approval, form_of)
from . import textedit

PRIORITY_NAMES = {7: "in-text", 6: "human", 5: "parser", 4: "computer",
                  3: "none", 2: "parser-no", 1: "human-no", 0: "-"}


# ---------------------------------------------------------------- output

def print_analyses(ranker, wordform):
    used = {}
    for seg in wordform.OccurrencesInTexts:
        for i in range(seg.AnalysesRS.Count):
            a = seg.AnalysesRS[i]
            if a.ClassName in ("WfiAnalysis", "WfiGloss") and a.Wordform.Hvo == wordform.Hvo:
                k = str(a.Analysis.Guid)
                used[k] = used.get(k, 0) + 1
    print(f"Analyses of '{form_of(wordform)}':")
    for n, wa in enumerate(sorted_analyses(wordform), 1):
        print(f"  {n}. {describe(wa):40s} {approval(ranker.guesser, wa):18s} "
              f"used in texts: {used.get(str(wa.Guid), 0)}   {str(wa.Guid)[:8]}")


def current_label(occ):
    a = occ.analysis
    if a.ClassName == "WfiWordform":
        return "(unanalysed - FLEx shows a guess)"
    wa = a if a.ClassName == "WfiAnalysis" else a.Analysis
    return describe(wa)


def print_ranking(ranker, occ, ignore_self=False, label=None):
    ranked = ranker.ranked(occ, ignore_self)
    why = ranker.explain(occ, ignore_self)
    head = f"#{occ.number} {occ.location()}"
    if label:
        head = f"{label}: {head}"
    print(head)
    print(f"    context : {occ.context()}")
    print(f"    current : {current_label(occ)}")
    if occ.is_guessable:
        guess = ranker.best_guess(occ)
        if guess.ClassName == "WfiGloss":
            guess = guess.Analysis
        shown = describe(guess) if guess.ClassName == "WfiAnalysis" else "(none)"
        print(f"    FLEx guess: {shown}")
    print(f"    {'rank':4s} {'prev+next=score':>17s}  {'priority':9s} {'count':>5s}  analysis")
    for n, wa in enumerate(ranked, 1):
        e = why.get(str(wa.Guid))
        if e is None:  # analysis of a case variant of the word
            print(f"    {n:<4d} {'':17s}  {'':9s} {'':5s}  {describe(wa)}  (case variant)")
            continue
        print(f"    {n:<4d} {e.prev_score:.2f}+{e.next_score:.2f}={e.score:.2f}"
              f"  {PRIORITY_NAMES[e.priority]:9s} {e.count:5d}  {describe(wa)}")
    return ranked


def top(ranked):
    return describe(ranked[0]) if ranked else "(nothing)"


# ---------------------------------------------------------------- helpers

def select_occurrences(project, args):
    occs = find_occurrences(project, args.word, getattr(args, "text", None))
    if not occs:
        raise SystemExit(f"'{args.word}' does not occur in any text")
    n = getattr(args, "occurrence", None)
    if n:
        if not 1 <= n <= len(occs):
            raise SystemExit(f"Occurrence must be 1..{len(occs)} (see the 'rank' command)")
        return [occs[n - 1]]
    return occs


def run_writing(args, body):
    """Open for writing, run body(project, ranker) as one undoable unit, then
    keep it (--commit) or undo it so the project is left as it was."""
    project = fw.open_project(args.project, write=True)
    try:
        ranker = Ranker(project, args.parser_mode)
        with project.UndoableOperation("parse-priority experiment"):
            body(project, ranker)
        if args.commit:
            print("\nCommitted: changes are saved to the project.")
        else:
            project.Undo()
            print("\nRolled back (dry run). Use --commit to keep the changes.")
    finally:
        project.CloseProject()


# ---------------------------------------------------------------- commands

def cmd_copy(args):
    dst = fw.copy_project(args.project, args.new_name)
    print(f"Copied to {dst}")


def cmd_analyses(args):
    project = fw.open_project(args.project)
    try:
        print_analyses(Ranker(project), find_wordform(project, args.word))
    finally:
        project.CloseProject()


def cmd_rank(args):
    project = fw.open_project(args.project)
    try:
        ranker = Ranker(project, args.parser_mode)
        for occ in select_occurrences(project, args):
            print_ranking(ranker, occ, args.ignore_self)
            print()
    finally:
        project.CloseProject()


def cmd_parse(args):
    from .parsing import parse_text, Filer
    project = fw.open_project(args.project, write=args.save)
    try:
        results = parse_text(project, args.text)
        for word, parses, error, _ in results:
            if error:
                print(f"{word}: ERROR {error}")
                continue
            if not parses:
                print(f"{word}: (no parse)")
                continue
            print(f"{word}:")
            for desc, match in parses:
                status = "in project" if match is not None else "NEW"
                print(f"    {desc:40s} {status}")
        if not args.save:
            print("\nNot saved (read-only). Use --save to file these results into the project.")
            return
        active = project.project.LangProject.MorphologicalDataOA.ActiveParser
        if active != "HC":
            print(f"\nWARNING: the project's active parser is {active}, not HermitCrab. The results "
                  f"are saved as approved by HCParser, but FLEx's guesser only counts approvals "
                  f"from the active parser, so they will rank as 'no opinion'. To make them count, "
                  f"choose HermitCrab in FLEx (Parser > Choose Parser).")
        filer = Filer(project)
        filed, failed = 0, []
        for word, _, error, result in results:
            if error:
                continue  # don't let a parser error count as "no parses" and disapprove everything
            if filer.file(word, result):
                filed += 1
            else:
                failed.append(word)
        print(f"\nSaved parser results for {filed} word(s).")
        if failed:
            print(f"Filer declined: {', '.join(failed)}")
    finally:
        project.CloseProject()


def cmd_approve(args):
    def body(project, ranker):
        occs = find_occurrences(project, text_name=args.text)
        if not occs:
            raise SystemExit(f"No words found in text '{args.text}'")
        approved = textedit.approve_guesses(ranker, occs)
        for occ, guess, basis in approved:
            wa = guess.Analysis if guess.ClassName == "WfiGloss" else guess
            print(f"  {form_of(occ.analysis):15s} -> {describe(wa):40s} ({basis})")
        print(f"\nApproved {len(approved)} of {len(occs)} word(s) in '{args.text}'.")
    run_writing(args, body)


def cmd_assign(args):
    def body(project, ranker):
        occ = select_occurrences(project, args)[0]
        wa = pick_analysis(occ.wordform, args.analysis)
        print_ranking(ranker, occ, args.ignore_self, "BEFORE")
        textedit.assign(project, occ, wa, approve=not args.no_approve)
        print(f"\nAssigned '{describe(wa)}' to #{occ.number}\n")
        others = [o for o in find_occurrences(project, args.word) if o.number != occ.number]
        for o in others:
            print_ranking(ranker, o, label="AFTER")
            print()
    run_writing(args, body)


def cmd_add(args):
    def body(project, ranker):
        assignments = {}
        for item in args.assign or []:
            word, _, sel = item.partition("=")
            wf = find_wordform(project, word)
            assignments[word.lower()] = pick_analysis(wf, sel)
        n, para = textedit.add_sentence(project, args.text, args.sentence, assignments,
                                        approve=not args.no_approve)
        print(f"Added to '{args.text}': {args.sentence}  ({n} occurrence(s) assigned)\n")
        for word in assignments:
            print_analyses(ranker, find_wordform(project, word))
    run_writing(args, body)


def cmd_demo(args):
    """
    Pick one occurrence, then add training sentences that repeat its
    neighbouring words with the word analysed as --to, until (or unless)
    the guesser's top choice for that occurrence flips.
    """
    def body(project, ranker):
        occ = select_occurrences(project, args)[0]
        wa = pick_analysis(occ.wordform, args.to)
        before = print_ranking(ranker, occ, args.ignore_self, "BEFORE")
        if before and before[0].Guid == wa.Guid:
            print(f"\n'{describe(wa)}' is already the top choice here.")
            return
        sentence = textedit.training_sentence(occ)
        word = form_of(occ.analysis).lower()
        print(f"\nTraining sentence: \"{sentence}\"  (with '{word}' = {describe(wa)})")
        for i in range(1, args.max + 1):
            textedit.add_sentence(project, args.train_text, sentence, {word: wa},
                                  approve=not args.no_approve)
            ranker.refresh()
            ranked = ranker.ranked(occ, args.ignore_self)
            print(f"  after {i} sentence(s): top = {top(ranked)}")
            if ranked and ranked[0].Guid == wa.Guid:
                break
        print()
        after = print_ranking(ranker, occ, args.ignore_self, "AFTER")
        flipped = after and after[0].Guid == wa.Guid
        print(f"\nResult: top choice {'FLIPPED to' if flipped else 'is still not'} "
              f"'{describe(wa)}'")
    run_writing(args, body)


# ---------------------------------------------------------------- argparse

def main(argv=None):
    # Vernacular text (e.g. combining diacritics) must survive piped/redirected output.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="parse_priority",
                                 description="Experiment with FieldWorks' analysis guesser.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, word=True):
        p.add_argument("project", help="FieldWorks project name (must be closed in FLEx)")
        if word:
            p.add_argument("word", help="the wordform to look at")
        p.add_argument("--parser-mode", action="store_true",
                       help="rank as in Parsing Development mode (parser approval first)")
        p.add_argument("--ignore-self", action="store_true",
                       help="leave the occurrence's own analysis out of the counts")

    def writing(p):
        p.add_argument("--commit", action="store_true",
                       help="keep the changes (default: roll back after showing results)")
        p.add_argument("--no-approve", action="store_true",
                       help="don't mark assigned analyses as human-approved")

    p = sub.add_parser("copy", help="copy a project to a scratch project")
    p.add_argument("project")
    p.add_argument("new_name")
    p.set_defaults(func=cmd_copy)

    p = sub.add_parser("analyses", help="list a word's analyses with numbers")
    common(p)
    p.set_defaults(func=cmd_analyses)

    p = sub.add_parser("rank", help="show the guesser's ranking for each occurrence")
    common(p)
    p.add_argument("--text", help="only this text (by title)")
    p.add_argument("-n", "--occurrence", type=int, help="only occurrence number N")
    p.set_defaults(func=cmd_rank)

    p = sub.add_parser("parse", help="run the HermitCrab parser on each word of a text (read-only)")
    p.add_argument("project")
    p.add_argument("--text", help="only this text (by title); default all texts")
    p.add_argument("--save", action="store_true",
                   help="file the results into the project like FLEx's Parse Words in Text "
                        "(cannot be undone; may delete unapproved, unused analyses)")
    p.set_defaults(func=cmd_parse)

    p = sub.add_parser("approve", help="approve the guesser's top parse for every word in a text "
                                       "(like FLEx's Approve All)")
    p.add_argument("project")
    p.add_argument("--text", required=True, help="text title")
    p.add_argument("--parser-mode", action="store_true",
                   help="rank as in Parsing Development mode (parser approval first)")
    p.add_argument("--commit", action="store_true",
                   help="keep the approvals (default: roll back after showing them)")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("assign", help="set an occurrence's analysis, then re-rank the others")
    common(p)
    writing(p)
    p.add_argument("-n", "--occurrence", type=int, required=True)
    p.add_argument("-a", "--analysis", required=True,
                   help="analysis number (see 'analyses'), GUID prefix or gloss substring")
    p.set_defaults(func=cmd_assign)

    p = sub.add_parser("add", help="append a sentence to a text with chosen analyses")
    common(p, word=False)
    writing(p)
    p.add_argument("--text", required=True, help="text title (created if missing)")
    p.add_argument("sentence")
    p.add_argument("--assign", action="append", metavar="WORD=ANALYSIS",
                   help="analysis for a word in the sentence (repeatable)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("demo", help="add training sentences until an occurrence's top guess flips")
    common(p)
    writing(p)
    p.add_argument("-n", "--occurrence", type=int, required=True)
    p.add_argument("--to", required=True, help="the analysis to promote")
    p.add_argument("--max", type=int, default=5, help="most training sentences to add")
    p.add_argument("--train-text", default="Parse priority training",
                   help="text the training sentences go into (created if missing)")
    p.set_defaults(func=cmd_demo)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
