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
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
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

import ReadConfig
import Utils

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   

from collections import defaultdict
from types import *

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Extract Source Text",
        FTM_Version    : "1.7",
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
    
    # We need to also find the TreeTran output file, if not don't do a Tree Tran sort
    if TreeTranSort:
        try:
            f_treeTranResultFile = open(treeTranResultFile)
        except:
            report.Error('There is a problem with the Tree Tran Result File path: '+treeTranResultFile+'. Please check the configuration file setting.')
            return
        
        # get the list of guids from the tree tran results file
        guidIDList = get_guids(f_treeTranResultFile)
            
    # Process the text
    report.Info("Exporting analyses...")

    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
        return

    getSurfaceForm = False
    retObject = Utils.get_interlin_data(DB, report, sent_punct, contents, typesList, getSurfaceForm, TreeTranSort)

    report.Info("Export of " + text_desired_eng + " complete.")
    
    if TreeTranSort:
        for myID in guidIDList:
            if myID not in retObject:
                continue
            else:
                outStr = retObject[myID]
                # Split compound words
                outStr = Utils.split_compounds(outStr)
                f_out.write(outStr.encode('utf-8'))
    else:
        # Write out all the words
        for outStr in retObject:
            # Split compound words
            outStr = Utils.split_compounds(outStr)
            f_out.write(outStr.encode('utf-8'))

    f_out.close()

def get_guids(f_input):
    
    guid_list = {}
    
    return guid_list
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
if __name__ == '__main__':
    FlexToolsModule.Help()
