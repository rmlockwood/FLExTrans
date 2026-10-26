"""
Running FieldWorks' parser (HermitCrab, via flexicon's project.Parser) on
the words of a text, and optionally filing the results into the project the
way FLEx's "Parse Words in Text" does (ParseFiler).

Filing cannot be undone: ParseFiler opens its own non-undoable unit of work.
It creates parser-approved analyses for new parses, re-approves existing
matches, marks parses the parser no longer produces as parser-disapproved,
and DELETES analyses that nobody approved and no text uses.
"""

from . import fw
from .guesser import find_occurrences, form_of, sense_for_msa, _text


def describe_parse(parse):
    """'le:DEF.M.SG' style description of a parser ParseAnalysis."""
    from SIL.LCModel import IMoForm
    parts = []
    for m in parse.Morphs:
        form = _text(IMoForm(m.Form).Form.VernacularDefaultWritingSystem) if m.Form else "?"
        sense = sense_for_msa(m.Msa)
        gloss = _text(sense.Gloss.AnalysisDefaultWritingSystem) if sense else "?"
        parts.append(f"{form}:{gloss}")
    return " + ".join(parts)


def parse_text(project, text_name=None):
    """
    Parse each distinct word in the text(s). Returns a list of
    (word, [(description, matching IWfiAnalysis or None)], error, ParseResult)
    in text order.
    """
    lcm = fw.lcm
    words = []
    for occ in find_occurrences(project, text_name=text_name):
        w = form_of(occ.analysis)
        if w.lower() not in (x.lower() for x in words):
            words.append(w)
    results = []
    for w in words:
        r = project.Parser.ParseWord(w)
        if not r.IsValid or r.ErrorMessage:
            results.append((w, [], r.ErrorMessage or "invalid parse result", r))
            continue
        wf = project.Wordforms.Find(w)
        existing = [lcm.IWfiAnalysis(a) for a in wf.AnalysesOC] if wf else []
        parses = []
        for pa in r.Analyses:
            match = next((wa for wa in existing if pa.MatchesIWfiAnalysis(wa)), None)
            parses.append((describe_parse(pa), match))
        results.append((w, parses, None, r))
    return results


class Filer:
    """Files ParseResults with FieldWorks' own ParseFiler, one word at a time.

    The filer only enqueues its work on an IdleQueue (normally run by the FLEx
    UI loop), so each word gets a fresh paused queue that is pumped by hand.
    Must be used with no unit of work open; the filer opens its own.
    """

    def __init__(self, project):
        import clr
        clr.AddReference("ParserCore")
        clr.AddReference("FwUtils")
        from SIL.FieldWorks.Common.FwUtils import IdleQueue
        from SIL.FieldWorks.WordWorks.Parser import ParseFiler, ParserPriority, TaskReport
        from SIL.LCModel import CmAgentTags, ICmAgentRepository
        from System import Action
        self._IdleQueue, self._ParseFiler, self._Low = IdleQueue, ParseFiler, ParserPriority.Low
        self._handler = Action[TaskReport](lambda _report: None)
        self.cache = project.project
        repo = project.ObjectRepository(ICmAgentRepository)
        self.agent = repo.GetObject(CmAgentTags.kguidAgentHermitCrabParser)
        self.project = project

    def file(self, word, parse_result):
        """Returns True if the filer ran all of its tasks for the word."""
        wf = self.project.Wordforms.Find(word)
        if wf is None:
            return False  # every word in a text already has a wordform
        queue = self._IdleQueue()
        queue.IsPaused = True
        filer = self._ParseFiler(self.cache, None, self._handler, queue, self.agent)
        filer.ProcessParse(fw.lcm.IWfiWordform(wf), self._Low, parse_result, False)
        tasks = list(queue)
        ok = bool(tasks)
        for task in tasks:
            queue.Remove(task)
            ok = bool(task.Delegate(task.Parameter)) and ok
        return ok
