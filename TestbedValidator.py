#
#   TestbedValidator
#
#   Ron Lockwood
#   SIL International
#   6/6/2018
#
#   Version 1.0 - 6/9/18 - Ron Lockwood
#    Initial Version
#
#   A Class to validate if a lexical unit is good by checking against the FLEx database.

import re
import copy
import tempfile
import os
import xml.etree.ElementTree as ET
import platform
import subprocess
import uuid
import Utils
import ReadConfig
from datetime import datetime

from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import IFsClosedFeatureRepository
from SIL.FieldWorks.FDO import IMoInflClassRepository
from SIL.FieldWorks.FDO.DomainServices import SegmentServices

TESTBED_CACHE_FILE = 'testbed_cache.txt'
GRAM_CATS = 'Grammatical Categories:'
TAGS = 'Tags:'
WORD_SENSES = 'Word Senses:'

class TestbedValidator():
    def __init__(self, database, report):
        
        self.db = database
        self.report = report
        self.mapWordSenses = {}
        self.mapTags = {}
        self.mapCats = {}
        
        # If the validator cache file exists
        if self.cacheExists():
            # check if it's out of date
            if self.isCacheOutOfDate() == False:
                
                self.loadFromCache()
                return
                
        self.readDatabaseValues()
        self.saveToCache()
    
    def isWordSenseValid(self, wordSense):
        # Change spaces to underscores. Phrases and the like are stored with underscores
        wordSense = re.sub(' ', '_', wordSense) # change spaces to underscores

        # Accept lower or upper case versions of the word sense.
        if wordSense in self.mapWordSenses:
            return True
        elif wordSense.lower() in self.mapWordSenses:
            return True
        return False
    def isGramCatValid(self, gramCat):
        if gramCat in self.mapCats:
            return True
        return False
    def isTagValid(self, tag):
        if tag in self.mapTags:
            return True
        return False
    def isValid(self, lexUnit):
        valid = True
        
        # Sentence punctuation is always valid
        if lexUnit.getGramCat() == Utils.SENT:
            return valid
        
        wordSense = lexUnit.getHeadWord() + '.' + lexUnit.getSenseNum()
        if self.isWordSenseValid(wordSense) and self.isGramCatValid(lexUnit.getGramCat()):
            
            # check tags
            tags = lexUnit.getOtherTags()
            for tag in tags:
                if not self.isTagValid(tag):
                    valid = False
                    break
        else:
            valid = False
                
        return valid

    def isCacheOutOfDate(self):
        
        # Build a DateTime object with the FLEx DB last modified date
        flexDate = self.db.GetDateLastModified()
        dbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
        
        # Get the date of the cache file
        try:
            mtime = os.path.getmtime(self.getCacheFilePath())
        except OSError:
            mtime = 0
        cacheFileDateTime = datetime.fromtimestamp(mtime)
        
        if dbDateTime > cacheFileDateTime: # FLEx DB is newer
            return True 
        else: # cache file is newer
            return False

    def saveToCache(self):
        f = open(self.getCacheFilePath(), 'w')
        
        # TODO: check encodings
        f.write(GRAM_CATS+'\n')
        for cat in sorted(self.mapCats.keys()):
            f.write(cat.encode('utf-8')+'\n')
            
        f.write(TAGS+'\n')
        for tag in sorted(self.mapTags.keys()):
            f.write(tag.encode('utf-8')+'\n')
            
        f.write(WORD_SENSES+'\n')
        for wordSense in sorted(self.mapWordSenses.keys()):
            f.write(wordSense.encode('utf-8')+'\n')
        
        f.close()
            
    def loadFromCache(self):
        f = open(self.getCacheFilePath())
        
        # start with grammatical categories
        myMap = self.mapCats
        
        # Read each section of the cache file
        for i,line in enumerate(f):
            
            # Skip the first line
            if i == 0:
                continue
            
            # Next tags. Skip this line
            if line.rstrip() == TAGS:
                myMap = self.mapTags
                continue
            
            # Next word senses. Skip this line
            if line.rstrip() == WORD_SENSES:
                myMap = self.mapWordSenses
                continue
            
            myMap[unicode(line.rstrip(), 'utf-8')] = 7 # dummy value
         
        f.close()
           
    def getCacheFilePath(self):
        # build the path in the temp dir using project name + testbed_cache.txt
        return os.path.join(tempfile.gettempdir(), str(self.db.lp)+'_'+TESTBED_CACHE_FILE)
    def cacheExists(self):
        return os.path.exists(self.getCacheFilePath())
    def readDatabaseValues(self):
        # Go through the lexicon and save word senses and affixes
        self.readLexicalInfo()
        
        # Save all the categories for the database
        self.readCategoryInfo()
        
        # Save features abbreviations
        self.readOtherInfo()
        
    def readLexicalInfo(self):
        
        configMap = ReadConfig.readConfig(self.report)

        morphNames = ReadConfig.getConfigVal(configMap, 'TargetMorphNamesCountedAsRoots', self.report)
        
        if not morphNames: 
            self.report.Warning('Configuration File Problem. Morphnames not found.')
            return 

        # Loop through all the entries
        for i,e in enumerate(self.db.LexiconAllEntries()):
        
            morphType = ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text
            
            # If no senses, skip it
            if e.SensesOS.Count == 0:
                continue
                
            else: # Entry with senses
                # Loop through senses
                for i, mySense in enumerate(e.SensesOS):
                    
                    gloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
                    
                    # Process roots
                    # Don't process clitics in this block
                    if e.LexemeFormOA and \
                       e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
                       e.LexemeFormOA.MorphTypeRA and morphType in morphNames:
                    
                        # Set the headword value and the homograph #, if necessary
                        headWord = ITsString(e.HeadWord).Text
                        headWord = Utils.add_one(headWord)
    
                        # Only take word senses that have a grammatical category set.
                        if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                            
                            if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:            
                                                      
                                # build the word sense and add it to the map
                                wordSense = headWord+'.'+str(i+1)
                                wordSense = re.sub(' ', '_', wordSense) # change spaces to underscores
                                self.mapWordSenses[wordSense] = 7 # dummy value

                    # Now process non-roots
                    else:
                        if gloss == None:
                            continue
                        elif e.LexemeFormOA == None:
                            continue
                        elif e.LexemeFormOA.MorphTypeRA == None:
                            continue
                        elif e.LexemeFormOA.ClassName != 'MoStemAllomorph':
                            if e.LexemeFormOA.ClassName == 'MoAffixAllomorph':
                                gloss = re.sub(r'\.', '_', gloss)
                                self.__saveAffixGloss(gloss)
                            else:
                                continue # err_list.append(('Skipping entry since the lexeme is of type: '+e.LexemeFormOA.ClassName, 1, TargetDB.BuildGotoURL(e)))
                        elif morphType not in morphNames:
                            if morphType == 'proclitic' or morphType == 'enclitic':
                                gloss = re.sub(r'\.', '_', gloss)
                                self.__saveAffixGloss(gloss)
                            else:
                                continue # err_list.append(('Skipping entry because the morph type is: ' + morphType, 1, TargetDB.BuildGotoURL(e)))

    def __saveAffixGloss(self, gloss):
        self.mapTags[gloss] = 7 # dummy value
                
    def readCategoryInfo(self):
        # loop through all categories
        for pos in self.db.lp.AllPartsOfSpeech:

            # save abbreviation
            posAbbr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
            posAbbr = re.sub(' ', '_', posAbbr)
            self.mapCats[posAbbr] = 7
            
    def readOtherInfo(self): 
        
        # Get all the inflection feature abbreviations
        for feature in self.db.ObjectsIn(IFsClosedFeatureRepository):
            for value in feature.ValuesOC:
                abbr = ITsString(value.Abbreviation.BestAnalysisAlternative).Text
                abbr = re.sub(r'\.', '_', abbr)
                self.mapTags[abbr] = 7

        # Get all the inflection class abbreviations
        for inflClass in self.db.ObjectsIn(IMoInflClassRepository):
            abbr = ITsString(inflClass.Abbreviation.BestAnalysisAlternative).Text
            abbr = re.sub(r'\.', '_', abbr)
            self.mapTags[abbr] = 7
