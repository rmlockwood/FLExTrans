#
#   fttranslator/bundleextract
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Extract Source Text without FieldWorks: a text's analyses plus a bundle's lexicon in, the Apertium stream out.
#
#   OVERVIEW (AI generated, then edited)
#
#   The first piece of the offline translator's runtime, and the reference for porting it to C#. It does what FLExTrans' Extract Source Text does on its usual (non-TreeTran) path - turn an
#   analyzed text into the Apertium stream that the bilingual lookup and transfer read - but from plain data instead of an open FLEx project: the lexicon from the bundle (bundle.py) and the
#   text's occurrences in the form golden.py writes them. It imports nothing from FieldWorks or FLExTrans, which is the point: if this file gives byte-identical output on the golden pairs, the
#   bundle holds everything Extract Source Text needs, and a port of this file to another language has a tested reference to follow.
#
#   HOW CLOSE THE PORT IS
#
#   Line for line. getInterlinData() and its helpers (InterlinData.py) became extractText() and the _Walker methods; TextEntirety, TextParagraph, TextSentence and TextWord (TextClasses.py)
#   became Text, Paragraph, Sentence and Word, keeping only what the non-TreeTran path uses; the few Utils functions involved are copied below with their regexes. Names follow the originals so
#   the two can be read side by side, and the odd-looking parts are kept on purpose, because changing them would change the output: affixes added before a root go in the root's slot, a
#   compound reuses its first root's stem features (Word.getStemFeatures), escapeReservedApertChars() is applied again to punctuation that is already escaped, the complex-form cache keeps the
#   first types list that matched an entry, and a lemma's capitalization comes from the occurrence's baseline text. Where the original would crash (a sense whose msa isn't a stem msa when its
#   category is read) this gives UNK instead; no real project can reach those cases and still produce a golden pair.
#
#   THE INPUTS
#
#   A Lexicon wraps lexicon.json and the config section of manifest.json. A text is golden.py's text dump: occurrences in order, each with para, seg, beg and end, and either punct or a word
#   (surface, baseline, kind, wordform, bundles). seg is an index, so the "new sentence" test compares it with None at the start instead of with FieldWorks' Hvo 0 - an index can be 0.
#
#   MESSAGES
#
#   The warnings and errors Extract Source Text's getInterlinData() gives are given here too, with the same English text, in a list of (level, text) pairs. compareGolden() compares them with
#   the messages saved in the golden index, leaving out the ones only the module itself gives (the "Exported ..." and "Export of ..." lines).
#
#   CODE STRUCTURE
#
#   The copied Utils pieces come first (escapeReservedApertChars(), containsInvalidLemmaChars(), addOne(), underscores(), splitCompounds(), doCapitalization()). Then Lexicon; then Word,
#   Sentence, Paragraph and Text; then _Walker, which holds getInterlinData()'s state and its per-occurrence steps; then extractText(), the entry point, and compareGolden(), which runs
#   extractText() over a folder of golden pairs and reports what differs (the check-golden command in cli.py calls it).
#

import json
import re
from pathlib import Path

# Copied from FLExTrans Utils, so this file needs neither FieldWorks nor FLExTrans
APERT_RESERVED = r'\[\]@/^${}<>*'
INVALID_LEMMA_CHARS = r'([\^$><{}])'
RAW_INVALID_LEMMA_CHARS = INVALID_LEMMA_CHARS[3:-2]
reApertReserved = re.compile(rf'(?<!\\)([{APERT_RESERVED}])')
reInvalidLemmaChars = re.compile(INVALID_LEMMA_CHARS)
reAddOne = re.compile(r'\d$', flags=re.RegexFlag.A)
reDataStream = re.compile('(>[^$<])')

# Copied from InterlinData and TextClasses
CHECK_DELIMITER = True
DELIMITER_STR = '{'
WFI_ANALYSIS = "WfiAnalysis"
WFI_GLOSS = "WfiGloss"
WFI_WORD_FORM = "WfiWordform"
ROOT_MISSING = "ROOT_MISSING"
PART_MISSING = "PART_MISSING"
MAX_SKIPPED_WORDS = 4
UNKNOWN_POS = 'UNK'
SENT_TAG = 'sent'

# The FlexTrans.config settings the manifest carries (ReadConfig's names)
SENTENCE_PUNCTUATION = 'SentencePunctuation'
SOURCE_FORMS_INFLECTION_1ST = 'SourceComplexFormsWithInflectionOn1stElement'
SOURCE_COMPLEX_TYPES = 'SourceComplexTypes'
SOURCE_DISCONTIG_TYPES = 'SourceDiscontigousComplexTypes'
SOURCE_DISCONTIG_SKIPPED = 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'
NO_PROPER_NOUN_WARNING = 'NoWarningForUnanalyzedProperNouns'

