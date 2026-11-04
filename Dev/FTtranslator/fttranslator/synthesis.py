#
#   fttranslator/synthesis
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17.1 - 11/4/26 - Ron Lockwood
#    Synthesize through HCSynthByGlossDll in this process (pythonnet, .NET 8), as FLExTrans' Live Rule Tester does, so the HermitCrab config is loaded once instead of for every text.
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. FLExTrans' Convert Text to Synthesizer Format and HermitCrab synthesis steps without FieldWorks: the target Apertium stream in, the synthesized text out.
#
#   OVERVIEW (AI generated, then edited)
#
#   The last piece of the offline translator's runtime. On the desktop, after Run Apertium, Convert Text to Synthesizer Format (ConvertTextToSTAMPformat.py) turns the transfer results into the
#   HermitCrab master file, breaking target complex forms into their components and swapping in irregularly inflected variants, and Synthesize Text (DoHermitCrabSynthesis.py) writes the parses
#   file from it, runs HCSynthByGloss on it and puts the surface forms back into the transfer results. This file does the same from the bundle's synthesis folder (see synthexport.py), with no
#   FieldWorks or FLExTrans imports: the target affix list, ConversionData's cache of the target complex forms and variants, and the target HermitCrab.config.
#
#   HOW CLOSE THE PORT IS
#
#   Line for line, as in bundleextract.py: names follow the originals so the two can be read side by side, and the odd parts are kept because changing them would change the output. Ported are
#   the parts of ANAInfo the HermitCrab path uses, ConversionData's loadFromCacheNew() and getAbbrList(), changeToVariant(), writeNonComplex() and writeComponents() with doHermitCrabSynthesis=True,
#   processComplexForm(), convertIt() with calculatePrePostPunctuation(), processLU(), processLUparseError() and getContextWords(), the HermitCrab half of convert_to_STAMP() (convertToHermitCrab()
#   here), and from DoHermitCrabSynthesis createHermitCrabParsesFile(), capitalize(), extractRootAndFirstTag(), getCapitalLemmas(), produceSynthesisFile(), fixUpText() and both branches of
#   synthesizeWithHermitCrab(), the exe and the DLL (see EXE OR DLL below). The few Utils functions involved are copied below with their regexes. The error lists keep FLExTrans' (message, 0/1/2) convention inside, with the same English text,
#   and are turned into (level, text) pairs, as bundleextract.py gives them, only at the end.
#
#   WHAT IS NOT PORTED
#
#   STAMP synthesis (the ANA file, ANAInfo.write() and escapePunc()), One project mode, tracing, and everything that reads the target project: ConversionData's readDatabaseValues(),
#   convertValuesToAnas() and the cache-or-rebuild decision, and extractHermitCrabConfig() with gatherWarnings(). Those run on the desktop when the bundle is exported.
#
#   EXE OR DLL
#
#   Synthesis is the slowest step when HCSynthByGloss runs as a program: each text starts .NET and loads the whole target HermitCrab.config again (about half a second for FTT-Scratch, more for
#   a big lexicon). FLExTrans' Live Rule Tester avoids that by keeping one HCSynthByGlossDll object (the class the program itself wraps) for the session: SetHcXmlFile() loads the config once, and
#   each synthesis is just SetGlossFile() and Process(). loadHCSynthDll() does the same here with pythonnet, from the .NET 8 HCSynthByGloss.dll that hcsynth/ builds (the class is compiled into
#   it), so after start-up a text takes a few hundredths of a second. The Synthesizer uses the DLL when it is given one (--hcsynth-dll) and the program otherwise (--hcsynth); both give the same
#   surface forms file. The DLL's traps:
#    - pythonnet must be started on CoreCLR (.NET 8), not its Windows default of .NET Framework, and only one runtime can be loaded in a process. So the DLL can't share a process with
#      FieldWorks (the desktop commands); the offline commands never load FieldWorks.
#    - The dll's folder goes on sys.path, because that is where pythonnet looks for the assemblies it depends on (SIL.Machine and the rest).
#    - The program sets the UI culture from its language code argument, but the DLL ignores its LocaleCode property, so the DLL branch sets the culture itself before each Process().
#    - One HCSynthByGlossDll object writes one output file and must not be used by two threads at once; the offline server handles one request at a time.
#
#   FILES INSTEAD OF STRINGS
#
#   The transfer results come in as a string and the synthesized text goes out as one, so convertIt() and produceSynthesisFile() take the string where the originals read the transfer results
#   file, and fixUpText() works on the string instead of rewriting the synthesis file. The master, parses and surface forms files are real files, in the Synthesizer's work folder, with the
#   desktop's names (target_words-HC.txt, target_words-parses.txt, target_words-surface.txt), because HCSynthByGloss reads and writes files and so they can be compared with the desktop's Build folder.
#   They are written and read in text mode, as on the desktop, so on Windows they get \r\n just like FLExTrans' own.
#
#   TRAPS
#
#    - In HermitCrab mode writeComponents() writes the components' parses itself and never calls writeNonComplex(), so a component of a complex form doesn't get the variant substitution.
#    - The master file holds each distinct lexical unit once, and produceSynthesisFile() replaces every occurrence with one global re.sub, in master file order, so an earlier replacement can
#      change the text a later lexical unit is looked for in. That is kept.
#    - createHermitCrabParsesFile() means to write @ words (unknown to the target lexicon) as blank lines and leave them out of luInfoList, but it tests the parse's second character, HCparseStr[1],
#      and the @ is the first. So @ words do go to HCSynthByGloss and come back as failures, %0%^@word<UNK>$%, on the desktop and here. The test is kept as it is.
#    - HCSynthByGloss lists the forms of an ambiguous word (%2%a%b%) in a different order from run to run, on Windows too, so a comparison with the desktop must treat them as a set.
#    - The language code passed to HCSynthByGloss is the one FLExTrans' interface uses (exported in the manifest); it chooses the language of HC's messages, which a failed word carries.
#    - getCapitalLemmas() is called once, when the Synthesizer is made, rather than for each text as on the desktop; the config doesn't change between texts, so the map is the same.
#
#   CODE STRUCTURE
#
#   The copied Utils pieces come first (capitalizeString(), unescapeReservedApertChars()), then ANAInfo and ConversionData (cache loading only). The Convert Text to Synthesizer Format functions
#   follow in the original's order: changeToVariant(), writeNonComplex(), writeComponents(), processComplexForm(), getContextWords(), convertIt(), calculatePrePostPunctuation(),
#   processLUparseError(), processLU() and convertToHermitCrab(). Then the DoHermitCrabSynthesis functions: produceSynthesisFile(), createHermitCrabParsesFile(), capitalize(),
#   extractRootAndFirstTag(), fixUpText(), getCapitalLemmas() and synthesizeWithHermitCrab(). loadHCSynthDll() loads the DLL object. Synthesizer, last, holds a bundle's
#   synthesis data and either the HCSynthByGloss command or the DLL object; its synthesize() calls convertToHermitCrab() and then synthesizeWithHermitCrab(). The offline-stream command in cli.py
#   uses it for --synthesize, and offlineserver.py for every request.
#

