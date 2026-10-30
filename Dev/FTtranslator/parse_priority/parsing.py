#
#   parse_priority/parsing
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.2 - 10/29/26 - Ron Lockwood
#    Prepare each word as FLEx does before parsing it: spaces become '.', so phrases parse, and the form is normalized to NFD.
#
#   Version 3.17.1 - 10/28/26 - Ron Lockwood
#    Parse a capitalized word in lowercase when it gets no parses as written.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Runs the HermitCrab parser on the words of a text and files the results the way FLEx does.
#
#   OVERVIEW (AI generated, then edited)
#
#   Runs FieldWorks' parser (HermitCrab, through flexicon's project.Parser) on each distinct word of a text, and optionally files the results into the project the way FLEx's "Parse Words in
#   Text" does, using FieldWorks' own ParseFiler.
#
#   CAPITALIZED WORDS
#
#   HermitCrab only accepts the characters the grammar defines as phonemes, and many grammars define only lowercase ones (Kurmanji does), so a sentence-initial or title-case word fails with
#   "undefined phoneme". When a word with capitals gets an error or no parses, parseText() parses its lowercase form, and uses that result only if it found parses. The guard matters: a proper
#   noun whose lexeme is capitalized gets no parses in lowercase, and filing that empty result would mark every existing analysis of the word as parser-disapproved; keeping the original error
#   makes the caller skip the word instead. The result is filed against the word as written, since that is the wordform the text uses. FLEx's ParserWorker.ParseAndUpdateWordform also parses
#   the lowercase form of a capitalized word.
#
#   PHRASES
#
#   When a text is added, FLEx joins words that match an existing multi-word wordform (a phrase such as 'hata sibuna li') into one occurrence. HermitCrab stops at a space with an "undefined
#   phoneme" error, but it takes '.' as the boundary between the words of a phrase, the way FieldWorks' HermitCrab loader writes multi-word lexemes. So parserForm() does what
#   ParserWorker.ParseAndUpdateWordform does before calling the parser: replace each space with '.' and normalize to NFD. The wordform keeps its spaces; only the parser sees the dots.
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
#   describeParse() describes a parser result for display, parserForm() prepares a word for the parser, _hasParses() tells whether a result found anything, parseText() parses a text's words,
#   and Filer files the results. FTtranslator's Parse Words step uses parseText() and Filer, and so does the parse command.
#

import unicodedata

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

def parserForm(word):
    '''Return word as the parser needs it: each space replaced with '.', normalized to NFD. See PHRASES above.'''

    return unicodedata.normalize("NFD", word.replace(" ", "."))

def _hasParses(parseResult):
    '''True if the parser ran without an error and found at least one parse.'''

    return bool(parseResult.IsValid and not parseResult.ErrorMessage and parseResult.Analyses.Count > 0)

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

        parseResult = project.Parser.ParseWord(parserForm(word))

        # A capitalized word may fail only because of its capitals. See CAPITALIZED WORDS above.
        if word.lower() != word and not _hasParses(parseResult):

            lowercaseResult = project.Parser.ParseWord(parserForm(word.lower()))

            if _hasParses(lowercaseResult):

                parseResult = lowercaseResult

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
