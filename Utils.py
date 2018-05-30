#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.1.5 - 1/10/18 - Ron Lockwood
#    Put run_makefile in this file so that both RunApertium and LiveRuleTesterTool
#    can use it. Put split_compounds in this file so that ExtractSourceText and 
#    LiveRuleTesterTool can use it.
#
#   Version 1.1.4 - 1/1/18 - Ron
#    Put process_lexical_unit and associated functions in this file so that
#    both ViewSrcTgt and LiveRuleTesterTool can use it.
#
#   Version 1.1.3 - 12/26/17 - Ron
#    Suppress warnings for standard format markers (e.g. \s) and some special
#    Combinations of a sfm and following text. Also suppress warnings when the
#    same unknown word occurs more than once, but give a warning that an
#    unknown word occurred multiple times.
#
#   Version 1.1.2 - 1/18/17 - Ron
#    Scripture text fixes. Surface forms had empty lines. Prevented this.
#    Changed some comments.
#
#   Version 1.1.1 - 11/9/16 - Ron
#    Handle any kind of text contents coming in -- scripture or standard.
#    Handle no analyses in a text.
#
#   Version 1.1 - 9/28/16 - Ron
#    Moved main extraction code from ExtractSourceText here to be shared with 
#    LiveRuleTesterTool.py
#
#   Shared functions

import re
import copy
import tempfile
import os
import xml.etree.ElementTree as ET
import platform
import subprocess

from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO.DomainServices import SegmentServices

# Main color of the headwords
LEMMA_COLOR = '000000' #black
# For grammatical category - always the 1st symbol
GRAM_CAT_COLOR = '0070C0' #blue
# The color of affixes or other things such as features, classes, etc.
AFFIX_COLOR = '00B050' #green
# The color of non-sentence punctuation. Sentence punctuation will be in its
# own lexical item with <sent> as the category
PUNC_COLOR = 'FFC000' #orange
# Lemmas that have cat: UNK
UNKNOWN_LEMMA_COLOR = 'CC0066' #dark pink
# The color of UNK
UNKNOWN_CAT_COLOR = 'FF99FF' #pink
# The color of a target lemma that is not found (when an @ is there)
NOT_FOUND_COLOR = 'FF0000' #red
# The size of the subscript numbers in %. E.g. 50 means the subscripts will be 
# 50% as big as it normally would be (which is already smaller than normal text)
SUBSCRIPT_SIZE_PERCENTAGE = '60'

# File and folder names
OUTPUT_FOLDER = 'Output'
TESTBED_FILE_PATH = OUTPUT_FOLDER + '\\testbed.xml'
TESTBED_LOG_FILE_PATH = OUTPUT_FOLDER + '\\testbed_log.xml'

# Run the makefile to run Apertium tools to do the transfer
# component of FLExTrans. The makefile is run by invoking a
# bash file. Absolute paths seem to be necessary.
# relPathToBashFile is expected to be with Windows backslashes
def run_makefile(relPathToBashFile):
    
    # Change path to bash based on the architecture
    is32bit = (platform.architecture()[0] == '32bit')
    system32 = os.path.join(os.environ['SystemRoot'],
                            'SysNative' if is32bit else 'System32')
    bash = os.path.join(system32, 'bash.exe')

    # Get the current working directory
    cwd = os.getcwd()
    cwd = re.sub(r'\\','/',cwd) # change to forward slashes
    (drive, tail) = os.path.splitdrive(cwd) # split off drive letter
    drive = re.sub(':','',drive) # remove colon
    unixRelPath = re.sub(r'\\','/',relPathToBashFile) # change to forward slashes
    dir_path = "/mnt/"+drive.lower()+tail+"/"+unixRelPath
    full_path = "'"+dir_path+"/do_make_direct.sh'"
    
    # Create the bash file which merely cds to the appropriate 
    # directory and runs make. Open as a binary file so that
    # we get unix line feeds not windows carriage return line feeds
    f = open(relPathToBashFile+'\\do_make_direct.sh', 'wb')
    f.write('#!/bin/sh\n')
    f.write('cd '+"'"+dir_path+"'"+'\n')
    f.write('make 2>err_out\n')
    #f.write('# '+full_path)
    f.close()
    
    cmd = [bash, '-c', full_path]
    #return subprocess.call(cmd)
    return 0

# Create a span element and set the color and text
def output_span(parent, color, text_str, rtl):
    
    span = ET.Element('span')
    parent.append(span)
    span.attrib['style'] = 'color:#' + color
    
    # Check for RTL
    if rtl == True:
        # prepend the RTL marker
        text_str = ur'\u200F'+text_str
        
    span.text = text_str
    
    return span

