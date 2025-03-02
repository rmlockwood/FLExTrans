#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.12.1 - 3/2/25 - Ron Lockwood
#    Fixes #914. Set the morphtype to be from the analysis writing system instead of English.
#    This is needed now that we let non-English morphtype names be used in the settings.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.3 - 10/26/24 - Ron Lockwood
#    Fixes #775. Give an error for invalid characters.
#
#   Version 3.11.2 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.1 - 9/12/24 - Ron Lockwood
#    Better error checking when critical settings not set.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.1 - 2/26/24 - Ron Lockwood
#    Fixes #565. Add inflection features/classes to the source side of the bilingual lexicon.
#    To do this, make the building of the element string for features and classes a separate function.
#    Also, add source features and classes to the symbol definition header part of the bilingual lexicon.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9.9 - 11/24/23 - Ron Lockwood
#    Add a new check when building the lexicon to see if there are headwords that only differ
#    in case and have the same part of speech. In such cases give a warning and skip the sense.
#
#   Version 3.9.8 - 8/18/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.7 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.6 - 7/17/23 - Ron Lockwood
#    Fixes #66. Use human-readable hyperlinks in the target equivalent custom field.
#
#   Version 3.9.5 - 7/4/23 - Ron Lockwood
#    Don't give an error if the sense custom field link setting is not there.
#
#   Version 3.9.4 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.9.3 - 6/19/23 - Ron Lockwood
#    Fixes #439. Error check after searching for the id 'replacement' or 'append'
#
#   Version 3.9.2 - 6/19/23 - Ron Lockwood
#    Fixes #387. If a replacement entry has a space, turn that into a </b> in the bilingual lexicon.
#    It's expected the user will use a normal space when needed for a lemma in the replacement file.
#
#   Version 3.9.1 - 6/3/23 - Ron Lockwood
#    Fixes #441. Catch a exception when writing the bilingual lexicon with ElementTree.
#
#   Version 3.8.4 - 5/5/23 - Ron Lockwood
#    Change Fatal error to Warning.
#
#   Version 3.8.3 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.2 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8.1 - 4/7/23 - Ron Lockwood
#    Change module name from Extract... to Build...
#
#   Version 3.8 - 4/7/23 - Ron Lockwood
#    Don't give the full path of the replacement file in the xml comment of the bilingual lexicon file.
#
#   Version 3.7.5 - 2/7/23 - Ron Lockwood
#    Fixes #390. Words that are linked to **none** now get a blank mapping in the bilingual
#    dictionary. This allows them to be deleted by default, or they can be overridden by
#    replacement file entries.
#
#   Version 3.7.4 - 2/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.3 - 1/18/23 - Ron Lockwood
#    Fixed bug where report was None in the doReplacements function and a warning was
#    attempted to be outputted. Have LinkSenseTool call extract_bilingual_lex with a report object.
#
#   Version 3.7.2 - 1/7/23 - Ron Lockwood
#    Fixes #214. Give a warning for replacement file entries that couldn't be
#    found in the bilingual lexicon.
#
#   earlier version history removed on 3/1/25
#
#   Create a bilingual dictionary in Apertium format. The bilingual dictionary is one
#   of two elements needed for the Apertium transfer system for transferring a text.
#   the other is a rule file that transforms the stream of input words.
#
#   An Apertium dictionary basically
#   links two lemmas (as the call them) without any other information, except perhaps
#   some tags for part of speech. For this implementation, I have chosen to name the
#   lemma as follows: headword + sense #. The headword is made up of citation form if
#   available or if not, lexeme form + a homograph #. If the homograph is 0 (no duplicate
#   form), the homograph # 1 is used.
#
#   Each root/stem entry in the source project is processed and a custom sense-level link
#   field is examined to see if it has a URL to the target entry. If no data is in the
#   link field, an identity entry is created in the Apertium dictionary which means the
#   source lemma will be duplicated as the target lemma in the Apertium transfer system.
#   When there is a URL in the link field, the sense number custom field is examined. If
#   the sense number field is empty, sense # 1 is assumed. The headword is retrieved from
#   the target project and combined with the aforementioned sense # to form the target
#   lemma.
#
#   Other details. In addition to the lemma, the POS is output as a tag for each entry as
#   well as any features that are present for the entry.
#

import re
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
import unicodedata
import io