# Messages only ExtractSourceText.py itself gives, which this file has no counterpart for
MODULE_ONLY_MESSAGES = re.compile(r'^(Exported .* sentence\(s\)|Export of .* complete\.)')

def escapeReservedApertChars(inStr):
    '''Utils.escapeReservedApertChars(): escape the Apertium stream's reserved characters, and lone backslashes, unless already escaped.'''

    inStr = reApertReserved.sub(r'\\\1', inStr)
    inStr = re.sub(rf'(?<!\\)\\([^{APERT_RESERVED}\\]|$)', r'\\\\\1', inStr)

    return inStr

def containsInvalidLemmaChars(myStr):

    return True if reInvalidLemmaChars.search(myStr) else False

def addOne(headWord):
    '''Utils.add_one(): a headword with no homograph number gets 1.'''

    if not reAddOne.search(headWord):

        return headWord + '1'

    return headWord

def underscores(inStr):

    return re.sub(r'\.', r'_', inStr)

def splitCompounds(outStr):
    '''Utils.split_compounds(): a word with several roots, ^a1.1<n>b1.1<n>$, becomes one lexical unit per root, ^a1.1<n>$^b1.1<n>$.'''

    # Sentence punctuation units are left alone
    if re.search(r'<sent>', outStr):

        return outStr

    match = re.match(r'(.*?\^)(.*?)(\$.*)', outStr, re.DOTALL)

    if match:

        beforePunc = match.group(1)
        middle = match.group(2)
        afterPunc = match.group(3)
    else:
        return outStr

    # Split where a > is followed by the start of the next lemma; the odd items are the two-character delimiters, which get $^ put in the middle
    toks = reDataStream.split(middle)

    if len(toks) > 1:

        middle = ''

        for i, tok in enumerate(toks):

            if i & 1:

                tok = tok[0] + "$^" + tok[1]

            middle += tok

    return f'{beforePunc}{middle}{afterPunc}'

def doCapitalization(wordToChange, modelWord):
    '''TextClasses.do_capitalization(): copy the model word's capitalization (all upper, or first letter upper) onto the word.'''

    if wordToChange and modelWord:

        if modelWord.isupper():

            return wordToChange.upper()

        elif modelWord[0].isupper():

            return wordToChange[0].upper() + wordToChange[1:]

    return wordToChange

class Lexicon:
    '''A bundle's lexicon.json plus the Extract Source Text settings from its manifest.json. Records are looked up by GUID, as bundle.py writes them.'''

    def __init__(self, lexiconData, config):

        self.entries = lexiconData["entries"]
        self.senses = lexiconData["senses"]
        self.msas = lexiconData["msas"]
        self.sentPunct = config[SENTENCE_PUNCTUATION]
        self.typesInfl1stList = config[SOURCE_FORMS_INFLECTION_1ST]
        self.typesInfl2ndList = config[SOURCE_COMPLEX_TYPES]
        self.discontigTypesList = config[SOURCE_DISCONTIG_TYPES]
        self.discontigPOSList = config[SOURCE_DISCONTIG_SKIPPED]
        self.noWarningProperNoun = config[NO_PROPER_NOUN_WARNING]

    @classmethod
    def load(cls, bundleDir):
        '''Read a bundle folder's lexicon.json and manifest.json.'''

        bundleDir = Path(bundleDir)
        manifest = json.loads((bundleDir / "manifest.json").read_text(encoding="utf-8"))
        lexiconData = json.loads((bundleDir / manifest["files"]["lexicon"]).read_text(encoding="utf-8"))

        return cls(lexiconData, manifest["config"])

    def resolve(self, entryGuid):
        '''Utils.GetEntryWithSensePlusFeat(): the entry a sense-less variant leads to, and the irregularly inflected form's feature abbreviations (already sorted). Other entries are their own.'''

        resolvesTo = self.entries[entryGuid].get("resolvesTo")

        if resolvesTo:

            return resolvesTo["entry"], list(resolvesTo["inflFeatures"])

        return entryGuid, []

    def headword(self, entryGuid):

        return self.entries[entryGuid]["headword"]

    def isClitic(self, entryGuid):

        return self.entries[entryGuid]["clitic"] is not None

    def isEnclitic(self, entryGuid):

        return self.entries[entryGuid]["clitic"] == "enclitic"

    def senseMsa(self, senseGuid):
        '''The msa record of a sense, or {} if it has none.'''

        msaGuid = self.senses[senseGuid]["msa"]

        return self.msas.get(msaGuid, {}) if msaGuid else {}

