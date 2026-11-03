#
#   fttranslator/tokenizer
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. FLEx's splitting of a paragraph into segments, words and punctuation, without FieldWorks.
#
#   OVERVIEW (AI generated, then edited)
#
#   When FTtranslator adds a text to the source project, FieldWorks' ParagraphParser (liblcm, DomainServices/ITextUtils.cs) breaks each paragraph into segments (sentences), and each segment into
#   occurrences: words, which become wordforms, and runs of punctuation. This file does the same from plain data, so a translator without FieldWorks gets the same occurrences, in the format
#   golden.py's dumpText() writes and bundleextract.py reads. It ports what a new paragraph of plain text goes through: WordMaker for the words, CollectSegmentForms() and
#   CreatePunctAnnotations() for the occurrences, and CreateOrReuseAnnotation(), TryCreatePhrase() and FindOrCreateWordform() for which wordform a word becomes. Sentences are found with a
#   simpler rule than FLEx's; see SENTENCES below.
#
#   SENTENCES
#
#   By Ron's decision (2026-11-03), a sentence ends at the whitespace right after a sentence-end character, and nowhere else. The characters are the ones FLEx ends sentences with
#   (SENTENCE_END_CHARS: the period, question mark and exclamation point and their equivalents in other scripts, such as the Arabic question mark, plus the section sign U+00A7). This replaces
#   FLEx's SegmentBreaker, which also treats ellipses and decimal numbers specially, lets closing quotes and brackets after the end character stay with the sentence, and needs a letter before
#   a sentence can end. So the segments here can differ from the ones FLEx would make; the words, punctuation and wordforms don't. Segments matter to Extract Source
#   Text (a new sentence changes how punctuation attaches) and to the guesser (a segment edge counts as a neighbour), so a translation can differ from the desktop's where the two disagree.
#
#   WHAT IT NEEDS
#
#   tokenizer.json in the bundle (written by bundle.exportTokenizerData()): the vernacular writing system's id and its word-forming overrides (the characters of its "main" character set, which
#   count as word-forming whatever Unicode says), every wordform's form, and the multi-word wordforms by their lowercased first word (the wordform repository's FirstWordToPhrases).
#
#   WHICH WORDFORM A WORD BECOMES
#
#   Most words become the wordform with exactly their form. Two things change that. A word that starts one of the project's phrases (a multi-word wordform such as 'hata sibuna li') is joined
#   with the words after it when they match the phrase, ignoring case; the longest phrase wins. And the first word of the paragraph (starting at offset 0 or 1, to allow a leading quote) falls
#   back to the existing lowercase wordform when there is none with its exact form, so a capitalized sentence-initial word finds its usual analyses. A word with no wordform gets a new one,
#   and that new wordform exists for the rest of the text: "dit-il" in one paragraph makes "il", so a sentence-initial "Il" in a later paragraph becomes "il". tokenizeText() keeps the new ones.
#
#   TRAPS
#
#    - Character classes come from Python's unicodedata, where FieldWorks asks ICU. The two only disagree on characters whose Unicode properties changed between their Unicode versions.
#    - Numbers count as word-forming inside words (WordMaker.IsWordforming, LT-10746), so "3.5" is one word.
#    - Offsets in the output are UTF-16 code units, as FieldWorks counts them; Python indexes code points. They differ only after a character outside the BMP.
#    - Lowercasing uses Python's str.lower(), with the Turkish and Azeri dotted and dotless i handled as ICU's locale rules would.
#    - compareTokens() checks against FLEx's own parsing, so it compares the words, punctuation and wordforms but not which segment each is in. See SENTENCES above.
#
#   CODE STRUCTURE
#
#   Tokenizer holds tokenizer.json. Its character tests come first (isWordForming(), isWordformingInWord(), isWhite()), then segments(), nextWord(),
#   matchesWordInText(), tryCreatePhrase() and wordformFor(), then tokenizeParagraph(), which puts them together, and tokenizeText(), which splits a text into paragraphs as FTtranslator's
#   Import Text does and returns a text dump.
#

import json
import unicodedata
from pathlib import Path

TOKENIZER_FILE = "tokenizer.json"

# Unicode categories TsStringUtils.IsWordForming() accepts: letters, non-spacing and spacing combining marks, and modifier symbols
WORD_FORMING_CATEGORIES = {"Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Mc", "Sk"}

# The characters a sentence can end with: FLEx's list (liblcm TsStringUtils.IsEndOfSentenceChar()) - the period, question mark and exclamation point and their equivalents in other scripts,
# such as the Arabic question mark (U+061F) and full stop (U+06D4), the Devanagari danda and double danda, and the Ethiopic full stop and question mark - plus the section sign. See SENTENCES above.
SENTENCE_END_CHARS = {chr(ch) for ch in (0x0021, 0x002E, 0x003F, 0x055C, 0x055E, 0x0589, 0x061F, 0x06D4, 0x0700, 0x0701, 0x0702, 0x0964, 0x0965, 0x104A, 0x104B, 0x1362, 0x1367, 0x1368,
                                         0x166E, 0x1803, 0x1809, 0x1944, 0x1945, 0x17D4, 0x17D5, 0x203C, 0x203D, 0x2047, 0x2048, 0x2049, 0x3002, 0xFE52, 0xFE56, 0xFE57, 0xFF01, 0xFF0E,
                                         0xFF1F, 0xFF61, 0x00A7)}
