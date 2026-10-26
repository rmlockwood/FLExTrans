#
#   parse_priority/cli
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The parse_priority command line for experimenting with FieldWorks' analysis guesser.
#
#   OVERVIEW (AI generated, then edited)
#
#   The command line for parse_priority, run as python -m parse_priority. It is a tool for seeing and changing how FieldWorks' analysis guesser ranks the analyses of a word in context; see
#   parse_priority_README.md for what the guesser does and a worked example. The commands fall into three groups:
#    - Read-only: analyses (a word's analyses, numbered), rank (the guesser's ranking for each occurrence, with the numbers behind it) and parse without --save.
#    - Writing: assign, add, approve and demo. These are dry runs by default - see DRY RUNS below.
#    - Utility: copy, which copies a project folder to a scratch project.
#
#   DRY RUNS
#
#   The writing commands open the project undoable and do all their changes in one UndoableOperation (runWriting()). They show the result and then undo it, unless --commit is given, so the
#   project is left as it was. parse --save is the exception: filing parser results can't be undone (see parsing.py), so it is opt-in instead.
#
#   CODE STRUCTURE
#
#   Output helpers first: printAnalyses(), currentLabel(), printRanking() and top(). Then selectOccurrences() and runWriting(), which the commands share, then one cmd function per command in
#   the order copy, analyses, rank, parse, approve, assign, add, demo. main() sets up argparse and runs the chosen command. The command line flags keep their dashes (--parser-mode); argparse is
#   given camelCase dest names so the code reads args.parserMode.
#

import argparse
import sys

from . import fw
from . import textedit
from .guesser import Ranker, approval, describe, findOccurrences, findWordform, formOf, pickAnalysis, sortedAnalyses

# Short names for the guesser's priorities, for the rank table
PRIORITY_NAMES = {7: "in-text", 6: "human", 5: "parser", 4: "computer", 3: "none", 2: "parser-no", 1: "human-no", 0: "-"}

def printAnalyses(ranker, wordform):
    '''Print a wordform's analyses, numbered as pickAnalysis() expects, with each one's approval status and how often texts use it.'''

    # How many times each analysis (by GUID) is used in texts
    usedCounts = {}

    for segment in wordform.OccurrencesInTexts:

        for index in range(segment.AnalysesRS.Count):

            analysis = segment.AnalysesRS[index]

            if analysis.ClassName in ("WfiAnalysis", "WfiGloss") and analysis.Wordform.Hvo == wordform.Hvo:

                analysisKey = str(analysis.Analysis.Guid)
                usedCounts[analysisKey] = usedCounts.get(analysisKey, 0) + 1

    print(f"Analyses of '{formOf(wordform)}':")

    for number, wordAnalysis in enumerate(sortedAnalyses(wordform), 1):

        print(f"  {number}. {describe(wordAnalysis):40s} {approval(ranker.guesser, wordAnalysis):18s} used in texts: {usedCounts.get(str(wordAnalysis.Guid), 0)}   {str(wordAnalysis.Guid)[:8]}")

def currentLabel(occurrence):
    '''What the occurrence has now: its analysis, or a note that it has none and FLEx shows a guess.'''

    analysis = occurrence.analysis

    if analysis.ClassName == "WfiWordform":

        return "(unanalysed - FLEx shows a guess)"

    wordAnalysis = analysis if analysis.ClassName == "WfiAnalysis" else analysis.Analysis

    return describe(wordAnalysis)

