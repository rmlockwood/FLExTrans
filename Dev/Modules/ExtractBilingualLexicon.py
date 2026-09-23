#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.17.2 - 9/8/26 - Ron Lockwood
#    Replaced the old description at the top with a code description block: overview, the lemma naming scheme, what each sense produces, the symbol definitions, the replacement file, whitespace, One project mode, caching and code structure.
#
#   Version 3.17.1 - 9/8/26 - Ron Lockwood
#    Test the replacement dictionary root element for None rather than for truth.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.2 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16.1 - 6/24/26 - Ron Lockwood
#    One project mode: read target lemmas in the target writing system, treat a missing link as a link to the same sense, and reuse the source project as the target.
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.3 - 3/30/26 - Ron Lockwood
#    Fixes for Python linter.
#
#   Version 3.15.2 - 3/30/26 - Ron Lockwood
#    Fixes #1282. Give an error when ERR comes back for an inflection feature.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14 - 5/16/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.2 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
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
#   2023 version history removed on 2/6/26
#
#   earlier version history removed on 3/1/25
#
#   OVERVIEW (AI generated, then edited)
#
#   This module builds the bilingual lexicon, one of the two files the Apertium transfer engine needs (the other being the transfer rules file). The lexicon is what turns a source word into a
#   target word: for every sense in the source project it writes one entry pairing the source lemma with the target lemma the user linked it to. Everything else Apertium does - reordering words,
#   changing features, inserting or deleting words - is the rules file's job. The output goes to the file named by the Bilingual Dictionary Output File setting, normally bilingual.dix in the
#   Output folder, in Apertium's .dix XML format.
#
#   The links come from a custom sense-level field in the source project holding a URL to a target sense, named by the Source Custom Field for Sense Link setting; the Sense Linker module is what
#   fills those in. This module only reads them and never writes to either FLEx project. A sense with no link still gets an entry - an identity entry that passes the source lemma through
#   unchanged - so that no word silently disappears from the translation.
#
#   THE LEMMA NAMING SCHEME
#
#   An Apertium lexicon pairs two lemmas plus a few tags and nothing else, so a lemma has to carry enough on its own to identify one FLEx sense unambiguously. The scheme is headword + '.' + sense
#   number, where the headword is the citation form if there is one and the lexeme form otherwise, followed by a homograph number. FLEx uses homograph 0 when a form is not duplicated, so
#   Utils.add_one() turns that into 1 and every lemma ends up with one, giving forms like house1.2. Every other FLExTrans module that emits or reads lemmas uses this same scheme, so it cannot be
#   changed here alone.
#
#   WHAT EACH SENSE PRODUCES
#
#   Only entries whose lexeme form is a stem with a morph type listed in the Source Morpheme Types Counted As Roots setting are processed; affixes and clitics are skipped deliberately and without
#   comment, since that is documented behavior. For each sense of such an entry one of the following is written:
#    - The link field holds Utils.NONE_HEADWORD, meaning the user deliberately mapped the sense to nothing: a <p> with a filled <l> and an empty <r>, which deletes the word from the target text.
#    - The link field holds a URL: the target sense is looked up in the target project and a <p> pairs the source lemma and tags with the target lemma and tags.
#    - The link field is empty and this is One project mode: the sense links to itself, so the target lemma is that same sense read in the target writing system.
#    - The source category appears in the Category Abbreviation Pairs setting: a <p> pairing the lemma with itself but with the category substituted, for when the two projects call the same
#      category by different names.
#    - Otherwise an <i> (identity) element, the one lemma standing for both sides.
#
#   The last two are reached through the targetFound flag rather than from the link field alone, and that is what makes the module forgiving: if anything above went wrong - no analysis object, an
#   unknown part of speech, a target sense whose part of speech is undefined - a warning is reported and the sense still falls through to an identity entry instead of vanishing from the lexicon.
#
#   Two headwords that differ only in case collapse to the same lemma once Apertium lowercases them. checkForDuplicateHeadword() catches that, keyed on the lowercased headword plus the category
#   and compared by entry Hvo so that two senses of one entry are not mistaken for a clash, and the second one is skipped with a warning.
#
#   THE SYMBOL DEFINITIONS
#
#   Every tag used anywhere in the file has to be declared in the <sdefs> section, so posMap accumulates them as the file is built: three built-in ones (sent, UNK and ERR), then all categories and
#   inflection classes from both projects through Utils.get_categories(), then every closed-feature value from both projects through addFeatureStringsToMap(), then whatever the replacement file
#   turns out to use. The <sdefs> element is created empty near the top of the tree but only filled in at the very end, after the replacement file has been read - that ordering is what lets a
#   symbol used only by a hand-written replacement entry still get declared.
#
#   A tag of ERR means an inflection feature could not be resolved, usually because it is not properly defined in FLEx. It is written into the lexicon rather than suppressed so that the user can
#   see where it landed, and getInflectionInfoSymbols() reports it as an error as well.
#
#   The last entry in the main section is not a word at all: it is an Apertium <re> (regular expression) matching any run of the characters in the Sentence Punctuation setting, mapped to the same
#   run tagged <sent>, so that sentence punctuation passes through transfer. The characters + ? | and * have to be escaped when they appear in that setting or the expression would mean something
#   else entirely.
#
#   THE REPLACEMENT FILE
#
#   A second .dix file, named by the Bilingual Dictionary Replacement File setting, to override or add entries that the generated ones get wrong; the Replacement Editor module is
#   what maintains it. Its <section> elements are appended to the output whole, so they land after the generated section and win. Older replacement files wrapped word text in <leftdata> and
#   <rightdata> elements, and convertOldEntries() rewrites those into the plain form so that an old file keeps working.
#
#   WHITESPACE IS DATA
#
#   In a .dix file the text inside <l>, <r> and <i> is the word itself, so whitespace added between tags would become part of the lemma. That has two consequences worth knowing before editing this
#   code. A lemma containing a space cannot simply be written as text: it goes out as text plus a <b/> element whose tail carries the next word, which is what insertWord() does. And the tree
#   cannot be pretty-printed - ET.indent() would corrupt every lemma in the file - so instead each entry element gets a hand-set tail of a newline and four spaces to keep the file readable, and
#   the file is written with ET.tostring() after a hand-written XML declaration and DOCTYPE rather than through ElementTree.write(). The DOCTYPE names dix.dtd so the result opens in the XMLmind
#   dictionary add-on.
#
#   ONE PROJECT MODE
#
#   When the Project Mode setting is One project there is no second FLEx project: the target is the same project read in a different writing system. TargetDB is then the very same object as DB, and
#   a target writing-system handle is resolved from the Target Writing System setting and passed down to the lemma lookups. Every place that would close the target project therefore tests
#   TargetDB is not DB first - closing it in One project mode would close the source project out from under the caller, which still needs it. There are three such places: two error exits and the
#   end of the run.
#
#   CACHING
#
#   When the Cache data for faster processing? setting is on and the caller asks for the cache, the whole rebuild is skipped if nothing it depends on has changed since bilingual.dix was written.
#   Both halves of that matter: bilingFileOutOfDate() compares the two FLEx projects' last-modified dates against the file, and replFileOutOfDate() compares the replacement file against it, since
#   editing replacements alone has to be enough to force a rebuild.
#
#   CODE STRUCTURE
#
#   Top to bottom the file goes: the docs dictionary FlexTools displays, then the small helpers - getFileTime(), getDBTime(), bilingFileOutOfDate() and replFileOutOfDate() for the cache check,
#   convertOldEntries() and insertWord() for building and repairing entry XML, and checkForDuplicateHeadword(), getInflectionInfoSymbols() and addFeatureStringsToMap() - then
#   extract_bilingual_lex(), which is the whole job, and finally MainFunction() and the FlexToolsModule declaration that FlexTools looks for at the very bottom.
#
#   extract_bilingual_lex() sets the order of the work: read and check the settings, resolve the target project (or the target writing system in One project mode), take the cache shortcut if it
#   can, build the output tree, loop over every entry and sense writing the entries described above, add the punctuation entry, merge the replacement file, write out the <sdefs> it accumulated
#   along the way, write the file, and close the target project if it opened one. It collects messages into a list of tuples as it goes rather than reporting them itself, and
#   Utils.processErrorList() turns that list into what the user sees.
#