import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .synthexport import AFFIX_GLOSS_FILE, CONVERSION_CACHE_FILE, HERMIT_CRAB_CONFIG_FILE, SYNTHESIS_DIR

# Copied from FLExTrans Utils, so this file needs neither FieldWorks nor FLExTrans
CIRCUMFIX_TAG_A = '_cfx_part_a'
CIRCUMFIX_TAG_B = '_cfx_part_b'
APERT_RESERVED = r'\[\]@/^${}<>*'
reApertReservedEscaped = re.compile(rf'\\([{APERT_RESERVED}\\])')

# Copied from ConvertTextToSTAMPformat
COMPLEX_FORMS = 'COMPLEX FORMS'
IRR_INFL_VARIANTS = 'IRREGULARLY INFLECTED VARIANT FORMS'
VARIANT_STR = "_variant_"

# The FlexTrans.config settings the manifest carries (ReadConfig's names)
SENTENCE_PUNCTUATION = 'SentencePunctuation'
TARGET_FORMS_INFLECTION_1ST = 'TargetComplexFormsWithInflectionOn1stElement'
TARGET_FORMS_INFLECTION_2ND = 'TargetComplexFormsWithInflectionOn2ndElement'
CLEANUP_UNKNOWN_WORDS = 'CleanUpUnknownTargetWords'

# The work folder's files, named as in the desktop's Build folder
MASTER_FILE = 'target_words-HC.txt'
PARSES_FILE = 'target_words-parses.txt'
SURFACE_FORMS_FILE = 'target_words-surface.txt'

# FLExTrans' error list codes, as the level names bundleextract.py uses
LEVEL_NAMES = {0: "info", 1: "warning", 2: "error"}

def capitalizeString(inStr, capitalizeCode):
    '''Utils.capitalizeString(): 2 is all upper case, 1 the first letter, 3 title case.'''

    if capitalizeCode == '2':

        return inStr.upper()

    elif capitalizeCode == '1':

        return inStr.capitalize()

    elif capitalizeCode == '3':

        return inStr.title()

    return inStr

def unescapeReservedApertChars(inStr):

    return reApertReservedEscaped.sub(r'\1', inStr)

class ANAInfo(object):
    '''One record of the ANA file: the analysis is kept as a string, 'pfx1 pfx2 < pos root > sfx1 sfx2', and the parts are pulled back out of it with regular expressions. Only the parts the
       HermitCrab path uses are ported (see WHAT IS NOT PORTED above).'''

    def __init__(self, pfxList=None, sfxList=None, pos=None, root=None, infxList=None):

        # If root is given, initialize with all the stuff.
        if root:

            # Treat the infixes as additional prefixes. (I believe we could put them either before or after the root)
            if infxList:

                newList = pfxList+infxList  # type: ignore  # a caller that gives a root gives the prefix list too
            else:
                newList = pfxList

            self.setAnalysisByPart(newList, pos, root, sfxList)

        self.setBeforePunc('')
        self.setAfterPunc('')
        self._firstComponentForHC = True
        self._originalLexicalUnitString = ''

    def addUnderscores(self, myStr):

        return re.sub(r' ', '_', myStr)

    def calcCase(self, word):

        if word.isupper():

            return '2'

        elif ' ' in word and word.istitle():

            return '3'

        elif word[0].isupper():

            return '1'
        else:
            return ''

    def capitalizeString(self, myStr):

        if self.getCapitalization() == '2':

            return myStr.upper()

        elif self.getCapitalization() == '1':

            return myStr.capitalize()

        elif self.getCapitalization() == '3':

            return myStr.title()
        else:
            return myStr

    def getAfterPunc(self):

        return self.AfterPunc

    def getAnalysis(self):

        return self.Analysis

    # The regexes are the original's; the analysis always has the '< pos root >' part, so the searches can't fail
    def getAnalysisPrefixes(self):  # returns [] if no prefix

        return re.search(r'(.*)\s*<', self.Analysis).group(1).split()  # type: ignore

    def getAnalysisRoot(self):

        return re.search(r'< .+ (.+) >', self.Analysis).group(1)  # type: ignore

    # Apply the capitalization code algoritm to possibly capitalize the root string.
    def getCapitalizedAnalysisRoot(self):

        return self.capitalizeString(re.search(r'< .+ (.+) >', self.Analysis).group(1))  # type: ignore

    def getAnalysisRootPOS(self):

        return re.search(r'< (.+) .+ >', self.Analysis).group(1)  # type: ignore

    def getAnalysisSuffixes(self):

        return re.search(r'>\s*(.*)', self.Analysis).group(1).split()  # type: ignore

    def getBeforePunc(self):

        return self.BeforePunc

    def getCapitalization(self):

        return self.Capitalization

    def getHCparseStr(self):
        '''The parse in HermitCrab order, <pfx1>...root<pos><sfx1>..., as the master file holds it.'''

        pfxs = '><'.join(self.getAnalysisPrefixes())

        if pfxs:

            # Remove circumfix extra stuff.
            pfxs = re.sub(CIRCUMFIX_TAG_A, '', pfxs)

            # Turn underscores to dots
            pfxs = re.sub('_', '.', pfxs)
            pfxs = '<' + pfxs + '>'

        sfxs = '><'.join(self.getAnalysisSuffixes())

        if sfxs:

            sfxs = '<' + sfxs + '>'

            # Remove the circumfix suffix entirely
            if re.search(CIRCUMFIX_TAG_B, sfxs):

                # find the end of the gloss
                endGloss = sfxs.index(CIRCUMFIX_TAG_B)

                # find the beg of the gloss
                begGloss = sfxs.rfind('<', 0, endGloss)+1

                # pull out the gloss string
                gloss = sfxs[begGloss:endGloss]

                # replace gloss string plus the tag (in angle-brackets) with nothing
                sfxs = re.sub('<'+gloss+CIRCUMFIX_TAG_B+'>', '', sfxs)

            sfxs = re.sub('_', '.', sfxs)

        # roots need to have underscores converted to spaces
        retStr = re.sub('_', ' ', self.getAnalysisRoot())

        pos = self.getAnalysisRootPOS()

        # if we have a variant, append the 'POS' to the lemma
        if pos == VARIANT_STR:

            retStr += pos

        # add the POS
        retStr += '<' + pos + '>'

        retStr = pfxs + retStr + sfxs
        return retStr

    def getOriginalLexicalUnitString(self):

        return '^'+self._originalLexicalUnitString+'$'

    def getPreDotRoot(self):  # in other words the headword

        g = re.search(r'< .+ (.+)\.\d+ >', self.Analysis, flags=re.RegexFlag.A)  # re.RegexFlag.A=ASCII-only match

        if g:

            ret = self.removeUnderscores(g.group(1))
            return ret

        return None

    def getSenseNum(self):

        return re.search(r'< .+ .+\.(\d+) >', self.Analysis, flags=re.RegexFlag.A).group(1)  # type: ignore  # only called for a root that getPreDotRoot() found, so it has a sense number

    def removeUnderscores(self, myStr):

        return re.sub(r'_', ' ', myStr)

    def removePeriods(self, myStr):

        return re.sub(r'\.', '', myStr)

    def setCapitalization(self, myCapitalization):

        self.Capitalization = myCapitalization

    def setAnalysis(self, myAnalysis):

        self.Analysis = myAnalysis

        # Call setAnalysisByPart to ensure the root is converted to lowercase
        self.setAnalysisByPart(self.getAnalysisPrefixes(), self.getAnalysisRootPOS(), self.getAnalysisRoot(), self.getAnalysisSuffixes())

    def setAnalysisByPart(self, prefixes, pos, root, suffixes):  # prefixes and suffixes are string lists

        self.Capitalization = self.calcCase(root)

        # change spaces to underscores in the root:
        myRoot = self.addUnderscores(root)

        # change spaces to underscores in the POS:
        myPos = self.addUnderscores(pos)

        # remove periods in the POS
        myPos = self.removePeriods(myPos)

        # if it's an unknown word, don't change the case, otherwise we always store lower case
        if pos != 'UNK':

            myRoot = myRoot.lower()

        self.Analysis = ' '.join(prefixes) + ' < '+myPos+' '+myRoot+' > '+' '.join(suffixes)

    def setAfterPunc(self, myAfterPunc):

        self.AfterPunc = myAfterPunc

    def setBeforePunc(self, myBeforePunc):

        self.BeforePunc = myBeforePunc

    def setOriginalLexicalUnitString(self, LUstr):

        self._originalLexicalUnitString = LUstr

