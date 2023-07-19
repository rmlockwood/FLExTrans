#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
#
#
#   Version 3.9.4 - 7/19/23 - Ron Lockwood
#    Fixes #469. Don't show guid to the user on errors.
#
#   Version 3.9.3 - 7/17/23 - Ron Lockwood
#    Fixes #470. Re-write entry urls as sense urls when loading the sense linker.
#    Also clear the sense num field for such entries.
#
#   Version 3.9.2 - 7/17/23 - Ron Lockwood
#    Fixes #66. Use human-readable hyperlinks in the target equivalent custom field.
#
#   Version 3.9.1 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.8.4 - 5/3/23 - Ron Lockwood
#    When extracting the interlinear info., instead of checking if one punctuation symbol of
#    a cluster is in the list of sentence-ending punctuation, require all of the cluster to be
#    in the list before we consider it a <sent> block. Otherwise consider the whole cluster to be
#    non-sentence ending punctuation. This might create issues in places where we are looking for
#    sentence breaks in the transfer rules. This fix was for places where a footnote ended right
#    before a period, so we got \f*. The *. was a cluster that was being allowed to be sentence
#    punctuation, but this caused problems elsewhere (convert to ana I think) where * wasn't recognized.
#    Also fixed was adding saved pre punctuation when the next word is sentence punctuation. Before
#    this fix, some punctuation was being lost.
#
#   Version 3.8.3 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names.
#
#   Version 3.8.2 - 4/20/23 - Ron Lockwood
#    Reworked import statements. Fixed duplicate processErrorList.
#
#   Version 3.8.1 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.12 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   Version 3.7.11 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.10 - 1/30/23 - Ron Lockwood
#    New function to determine if a string has RTL characters.
#
#   Version 3.7.9 - 1/5/23 - Ron Lockwood
#    Support fixes to issue 229 by adding a parameter to check_for_cat_errors.
#
#   Version 3.7.8 - 12/25/22 - Ron Lockwood
#    Moved text and testbed classes to separate files TextClasses.py and Testbed.py
#
#   Version 3.7.7 - 12/24/22 - Ron Lockwood
#    added GetEntryWithSense, renamed old one to GetEntryWithSensPlusFeat
#
#   Version 3.7.6 - 12/24/22 - Ron Lockwood
#    Output a verse number also when getting a word by guid. Only for the first call
#    for a sentence.
#
#   Version 3.7.5 - 12/19/22 - Ron Lockwood
#    Output a verse number at the beg. of the sentence when getting surface and data
#    tuples if a verse number is present.
#
#   Version 3.7.4 - 12/13/22 - Ron Lockwood
#    handle file not found in the un fixproblemchars function.
#
#   Version 3.7.3 - 12/12/22 - Ron Lockwood
#    added none headword constant.
#
#   Version 3.7.2 - 12/1/22 - Ron Lockwood
#    Set PATH="" in the do_make.bat file we create to prevent other make programs
#    from being found and executed.
#
#   Version 3.7.1 - 11/7/22 - Ron Lockwood
#    Moved function here for stripping DOCTYPE from transfer rules file.
#
#   Version 3.7 - 11/5/22 - Ron Lockwood
#    New function loadSourceTextList to load a combo box with source texts titles
#
#   Version 3.6.10 - 10/19/22 - Ron Lockwood
#    Fixes #244. Give a warning if an attribute matches a grammatical category.
#
#   Version 3.6.9 - 9/2/22 - Ron Lockwood
#    Slash fix had a problem passing re MULTILINE to a pre-compiled regex.
#    It was actually passing 8 to the sub function to only do 8 substitutions.
#    Did away with the MULTILINE since it wasn't needed.
#
#   Version 3.6.8 - 9/2/22 - Ron Lockwood
#    Fixes #255. Convert slashes in symbols before running Apertium
#
#   Version 3.6.7 - 9/1/22 - Ron Lockwood
#   Fixes #254. Convert * to _ in stems.
#   Also reworked the convert problem chars function and calling functions.
#
#   Version 3.6.6 - 8/27/22 - Ron Lockwood
#   Made isProClitic, etc. global functions.
#
#   Version 3.6.5 - 8/26/22 - Ron Lockwood
#   Fixes #215 Check morpheme type against guid in the object instead of
#   the analysis writing system so we aren't dependent on an English WS.
#   Added a guid map for morpheme types.
#
#   Version 3.6.4 - 8/18/22 - Ron Lockwood
#    New function getXMLEntryText to get the string part of a left or right element
#    of the bilingual lexicon entry. Uses tail to get the text after <b/>. Modified the new
#    convertXMLEntryToColoredString
#
#   Version 3.6.3 - 8/18/22 - Ron Lockwood
#    Fixes #223. Show a tooltip for each word in the Select Words (checkbox) view.
#    The tooltip display the entry or entries for the word that are found in the
#    bilingual lexicon. For Utils this meant pulling out some code from process lexical unit()
#    and making a new function. Then a new function to convert XML to colored string was added.
#
#   Version 3.6.2 - 8/11/22 - Ron Lockwood
#    Fixes #198. Warn the user for periods in attribute definitions.
#
#   Version 3.6.1 - 8/11/22 - Ron Lockwood
#    Save transfer rule file in decomposed unicode.
#
#   Version 3.6 - 8/10/22 - Ron Lockwood
#    Save testbed file in composed or decomposed unicode depending on the config.
#    setting. Always convert the file to decomposed when first reading it.
#
#   Version 3.5.5 - 7/16/22 - Ron Lockwood
#    Fixes #142 (preceding spaces in entries)
#
#   Version 3.5.4 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5.3 - 6/13/22 - Ron Lockwood
#    Run make file changes to support the Windows version of the Apertium tools. Fixes #143.
#    This includes creating a batch file instead of a bash file and stripping out 
#    the DocType info. from the rules file within code here instead of the old fix.py.
#
#   Version 3.5.2 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.5.1 - 5/5/22 - Ron Lockwood
#    Moved CreateUniqueTitle from InsertTargetText to here so that ImportFromParatext
#    could use it. 
#
#   Version 3.5 - 4/1/22 - Ron Lockwood
#    Support functions used by Extract Bilingual Lexicon that may have a null
#    report object. Fixes #37
#
#   Version 3.4.4 - 3/21/22 - Ron Lockwood
#    Handle when transfer rules file and testbed file locations are not set in
#    the configuration file. Issue #95. Applies to run_makefile for Apertium.
#
#   Version 3.4.3 - 3/17/22 - Ron Lockwood
#    Allow for a user configurable Testbed location. Issue #70.
#
#   Version 3.4.2 - 3/10/22 - Ron Lockwood
#    Don't do the discontiguous types processing if there is nothing on the list
#    in the config file. This is a fix for issue #87.
#
#   Version 3.4.1 - 3/5/22 - Ron Lockwood
#    Use a config file setting for the transfer rules file. Make it an 
#    environment variable that the makefile can use.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.3 - 1/29/22 - Ron Lockwood
#    Fixed bug introduced in 3.3.1. Which output a 2nd version of unknown words.
#    Also, if a later part of the word lacks a sense or entry, don't put out another
#    lemma, instead put out a bogus affix: PartMissing. Fixes #54
#
#   Version 3.3.2 - 1/27/22 - Ron Lockwood
#    Major overhaul of the Setup Transfer Rule Grammatical Categories Tool.
#    Now the setup tool and the bilingual lexicon uses common code for getting
#    the grammatical categories from each lexicon. Fixes #50.
#
#   Version 3.3.1 - 1/27/22 - Ron Lockwood
#    Fixed index error bug when an index to the sense list overflowed. This is in
#    The TextWord class. Also prevent empty lexical units from being produced when
#    no root is present. This fixes #39 & #40.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2.6 - 12/30/21 - Ron Lockwood
#    Optimized Testbed Viewing. Particularly through caching Lexical Units. 
#
#   Version 3.2.5 - 11/30/21 - Ron Lockwood
#    New methods for TextSentence, TextWord to support Linker enhancements 
#
#   Version 3.2.4 - 10/22/21 - Ron Lockwood
#    Process the insertList first when building the guid map. This way uses
#    of az or va in the current sentence override the inserList ones. This
#    matters for punctuation. 
#
#   Version 3.2.3 - 7/1/21 - Ron Lockwood
#    punctuation_eval() moved here from ExtractSourceText
#
#   Version 3.2.2 - 4/30/21 - Ron Lockwood
#    More detailed error when GUID not found.
#
#   Version 3.2.1 - 3/8/21 - Ron Lockwood
#    Error checking for missing guid in XML files
#
#   Version 3.2 - 3/4/21 - Ron Lockwood
#    Support for discontiguous complex forms
#
#   Version 3.1.2 - 3/4/21 - Ron Lockwood
#    Support for testbed editing in the XML Editor XXE
#
#   Version 3.1.1 - 2/25/21 - Ron Lockwood
#    Fixed bug where stem features would be duplicated if getStemFeatures was
#    called more than once. Also set the surface form in the new initialize() method.
#
#   Version 3.1 - 2/25/21 - Ron Lockwood
#    Support an insert word list file for extraction purposes. Added a parameter
#    to createGuidMaps functions. New initialize() method in TextWord. New function:
#    getInsertedWordsList.
#
#   Version 3.0.1 - 2/19/21 - Ron Lockwood
#    remove @EOL or just EOL
#
#   Version 3.0 - 1/25/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.1.8 - 7/29/20 - Ron Lockwood
#    Return a count from writePrecedingSentPunc
#    
#   Version 2.1.7 - 7/29/20 - Ron Lockwood
#    In CheckForUnknown, check the surface form, not punctuation.
#    
#   Version 2.1.6 - 7/29/20 - Ron Lockwood
#    Support writing the word data and the punctuation separately in the Word
#    and Sent classes. This is for keeping punctuation in the same place during
#    TreeTran transformations.
#    
#   Version 2.1.5 - 7/29/20 - Ron Lockwood
#    Moved pre-punctuation check in getInterlinear above check for new sent.
#    
#   Version 2.1.4 - 3/27/20 - Ron Lockwood
#    Handle adding sentence punctuation when using TreeTran.
#    
#   Version 2.1.3 - 3/26/20 - Ron Lockwood
#    Moved TreeTran related class and functions from ExtractSourceText to the 
#    Utils file.
#
#   Version 2.1.2 - 3/22/20 - Ron Lockwood
#    Reorganized the punctuation part. Put the check for new sentence and
#    paragraph into a function. The logic is more linear now.
#
#   Version 2.1.1 - 3/21/20 - Ron Lockwood
#    Rewrote the TextWord class to handle multiple entries with associated lemmas
#    affix sets, etc. This was needed to handle compound words where more than one
#    root or stem is present in a 'word'. Calling functions were changed to 
#    accommodate the class changes. Also we rewrote the logic for doing punctuation.
#    Also corrected the logic for letting certain unknown words pass without
#    warning and pass down a text-wide unknown words map.
#
#   Version 2.1 - 3/20/20 - Ron Lockwood
#    Total rewrite of getInterlinData. Added a bunch of new classes that 
#    encapsulate texts, paragraphs, sentences, and words. Greatly reduced the
#    basic loop that goes through all analysis bundles and the elements of each
#    bundle. Now all the data is stored in the objects with the word object holding
#    most of it. The handling of complex forms is now done after we have gathered
#    all of the data. We also create the guid map only when needed for TreeTran.
# 
#   Version 2.0.3 - 2/12/20 - Ron Lockwood
#    Don't use sentence number as part of the guid map key.
# 
#   Version 2.0.2 - 2/4/20 - Ron Lockwood
#    Fixed bug where prev_e not being set in the correct loop.
#
#   Version 2.0.1 - 1/22/20 - Ron Lockwood
#    Add a new return object from get_interlinear that is a list of sentences
#    each sentence contains two items for each word, the lexical item in data stream 
#    format and the spacing or punctuation afterwards. Also fixed the Guid list use;
#    in the case of phrasal verbs, the first element of the compound wasn't getting
#    deleted from the Guid list.
#
#   Version 1.7.1 - 4/22/19 - Ron Lockwood
#    Fixed bug where two entries that occur together but were not part of the 
#    same complex form cause the 2nd one to be ignored. E.g. dust enteqad kon
#    the code saw dust was part of a complex form, when it got to enteqad it saw
#    it too was part of a complex form, but it wasn't in the right position so it
#    ignored it and the complex form enteqad kon didn't get recognized. Now when
#    enteqad is reached, the counter starts over for looking for new complex forms.
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.6.1 - 3/27/19 - Ron Lockwood
#    New methods in the TestbedTestXMLObject: getTest, getTestsList. Compile a
#    RegEx at the beginning.
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
import tempfile
import os
import shutil
import xml.etree.ElementTree as ET
import subprocess
import unicodedata

