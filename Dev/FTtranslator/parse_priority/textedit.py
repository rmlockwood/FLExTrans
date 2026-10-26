"""
Changing texts so the guesser's counts change.

Two kinds of edit move the counts:
  * assigning an analysis to an occurrence that is already in a text
    (what a user does by confirming a guess or picking a parse in the
    Analyze/Gloss tab);
  * adding new sentences in which the word is analysed a particular way.

Both must run inside a unit of work; callers wrap them in
project.UndoableOperation() so a whole run can be undone.
"""

from . import fw
from .guesser import find_occurrences, form_of, iter_texts


def assign(project, occurrence, analysis, approve=True):
    """Set an occurrence's analysis, as confirming a parse in FLEx does."""
    seg = occurrence.segment
    seg.AnalysesRS[occurrence.index] = analysis
    if approve:
        _approve(project, analysis)


def _approve(project, analysis):
    # FLEx records a human-approved evaluation when a user confirms an analysis.
    # `analysis` may be a WfiGloss; the evaluation goes on its owning analysis.
    lp = project.project.LangProject
    from SIL.LCModel import Opinions
    fw.lcm.IWfiAnalysis(analysis.Analysis).SetAgentOpinion(lp.DefaultUserAgent, Opinions.approves)


def approve_guesses(ranker, occurrences):
    """
    Approve the guesser's top choice for every occurrence that has a guess,
    as FLEx's Approve All does: all guesses are taken first, then applied,
    so earlier approvals don't change later guesses. The guess may be a
    gloss (when the analysis has one); it is stored as is.
    Returns [(occurrence, guess, basis)] for the approved ones.
    """
    planned = []
    for occ in occurrences:
        if occ.analysis.ClassName not in ("WfiWordform", "WfiAnalysis"):
            continue  # already glossed
        guess = ranker.best_guess(occ)
        if _class(guess) not in ("WfiAnalysis", "WfiGloss") or guess.Hvo == occ.analysis.Hvo:
            continue
        planned.append((occ, guess, ranker.basis(occ)))
    for occ, guess, _ in planned:
        occ.segment.AnalysesRS[occ.index] = guess
        _approve(ranker.project, guess)
    return planned


def _class(obj):
    try:
        return obj.ClassName  # a NullWAG ("no guess") has none
    except Exception:
        return None


def get_or_create_text(project, title):
    for name, text in iter_texts(project, title):
        return text
    return project.Texts.Create(title)


def add_sentence(project, text_title, sentence, assignments, approve=True):
    """
    Append `sentence` as a new paragraph of `text_title` (created if missing),
    tokenise it into segments/wordforms the way FLEx does, then set
    analyses: `assignments` maps a lowercase word to an IWfiAnalysis and is
    applied to every occurrence of that word in the new paragraph.
    Returns the number of occurrences assigned.
    """
    lcm = fw.lcm
    text = get_or_create_text(project, text_title)
    para = lcm.IStTxtPara(project.Paragraphs.Create(text, sentence))
    lcm.ParagraphParser.ParseParagraph(para, True, True)
    assigned = 0
    for seg in para.SegmentsOS:
        for i in range(seg.AnalysesRS.Count):
            a = seg.AnalysesRS[i]
            target = assignments.get(form_of(a).lower())
            if target is None:
                continue
            seg.AnalysesRS[i] = target
            if approve:
                _approve(project, target)
            assigned += 1
    return assigned, para


def training_sentence(occurrence):
    """'<prev> <word> <next>' from an occurrence's own context, for add-context training."""
    words = []
    prev = occurrence.neighbour(True)
    nxt = occurrence.neighbour(False)
    if prev != "<edge>":
        words.append(form_of(prev))
    words.append(form_of(occurrence.analysis))
    if nxt != "<edge>":
        words.append(form_of(nxt))
    sentence = " ".join(words)
    # Close the sentence so each training sentence is its own segment.
    if not sentence.endswith((".", "!", "?")):
        sentence += "."
    return sentence