class ConversionData():
    '''The target complex forms and irregularly inflected variants, loaded from the bundle's copy of ConversionData's cache file. Only loadFromCacheNew() and what it needs are ported; the
       desktop decides whether the cache is current and rebuilds it when the bundle is exported (see synthexport.py). The file's layout is described in ConvertTextToSTAMPformat.py.'''

    def __init__(self, cacheFilePath):

        self.cacheFilePath = str(cacheFilePath)
        self.rootComponentANAlistMap = {}
        self.rootVariantANAandFeatlistMap = {}
        self.loadFromCacheNew()

    def getAbbrList(self, indx, lines):

        abbrList = []

        # Get number of abbreviations to read in
        numAbbr = int(lines[indx].rstrip())
        indx += 1

        # read in the name value pairs in consecutive lines
        for _ in range(0, numAbbr):

            name = lines[indx].rstrip()
            val = lines[indx+1].rstrip()
            indx += 2

            # Add them to the list
            abbrList.append((name, val))

        return abbrList

    def getCacheFilePath(self):

        return self.cacheFilePath

    def getData(self):

        return (self.rootComponentANAlistMap, self.rootVariantANAandFeatlistMap)

    def loadFromCacheNew(self):

        f = open(self.getCacheFilePath(), encoding='utf-8')

        complexLines = []
        inflLines = []

        # start with complex forms
        doingComplexForms = True

        # Read each section of the cache file
        for i, line in enumerate(f):

            # Skip the first line
            if i == 0:

                continue

            # Next read the irregular forms. Skip this line
            if line.rstrip() == IRR_INFL_VARIANTS:

                doingComplexForms = False
                continue

            if doingComplexForms == True:

                complexLines.append(line.rstrip())
            else:  # variant forms
                inflLines.append(line.rstrip())

        # Process complex forms
        i = 0
        t = len(complexLines)

        while i < t:

            # Get the basic info.
            headWord = complexLines[i].rstrip()
            inflectionOnFirst = complexLines[i+1].rstrip() == 'True'
            numComponents = int(complexLines[i+2].rstrip())

            i += 3
            componentAnaList = []

            # Get the components for the current complex form
            for _ in range(0, numComponents):

                newANA = ANAInfo()
                newANA.setAnalysis(complexLines[i].rstrip())
                componentAnaList.append(newANA)

                i += 1

            self.rootComponentANAlistMap[headWord] = componentAnaList, inflectionOnFirst

        # Process irregular forms
        i = 0
        t = len(inflLines)

        while i < t:

            headWord = inflLines[i].rstrip()
            numVariants = int(inflLines[i+1].rstrip())
            i += 2
            variantANAandFeatlist = []

            for _ in range(0, numVariants):

                newANA = ANAInfo()
                newANA.setAnalysis(inflLines[i].rstrip())

                i += 1
                abbrList = self.getAbbrList(i, inflLines)

                # move the i index past all the abbreviations. Length x2 since each abbr. has two lines (name, val). 1 more for the num of abbreviations at the start of the abbrev. block
                i += len(abbrList)*2 + 1

                variantANAandFeatlist.append((newANA, abbrList))

            self.rootVariantANAandFeatlistMap[headWord] = variantANAandFeatlist

        f.close()
        return True