from System import Guid
from System import String

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString  
from SIL.LCModel.Core.Text import TsStringUtils
from SIL.LCModel.DomainServices import StringServices                                                  
from SIL.LCModel.DomainServices import SegmentServices

from flexlibs import FLExProject, AllProjectNames

import ReadConfig as MyReadConfig 
from TextClasses import TextEntirety, TextParagraph, TextSentence, TextWord
import FTPaths

NONE_HEADWORD = '**none**'

GRAM_CAT_ATTRIBUTE = 'a_gram_cat'

MAKEFILE_DICT_VARIABLE = 'DICTIONARY_PATH'
MAKEFILE_SOURCE_VARIABLE = 'SOURCE_PATH'
MAKEFILE_TARGET_VARIABLE = 'TARGET_PATH'
MAKEFILE_FLEXTOOLS_VARIABLE = 'FLEXTOOLS_PATH'
APERTIUM_ERROR_FILE = 'apertium_error.txt'
DO_MAKE_SCRIPT_FILE = 'do_make.bat'
CONVERSION_TO_STAMP_CACHE_FILE = 'conversion_to_STAMP_cache2.txt'
TESTBED_CACHE_FILE = 'testbed_cache.txt'
STRIPPED_RULES = 'tr.t1x'

## For TreeTran
GOOD_PARSES_LOG = 'good_parses.log'

CHECK_DELIMITER = True
DELIMITER_STR = '{'
ID = 'id' 

# File and folder names
OUTPUT_FOLDER = 'Output'
BUILD_FOLDER = 'Build'

# Style used for hyperlink style
globalStyle = 'NotSet'

