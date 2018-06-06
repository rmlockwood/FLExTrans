#
#   TestbedValidator
#
#   Ron Lockwood
#   SIL International
#   6/6/2018
#
#   Version 1.0 - ??/??/18 - Ron Lockwood
#    ???
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

from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO.DomainServices import SegmentServices

class TestbedValidator():
    def __init__(self, database, report):
        
        self.db = database
        self.report = report
        self.mapWordSenses = {}
        self.mapTags = {}
        
        # If validator cache file exists
        if self.cacheExists():
            # check if it's out of date
            if self.isCacheOutOfDate() == False:
                
                self.loadCache()
                
        self.readDatabaseValues()
        self.createCache()
    
    def isValid(self, lexUnit):
        valid = True
        
        wordSense = lexUnit.getHeadWord() + '.' + lexUnit.getSensNum()
        if self.isWordSenseValid(wordSense) and self.isGramCatValid(lexUnit.getGramCat()):
            
            # check tags
            tags = lexUnit.getOtherTags()
            for tag in tags:
                if not self.isTagValid(tag):
                    valid = False
                    break
            
        return valid
            

    def isCacheOutOfDate(self):
        pass
    def createCache(self):
        pass
    def loadCache(self):
        pass
    def cacheExists(self):
        return False
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
                                self.__saveAffixGloss(gloss)
                            else:
                                continue # err_list.append(('Skipping entry since the lexeme is of type: '+e.LexemeFormOA.ClassName, 1, TargetDB.BuildGotoURL(e)))
                        elif morphType not in morphNames:
                            if morphType == 'proclitic' or morphType == 'enclitic':
                                self.__saveAffixGloss(gloss)
                            else:
                                continue # err_list.append(('Skipping entry because the morph type is: ' + morphType, 1, TargetDB.BuildGotoURL(e)))

    def __saveAffixGloss(self, gloss):
        self.mapTags[gloss] = 7 # dummy value
                
    def readCategoryInfo(self):
        pass
    def readOtherInfo(self):
        pass
    def isWordSenseValid(self):
        pass
    def isGramCatValid(self):
        pass
    def isTagValid(self):
        pass
    