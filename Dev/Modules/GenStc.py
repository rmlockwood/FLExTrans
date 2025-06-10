#
#   GenerateSentences
#
#   Generate sentences based on a model sentence, with some elements set as variables
#   to be iteratively replaced by appropriate items in the dictionary.
#
#   25 Apr 2025 dm re-organized structure. Deleted old methods that weren't being used. 
#
#   28 Mar 2025 dm created GenWord class for encapsulation, very rudementary gloss printing
# 
#   24 Feb 2025 dm GenStc now uses the settings to determine substituable words and grabs words,
#                                           inflection class, and inflection features from lexicon. 
#                                           second dependents can now be substituted. 
# 
#   29 Jan 2025 dm  re-organized code. Added more functionality, made code more modular. 
# 
#   21 Nov 2024 bb  v3.10.12  Update use of GetInterlinData for changes in Utils.py at version 3.10.11
#                                           on 3/20/24.  Add analytics.
#
#   15 Feb 2024 bb  v3.8.6  Incorporate parts of ExtractSourceText.py to read from FLEx text
#
#   30 Jun 2023 bb  Get it working as a module in FLExTrans
#
#   Original version: BB
#    SIL International
#    31 May 2023
#
import re
import os
from datetime import datetime
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
from flextoolslib import *
from flexlibs import FLExProject
from SIL.LCModel import IMoStemMsa
from TextClasses import TextSentence, TextWord
import ReadConfig
import Utils
import InterlinData
import random
import itertools

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {
    FTM_Name: "Generate sentences from model",
    FTM_Version: "3.10.12",
    FTM_ModifiesDB: False,
    FTM_Synopsis: "Iterate over certain POS in a model sentence to produce variations.",
    FTM_Help: "",
    FTM_Description: "Put a better description here."
}
#----------------------------------------------------------------

class GenWord:
    """Represents a word with lemma, POS, gloss, and inflection features."""
    def __init__(self, report):
        self.__lemma = ""
        self.__inflection_features = []
        self.__pos = ""
        self.__gloss = ""
    
    def __repr__(self):
        return f"Word(lemma='{self.__lemma}', pos='{self.__pos}', gloss='{self.__gloss}', inflection_features={self.__inflection_features})"
    
    def __str__(self):
        return f"{self.__lemma} ({self.__pos}): {self.__gloss} | Features: {', '.join(self.__inflection_features)}"
    
    def writeGloss(self, fOut):
        """Write the gloss to the given file object."""
        fOut.write(self.__gloss)

    # Property getters and setters
    @property
    def lemma(self):
        return self.__lemma
    
    @lemma.setter
    def lemma(self, new_lemma):
        self.__lemma = new_lemma
    
    @property
    def inflection_features(self):
        return self.__inflection_features
    
    @inflection_features.setter
    def inflection_features(self, new_features):
        self.__inflection_features = new_features
    
    @property
    def pos(self):
        return self.__pos
    
    @pos.setter
    def pos(self, new_pos):
        self.__pos = new_pos
    
    @property
    def gloss(self):
        return self.__gloss
    
    @gloss.setter
    def gloss(self, new_gloss):
        self.__gloss = new_gloss

#----------------------------------------------------------------
# Configuration and Setup Functions
def loadConfiguration(report):
    """Read and load the configuration file."""
    return ReadConfig.readConfig(report)

def setupSettings(configMap, report):
    """Set up POS focus and stem limits based on configuration."""
    # Get POS settings
    posFocusN = _cleanConfigList(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_N, report))
    posFocus1 = _cleanConfigList(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_1, report))
    posFocus2 = _cleanConfigList(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_2, report))

    # Get Lemma settings and format them
    lemmaFocusN = _formatLemmaSetting(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_N, report))
    lemmaFocus1 = _formatLemmaSetting(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_1, report))
    lemmaFocus2 = _formatLemmaSetting(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_2, report))

    # Get stem limit setting
    stemLimit = _getStemLimit(ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_STEM_COUNT, report))

    return posFocusN, posFocus1, posFocus2, lemmaFocusN, lemmaFocus1, lemmaFocus2, stemLimit

