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
import uuid
from datetime import datetime
import TestbedValidator

from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO.DomainServices import SegmentServices

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
TARGET_OUTPUT = 'targetOutput' 
EXPECTED_RESULT = 'expectedResult' 
ACTUAL_RESULT = 'actualResult' 
SOURCE_DIRECTION = 'source_direction' 
TARGET_DIRECTION = 'target_direction' 
N_ATTRIB = 'n' 
ID = 'id' 
IS_VALID = 'is_valid' 
ORIGIN = 'origin' 
RTL = 'rtl' 
LTR = 'ltr' 
NA = 'n/a' 
YES = 'yes'
NO = 'no'
DEFAULT = 'default'

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
    def isWellFormed(self):
        if self.__testNode.attrib[IS_VALID] == YES:
            return True
        return False
    def getOrigin(self):
        return self.__testNode.find(SOURCE_INPUT).attrib(ORIGIN)
    def getExpectedResult(self):
        return self.__testNode.find(TARGET_OUTPUT+'/'+EXPECTED_RESULT).text
    def getActualResult(self):
        return self.__testNode.find(TARGET_OUTPUT+'/'+ACTUAL_RESULT).text
    def getTestNode(self):
        return self.__testNode
    
    # Convert all the lexical units into one string    
    def getLUString(self):
        ret_str = ''
        
        for lu in self.__luList:
            ret_str += ' ' + lu.toString()
        
        return ret_str.strip()
    
    def getApertiumString(self):
        ret_str = ''
        
        for lu in self.__luList:
            ret_str += ' ' + lu.toApertiumString()
            
        return ret_str.strip()
    
    # See if this object is equal to another object in terms of the lexical unit portion
    def equalLexUnits(self, myTestObj):
        localLUString = self.getLUString()
        cmpLUString = myTestObj.getLUString()
        
        if localLUString == cmpLUString:
            return True
        
        return False 

    def validate(self, myValidator):
        markInvalid = False
        
        testNode = self.getTestNode()

        if testNode.attrib[IS_VALID] == YES:
            prevInvalidFlag = True
        else:
            prevInvalidFlag = False

        for lu in self.__luList:
            
            # any one invalid lexical unit means the test is invalid
            if myValidator.isValid(lu) == False:
                markInvalid = True
                break
        
        # See if we have a different value from before
        if markInvalid == prevInvalidFlag:
            
            self.__testChanged = True
            
            if markInvalid:
                testNode.attrib[IS_VALID] = NO
            else:
                testNode.attrib[IS_VALID] = YES
    
    def didTestChange(self):
        return self.__testChanged
            
    def dump(self, f_out):
        
        # each test goes on its own line
        f_out.write(self.getApertiumString().encode('utf-8')+'\n')

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
            myRoot = FLExTransTestbedXMLObject.getRoot()
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
    
    def startTest(self, testbedXMLObj):
        self.__rootNode.attrib[START_DATE_TIME] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    
    def initTestResult(self, testbedXMLObj):
        
        # create a new result object and set the start time and give it a blank end time
        resultXMLObj = TestbedResultXMLObject(self.__rootNode, None)
        resultXMLObj.startTest(testbedXMLObj)
        
        # new results are always put at the top of the list
        self.__resultXMLObjList.insert(0, resultXMLObj)
    
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
TESTBED_RESULTS_FILE_PATH = OUTPUT_FOLDER + '\\testbed_results.xml'

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