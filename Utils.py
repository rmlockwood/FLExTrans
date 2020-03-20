#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
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
import copy
import tempfile
import os
import xml.etree.ElementTree as ET
import platform
import subprocess
import uuid
from datetime import datetime
import TestbedValidator

from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   
from SIL.LCModel.DomainServices import SegmentServices
from __builtin__ import False, True
from future.backports.test.pystone import FALSE, TRUE

## For TreeTran
GOOD_PARSES_LOG = 'good_parses.log'

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
TESTBED_FILE_PATH = OUTPUT_FOLDER + '\\testbed.xml'
TESTBED_RESULTS_FILE_PATH = OUTPUT_FOLDER + '\\testbed_results.xml'

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

reObjAddOne = re.compile('\d$')
reDataStream = re.compile('(>[^$<])')   
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
        ret_str = self.__headWord
        if self.__gramCat != SENT:
            ret_str += '.' + self.__senseNum
        ret_str += ' ' + self.__gramCat
        for tag in self.__otherTags:
            ret_str += ' ' + tag
        return ret_str
    
    def toFormattedString(self, rtl = False):
        # Create an element
        p = ET.Element('span')
        
        # Split off the homograph_num (if present; sent punctuation won't have it)
        lemma_parts = re.split('(\d+)', self.__headWord) # last item is empty
        
        # Output the lexeme
        span = output_span(p, LEMMA_COLOR, lemma_parts[0], rtl)
    
        # Output the subscript homograph # and sense # (if they exist)
        if self.__gramCat != SENT:
            add_subscript(span, lemma_parts[1]+'.'+self.__senseNum)
        
        # Check for RTL
        if rtl == True:
            # prepend the RTL marker
            symb = ur'\u200F' + self.__gramCat
        else:
            symb = self.__gramCat
        
        # output the symbol
        output_span(p, GRAM_CAT_COLOR, ' '+symb, rtl)
        
        for tag in self.__otherTags:
        
            # Check for RTL
            if rtl == True:
                # prepend the RTL marker
                symb = ur'\u200F' + tag
            else:
                symb = tag
            
            # output the symbol
            output_span(p, AFFIX_COLOR, ' '+symb, rtl)
        
        return ET.tostring(p)
    
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
        tokens = filter(None, tokens) # filter out the empty strings
        
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
        self.__inputStr = unicode(string2Parse)
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
    def __init__(self, luList=None, origin=None, synthResult=None, testNode=None):
        self.__luList = luList
        self.__origin = origin
        self.__synthResult = synthResult
        self.__testNode = testNode
        self.__testChanged = False
        
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
            lu = LexicalUnit(None, luNode) # 1st param is str2parse
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
        return self.__testNode.find(TARGET_OUTPUT+'/'+EXPECTED_RESULT).text
    def getActualResult(self):
        return self.__testNode.find(TARGET_OUTPUT+'/'+ACTUAL_RESULT).text
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
        f_out.write(self.getApertiumString().encode('utf-8')+' ^EOL<eol>$\n')

    def extractResults(self, f_out):
        
        try:
            # each test goes on its own line
            line = f_out.readline()
        except:
            raise ValueError('No more lines to read in the synthesis file.')
        
        line = unicode(line, 'utf-8')
        
        # Remove the dummy EOL lexical unit at the end.
        line = re.sub(' @EOL', '', line)
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
        tot_failed = 0
        tot_invalid = 0
        for test in self.__TestXMLObjectList:
            (failed, invalid) = test.getFailedAndInvalid()
            tot_failed += failed
            tot_invalid += invalid
        return (tot_failed, tot_invalid)
            
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
            # Initialize a result object and add it to the list
            newTestXMLObj = TestbedTestXMLObject(None, None, None, testNode) # luList=None, origin=None, synthResult=None
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
    def __init__(self, direction):
        
        self.__isNew = False
        
        # check if the file exists
        if os.path.exists(TESTBED_FILE_PATH) == False:
            
            # we will create it
            self.__isNew = True
            self.__XMLObject = FLExTransTestbedXMLObject(None, direction)
            myRoot = self.__XMLObject.getRoot()
            self.__testbedTree = ET.ElementTree(myRoot)
        else:
            try:
                self.__testbedTree = ET.parse(TESTBED_FILE_PATH)
            except:
                raise ValueError('The testbed file: ' + TESTBED_FILE_PATH + ' is invalid.')

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
        self.__testbedTree.write(TESTBED_FILE_PATH, encoding='utf-8', xml_declaration=True)