def _cleanConfigList(configList):
    """Remove empty strings from config lists."""
    if configList and configList[-1] == '':
        configList.pop()
    return configList or []

def _formatLemmaSetting(lemmaSetting):
    """Format lemma settings consistently."""
    if not lemmaSetting:
        return "UNK"
    return lemmaSetting if lemmaSetting.endswith("1.1") else f"{lemmaSetting}1.1"

def _getStemLimit(stemLimit):
    """Validate and return stem limit."""
    try:
        return int(stemLimit) if stemLimit else 10
    except ValueError:
        return 10

#----------------------------------------------------------------
# File Handling Functions
def initializeOutputFile(configMap, report, configKey):
    """Initialize an output file for writing."""
    filePath = ReadConfig.getConfigVal(configMap, configKey, report)
    if not filePath:
        return None
    
    try:
        return open(filePath, 'w', encoding='utf-8')
    except IOError:
        report.Error(f'Problem with output file path: {filePath}. Please check configuration.')
        return None

#----------------------------------------------------------------
# Data Extraction Functions
def getSourceText(DB, report, configMap):
    """Fetch the source text from the database."""
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceTextName:
        return None

    matchingContentsObjList = []
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    
    if sourceTextName not in sourceTextList:
        report.Error(f'Text not found: {sourceTextName}')
        return None
        
    return matchingContentsObjList[sourceTextList.index(sourceTextName)]

def extractLanguageVariables(myText, posFocusN, posFocus1, posFocus2, report):
    """Extract lemmas and POS for substituting from the source text."""
    match_n_lem, match_n_pos = [], []
    match_1_lem, match_1_pos = [], []
    match_2_lem, match_2_pos = [], []

    stcCount = myText.getSentCount()
    report.Info(f"Found {stcCount} sentences in the text")

    for i in range(stcCount):
        stc = myText.getSent(i)
        wrdList = stc.getWords()

        for w in wrdList:
            thisLemma = w.getLemma(0)
            thisPOS = w.getPOS(0)

            if thisPOS in posFocusN:
                match_n_lem.append(thisLemma)
                match_n_pos.append(thisPOS)
            elif thisPOS in posFocus1:
                match_1_lem.append(thisLemma)
                match_1_pos.append(thisPOS)
            elif thisPOS in posFocus2:
                match_2_lem.append(thisLemma)
                match_2_pos.append(thisPOS)

    return (list(set(match_n_lem)), list(set(match_n_pos)),
            list(set(match_1_lem)), list(set(match_1_pos)),
            list(set(match_2_lem)), list(set(match_2_pos)))

def extractFromLemmas(myText, lemmaFocusN, lemmaFocus1, lemmaFocus2, report):
    """Extract lemmas from source text based on settings."""
    match_n_lem, match_1_lem, match_2_lem = [], [], []
    stcCount = myText.getSentCount()

    for i in range(stcCount):
        stc = myText.getSent(i)
        for w in stc.getWords():
            thisLemma = w.getLemma(0)
            
            if thisLemma == lemmaFocusN:
                match_n_lem.append(thisLemma)
            elif thisLemma == lemmaFocus1:
                match_1_lem.append(thisLemma)
            elif thisLemma == lemmaFocus2:
                match_2_lem.append(thisLemma)

    return list(set(match_n_lem)), list(set(match_1_lem)), list(set(match_2_lem))

def getLexicalEntries(DB, match_n_pos, match_1_pos, match_2_pos, report):
    """Fetch lexical entries and return lists of GenWord objects."""
    wordListN, wordList1, wordList2 = [], [], []

    for entry in DB.LexiconAllEntries():
        lex = (DB.LexiconGetCitationForm(entry) or DB.LexiconGetLexemeForm(entry)) + '1.1'
        
        if not lex or entry.SensesOS.Count == 0:
            continue
            
        for s in entry.SensesOS:
            if s.MorphoSyntaxAnalysisRA and s.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                msa = IMoStemMsa(s.MorphoSyntaxAnalysisRA)
                if msa.PartOfSpeechRA:
                    pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                    if pos not in match_n_pos + match_1_pos + match_2_pos:
                        continue
                        
                    word = GenWord(report)
                    word.lemma = lex
                    word.inflection_features = Utils.getInflectionTags(msa)
                    word.pos = pos
                    word.gloss = Utils.as_string(s.Gloss)

                    if pos in match_n_pos:
                        wordListN.append(word)
                    elif pos in match_1_pos:
                        wordList1.append(word)
                    elif pos in match_2_pos:
                        wordList2.append(word)

    random.shuffle(wordListN)
    random.shuffle(wordList1)
    random.shuffle(wordList2)
    
    return wordListN, wordList1, wordList2

