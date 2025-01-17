#
#   GenerateSentences
#
#   Generate sentences based on a model sentence, with some elements set as variables
#   to be iteratively replaced by appropriate items in the dictionary.
#
#
#   21 Nov 2024 bb  v3.10.12  Update use of GetInterlinData for changes in Utils.py at version 3.10.11
#                                               on 3/20/24.  Add analytics.
#
#   15 Feb 2024 bb  v3.8.6  Incorporate parts of ExtractSourceText.py to read from FLEx text
#
#   30 Jun 2023 bb  Get it working as a module in FLExTrans
#
#   13 Jan 2025 dm  adding more functionality (grabbing words from lexicon, settings)
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
    IMoInflAffMsa,
    IMoDerivAffMsa,
)

import ReadConfig
import Utils

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



def MainFunction(DB, report, modifyAllowed):

    # These are words in the Frame Sentence that we want to replace with "all possible values".
    # These variables specify:
    #   - The headword lemma and POS.  (Must match the analysis on the Analyze tab.)
    #   - A variable number of other words that agree with it.
    # Eventually we want to read from the config (settings file), but for now we'll hard code the values
    ## TODO:  Will it match if there are non-ascii chars?  Didn't seem to work for pequeño.
    ## Needs to be investigated.
    # Currently this is hard-coded to work with project Spanish-GenerateSentences, for the Text "Model Text".
    # I was experimenting with different values.

    #lang = "TKW"
    lang = "SPA"

    if lang == "SPA":
        # DM: making the lemma(s) a list instead of individual values
        #    match_n_lem = ["coche1.1"]
        #    match_n_pos = ["n"]
        match_n_lem = ["jugar1.1"]
        match_n_pos = ["v"]
        #    match_1_lem = ["amarillo1.1"]
        match_1_lem = ["rojo1.1"]
        match_1_pos = ["adj"]
        match_2_lem = [""]
        match_2_pos = [""]

    else:
        # For Noun Adj Poss text
        match_n_lem = ["thu1.1"]
        match_n_pos = ["n"]
        #match_1_lem = ["_ng'ono1.1"]
        match_1_lem = ["lubale1.1"]
        match_1_pos = ["adj"]
        match_2_lem = ["aga1.1"]
        match_2_pos = ["poss"]

## For Test 3/4 text in TKW database
#    match_n_lem = "_nddo1.1"
#    match_n_pos = "n"
#    match_1_lem = "_jinji1.1"
#    match_1_pos = "adj"
    


#    # Read the configuration file which we assume is in the current directory.
#    configMap = ReadConfig.readConfig(report)
#    if not configMap:
#        return

#    # Get the values of interest from the config file
#    POSN-LEM = ReadConfig.getConfigVal(configMap, ReadConfig.POSN-LE, report)
#    POSN-CAT = ReadConfig.getConfigVal(configMap, ReadConfig.POSN-CAT, report, giveError=False) # don't give error yet
    
#    # Get the model file name  [BB: I think this is the name of the Model text.  This setting hasn't been created yet.
#    # or maybe we don't need this?]
#    modelFile = ReadConfig.getConfigVal(configMap, ReadConfig.MODEL_FILE, report)

#    if not modelFile:
#
#        errorList.append((f'Configuration file problem with: {ReadConfig.MODEL_FILE}.', 2))
#        return errorList
#------------ end of prelims?

## This code came from another module and it's here to show me how other modules are reading 
# from the Texts area in FLEx.
# I think this is indeed reading from the text, but I have a feeling there is extra stuff here that doesn't need
# to be here, left over from the other module.
# Eventually we want to be able to write the result back into the FLEx project I think.
#------------------From ExtractText.py--------------------------------

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Open the output file
    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not outFileVal:
        return
    fullPathTextOutputFile = outFileVal
    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: '+fullPathTextOutputFile+'. Please check the configuration file setting.')
        return
    
    # DM: inserting data gathered from settings (POS filter, Stem Limit)
    posFocus = ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_POS, report)
    stemLimit= ReadConfig.getConfigVal(configMap, ReadConfig.GEN_STC_LIMIT_STEM_COUNT, report)
    # validation
    if posFocus:
        # last POS is likely empty (from GenerateParses)
        if posFocus[-1] == '':
            posFocus.pop()
        report.Info('  Only collecting templates for these POS: '+str(posFocus))
    else:
        posFocus = []  # Default to an empty list if not provided

    if stemLimit:
        try:
            stemLimit = int(stemLimit)
        except ValueError:
            stemLimit = 10  # Default value if invalid
    else:
        stemLimit = 10  # Default to 10 if not specified
    ##########################################################################

    # Find the desired text in the FLEx project
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceTextName:
        return    
        
    matchingContentsObjList = []
    
    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    if sourceTextName not in sourceTextList:        
        report.Error('The text named: '+sourceTextName+' not found.')
        return
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceTextName)]
    
    # Process the text
    report.Info("Exporting analyses...")

    # Get various bits of data for the get interlinear function
    interlinParams = Utils.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return

    # Get interlinear data. A complex text object is returned.
    myText = Utils.getInterlinData(DB, report, interlinParams)
        
