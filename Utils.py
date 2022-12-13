#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
#
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
import uuid
import unicodedata
from datetime import datetime
import TestbedValidator
from System import Guid
from System import String

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   
from SIL.LCModel.DomainServices import SegmentServices
from flexlibs import FLExProject, AllProjectNames

import ReadConfig as MyReadConfig 
from FTPaths import CONFIG_PATH

NONE_HEADWORD = '**none**'

GRAM_CAT_ATTRIBUTE = 'a_gram_cat'

MAKEFILE_DICT_VARIABLE = 'DICTIONARY_PATH'
MAKEFILE_SOURCE_VARIABLE = 'SOURCE_PATH'
MAKEFILE_TARGET_VARIABLE = 'TARGET_PATH'
MAKEFILE_FLEXTOOLS_VARIABLE = 'FLEXTOOLS_PATH'
APERTIUM_ERROR_FILE = 'apertium_error.txt'
DO_MAKE_SCRIPT_FILE = 'do_make.bat'
CONVERSION_TO_STAMP_CACHE_FILE = 'conversion_to_STAMP_cache.txt'
TESTBED_CACHE_FILE = 'testbed_cache.txt'
STRIPPED_RULES = 'tr.t1x'

## For TreeTran
GOOD_PARSES_LOG = 'good_parses.log'

CHECK_DELIMITER = True
DELIMITER_STR = '{'

## Viewer constants
# Main color of the headwords
LEMMA_COLOR = '000000' #black
CHUNK_LEMMA_COLOR = 'FF00FF' #purple
# For grammatical category - always the 1st symbol
GRAM_CAT_COLOR = '0070C0' #blue
CHUNK_GRAM_CAT_COLOR = '0000FF' #darker blue
# The color of affixes or other things such as features, classes, etc.
AFFIX_COLOR = '00B050' #green
CHUNK_AFFIX_COLOR = '00E000' #darker green
# The color of non-sentence punctuation. Sentence punctuation will be in its
# own lexical item with <sent> as the category
PUNC_COLOR = 'D0802B' #orange
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
BUILD_FOLDER = 'Build'

# Testbed XML constants
FLEXTRANS_TESTBED = 'FLExTransTestbed'
FLEXTRANS_TESTBED_RESULTS = 'FLExTransTestbedResults'
TESTBED_RESULT = 'testbedResult' 
START_DATE_TIME = 'startDateTime' 
END_DATE_TIME = 'endDateTime' 
TESTBEDS = 'testbeds' 
TESTBED = 'testbed' 
TESTS = 'tests' 
TEST = 'test' 
SOURCE_INPUT = 'sourceInput'
LEXICAL_UNITS = 'lexicalUnits'
LEXICAL_UNIT = 'lexicalUnit'
HEAD_WORD = 'headWord'        
SENSE_NUM = 'senseNum'        
GRAM_CAT = 'grammaticalCategoryTag'        
OTHER_TAGS = 'otherTags'        
TAG = 'tag'     
SENT = 'sent'   
SENT_TAG = '<'+SENT+'>'
TARGET_OUTPUT = 'targetOutput' 
EXPECTED_RESULT = 'expectedResult' 
ACTUAL_RESULT = 'actualResult' 
TGT_EXPECTED = TARGET_OUTPUT+'/'+EXPECTED_RESULT
TGT_ACTUAL = TARGET_OUTPUT+'/'+ACTUAL_RESULT
SOURCE_DIRECTION = 'source_direction' 
TARGET_DIRECTION = 'target_direction' 
N_ATTRIB = 'n' 
ID = 'id' 
IS_VALID = 'is_valid' 
INVALID_REASON = 'invalidReason'
ORIGIN = 'origin' 
RTL = 'rtl' 
LTR = 'ltr' 
NA = 'n/a' 
YES = 'yes'
NO = 'no'
DEFAULT = 'default'
XML_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

reObjAddOne = re.compile('\d$', re.A) # ASCII-only match
reDataStream = re.compile('(>[^$<])')  
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
    
def processErrorList(report, error_list):    
    # output info, warnings, errors
    for msg in error_list:
        
        # msg is a pair -- string & code
        if msg[1] == 0:
            report.Info(msg[0])
        elif msg[1] == 1:
            report.Warning(msg[0])
        else: # error=2
            report.Error(msg[0])

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
    
def convertXMLEntryToColoredString(entryElement, isRtl):
    
    fullLemma = getXMLEntryText(entryElement)
    
    # Create a <p> html element
    paragraph_element = ET.Element('p')
    
    # Collect all the symbols
    symbols = []
    for symbol in entryElement.findall('s'):
        
        # the symbol looks like: <s n="pro" />, so get the 'n' attribute
        if 'n' in symbol.attrib:
            
            symbols.append(symbol.attrib['n'])

    colorInnerLU(fullLemma, symbols, paragraph_element, isRtl, show_unk=True)
    
    retStr = '<p>'
    
    # Instead of using toString, build the string manually, this way we can substitute
    # in the text portion stuff for better display
    for spanEl in paragraph_element:
        
        retStr += f'<{spanEl.tag} '
        
        for key, val in spanEl.attrib.items():
            
            retStr += f'{key}="{val}" '
            
        retStr += 'style="white-space: nowrap;"'
        retStr += f'>'
        
        # substitute a space with a non-breaking space and a hypen with a non-breaking hyphen
        textPart = re.sub(' ', '&nbsp;', spanEl.text)
        textPart = re.sub('-', '&#8209;', textPart)
        
        retStr += textPart
        retStr += f'</{spanEl.tag}>'
        
    retStr += '</p>'
    
    return retStr

# Search for a text name in the list of texts in FLEx
def findTextName(TargetDB, myTextName, textNameList):
    foundText = False
    
    if len(textNameList) == 0:
        
        for text in TargetDB.ObjectsIn(ITextRepository):
            
            tName = ITsString(text.Name.BestVernacularAnalysisAlternative).Text
            textNameList.append(tName)
            
            if myTextName == tName:
                
                foundText = True
    else:
        if myTextName in textNameList:
            
            foundText = True
            
    return foundText

# Create a unique text title for FLEx
def createUniqueTitle(DB, title):
      
    textNameList = []
    
    if findTextName(DB, title, textNameList):
        
        title += ' - Copy'
        if findTextName(DB, title, textNameList): 
            
            done = False
            i = 2
            
            while not done: 
                
                tryName = title + ' (' + str(i) + ')'
                
                if not findTextName(DB, tryName, textNameList): 
                    
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
        

