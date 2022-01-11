#
#   ExtractSourceText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Dump an interlinear text into Apertium format so that it can be
#   used by the Apertium transfer engine.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2.4 - 7/1/21 - Ron Lockwood
#    Add 1 to sent# for reporting not found sentences.
#
#   Version 3.2.3 - 7/1/21 - Ron Lockwood
#    Fixed bugs with punctuation algorithm. Initialize maps properly. Output the
#    preceding punctuation of a sentence. Moved punctuation_eval() to Utils
#    Put out a space after writing 'after' and 'final' punctuation. 
#    When a sentence doesn't have parsing don't automatically put out a newline.
#    Only do it when it is the last sentence of the paragraph.
#    Omit 'ra' when building punctuation maps.
#
#   Version 3.2.2 - 5/12/21 - Ron Lockwood
#    Only look for TreeTranInsertWordsFile in the config file if we are looking
#    already for a TreeTran output file.
#
#   Version 3.2.1 - 3/8/21 - Ron Lockwood
#    Error checking for missing guid in XML files
#
#   Version 3.2 - 3/4/21 - Ron Lockwood
#    Support for discontiguous complex forms
#
#   Version 3.1 - 2/25/21 - Ron Lockwood
#    Support an insert word list file for extraction purposes. Get new item:
#    TreeTranInsertWordsFile from the config file. call getInsertedWordsList
#    and addInseredWordsList. Bug fix: check if we get None for the sent. object
#    for the number given. Give an error if needed.
#
#   Version 3.0 - 1/26/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.1.4 - 7/29/20 - Ron Lockwood
#    Use an offset when writing punctuation in TreeTran case.
#    
#   Version 2.1.3 - 7/29/20 - Ron Lockwood
#    Write the punctuation of the words in their normal order when doing TreeTran.
#    This avoids punctuation staying with words that change their order.
#    
#   Version 2.1.2 - 3/27/20 - Ron Lockwood
#    Handle adding sentence punctuation when using TreeTran.
#    
#   Version 2.1.1 - 3/26/20 - Ron Lockwood
#    Moved TreeTran-related class and function to the Utils file.
#
#   Version 2.1 - 3/20/20 - Ron Lockwood
#    Use new getInterlinData function and text and sentence objects we get back.
#
#   Version 2.0.4 - 2/12/20 - Ron Lockwood
#    Don't use sentence number as part of the guid map key.
# 
#   Version 2.0.3 - 2/4/20 - Ron Lockwood
#    Only a tuple of two now coming back from get_interlin.
# 
#   Version 2.0.2 - 1/29/20 - Ron Lockwood
#    Write a newline after a sentence that didn't have a parse. Also put out a 
#    warning with the # of unparsed sentences.
# 
#   Version 2.0.1 - 1/22/20 - Ron Lockwood
#    Use a sentence list from the get_interlinear function to use when there is not
#    a parse available from TreeTran. This fixes the problem where a phrasal verb
#    was reducing the word count and causing the non-parsed sentence to be off by
#    one.
# 
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.3.9 - 1/10/18 - Ron Lockwood
#    Moved the split_compounds function into the Utils file for use by
#    other modules.
#
#   Version 1.3.8 - 12/26/17 - Ron
#    Report the name of the extracted text.
#
#   Version 1.3.7 - 5/3/17 - Ron
#    Convert punctuation string to unicode
#
#   Version 1.3.6 - 12/12/16 - Ron
#    Simpler extraction of Scripture text title.
#
#   Version 1.3.5 - 11/9/16 - Ron
#    If a text name is not found, check to see if it matches a scripture section.
#
#   Version 1.3.4 - 9/28/16 - Ron
#    Moved main extraction code into Utils.py to be shared with 
#    LiveRuleTesterTool.py
#
#   Version 1.3.3 - 6/18/16 - Ron
#    Handle variants of senses.
#
#   Version 1.3.2 - 5/9/16 - Ron
#    Make sure bundle.MorphRA is not null. This can happen when a lexical
#    item gets updated in the lexicon and it leaves no lexical entry link there
#    are *** instead. The sense information might still be there.
#
#   Version 1.3.1 - 4/15/16 - Ron
#    No changes to this module.
#
#   Version 1.2.1 - 2/11/16 - Ron
#    Error checking when opening the analyzed text file.
#
#   Version 1.2.0 - 1/28/16 - Ron
#    Punctuation support. Allow the user to specify the punctuation that 
#    indicates the end of a sentence. This punctuation will get marked
#    with the tag <sent>. The user specifies it in the configuration file.
#    Compound word support. Change one lexical unit containing multiple words
#    to multiple lexical units, one for each word. For example: 
#    ^room1.1<n>service1.1<n>number1.1<n>$ ->
#    ^room1.1<n>$^service1.1<n>$^number1.1<n>$ 
#
#   Version 4 - 7/24/15 - Ron
#    Preserve case in words. 
#    Do capitalization of the extracted word. Use the baseline word as a model
#    for how to capitalize it. For the complex form case, save the 1st base-
#    line word for a model of the whole complex form. Removed large commented
#    section of code that was for checking if the whole text had been analyzed.
#
#   Version 3 - 7/16/15 - Ron
#    Handle irregularly inflected forms. Do this by collecting inflection 
#    features when moving through variants to get to a main entry. Output those
#    saved inflection features as tags. 
#    Handle morphology on initial component(s) of complex forms. Save any tags
#    that are present on the initial component(s) and add them to the complex
#    form as morphology.
#
#   Version 2 - 7/4/15 - Ron
#    Dump a possible inflection class present for the root/stem.
#    Changed module description.
#