#------------------End of from ExtractText.py--------------------------------        
        
    ## Generate the lists of words that will be cycled through for each of the "words to be replaced"
    ## in the frame sentence.
    # These will be eventually be calculated (found in the lexicon based on criteria), 
    # but for now they are hard coded for testing.
    
    # When we are getting these from the lexicon, we need to bring in not only the lemma, but also
    # the POS and any features that are in that lexical entry.
    # An example of fetching features is in the function getInflectionInfoSymbols in ExtractBilingualLexicon.py
    
    # The words we matched could also be in this list, when it gets calculated from the Lexicon,
    # but I'm excluding them from these lists for now.
    # For the substitution words, eventually it would be nice if the user could specify more than one POS to 
    # include, e.g., adj, AdjMF?  
    # But for now, if they want more than one POS, they need to make another sentence for it.
    
 ## Temporarily hardcoding these lists

    ## For Spanish-GenerateSentences project
    # Noun list
    subListN = []  # For Nouns (or any headword POS you want)
    subList1 = []  # For Adjectives or other POS
    subList2 = []  # For second words or another category

    # Fetch lexical entries from FLEx

    for entry in DB.LexiconAllEntries():
        lex = DB.LexiconGetLexemeForm(entry) or DB.LexiconGetCitationForm(entry)
        pos = 'UNK'
        if lex and entry.SensesOS.Count > 0:
            for s in entry.SensesOS:
                if s.MorphoSyntaxAnalysisRA:
                    if s.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        msa = IMoStemMsa(s.MorphoSyntaxAnalysisRA)
                        if msa.PartOfSpeechRA:
                            pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                            if pos in match_n_pos:  # Filter by target POS
                                subListN.append(lex)
#    if lang == "SPA":
#        #subListN = ["papel1.1", "caramelo1.1", "tren1.1", "pescado1.1", "luz1.1", "perro1.1", "coche1.1"]
#        subListN = ["hablar1.1", "comer1.1", "existir1.1", "venir1.1"]
#    else:
#        subListN = ["sogoleli1.1","thu1.1","hima1.1","mwihiyana1.1","nyakoddo1.1"]
#    report.Info("ListN = ", subListN)

    # In order to apply the rules correctly to do agreement; we need to include all the features from 
    # these lexical entries.  In the hard-coded version, I haven't included those, so anything masculine
    # in a sentence that expects feminine, comes out as "not found" (@caramelo1.1) currently.
    # Adjective list
    for entry in DB.LexiconAllEntries():
        lex = DB.LexiconGetLexemeForm(entry) or DB.LexiconGetCitationForm(entry)
        pos = 'UNK'
        if lex and entry.SensesOS.Count > 0:
            for s in entry.SensesOS:
                if s.MorphoSyntaxAnalysisRA:
                    if s.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        msa = IMoStemMsa(s.MorphoSyntaxAnalysisRA)
                        if msa.PartOfSpeechRA:
                            pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                            if pos in match_1_pos:  # Filter by target POS
                                subList1.append(lex)
#    if lang == "SPA":
#        subList1 = ["bueno1.1", "largo1.1", "verde1.1", "amarillo1.1"]
#        # verde doesn't work right because in the lexicon it is AdjMF instead of adj.  I'm keeping it here
#        # for now just to show what it looks like when a word doesn't match.
#    else:
#        subList1 = ["jinji1.1","ng'ono1.1","lubale1.1","xa1.1"]
    report.Info("List1 = ", subList1)

    # DM: adding sublist2 for the future 
    #subList2 = []
#    if lang == "SPA":
#        subList2 = ["un1.1"]
#    else:
#        subList2 = ["aga1.1","aye1.1","ihu1.1"]

    


#################################################################################
### I was testing with a Takwane database.
### We do want to verify that this works with a Bantu language.
#    ## For Test 3/4 text in Takwane Sentences project:
#    # Words to use for replacing the Noun
#    subListN = ["nddo1.1","thanko1.1","hobo1.1","ziwo1.1","selo1.1"]
#    # Words to use for replacing the first substitutable word
#    subList1 = ["jinji1.1","ng'ono1.1","lubale1.1","xa1.1"]

