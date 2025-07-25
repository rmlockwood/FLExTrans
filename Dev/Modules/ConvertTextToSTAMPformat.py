#
#   ConvertTextToSTAMPformat
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13.2 - 3/20/25 - Ron Lockwood
#    Modularized the main function to make it easy to call from other modules.
# 
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
# 
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 1/2/25 - Ron Lockwood
#    Fixes problem with HC synthesis where title-cased phrases were not coming out in the write case.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.6 - 3/7/24 - Ron Lockwood
#    Fixes #579. Space wasn't being inserted when there's punctuation with a space between.
#
#   Version 3.10.5 - 3/5/24 - Ron Lockwood
#    Fixes #580. Correctly form the circumfix affix for HermitCrab.
#
#   Version 3.10.4 - 1/26/24 - Ron Lockwood
#    Total rewrite of Conversion function. Instead of reading a line at a time of the transfer
#    results file, read it all at once, split it on lexical units and deal with the entire
#    punctuation between lexical units at one time. Parsing of the lexical units didn't change.
#
#   Version 3.10.3 - 1/12/24 - Ron Lockwood
#    Fixes #538. Escape brackets in the pre or post punctuation.
#
#   Version 3.10.2 - 1/3/24 - Ron Lockwood
#    Fixes #534. Give a better error message when the morphs for a lexical unit are less than 2.
#    Give the user the previous two and following two words for context.
#
#   Version 3.10.1 - 1/2/24 - Ron Lockwood
#    Fix problem where the 1st component ANA object wasn't getting its capitalization code
#    carried over to the final component ANA list.
#
#   Version 3.10 - 1/1/24 - Ron Lockwood
#    Fixes #506. Better handling of 'punctuation' text that is a complete paragraph (line).
#
#   Version 3.9.4 - 12/9/23 - Ron Lockwood
#    Use Utils version of get_feat_abbr_list. Re-indent some code.
#
#   Version 3.9.3 - 12/6/23 - Ron Lockwood
#    Fixes #517. Transfer \\nd and similar instead of interpreting as a newline.
#
#   Version 3.9.2 - 9/1/23 - Ron Lockwood
#    Fixes #492. Gracefully fail when HC master file setting is blank.
#
#   Version 3.9.1 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.6 - 5/9/23 - Ron Lockwood
#    Put out the sense # for variants when doing HermitCrab synthesis.
#
#   Version 3.8.5 - 5/3/23 - Ron Lockwood
#    Fixed bug in convert function where 'punctuation' at the end of a line wasn't carrying over
#    to the next line to become pre-punctuation for the first word.
#
#   Version 3.8.4 - 4/28/23 - Ron Lockwood
#    Don't give an error if the HermitCrab Synthesis flag (y/n) is not found in the config file.
#
#   Version 3.8.3 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.2 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8.1 - 4/7/23 - Ron Lockwood
#    Change module name from ...STAMP... to ...Synthesizer...
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.2 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   earlier version history removed on 3/10/25
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
#   For the design on how this module works in the HermitCrab synthesis situation,
#   see Basic Design in the DoHermitCrabSynthesis.py file.
#   
import re 
import os
from datetime import datetime

from SIL.LCModel import ( # type: ignore
    ILexSense,
    ILexEntryInflType,
    IFsClosedValue,
    IFsFeatStruc,
    IFsComplexValue,
    ILexEntry,
    IMoStemMsa,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString          # type: ignore

from flextoolslib import *                                                 
from flexlibs import FLExProject

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

import Mixpanel
import ReadConfig
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'ConvertTextToSTAMPformat'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Convert Text to Synthesizer Format",
        FTM_Version    : "3.14",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("ConvertTextToSTAMPformat", "Convert the file produced by Run Apertium into a text file in a Synthesizer format"),
        FTM_Help  : "", 
        FTM_Description: _translate("ConvertTextToSTAMPformat",
"""This module will take the Target Transfer Results File created by Apertium and convert it to a format suitable 
for synthesis, using information from the Target Project indicated in the settings.  Depending on the setting for 
HermitCrab synthesis, the output file will either be in STAMP format or in a format suitable for the HermitCrab 
synthesis program. 
The output file will be stored in different files depending on whether you are doing STAMP synthesis (default) or
HermitCrab synthesis. For STAMP, the file is what you specified by the Target Output ANA File setting -- typically
called target_text-ana.txt.
For HermitCrab, the file is what you specified by the Hermit Crab Master File setting -- typically called 
target_words-HC.txt. Both files are usually in the Build folder.
NOTE: messages and the task bar will show the SOURCE database as being used. Actually the target database 
is being used.""")}

app.quit()
del app

COMPLEX_FORMS = 'COMPLEX FORMS'
IRR_INFL_VARIANTS = 'IRREGULARLY INFLECTED VARIANT FORMS'
VARIANT_STR = "_variant_"