def getMatchingLemmaWords(match_x_lem, subListX):
    words = []
    for word in subListX:
        if word.lemma in match_x_lem:
            words.append(word)
    return words

def getGlossList(subListX): 
    glosses = []
    for word in subListX: 
        glosses.append(word.gloss())
    return glosses

#----------------------------------------------------------------
# Sentence Processing Functions
def processSentence(wrdList, idxNList, idx1List, idx2List, subListN, subList1, subList2, f_out, stc, report):
    """Process and substitute words in the sentence, writing to output file."""
    for genWordN in subListN:
        _processWord(wrdList, idxNList, genWordN, report)
        
        if not idx1List:
            _writeSentence(stc, f_out)
        else:
            for genWord1 in subList1:
                _processWord(wrdList, idx1List, genWord1, report)
                
                if not idx2List:
                    _writeSentence(stc, f_out)
                else:
                    for genWord2 in subList2:
                        _processWord(wrdList, idx2List, genWord2, report)
                        _writeSentence(stc, f_out)

def _processWord(wrdList, idxList, genWord, report):
    """Process a single word in the sentence."""
    word = genWord.lemma
    info = genWord.inflection_features
    
    for idx in idxList:
        wrd = wrdList[idx]
        report.Info(f"Testing idx {str(idx)} Match {wrd._TextWord__lemmaList[0]} Replace {word}")
        wrd._TextWord__lemmaList[0] = word
        
        if info:
            _applyInflectionFeatures(wrd, info, report)

def _applyInflectionFeatures(wrd, features, report):
    """Apply inflection features to a word."""
    report.Info(f"Before modification: {wrd.getInflClass(0)}")
    report.Info(f"Before modification: {wrd._TextWord__inflFeatAbbrevsList}")

    wrd.setInflClass(str(features[0]))
    wrd.setIgnoreInflectionClass(False)
    wrd.setIgnoreStemFeatures(False)
    wrd.setStemFeatAbbrevList([])
    wrd._TextWord__inflFeatAbbrevsList = [[] for _ in wrd._TextWord__inflFeatAbbrevsList]

    if len(features) > 1:
        for i, feat in enumerate(features[1:]):
            report.Info(f"Assigning feature {feat} at index {i}")
            wrd._TextWord__inflFeatAbbrevsList[i] = [("None", feat)]

    report.Info(f"After modification: {wrd._TextWord__inflFeatAbbrevsList}")

def _writeSentence(stc, f_out):
    """Write the sentence to the output file."""
    stc.write(f_out)
    f_out.write('\n')

def processFreeTranslation(wrdList, idxN_list, idx1_list, idx2_list, subListN, subList1, subList2, f_out2=None, translation, report):
    """
    Iteratively replace target words in the free translation with glosses from the corresponding subLists.
    """
    if not translation:
        return
        
    for genWordN in subListN:
        _processWord(wrdList, idxNList, genWordN, report)
        
        if not idx1List:
            f_out2.write(translation)
            f_out2.write('\n')
        else:
            for genWord1 in subList1:
                _processWord(wrdList, idx1List, genWord1, report)
                
                if not idx2List:
                    f_out2.write(translation)
                    f_out2.write('\n')
                else:
                    for genWord2 in subList2:
                        _processWord(wrdList, idx2List, genWord2, report)
                        f_out2.write(translation)
                        f_out2.write('\n')