class Word:
    '''TextClasses.TextWord: one word (or sentence-punctuation unit) and the data its lexical unit is built from. Entries and senses are GUIDs into the Lexicon.'''

    def __init__(self, lexicon):

        self.lexicon = lexicon
        self.initPunc = ''
        self.finalPunc = ''
        self.surfaceForm = ''
        self.lemmaList = []
        self.eList = []
        self.affixLists = []
        self.componentList = []
        self.senseList = []
        self.inflFeatAbbrevsList = []

        # Filled by the first root with stem features and then used for every root that has a feature structure. See Word.getStemFeatures().
        self.stemFeatAbbrList = []

    def addAffixesFromList(self, strList):

        self.affixLists[0] += strList

    def addEntry(self, e):

        self.eList.append(e)
        self.affixLists.append([])
        self.inflFeatAbbrevsList.append([])

    def addFinalPunc(self, myStr):

        self.finalPunc += escapeReservedApertChars(myStr)

    def addInflFeatures(self, inflFeatAbbrevs):

        self.inflFeatAbbrevsList[-1] = inflFeatAbbrevs

    def addInitialPunc(self, myStr):

        self.initPunc += escapeReservedApertChars(myStr)

    def addLemma(self, lemma):

        self.lemmaList.append(lemma)

    def addPlainTextAffix(self, myStr):

        # Before any root the affix starts the first slot; after one it goes in the last root's slot (index -1 when there are affixes but no entries yet)
        if not self.isInitialized():

            self.affixLists.append([myStr])
        else:
            self.affixLists[len(self.eList) - 1].append(myStr)

    def addSense(self, sense):

        self.senseList.append(sense)

    def buildLemmaAndAdd(self, baseStr, senseNum):

        # The last entry added is the root the lemma is for
        lem = doCapitalization(self.lexicon.headword(self.eList[-1]), baseStr)
        self.addLemma(addOne(lem) + '.' + str(senseNum + 1))

    def getAffixSymbols(self):

        return self.affixLists[0]

    def getDataStreamSymbols(self, i):

        symbols = []

        # Category first, except for <sent> units; then inflection class, stem features, irregular-form features and affixes
        if not self.isSentPunctutationWord():

            symbols = [self.getPOS(i)]

        symbols += self.getInflClass(i)
        symbols += self.getStemFeatures(i)
        symbols += self.getInflFeatures(i)

        if i < len(self.affixLists):

            symbols += self.affixLists[i]

        return '<' + '><'.join(underscores(x) for x in symbols) + '>'

    def getEntryHandle(self):

        if self.hasEntries():

            return self.eList[0]

        return 0

    def getFirstEntry(self):

        if self.hasEntries():

            return self.eList[0]

        return None

    def getInflClass(self, i):

        # A class with an empty abbreviation still gives a (blank) tag, as in the original
        msa = self._senseMsa(i)

        if msa.get("inflClass") is not None:

            return [msa["inflClass"]]

        return []

    def getInflFeatures(self, i):

        if i < len(self.inflFeatAbbrevsList):

            return list(self.inflFeatAbbrevsList[i])

        return []

    def getLemma(self, i):

        if i < len(self.lemmaList):

            return self.lemmaList[i]

        return ''

    def getPOS(self, i):

        # A sense whose msa has no category (or isn't a stem msa, where the original would crash) gives UNK; a category with an empty abbreviation gives an empty tag
        pos = self._senseMsa(i).get("pos")

        if pos is not None:

            return pos

        return UNKNOWN_POS

    def getStemFeatures(self, i):

        # As the original: the first root with a non-empty list fills the cache, and any root with a feature structure (even an empty one) then gets the cache
        msa = self._senseMsa(i)

        if msa.get("stemFeatures") is None:

            return []

        if len(self.stemFeatAbbrList) == 0:

            self.stemFeatAbbrList = list(msa["stemFeatures"])

        return list(self.stemFeatAbbrList)

    def hasEntries(self):

        return len(self.eList) > 0

    def hasComponents(self):

        return len(self.componentList) > 0

    def hasSenses(self):

        return len(self.senseList) > 0

    def initWithComplex(self, cmplxE, componentList, inflectionOnFirstElement):
        '''Make this word the complex form that replaces componentList. Affix tags come from the first or last component, by where the complex form's type puts the inflection.'''

        self.addEntry(cmplxE)
        self.componentList = componentList
        self.surfaceForm = ' '.join(w.surfaceForm for w in componentList)

        # Sense 1 of the complex entry, capitalized like the first component
        self.buildLemmaAndAdd(componentList[0].surfaceForm, 0)
        self.addSense(self.lexicon.entries[cmplxE]["senses"][0])

        firstComponent = componentList[0]
        lastComponent = componentList[-1]

        if inflectionOnFirstElement:

            affixList = firstComponent.getAffixSymbols()
        else:
            affixList = lastComponent.getAffixSymbols()

        self.addAffixesFromList(affixList)
        self.addInitialPunc(firstComponent.initPunc)
        self.addFinalPunc(lastComponent.finalPunc)

    def isInitialized(self):

        if not self.hasSenses() and len(self.affixLists) == 0:

            return False

        return True

    def isSentPunctutationWord(self):

        if len(self.affixLists) > 0 and len(self.affixLists[0]) > 0:

            if self.affixLists[0][0] == SENT_TAG:

                return True

        return False

    def notCompound(self):

        return len(self.eList) <= 1

    def outputDataStream(self, escapeLemma=False):

        return self.initPunc + '^' + self._outputDataForAllRoots(escapeLemma) + '$' + self.finalPunc

    def posMatchForMiddleItemInDiscontigousList(self, discontigPOSList):

        return self.getPOS(0) in discontigPOSList

    def write(self):

        return splitCompounds(self.outputDataStream(escapeLemma=True))

    def _outputDataForAllRoots(self, escapeLemma):

        if self.isSentPunctutationWord():

            return escapeReservedApertChars(self.getLemma(0)) + self.getDataStreamSymbols(0)

        retStr = ''

        for i, _ in enumerate(self.lemmaList):

            retStr += escapeReservedApertChars(self.getLemma(i)) if escapeLemma else self.getLemma(i)
            retStr += self.getDataStreamSymbols(i)

        return retStr

    def _senseMsa(self, i):
        '''The msa record of the ith root's sense, or {} if there is no such sense.'''

        if i < len(self.senseList) and self.senseList[i]:

            return self.lexicon.senseMsa(self.senseList[i])

        return {}

