#
#   GenerateSentences
#
#   Generate sentences based on a model sentence, with some elements set as variables
#   to be iteratively replaced by appropriate items in the dictionary.
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

from SIL.LCModel import (
    IMoStemMsa,
)

import ReadConfig
import Utils
import random
import itertools

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Generate sentences from model",
        FTM_Version    : "3.10.12",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Iterate over certain POS in a model sentence to produce variations.",
        FTM_Help  : "", 
        FTM_Description:  
"""
Put a better description here.
""" }

def loadConfiguration(report):
    """Reads and loads the configuration file."""
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return None
    return configMap


def setupSettings(configMap, report):
    """Sets up POS focus and stem limits based on the configuration."""
    # this will set up the settings that have been created for GenStc from the settings menu. 

    # grabbing POS settings 
    posFocusN = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_N, report)
    posFocus1 = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_1, report)
    posFocus2 = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS_2, report)

    # grabbing Lemma settings
    lemmaFocusN = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_N, report)
    lemmaFocus1 = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_1, report)
    lemmaFocus2 = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_LEMMA_2, report)

    # grabbing stem limit settings
    stemLimit = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_STEM_COUNT, report)

    # error correct posFocus 
    if posFocusN:
        if posFocusN[-1] == '':
            posFocusN.pop()
        report.Info('  Only collecting templates for these POS: ' + str(posFocusN))
    else:
        posFocusN = []  # Default to an empty list if not provided

    if posFocus1:
        if posFocus1[-1] == '':
            posFocus1.pop()
        report.Info('  Only collecting templates for these POS: ' + str(posFocus1))
    else:
        posFocus1 = []  # Default to an empty list if not provided

    if posFocus2:
        if posFocus2[-1] == '':
            posFocus2.pop()
        report.Info('  Only collecting templates for these POS: ' + str(posFocus2))
    else:
        posFocus2 = []  # Default to an empty list if not provided

    # error correct lemma focus
    lemma_focus_vars = {"lemmaFocusN": lemmaFocusN, "lemmaFocus1": lemmaFocus1, "lemmaFocus2": lemmaFocus2}

    for key in lemma_focus_vars:
        if not lemma_focus_vars[key]:
            lemma_focus_vars[key] = "UNK"
    
        # debug
        #report.Info(f"{key}: {lemma_focus_vars[key]}")
    
        if lemma_focus_vars[key] != "UNK" and not lemma_focus_vars[key].endswith("1.1"):
            lemma_focus_vars[key] += "1.1"
    
        # debug
        #report.Info(f"{key}: {lemma_focus_vars[key]}")

    # Unpack back to original variables if needed
    lemmaFocusN, lemmaFocus1, lemmaFocus2 = lemma_focus_vars.values()

    # error correct stem limit
    if stemLimit:
        try:
            stemLimit = int(stemLimit)
        except ValueError:
            stemLimit = 10  # Default value if invalid
    else:
        stemLimit = 10  # Default to 10 if not specified

    return posFocusN, posFocus1, posFocus2, lemmaFocusN, lemmaFocus1, lemmaFocus2, stemLimit


def initializeOutputFile(configMap, report):
    """Initializes the output file for writing."""
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not outFileVal:
        return None
    fullPathTextOutputFile = outFileVal
    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
        return f_out
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: ' + fullPathTextOutputFile + '. Please check the configuration file setting.')
        return None

def getSourceTextName(report, configMap):
    """Fetches the name of the source text."""
    return ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)

def getSourceText(DB, report, configMap):
    """Fetches the source text from the database."""
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceTextName:
        return None

    matchingContentsObjList = []
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    if sourceTextName not in sourceTextList:
        report.Error('The text named: ' + sourceTextName + ' not found.')
        return None
    return matchingContentsObjList[sourceTextList.index(sourceTextName)]

def initializeLanguageVariables(lang):
    """(OLD) Initializes language-specific variables. (OLD) (UNUSED)"""

    if lang == "SPA":
        match_n_lem = ["hacer1.1", "jugar1.1"]
        match_n_pos = ["v"]
        match_1_lem = ["rojo1.1"]
        match_1_pos = ["adj"]
        match_2_lem = [""]
        match_2_pos = [""]
    elif lang == "HIN":
        match_n_lem = ["machli1.1"]
        match_n_pos = ["n"]
        match_1_lem = ["chota1.1"]
        match_1_pos = ["adj"]
        match_2_lem = [""]
        match_2_pos = [""]
    else: # lang = 'TKW' 
        match_n_lem = ["thu1.1"]
        match_n_pos = ["n"]
        match_1_lem = ["_ng'ono1.1"]
        match_1_pos = ["adj"]
        match_2_lem = ["aga1.1"]
        match_2_pos = ["poss"]
    return match_n_lem, match_n_pos, match_1_lem, match_1_pos, match_2_lem, match_2_pos