#################################################################################

    # DM: limiting lists to the limit specified in settings
    subListN = subListN[:stemLimit]
    subList1 = subList1[:stemLimit]
    subList2 = subList2[:stemLimit]
    
    report.Info("ListN = ", subListN)
    report.Info("List1 = ", subList1)

    
    # Practice using TextClasses
    # (I just wanted to see how these functions worked, and prove that I could call them on the FLEx project.)
    stcCount = myText.getSentCount()
    report.Info("Found " + str(stcCount) + " sentences in text")
    # End of practice
    
    # Get the sentence  
    # For now we are getting the first sentence in the specified text.
    # TODO: allow multiple sentences, and cycle through them.
    # Sentence numbers start with 0
    stc = myText.getSent(0)
    wrdCount = stc.getWordCount()
    report.Info("Found " + str(wrdCount) + " words in sentence 1")
    # Build a list from the words in the sentence
    wrdList = stc.getWords()

    # DM: trying a solution to allow for multiple verbs in one sentence 
    #   (this is not robust yet)
    # Initialize empty lists to store indices for each part of speech
    idxN_list = []  # List for head words (n/v)
    idx1_list = []  # List for dependents 1
    idx2_list = []  # List for dependents 2

    # Iterate over words in the sentence
    for idx, w in enumerate(wrdList):
        thisLemma = w.getLemma(0)
        thisPOS = w.getPOS(0)

        # Only process the word if its POS is in the posFocus list
        if thisPOS in posFocus:
            report.Info(f"Checking word: {thisLemma} {thisPOS} at index {idx}")

            # Add indices to the respective lists, ensuring no overwriting
            if thisLemma in match_n_lem and thisPOS in match_n_pos:
                idxN_list.append(idx)  # Store all matched noun indices
                report.Info(f"Matched Noun (hacer or others): {thisLemma} {thisPOS} at idxN {str(idx)}")

            if thisLemma in match_1_lem and thisPOS in match_1_pos:
                idx1_list.append(idx)  # Store all matched adjective indices
                report.Info(f"Matched Adjective: {thisLemma} {thisPOS} at idx1 {str(idx)}")

            if thisLemma in match_2_lem and thisPOS in match_2_pos:
                idx2_list.append(idx)  # Store all matched second word indices
                report.Info(f"Matched Second word: {thisLemma} {thisPOS} at idx2 {str(idx)}")

    # Now perform the substitutions for each of the matched indices

    # Now, perform the substitutions with the limited lists
    for wordNoun in subListN:
        for idxN in idxN_list:
            report.Info(f"  Testing idxN {str(idxN)}")
            report.Info(f"  Testing idxN {str(idxN)} Match {wrdList[idxN]._TextWord__lemmaList[0]} Replace {wordNoun}")
            wrdList[idxN]._TextWord__lemmaList[0] = wordNoun

            # Write sentence for cases with only the Noun substituted
            if not idx1_list:
                stc.write(f_out)
                f_out.write('\n')
            else:
                # Loop for the first substitutable word
                for idx1 in idx1_list:
                    for word1 in subList1:
                        report.Info(f"  Testing idx1 {str(idx1)}  Match {wrdList[idx1]._TextWord__lemmaList[0]} Replace {word1}")
                        wrdList[idx1]._TextWord__lemmaList[0] = word1

                        if not idx2_list:
                            # Write sentence at Level 1
                            stc.write(f_out)
                            f_out.write('\n')
                        else:
                            # Loop for the second substitutable word
                            for idx2 in idx2_list:
                                for word2 in subList2:
                                    report.Info(f"  Testing idx2 {str(idx2)}   Match {wrdList[idx2]._TextWord__lemmaList[0]} Replace {word2}")
                                    wrdList[idx2]._TextWord__lemmaList[0] = word2
                                    # Write out the sentence with the current substitutions
                                    stc.write(f_out)
                                    f_out.write('\n')


    # COMMENTED OUT OLD CODE: 

    # Now set the index for each of the words to substitute
    #idx = 0
    # Initialize to an unlikely number, so we can test if they have been set
    #idxN = idx1 = idx2 = idx3 = idx4 = 99
    # Flag to indicate if the sentence has been written yet
    #did_write = 0

    # Iterate over words in the sentence
    #for w in wrdList:
        #thisLemma = w.getLemma(0)
        #thisPOS = w.getPOS(0)

        # Only process the word if its POS is in the posFocus list
         # Writing output for debugging purposes
        #if thisPOS in posFocus:
            #report.Info(f"This word is {thisLemma} {thisPOS}")

            # Get the info for the Noun (head) word
            #if thisLemma in match_n_lem and thisPOS in match_n_pos:
                #report.Info("Matched N: "  + thisLemma + " " + thisPOS)
                #idxN = idx
                #report.Info(f"Matched N: {wrdList[idxN]._TextWord__lemmaList[0]} {thisPOS} at idxN {str(idxN)}")
                # Debug output to see what the features on this word are
                
                #report.Info("")

            #if thisLemma in match_1_lem and thisPOS in match_1_pos:
                #idx1 = idx
                #report.Info(f"Matched 1: {thisLemma} {thisPOS} at idx1 {str(idx1)}")

                #report.Info("")
            # Get the info for the Second substitutable word
            #if thisLemma in match_2_lem and thisPOS in match_2_pos:
                #idx2 = idx
                #report.Info(f"Matched 2: {thisLemma} {thisPOS} at idx2 {str(idx2)}")
            # Eventually we want to do this for however many substitutable words were specified.
            # How to figure out which ones to do it for or not?
            # The current approach is to initialize idx3 (etc) to 99, so that value will indicate the first one that wasn't 
            # part of the frame. There is code below to stop when it gets to that point.
            # But there are surely other ways.

        # Increment for next loop through the words in the sentence
        #idx += 1

    # Now, perform the substitutions with the limited lists
    #for wordNoun in subListN:
        #report.Info(f"  Testing idxN {str(idxN)}")
        #if idxN != 99:
            #report.Info(f"  Testing idxN {str(idxN)} Match {wrdList[idxN]._TextWord__lemmaList[0]} Replace {wordNoun}")
            #wrdList[idxN]._TextWord__lemmaList[0] = wordNoun

            # Write sentence for cases with only the Noun substituted
            #if idx1 == 99:
                #stc.write(f_out)
                #f_out.write('\n')
            #else:
                # Loop for the first substitutable word
                #for word1 in subList1:
                    #report.Info(f"  Testing idx1 {str(idx1)}  Match {wrdList[idx1]._TextWord__lemmaList[0]} Replace {word1}")
                    #wrdList[idx1]._TextWord__lemmaList[0] = word1

                    #if idx2 == 99:
                        # Write sentence at Level 1
                        #stc.write(f_out)
                        #f_out.write('\n')
                    #else:
                        # Loop for the second substitutable word
                        #for word2 in subList2:
                            #report.Info(f"  Testing idx2 {str(idx2)}   Match {wrdList[idx2]._TextWord__lemmaList[0]} Replace {word2}")
                            #wrdList[idx2]._TextWord__lemmaList[0] = word2
                            # Write out the sentence with the current substitutions
                            #stc.write(f_out)
                            #f_out.write('\n')

    # Iterate through the words to substitute, and put them in the sentence
    # (This is a bit of an abuse, because each word has a GUID.  But the GUID
    # is not being used or output anywhere, so we're just "borrowing" the structure.)
    # Outer loop is for the Noun (head) word
    #for wordNoun in subListN:
        #report.Info("  Testing idxN " + str(idxN))
        #if idxN != 99:
            #report.Info("  Testing idxN " + str(idxN) + " Match " + wrdList[idxN]._TextWord__lemmaList[0] + " Replace " + wordNoun)
            #wrdList[idxN]._TextWord__lemmaList[0] = wordNoun

            # Write sentence for cases with only the Noun substituted
            #if idx1 == 99:
                #stc.write(f_out)
                #f_out.write('\n')

            # Otherwise loop for the First substitutable word
            #else:
                #for word1 in subList1:
                    #report.Info("  Testing idx1 " + str(idx1) + "  Match " + wrdList[idx1]._TextWord__lemmaList[0] + " Replace " + word1)
                    #wrdList[idx1]._TextWord__lemmaList[0] = word1

                    #if idx2 == 99:
                        # Write sentence at Level 1
                        #stc.write(f_out)
                        #f_out.write('\n')
                    # Otherwise loop for the Second substitutable word
                    #else:
                        #for word2 in subList2:
                            #report.Info("  Testing idx2 " + str(idx2) + "   Match " + wrdList[idx2]._TextWord__lemmaList[0] + " Replace " + word2)
                            #wrdList[idx2]._TextWord__lemmaList[0] = word2
                            # Write out the sentence with the current substitutions
                            #stc.write(f_out)
                            #f_out.write('\n')
                    
## The loop above goes as deep as the second substitutable word.  Eventually we want to allow three or four.
## But I wanted to get it working for this much first.

### This was more code from ExtractText.py, from after the text was processed.
###  But I'm writing out one sentence at a time, not the whole text at a time, so I don't think I need this.
###  It would probably be nice to do some reporting though.
###  I'm just using the close part for now.        
#------------------From ExtractText.py--------------------------------

#    if 1:
#        # Write out all the words in Apertium format
#        myText.write(f_out)
#        
#        report.Info("Exported: " + str(myText.getSentCount()) + " sentence(s).")
        
    f_out.close()

    report.Info("Export of " + sourceTextName + " complete.")
    

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



