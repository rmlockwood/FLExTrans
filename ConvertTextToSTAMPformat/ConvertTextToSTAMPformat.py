#
#   ConvertTextToSTAMPformat
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Create an ANA file from the output file after the Apertium transfer
#   has been done. Process the ANA file to deal with complex forms.
#
#   Conversion details: Each lemma+tags is converted to an ANA record which
#   consists of 3 possible lines staring with an sfm marker.
#   \a PREFIX_ENTRY... < POS ROOT_ENTRY > SUFFIX_ENTRY...    
#  (the entries are found in the root, suffix or prefix dictionaries)
#   \f leading punctuation
#   \n trailing punctuation
#   A prefix list which was created by another module is read in. This gives 
#   us a list of what all the prefixes are in the database. When we read a tag 
#   we check to see if it is a prefix, if not, it's a suffix. Note that we 
#   assume no features come out of the transfer process.
#
#   ANA re-processing details: each ANA root could potentially be a complex
#   form. We check each root against a list of all complex forms and if it is
#   complex, we process recursively all the components. The end result is possibly
#   multiple ANA records. I say possibly because some complex forms may map to
#   clitics plus their roots without being multiple words.
#   
#   Version 2 - 7/17/15 - Ron
#    Handle morphology on the first part of a complex form.
#    Read in the TargetComplexFormsWithInflectionOn1stElement configuration 
#    property. Verify that this and the other property are lists. Do all config.
#    file processing before opening the target DB. Add the 1stElement types to
#    the complexFormTypeMap with values set to 0. Code clean up.
#
#   Version 2 - 7/16/15 - Ron
#    Handle irregularly inflected forms. Added new methods to the ANAInfo class.
#    Trim newlines when reading in lines. Added functions get_feat_abbr_list and
#    change_to_variant to support changing to a variant form. Also added logic
#    to store all entries that have infl. variants.
#

import sys
import re 
import os
import tempfile
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

docs = {'moduleName'       : "Convert Text to STAMP Format",
        'moduleVersion'    : 3,
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Create a text file in STAMP format",
        'moduleDescription'   :
u"""
The target database set in the configuration file will be used. This module will 
create a text file in STAMP format using the Apertium transfer results. 
NOTE: messages and the task bar will show the SOURCE database
as being used. Actually the target database is being used.
""" }


#----------------------------------------------------------------
# The main processing function
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import IStText
from SIL.FieldWorks.FDO import IWfiGloss, IWfiWordform, IWfiAnalysis
from SIL.FieldWorks.FDO import ILexEntryRepository
from SIL.FieldWorks.FDO.DomainServices import SegmentServices
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
from collections import defaultdict
from System import Guid
from System import String

# model the information contained in one record in the ANA file
class ANAInfo(object):
    def __init__(self, myAnalysis=None, myBeforePunc=None, myAfterPunc=None):
        self.Analysis = myAnalysis # \a
        self.BeforePunc = myBeforePunc # \f
        self.AfterPunc = myAfterPunc # \n
    def getAnalysis(self):
        return self.Analysis
    def getAnalysisPrefixes(self): # returns '' if no prefix
        return re.search(r'(.*)<',self.Analysis).group(1)
    def getAnalysisRoot(self):
        return re.search(r'< .+ (.+) >',self.Analysis).group(1)
    def getAnalysisRootPOS(self):
        return re.search(r'< (.+) .+ >',self.Analysis).group(1)
    def getAnalysisSuffixes(self):
        return re.search(r'>(.*)',self.Analysis).group(1)
    def getPreDotRoot(self): # in other words the headword
        g = re.search(r'< .+ (.+)\.\d+ >',self.Analysis)
        if g:
            ret = self.removeUnderscores(g.group(1))
            return unicode(ret)
        return None
    def getSenseNum(self):
        return re.search(r'< .+ .+\.(\d+) >',self.Analysis).group(1)
    def getAfterPunc(self):
        return self.AfterPunc
    def getBeforePunc(self):
        return self.BeforePunc
    def addUnderscores(self, myStr):
        return re.sub(r' ', '_', myStr)
    def removeUnderscores(self, myStr):
        return re.sub(r'_', ' ', myStr)
    def setAnalysis(self, myAnalysis):
        self.Analysis = myAnalysis
    def setAnalysisByPart(self, prefixes, pos, root, suffixes): # prefixes and suffixes are string lists
        self.Analysis = '{0} < {1} {2} > {3}'.format(' '.join(prefixes), pos, self.addUnderscores(root), ' '.join(suffixes))
    def setAfterPunc(self, myAfterPunc):
        self.AfterPunc = myAfterPunc
    def setBeforePunc(self, myBeforePunc):
        self.BeforePunc = myBeforePunc
    def write(self, f_ana):
        f_ana.write('\\a ' + self.getAnalysis().encode('utf-8') + '\n')
        if self.getBeforePunc():
            f_ana.write('\\f ' + self.getBeforePunc().encode('utf-8') + '\n')
        if self.getAfterPunc():
            f_ana.write('\\n ' + self.getAfterPunc().encode('utf-8') + '\n')
        f_ana.write('\n')
        

