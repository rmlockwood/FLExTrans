#
#   TextClasses
#
#   Ron Lockwood
#   SIL International
#   12/24/2022
#
#   Version 3.11.2 - 9/5/24 - Ron Lockwood
#    Escape Apertium lemmas when writing the data stream to a file.
#    Unescape Apertium lemmas when coming from a file for user display.
#
#   Version 3.11.1 - 9/4/24 - Ron Lockwood
#    Add * to APERT_RESERVED and remove unneeded lemmaProbData stuff. Escape reserved characters
#    when getting the lemma.
#
#   Version 3.11 - 8/15/24 - Ron Lockwood
#    Support FLEx Alpha 9.2.2 which no longer supports Get Instance, use Get Service instead.
#
#   Version 3.10.3 - 5/1/24 - Ron Lockwood
#    More checking for None fixes when comparing to a guid.
#
#   Version 3.10.2 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10.1 - 1/12/24 - Ron Lockwood
#    Fixes #538. Escape brackets in the pre or post punctuation.
#
#   Version 3.10 - 1/1/24 - Ron Lockwood
#    Fixes #506. Better handling of 'punctuation' text that is a complete paragraph (line).
#
#   Version 3.9.2 - 8/17/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.1 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.8.3 - 5/5/23 - Ron Lockwood
#    Add a column to the table to show the verse number if it precedes a word. To do this a new class was added
#    which encapsulates the Link class and adds the verse number attribute.
#
#   Version 3.8.2 - 5/3/23 - Ron Lockwood
#    Don't substitute problem characters if it's a punctuation word.
#
#   Version 3.8.1 - 4/27/23 - Ron Lockwood
#    Fixes #363. Reworked the logic to get the interlinear text information first, then if there are
#    no senses to process, exit. Also do the progress indicator 3 times, once for getting interlinear data, once
#    for the gloss map and once for the building of the linking objects.
#
#   Version 3.8 - 4/18/23 - Ron Lockwood
#    Allow more than 1 word between complex form components. For now allow up to 4.
#
#   Version 3.7 - 12/24/22 - Ron Lockwood
#    Initial version.
#
#   Classes that model text objects from whole text down to word.