class Sentence:
    '''TextClasses.TextSentence: the words of one FLEx segment, and the complex-form substitution done on them.'''

    def __init__(self, messages):

        self.messages = messages
        self.wordList = []
        self.firstElemTypesList = []

    def findComplexForms(self, cmplxFormMap, typesList, lexicon):
        '''Cache, for each single-root word's entry, the complex forms of a type in typesList that it is part of. An entry already cached (by an earlier types list) is not looked at again.'''

        for wrd in self.wordList:

            if wrd.hasEntries() and wrd.notCompound() and wrd.getEntryHandle() not in cmplxFormMap:

                cmplxEntryTupList = []

                # One item per complex-form ref, with its types; a ref matching several types is added once per type, as in the original
                for complexForm in lexicon.entries[wrd.getEntryHandle()].get("complexForms", []):

                    for typeName in complexForm["types"]:

                        if typeName in typesList:

                            inflectionOnFirstElement = typeName in self.firstElemTypesList
                            cmplxEntryTupList.append((complexForm["entry"], complexForm["components"], inflectionOnFirstElement))

                if len(cmplxEntryTupList) > 0:

                    cmplxFormMap[wrd.getEntryHandle()] = list(cmplxEntryTupList)

    def modifyList(self, myIndex, count, complexEn, inflectionOnFirstElement, lexicon):

        componentList = []

        for _ in range(0, count):

            componentList.append(self.wordList.pop(myIndex))

        newWord = Word(lexicon)
        newWord.initWithComplex(complexEn, componentList, inflectionOnFirstElement)
        self.wordList.insert(myIndex, newWord)

    def modifyDiscontiguousList(self, myIndex, skippedWordsCount, complexEn, inflectionOnFirstElement, lexicon):

        # After the first pop everything moves up one, so the second component is at myIndex + skippedWordsCount
        componentList = []
        componentList.append(self.wordList.pop(myIndex))
        componentList.append(self.wordList.pop(myIndex + skippedWordsCount))

        newWord = Word(lexicon)
        newWord.initWithComplex(complexEn, componentList, inflectionOnFirstElement)
        self.wordList.insert(myIndex + skippedWordsCount, newWord)

    def substituteComplexForms(self, cmplxFormMap, lexicon):

        myIndex = 0

        # The last word can't start a match of two or more words
        while myIndex < len(self.wordList) - 1:

            wrd = self.wordList[myIndex]

            # The complex form that matched, if any. The original reads the loop variables after the loop; keeping the match here instead gives the same result.
            matched = None

            if wrd.getEntryHandle() in cmplxFormMap:

                cmplxEnList = cmplxFormMap[wrd.getEntryHandle()]

                if len(cmplxEnList) > 0:

                    # Most components first. Python's sort is stable, so equal lengths keep their order; a port must use a stable sort too.
                    cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True)

                    for cmplxEn, componentEList, inflectionOnFirstElement in cmplxEnList:

                        match = False
                        count = len(componentEList)

                        if count > 1 and myIndex + count - 1 < len(self.wordList):

                            for j in range(0, count):

                                if self.wordList[myIndex + j].getFirstEntry() == componentEList[j]:

                                    match = True
                                else:
                                    match = False
                                    break

                            if match:

                                matched = (count, cmplxEn, inflectionOnFirstElement)
                                break

                if matched:

                    self.modifyList(myIndex, matched[0], matched[1], matched[2], lexicon)

            myIndex += 1

    def substituteDiscontiguousComplexForms(self, cmplxFormMap, discontigPOSList, lexicon):

        myIndex = 0

        while myIndex < len(self.wordList) - 1:

            increment = 1
            wrd = self.wordList[myIndex]

            if wrd.getEntryHandle() in cmplxFormMap:

                cmplxEnList = cmplxFormMap[wrd.getEntryHandle()]

                if len(cmplxEnList) > 0:

                    cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True)
                    match = False
                    skippedCount = 0

                    # The complex form that matched, if any, as in substituteComplexForms()
                    matched = None

                    for cmplxEn, componentEList, inflectionOnFirstElement in cmplxEnList:

                        # Only two-component complex forms can be discontiguous
                        if len(componentEList) == 2 and self.wordList[myIndex].getFirstEntry() == componentEList[0]:

                            index = myIndex + 1
                            skippedCount = index - myIndex

                            # Look for the second component past up to MAX_SKIPPED_WORDS words of the allowed categories
                            while skippedCount <= MAX_SKIPPED_WORDS and index + 1 < len(self.wordList):

                                if not self.wordList[index].posMatchForMiddleItemInDiscontigousList(discontigPOSList):

                                    break

                                if self.wordList[index + 1].getFirstEntry() == componentEList[1]:

                                    match = True
                                    break

                                index += 1
                                skippedCount = index - myIndex

                            if match:

                                matched = (cmplxEn, inflectionOnFirstElement)
                                break

                    if matched:

                        self.modifyDiscontiguousList(myIndex, skippedCount, matched[0], matched[1], lexicon)
                        increment = skippedCount + 2 - 1

            myIndex += increment

    def warnForUnknownWords(self, unknownWordMap, noWarningProperNoun):

        multipleUnknownWords = False

        for myIndex, word in enumerate(self.wordList):

            # An uninitialized word is unknown; SFM markers are left alone
            if word.isInitialized() or (len(word.surfaceForm) > 0 and word.surfaceForm[0] == '\\'):

                continue

            if word.surfaceForm in unknownWordMap:

                multipleUnknownWords = True

            # A capitalized word after the first is taken for a proper noun, if the setting says so
            elif noWarningProperNoun and len(word.surfaceForm) > 0 and word.surfaceForm[0].isupper() and myIndex > 0:

                continue
            else:
                self.messages.append(("warning", "No analysis found for the word: " + word.surfaceForm + " Treating this as an unknown word."))
                unknownWordMap[word.surfaceForm] = 1

        return multipleUnknownWords

    def write(self):

        return ''.join(word.write() for word in self.wordList)

