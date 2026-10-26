"""
Querying FieldWorks' analysis guesser for word occurrences in texts.

The guesser is SIL.LCModel.DomainServices.AnalysisGuessServices (liblcm). It is
not a trained model; it ranks a wordform's analyses with counts taken from the
texts every time it is asked (nothing is persisted):

  1. Context score = P(analysis | previous word) + P(analysis | next word),
     where the probabilities are counts of analyses already set on other
     occurrences of the word in texts, next to that same neighbouring word.
     Segment edges count as an "empty" neighbour.
  2. Ties fall back to a priority: used in a text (7) > human approved (6) >
     parser approved (5) > computer approved (4) > no opinion (3) >
     parser disapproved (2) > human disapproved (1).
  3. Then the raw count at that priority, then non-lowercased, then GUID.

The ranking shown by this tool always comes from the C# service itself. The
per-analysis numbers next to it (explain()) are a Python re-computation of
steps 1-3 for display; they ignore the guesser's merging of capitalised and
lowercase wordforms, so for a sentence-initial capitalised word they can differ.
"""

from dataclasses import dataclass, field

from . import fw

EMPTY = "<edge>"  # neighbour of the first/last word in a segment


# ---------------------------------------------------------------- formatting

def _text(ts):
    try:
        return ts.Text or ""
    except Exception:
        return ""


def form_of(analysis):
    """Surface form for any IAnalysis (wordform, analysis, gloss, punctuation)."""
    if analysis is None:
        return "?"
    if analysis.ClassName == "PunctuationForm":
        return _text(fw.lcm.IPunctuationForm(analysis).Form)
    wf = analysis.Wordform
    return _text(wf.Form.VernacularDefaultWritingSystem) if wf else "?"


def describe(wa):
    """'mang:eat + e:PRS.3SG' for an IWfiAnalysis."""
    lcm = fw.lcm
    wa = lcm.IWfiAnalysis(wa)
    parts = []
    for b in wa.MorphBundlesOS:
        morph = _text(b.MorphRA.Form.VernacularDefaultWritingSystem) if b.MorphRA else "?"
        sense = b.SenseRA or sense_for_msa(b.MsaRA)  # parser-made bundles have no sense
        gloss = _text(sense.Gloss.AnalysisDefaultWritingSystem) if sense else "?"
        parts.append(f"{morph}:{gloss}")
    cat = wa.CategoryRA
    pos = f" [{_text(cat.Abbreviation.BestAnalysisAlternative)}]" if cat else ""
    return (" + ".join(parts) or "(no morphemes)") + pos


def sense_for_msa(msa):
    """The first sense of the msa's entry that uses that msa, or None."""
    if msa is None:
        return None
    from SIL.LCModel import ILexEntry
    for sense in ILexEntry(msa.Owner).AllSenses:
        if sense.MorphoSyntaxAnalysisRA is not None and sense.MorphoSyntaxAnalysisRA.Hvo == msa.Hvo:
            return sense
    return None


def approval(guesser, wa):
    if guesser.IsHumanApproved(wa):
        return "human-approved"
    if guesser.IsHumanDisapproved(wa):
        return "human-disapproved"
    if guesser.IsParserApproved(wa):
        return "parser-approved"
    if guesser.IsParserDisapproved(wa):
        return "parser-disapproved"
    if guesser.IsComputerApproved(wa):
        return "computer-approved"
    return "no opinion"


# ---------------------------------------------------------------- occurrences