import re
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import unicodedata
import io

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from SIL.LCModel import ( # type: ignore
    IMoStemMsa,
    IFsClosedFeature,
    FsClosedFeatureTags,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString  # type: ignore

from flextoolslib import * # type: ignore

import Mixpanel
import ReadConfig
import Utils
from ReplacementEditor import docs as ReplEditorDocs

DONT_CACHE = True

DICTIONARY = 'dictionary'
REPLDICTIONARY = 'repldictionary'

# Define _translate for convenience
_translate = QCoreApplication.translate

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['ExtractBilingualLexicon'], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("ExtractBilingualLexicon", "Build Bilingual Lexicon"),
        FTM_Version    : "3.17.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("ExtractBilingualLexicon", "Builds an Apertium-style bilingual lexicon."),
        FTM_Help   : "",
        FTM_Description: _translate("ExtractBilingualLexicon", 
"""This module will build a bilingual lexicon for two projects. The
project that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these links.
The bilingual lexicon will be stored in the file specified by the Bilingual Dictionary Output File setting.
This is typically called bilingual.dix and is usually in the Output folder.\n
You can make custom changes to the bilingual lexicon by using the {replEditorModule}. See the help
document for more details.""").format(replEditorModule=ReplEditorDocs[FTM_Name])}

#app.quit()
#del app

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

