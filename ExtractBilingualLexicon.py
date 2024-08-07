#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
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
#   Version 3.7.1 - 12/25/22 - Ron Lockwood
#    Added RegexFlag before re constants
#
#   Version 3.7 - 12/12/22 - Ron Lockwood
#    Skip entries that are mapped to the 'none' headword
#
#   Version 3.6.3 - 9/1/22 - Ron Lockwood
#    Fixes #254. Convert * to _ in stems.
#
#   Version 3.6.2 - 8/26/22 - Ron Lockwood
#    Fixes #215 Check morpheme type against guid in the object instead of
#    the analysis writing system so we aren't dependent on an English WS.
#
#   Version 3.6.1 - 8/19/22 - Ron Lockwood
#    Use new new function getXMLEntryText which should be more efficient.
#
#   Version 3.6 - 8/11/22 - Ron Lockwood
#    Fixes #65. Decompose the replacement file before combining with bilingual lexicon.
#
#   Version 3.5.4 - 8/8/22 - Ron Lockwood
#    Fixes #142. Warn when entries start with a space.
#
#   Version 3.5.3 - 7/9/22 - Ron Lockwood
#    Use a new config setting for using cache. Fixes #115.
#
#   Version 3.5.2 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.1 - 6/22/22 - Ron Lockwood
#    Change in FlexTools 2.1 means that an empty string gets returned now from
#    a custom field that has nothing in it. Before it was None. Fixes #156
#
#   Version 3.5 - 4/1/22 - Ron Lockwood
#    Put the code that does the main work into its own function so it can be
#    called by the Live Rule Tester. This means that a possible null report
#    object is passed in. Also use an error list in the new function instead of
#    report object. Output collected errors at the end. Fixes #37
#
#   Version 3.4.2 - 3/11/22 - Ron Lockwood
#    Give errors if biling lex file or replacement file values not found in the
#    configuration file.
#    Fixed bug where the old style replacement file wasn't doing the append section
#    correctly.
#
#   Version 3.4.1 - 3/4/22 - Ron Lockwood
#    Set sourcePOSabbrev variable in the main loop to prevent crash shown in issue #79.
#    Also put out UNK as a symbol in the symbol definitions for the
#    bilingual.dix file. Simplified building the sdef string.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.3 - 2/4/22 - Ron Lockwood
#    Changed replacement file to a different format for improved editing. Handle
#    either the old format or the new which uses new elements <leftdata> <rightdata>
#
#   Version 3.3.2 - 1/27/22 - Ron Lockwood
#    Major overhaul of the Setup Transfer Rule Grammatical Categories Tool.
#    Now the setup tool and the bilingual lexicon uses common code for getting
#    the grammatical categories from each lexicon. Fixes #50.
#
#   Version 3.3.1 - 1/25/22 - Ron Lockwood
#    Fixed crash when grammatical category not set for a word.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2.1 - 11/30/21 - Ron Lockwood
#    Report when the bilingual lexicon is up to date (taken from cache).
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Put underscores in target feature abbreviations if necessary.
#
#   Version 3.0.5 - 7/8/21 - Ron Lockwood
#    Handle slash in category name
#
#   Version 3.0.4 - 7/1/21 - Ron Lockwood
#    Instead of just using the text in the <l> element as the key for finding
#    lines in the bilingual file, use everything between <l>
#    and </l> including </b>, but remove any <s> elements. This is because sometimes
#    we have a phrase in the replacement file that has a space (/b) and before we would
#    only pick up the text before the space.
#
#   Version 3.0.3 - 4/30/21 - Ron Lockwood
#    Just give one warning for spaces in categories and likewise one warning for
#    periods in categories. Make the "suppressing" message just info. not a warning
#    This cuts down on the number of warning you always have
#    to see if these warnings are prevalent.
#
#   Version 3.0.2 - 2/26/21 - Ron Lockwood
#    Check if the bilingual file is older than the replacement file and if so
#    process everything.
#
#   Version 3.0.1 - 2/15/21 - Ron Lockwood
#    Always process the replacement file, even if the biling file is up-to-date.
#    This will allow changes there to be seen in results every time.
#
#   Version 3.0 - 1/27/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0.2 - 2/4/20 - Ron Lockwood
#    give an error when the target db open fails.
#
#   Version 2.0.1 - 1/22/20 - Ron Lockwood
#    Only do replacement file if the dictionary is out of date.
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.6.2 - 4/5/19 - Ron Lockwood
#    Check if the bilingual dictionary is out of date in respect to the source
#    and target databases. If not, just process the replacement file. Don't do
#    anything else. This helps performance.
#
#   Version 1.6.1 - 3/27/19 - Ron Lockwood
#    Limit the number of warnings shown for pos abbreviations in the wrong format.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.3.7 - 12/24/17 - Ron Lockwood
#    When processing replacements, don't add symbols that already exist in the
#    bilingual dictionary. Add new lines at then end of comment elements to get
#    multiple lines.
#
#   Version 1.3.6 - 12/24/17 - Ron
#    Changed the way the replacement file is processed since it is now a fully
#    valid XML file with two section elements for replacing or appending. We
#    now process both the replacement file and the bilingual file with
#    ElementTree & Element objects. Loop through objects in both XML files and
#    replace or add entries from the replacement file in the bilingual dic. file.
#
#   Version 1.3.5 - 7/28/17 - Ron
#    Check that there is a valid target POS before processing the POS names and
#    abbreviations.
#
#   Version 1.3.4 - 1/18/17 - Ron
#    Give a warning if there is a space or an period in a grammatical category.
#    Change the space to an underscore and remove periods.
#
#   Version 1.3.3 - 5/7/16 - Ron
#    Give a more helpful message when the target database is not found.
#    Give an error for every category abbreviation that has a space in it then
#    exit.
#
#   Version 1.3.2 - 4/23/16 - Ron
#    Check for valid analysis object before checking class name.
#    Don't use tempfile for the bilingual dictionary file.
#
#   Version 1.3.1 - 4/15/16 - Ron
#    No changes to this module.
#
#   Version 1.2.1 - 2/11/16 - Ron
#    Error checking when opening the replacement file.
#
#   Version 1.2.0 - 1/28/16 - Ron
#    Punctuation support. Use what the user specified in the configuration file for
#    what is put at the bottom of the bilingual dictionary to handle sentence
#    punctuation.
#    Bug fix. When getting inflection class information recursively set the name
#    before checking for sub inflection classes.
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