# Check if the tags (prefixes & suffixes) match the features of one of the main entry's variants. If so replace the main entry headword with the variant and remove the tags that matched.
# E.g. if the main entry 'be1.1' has an irr. infl. form variant 'am1.1' with a variant type called 1Sg which has features [per: 1ST, num: SG] and the Ana entry is '< cop be1.1 >  1ST SG',
# we want a new Ana entry that looks like this: '< _variant_ am1.1 >'. Only the HermitCrab branch is ported; the original's two branches are the same anyway.
def changeToVariant(myAnaInfo, rootVariantANAandFeatlistMap):

    oldCap = myAnaInfo.getCapitalization()
    pfxs = myAnaInfo.getAnalysisPrefixes()
    numPfxs = len(pfxs)
    sfxs = myAnaInfo.getAnalysisSuffixes()
    tags = pfxs+sfxs
    numFeatures = 0
    variantMatches = False
    i = 0
    varAna = None

    # loop through the irr. infl. form variant list for this main entry
    variantANAandFeatlist = rootVariantANAandFeatlistMap[myAnaInfo.getPreDotRoot()]

    for varAna, featAbbrList in variantANAandFeatlist:  # each tuple as form (entry, featAbbrList)

        # See if there is a variant that has inflection features that match the tags in this entry
        variantMatches = False
        featList = [y[1] for y in sorted(featAbbrList, key=lambda x: x[0])]
        numFeatures = len(featList)

        # There has to be at least as many tags as features
        if len(tags) >= numFeatures:

            # Loop through slices of the tag list
            for i in range(0, len(tags)-numFeatures+1):

                # See if we match regardless of order
                if sorted(tags[i:i+numFeatures]) == sorted(featList):

                    variantMatches = True
                    break

            if variantMatches:

                break

    if variantMatches and varAna is not None:

        # Remove the matched tags
        del pfxs[i:i+numFeatures]
        beg = i-numPfxs

        if beg < 0:

            beg = 0

        end = i-numPfxs+numFeatures

        if end < 0:

            end = 0

        del sfxs[beg:end]

        # Reset the Ana info. For HermitCrab we put out the sense #. A variant can be a variant of an entry with multiple senses, whose categories could take affixes differently.
        myAnaInfo.setAnalysisByPart(pfxs, VARIANT_STR, varAna.getCapitalizedAnalysisRoot()+'.'+myAnaInfo.getSenseNum(), sfxs)

        # Change the case as necessary
        myAnaInfo.setCapitalization(oldCap)

def writeNonComplex(myAnaInfo, rootVariantANAandFeatlistMap, fOutput, HCparseStrMap):
    '''Write one master file line for a word that isn't a complex form, substituting a variant first when one matches. A lexical unit already written is skipped.'''

    root = myAnaInfo.getPreDotRoot()

    if root in rootVariantANAandFeatlistMap:

        # replace main entry with variant entry and remove appropriate tags (pfxs & sfxs)
        changeToVariant(myAnaInfo, rootVariantANAandFeatlistMap)

    originalLexicalUnitStr = myAnaInfo.getOriginalLexicalUnitString()

    # see if the orignal LU string for is already in our map
    if HCparseStrMap is not None and originalLexicalUnitStr not in HCparseStrMap:

        # Get the string that we would write to the parses file
        HCparseStr = myAnaInfo.getHCparseStr()
        cap = myAnaInfo.getCapitalization()

        fOutput.write(originalLexicalUnitStr + ',' + HCparseStr + ';' + cap + '\n')

        HCparseStrMap[originalLexicalUnitStr] = 1

def writeComponents(componentList, fOutput, theAnaInfo, HCparseStrMap):
    '''Write one master file line for a complex form: its lexical unit, then each component's parse, separated by |. No variant substitution happens here (see TRAPS above).'''

    originalLexicalUnitStr = theAnaInfo.getOriginalLexicalUnitString()

    # see if the orignal LU string for this complex form is already in our map
    if HCparseStrMap is not None and originalLexicalUnitStr not in HCparseStrMap:

        for i, listAnaInfo in enumerate(componentList):

            # Get the string that we would write to the parses file
            HCparseStr = listAnaInfo.getHCparseStr()
            cap = listAnaInfo.getCapitalization()

            # First component, write the original LU string and the first component
            if i == 0:

                fOutput.write(originalLexicalUnitStr + ',' + HCparseStr + ';' + cap)

            # Write all other components
            else:
                fOutput.write('|' + HCparseStr + ';' + cap)

        fOutput.write('\n')
        HCparseStrMap[originalLexicalUnitStr] = 1

def processComplexForm(textAnaInfo, componANAlist, inflectionOnFirst):

    firstRoot = True
    newCompANAlist = []

    for index, myAnaInfo in enumerate(componANAlist):

        # See if we are at the beginning or the end, depending on where the inflection goes, write out all the stuff with inflection
        if (inflectionOnFirst and firstRoot) or (not inflectionOnFirst and index == len(componANAlist)-1):

            # Create a new Ana info object
            newAna = ANAInfo()

            # add affixation to the ANA object. Affixes on the myAnaInfo are proclitics and enclitics if they exist. Put text prefixes after proclitics and suffixes before enclitics.
            newAna.setAnalysisByPart(myAnaInfo.getAnalysisPrefixes()+textAnaInfo.getAnalysisPrefixes(), myAnaInfo.getAnalysisRootPOS(), myAnaInfo.getCapitalizedAnalysisRoot(), textAnaInfo.getAnalysisSuffixes()+myAnaInfo.getAnalysisSuffixes())

            newCompANAlist.append(newAna)
            currentAna = newAna
        else:
            newCompANAlist.append(myAnaInfo)
            currentAna = myAnaInfo

        # Set the capitalization of the first ANA object to be the same as the original complex form ANA object. This is because a complex form that is normally lower case might be capitalized in the text.
        if firstRoot:

            currentAna.setCapitalization(textAnaInfo.getCapitalization())

        firstRoot = False

    return newCompANAlist

def getContextWords(wrdCnt, wordToks):

    # Determine the context words around the problem word
    if wrdCnt-2 >= 0:

        prev2words = wordToks[wrdCnt-2] + ' ' + wordToks[wrdCnt-1]
    else:
        if wrdCnt-1 >= 0:

            prev2words = wordToks[wrdCnt-1]
        else:
            prev2words = ''

    if wrdCnt+2 < len(wordToks):

        foll2words = wordToks[wrdCnt+1] + ' ' + wordToks[wrdCnt+2]
    else:
        if wrdCnt+1 < len(wordToks):

            foll2words = wordToks[wrdCnt+1]
        else:
            foll2words = ''

    return prev2words, foll2words