def getInflectionInfoSymbols(MSAobject, errorList, rawHeadWord, sourceURL):

    POS = Utils.as_string(MSAobject.PartOfSpeechRA.Abbreviation)
    POS = Utils.convertProblemChars(POS, Utils.catProbData)

    tagsList = Utils.getInflectionTags(MSAobject)

    # Check if any of the tags have the value ERR and if so, log an error
    # ERR can come from a feature that isn't properly defined.
    for tag in tagsList:

        if tag == 'ERR':
            errorList.append((_translate("ExtractBilingualLexicon", "Encountered a sense that has an invalid feature while processing source headword: {rawHeadWord}").format(rawHeadWord=rawHeadWord), 2, sourceURL))

    return [POS] + tagsList

def addFeatureStringsToMap(myDB, myMap):

    for feat in myDB.lp.MsFeatureSystemOA.FeaturesOC:

        if feat.ClassID == FsClosedFeatureTags.kClassId: # FsClosedFeature

            for val in IFsClosedFeature(feat).ValuesOC:

                featAbbr = Utils.as_string(val.Abbreviation)
                featName = Utils.as_string(val.Name)
                myMap[Utils.underscores(featAbbr)] = featName

def extract_bilingual_lex(DB, configMap, report=None, useCacheIfAvailable=False):

    errorList = []
    catSub           = ReadConfig.getConfigVal(configMap, ReadConfig.CATEGORY_ABBREV_SUB_LIST, report)
    linkField        = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    senseNumField    = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, report, giveError=False)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)
    sentPunct        = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)
    
    if not linkField:
        errorList.append((_translate("ExtractBilingualLexicon", "Custom field for linking doesn't exist. Please read the instructions."), 2))

    if not sourceMorphNames:
        errorList.append((_translate("ExtractBilingualLexicon", "No Source Morphnames to count as root found. Review your Settings."), 2))

    if not sentPunct:
        errorList.append((_translate("ExtractBilingualLexicon", "No Sentence Punctuation found. Review your Settings."), 2))
        sentPunct = ''

    if len(errorList) > 0:
        return errorList

    # Transform the straight list of category abbreviations to a list of tuples
    catSubDict = {}
    if catSub:
        if len(catSub) % 2 != 0:
            errorList.append((_translate("ExtractBilingualLexicon", 'Ill-formed property: "CategoryAbbrevSubstitutionList". Expected pairs of categories.'), 2))
            return errorList
        for i in range(0,len(catSub),2):
            catSubDict[catSub[i]] = catSub[i+1]

    # Set objects for the two custom fields. Report errors if they don't exist in the source project.
    custSenseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    custSenseNumField = DB.LexiconGetSenseCustomFieldNamed(senseNumField)

    if not (custSenseEquivField):
        errorList.append((_translate("ExtractBilingualLexicon", "Custom field: {linkField} doesn't exist. Please read the instructions.").format(linkField=linkField), 2))
        return errorList

    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not bilingFile:
        errorList.append((_translate("ExtractBilingualLexicon", "A value for {key} not found in the configuration file.").format(key=ReadConfig.BILINGUAL_DICTIONARY_FILE), 2))
        return errorList

    fullPathBilingFile = bilingFile

    replFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
    if not replFile:
        errorList.append((_translate("ExtractBilingualLexicon", "A value for {key} not found in the configuration file.").format(key=ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE), 2))
        return errorList

    # In One project mode there is no separate target project: the "target" is the same project read in the target writing
    # system. So reuse the source DB and resolve the target WS handle; otherwise open the configured target project as usual.
    twoProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False)
    oneProjectMode = twoProjectMode == 'n'
    targetWSHandle = None

    if oneProjectMode:

        TargetDB = DB
        targetWSTag = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_WRITING_SYSTEM, report, giveError=False)

        if targetWSTag:

            targetWSHandle = DB.WSHandle(targetWSTag)
    else:
        TargetDB = Utils.openTargetProject(configMap, report)

    if not TargetDB:
        return

    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        errorList.append((_translate("ExtractBilingualLexicon", "A value for {key} not found in the configuration file.").format(key=ReadConfig.CACHE_DATA), 2))
        return errorList

    if cacheData == 'y':

        DONT_CACHE = False
    else:
        DONT_CACHE = True

    # If the target project hasn't changed since we created the affix file, don't do anything.
    if not DONT_CACHE and useCacheIfAvailable and bilingFileOutOfDate(DB, TargetDB, bilingFile) == False and replFileOutOfDate(bilingFile, replFile) == False:

        errorList.append((_translate("ExtractBilingualLexicon", "The bilingual dictionary is up to date."), 0))
        pass

    else: # build the file

        posMap = {
            'sent': 'Sentence marker',
            'UNK': 'Unknown',
            'ERR': 'Error in inflection class/feature',
        }

        outputTree = ET.Element('dictionary')
        ET.SubElement(outputTree, 'alphabet')
        sdefs = ET.SubElement(outputTree, 'sdefs')
        mainSection = ET.SubElement(outputTree, 'section', id='main', type='standard')

        # Get all source and target categories along with inflection classes
        if Utils.get_categories(DB, report, posMap, TargetDB, numCatErrorsToShow=1, addInflectionClasses=True) == True:

            errorList.append((_translate("ExtractBilingualLexicon", "Error retrieving categories."), 2))

            if TargetDB is not DB:

                TargetDB.CloseProject()

            return errorList

        # save features so they can go in the symbol definition section. Source and Target DBs.
        addFeatureStringsToMap(DB, posMap)
        addFeatureStringsToMap(TargetDB, posMap)

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
                    errorList.append((_translate("ExtractBilingualLexicon", "Found a headword with preceding or trailing spaces while processing source headword: {rawHeadWord}. The spaces were removed, but please correct this in the lexicon.").format(rawHeadWord=rawHeadWord), 1, sourceURL))

                if Utils.containsInvalidLemmaChars(headWord):
                    errorList.append((_translate("ExtractBilingualLexicon", "Found a headword with one of the following invalid characters: {chars} in {rawHeadWord}. Please correct this in the lexicon before continuing.").format(chars=Utils.RAW_INVALID_LEMMA_CHARS, rawHeadWord=rawHeadWord), 1, sourceURL))

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

                                sourcePOSabbrev = Utils.as_string(sourceMsa.PartOfSpeechRA.Abbreviation)
                                sourcePOSabbrev = Utils.convertProblemChars(sourcePOSabbrev, Utils.catProbData)

                                # Get source inflection strings (containing class and feature abbreviations)
                                sourceTags = getInflectionInfoSymbols(sourceMsa, errorList, rawHeadWord, sourceURL)
                                sourcePOSabbrev = sourceTags[0]

                            else:
                                errorList.append((_translate("ExtractBilingualLexicon", "Encountered a sense that has unknown POS while processing source headword: {rawHeadWord}").format(rawHeadWord=rawHeadWord), 1, sourceURL))
                                sourceTags = ['UNK']
                                sourcePOSabbrev = 'UNK'

                            # Check if we have a duplicate headword-POS which can happen if the POS is the same and the headwords differ only in case.
                            if checkForDuplicateHeadword(senseHeadWord, sourcePOSabbrev, sourceEntry.Hvo, duplicateHeadwordPOSmap):

                                errorList.append((_translate("ExtractBilingualLexicon", "Encountered a headword that only differs in case from another headword with the same POS ({sourcePOSabbrev}). Skipping this sense. Source headword: {rawHeadWord}").format(sourcePOSabbrev=sourcePOSabbrev, rawHeadWord=rawHeadWord), 1, sourceURL))
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
                                                                    custSenseNumField, report, remove1dot1Bool=False, targetWSHandle=targetWSHandle)
                                if targetSense:

                                    targetTags = []

                                    if targetSense.MorphoSyntaxAnalysisRA and targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':

                                        targetMsa = IMoStemMsa(targetSense.MorphoSyntaxAnalysisRA)
                                        if targetMsa.PartOfSpeechRA:

                                            targetFound = True

                                            # Get target inflection strings (containing class and feature abbreviations)
                                            targetTags = getInflectionInfoSymbols(targetMsa, errorList, rawHeadWord, sourceURL)

                                            pairElem = ET.SubElement(entryElem, 'p')
                                            leftElem = ET.SubElement(pairElem, 'l')
                                            rightElem = ET.SubElement(pairElem, 'r')
                                            insertWord(leftElem, senseHeadWord, sourceTags)
                                            insertWord(rightElem, targetLemma, targetTags)


                                            recordsDumpedCount += 1

                                        else:
                                            errorList.append((_translate("ExtractBilingualLexicon", "Skipping sense because the target POS is undefined for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}").format(targetHeadWord=ITsString(ILexEntry(targetSense.Entry).HeadWord).Text, rawHeadWord=rawHeadWord), 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                    else:
                                        errorList.append((_translate("ExtractBilingualLexicon", "Skipping sense because it is of this class: {className} for target headword: {targetHeadWord} while processing source headword: {rawHeadWord}").format(className=targetMsa.ClassName, targetHeadWord=ITsString(ILexEntry(targetSense.Entry).HeadWord).Text, rawHeadWord=rawHeadWord), 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                else:
                                    # Error already reported
                                    pass
                            elif oneProjectMode:

                                # No link in the custom field. In One project mode the entry links to itself, so the target is the
                                # same sense rendered in the target writing system (same entry, same POS, just a different WS).
                                targetLemma = Utils.fixupLemma(sourceEntry, i+1, wsHandle=targetWSHandle)

                                pairElem = ET.SubElement(entryElem, 'p')
                                leftElem = ET.SubElement(pairElem, 'l')
                                rightElem = ET.SubElement(pairElem, 'r')
                                insertWord(leftElem, senseHeadWord, sourceTags)
                                insertWord(rightElem, targetLemma, sourceTags)
                                targetFound = True
                                recordsDumpedCount += 1
                            else:
                                # Don't report this. Most of the time the equivalent field will be empty.
                                pass
                        else:
                            errorList.append((_translate("ExtractBilingualLexicon", "Skipping sense that is of class: {className} for headword: {rawHeadWord}").format(className=sourceSense.MorphoSyntaxAnalysisRA.ClassName, rawHeadWord=rawHeadWord), 1, sourceURL))
                    else:
                        errorList.append((_translate("ExtractBilingualLexicon", "Skipping sense, no analysis object for headword: {rawHeadWord}").format(rawHeadWord=rawHeadWord), 1, sourceURL))
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

                    errorList.append((_translate("ExtractBilingualLexicon", "No lexeme form. Skipping. Headword: {rawHeadWord}").format(rawHeadWord=rawHeadWord), 1, sourceURL))

                elif sourceEntry.LexemeFormOA.ClassName != 'MoStemAllomorph':

                    # We've documented that affixes are skipped. Don't report this
                    pass

                elif sourceEntry.LexemeFormOA.MorphTypeRA == None:

                    errorList.append((_translate("ExtractBilingualLexicon", "No Morph Type. Skipping. {rawHeadWord} Best Vern: {vernString}").format(rawHeadWord=rawHeadWord, vernString=Utils.as_vern_string(sourceEntry.LexemeFormOA.Form)), 1, sourceURL))

        mainSection.append(ET.Comment(' SECTION: Punctuation '))

        # Create a regular expression string for the punctuation characters
        # Note that we have to escape ? + * | if they are found in the sentence-final punctuation
        reStr = re.sub(r'([+?|*])', r'\\\1', sentPunct)
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
            errorList.append((_translate("ExtractBilingualLexicon", "There is a problem with the Bilingual Dictionary Replacement File: {replFile}. Please check the configuration file setting.").format(replFile=Utils.shortenPathForDisplay(replFile)), 2))

        if replTree is not None:
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
            errorList.append((_translate("ExtractBilingualLexicon", "There was a problem creating the Bilingual Dictionary Output File: {fullPathBilingFile}. Please check the configuration file setting.").format(fullPathBilingFile=Utils.shortenPathForDisplay(fullPathBilingFile)), 2))

            if TargetDB is not DB:

                TargetDB.CloseProject()

            return errorList

        errorList.append((_translate("ExtractBilingualLexicon", "Creation complete to the file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(fullPathBilingFile)), 0))
        errorList.append((_translate("ExtractBilingualLexicon", "{recordsDumpedCount} records created.").format(recordsDumpedCount=recordsDumpedCount), 0))

    # In One project mode TargetDB is the same object as DB, so don't close it here (the caller still needs the source project).
    if TargetDB is not DB:

        TargetDB.CloseProject()

    return errorList

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + ['ExtractBilingualLexicon'], 
                           translators, loadBase=True)

    # Read the configuration file
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
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