class Paragraph:
    '''TextClasses.TextParagraph.'''

    def __init__(self):

        self.sentList = []

    def write(self):

        return ''.join(sent.write() for sent in self.sentList) + '\n'

class Text:
    '''TextClasses.TextEntirety: the paragraphs of a text, and the complex-form processing done across them.'''

    def __init__(self):

        self.parList = []
        self.cmplxFormMap = {}

    def getSentCount(self):

        return sum(len(par.sentList) for par in self.parList)

    def processComplexForms(self, lexicon):

        # Both types lists fill one cache, paragraph by paragraph, the first-element list first; see Sentence.findComplexForms()
        for par in self.parList:

            for sent in par.sentList:

                sent.firstElemTypesList = lexicon.typesInfl1stList

            for typesList in (lexicon.typesInfl1stList, lexicon.typesInfl2ndList):

                for sent in par.sentList:

                    sent.findComplexForms(self.cmplxFormMap, typesList, lexicon)

        for par in self.parList:

            for sent in par.sentList:

                sent.substituteComplexForms(self.cmplxFormMap, lexicon)

    def processDiscontiguousComplexForms(self, lexicon):

        # The original only works when the discontiguous types are the first-element types (it then shares the cache); otherwise it stops with an AttributeError
        if lexicon.typesInfl1stList != lexicon.discontigTypesList:

            raise NotImplementedError("Extract Source Text can't process discontiguous complex types that differ from the complex types with inflection on the first element.")

        for par in self.parList:

            for sent in par.sentList:

                sent.substituteDiscontiguousComplexForms(self.cmplxFormMap, lexicon.discontigPOSList, lexicon)

    def warnForUnknownWords(self, noWarningProperNoun):

        unknownWordMap = {}
        multipleUnknownWords = False

        for par in self.parList:

            for sent in par.sentList:

                if sent.warnForUnknownWords(unknownWordMap, noWarningProperNoun):

                    multipleUnknownWords = True

        return multipleUnknownWords

    def write(self):

        return ''.join(par.write() for par in self.parList)