def printRanking(ranker, occurrence, ignoreSelf=False, label=None):
    '''Print the occurrence's context, current analysis, FLEx's guess and the full ranking with explain()'s numbers. Returns the ranking.'''

    ranked = ranker.ranked(occurrence, ignoreSelf)
    explained = ranker.explain(occurrence, ignoreSelf)
    heading = f"#{occurrence.number} {occurrence.location()}"

    if label:

        heading = f"{label}: {heading}"

    print(heading)
    print(f"    context : {occurrence.context()}")
    print(f"    current : {currentLabel(occurrence)}")

    if occurrence.isGuessable:

        guess = ranker.bestGuess(occurrence)

        if guess.ClassName == "WfiGloss":

            guess = guess.Analysis

        shown = describe(guess) if guess.ClassName == "WfiAnalysis" else "(none)"
        print(f"    FLEx guess: {shown}")

    print(f"    {'rank':4s} {'prev+next=score':>17s}  {'priority':9s} {'count':>5s}  analysis")

    for number, wordAnalysis in enumerate(ranked, 1):

        numbers = explained.get(str(wordAnalysis.Guid))

        # An analysis of a case variant of the word, which explain() doesn't cover
        if numbers is None:

            print(f"    {number:<4d} {'':17s}  {'':9s} {'':5s}  {describe(wordAnalysis)}  (case variant)")
            continue

        print(f"    {number:<4d} {numbers.prevScore:.2f}+{numbers.nextScore:.2f}={numbers.score:.2f}  {PRIORITY_NAMES[numbers.priority]:9s} {numbers.count:5d}  {describe(wordAnalysis)}")

    return ranked

def top(ranked):
    '''The description of the top analysis in a ranking.'''

    return describe(ranked[0]) if ranked else "(nothing)"

def selectOccurrences(project, args):
    '''Return the occurrences of args.word (in args.text, if the command has --text), or only number args.occurrence if given. Stops with an error if there are none.'''

    occurrences = findOccurrences(project, args.word, getattr(args, "text", None))

    if not occurrences:

        raise SystemExit(f"'{args.word}' does not occur in any text")

    number = getattr(args, "occurrence", None)

    if number:

        if not 1 <= number <= len(occurrences):

            raise SystemExit(f"Occurrence must be 1..{len(occurrences)} (see the 'rank' command)")

        return [occurrences[number - 1]]

    return occurrences

def runWriting(args, body):
    '''Open the project for writing, run body(project, ranker) as one undoable operation, then keep it (--commit) or undo it so the project is left as it was. See DRY RUNS above.'''

    project = fw.openProject(args.project, write=True)

    try:
        ranker = Ranker(project, args.parserMode)

        with project.UndoableOperation("parse-priority experiment"):

            body(project, ranker)

        if args.commit:

            print("\nCommitted: changes are saved to the project.")
        else:
            project.Undo()
            print("\nRolled back (dry run). Use --commit to keep the changes.")

    finally:
        project.CloseProject()

def cmdCopy(args):

    newDir = fw.copyProject(args.project, args.newName)
    print(f"Copied to {newDir}")

def cmdAnalyses(args):

    project = fw.openProject(args.project)

    try:
        printAnalyses(Ranker(project), findWordform(project, args.word))
    finally:
        project.CloseProject()

def cmdRank(args):

    project = fw.openProject(args.project)

    try:
        ranker = Ranker(project, args.parserMode)

        for occurrence in selectOccurrences(project, args):

            printRanking(ranker, occurrence, args.ignoreSelf)
            print()

    finally:
        project.CloseProject()

def cmdParse(args):

    from .parsing import Filer, parseText

    project = fw.openProject(args.project, write=args.save)

    try:
        results = parseText(project, args.text)

        # List each word's parses, marking the ones the project doesn't have yet
        for word, parses, error, _ in results:

            if error:

                print(f"{word}: ERROR {error}")
                continue

            if not parses:

                print(f"{word}: (no parse)")
                continue

            print(f"{word}:")

            for description, match in parses:

                status = "in project" if match is not None else "NEW"
                print(f"    {description:40s} {status}")

        if not args.save:

            print("\nNot saved (read-only). Use --save to file these results into the project.")
            return

        # The guesser only counts approvals from the active parser
        activeParser = project.project.LangProject.MorphologicalDataOA.ActiveParser

        if activeParser != "HC":

            print(f"\nWARNING: the project's active parser is {activeParser}, not HermitCrab. The results are saved as approved by HCParser, but FLEx's guesser only counts approvals from the active parser, so they will rank as 'no opinion'. To make them count, choose HermitCrab in FLEx (Parser > Choose Parser).")

        filer = Filer(project)
        filedCount, declined = 0, []

        for word, _, error, parseResult in results:

            # Don't let a parser error count as "no parses" and disapprove everything
            if error:

                continue

            if filer.file(word, parseResult):

                filedCount += 1
            else:
                declined.append(word)

        print(f"\nSaved parser results for {filedCount} word(s).")

        if declined:

            print(f"Filer declined: {', '.join(declined)}")

    finally:
        project.CloseProject()

