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
#   Version 2.1.3 - 3/27/20 - Ron Lockwood
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

import sys
import os
import re 
import tempfile
import copy
import xml.etree.ElementTree as ET
from System import Guid
from System import String

import ReadConfig
import Utils

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   

from FTModuleClass import FlexToolsModuleClass
from collections import defaultdict
from types import *
from future.backports.test.pystone import FALSE, TRUE
from __builtin__ import True

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Extract Source Text",
        FTM_Version    : "2.1.3",
        FTM_ModifiesDB: False,
        FTM_Synopsis  : "Extracts an Analyzed FLEx Text into Apertium format.",
        FTM_Help : '',
        FTM_Description :
u"""
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
    #fullPathTextOutputFile = os.path.join(tempfile.gettempdir(), outFileVal)
    fullPathTextOutputFile = outFileVal
    try:
        f_out = open(fullPathTextOutputFile, 'w')
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
    sent_punct = unicode(ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report), "utf-8")
    
    if not sent_punct:
        return
    
    # Check if we are using TreeTran for sorting the text output
    treeTranResultFile = unicode(ReadConfig.getConfigVal(configMap, 'AnalyzedTextTreeTranOutputFile', report), "utf-8")
    
    if not treeTranResultFile:
        TreeTranSort = False
    else:
        TreeTranSort = True
    
    #TreeTranSort = False
    
    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile)
            f_treeTranResultFile.close()
        except:
            report.Error('There is a problem with the Tree Tran Result File path: '+treeTranResultFile+'. Please check the configuration file setting.')
            return
        
        # get the list of guids from the TreeTran results file
        treeSentList = Utils.getTreeSents(treeTranResultFile)
        
        # get log info. that tells us which sentences have a syntax parse and # words per sent
        logInfo = Utils.importGoodParsesLog()
            
    # Process the text
    report.Info("Exporting analyses...")

    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
        return

    # NEW CODE
    myText = Utils.getInterlinData(DB, report, sent_punct, contents, typesList)
        
    #DELETE
    # Get the morphemes from the interlinear text in FLEx
    #getSurfaceForm = False
    #retObject = Utils.get_interlin_data_old(DB, report, sent_punct, contents, typesList, getSurfaceForm, TreeTranSort)

    if TreeTranSort:
        
        #DELETE
        #(guidMap, sentList) = retObject
        
        # create a map of bundle guids to word objects. This gets used when the TreeTran module is used.
        myText.createGuidMaps()
        
        p = 0
        noParseSentCount = 0
        
        # Loop through each sent
        for sentNum, (_, parsed) in enumerate(logInfo):
            
            # If we have a parse for a sentence, TreeTran may have rearranged the words.
            # We need to put them out in the new TreeTran order.
            if parsed == True:
                myTreeSent = treeSentList[p]
                
                # NEW CODE
                myFLExSent = myText.getSent(sentNum)
                isLastSent = myText.isLastSentInParagraph(sentNum)
                
                if myFLExSent is None:
                    report.Error('Sentence ' + str(sentNum) + ' from TreeTran not found')
                    return
                    
                # Output any punctuation preceding the sentence.
                myFLExSent.writePrecedingSentPunc(f_out)
                
                # Loop through each word in the sentence and get the Guids
                for wrdNum in range(0, myTreeSent.getLength()):
                    myGuid = myTreeSent.getNextGuidAndIncrement()
                    
                    if myGuid == None:
                        report.Error('Null Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                        break
                    
                    # NEW CODE
                    # If we couldn't find the guid, see if there's a reason
                    if myFLExSent.haveGuid(myGuid) == False:
                        # Check if the reason we didn't have a guid found is that it got replaced as part of a complex form replacement
                        nextGuid = myTreeSent.getNextGuid()
                        if nextGuid is None or myFLExSent.notPartOfAdjacentComplexForm(myGuid, nextGuid) == True:
                            report.Warning('Could not find the desired Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                    #DELETE
                    #if myGuid not in guidMap:
                    #    report.Warning('Could not find the desired Guid in sentence ' + str(sentNum+1) + ', word ' + str(wrdNum+1))
                    
                    # NEW CODE
                    # We want the punctuation to be at the same points as in the original sentence. This won't always come out right, but maybe close.
                    else:
                        # Write the original word order punctuation.
                        myFLExSent.writePrePunc(wrdNum, f_out)

                        # Write the data that's between the punctuation
                        myFLExSent.writeWordDataForThisGuid(f_out, myGuid)
                        
                        #myFLExSent.writeThisGuid(f_out, myGuid)
                        
                        # Write the original word order punctuation.
                        myFLExSent.writePostPunc(wrdNum, f_out)
                    
                    #DELETE
                    #else:
                        #DELETE
                        #outStr = guidMap[myGuid]
                        
                        # Split compound words
                        #DELETE
                        #outStr = Utils.split_compounds(outStr)
                        #f_out.write(outStr.encode('utf-8'))

                # Output any punctuation at the of the sentence.
                myFLExSent.writeFinalSentPunc(f_out)
                
                if isLastSent:
                    f_out.write('\n')

                p += 1
                
            # No syntax parse from PC-PATR. Put words out in their default order since TreeTran didn't rearrange anything.                        
            else:
                noParseSentCount += 1
                
                # NEW CODE
                # Get the sentence in question
                myFLExSent = myText.getSent(sentNum)
                myFLExSent.write(f_out)
                f_out.write('\n'.encode('utf-8'))
                
                # Get the sentence in question
                #DELETE
                #sent = sentList[sentNum]
                
                # Output each part of the sentence   
                #DELETE 
#                 for i in range(0, len(sent), 2):
#                 
#                     outStr = sent[i]
#                     outStrPunct = sent[i+1]
#                     
#                     # Split compound words
#                     outStr = Utils.split_compounds(outStr)
#                     f_out.write(outStr.encode('utf-8'))
#                     f_out.write(outStrPunct.encode('utf-8'))
#                 #DELETE
#                 f_out.write('\n'.encode('utf-8'))

        report.Info("Exported: " + str(len(logInfo)) + " sentence(s) using TreeTran results.")
        
        if noParseSentCount > 0:
            report.Warning('No parses found for ' + str(noParseSentCount) + ' sentence(s).')

    else:
        # NEW CODE
        # Write out all the words
        myText.write(f_out)
        
        report.Info("Exported: " + str(myText.getSentCount()) + " sentence(s).")
        
        #DELETE
        # retObject is a list
        #for outStr in retObject:
            # Split compound words
            #outStr = Utils.split_compounds(outStr)
            #f_out.write(outStr.encode('utf-8'))

    f_out.close()

    report.Info("Export of " + text_desired_eng + " complete.")
    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
if __name__ == '__main__':
    FlexToolsModule.Help()