from System import Guid
from System import String

from SIL.LCModel import (
    IMoStemMsa,
    IFsClosedFeature,
    FsClosedFeatureTags,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString

from flextoolslib import *

import ReadConfig
import Utils

DONT_CACHE = True

DICTIONARY = 'dictionary'
REPLDICTIONARY = 'repldictionary'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Build Bilingual Lexicon",
        FTM_Version    : "3.10",
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

    POS = ITsString(MSAobject.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
    POS = Utils.convertProblemChars(POS, Utils.catProbData)

    symbols = []

    if MSAobject.InflectionClassRA:
        symbols.append(ITsString(MSAobject.InflectionClassRA.Abbreviation.BestAnalysisAlternative).Text)

    if MSAobject.MsFeaturesOA:

        featureAbbrList = []

        # The features might be complex, make a recursive function call to find all leaf features
        Utils.get_feat_abbr_list(MSAobject.MsFeaturesOA.FeatureSpecsOC, featureAbbrList)

        symbols += [abb for grpName, abb in sorted(featureAbbrList)]

    return [POS] + [Utils.underscores(abb) for abb in symbols]

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

    if not (linkField and sourceMorphNames and sentPunct):
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
               sourceEntry.LexemeFormOA.MorphTypeRA and Utils.morphTypeMap[sourceEntry.LexemeFormOA.MorphTypeRA.Guid.ToString()] in sourceMorphNames:

                # Get the headword string
                # If there is not a homograph # at the end, make it 1
                headWord = Utils.add_one(rawHeadWord)

                # Convert problem chars in the headWord
                headWord = Utils.convertProblemChars(headWord, Utils.lemmaProbData)

                if headWord != headWord.strip():
                    errorList.append((f'Found an entry with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon', 1, sourceURL))

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

                                # Get source inflection strings (containing class and feature abbreviations)
                                sourceTags = getInflectionInfoSymbols(sourceMsa)
                                sourcePOSabbrev = sourceTags[0]

                            else:
                                errorList.append(('Encountered a sense that has unknown POS'+\
                                                  ' while processing source headword: '+rawHeadWord, 1, sourceURL))
                                sourceTags = ['UNK']
                                sourcePOSabbrev = 'UNK'

                            # Check if we have a duplicate headword-POS which can happen if the POS is the same and the headwords differ only in case.
                            if checkForDuplicateHeadword(headWord, sourcePOSabbrev, sourceEntry.Hvo, duplicateHeadwordPOSmap):

                                errorList.append((f'Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense.'+\
                                                  'Source headword: '+rawHeadWord, 1, sourceURL))
                                continue

                            entryElem = ET.SubElement(mainSection, 'e', w='1')

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
                                            insertWord(leftElem, headWord, sourceTags)
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
            with open(replFile) as fin:
                text = fin.read()
                text = unicodedata.normalize('NFD', text)
                replTree = ET.parse(io.StringIO(text)).getroot()
        except:
            errorList.append((f'There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.', 2))

        if replTree:
            convertOldEntries(replTree)
            for sdef in replTree.findall('.//sdef'):
                if 'c' in sdef.attrib:
                    posMap[sdef.attrib['n']] = sdef.attrib['c']
            for symbol in replTree.findall('.//s'):
                posMap.setdefault(symbol.attrib['n'], '')
            for section in replTree.findall('.//section'):
                outputTree.append(section)

        for abbr, name in sorted(posMap.items(), key=lambda x: (x[0].lower(), x[1])):
            if name:
                ET.SubElement(sdefs, 'sdef', n=abbr, c=name)
            else:
                ET.SubElement(sdefs, 'sdef', n=abbr)

        ET.indent(outputTree)

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