ZERO_WIDTH_SPACE = 0x200B

class Tokenizer:
    '''FLEx's paragraph parsing for new plain-text paragraphs. See the overview above.'''

    def __init__(self, data):

        self.wsId = data["wsId"]
        self.overrides = set(data["wordFormingOverrides"])
        self.wordforms = set(data["wordforms"])
        self.phrases = data["phrases"]

    @classmethod
    def load(cls, bundleDir):

        return cls(json.loads((Path(bundleDir) / TOKENIZER_FILE).read_text(encoding="utf-8")))

    def toLower(self, text):
        '''CaseFunctions.ToLower() for the vernacular writing system.'''

        if self.wsId.split("-")[0] in ("tr", "az"):

            text = text.replace("I", "ı").replace("İ", "i")

        return text.lower()

    def isWordForming(self, ch):
        '''The writing system's word-forming test (CoreWritingSystemDefinition.get_IsWordForming()).'''

        return ord(ch) in self.overrides or unicodedata.category(ch) in WORD_FORMING_CATEGORIES

    def isWordformingInWord(self, ch):
        '''WordMaker.IsWordforming(): word-forming, or a number (numbers are part of words since LT-10746). See TRAPS above.'''

        return self.isWordForming(ch) or unicodedata.numeric(ch, None) is not None

    @staticmethod
    def isWhite(ch):

        return unicodedata.category(ch) == "Zs" or ord(ch) == ZERO_WIDTH_SPACE

    def segments(self, text):
        '''The (start, limit) of each segment (sentence), in code points: a sentence ends at the whitespace right after a period, question mark, exclamation point or section sign.
           See SENTENCES above.'''

        segments = []
        start = 0

        for i in range(1, len(text)):

            if text[i - 1] in SENTENCE_END_CHARS and text[i].isspace():

                segments.append((start, i))
                start = i

        if start < len(text):

            segments.append((start, len(text)))

        return segments

    def nextWord(self, text, pos):
        '''WordMaker.NextWord(): the next word at or after pos, as (start, limit), or None.'''

        start = None

        for i in range(pos, len(text)):

            wordForming = self.isWordformingInWord(text[i])

            if wordForming and start is None:

                start = i

            elif not wordForming and start is not None:

                return start, i

        if start is not None:

            return start, len(text)

        return None

    def matchesWordInText(self, text, phrase, ichMin):
        '''WordMaker.MatchesWordInText(): the phrase is in the text at ichMin, ignoring case, and ends where a word ends.'''

        ichLim = ichMin + len(phrase)

        if not phrase or ichLim > len(text):

            return False

        if ichLim < len(text) and self.isWordformingInWord(text[ichLim]):

            return False

        found = text[ichMin:ichLim]

        return found == phrase or self.toLower(found) == self.toLower(phrase)

    def tryCreatePhrase(self, text, word, ichMin):
        '''ParagraphParser.TryCreatePhrase(): the longest of the project's phrases that starts with this word and is in the text here, or None.'''

        best = word

        for phrase in self.phrases.get(self.toLower(word), []):

            if len(phrase) <= len(word) or len(best) > len(phrase) or not self.matchesWordInText(text, phrase, ichMin):

                continue

            best = phrase

        return best if len(best) > len(word) else None

    def wordformFor(self, form, isFirstWord, created):
        '''FindOrCreateWordform(): the form of the wordform a word becomes. created holds the wordforms made earlier in the same text, and a new one is added to it.
           See WHICH WORDFORM A WORD BECOMES above.'''

        if form in self.wordforms or form in created:

            return form

        lowered = self.toLower(form)

        if isFirstWord and (lowered in self.wordforms or lowered in created):

            return lowered

        created.add(form)

        return form

    def tokenizeParagraph(self, text, paraIndex=0, segOffset=0, created=None):
        '''The occurrences of one paragraph, in dumpText()'s format, and the number of segments. segOffset numbers the segments on from earlier paragraphs, and created holds the
           wordforms earlier paragraphs of the text made (see wordformFor()).'''

        created = set() if created is None else created

        occurrences = []
        segments = self.segments(text)
        pos = 0
        ichLimLast = 0
        pendingWord = None
        utf16 = self._utf16Offsets(text)

        def punctuation(ichMin, ichLim, seg):

            # CreatePunctAnnotations(): each run of non-white characters is one occurrence
            start = None

            for i in range(ichMin, ichLim):

                if self.isWhite(text[i]):

                    if start is not None:

                        occurrences.append({"para": paraIndex, "seg": seg, "beg": utf16[start], "end": utf16[i], "punct": text[start:i]})
                        start = None

                elif start is None:

                    start = i

            if start is not None:

                occurrences.append({"para": paraIndex, "seg": seg, "beg": utf16[start], "end": utf16[ichLim], "punct": text[start:ichLim]})

        for segIndex, (_, segLim) in enumerate(segments):

            seg = segOffset + segIndex

            # CollectSegmentForms(), which starts where the word scanner stopped; a word found past the last segment's end is this segment's first
            if pendingWord is not None:

                word = pendingWord
                pendingWord = None
            else:
                word = self.nextWord(text, pos)

                if word is not None:

                    pos = word[1]

            while True:

                if word is None:

                    # No more words: the rest of the segment is punctuation. Unlike FLEx's segments, a sentence here can follow the last word (e.g. a closing ' »'), so the
                    # punctuation is marked as done, or the next segment would repeat it.
                    punctuation(ichLimLast, segLim, seg)
                    ichLimLast = max(ichLimLast, segLim)
                    break

                ichMin, ichLim = word

                if ichLimLast != ichMin:

                    punctuation(ichLimLast, min(ichMin, segLim), seg)

                    if ichMin >= segLim:

                        pendingWord = word
                        ichLimLast = segLim
                        break

                # A phrase, the exact wordform, or the first word's lowercase wordform
                wordText = text[ichMin:ichLim]
                phrase = self.tryCreatePhrase(text, wordText, ichMin) if self.phrases else None
                annotationForm = phrase if phrase else wordText
                wordform = self.wordformFor(annotationForm, ichMin < 2, created)

                if phrase:

                    ichLimLast = ichMin + len(phrase)
                    pos = ichLimLast
                else:
                    ichLimLast = ichLim

                occurrences.append({"para": paraIndex, "seg": seg, "beg": utf16[ichMin], "end": utf16[ichLimLast], "surface": text[ichMin:ichLimLast], "baseline": text[ichMin:ichLimLast], "kind": "WfiWordform", "wordform": wordform})

                word = self.nextWord(text, pos)

                if word is not None:

                    pos = word[1]

        return occurrences, len(segments)

    def tokenizeText(self, text, title=""):
        '''Split a text into paragraphs as Import Text does (each non-blank line, stripped) and tokenize them. Returns a text dump in golden.py's format.'''

        occurrences = []
        paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
        segOffset = 0
        created = set()

        for paraIndex, paragraph in enumerate(paragraphs):

            paraOccurrences, segCount = self.tokenizeParagraph(unicodedata.normalize("NFD", paragraph), paraIndex, segOffset, created)
            occurrences += paraOccurrences
            segOffset += segCount

        return {"title": title, "paragraphs": paragraphs, "occurrences": occurrences}

    def compareTokens(self, tokensPath, out, showDiffs=5):
        '''Tokenize the paragraphs in a tokens.json (golden.py's captureTokens()) and print how many give FieldWorks' occurrences. Returns the number of paragraphs that differ.'''

        golden = json.loads(Path(tokensPath).read_text(encoding="utf-8"))
        expectedByPara = {}

        for occurrence in golden["occurrences"]:

            expectedByPara.setdefault(occurrence["para"], []).append(occurrence)

        # Segments are found by a different rule from FLEx's, so they aren't compared. See SENTENCES above.
        def normalized(occurrences):

            return [{key: value for key, value in occurrence.items() if key in ("beg", "end", "punct", "surface", "wordform")} for occurrence in occurrences]

        differing = []

        # The paragraphs were added to one text, so wordforms made by one are there for the next
        created = set()

        for paraIndex, paragraph in enumerate(golden["paragraphs"]):

            actual, _ = self.tokenizeParagraph(unicodedata.normalize("NFD", paragraph), paraIndex, created=created)
            expected = expectedByPara.get(paraIndex, [])

            if normalized(actual) != normalized(expected):

                differing.append((paragraph, normalized(expected), normalized(actual)))

        print(f"Tokenized {len(golden['paragraphs'])} paragraph(s): {len(golden['paragraphs']) - len(differing)} identical to FieldWorks, {len(differing)} differ.", file=out)

        for paragraph, expected, actual in differing[:showDiffs]:

            firstDiff = next((i for i, (e, a) in enumerate(zip(expected, actual)) if e != a), min(len(expected), len(actual)))
            print(f"\n{paragraph[:150]}\n  occurrence {firstDiff + 1}: FieldWorks {expected[firstDiff:firstDiff + 2]}\n  {' ' * len(str(firstDiff + 1))}              tokenizer {actual[firstDiff:firstDiff + 2]}", file=out)

        return len(differing)

    @staticmethod
    def _utf16Offsets(text):
        '''For each code point index (and the end), the UTF-16 offset FieldWorks would give it. See TRAPS above.'''

        offsets = [0]

        for ch in text:

            offsets.append(offsets[-1] + (2 if ord(ch) > 0xFFFF else 1))

        return offsets
