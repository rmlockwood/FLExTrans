#
#   parse_priority/guesser
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Finds word occurrences in texts and asks FieldWorks' analysis guesser to rank their analyses.
#
#   OVERVIEW (AI generated, then edited)
#
#   The guesser is SIL.LCModel.DomainServices.AnalysisGuessServices in liblcm - the component that picks which analysis FLEx proposes for an unanalysed word in a text. It is not a trained model.
#   It ranks a wordform's analyses from counts taken from the texts every time it is asked, and nothing is stored:
#    1. Context score = P(analysis | previous word) + P(analysis | next word), where the probabilities are counts of analyses already set on other occurrences of the word in texts, next to the
#       same neighbouring word. A segment edge counts as an "empty" neighbour.
#    2. Ties fall back to a priority: used in a text (7) > human approved (6) > parser approved (5) > computer approved (4) > no opinion (3) > parser disapproved (2) > human disapproved (1).
#    3. Then the raw count at that priority, then a non-lowercased form, then the GUID - so a full tie is settled arbitrarily.
#
#   THE TWO RANKINGS
#
#   The ranking this package reports always comes from the C# service itself (Ranker.ranked() and bestGuess()). The numbers shown next to it come from explain(), a Python re-computation of steps
#   1-3 for display only. It doesn't model the guesser's merging of capitalised and lowercase wordforms, so for a sentence-initial capitalised word its numbers can disagree with the real order;
#   an analysis explain() has no numbers for is a case variant. The guesser also caches its counts, so Ranker clears them before every question (refresh()).
#
#   OCCURRENCES
#
#   An Occurrence is one word in a text: where it is (text, paragraph, segment, index) and the segment it is in. Its analysis is read from the segment each time rather than stored, so it is
#   always current after an edit. The neighbours that matter to the guesser are wordforms (an analysed neighbour is reduced to its wordform), punctuation, or the EMPTY marker at a segment edge.
#
#   CODE STRUCTURE
#
#   Formatting helpers first: _text(), formOf(), describe(), senseForMsa() and approval(). Then occurrences: Occurrence, neighbour(), _key(), iterTexts(), findOccurrences(), findWordform(),
#   sortedAnalyses() and pickAnalysis(). Last, ranking: Explained holds explain()'s numbers for one analysis, and Ranker wraps AnalysisGuessServices (ranked(), bestGuess(), basis(), explain()).
#   FTtranslator's ingest steps use findOccurrences(), Ranker and the formatting helpers; the parse_priority commands use all of it.
#

from dataclasses import dataclass, field
from typing import Any

from . import fw

# The neighbour of the first or last word in a segment
EMPTY = "<edge>"

def _text(tsString):
    '''The text of an ITsString, or "" if it has none.'''

    try:
        return tsString.Text or ""

    except Exception:

        return ""

def formOf(analysis):
    '''The surface form of any IAnalysis: a wordform, analysis, gloss or punctuation.'''

    if analysis is None:

        return "?"

    if analysis.ClassName == "PunctuationForm":

        return _text(fw.lcm.IPunctuationForm(analysis).Form)

    wordform = analysis.Wordform

    return _text(wordform.Form.VernacularDefaultWritingSystem) if wordform else "?"

def describe(wordAnalysis):
    '''Describe an IWfiAnalysis as 'mang:eat + e:PRS.3SG [v]': each morph with its gloss, then the category.'''

    wordAnalysis = fw.lcm.IWfiAnalysis(wordAnalysis)
    parts = []

    for bundle in wordAnalysis.MorphBundlesOS:

        morph = _text(bundle.MorphRA.Form.VernacularDefaultWritingSystem) if bundle.MorphRA else "?"

        # Parser-made bundles have no sense, only an msa
        sense = bundle.SenseRA or senseForMsa(bundle.MsaRA)
        gloss = _text(sense.Gloss.AnalysisDefaultWritingSystem) if sense else "?"
        parts.append(f"{morph}:{gloss}")

    category = wordAnalysis.CategoryRA
    partOfSpeech = f" [{_text(category.Abbreviation.BestAnalysisAlternative)}]" if category else ""

    return (" + ".join(parts) or "(no morphemes)") + partOfSpeech