## Testbed classes
# Models a single FLExTrans lexical unit
# A lexical unit consists of a headword, a sense number, a grammatical category 
# and zero or more tags which could be affix glosses, inflection feature abbreviations, etc.
class LexicalUnit():
    # You initialize the class in two ways
    # 1) give a string and it parses it and sets the members
    # 2) give it a <lexicalUnit> xml object (ElementTree.Element) and it sets the members
    def __init__(self, str2Parse=None, luNode=None):
        self.__headWord = None
        self.__senseNum = None
        self.__gramCat = None
        self.__otherTags = []
        self.__badly_formed = False 
        self.__formatedString = None
        self.__plainString = None
        
        if str2Parse != None:
            self.__inStr = str2Parse
            self.__parse()
        elif luNode != None:
            self.__luNode = luNode
            self.__unpackXML()
    def getHeadWord(self):
        return self.__headWord
    def getSenseNum(self):
        return self.__senseNum
    def getGramCat(self):
        return self.__gramCat
    def getOtherTags(self):
        return self.__otherTags
    def isWellFormed(self):
        if self.__badly_formed == True:
            return False
        else:
            if self.__gramCat != SENT:
                # Do a detailed check of well-formedness
                if self.__headWord == None or self.__senseNum == None or self.__gramCat == None:
                    return False
                if len(self.__headWord) < 1 or len(self.__senseNum) < 1 or len(self.__gramCat) < 1:
                    return False
                # Check homograph #
                if not self.__headWord[-1].isdigit():
                    return False
                # Check senseNum
                if not self.__senseNum.isdigit():
                    return False
            
    def toString(self):
        
        if self.__plainString == None:
            
            ret_str = self.__headWord
            
            if self.__gramCat != SENT:
                ret_str += '.' + self.__senseNum
                
            ret_str += ' ' + self.__gramCat
            
            for tag in self.__otherTags:
                ret_str += ' ' + tag
                
            self.__plainString = ret_str
            
        return self.__plainString
    
    def toFormattedString(self, rtl = False):
        
        if self.__formatedString == None:
            
            # Create an element
            p = ET.Element('span')
            
            # Split off the homograph_num (if present; sent punctuation won't have it)
            lemma_parts = re.split('(\d+)', self.__headWord, re.A) # last item is empty re.A=ASCII-only match
            
            # Output the lexeme
            span = output_span(p, LEMMA_COLOR, lemma_parts[0], rtl)
        
            # Output the subscript homograph # and sense # (if they exist)
            if self.__gramCat != SENT:
                add_subscript(span, lemma_parts[1]+'.'+self.__senseNum)
            
            # Check for RTL
            if rtl == True:
                # prepend the RTL marker
                symb = '\u200F' + self.__gramCat
            else:
                symb = self.__gramCat
            
            # output the symbol
            output_span(p, GRAM_CAT_COLOR, ' '+symb, rtl)
            
            for tag in self.__otherTags:
            
                # Check for RTL
                if rtl == True:
                    # prepend the RTL marker
                    symb = '\u200F' + tag
                else:
                    symb = tag
                
                # output the symbol
                output_span(p, AFFIX_COLOR, ' '+symb, rtl)
            
            self.__formatedString = ET.tostring(p, encoding='unicode')
        else:
            pass
            
        return self.__formatedString
    
    def toApertiumString(self):
        ret_str = '^' + self.__headWord
        if self.__gramCat != SENT:
            ret_str += '.' + self.__senseNum
        ret_str += '<' + self.__gramCat + '>'
        for tag in self.__otherTags:
            ret_str += '<' + tag + '>'
        ret_str += '$'
        return ret_str
    
    def __parse(self):
        if re.search('>', self.__inStr):
            self.__parseApertiumStyle()
        else:    
            self.__parsePlainText()
            
    def __unpackXML(self):
        self.__headWord = self.__luNode.find(HEAD_WORD).text
        self.__senseNum = self.__luNode.find(SENSE_NUM).text
        self.__gramCat = self.__luNode.find(GRAM_CAT).text
        for tagNode in list(self.__luNode.find(OTHER_TAGS)):
            self.__otherTags.append(tagNode.text)
        
    def __parseApertiumStyle(self):
        
        # Split off the symbols from the lemma in the lexical unit
        tokens = re.split('<|>', self.__inStr)
        
        #Python 2 code: tokens = filter(None, tokens) # filter out the empty strings
        tokens = [_f for _f in tokens if _f] # filter out the empty strings
        
        # If we have less than 2 items, it's badly_formed. We need at least a value plus it's gramm. category
        if len(tokens) < 2:
            self.__badly_formed = True
            return
        
        # lemma (e.g. haus1.1) is the first one
        lemma = tokens.pop(0)
        
        # gram. cat. is the next one
        self.__gramCat = tokens.pop(0)
        
        # if sentence punctuation, don't assign sense number
        if self.__gramCat != SENT:
            myResult = lemma.split('.')
            if len(myResult) != 2:
                self.__badly_formed = True
                return 
            else:
                (self.__headWord, self.__senseNum) = myResult
        else:
            self.__headWord = lemma
        
        self.__otherTags = tokens
        
    def __parsePlainText(self):
        
        tokens = re.split(' ',  self.__inStr)
        
        # If we have less than 2 items, it's badly_formed. We need at least a headword plus it's gramm. category
        if len(tokens) < 2:
            self.__badly_formed = True
            return    
        
        # lemma (e.g. haus1.1) is the first one
        lemma = tokens.pop(0)
        
        # gram. cat. is the next one
        self.__gramCat = tokens.pop(0)
        
        # split off the sense #
        myResult = lemma.split('.')
        if len(myResult) != 2:
            self.__badly_formed = True
            return 
        else:
            (self.__headWord, self.__senseNum) = myResult
            
        self.__otherTags = tokens

# This class helps you to parse multiple lexical units in a string
# into LexicalUnit objects        
# It contains a list of LexicalUnit objects
class LexicalUnitParser():
    
    def __init__(self, string2Parse):
        self.__inputStr = string2Parse
        self.__badly_formed = False
        self.__lexUnitList = []
        self.__parse()
    
    def isWellFormed(self):
        return not self.__badly_formed    
    def __parse(self):
        if re.search('>', self.__inputStr):
            self.__parseApertiumStyle()
        else:    
            self.__parsePlainText()
    
    def __parseApertiumStyle(self):
        myStr = self.__inputStr
        
        luStr = split_compounds(myStr)
        
        tokens = re.split('\^|\$', luStr)
        
        # If we have less than 2 tokens, there is something wrong. It may mean there are no ^$ delimiters
        if len(tokens) < 2:
            self.__badly_formed = True
            return
        
        # process pairs of tokens (white space and lexical unit)
        # we only care about the 2nd item in the pair, the lexical unit
        for j in range(0,len(tokens)-1,2):
    
            lu = LexicalUnit(tokens[j+1])
            if lu.isWellFormed() == False:
                self.__badly_formed = True
                return
            self.__lexUnitList.append(lu)
        
    def __parsePlainText(self):
        myStr = self.__inputStr
        
        # Split on the . that's between homograph # and sense #
        # We'll get something like: ['ich1', '1 pro lieben2', '2 v 1/3SG dich3', '44 pro suf1 suf2']
        tokens = re.split('\.', myStr)
        
        # Go through the tokens
        for i, tok in enumerate(tokens):
            
            # first one is just the headword
            if i == 0:
                # save the headword
                headword = tok
                
            # last one - everything but the headword which we get from the previous save of headword
            elif i == len(tokens)-1:
                
                # build the lu
                luStr = headword+'.'+tok
                
                # initialize a Lexical unit object with the string
                lu = LexicalUnit(luStr)
                
                # check if it's valid
                if lu.isWellFormed() == False:
                    self.__badly_formed = True
                    return 
                
                # Add it to the list
                self.__lexUnitList.append(lu)
                
            else: # not first or last - use the saved headword and add the current token
                #   except for the last word which is the next headword
                
                # separate on space  
                subTokens = re.split(' ', tok)

                # build the lu
                luStr = headword+'.'+' '.join(subTokens[0:-1])
                
                # save the headword
                headword = subTokens[-1]
                
                # initialize a Lexical unit object with the string
                lu = LexicalUnit(luStr)
                
                # check if it's valid
                if lu.isWellFormed() == False:
                    self.__badly_formed = True
                    return 
                
                # Add it to the list
                self.__lexUnitList.append(lu)
        
        if len(self.__lexUnitList) == 0:
            self.__badly_formed = True
                
    def getLexicalUnits(self):
        return self.__lexUnitList 