# precompiled reguglar expressions
reDataStream = re.compile('(>[^$<])')  
reObjAddOne = re.compile('\d$', flags=re.RegexFlag.A) # ASCII-only match
reTestID = re.compile('test id=".+?"')
reSpace = re.compile(r'\s') 
rePeriod = re.compile(r'\.') 
reForwardSlash = re.compile(r'/') 
reHyphen = re.compile(r'-') 
reAsterisk = re.compile(r'\*') 
# the key is to find non-left or right angle brackets for the alphanumeric parts of the symbol
reSlashInSymbol = re.compile(r'(="[^<>=]+?)(/)([^<>=]+?")')
reSLASHInSymbol = re.compile(r'(<[^<>]+?)SLASH([^<>]+?>)')
reDoubleNewline = re.compile(r'\n\n')

NGRAM_SIZE = 5

morphTypeMap = {
"d7f713e4-e8cf-11d3-9764-00c04f186933": "bound root",
"d7f713e7-e8cf-11d3-9764-00c04f186933": "bound stem",
"d7f713df-e8cf-11d3-9764-00c04f186933": "circumfix",
"c2d140e5-7ca9-41f4-a69a-22fc7049dd2c": "clitic",
"0cc8c35a-cee9-434d-be58-5d29130fba5b": "discontiguous phrase",
"d7f713e1-e8cf-11d3-9764-00c04f186933": "enclitic",
"d7f713da-e8cf-11d3-9764-00c04f186933": "infix",
"18d9b1c3-b5b6-4c07-b92c-2fe1d2281bd4": "infixing interfix",
"56db04bf-3d58-44cc-b292-4c8aa68538f4": "particle",
"a23b6faa-1052-4f4d-984b-4b338bdaf95f": "phrase",
"d7f713db-e8cf-11d3-9764-00c04f186933": "prefix",
"af6537b0-7175-4387-ba6a-36547d37fb13": "prefixing interfix",
"d7f713e2-e8cf-11d3-9764-00c04f186933": "proclitic",
"d7f713e5-e8cf-11d3-9764-00c04f186933": "root",
"d7f713e8-e8cf-11d3-9764-00c04f186933": "stem",
"d7f713dd-e8cf-11d3-9764-00c04f186933": "suffix",
"3433683d-08a9-4bae-ae53-2a7798f64068": "suffixing interfix"} 

# Invalid category characters & descriptions & messages & replacements
catProbData = [['space', 'converted to an underscore', '_', reSpace],
           ['period', 'removed', '', rePeriod],
           ['slash', 'converted to a vertical bar', '|', reForwardSlash]
#          ['x char', 'fatal', '']
          ]

lemmaProbData = [['asterisk', 'converted to an underscore', '_', reAsterisk]
            ]
                        
bilingFixSymbProbData = [['slash', 'converted to SLASH', r'\1SLASH\3', reSlashInSymbol]
                        ]

bilingUnFixSymbProbData = [['SLASH', 'converted to slash', r'\1/\2', reSLASHInSymbol],
                           ['double newline', 'converted to single newline', r'\n', reDoubleNewline]
                          ]

def convertProblemChars(convertStr, problemDataList):                                                

    # Convert spaces to underscores and remove periods and convert slash to bar, etc.
    for probDataRow in problemDataList:
        
        # 3 = the compiled RE, 2 = the string to replace with
        convertStr = probDataRow[3].sub(probDataRow[2], convertStr)
        
    return convertStr

def getListOfSymbolSubPairs(convertStr, problemDataList):

    masterList = []
    
    for probDataRow in problemDataList:

        foundList = probDataRow[3].findall(convertStr)
    
        # remove duplicates
        foundList = list(set(foundList))
        
        # Assume we are getting a tuple because of the capture elements
        if len(foundList) > 0 and isinstance(foundList[0], tuple) == False:
            return []  
        
        for myItem in foundList:
            
            # join the tuple into a string
            trimmedItem = ''.join(myItem)
            
            replStr = probDataRow[3].sub(probDataRow[2], trimmedItem)
            masterList.append((trimmedItem, replStr))
    
    # return a list with duplicates removed
    return masterList
    
def isClitic(myEntry):
    
    return isProclitic(myEntry) or isEnclitic(myEntry)

def isProclitic(entry):
    
    ret_val = False
    
    # What might be passed in for a component could be a sense which isn't a clitic
    if entry.ClassName == 'LexEntry' and entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:
        
        morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
        morphType = morphTypeMap[morphGuidStr]
        
        if morphType  == 'proclitic':
        
            ret_val = True
            
    return ret_val
    
def isEnclitic(entry):

    ret_val = False
    
    # What might be passed in for a component could be a sense which isn't a clitic
    if entry.ClassName == 'LexEntry' and entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:
        
        morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
        morphType = morphTypeMap[morphGuidStr]
        
        if morphType  == 'enclitic':
        
            ret_val = True
            
    return ret_val

def getXMLEntryText(node):
    
    # Start with nodeText as the text part of the left node
    nodeText = node.text
    
    # But there is potentially more data. <b />'s which represent blanks might be there
    # Each b has a tail portion that needs to be concatenated to the nodeText
    for bElement in node.findall('b'):
        
        if bElement.tail:
            
            nodeText += ' ' + bElement.tail

    return nodeText
    
# Create a unique text title for FLEx
def createUniqueTitle(DB, title):
      
    # Create a list of source text names
    sourceTextList = getSourceTextList(DB)
    
    if title in sourceTextList:
    
        title += ' - Copy'

        if title in sourceTextList:
            
            done = False
            i = 2
            
            while not done: 
                
                tryName = title + ' (' + str(i) + ')'
                
                if tryName not in sourceTextList:
                    
                    title = tryName
                    done = True 
                    
                i += 1
    return title

def removeTestID(inStr):
    
    return reTestID.sub('', inStr)
    
def punctuation_eval(i, treeTranSentObj, myFLExSent, beforeAfterMap, wordGramMap, puncOutputMap, wordsHandledMap):      
    
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

# Get relative path to the given build folder and file
def turnPathIntoEnvironPath(absPathToBuildFolder, myPath):
    
    # See if we have an absolute path
    if os.path.isabs(myPath):
        
        relPath = os.path.relpath(myPath, absPathToBuildFolder)
    
    # If it's not an absolute path, we assume it's relative to the work project subfolder (e.g. WorkProjects\German-Swedish)
    # So from doing the make from the Build folder, we need to add ..\ to all of the paths we get from the config file.
    else:
        relPath = os.path.join('..', myPath)
        
    return relPath
    
