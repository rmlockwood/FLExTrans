#
#   parse_priority/parsing
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Runs the HermitCrab parser on the words of a text and files the results the way FLEx does.
#
#   OVERVIEW (AI generated, then edited)
#
#   Runs FieldWorks' parser (HermitCrab, through flexicon's project.Parser) on each distinct word of a text, and optionally files the results into the project the way FLEx's "Parse Words in
#   Text" does, using FieldWorks' own ParseFiler.
#
#   FILING CANNOT BE UNDONE
#
#   ParseFiler opens its own non-undoable unit of work. It creates parser-approved analyses for new parses, re-approves existing matches, marks parses the parser no longer produces as
#   parser-disapproved, and DELETES analyses that nobody approved and no text uses. So a Filer must be used with no unit of work open, and a caller that rolls back with Undo can't roll this back.
#
#   PUMPING THE FILER BY HAND
#
#   The filer doesn't do its work when asked: it queues tasks on an IdleQueue, which the FLEx UI loop normally runs when idle. There is no UI loop here, so Filer.file() gives each word a fresh,
#   paused queue, takes the tasks off it and runs them itself. A word whose filer queued nothing, or one of whose tasks returned False, counts as not filed.
#
#   CODE STRUCTURE
#
#   describeParse() describes a parser result for display, parseText() parses a text's words, and Filer files the results. FTtranslator's Parse Words step uses parseText() and Filer, and so
#   does the parse command.
#

from . import fw
from .guesser import findOccurrences, formOf, senseForMsa, _text

def describeParse(parse):
    '''Describe a parser ParseAnalysis as 'le:DEF.M.SG + ...': each morph's form with its gloss.'''

    from SIL.LCModel import IMoForm  # type: ignore  # only importable once FieldWorks is initialized

    parts = []

    for morph in parse.Morphs:

        form = _text(IMoForm(morph.Form).Form.VernacularDefaultWritingSystem) if morph.Form else "?"
        sense = senseForMsa(morph.Msa)
        gloss = _text(sense.Gloss.AnalysisDefaultWritingSystem) if sense else "?"
        parts.append(f"{form}:{gloss}")

    return " + ".join(parts)

def parseText(project, textName=None):
    '''Parse each distinct word in the text titled textName (or in all texts). Returns a list of (word, [(description, matching IWfiAnalysis or None)], error, ParseResult), in text
       order. error is None unless the parser failed on the word, and then the parse list is empty.'''

    lcm = fw.lcm

    # Each word once, compared case-insensitively, in the order it first appears
    words = []

    for occurrence in findOccurrences(project, textName=textName):

        word = formOf(occurrence.analysis)

        if word.lower() not in (existingWord.lower() for existingWord in words):

            words.append(word)

    results = []

    for word in words:

        parseResult = project.Parser.ParseWord(word)

        if not parseResult.IsValid or parseResult.ErrorMessage:

            results.append((word, [], parseResult.ErrorMessage or "invalid parse result", parseResult))
            continue

        # Match each parse against the analyses the word already has, so the caller can tell which ones are new
        wordform = project.Wordforms.Find(word)
        existingAnalyses = [lcm.IWfiAnalysis(analysis) for analysis in wordform.AnalysesOC] if wordform else []
        parses = []

        for parse in parseResult.Analyses:

            match = next((wordAnalysis for wordAnalysis in existingAnalyses if parse.MatchesIWfiAnalysis(wordAnalysis)), None)
            parses.append((describeParse(parse), match))

        results.append((word, parses, None, parseResult))

    return results

class Filer:
    '''Files ParseResults with FieldWorks' own ParseFiler, one word at a time. Must be used with no unit of work open; the filer opens its own. See PUMPING THE FILER BY HAND above.'''

    def __init__(self, project):

        # The parser and FwUtils assemblies aren't loaded by flexicon
        import clr
        clr.AddReference("ParserCore")  # type: ignore  # pythonnet adds AddReference to clr at run time, so the checker can't see it
        clr.AddReference("FwUtils")  # type: ignore

        from SIL.FieldWorks.Common.FwUtils import IdleQueue  # type: ignore  # .NET namespaces have no stubs
        from SIL.FieldWorks.WordWorks.Parser import ParseFiler, ParserPriority, TaskReport  # type: ignore
        from SIL.LCModel import CmAgentTags, ICmAgentRepository  # type: ignore
        from System import Action  # type: ignore

        self._IdleQueue, self._ParseFiler, self._lowPriority = IdleQueue, ParseFiler, ParserPriority.Low

        # The filer reports its progress through this; nothing here needs it
        self._handler = Action[TaskReport](lambda _report: None)
        self.cache = project.project
        agentRepository = project.ObjectRepository(ICmAgentRepository)
        self.agent = agentRepository.GetObject(CmAgentTags.kguidAgentHermitCrabParser)
        self.project = project

    def file(self, word, parseResult):
        '''File the parse result for word. Returns True if the filer ran all of its tasks for the word.'''

        wordform = self.project.Wordforms.Find(word)

        # Every word in a text already has a wordform
        if wordform is None:

            return False

        queue = self._IdleQueue()
        queue.IsPaused = True
        filer = self._ParseFiler(self.cache, None, self._handler, queue, self.agent)
        filer.ProcessParse(fw.lcm.IWfiWordform(wordform), self._lowPriority, parseResult, False)

        # Run the queued tasks ourselves, since nothing else will
        tasks = list(queue)
        ok = bool(tasks)

        for task in tasks:

            queue.Remove(task)
            ok = bool(task.Delegate(task.Parameter)) and ok

        return ok