def extractLanguageVariables(myText, posFocusN, posFocus1, posFocus2, report):
    """Extract lemmas and POS for substituting from the source text."""
    match_n_lem = []
    match_n_pos = []
    match_1_lem = []
    match_1_pos = []
    match_2_lem = []
    match_2_pos = []

    stcCount = myText.getSentCount()
    report.Info(f"Found {stcCount} sentences in the text")

    for i in range(stcCount):
        stc = myText.getSent(i)  # Get each sentence
        wrdList = stc.getWords()  # Get the list of words in the sentence

        # Collect indices of words that match the specified lemmas and POS
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

    matchLemmaN = list(set(match_n_lem))
    matchLemma1 = list(set(match_1_lem))
    matchLemma2 = list(set(match_2_lem))
    report.Info(f"matching these words (head): ({matchLemmaN})")
    report.Info(f"matching these words (dependent): ({matchLemma1})")
    report.Info(f"matching these words (2nd dependent): {matchLemma2}")

    return matchLemmaN, match_n_pos, matchLemma1, match_1_pos, matchLemma2, match_2_pos

def extractFromLemmas(myText, lemmaFocusN, lemmaFocus1, lemmaFocus2, report):
    """Extract lemmas for substituting from the source text from lemmas entered into settings box."""
    match_n_lem = []
    match_1_lem = []
    match_2_lem = []

    stcCount = myText.getSentCount()
    report.Info(f"Found {stcCount} sentences in the text")

    for i in range(stcCount):
        stc = myText.getSent(i)  # Get each sentence
        wrdList = stc.getWords()  # Get the list of words in the sentence

        # Collect indices of words that match the specified lemmas and POS
        for w in wrdList:
            thisLemma = w.getLemma(0)

            if thisLemma in lemmaFocusN:
                match_n_lem.append(thisLemma)

            elif thisLemma in lemmaFocus1:
                match_1_lem.append(thisLemma)

            elif thisLemma in lemmaFocus2:
                match_2_lem.append(thisLemma)

    matchLemmaN = list(set(match_n_lem))
    matchLemma1 = list(set(match_1_lem))
    matchLemma2 = list(set(match_2_lem))

    return matchLemmaN, matchLemma1, matchLemma2

def getLexicalEntries(DB, match_n_pos, match_1_pos, match_2_pos, report):
    """Fetches lexical entries from the database."""
    # this function grabs all the lexical entries from the database and shuffles them. 
    # the stem limit from the settings is added in the main function. 
    subListN = {}
    subList1 = {}
    subList2 = {}
    glossListN = []
    glossList1 = []
    glossList2 = []

    # need to edit so it grabs inflection features as well. 
    for entry in DB.LexiconAllEntries():
        lex = DB.LexiconGetCitationForm(entry) or DB.LexiconGetLexemeForm(entry)
        lex += '1.1'
        pos = 'UNK'
        if lex and entry.SensesOS.Count > 0:
            for s in entry.SensesOS:
                gloss = s.Gloss
                if s.MorphoSyntaxAnalysisRA:
                    if s.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        msa = IMoStemMsa(s.MorphoSyntaxAnalysisRA)
                        if msa.PartOfSpeechRA:
                            inflectionInfo = Utils.getInflectionTags(msa)
                        
                            pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                            if pos in match_n_pos:
                                subListN[lex] = inflectionInfo
                                glossListN.append(Utils.as_string(gloss))
                            if pos in match_1_pos:
                                subList1[lex] = inflectionInfo
                                glossList1.append(Utils.as_string(gloss))
                            if pos in match_2_pos:
                                subList2[lex] = inflectionInfo
                                glossList2.append(Utils.as_string(gloss))

    lexKeysN = list(subListN.keys())
    lexKeys1 = list(subList1.keys())
    lexKeys2 = list(subList2.keys())

    random.shuffle(lexKeysN)
    random.shuffle(lexKeys1)
    random.shuffle(lexKeys2)

    subDictN = {key:subListN[key] for key in lexKeysN}
    subDict1 = {key:subList1[key] for key in lexKeys1}
    subDict2 = {key:subList2[key] for key in lexKeys2}

    return subDictN, subDict1, subDict2, glossListN, glossList1, glossList2