# Run the makefile to run Apertium tools to do the transfer
# component of FLExTrans. The makefile is run by invoking a
# bash file. Absolute paths seem to be necessary.
# relPathToBashFile is expected to be with Windows backslashes
def run_makefile(absPathToBuildFolder, report):
    
    configMap = MyReadConfig.readConfig(report)
    if not configMap:
        return True

    # Get the path to the dictionary file
    dictionaryPath = MyReadConfig.getConfigVal(configMap, MyReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not dictionaryPath:
        return True
    
    dictionaryPath = turnPathIntoEnvironPath(absPathToBuildFolder, dictionaryPath)
    
    # Get the path to the source apertium file
    analyzedPath = MyReadConfig.getConfigVal(configMap, MyReadConfig.ANALYZED_TEXT_FILE, report)
    if not analyzedPath:
        return True
    
    analyzedPath = turnPathIntoEnvironPath(absPathToBuildFolder, analyzedPath)
    
    # Get the path to the target apertium file
    transferResultsPath = MyReadConfig.getConfigVal(configMap, MyReadConfig.TRANSFER_RESULTS_FILE, report)
    if not transferResultsPath:
        return True
    
    transferResultsPath = turnPathIntoEnvironPath(absPathToBuildFolder, transferResultsPath)

    # Create the batch file which merely cds to the appropriate 
    # directory and runs make. 
    fullPathMake = os.path.join(absPathToBuildFolder, DO_MAKE_SCRIPT_FILE)
    f = open(fullPathMake, 'w', encoding='utf-8')
    
    # make a variable for where the bilingual dictionary file should be found
    outStr = f'set {MAKEFILE_DICT_VARIABLE}={dictionaryPath}\n' 
    
    # make a variable for where the analyzed text file should be found
    outStr += f'set {MAKEFILE_SOURCE_VARIABLE}={analyzedPath}\n' 
    
    # make a variable for where the transfer results file should be found
    outStr += f'set {MAKEFILE_TARGET_VARIABLE}={transferResultsPath}\n' 
    
    # Get the current working directory which should be the FlexTools folder
    # cwd = os.getcwd()
    
    flexToolsPath = turnPathIntoEnvironPath(absPathToBuildFolder, FTPaths.TOOLS_DIR)

    # make a variable for where the apertium executable files and dlls are found
    outStr += f'set {MAKEFILE_FLEXTOOLS_VARIABLE}={flexToolsPath}\n' 
    
    # set path to nothing
    outStr += f'set PATH=""\n' 
    
    # Put quotes around the path in case there's a space
    outStr += f'cd "{absPathToBuildFolder}"\n'
    
    #fullPathErrFile = os.path.join(absPathToBuildFolder, APERTIUM_ERROR_FILE)
    outStr += f'"{FTPaths.MAKE_EXE}" 2>"{APERTIUM_ERROR_FILE}"\n'
    
    f.write(outStr)
    f.close()
    
    retVal = subprocess.call([fullPathMake])
    
    return retVal

def fixProblemChars(fullDictionaryPath):
    
    # Save a copy of the bilingual dictionary
    shutil.copy2(fullDictionaryPath, fullDictionaryPath+'.before_fix')
    
    f = open(fullDictionaryPath, encoding='utf-8')
    contentsStr = f.read()
    f.close()
    
    subPairs = getListOfSymbolSubPairs(contentsStr, bilingFixSymbProbData)
    
    # Replace / with || 
    contentsStr = convertProblemChars(contentsStr, bilingFixSymbProbData)

    f = open(fullDictionaryPath, 'w', encoding='utf-8')
    f.write(contentsStr)
    f.close()
    
    return subPairs

def unfixProblemCharsDict(fullDictionaryPath):

    # Restore original bilingual dictionary
    shutil.copy2(fullDictionaryPath+'.before_fix', fullDictionaryPath)

    # Delete the temporary dictionary file
    os.remove(fullDictionaryPath+'.before_fix')
    
def unfixProblemCharsRuleFile(fullTransferResultsPath):

    try:
        f = open(fullTransferResultsPath, encoding='utf-8')

        contentsStr = f.read()
        f.close()
        
        # Replace || with /
        contentsStr = convertProblemChars(contentsStr, bilingUnFixSymbProbData)
    
        f = open(fullTransferResultsPath, 'w', encoding='utf-8')
        f.write(contentsStr)
        f.close()
    
    except:
        pass
    
def subProbSymbols(buildFolder, ruleFile, subPairs):

    f = open(os.path.join(buildFolder, ruleFile), encoding='utf-8')
    
    contentsStr = f.read()
    f.close()
    
    # go through all problem symbols
    for pair in subPairs:
        
        # substitute all occurrences
        contentsStr = re.sub(pair[0], pair[1], contentsStr)

    f = open(os.path.join(buildFolder, ruleFile) ,"w", encoding='utf-8')
    f.write(contentsStr)
    f.close()
    
def decompose(myFile):
    
    try:
        # Open the file and read all the lines
        f = open(myFile , "r", encoding='utf-8')
    except:
        raise ValueError(f'Could not open the file {myFile} when converting to NFD.')

    lines = f.readlines()
    f.close()
    
    f = open(myFile ,"w", encoding='utf-8')
    
    # Go through the existing rule file and write everything to the new file except Doctype stuff.
    for line in lines:

        # Always convert lines to decomposed unicode
        f.write(unicodedata.normalize('NFD', line))
    f.close()
        
def checkRuleAttributes(tranferRulePath):
    
    error_list = []
    
    # Verify we have a valid transfer file.
    try:
        rulesTree = ET.parse(tranferRulePath)
    except:
        error_list.append(('Invalid File', f'The transfer file: {tranferRulePath} is invalid.', 2))
        return error_list
    
    # Find the attributes element
    myRoot = rulesTree.getroot()
    
    func_err_list = checkRuleAttributesXML(myRoot)
    
    error_list.extend(func_err_list)
    
    return error_list

def checkRuleAttributesXML(myRoot):
        
    error_list = []
    
    def_attrs_element = myRoot.find('section-def-attrs')
    
    if def_attrs_element:
        
        gramCatSet = set()
        
        # Loop through each attribute definition
        for def_attr_el in def_attrs_element:
            
            # If we have the special attribute for grammatical categories, add them to a list
            if def_attr_el.attrib['n'] == GRAM_CAT_ATTRIBUTE:
                
                # Loop through each grammatical category
                for attr_item_el in def_attr_el:
                
                    # Add the next one to the list
                    gramCatSet.add(attr_item_el.attrib['tags'])
                
                # Once we found the grammatical category, stop
                break
                    
        # Loop through each attribute definition
        for def_attr_el in def_attrs_element:
            
            # Loop through each attribute
            for attr_item_el in def_attr_el:
            
                attribStr = attr_item_el.attrib['tags']
                
                # If the attribute is the same as a grammatical category, give a warning. Of course don't check the gram cat attribute itself for this warning.
                if def_attr_el.attrib['n'] != GRAM_CAT_ATTRIBUTE:
                    
                    if attribStr in gramCatSet:
                    
                        error_list.append((f'The attribute: "{attribStr}" in "{def_attr_el.attrib["n"]}" is the same as a gramm. cat. Your rules may not work as expected.', 1))

                # Make sure there are no periods in the attribute, if there are give a warning
                if attribStr and re.search(r'\.', attribStr):
                    
                    error_list.append((f'The attribute: "{attribStr}" in "{def_attr_el.attrib["n"]}" has a period in it. It needs to be an underscore. Your rules may not work as expected.', 1))
    return error_list

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
    if not reObjAddOne.search(headWord):
        return (headWord + '1')
    return headWord 

# Duplicate the capitalization of the model word on the input word
def do_capitalization(wordToChange, modelWord):
    if wordToChange and modelWord:
        if modelWord.isupper():
            return wordToChange.upper()
        elif modelWord[0].isupper():
            return wordToChange[0].upper()+wordToChange[1:]
    return wordToChange

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return

def getHeadwordStr(e):
    return ITsString(e.HeadWord).Text
    
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
                    # if the variant we found is a variant of sense, we are done. Use the owning entry.
                    if entryRef.ComponentLexemesRS.ToArray()[0].ClassName == 'LexSense':
                        e = entryRef.ComponentLexemesRS.ToArray()[0].OwningEntry
                        break
                    else: # normal variant of entry
                        e = entryRef.ComponentLexemesRS.ToArray()[0]
                        continue
        notDoneWithVariants = False
    return e

def GetEntryWithSensePlusFeat(e, inflFeatAbbrevs):
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

# Compound words get put within one ^...$ block. Split them into one per word.
def split_compounds(outStr):
    # Split into tokens where we have a > followed by a character other than $ or < (basically a lexeme)
    # this makes ^room1.1<n>service1.1<n>number1.1<n>$ into ['^room1.1<n', '>s', 'ervice1.1<n', '>n', 'umber1.1<n>$']
    toks = reDataStream.split(outStr)
    
    # If there is only one token returned from the split, we don't have multiple words just
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

# Convert . (dot) to _ (underscore)
def underscores(inStr):
    return re.sub(r'\.', r'_', inStr)

def initProgress(contents, report): 
    # count analysis objects
    obj_cnt = -1
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for obj_cnt, _ in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
        pass
    
    if obj_cnt == -1:
        report.Warning('No analyses found.')
    else:
        report.ProgressStart(obj_cnt+1)

def checkForNewSentOrPar(report, myWord, mySent, myPar, myText, newSentence, newParagraph, spacesStr):
    if newSentence:
        
        # Create a new sentence object and add it to the paragraph
        mySent = TextSentence(report)
        newSentence = False
        
        # If we have a new paragraph, create the paragraph and add it to the text
        if newParagraph:
            myPar = TextParagraph()
            myText.addParagraph(myPar)
            newParagraph = False
        
        # Add the sentence to the paragraph
        myPar.addSentence(mySent)
        
    # Add the word to the current sentence
    mySent.addWord(myWord)
    
    # Add initial spaces
    myWord.addInitialPunc(spacesStr)
    
    return newSentence, newParagraph, mySent, myPar

# This is a key function used by the ExtractSourceText, LinkSenseTool and LiveRuleTesterTool modules
# Go through the interlinear text and each word bundle in the text and collect the words (stems/roots),
# the affixes and stuff associated with the words such as part of speech (POS), features, and classes.
# The FLEx text is organized into paragraphs and paragraphs are organized into segments. Segments
# contain word bundles. We collect words and associated data into Word objects which are containted in
# Sentence objects (corresponding to Segments) which are contained in Paragraph objectes which are 
# containted in a Text object. The text object is returned to the calling module.
# Punctuation is interspersed between word bundles as they occur. We associate punctuation with a Word
# object except for special sentence ending punctuation which is given in the sentPuct parameter. This
# kind of punctuation becomes its own Word object since eventually we want to output it as its own thing.
# At the end of the function we figure out appropriate warnings for unknown words and we process 
# complex forms which basically is substituting complex forms when we find contiguous words that match
# the complex form's components.
def getInterlinData(DB, report, sentPunct, contents, typesList, discontigTypesList, discontigPOSList):
    
    prevEndOffset = 0
    currSegNum = 0
    myWord = None
    mySent = None
    savedPrePunc = ''
    newParagraph = False
    newSentence = False
        
    initProgress(contents, report)
    
    # Initialize the text and the first paragraph object
    myText = TextEntirety()
    myPar = TextParagraph()
    
    # Add the first paragraph
    myText.addParagraph(myPar)
    
    # Loop through each thing in the text
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(prog_cnt)
        
        # Get the number of spaces between words. This becomes initial spaces for the next word        
        numSpaces = analysisOccurance.GetMyBeginOffsetInPara() - prevEndOffset
        spacesStr = ' '*numSpaces

        # See if we are on a new paragraph (numSpaces is negative)
        if numSpaces < 0:
            newParagraph = True
            
        # If we are on a different segment, it's a new sentence.
        if analysisOccurance.Segment.Hvo != currSegNum:
            newSentence = True
            
        # Save where we are    
        currSegNum = analysisOccurance.Segment.Hvo
        prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()
        
        # Deal with punctuation first
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            
            textPunct = ITsString(analysisOccurance.Analysis.Form).Text
            
            # See if one or more symbols is part of the user-defined sentence punctuation. If so, save the punctuation as if it is its own word. E.g. ^.<sent>$
            if set(list(textPunct)).issubset(set(list(sentPunct))):
                
                # create a new word object
                myWord = TextWord(report)
                
                # initialize it with the puctuation and sent as the "POS"
                myWord.addLemma(textPunct)
                myWord.setSurfaceForm(textPunct)
                myWord.addPlainTextAffix('sent')
                
                # See if we have any pre-punctuation
                if len(savedPrePunc) > 0:
                    myWord.addInitialPunc(savedPrePunc)
                    savedPrePunc = ""

                # Check for new sentence or paragraph. If needed create it and add to parent object. Also add current word to the sentence.
                newSentence, newParagraph, mySent, myPar = checkForNewSentOrPar(report, myWord, mySent, myPar, myText, newSentence, newParagraph, spacesStr)
                
            # If not, assume this is non-sentence punctuation and just save the punctuation to go with the current/next word.
            else:
                # If we have a word that has been started, that isn't the beginning of a new sentence, make this final punctuation.
                if myWord != None and not newSentence and (CHECK_DELIMITER and not textPunct == DELIMITER_STR): 
                    
                    myWord.addFinalPunc(spacesStr + textPunct) 
                else:
                    # Save this punctuation for initial punctuation on the next word
                    savedPrePunc += spacesStr + textPunct
        
            continue
        
        ## Now we know we have something other than punctuation
        
        # Start with a new word
        myWord = TextWord(report)
        
        # See if we have any pre-punctuation
        if len(savedPrePunc) > 0:
            myWord.addInitialPunc(savedPrePunc)
            savedPrePunc = ""
            
        # Check for new sentence or paragraph. If needed create it and add to parent object. Also add current word to the sentence.
        newSentence, newParagraph, mySent, myPar = checkForNewSentOrPar(report, myWord, mySent, myPar, myText, newSentence, newParagraph, spacesStr)
        
        # Figure out the surface form and set it.
        beg = analysisOccurance.GetMyBeginOffsetInPara()
        end = analysisOccurance.GetMyEndOffsetInPara()
        surfaceForm = ITsString(analysisOccurance.Paragraph.Contents).Text[beg:end]
        
        # Set lemma to surfaceForm initially
        myWord.setSurfaceForm(surfaceForm)

        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
            
        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = analysisOccurance.Analysis
            
        # We get into this block if there are no analyses for the word or an analysis suggestion hasn't been accepted. 
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
            
            # Lemma will be the same as the surface form, I think
            myWord.addLemmaFromObj(analysisOccurance.Analysis)
            continue
        
        # Don't know when we ever would get here
        else:
            wfiAnalysis = None
        
        # Go through each morpheme bundle in the word
        for bundle in wfiAnalysis.MorphBundlesOS:
            
            if bundle.SenseRA:
                if bundle.MsaRA and bundle.MorphRA:
                        
                    tempEntry = bundle.MorphRA.Owner
                    
                    # We have a stem. We just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':
                        
                        # Just save the the bundle guid for the first root in the bundle
                        if myWord.getGuid() == None:
                            myWord.setGuid(bundle.Guid) # identifies a bundle for matching with TreeTran output
            
                        # If we have an invalid POS, give a warning
                        if not bundle.MsaRA.PartOfSpeechRA:
                            
                            myWord.addLemmaFromObj(wfiAnalysis.Owner)
                            report.Warning('No POS found for the word: '+ myWord.getSurfaceForm(), DB.BuildGotoURL(tempEntry))
                            break
                        
                        if bundle.MorphRA:
                            # Go from variant(s) to entry/variant that has a sense. We are only dealing with senses, so we have to get to one. Along the way
                            # collect inflection features associated with irregularly inflected variant forms so they can be outputted.
                            inflFeatAbbrevs = []
                            tempEntry = GetEntryWithSensePlusFeat(tempEntry, inflFeatAbbrevs)
                            
                            # If we have an enclitic or proclitic add it as an affix, unless we got an enclitic with no root so far 
                            # in this case, treat it as a root
                            if isClitic(tempEntry) == True and not (isEnclitic(tempEntry) and myWord.hasEntries() == False):
                                # Get the clitic gloss.
                                myWord.addAffix(bundle.SenseRA.Gloss)
                                
                            # Otherwise we have a root or stem or phrase
                            else:
                                myWord.addEntry(tempEntry)
                                myWord.addInflFeatures(inflFeatAbbrevs) # this assumes we don't pick up any features from clitics
                                
                                # Go through each sense and identify which sense number we have
                                foundSense = False
                                for senseNum, mySense in enumerate(tempEntry.SensesOS):
                                    if mySense.Guid == bundle.SenseRA.Guid:
                                        myWord.addSense(mySense)
                                        foundSense = True
                                        break
                                if foundSense:
                                    # Construct and set the lemma
                                    myWord.buildLemmaAndAdd(analysisOccurance.BaselineText, senseNum)
                                else:
                                    myWord.addSense(None)
                                    report.Warning("Couldn't find the sense for headword: "+getHeadwordStr(tempEntry))    
                        else:
                            report.Warning("Morph object is null.")    

                    # We have an affix
                    else:
                        if bundle.SenseRA:
                            # Get the clitic gloss. Substitute periods with underscores. dots cause problems because in rules Apertium sees them as additional tags
                            myWord.addAffix(bundle.SenseRA.Gloss)
                        else:
                            report.Warning("Sense object for affix is null.")
                else:
                    if myWord.getLemma(0) == '':
                        myWord.addLemmaFromObj(wfiAnalysis.Owner)
                    else:
                        # Give a clue that a part is missing by adding a bogus affix
                        myWord.addPlainTextAffix('PartMissing')
                        
                    report.Warning('No morphosyntactic analysis found for some part of the word: '+ myWord.getSurfaceForm())
                    break # go on to the next word    
            else:
                # Part of the word has not been tied to a lexical entry-sense
                if myWord.getLemma(0) == '':
                    myWord.addLemmaFromObj(wfiAnalysis.Owner)
                else:
                    # Give a clue that a part is missing by adding a bogus affix
                    myWord.addPlainTextAffix('PART_MISSING')
                    
                report.Warning('No sense found for some part of the word: '+ myWord.getSurfaceForm())
                break # go on to the next word    
    
        # if we don't have a root or stem and we have something else like an affix, give a warning
        if myWord.getLemma(0) == '': 
            
            # TODO: we might need to support a proclitic standing alone (no root) in which case we would convert the last proclitic to a root
            
            # need a root
            myWord.addLemmaFromObj(wfiAnalysis.Owner)
            report.Warning('No root or stem found for: '+ myWord.getSurfaceForm())
        
    # Don't warn for sfm markers, but warn once for others        
    if myText.warnForUnknownWords() == True:
        report.Warning('One or more unknown words occurred multiple times.')

    # substitute a complex form when its components are found contiguous in the text      
    myText.processComplexForms(typesList) 
    
    # substitute a complex form when its components are found discontiguous in the text  
    if len(discontigTypesList) > 0 and len(discontigPOSList) > 0 and len(typesList) > 0:
            
        myText.processDiscontiguousComplexForms(typesList, discontigTypesList, discontigPOSList) 
    
    return myText

def importGoodParsesLog():
    logList = []
    
    f = open(os.path.join(tempfile.gettempdir(), GOOD_PARSES_LOG))
    
    for line in f:
        (numWordsStr, flagStr) = line.rstrip().split(',')
        
        if flagStr == '1':
            parsed = True
        else:
            parsed = False
    
        logList.append((int(numWordsStr), parsed))
    
    return logList
    
class treeTranSent():
    def __init__(self):
        self.__singleTree = True
        self.__guidList = []
        self.__index = 0
    def getSingleTree(self):
        return self.__singleTree
    def getGuidList(self):
        return self.__guidList
    def setSingleTree(self, val):
        self.__singleTree = val
    def addGuid(self, myGuid):
        self.__guidList.append(myGuid)
    def getNextGuid(self):
        if self.__index >= len(self.__guidList):
            return None
        return self.__guidList[self.__index]
    def getNextGuidAndIncrement(self):
        if self.__index >= len(self.__guidList):
            return None
        g = self.__guidList[self.__index]    
        self.__index += 1
        return g
    def getLength(self):
        return len(self.__guidList)

def getTreeSents(inputFilename, report):
    
    obj_list = []

    try:
        myETree = ET.parse(inputFilename)
    except:
        raise ValueError('The Tree Tran Result File has invalid XML content.' + ' (' + inputFilename + ')')
    
    myRoot = myETree.getroot()
    
    newSent = True
    myTreeSent = None
    
    # Loop through the anaRec's 
    for anaRec in myRoot:
        # Create a new treeTranSent object
        if newSent == True:
            myTreeSent = treeTranSent()
            obj_list.append(myTreeSent) # add it to the list
            newSent = False
            
        # See if this word has multiple parses which means it wasn't syntax-parsed
        mparses = anaRec.findall('mparse')
        if len(mparses) > 1:
            myTreeSent.setSingleTree(False)
        
        pNode = anaRec.find('./mparse/a/root/p')
        
        if pNode == None:
            report.Error("Could not find a GUID in the TreeTran results file. Perhaps TreeTran is not putting out all that you expect. anaRec id=" + anaRec.attrib[ID] + ". Exiting.")
            return None
        
        currGuid = Guid(String(pNode.text))
        analysisNode = anaRec.find('Analysis')
        if analysisNode != None:
            newSent = True
        
        myTreeSent.addGuid(currGuid)
    
    return obj_list

def getInsertedWordsList(inputFilename, report, DB):
    
    obj_list = []

    try:
        myETree = ET.parse(inputFilename)
    except:
        raise ValueError('The Tree Tran Words to Insert File has invalid XML content.' + ' (' + inputFilename + ')')
    
    myRoot = myETree.getroot()
    
    # Loop through the anaRec's 
    for anaRec in myRoot:
        
        # get the element that has the bundle guid
        pNode = anaRec.find('./mparse/a/root/p')

        if pNode == None:
            report.Error("Could not find a GUID in the Inserted Words Lists file. Exiting.")
            return None
        
        currGuid = Guid(String(pNode.text))
        
        # create and initialize a TextWord object
        currWord = TextWord(report)
        currWord.initialize(currGuid, DB)
        
        obj_list.append(currWord)
        
    return obj_list

def openTargetProject(configMap, report):
    
    TargetDB = FLExProject()

    # Open the target database
    targetProj = MyReadConfig.getConfigVal(configMap, MyReadConfig.TARGET_PROJECT, report)
    if not targetProj:
        return
    
    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():
        if report:
            report.Error('The Target Database does not exist. Please check the configuration file.')
        return
    
    try:
        TargetDB.OpenProject(targetProj, True)
    except: #FDA_DatabaseError, e:
        if report:
            report.Error('There was an error opening target database: '+targetProj+'. Perhaps the dabase is open.')
        raise
    
    if report:
        report.Info('Using: '+targetProj+' as the target database.')
    
    return TargetDB

# This is a recursive function to get all inflection subclasses
def get_sub_inflection_classes(mySubClasses):
    
    ic_list = []
    
    for ic in mySubClasses:
        
        icAbbr = ITsString(ic.Abbreviation.BestAnalysisAlternative).Text
        icName = ITsString(ic.Name.BestAnalysisAlternative).Text
        
        ic_list.append((icAbbr,icName))
        
        if ic.SubclassesOC and len(ic.SubclassesOC.ToArray()) > 0:
            
            icl = get_sub_inflection_classes(ic.SubclassesOC)
            ic_list.extend(icl)
            
    return ic_list

def get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=True):

    haveError = False
    dbList = [(DB, 'source')]
    
    # Sometime the caller may just want source categories
    if TargetDB:
        
        dbList.append((TargetDB, 'target'))

    for dbTup in dbList:
        
        dbObj = dbTup[0]
        dbType = dbTup[1]
        
        # initialize a list of error counters to 0
        countList = [0]*len(catProbData)
            
        # loop through all database categories
        for pos in dbObj.lp.AllPartsOfSpeech:
    
            # save abbreviation and full name
            posAbbrStr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            posFullNameStr = pos.ToString()
            
            # check for errors or warnings, pass in the error counter list which may have been incremented
            countList, posAbbrStr = check_for_cat_errors(report, dbType, posFullNameStr, posAbbrStr, countList, numCatErrorsToShow)
            
            # add a (possibly changed abbreviation string) to the map
            add_to_cat_map(posMap, posFullNameStr, posAbbrStr)
            
            # add inflection classes to the map if there are any if we are working on the target database
            if addInflectionClasses and dbType == dbList[1][1]: #target
                
                process_inflection_classes(posMap, pos)
            
            # check for serious error
            if countList[0] == 999:
                
                # Note we have the error, but keep going so tha we give all errors at once
                # reset error (warning) counter to zero
                countList[0] = 0
                haveError = True
    
    if haveError == True:
        return True
    else:
        return False