from System import Guid
from System import String

import ReadConfig
import Utils
import copy

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   
from FTModuleClass import FlexToolsModuleClass
from collections import defaultdict

NGRAM_SIZE = 5

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Extract Source Text",
        FTM_Version    : "3.3",
        FTM_ModifiesDB: False,
        FTM_Synopsis  : "Extracts an Analyzed FLEx Text into Apertium format.",
        FTM_Help : '',
        FTM_Description :
"""
The source database should be chosen for this module. This module will first check 
to see if each word in the selected text is
fully analyzed (word gloss or category is not necessary). If the text is not
fully analyzed an error will be generated.
Next, this module will go through each bundle in the interlinear text and export
information in the format that Apertium needs. The general idea is that
affixes and clitics will be exported as <gloss> and root/stems will be exported
as head_word<pos><feat1>...<featN><class>. Where feat1 to featN are one or more 
inflection features that may be present for the root/stem 
and class is an inflection class that may be present on the stem.
This Module assumes the file FlexTrans.config is in the FlexTools folder.
""" }

#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modifyAllowed):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, 'AnalyzedTextOutputFile', report)
    if not outFileVal:
        return
    
    fullPathTextOutputFile = outFileVal
    
    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: '+fullPathTextOutputFile+'. Please check the configuration file setting.')
        return
    
    # Find the desired text
    text_desired_eng = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    if not text_desired_eng:
        return
    
    foundText = False
    for text in DB.ObjectsIn(ITextRepository):
        if text_desired_eng == ITsString(text.Name.BestAnalysisAlternative).Text:
            foundText = True
            contents = text.ContentsOA
            break;
        
    if not foundText:
        
        # check if it's scripture text
        for section in DB.ObjectsIn(IScrSectionRepository):
            if text_desired_eng == ITsString(section.ContentOA.Title.BestAnalysisAlternative).Text:
                contents = section.ContentOA
                foundText = True
                break
                
        # Pattern not found
        if not foundText:
            report.Error('The text named: '+text_desired_eng+' not found.')
            return
    
    # Get punctuation string
    sent_punct = ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report)
    
    if not sent_punct:
        return
    
    # Check if we are using TreeTran for sorting the text output
    treeTranResultFile = ReadConfig.getConfigVal(configMap, 'AnalyzedTextTreeTranOutputFile', report)
    
    if not treeTranResultFile:
        TreeTranSort = False
    else:
        TreeTranSort = True
    
        # Check if we are using an Insert Words File for TreeTran 
        treeTranInsertWordsFile = ReadConfig.getConfigVal(configMap, 'TreeTranInsertWordsFile', report)
        
        if not treeTranInsertWordsFile:
            insertWordsFile = False
        else:
            insertWordsFile = True
            
            insertWordsList = Utils.getInsertedWordsList(treeTranInsertWordsFile, report, DB)
    
            if insertWordsList == None: 
                return # error already reported
        
    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile)
            f_treeTranResultFile.close()
        except:
            report.Error('There is a problem with the Tree Tran Result File path: '+treeTranResultFile+'. Please check the configuration file setting.')
            return
        
        # get the list of guids from the TreeTran results file
        treeSentList = Utils.getTreeSents(treeTranResultFile, report)
        
        if treeSentList == None: 
            return # error already reported
        
        # get log info. that tells us which sentences have a syntax parse and # words per sent
        logInfo = Utils.importGoodParsesLog()
            
    # Process the text
    report.Info("Exporting analyses...")

    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
        return

    discontigTypesList = ReadConfig.getConfigVal(configMap, 'SourceDiscontigousComplexTypes', report)
    if not discontigTypesList:
        discontigTypesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceDiscontigousComplexTypes', report):
        return

    discontigPOSList = ReadConfig.getConfigVal(configMap, 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories', report)
    if not discontigPOSList:
        discontigPOSList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories', report):
        return

    # Get interlinear data. A complex text object is returned.
    myText = Utils.getInterlinData(DB, report, sent_punct, contents, typesList, discontigTypesList, discontigPOSList)
        
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
                    report.Error('Sentence ' + str(sentNum+1) + ' from TreeTran not found')
                    return
                
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
                    
                    if myGuid == None:
                        report.Error('Null Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                        break
                    
                    # If we couldn't find the guid, see if there's a reason
                    if myFLExSent.haveGuid(myGuid) == False:
                        # Check if the reason we didn't have a guid found is that it got replaced as part of a complex form replacement
                        nextGuid = myTreeSent.getNextGuid()
                        if nextGuid is None or myFLExSent.notPartOfAdjacentComplexForm(myGuid, nextGuid) == True:
                            report.Warning('Could not find the desired Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                    
                    # We want the punctuation to be at the same points as in the original sentence. This won't always come out right, but maybe close.
                    else:
                        # Write the original word order punctuation.
                        # Use the punctuation words written above as the offset to make sure the guid word is the same as the flex sentence word.
                        #myFLExSent.writePrePunc(wrdNum+puncWrdsWritten, f_out)

                        # See if we should write punctuation for this word or if we should write punctuation for a different word
                        writePunc = Utils.punctuation_eval(wrdNum, myTreeSent, myFLExSent, beforeAfterMap, wordGramMap, puncOutputMap, wordsHandledMap)
                        
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
                    
                    report.Error('Sentence: ' + str(sentNum+1) + ' not found. Check that the right parses are present.')
                    continue 
                
                myFLExSent.write(f_out)
                
                if myText.isLastSentInParagraph(sentNum):
                    f_out.write('\n')
                
        report.Info("Exported: " + str(len(logInfo)) + " sentence(s) using TreeTran results.")
        
        if noParseSentCount > 0:
            report.Warning('No parses found for ' + str(noParseSentCount) + ' sentence(s).')

    else:
        # Write out all the words
        myText.write(f_out)
        
        report.Info("Exported: " + str(myText.getSentCount()) + " sentence(s).")
        
    f_out.close()

    report.Info("Export of " + text_desired_eng + " complete.")

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
            befAftMap[wordObj.getID()] = (wordObjList[i-1].getID(), wordObjList[i+1].getID())
            
    # set up the word-gram map which is the current word + 1-n following words. e.g. for abcd: ab, abc, abcd, bc, bcd, cd (if n was 4 or more)
    for i in range(0, numWords-1):
        for j in range(2, NGRAM_SIZE+1):
            
            keyList = []
            if i+j <= numWords:
                
                for k in range(i, i+j):
                    if k < numWords:
                        
                        myID = wordObjList[k].getID()
                        
                        if myID != None:
                            keyList.append(myID)
                        else:
                            break
                        
                if len(keyList) > 1 and myID != None:
                    # we can't use a list as the map value, a tuple works, why not make a hash of it
                    wrdGramMap[hash(tuple(keyList))] = 1
                    

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
if __name__ == '__main__':
    FlexToolsModule.Help()