import re
from SIL.LCModel import (
    IMoStemMsa,
    IWfiMorphBundleRepository,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString
import Utils

MAX_SKIPPED_WORDS = 4

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
    def getParagraphCount(self):
        return len(self.__parList)
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
    def getWordCount(self):
        return sum([x.getWordCount() for x in self.__parList])
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
    def warnForUnknownWords(self, noWarningProperNoun):
        multipleUnknownWords = False
        for par in self.__parList:
            if par.warnForUnknownWords(self.__unknownWordMap, noWarningProperNoun) == True:
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
    def getWordCount(self):
        return sum([x.getWordCount() for x in self.__sentList])
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
    def warnForUnknownWords(self, unknownWordMap, noWarningProperNoun):
        multipleUnknownWords = False
        for sent in self.__sentList:
            if sent.warnForUnknownWords(unknownWordMap, noWarningProperNoun) == True:
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
        self.firstGetByGuid = True
    def addWord(self, textWord):
        self.__wordList.append(textWord)
    def createGuidMap(self, insertList):
        for word in insertList:
            self.__guidMap[word.getGuid()] = word
        for word in self.__wordList:
            self.__guidMap[word.getGuid()] = word
    def getSurfaceAndDataForGuid(self, guid):
        if self.firstGetByGuid:
            self.firstGetByGuid = False
            return self.__guidMap[guid].getSurfaceFormWithVerseNum(),  self.__guidMap[guid].outputDataStream()
        else:
            return self.__guidMap[guid].getSurfaceForm(), self.__guidMap[guid].outputDataStream()
    def getSurfaceAndDataTupleList(self, tupList):
        for i, word in enumerate(self.__wordList):
            if i == 0:
                tupList.append((word.getSurfaceFormWithVerseNum(), word.outputDataStream()))
            else:
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
        if len(self.__wordList) > 0 and myGuid is not None:
            if self.__wordList[0].getGuid() is not None and self.__wordList[0].getGuid() == myGuid:
                return True
        return False
    def matchesLastWord(self, myGuid):
        if len(self.__wordList) > 1 and myGuid is not None: # > 1 since we may go back 2 words
            
            if self.__wordList[-1].isSentPunctutationWord():
                last = -2
            else:
                last = -1
            if self.__wordList[last].getGuid() is not None and self.__wordList[last].getGuid() == myGuid:
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
                                            
    def modifyList(self, myIndex, count, complexEn):
        componentList = []
        
        # Loop through the part of the word list that we will remove. Save the components in a list that we will add to the new word.
        for _ in range(0, count):
            componentList.append(self.__wordList.pop(myIndex)) # don't increment, the next one is in position myIndex after the previous pop
        
        # New object
        newWord = TextWord(self.__report)
        
        # Initialize it with the complex entry being the main entry of the word. Other attributes are drawn from the last
        # matching component. Tags will also transferred as needed
        newWord.initWithComplex(complexEn, componentList)
        
        # Insert the new word into the word list
        self.__wordList.insert(myIndex, newWord)
        
        # Update the guid map
        self.__guidMap[newWord.getGuid()] = newWord
        
    def modifyDiscontiguousList(self, myIndex, skippedWordsCount, complexEn):
        componentList = []
        
        # We want to pop the ith word and the i+skippedWordsCount+1 word, after the first pop everything moved up so pop i+skippedWordsCount the 2nd time
        componentList.append(self.__wordList.pop(myIndex))
        componentList.append(self.__wordList.pop(myIndex+skippedWordsCount))
        
        # New object
        newWord = TextWord(self.__report)
        
        # Initialize it with the complex entry being the main entry of the word. Other attributes are drawn from the last
        # matching component. Tags will also transferred as needed
        newWord.initWithComplex(complexEn, componentList)
        
        # Insert the new word into the word list after the skipped word
        self.__wordList.insert(myIndex+skippedWordsCount, newWord)
        
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
        myIndex = 0
        # Loop through the word list
        while myIndex < len(self.__wordList) - 1: # we don't have to check the last one, it can't match 2 or more things
            wrd = self.__wordList[myIndex]

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
                            if myIndex + count - 1 < len(self.__wordList):
                                
                                # All components have to match
                                for j in range(0, count):
                                    
                                    # Check if we have a match  
                                    if self.__wordList[myIndex+j].getFirstEntry() == componentEList[j]: # jth component in the list
                                        match = True
                                    else:
                                        match = False
                                        break
                                # break out of the outer loop
                                if match == True:
                                    break
                    if match == True:
                        # pop the matching words from the list and insert the complex word
                        self.modifyList(myIndex, count, cmplxEn)
            myIndex += 1
            
    def substituteDiscontiguousComplexForms(self, cmplxFormMap, discontigPOSList):
        myIndex = 0

        # Loop through the word list
        while myIndex < len(self.__wordList) - 1: # we don't have to check the last one, it can't match 2 or more things
            
            increment = 1
            wrd = self.__wordList[myIndex]

            # Process words that have complex entries
            if wrd.getEntryHandle() in cmplxFormMap:
                
                cmplxEnList = cmplxFormMap[wrd.getEntryHandle()]
                
                # We only need to deal with the list that is non-empty
                if len(cmplxEnList) > 0:
                    
                    # Sort the list from most components to least components
                    # each list item is a tuple. See below. We want the length of the component list.
                    cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True)
                    
                    match = False

                    # Loop through the complex entries tuples (cmplxEntry, componentEntryList)
                    for cmplxEn, componentEList in cmplxEnList:
                        
                        count = len(componentEList)

                        # Only process component lists with two items, i.e. a complex form with two components. 
                        # Working with 3 or more components makes it too complicated to figure out where the skipped words would be.
                        if count == 2:

                            # See if we match the first component
                            if self.__wordList[myIndex].getFirstEntry() == componentEList[0]:

                                # Now go hunting for the matching component as long as we don't exceed the max number of skipped words
                                # and the skipped words have a POS that's on the skipped words POS list
                                index = myIndex + 1
                                skippedCount = index-myIndex

                                # Loop until we hit the max or we would go off the end of the list.
                                while skippedCount <= MAX_SKIPPED_WORDS and index + 1 < len(self.__wordList):

                                    # POS not on the list
                                    if self.__wordList[index].posMatchForMiddleItemInDiscontigousList(discontigPOSList) == False:
                                        break

                                    # See if we find the 2nd component
                                    if self.__wordList[index+1].getFirstEntry() == componentEList[1]:

                                        match = True
                                        break

                                    index += 1
                                    skippedCount = index-myIndex

                                # break out of the outer loop
                                if match == True:
                                    break
                    if match == True:

                        # pop the matching words from the list and insert the complex word
                        self.modifyDiscontiguousList(myIndex, skippedCount, cmplxEn)
                        increment = skippedCount + 2 - 1 # 2 components, -1 because we popped off one component that didn't get replaced

            myIndex += increment
            
    def warnForUnknownWords(self, unknownWordMap, noWarningProperNoun):
        multipleUnknownWords = False
        for myIndex, word in enumerate(self.__wordList):

            # See if we have an uninitialized word which indicates it's unknown
            if word.isInitialized() == False:

                # Allow some unknown "words" without warning, such as sfm markers
                if len(word.getSurfaceForm()) > 0 and word.getSurfaceForm()[0] == '\\':
                    continue

                # Don't warn on the second time an unknown word is encountered
                if word.getSurfaceForm() in unknownWordMap:
                    multipleUnknownWords = True
                else:

                    # Don't warn if the word is capitalized, non-initial and the user wants to ignore non-sentence-initial capitalized words (Proper Nouns)
                    if noWarningProperNoun == True and len(word.getSurfaceForm()) > 0 and word.getSurfaceForm()[0].isupper() and myIndex > 0:
                        continue

                    # Give the warning
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
        self.__finalPunc += self.escapeReservedApertChars(myStr)
    def addInflFeatures(self, inflFeatAbbrevs):
        self.__inflFeatAbbrevsList[-1] = inflFeatAbbrevs # add to last slot
    def addInitialPunc(self, myStr):
        self.__initPunc += self.escapeReservedApertChars(myStr)
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
                                
        lem = Utils.do_capitalization(Utils.getHeadwordStr(self.__eList[-1]), myStr) # assume we can use the last entry as the one we want
        self.addLemma(Utils.add_one(lem) + '.' + str(senseNum+1))
    def escapeReservedApertChars(self, inStr):
        return Utils.reApertReserved.sub(r'\\\1', inStr)
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
    def getDataStreamSymbols(self, i, escapeLemma=False):
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
        
        newList = []

        # Put each symbol in angle brackets e.g. <sbjv>. Also _ for .
        for symbStr in symbols:

            symbStr = Utils.underscores(symbStr)

            if False: #escapeLemma:

                newList.append(self.escapeReservedApertChars(symbStr))
            else:
                newList.append(symbStr)
        
        return '<'+'><'.join(Utils.underscores(x) for x in newList)+'>'
    
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
    def getID(self):
        return self.getGuid()
    def getEntryIndex(self, e):
        for i, myE in enumerate(self.__eList):
            if myE == e:
                return i
        return None
    def getInflClass(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            if mySense := self.__senseList[i]:
                msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                if msa.InflectionClassRA:
                    return [ITsString(msa.InflectionClassRA.Abbreviation.BestAnalysisAlternative).Text]
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
            return self.__lemmaList[i]
        return ''
    def getPOS(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            if mySense := self.__senseList[i]:
                msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                if msa.PartOfSpeechRA:
                    return Utils.convertProblemChars(ITsString(msa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text, Utils.catProbData)
        return self.getUnknownPOS()
    def getSense(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            return self.__senseList[i]
        return None
    def getStemFeatures(self, i):
        if self.hasSenses() and i < len(self.__senseList):
            if mySense := self.__senseList[i]:
                msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                if msa.MsFeaturesOA:
                    # if we already have a populated list, we don't need to do it again.
                    if len(self.__stemFeatAbbrList) == 0:
                        # The features might be complex, make a recursive function call to find all features. Features keep getting added to list.
                        Utils.get_feat_abbr_list(msa.MsFeaturesOA.FeatureSpecsOC, self.__stemFeatAbbrList)
                    return self.getFeatures(self.__stemFeatAbbrList)
        return []
    def getSurfaceForm(self):
        return self.__surfaceForm
    def getSurfaceFormWithVerseNum(self):
        versNum = self.getVerseNum()
        if versNum:
            return versNum + ' ' + self.__surfaceForm
        else:
            return self.__surfaceForm
    def getUnknownPOS(self):
        return 'UNK'
    def getVerseNum(self):
        matchObj = re.search(r'\\v (\S+?) ', self.__initPunc)
        if matchObj:
            return matchObj.group(1)
        else:
            return ''
    def hasComponents(self):
        if len(self.__componentList) > 0:
            return True
        return False
    def hasEntries(self):
        if len(self.__eList) > 0:
            return True
        return False
    def hasPunctuation(self):
        # check for punctuation that is not spaces
        if re.search(r'\S', self.__initPunc) or re.search(r'\S', self.__finalPunc):
            return True
        return False
    def hasSenses(self):
        if len(self.__senseList) > 0:
            return True
        return False
    # Use bundle guid to look up the entry and initialize the entry, sense, and lemma
    def initialize(self, bundleGuid, DB):
        
        # get the repository that holds bundle guids
        repo = DB.project.ServiceLocator.GetService(IWfiMorphBundleRepository)
        
        # look up the guid
        try:
            bundleObject = repo.GetObject(bundleGuid)
        except:
            self.__report.Error('Could not find bundle Guid for word in the inserted word list.')
            return 
        
        # get the entry object and add it
        myEntry = ILexEntry(bundleObject.MorphRA.Owner)
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
            lem = headword = Utils.getHeadwordStr(myEntry)
            lem = Utils.add_one(lem)
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
        
    def matchCaseOfEntry(self, inputHeadWord, i):
        retStr = inputHeadWord
        if i < len(self.__lemmaList):

            if not self.isSentPunctutationWord():
                
                entryHeadword = Utils.getHeadwordStr(self.__eList[i])

                # If the entry headword starts with lower case, and the input headword starts with upper case, make it lower case
                if (len(entryHeadword) > 0 and entryHeadword[0].islower()) and (len(inputHeadWord) > 0 and inputHeadWord[0].isupper()):

                    retStr = inputHeadWord.lower()
        return retStr
    
    def notCompound(self):
        if len(self.__eList) > 1:
            return False # we have a compound of 2 or more entries
        return True
    def __outputDataForAllRoots(self, escapeLemma):
        retStr = ''
        if self.isSentPunctutationWord():
            return self.getLemma(0) + self.getDataStreamSymbols(0)
        else:
            for i, _ in enumerate(self.__lemmaList):
                retStr += self.escapeReservedApertChars(self.getLemma(i)) if escapeLemma else self.getLemma(i)
                retStr += self.getDataStreamSymbols(i, escapeLemma)
        return retStr
    def outputDataStream(self, escapeLemma=False):
        retStr = self.__initPunc+self.__outputWordDataStream(escapeLemma)+self.__finalPunc
        return retStr
    def __outputWordDataStream(self, escapeLemma):
        retStr = '^'+self.__outputDataForAllRoots(escapeLemma)+'$'
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
        fOut.write(Utils.split_compounds(self.outputDataStream(escapeLemma=True)))
    def writePrePunc(self, fOut):
        fOut.write(self.__initPunc)
    def writePostPunc(self, fOut):
        fOut.write(self.__finalPunc)
    def writeWordData(self, fOut):
        fOut.write(Utils.split_compounds(self.__outputWordDataStream(escapeLemma=True)))
        
