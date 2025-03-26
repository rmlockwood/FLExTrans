#
#   InterlinData
#
#   Ron Lockwood
#   SIL International
#   3/23/25
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Fixes #948. Use surface form for lemma when there is no analysis. This has the side effect that unanalyzed
#    words that are capitalized because they are at the beginning of a sentence will now be capitalized. FLEx
#    apparently changed because we used to be able to get the right cased form from the analysis object.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Initial version. Moved from Utils.py
#
#   Functions for getting interlinear data.

import re
import os
import xml.etree.ElementTree as ET
import tempfile

import Utils
import ReadConfig
from TextClasses import TextEntirety, TextParagraph, TextSentence, TextWord

from SIL.LCModel import ( # type: ignore
    ILexEntry,
    IPunctuationForm,
    IMoStemMsa,
    IWfiAnalysis,
    IWfiWordform,
    )

from SIL.LCModel.DomainServices import SegmentServices  # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore
from System import Guid   # type: ignore
from System import String # type: ignore

CHECK_DELIMITER = True
DELIMITER_STR = '{'

class GetInterlinParams():

    def __init__(self, sentPunct, contents, typesList, discontigTypesList, discontigPOSList, noWarningProperNoun):

        self.sentPunct = sentPunct
        self.contents = contents
        self.typesList = typesList
        self.discontigTypesList = discontigTypesList
        self.discontigPOSList = discontigPOSList
        self.noWarningProperNoun = noWarningProperNoun

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

def importGoodParsesLog():

    logList = []

    f = open(os.path.join(tempfile.gettempdir(), Utils.GOOD_PARSES_LOG))

    for line in f:

        (numWordsStr, flagStr) = line.rstrip().split(',')

        if flagStr == '1':
            parsed = True
        else:
            parsed = False

        logList.append((int(numWordsStr), parsed))

    return logList

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
            report.Error("Could not find a GUID in the TreeTran results file. Perhaps TreeTran is not putting out all that you expect. anaRec id=" + anaRec.attrib[Utils.ID_STR] + ". Exiting.")
            return None

        currGuid = Guid(String(pNode.text))
        analysisNode = anaRec.find('Analysis')
        if analysisNode != None:
            newSent = True

        myTreeSent.addGuid(currGuid)

    return obj_list

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

