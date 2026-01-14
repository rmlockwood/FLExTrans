#
#   Testbed
#
#   Ron Lockwood
#   SIL International
#   12/24/2022
#
#   Version 3.14.1 - 7/23/25 - Ron Lockwood
#    Fixes #1016. Repeat the expected result in the actual result column.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.2 - 2/17/25 - Ron Lockwood
#    Better handling of angle brackets. Improved escaping reserved Apertium characters
#    by making sure the character is not already escaped. This avoids double-escaping.
#    Also a new parse string function to better find the lemma and symbols when 
#    escaped angle brackets are present.
#
#   Version 3.12.1 - 1/3/25 - Ron Lockwood
#    Fixes #241. Also fix if the lemma is something like 7.1, we have an empty lemma.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11 - 9/5/24 - Ron Lockwood
#    Escape Apertium lemmas when writing the data stream to a file.
#    Unescape Apertium lemmas when coming from a file for user display.
#
#   Version 3.10.5 - 7/13/24 - Ron Lockwood
#    Fixes #668. The N.N wasn't being shown in the tooltip. Show it always.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Fixes #476. Remove the EOL stuff we get from HermitCrab.
#
#   Version 3.7.2 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.1 - 1/10/23 - Ron Lockwood
#    Renamed some functions to be camel case. Also added common function processAdvancedResults.
#
#   Version 3.7 - 12/24/22 - Ron Lockwood
#    Initial version.
#
#   Classes that model objects for the testbed.
#   See design diagrams here: https://app.moqups.com/pNl8pLlTB6/view/page/a8dd9b3cb 

import re
import os
import xml.etree.ElementTree as ET
import uuid
import unicodedata
from datetime import datetime

import TestbedValidator
import ReadConfig 
import Utils

from PyQt5.QtCore import QCoreApplication, QDateTime

# Define _translate for convenience
_translate = QCoreApplication.translate

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
XML_DATETIME_FORMAT_QT = 'yyyy-MM-dd hh:mm:ss' # Qt format for date time

## Viewer constants
# Main color of the headwords
LEMMA_COLOR = '000000' #black
CHUNK_LEMMA_COLOR = 'FF00FF' #purple
# For grammatical category - always the 1st symbol
GRAM_CAT_COLOR = '0070C0' #blue
CHUNK_GRAM_CAT_COLOR = '0000FF' #darker blue
# The color of affixes or other things such as features, classes, etc.
AFFIX_COLOR = '00B050' #green
SUCCESS_COLOR = '00B050' #green
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