def senseForMsa(msa):
    '''The first sense of the msa's entry that uses that msa, or None.'''

    if msa is None:

        return None

    from SIL.LCModel import ILexEntry  # type: ignore  # only importable once FieldWorks is initialized

    for sense in ILexEntry(msa.Owner).AllSenses:

        if sense.MorphoSyntaxAnalysisRA is not None and sense.MorphoSyntaxAnalysisRA.Hvo == msa.Hvo:

            return sense

    return None

def approval(guesser, wordAnalysis):
    '''The analysis's approval status, in words.'''

    if guesser.IsHumanApproved(wordAnalysis):

        return "human-approved"

    if guesser.IsHumanDisapproved(wordAnalysis):

        return "human-disapproved"

    if guesser.IsParserApproved(wordAnalysis):

        return "parser-approved"

    if guesser.IsParserDisapproved(wordAnalysis):

        return "parser-disapproved"

    if guesser.IsComputerApproved(wordAnalysis):

        return "computer-approved"

    return "no opinion"

@dataclass
class Occurrence:
    '''One word in a text. See OCCURRENCES above.'''

    number: int          # 1-based, in corpus order among the matches
    text: str
    para: int            # 1-based
    seg: int             # 1-based
    index: int           # 0-based position in the segment's AnalysesRS
    segment: Any         # ISegment
    occ: Any             # AnalysisOccurrence

    @property
    def analysis(self):

        return self.segment.AnalysesRS[self.index]

    @property
    def wordform(self):

        return fw.lcm.IWfiWordform(self.analysis.Wordform)

    @property
    def isGuessable(self):
        '''FLEx shows a guess only where the occurrence has no analysis yet.'''

        return self.analysis.ClassName == "WfiWordform"

    def neighbour(self, previous):

        return neighbour(self.segment, self.index, previous)

    def location(self):

        return f"{self.text} ¶{self.para} s{self.seg} w{self.index + 1}"

    def context(self):
        '''The segment's words with this one in brackets.'''

        words = [formOf(analysis) for analysis in self.segment.AnalysesRS]
        words[self.index] = f"[{words[self.index]}]"

        return " ".join(words)

def neighbour(segment, index, previous):
    '''The wordform or punctuation object next to position index (before it if previous), or EMPTY at a segment edge.'''

    neighbourIndex = index - 1 if previous else index + 1

    if neighbourIndex < 0 or neighbourIndex >= segment.AnalysesRS.Count:

        return EMPTY

    adjacent = segment.AnalysesRS[neighbourIndex]

    # The guesser compares wordforms, so an analysed neighbour counts as its wordform
    return adjacent.Wordform if adjacent.ClassName in ("WfiAnalysis", "WfiGloss") else adjacent

def _key(neighbourObject):
    '''A neighbour as a dictionary key: EMPTY itself, or the object's GUID.'''

    return neighbourObject if neighbourObject == EMPTY else str(neighbourObject.Guid)

def iterTexts(project, textName=None):
    '''Yield (title, text) for each text with contents, or only the one titled textName (case-insensitive).'''

    for text in project.Texts.GetAll():

        title = _text(text.Name.BestVernacularAnalysisAlternative)

        if textName and title.lower() != textName.lower():

            continue

        if text.ContentsOA is not None:

            yield title, text

def findOccurrences(project, word=None, textName=None):
    '''Return every word occurrence in the texts (or in the text titled textName), in corpus order. With word, only the occurrences of that word, compared case-insensitively.'''

    lcm = fw.lcm
    occurrences = []

    for title, text in iterTexts(project, textName):

        for paraNumber, para in enumerate(text.ContentsOA.ParagraphsOS, 1):

            para = lcm.IStTxtPara(para)

            for segNumber, segment in enumerate(para.SegmentsOS, 1):

                for index in range(segment.AnalysesRS.Count):

                    analysis = segment.AnalysesRS[index]

                    if analysis.ClassName == "PunctuationForm":

                        continue

                    if word and formOf(analysis).lower() != word.lower():

                        continue

                    occurrences.append(Occurrence(len(occurrences) + 1, title, paraNumber, segNumber, index, segment, lcm.AnalysisOccurrence(segment, index)))

    return occurrences