def initInterlinParams(configMap, report, contents):

    # Get punctuation string
    sentPunct = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)

    if not sentPunct:
        return

    typesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report)
    if not typesList:
        typesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_COMPLEX_TYPES, report):
        return None

    discontigTypesList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report)
    if not discontigTypesList:
        discontigTypesList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_TYPES, report):
        return None

    discontigPOSList = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report)
    if not discontigPOSList:
        discontigPOSList = []
    elif not ReadConfig.configValIsList(configMap, ReadConfig.SOURCE_DISCONTIG_SKIPPED, report):
        return None

    noWarningProperNounStr = ReadConfig.getConfigVal(configMap, ReadConfig.NO_PROPER_NOUN_WARNING, report, giveError=False)

    if not noWarningProperNounStr or noWarningProperNounStr == 'n':
        noWarningProperNoun = False
    else:
        noWarningProperNoun = True

    # Initialize a class
    interlinParams = GetInterlinParams(sentPunct, contents, typesList, discontigTypesList, discontigPOSList, noWarningProperNoun)

    return interlinParams

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
def getInterlinData(DB, report, params):

    prevEndOffset = 0
    currSegNum = 0
    myWord = None
    mySent = None
    savedPrePunc = ''
    newParagraph = False
    newSentence = False
    inMultiLinePuncBlock = False

    initProgress(params.contents, report)

    # Save a regex for splitting on sentence punctuation so we can clump sentence-final and sentence-non-final together
    # For the string "xy.'):\\" this would produce ['', '::', 'xy', ".'", ')', ':', '\\'] assuming :'. are in sentPunct
    reSplitPuncObj = re.compile(rf"([{''.join(params.sentPunct)}]+)")

    # Initialize the text and the first paragraph object
    myText = TextEntirety()
    myPar = TextParagraph()

    # Add the first paragraph
    myText.addParagraph(myPar)

    # Loop through each thing in the text
    ss = SegmentServices.StTextAnnotationNavigator(params.contents)
    for prog_cnt,analysisOccurance in enumerate(ss.GetAnalysisOccurrencesAdvancingInStText()):

        report.ProgressUpdate(prog_cnt)

        # Get the number of spaces between words. This becomes initial spaces for the next word
        numSpaces = analysisOccurance.GetMyBeginOffsetInPara() - prevEndOffset
        spacesStr = ' '*numSpaces

        # See if we are on a new paragraph (numSpaces is negative), as long as the current paragrah isn't empty
        if numSpaces < 0 and myPar.getSentCount() > 0:
            newParagraph = True

        # If we are on a different segment, it's a new sentence.
        if analysisOccurance.Segment.Hvo != currSegNum:
            newSentence = True

        # Save where we are
        currSegNum = analysisOccurance.Segment.Hvo
        prevEndOffset = analysisOccurance.GetMyEndOffsetInPara()

        # Deal with punctuation first
        if analysisOccurance.Analysis.ClassName == "PunctuationForm":

            puncForm = IPunctuationForm(analysisOccurance.Analysis)
            textPunct = ITsString(puncForm.Form).Text

            # Divide up the punctuation into sentence ending (ones that are in sentPunct) one ones that aren't
            myPuncList = reSplitPuncObj.split(textPunct) # also see above where this object is defined

            # Go through each cluster
            for i, myPunc in enumerate(myPuncList):

                # Skip empty list elements
                if myPunc == '':
                    continue

                # even indexes which are the non-sentence final ones
                # or odd indexes (sent final) where we are in the middle of a punctuation section (e.g. \xo 27.2-8)
                # this is shown by there being some final punctuation or some saved pre-punctuation
                if i % 2 == 0 or (i % 2 == 1 and myWord and (myWord.getFinalPunc() or savedPrePunc)):

                    # If we have a word that has been started, that isn't the beginning of a new sentence, and it's not sent. punc., make this final punctuation.
                    if myWord and not myWord.isSentPunctutationWord() and not newSentence and (CHECK_DELIMITER and not myPunc == DELIMITER_STR):

                        myWord.addFinalPunc(spacesStr + myPunc)
                        savedPrePunc = ''
                    else:

                        # New paragraph
                        if numSpaces < 0:

                            # if we have some prepunctutation and there's no final punctuation on the word (which means we haven't move pre-punct to final before)
                            # and we are not in a block of punctuation lines after punctuation lines, move the pre-punctuation to final on the word and reset pre-punctutation
                            if savedPrePunc and myWord and not myWord.getFinalPunc() and not inMultiLinePuncBlock:

                                myWord.addFinalPunc(savedPrePunc)
                                savedPrePunc = spacesStr + myPunc

                            # If we haven't processed any pre-punctuation yet, add to saved pre-punctuation as normal (no preceding newline)
                            elif not savedPrePunc:

                                savedPrePunc += spacesStr + myPunc
                                inMultiLinePuncBlock = True

                            # If we have already had saved pre-punctuation, now add a preceding newline
                            else:
                                savedPrePunc += '\n' + spacesStr + myPunc

                        # Not a new paragraph
                        else:
                            savedPrePunc += spacesStr + myPunc

                else: # odd - sent-final ones

                    ## save the punctuation as if it is its own word. E.g. ^.<sent>$

                    # create a new word object
                    myWord = TextWord(report)

                    # initialize it with the puctuation and sent as the "POS"
                    myWord.addLemma(myPunc)
                    myWord.setSurfaceForm(myPunc)
                    myWord.addPlainTextAffix('sent')

                    # See if we have any pre-punctuation
                    if len(savedPrePunc) > 0:
                        myWord.addInitialPunc(savedPrePunc)
                        savedPrePunc = ""

                    # Check for new sentence or paragraph. If needed create it and add to parent object. Also add current word to the sentence.
                    newSentence, newParagraph, mySent, myPar = checkForNewSentOrPar(report, myWord, mySent, myPar, myText, newSentence, newParagraph, spacesStr)

                # After the first time through, we've dealt with the spaces
                spacesStr = ''

            continue

        ## Now we know we have something other than punctuation

        prevWord = myWord

        # Start with a new word
        myWord = TextWord(report)

        # See if we have any pre-punctuation
        if savedPrePunc:

            # See if we have a new paragraph (which is shown by the numSpaces being negative) which means a paragraph of only punctuation.
            # If so, add a newline to the punctuation
            if numSpaces < 0:

                if prevWord and not prevWord.getFinalPunc() and not inMultiLinePuncBlock:

                    prevWord.addFinalPunc(savedPrePunc)
                    savedPrePunc = ''
                else:
                    savedPrePunc += '\n'

                # prevent an empty 1st paragrah
                if myText.getParagraphCount() == 1 and myText.getSentCount() == 0:
                    newParagraph = False

            myWord.addInitialPunc(savedPrePunc)
            savedPrePunc = ""

        inMultiLinePuncBlock = False

        # Check for new sentence or paragraph. If needed create it and add to parent object. Also add current word to the sentence.
        newSentence, newParagraph, mySent, myPar = checkForNewSentOrPar(report, myWord, mySent, myPar, myText, newSentence, newParagraph, spacesStr)

        # Figure out the surface form and set it.
        beg = analysisOccurance.GetMyBeginOffsetInPara()
        end = analysisOccurance.GetMyEndOffsetInPara()
        surfaceForm = ITsString(analysisOccurance.Paragraph.Contents).Text[beg:end]

        # Set surfaceForm 
        myWord.setSurfaceForm(surfaceForm)

        if analysisOccurance.Analysis.ClassName == "WfiGloss":
            wfiAnalysis = IWfiAnalysis(analysisOccurance.Analysis.Analysis)   # Same as Owner

        elif analysisOccurance.Analysis.ClassName == "WfiAnalysis":
            wfiAnalysis = IWfiAnalysis(analysisOccurance.Analysis)

        # We get into this block if there are no analyses for the word or an analysis suggestion hasn't been accepted.
        elif analysisOccurance.Analysis.ClassName == "WfiWordform":

            # Set the lemma to be the same as the surface form.
            myWord.addLemma(surfaceForm)
            continue

        # Don't know when we ever would get here
        else:
            wfiAnalysis = None

        # Go through each morpheme bundle in the word
        for bundle in wfiAnalysis.MorphBundlesOS:

            if bundle.SenseRA:
                if bundle.MsaRA and bundle.MorphRA:

                    tempEntry = ILexEntry(bundle.MorphRA.Owner)

                    # We have a stem. We just want the headword and it's POS
                    if bundle.MsaRA.ClassName == 'MoStemMsa':

                        msa = IMoStemMsa(bundle.MsaRA)

                        tempGuid = myWord.getGuid()

                        # Just save the the bundle guid for the first root in the bundle
                        if tempGuid is None: # we can't use == None because the guid class doesn't implement __eq__

                            # Only save the guid for a root, not a clitic
                            if not Utils.isClitic(tempEntry):

                                myWord.setGuid(bundle.Guid) # identifies a bundle for matching with TreeTran output

                        # If we have an invalid POS, give a warning
                        if not msa.PartOfSpeechRA:

                            #myWord.addLemmaFromObj(wfiAnalysis.Owner)
                            report.Warning('No grammatical category found for the source word: '+ myWord.getSurfaceForm(), DB.BuildGotoURL(tempEntry))
                            break

                        if bundle.MorphRA:
                            # Go from variant(s) to entry/variant that has a sense. We are only dealing with senses, so we have to get to one. Along the way
                            # collect inflection features associated with irregularly inflected variant forms so they can be outputted.
                            inflFeatAbbrevs = []
                            tempEntry = Utils.GetEntryWithSensePlusFeat(tempEntry, inflFeatAbbrevs)

                            # If we have an enclitic or proclitic add it as an affix, unless we got an enclitic with no root so far
                            # in this case, treat it as a root
                            if Utils.isClitic(tempEntry) == True and not (Utils.isEnclitic(tempEntry) and myWord.hasEntries() == False):

                                # Check for invalid characters
                                if Utils.containsInvalidLemmaChars(Utils.as_string(bundle.SenseRA.Gloss)):

                                    report.Error(f'Invalid characters in the affix: {Utils.as_string(bundle.SenseRA.Gloss)}. The following characters are not allowed: {Utils.RAW_INVALID_LEMMA_CHARS}', DB.BuildGotoURL(tempEntry))
                                    return myText
                                
                                # Add the clitic
                                myWord.addAffix(bundle.SenseRA.Gloss)

                            # Otherwise we have a root or stem or phrase
                            else:

                                # See if there are any invalid chars in the headword
                                if Utils.containsInvalidLemmaChars(Utils.getHeadwordStr(tempEntry)):
                                    
                                    report.Error(f'Invalid characters in the source headword: {Utils.getHeadwordStr(tempEntry)}. The following characters are not allowed: {Utils.RAW_INVALID_LEMMA_CHARS}', DB.BuildGotoURL(tempEntry))
                                    return myText

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
                                    report.Warning("Couldn't find the sense for source headword: "+Utils.getHeadwordStr(tempEntry))
                        else:
                            report.Warning("Morph object is null.")

                    # We have an affix
                    else:
                        if bundle.SenseRA:
                             
                                # Check for invalid characters
                            if Utils.containsInvalidLemmaChars(Utils.as_string(bundle.SenseRA.Gloss)):

                                report.Error(f'Invalid characters in the affix: {Utils.as_string(bundle.SenseRA.Gloss)}. The following characters are not allowed: {Utils.RAW_INVALID_LEMMA_CHARS}')
                                return myText
                            
                            myWord.addAffix(bundle.SenseRA.Gloss)
                        else:
                            report.Warning("Sense object for a source affix is null.")
                else:
                    if myWord.getLemma(0) == '' and wfiAnalysis.Owner.ClassName == 'WfiWordform':
                        myWord.addLemmaFromObj(IWfiWordform(wfiAnalysis.Owner))
                    else:
                        # Give a clue that a part is missing by adding a bogus affix
                        myWord.addPlainTextAffix('PartMissing')

                    report.Warning('No morphosyntactic analysis found for some part of the source word: '+ myWord.getSurfaceForm())
                    break # go on to the next word
            else:
                # Part of the word has not been tied to a lexical entry-sense
                if myWord.getLemma(0) == '' and wfiAnalysis.Owner.ClassName == 'WfiWordform':
                    myWord.addLemmaFromObj(IWfiWordform(wfiAnalysis.Owner))
                else:
                    # Give a clue that a part is missing by adding a bogus affix
                    myWord.addPlainTextAffix('PART_MISSING')

                report.Warning('No sense found for some part of the source word: '+ myWord.getSurfaceForm())
                break # go on to the next word

        # if we don't have a root or stem and we have something else like an affix, give a warning
        if myWord.getLemma(0) == '':

            # TODO: we might need to support a proclitic standing alone (no root) in which case we would convert the last proclitic to a root

            # need a root
            if wfiAnalysis.Owner.ClassName == 'WfiWordform':
                myWord.addLemmaFromObj(IWfiWordform(wfiAnalysis.Owner))
            else:
                myWord.addPlainTextAffix('ROOT_MISSING')

            report.Warning('No root or stem found for source word: '+ myWord.getSurfaceForm())

    # Handle any final punctuation text at the end of the text in its own paragraph
    if len(savedPrePunc) > 0:

        myWord.addFinalPunc('\n'+savedPrePunc)

    # Don't warn for sfm markers, but warn once for others
    if myText.warnForUnknownWords(params.noWarningProperNoun) == True:
        report.Warning('One or more unknown words occurred multiple times.')

    # substitute a complex form when its components are found contiguous in the text
    myText.processComplexForms(params.typesList)

    # substitute a complex form when its components are found discontiguous in the text
    if len(params.discontigTypesList) > 0 and len(params.discontigPOSList) > 0 and len(params.typesList) > 0:

        myText.processDiscontiguousComplexForms(params.typesList, params.discontigTypesList, params.discontigPOSList)

    return myText