def getXMLEntryText(node):

    # Start with nodeText as the text part of the left node
    nodeText = node.text

    # But there is potentially more data. <b />'s which represent blanks might be there
    # Each b has a tail portion that needs to be concatenated to the nodeText
    for bElement in node.findall('b'):

        if bElement.tail:

            nodeText += ' ' + bElement.tail

    return nodeText

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
            lemma_parts = re.split('(\d+)', self.__headWord, flags=re.RegexFlag.A) # last item is empty re.RegexFlag.A=ASCII-only match
            
            # Output the lexeme
            span = outputLUSpan(p, LEMMA_COLOR, lemma_parts[0], rtl)
        
            # Output the subscript homograph # and sense # (if they exist)
            if self.__gramCat != SENT:
                addSubscript(span, lemma_parts[1]+'.'+self.__senseNum)
            
            # Check for RTL
            if rtl == True:
                # prepend the RTL marker
                symb = '\u200F' + self.__gramCat
            else:
                symb = self.__gramCat
            
            # output the symbol
            outputLUSpan(p, GRAM_CAT_COLOR, ' '+symb, rtl)
            
            for tag in self.__otherTags:
            
                # Check for RTL
                if rtl == True:
                    # prepend the RTL marker
                    symb = '\u200F' + tag
                else:
                    symb = tag
                
                # output the symbol
                outputLUSpan(p, AFFIX_COLOR, ' '+symb, rtl)
            
            self.__formatedString = ET.tostring(p, encoding='unicode')
        else:
            pass
            
        return self.__formatedString
    
    def toApertiumString(self):
        
        # Escape reserved characters with a backslash
        ret_str = '^' + Utils.escapeReservedApertChars(self.__headWord)

        if self.__gramCat != SENT:
            ret_str += '.' + self.__senseNum

        # Add grammatical category as a tag
        ret_str += '<' + self.__gramCat + '>'

        # Add the rest of the tags
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
        lemma, tokens = parseString(self.__inStr)

        # If we have less than 1 item, it's badly_formed. We need at least a lemma plus it's gramm. category
        if len(tokens) < 1:
            self.__badly_formed = True
            return
        
        # gram. cat. is the first one
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
        
        # If we have less than 1 item, it's badly_formed. We need at least a lemma plus it's gramm. category
        if len(tokens) < 1:
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
        
        luStr = Utils.split_compounds(myStr)
        
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
            raise ValueError(_translate("Testbed", 'No more lines to read in the synthesis file.'))
        
        # Remove the dummy EOL lexical unit at the end. STAMP results.
        line = re.sub(r' @*EOL', '', line)
        
        # Remove the dummy EOL lexical unit at the end. HermitCrab results.
        line = re.sub(' %0%\^@EOL<EOL>\$%', '', line)
        
        # Remove multiple spaces
        line = re.sub('\s{2,}', ' ', line)
        line = line.rstrip()

        # Convert to decomposed unicode for comparison. When we read in the file testbed
        # We did the same. For some reason this wasn't needed for STAMP output, but seems to be needed for HermitCrab
        line = unicodedata.normalize('NFD', line)

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
        
        configMap = ReadConfig.readConfig(report)
        if not configMap:
            raise ValueError()
    
        self.__testbedPath = ReadConfig.getConfigVal(configMap, ReadConfig.TESTBED_FILE, report)
        if not self.__testbedPath:
            raise ValueError()
        
        # Get the composed characters setting
        composed = ReadConfig.getConfigVal(configMap, ReadConfig.COMPOSED_CHARACTERS, report)
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
                raise ValueError(_translate("Testbed", "The testbed file: {filePath} could not be read or written.").format(filePath=self.__testbedPath))
            
            try:
                self.__testbedTree = ET.parse(self.__testbedPath)
            except:
                raise ValueError(_translate("Testbed", "The testbed file: {filePath} is invalid.").format(filePath=self.__testbedPath))

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
        self.__rootNode.attrib[END_DATE_TIME] = QDateTime.currentDateTime().toString(XML_DATETIME_FORMAT_QT)

    def startTest(self, testbedXMLObj):
        self.__rootNode.attrib[START_DATE_TIME] = QDateTime.currentDateTime().toString(XML_DATETIME_FORMAT_QT)
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

        configMap = ReadConfig.readConfig(report)
        if not configMap:
            raise ValueError()
    
        resultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TESTBED_RESULTS_FILE, report)
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
                raise ValueError(_translate("Testbed", "The testbed results file: {resultsPath} is invalid.").format(resultsPath=resultsPath))

            self.__XMLObject = FLExTransTestbedResultsXMLObject(self.__testbedResultsTree.getroot())
    
    def getResultsXMLObj(self):
        return self.__XMLObject
    
    def write(self):
        self.__testbedResultsTree.write(self.__resultsPath, encoding='utf-8', xml_declaration=True)

# Create a span element and set the color and text
def outputLUSpan(parent, color, text_str, rtl):
    
    span = ET.Element('span')
    parent.append(span)
    span.attrib['style'] = 'color:#' + color
    
    # Check for RTL
    if rtl == True:
        
        # prepend the RTL marker
        text_str = '\u200F'+text_str
        
    span.text = text_str
    
    return span

def addSubscript(span, num):
    
    sub = ET.Element('sub')
    sub.attrib['style'] = 'font-size:' + SUBSCRIPT_SIZE_PERCENTAGE + '%'
    span.append(sub)
    sub.text = num
        
