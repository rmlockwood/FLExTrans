"""
Getting the source text into the source project with the right analyses:
import it as a new text, parse its words with HermitCrab, then approve the
guesser's most likely analysis for each word in context.

Approvals are temporary by default. In-text analyses count most for the
guesser (priority 7), so auto-approved mistakes would vote for themselves in
every later translation. The approvals are kept only long enough for the
source text to be extracted, then undone (release_approvals); the text stays
in the project with its words unapproved, FLEx shows the same guesses, and a
person who confirms them in FLEx adds them to the corpus. --keep-approvals
keeps them as FLExTrans users normally would.
"""

from datetime import datetime

from parse_priority import textedit
from parse_priority.guesser import (Ranker, describe, find_occurrences, form_of, iter_texts,
                                    sense_for_msa)
from parse_priority.parsing import Filer, parse_text

from ..pipeline import Step


def unique_title(project, title):
    existing = {name.lower() for name, _ in iter_texts(project)}  # titles match case-insensitively
    if title.lower() not in existing:
        return title
    n = 2
    while f"{title} ({n})".lower() in existing:
        n += 1
    return f"{title} ({n})"


def import_text(ctx):
    paragraphs = [p.strip() for p in ctx.result.source.splitlines() if p.strip()]
    if not paragraphs:
        ctx.report.Error("There is no source text to translate.")
        return False
    stamp = datetime.now().strftime("%Y-%m-%d %H%M%S")
    title = unique_title(ctx.db, ctx.options.title or f"{ctx.profile.title_prefix} {stamp}")
    with ctx.db.UndoableOperation("FTtranslator: import text"):
        for p in paragraphs:
            textedit.add_sentence(ctx.db, title, p, {}, approve=False)
    ctx.result.title = title
    # FLExTrans reads the text to translate from SourceTextName. Only this
    # run's copy of the configuration changes; FlexTrans.config is untouched.
    import ReadConfig
    ctx.config_map[ReadConfig.SOURCE_TEXT_NAME] = title
    ctx.report.Info(f"Added text '{title}' ({len(paragraphs)} paragraph(s)).")
    return True


def parse_words(ctx):
    active = ctx.db.project.LangProject.MorphologicalDataOA.ActiveParser
    if active != "HC":
        ctx.report.Warning(
            f"The source project's active parser is {active}, not HermitCrab. Parser approvals "
            f"will rank as 'no opinion' in the guesser (choose HermitCrab in FLEx: Parser > Choose Parser).")
    results = parse_text(ctx.db, ctx.result.title)
    filer = Filer(ctx.db)
    for word, parses, error, result in results:
        if error:
            ctx.report.Warning(f"Parser error on '{word}': {error}")
            ctx.result.unparsed.append(word)
            continue  # a parser error must not count as "no parses" and disapprove everything
        if not parses:
            ctx.result.unparsed.append(word)
        if not filer.file(word, result):
            ctx.report.Warning(f"The parse filer declined '{word}'.")
    ctx.report.Info(f"Parsed {len(results)} distinct word(s); "
                    f"{len(ctx.result.unparsed)} with no parse.")
    return True


def approve_guesses(ctx):
    ranker = Ranker(ctx.db)
    occs = find_occurrences(ctx.db, text_name=ctx.result.title)
    with ctx.db.UndoableOperation("FTtranslator: approve guesses"):
        approved = textedit.approve_guesses(ranker, occs)
        for _, guess, _ in approved:
            fill_senses(guess)
    if not ctx.options.keep_approvals:
        ctx.state["approvals_pending"] = _undo_depth(ctx)
    done = set()
    for occ, guess, basis in approved:
        wa = guess.Analysis if guess.ClassName == "WfiGloss" else guess
        ctx.result.approved.append({"word": form_of(occ.analysis), "location": occ.location(),
                                    "analysis": describe(wa), "basis": basis})
        done.add((occ.para, occ.seg, occ.index))
    ctx.result.unanalysed = [form_of(o.analysis) for o in occs
                             if (o.para, o.seg, o.index) not in done and o.is_guessable]
    ctx.report.Info(f"Approved {len(approved)} of {len(occs)} word(s).")
    return True


def fill_senses(guess):
    """Give each morph of a parser-made analysis a sense, as FLEx does when a
    user confirms a parse. The parser only sets the msa, and FLExTrans needs
    senses (for glosses and the links to the target lexicon)."""
    from parse_priority import fw
    wa = fw.lcm.IWfiAnalysis(guess.Analysis if guess.ClassName == "WfiGloss" else guess)
    for bundle in wa.MorphBundlesOS:
        if bundle.SenseRA is None and bundle.MsaRA is not None:
            sense = sense_for_msa(bundle.MsaRA)
            if sense is not None:
                bundle.SenseRA = sense


def _undo_depth(ctx):
    return ctx.db.project.ActionHandlerAccessor.UndoableSequenceCount


def release_approvals(ctx):
    """Undo the guess approvals (once), unless they are to be kept.

    Undo takes back the most recent undoable operation, so this is only safe
    while the approvals are still on top of the stack. If a custom step has
    changed the source project since, the approvals are kept instead."""
    depth = ctx.state.pop("approvals_pending", None)
    if depth is None:
        return True
    if _undo_depth(ctx) != depth:
        ctx.report.Warning("A step changed the source project after the guesses were approved, "
                           "so the approvals were kept (as with --keep-approvals). Review the text in FLEx.")
        return True
    ctx.db.Undo()
    ctx.report.Info("Guessed analyses released; the text is left for review in FLEx.")
    return True


STEPS = [
    Step("Import Text", import_text, "ftt"),
    Step("Parse Words", parse_words, "ftt"),
    Step("Approve Guesses", approve_guesses, "ftt"),
]