def findWordform(project, word):
    '''Return the project's wordform for word, or stop with an error if there is none.'''

    wordform = project.Wordforms.Find(word)

    if wordform is None:

        raise SystemExit(f"No wordform '{word}' in the project")

    return fw.lcm.IWfiWordform(wordform)

def sortedAnalyses(wordform):
    '''A wordform's analyses in a stable order for showing to the user (numbered from 1): by description, then GUID.'''

    lcm = fw.lcm

    return sorted((lcm.IWfiAnalysis(analysis) for analysis in wordform.AnalysesOC), key=lambda analysis: (describe(analysis), str(analysis.Guid)))

def pickAnalysis(wordform, selector):
    '''Return the analysis selector names: its number from sortedAnalyses() ('2'), a GUID prefix, or a substring of its description. Stops with an error unless exactly one matches.'''

    analyses = sortedAnalyses(wordform)

    # A number
    if str(selector).isdigit():

        number = int(selector)

        if 1 <= number <= len(analyses):

            return analyses[number - 1]

        raise SystemExit(f"Analysis number must be 1..{len(analyses)}")

    # A GUID prefix, or failing that a piece of the description
    selectorText = str(selector).lower()
    hits = [analysis for analysis in analyses if str(analysis.Guid).lower().startswith(selectorText)] or [analysis for analysis in analyses if selectorText in describe(analysis).lower()]

    if len(hits) != 1:

        raise SystemExit(f"'{selector}' matches {len(hits)} analyses; use the number from the 'analyses' command")

    return hits[0]

@dataclass
class Explained:
    '''explain()'s numbers for one analysis: the context scores for the previous and next words, and the priority and count it ties are broken on.'''

    analysis: object
    prevScore: float = 0.0
    nextScore: float = 0.0
    priority: int = 0
    count: int = 0
    inTextPrev: dict = field(default_factory=dict)

    @property
    def score(self):

        return self.prevScore + self.nextScore