def colorInnerLU(lemma, symbols, parent_element, rtl, show_unk):

    # Split off the homograph_num.sense_num (if present; sent punctuation won't have it)
    lemma_parts = re.split('(\d+\.\d+)', lemma, flags=re.RegexFlag.A) # last item is empty, re.RegexFlag.A=ASCII only match
    
    # Check for an @
    if lemma_parts[0] and lemma_parts[0][0] == '@':
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
    span = outputLUSpan(parent_element, lexeme_color, lemma_parts[0], rtl)
    
    # Output the subscript
    if len(lemma_parts) > 1:
        addSubscript(span, lemma_parts[1])
    
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
        outputLUSpan(parent_element, symbol_color, ' '+symb, rtl)

def parseString(inputStr):
    """
    Parse a string into main part and symbols using regex.
    Symbols are defined as content between < and > at the end of the string.
    The main part can contain escaped brackets \< and \>.
    
    Args:
        inputStr (str): Input string to parse
        
    Returns:
        tuple: (mainPart, listOfSymbols)
        
    Examples:
        >>> parseString("abc<zx><uv>")
        ('abc', ['zx', 'uv'])
        >>> parseString("abc\\<def\\><zx>")
        ('abc\\<def\\>', ['zx'])
        >>> parseString(">><sent>")
        ('>>', ['sent'])
        >>> parseString("\\>\\><sent>")
        ('\\>\\>', ['sent'])
        >>> parseString("d\>a<b>c<zx><uv>")
        ('d\\>a<b>c', ['zx', 'uv'])
        >>> parseString("d<<c<zx><uv>")
        ('d<<c', ['zx', 'uv'])
    """
    # Need a string without at least trailing spaces.
    newIn = inputStr.strip()
    
    # Find all matches from the string
    allMatches = list(Utils.reFindSymbols.finditer(newIn))
    
    # If no matches found, return original string and empty list
    if not allMatches:
        return newIn, []
    
    # Check if the matches are consecutive at the end
    symbolList = []
    lastPosition = len(newIn)
    
    # Process matches from right to left
    for match in reversed(allMatches):

        if match.end() == lastPosition:

            # This is a valid symbol at the end
            symbolList.insert(0, match.group()[1:-1])  # Remove < and >
            lastPosition = match.start()
        else:
            # Stop when we find a non-consecutive match
            break
    
    mainPart = newIn[:lastPosition]

    # If the lu ends in a space add a space 'symbol'
    # We're doing this because that's what the old code did and other functions expect this.
    # Without it, the display in the LRT doesn't have spaces between displayed LUs.
    if inputStr[-1] == ' ':
        
        symbolList.append(' ')

    return mainPart, symbolList

# Split a compound from one lexical unit containing multiple words to multiple
def processLexicalUnit(lu_str, parent_element, rtl, show_unk):
    
    # Split off the symbols from the lemma in the lexical unit
    lemma, symbols = parseString(lu_str)

    # Remove the slash in front of reserved characters. We really only need this for displaying the
    # Execution log, but I think it doesn't hurt for other contexts.
    lemma = Utils.unescapeReservedApertChars(lemma)
    
    colorInnerLU(lemma, symbols, parent_element, rtl, show_unk)
    
def processChunkLexicalUnit(lu_str, parent_element, rtl):
    
    # Split off the symbols from the lemma in the lexical unit
    lemma, symbols = parseString(lu_str)

    # if the first symbol is UNK, use a special lemma color
    if len(symbols) > 0 and symbols[0] == 'UNK':
        
        lexeme_color = UNKNOWN_LEMMA_COLOR
    else:
        lexeme_color = CHUNK_LEMMA_COLOR
    
    # Output the lexeme
    outputLUSpan(parent_element, lexeme_color, lemma, rtl)
    
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
        outputLUSpan(parent_element, symbol_color, ' '+symb, rtl)