class _Walker:
    '''getInterlinData()'s state (InterlinData.interlinInfo) and the steps it takes for each occurrence.'''

    def __init__(self, lexicon, messages):

        self.lexicon = lexicon
        self.messages = messages
        self.myWord = None
        self.mySent = None
        self.myPar = Paragraph()
        self.myText = Text()
        self.isNewSentence = False
        self.isNewParagraph = False
        self.inMultiLinePuncBlock = False
        self.savedPrePunc = ''
        self.spacesStr = ''
        self.numSpaces = 0

        # The first paragraph is there from the start
        self.myText.parList.append(self.myPar)

    def setFlagsAndSpaces(self, occurrence, prevEndOffset, currSeg):

        # The gap since the last occurrence becomes the next word's leading spaces; a negative gap means a new paragraph (unless the current one is still empty)
        self.numSpaces = occurrence["beg"] - prevEndOffset
        self.spacesStr = ' ' * self.numSpaces

        if self.numSpaces < 0 and len(self.myPar.sentList) > 0:

            self.isNewParagraph = True

        if occurrence["seg"] != currSeg:

            self.isNewSentence = True

    def checkForNewSentOrPar(self):

        if self.isNewSentence:

            self.mySent = Sentence(self.messages)
            self.isNewSentence = False

            if self.isNewParagraph:

                self.myPar = Paragraph()
                self.myText.parList.append(self.myPar)
                self.isNewParagraph = False

            self.myPar.sentList.append(self.mySent)

        self.mySent.wordList.append(self.myWord)  # type: ignore  # set on the first occurrence, which is always a new sentence
        self.myWord.addInitialPunc(self.spacesStr)  # type: ignore

    def handlePunctuationOnlyParagraph(self, prevWord):

        # A new paragraph holding only punctuation: its punctuation goes on the previous word, or onto the saved punctuation after a newline
        if self.numSpaces < 0:

            if prevWord and not prevWord.finalPunc and not self.inMultiLinePuncBlock:

                prevWord.addFinalPunc(self.savedPrePunc)
                self.savedPrePunc = ''
            else:
                self.savedPrePunc += '\n'

            # Keep the first paragraph from being empty
            if len(self.myText.parList) == 1 and self.myText.getSentCount() == 0:

                self.isNewParagraph = False

    def processPunctuation(self, textPunct, reSplitPuncObj):

        # Odd items of the split are runs of sentence punctuation, even items the rest
        puncList = reSplitPuncObj.split(textPunct)

        for i, currPunc in enumerate(puncList):

            if currPunc == '':

                continue

            # Non-sentence punctuation, or sentence punctuation in the middle of a punctuation section (e.g. \xo 27.2-8)
            if i % 2 == 0 or (i % 2 == 1 and self.myWord and (self.myWord.finalPunc or self.savedPrePunc)):

                if self.myWord and not self.myWord.isSentPunctutationWord() and not self.isNewSentence and (CHECK_DELIMITER and not currPunc == DELIMITER_STR):

                    self.myWord.addFinalPunc(self.spacesStr + currPunc)
                    self.savedPrePunc = ''

                elif self.numSpaces < 0:

                    if self.savedPrePunc and self.myWord and not self.myWord.finalPunc and not self.inMultiLinePuncBlock:

                        self.myWord.addFinalPunc(self.savedPrePunc)
                        self.savedPrePunc = self.spacesStr + currPunc

                    elif not self.savedPrePunc:

                        self.savedPrePunc += self.spacesStr + currPunc
                        self.inMultiLinePuncBlock = True
                    else:
                        self.savedPrePunc += '\n' + self.spacesStr + currPunc
                else:
                    self.savedPrePunc += self.spacesStr + currPunc

            # Sentence punctuation becomes its own unit, e.g. ^.<sent>$
            else:
                self.myWord = Word(self.lexicon)
                self.myWord.addLemma(currPunc)
                self.myWord.surfaceForm = currPunc
                self.myWord.addPlainTextAffix(SENT_TAG)

                if len(self.savedPrePunc) > 0:

                    self.myWord.addInitialPunc(self.savedPrePunc)
                    self.savedPrePunc = ""

                self.checkForNewSentOrPar()

            # The spaces are used up by the first item
            self.spacesStr = ''

    def processInvalidObjError(self, word, wordform, msg):

        # Part of the word isn't tied to an entry and sense: fall back to the wordform for the lemma, or mark the gap with a bogus affix
        if word.getLemma(0) == '' and wordform is not None:

            word.addLemma(wordform)
        else:
            word.addPlainTextAffix(PART_MISSING)

        self.messages.append(("warning", msg + word.surfaceForm))

    def processWord(self, occurrence):
        '''The word part of getInterlinData()'s loop, after the word is made and placed. Returns False if an invalid character means the whole text stops here.'''

        word = self.myWord
        lexicon = self.lexicon

        # A word with no analysis has its surface form as its lemma
        if occurrence["kind"] == WFI_WORD_FORM:

            word.addLemma(occurrence["surface"])  # type: ignore
            return True

        if occurrence["kind"] not in (WFI_ANALYSIS, WFI_GLOSS):

            return True

        for morphBundle in occurrence["bundles"]:

            if not morphBundle["sense"]:

                self.processInvalidObjError(word, occurrence["wordform"], "No sense found for some part of the source word: ")
                break

            if not (morphBundle["msa"] and morphBundle["morphEntry"]):

                self.processInvalidObjError(word, occurrence["wordform"], "No morphosyntactic analysis found for some part of the source word: ")
                break

            # Variants lead to the entry that has the sense, picking up an irregularly inflected form's features on the way
            tempEntry, inflFeatAbbrevs = lexicon.resolve(morphBundle["morphEntry"])
            bundleMsa = lexicon.msas[morphBundle["msa"]]

            # An affix or clitic (but not an enclitic standing alone, which is treated as a root)
            if not bundleMsa["stem"] or (lexicon.isClitic(tempEntry) and not (lexicon.isEnclitic(tempEntry) and not word.hasEntries())):  # type: ignore

                gloss = lexicon.senses[morphBundle["sense"]]["gloss"]

                if containsInvalidLemmaChars(gloss):

                    self.messages.append(("error", f"Invalid characters in the affix: {gloss}. The following characters are not allowed: {RAW_INVALID_LEMMA_CHARS}"))
                    return False

                word.addPlainTextAffix(gloss)  # type: ignore

            # A stem or stand-alone enclitic
            else:
                if bundleMsa.get("pos") is None:

                    self.messages.append(("warning", "No grammatical category found for the source word: " + word.surfaceForm))  # type: ignore
                    break

                if containsInvalidLemmaChars(lexicon.headword(tempEntry)):

                    self.messages.append(("error", f"Invalid characters in the affix: {lexicon.headword(tempEntry)}. The following characters are not allowed: {RAW_INVALID_LEMMA_CHARS}"))
                    return False

                word.addEntry(tempEntry)  # type: ignore
                word.addInflFeatures(inflFeatAbbrevs)  # type: ignore

                # The lemma's sense number is the bundle sense's place among the resolved entry's top-level senses
                entrySenses = lexicon.entries[tempEntry]["senses"]

                if morphBundle["sense"] in entrySenses:

                    word.addSense(morphBundle["sense"])  # type: ignore
                    word.buildLemmaAndAdd(occurrence["baseline"], entrySenses.index(morphBundle["sense"]))  # type: ignore
                else:
                    word.addSense(None)  # type: ignore
                    self.messages.append(("warning", "Couldn't find the sense for source headword: " + lexicon.headword(tempEntry)))

        # No root after all the bundles
        if word.getLemma(0) == '':  # type: ignore

            if occurrence["wordform"] is not None:

                word.addLemma(occurrence["wordform"])  # type: ignore
            else:
                word.addPlainTextAffix(ROOT_MISSING)  # type: ignore

            self.messages.append(("warning", "No root or stem found for source word: " + word.surfaceForm))  # type: ignore

        return True