# Models the test element portion of the testbed XML file
# It contains a list of LexicalUnit objects
class TestbedTestXMLObject():
    # You can initialize this class in two ways:
    # 1) Give it a list of LexicalUnit objects + origin + synthesis result and it creates the testbed XML object
    # 2) Give it a <test> XML object (ElementTree.Element) and it initializes the LexicalUnit List
    def __init__(self, luList=None, origin=None, synthResult=None, testNode=None, luCache={}):
        self.__luList = luList
        self.__origin = origin
        self.__synthResult = synthResult
        self.__testNode = testNode
        self.__testChanged = False
        self.__actResult = None
        self.__expResult = None
        self.__luCache = luCache
        
        # If no lexical unit object list is given, create it
        if luList == None:
            self.__createLUListFromXMLStructure()
        else:
            self.__createXMLStructureFromLUList()
            
    def getFailedAndInvalid(self):
        invalidCount = 0
        failedCount = 0
        
        if self.isValid():
            if self.getExpectedResult() != self.getActualResult():
                failedCount = 1
        else:
            invalidCount = 1
    
        return (failedCount, invalidCount)
    
    def getLexicalUnitList(self):
        return self.__luList
    
    def __createLUListFromXMLStructure(self):
        self.__luList = []

        sourceInputNode = self.__testNode.find(SOURCE_INPUT)
        lexicalUnitsNode = sourceInputNode.find(LEXICAL_UNITS)
        
        # Go through all the lexical units 
        for luNode in list(lexicalUnitsNode):

            # Do hash on headword + sense number + tags concatenated (don't need gramm. cat since x1.1 will generally have same gramm. cat)            
            tags = ''.join([x.text for x in list(luNode.find(OTHER_TAGS))])
            myHash = hash(tuple((luNode.find(HEAD_WORD).text, luNode.find(SENSE_NUM).text, tags)))
            
            # See if this hash value is in the cache and if so use it.
            if myHash in self.__luCache:
                
                lu = self.__luCache[myHash]
            else:
                lu = LexicalUnit(None, luNode) # 1st param is str2parse
                self.__luCache[myHash] = lu
                
            self.__luList.append(lu)
            
    def __createXMLStructureFromLUList(self):
        self.__testNode = ET.Element(TEST)
        self.__testNode.attrib[ID] = str(uuid.uuid4())
        self.__testNode.attrib[IS_VALID] = YES
        sourceInput = ET.SubElement(self.__testNode, SOURCE_INPUT)
        sourceInput.attrib[ORIGIN] = self.__origin
        lexicalUnitsXML = ET.SubElement(sourceInput, LEXICAL_UNITS)
        
        for lu in self.__luList:
            lexicalUnitXML = ET.Element(LEXICAL_UNIT)
            lexicalUnitsXML.append(lexicalUnitXML)
            headWord = ET.SubElement(lexicalUnitXML, HEAD_WORD)
            headWord.text = lu.getHeadWord()
            senseNum = ET.SubElement(lexicalUnitXML, SENSE_NUM)
            grammaticalCategoryTag = ET.SubElement(lexicalUnitXML, GRAM_CAT)
            grammaticalCategoryTag.text = lu.getGramCat()
            
            if grammaticalCategoryTag.text != SENT:       
                senseNum.text = lu.getSenseNum()
            else:
                senseNum.text = NA
            
            otherTags = ET.SubElement(lexicalUnitXML, OTHER_TAGS)
            for myTag in lu.getOtherTags():
                tag = ET.Element(TAG)
                otherTags.append(tag)
                tag.text = myTag
        
        targetOutput = ET.SubElement(self.__testNode, TARGET_OUTPUT)
        expectedResult = ET.SubElement(targetOutput, EXPECTED_RESULT)
        expectedResult.text = self.__synthResult
        ET.SubElement(targetOutput, ACTUAL_RESULT)
    
    def getID(self):
        return self.__testNode.attrib[ID]
    def isValid(self):
        if self.__testNode.attrib[IS_VALID] == YES:
            return True
        return False
    def getOrigin(self):
        return self.__testNode.find(SOURCE_INPUT).attrib[ORIGIN]
    def getExpectedResult(self):
        if self.__expResult == None:
            self.__expResult = self.__testNode.find(TGT_EXPECTED).text
        return self.__expResult
    def getActualResult(self):
        if self.__actResult == None:
            self.__actResult = self.__testNode.find(TGT_ACTUAL).text
        return self.__actResult
    def setActualResult(self, myStr):
        self.__testNode.find(TARGET_OUTPUT+'/'+ACTUAL_RESULT).text = myStr
    def getTestNode(self):
        return self.__testNode
    # Convert all the lexical units into one string    
    def getLUString(self):
        ret_str = ''
        
        for lu in self.__luList:
            ret_str += ' ' + lu.toString()
        
        return ret_str.strip()
    # Return colorized html form of all LUs
    def getFormattedLUString(self, rtl=False):
        ret_str = ''
        
        for lu in self.__luList:
            ret_str += ' ' + lu.toFormattedString(rtl)
        
        return ret_str.strip()
    
    def getApertiumString(self):
        ret_str = ''
        
        for lu in self.__luList:
            myStr = lu.toApertiumString()
            if re.search(SENT_TAG, myStr):
                ret_str += lu.toApertiumString()
            else:
                ret_str += ' ' + lu.toApertiumString()
            
        return ret_str.strip()
    
    # See if this object is equal to another object in terms of the lexical unit portion
    def equalLexUnits(self, myTestObj):
        localLUString = self.getLUString()
        cmpLUString = myTestObj.getLUString()
        
        if localLUString == cmpLUString:
            return True
        
        return False 

    def getInvalidReason(self):
        testNode = self.getTestNode()
        if INVALID_REASON in testNode.attrib:
            return testNode.attrib[INVALID_REASON]
        return ''
    
    def validate(self, myValidator):
        markInvalid = False
        reasonChanged = False
        
        testNode = self.getTestNode()

        if testNode.attrib[IS_VALID] == YES:
            prevInvalidFlag = True
        else:
            prevInvalidFlag = False

        for lu in self.__luList:
            
            # any one invalid lexical unit means the test is invalid
            if myValidator.isValid(lu) == False:
                
                # get the reason it was invalid
                reason = myValidator.getInvalidReason()
                
                # see if the reason it was invalid changed
                if reason != self.getInvalidReason():
                    reasonChanged = True
                    
                markInvalid = True
                break
        
        # See if we have a different value from before
        if markInvalid == prevInvalidFlag or reasonChanged:
            
            self.__testChanged = True
            
            if markInvalid:
                testNode.attrib[IS_VALID] = NO
                testNode.attrib[INVALID_REASON] = reason
            else:
                testNode.attrib[IS_VALID] = YES
                testNode.attrib[INVALID_REASON] = ''
    
    def didTestChange(self):
        return self.__testChanged
       
    def getTest(self):
        
        LUStr = self.getLUString()
        ResultStr = self.getExpectedResult()
        
        return [LUStr, ResultStr]
             
    def dump(self, f_out):
        
        # each test goes on its own line. Add a dummy EOL lexical unit so that
        # transfer rules don't go to the next line unintentially 
        f_out.write(self.getApertiumString() + ' ^EOL<eol>$\n')

    def extractResults(self, f_out):
        
        try:
            # each test goes on its own line
            line = f_out.readline()
        except:
            raise ValueError('No more lines to read in the synthesis file.')
        
        # Remove the dummy EOL lexical unit at the end.
        line = re.sub(r' @*EOL', '', line)
        
        # Remove multiple spaces
        line = re.sub('\s{2,}', ' ', line)
        line = line.rstrip()
        self.setActualResult(line)
        return 1
    
# Models the top-level testbed XML object        
# It contains a list of TestXMLObjects 
class FLExTransTestbedXMLObject():
    # You can create this class in two ways:
    # 1) initialize a new one which creates the basic structure without test elements
    # 2) initialize from an existing XML node which fills out everything including a list of TestXMLObjects 
    def __init__(self, root, direction):
        self.__rootNode = root
        self.__TestXMLObjectList = []
        self.__direction = direction
        self.__testbedChanged = False
        self.__testCache = {}
        self.__luCache = {}
        self.__failedAndInvalid = None
        
        # if new (tree==None), create the structure down to the tests node
        if root == None:
            self.__initBasicStructure()
            
        # else we assume we have a full structure create a list of test nodes
        else:
            self.__direction = self.__rootNode.attrib[SOURCE_DIRECTION] # direction passed in is ignored
            self.__testsNode = self.__getTestsNode()
            self.__createTestXMLObjectList()
    
    def __initBasicStructure(self):
        self.__rootNode = ET.Element(FLEXTRANS_TESTBED)
        self.__rootNode.attrib[SOURCE_DIRECTION] = self.__direction
        testbeds = ET.SubElement(self.__rootNode, TESTBEDS)
        testbed = ET.SubElement(testbeds, TESTBED)
        testbed.attrib[N_ATTRIB] = DEFAULT
        self.__testsNode = ET.SubElement(testbed, TESTS)
    
    def getFailedAndInvalid(self):
        
        if self.__failedAndInvalid == None:
                
            tot_failed = 0
            tot_invalid = 0
            for test in self.__TestXMLObjectList:
                (failed, invalid) = test.getFailedAndInvalid()
                tot_failed += failed
                tot_invalid += invalid
            
            self.__failedAndInvalid = (tot_failed, tot_invalid)
            
        return self.__failedAndInvalid
            
    def getNumTests(self):
        return len(self.__TestXMLObjectList)
        
    def getRoot(self):
        return self.__rootNode
    
    def getDirection(self):
        return self.__direction
    
    def addToTestbed(self, newTestObj):
        newNode = newTestObj.getTestNode()
        self.__testsNode.append(newNode)
    
    def overwriteInTestbed(self, oldTestObj, newTestObj):
        # get the id for the old test
        oldId = oldTestObj.getID()
        
        # loop through all the tests until we get a match
        for i, testNode  in enumerate(list(self.__testsNode)):
            # when we find it, remove it and replace with the new 
            currId = testNode.attrib[ID]
            if currId == oldId:
                newNode = newTestObj.getTestNode()
                self.__testsNode.insert(i, newNode)
                self.__testsNode.remove(testNode)
                break
            
    def __getTestsNode(self):
        # For now we assume just one testbed (named 'default')
        # In the future we will support a user selected testbed or testbeds
        return self.__rootNode.find(TESTBEDS+'/'+TESTBED+'/'+TESTS)
    
    def getTestXMLObjectList(self):
        return self.__TestXMLObjectList
    
    def __createTestXMLObjectList(self):
        # loop through all the tests 
        for testNode in list(self.__testsNode):
            
            # Make a hash key based on expected result text plus # lexical units
            #numLexUnits = len(testNode.findall('./'+SOURCE_INPUT+'/'+LEXICAL_UNITS+'/'+LEXICAL_UNIT))
            #targetNode = testNode.find(TARGET_OUTPUT)
            myHash = 0#  hash(tuple((targetNode.find(EXPECTED_RESULT).text, targetNode.find(ACTUAL_RESULT).text, numLexUnits)))
            
            # See if this hash value is in the cache and if so use it.
            if myHash in self.__testCache:
                
                newTestXMLObj = self.__testCache[myHash]
            else:
                # Initialize a result object and add it to the list
                newTestXMLObj = TestbedTestXMLObject(None, None, None, testNode, self.__luCache) # luList=None, origin=None, synthResult=None
                #self.__testCache[myHash] = newTestXMLObj
                
            self.__TestXMLObjectList.append(newTestXMLObj)
    
    def validate(self, DB, report):
        
        myValidator = TestbedValidator.TestbedValidator(DB, report)
        
        for testXMLObj in self.__TestXMLObjectList:
            testXMLObj.validate(myValidator)
            if testXMLObj.didTestChange() == True:
                self.__testbedChanged = True
    
    def didTestbedChange(self):
        return self.__testbedChanged
    
    def dump(self, f_out):
        
        for obj in self.__TestXMLObjectList:     
            obj.dump(f_out)
        
        # return the number of tests dumped
        return(len(self.__TestXMLObjectList))    

    def getTestsList(self):
        
        myTestsList = []
        
        for obj in self.__TestXMLObjectList:     
            test = obj.getTest()
            myTestsList.append(test)
        
        # return the list
        return(myTestsList)    

    def extractResults(self, f_out):
        total = 0
        
        for obj in self.__TestXMLObjectList:     
            total += obj.extractResults(f_out)
        
        return total    

    def isRTL(self):    
        
        if self.getDirection() == RTL:
            return True
        return False