from System import Guid # type: ignore
from System import String # type: ignore

from SIL.LCModel import ( # type: ignore
    IMoStemMsa,
    IFsClosedFeature,
    FsClosedFeatureTags,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString  # type: ignore

from flextoolslib import *

import ReadConfig
import Utils

DONT_CACHE = True

DICTIONARY = 'dictionary'
REPLDICTIONARY = 'repldictionary'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Build Bilingual Lexicon",
        FTM_Version    : "3.12.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Builds an Apertium-style bilingual lexicon.",
        FTM_Help   : "",
        FTM_Description:
"""
This module will build a bilingual
lexicon for two projects. The
database that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these link.

You can make custom changes to the bilingual lexicon by using a replacement file. See the help
document for more details.
""" }

#----------------------------------------------------------------

def getFileTime(path):
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0
    return datetime.fromtimestamp(mtime)

def getDBTime(DB):
    flexDate = DB.GetDateLastModified()
    return datetime(
        flexDate.get_Year(), flexDate.get_Month(), flexDate.get_Day(),
        flexDate.get_Hour(), flexDate.get_Minute(), flexDate.get_Second(),
    )

def bilingFileOutOfDate(sourceDB, targetDB, bilingFile):

    bilingDate = getFileTime(bilingFile)

    sourceNewer = getDBTime(sourceDB) > bilingDate
    targetNewer = getDBTime(targetDB) > bilingDate

    return sourceNewer or targetNewer

def replFileOutOfDate(bilingFile, replFile):

    return getFileTime(replFile) > getFileTime(bilingFile)

def convertOldEntries(tree):
    for node in tree.findall('.//leftdata/..') + tree.findall('.//rightdata/..'):
        i = 0
        while i < len(node):
            if node[i].tag in ['leftdata', 'rightdata']:
                content = (node[i].text or '') + (node[i].tail or '')
                node.remove(node[i])
                pieces = content.split()
                if not pieces:
                    continue
                if i == 0:
                    node.text = (node.text or '') + pieces[0]
                else:
                    node[i-1].tail = (node[i-1].tail or '') + pieces[0]
                for j in range(1, len(pieces)):
                    b = ET.Element('b')
                    b.tail = pieces[j]
                    node.insert(i, b)
                    i += 1
            else:
                i += 1

def insertWord(elem, headWord, tags):

    pieces = headWord.split()
    elem.text = pieces[0]
    for i in range(1, len(pieces)):
        b = ET.SubElement(elem, 'b')
        b.tail = pieces[i]
    for tag in tags:
        ET.SubElement(elem, 's', n=tag)

# Convert the headword to lower case, tag on the POS and see if that already is in the map
def checkForDuplicateHeadword(headWord, POSabbrev, hvo, duplicateHeadwordPOSmap):

    lowerCaseStr = headWord.lower() + POSabbrev

    # if we already have the headword with this pos in the list and it's not part of the same entry (the hvo number is the same) we have a duplicate entry
    if lowerCaseStr in duplicateHeadwordPOSmap and duplicateHeadwordPOSmap[lowerCaseStr] != hvo:

        return True

    duplicateHeadwordPOSmap[lowerCaseStr] = hvo

    return False

def getInflectionInfoSymbols(MSAobject):

    POS = Utils.as_string(MSAobject.PartOfSpeechRA.Abbreviation)
    POS = Utils.convertProblemChars(POS, Utils.catProbData)

    return [POS] + Utils.getInflectionTags(MSAobject)

def addFeatureStringsToMap(myDB, myMap):

    for feat in myDB.lp.MsFeatureSystemOA.FeaturesOC:

        if feat.ClassID == FsClosedFeatureTags.kClassId: # FsClosedFeature

            for val in IFsClosedFeature(feat).ValuesOC:

                featAbbr = ITsString(val.Abbreviation.BestAnalysisAlternative).Text
                featName = ITsString(val.Name.BestAnalysisAlternative).Text
                myMap[Utils.underscores(featAbbr)] = featName