def convertIt(pfxName, resultsFileStr):
    '''Split the transfer results into lexical units and the punctuation between them, and return (errorList, the ANAInfo list). The original reads the transfer results file; this takes its text.'''

    errorList = []
    wordAnaInfoList = []
    anaObj = None

    affixMap = {}

    # Read in the target affix list.
    fAfx = open(pfxName, 'r', encoding='utf-8')

    for line in fAfx:

        (affix, morphType) = re.split(r'\|', line.rstrip())
        affixMap[affix] = morphType

    fAfx.close()

    # Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x
    resultsFileStr = re.sub(r'\^([^^]+?)<sent>\$', r'\1', resultsFileStr)  # use [^^] (meaning not caret because otherwise using . might match a ^)

    # Split the string into lexical units and 'punctuation' (non-lexical units)
    tokens = re.split(r'\^(.+?)\$', resultsFileStr)

    # Pair up the tokens. The first is the punctuation, the second is the LU
    tokenPairs = list(zip(tokens[::2], tokens[1::2]))

    # Loop through pairs of tokens.
    for cnt, (punc, lu) in enumerate(tokenPairs):

        # Special handling of first word (no post punctuation gets added)
        if cnt == 0:

            # Process the lexical unit string and get an ANA object back
            anaObj, morphs = processLU(lu, affixMap)

            if anaObj == None:

                return processLUparseError(cnt, tokens[1::2], morphs), wordAnaInfoList

            anaObj.setBeforePunc(punc)
        else:
            # Determine what part of the punctuation goes at the end of the last word and which goes to the beginning of the current word.
            pre, post = calculatePrePostPunctuation(punc)

            # 'post' belongs to the previous word (anaObj isn't reassigned to the current word until below). Guard in case the previous word never produced a valid ANA object.
            if anaObj is not None:

                anaObj.setAfterPunc(post)

            # Process the lexical unit string and get an ANA object back
            anaObj, morphs = processLU(lu, affixMap)

            if anaObj == None:

                return processLUparseError(cnt, tokens[1::2], morphs), wordAnaInfoList

            anaObj.setBeforePunc(pre)

        wordAnaInfoList.append(anaObj)

    # Process a possible last punctuation string
    if anaObj and len(tokens) > 0 and tokens[-1] != '':

        anaObj.setAfterPunc(re.sub(r'^ ', '', tokens[-1]))  # remove preceding space

    return errorList, wordAnaInfoList

def calculatePrePostPunctuation(puncStr):

    pre = post = ''

    if puncStr:

        puncList = re.split(' ', puncStr)
        post = puncList[0]
        pre = " ".join(puncList[1:])

        # If post punctuation is non-empty add a trailing space. Otherwise we will get two words jammed together by STAMP. It doesn't put a space between words when \n is used.
        if post and post[-1] != '\n':

            post += ' '

    return pre, post

def processLUparseError(cnt, tokList, morphs):

    prev2words, foll2words = getContextWords(cnt, tokList)  # just pass the lexical units
    errorList = [("Lemma or grammatical category missing for a target word near word {wordNum}. Found only: {morphs}. The preceding two words were: {prevWords}. The following two words were: {follWords}. Processing stopped.".format(wordNum=str(cnt+1), morphs=",".join(morphs), prevWords=prev2words, follWords=foll2words), 2)]
    return errorList

def processLU(lexUnitStr, affixMap):

    prefixList = []
    suffixList = []
    infixList = []
    circumfixList = []
    wordAnaInfo = None

    # Get the root, root category and any affixes
    morphs = re.split('<|>', lexUnitStr)
    morphs = [tk for tk in morphs if tk]  # remove empty strings

    # start at position 2 since this is where the affixes start
    for i in range(2, len(morphs)):

        # If we don't have the item in the affix map, then it must be a feature. Treat it like a suffix, because change_to_variant will use the feature(s) to find a variant
        if morphs[i] not in affixMap:

            suffixList.append(morphs[i])

        # We use English morphnames as a standard in the target affix glosses file. prefix
        elif affixMap[morphs[i]] in ['prefix', 'proclitic', 'prefixing interfix']:

            prefixList.append(morphs[i])

        # infix
        elif affixMap[morphs[i]] in ['infix', 'infixing interfix']:

            infixList.append(morphs[i])

        # circumfix
        elif affixMap[morphs[i]] == 'circumfix':

            # Circumfixes are made of two parts, a prefix part and a suffix part when we encounter a new circumfix, give it a unique new gloss and add it to the prefix list. When we see one that
            # we've seen before, it must be the suffix part. Give it a unique new gloss and add it to the suffix list.
            if morphs[i] not in circumfixList:

                prefixList.append(morphs[i]+CIRCUMFIX_TAG_A)
                circumfixList.append(morphs[i])
            else:
                suffixList.append(morphs[i]+CIRCUMFIX_TAG_B)

        # suffix. Treat everything else as a suffix (suffix, enclitic, suffixing interfix). The other types are not supported, but will end up here.
        else:
            suffixList.append(morphs[i])

    if len(morphs) < 2:

        return wordAnaInfo, morphs

    # Create an ANA Info object. We have the root (morphs[0]) and the POS of the root (morphs[1])
    wordAnaInfo = ANAInfo(prefixList, suffixList, morphs[1], morphs[0], infixList)
    wordAnaInfo.setOriginalLexicalUnitString(lexUnitStr)

    return wordAnaInfo, morphs

def convertToHermitCrab(convData, affixFile, resultsFileStr, HCmasterFile, complexForms1st, complexForms2nd, sentPunct):
    '''The HermitCrab half of convert_to_STAMP(): write the master file from the transfer results. Returns the error list. The type lists were checked when the bundle was exported.'''

    errorList = []

    if not (affixFile and sentPunct):

        errorList.append(("Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct", 2))
        return errorList

    # Build the complex forms map. Create a map that tracks which complex form types are for first or for last. convert_to_STAMP() hands it to ConversionData, which only uses it when it
    # rebuilds its cache; the bundle's cache was made on the desktop, so here it is built only to keep the original's steps.
    complexFormTypeMap = {}

    if complexForms1st:

        for cmplxType in complexForms1st:

            complexFormTypeMap[cmplxType] = 0  # 0 - inflection on first root

    if complexForms2nd:

        for cmplxType in complexForms2nd:

            complexFormTypeMap[cmplxType] = 1  # 1 - inflection on last root

    # Convert the Apertium text to an ANA list
    errList, anaInfoList = convertIt(affixFile, resultsFileStr)

    if len(errList) > 0:

        errorList.extend(errList)
        return errorList

    # retrieve the data that got initialized in the Conversion data class
    (rootComponANAlistMap, rootVariantANAandFeatlistMap) = convData.getData()

    # Now we are going to process the ANA list, breaking down each complex form into separate ANA records if needed. This is needed for instance if a source word maps to multiple words in the
    # target language.
    try:
        fOutput = open(HCmasterFile, 'w', encoding='utf-8')

    except OSError:

        errorList.append(("Error writing the output file.", 2))
        return errorList

    count = 0
    HCparseStrMap = {}

    # Loop through all the ANA pieces
    for anaInfo in anaInfoList:

        # If an ANA root matches a complex form, rewrite the ana file with complex forms broken down into components
        root = anaInfo.getPreDotRoot()

        if root in rootComponANAlistMap:

            componANAlist, inflectionOnFirst = rootComponANAlistMap[root]
            newCompANAlist = processComplexForm(anaInfo, componANAlist, inflectionOnFirst)
            writeComponents(newCompANAlist, fOutput, anaInfo, HCparseStrMap)
        else:  # write it out as normal. This also converts variant forms if needed.
            writeNonComplex(anaInfo, rootVariantANAandFeatlistMap, fOutput, HCparseStrMap)

        count += 1

    errorList.append((f"Converted target words put in the file: {HCmasterFile}", 0))
    errorList.append((f"{count} records exported in HermitCrab format.", 0))

    fOutput.close()

    return errorList