# Models the testbed XML file.
# It creates the XML file if it doesn't exist.
class FlexTransTestbedFile():
    def __init__(self, direction, report):
        
        self.__isNew = False
        
        configMap = MyReadConfig.readConfig(report)
        if not configMap:
            raise ValueError()
    
        self.__testbedPath = MyReadConfig.getConfigVal(configMap, MyReadConfig.TESTBED_FILE, report)
        if not self.__testbedPath:
            raise ValueError()
        
        # Get the composed characters setting
        composed = MyReadConfig.getConfigVal(configMap, MyReadConfig.COMPOSED_CHARACTERS, report)
        if not composed:
            raise ValueError()
        
        if composed == 'y':
            
            self.composed = True
        else:
            self.composed = False
            
        # check if the file exists
        if os.path.exists(self.__testbedPath) == False:
            
            # we will create it
            self.__isNew = True
            self.__XMLObject = FLExTransTestbedXMLObject(None, direction)
            myRoot = self.__XMLObject.getRoot()
            self.__testbedTree = ET.ElementTree(myRoot)
        else:
            try:
                # Open the testbed file
                f = open(self.__testbedPath, encoding='utf-8')
                lines = f.readlines()
                f.close()
                
                # Convert the file to decomposed form. All the FLEx values are decomposed so standardize on NFD when we read it in.
                for i in range(0, len(lines)):
                    
                    lines[i] = unicodedata.normalize('NFD', lines[i])
                        
                f = open(self.__testbedPath, 'w', encoding='utf-8')
                f.writelines(lines)
                f.close()
                
            except:
                raise ValueError('The testbed file: ' + self.__testbedPath + ' could not be read or written.')
            
            try:
                self.__testbedTree = ET.parse(self.__testbedPath)
            except:
                raise ValueError('The testbed file: ' + self.__testbedPath + ' is invalid.')

            self.__XMLObject = FLExTransTestbedXMLObject(self.__testbedTree.getroot(), direction)
    
    def getFLExTransTestbedXMLObject(self):
        return self.__XMLObject
    
    def isNew(self):
        return self.__isNew
    
    def exists(self):
        return not self.__isNew
    
    def validate(self, DB, report):
        
        self.__XMLObject.validate(DB, report)
        
        # Only rewrite the testbed XML file if there was a change
        if self.__XMLObject.didTestbedChange() == True:
            
            self.write()

    def write(self):
        self.__testbedTree.write(self.__testbedPath, encoding='utf-8', xml_declaration=True)
        
        # Re-open the testbed file
        f = open(self.__testbedPath, encoding='utf-8')
        lines = f.readlines()
        f.close()
        
        # Convert the file to composed or decomposed as set in the config file.
        for i in range(0, len(lines)):
            
            if self.composed == True:
                
                lines[i] = unicodedata.normalize('NFC', lines[i])
            else:
                lines[i] = unicodedata.normalize('NFD', lines[i])
                
        # Add the DOCTYPE declaration
        lines.insert(1, '<!DOCTYPE FLExTransTestbed PUBLIC "-//XMLmind//DTD FLExTransTestbed//EN" "FLExTransTestbed.dtd">\n')
        f = open(self.__testbedPath, 'w', encoding='utf-8')
        f.writelines(lines)
        f.close()

# Models the result part of the XML structure for a results log
# It contains a list of FLExTransTestbedXMLObject's
class TestbedResultXMLObject():
    # You can initialize this class in two ways:
    # 1) Give just a parent element and it creates an empty <result> element for the parent
    # 2) Give it a <result> XML object (ElementTree.Element) and it initializes the testbed object list from the testbed xml elements.
    def __init__(self, parentNode, rootNode=None, luCache={}, testCache={}):
        self.__rootNode = rootNode
        self.__testbedXMLObjList = []
        
        if rootNode == None:
            self.__rootNode = ET.Element(TESTBED_RESULT)
            
            # The new <result> element alwasy goes at the top
            parentNode.insert(0, self.__rootNode)
            
        else:
            for testbedNode in list(self.__rootNode):
                # create a testbed object and add it to the list
                testbedXMLObj = FLExTransTestbedXMLObject(testbedNode, None) # direction is None
                self.__testbedXMLObjList.append(testbedXMLObj)
    
    def getFLExTransTestbedXMLObjectList(self):
        return self.__testbedXMLObjList
    
    def getRoot(self):
        return self.__rootNode
    
    def getStartDateTime(self):
        return self.__rootNode.attrib[START_DATE_TIME]
        
    def getEndDateTime(self):
        return self.__rootNode.attrib[END_DATE_TIME]
        
    def getFailedAndInvalid(self):
        tot_failed = 0
        tot_invalid = 0
        for testbed in self.__testbedXMLObjList:
            (failed, invalid) = testbed.getFailedAndInvalid()
            tot_failed += failed
            tot_invalid += invalid
        return (tot_failed, tot_invalid)
    
    def getNumTests(self):
        total = 0
        for testbed in self.__testbedXMLObjList:
            total += testbed.getNumTests()
        return total
    
    def isIncomplete(self):
        if self.__rootNode.attrib[END_DATE_TIME] == '':
            return True
        return False
   
    def endTest(self):
        self.__rootNode.attrib[END_DATE_TIME] = datetime.now().strftime(XML_DATETIME_FORMAT)

    def startTest(self, testbedXMLObj):
        self.__rootNode.attrib[START_DATE_TIME] = datetime.now().strftime(XML_DATETIME_FORMAT)
        self.__rootNode.attrib[END_DATE_TIME] = ''
        
        # add the <FLExTransTestbed> element below the <testResult> element
        self.__rootNode.append(testbedXMLObj.getRoot())
        
        # add the testbed object to the internal list
        self.__testbedXMLObjList.append(testbedXMLObj)
    
    def dump(self, f_out):
        total = 0
        for obj in self.__testbedXMLObjList:
            total += obj.dump(f_out)
        
        return total
    
    def extractResults(self, f_out):
        total = 0
        for obj in self.__testbedXMLObjList:
            total += obj.extractResults(f_out)
        
        return total

    def isRTL(self):    
        for obj in self.__testbedXMLObjList:
            if obj.isRTL():
                return True
        return False
    
# Models the testbed results top XML element        
# It contains a list of TestResultXMLObjects 
class FLExTransTestbedResultsXMLObject():
    # You can create this class in two ways:
    # 1) initialize a new one which creates the basic structure without result elements
    # 2) initialize from an existing XML node which fills out everything including a list of TestbedResultXMLObjects 
    def __init__(self, root=None):
        self.__rootNode = root
        self.__resultXMLObjList = []
        self.__luCache = {}
        self.__testCache = {}
        if root == None:
            self.__rootNode = ET.Element(FLEXTRANS_TESTBED_RESULTS)
        else:
            self.__createTestbedResultXMLObjectList()
    
    def getTestbedResultXMLObjectList(self):
        return self.__resultXMLObjList
    
    def initTestResult(self, testbedXMLObj):
        
        # create a new result object and set the start time and give it a blank end time
        resultXMLObj = TestbedResultXMLObject(self.__rootNode, None, None)
        resultXMLObj.startTest(testbedXMLObj)
        
        # new results are always put at the top of the list
        self.__resultXMLObjList.insert(0, resultXMLObj)
    
    def endTest(self):
        # get the top result object and set the end time 
        self.__resultXMLObjList[0].endTest() 
        
    def getRoot(self):
        return self.__rootNode
    
    def __createTestbedResultXMLObjectList(self):
        # loop through all the result objects 
        for resultNode in list(self.__rootNode):

            # initialize a result object and add it to the list
            newResultXMLObj = TestbedResultXMLObject(None, resultNode, self.__luCache, self.__testCache)
            self.__resultXMLObjList.append(newResultXMLObj)

    def dump(self, f_out):
        # dump the testbed contents from the topmost result object
        return self.__resultXMLObjList[0].dump(f_out)

    def initializedTestMissing(self):
        
        # See if there are any results objects
        if len(self.__resultXMLObjList) < 1:
            return True
        
        resultObj = self.__resultXMLObjList[0]
        resultNode = resultObj.getRoot()
        
        # We expect the end date-time to be '' when a result is ready
        # to have its actual results filled in
        if len(resultNode.attrib[END_DATE_TIME]) < 1:
            return False
        return True
    
    def extractResults(self, f_out):
        # check that there was a test started
        if self.initializedTestMissing() == True:
            return 0
        else:
            return self.__resultXMLObjList[0].extractResults(f_out)
        
    def isRTL(self):
        
        for result in self.__resultXMLObjList:
            if result.isRTL():
                return True
        return False