# model the information contained in one record in the ANA file
class ANAInfo(object):
    def __init__(self, pfxList=None, sfxList=None, pos=None, root=None, infxList=None):
        
        # If root is given, initialize with all the stuff.
        if root:
            # Treat the infixes as additional prefixes.
            # (I believe we could put them either before or after the root)
            if infxList:
                
                newList = pfxList+infxList
            else:
                newList = pfxList
                
            self.setAnalysisByPart(newList, pos, root, sfxList)
            
        self.setBeforePunc('')
        self.setAfterPunc('')
        self._firstComponentForHC = True
        self._originalLexicalUnitString = ''
    
    def addUnderscores(self, myStr):
        return re.sub(r' ', '_', myStr)
    def calcCase(self, word):
        
        if word.isupper():
            return '2'
        elif ' ' in word and word.istitle():
            return '3'
        elif word[0].isupper():
            return '1'
        else:
            return ''

    def capitalizeString(self, myStr):

        if self.getCapitalization() == '2':
            return myStr.upper()
        elif self.getCapitalization() == '1':
            return myStr.capitalize()
        elif self.getCapitalization() == '3':
            return myStr.title()
        else:
            return myStr

    def escapePunc(self, myStr):
        
        # if we have an sfm marker and the slash is not yet doubled, double it. Synthesize removes backslashes otherwise. And skip \n, but double \nd \no \nb
        if re.search(r'\\', myStr) and re.search(r'\\\\', myStr) == None:
            
            myStr =  re.sub(r'\\([^n]|nd|no|nb)', r'\\\\\1', myStr) 

        # Now convert newlines to slash n which STAMP will interpret as a newline
        myStr = re.sub('\n', r'\\n', myStr)

        return myStr
    
    def getAfterPunc(self):
        return self.AfterPunc
    def getAnalysis(self):
        return self.Analysis
    def getAnalysisPrefixes(self): # returns [] if no prefix
        return re.search(r'(.*)\s*<',self.Analysis).group(1).split()
    def getAnalysisRoot(self):
        return re.search(r'< .+ (.+) >',self.Analysis).group(1)
    # Apply the capitalization code algoritm to possibly capitalize the root string.
    def getCapitalizedAnalysisRoot(self):
        return self.capitalizeString(re.search(r'< .+ (.+) >',self.Analysis).group(1))
    def getAnalysisRootPOS(self):
        return re.search(r'< (.+) .+ >',self.Analysis).group(1)
    def getAnalysisSuffixes(self):
        return re.search(r'>\s*(.*)',self.Analysis).group(1).split()
    def getBeforePunc(self):
        return self.BeforePunc
    def getCapitalization(self, foldForANA=False):
        # For ANA format for STAMP, don't use the new '3' (title) case. Fold it to '1'. STAMP only supports 1 or 2.
        if foldForANA and self.Capitalization == '3':
            return '1'
        else:
            return self.Capitalization
    def getHCparseStr(self):

        pfxs = '><'.join(self.getAnalysisPrefixes())
        if pfxs:
            # Remove circumfix extra stuff.
            pfxs = re.sub(Utils.CIRCUMFIX_TAG_A, '', pfxs)

            # Turn underscores to dots
            pfxs = re.sub('_', '.', pfxs)
            pfxs = '<' + pfxs + '>' 

        sfxs = '><'.join(self.getAnalysisSuffixes())
        if sfxs:
            sfxs = '<' + sfxs + '>' 

            ## Remove the circumfix suffix entirely
            if re.search(Utils.CIRCUMFIX_TAG_B, sfxs):

                # find the end of the gloss
                endGloss = sfxs.index(Utils.CIRCUMFIX_TAG_B)
                
                # find the beg of the gloss
                begGloss = sfxs.rfind('<', 0, endGloss)+1
                
                # pull out the gloss string
                gloss = sfxs[begGloss:endGloss]

                # replace gloss string plus the tag (in angle-brackets) with nothing
                sfxs = re.sub('<'+gloss+Utils.CIRCUMFIX_TAG_B+'>', '', sfxs)

            sfxs = re.sub('_', '.', sfxs)

        # roots need to have underscores converted to spaces
        retStr = re.sub('_', ' ', self.getAnalysisRoot()) 

        pos = self.getAnalysisRootPOS()

        # if we have a variant, append the 'POS' to the lemma
        if pos == VARIANT_STR:

            retStr += pos
        
        # add the POS
        retStr += '<' + pos + '>'

        retStr = pfxs + retStr + sfxs
        return retStr

    def getOriginalLexicalUnitString(self):
        return '^'+self._originalLexicalUnitString+'$'
    def getPreDotRoot(self): # in other words the headword
        
        g = re.search(r'< .+ (.+)\.\d+ >',self.Analysis, flags=re.RegexFlag.A) # re.RegexFlag.A=ASCII-only match
        
        if g:
            ret = self.removeUnderscores(g.group(1))
            return ret
        
        return None
    
    def getFirstCompForHCoutput(self):
        return self._firstComponentForHC
    def getSenseNum(self):
        return re.search(r'< .+ .+\.(\d+) >',self.Analysis, flags=re.RegexFlag.A).group(1) # re.RegexFlag.A=ASCII-only match
    def removeUnderscores(self, myStr):
        return re.sub(r'_', ' ', myStr)
    def removePeriods(self, myStr):
        return re.sub(r'\.', '', myStr)
    def setCapitalization(self, myCapitalization):
        self.Capitalization = myCapitalization
    def setAnalysis(self, myAnalysis):
        
        self.Analysis = myAnalysis
        
        # Call setAnalysisByPart to ensure the root is converted to lowercase
        self.setAnalysisByPart(self.getAnalysisPrefixes(), self.getAnalysisRootPOS(), self.getAnalysisRoot(), self.getAnalysisSuffixes())
        
    def setAnalysisByPart(self, prefixes, pos, root, suffixes): # prefixes and suffixes are string lists
        
        self.Capitalization = self.calcCase(root)
        
        # change spaces to underscores in the root:
        myRoot = self.addUnderscores(root)
        
        # change spaces to underscores in the POS:
        myPos = self.addUnderscores(pos)
        
        # remove periods in the POS
        myPos = self.removePeriods(myPos)
        
        # if it's an unknown word, don't change the case, otherwise we always store lower case
        if pos != 'UNK': 
            
            myRoot = myRoot.lower()
            
        self.Analysis = ' '.join(prefixes) + ' < '+myPos+' '+myRoot+' > '+' '.join(suffixes)
        
    def setAfterPunc(self, myAfterPunc):
        self.AfterPunc = myAfterPunc
    def setBeforePunc(self, myBeforePunc):
        self.BeforePunc = myBeforePunc
    def setOriginalLexicalUnitString(self, LUstr):
        self._originalLexicalUnitString = LUstr
    def setFirstCompForHCoutput(self, sameLineBool):
        self._firstComponentForHC = sameLineBool
    def write(self, fOutput):
        
        fOutput.write('\\a ' + self.getAnalysis() + '\n')
        
        if self.getBeforePunc():
            
            fOutput.write('\\f ' + self.escapePunc(Utils.unescapeReservedApertChars(self.getBeforePunc())) + '\n')
            
        if self.getAfterPunc():
            
            fOutput.write('\\n ' + self.escapePunc(Utils.unescapeReservedApertChars(self.getAfterPunc())) + '\n')
            
        if self.getCapitalization():
            
            fOutput.write('\\c ' + self.getCapitalization(foldForANA=True) + '\n')
            
        fOutput.write('\n')
        