def cmdApprove(args):

    def body(project, ranker):

        occurrences = findOccurrences(project, textName=args.text)

        if not occurrences:

            raise SystemExit(f"No words found in text '{args.text}'")

        approved = textedit.approveGuesses(ranker, occurrences)

        for occurrence, guess, basis in approved:

            wordAnalysis = guess.Analysis if guess.ClassName == "WfiGloss" else guess
            print(f"  {formOf(occurrence.analysis):15s} -> {describe(wordAnalysis):40s} ({basis})")

        print(f"\nApproved {len(approved)} of {len(occurrences)} word(s) in '{args.text}'.")

    runWriting(args, body)

def cmdAssign(args):

    def body(project, ranker):

        occurrence = selectOccurrences(project, args)[0]
        wordAnalysis = pickAnalysis(occurrence.wordform, args.analysis)
        printRanking(ranker, occurrence, args.ignoreSelf, "BEFORE")
        textedit.assign(project, occurrence, wordAnalysis, approve=not args.noApprove)
        print(f"\nAssigned '{describe(wordAnalysis)}' to #{occurrence.number}\n")

        # Show how the change moved the ranking of the word's other occurrences
        others = [other for other in findOccurrences(project, args.word) if other.number != occurrence.number]

        for other in others:

            printRanking(ranker, other, label="AFTER")
            print()

    runWriting(args, body)

def cmdAdd(args):

    def body(project, ranker):

        # Each --assign is WORD=ANALYSIS
        assignments = {}

        for item in args.assign or []:

            word, _, selector = item.partition("=")
            wordform = findWordform(project, word)
            assignments[word.lower()] = pickAnalysis(wordform, selector)

        assignedCount, _ = textedit.addSentence(project, args.text, args.sentence, assignments, approve=not args.noApprove)
        print(f"Added to '{args.text}': {args.sentence}  ({assignedCount} occurrence(s) assigned)\n")

        for word in assignments:

            printAnalyses(ranker, findWordform(project, word))

    runWriting(args, body)

def cmdDemo(args):
    '''Pick one occurrence, then add training sentences that repeat its neighbouring words with the word analysed as --to, until (or unless) the guesser's top choice for that occurrence
       flips.'''

    def body(project, ranker):

        occurrence = selectOccurrences(project, args)[0]
        wordAnalysis = pickAnalysis(occurrence.wordform, args.to)
        before = printRanking(ranker, occurrence, args.ignoreSelf, "BEFORE")

        if before and before[0].Guid == wordAnalysis.Guid:

            print(f"\n'{describe(wordAnalysis)}' is already the top choice here.")
            return

        sentence = textedit.trainingSentence(occurrence)
        word = formOf(occurrence.analysis).lower()
        print(f"\nTraining sentence: \"{sentence}\"  (with '{word}' = {describe(wordAnalysis)})")

        # Add one sentence at a time and stop as soon as the top choice flips
        for sentenceCount in range(1, args.max + 1):

            textedit.addSentence(project, args.trainText, sentence, {word: wordAnalysis}, approve=not args.noApprove)
            ranker.refresh()
            ranked = ranker.ranked(occurrence, args.ignoreSelf)
            print(f"  after {sentenceCount} sentence(s): top = {top(ranked)}")

            if ranked and ranked[0].Guid == wordAnalysis.Guid:

                break

        print()
        after = printRanking(ranker, occurrence, args.ignoreSelf, "AFTER")
        flipped = after and after[0].Guid == wordAnalysis.Guid
        print(f"\nResult: top choice {'FLIPPED to' if flipped else 'is still not'} '{describe(wordAnalysis)}'")

    runWriting(args, body)