def extract_bilingual_lex(DB, configMap, report=None, useCacheIfAvailable=False):

    errorList = []
    catSub           = ReadConfig.getConfigVal(configMap, ReadConfig.CATEGORY_ABBREV_SUB_LIST, report)
    linkField        = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    senseNumField    = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, report, giveError=False)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)
    sentPunct        = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)
    
    if not linkField:
        errorList.append((f"Custom field for linking doesn't exist. Please read the instructions.", 2))

    if not sourceMorphNames:
        errorList.append((f"No Source Morphnames to count as root found. Review your Settings.", 2))

    if not sentPunct:
        errorList.append((f"No Sentence Punctuation found. Review your Settings.", 2))

    if len(errorList) > 0:
        return errorList

    # Transform the straight list of category abbreviations to a list of tuples
    catSubDict = {}
    if catSub:
        if len(catSub) % 2 != 0:
            errorList.append(('Ill-formed property: "CategoryAbbrevSubstitutionList". Expected pairs of categories.', 2))
            return errorList
        for i in range(0,len(catSub),2):
            catSubDict[catSub[i]] = catSub[i+1]

    # Set objects for the two custom fields. Report errors if they don't exist in the source project.
    custSenseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    custSenseNumField = DB.LexiconGetSenseCustomFieldNamed(senseNumField)

    if not (custSenseEquivField):
        errorList.append((f"Custom field: {linkField} doesn't exist. Please read the instructions.", 2))
        return errorList

    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not bilingFile:
        errorList.append((f'A value for {ReadConfig.BILINGUAL_DICTIONARY_FILE} not found in the configuration file.', 2))
        return errorList

    fullPathBilingFile = bilingFile

    replFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
    if not replFile:
        errorList.append((f'A value for {ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE} not found in the configuration file.', 2))
        return errorList

    TargetDB = Utils.openTargetProject(configMap, report)

    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        errorList.append((f'A value for {ReadConfig.CACHE_DATA} not found in the configuration file.', 2))
        return errorList

    if cacheData == 'y':

        DONT_CACHE = False
    else:
        DONT_CACHE = True

    # If the target database hasn't changed since we created the affix file, don't do anything.
    if not DONT_CACHE and useCacheIfAvailable and bilingFileOutOfDate(DB, TargetDB, bilingFile) == False and replFileOutOfDate(bilingFile, replFile) == False:

        errorList.append(("The bilingual dictionary is up to date.", 0))
        pass

    else: # build the file

        posMap = {
            'sent': 'Sentence marker',
            'UNK': 'Unknown',
        }

        outputTree = ET.Element('dictionary')
        ET.SubElement(outputTree, 'alphabet')
        sdefs = ET.SubElement(outputTree, 'sdefs')
        mainSection = ET.SubElement(outputTree, 'section', id='main', type='standard')

        # Get all source and target categories along with inflection classes
        if Utils.get_categories(DB, report, posMap, TargetDB, numCatErrorsToShow=1, addInflectionClasses=True) == True:

            errorList.append(('Error retrieving categories.'), 2)
            TargetDB.CloseProject()
            return errorList

        # save features so they can go in the symbol definition section. Source and Target DBs.
        addFeatureStringsToMap(DB, posMap)
        addFeatureStringsToMap(TargetDB, posMap)

        errorList.append(("Building the bilingual dictionary...", 0))
        recordsDumpedCount = 0
        if report:
            report.ProgressStart(DB.LexiconNumberOfEntries())

        duplicateHeadwordPOSmap = {}

        # Loop through all the entries
        for entryCount, sourceEntry in enumerate(DB.LexiconAllEntries()):

            if report:
                report.ProgressUpdate(entryCount)

            # Simplify error reporting
            rawHeadWord = ITsString(sourceEntry.HeadWord).Text
            sourceURL = DB.BuildGotoURL(sourceEntry)

            # Don't process affixes, clitics  
            if sourceEntry.LexemeFormOA and sourceEntry.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
               sourceEntry.LexemeFormOA.MorphTypeRA and Utils.as_string(sourceEntry.LexemeFormOA.MorphTypeRA.Name) in sourceMorphNames:

                # Get the headword string
                headWord = ITsString(sourceEntry.HeadWord).Text

                # If there is not a homograph # at the end, make it 1
                headWord = Utils.add_one(headWord)

                if headWord != headWord.strip():
                    errorList.append((f'Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon', 1, sourceURL))

                if Utils.containsInvalidLemmaChars(headWord):
                    errorList.append((f'Found a headword with one of the following invalid characters: {Utils.RAW_INVALID_LEMMA_CHARS} in {rawHeadWord}. Please correct this in the lexicon before continuing.', 1, sourceURL))

                # Loop through senses
                for i, sourceSense in enumerate(sourceEntry.SensesOS):

                    targetFound = False
                    sourcePOSabbrev = 'UNK'
                    sourceTags = []
                    senseHeadWord = headWord + '.' + str(i+1)

                    # Make sure we have a valid analysis object
                    if sourceSense.MorphoSyntaxAnalysisRA:

                        # Get the POS abbreviation for the current sense, assuming we have a stem
                        if sourceSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':

                            sourceMsa = IMoStemMsa(sourceSense.MorphoSyntaxAnalysisRA)
                            if sourceMsa.PartOfSpeechRA:

                                sourcePOSabbrev = ITsString(sourceMsa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                                sourcePOSabbrev = Utils.convertProblemChars(sourcePOSabbrev, Utils.catProbData)

                                # Get source inflection strings (containing class and feature abbreviations)
                                sourceTags = getInflectionInfoSymbols(sourceMsa)
                                sourcePOSabbrev = sourceTags[0]

                            else:
                                errorList.append(('Encountered a sense that has unknown POS'+\
                                                  ' while processing source headword: '+rawHeadWord, 1, sourceURL))
                                sourceTags = ['UNK']
                                sourcePOSabbrev = 'UNK'

                            # Check if we have a duplicate headword-POS which can happen if the POS is the same and the headwords differ only in case.
                            if checkForDuplicateHeadword(senseHeadWord, sourcePOSabbrev, sourceEntry.Hvo, duplicateHeadwordPOSmap):

                                errorList.append((f'Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense.'+\
                                                  'Source headword: '+rawHeadWord, 1, sourceURL))
                                continue

                            entryElem = ET.SubElement(mainSection, 'e', w='1')
                            # we can't use indent() because that would end up
                            # inserting spaces between tags
                            entryElem.tail = '\n    '

                            # If we have a link to a target entry, process it
                            equivStr = Utils.getTargetEquivalentUrl(DB, sourceSense, custSenseEquivField)

                            # handle a sense mapped intentionally to nothing. Skip it.
                            if equivStr == Utils.NONE_HEADWORD:

                                pairElem = ET.SubElement(entryElem, 'p')
                                leftElem = ET.SubElement(pairElem, 'l')
                                rightElem = ET.SubElement(pairElem, 'r')
                                insertWord(leftElem, senseHeadWord, sourceTags)
                                # the output is blank, so don't fill in the <r>
                                targetFound = True

                                recordsDumpedCount += 1

                            elif equivStr:

                                targetSense, targetLemma, senseNum = Utils.getTargetSenseInfo(sourceEntry, DB, TargetDB, sourceSense, equivStr, \
                                                                    custSenseNumField, report, remove1dot1Bool=False)
                                if targetSense:

                                    targetTags = []

                                    if targetSense.MorphoSyntaxAnalysisRA and targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':

                                        targetMsa = IMoStemMsa(targetSense.MorphoSyntaxAnalysisRA)
                                        if targetMsa.PartOfSpeechRA:

                                            targetFound = True

                                            # Get target inflection strings (containing class and feature abbreviations)
                                            targetTags = getInflectionInfoSymbols(targetMsa)

                                            pairElem = ET.SubElement(entryElem, 'p')
                                            leftElem = ET.SubElement(pairElem, 'l')
                                            rightElem = ET.SubElement(pairElem, 'r')
                                            insertWord(leftElem, senseHeadWord, sourceTags)
                                            insertWord(rightElem, targetLemma, targetTags)


                                            recordsDumpedCount += 1

                                        else:
                                            errorList.append(('Skipping sense because the target POS is undefined '+\
                                                            ' for target headword: '+ITsString(ILexEntry(targetSense.Entry).HeadWord).Text+\
                                                            ' while processing source headword: '+rawHeadWord, 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                    else:
                                        errorList.append(('Skipping sense because it is of this class: '+targetMsa.ClassName+\
                                                        ' for target headword: '+ITsString(ILexEntry(targetSense.Entry).HeadWord).Text+\
                                                        ' while processing source headword: '+rawHeadWord, 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                else:
                                    # Error already reported
                                    pass
                            else:
                                # Don't report this. Most of the time the equivalent field will be empty.
                                pass
                        else:
                            errorList.append(('Skipping sense that is of class: '+sourceSense.MorphoSyntaxAnalysisRA.ClassName+\
                                              ' for headword: '+rawHeadWord, 1, sourceURL))
                    else:
                        errorList.append(('Skipping sense, no analysis object'\
                                           ' for headword: '+rawHeadWord, 1, sourceURL))
                    if not targetFound:
                        # output the bilingual dictionary line -- source and target are the same

                        # do substitutions of categories. This is for standard substitutions where
                        # the target category name is different even though essentially the categories are equivalent.

                        if sourcePOSabbrev in catSubDict:
                            pairElem = ET.SubElement(entryElem, 'p')
                            leftElem = ET.SubElement(pairElem, 'l')
                            rightElem = ET.SubElement(pairElem, 'r')
                            insertWord(leftElem, senseHeadWord, sourceTags)
                            insertWord(rightElem, senseHeadWord, [catSubDict[sourcePOSabbrev]] + sourceTags[1:])

                        else:
                            identityElem = ET.SubElement(entryElem, 'i')
                            insertWord(identityElem, senseHeadWord, sourceTags)

                        recordsDumpedCount += 1

            else:
                if sourceEntry.LexemeFormOA == None:

                    errorList.append(('No lexeme form. Skipping. Headword: '+rawHeadWord, 1, sourceURL))

                elif sourceEntry.LexemeFormOA.ClassName != 'MoStemAllomorph':

                    # We've documented that affixes are skipped. Don't report this
                    pass

                elif sourceEntry.LexemeFormOA.MorphTypeRA == None:

                    errorList.append(('No Morph Type. Skipping.'+rawHeadWord+' Best Vern: '+ITsString(sourceEntry.LexemeFormOA.Form.BestVernacularAlternative).Text, 1, sourceURL))

        mainSection.append(ET.Comment(' SECTION: Punctuation '))

        # Create a regular expression string for the punctuation characters
        # Note that we have to escape ? + * | if they are found in the sentence-final punctuation
        reStr = re.sub(r'([+?|*])',r'\\\1',sentPunct)
        reStr = '['+reStr+']+'

        # This notation in Apertium basically means that any combination of the given punctuation characters
        # with the tag <sent> will be substituted with the same thing plus the <sent> tag.

        punctEntry = ET.SubElement(mainSection, 'e', w='1')
        reElem = ET.SubElement(punctEntry, 're')
        reElem.text = reStr
        posElem = ET.SubElement(punctEntry, 'i')
        ET.SubElement(posElem, 's', n='sent')

        replTree = None

        try:
            with open(replFile, encoding='utf-8') as fin:
                text = fin.read()
                text = unicodedata.normalize('NFD', text)
                replTree = ET.parse(io.StringIO(text)).getroot()
        except:
            errorList.append((f'There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.', 2))

        if replTree:
            # get rid of <leftdata> and <rightdata> (if present)
            convertOldEntries(replTree)
            # add any missing <sdef>s
            for sdef in replTree.findall('.//sdef'):
                if 'c' in sdef.attrib:
                    posMap[sdef.attrib['n']] = sdef.attrib['c']
            for symbol in replTree.findall('.//s'):
                posMap.setdefault(symbol.attrib['n'], '')
            # add the entries
            for section in replTree.findall('.//section'):
                outputTree.append(section)

        for abbr, name in sorted(posMap.items(), key=lambda x: (x[0].lower(), x[1])):
            if name:
                ET.SubElement(sdefs, 'sdef', n=abbr, c=name)
            else:
                ET.SubElement(sdefs, 'sdef', n=abbr)

        try:
            with open(fullPathBilingFile, 'wb') as fout:
                fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
                fout.write(b'<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
                fout.write(ET.tostring(outputTree, encoding='utf-8'))
        except IOError as err:
            errorList.append((f'There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.', 2))
            TargetDB.CloseProject()
            return errorList

        errorList.append(('Creation complete to the file: '+fullPathBilingFile+'.', 0))
        errorList.append((f'{recordsDumpedCount} records created in the bilingual dictionary.', 0))

    TargetDB.CloseProject()
    return errorList

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Call the main function
    errorList = extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=True)

    # output info, warnings, errors and url links
    Utils.processErrorList(errorList, report)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