def add_to_cat_map(posMap, posFullNameStr, posAbbrStr):
    
    # add the pos category to a map    
    if posAbbrStr not in posMap:
        
        posMap[posAbbrStr] = posFullNameStr
    else:
        # If we already have the abbreviation in the map and the full category name
        # is not the same as the source one, append the target one to the source one
        if posMap[posAbbrStr] != posFullNameStr:
            
            posMap[posAbbrStr] += ' / ' + posFullNameStr

def process_inflection_classes(posMap, pos):
    
    if pos.InflectionClassesOC and len(pos.InflectionClassesOC.ToArray()) > 0:
        
        # Get a list of abbreviation and name tuples
        AN_list = get_sub_inflection_classes(pos.InflectionClassesOC)
        
        for icAbbr, icName in AN_list:
            
            posMap[icAbbr] = icName
    
def check_for_cat_errors(report, dbType, posFullNameStr, posAbbrStr, countList, numCatErrorsToShow, myType='category'):

    haveError = False
    
    # loop through the possible invalid characters
    for i, outStrings in enumerate(catProbData):
        
        charName = outStrings[0]
        message = outStrings[1]
        replChar = outStrings[2]
        invalidCharCompiledRE = outStrings[3]
        
        # give a warning if we find an invalid character
        if invalidCharCompiledRE.search(posAbbrStr):
            
            # check for a fatal error
            if message == 'fatal':
                
                if report:
                    report.Error(f"The abbreviation: '{posAbbrStr}' for {myType}: '{posFullNameStr}' can't have a {charName} in it. Could not complete, please correct this {myType} in the {dbType} database.")
                haveError = True
                
                # show all fatal errors
                continue
            
            oldAbbrStr = posAbbrStr
            
            # do the conversion    
            posAbbrStr = invalidCharCompiledRE.sub(replChar, posAbbrStr)

            # If we are under the max errors to show number, give a warning
            if countList[i] < numCatErrorsToShow:
                
                if report:
                    report.Warning(f"The abbreviation: '{oldAbbrStr}' for {myType}: '{posFullNameStr}' in the {dbType} database can't have a {charName} in it. The {charName}" + \
                                   f" has been {message}, forming {posAbbrStr}. Keep this in mind when referring to this {myType} in transfer rules.")
            
            # Give suppressing message when we go 1 beyond the max
            elif countList[i] == numCatErrorsToShow:
                
                if report:
                    report.Info("Suppressing further warnings of this type.")
                
            countList[i] += 1
    
    if haveError:
        countList[0] = 999
        return countList, posAbbrStr
    
    return countList, posAbbrStr