def main(argv=None):

    # Vernacular text (e.g. combining diacritics) must survive piped or redirected output. The streams are typed as TextIO, which has no reconfigure(), but they are TextIOWrappers here.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

    argParser = argparse.ArgumentParser(prog="parse_priority", description="Experiment with FieldWorks' analysis guesser.")
    subparsers = argParser.add_subparsers(dest="cmd", required=True)

    # The project and word, and the ranking options, shared by most commands
    def addCommon(subparser, word=True):

        subparser.add_argument("project", help="FieldWorks project name (must be closed in FLEx)")

        if word:

            subparser.add_argument("word", help="the wordform to look at")

        subparser.add_argument("--parser-mode", dest="parserMode", action="store_true", help="rank as in Parsing Development mode (parser approval first)")
        subparser.add_argument("--ignore-self", dest="ignoreSelf", action="store_true", help="leave the occurrence's own analysis out of the counts")

    # The options of the commands that write
    def addWriting(subparser):

        subparser.add_argument("--commit", action="store_true", help="keep the changes (default: roll back after showing results)")
        subparser.add_argument("--no-approve", dest="noApprove", action="store_true", help="don't mark assigned analyses as human-approved")

    subparser = subparsers.add_parser("copy", help="copy a project to a scratch project")
    subparser.add_argument("project")
    subparser.add_argument("newName", metavar="new_name")
    subparser.set_defaults(func=cmdCopy)

    subparser = subparsers.add_parser("analyses", help="list a word's analyses with numbers")
    addCommon(subparser)
    subparser.set_defaults(func=cmdAnalyses)

    subparser = subparsers.add_parser("rank", help="show the guesser's ranking for each occurrence")
    addCommon(subparser)
    subparser.add_argument("--text", help="only this text (by title)")
    subparser.add_argument("-n", "--occurrence", type=int, help="only occurrence number N")
    subparser.set_defaults(func=cmdRank)

    subparser = subparsers.add_parser("parse", help="run the HermitCrab parser on each word of a text (read-only)")
    subparser.add_argument("project")
    subparser.add_argument("--text", help="only this text (by title); default all texts")
    subparser.add_argument("--save", action="store_true", help="file the results into the project like FLEx's Parse Words in Text (cannot be undone; may delete unapproved, unused analyses)")
    subparser.set_defaults(func=cmdParse)

    subparser = subparsers.add_parser("approve", help="approve the guesser's top parse for every word in a text (like FLEx's Approve All)")
    subparser.add_argument("project")
    subparser.add_argument("--text", required=True, help="text title")
    subparser.add_argument("--parser-mode", dest="parserMode", action="store_true", help="rank as in Parsing Development mode (parser approval first)")
    subparser.add_argument("--commit", action="store_true", help="keep the approvals (default: roll back after showing them)")
    subparser.set_defaults(func=cmdApprove)

    subparser = subparsers.add_parser("assign", help="set an occurrence's analysis, then re-rank the others")
    addCommon(subparser)
    addWriting(subparser)
    subparser.add_argument("-n", "--occurrence", type=int, required=True)
    subparser.add_argument("-a", "--analysis", required=True, help="analysis number (see 'analyses'), GUID prefix or gloss substring")
    subparser.set_defaults(func=cmdAssign)

    subparser = subparsers.add_parser("add", help="append a sentence to a text with chosen analyses")
    addCommon(subparser, word=False)
    addWriting(subparser)
    subparser.add_argument("--text", required=True, help="text title (created if missing)")
    subparser.add_argument("sentence")
    subparser.add_argument("--assign", action="append", metavar="WORD=ANALYSIS", help="analysis for a word in the sentence (repeatable)")
    subparser.set_defaults(func=cmdAdd)

    subparser = subparsers.add_parser("demo", help="add training sentences until an occurrence's top guess flips")
    addCommon(subparser)
    addWriting(subparser)
    subparser.add_argument("-n", "--occurrence", type=int, required=True)
    subparser.add_argument("--to", required=True, help="the analysis to promote")
    subparser.add_argument("--max", type=int, default=5, help="most training sentences to add")
    subparser.add_argument("--train-text", dest="trainText", default="Parse priority training", help="text the training sentences go into (created if missing)")
    subparser.set_defaults(func=cmdDemo)

    args = argParser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":

    sys.exit(main())