# Models the result part of the XML structure for a results log
# It contains a list of FLExTransTestbedXMLObject's
class TestbedResultXMLObject():
    # You can initialize this class in two ways:
    # 1) Give just a parent element and it creates an empty <result> element for the parent
    # 2) Give it a <result> XML object (ElementTree.Element) and it initializes the testbed object list from the testbed xml elements.
    def __init__(self, parentNode, rootNode=None):
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
        if root == None:
            self.__rootNode = ET.Element(FLEXTRANS_TESTBED_RESULTS)
        else:
            self.__createTestbedResultXMLObjectList()
    
    def getTestbedResultXMLObjectList(self):
        return self.__resultXMLObjList
    
    def initTestResult(self, testbedXMLObj):
        
        # create a new result object and set the start time and give it a blank end time
        resultXMLObj = TestbedResultXMLObject(self.__rootNode, None)
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
            newResultXMLObj = TestbedResultXMLObject(None, resultNode)
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
    def __init__(self):
        if os.path.exists(TESTBED_RESULTS_FILE_PATH) == False:
            
            self.__XMLObject = FLExTransTestbedResultsXMLObject()
            myRoot = self.__XMLObject.getRoot()
            self.__testbedResultsTree  = ET.ElementTree(myRoot)
        else:
            try:
                self.__testbedResultsTree = ET.parse(TESTBED_RESULTS_FILE_PATH)
            except:
                raise ValueError('The testbed results file: ' + TESTBED_RESULTS_FILE_PATH + ' is invalid.')

            self.__XMLObject = FLExTransTestbedResultsXMLObject(self.__testbedResultsTree.getroot())
    
    def getResultsXMLObj(self):
        return self.__XMLObject
    
    def write(self):
        self.__testbedResultsTree.write(TESTBED_RESULTS_FILE_PATH, encoding='utf-8', xml_declaration=True)

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
    return subprocess.call(cmd)
    #return 0

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
        
def process_chunk_lexical_unit(lu_str, parent_element, rtl):
    # Split off the symbols from the lemma in the lexical unit (which is i+1)
    symbols = re.split('<|>', lu_str)
    symbols = filter(None, symbols) # filter out the empty strings
    
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
            symb = ur'\u200F' + symb
        
        # output the symbol
        output_span(parent_element, symbol_color, ' '+symb, rtl)

# Split a compound from one lexical unit containing multiple words to multiple
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
            symb = ur'\u200F' + symb
        
        # output the symbol
        output_span(parent_element, symbol_color, ' '+symb, rtl)

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

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
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

# Convert . (dot) to _ (underscore)
def underscores(inStr):
    return re.sub(r'\.', r'_', inStr)

