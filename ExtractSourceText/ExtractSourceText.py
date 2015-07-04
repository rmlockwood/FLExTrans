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
#   1.0.1 - 7/4/15 - Ron
#    Dump a possible inflection class present for the root/stem.
#    Changed module description.

import sys
import os
import re 
import tempfile
import copy

import ReadConfig

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Extract Source Text",
        'moduleVersion'    : 1.0.1,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Extracts an Analyzed FLEx Text into Apertium format.",
        'moduleDescription':
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
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import ITextFactory
from SIL.FieldWorks.FDO import IStTextFactory
from SIL.FieldWorks.FDO import IStTxtParaFactory
from SIL.FieldWorks.FDO import IStText
from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr
from SIL.FieldWorks.FDO import IWfiGloss, IWfiWordform, IWfiAnalysis
from SIL.FieldWorks.FDO import ILexEntryRepository
from SIL.FieldWorks.FDO.DomainServices import SegmentServices
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
from collections import defaultdict
from System import Guid
from System import String

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            myList = get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return

def get_component_count(e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            return entryRef.ComponentLexemesRS.Count
        
def get_position_in_component_list(e, complex_e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in complex_e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            # loop through components
            for i, my_e in enumerate(entryRef.ComponentLexemesRS):
                if e == my_e:
                    return i

def GetEntryWithSense(e):
    # If the entry is a variant and it has no senses, loop through its references 
    # until we get to an entry that has a sense
    notDoneWithVariants = True
    while notDoneWithVariants:
        if e.SensesOS.Count == 0:
            if e.EntryRefsOS:
                foundVariant = False
                for entryRef in e.EntryRefsOS:
                    if entryRef.RefType == 0: # we have a variant
                        foundVariant = True
                        break
                if foundVariant and entryRef.ComponentLexemesRS.Count > 0:
                    e = entryRef.ComponentLexemesRS.ToArray()[0]
                    continue
        notDoneWithVariants = False
    return e
       
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
    f_out = open(fullPathTextOutputFile, 'w')

    # Find the desired text
    text_desired_eng = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    if not text_desired_eng:
        return
    
    foundText = False
    for text in DB.ObjectsIn(ITextRepository):
        if text_desired_eng == ITsString(text.Name.BestAnalysisAlternative).Text:
            foundText = True
            break;
        
    if not foundText:
        report.Error('The text named: '+text_desired_eng+' not found.')
        return
    
    # Check to see if everything is analyzed
#    report.Info("Checking for full analysis...")
#    allAnalyzed = True
#    ss = SegmentServices.StTextAnnotationNavigator(text.ContentsOA)
#    for analysisOccurance in ss.GetAnalysisOccurrencesAdvancingInStText():
#        
#        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
#            continue
#        if analysisOccurance.Analysis.ClassName == "WfiGloss":
#            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
#        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
#            wfiAnalysis = analysisOccurance.Analysis
#        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
#            report.Error('No analysis found for the word: '+ITsString(analysisOccurance.Analysis.Form.BestVernacularAlternative).Text)
#            allAnalyzed = False
#            continue
#        else:
#            wfiAnalysis = None
#            
#        if wfiAnalysis.MorphBundlesOS:
#            for bundle in wfiAnalysis.MorphBundlesOS:
#                if not bundle.SenseRA:
#                    report.Error('No sense found for the word: '+ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text)
#                    allAnalyzed = False
#                elif not bundle.MsaRA:
#                    report.Error('No morphosyntactic analysis found for the word: '+ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text)
#                    allAnalyzed = False
#                elif bundle.MsaRA.ClassName == 'MoStemMsa' and not bundle.MsaRA.PartOfSpeechRA:
#                    report.Error('No POS found for the word: '+ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text)
#                    allAnalyzed = False
#            
#        if not wfiAnalysis.MorphBundlesOS or wfiAnalysis.MorphBundlesOS.Count == 0:
#            allAnalyzed = False
#               
#    if not allAnalyzed:
#        report.Error('All of the words have not been analyzed. See errors above.')
#        return
    
    prev_pv_list = []
    prev_e = None
    outputStrList = []
    ccc = 0 # current_complex_component
    
    # Process the text
    report.Info("Exporting analyses...")

    typesList = ReadConfig.getConfigVal(configMap, 'SourceComplexTypes', report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, 'SourceComplexTypes', report):
        return

    prevEndOffset = 0
    
    # count analysis objects
    ss = SegmentServices.StTextAnnotationNavigator(text.ContentsOA)
    for obj_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
        pass
    
    report.ProgressStart(obj_cnt)
    ss = SegmentServices.StTextAnnotationNavigator(text.ContentsOA)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(prog_cnt)
        outStr = affixStr = ''
        
        if prevEndOffset > 0:
            numSpaces = analysisOccurance.GetMyBeginOffsetInPara() - prevEndOffset
            if numSpaces > 0:
                outputStrList.append(' '*numSpaces)
            elif numSpaces < 0: # new paragraph
                outputStrList.append('\n')
        
        prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()
            
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            outputStrList.append(ITsString(analysisOccurance.Analysis.Form).Text)
            continue
        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = analysisOccurance.Analysis
        # We get into this block if there are no analyses for the word or a analysis suggestion hasn't been accepted.
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
            outStr = ITsString(analysisOccurance.Analysis.Form.BestVernacularAlternative).Text
            report.Warning('No analysis found for the word: '+ outStr + ' Treating this is an unknown word.')
            outStr += '<UNK>'
            outputStrList.append('^'+outStr+'$')
            continue
        else:
            wfiAnalysis = None
            
        # Go through each morpheme in the word (i.e. bundle)
        for bundle in wfiAnalysis.MorphBundlesOS:
            if bundle.SenseRA:
                if bundle.MsaRA:
                    # Get the LexEntry object
                    e = bundleEntry = bundle.MorphRA.Owner
                        
                    # For a stem we just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':
                        
                        # Check for valid POS
                        if not bundle.MsaRA.PartOfSpeechRA:
                            outStr = ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text
                            report.Warning('No POS found for the word: '+ outStr + ' Treating this is an unknown word.')
                            outStr += '<UNK>'
                            break
                        if bundle.MorphRA:
                            
                            # Go from variant(s) to entry/variant that has a sense
                            # We are only dealing with senses, so we have to get to one.
                            e = GetEntryWithSense(e)
                            
                            # See if we have an enclitic or proclitic
                            if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in ('proclitic','enclitic'):
                                # Get the clitic gloss. Substitute periods with underscores to make it easier in Apertium.
                                affixStr += '<' + re.sub(r'\.', r'_',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                            
                            # Otherwise we have a root or stem or phrase
                            else:
                                pv_list = []
                                shared_complex_e = None
                                
                                # Check for adjacent words that point to the same complex form
                                # If the form is a phrasal verb use it as the headword to output
                                if e.ComplexFormEntries.Count > 0:
                                    # each word could be part of multiple complex forms (e.g. ra -> char ra, ra raftan
                                    for complex_e in e.ComplexFormEntries:
                                        if complex_e.EntryRefsOS:
                                            # find the complex entry ref (there could be one or more variant entry refs listed along side the complex entry)
                                            for entryRef in complex_e.EntryRefsOS:
                                                if entryRef.RefType == 1: # 1=complex form, 0=variant
                                                    if entryRef.ComplexEntryTypesRS:
                                                        # there could be multiple types assigned to a complex form (e.g. Phrasal Verb, Derivative)
                                                        # just see if one of them is Phrasal Verb
                                                        for complexType in entryRef.ComplexEntryTypesRS:
                                                            if ITsString(complexType.Name.BestAnalysisAlternative).Text in typesList:
                                                                pos_in_list = get_position_in_component_list(e, complex_e)
                                                                # The entry we are on has to be at the right postion in the complex form's component list
                                                                if pos_in_list == ccc:
                                                                    pv_list.append(complex_e)
                                                                    break;
                                    # See if we ended up with any phrasal verbs
                                    if len(pv_list) == 0: # no phrasal verbs
                                        prev_pv_list = []
                                        ccc = 0
                                    else: # yes, we have phrasal verbs
                                        ccc += 1
                                        # First make sure that the entry of the last word isn't the same as this word. In that case, of course there are going to be shared complex forms, but we are only interested in different entries forming a phrasal verb.
                                        # See if the previous word had a link to a complex phrasal verb
                                        if prev_e != e and len(prev_pv_list) > 0:
                                            found = False
                                            # See if there is a match between something on the list for the
                                            # previous word and this word.
                                            for i in range(0, len(prev_pv_list)):
                                                for j in range(0, len(pv_list)):
                                                    if prev_pv_list[i].Guid == pv_list[j].Guid:
                                                        shared_complex_e = pv_list[j]
                                                        found = True
                                                        break
                                                if found:
                                                    break
                                            # If we found a match, we remove the previous word from the output and use the complex form
                                            if found:
                                                component_count = get_component_count(shared_complex_e)
                                                if ccc == component_count:
                                                    ccc = 0
                                                    pv_list = []
                                                    
                                                # remove n/adj/... and it's tag from being output
                                                # need the 2nd pop to get rid of the punctuation or spaces
                                                outputStrList.pop() 
                                                if len(outputStrList) > 0:
                                                    outputStrList.pop() 
                                                
                                        prev_pv_list = copy.copy(pv_list) 
                                        prev_e = e
                                else:
                                    ccc = 0
                                    
                                if shared_complex_e:
                                    
                                    if shared_complex_e.SensesOS:
                                        senseNum = 0 # require only one sense for a complex form
                                        
                                        # Get headword and set homograph # if necessary
                                        headWord = ITsString(shared_complex_e.HeadWord).Text
                                        if not re.search('(\d$)', headWord):
                                            headWord += '1'
                                                                    
                                        outStr += headWord + '.' + str(senseNum+1)
                                        
                                        senseOne = shared_complex_e.SensesOS.ToArray()[0]
                                        
                                        # Get the POS
                                        if senseOne.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                                            outStr += '<' + ITsString(senseOne.MorphoSyntaxAnalysisRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text + '>'
                                        else:
                                            report.Warning("PartOfSpeech object is null.")
                                        
                                        # Get inflection class abbreviation  
                                        if senseOne.MorphoSyntaxAnalysisRA.InflectionClassRA:
                                            outStr += '<'+ITsString(senseOne.MorphoSyntaxAnalysisRA.InflectionClassRA.\
                                                                  Abbreviation.BestAnalysisAlternative).Text+'>'         

                                        # Get any features the stem or root might have
                                        if senseOne.MorphoSyntaxAnalysisRA.MsFeaturesOA:
                                            feat_abbr_list = []
                                            # The features might be complex, make a recursive function call to find all features
                                            get_feat_abbr_list(senseOne.MorphoSyntaxAnalysisRA.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
                                            
                                            # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                            for grpName, abb in sorted(feat_abbr_list, key=lambda x: x[0]):
                                                outStr += '<' + abb + '>'
                                    else:
                                        report.Warning("No senses found for the complex form.")
                                else:
                                    # Go through each sense and identify which sense number we have
                                    foundSense = False
                                    senseNum = 0
                                    for i, mySense in enumerate(e.SensesOS):
                                        if mySense.Guid == bundle.SenseRA.Guid:
                                            foundSense = True
                                            break
                                    if foundSense:
                                        senseNum = i
                                    else:
                                        report.Warning("Couldn't find the sense for headword: "+ITsString(e.HeadWord).Text)    
                                        
                                    # Get headword and set homograph # if necessary
                                    headWord = ITsString(e.HeadWord).Text
                                    if not re.search('(\d$)', headWord):
                                        headWord += '1'
                                    outStr += headWord + '.' + str(senseNum+1)
                                 
                                    # Get the POS
                                    if bundle.MsaRA.PartOfSpeechRA:
                                        outStr += '<' + ITsString(bundle.MsaRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text + '>'
                                    else:
                                        report.Warning("PartOfSpeech object is null.")
                                        
                                    # Get inflection class abbreviation  
                                    if bundle.MsaRA.InflectionClassRA:
                                        outStr += '<'+ITsString(bundle.MsaRA.InflectionClassRA.\
                                                              Abbreviation.BestAnalysisAlternative).Text+'>'         

                                    # Get any features the stem or root might have
                                    if bundle.MsaRA.MsFeaturesOA:
                                        feat_abbr_list = []
                                        # The features might be complex, make a recursive function call to find all features
                                        get_feat_abbr_list(bundle.MsaRA.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
                                        
                                        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                        for grpName, abb in sorted(feat_abbr_list, key=lambda x: x[0]):
                                            outStr += '<' + abb + '>'
                                    
                        else:
                            report.Warning("Morph object is null.")    
                    # We have an affix
                    else:
                        if bundle.SenseRA:
                            # Get the affix gloss. Substitute periods with underscores to make it easier in Apertium.
                            affixStr += '<' + re.sub(r'\.', r'_',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                        else:
                            #e = GetEntryWithSense(e)
                            report.Warning("Sense object for affix is null.")
                else:
                    outStr = ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text
                    report.Warning('No morphosyntactic analysis found for some part of the word: '+ outStr + ' Treating this is an unknown word.')
                    outStr += '<UNK>'
                    break # go on to the next word    
            else:
                # Part of the word has not been tied to a lexical entry-sense
                outStr = ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text
                report.Warning('No sense found for some part of the word: '+ outStr + ' Treating this is an unknown word.')
                outStr += '<UNK>'
                break # go on to the next word    
        outStr += affixStr
        outputStrList.append('^'+outStr+'$')
    
    # Write out all the words
    for outStr in outputStrList:
        f_out.write(outStr.encode('utf-8'))

    report.Info('Export of '+str(obj_cnt+1)+' analyses complete to the file: '+fullPathTextOutputFile+'.')

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
if __name__ == '__main__':
    FlexToolsModule.Help()