# Read an ANA file and convert it to a list of ANAInfo objects
def get_ANA_info(file_name_str):
    
    f_ana = open(file_name_str, 'r')
    
    infoList = []
    for line in f_ana:
        line = unicode(line,'utf-8')
        if len(line) < 2:
            continue
        elif (line[1] == 'a'):
            myInfo = ANAInfo()
            infoList.append(myInfo)
            myInfo.setAnalysis(line[3:-1])
        elif (line[1] == 'f'):
            myInfo.setBeforePunc(line[3:-1])
        elif (line[1] == 'n'):
            myInfo.setAfterPunc(line[3:-1])
    
    return infoList

# Convert the output from the Apertium transfer to an ANA file
def convertIt(ana_name, pfx_name, out_name, report):
    
    f_ana = open(ana_name, 'w')
    
    all_prefixes = []
    
    # Read in the target prefix list. We need this to figure out which affixes (tags)
    # are prefixes. The rest are suffixes.
    f_pfx = open(pfx_name, 'r')
    for line in f_pfx:
        all_prefixes.append(line.rstrip())
        
    f_pfx.close()

    try:
        f_test = open(out_name, 'r')
    except IOError:
        report.Error('The file: '+out_name+' was not found.')
        return
        
    num_lines = sum(1 for line in open(out_name))
    report.ProgressStart(num_lines)
    
    # Read the output file. Sample text: xxx1.1<perspro><acc/dat>$ ^xx1.1<vpst><pfv><3sg_pst>$: xxx1.1<perspro>$
    f_apert = open(out_name, 'r')
    
    # Have to start with a blank line with utf8 files
    f_ana.write('\n')

    # Each line represents a paragraph
    for j, line in enumerate(f_apert):
        report.ProgressUpdate(j)
        line = unicode(line,'utf-8')
        
        # split on ^ or $ to get the 'word packages' (word + POS + affixes) E.g. ^xx1.1<vpst><pfv><3sg_pst>$ (assumption that no feature tags come out of the transfer process)
        aper_toks = re.split('\^|\$', line) 
        aper_toks = filter(None, aper_toks) # remove empty strings (typically at the beginning and end)
        
        # each token can contain multiple words packages, flesh these out
        # E.g. ^xxx1.1<ez>xxx1.1<ez>$
        word_toks = []
        for aper_tok in aper_toks:
            
            # If we have at least one word-forming char, then we have a word package(s)
            if re.search('\w', aper_tok, re.U):
                
                # Split on < or >. For ^rast<ez>dast<ez> we get ['^rast', '<', 'ez', '>', 'dast', '<', 'ez', '>', '']
                sub_toks = re.split('(<|>)', aper_tok) # Note: we get the < and > in the list because we used parens
                sub_toks = filter(None, sub_toks) # remove empty strings (typically at the end)
            
                # loop through all the sub tokens which may have multiple words
                my_list = []
                for i, t in enumerate(sub_toks):
                    my_list.append(t)
                    # if we are at the end of the 'word package' or end of the string build the word string
                    # we check for the end by not seeing a < after a >, >< means we are still on an affix/POS or being at the end
                    if (t == '>' and (i+1 >= len(sub_toks) or sub_toks[i+1][0] != '<')):
                        j = "".join(my_list)
                        word_toks.append(j) # add the word package to the list
                        my_list = []
            else:
                word_toks.append(aper_tok)
        
        wordStr = ''
        pre_punct = ''
        next_pre_punct = ''
        post_punct = ''

        # Loop through all word packages
        for tok in word_toks:
            # if the token is only spaces, ignore it. We will eventually output
            # one space between words
            if re.match('\s*$', tok): # match starts at beg. of string
                continue
            # word plus possible affixes
            elif re.search('\w', tok, re.U):
                
                # write out the last word we processed.
                if wordStr:
                    f_ana.write('\\a' + wordStr.encode('utf-8') + '\n')
                    
                    if pre_punct:
                        f_ana.write('\\f ' + pre_punct.encode('utf-8') + '\n')
                    
                    if post_punct:
                        f_ana.write('\\n ' + post_punct.encode('utf-8') + '\n')
                        
                    f_ana.write('\n')
                    
                    pre_punct = next_pre_punct
                    next_pre_punct = post_punct = ''
                else:
                    # handle punctuation at the beginning of the paragraph (before the word)
                    if post_punct:
                        pre_punct = post_punct
                        
                    # if first word of a non-initial paragraph
                    if j > 0:
                        pre_punct = '\\n' + pre_punct
                
                # Get the root, root category and any affixes
                morphs = re.split('<|>', tok, re.U)
                morphs = filter(None, morphs) # remove empty strings
                
                prefix_list = []
                suffix_list = []
                # start at position 2 since this is where the affixes start
                for i in range(2,len(morphs)):
                    # prefix
                    if morphs[i] in all_prefixes:
                        prefix_list.append(morphs[i])
                    # suffix
                    else:
                        suffix_list.append(morphs[i])
                
                wordStr = ''

                if len(morphs) <2:
                    report.Error("Word or POS missing. Found: "+",".join(morphs))
                    for m in morphs:
                        f_ana.write(m.encode('utf-8'))
                    raise BaseException
                
                # build output word in .ana style
                for pr in prefix_list:
                    wordStr += ' '+pr
                
                # change spaces to underscores
                morphs[0] = re.sub('\s', '_', morphs[0])
                
                # now we have the root (morphs[0]) and the POS of the root (morphs[1])
                # .ana requires the POS first
                wordStr += ' < '+ morphs[1] + ' ' + morphs[0] + ' > '
                for su in suffix_list:
                    wordStr += ' '+su
            
            # some kind of punctuation with possible spaces between. E.g. .>> <<
            else:
                if tok[0] == ' ': # we have pre-punctuation that goes with the next word
                    next_pre_punct = tok.lstrip()
                else:
                    puncts = tok.split()
                    post_punct = puncts[0] + ' '
                    
                    if len(puncts)>1:
                        next_pre_punct = ' '.join(puncts[1:len(puncts)])
            
        # write out the last word 
        if wordStr:
            f_ana.write('\\a' + wordStr.encode('utf-8') + '\n')
            
            if pre_punct:
                f_ana.write('\\f ' + pre_punct.encode('utf-8') + '\n')
            
            if post_punct:
                f_ana.write('\\n ' + post_punct.encode('utf-8') + '\n')
                
            f_ana.write('\n')

    f_ana.close()      