# Models the results log XML file.
# It creates the XML file if it doesn't exist.
class FlexTransTestbedResultsFile():
    def __init__(self, report):

        configMap = MyReadConfig.readConfig(report)
        if not configMap:
            raise ValueError()
    
        resultsPath = MyReadConfig.getConfigVal(configMap, MyReadConfig.TESTBED_RESULTS_FILE, report)
        if not resultsPath:
            raise ValueError()
        
        self.__resultsPath = resultsPath

        if os.path.exists(resultsPath) == False:
            
            self.__XMLObject = FLExTransTestbedResultsXMLObject()
            myRoot = self.__XMLObject.getRoot()
            self.__testbedResultsTree  = ET.ElementTree(myRoot)
        else:
            try:
                self.__testbedResultsTree = ET.parse(resultsPath)
            except:
                raise ValueError(f'The testbed results file: {resultsPath} is invalid.')

            self.__XMLObject = FLExTransTestbedResultsXMLObject(self.__testbedResultsTree.getroot())
    
    def getResultsXMLObj(self):
        return self.__XMLObject
    
    def write(self):
        self.__testbedResultsTree.write(self.__resultsPath, encoding='utf-8', xml_declaration=True)

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
    cwd = os.getcwd()
    
    flexToolsPath = turnPathIntoEnvironPath(absPathToBuildFolder, cwd)

    # make a variable for where the apertium executable files and dlls are found
    outStr += f'set {MAKEFILE_FLEXTOOLS_VARIABLE}={flexToolsPath}\n' 
    
    # set path to nothing
    outStr += f'set PATH=""\n' 
    
    # Put quotes around the path in case there's a space
    outStr += f'cd "{absPathToBuildFolder}"\n'
    
    #fullPathErrFile = os.path.join(absPathToBuildFolder, APERTIUM_ERROR_FILE)
    outStr += f'"{cwd}\\make" 2>"{APERTIUM_ERROR_FILE}"\n'
    
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

def unfixProblemChars(fullDictionaryPath, fullTransferResultsPath):

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
    
    # Restore original bilingual dictionary
    shutil.copy2(fullDictionaryPath+'.before_fix', fullDictionaryPath)

    # Delete the temporary dictionary file
    os.remove(fullDictionaryPath+'.before_fix')
    
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

# Create a span element and set the color and text
def output_span(parent, color, text_str, rtl):
    
    span = ET.Element('span')
    parent.append(span)
    span.attrib['style'] = 'color:#' + color
    
    # Check for RTL
    if rtl == True:
        # prepend the RTL marker
        text_str = '\u200F'+text_str
        
    span.text = text_str
    
    return span

def add_subscript(span, num):
    
    sub = ET.Element('sub')
    sub.attrib['style'] = 'font-size:' + SUBSCRIPT_SIZE_PERCENTAGE + '%'
    span.append(sub)
    sub.text = num
        
def process_chunk_lexical_unit(lu_str, parent_element, rtl):
    # Split off the symbols from the lemma in the lexical unit (which is i+1)
    symbols = re.split('<|>', lu_str)
    symbols = [_f for _f in symbols if _f] # filter out the empty strings
    
    # Lemma is the first one
    lemma = symbols.pop(0)
    
    # if the first symbol is UNK, use a special lemma color
    if len(symbols) > 0 and symbols[0] == 'UNK':
        lexeme_color = UNKNOWN_LEMMA_COLOR
    else:
        lexeme_color = CHUNK_LEMMA_COLOR
    
    # Output the lexeme
    output_span(parent_element, lexeme_color, lemma, rtl)
    
    # Loop through the symbols
    for i, symb in enumerate(symbols):
        # Check for unknown category
        if symb == 'UNK':
            symbol_color = UNKNOWN_CAT_COLOR
        elif i == 0:
            symbol_color = CHUNK_GRAM_CAT_COLOR
        else:
            symbol_color = CHUNK_AFFIX_COLOR
        
        # Check for RTL
        if rtl == True:
            # prepend the RTL marker
            symb = '\u200F' + symb
        
        # output the symbol
        output_span(parent_element, symbol_color, ' '+symb, rtl)

def colorInnerLU(lemma, symbols, parent_element, rtl, show_unk):

    # Split off the homograph_num.sense_num (if present; sent punctuation won't have it)
    lemma_parts = re.split('(\d+\.\d+)', lemma, re.A) # last item is empty, re.A=ASCII only match
    
    # Check for an @
    if lemma_parts[0][0] == '@':
        # color it red for not found
        lexeme_color = NOT_FOUND_COLOR
        
        # remove the @
        lemma_parts[0] = lemma_parts[0][1:]
        
    # if the first symbol is UNK, use a special lemma color
    elif len(symbols) > 0 and symbols[0] == 'UNK':
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
            symb = '\u200F' + symb
        
        # output the symbol
        output_span(parent_element, symbol_color, ' '+symb, rtl)

# Split a compound from one lexical unit containing multiple words to multiple
def process_lexical_unit(lu_str, parent_element, rtl, show_unk):
    # Split off the symbols from the lemma in the lexical unit (which is i+1)
    symbols = re.split('<|>', lu_str)
    symbols = [_f for _f in symbols if _f] # filter out the empty strings
    
    # Lemma is the first one
    lemma = symbols.pop(0)
    
    colorInnerLU(lemma, symbols, parent_element, rtl, show_unk)
    
# Compound words get put within one ^...$ block. Split them into one per word.
def split_compounds(outStr):
    # Split into tokens where we have a > followed by a character other than $ or < (basically a lexeme)
    # this makes ^room1.1<n>service1.1<n>number1.1<n>$ into ['^room1.1<n', '>s', 'ervice1.1<n', '>n', 'umber1.1<n>$']
    toks = reDataStream.split(outStr)
    
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

"""
# OLD CODE -- TO BE DELETED        
def get_component_count(e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            return entryRef.ComponentLexemesRS.Count

# OLD CODE -- TO BE DELETED        
def get_position_in_component_list(e, complex_e):
    # loop through all entryRefs (we'll use just the complex form one)
    for entryRef in complex_e.EntryRefsOS:
        if entryRef.RefType == 1: # 1=complex form, 0=variant
            # loop through components
            for i, my_e in enumerate(entryRef.ComponentLexemesRS):
                if e == my_e:
                    return i
"""

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

# Convert . (dot) to _ (underscore)
def underscores(inStr):
    return re.sub(r'\.', r'_', inStr)


# The whole text from FLEx
class TextEntirety():
    def __init__(self):
        self.__parList = []
        self.__cmplxFormMap = {}
        self.__discontigCmplxFormMap = {}
        self.__unknownWordMap = {}
        self.__insertedWordsList = []
    def addInsertedWordsList(self, insertList):
        self.__insertedWordsList = insertList
    def addParagraph(self, textPar):
        self.__parList.append(textPar)
    def createGuidMaps(self):
        for par in self.__parList:
            par.createGuidMaps(self.__insertedWordsList)
    def getParagraphs(self):
        return self.__parList
    def getParAndSentIndex(self, sentNum):
        count = 0
        # Find the paragraph that holds this sentence
        for par in self.__parList:
            count += len(par.getSentences())
            if sentNum < count:
                break
        return (count, par)
    # determine which par and index into it to return the right sentence
    def getSent(self, sentNum):
        (count, par) = self.getParAndSentIndex(sentNum)
        if sentNum >= count:
            return None
        return par.getSent(sentNum-(count-len(par.getSentences())))
    def getSentCount(self):
        return sum([x.getSentCount() for x in self.__parList])
    def getSurfaceAndDataTupleListBySent(self):
        tupBySentList = []
        for par in self.__parList:
            par.getSurfaceAndDataTupleListBySent(tupBySentList)
        return tupBySentList
    def hasMultipleUnknownWords(self):
        return self.__multipleUnknownWords
    def haveData(self):
        if len(self.__parList) > 0:
            return True
        return False
    def isLastSentInParagraph(self, sentNum):
        (count, _) = self.getParAndSentIndex(sentNum)
        if sentNum == count-1:
            return True
        return False
    def processComplexForms(self, typesList):
        for par in self.__parList:
            par.findComplexForms(self.__cmplxFormMap, typesList)
        for par in self.__parList:
            par.substituteComplexForms(self.__cmplxFormMap)
    def processDiscontiguousComplexForms(self, typesList, discontigTypesList, discontigPOSList): 
        if typesList == discontigTypesList:
            self.__discontigCmplxFormMap = self.__cmplxFormMap
        else:
            # findDiscontig... method not coded yet !!!!
            for par in self.__parList:
                par.findDiscontiguousComplexForms(self.__discontigCmplxFormMap, discontigTypesList)
        for par in self.__parList:
            par.substituteDiscontiguousComplexForms(self.__discontigCmplxFormMap, discontigPOSList)
    def warnForUnknownWords(self):
        multipleUnknownWords = False
        for par in self.__parList:
            if par.warnForUnknownWords(self.__unknownWordMap) == True:
                multipleUnknownWords = True
        return multipleUnknownWords
    def write(self, fOut):
        for par in self.__parList:
            par.write(fOut)
            