def processSentence(wrdList, idxNList, idx1List, idx2List, subDictN, subDict1, subDict2, f_out, stc, report):
    """Processes and substitutes words in the sentence, writes them to output file."""
    # unchanged processing algorithm 
    for wordN, infoN in subDictN.items(): # head word 
        for idxN in idxNList:
            report.Info(f"Testing idxN {str(idxN)} Match {wrdList[idxN]._TextWord__lemmaList[0]} Replace {wordN}")
            wrdList[idxN]._TextWord__lemmaList[0] = wordN

            if infoN:
                # checking contents
                report.Info(f"inflection info of {wordN}: {infoN}")

                # pre-adjustment
                report.Info(f"Before modification: {wrdList[idxN].getInflClass(0)}")
                report.Info(f"Before modification: {wrdList[idxN].getStemFeatures(0)}")
                report.Info(f"Before modification: {wrdList[idxN]._TextWord__inflFeatAbbrevsList}")
    
                # changing inflection class
                wrdList[idxN].setInflClass(str(infoN[0]))
                wrdList[idxN].setIgnoreInflectionClass(False)
                wrdList[idxN].setIgnoreStemFeatures(False)
                wrdList[idxN].setStemFeatAbbrevList([])

                # Reset inflection features before assigning new ones
                wrdList[idxN]._TextWord__inflFeatAbbrevsList = [[] for _ in wrdList[idxN]._TextWord__inflFeatAbbrevsList]

                # changing inflection info
                if len(infoN) > 1:
                    for i, feat in enumerate(infoN[1:]):  # Iterate through infoN[1:] directly
                        report.Info(f"Assigning feature {feat} at index {i}")
                        wrdList[idxN]._TextWord__inflFeatAbbrevsList[i] = [("None", feat)]

                    #for i, sublist in enumerate(wrdList[idxN]._TextWord__inflFeatAbbrevsList):
                        #report.Info(f"accessing sublist at index {i}: {sublist}")
                        #wrdList[idxN]._TextWord__inflFeatAbbrevsList[i] = [("None", feat) for feat in infoN[1:]]

                # post-adjustment
                report.Info(f"After modification: {wrdList[idxN].getInflClass(0)}")
                report.Info(f"After modification: {wrdList[idxN].getStemFeatures(0)}")
                report.Info(f"After modification: {wrdList[idxN]._TextWord__inflFeatAbbrevsList}")

            
            if not idx1List:
                stc.write(f_out)
                f_out.write('\n')
            else:
                for idx1 in idx1List: # first dependent 
                    for word1, info1 in subDict1.items():
                        report.Info(f"Testing idx1 {str(idx1)}  Match {wrdList[idx1]._TextWord__lemmaList[0]} Replace {word1}")
                        wrdList[idx1]._TextWord__lemmaList[0] = word1

                        if info1:
                            # pre-adjustment
                            report.Info(f"Before modification: {wrdList[idx1].getInflClass(0)}")
                            report.Info(f"Before modification: {wrdList[idx1]._TextWord__inflFeatAbbrevsList}")

                            # changing inflection class
                            wrdList[idx1].setInflClass(str(info1[0]))
                            wrdList[idx1].setIgnoreInflectionClass(False)
                            wrdList[idx1].setIgnoreStemFeatures(False)
                            wrdList[idx1].setStemFeatAbbrevList([])

                            # Reset inflection features before assigning new ones
                            wrdList[idx1]._TextWord__inflFeatAbbrevsList = [[] for _ in wrdList[idx1]._TextWord__inflFeatAbbrevsList]

                            if len(info1) > 1:
                                for i, feat in enumerate(info1[1:]):  # Iterate through infoN[1:] directly
                                    report.Info(f"Assigning feature {feat} at index {i}")
                                    wrdList[idx1]._TextWord__inflFeatAbbrevsList[i] = [("None", feat)]

                            # post-adjustment
                            report.Info(f"After modification: {wrdList[idx1]._TextWord__inflFeatAbbrevsList}")


                        if not idx2List:
                            stc.write(f_out)
                            f_out.write('\n')
                        else:
                            for idx2 in idx2List: # second dependent
                                for word2, info2 in subDict2.items():
                                    report.Info(f"Testing idx2 {str(idx2)}   Match {wrdList[idx2]._TextWord__lemmaList[0]} Replace {word2}")
                                    wrdList[idx2]._TextWord__lemmaList[0] = word2

                                    if info2:
                                        # pre-adjustment
                                        report.Info(f"Before modification: {wrdList[idx2].getInflClass(0)}")
                                        report.Info(f"Before modification: {wrdList[idx2]._TextWord__inflFeatAbbrevsList}")

                                        # changing inflection class
                                        wrdList[idx2].setInflClass(str(info2[0]))
                                        wrdList[idx2].setIgnoreInflectionClass(False)
                                        wrdList[idx2].setIgnoreStemFeatures(False)
                                        wrdList[idx2].setStemFeatAbbrevList([])

                                        # Reset inflection features before assigning new ones
                                        wrdList[idx2]._TextWord__inflFeatAbbrevsList = [[] for _ in wrdList[idx2]._TextWord__inflFeatAbbrevsList]

                                        if len(info2) > 1:
                                            for i, feat in enumerate(info2[1:]):  # Iterate through infoN[1:] directly
                                                report.Info(f"Assigning feature {feat} at index {i}")
                                                wrdList[idx2]._TextWord__inflFeatAbbrevsList[i] = [("None", feat)]

                                        # post-adjustment
                                        report.Info(f"After modification: {wrdList[idx2]._TextWord__inflFeatAbbrevsList}")

                                    stc.write(f_out)
                                    f_out.write('\n')