# Append '1' to the headWord if there is no homograph #
def add_one(headWord): 
    if not re.search('(\d$)', headWord):
        return (headWord + '1')
    else:
        return headWord 

def is_proclitic(e):
    ret_val = False
    # What might be passed in for a component could be a sense which isn't a clitic
    if e.ClassName == 'LexEntry' and \
       ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text == 'proclitic':
        ret_val = True
    return ret_val
    
def is_enclitic(e):
    ret_val = False
    # What might be passed in for a component could be a sense which isn't a clitic
    if e.ClassName == 'LexEntry' and \
       ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text == 'enclitic':
        ret_val = True
    return ret_val

# Get the gloss from the first sense

def get_gloss(e):    
    # follow the chain of variants to get an entry with a sense
    e = GetEntryWithSense(e)
    return ITsString(e.SensesOS.ToArray()[0].Gloss.BestAnalysisAlternative).Text

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

# Get the needed data from the entry object and return as a tuple
# This function will handle when an entry points to a component that is a sense not a lexeme
def get_ana_data_from_entry(comp_e):
    
    # default to 1st sense. At the moment this isn't a big deal because we aren't doing anything with target senses. But eventually this needs to be gleaned somehow from the complex form.
    sense_num = '1'
    
    # The thing the component lexeme points to could be a sense rather than an entry
    if comp_e.ClassName == 'LexSense':
        comp_sense = comp_e
        # Get the headword text of the owning entry
        owning_e = comp_e.Owner # Assumption here that this isn't a subsense
        
        a = ITsString(owning_e.HeadWord).Text
        a = add_one(a)
        
        posObj = comp_sense.MorphoSyntaxAnalysisRA.PartOfSpeechRA
        if posObj:            
                abbrev = ITsString(posObj.Abbreviation.BestAnalysisAlternative).Text
                   
        # Get the sense # from the sense Headword E.g. xxx 2 (keep.pst) or xxx (foot)
        sense_num = re.search(r'(\d*) \(',ITsString(comp_sense.HeadWord).Text).group(1)
        
        # No number found, so use sense 1
        if sense_num == '':
            sense_num = '1'
        
    else: # entry
        comp_e = GetEntryWithSense(comp_e)
        
        a = ITsString(comp_e.HeadWord).Text
        a = add_one(a)
        #print a   
        # Get POS
        abbrev = 'NULL'
        if comp_e.SensesOS.Count > 0:
            posObj = comp_e.SensesOS.ToArray()[0].MorphoSyntaxAnalysisRA.PartOfSpeechRA
            if posObj:            
                abbrev = ITsString(posObj.Abbreviation.BestAnalysisAlternative).Text
    
    return (a, abbrev, sense_num)