def extractText(textDump, lexicon):
    '''Extract Source Text for one text (golden.py's dump of it) and a Lexicon: returns the Apertium stream, with \\n line ends, and the messages as (level, text) pairs.'''

    messages = []
    walker = _Walker(lexicon, messages)
    prevEndOffset = 0
    currSeg = None
    occurrences = textDump["occurrences"]

    if not occurrences:

        messages.append(("warning", "No analyses found."))

    # Sentence punctuation runs are split out, so sentence-final and other punctuation can be told apart
    reSplitPuncObj = re.compile(rf"([{''.join(lexicon.sentPunct)}]+)")

    for occurrence in occurrences:

        walker.setFlagsAndSpaces(occurrence, prevEndOffset, currSeg)
        prevEndOffset = occurrence["end"]
        currSeg = occurrence["seg"]

        if "punct" in occurrence:

            walker.processPunctuation(occurrence["punct"], reSplitPuncObj)
            continue

        prevWord = walker.myWord
        walker.myWord = Word(lexicon)

        if walker.savedPrePunc:

            walker.handlePunctuationOnlyParagraph(prevWord)
            walker.myWord.addInitialPunc(walker.savedPrePunc)
            walker.savedPrePunc = ""

        walker.inMultiLinePuncBlock = False
        walker.checkForNewSentOrPar()
        walker.myWord.surfaceForm = occurrence["surface"]

        # An invalid character stops the whole text, as in the original, which returns the text as it stands
        if not walker.processWord(occurrence):

            return walker.myText.write(), messages

    # Punctuation left over at the end of the text, in its own paragraph
    if len(walker.savedPrePunc) > 0:

        walker.myWord.addFinalPunc('\n' + walker.savedPrePunc)  # type: ignore

    if walker.myText.warnForUnknownWords(lexicon.noWarningProperNoun):

        messages.append(("warning", "One or more unknown words occurred multiple times."))

    walker.myText.processComplexForms(lexicon)

    if len(lexicon.discontigTypesList) > 0 and len(lexicon.discontigPOSList) > 0 and (len(lexicon.typesInfl1stList) > 0 or len(lexicon.typesInfl2ndList) > 0):

        walker.myText.processDiscontiguousComplexForms(lexicon)

    return walker.myText.write(), messages