def stripRulesFile(report, buildFolder, tranferRulePath, strippedRulesFileName):
    
    # Open the existing rule file and read all the lines
    try:
        f = open(tranferRulePath ,"r", encoding='utf-8')
    except:
        report.Error(f'Error in opening the file: "{tranferRulePath}", check that it exists.')
        return True

    lines = f.readlines()
    f.close()
    
    # Create a new file tr.t1x to be used by Apertium
    f = open(os.path.join(buildFolder, strippedRulesFileName) ,"w", encoding='utf-8')
    
    # Go through the existing rule file and write everything to the new file except Doctype stuff.
    for line in lines:
        
        strippedLine = line.strip()
        
        if strippedLine == '<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN"' or \
               strippedLine == '<!DOCTYPE interchunk PUBLIC "-//XMLmind//DTD interchunk//EN"' or \
               strippedLine == '<!DOCTYPE postchunk PUBLIC "-//XMLmind//DTD postchunk//EN"' or \
               strippedLine == '"transfer.dtd">' or \
               strippedLine == '"interchunk.dtd">' or \
               strippedLine == '"postchunk.dtd">':
            continue
        
        # Always write transfer rule data as decomposed
        f.write(unicodedata.normalize('NFD', line))
    f.close()
    
    return False

def getSourceTextList(DB, matchingContentsObjList=None):

    sourceList = []
    for interlinText in DB.ObjectsIn(ITextRepository):

        sourceList.append(ITsString(interlinText.Name.BestAnalysisAlternative).Text.strip())

        # if the caller wants to get a list of contents objects, add to the provided list
        if matchingContentsObjList != None:

            matchingContentsObjList.append(interlinText.ContentsOA)

    return sourceList