# A paragraph within a FLEx text       
class TextParagraph():
    def __init__(self):
        self.__sentList = []
    def addSentence(self, textSent):
        self.__sentList.append(textSent)
    def createGuidMaps(self, insertList):
        for sent in self.__sentList:
            sent.createGuidMap(insertList)
    def findComplexForms(self, cmplxFormMap, typesList):
        for sent in self.__sentList:
            sent.findComplexForms(cmplxFormMap, typesList)
    def getSent(self, sentNum):
        if sentNum >= len(self.__sentList) or sentNum < 0:
            return None
        return self.__sentList[sentNum]
    def getSentCount(self):
        return len(self.__sentList)
    def getSentences(self):
        return self.__sentList
    def getSurfaceAndDataTupleListBySent(self, tupBySentList):
        for sent in self.__sentList:
            tupList = []
            sent.getSurfaceAndDataTupleList(tupList)
            tupBySentList.append(tupList)
    def substituteComplexForms(self, cmplxFormMap):
        for sent in self.__sentList:
            sent.substituteComplexForms(cmplxFormMap)
    def substituteDiscontiguousComplexForms(self, cmplxFormMap, discontigPOSList):
        for sent in self.__sentList:
            sent.substituteDiscontiguousComplexForms(cmplxFormMap, discontigPOSList)
    def warnForUnknownWords(self, unknownWordMap):
        multipleUnknownWords = False
        for sent in self.__sentList:
            if sent.warnForUnknownWords(unknownWordMap) == True:
                multipleUnknownWords = True
        return multipleUnknownWords
    def write(self, fOut):
        for sent in self.__sentList:
            sent.write(fOut)
        fOut.write('\n')
            
# A sentence within a FLex text paragraph which includes everything FLEx
# considers to be within one segment.
class TextSentence():
    def __init__(self, report):
        self.__report = report
        self.__wordList = []
        self.__guidMap = {}
    def addWord(self, textWord):
        self.__wordList.append(textWord)
    def createGuidMap(self, insertList):
        for word in insertList:
            self.__guidMap[word.getGuid()] = word
        for word in self.__wordList:
            self.__guidMap[word.getGuid()] = word
    def getSurfaceAndDataForGuid(self, guid):
        return self.__guidMap[guid].getSurfaceForm(), self.__guidMap[guid].outputDataStream()
    def getSurfaceAndDataTupleList(self, tupList):
        for word in self.__wordList:
            tupList.append((word.getSurfaceForm(), word.outputDataStream()))
    # Write out final sentence punctuation (possibly multiple)
    def getSurfaceAndDataFinalSentPunc(self):
        tupList = []
        for word in reversed(self.__wordList):
            if word.isSentPunctutationWord():
                tupList.insert(0,(word.getSurfaceForm(), word.outputDataStream()))
            else: # stop on the first non-sent punc. word
                break
        return tupList
    def getSurfaceAndDataPrecedingSentPunc(self):
        tupList = []
        for word in self.__wordList:
            if word.isSentPunctutationWord():
                tupList.append((word.getSurfaceForm(), word.outputDataStream()))
            else: # stop on the first non-sent punc. word
                break
        return tupList
    def getWordCount(self):
        return len(self.__wordList)
    def getWords(self):
        return self.__wordList
    def hasPunctuation(self, myGuid):
        if myGuid in self.__guidMap:
            return self.__guidMap[myGuid].hasPunctuation()
        return False
    def haveGuid(self, myGuid):
        return myGuid in self.__guidMap
    def matchesFirstWord(self, myGuid):
        if len(self.__wordList) > 0:
            if self.__wordList[0].getGuid() == myGuid:
                return True
        return False
    def matchesLastWord(self, myGuid):
        if len(self.__wordList) > 1: # > 1 since we may go back 2 words
            
            if self.__wordList[-1].isSentPunctutationWord():
                last = -2
            else:
                last = -1
            if self.__wordList[last].getGuid() == myGuid:
                return True
        return False
    def write(self, fOut):
        for word in self.__wordList:
            word.write(fOut)
    def writeAfterPunc(self, fOut, myGuid):
        if myGuid in self.__guidMap:
            self.__guidMap[myGuid].writePostPunc(fOut)
    def writeBeforePunc(self, fOut, myGuid):
        if myGuid in self.__guidMap:
            self.__guidMap[myGuid].writePrePunc(fOut)
        
    # Write out final sentence punctuation (possibly multiple)
    def writeFinalSentPunc(self, fOut):
        myList = []
        for word in reversed(self.__wordList):
            if word.isSentPunctutationWord():
                myList.insert(0, word) # add to beg. of list
            else: # stop on the first non-sent punc. word
                break
        for word in myList: # write out in original order
            word.write(fOut)
    
    def writePrePunc(self, wrdNum, fOut):
        if wrdNum <= len(self.__wordList) - 1:
            self.__wordList[wrdNum].writePrePunc(fOut)
             
    # Write out preceeding sentence punctuation (possibly multiple)
    def writePrecedingSentPunc(self, fOut):
        count = 0
        for word in self.__wordList:
            if word.isSentPunctutationWord():
                word.write(fOut)
                count += 1
            else: # stop on the first non-sent punc. word
                break
        return count
    def writePostPunc(self, wrdNum, fOut):
        if wrdNum <= len(self.__wordList) - 1:
            self.__wordList[wrdNum].writePostPunc(fOut)
             
    def writeThisGuid(self, fOut, myGuid):
        self.__guidMap[myGuid].write(fOut)
        
    # Don't write punctuation, just word data
    def writeWordDataForThisGuid(self, fOut, myGuid):
        self.__guidMap[myGuid].writeWordData(fOut)
    
    ### Long methods - in alphabetical order
    
    def findComplexForms(self, cmplxFormMap, typesList):
        # Loop through the word list
        for wrd in self.__wordList:
            if wrd.hasEntries() and wrd.notCompound():
                # Check if we have already found complex forms for this word and cached them
                if wrd.getEntryHandle() not in cmplxFormMap:
                    cmplxEntryTupList = []

                    # Loop through the complex entries for this word
                    for cmplxEntry in wrd.getComplexFormEntries():
                        # Make sure we have entry references of the right type
                        if cmplxEntry.EntryRefsOS:
                            # find the complex entry ref (there could be one or more variant entry refs listed along side the complex entry)
                            for entryRef in cmplxEntry.EntryRefsOS:
                                if entryRef.RefType == 1 and entryRef.ComplexEntryTypesRS: # 1=complex form, 0=variant

                                    # there could be multiple types assigned to a complex form (e.g. Phrasal Verb, Derivative)
                                    # just see if one of them is one of the ones in the types list (e.g. Phrasal Verb)
                                    for complexType in entryRef.ComplexEntryTypesRS:
                                        if ITsString(complexType.Name.BestAnalysisAlternative).Text in typesList:
                                            
                                            # get the component entries
                                            componentEs = []
                                            for cE in entryRef.ComponentLexemesRS:
                                                componentEs.append(cE)
                                            
                                            # add the complex entry and its components to the list
                                            cmplxEntryTupList.append((cmplxEntry, componentEs))
                    
                    # Map from an entry's handle # to the complex entry/components tuple                        
                    cmplxFormMap[wrd.getEntryHandle()] = list(cmplxEntryTupList) # Create a new list in memory
                                            
    def modifyList(self, i, count, complexEn):
        componentList = []
        
        # Loop through the part of the word list that we will remove. Save the components in a list that we will add to the new word.
        for _ in range(0, count):
            componentList.append(self.__wordList.pop(i)) # don't increment, the next one is in position i after the previous pop
        
        # New object
        newWord = TextWord(self.__report)
        
        # Initialize it with the complex entry being the main entry of the word. Other attributes are drawn from the last
        # matching component. Tags will also transferred as needed
        newWord.initWithComplex(complexEn, componentList)
        
        # Insert the new word into the word list
        self.__wordList.insert(i, newWord)
        
        # Update the guid map
        self.__guidMap[newWord.getGuid()] = newWord
        
    def modifyDiscontiguousList(self, i, count, complexEn):
        componentList = []
        
        # we assume count is 2, we want to pop the ith and the i+2th, after the first pop everything moved up so just pop i+1 the 2nd time
        componentList.append(self.__wordList.pop(i))
        componentList.append(self.__wordList.pop(i+1))
        
        # New object
        newWord = TextWord(self.__report)
        
        # Initialize it with the complex entry being the main entry of the word. Other attributes are drawn from the last
        # matching component. Tags will also transferred as needed
        newWord.initWithComplex(complexEn, componentList)
        
        # Insert the new word into the word list after the skipped word
        self.__wordList.insert(i+1, newWord)
        
        # Update the guid map
        self.__guidMap[newWord.getGuid()] = newWord
        
    # See if a bundle is not part of a neighboring complex form
    def notPartOfAdjacentComplexForm(self, currGuid, nextGuid):
        if nextGuid not in self.__guidMap:
            return True
        
        # Get the next word object
        nextWrd = self.__guidMap[nextGuid]
        
        # Check if the current word's bundle guid matches the first component of the next word
        if nextWrd.hasComponents():
            guidFirstComponent = nextWrd.getComponent(0).getGuid()
            if guidFirstComponent == currGuid:
                return False
        return True

    def substituteComplexForms(self, cmplxFormMap):
        i = 0
        # Loop through the word list
        while i < len(self.__wordList) - 1: # we don't have to check the last one, it can't match 2 or more things
            wrd = self.__wordList[i]

            # Process words that have complex entries
            if wrd.getEntryHandle() in cmplxFormMap:
                
                cmplxEnList = cmplxFormMap[wrd.getEntryHandle()]
                
                # We only need to deal with the list that is non-empty
                if len(cmplxEnList) > 0:
                    
                    # Sort the list from most components to least components
                    # each list item is a tuple. See below. We want the length of the component list.
                    cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True)
                    
                    # Loop through the complex entries tuples (cmplxEntry, componentEntryList)
                    for cmplxEn, componentEList in cmplxEnList:
                        match = False
                        
                        count = len(componentEList)

                        # A complex form with only one component doesn't make sense to process
                        if count > 1:
                            # Only continue if we won't go off the end of the list
                            if i + count - 1 < len(self.__wordList):
                                
                                # All components have to match
                                for j in range(0, count):
                                    
                                    # Check if we have a match  
                                    if self.__wordList[i+j].getFirstEntry() == componentEList[j]: # jth component in the list
                                        match = True
                                    else:
                                        match = False
                                        break
                                # break out of the outer loop
                                if match == True:
                                    break
                    if match == True:
                        # pop the matching words from the list and insert the complex word
                        self.modifyList(i, count, cmplxEn)
            i += 1
            
    def substituteDiscontiguousComplexForms(self, cmplxFormMap, discontigPOSList):
        i = 0
        # Loop through the word list
        while i < len(self.__wordList) - 1: # we don't have to check the last one, it can't match 2 or more things
            wrd = self.__wordList[i]

            # Process words that have complex entries
            if wrd.getEntryHandle() in cmplxFormMap:
                
                cmplxEnList = cmplxFormMap[wrd.getEntryHandle()]
                
                # We only need to deal with the list that is non-empty
                if len(cmplxEnList) > 0:
                    
                    # Sort the list from most components to least components
                    # each list item is a tuple. See below. We want the length of the component list.
                    cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True)
                    
                    # Loop through the complex entries tuples (cmplxEntry, componentEntryList)
                    for cmplxEn, componentEList in cmplxEnList:
                        match = False
                        
                        count = len(componentEList)

                        # Only process component lists with two items
                        if count == 2:
                            # Only continue if we won't go off the end of the list
                            if i + 2 < len(self.__wordList):
                                
                                # This word and the word + 2 has to match. Also the inbetween word has to match one of the allowed POSs.
                                if self.__wordList[i].getFirstEntry() == componentEList[0] and \
                                   self.__wordList[i+2].getFirstEntry() == componentEList[1] and \
                                   self.__wordList[i+1].posMatchForMiddleItemInDiscontigousList(discontigPOSList) == True: 

                                    match = True
                                else:
                                    match = False
                                    
                                # break out of the outer loop
                                if match == True:
                                    break
                    if match == True:
                        # pop the matching words from the list and insert the complex word
                        self.modifyDiscontiguousList(i, count, cmplxEn)
            i += 1
            
    def warnForUnknownWords(self, unknownWordMap):
        multipleUnknownWords = False
        for i, word in enumerate(self.__wordList):
            # See if we have an uninitialized word which indicates it's unknown
            if word.isInitialized() == False:
                # Allow some unknown "words" without warning, such as sfm markers
                if len(word.getSurfaceForm()) > 0 and word.getSurfaceForm()[0] == '\\':
                    continue
                if i > 0:
                    prvWrd = self.__wordList[i-1]
                    if word.getSurfaceForm().isdigit():
                        if prvWrd.getInitialPunc() == '\\':
                            if prvWrd.getSurfaceForm() == 'v' or prvWrd.getSurfaceForm() == 'c':
                                continue  
                    if prvWrd.getInitialPunc() == '\\':
                        if prvWrd.getSurfaceForm() == 'f' or prvWrd.getSurfaceForm() == 'fr':
                            continue
                # Don't warn on the second time an unknown word is encountered
                if word.getSurfaceForm() in unknownWordMap:
                    multipleUnknownWords = True
                else:
                    self.__report.Warning('No analysis found for the word: '+ word.getSurfaceForm() + ' Treating this is an unknown word.')
                    
                    # Check if we've had this unknown word already
                    if word.getSurfaceForm() not in unknownWordMap:
                        # Add this word to the unknown word map
                        unknownWordMap[word.getSurfaceForm()] = 1
                        
        return multipleUnknownWords
    