class Ranker:
    '''Asks AnalysisGuessServices about occurrences. prioritizeParser ranks as FLEx's Parsing Development mode does, with parser approval first.'''

    def __init__(self, project, prioritizeParser=False):

        self.project = project
        self.cache = project.project
        self.guesser = fw.lcm.AnalysisGuessServices(self.cache, prioritizeParser)

    def refresh(self):
        '''Clear the guesser's cached counts. Call after changing texts.'''

        self.guesser.ClearGuessData()

    def ranked(self, occurrence, ignoreSelf=False):
        '''The analyses of the occurrence's wordform, best first, as the C# service ranks them. ignoreSelf leaves the occurrence's own analysis out of the counts.'''

        guesser = self.guesser
        guesser.IgnoreOccurrence = occurrence.occ if ignoreSelf else None

        try:
            self.refresh()
            return list(guesser.GetSortedAnalysisGuesses(occurrence.wordform, occurrence.occ, True))
        finally:
            guesser.IgnoreOccurrence = None
            self.refresh()

    def bestGuess(self, occurrence):
        '''What FLEx would display for an unanalysed occurrence. It may be a gloss.'''

        self.refresh()

        return self.guesser.GetBestGuess(occurrence.occ, True, True)

    def basis(self, occurrence):
        '''Which rule put the top analysis ahead of the runner-up, in words.'''

        ranked = self.ranked(occurrence)

        if len(ranked) < 2:

            return "only parse"

        explained = self.explain(occurrence)
        first, second = explained.get(str(ranked[0].Guid)), explained.get(str(ranked[1].Guid))

        if first is None or second is None:

            return "case variant"

        if first.score != second.score:

            return f"context {first.score:.2f} vs {second.score:.2f}"

        if first.priority != second.priority:

            return f"priority {first.priority} vs {second.priority}"

        if first.count != second.count:

            return f"count {first.count} vs {second.count}"

        return "TIE (decided by GUID)"

    def explain(self, occurrence, ignoreSelf=False):
        '''Re-compute the guesser's numbers for each analysis of the occurrence's wordform, for display. Returns a dictionary from analysis GUID to Explained. See THE TWO RANKINGS above.'''

        lcm = fw.lcm
        wordform = occurrence.wordform

        # Counts by previous word, by next word, and with no context (the priority/count fallback). Each maps a context key to {analysis GUID: [priority, count]}.
        prevCounts, nextCounts, backoffCounts = {}, {}, {}

        def addCount(table, context, analysisKey, priority):

            # Mirrors AnalysisGuessServices.AddAnalysisCount: a higher priority count replaces a lower one; an equal priority increments
            cell = table.setdefault(context, {}).setdefault(analysisKey, [0, 0])

            if cell[0] > priority:

                return

            if cell[0] < priority:

                cell[:] = [priority, 0]

            cell[1] += 1

        # In-text uses, priority 7. A segment can be listed more than once, so each is counted once.
        seenSegments = set()

        for segment in wordform.OccurrencesInTexts:

            if segment.Hvo in seenSegments or not segment.IsValidObject:

                continue

            seenSegments.add(segment.Hvo)

            for index in range(segment.AnalysesRS.Count):

                analysis = segment.AnalysesRS[index]

                if analysis.Wordform is None or analysis.Wordform.Hvo != wordform.Hvo:

                    continue

                if ignoreSelf and segment.Hvo == occurrence.segment.Hvo and index == occurrence.index:

                    continue

                if analysis.ClassName == "WfiGloss":

                    analysis = analysis.Analysis

                if analysis.ClassName != "WfiAnalysis":

                    continue

                analysisKey = str(analysis.Guid)
                addCount(prevCounts, _key(neighbour(segment, index, True)), analysisKey, 7)
                addCount(nextCounts, _key(neighbour(segment, index, False)), analysisKey, 7)
                addCount(backoffCounts, None, analysisKey, 7)

        # Approval opinions, priorities 6 down to 1. Human-disapproved analyses are left out, except in Parsing Development mode.
        guesser = self.guesser

        if not ignoreSelf:

            for wordAnalysis in wordform.AnalysesOC:

                wordAnalysis = lcm.IWfiAnalysis(wordAnalysis)

                if guesser.IsHumanDisapproved(wordAnalysis) and not guesser.PrioritizeParser:

                    continue

                if guesser.IsHumanApproved(wordAnalysis):

                    priority = 6

                elif guesser.IsHumanDisapproved(wordAnalysis):

                    priority = 1

                elif guesser.IsParserApproved(wordAnalysis):

                    priority = 5

                elif guesser.IsParserDisapproved(wordAnalysis):

                    priority = 2

                elif guesser.IsComputerApproved(wordAnalysis):

                    priority = 4
                else:
                    priority = 3

                addCount(backoffCounts, None, str(wordAnalysis.Guid), priority)

        def contextScore(table, context, analysisKey):

            # This analysis's share of all the counts in the context
            row = table.get(context, {})
            total = sum(count for _, count in row.values())

            return row[analysisKey][1] / total if total and analysisKey in row else 0.0

        prevContext = _key(occurrence.neighbour(True))
        nextContext = _key(occurrence.neighbour(False))
        explained = {}

        for wordAnalysis in wordform.AnalysesOC:

            analysisKey = str(wordAnalysis.Guid)
            priority, count = backoffCounts.get(None, {}).get(analysisKey, [0, 0])
            explained[analysisKey] = Explained(lcm.IWfiAnalysis(wordAnalysis), contextScore(prevCounts, prevContext, analysisKey), contextScore(nextCounts, nextContext, analysisKey), priority, count)

        return explained