def loadSourceTextList(widget, sourceText, sourceTextList):
    
    # Add items and when we find the one that matches the config file. Set that one to be displayed.
    for i, itemStr in enumerate(sorted(sourceTextList, key=str.casefold)):
        
        widget.addItem(itemStr)
        
        if itemStr == sourceText:
            
            widget.setCurrentIndex(i)

def hasRtl(text):
    
    for char in text:
        
        if unicodedata.bidirectional(char) in ('R', 'AL'):
            
            return True
        
    return False

# Eventually make this function locale sensitive. So if we are using Turkish locale we will do the right thing.
def capitalizeString(inStr, capitalizeCode, useCurrentLocaleRules=False):

    if capitalizeCode == '2':

        return inStr.upper()
    
    elif capitalizeCode == '1':

        return inStr.capitalize()
    
    return inStr

def processErrorList(error_list, report):

    for msg in error_list:
        
        # See if there is extra info to pass to the error reporter
        if len(msg) > 2:
            infoStr = msg[2]
        else:
            infoStr = ''

        # msg is a pair -- string & code & optional url
        if msg[1] == 0:
            report.Info(msg[0], infoStr)
        elif msg[1] == 1:
            report.Warning(msg[0], infoStr)
        else: # error=2
            report.Error(msg[0], infoStr)