@dataclass
class Occurrence:
    number: int          # 1-based, in corpus order among matches
    text: str
    para: int            # 1-based
    seg: int             # 1-based
    index: int           # 0-based position in the segment's AnalysesRS
    segment: object      # ISegment
    occ: object          # AnalysisOccurrence

    @property
    def analysis(self):
        return self.segment.AnalysesRS[self.index]

    @property
    def wordform(self):
        return fw.lcm.IWfiWordform(self.analysis.Wordform)

    @property
    def is_guessable(self):
        """FLEx shows a guess only where the occurrence has no analysis yet."""
        return self.analysis.ClassName == "WfiWordform"

    def neighbour(self, previous):
        return neighbour(self.segment, self.index, previous)

    def location(self):
        return f"{self.text} ¶{self.para} s{self.seg} w{self.index + 1}"

    def context(self):
        words = [form_of(a) for a in self.segment.AnalysesRS]
        words[self.index] = f"[{words[self.index]}]"
        return " ".join(words)


def neighbour(segment, i, previous):
    """The neighbouring wordform/punctuation object, or EMPTY at a segment edge."""
    j = i - 1 if previous else i + 1
    if j < 0 or j >= segment.AnalysesRS.Count:
        return EMPTY
    adj = segment.AnalysesRS[j]
    return adj.Wordform if adj.ClassName in ("WfiAnalysis", "WfiGloss") else adj


def _key(obj):
    return obj if obj == EMPTY else str(obj.Guid)


def iter_texts(project, text_name=None):
    for text in project.Texts.GetAll():
        title = _text(text.Name.BestVernacularAnalysisAlternative)
        if text_name and title.lower() != text_name.lower():
            continue
        if text.ContentsOA is not None:
            yield title, text


def find_occurrences(project, word=None, text_name=None):
    """All word occurrences (optionally only of `word`, case-insensitive)."""
    lcm = fw.lcm
    result = []
    for title, text in iter_texts(project, text_name):
        for p, para in enumerate(text.ContentsOA.ParagraphsOS, 1):
            para = lcm.IStTxtPara(para)
            for s, seg in enumerate(para.SegmentsOS, 1):
                for i in range(seg.AnalysesRS.Count):
                    a = seg.AnalysesRS[i]
                    if a.ClassName == "PunctuationForm":
                        continue
                    if word and form_of(a).lower() != word.lower():
                        continue
                    result.append(Occurrence(len(result) + 1, title, p, s, i, seg,
                                             lcm.AnalysisOccurrence(seg, i)))
    return result


def find_wordform(project, word):
    wf = project.Wordforms.Find(word)
    if wf is None:
        raise SystemExit(f"No wordform '{word}' in the project")
    return fw.lcm.IWfiWordform(wf)


def sorted_analyses(wordform):
    """A wordform's analyses in a stable, user-facing order (numbered from 1)."""
    lcm = fw.lcm
    return sorted((lcm.IWfiAnalysis(a) for a in wordform.AnalysesOC),
                  key=lambda a: (describe(a), str(a.Guid)))


def pick_analysis(wordform, selector):
    """Resolve '2', a GUID prefix, or a substring of the description."""
    analyses = sorted_analyses(wordform)
    if str(selector).isdigit():
        n = int(selector)
        if 1 <= n <= len(analyses):
            return analyses[n - 1]
        raise SystemExit(f"Analysis number must be 1..{len(analyses)}")
    sel = str(selector).lower()
    hits = [a for a in analyses if str(a.Guid).lower().startswith(sel)] or \
           [a for a in analyses if sel in describe(a).lower()]
    if len(hits) != 1:
        raise SystemExit(f"'{selector}' matches {len(hits)} analyses; use the number "
                         f"from the 'analyses' command")
    return hits[0]


# ---------------------------------------------------------------- ranking

@dataclass
class Explained:
    analysis: object
    prev_score: float = 0.0
    next_score: float = 0.0
    priority: int = 0
    count: int = 0
    in_text_prev: dict = field(default_factory=dict)

    @property
    def score(self):
        return self.prev_score + self.next_score