# Format advanced (chunk) output with color coding.
# This function is used in 3 places. 
# 1) for showing transfer results in the Live Rule Tester
# 2) for displaying lines with the View Source/Target Apertium Text Tool
# 3) for displaying apertium log results. This one uses a stripped down version of the function.
# we need the dummy parameter for use in the LRT processLogLines function
def processAdvancedResults(targetOutput, pElem, RTLflag, dummy=True, punctuationPresent=False):            
        
        # Split off the advanced stuff that precedes the brace {
        # parsing: '--^ch_xx<ABC>{^hello1.1<excl>$ ^Ron1.1<Prop>$}$~~ ^ch_yy<Z>{^yo1.1<n>$}$++'
        # gives: ['--^ch_xx<ABC>', '^hello1.1<excl>$ ^Ron1.1<Prop>$', '$~~ ^ch_yy<Z>', '^yo1.1<n>$', '$++']
        tokens = re.split('{|}', targetOutput)
        
        # process pairs of tokens
        for i in range(0, len(tokens)-1): # skip the last one for now
            
            tok = tokens[i]
        
            # the even # elements are the advanced stuff
            if i%2 == 0:
                
                chunk = tok
                
                if punctuationPresent:
                    
                    # remove the $ from the advanced part
                    tok = re.sub('\$', '', tok)
                    
                    # split on ^ and output any punctuation
                    [punc, chunk] = re.split('\^', tok)
                
                    # don't put out anything when it's a default chunk
                    if re.search('^default', chunk):
                        continue
                
                    # TODO: not sure if we have punctuation in the the live rule tester. Might not need a lot of this code
                    # First, put out the punctuation. If the punctuation is null, put
                    # out a space. Except if it's the first punctuation and it null.
                    if len(punc) > 0:
                        
                        outputLUSpan(pElem, PUNC_COLOR, punc, RTLflag)
                    
                    elif i > 0:
                        
                        outputLUSpan(pElem, PUNC_COLOR, ' ', RTLflag)
                        
                # Now put out the chunk part
                processChunkLexicalUnit(chunk, pElem, RTLflag)
                
                # Put out a [ to surround the normal lex. unit
                outputLUSpan(pElem, CHUNK_LEMMA_COLOR, ' [', RTLflag)

            # process odd # elements -- the normal stuff (that was within the braces)
            else:
                
                # parse the lexical units. This will give us tokens before, between 
                # and after each lu. E.g. ^hi1.1<n>$, ^there2.3<dem><pl>$ gives
                #                         ['', 'hi1.1<n>', ', ', 'there2.3<dem><pl>', '']
                subTokens = re.split('\^|\$', tok)
                
                # process pairs of tokens (punctuation and lexical unit)
                for j in range(0, len(subTokens)-1, 2):
                    
                    myStr = ''
                    
                    if punctuationPresent:
                        
                        # First, put out the punctuation. If the punctuation is null, put
                        # out a space. Except if it's the first punctuation and it null.
                        if len(subTokens[j]) > 0:
                            
                            outputLUSpan(pElem, PUNC_COLOR, subTokens[j], RTLflag)
                        else:
                            # we need a preceding space if we are not within brackets
                            if re.search('^default', chunk) is not None:
                                
                                myStr = ' '
                    else:
                        # Put a space between LUs inside the braces
                        if j > 0:

                            myStr = ' '
                                    
                    outputLUSpan(pElem, PUNC_COLOR, myStr, RTLflag)
                    
                    # parse the lexical unit and add the elements needed to the list item element
                    processLexicalUnit(subTokens[j+1], pElem, RTLflag, True)
                    
                # process last subtoken for the stuff inside the {}
                if len(subTokens[-1]) > 0:
                    
                    outputLUSpan(pElem, PUNC_COLOR, subTokens[-1], RTLflag)
                
                # Put out a closing ] if it wasn't a default chunk
                if re.search('^default', chunk) is None:
                    
                    outputLUSpan(pElem, CHUNK_LEMMA_COLOR, ']', RTLflag)

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

        # If we have a sub-element which will be the 1.1 numeric thing
        if len(spanEl) > 0:

            retStr += ET.tostring(spanEl[0], encoding='unicode')
        
        retStr += f'</{spanEl.tag}>'

    retStr += '</p>'
    
    return retStr