def checkForFatalError(errorList, report):

    fatal = False
    msg = ''

    for triplet in errorList:

        msg = triplet[0]

        if triplet[1] == 2:

            fatal = True

            if report == None:
                break

            report.Error(msg)
    
    return fatal, msg

def getTargetSenseInfo(entry, DB, TargetDB, mySense, tgtEquivUrl, senseNumField, report, remove1dot1Bool=False, rewriteEntryLinkAsSense=False, preGuidStr='', senseEquivField=None):

    retVal = (None, None, None)

    senseNumStr = '1'

    # If not sense num custom field, that's ok
    if senseNumField:
    
        senseNumStr = DB.LexiconGetFieldText(mySense.Hvo, senseNumField)
    
        # If no sense number, assume it is 1
        if senseNumStr == None or not senseNumStr.isdigit():
            
            senseNumStr = '1'
    
    senseNum = int(senseNumStr)

    # Get the guid from the url
    u = tgtEquivUrl.index('guid')
    guidSubStr = tgtEquivUrl[u+7:u+7+36]

    # Look up the entry in the trgt project by guid
    repo = TargetDB.project.ServiceLocator.GetInstance(ICmObjectRepository)
    # repo = TargetDB.project.ServiceLocator.GetInstance(ILexEntryRepository)

    try:
        guid = Guid(String(guidSubStr))
        targetObj = repo.GetObject(guid)
    except:
        headWord = ITsString(entry.HeadWord).Text
        report.Error(f'Invalid url link or url not found in the target database while processing source headword: {headWord}.',\
                     DB.BuildGotoURL(entry))
        return retVal
    
    if targetObj:
        
        # See if this guid was for an entry or a sense. The old method was an entry with a given sense num.
        if targetObj.ClassName == 'LexEntry':

            targetEntry = targetObj

            if senseNum <= len(targetEntry.SensesOS.ToArray()):
                
                targetSense = targetEntry.SensesOS.ToArray()[senseNum-1]

                # If requested, rewrite entry link as sense link
                if rewriteEntryLinkAsSense:

                    myStyle = getHyperLinkStyle(DB)

                    if myStyle != None: # style 'hyperlink' doesn't exist

                        urlStr = preGuidStr + targetSense.Guid.ToString() + '%26tag%3d'

                        writeSenseHyperLink(DB, mySense, targetEntry, targetSense, senseEquivField, urlStr, myStyle)

                        # If the sense number field is None, we aren't using it
                        if senseNumField:

                            DB.LexiconSetFieldText(mySense, senseNumField, '')
            else:
                targetSense = None
        else:
            targetSense = targetObj
            targetEntry = targetSense.OwningEntry

            # Find which sense number this is
            for i, mySense in enumerate(targetEntry.SensesOS):

                if mySense == targetSense:
                    break
            
            senseNum = i+1

        # Make the lemma in the form x.x (but remove if 1.1)
        lem = fixupLemma(targetEntry, senseNum, remove1dot1Bool)

    return (targetSense, lem, senseNum)

def remove1dot1(lem):

    return re.sub('1\.1', '', lem)
    
def fixupLemma(entry, senseNum, remove1dot1Bool=False):
    
    lem = ITsString(entry.HeadWord).Text
    lem = add_one(lem)
    lem = lem + '.' + str(senseNum) # add sense number
    
    # If the lemma ends with 1.1, remove it (for optics)
    if remove1dot1Bool:

        return remove1dot1(lem)
    else:
        return lem

def removeLemmaOnePointSomething(lemmaStr):

    # Remove everything following the dot and optionally the 1 if it's there
    # So 2.1 or 2.2 would turn into 2, 3.1 -> 3
    # Basically we want to show the non-1 homograph numbers
    return re.sub(r'1*\..+', '', lemmaStr)

def getTargetEquivalentUrl(DB, senseObj, senseEquivField):
    
    equivStr = None

    # Get tsString with the custom field contents
    tsEquiv = DB.GetCustomFieldValue(senseObj.Hvo, senseEquivField)

    if tsEquiv.Text:

        # Initialize a builder object
        bldr = TsStringUtils.MakeStrBldr()
        bldr.ReplaceTsString(bldr.Length, bldr.Length, tsEquiv)

        # Get the properties of the string at position 0
        textPropObj = bldr.get_Properties(0)

        # The embedded object property is value 6
        urlStr = textPropObj.GetStrPropValue(6)

        if urlStr:

            # Discard the first character which is the ID
            equivStr = urlStr[1:]
        else:

            # No hyperlink, use the link directly
            # the Text member of the tsString holds the character string
            equivStr = tsEquiv.Text

    return equivStr

def writeSenseHyperLink(DB, sourceSense, targetEntry, targetSense, senseEquivField, urlStr, myStyle):

    # This headword should have a number if there is more than one of them
    headWordStr = ITsString(targetEntry.HeadWord).Text

    # Add a fake .1 so we can remove any 1.Xs
    headWordStr = removeLemmaOnePointSomething(headWordStr + '.1')
    glossStr = ITsString(targetSense.Gloss.BestAnalysisAlternative).Text

    # Put the string we want for the link name into a tsString
    linkName = f'linked to entry: {headWordStr}, sense: {glossStr}'

    # Make the string in the analysis writing system
    tss = TsStringUtils.MakeString(linkName, DB.project.DefaultAnalWs)

    # We use a builder object to set the hyperlink, initialize it with tss
    bldr = TsStringUtils.MakeStrBldr()
    bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)

    # Set the hyperlink to cover the whole string (0-length), using the above url and 'hyperlink' style
    StringServices.MarkTextInBldrAsHyperlink(bldr, 0, len(linkName), urlStr, myStyle)

    # Extract the changed tsString
    tss = bldr.GetString()

    # Call the set string function directly instead of using the FlexTools function since we need the hyperlink
    # This is a bit riskier, because it bypasses checks, but we assume it's a text field and not a multi WS string
    DB.project.DomainDataByFlid.SetString(sourceSense.Hvo, senseEquivField, tss)

def getHyperLinkStyle(DB):

    if globalStyle == 'NotSet':

        # Find the hyperlink style
        for Style in DB.ObjectsIn(IStStyleRepository):

            if Style.Name == 'Hyperlink':
                break

        # If it wasn't found, set the style to None
        if Style.Name != 'Hyperlink':
            Style = None
    else:
        Style = globalStyle
    
    return Style