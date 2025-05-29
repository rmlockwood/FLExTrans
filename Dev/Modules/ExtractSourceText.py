#
#   ExtractSourceText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.14 - 5/16/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13.2 - 3/20/25 - Ron Lockwood
#    Modularized the main function to make it easy to call from other modules.
# 
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.2 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.1 - 9/6/24 - Ron Lockwood
#    Test using mixpanel usage statistics.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.3 - 5/1/24 - Ron Lockwood
#    More checking for None fixes when comparing to a guid.
#
#   Version 3.10.2 - 3/20/24 - Ron Lockwood
#    Refactoring to put changes to allow get interlinear parameter changes to all be in Utils
#
#   Version 3.10.1 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9.1 - 8/17/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names. Removed fallback to use scripture text names.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   earlier version history removed on 3/10/25
#
#   Dump an interlinear text into Apertium format so that it can be
#   used by the Apertium transfer engine.
#

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

import InterlinData
from SIL.LCModel import * # type: ignore
from flextoolslib import *

import Mixpanel
import ReadConfig
import Utils

NGRAM_SIZE = 5

# Define _translate for convenience
_translate = QCoreApplication.translate

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['ExtractSourceText'], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'InterlinData', 'TextClasses'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Extract Source Text",
        FTM_Version    : "3.13.3",
        FTM_ModifiesDB: False,
        FTM_Synopsis   : _translate("ExtractSourceText", "Builds an Apertium-style bilingual lexicon."),
        FTM_Help : '',
        FTM_Description: _translate("ExtractSourceText", 
"""This module will use the Source Text Name set in the Settings. It will first check 
to see if each word in the selected text is
fully analyzed (word gloss or category is not necessary). If the text is not
fully analyzed you will get warnings.
Next, this module will go through each bundle in the interlinear text and export
information in the format that Apertium needs. The general idea is that
affixes and clitics will be exported as <gloss> and root/stems will be exported
as head_word<pos><feat1>...<featN><class1>...<classN>. Where feat1 to featN are one or more 
inflection features that may be present for the root/stem 
and class1 to classN are inflection classes that may be present on the stem.
The exported sentences will be stored in the file specified by the Analyzed Text Output File setting.
This is typically called source_text-aper.txt and is usually in the Build folder.""")}

app.quit()
del app

def punctuationEval(i, treeTranSentObj, myFLExSent, beforeAfterMap, wordGramMap, puncOutputMap, wordsHandledMap):

    wordList = treeTranSentObj.getGuidList()
    numWords = len(wordList)

    # See if we match an n-gram that was reversed in the tree tran sentence
    for j in list(reversed(range(2, NGRAM_SIZE+1))): # start with biggest n-gram and reduce it, because we want to make the biggest match possible

        endPos = i+j-1
        if endPos < numWords:

            if hash(tuple(list(reversed(wordList[i:endPos+1])))) in wordGramMap:

                # Situation 1 current word has punct. and needs to be put somewhere else
                if myFLExSent.hasPunctuation(wordList[i]) == True:

                    # Save this puctuation for output at position i+j-1
                    puncOutputMap[endPos] = wordList[i]

                # Situation 2 current word needs punctuation from a word somewhere else
                if myFLExSent.hasPunctuation(wordList[endPos]) == True and endPos not in wordsHandledMap:

                    # Save this punctuation for output at position i, i.e. current position
                    puncOutputMap[i] = wordList[endPos]

                    # Keep track of words we handled for punctuation, so we don't do them again
                    wordsHandledMap[endPos] = 1

                return False

    # Only process a word that has punctuation
    if myFLExSent.hasPunctuation(wordList[i]) == True:

        # TreeTran first word matches original first word
        if i == 0:

            if myFLExSent.matchesFirstWord(wordList[i]):

                return True # output punctuation for this word

        # If last word
        if i == numWords-1:

            # and matches original last word
            if myFLExSent.matchesLastWord(wordList[i]):

                return True

        # Look to see if the previous and next words are the same as in the original
        #myID = myFLExSent.getWordByGuid(wordList[i]).getID()
        myID = wordList[i]

        # Not first word or last word and this word is in the map
        if i != 0 and i != numWords - 1 and myID in beforeAfterMap:

            # First the simple case, the direct previous and direct following word
            if beforeAfterMap[myID] == (wordList[i-1], wordList[i+1]):

                return True

            # Check a reversed n-gram for the previous word with the direct following word.
            for j in range(2, NGRAM_SIZE+1):

                if i-j > 0:
                    if hash(tuple(list(reversed(wordList[i-j:i])))) in wordGramMap and \
                       beforeAfterMap[myID] == (wordList[i-j], wordList[i+1]):

                        return True

            # Check the direct previous word with a reversed n-gram for the next word
            for j in range(2, NGRAM_SIZE+1):

                if i+j < numWords:
                    if hash(tuple(list(reversed(wordList[i+1:i+j+1])))) in wordGramMap and \
                       beforeAfterMap[myID] == (wordList[i-1], wordList[i+j]):

                        return True

            # Check a reversed n-gram for the previous and a reversed n-gram for the following word
            for j in range(2, NGRAM_SIZE+1):
                for l in range(2, NGRAM_SIZE+1):

                    if i-j > 0 and i+l < numWords:

                        if hash(tuple(list(reversed(wordList[i-j:i])))) in wordGramMap and \
                           hash(tuple(list(reversed(wordList[i+1:i+l+1])))) in wordGramMap and \
                           beforeAfterMap[myID] == (wordList[i-j], wordList[i+l]):

                            return True
    return False