def add_subscript(span, num):
    
    sub = ET.Element('sub')
    sub.attrib['style'] = 'font-size:' + SUBSCRIPT_SIZE_PERCENTAGE + '%'
    span.append(sub)
    sub.text = num
        
def process_lexical_unit(lu_str, parent_element, rtl, show_unk):
    # Split off the symbols from the lemma in the lexical unit (which is i+1)
    symbols = re.split('<|>', lu_str)
    symbols = filter(None, symbols) # filter out the empty strings
    
    # Lemma is the first one
    lemma = symbols.pop(0)
    
    # Split off the homograph_num.sense_num (if present; sent punctuation won't have it)
    lemma_parts = re.split('(\d+\.\d+)', lemma) # last item is empty
    
    # Check for an @
    if lemma_parts[0][0] == '@':
        # color it red for not found
        lexeme_color = NOT_FOUND_COLOR
        
        # remove the @
        lemma_parts[0] = lemma_parts[0][1:]
        
    # if the first symbol is UNK, use a special lemma color
    elif symbols[0] == 'UNK':
        lexeme_color = UNKNOWN_LEMMA_COLOR
    else:
        lexeme_color = LEMMA_COLOR
    
    # Output the lexeme
    span = output_span(parent_element, lexeme_color, lemma_parts[0], rtl)
    
    # Output the subscript
    if len(lemma_parts) > 1:
        add_subscript(span, lemma_parts[1])
    
    # Loop through the symbols
    for i, symb in enumerate(symbols):
        # Check for unknown category
        if symb == 'UNK':
            symbol_color = UNKNOWN_CAT_COLOR
            
            if show_unk == False:
                # skip this symbol in the output
                continue
        elif i == 0:
            symbol_color = GRAM_CAT_COLOR
        else:
            symbol_color = AFFIX_COLOR
        
        # Check for RTL
        if rtl == True:
            # prepend the RTL marker
            symb = ur'\u200F' + symb
        
        # output the symbol
        output_span(parent_element, symbol_color, ' '+symb, rtl)

# Split a compound from one lexical unit containing multiple words to multiple
# lexical units, 
def split_compounds(outStr):
    # Split into tokens where we have a > followed by a character other than $ or < (basically a lexeme)
    # this makes ^room1.1<n>service1.1<n>number1.1<n>$ into ['^room1.1<n', '>s', 'ervice1.1<n', '>n', 'umber1.1<n>$']
    toks = re.split('(>[^$<])', outStr)
    
    # If there is only one token return from the split, we don't have multiple words just
    # return the input string
    if len(toks) > 1:
        outStr = ''
        
        # Every odd token will be the delimeter that was matched in the split operation
        # Insert $^ between the > and letter of the 2-char delimeter.
        for i,tok in enumerate(toks):
            # if we have an odd numbered index
            if i&1:
                tok = tok[0]+"$^"+tok[1]
            outStr+=tok
    return outStr

# If the given path is has any relative or full paths
# I.e. there is a slash somewhere, then don't use the
# temp folder. Otherwise use the temp folder.
def build_path_default_to_temp(config_path):    
    # Check for a slash
    if '/' in config_path or '\\' in config_path:
        ret_path = config_path
    else:
        ret_path = os.path.join(tempfile.gettempdir(), config_path)
    return ret_path


# Append '1' to the headWord if there is no homograph #
def add_one(headWord): 
    if not re.search('(\d$)', headWord):
        return (headWord + '1')
    else:
        return headWord 

# Duplicate the capitalization of the model word on the input word
def do_capitalization(wordToChange, modelWord):
    if wordToChange and modelWord:
        if modelWord.isupper():
            return wordToChange.upper()
        elif modelWord[0].isupper():
            return wordToChange[0].upper()+wordToChange[1:]
        else:
            return wordToChange

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

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            myList = get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return

def GetEntryWithSense(e, inflFeatAbbrevs):
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
                        
                        # Collect any inflection features that are assigned to the special
                        # variant types called Irregularly Inflected Form
                        for varType in entryRef.VariantEntryTypesRS:
                            if varType.ClassName == "LexEntryInflType" and varType.InflFeatsOA:
                                my_feat_abbr_list = []
                                # The features might be complex, make a recursive function call to find all features
                                get_feat_abbr_list(varType.InflFeatsOA.FeatureSpecsOC, my_feat_abbr_list)
                                inflFeatAbbrevs.extend(my_feat_abbr_list)
                        break
                if foundVariant and entryRef.ComponentLexemesRS.Count > 0:
                    # if the variant we found is a variant of sense, we are done. Use the owning entry.
                    if entryRef.ComponentLexemesRS.ToArray()[0].ClassName == 'LexSense':
                        e = entryRef.ComponentLexemesRS.ToArray()[0].OwningEntry
                        break
                    else: # normal variant of entry
                        e = entryRef.ComponentLexemesRS.ToArray()[0]
                        continue
        notDoneWithVariants = False
    return e

