#
#   fttranslator/steps/ingest
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.1 - 10/26/26 - Ron Lockwood
#    The default title of the imported text ends with the text's first three words. The title is read back as stored (NFD) so FLExTrans finds non-ASCII titles.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The first three steps: import the text, parse its words with HermitCrab, approve the guesser's choices.
#
#   OVERVIEW (AI generated, then edited)
#
#   These steps get the source text into the source project with the analyses FLExTrans needs. Import Text adds it as a new text, Parse Words parses each distinct word with HermitCrab and files
#   the results as FLEx's Parse Words in Text does, and Approve Guesses approves the guesser's most likely analysis for each word in context, as FLEx's Approve All does. The parsing and guessing
#   themselves are in parse_priority; these steps put them in order and record what happened in the run result.
#
#   APPROVALS ARE TEMPORARY BY DEFAULT
#
#   The guesser counts an analysis used in a text above everything else (priority 7), so auto-approved mistakes would vote for themselves in every later translation. Unless --keep-approvals is
#   given, the approvals are kept only long enough for Extract Source Text to read them, and then undone (releaseApprovals). The text stays in the project with its words unapproved; FLEx shows
#   the same guesses there, and a person who confirms them in FLEx adds them to the corpus.
#
#   Undo takes back the most recent undoable operation, so releasing is only safe while the approvals are still on top of the undo stack. approveGuesses() records the stack depth right after
#   approving (in ctx.state), and releaseApprovals() undoes only if the depth is unchanged. If a custom step has changed the source project in between, the approvals are kept and a warning given.
#   releaseApprovals() runs once - Extract Source Text calls it, and Translator.translate() calls it again in case the run stopped earlier; the state entry is removed the first time.
#
#   TRAPS
#
#    - FieldWorks stores the title decomposed (NFD), and FLExTrans modules compare SourceTextName with == against the stored titles. importText() reads the title back after creating the text,
#      so a title with an accented letter (from --title or the text's first words) still matches.
#    - Filing parser results (parse_priority's Filer) can't be undone, as in FLEx. It runs outside any unit of work, so Parse Words is not wrapped in an UndoableOperation.
#    - A parser error on a word must not be filed as "no parses", or the filer would mark every existing analysis of the word as parser-disapproved. Such a word is skipped.
#    - HermitCrab-filed analyses have an msa but no sense on each morph bundle, and FLExTrans then reports "No sense found". fillSenses() sets each bundle's sense from its msa while approving,
#      as FLEx does when a parse is confirmed.
#
#   CODE STRUCTURE
#
#   uniqueTitle() picks an unused title for the new text, and firstWords() gives the words the default title ends with. Then the three steps in pipeline order: importText(), parseWords() and approveGuesses() (with its helper fillSenses()). _undoDepth() and
#   releaseApprovals() undo the approvals. STEPS lists the steps for Translator.steps().
#

import unicodedata
from datetime import datetime

from parse_priority import textedit
from parse_priority.guesser import Ranker, describe, findOccurrences, formOf, iterTexts, senseForMsa, titleKey
from parse_priority.parsing import Filer, parseText

from ..pipeline import Step

# The ctx.state entry holding the undo-stack depth right after the approvals, while they are still to be released
APPROVALS_PENDING = "approvalsPending"

def uniqueTitle(project, title):
    '''Return title, or title with " (2)", " (3)", ... added if a text already has it. Titles are compared case-insensitively, as FLEx does, and ignoring Unicode normalization.'''

    existing = {titleKey(name) for name, _ in iterTexts(project)}

    if titleKey(title) not in existing:

        return title

    number = 2

    while titleKey(f"{title} ({number})") in existing:

        number += 1

    return f"{title} ({number})"

def firstWords(paragraphs, count):
    '''Return the first count words of the text, without the punctuation that ends the last one (e.g. "Bonjour." gives "Bonjour").'''

    words = " ".join(paragraphs).split()[:count]
    snippet = " ".join(words)

    # Strip by Unicode category rather than with \w, which would also strip a combining diacritic at the end of a word
    while snippet and unicodedata.category(snippet[-1]).startswith("P"):

        snippet = snippet[:-1]

    return snippet

def importText(ctx):
    '''Add the source text to the source project as a new text, one paragraph per non-blank line, and point this run's configuration at it.'''

    paragraphs = [line.strip() for line in ctx.result.source.splitlines() if line.strip()]

    if not paragraphs:

        ctx.report.Error("There is no source text to translate.")
        return False

    # The default title ends with the first few words of the text, so the texts FTtranslator adds can be told apart in FLEx's list of texts
    stamp = datetime.now().strftime("%Y-%m-%d %H%M%S")
    title = uniqueTitle(ctx.db, ctx.options.title or f"{ctx.profile.titlePrefix} {stamp} {firstWords(paragraphs, 3)}")

    with ctx.db.UndoableOperation("FTtranslator: import text"):

        for paragraph in paragraphs:

            textedit.addSentence(ctx.db, title, paragraph, {}, approve=False)

    # Use the title as FieldWorks stored it. It is stored decomposed (NFD), and FLExTrans compares titles exactly, so "garçons" as typed (NFC) wouldn't be found by Extract Source Text.
    for storedTitle, _ in iterTexts(ctx.db, title):

        title = storedTitle
        break

    ctx.result.title = title

    # FLExTrans reads the text to translate from SourceTextName. Only this run's copy of the configuration changes; FlexTrans.config is untouched.
    import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

    ctx.configMap[ReadConfig.SOURCE_TEXT_NAME] = title
    ctx.report.Info(f"Added text '{title}' ({len(paragraphs)} paragraph(s)).")

    return True