def setUpOrigSentMaps(sentObj, befAftMap, wrdGramMap):
    
    wordObjList = []
    
    fullList = sentObj.getWords()
    
    deleteList = ['را1.1']
    
    # Remove words that are going to be deleted
    for wordObj in fullList:
        
        if wordObj.getLemma(0) not in deleteList:
            
            wordObjList.append(wordObj)
    
    numWords = len(wordObjList)
    
    # set up the before/after map which is a map of the current word to its before and after words
    for i, wordObj in enumerate(wordObjList):
        
        if i > 0 and i < numWords-1: # not first or last

            if wordObjList[i-1].getID() is not None and wordObjList[i+1].getID() is not None:

                befAftMap[wordObj.getID()] = (wordObjList[i-1].getID(), wordObjList[i+1].getID())
            
    # set up the word-gram map which is the current word + 1-n following words. e.g. for abcd: ab, abc, abcd, bc, bcd, cd (if n was 4 or more)
    for i in range(0, numWords-1):
        for j in range(2, NGRAM_SIZE+1):
            
            keyList = []
            if i+j <= numWords:
                
                for k in range(i, i+j):
                    if k < numWords:
                        
                        myID = wordObjList[k].getID()
                        
                        # see if the guid is not None
                        if myID is not None:
                            keyList.append(myID)
                        else:
                            break
                        
                if len(keyList) > 1 and len(str(myID)) > 0:
                    # we can't use a list as the map value, a tuple works, why not make a hash of it
                    wrdGramMap[hash(tuple(keyList))] = 1
                    