def MainFunction(DB, report, modifyAllowed):

    configMap = loadConfiguration(report)
    if not configMap:
        return

    # Set up POS filter and stem limit (settings could change later)
    posFocusN, posFocus1, posFocus2, lemmaFocusN, lemmaFocus1, lemmaFocus2, stemLimit = setupSettings(configMap, report)

    f_out = initializeOutputFile(configMap, report)
    if not f_out:
        return

    contents = getSourceText(DB, report, configMap)
    if not contents:
        return


    # Get interlinear data
    interlinParams = Utils.initInterlinParams(configMap, report, contents)
    if interlinParams is None:
        return
    myText = Utils.getInterlinData(DB, report, interlinParams)

    # Initialize language-specific variables

    # OLD CODE USING initializeLanguageVariables
    #lang = "SPA"
    #match_n_lem, match_n_pos, match_1_lem, match_1_pos, match_2_lem, match_2_pos = initializeLanguageVariables(lang)
    
    # Extracting language variables from settings 
    match_n_lem, match_n_pos, match_1_lem, match_1_pos, match_2_lem, match_2_pos = extractLanguageVariables(myText, posFocusN, posFocus1, posFocus2, report)

    # If at least one lemma is provided, run extractFromLemmas
    if lemmaFocusN != 'UNK' or lemmaFocus1 != 'UNK' or lemmaFocus2 != 'UNK':
        extracted_n_lem, extracted_1_lem, extracted_2_lem = extractFromLemmas(myText, lemmaFocusN, lemmaFocus1, lemmaFocus2, report)
    
        # Replace only the lists where a lemma was actually provided
        if lemmaFocusN != 'UNK':
            match_n_lem = extracted_n_lem
        if lemmaFocus1 != 'UNK':
            match_1_lem = extracted_1_lem
        if lemmaFocus2 != 'UNK':
            match_2_lem = extracted_2_lem

    # Fetch lexical entries from FLEx
    subDictN, subDict1, subDict2, glossListN, glossList1, glossList2 = getLexicalEntries(DB, match_n_pos, match_1_pos, match_2_pos, report)

    report.Info(f"gloss list N: {glossListN}")
    report.Info(f"gloss list N: {glossList1}")
    report.Info(f"gloss list N: {glossList2}")

    # Apply stem limit
    subDictN = dict(itertools.islice(subDictN.items(), stemLimit))
    subDict1 = dict(itertools.islice(subDict1.items(), stemLimit))
    subDict2 = dict(itertools.islice(subDict2.items(), stemLimit))

    stcCount = myText.getSentCount()
    report.Info(f"Found {stcCount} sentences in the text")

    for i in range(stcCount):
        stc = myText.getSent(i)  # Get each sentence
        wrdList = stc.getWords()  # Get the list of words in the sentence

        # Initialize POS index lists for this sentence
        idxN_list, idx1_list, idx2_list = [], [], []

        # Collect indices of words that match the specified lemmas and POS
        for idx, w in enumerate(wrdList):
            thisLemma = w.getLemma(0)
            thisPOS = w.getPOS(0)

            if thisPOS in posFocusN or posFocus1 or posFocus2:
                if thisLemma in match_n_lem and thisPOS in match_n_pos:
                    idxN_list.append(idx)
                if thisLemma in match_1_lem and thisPOS in match_1_pos:
                    idx1_list.append(idx)
                if thisLemma in match_2_lem and thisPOS in match_2_pos:
                    idx2_list.append(idx)

        # Process and substitute words in the current sentence
        processSentence(wrdList, idxN_list, idx1_list, idx2_list, subDictN, subDict1, subDict2, f_out, stc, report)

    f_out.close()

    report.Info("Export of " + getSourceTextName(report, configMap) + " complete.")
    

###  This is how other modules run their process and generate error messages.
###  I don't have this part working yet.    
 ###-----------Run the process?
    #errorList = genStc(DB, configMap, targetGENFile, modelFile, report)

#    # output info, warnings, errors and url links
#    Utils.processErrorList(errorList, report)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()