#----------------------------------------------------------------
# Main Function
def MainFunction(DB, report, modifyAllowed):
    """Main function that orchestrates the entire process."""
    # Load configuration
    configMap = loadConfiguration(report)
    if not configMap:
        return

    # Initialize settings and files
    posFocusN, posFocus1, posFocus2, lemmaFocusN, lemmaFocus1, lemmaFocus2, stemLimit = setupSettings(configMap, report)
    f_out = initializeOutputFile(configMap, report, ReadConfig.ANALYZED_TEXT_FILE)
    if not f_out:
        return
        
    f_out2 = initializeOutputFile(configMap, report, ReadConfig.GENSTC_ANALYZED_GLOSS_TEXT_FILE)
    translationFile = bool(f_out2)

    # Get source text data
    contents = getSourceText(DB, report, configMap)
    if not contents:
        return

    # Get interlinear data
    interlinParams = InterlinData.initInterlinParams(configMap, report, contents)
    if not interlinParams:
        return
    myText = InterlinData.getInterlinData(DB, report, interlinParams)

    # Extract language variables
    match_n_lem, match_n_pos, match_1_lem, match_1_pos, match_2_lem, match_2_pos = extractLanguageVariables(
        myText, posFocusN, posFocus1, posFocus2, report)

    # Handle lemma focus if specified
    if any(lemma != 'UNK' for lemma in [lemmaFocusN, lemmaFocus1, lemmaFocus2]):
        extracted_n_lem, extracted_1_lem, extracted_2_lem = extractFromLemmas(
            myText, lemmaFocusN, lemmaFocus1, lemmaFocus2, report)
        
        if lemmaFocusN != 'UNK':
            match_n_lem = extracted_n_lem
        if lemmaFocus1 != 'UNK':
            match_1_lem = extracted_1_lem
        if lemmaFocus2 != 'UNK':
            match_2_lem = extracted_2_lem

    # Get lexical entries and apply stem limit
    subListN, subList1, subList2 = getLexicalEntries(DB, match_n_pos, match_1_pos, match_2_pos, report)

    # word search for the matching n, 1, 2 words (find the GenWord w/ gloss)
    genwordsN = getMatchingLemmaWords(match_n_lem, subListN)
    genwords1 = getMatchingLemmaWords(match_1_lem, subList1)
    genwords2 = getMatchingLemmaWords(match_2_lem, subList2)

    matchGlossesN = getGlossList(genwordsN)
    matchGlosses1 = getGlossList(genwords1)
    matchGlosses2 = getGlossList(genwords2)
    
    subListN = subListN[:stemLimit]
    subList1 = subList1[:stemLimit]
    subList2 = subList2[:stemLimit]

    # Process each sentence
    stcCount = myText.getSentCount()
    report.Info(f"Found {stcCount} sentences in the text")

    for i in range(stcCount):
        stc = myText.getSent(i)
        wrdList = stc.getWords()

        # Find indices of words to replace
        idxN_list, idx1_list, idx2_list = [], [], []
        for idx, w in enumerate(wrdList):
            thisLemma = w.getLemma(0)
            thisPOS = w.getPOS(0)

            if thisPOS in posFocusN and thisLemma in match_n_lem:
                idxN_list.append(idx)
            elif thisPOS in posFocus1 and thisLemma in match_1_lem:
                idx1_list.append(idx)
            elif thisPOS in posFocus2 and thisLemma in match_2_lem:
                idx2_list.append(idx)

        free_translation = stc.getFreeTranslation()
        freeT_wrdList = free_translation.split()

        idxFTN_list, idxFT1_list, idxFT2_list = [], [], []
        for idxFT, wFT in enumerate(freeT_wrdList): 
            if wFT in matchGlossesN: 
                idxFTN_list.append(idx)
            elif wFT in matchGlosses1: 
                idxFT1_list.append(idx)
            elif wFT in matchGlosses2: 
                idxFT2_list.append(idx)
        
        processSentence(wrdList, idxN_list, idx1_list, idx2_list, subListN, subList1, subList2, f_out, stc, report)
        processFreeTranslation(freeT_wrdList, idxFTN_list, idxFT1_list, idxFT2_list, subListN, subList1, subList2, f_out2, free_translation, report)

            
    # Clean up
    f_out.close()
    if f_out2:
        f_out2.close()

    report.Info(f"Export of {ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)} complete.")

#----------------------------------------------------------------
# FlexTools Module Setup
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