def doExtractSourceText(DB, configMap, report):

    # Build an output path using the system temp directory.
    fullPathTextOutputFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not fullPathTextOutputFile:
        return None
    
    abbrPath = Utils.getPathRelativeToWorkProjectsDir(fullPathTextOutputFile)

    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
    except IOError:
        report.Error(_translate("ExtractSourceText", "There is a problem with the Analyzed Text Output File path: {path}. Please check the configuration file setting.").format(path=fullPathTextOutputFile))
        return None
    
    # Find the desired text
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    if not sourceTextName:
        return None
    
    matchingContentsObjList = []

    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    
    if sourceTextName not in sourceTextList:
        
        report.Error(_translate("ExtractSourceText", "The text named: {textName} not found.").format(textName=sourceTextName))
        return None
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceTextName)]
    
    # Check if we are using TreeTran for sorting the text output
    treeTranResultFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, report)
    
    if not treeTranResultFile:
        TreeTranSort = False
    else:
        TreeTranSort = True
    
        # Check if we are using an Insert Words File for TreeTran 
        treeTranInsertWordsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TREETRAN_INSERT_WORDS_FILE, report)
        
        if not treeTranInsertWordsFile:
            insertWordsFile = False
        else:
            insertWordsFile = True
            
            insertWordsList = InterlinData.getInsertedWordsList(treeTranInsertWordsFile, report, DB)
    
            if insertWordsList == None: 
                return None # error already reported
        
    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile)
            f_treeTranResultFile.close()
        except:
            report.Error(_translate("ExtractSourceText", "There is a problem with the Tree Tran Result File path: {path}. Please check the configuration file setting.").format(path=treeTranResultFile))
            return None
        
        # get the list of guids from the TreeTran results file
        treeSentList = InterlinData.getTreeSents(treeTranResultFile, report)
        
        if treeSentList == None: 
            return None # error already reported
        
        # get log info. that tells us which sentences have a syntax parse and # words per sent
        logInfo = Utils.importGoodParsesLog()
            
    # Process the text

    # Get various bits of data for the get interlinear function
    interlinParams = InterlinData.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return None

    # Get interlinear data. A complex text object is returned.
    myText = InterlinData.getInterlinData(DB, report, interlinParams)
        
    if TreeTranSort:
        
        # If we are using an Insert Words file, add the words to the text object
        if insertWordsFile == True:
            myText.addInsertedWordsList(insertWordsList)
        
        # create a map of bundle guids to word objects. This gets used when the TreeTran module is used.
        myText.createGuidMaps()
        
        p = 0
        noParseSentCount = 0
        
        # Loop through each sent
        for sentNum, (_, parsed) in enumerate(logInfo):
            
            # If we have a parse for a sentence, TreeTran may have rearranged the words.
            # We need to put them out in the new TreeTran order.
            if parsed == True and p < len(treeSentList):
                myTreeSent = treeSentList[p]
                
                myFLExSent = myText.getSent(sentNum)
                isLastSent = myText.isLastSentInParagraph(sentNum)
                
                if myFLExSent is None:
                    report.Error(_translate("ExtractSourceText", "Sentence {sentNum} from TreeTran not found").format(sentNum=str(sentNum + 1)))
                    return None
                
                beforeAfterMap = {}
                wordGramMap = {}
                wordsHandledMap = {}
                
                # Set up the maps for the original sentnece
                setUpOrigSentMaps(myFLExSent, beforeAfterMap, wordGramMap)
                    
                # Output any punctuation preceding the sentence.
                _ = myFLExSent.writePrecedingSentPunc(f_out)
                
                puncOutputMap = {}
                
                # Loop through each word in the sentence and get the Guids
                # NB: any <sent> 'words' won't get processed since they are not in the guid list.
                for wrdNum in range(0, myTreeSent.getLength()):
                    myGuid = myTreeSent.getNextGuidAndIncrement()
                    
                    if len(str(myGuid)) == 0:
                        report.Error(_translate("ExtractSourceText", "Null Guid in sentence {sentNum}, word {wordNum}").format(sentNum=str(sentNum + 1), wordNum=str(wrdNum + 1)))
                        break
                    
                    # If we couldn't find the guid, see if there's a reason
                    if myFLExSent.haveGuid(myGuid) == False:
                        # Check if the reason we didn't have a guid found is that it got replaced as part of a complex form replacement
                        nextGuid = myTreeSent.getNextGuid()
                        if nextGuid is None or myFLExSent.notPartOfAdjacentComplexForm(myGuid, nextGuid) == True:
                            report.Warning(_translate("ExtractSourceText", "Could not find the desired Guid in sentence {sentNum}, word {wordNum}").format(sentNum=str(sentNum + 1), wordNum=str(wrdNum + 1)))
                    
                    # We want the punctuation to be at the same points as in the original sentence. This won't always come out right, but maybe close.
                    else:
                        # Write the original word order punctuation.
                        # Use the punctuation words written above as the offset to make sure the guid word is the same as the flex sentence word.
                        #myFLExSent.writePrePunc(wrdNum+puncWrdsWritten, f_out)

                        # See if we should write punctuation for this word or if we should write punctuation for a different word
                        writePunc = punctuationEval(wrdNum, myTreeSent, myFLExSent, beforeAfterMap, wordGramMap, puncOutputMap, wordsHandledMap)
                        
                        if writePunc == True:
                        
                            myFLExSent.writeBeforePunc(f_out, myGuid)
                        
                        # if we are on a word that we saved for outputting punctuation, put out that word's punctuation now
                        elif wrdNum in puncOutputMap:
                            
                            myFLExSent.writeBeforePunc(f_out, puncOutputMap[wrdNum])
                            
                        # Write the data that's between the punctuation
                        myFLExSent.writeWordDataForThisGuid(f_out, myGuid)
                        
                        if writePunc == True:
                            
                            myFLExSent.writeAfterPunc(f_out, myGuid)
                            f_out.write(' ')

                        elif wrdNum in puncOutputMap:
                            
                            myFLExSent.writeAfterPunc(f_out, puncOutputMap[wrdNum])
                            f_out.write(' ')

                        #myFLExSent.writeThisGuid(f_out, myGuid)
                        
                        # Write the original word order punctuation.
                        #myFLExSent.writePostPunc(wrdNum+puncWrdsWritten, f_out)
                    
                # Output any punctuation at the of the sentence.
                myFLExSent.writeFinalSentPunc(f_out)
                f_out.write(' ')
                
                if isLastSent:
                    f_out.write('\n')

                p += 1
                
            # No syntax parse from PC-PATR. Put words out in their default order since TreeTran didn't rearrange anything.                        
            else:
                noParseSentCount += 1
                
                # NEW CODE
                # Get the sentence in question
                myFLExSent = myText.getSent(sentNum)
                
                if myFLExSent == None:
                    
                    report.Error(_translate("ExtractSourceText", "Sentence: {sentNum} not found. Check that the right parses are present.").format(sentNum=str(sentNum + 1)))
                    continue 
                
                myFLExSent.write(f_out)
                
                if myText.isLastSentInParagraph(sentNum):
                    f_out.write('\n')
                
        report.Info(_translate("ExtractSourceText", "Exported: {count} sentence(s) using TreeTran results.").format(count=str(len(logInfo))))
        
        if noParseSentCount > 0:
            report.Warning(_translate("ExtractSourceText", "No parses found for {count} sentence(s).").format(count=str(noParseSentCount)))

    else:
        # Write out all the words
        myText.write(f_out)
        totalStr = str(myText.getSentCount())
        #endstr = 's' if totalStr != '1' else ''
        report.Info(_translate("ExtractSourceText", "Exported {count} sentence(s) to {path}.").format(count=totalStr, path=abbrPath))
        
    f_out.close()

    report.Info(_translate("ExtractSourceText", "Export of {textName} complete.").format(textName=sourceTextName))
    return 1

def MainFunction(DB, report, modifyAllowed):
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + ['ExtractSourceText'], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    doExtractSourceText(DB, configMap, report)


#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
if __name__ == '__main__':
    FlexToolsModule.Help()