# The whole text from FLEx
class TextEntirety():
    def __init__(self):
        self.__parList = []
        self.__cmplxFormMap = {}
    def addParagraph(self, textPar):
        self.__parList.append(textPar)
    def createGuidMaps(self):
        for par in self.__parList:
            par.createGuidMaps()
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
    def warnForUnknownWords(self):
        multipleUnknownWords = False
        for par in self.__parList:
            if par.warnForUnknownWords() == True:
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
    def createGuidMaps(self):
        for sent in self.__sentList:
            sent.createGuidMap()
    def findComplexForms(self, cmplxFormMap, typesList):
        for sent in self.__sentList:
            sent.findComplexForms(cmplxFormMap, typesList)
    def getSent(self, sentNum):
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
    def warnForUnknownWords(self):
        multipleUnknownWords = False
        for sent in self.__sentList:
            if sent.warnForUnknownWords() == True:
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
        self.__unknownWordMap = {}
        self.__guidMap = {}
    def addWord(self, textWord):
        self.__wordList.append(textWord)
    def createGuidMap(self):
        for word in self.__wordList:
            self.__guidMap[word.getGuid()] = word
    def getSurfaceAndDataTupleList(self, tupList):
        for word in self.__wordList:
            tupList.append((word.getSurfaceForm(), word.outputDataStream()))
    def getWordCount(self):
        return len(self.__wordList)
    def getWordList(self):
        return self.__wordList
    def haveGuid(self, myGuid):
        return myGuid in self.__guidMap
    # See if a bundle is not part of a neighboring complex form
    def notPartOfAdjacentComplexForm(self, currGuid, nextGuid):
        # Get the next word object
        nextWrd = self.__guidMap[nextGuid]
        
        # Check if the current word's bundle guid matches the first component of the next word
        if nextWrd.hasComponents():
            guidFirstComponent = nextWrd.getComponent(0).getGuid()
            if guidFirstComponent == currGuid:
                return False
        return True
    def write(self, fOut):
        for word in self.__wordList:
            word.write(fOut)
    def writeThisGuid(self, fOut, myGuid):
        self.__guidMap[myGuid].write(fOut)
    
    ### Long methods - in alphabetical order
    def findComplexForms(self, cmplxFormMap, typesList):
        # Loop through the word list
        for wrd in self.__wordList:
            if wrd.getEntry() is not None:
                # Check if we have already found complex forms for this word and cached them
                if wrd.getEntryHandle() not in cmplxFormMap:
                    cmplxEntryTupList = []

                    # Loop through the complex entries for this word
                    for cmplxEntry in wrd.getEntry().ComplexFormEntries:
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
            componentList.append(self.__wordList.pop(i)) # don't increment the next one is in position i after the previous pop
        
        # New object
        newWord = TextWord(self.__report)
        
        # Initialize it with the complex entry being the main entry of the word. Other attributes are drawn from the last
        # matching component. Tags will also transferred as needed
        newWord.initWithComplex(complexEn, componentList)
        
        # Insert the new word into the word list
        self.__wordList.insert(i, newWord)
        
        # Update the guid map
        self.__guidMap[newWord.getGuid()] = newWord
        
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
                                    if self.__wordList[i+j].getEntry() == componentEList[j]: # jth component in the list
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
            
    def warnForUnknownWords(self):
        multipleUnknownWords = False
        for i, word in enumerate(self.__wordList):
            # See if we have an uninitialized word which indicates it's unknown
            if word.IsInitialized() == False:
                # Allow some unknown "words" without warning, such as sfm markers
                if word.getLemma()[0] == '\\':
                    pass
                elif i > 0 and word.getLemma().isdigit() and (self.__wordList[i-1] == '\\v' or self.__wordList[i-1] == '\\c'):
                    pass
                elif i > 0 and (self.__wordList[i-1] == '\\f' or self.__wordList[i-1] == '\\fr'):
                    pass
                # Don't warn on the second time an unknown word is encountered
                elif word.getLemma() in self.__unknownWordMap:
                    multipleUnknownWords = True
                else:
                    self.__report.Warning('No analysis found for the word: '+ word.getLemma() + ' Treating this is an unknown word.')
                    
                    # Check if we've had this unknown word already
                    if word.getLemma() not in self.__unknownWordMap:
                        # Add this word to the unknown word map
                        self.__unknownWordMap[word.getLemma()] = 1
                        
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
        self.__lemma = ''
        self.__e = None # entry object
        self.__affixList = []
        self.__componentList = []
        self.__guid = None
        self.__sense = None
        self.__inflFeatAbbrevs = []
        self.__stemFeatAbbrList = []
    def addAffix(self, myObj):
        self.addPlainTextAffix(ITsString(myObj.BestAnalysisAlternative).Text)
    def addAffixesFromList(self, strList):
        self.__affixList += strList
    def addFinalPunc(self, myStr):
        self.__finalPunc += myStr
    def addInitialPunc(self, myStr):
        self.__initPunc += myStr
    def addPlainTextAffix(self, myStr):
        self.__affixList.append(myStr)
    def addUnknownAffix(self):
        self.addPlainTextAffix('UNK')
    def buildLemma(self, baseStr, senseNum):
        if type(baseStr) == str or type(baseStr) == unicode:
            myStr = baseStr 
        else:
            myStr = ITsString(baseStr).Text
        lem = do_capitalization(self.getHeadwordStr(), myStr)
        self.__lemma = add_one(lem) + '.' + str(senseNum+1)
    def componentMatch(self, wrd):
        for c in self.__componentList:
            if c.getEntry() == wrd.getEntry():
                return True
        return False
    
    def getComponent(self, index):
        if index < len(self.__componentList):
            return self.__componentList[index]
        return None
    def getEntry(self):
        return self.__e
    def getEntryHandle(self):
        if self.__e:
            return self.__e.Hvo
        return 0
    def getDataStreamSymbols(self):
        symbols = []
        
        # Start with POS. <sent> words are special, no POS
        if not self.isSentPunctutationWord():
            symbols = [self.getPOS()]
        # Then inflection class
        symbols += self.getInflClass()
        # Then stem features
        symbols += self.getStemFeatures()
        # Then features from irregularly inflected forms
        if len(self.__inflFeatAbbrevs) > 0:
            symbols += self.getInflFeatures()
        # Then affixes
        symbols += self.__affixList
        
        # Put each symbol in angle brackets e.g. <sbjv>. Also _ for .
        return '<'+'><'.join(underscores(x) for x in symbols)+'>'
    
    def getFeatures(self, featList):
        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
        return [abb for _, abb in sorted(featList, key=lambda x: x[0])]
    def getGuid(self):
        return self.__guid
    def getHeadwordStr(self):
        return ITsString(self.__e.HeadWord).Text
    def getInflClass(self):
        if self.__sense and self.__sense.MorphoSyntaxAnalysisRA.InflectionClassRA:
            return [ITsString(self.__sense.MorphoSyntaxAnalysisRA.InflectionClassRA.Abbreviation.BestAnalysisAlternative).Text]
        return []
    def getInflFeatures(self):
        # Get any features that come from irregularly inflected forms   
        return self.getFeatures(self.__inflFeatAbbrevs)
    def getLemma(self):
        return self.__lemma
    def getNonPOSSymbols(self):
        return self.getInflClass() + self.getStemFeatures() + self.getInflFeatures() + self.__affixList
    def getPOS(self):
        if self.__sense is None or self.__sense.MorphoSyntaxAnalysisRA.PartOfSpeechRA is None:
            return self.getUnknownPOS()
        return ITsString(self.__sense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
    def getStemFeatures(self):
        if self.__sense and self.__sense.MorphoSyntaxAnalysisRA.MsFeaturesOA:
            # The features might be complex, make a recursive function call to find all features
            get_feat_abbr_list(self.__sense.MorphoSyntaxAnalysisRA.MsFeaturesOA.FeatureSpecsOC, self.__stemFeatAbbrList)
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
    def isEnclitic(self, myEntry):
        return ITsString(myEntry.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text in ('proclitic','enclitic')
    def isSentPunctutationWord(self):
        if len(self.__affixList) > 0 and self.__affixList[0] == 'sent':
            return True
        return False
    def IsInitialized(self):
        if self.__sense == None and len(self.__affixList) == 0:
            return False
        return True
    def initWithComplex(self, cmplxE, componentList):
        self.setEntry(cmplxE)
        self.setComponentList(componentList)
        
        # set the surface form as the concatenation of all the component's surface forms
        self.setSurfaceForm(' '.join(w.getSurfaceForm() for w in componentList))
        
        # build the lemma. For capitalization check use first surface form
        self.buildLemma(componentList[0].getSurfaceForm(), 0) # we are going to just use sense 1 for complex forms

        # set the POS
        self.setSense(cmplxE.SensesOS.ToArray()[0])
        
        # use the bundle guid from the last component as this word's guid
        lastComponent = componentList[-1]
        self.setGuid(lastComponent.getGuid())
        
        # Transfer tags from one component to our new word
        # TODO: allow the user to specify taking affixes and features from last element
        x = componentList[-1].getNonPOSSymbols()
        self.addAffixesFromList(x)
        
    def outputDataStream(self):
        retStr = self.__initPunc+'^'+self.getLemma()+self.getDataStreamSymbols()+'$'+self.__finalPunc
        return retStr
    def setComponentList(self, cList):
        self.__componentList = cList
    def setEntry(self, e):
        self.__e = e
    def setGuid(self, myGuid):
        self.__guid = myGuid
    def setInflFeatures(self, inflFeatAbbrevs):
        self.__inflFeatAbbrevs = inflFeatAbbrevs
    def setLemma(self, lemma):
        self.__lemma = lemma
    def setLemmaFromObj(self, myObj):
        self.__lemma = ITsString(myObj.Form.BestVernacularAlternative).Text
    def setSense(self, sense):
        self.__sense = sense
    def setSurfaceForm(self, myStr):
        self.__surfaceForm = myStr
    def write(self, fOut):
        fOut.write(split_compounds(self.outputDataStream()).encode('utf-8'))
        
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
def getInterlinData(DB, report, sentPunct, contents, typesList):
    
    prevEndOffset = 0
    currSegNum = 0
    myWord = None
    savedPrePunc = ''
    
    initProgress(contents, report)
    
    # Initialize the text and the first paragraph object
    myText = TextEntirety()
    myPar = TextParagraph()
    
    # Loop through each thing in the text
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(prog_cnt)
        
        # Always create a new word to start with
        myWord = TextWord(report)

        # Get the number of spaces between words        
        numSpaces = analysisOccurance.GetMyBeginOffsetInPara() - prevEndOffset
        myPunc = ' '*numSpaces
        
        # If we are on a different segment, it's a new sentence.
        if analysisOccurance.Segment.Hvo <> currSegNum:
            
            # Create a new sentence object and add it to the paragraph
            mySent = TextSentence(report)

            # If we have a negative number, it's new paragraph
            if numSpaces < 0 or prog_cnt == 0: # or first time through 
                myPar = TextParagraph()
                myText.addParagraph(myPar)
            
            # Add the sentence to the paragraph
            myPar.addSentence(mySent)
            
        # Add the word to the current sentence
        mySent.addWord(myWord)
        
        # Save where we are    
        prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()
        currSegNum = analysisOccurance.Segment.Hvo
                
        # Deal with different Analysis classes differently
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            
            textPunct = ITsString(analysisOccurance.Analysis.Form).Text
            
            # See if one or more symbols is part of the user-defined sentence punctuation. 
            # if so, save the punctuation as if it is its own word. E.g. ^.<sent>$
            if set(list(textPunct)).intersection(set(list(sentPunct))):
                myWord.setLemma(textPunct)
                myWord.addPlainTextAffix('sent')
                
            # If not, assume this is non-sentence punctuation and just save the punctuation to go with the current word.
            else:
                # If we have spaces at the beginning of a sentence, save them for later
                if mySent.getWordCount() == 0:
                    savedPrePunc = myPunc
                else:
                    myWord.addFinalPunc(myPunc)
                    savedPrePunc = ''
            continue
        
        ## Now we know we have something other than punctuation
        # See if we have any pre-punctuation
        if len(savedPrePunc) > 0:
            myWord.addInitialPunc(savedPrePunc)
            
        # Figure out the surface form and set it.
        beg = analysisOccurance.GetMyBeginOffsetInPara()
        end = analysisOccurance.GetMyEndOffsetInPara()
        surfaceForm = ITsString(analysisOccurance.Paragraph.Contents).Text[beg:end]
        
        # Set lemma to surfaceForm initially
        myWord.lemma = surfaceForm
        myWord.setSurfaceForm(surfaceForm)

        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = analysisOccurance.Analysis.Analysis   # Same as Owner
            
        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = analysisOccurance.Analysis
            
        # We get into this block if there are no analyses for the word or an analysis suggestion hasn't been accepted. 
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":
            
            # Lemma will be the same as the surface form, I think
            myWord.setLemmaFromObj(analysisOccurance.Analysis)
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
                        
                        # Just save the the guid for the first root in the bundle
                        if myWord.getGuid() == None:
                            myWord.setGuid(bundle.Guid) # identifies a bundle for matching with TreeTran output
            
                        # If we have an invalid POS, give a warning
                        if not bundle.MsaRA.PartOfSpeechRA:
                            
                            myWord.setLemmaFromObj(wfiAnalysis.Owner)
                            report.Warning('No POS found for the word: '+ myWord.getSurfaceForm(), DB.BuildGotoURL(tempEntry))
                            break
                        
                        if bundle.MorphRA:
                            # Go from variant(s) to entry/variant that has a sense. We are only dealing with senses, so we have to get to one. Along the way
                            # collect inflection features associated with irregularly inflected variant forms so they can be outputted.
                            inflFeatAbbrevs = []
                            tempEntry = GetEntryWithSense(tempEntry, inflFeatAbbrevs)
                            
                            # See if we have an enclitic or proclitic
                            if myWord.isEnclitic(tempEntry) == True:
                                # Get the clitic gloss.
                                myWord.addAffix(bundle.SenseRA.Gloss)
                                
                            # Otherwise we have a root or stem or phrase
                            else:
                                myWord.setEntry(tempEntry)
                                myWord.setInflFeatures(inflFeatAbbrevs) # this assumes we don't pick up any features from clitics
                                
                                # Go through each sense and identify which sense number we have
                                foundSense = False
                                for senseNum, mySense in enumerate(myWord.getEntry().SensesOS):
                                    if mySense.Guid == bundle.SenseRA.Guid:
                                        myWord.setSense(mySense)
                                        foundSense = True
                                        break
                                if foundSense:
                                    # Construct and set the lemma
                                    myWord.buildLemma(analysisOccurance.BaselineText, senseNum)
                                else:
                                    report.Warning("Couldn't find the sense for headword: "+myWord.GetHeadwordStr())    
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
                    myWord.setLemmaFromObj(wfiAnalysis.Owner)
                    report.Warning('No morphosyntactic analysis found for some part of the word: '+ myWord.getLemma())
                    break # go on to the next word    
            else:
                # Part of the word has not been tied to a lexical entry-sense
                myWord.setLemmaFromObj(wfiAnalysis.Owner)
                report.Warning('No sense found for some part of the word: '+ myWord.getLemma())
                break # go on to the next word    
    
    # Don't warn for sfm markers, but warn once for others        
    if myText.warnForUnknownWords() == True:
        report.Warning('One or more unknown words occurred multiple times.')

    # substitute a complex form when its components are found contiguous in the text      
    myText.processComplexForms(typesList) 
    
    return myText

# Old function to get interlinear data        
def get_interlin_data_old(DB, report, sent_punct, contents, typesList, getSurfaceForm, TreeTranSort=False):
    
    prev_pv_list = []
    prev_e = None
    ccc = 0 # current_complex_component
    segment_list = []
    sent_list = []
    outputStrList = []
    BundleGuidMap = {}
    curr_SegNum = 0
    prevEndOffset = 0
    sentNum = 0
    begSentIndex = 0
    itemCount = 0
    savedTags = ''
    bundle_list = []
    surfaceForm = ''
    saved1stbaselineWord = ''
        
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
    prevGuid = None 
    unknownWordList = []
    multiple_unknown_words = False
    
    # Loop through each segment
    ss = SegmentServices.StTextAnnotationNavigator(contents)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):
       
        report.ProgressUpdate(prog_cnt)
        outStr = affixStr = ''
        bundleGuid = None        
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
                    if TreeTranSort:
                        BundleGuidMap[prevGuid] =  BundleGuidMap[prevGuid] + ' '*numSpaces
                    outputStrList.append(' '*numSpaces)
                    itemCount += 1
                elif numSpaces < 0: # new paragraph
                    if TreeTranSort:
                        BundleGuidMap[prevGuid] = BundleGuidMap[prevGuid] + '\n'
                    outputStrList[len(outputStrList)-1] += '\n'
            
            prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()
                
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":
            
            text_punct = ITsString(analysisOccurance.Analysis.Form).Text
            
            # See if one or more symbols is part of the user-defined sentence punctuation. If so output the
            # punctuation as part of the data stream along with the symbol/tag <sent>
            # convert to lists and take the set intersection
            if set(list(text_punct)).intersection(set(list(sent_punct))):
                outStr = "^"+text_punct+"<sent>$"
                
                sentNum += 1
                
                if getSurfaceForm:
                    bundle_list.append((text_punct,outStr))
                    
            # If not, assume this is non-sentence punctuation and just output the punctuation without a "symbol" e.g. <xxx>
            else:
                outStr = text_punct
            
            if not getSurfaceForm:
                if TreeTranSort and prevGuid != None:
                    BundleGuidMap[prevGuid] = BundleGuidMap[prevGuid] + outStr

                outputStrList.append(outStr)
                itemCount += 1
                     
                if TreeTranSort:
                    # Since we are on new sentence. Append the last one and start a new one.
                    if TreeTranSort:
                        sent = outputStrList[begSentIndex:]
                        sent_list.append(sent)
                        begSentIndex = itemCount
                    
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
            outStr = '^'+outStr+'$'
            
            if getSurfaceForm:
                bundle_list.append((surfaceForm, outStr))
            else:
                if TreeTranSort:
                    BundleGuidMap[prevGuid] = BundleGuidMap[prevGuid] + outStr
                outputStrList.append(outStr)
                itemCount += 1
                
            continue
        else:
            wfiAnalysis = None
            
        # Go through each morpheme in the word (i.e. bundle)
        for bundle in wfiAnalysis.MorphBundlesOS:
            
            if bundle.SenseRA:
                if bundle.MsaRA and bundle.MorphRA:
                    # Get the LexEntry object
                    e = bundle.MorphRA.Owner
                        
                    # For a stem we just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':
                        
                        #report.Info(ITsString(e.HeadWord).Text)
                        
                        # Just save the the guid for the first root in the bundle
                        if bundleGuid == None:
                            bundleGuid = bundle.Guid # identifies a bundle for matching with TreeTran output
            
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
                                affixStr += '<' + underscores(ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                                
                                # TODO: have a config file defined way to change . to ><. This could be useful for port manteau languages.
                                # Get the clitic gloss. Substitute periods with >< to produce multiple tags a la Apertium.
                                #affixStr += '<' + re.sub(r'\.', r'><',ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                            
                            # Otherwise we have a root or stem or phrase
                            else:
                                pv_list = []
                                shared_complex_e = None
                                foundAtLeastOneMatch = startOfNewList = False
                                # Check for adjacent words that point to the same complex form
                                # If the form is a phrasal verb use it as the headword to output
                                if len(e.ComplexFormEntries) > 0:
                                    
                                    # Get a list of complex forms that match our criteria
                                    (pv_list, ccc, foundAtLeastOneMatch, startOfNewList) = getComplexForms(e, e.ComplexFormEntries, pv_list, ccc, typesList, foundAtLeastOneMatch, startOfNewList)
                                                                    
                                    # See if we ended up with any phrasal verbs
                                    (prev_pv_list, ccc, surfaceForm, outputStrList, BundleGuidMap, itemCount, saved1stbaselineWord, shared_complex_e) = \
                                    collectPhrasalVerbs(e, pv_list, ccc, foundAtLeastOneMatch, startOfNewList, analysisOccurance, prev_e, getSurfaceForm, bundle_list, \
                                                        outputStrList, TreeTranSort, prevGuid, BundleGuidMap, itemCount, savedTags, shared_complex_e, prev_pv_list, saved1stbaselineWord)
                                    
                                else:
                                    ccc = 0
                                    
                                if shared_complex_e:
                                    
                                    outStr = processSharedComplexForm(shared_complex_e, saved1stbaselineWord, outStr, report, inflFeatAbbrevs, savedTags)
                                    
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
                                        outStr += '<'+underscores(ITsString(bundle.MsaRA.InflectionClassRA.\
                                                              Abbreviation.BestAnalysisAlternative).Text)+'>'         

                                    # Get any features the stem or root might have
                                    if bundle.MsaRA.MsFeaturesOA:
                                        feat_abbr_list = []
                                        # The features might be complex, make a recursive function call to find all features
                                        get_feat_abbr_list(bundle.MsaRA.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
                                        
                                        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                        for grpName, abb in sorted(feat_abbr_list, key=lambda x: x[0]):
                                            outStr += '<' + underscores(abb) + '>'
                                    
                                    # Get any features that come from irregularly inflected forms        
                                    # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                    for grpName, abb in sorted(inflFeatAbbrevs, key=lambda x: x[0]):
                                        outStr += '<' + underscores(abb) + '>'
                            prev_pv_list = copy.copy(pv_list) 
                            prev_e = e            
                        else:
                            report.Warning("Morph object is null.")    
                    # We have an affix
                    else:
                        if bundle.SenseRA:
                            # Get the clitic gloss. Substitute periods with underscores. dots cause problems because in rules Apertium sees them as additional tags
                            affixStr += '<' + underscores(ITsString(bundle.SenseRA.Gloss.BestAnalysisAlternative).Text) +'>'
                            
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
        outStr = '^'+outStr+'$' #  apertium-style lexical unit
        
        if getSurfaceForm:
            # The bundle list is a tuple of surface form and apertium-style lexical unit
            bundle_list.append((surfaceForm,outStr))
        else:
            # If we will sort the output by the TreeTran output order, i.e. the syntax tree rearranged, build a map of this 
            # bundle Guid to the lexical unit output that goes with it
            if TreeTranSort:
                BundleGuidMap[bundleGuid] = outStr
                prevGuid = bundleGuid
            outputStrList.append(outStr)
            itemCount += 1

    if multiple_unknown_words:
        report.Warning('One or more unknown words occurred multiple times.')
    if getSurfaceForm:
        report.Info('Processed '+unicode(obj_cnt+1)+' analyses.')
        return segment_list
    else:
        report.Info('Export of '+unicode(obj_cnt+1)+' analyses complete.')

        if TreeTranSort:
            return (BundleGuidMap, sent_list)
        else:
            return outputStrList

# Loop through all the complex entries that are 1) complex form type and 2) in our
# list of complex types we care about (from the config file) 3) in the right position.
# If these are true, add the complex form to our list.        
def getComplexForms(e, complexEntriesList, pv_list, currentComplexCount, typesList, foundAtLeastOneMatch, startOfNewList):
    
    # each word could be part of multiple complex forms (e.g. ra -> char ra, ra raftan
    for complex_e in complexEntriesList:
        if complex_e.EntryRefsOS:
            
            # find the complex entry ref (there could be one or more variant entry refs listed along side the complex entry)
            for entryRef in complex_e.EntryRefsOS:
                if entryRef.RefType == 1: # 1=complex form, 0=variant
                    if entryRef.ComplexEntryTypesRS:
                        
                        # there could be multiple types assigned to a complex form (e.g. Phrasal Verb, Derivative)
                        # just see if one of them is one of the ones in the types list (e.g. Phrasal Verb)
                        for complexType in entryRef.ComplexEntryTypesRS:
                            if ITsString(complexType.Name.BestAnalysisAlternative).Text in typesList:
                                pos_in_list = get_position_in_component_list(e, complex_e)
                                
                                # The entry we are on has to be at the right position in the complex form's component list
                                # if we match the current component count this means we have a part of a complex form that is
                                # in the right position. Add the complex entry to the list.
                                if pos_in_list == currentComplexCount:
                                    foundAtLeastOneMatch = True
                                    pv_list.append(complex_e)
                                    break;
                                
                                # if we didn't match a currently going complex search and the position in the list is 0, 
                                # it could be this is the start of a new complex form
                                elif pos_in_list == 0 and currentComplexCount > 0:
                                    startOfNewList = True
                                    pv_list.append(complex_e)
                                    break;
                                    
    return (pv_list, currentComplexCount, foundAtLeastOneMatch, startOfNewList)

def collectPhrasalVerbs(e, pv_list, ccc, foundAtLeastOneMatch, startOfNewList, analysisOccurance, prev_e, getSurfaceForm, bundle_list, outputStrList, TreeTranSort, \
                        prevGuid, BundleGuidMap, itemCount, savedTags, shared_complex_e, prev_pv_list, saved1stbaselineWord):
    surfaceForm = ''
    
    if len(pv_list) == 0: # no phrasal verbs
        prev_pv_list = []
        ccc = 0
    else: # yes, we have phrasal verbs
        # It could happen that we find a word that is the beginning of one complex form and at the same time
        # a non-initial part of another. In this case we go with the non-initial match and we don't reset the ccc to 0
        # Only reset it if we only find this entry to be the start of a new complex entry.
        if foundAtLeastOneMatch == False and startOfNewList == True:
            prev_pv_list = []
            ccc = 0
        if ccc == 0:
            saved1stbaselineWord = ITsString(analysisOccurance.BaselineText).Text
        ccc += 1
        # First make sure that the entry of the last word isn't the same as this word, i.e. a word doubled. In that case, 
        # of course there are going to be shared complex forms, but we are only interested in different entries forming 
        # a phrasal verb.
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
                    # remove 2 things, the n/adj/... and it's tag from being output
                    saveStr = outputStrList.pop()
                    # very first pop may have just popped punctuation or spacing, if so don't pop again
                    if len(outputStrList) > 0:
                        saveStr = outputStrList.pop() 
                    
                    # If TreeTran remove the previous word from the Guid Map
                    if TreeTranSort:
                        BundleGuidMap.pop(prevGuid, None) # if not found None is returned
                        # itemCount is used to track the beginning of each sentence. Since we removed two 
                        # items from the output string list, we reduce the item count by 2.
                        itemCount -= 2 
                
                # The first component(s) could have tags (from affixes or inflection info.)
                # Save these tags so they can be put on the end of the complex form.
                # This kind of assumes that inflection isn't happening on multiple components
                # because that might give a mess when it's all duplicated on the complex form.
                g = re.search(r'.+?<\w+>(<.+>)', saveStr)
                if (g): 
                    savedTags += g.group(1)
                    
    return (prev_pv_list, ccc, surfaceForm, outputStrList, BundleGuidMap, itemCount, saved1stbaselineWord, shared_complex_e)

def processSharedComplexForm(shared_complex_e, saved1stbaselineWord, outStr, report, inflFeatAbbrevs, savedTags):

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
            outStr += '<'+underscores(ITsString(senseOne.MorphoSyntaxAnalysisRA.InflectionClassRA.\
                                  Abbreviation.BestAnalysisAlternative).Text)+'>'         

        # Get any features the stem or root might have
        if senseOne.MorphoSyntaxAnalysisRA.MsFeaturesOA:
            feat_abbr_list = []
            # The features might be complex, make a recursive function call to find all features
            get_feat_abbr_list(senseOne.MorphoSyntaxAnalysisRA.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
            
            # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
            for _, abb in sorted(feat_abbr_list, key=lambda x: x[0]): # 1st item group name
                outStr += '<' + underscores(abb) + '>'
        
        # Get any features that come from irregularly inflected forms        
        # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
        for _, abb in sorted(inflFeatAbbrevs, key=lambda x: x[0]):
            outStr += '<' + underscores(abb) + '>'
            
        # Add the saved tags from a previous complex form component
        outStr += savedTags
    else:
        report.Warning("No senses found for the complex form.")

    return outStr