def parseWords(ctx):
    '''Parse each distinct word of the new text with HermitCrab and file the results into the source project. Words with no parse are recorded in the run result.'''

    activeParser = ctx.db.project.LangProject.MorphologicalDataOA.ActiveParser

    # The guesser only counts approvals from the active parser
    if activeParser != "HC":

        ctx.report.Warning(f"The source project's active parser is {activeParser}, not HermitCrab. Parser approvals will rank as 'no opinion' in the guesser (choose HermitCrab in FLEx: Parser > Choose Parser).")

    results = parseText(ctx.db, ctx.result.title)
    filer = Filer(ctx.db)

    for word, parses, error, parseResult in results:

        # A parser error must not count as "no parses", which would disapprove every analysis of the word
        if error:

            ctx.report.Warning(f"Parser error on '{word}': {error}")
            ctx.result.unparsed.append(word)
            continue

        if not parses:

            ctx.result.unparsed.append(word)

        if not filer.file(word, parseResult):

            ctx.report.Warning(f"The parse filer declined '{word}'.")

    ctx.report.Info(f"Parsed {len(results)} distinct word(s); {len(ctx.result.unparsed)} with no parse.")
    return True

def approveGuesses(ctx):
    '''Approve the guesser's top analysis for every word of the new text, and record what was approved and what was left without an analysis.'''

    ranker = Ranker(ctx.db)
    occurrences = findOccurrences(ctx.db, textName=ctx.result.title)

    with ctx.db.UndoableOperation("FTtranslator: approve guesses"):

        approved = textedit.approveGuesses(ranker, occurrences)

        for _, guess, _ in approved:

            fillSenses(guess)

    # Remember where the approvals sit on the undo stack, so releaseApprovals() can tell whether it is still safe to undo them
    if not ctx.options.keepApprovals:

        ctx.state[APPROVALS_PENDING] = _undoDepth(ctx)

    approvedPositions = set()

    for occurrence, guess, basis in approved:

        wordAnalysis = guess.Analysis if guess.ClassName == "WfiGloss" else guess
        ctx.result.approved.append({"word": formOf(occurrence.analysis), "location": occurrence.location(), "analysis": describe(wordAnalysis), "basis": basis})
        approvedPositions.add((occurrence.para, occurrence.seg, occurrence.index))

    ctx.result.unanalysed = [formOf(occurrence.analysis) for occurrence in occurrences if (occurrence.para, occurrence.seg, occurrence.index) not in approvedPositions and occurrence.isGuessable]
    ctx.report.Info(f"Approved {len(approved)} of {len(occurrences)} word(s).")

    return True

def fillSenses(guess):
    '''Give each morph of a parser-made analysis a sense, as FLEx does when a user confirms a parse. The parser only sets the msa, and FLExTrans needs senses (for glosses and for the links
       to the target lexicon).'''

    from parse_priority import fw

    wordAnalysis = fw.lcm.IWfiAnalysis(guess.Analysis if guess.ClassName == "WfiGloss" else guess)

    for bundle in wordAnalysis.MorphBundlesOS:

        if bundle.SenseRA is None and bundle.MsaRA is not None:

            sense = senseForMsa(bundle.MsaRA)

            if sense is not None:

                bundle.SenseRA = sense

def _undoDepth(ctx):

    return ctx.db.project.ActionHandlerAccessor.UndoableSequenceCount

def releaseApprovals(ctx):
    '''Undo the guess approvals, once, unless they are to be kept. Keeps them, with a warning, if another step has changed the source project since. See APPROVALS ARE TEMPORARY BY DEFAULT above.'''

    depth = ctx.state.pop(APPROVALS_PENDING, None)

    # Nothing to release: kept on purpose, never approved, or already released
    if depth is None:

        return True

    if _undoDepth(ctx) != depth:

        ctx.report.Warning("A step changed the source project after the guesses were approved, so the approvals were kept (as with --keep-approvals). Review the text in FLEx.")
        return True

    ctx.db.Undo()
    ctx.report.Info("Guessed analyses released; the text is left for review in FLEx.")

    return True

STEPS = [Step("Import Text", importText, "ftt"), Step("Parse Words", parseWords, "ftt"), Step("Approve Guesses", approveGuesses, "ftt")]