# Output the components of a complex entry
# Assumptions: no sub-senses, clitics will be attached on the component that takes the inflection
# This is a recursive function
def gather_components(root, complexFormTypeMap, complex_map, anaInfo, comp_list):
    # Get the entry that has components
    e = complex_map[root]
    
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            for complexType in entryRef.ComplexEntryTypesRS:
                formType = ITsString(complexType.Name.BestAnalysisAlternative).Text
                if formType in complexFormTypeMap: # this is one the user designated (via config. file) as a complex form to break down
                    
                    # See where the inflection is to go
                    if complexFormTypeMap[formType] == 0:
                        inflectionOnFirst = True
                        inflectionOnLast = False
                    else:
                        inflectionOnFirst = False
                        inflectionOnLast = True
                        
                    first_root = True
                    enclGloss = proGloss = ''
                    # Write out all the components
                    for lex_index, comp_e in enumerate(entryRef.ComponentLexemesRS):
                        
                        # If the component is a proclitic, save the gloss string (with a space on the end)
                        if is_proclitic(comp_e):
                            proGloss = get_gloss(comp_e)+' '
                            continue
                        
                        # If the component is an enclitic, save it with a preceding space
                        elif is_enclitic(comp_e):
                            enclGloss = ' '+get_gloss(comp_e)
                            
                        # Otherwise we have a root
                        else:
                            # Get the needed data from the entry object
                            (head_word, gram_cat_abbrev, sense_num) = get_ana_data_from_entry(comp_e)
                            
                            # See if this head word has components itself and call this function recursively
                            if head_word in complex_map:
                                gather_components(head_word, complexFormTypeMap, complex_map, anaInfo, comp_list)
                            else:
                                # See if we are at the beginning or the end, depending on where the
                                # inflection goes, write out all the stuff with inflection
                                if (inflectionOnFirst and first_root) or \
                                   (inflectionOnLast and lex_index==entryRef.ComponentLexemesRS.Count-1):
                                    # Build the \a string
                                    a = proGloss + anaInfo.getAnalysisPrefixes() + '< ' + gram_cat_abbrev + \
                                        ' ' + head_word + '.' + sense_num + ' >' + \
                                        anaInfo.getAnalysisSuffixes() + enclGloss 
                                        
                                # Write out the bare bones root in the analysis part
                                else:
                                    a = '< ' + gram_cat_abbrev + ' ' + head_word + '.' + sense_num + ' >'
                            
                                comp_list.append(a)
                            first_root = False
                break
        break
    