def compareGolden(bundleDir, goldenDir, out, showDiffs=5):
    '''Run extractText() on every golden pair in goldenDir with the bundle in bundleDir, and print to out how many outputs (and message lists) match. Returns the number of texts whose output
       differs.'''

    lexicon = Lexicon.load(bundleDir)
    goldenDir = Path(goldenDir)
    index = json.loads((goldenDir / "index.json").read_text(encoding="utf-8"))
    outputDiffs = []
    messageDiffs = []
    compared = 0

    for text in index["texts"]:

        # A text Extract Source Text failed on has no expected output to compare with
        if not text["ok"]:

            continue

        textDump = json.loads((goldenDir / f"{text['stem']}.text.json").read_text(encoding="utf-8"))
        expected = (goldenDir / f"{text['stem']}.expected.txt").read_text(encoding="utf-8").replace('\r\n', '\n')
        actual, messages = extractText(textDump, lexicon)
        compared += 1

        if actual != expected:

            outputDiffs.append((text, _firstDifference(expected, actual)))

        # The messages getInterlinData() gives, as a multiset, since only their content matters
        expectedMessages = sorted((m["level"], m["message"]) for m in text["messages"] if m["level"] in ("warning", "error") and not MODULE_ONLY_MESSAGES.match(m["message"]))

        if sorted(messages) != expectedMessages:

            messageDiffs.append(text["title"])

    print(f"Compared {compared} text(s): output identical for {compared - len(outputDiffs)}, messages identical for {compared - len(messageDiffs)}.", file=out)

    for text, difference in outputDiffs[:showDiffs]:

        print(f"\n{text['stem']} '{text['title']}': {difference}", file=out)

    if len(outputDiffs) > showDiffs:

        print(f"\n... and {len(outputDiffs) - showDiffs} more text(s) with different output.", file=out)

    if messageDiffs:

        print(f"\nMessages differ for: {', '.join(messageDiffs[:10])}" + (" ..." if len(messageDiffs) > 10 else ""), file=out)

    return len(outputDiffs)

def _firstDifference(expected, actual):
    '''Where two outputs first differ, as the line number and the two lines.'''

    expectedLines = expected.split('\n')
    actualLines = actual.split('\n')

    for lineNumber, (expectedLine, actualLine) in enumerate(zip(expectedLines, actualLines), 1):

        if expectedLine != actualLine:

            column = next((i for i, (a, b) in enumerate(zip(expectedLine, actualLine)) if a != b), min(len(expectedLine), len(actualLine)))
            return f"line {lineNumber}, column {column + 1}\n  expected: ...{expectedLine[max(0, column - 60):column + 80]}\n  actual:   ...{actualLine[max(0, column - 60):column + 80]}"

    return f"the outputs have {len(expectedLines)} and {len(actualLines)} lines"