def produceSynthesisFile(luInfoList, surfaceFormsFile, resultsFileStr):
    '''Put the surface forms into the transfer results. Returns (errorList, the synthesized text, or None on an error). The original reads the transfer results file and writes the synthesis file.'''

    errorList = []

    # Open the surface forms file
    try:
        fSurfaceForms = open(surfaceFormsFile, encoding='utf-8-sig')

    except OSError:

        errorList.append(('There was an error opening the HermitCrab surface forms file.', 2))
        return errorList, None

    # Read in the surface forms
    surfaceFormsList = fSurfaceForms.readlines()
    fSurfaceForms.close()

    # Remove blank lines
    surfaceFormsList = [line for line in surfaceFormsList if line.strip()]

    # Do a sanity check to see if the number of surface forms matches the number of Lexical unit strings
    if len(surfaceFormsList) != len(luInfoList):

        errorList.append(('The number of surface forms does not match the number of Lexical Units.', 2))
        return errorList, None

    # Loop through the surface forms file. Some lines will have multiple surface forms
    for i, line in enumerate(surfaceFormsList):

        line = line.strip()

        # parse multiple surface forms
        surfaceStrList = re.split(',', line)

        (originalLUStr, capCodeList) = luInfoList[i]

        newSurfaceList = []

        # Loop through possible multiple surface forms
        for j, surfaceStr in enumerate(surfaceStrList):

            # See if we have an error E.g. %0%^iba1.1<n><PC.1Sg>$%
            if surfaceStr[0:3] == '%0%':

                # Everything left of the last % is what we are saving for the surface string
                saveStr = surfaceStr[:surfaceStr.rindex('%')+1]

                # Save the error. Everthing to the right of the last %. Make this a warning, code = 1
                errStr = surfaceStr[surfaceStr.rindex('%')+1:]

                if errStr.strip() == '':

                    errStr = f'Synthesis failed. ({saveStr})'

                errorList.append((errStr, 1))
                surfaceStr = saveStr

            surfaceStr = capitalizeString(surfaceStr, capCodeList[j])
            newSurfaceList.append(surfaceStr)

        # substitute the Apertium parse with the surface form throughout the target text
        resultsFileStr = re.sub(re.escape(originalLUStr), " ".join(newSurfaceList), resultsFileStr)

    # Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x. This regex looks for a non-% or beg. of string followed by a ^ in order to find the sentence lexical unit. The
    # non-% is needed because a word that didn't synthesize leaves an error string like %0%^iba1.1<n><PC.1Sg>$%, whose ^ must not start the match. An error string can also come right before it, so $%^.
    resultsFileStr = re.sub(r'([^%]|^|\$%)\^(.+?)<sent>\$', r'\1\2', resultsFileStr)

    return errorList, resultsFileStr

def createHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap):

    errorList = []

    # Open master file
    try:
        fMaster = open(masterFile, encoding='utf-8')

    except OSError:

        errorList.append((f'There was an error opening the HermitCrab master file. Do you have the setting "Use HermitCrab Synthesis" turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}', 2))
        return errorList

    # Open parses file
    try:
        fParses = open(parsesFile, 'w', encoding='utf-8')

    except OSError:

        fMaster.close()
        errorList.append(('There was an error opening the HermitCrab parses file.', 2))
        return errorList

    # Parse each line - format: LU,HCparse1;capitalizationCode|HCparse2;capitalizationCode|...
    for line in fMaster:

        line = line.rstrip()

        if len(line) == 0:

            continue

        # Get the lexical unit (expect exactly one comma separating LU and parses)
        parts = re.split(',', line)

        if len(parts) != 2:

            errorList.append((f'Malformed Lexical Unit in HermitCrab master file skipping this line: {line}', 2))
            continue

        luStr, HCparseStr = parts

        # skip @ words. They have the form: ^@...
        if HCparseStr[1] == '@':

            fParses.write('\n')
            continue

        # Get the parses
        HCparsesList = re.split(r'\|', HCparseStr)
        capCodeList = []

        # Get the parse and capitalization code pair
        for hcparseCombo in HCparsesList:

            hcParse, capCode = re.split(';', hcparseCombo)
            capCodeList.append(capCode)

            # Capitalize if necessary
            if capCode:

                hcParse = capitalize(hcParse, HCcapitalLemmasMap)

            # Write the parse to the parses file
            fParses.write('^' + hcParse + '$')

        fParses.write('\n')
        luInfoList.append((luStr, capCodeList))

    fMaster.close()
    fParses.close()
    return errorList

def capitalize(hcParse, HCcapitalLemmasMap):

    root, posName = extractRootAndFirstTag(hcParse)

    if root is None or posName is None:

        return hcParse  # fallback

    key = root.lower() + (posName if posName else "")
    rootCap = HCcapitalLemmasMap.get(key, root)

    # Replace only the first occurrence of root with rootCap
    rebuilt = hcParse.replace(root, rootCap, 1)
    return rebuilt