class Ranker:
    def __init__(self, project, prioritize_parser=False):
        self.project = project
        self.cache = project.project
        self.guesser = fw.lcm.AnalysisGuessServices(self.cache, prioritize_parser)

    def refresh(self):
        """The guesser caches its counts; call after changing texts."""
        self.guesser.ClearGuessData()

    def ranked(self, occurrence, ignore_self=False):
        """Analyses of the occurrence's wordform, best first (from the C# service)."""
        g = self.guesser
        g.IgnoreOccurrence = occurrence.occ if ignore_self else None
        try:
            self.refresh()
            return list(g.GetSortedAnalysisGuesses(occurrence.wordform, occurrence.occ, True))
        finally:
            g.IgnoreOccurrence = None
            self.refresh()

    def best_guess(self, occurrence):
        """What FLEx would display for an unanalysed occurrence (may be a gloss)."""
        self.refresh()
        return self.guesser.GetBestGuess(occurrence.occ, True, True)

    def basis(self, occurrence):
        """Which rule put the top analysis ahead of the runner-up, in words."""
        ranked = self.ranked(occurrence)
        if len(ranked) < 2:
            return "only parse"
        why = self.explain(occurrence)
        a, b = why.get(str(ranked[0].Guid)), why.get(str(ranked[1].Guid))
        if a is None or b is None:
            return "case variant"
        if a.score != b.score:
            return f"context {a.score:.2f} vs {b.score:.2f}"
        if a.priority != b.priority:
            return f"priority {a.priority} vs {b.priority}"
        if a.count != b.count:
            return f"count {a.count} vs {b.count}"
        return "TIE (decided by GUID)"

    def explain(self, occurrence, ignore_self=False):
        """Re-compute the guesser's per-analysis numbers for display."""
        lcm = fw.lcm
        wf = occurrence.wordform
        prev, nxt, backoff = {}, {}, {}

        def add(table, ctx, a, prio):
            # Mirrors AnalysisGuessServices.AddAnalysisCount: a higher priority
            # count replaces a lower one; equal priority increments.
            cell = table.setdefault(ctx, {}).setdefault(a, [0, 0])
            if cell[0] > prio:
                return
            if cell[0] < prio:
                cell[:] = [prio, 0]
            cell[1] += 1

        seen = set()
        for seg in wf.OccurrencesInTexts:
            if seg.Hvo in seen or not seg.IsValidObject:
                continue
            seen.add(seg.Hvo)
            for i in range(seg.AnalysesRS.Count):
                a = seg.AnalysesRS[i]
                if a.Wordform is None or a.Wordform.Hvo != wf.Hvo:
                    continue
                if ignore_self and seg.Hvo == occurrence.segment.Hvo and i == occurrence.index:
                    continue
                if a.ClassName == "WfiGloss":
                    a = a.Analysis
                if a.ClassName != "WfiAnalysis":
                    continue
                k = str(a.Guid)
                add(prev, _key(neighbour(seg, i, True)), k, 7)
                add(nxt, _key(neighbour(seg, i, False)), k, 7)
                add(backoff, None, k, 7)
        g = self.guesser
        if not ignore_self:
            for wa in wf.AnalysesOC:
                wa = lcm.IWfiAnalysis(wa)
                if g.IsHumanDisapproved(wa) and not g.PrioritizeParser:
                    continue
                prio = (6 if g.IsHumanApproved(wa) else 1 if g.IsHumanDisapproved(wa) else
                        5 if g.IsParserApproved(wa) else 2 if g.IsParserDisapproved(wa) else
                        4 if g.IsComputerApproved(wa) else 3)
                add(backoff, None, str(wa.Guid), prio)

        def score(table, ctx, k):
            row = table.get(ctx, {})
            total = sum(c for _, c in row.values())
            return row[k][1] / total if total and k in row else 0.0

        pctx = _key(occurrence.neighbour(True))
        nctx = _key(occurrence.neighbour(False))
        out = {}
        for wa in wf.AnalysesOC:
            k = str(wa.Guid)
            prio, count = backoff.get(None, {}).get(k, [0, 0])
            out[k] = Explained(lcm.IWfiAnalysis(wa), score(prev, pctx, k),
                               score(nxt, nctx, k), prio, count)
        return out