def write_components(comp_list, f_ana, anaInfo):
    for i, comp in enumerate(comp_list):
        
        # Write analysis string
        f_ana.write('\\a ' + comp.encode('utf-8') + '\n')
        
        # Handle pre-punctuation
        if i == 0:
            if anaInfo.getBeforePunc():
                f_ana.write('\\f ' + anaInfo.getBeforePunc().encode('utf-8') + '\n')
                
        # Handle post-punctuation
        if i == len(comp_list)-1:
            if anaInfo.getAfterPunc():
                f_ana.write('\\n ' + anaInfo.getAfterPunc().encode('utf-8') + '\n')
        
        f_ana.write('\n')    

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            myList = get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return

# Check if the tags (prefixes & suffixes) match the features of one of
# the main entry's variants. If so replace the main entry headword with
# the variant and remove the tags that matched.
# E.g. if the main entry 'be1.1' has an irr. infl. form variant 'am1.1' with a 
# variant type called 1Sg which has features [per: 1ST, num: SG] and the
# Ana entry is '< cop be1.1 >  1ST SG', we want a new Ana entry that looks like 
# this: '< cop be1.1 >'
def change_to_variant(myAnaInfo, my_irr_infl_var_map):

    pfxs = myAnaInfo.getAnalysisPrefixes().split()
    num_pfxs = len(pfxs)
    sfxs = myAnaInfo.getAnalysisSuffixes().split()
    tags = pfxs+sfxs
    
    # loop through the irr. infl. form variant list for this main entry
    varList = my_irr_infl_var_map[myAnaInfo.getPreDotRoot()]
    
    for varTuple in varList: # each tuple as form (entry, feat_abbr_list)
        e = varTuple[0]
        feat_abbr_list = varTuple[1]

        # See if there is a variant that has inflection features that match the tags in this entry
        variant_matches = False
        featList = [y[1] for y in sorted(feat_abbr_list, key=lambda x: x[0])]
        num_features = len(featList)
        
        # There has to be at least as many tags as features
        if len(tags) >= num_features:
            # Loop through slices of the tag list
            for i in range(0,len(tags)-num_features+1):
                # See if we match regardless of order
                if sorted(tags[i:i+num_features]) == sorted(featList):
                    variant_matches = True
                    break
            if variant_matches:
                break
    
    if variant_matches:
        
        # Set the headword value and the homograph #
        headWord = ITsString(e.HeadWord).Text
            
        # If there is not a homograph # at the end, make it 1
        headWord = add_one(headWord)
            
        # Remove the matched tags
        del pfxs[i:i+num_features]
        beg = i-num_pfxs
        if beg < 0:
            beg = 0
        end = i-num_pfxs+num_features
        if end < 0:
            end = 0
        del sfxs[beg:end]
        
        # We are intentionally not adding the sense number.
        myAnaInfo.setAnalysisByPart(pfxs, "_variant_", headWord, sfxs)

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    targetANA = ReadConfig.getConfigVal(configMap, 'TargetOutputANAFile', report)
    prefixFile = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
    complexForms1st = ReadConfig.getConfigVal(configMap, 'TargetComplexFormsWithInflectionOn1stElement', report)
    complexForms2nd = ReadConfig.getConfigVal(configMap, 'TargetComplexFormsWithInflectionOn2ndElement', report)
    transferResults = ReadConfig.getConfigVal(configMap, 'TargetTranferResultsFile', report)
    if not (targetANA and prefixFile and transferResults):
        return

    # Check the validity of the complex forms lists
    if complexForms1st and not ReadConfig.configValIsList(configMap, 'TargetComplexFormsWithInflectionOn1stElement', report):
        return
    if complexForms2nd and not ReadConfig.configValIsList(configMap, 'TargetComplexFormsWithInflectionOn2ndElement', report):
        return

    TargetDB = FLExDBAccess()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenDatabase(targetProj, verbose = True)
    except FDA_DatabaseError, e:
        report.Error(e.message)
        print "FDO Cache Create failed!"
        print e.message
        return

    report.Info('Using: '+targetProj+' as the target database.')

    anaFileName = os.path.join(tempfile.gettempdir(), targetANA)
    prefixFileName = os.path.join(tempfile.gettempdir(), prefixFile)
    
    # Build the complex forms map
    complexFormTypeMap = {}
    
    # Create a map that tracks which complex form types are for first or for last 
    for cmplx_type in complexForms1st:
        complexFormTypeMap[cmplx_type] = 0  # 0 - inflection on first root
    for cmplx_type in complexForms2nd:
        complexFormTypeMap[cmplx_type] = 1  # 1 - inflection on last root
    
    # Convert the Apertium file to an ANA file
    convertIt(anaFileName, prefixFileName, transferResults, report)

    complex_map = {}
    irr_infl_var_map = {}
    report.ProgressStart(TargetDB.LexiconNumberOfEntries())
  
    # Loop through all the entries in the lexicon 
    for i,e in enumerate(TargetDB.LexiconAllEntries()):
    
        report.ProgressUpdate(i)
        
        # Set the headword value and the homograph #
        headWord = ITsString(e.HeadWord).Text
        
        # If there is not a homograph # at the end, make it 1
        if not re.search('(\d$)', headWord):
            headWord += '1'
                                
        # Store all the complex entries by creating a map from headword to the the complex entry
        if e.EntryRefsOS.Count > 0: # only process complex forms
            for entryRef in e.EntryRefsOS:
                if entryRef.ComponentLexemesRS and \
                   entryRef.ComponentLexemesRS.Count > 1 and \
                   entryRef.RefType == 1: # 1=complex form, 0=variant # At least 2 components
                    if entryRef.ComplexEntryTypesRS:
                        # there could be multiple types assigned to a complex form (e.g. Phrasal Verb, Derivative)
                        # just see if one of them is Phrasal Verb
                        for complexType in entryRef.ComplexEntryTypesRS:
                            if ITsString(complexType.Name.BestAnalysisAlternative).Text in complexFormTypeMap:
        
                                complex_map[headWord] = e
                                break
                        break # if we found a complex form, there won't be any more
        
        # Store all the entries that have inflectional variants with features assigned
        if e.VariantFormEntries.Count > 0:
            for variantForm in e.VariantFormEntries:
                for entryRef in variantForm.EntryRefsOS:
                    if entryRef.RefType == 0: # we have a variant
                        
                        # Collect any inflection features that are assigned to the special
                        # variant types called Irregularly Inflected Form
                        for varType in entryRef.VariantEntryTypesRS:
                            if varType.ClassName == "LexEntryInflType":
                                if varType.InflFeatsOA:
                                    my_feat_abbr_list = []
                                    # The features might be complex, make a recursive function call to find all features
                                    get_feat_abbr_list(varType.InflFeatsOA.FeatureSpecsOC, my_feat_abbr_list)
                                    if len(my_feat_abbr_list) > 0:
                                        myTuple = (variantForm, my_feat_abbr_list)
                                        if headWord not in irr_infl_var_map:
                                            irr_infl_var_map[headWord] = [myTuple]
                                        else:
                                            irr_infl_var_map[headWord].append(myTuple)
                            
    # Now we are going to re-process the ANA file breaking down each complex form
    # into separate ANA records if needed. This is needed for instance if a source word
    # maps to multiple words in the target language. The multi-word ANA record needs to
    # be broken down into multiple ANA records
         
    # Read in the ANA file we created above storing all the ana pieces (\a + \f + \n)
    anaInfoList = get_ANA_info(anaFileName)
    
    f_ana = open(anaFileName, 'w')
    f_ana.write('\n') # always need a blank line at the top
    
    count = 0
    
    # Loop through all the ANA pieces
    for anaInfo in anaInfoList:
        
        # If an ANA root matches a complex form, rewrite the ana file with complex forms 
        # broken down into components
        root = anaInfo.getPreDotRoot()
        if root in complex_map:
            comp_list = []
            gather_components(root, complexFormTypeMap, complex_map, anaInfo, comp_list)
            write_components(comp_list, f_ana, anaInfo)
            
        else: # write it out as normal
            if root in irr_infl_var_map: # assume an entry can't be complex and an inflectional variant
                # replace main entry with variant entry and remove appropriate tags (pfxs & sfxs)
                change_to_variant(anaInfo, irr_infl_var_map)
                
            anaInfo.write(f_ana)
        
        count += 1
    
    report.Info(str(count)+' records exported in ANA format.')        
    print 'done.'

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

