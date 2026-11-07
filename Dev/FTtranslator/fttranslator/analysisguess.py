#
#   fttranslator/analysisguess
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17.1 - 11/6/26 - Ron Lockwood
#    File a word's parses in a fixed order, so a text gets the same analyses every time; HermitCrab's order changes from run to run.
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. FTtranslator's Parse Words and Approve Guesses steps without FieldWorks, and the chain from source text to Extract Source Text's output.
#
#   OVERVIEW (AI generated, then edited)
#
#   On the desktop, FTtranslator gets a text's analyses in three steps: Import Text (FLEx splits the text into words), Parse Words (HermitCrab parses each word and FieldWorks' ParseFiler files
#   the results as the word's analyses) and Approve Guesses (FLEx's analysis guesser, liblcm's AnalysisGuessServices, picks one analysis per word). This file does the last two from the bundle
#   (guesser.json, see guessexport.py) and hcparse, and translateToStream() puts the whole chain together: tokenizer.py, then these, then bundleextract.py, giving the Apertium stream Extract
#   Source Text would write.
#
#   FILING
#
#   Guesser.file() follows ParseFiler: every analysis loses its parser opinion; each parse approves the analyses it matches (same allomorphs, the same msas after the parser's merging of
#   equivalent msas, the same inflection types), or becomes a new parser-approved analysis; then analyses a text uses get the user's approval, and any analysis the parser didn't approve is
#   deleted if the user has no opinion of it, and otherwise disapproved by the parser (but not after a parse error). parseAndFile() chooses the words as FTtranslator's Parse Words does: each
#   word once, ignoring case, as first spelled; a capitalized word that gets no parses is parsed in lowercase; a word whose parse fails is left alone.
#
#   GUESSING
#
#   Guesser.bestGuess() follows AnalysisGuessServices.GetBestGuess(): the candidates are the analyses of the word's wordform, of the wordform with the word's own spelling, and, for the first
#   word of a segment, of its lowercase form. Each analysis a text uses counts with priority 7, also under its neighbours (the context); every other analysis counts once with its approval's
#   priority (human 6, parser 5, computer 4, none 3, parser-disapproved 2; human-disapproved ones are left out). The best is the one with the highest context score (the share of its counts next
#   to this word's neighbours, before plus after), then priority, then count, then not from the lowercase form, then the lowest GUID. A wordform with no analyses first gets a computer-approved
#   one from a matching single-morpheme entry, if there is one. As in FTtranslator, all guesses are taken before any is applied, and an approved analysis's morphs without a sense get the sense
#   of their msa (fillSenses()).
#
#   TRAPS
#
#    - A GUID tie can't be broken as on the desktop for a new analysis, which FieldWorks gives a random GUID. New analyses here get GUIDs that sort after every real one, in parse order.
#      HermitCrab gives a word's parses in a different order from run to run, so file() takes them in a fixed order (parseSortKey()); otherwise two new analyses tied on everything else
#      would swap GUIDs between runs and the same text could be translated two ways (it happened with Mato-Uma's "Hainga").
#    - Glosses aren't guessed: Extract Source Text reads a gloss's analysis, so the analysis is all it needs.
#    - The guesser's capitalization tests (title case, all upper case) use Python's str methods where FLEx uses ICU's CaseFunctions.
#    - Sentences come from tokenizer.py's rule, not FLEx's, and a segment edge is a neighbour, so a guess near a sentence break can differ from the desktop's where the two rules differ.
#
#   CODE STRUCTURE
#
#   HCParseProcess runs hcparse; parseSortKey() orders a word's parses for filing and parserForm() prepares a word for the parser. Guesser holds guesser.json: file() and its helpers come first, then the counting (_analysisCounts(), _addCount(), _contextCounts()), the candidates
#   (_wordformIfNeeded(), _generateEntryGuess()), and bestGuess() with _compare(). parseAndFile(), applyGuesses() and translateToStream() are the steps.
#

import copy
import json
import subprocess
import unicodedata
from functools import cmp_to_key
from pathlib import Path

from . import bundleextract
from .tokenizer import Tokenizer

GUESSER_FILE = "guesser.json"
EMPTY_CONTEXT = "<edge>"
NULL_CONTEXT = None