def get_interlin_data(DB, report, sent_punct, contents, typesList, getSurfaceForm):
    
    prev_pv_list = []
    prev_e = None
    ccc = 0 # current_complex_component
    segment_list = []
    outputStrList = []
    curr_SegNum = 0
    prevEndOffset = 0

    # count analysis objects
    obj_cnt = -1
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for obj_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
        pass
    
    if obj_cnt == -1:
        report.Warning('No analyses found.')
    else:
        report.ProgressStart(obj_cnt+1)
    
    prevOutStr = ''    
    unknownWordList = []
    multiple_unknown_words = False
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(prog_cnt)
        outStr = affixStr = ''
        
        if getSurfaceForm:
            
            # If we are on a different segment, start a new list (if the last one was non-empty)
            if analysisOccurance.Segment.Hvo <> curr_SegNum:
                if len(segment_list) == 0 or len(segment_list[-1]) > 0:
                    bundle_list = []
                    segment_list.append(bundle_list)
                curr_SegNum = analysisOccurance.Segment.Hvo
        else:
            
            if prevEndOffset > 0:
                numSpaces = analysisOccurance.GetMyBeginOffsetInPara() - prevEndOffset
                if numSpaces > 0:
                    outputStrList.append(' '*numSpaces)
                elif numSpaces < 0: # new paragraph
                    outputStrList.append('\n')
            
            prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()
                
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            
            text_punct = ITsString(analysisOccurance.Analysis.Form).Text
            
            # See if one or more symbols is part of the user-defined sentence punctuation. If so output the
            # punctuation as part of a data stream along with the symbol/tag <sent>
            # convert to lists and take the set intersection
            if set(list(text_punct)).intersection(set(list(sent_punct))):
                outStr = "^"+text_punct+"<sent>$"
                
                if getSurfaceForm:
                    bundle_list.append((text_punct,outStr))
                
            # If not, assume this is non-sentence punctuation and just output the punctuation without a "symbol" e.g. <xxx>
            else:
                outStr = text_punct
            
            if not getSurfaceForm:
                outputStrList.append(outStr)     
            continue
        
        if getSurfaceForm:
            beg = analysisOccurance.GetMyBeginOffsetInPara()
            end = analysisOccurance.GetMyEndOffsetInPara()
            surfaceForm = ITsString(analysisOccurance.Paragraph.Contents).Text[beg:end]

        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = analysisOccurance.Analysis
        # We get into this block if there are no analyses for the word or an analysis suggestion hasn't been accepted.
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
            outStr = ITsString(analysisOccurance.Analysis.Form.BestVernacularAlternative).Text
            
            if getSurfaceForm:
                surfaceForm = outStr
            
            # Don't give the warning if it's an sfm marker or a number following a \v or \c
            if outStr[0] == '\\':
                pass
            elif (prevOutStr == '\\v' or prevOutStr == '\\c') and outStr.isdigit():
                pass
            # or anything after \f or \fr
            elif prevOutStr == '\\f' or prevOutStr == '\\fr':
                pass
            # Don't warn on the second time an unknown word is encountered
            elif outStr in unknownWordList:
                multiple_unknown_words = True
                pass
            else:
                report.Warning('No analysis found for the word: '+ outStr + ' Treating this is an unknown word.')
                
                # Check if we've had this unknown word already
                if outStr not in unknownWordList:
                    # Add this word to the unknown word list
                    unknownWordList.append(outStr)
                
            prevOutStr = outStr
            outStr += '<UNK>'
            
            if getSurfaceForm:
                bundle_list.append((surfaceForm, '^'+outStr+'$'))
            else:
                outputStrList.append('^'+outStr+'$')
            
            continue
        else:
            wfiAnalysis = None
            
        # Go through each morpheme in the word (i.e. bundle)
        for bundle in wfiAnalysis.MorphBundlesOS:
            if bundle.SenseRA:
                if bundle.MsaRA and bundle.MorphRA:
                    # Get the LexEntry object
                    e = bundleEntry = bundle.MorphRA.Owner
                        
                    # For a stem we just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':
                        
                        # Check for valid POS
                        if not bundle.MsaRA.PartOfSpeechRA:
                            outStr = ITsString(wfiAnalysis.Owner.Form.BestVernacularAlternative).Text
                            report.Warning('No POS found for the word: '+ outStr + ' Treating this is an unknown word.', DB.BuildGotoURL(e))
                            outStr += '<UNK>'
                            break
                        if bundle.MorphRA:
                            
                            # Go from variant(s) to entry/variant that has a sense
                            # We are only dealing with senses, so we have to get to one.
                            # Along the way collect inflection features associated with
                            # irregularly inflected variant forms so they can be outputted
                            inflFeatAbbrevs = []
                            e = GetEntryWithSense(e, inflFeatAbbrevs)
                            
                            # See if we have an enclitic or proclitic
                            if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in ('proclitic','enclitic'):
                                # Get the clitic gloss. Substitute periods with underscores. dots cause problems because in rules Apertium sees them as additional tags
                                affixStr += '<' + re.sub(r'\.', r'_',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                                
                                # TODO: have a config file defined way to change . to ><. This could be useful for port manteau languages.
                                # Get the clitic gloss. Substitute periods with >< to produce multiple tags a la Apertium.
                                #affixStr += '<' + re.sub(r'\.', r'><',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                            
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
                                                                # The entry we are on has to be at the right position in the complex form's component list
                                                                if pos_in_list == ccc:
                                                                    pv_list.append(complex_e)
                                                                    break;
                                    # See if we ended up with any phrasal verbs
                                    if len(pv_list) == 0: # no phrasal verbs
                                        prev_pv_list = []
                                        ccc = 0
                                    else: # yes, we have phrasal verbs
                                        if ccc == 0:
                                            saved1stbaselineWord = ITsString(analysisOccurance.BaselineText).Text
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
                                                    savedTags = ''
                                                    pv_list = []
                                                
                                                if getSurfaceForm:    
                                                    # We need to show both surface forms with one data stream for the complex form
                                                    # Get previous tuple from the bundle list and remove it
                                                    myTup = bundle_list.pop()
                                                    
                                                    # Add the previous surface form before the current surface form
                                                    surfaceForm = myTup[0] + ' ' + surfaceForm
                                                    
                                                    # Save the data stream part
                                                    saveStr = myTup[1]
                                                else:
                                                    # remove n/adj/... and it's tag from being output
                                                    saveStr = outputStrList.pop()
                                                    # first pop may have just popped punctuation of spacing
                                                    if len(outputStrList) > 0:
                                                        saveStr = outputStrList.pop() 
                                                    
                                                
                                                # The first component(s) could have tags (from affixes or inflection info.)
                                                # Save these tags so they can be put on the end of the complex form.
                                                # This kind of assumes that inflection isn't happening on multiple components
                                                # because that might give a mess when it's all duplicated on the complex form.
                                                g = re.search(r'.+?<\w+>(<.+>)', saveStr)
                                                if (g): 
                                                    savedTags += g.group(1)
                                                
                                        prev_pv_list = copy.copy(pv_list) 
                                        prev_e = e
                                else:
                                    ccc = 0
                                    
                                if shared_complex_e:
                                    
                                    if shared_complex_e.SensesOS:
                                        senseNum = 0 # require only one sense for a complex form
                                        
                                        # Get headword and set homograph # if necessary
                                        headWord = ITsString(shared_complex_e.HeadWord).Text
                                        headWord = do_capitalization(headWord, saved1stbaselineWord)
                                        headWord = add_one(headWord)
                                                                    
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
                                        
                                        # Get any features that come from irregularly inflected forms        
                                        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                        for grpName, abb in sorted(inflFeatAbbrevs, key=lambda x: x[0]):
                                            outStr += '<' + abb + '>'
                                            
                                        # Add the saved tags from a previous complex form component
                                        outStr += savedTags
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
                                    headWord = do_capitalization(headWord, ITsString(analysisOccurance.BaselineText).Text)
                                    headWord = add_one(headWord)
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
                                    
                                    # Get any features that come from irregularly inflected forms        
                                    # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                    for grpName, abb in sorted(inflFeatAbbrevs, key=lambda x: x[0]):
                                        outStr += '<' + abb + '>'
                        else:
                            report.Warning("Morph object is null.")    
                    # We have an affix
                    else:
                        if bundle.SenseRA:
                            # Get the clitic gloss. Substitute periods with underscores. dots cause problems because in rules Apertium sees them as additional tags
                            affixStr += '<' + re.sub(r'\.', r'_',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                            
                            # TODO: have a config file defined way to change . to ><. This could be useful for port manteau languages.
                            # Get the clitic gloss. Substitute periods with >< to produce multiple tags a la Apertium.
                            #affixStr += '<' + re.sub(r'\.', r'><',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
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
        
        if getSurfaceForm:
            # The bundle list is a tuple of surface form and apertium-style lexical unit
            bundle_list.append((surfaceForm,'^'+outStr+'$'))
        else:
            outputStrList.append('^'+outStr+'$')
    
    if multiple_unknown_words:
        report.Warning('One or more unknown words occurred multiple times.')
    if getSurfaceForm:
        report.Info('Processed '+str(obj_cnt+1)+' analyses.')
        return segment_list
    else:
        report.Info('Export of '+str(obj_cnt+1)+' analyses complete.')
        return outputStrList