def extractRootAndFirstTag(hcParse):
    '''Returns (root, firstTagAfterRoot) from a HermitCrab parse string. Example: <2s.S2>tang1.1<v><3sg><obj> -> ('tang1.1', 'v')'''

    # Find all tags. There should be at least one tag - the POS
    tagMatches = list(re.finditer(r'<([^>]+)>', hcParse))
    root = None
    firstTagAfterRoot = None

    # If there are no tags, the whole string is the root
    if not tagMatches:

        return hcParse, None

    # Find the root: the text between the last '>' and the next '<'
    for i, match in enumerate(tagMatches):

        # No tags before the root
        if i == 0 and match.start() > 0:

            root = hcParse[0:match.start()]

            # The first tag will this 0th match
            firstTagAfterRoot = match.group(1)
            return root, firstTagAfterRoot

        # Root must be after a prefix
        elif i > 0:

            prev = tagMatches[i-1]

            # The root will be found where there is a gap between tags
            if prev.end() < match.start():

                root = hcParse[prev.end():match.start()]

                # The first tag will be the ith match (the one after the gap)
                firstTagAfterRoot = match.group(1)
                return root, firstTagAfterRoot

    # If no root found in the loop, check after the last tag
    lastTag = tagMatches[-1]

    if lastTag.end() < len(hcParse):

        root = hcParse[lastTag.end():]
        return root, None

    # Fallback: no root found
    return None, None

def fixUpText(synFileContents, cleanUpText):
    '''Remove @ signs at the beginning of words and N.N at the end of words if so desired in the settings, also symbols and ^%0%...%$. The original rewrites the synthesis file; this returns the text.'''

    if cleanUpText:

        # Remove n.n on lemmas
        synFileContents = re.sub(r'\d+\.\d+', '', synFileContents, flags=re.RegexFlag.A)  # re.A=ASCII-only match

        # Remove at signs
        synFileContents = re.sub('@', '', synFileContents)

        # Remove symbols, i.e. <xyz>
        synFileContents = re.sub('<.*?>', '', synFileContents)

        # Remove the ^%0%...%$ (^ and $ are optional which is the case for unknown punctuation)
        synFileContents = re.sub(r'%0%\^{0,1}(.*?)\${0,1}%', r'\1', synFileContents)

    # Un-escape punctuation text that was escaped before running apertium tools. E.g. convert \] to ]
    synFileContents = unescapeReservedApertChars(synFileContents)

    return synFileContents

def getCapitalLemmas(HCconfigPath):

    # Create a dictionary to store the extracted lemmas
    HCcapitalLemmasMap = {}

    # Parse the HermitCrab.config XML file
    try:
        tree = ET.parse(HCconfigPath)
        root = tree.getroot()

    except (OSError, ET.ParseError):

        return None

    # Find the PartsOfSpeech element
    partsOfSpeechElem = root.find('.//PartsOfSpeech')

    # Build a dictionary mapping part of speech id to name
    partOfSpeechMap = {}

    if partsOfSpeechElem is not None:

        for posElem in partsOfSpeechElem.findall('PartOfSpeech'):

            posId = posElem.get('id')
            nameElem = posElem.find('Name')

            if posId and nameElem is not None and nameElem.text:

                partOfSpeechMap[posId] = nameElem.text

    # Iterate over all LexicalEntry elements
    for lexEntry in root.findall('.//LexicalEntry'):

        glossElem = lexEntry.find('Gloss')
        posId = lexEntry.get('partOfSpeech')

        # Only proceed if both gloss and partOfSpeech are present and valid
        if glossElem is not None and glossElem.text and posId in partOfSpeechMap:

            glossText = glossElem.text
            posName = partOfSpeechMap[posId]

            # Only add if any letter in the gloss is uppercase
            if any(char.isupper() for char in glossText):

                # Build a key for the map of gloss name + POS
                key = (glossText.lower() + posName)
                HCcapitalLemmasMap[key] = glossText

    return HCcapitalLemmasMap

def synthesizeWithHermitCrab(hcsynthCommand, languageCode, HCconfigPath, HCcapitalLemmasMap, parsesFile, masterFile, surfaceFormsFile, resultsFileStr, clean, DLLobj=None):
    '''synthesizeWithHermitCrab(): write the parses file, run HCSynthByGloss (the DLL object if there is one, otherwise the program) and put its surface forms into the transfer results. Returns
       (errorList, the synthesized text or None). The capital lemmas map is made once by the Synthesizer (see TRAPS above), and clean is the CleanUpUnknownTargetWords value.'''

    luInfoList = []

    if HCcapitalLemmasMap is None:

        return [('Unable to open the HC master file.', 2)], None

    errorList = createHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap)

    for triplet in errorList:

        if triplet[1] == 2:  # error

            return errorList, None

    # Call HCSynthesis to produce surface forms. Do the operation with a dll differently than with the program; the dll already holds the HermitCrab config and writes surfaceFormsFile.
    if DLLobj:

        # The program sets the UI culture from its language code, which chooses the language of HC's messages; the DLL doesn't, so it is done here (see EXE OR DLL above)
        from System.Globalization import CultureInfo  # type: ignore  # a .NET namespace that pythonnet provides at run time
        from System.Threading import Thread  # type: ignore

        culture = CultureInfo.GetCultureInfo(languageCode)
        CultureInfo.DefaultThreadCurrentUICulture = culture
        Thread.CurrentThread.CurrentUICulture = culture
        DLLobj.LocaleCode = languageCode
        DLLobj.DoTracing = False
        DLLobj.ShowTracing = False

        try:
            if DLLobj.SetGlossFile(str(parsesFile)) != DLLobj.kSuccess:

                errorList.append(('An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).', 2))
                return errorList, None

        except Exception as e:

            errorList.append((f'An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}', 2))
            return errorList, None

        try:
            if DLLobj.Process() != DLLobj.kSuccess:

                errorList.append(('An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).', 2))
                return errorList, None

        except Exception as e:

            errorList.append((f'An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}', 2))
            return errorList, None
    else:
        # hcsynthCommand stands in for FTPaths.HC_SYNTHESIZE; the arguments are the same
        params = list(hcsynthCommand) + [languageCode, '-h', str(HCconfigPath), '-g', str(parsesFile), '-o', str(surfaceFormsFile)]

        try:
            result = subprocess.run(params, capture_output=True, check=True)

            if result.returncode != 0:

                errorList.append(('An error happened when running the HermitCrab Synthesize By Gloss tool.', 2))
                errorList.append((result.stderr.decode(), 2))
                return errorList, None

        except subprocess.CalledProcessError as e:

            errorList.append(('An error happened when running the HermitCrab Synthesize By Gloss tool.', 2))
            errorList.append((e.stderr.decode(), 2))
            return errorList, None

    # Count the # of lexical units
    with open(parsesFile, encoding='utf-8') as f:

        lines = f.readlines()
        nonEmptyLines = [line for line in lines if line.strip()]
        LUsCount = len(nonEmptyLines)

    errorList.append((f'Processing {LUsCount} unique lexical units.', 0))

    # Produce synthesis file
    errList, synFileContents = produceSynthesisFile(luInfoList, surfaceFormsFile, resultsFileStr)
    errorList.extend(errList)

    # check for fatal errors
    if synFileContents is None or any(triplet[1] == 2 for triplet in errorList):

        return errorList, None

    if not clean:

        errorList.append((f'Configuration file problem with the value: {CLEANUP_UNKNOWN_WORDS}.', 2))
        return errorList, None

    if clean[0].lower() == 'y':

        cleanUpText = True
    else:
        cleanUpText = False

    synFileContents = fixUpText(synFileContents, cleanUpText)

    errorList.append(('Synthesis complete.', 0))

    return errorList, synFileContents