class HCParseProcess:
    '''A running hcparse, fed one word at a time. command is how to start it without its two file arguments, e.g. ["dotnet", ".../HCParse.dll"].'''

    def __init__(self, command, bundleDir):

        bundleDir = Path(bundleDir)
        self.process = subprocess.Popen(list(command) + [str(bundleDir / "parser.xml"), str(bundleDir / "parser.json")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8")

    def parse(self, word):

        self.process.stdin.write(word + "\n")  # type: ignore  # stdin and stdout are pipes, set above
        self.process.stdin.flush()  # type: ignore

        return json.loads(self.process.stdout.readline())  # type: ignore

    def close(self):

        self.process.stdin.close()  # type: ignore
        self.process.wait()

def parseSortKey(parse):
    '''The order Guesser.file() files a word's parses in: by each morph's form, entry, msa, inflection type and guessed text, missing ones as "". FTOffline's Guesser.cs uses the same order.'''

    return [(morph["form"] or "", morph["entry"] or "", morph["msa"] or "", morph["inflType"] or "", morph["guessed"] or "") for morph in parse]

def parserForm(word):
    '''parse_priority's parserForm(): what the parser is given for a word.'''

    return unicodedata.normalize("NFD", word.replace(" ", "."))

class Guesser:
    '''The parse filer and the analysis guesser over guesser.json. See FILING and GUESSING above.'''

    def __init__(self, data, lexicon):

        self.lexicon = lexicon
        self.wordforms = copy.deepcopy(data["wordforms"])
        self.repMsas = data["repMsas"]
        self.monomorphemic = data["monomorphemic"]
        self.newCount = 0

        # Each analysis's wordform, by GUID
        self.owner = {analysis["guid"]: form for form, wordform in self.wordforms.items() for analysis in wordform["analyses"]}

    @classmethod
    def load(cls, bundleDir, lexicon):

        return cls(json.loads((Path(bundleDir) / GUESSER_FILE).read_text(encoding="utf-8")), lexicon)

    def _wordform(self, form):

        return self.wordforms.setdefault(form, {"guid": None, "analyses": [], "contexts": []})

    def _newAnalysis(self, form, bundles, opinions):
        '''Add an analysis the desktop would create. Its GUID sorts after every real one; see TRAPS above.'''

        self.newCount += 1
        analysis = {"guid": f"ffffffff-ffff-ffff-ffff-{self.newCount:012x}", "human": None, "parser": None, "computer": None, "user": None, "used": False, "bundles": bundles}
        analysis.update(opinions)
        self._wordform(form)["analyses"].append(analysis)
        self.owner[analysis["guid"]] = form

        return analysis

    def file(self, form, parseResult):
        '''ParseFiler: file a parse result (hcparse's format) against the wordform. See FILING above.'''

        wordform = self._wordform(form)

        for analysis in wordform["analyses"]:

            analysis["parser"] = None

        if parseResult["error"]:

            self._setUnsuccessfulParseEvals(wordform, None)
            return

        # In a fixed order, since HermitCrab's changes from run to run and decides the new analyses' GUIDs (see TRAPS above)
        for parse in sorted(parseResult["analyses"], key=parseSortKey):

            matches = [analysis for analysis in wordform["analyses"] if self._matches(parse, analysis)]

            if not matches:

                bundles = [{"form": morph["form"], "entry": morph["entry"], "msa": morph["msa"], "sense": None, "inflType": morph["inflType"], "text": morph["guessed"]} for morph in parse]
                matches = [self._newAnalysis(form, bundles, {})]

            for analysis in matches:

                analysis["parser"] = "approves"

        self._setUnsuccessfulParseEvals(wordform, "disapproves")

    def _matches(self, parse, analysis):
        '''ParseAnalysis.MatchesIWfiAnalysis().'''

        bundles = analysis["bundles"]

        if len(bundles) != len(parse):

            return False

        for morphBundle, morph in zip(bundles, parse):

            if morphBundle["form"] != morph["form"] or self.repMsas.get(morphBundle["msa"], morphBundle["msa"]) != morph["msa"] or morphBundle["inflType"] != morph["inflType"]:

                return False

            if morph["guessed"] is not None and morphBundle["text"] != morph["guessed"]:

                return False

        return True

    def _setUnsuccessfulParseEvals(self, wordform, opinion):

        for analysis in list(wordform["analyses"]):

            # A used analysis gets the user's (human) approval
            if analysis["used"]:

                analysis["user"] = "approves"
                analysis["human"] = "approves"

            if analysis["parser"] is None:

                if analysis["user"] is None:

                    wordform["analyses"].remove(analysis)

                elif opinion is not None:

                    analysis["parser"] = opinion

    @staticmethod
    def _addCount(counts, context, guid, priority, lowercased):
        '''AnalysisGuessServices.AddAnalysisCount(): a count under its context, and under the null (no context) entry too.'''

        if context is not NULL_CONTEXT:

            Guesser._addCount(counts, NULL_CONTEXT, guid, priority, lowercased)

        entry = counts.setdefault(context, {}).setdefault(guid, {"priority": 0, "count": 0, "lowercased": False})

        if entry["priority"] > priority:

            return

        if entry["priority"] < priority:

            entry.update(priority=priority, lowercased=lowercased, count=0)

        entry["count"] += 1

    def _analysisCounts(self, form, lowercased, previous, counts):
        '''GetAnalysisCounts(): the counts for one wordform, added to counts.'''

        wordform = self.wordforms.get(form)

        if wordform is None:

            return counts

        for guid, previousKey, nextKey in wordform["contexts"]:

            self._addCount(counts, previousKey if previous else nextKey, guid, 7, lowercased)

        for analysis in wordform["analyses"]:

            # Human-disapproved analyses are left out
            if analysis["human"] == "disapproves":

                continue

            priority = 6 if analysis["human"] == "approves" else 5 if analysis["parser"] == "approves" else 2 if analysis["parser"] == "disapproves" else 4 if analysis["computer"] == "approves" else 3
            self._addCount(counts, NULL_CONTEXT, analysis["guid"], priority, lowercased)

        return counts

    def _freshCounts(self, form, lowercased=False):

        previous = self._analysisCounts(form, lowercased, True, {})
        following = self._analysisCounts(form, lowercased, False, {})

        return {"previous": previous, "next": following, "wordform": previous.get(NULL_CONTEXT, {})}

    def _contextCounts(self, form, originalCase, lowercase):
        '''GetContextCounts(): the counts for the word's wordform, with its original-case and lowercase wordforms' counts added.'''

        if lowercase == form:

            if originalCase is not None:

                form, originalCase = originalCase, None
            else:
                lowercase = None

        if originalCase == form:

            originalCase = None

        counts = self._freshCounts(form)
        hasOriginal = originalCase is not None and self._freshCounts(originalCase)["wordform"]
        hasLowercase = lowercase is not None and self._freshCounts(lowercase)["wordform"]

        if hasOriginal or hasLowercase:

            for variant, lowercased in ((originalCase, False), (lowercase, True)):

                if variant is not None and self._freshCounts(variant)["wordform"]:

                    self._analysisCounts(variant, lowercased, True, counts["previous"])
                    self._analysisCounts(variant, lowercased, False, counts["next"])

            counts["wordform"] = counts["previous"].get(NULL_CONTEXT, {})

        return counts

    def _wordformIfNeeded(self, form):
        '''GetWordformIfNeeded(): the wordform with this form if there is one, or a new one if a single-morpheme entry matches it; else None.'''

        if form in self.wordforms:

            return form

        if self._monomorphemicMatch(form) is not None:

            self._wordform(form)
            return form

        return None

    def _monomorphemicMatch(self, form):

        normalized = unicodedata.normalize("NFD", form)

        return next((candidate for candidate in self.monomorphemic if unicodedata.normalize("NFD", candidate["form"]) == normalized), None)

    def _generateEntryGuess(self, form):
        '''GenerateEntryGuesses(): a wordform with no analyses gets a computer-approved one from a matching single-morpheme entry.'''

        if form is None or self._wordform(form)["analyses"]:

            return

        match = self._monomorphemicMatch(form)

        if match is not None:

            self._newAnalysis(form, [{"form": match["morph"], "entry": match["entry"], "msa": match["msa"], "sense": match["sense"], "inflType": None, "text": None}], {"computer": "approves"})

    def bestGuess(self, form, baseline, indexInSegment, previousKey, nextKey):
        '''GetBestGuess() for a word of the new text: its wordform, its baseline text, its index in its segment and its neighbours' context keys. Returns an analysis record or None.'''

        originalCase = self._wordformIfNeeded(baseline)
        lowercase = None

        # The lowercase form is only tried for the first word of a segment: initial capital first, then all capitals
        if indexInSegment == 0 and baseline:

            if baseline[0].isupper():

                lowercase = self._wordformIfNeeded(baseline[0].lower() + baseline[1:])

            if lowercase is None and all(ch.isupper() for ch in baseline):

                lowercase = self._wordformIfNeeded(baseline.lower())

        for variant in (originalCase, lowercase, form):

            self._generateEntryGuess(variant)

        counts = self._contextCounts(form, originalCase, lowercase)
        best = None

        for guid in counts["wordform"]:

            if best is None or self._compare(guid, best, counts, previousKey, nextKey) < 0:

                best = guid

        if best is None:

            return None

        return next(analysis for analysis in self.wordforms[self.owner[best]]["analyses"] if analysis["guid"] == best)

    @staticmethod
    def _contextScore(guid, counts, previousKey, nextKey):

        score = 0.0

        for key, table in ((previousKey, counts["previous"]), (nextKey, counts["next"])):

            if key in table and guid in table[key]:

                total = sum(entry["count"] for entry in table[key].values())

                if total > 0:

                    score += table[key][guid]["count"] / total

        return score

    def _compare(self, a1, a2, counts, previousKey, nextKey):
        '''ComparePriorityCounts(): negative if a1 is the better guess.'''

        score1 = self._contextScore(a1, counts, previousKey, nextKey)
        score2 = self._contextScore(a2, counts, previousKey, nextKey)

        if score1 != score2:

            return -1 if score1 > score2 else 1

        empty = {"priority": 0, "count": 0, "lowercased": False}
        entry1 = counts["wordform"].get(a1, empty)
        entry2 = counts["wordform"].get(a2, empty)

        for key in ("priority", "count"):

            if entry1[key] != entry2[key]:

                return -1 if entry1[key] > entry2[key] else 1

        if entry1["lowercased"] != entry2["lowercased"]:

            return 1 if entry1["lowercased"] else -1

        # A GUID's string order is .NET's Guid.CompareTo() order
        return -1 if a1 < a2 else 1 if a1 > a2 else 0

def parseAndFile(textDump, guesser, parser):
    '''FTtranslator's Parse Words: parse each distinct word (ignoring case, as first spelled) and file the result. Returns the words with no parse. See FILING above.'''

    words = []

    for occurrence in textDump["occurrences"]:

        if "punct" not in occurrence and occurrence["wordform"].lower() not in (word.lower() for word in words):

            words.append(occurrence["wordform"])

    unparsed = []

    for word in words:

        result = parser.parse(parserForm(word))

        # A capitalized word may fail only because of its capitals
        if word.lower() != word and (result["error"] or not result["analyses"]):

            lowercaseResult = parser.parse(parserForm(word.lower()))

            if not lowercaseResult["error"] and lowercaseResult["analyses"]:

                result = lowercaseResult

        if result["error"]:

            unparsed.append(word)
            continue

        if not result["analyses"]:

            unparsed.append(word)

        guesser.file(word, result)

    return unparsed

def applyGuesses(textDump, guesser):
    '''FTtranslator's Approve Guesses: take every word's guess, then apply them all, filling in senses from msas (fillSenses()). Changes textDump's occurrences in place.'''

    # A word's neighbours within its segment, as context keys
    segments = {}

    for occurrence in textDump["occurrences"]:

        segments.setdefault(occurrence["seg"], []).append(occurrence)

    def contextKey(occurrence):

        return "p:" + occurrence["punct"] if "punct" in occurrence else "w:" + occurrence["wordform"]

    planned = []

    for segmentOccurrences in segments.values():

        for index, occurrence in enumerate(segmentOccurrences):

            if "punct" in occurrence:

                continue

            previousKey = contextKey(segmentOccurrences[index - 1]) if index > 0 else EMPTY_CONTEXT
            nextKey = contextKey(segmentOccurrences[index + 1]) if index < len(segmentOccurrences) - 1 else EMPTY_CONTEXT
            guess = guesser.bestGuess(occurrence["wordform"], occurrence["baseline"], index, previousKey, nextKey)

            if guess is not None:

                planned.append((occurrence, guess))

    for occurrence, guess in planned:

        bundles = []

        for morphBundle in guess["bundles"]:

            sense = morphBundle["sense"]

            # fillSenses(): a parser-made morph has an msa but no sense
            if sense is None and morphBundle["msa"] is not None:

                sense = guesser.lexicon.msas.get(morphBundle["msa"], {}).get("sense")

            bundles.append({"morphEntry": morphBundle["entry"], "sense": sense, "msa": morphBundle["msa"]})

        occurrence.update(kind=bundleextract.WFI_ANALYSIS, wordform=guesser.owner[guess["guid"]], bundles=bundles, analysis=guess["guid"])

    return planned

def translateToStream(text, bundleDir, parser):
    '''The whole chain: tokenize, parse and file, guess, and Extract Source Text. Returns (the Apertium stream, the messages, the text dump with its analyses, the unparsed words).'''

    lexicon = bundleextract.Lexicon.load(bundleDir)
    tokenizer = Tokenizer.load(bundleDir)
    guesser = Guesser.load(bundleDir, lexicon)

    textDump = tokenizer.tokenizeText(text)
    unparsed = parseAndFile(textDump, guesser, parser)
    applyGuesses(textDump, guesser)
    stream, messages = bundleextract.extractText(textDump, lexicon)

    return stream, messages, textDump, unparsed