# TODO: have a config file defined way to change . to ><. This could be useful for port manteau languages.
# Get the clitic gloss. Substitute periods with >< to produce multiple tags a la Apertium.
#affixStr += '<' + re.sub(r'\.', r'><',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'

# A word within a sentence in a FLEx text    
class TextWord():
    def __init__(self, report):
        self.__report = report
        self.__initPunc = ''
        self.__finalPunc = ''
        self.__surfaceForm = ''
        self.__lemmaList = []
        self.__eList = [] # entry object list
        self.__affixLists = [] # a list of lists
        self.__componentList = []
        self.__guid = None
        self.__senseList = []
        self.__inflFeatAbbrevsList = [] # a list of lists
        self.__stemFeatAbbrList = []
    def addAffix(self, myObj):
        self.addPlainTextAffix(ITsString(myObj.BestAnalysisAlternative).Text)
    def addAffixesFromList(self, strList):
        # assume we don't have two or more entries, i.e. compound
        self.__affixLists[0] += strList
    def addEntry(self, e):
        self.__eList.append(e)
        self.__affixLists.append([]) # create an empty list
        self.__inflFeatAbbrevsList.append([]) # create an empty list
    def addFinalPunc(self, myStr):
        self.__finalPunc += myStr
    def addInflFeatures(self, inflFeatAbbrevs):
        self.__inflFeatAbbrevsList[-1] = inflFeatAbbrevs # add to last slot
        i = 1
    def addInitialPunc(self, myStr):
        self.__initPunc += myStr
    def addLemma(self, lemma):
        self.__lemmaList.append(lemma)
    def addLemmaFromObj(self, myObj):
        self.__lemmaList.append(ITsString(myObj.Form.BestVernacularAlternative).Text)
    def addPlainTextAffix(self, myStr):
        # if there's no affix lists yet, create one with this string
        if self.isInitialized() == False:
            self.__affixLists.append([myStr])
        else:
            # Add the affix to the slot that matches the last entry
            maxIndex = len(self.__eList)-1
            self.__affixLists[maxIndex].append(myStr)
    def addSense(self, sense):
        self.__senseList.append(sense)
    def addUnknownAffix(self):
        self.addPlainTextAffix('UNK')
    def buildLemmaAndAdd(self, baseStr, senseNum):
        if type(baseStr) == str: # Python2 code: or type(baseStr) == unicode:
            myStr = baseStr 
        else:
            myStr = ITsString(baseStr).Text
                                
        lem = do_capitalization(getHeadwordStr(self.__eList[-1]), myStr) # assume we can use the last entry as the one we want
        self.addLemma(add_one(lem) + '.' + str(senseNum+1))
    def getAffixSymbols(self):
        # assume no compound roots for this word
        return self.__affixLists[0]
    def getComplexFormEntries(self):
        if self.hasEntries():
            return self.__eList[0].ComplexFormEntries
    def getComponent(self, index):
        # assume no compound roots for this word
        if index < len(self.__componentList):
            return self.__componentList[index]
        return None
    def getEntryHandle(self):
        # assume no compound roots for this word
        if self.hasEntries():
            return self.__eList[0].Hvo
        return 0
    def getFirstEntry(self):
        if self.hasEntries():
            return self.__eList[0]
        return None
    def getDataStreamSymbols(self, i):
        symbols = []
        
        # Start with POS. <sent> words are special, no POS
        if not self.isSentPunctutationWord():
            symbols = [self.getPOS(i)]
        # Then inflection class
        symbols += self.getInflClass(i)
        # Then stem features
        symbols += self.getStemFeatures(i)
        # Then features from irregularly inflected forms
        symbols += self.getInflFeatures(i)
        # Then affixes
        if i < len(self.__affixLists):
            symbols += self.__affixLists[i]
        
        # Put each symbol in angle brackets e.g. <sbjv>. Also _ for .
        return '<'+'><'.join(underscores(x) for x in symbols)+'>'
    
    def getEntries(self):
        return self.__eList
    def getFeatures(self, featList):
        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
        return [abb for _, abb in sorted(featList, key=lambda x: x[0])]
    def getFinalPunc(self):
        return self.__finalPunc
        # I believe there's one sense for each entry
    def getGuid(self):
        return self.__guid
    def hasPunctuation(self):
        # check for punctuation that is not spaces
        if re.search(r'\S', self.__initPunc) or re.search(r'\S', self.__finalPunc):
            return True
        return False
    def getID(self):
        return self.getGuid()
    def getEntryIndex(self, e):
        for i, myE in enumerate(self.__eList):
            if myE == e:
                return i
        return None
    def getInflClass(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            mySense = self.__senseList[i]
            if mySense and mySense.MorphoSyntaxAnalysisRA.InflectionClassRA:
                return [ITsString(mySense.MorphoSyntaxAnalysisRA.InflectionClassRA.Abbreviation.BestAnalysisAlternative).Text]
        return []
    def getInflFeatures(self, i):
        # Get any features that come from irregularly inflected forms   
        if i < len(self.__inflFeatAbbrevsList):
            return self.getFeatures(self.__inflFeatAbbrevsList[i])
        return []
    def getInitialPunc(self):
        return self.__initPunc
    def getLemma(self, i):
        if i < len(self.__lemmaList):
            return convertProblemChars(self.__lemmaList[i], lemmaProbData)
        return ''
    def getPOS(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            mySense = self.__senseList[i]
            if mySense and mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                return convertProblemChars(ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text, catProbData)
        return self.getUnknownPOS()
    def getSense(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            return self.__senseList[i]
        return None
    def getStemFeatures(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            mySense = self.__senseList[i]
            if mySense and mySense.MorphoSyntaxAnalysisRA.MsFeaturesOA:
                # if we already have a populated list, we don't need to do it again.
                if len(self.__stemFeatAbbrList) == 0:
                    # The features might be complex, make a recursive function call to find all features. Features keep getting added to list.
                    get_feat_abbr_list(mySense.MorphoSyntaxAnalysisRA.MsFeaturesOA.FeatureSpecsOC, self.__stemFeatAbbrList)
                return self.getFeatures(self.__stemFeatAbbrList)
        return []
    def getSurfaceForm(self):
        return self.__surfaceForm
    def getUnknownPOS(self):
        return 'UNK'
    def hasComponents(self):
        if len(self.__componentList) > 0:
            return True
        return False
    def hasEntries(self):
        if len(self.__eList) > 0:
            return True
        return False
    def hasSenses(self):
        if len(self.__senseList) > 0:
            return True
        return False
    # Use bundle guid to look up the entry and initialize the entry, sense, and lemma
    def initialize(self, bundleGuid, DB):
        
        # get the repository that holds bundle guids
        repo = DB.project.ServiceLocator.GetInstance(IWfiMorphBundleRepository)
        
        # look up the guid
        try:
            bundleObject = repo.GetObject(bundleGuid)
        except:
            self.__report.Error('Could not find bundle Guid for word in the inserted word list.')
            return 
        
        # get the entry object and add it
        myEntry = bundleObject.MorphRA.Owner
        self.addEntry(myEntry)
        
        # set the guid for this word
        self.setGuid(bundleGuid)
        
        # Go through each sense and identify which sense number we have
        foundSense = False
        for senseNum, mySense in enumerate(myEntry.SensesOS):
            
            if mySense.Guid == bundleObject.SenseRA.Guid:
                foundSense = True
                break
            
        if foundSense:
            
            self.addSense(mySense)
            
            # Construct and set the lemma in the form xyzN.M
            lem = headword = getHeadwordStr(myEntry)
            lem = add_one(lem)
            lem = lem + '.' + str(senseNum+1) # add sense number
            self.addLemma(lem)
            self.__surfaceForm = re.sub(r'\d', '', headword)
        else:
            self.__report.Error('Could not find the sense for word in the inserted word list.')
            return    

    def isSentPunctutationWord(self):
        # assume no compound roots for this word
        if len(self.__affixLists) > 0 and len(self.__affixLists[0]) > 0:
            if self.__affixLists[0][0] == 'sent':
                return True
        return False
    def isInitialized(self):
        if self.hasSenses() == False and len(self.__affixLists) == 0:
            return False
        return True
    def initWithComplex(self, cmplxE, componentList):
        self.addEntry(cmplxE)
        self.setComponentList(componentList)
        
        # set the surface form as the concatenation of all the component's surface forms
        self.setSurfaceForm(' '.join(w.getSurfaceForm() for w in componentList))
        
        # build the lemma. For capitalization check use first surface form
        self.buildLemmaAndAdd(componentList[0].getSurfaceForm(), 0) # we are going to just use sense 1 for complex forms

        # add the sense
        self.addSense(cmplxE.SensesOS.ToArray()[0])
        
        # use the bundle guid from the last component as this word's guid
        lastComponent = componentList[-1]
        self.setGuid(lastComponent.getGuid())
        
        # Transfer tags from one component to our new word
        # TODO: allow the user to specify taking affixes and features from first or last element
        affixList = lastComponent.getAffixSymbols()
        self.addAffixesFromList(affixList)
        
        # Transfer begin punctuation from the first component
        firstComponent = componentList[0]
        self.addInitialPunc(firstComponent.getInitialPunc())
        
        # Transfer end punctuation from the last component
        self.addFinalPunc(lastComponent.getFinalPunc())
        
    def notCompound(self):
        if len(self.__eList) > 1:
            return False # we have a compound of 2 or more entries
        return True
    def outputDataForAllRoots(self):
        retStr = ''
        if self.isSentPunctutationWord():
            return self.getLemma(0) + self.getDataStreamSymbols(0)
        else:
            for i, _ in enumerate(self.__lemmaList):
                retStr += self.getLemma(i)
                retStr += self.getDataStreamSymbols(i)
        return retStr
    def outputDataStream(self):
        retStr = self.__initPunc+self.outputWordDataStream()+self.__finalPunc
        return retStr
    def outputWordDataStream(self):
        retStr = '^'+self.outputDataForAllRoots()+'$'
        return retStr
    def posMatchForMiddleItemInDiscontigousList(self, discontigPOSList):
        if self.getPOS(0) in discontigPOSList:
            return True
        return False
    def setComponentList(self, cList):
        self.__componentList = cList
    def setGuid(self, myGuid):
        self.__guid = myGuid
    def setSurfaceForm(self, myStr):
        self.__surfaceForm = myStr
    def write(self, fOut):
        fOut.write(split_compounds(self.outputDataStream()))
    def writePrePunc(self, fOut):
        fOut.write(self.__initPunc)
    def writePostPunc(self, fOut):
        fOut.write(self.__finalPunc)
    def writeWordData(self, fOut):
        fOut.write(split_compounds(self.outputWordDataStream()))
        
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

# This is a key function used by the ExtractSourceText and LiveRuleTesterTool modules
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
            if set(list(textPunct)).intersection(set(list(sentPunct))):
                
                # create a new word object
                myWord = TextWord(report)
                
                # initialize it with the puctuation and sent as the "POS"
                myWord.addLemma(textPunct)
                myWord.setSurfaceForm(textPunct)
                myWord.addPlainTextAffix('sent')
                
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
                            tempEntry = GetEntryWithSense(tempEntry, inflFeatAbbrevs)
                            
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

def get_categories(DB, TargetDB, report, posMap, numCatErrorsToShow=1, addInflectionClasses=True):

    haveError = False
    dbList = [(DB, 'source'), (TargetDB, 'target')]

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
    
def check_for_cat_errors(report, dbType, posFullNameStr, posAbbrStr, countList, numCatErrorsToShow):

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
                    report.Error(f"The abbreviation: '{posAbbrStr}' for category: '{posFullNameStr}' can't have a {charName} in it. Could not complete, please correct this category in the {dbType} database.")
                haveError = True
                
                # show all fatal errors
                continue
            
            oldAbbrStr = posAbbrStr
            
            # do the conversion    
            posAbbrStr = invalidCharCompiledRE.sub(replChar, posAbbrStr)

            # If we are under the max errors to show number, give a warning
            if countList[i] < numCatErrorsToShow:
                
                if report:
                    report.Warning(f"The abbreviation: '{oldAbbrStr}' for category: '{posFullNameStr}' in the {dbType} database can't have a {charName} in it. The {charName}" + \
                                   f" has been {message}, forming {posAbbrStr}. Keep this in mind when referring to this category in transfer rules.")
            
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

def loadSourceTextList(widget, DB, sourceText):
    
    sourceList = []
    for interlinText in DB.ObjectsIn(ITextRepository):

        sourceList.append(ITsString(interlinText.Name.BestAnalysisAlternative).Text.strip())

    sortedSourceList = sorted(sourceList, key=str.casefold)
    
    # Add items and when we find the one that matches the config file. Set that one to be displayed.
    for i, itemStr in enumerate(sortedSourceList):
        
        widget.addItem(itemStr)
        
        if itemStr == sourceText:
            
            widget.setCurrentIndex(i)