def loadHCSynthDll(dllPath, HCconfigPath, surfaceFormsFile):
    '''Load the .NET 8 HCSynthByGloss.dll in this process and return an HCSynthByGlossDll object that writes surfaceFormsFile, with the HermitCrab config already loaded, as Live Rule Tester's
       setUpHermitCrab() and extractHermitCrabConfig() do. Raises RuntimeError saying what went wrong. See EXE OR DLL above.'''

    dllPath = Path(dllPath).resolve()

    if not dllPath.is_file():

        raise RuntimeError(f"Could not find the HermitCrab synthesis DLL: {dllPath}")

    try:
        import pythonnet

    except ImportError:

        raise RuntimeError("Loading the HermitCrab synthesis DLL needs pythonnet (pip install pythonnet).")

    # Start .NET 8 with the dll's own runtime config, unless this process already has a runtime; only one can be loaded, and it has to be CoreCLR
    runtimeInfo = pythonnet.get_runtime_info()

    if runtimeInfo is None:

        try:
            pythonnet.load("coreclr", runtime_config=str(dllPath.with_suffix(".runtimeconfig.json")))

        except Exception as e:

            raise RuntimeError(f"Could not start .NET 8 for the HermitCrab synthesis DLL. Error: {e}")

    elif runtimeInfo.kind != "CoreCLR":

        raise RuntimeError(f"The HermitCrab synthesis DLL needs .NET 8, but this process already runs {runtimeInfo.kind}.")

    # pythonnet looks for the assemblies the dll depends on in sys.path's folders
    if str(dllPath.parent) not in sys.path:

        sys.path.append(str(dllPath.parent))

    try:
        import clr

        clr.AddReference(str(dllPath))  # type: ignore  # pythonnet adds AddReference to clr at run time, so the checker can't see it
        from SIL.HCSynthByGloss import HCSynthByGlossDll  # type: ignore  # a .NET namespace that pythonnet provides at run time

        DLLobj = HCSynthByGlossDll(str(surfaceFormsFile))

    except Exception as e:

        raise RuntimeError(f"An exception occurred. Could not initialize the HermitCrab synthesis DLL. Error: {e}")

    # Load the HermitCrab config, once for the life of the object
    try:
        ret = DLLobj.SetHcXmlFile(str(HCconfigPath))

    except Exception as e:

        raise RuntimeError(f"An exception happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL) Error: {e}")

    if ret != DLLobj.kSuccess:

        raise RuntimeError(f"An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL) {ret}")

    return DLLobj

class Synthesizer:
    '''A bundle's synthesis data, loaded once, and how to run HCSynthByGloss: the DLL object when hcsynthDll (the path of the .NET 8 HCSynthByGloss.dll) is given, otherwise the hcsynthCommand
       program. synthesize() turns one target Apertium stream into the synthesized text. See the overview above.'''

    def __init__(self, bundleDir, hcsynthCommand=None, workDir=None, hcsynthDll=None):

        bundleDir = Path(bundleDir)
        manifest = json.loads((bundleDir / "manifest.json").read_text(encoding="utf-8"))
        files = manifest["files"].get("synthesis")

        if not files:

            raise RuntimeError(f"The bundle in {bundleDir} has no synthesis data; export it again with export-bundle.")

        synthesisDir = bundleDir / files.get("dir", SYNTHESIS_DIR)
        self.affixFile = str(synthesisDir / files.get("affixGlosses", AFFIX_GLOSS_FILE))
        self.HCconfigPath = str(synthesisDir / files.get("hermitCrabConfig", HERMIT_CRAB_CONFIG_FILE))
        self.convData = ConversionData(synthesisDir / files.get("conversionCache", CONVERSION_CACHE_FILE))
        self.HCcapitalLemmasMap = getCapitalLemmas(self.HCconfigPath)

        config = manifest["config"]
        self.sentPunct = config.get(SENTENCE_PUNCTUATION)
        self.complexForms1st = config.get(TARGET_FORMS_INFLECTION_1ST) or []
        self.complexForms2nd = config.get(TARGET_FORMS_INFLECTION_2ND) or []
        self.clean = config.get(CLEANUP_UNKNOWN_WORDS)
        self.languageCode = manifest.get("interfaceLanguage") or "en"

        self.hcsynthCommand = list(hcsynthCommand or [])
        self.workDir = Path(workDir) if workDir else Path(tempfile.mkdtemp(prefix="ftt_synthesis_"))
        self.workDir.mkdir(parents=True, exist_ok=True)
        self.masterFile = self.workDir / MASTER_FILE
        self.parsesFile = self.workDir / PARSES_FILE
        self.surfaceFormsFile = self.workDir / SURFACE_FORMS_FILE

        # The DLL object, which loads the HermitCrab config now, once; see EXE OR DLL above
        self.DLLobj = loadHCSynthDll(hcsynthDll, self.HCconfigPath, self.surfaceFormsFile) if hcsynthDll else None

        if not self.DLLobj and not self.hcsynthCommand:

            raise RuntimeError("HermitCrab synthesis needs either the HCSynthByGloss command or the path of HCSynthByGloss.dll.")

    def synthesize(self, stream):
        '''Convert Text to Synthesizer Format and Synthesize Text on a target stream (Run Apertium's output). Returns (the synthesized text, or None after an error, and the messages as
           (level, text) pairs).'''

        errorList = convertToHermitCrab(self.convData, self.affixFile, stream, self.masterFile, self.complexForms1st, self.complexForms2nd, self.sentPunct)
        text = None

        if not any(triplet[1] == 2 for triplet in errorList):

            errList, text = synthesizeWithHermitCrab(self.hcsynthCommand, self.languageCode, self.HCconfigPath, self.HCcapitalLemmasMap, self.parsesFile, self.masterFile, self.surfaceFormsFile, stream, self.clean, DLLobj=self.DLLobj)
            errorList.extend(errList)

        return text, [(LEVEL_NAMES.get(code, "error"), message) for message, code in errorList]