class ConversionData():
    
    def __init__(self, errorList, configMap, report, complexFormTypeMap):
        
        self.errorList = errorList
        self.configMap = configMap
        self.report = report
        self.complexMap = {}
        self.irrInflVarMap = {}
        self.rootComponentANAlistMap = {}
        self.rootVariantANAandFeatlistMap = {}
        self.complexFormTypeMap = complexFormTypeMap
        self.haveError = False

        targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)

        if not targetProj:
            return
            
        self.targetProj = targetProj
        
        # Get lexicon files folder setting, we use this for the place to put the cache file.
        lexFolder = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report)
        
        if not lexFolder:
            
            errorList.append((_translate("ConvertTextToSTAMPformat", 'Configuration file problem with {fileType}.').format(fileType=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
            self.haveError = True
            return 
                
        self.lexFolder = lexFolder

        # Check that we have a valid folder
        if os.path.isdir(lexFolder) == False:
            
            errorList.append((_translate("ConvertTextToSTAMPformat", 'Lexicon files folder: {fileType} does not exist.').format(fileType=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
            self.haveError = True
            return errorList
    
        # Get cache data setting
        cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
        
        if not cacheData:
            
            errorList.append((_translate("ConvertTextToSTAMPformat", 'Configuration file problem with {fileType}.').format(fileType=ReadConfig.CACHE_DATA), 2))
            self.haveError = True
            return errorList
    
        # If the validator cache file exists
        if cacheData == 'y' and self.cacheExists():
            
            # check if it's out of date
            if self.isCacheOutOfDate() == False:
                
                if self.loadFromCacheNew() == False: # False == error
                    pass
                else:
                    return
                
        TargetDB = FLExProject()
    
        try:
            TargetDB.OpenProject(targetProj, True)
        except: #FDA_DatabaseError, e:
            report.Error(_translate("ConvertTextToSTAMPformat", 'Failed to open the target database.'))
            raise
    
        self.project = TargetDB
        
        # Read the db and initialize the complex map and inflect variant map
        self.readDatabaseValues()
        
        # Convert these maps to Ana objects
        self.convertValuesToAnas()
        
        if cacheData == 'y':
            
            self.saveToCache()
            
        TargetDB.CloseProject()
            
    def cacheExists(self):
        
        return os.path.exists(self.getCacheFilePath())

    def convertValuesToAnas(self):
        
        # Loop through all our entries that have complex forms
        for root in self.complexMap.keys():
            
            componentANAlist = []
            
            # Get the component entries as ANA Info objects
            inflectionOnFirst = self.gatherComponents(root, self.complexFormTypeMap, self.complexMap, componentANAlist)
            
            # Add the root and component list ANAs to the map. And also the inflection on first component flag
            self.rootComponentANAlistMap[root] = componentANAlist, inflectionOnFirst
    
        # Loop through all the variants for entries
        for root, varList in self.irrInflVarMap.items():
            
            variantANAandFeatlist = []
            
            self.gatherVariants(varList, variantANAandFeatlist)
            
            self.rootVariantANAandFeatlistMap[root] = variantANAandFeatlist
    
    # Output the components of a complex entry
    # Assumptions: no sub-senses, clitics will be attached on the component that takes the inflection
    # This is a recursive function
    def gatherComponents(self, root, complexFormTypeMap, complexMap, compList):
        
        # Get the entry that has components
        # TODO: Handle roots that have more than one complex entry associated with it
        entry = complexMap[root]
        
        # loop through all entryRefs (we'll use just the complex form one)
        for entryRef in entry.EntryRefsOS:
            
            if entryRef.RefType == 1: # 1=complex form, 0=variant
                
                for complexType in entryRef.ComplexEntryTypesRS:
                    
                    formType = Utils.as_string(complexType.Name)
                    
                    if formType in complexFormTypeMap: # this is one the user designated (via config. file) as a complex form to break down
                        
                        # See where the inflection is to go
                        if complexFormTypeMap[formType] == 0:
                            
                            inflectionOnFirst = True
                            inflectionOnLast = False
                        else:
                            inflectionOnFirst = False
                            inflectionOnLast = True
                            
                        firstRoot = True
                        enclGloss = proGloss = ''
                        
                        # Write out all the components
                        for lexIndex, compEntry in enumerate(entryRef.ComponentLexemesRS):
                            
                            # If the component is a proclitic, save the gloss string (with a space on the end)
                            if Utils.isProclitic(compEntry):
                                
                                proGloss = self.getGloss(compEntry)+' '
                            
                            # If the component is an enclitic, save it with a preceding space
                            elif Utils.isEnclitic(compEntry):
                                
                                enclGloss = ' ' + self.getGloss(compEntry)
                                
                            # Otherwise we have a root
                            else:
                                # Get the needed data from the entry object
                                (headWord, gramCatAbbrev, senseNum) = self.getAnaDataFromEntry(compEntry)
                                
                                # See if this head word has components itself and call this function recursively
                                if headWord in complexMap:
                                    
                                    self.gatherComponents(headWord, complexFormTypeMap, complexMap, compList)
                                else:
                                    # See if we are at the beginning or the end, depending on where the
                                    # inflection goes, write out all the stuff with inflection
                                    if (inflectionOnFirst and firstRoot) or (inflectionOnLast and lexIndex==entryRef.ComponentLexemesRS.Count-1):
                                        
                                        # Build the an ANA Info object
                                        currANAInfo = ANAInfo([proGloss], 
                                                              [enclGloss], 
                                                              gramCatAbbrev, headWord + '.' + senseNum)
                                            
                                    # Write out the bare bones root in the analysis part
                                    else:
                                        # no prefixes or suffixes, give []
                                        currANAInfo = ANAInfo([], [], gramCatAbbrev, headWord + '.' + senseNum)
                                
                                    compList.append(currANAInfo)
                                    
                                firstRoot = False
                    continue
            continue
        
        return inflectionOnFirst

    def gatherVariants(self, varList, variantANAandFeatlist):
        
        for varTuple in varList: # each tuple as form (entry, featAbbrList)
            
            entry = varTuple[0]
            featAbbrList = varTuple[1]
    
            # Set the headword value and the homograph #
            headWord = ITsString(entry.HeadWord).Text
                
            # If there is not a homograph # at the end, make it 1
            headWord = Utils.add_one(headWord)
                
            # Create an ANA Info object with the POS being _variant_
            # (We are intentionally not adding the sense number.)
            # no prefixes or suffixes
            myAnaInfo = ANAInfo()
            myAnaInfo.setAnalysisByPart([], VARIANT_STR, headWord, [])
            
            variantANAandFeatlist.append((myAnaInfo, featAbbrList))
        
    def getAbbrList(self, indx, lines):
        
        abbrList = []
        
        # Get number of abbreviations to read in
        numAbbr = int(lines[indx].rstrip())
        indx += 1
        
        # read in the name value pairs in consecutive lines
        for _ in range(0, numAbbr):
            name = lines[indx].rstrip()
            val = lines[indx+1].rstrip()
            indx += 2
            
            # Add them to the list
            abbrList.append((name, val))
        
        return abbrList
            
    # Get the needed data from the entry object and return as a tuple
    # This function will handle when an entry points to a component that is a sense not a lexeme
    def getAnaDataFromEntry(self, compEntry):
        
        # default to 1st sense. At the moment this isn't a big deal because we aren't doing anything with target senses. But eventually this needs to be gleaned 
        # somehow from the complex form.
        senseNum = '1'
        
        # The thing the component lexeme points to could be a sense rather than an entry
        if compEntry.ClassName == 'LexSense':
            
            compSense = ILexSense(compEntry)
            
            # Get the headword text of the owning entry
            owningEntry = ILexEntry(compSense.Entry) # Assumption here that this isn't a subsense
            
            a = ITsString(owningEntry.HeadWord).Text
            a = Utils.add_one(a)
            
            moAnalysis = IMoStemMsa(compSense.MorphoSyntaxAnalysisRA)
            posObj = moAnalysis.PartOfSpeechRA
            
            if posObj:            
                
                abbrev = Utils.as_string(posObj.Abbreviation)

            # Find which sense number this is
            for i, mySense in enumerate(owningEntry.SensesOS):

                if mySense == compSense:
                    break

            senseNum = str(i+1)

        else: # entry
            
            compEntry = ILexEntry(Utils.GetEntryWithSense(compEntry))
            
            a = ITsString(compEntry.HeadWord).Text
            a = Utils.add_one(a)
              
            # Get POS
            abbrev = 'NULL'
            
            if compEntry.SensesOS.Count > 0:
                
                mySense = compEntry.SensesOS.ToArray()[0]
                moAnalysis = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                posObj = moAnalysis.PartOfSpeechRA
                
                if posObj:
                                
                    abbrev = Utils.as_string(posObj.Abbreviation)
        
        return (a, abbrev, senseNum)
    
    def getCacheFilePath(self):
        
        # build the path in the build dir using project name + testbed_cache.txt
        return os.path.join(self.lexFolder, self.targetProj+'_'+Utils.CONVERSION_TO_STAMP_CACHE_FILE)
    
    def getData(self):
        
        return (self.rootComponentANAlistMap, self.rootVariantANAandFeatlistMap)
    
    def getFeatAbbrList(self, SpecsOC, featAbbrevList):
        
        for spec in SpecsOC:
            if spec.ClassID == 53: # FsComplexValue
                
                spec = IFsComplexValue(spec)
                featStruc = IFsFeatStruc(spec.ValueOA)
                self.getFeatAbbrList(featStruc.FeatureSpecsOC, featAbbrevList)
                
            else: # FsClosedValue - I don't think the other types are in use
                
                spec = IFsClosedValue(spec)
                featGrpName = Utils.as_string(spec.FeatureRA.Name)
                abbValue = Utils.as_string(spec.ValueRA.Abbreviation)
                abbValue = re.sub('\.', '_', abbValue)
                featAbbrevList.append((featGrpName, abbValue))
        return
    
    def getGloss(self, entry):
            
        # follow the chain of variants to get an entry with a sense
        entry = Utils.GetEntryWithSense(entry)
        
        return Utils.as_string(entry.SensesOS.ToArray()[0].Gloss)
    
    def isCacheOutOfDate(self):
        
        # Build a DateTime object with the FLEx DB last modified date
        #flexDate = self.project.GetDateLastModified()
        #dbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
        
        # Get the date of target affixes file
        tgtAffixFile = ReadConfig.getConfigVal(self.configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, self.report, giveError=False) # don't give error yet
        
        try:
            affTime = os.path.getmtime(tgtAffixFile)
        except OSError:
            return True
        affixFileDateTime = datetime.fromtimestamp(affTime)
        
        # Get the date of the cache file
        try:
            mtime = os.path.getmtime(self.getCacheFilePath())
        except OSError:
            mtime = 0
        cacheFileDateTime = datetime.fromtimestamp(mtime)
        
        if affixFileDateTime > cacheFileDateTime: # The affix file is newer
            return True 
        else: # cache file is newer
            return False

    def loadFromCacheNew(self):
        
        f = open(self.getCacheFilePath(), encoding='utf-8')
        
        complexLines = []
        inflLines = []
        
        # start with complex forms
        doingComplexForms = True
        
        # Read each section of the cache file
        for i,line in enumerate(f):
            
            # Skip the first line
            if i == 0:
                continue
            
            # Next read the irregular forms. Skip this line
            if line.rstrip() == IRR_INFL_VARIANTS:
                doingComplexForms = False
                continue

            if doingComplexForms == True:
                complexLines.append(line.rstrip())      
            else: # variant forms
                inflLines.append(line.rstrip())
         
        # Process complex forms
        i = 0
        t = len(complexLines)
        while i < t:
            
            # Get the basic info.
            headWord = complexLines[i].rstrip()
            inflectionOnFirst = complexLines[i+1].rstrip() == 'True'
            numComponents = int(complexLines[i+2].rstrip())
            
            i += 3
            componentAnaList = []
            
            # Get the components for the current complex form
            for _ in range(0, numComponents):
                
                newANA = ANAInfo()
                newANA.setAnalysis(complexLines[i].rstrip())
                componentAnaList.append(newANA)
                
                i += 1

            self.rootComponentANAlistMap[headWord] = componentAnaList, inflectionOnFirst
        
        # Process irregular forms
        i = 0
        t = len(inflLines)
        
        while i < t:
            
            headWord = inflLines[i].rstrip()
            numVariants = int(inflLines[i+1].rstrip())
            i += 2
            variantANAandFeatlist = []
            
            for _ in range(0, numVariants):

                newANA = ANAInfo()
                newANA.setAnalysis(inflLines[i].rstrip())

                i += 1
                abbrList = self.getAbbrList(i, inflLines)
                
                # move the i index past all the abbreviations. Length x2 since each abbr. has two lines (name, val)
                # 1 more for the num of abbreviations at the start of the abbrev. block
                i += len(abbrList)*2 + 1 

                variantANAandFeatlist.append((newANA, abbrList))
            
            self.rootVariantANAandFeatlistMap[headWord] = variantANAandFeatlist
        
        f.close()
        return True
           
    def readDatabaseValues(self):

        if self.report is not None:
            self.report.ProgressStart(self.project.LexiconNumberOfEntries())
      
        # Loop through all the entries in the lexicon 
        for i,e in enumerate(self.project.LexiconAllEntries()):
        
            if self.report is not None:
                self.report.ProgressUpdate(i)
            
            # Set the headword value and the homograph #
            headWord = ITsString(e.HeadWord).Text
            
            # If there is not a homograph # at the end, make it 1
            # Also make it lower case. All ANA "roots" are lower case so we need to match them that way
            headWord = Utils.add_one(headWord).lower()
                                    
            # Store all the complex entries by creating a map from headword to the complex entry
            if e.EntryRefsOS.Count > 0: # only process complex forms
                
                for entryRef in e.EntryRefsOS:
                    
                    if entryRef.ComponentLexemesRS and \
                       entryRef.ComponentLexemesRS.Count > 1 and \
                       entryRef.RefType == 1: # 1=complex form, 0=variant # At least 2 components
                        
                        if entryRef.ComplexEntryTypesRS:
                            
                            # there could be multiple types assigned to a complex form (e.g. Phrasal Verb, Derivative)
                            # just see if one of them is Phrasal Verb
                            for complexType in entryRef.ComplexEntryTypesRS:
                                
                                if Utils.as_string(complexType.Name) in self.complexFormTypeMap:
            
                                    self.complexMap[headWord] = e
                                    break
                            break # if we found a complex form, there won't be any more
            
            # Store all the entries that have inflectional variants with features assigned
            for variantForm in e.VariantFormEntries:
                
                for entryRef in variantForm.EntryRefsOS:
                    
                    if entryRef.RefType == 0: # we have a variant
                        
                        # Collect any inflection features that are assigned to the special
                        # variant types called Irregularly Inflected Form
                        for varType in entryRef.VariantEntryTypesRS:
                            
                            if varType.ClassName == "LexEntryInflType":
                                
                                varType = ILexEntryInflType(varType)

                                if varType.InflFeatsOA:
                                    
                                    myFeatAbbrList = []
                                    
                                    # The features might be complex, make a recursive function call to find all features
                                    Utils.get_feat_abbr_list(varType.InflFeatsOA.FeatureSpecsOC, myFeatAbbrList)
                                    
                                    if len(myFeatAbbrList) > 0:
                                        
                                        myTuple = (variantForm, myFeatAbbrList)
                                        
                                        if headWord not in self.irrInflVarMap:
                                            
                                            self.irrInflVarMap[headWord] = [myTuple]
                                        else:
                                            self.irrInflVarMap[headWord].append(myTuple)

    def saveToCache(self):
        
        f = open(self.getCacheFilePath(), 'w', encoding='utf-8')
        
        # TODO: HANDLE writing all forms for each headword
        f.write(COMPLEX_FORMS+'\n')
        
        for headWord, (componentANAlist, inflectionOnFirst) in self.rootComponentANAlistMap.items():
            
            # output head word
            f.write(headWord+'\n')
            
            # write out the inflection on first component flag
            f.write(str(inflectionOnFirst)+'\n')

            # write out the # of components
            f.write(str(len(componentANAlist))+'\n')
            
            for compANA in componentANAlist:
                
                # output the ana main line
                f.write(compANA.getAnalysis().strip()+'\n')
            
        f.write(IRR_INFL_VARIANTS+'\n')
        
        for headWord, variantANAandFeatlist in sorted(self.rootVariantANAandFeatlistMap.items()):
            
            # output head word
            f.write(headWord+'\n')

            # output the number of # of variants for this head word
            f.write(str(len(variantANAandFeatlist))+'\n')
                        
            for (varAna, abbrList) in variantANAandFeatlist:
                
                # output the ana main line
                f.write(varAna.getAnalysis().strip()+'\n')

                self.writeAbbrList(f, abbrList)
            
        f.close()

    def writeAbbrList(self, f, abbList):
        
        # Write out the number of abbreviations we have
        f.write(str(len(abbList))+'\n')
        
        for (featGrpName, abbValue) in abbList:
            # Write out the feature name and the value
            f.write(featGrpName+'\n')
            f.write(abbValue+'\n')
            
# Check if the tags (prefixes & suffixes) match the features of one of
# the main entry's variants. If so replace the main entry headword with
# the variant and remove the tags that matched.
# E.g. if the main entry 'be1.1' has an irr. infl. form variant 'am1.1' with a 
# variant type called 1Sg which has features [per: 1ST, num: SG] and the
# Ana entry is '< cop be1.1 >  1ST SG', we want a new Ana entry that looks like 
# this: '< _variant_ am1 >'
def changeToVariant(myAnaInfo, rootVariantANAandFeatlistMap, doHermitCrabSynthesis):

    oldCap = myAnaInfo.getCapitalization()
    pfxs = myAnaInfo.getAnalysisPrefixes()
    numPfxs = len(pfxs)
    sfxs = myAnaInfo.getAnalysisSuffixes()
    tags = pfxs+sfxs
    
    # loop through the irr. infl. form variant list for this main entry
    variantANAandFeatlist = rootVariantANAandFeatlistMap[myAnaInfo.getPreDotRoot()]
    
    for varAna, featAbbrList in variantANAandFeatlist: # each tuple as form (entry, featAbbrList)

        # See if there is a variant that has inflection features that match the tags in this entry
        variantMatches = False
        featList = [y[1] for y in sorted(featAbbrList, key=lambda x: x[0])]
        numFeatures = len(featList)
        
        # There has to be at least as many tags as features
        if len(tags) >= numFeatures:
            
            # Loop through slices of the tag list
            for i in range(0,len(tags)-numFeatures+1):
                
                # See if we match regardless of order
                if sorted(tags[i:i+numFeatures]) == sorted(featList):
                    
                    variantMatches = True
                    break
            if variantMatches:
                break
    
    if variantMatches:
        
        # Remove the matched tags
        del pfxs[i:i+numFeatures]
        beg = i-numPfxs
        
        if beg < 0:
            beg = 0
            
        end = i-numPfxs+numFeatures
        
        if end < 0:
            end = 0
            
        del sfxs[beg:end]
        
        # Reset the Ana info
        if doHermitCrabSynthesis:

            # For HermitCrab we put out the sense # (TODO: we need to probably do this for STAMP as well)
            # A variant can be a variant of an entry with multiple senses. The senses could have different categories
            # How those categories take affixes could be different, e.g. different affix template. (STAMP doesn't use templates, but HC does)
            myAnaInfo.setAnalysisByPart(pfxs, VARIANT_STR, varAna.getCapitalizedAnalysisRoot()+'.'+myAnaInfo.getSenseNum(), sfxs)
        else:
            # (We are intentionally not adding the sense number.)
            myAnaInfo.setAnalysisByPart(pfxs, VARIANT_STR, varAna.getCapitalizedAnalysisRoot(), sfxs)
        
        # Change the case as necessary
        myAnaInfo.setCapitalization(oldCap)

def writeNonComplex(myAnaInfo, rootVariantANAandFeatlistMap, fOutput, doHermitCrabSynthesis, HCparseStrMap=None):
    
    root = myAnaInfo.getPreDotRoot()
    
    if root in rootVariantANAandFeatlistMap: 
        
        # replace main entry with variant entry and remove appropriate tags (pfxs & sfxs)
        changeToVariant(myAnaInfo, rootVariantANAandFeatlistMap, doHermitCrabSynthesis)
                
    if doHermitCrabSynthesis:

        originalLexicalUnitStr = myAnaInfo.getOriginalLexicalUnitString()

        # see if the orignal LU string for is already in our map
        if originalLexicalUnitStr not in HCparseStrMap:

            # Get the string that we would write to the parses file
            HCparseStr = myAnaInfo.getHCparseStr()
            cap = myAnaInfo.getCapitalization()

            fOutput.write(originalLexicalUnitStr + ',' + HCparseStr + ';' + cap + '\n')

            HCparseStrMap[originalLexicalUnitStr] = 1
    else:
        myAnaInfo.write(fOutput)
        
def writeComponents(componentList, fOutput, theAnaInfo, rootVariantANAandFeatlistMap, doHermitCrabSynthesis, HCparseStrMap=None):
        
    if doHermitCrabSynthesis:

        originalLexicalUnitStr = theAnaInfo.getOriginalLexicalUnitString()

        # see if the orignal LU string for this complex form is already in our map
        if originalLexicalUnitStr not in HCparseStrMap:

            for i, listAnaInfo in enumerate(componentList):
                
                # Get the string that we would write to the parses file
                HCparseStr = listAnaInfo.getHCparseStr()
                cap = listAnaInfo.getCapitalization()

                # First component, write the original LU string and the first component
                if i == 0:

                    fOutput.write(originalLexicalUnitStr + ',' + HCparseStr + ';' + cap)
    
                # Write all other components
                else:
                    fOutput.write('|' + HCparseStr + ';' + cap)

            fOutput.write('\n')
            HCparseStrMap[originalLexicalUnitStr] = 1

    else: # Standard ANA file

        for i, listAnaInfo in enumerate(componentList):
            
            # Give this object pre-punctuation if it's the first component
            if i == 0:
                
                listAnaInfo.setBeforePunc(theAnaInfo.getBeforePunc())
                
                # Change the case as necessary
                theAnaInfo.setCapitalization(theAnaInfo.calcCase(theAnaInfo.getAnalysisRoot()))
                    
            # Give this object post-punctuation if it's the last component
            if i == len(componentList)-1:
                
                listAnaInfo.setAfterPunc(theAnaInfo.getAfterPunc())

            # This also converts variant forms if needed
            writeNonComplex(listAnaInfo, rootVariantANAandFeatlistMap, fOutput, doHermitCrabSynthesis, HCparseStrMap)    

def processComplexForm(textAnaInfo, componANAlist, inflectionOnFirst):

    firstRoot = True
    newCompANAlist = []

    for index, myAnaInfo in enumerate(componANAlist):

        # See if we are at the beginning or the end, depending on where the
        # inflection goes, write out all the stuff with inflection
        if (inflectionOnFirst and firstRoot) or (not inflectionOnFirst and index == len(componANAlist)-1):
            
            # Create a new Ana info object
            newAna = ANAInfo()
            
            # add affixation to the ANA object. Affixes on the myAnaInfo are proclitics and enclitics if they exist. Put text prefixes after proclitics and suffixes before enclitics.
            newAna.setAnalysisByPart(myAnaInfo.getAnalysisPrefixes()+textAnaInfo.getAnalysisPrefixes(),
                                        myAnaInfo.getAnalysisRootPOS(), 
                                        myAnaInfo.getCapitalizedAnalysisRoot(),
                                        textAnaInfo.getAnalysisSuffixes()+myAnaInfo.getAnalysisSuffixes())

            newCompANAlist.append(newAna)
        else:
            newCompANAlist.append(myAnaInfo)
            
        firstRoot = False
        
    return newCompANAlist
        
def haveWordPackage(token):
                
    if re.search(r'\d+\.\d+<', token) or re.search(r'@', token):

        return True
    
    return False

def getContextWords(wrdCnt, wordToks):

    # Determine the context words around the problem word
    if wrdCnt-2 >= 0:
        prev2words = wordToks[wrdCnt-2] + ' ' + wordToks[wrdCnt-1]
    else:
        if wrdCnt-1 >= 0:
            prev2words = wordToks[wrdCnt-1]
        else:
            prev2words = ''

    if wrdCnt+2 < len(wordToks):
        foll2words = wordToks[wrdCnt+1] + ' ' + wordToks[wrdCnt+2]
    else:
        if wrdCnt+1 < len(wordToks):
            foll2words = wordToks[wrdCnt+1]
        else:
            foll2words = ''

    return prev2words, foll2words

# Convert the output from the Apertium transfer to an ANA file
def convertIt(pfxName, outName, report, sentPunct):

    errorList = []
    wordAnaInfoList = []
    anaObj = None
    
    affixMap = {}
    
    # Read in the target affix list. 
    fAfx = open(pfxName, 'r', encoding='utf-8')
    
    for line in fAfx:
        
        (affix, morphType) = re.split('\|', line.rstrip())
        affixMap[affix] = morphType
        
    fAfx.close()

   # Open the transfer results file. Sample text: ^xxx1.1<perspro><acc/dat>$ ^xx1.1<vpst><pfv><3sg_pst>$: ^xxx1.1<perspro>
    try:
        fResults = open(outName, encoding='utf-8')

    except:
        errorList.append((_translate("ConvertTextToSTAMPformat", 'The file: {fileName} was not found. Did you run the Run Apertium module?').format(fileName=outName), 2))
        return errorList, wordAnaInfoList
    
    resultsFileStr = fResults.read()
    fResults.close()

    # Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x
    resultsFileStr = re.sub(r'\^([^^]+?)<sent>\$', r'\1', resultsFileStr) # use [^^] (meaning not caret because otherwise using . might match a ^)

    # Split the string into lexical units and 'punctuation' (non-lexical units)
    tokens = re.split(r'\^(.+?)\$', resultsFileStr)

    # Pair up the tokens. The first is the punctuation, the second is the LU
    tokenPairs = list(zip(tokens[::2], tokens[1::2]))

    # Initialize the progress counter
    if report is not None:
        
        report.ProgressStart(len(tokenPairs))
    
    # Loop through pairs of tokens. 
    for cnt, (punc, lu) in enumerate(tokenPairs):

        # Update the progress counter
        if report is not None:
            
            report.ProgressUpdate(cnt)
            
        # Special handling of first word (no post punctuation gets added)
        if cnt == 0:    
            # Process the lexical unit string and get an ANA object back
            anaObj, morphs = processLU(lu, affixMap)

            if anaObj == None:

                return processLUparseError(cnt, tokens[1::2], morphs), wordAnaInfoList
        
            anaObj.setBeforePunc(punc)

        else:
            # Determine what part of the punctuation goes at the end of the last word 
            # and which goes to the beginning of the current word.
            pre, post = calculatePrePostPunctuation(punc)
            anaObj.setAfterPunc(post)

            # Process the lexical unit string and get an ANA object back
            anaObj, morphs = processLU(lu, affixMap)

            if anaObj == None:

                return processLUparseError(cnt, tokens[1::2], morphs), wordAnaInfoList
        
            anaObj.setBeforePunc(pre)

        wordAnaInfoList.append(anaObj)

    # Process a possible last punctuation string
    if anaObj and len(tokens) > 0 and tokens[-1] != '':

        anaObj.setAfterPunc(re.sub(r'^ ', '', tokens[-1])) # remove preceding space

    return errorList, wordAnaInfoList

def calculatePrePostPunctuation(puncStr):

    pre = post = ''

    if puncStr:

        puncList = re.split(' ', puncStr)
        post = puncList[0]
        pre = " ".join(puncList[1:])

        # If post punctuation is non-empty add a trailing space. Otherwise we will get two words jammed together by STAMP
        # It doesn't put a space between words when \n is used.
        # DELETE We also don't want the space when there was a newline at the beg. we want it to butt against the word.
        # Also we don't want a space after a newline, that would indent the next line by a space
        # if post and post[0] != '\n' and post[-1] != '\n':
        if post and post[-1] != '\n':
            post += ' '
    
    return pre, post

def processLUparseError(cnt, tokList, morphs):

    prev2words, foll2words = getContextWords(cnt, tokList) # just pass the lexical units
    errorList = [(_translate("ConvertTextToSTAMPformat", "Lemma or grammatical category missing for a target word near word {wordNum}. Found only: {morphs}. The preceding two words were: {prevWords}. The following two words were: {follWords}. Processing stopped.").format(wordNum=str(cnt+1), morphs=",".join(morphs), prevWords=prev2words, follWords=foll2words),2)]
    return errorList

def processLU(lexUnitStr, affixMap):

    prefixList = []
    suffixList = []
    infixList = []
    circumfixList = []
    wordAnaInfo = None

    # Get the root, root category and any affixes
    morphs = re.split('<|>', lexUnitStr)
    morphs = [tk for tk in morphs if tk] # remove empty strings

    # start at position 2 since this is where the affixes start
    for i in range(2,len(morphs)):
        
        # If we don't have the item in the affix map, then it must be a feature.
        # Treat it like a suffix, because change_to_variant will use the feature(s) to find a variant
        if morphs[i] not in affixMap:
            
            suffixList.append(morphs[i])
            
        ## We use English morphnames as a standard in the target affix glosses file

        # prefix
        elif affixMap[morphs[i]] in ['prefix', 'proclitic', 'prefixing interfix']:
            
            prefixList.append(morphs[i])
            
        # infix
        elif affixMap[morphs[i]] in ['infix', 'infixing interfix']:
            
            infixList.append(morphs[i])
            
        # circumfix
        elif affixMap[morphs[i]] == 'circumfix':
            
            # Circumfixes are made of two parts, a prefix part and a suffix part
            # when we encounter a new circumfix, give it a unique new gloss and
            # add it to the prefix list. When we see one that we've seen before,
            # it must be the suffix part. Give it a unique new gloss and add it to
            # the suffix list.
            if morphs[i] not in circumfixList:
                
                prefixList.append(morphs[i]+Utils.CIRCUMFIX_TAG_A)
                circumfixList.append(morphs[i])
            else:
                suffixList.append(morphs[i]+Utils.CIRCUMFIX_TAG_B)
                
        # suffix. Treat everything else as a suffix (suffix, enclitic, suffixing interfix).
        # The other types are not supported, but will end up here.
        else:
            suffixList.append(morphs[i])

    if len(morphs) <2:
        
        return wordAnaInfo, morphs

    # Create an ANA Info object
    # We have the root (morphs[0]) and the POS of the root (morphs[1])
    wordAnaInfo = ANAInfo(prefixList, suffixList, morphs[1], morphs[0], infixList)
    wordAnaInfo.setOriginalLexicalUnitString(lexUnitStr)

    return wordAnaInfo, morphs

def convert_to_STAMP(DB, configMap, targetANAFile, affixFile, transferResultsFile, doHermitCrabSynthesis=False, HCmasterFile=None, report=None):
    
    errorList = []
    
    complexForms1st = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_FORMS_INFLECTION_1ST, report)
    complexForms2nd = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_FORMS_INFLECTION_2ND, report)
    sentPunct = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)

    if not (targetANAFile and affixFile and transferResultsFile and sentPunct):
        
        errorList.append((_translate("ConvertTextToSTAMPformat", "Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct"), 2))
        return errorList

    # Check the validity of the complex forms lists
    if complexForms1st and not ReadConfig.configValIsList(configMap, ReadConfig.TARGET_FORMS_INFLECTION_1ST, report):
        
        errorList.append((_translate("ConvertTextToSTAMPformat", "Configuration file problem with: {property}.").format(property=ReadConfig.TARGET_FORMS_INFLECTION_1ST), 2))
        return errorList
    
    if complexForms2nd and not ReadConfig.configValIsList(configMap, ReadConfig.TARGET_FORMS_INFLECTION_2ND, report):
        
        errorList.append((_translate("ConvertTextToSTAMPformat", "Configuration file problem with: {property}.").format(property=ReadConfig.TARGET_FORMS_INFLECTION_2ND), 2))
        return errorList

    # Build the complex forms map
    complexFormTypeMap = {}
    
    # Create a map that tracks which complex form types are for first or for last 
    for cmplxType in complexForms1st:
        
        complexFormTypeMap[cmplxType] = 0  # 0 - inflection on first root
        
    for cmplxType in complexForms2nd:
        
        complexFormTypeMap[cmplxType] = 1  # 1 - inflection on last root
    
    # Convert the Apertium file to an ANA list
    errList, anaInfoList = convertIt(affixFile, transferResultsFile, report, sentPunct)
    
    if len(errList) > 0:
        
        errorList.extend(errList)
        return errorList

    # Get the complex forms and inflectional variants
    # This may be slow if the data is not in the cache
    convData = ConversionData(errorList, configMap, report, complexFormTypeMap)
    
    if convData.haveError:
        
        return errorList
    
    # retrieve the data that got initialized in the Conversion data class
    (rootComponANAlistMap, rootVariantANAandFeatlistMap) = convData.getData()
        
    # Now we are going to process the ANA list, breaking down each complex form
    # into separate ANA records if needed. This is needed for instance if a source word
    # maps to multiple words in the target language. The multi-word ANA record needs to
    # be broken down into multiple ANA records
         
    try:         
        # Open the output file
        if not doHermitCrabSynthesis:

            fOutput = open(targetANAFile, 'w', encoding='utf-8')
            fOutput.write('\n') # always need a blank line at the top

        else:
            fOutput = open(HCmasterFile, 'w', encoding='utf-8')
    except:

        errorList.append((_translate("ConvertTextToSTAMPformat", "Error writing the output file."), 2))
        return errorList
    
    count = 0
    HCparseStrMap = {}

    # Loop through all the ANA pieces
    for anaInfo in anaInfoList:
        
        # If an ANA root matches a complex form, rewrite the ana file with complex forms 
        # broken down into components
        root = anaInfo.getPreDotRoot()
        
        if root in rootComponANAlistMap:
            
            componANAlist, inflectionOnFirst = rootComponANAlistMap[root]
            newCompANAlist = processComplexForm(anaInfo, componANAlist, inflectionOnFirst)
            writeComponents(newCompANAlist, fOutput, anaInfo, rootVariantANAandFeatlistMap, doHermitCrabSynthesis, HCparseStrMap)
            
        else: # write it out as normal
            
            # This also converts variant forms if needed
            writeNonComplex(anaInfo, rootVariantANAandFeatlistMap, fOutput, doHermitCrabSynthesis, HCparseStrMap)
        
        count += 1
    
    if not doHermitCrabSynthesis:
        errorList.append((_translate("ConvertTextToSTAMPformat", "Converted target words put in the file: {filePath}.").format(filePath=Utils.getPathRelativeToWorkProjectsDir(targetANAFile)), 0))
        errorList.append((_translate("ConvertTextToSTAMPformat", "{count} records exported in ANA format.").format(count=str(count)), 0))
    else:
        errorList.append((_translate("ConvertTextToSTAMPformat", "Converted target words put in the file: {filePath}").format(filePath=Utils.getPathRelativeToWorkProjectsDir(HCmasterFile)), 0))
        errorList.append((_translate("ConvertTextToSTAMPformat", "{count} records exported in HermitCrab format.").format(count=str(count)), 0))

    fOutput.close()
    
    return errorList

def convertToSynthesizerFormat(DB, configMap, report):
    
    targetANAFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet
    
    if not affixFile:
        
        # Try the old config value name
        affixFile = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
        
    # Verify that the affix file exist.
    if not os.path.exists(affixFile):
        
        report.Error(_translate("ConvertTextToSTAMPformat", "The Catalog Target Affixes module must be run before this module. The {fileType}: {filePath} does not exist.").format(fileType=ReadConfig.TARGET_AFFIX_GLOSS_FILE, filePath=affixFile))
        return None
    
    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False)

    doHermitCrabSynthesis = True if hermitCrabSynthesisYesNo == 'y' else False
    HCmasterFile = None
    
    # Get the master file name
    if doHermitCrabSynthesis:

        HCmasterFile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_MASTER_FILE, report)

        if not HCmasterFile:

            report.Error(_translate("ConvertTextToSTAMPformat", "Configuration file problem with: {fileType}.").format(fileType=ReadConfig.HERMIT_CRAB_MASTER_FILE))
            return None 
    
    errorList = convert_to_STAMP(DB, configMap, targetANAFile, affixFile, transferResultsFile, doHermitCrabSynthesis, HCmasterFile, report)

    # output info, warnings, errors and url links
    Utils.processErrorList(errorList, report)
    return 1

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    convertToSynthesizerFormat(DB, configMap, report)



#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

