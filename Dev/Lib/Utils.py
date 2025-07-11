#
#   Utils
#
#   Ron Lockwood
#   SIL International
#   7/23/2014
#
#   Version 3.14.1 - 7/11/25 - Ron Lockwood
#    Use the new UI Language flextools ini file setting.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.6 - 4/3/25 - Ron Lockwood
#    Replaced magic strings with constants.
#
#   Version 3.13.5 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13.4 - 3/22/25 - Ron Lockwood
#    Fixes #946. We want the contents of all of \w to be vernacular.
#    But we also want \fig with | symbols to be handled correctly. For \fig we want the text
#    without an attribute like xyz= to be vernacular, but the others to be analysis. Also make
#    the | be analysis.
#
#   Version 3.13.3 - 3/19/25 - Ron Lockwood
#    New function to get shorter path including and below WorkProjects.
#    Also don't report which target database.
#
#   Version 3.13.2 - 3/18/25 - Ron Lockwood
#    Fixes #939. Bug in get All Stem Features where wrong object referenced.
#
#   Version 3.13.1 - 3/10/25 - Ron Lockwood
#    Fixes #928. Look for newlines between | and * when splitting what will be analysis WS text.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.18 - 3/3/25 - Ron Lockwood
#    Fixes #915. More checks for invalid chars in lemmas or affixes.
#
#   Version 3.12.17 - 3/2/25 - Ron Lockwood
#    Fixes #914. Set the morphtype to be from the analysis writing system instead of English.
#    This is needed now that we let non-English morphtype names be used in the settings.
#
#   Version 3.12.16 - 2/21/25 - Ron Lockwood
#    Fixes #907. Fix places where FLEx puts a newline between the \ and sfm chars so that
#    inserting into the target text will come out with the \ on the next line.
#
#   Version 3.12.15 - 2/17/25 - Ron Lockwood
#    Better handling of angle brackets. Improved escaping reserved Apertium characters
#    by making sure the character is not already escaped. This avoids double-escaping.
#
#   Version 3.12.14 - 2/12/25 - Ron Lockwood
#    Fixes #888. Show better error when there is a Fatal error from HermitCrab tools in the LRT.
#
#   Version 3.12.13 - 2/11/25 - Ron Lockwood
#    Fixes #649. Better error message when the rules file is invalid.
#
#   Version 3.12.12 - 2/4/25 - Ron Lockwood
#    Fixes #876. Split a text to insert into FLEx also on newlines so that paragraphs get divided properly.
#
#   Version 3.12.11 - 1/23/25 - Ron Lockwood
#    Support import of Glossary book (GLO).
#
#   Version 3.12.10 - 1/18/25 - Ron Lockwood
#    Escape angle brackets.
#
#   Version 3.12.9 - 1/15/25 - Ron Lockwood
#    Reversal morpheme map added.
#
#   Version 3.12.8 - 1/6/25 - Ron Lockwood
#    Clean up more Rule Assistant files.
#
#   Version 3.12.7 - 1/2/25 - Ron Lockwood
#    Fixes problem with HC synthesis where title-cased phrases were not coming out in the write case.
#
#   Version 3.12.6 - 12/30/24 - Ron Lockwood
#   Fixes #742. Set the IsTranslated and Source metadata fields for the new text.
#
#   Version 3.12.5 - 12/30/24 - Ron Lockwood
#    Handle missing project.
#
#   Version 3.12.4 - 12/17/24 - Ron Lockwood
#    New function to open any project.
#
#   Version 3.12.3 - 12/4/24 - Ron Lockwood
#    Fixes #823. Use the same logic that's in the Import from Ptx module to mark sfms as analysis writing system.
#
#   Version 3.12.2 - 12/3/24 - Ron Lockwood
#    Fixes #821. Don't escape < and > in literal strings. Right now we don't allow them in lemmas anyway
#    and this messes up rules that are looking for literal strings starting with <xyz, i.e. a tag.
#
#   Version 3.12.1 - 11/2/24 - Ron Lockwood
#    Fixes #802. Only escape reserved chars in a literal string that's a child of test.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.5 - 10/26/24 - Ron Lockwood
#    Fixes #775. Give an error for invalid characters.
#
#   Version 3.11.4 - 10/16/24 - Ron Lockwood
#    When splitting compounds, separate out the lexical unit from punctuation.
#
#   Version 3.11.3 - 10/12/24 - Ron Lockwood
#    Change some warnings to reference source words.
#
#   Version 3.11.2 - 9/5/24 - Ron Lockwood
#    Escape Apertium lemmas when writing the data stream to a file.
#    Unescape Apertium lemmas when coming from a file for user display.
#
#   Version 3.11.4 - 9/4/24 - Ron Lockwood
#    Add * to APERT_RESERVED and remove unneeded lemmaProbData stuff. Escape reserved characters
#    when getting the lemma.
#
#   Version 3.11.3 - 8/15/24 - Ron Lockwood
#    Support FLEx Alpha 9.2.2 which no longer supports Get Instance, use Get Service instead.
#
#   Version 3.11.2 - 8/15/24 - Ron Lockwood
#    Various changes from DS for the Rule Assistant
#
#   Version 3.11.1 - 5/13/24 - Ron Lockwood
#    Fixed mistake in not matching feature category abbreviation.
#
#   Version 3.11 - 5/13/24 - Ron Lockwood
#    Fixed get affix glosses for feature function to only match for the given category.
#
#   Version 3.10.13 - 4/27/24 - Ron Lockwood
#    Fixed bug when using TreeTran where guid of the root of an inflected word didn't match
#    the TreeTran guid. Fixed the logic in get interlinear to not use the guid of a clitic.
#
#   Version 3.10.12 - 4/15/24 - Ron Lockwood
#    Fixed bug of casting to ILexEntry when it should be ILexSense for variants of a sense.
#
#   Version 3.10.11 - 3/20/24 - Ron Lockwood
#    Refactoring to put changes to allow get interlinear parameter changes to all be in Utils
#
#   Version 3.10.10 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10.9 - 3/6/24 - Ron Lockwood
#    Fixes #579. Re-write how to handle punctuation in the get interlinear function.
#
#   Version 3.10.8 - 3/6/24 - Ron Lockwood
#    Fixes #581. Skip reporting a bad url link if the report object is None.
#
#   Version 3.10.7 - 3/5/24 - Ron Lockwood
#    Fixes #580. Correctly form the circumfix affix for HermitCrab.
#
#   Version 3.10.6 - 2/26/24 - Ron Lockwood
#    Fixes #565. Add inflection features/classes to the source side of the bilingual lexicon.
#    Default to collecting inflection classes for both source and target DBs.
#
#   Version 3.10.5 - 1/25/24 - Ron Lockwood
#    Prevent initial new line.
#
#   Version 3.10.4 - 1/25/24 - Ron Lockwood
#    Fixes #558. Don't add lemma when POS is missing, just give warning.
#
#   Version 3.10.3 - 1/24/24 - Ron Lockwood
#    Fixes #510. Catch an error where the string 'guid' is not present in the link field.
#
#   Version 3.10.2 - 1/1/24 - Ron Lockwood
#    Fixes #503. Fix error message to mention abbrev. or name.
#
#   Version 3.10.1 - 1/1/24 - Ron Lockwood
#    Fixes #506. Better handling of 'punctuation' text that is a complete paragraph (line).
#
#   Version 3.10 - 1/6/24 - Ron Lockwood
#    Output the target DB name in the sense link text.
#
#   Version 3.10.2 - 1/12/24 - Ron Lockwood
#    Fixes #538. Escape brackets in the pre or post punctuation.
#
#   Version 3.9.9 - 12/9/23 - Ron Lockwood
#    Fixes #522. Put out ERR for feature name and value if the corresponding objects are None.
#
#   Version 3.9.9 - 9/11/23 - Ron Lockwood
#    Two functions added to support creating apertium rules.
#
#   Version 3.9.8 - 8/18/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.7 - 8/17/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.6 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.5 - 7/21/23 - Ron Lockwood
#    Fixed error message when target project fails to open.
#
#   Version 3.9.4 - 7/19/23 - Ron Lockwood
#    Fixes #469. Don't show guid to the user on errors.
#
#   Version 3.9.3 - 7/17/23 - Ron Lockwood
#    Fixes #470. Re-write entry urls as sense urls when loading the sense linker.
#    Also clear the sense num field for such entries.
#
#   Version 3.9.2 - 7/17/23 - Ron Lockwood
#    Fixes #66. Use human-readable hyperlinks in the target equivalent custom field.
#
#   Version 3.9.1 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.8.4 - 5/3/23 - Ron Lockwood
#    When extracting the interlinear info., instead of checking if one punctuation symbol of
#    a cluster is in the list of sentence-ending punctuation, require all of the cluster to be
#    in the list before we consider it a <sent> block. Otherwise consider the whole cluster to be
#    non-sentence ending punctuation. This might create issues in places where we are looking for
#    sentence breaks in the transfer rules. This fix was for places where a footnote ended right
#    before a period, so we got \f*. The *. was a cluster that was being allowed to be sentence
#    punctuation, but this caused problems elsewhere (convert to ana I think) where * wasn't recognized.
#    Also fixed was adding saved pre punctuation when the next word is sentence punctuation. Before
#    this fix, some punctuation was being lost.
#
#   Version 3.8.3 - 4/21/23 - Ron Lockwood
#    Fixes #417. Stripped whitespace from source text name. Consolidated code that
#    collects all the interlinear text names.
#
#   Version 3.8.2 - 4/20/23 - Ron Lockwood
#    Reworked import statements. Fixed duplicate processErrorList.
#
#   Version 3.8.1 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.12 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   Version 3.7.11 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.10 - 1/30/23 - Ron Lockwood
#    New function to determine if a string has RTL characters.
#
#   Version 3.7.9 - 1/5/23 - Ron Lockwood
#    Support fixes to issue 229 by adding a parameter to check_for_cat_errors.
#
#   earlier version history removed on 1/15/25
#
#   Shared functions

import re
import tempfile
import os
import unicodedata
import itertools
from collections import defaultdict

from PyQt5.QtCore import QCoreApplication, QTranslator, QLibraryInfo, QLocale

from System import Guid   # type: ignore
from System import String # type: ignore

from SIL.LCModel import ( # type: ignore
    ICmObjectRepository,
    ILexEntry,
    ILexSense,
    ITextRepository,
    IMoStemMsa,
    IFsFeatStruc,
    IFsComplexFeature,
    IFsComplexValue,
    IFsClosedValue,
    IFsClosedFeatureRepository,
    IStStyleRepository,
    ILexEntryInflType,
    IMoInflAffMsa,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore
from SIL.LCModel.Core.Text import TsStringUtils         # type: ignore
from SIL.LCModel.DomainServices import StringServices   # type: ignore

from flexlibs import FLExProject, AllProjectNames
from flextoolslib import FTConfig

import ReadConfig as MyReadConfig
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate

CIRCUMFIX_TAG_A = '_cfx_part_a'
CIRCUMFIX_TAG_B = '_cfx_part_b'
# reserved characters listed at here:
# https://wiki.apertium.org/wiki/Apertium_stream_format
# But +, ~, # don't affect the behavior of lt-proc or apertium-transfer
# { and } need to be escaped if we're using apertium-interchunk
# Don't list backslash here, it is handled in the functions that use the
# reserved character list
APERT_RESERVED = r'\[\]@/^${}<>*'
INVALID_LEMMA_CHARS = r'([\^$><{}])'
RAW_INVALID_LEMMA_CHARS = INVALID_LEMMA_CHARS[3:-2]
NONE_HEADWORD = '**none**'
MO_STEM_MSA = 'MoStemMsa'
MO_STEM_ALLOMORPH = 'MoStemAllomorph'
MO_INFL_AFF_MSA = 'MoInflAffMsa'
FS_COMPLEX_FEATURE = 'FsComplexFeature'
FS_CLOSED_FEATURE = 'FsClosedFeature'
LEX_ENTRY = 'LexEntry'
LEX_SENSE = 'LexSense'
LEX_ENTRY_INFL_TYPE = 'LexEntryInflType'
STYLE_HYPERLINK = 'Hyperlink'
STYLE_NOT_SET = 'NotSet'

CONVERSION_TO_STAMP_CACHE_FILE = 'conversion_to_STAMP_cache2.txt'
TESTBED_CACHE_FILE = 'testbed_cache.txt'
STRIPPED_RULES = 'tr.t1x'

## For TreeTran
GOOD_PARSES_LOG = 'good_parses.log'

ID_STR = 'id'

# File and folder names
OUTPUT_FOLDER = 'Output'
BUILD_FOLDER = 'Build'

RA_GUI_INPUT_FILE = 'ruleAssistantGUIinput.xml'
RULE_ASSISTANT_SOURCE_TEST_DATA_FILE = 'RuleAssistantSourceTestData.txt'
RULE_ASSISTANT_TARGET_TEST_DATA_FILE = 'RuleAssistantTargetTestData.txt'
RULE_ASSISTANT_DISPLAY_DATA_FILE = 'RuleAssistantDisplayData.html'

# Style used for hyperlink style
globalStyle = STYLE_NOT_SET

# precompiled reguglar expressions
reDataStream = re.compile('(>[^$<])')
reObjAddOne = re.compile(r'\d$', flags=re.RegexFlag.A) # ASCII-only match
reTestID = re.compile('test id=".+?"')
reSpace = re.compile(r'\s')
rePeriod = re.compile(r'\.')
reHyphen = re.compile(r'-')
reAsterisk = re.compile(r'\*')
reApertReserved = re.compile(rf'(?<!\\)([{APERT_RESERVED}])') # Use a negative lookbehind assertion to assure the letter is not already escaped
reApertReservedEscaped = re.compile(rf'\\([{APERT_RESERVED}\\])')
reBetweenCaretAndFirstAngleBracket = re.compile(r'(\^)(.*?)(?<!\\)(<)') # Use a negative lookbehind assertion to assure the < is not already escaped
reInvalidLemmaChars = re.compile(INVALID_LEMMA_CHARS)
reFindSymbols = re.compile(r'(?<!\\)(?:<([^<>]+)>)')

morphTypeMap = {
"d7f713e4-e8cf-11d3-9764-00c04f186933": "bound root",
"d7f713e7-e8cf-11d3-9764-00c04f186933": "bound stem",
"d7f713df-e8cf-11d3-9764-00c04f186933": "circumfix",
"c2d140e5-7ca9-41f4-a69a-22fc7049dd2c": "clitic",
"0cc8c35a-cee9-434d-be58-5d29130fba5b": "discontiguous phrase",
"d7f713e1-e8cf-11d3-9764-00c04f186933": "enclitic",
"d7f713da-e8cf-11d3-9764-00c04f186933": "infix",
"18d9b1c3-b5b6-4c07-b92c-2fe1d2281bd4": "infixing interfix",
"56db04bf-3d58-44cc-b292-4c8aa68538f4": "particle",
"a23b6faa-1052-4f4d-984b-4b338bdaf95f": "phrase",
"d7f713db-e8cf-11d3-9764-00c04f186933": "prefix",
"af6537b0-7175-4387-ba6a-36547d37fb13": "prefixing interfix",
"d7f713e2-e8cf-11d3-9764-00c04f186933": "proclitic",
"d7f713e5-e8cf-11d3-9764-00c04f186933": "root",
"d7f713e8-e8cf-11d3-9764-00c04f186933": "stem",
"d7f713dd-e8cf-11d3-9764-00c04f186933": "suffix",
"3433683d-08a9-4bae-ae53-2a7798f64068": "suffixing interfix"}

morphTypeReverseMap = {
"bound root"           : "d7f713e4-e8cf-11d3-9764-00c04f186933",                   
"bound stem"           : "d7f713e7-e8cf-11d3-9764-00c04f186933",      
"circumfix"            : "d7f713df-e8cf-11d3-9764-00c04f186933",     
"clitic"               : "c2d140e5-7ca9-41f4-a69a-22fc7049dd2c",  
"discontiguous phrase" : "0cc8c35a-cee9-434d-be58-5d29130fba5b",                
"enclitic"             : "d7f713e1-e8cf-11d3-9764-00c04f186933",    
"infix"                : "d7f713da-e8cf-11d3-9764-00c04f186933", 
"infixing interfix"    : "18d9b1c3-b5b6-4c07-b92c-2fe1d2281bd4",             
"particle"             : "56db04bf-3d58-44cc-b292-4c8aa68538f4",    
"phrase"               : "a23b6faa-1052-4f4d-984b-4b338bdaf95f",  
"prefix"               : "d7f713db-e8cf-11d3-9764-00c04f186933",  
"prefixing interfix"   : "af6537b0-7175-4387-ba6a-36547d37fb13",              
"proclitic"            : "d7f713e2-e8cf-11d3-9764-00c04f186933",     
"root"                 : "d7f713e5-e8cf-11d3-9764-00c04f186933",
"stem"                 : "d7f713e8-e8cf-11d3-9764-00c04f186933",
"suffix"               : "d7f713dd-e8cf-11d3-9764-00c04f186933",  
"suffixing interfix"   : "3433683d-08a9-4bae-ae53-2a7798f64068"}              


# Invalid category characters & descriptions & messages & replacements
catProbData = [[_translate("Utils", 'space'), _translate("Utils", 'converted to an underscore'), '_', reSpace],
           [_translate("Utils", 'period'), _translate("Utils", 'removed'), '', rePeriod],
#          ['x char', 'fatal', '']
          ]

def convertProblemChars(convertStr, problemDataList):

    # Convert spaces to underscores and remove periods and convert slash to bar, etc.
    for probDataRow in problemDataList:

        # 3 = the compiled RE, 2 = the string to replace with
        convertStr = probDataRow[3].sub(probDataRow[2], convertStr)

    return convertStr

def isClitic(myEntry):

    return isProclitic(myEntry) or isEnclitic(myEntry)

def isProclitic(entry):

    ret_val = False

    # What might be passed in for a component could be a sense which isn't a clitic
    if entry.ClassName == LEX_ENTRY:

        entry = ILexEntry(entry)

        if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:

            morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
            affixGuidStr = morphTypeReverseMap['proclitic']
            
            if morphGuidStr == affixGuidStr:

                ret_val = True

    return ret_val

def isEnclitic(entry):

    ret_val = False

    # What might be passed in for a component could be a sense which isn't a clitic
    if entry.ClassName == LEX_ENTRY:

        entry = ILexEntry(entry)

        if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:

            morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
            affixGuidStr = morphTypeReverseMap['enclitic']
            
            if morphGuidStr == affixGuidStr:

                ret_val = True

    return ret_val

# Create a unique text title for FLEx
def createUniqueTitle(DB, title):

    # Create a list of source text names
    sourceTextList = getSourceTextList(DB)

    if title in sourceTextList:

        title += _translate("Utils", ' - Copy')

        if title in sourceTextList:

            done = False
            i = 2

            while not done:

                tryName = title + ' (' + str(i) + ')'

                if tryName not in sourceTextList:

                    title = tryName
                    done = True

                i += 1
    return title

def removeTestID(inStr):

    return reTestID.sub('', inStr)

def decompose(myFile):

    try:
        # Open the file and read all the lines
        f = open(myFile , "r", encoding='utf-8')
    except:
        raise ValueError(_translate("Utils", "Could not open the file {myFile} when converting to NFD.").format(myFile=myFile))

    lines = f.readlines()
    f.close()

    f = open(myFile ,"w", encoding='utf-8')

    # Go through the existing rule file and write everything to the new file except Doctype stuff.
    for line in lines:

        # Always convert lines to decomposed unicode
        f.write(unicodedata.normalize('NFD', line))
    f.close()

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
    if not reObjAddOne.search(headWord):
        return (headWord + '1')
    return headWord

def as_string(obj):
    return ITsString(obj.BestAnalysisAlternative).Text

def as_vern_string(obj):
    return ITsString(obj.BestVernacularAlternative).Text

def as_tag(obj):
    return underscores(as_string(obj.Abbreviation))

def get_feat_abbr_list(SpecsOC, feat_abbr_list):

    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            spec = IFsComplexValue(spec)
            value = IFsFeatStruc(spec.ValueOA)
            get_feat_abbr_list(value.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            spec = IFsClosedValue(spec)

            if spec.FeatureRA:
                featGrpName = as_string(spec.FeatureRA.Name)
            else:
                featGrpName = "ERR"
            if spec.ValueRA:
                abbValue = as_tag(spec.ValueRA)
            else:
                abbValue = "ERR"
            feat_abbr_list.append((featGrpName, abbValue))
    return

def getHeadwordStr(e):
    return ITsString(e.HeadWord).Text

def GetEntryWithSense(e):
    # If the entry is a variant and it has no senses, loop through its references
    # until we get to an entry that has a sense
    notDoneWithVariants = True
    while notDoneWithVariants:
        if e.ClassName == LEX_ENTRY:
            e = ILexEntry(e)
            if e.SensesOS.Count == 0:
                if e.EntryRefsOS:
                    foundVariant = False
                    for entryRef in e.EntryRefsOS:
                        if entryRef.RefType == 0: # we have a variant
                            foundVariant = True
                            break
                    if foundVariant and entryRef.ComponentLexemesRS.Count > 0:
                        # if the variant we found is a variant of sense, we are done. Use the owning entry.
                        if entryRef.ComponentLexemesRS.ToArray()[0].ClassName == LEX_SENSE:
                            e = ILexEntry(entryRef.ComponentLexemesRS.ToArray()[0].Entry)
                            break
                        else: # normal variant of entry
                            e = entryRef.ComponentLexemesRS.ToArray()[0]
                            continue
        notDoneWithVariants = False
    return e

def GetEntryWithSensePlusFeat(e, inflFeatAbbrevs):
    # If the entry is a variant and it has no senses, loop through its references
    # until we get to an entry that has a sense
    notDoneWithVariants = True
    while notDoneWithVariants:
        if e.ClassName == LEX_ENTRY:
            e = ILexEntry(e)
            if e.SensesOS.Count == 0:
                if e.EntryRefsOS:
                    foundVariant = False
                    for entryRef in e.EntryRefsOS:
                        if entryRef.RefType == 0: # we have a variant
                            foundVariant = True

                            # Collect any inflection features that are assigned to the special
                            # variant types called Irregularly Inflected Form
                            for varType in entryRef.VariantEntryTypesRS:
                                if varType.ClassName == LEX_ENTRY_INFL_TYPE:
                                    varType = ILexEntryInflType(varType)
                                    if  varType.InflFeatsOA:
                                        my_feat_abbr_list = []
                                        # The features might be complex, make a recursive function call to find all features
                                        get_feat_abbr_list(varType.InflFeatsOA.FeatureSpecsOC, my_feat_abbr_list)
                                        inflFeatAbbrevs.extend(my_feat_abbr_list)
                            break
                    if foundVariant and entryRef.ComponentLexemesRS.Count > 0:
                        # if the variant we found is a variant of sense, we are done. Use the owning entry.
                        if entryRef.ComponentLexemesRS.ToArray()[0].ClassName == LEX_SENSE:
                            mySense = ILexSense(entryRef.ComponentLexemesRS.ToArray()[0])
                            e = mySense.Entry
                            break
                        else: # normal variant of entry
                            e = ILexEntry(entryRef.ComponentLexemesRS.ToArray()[0])
                            continue
        notDoneWithVariants = False
    return e

# Compound words get put within one ^...$ block. Split them into one per word.
def split_compounds(outStr):

    # Ignore <sent> lexical units
    if re.search(r'<sent>', outStr):

        return outStr
    
    # TODO: this function sometimes get called with multiple LUs. Right now it doesn't remove punctuation from all places between punctuation.
    # TODO: This needs to be done because punctuation could have > chars in it.
    # TODO: In fact, this probably won't handle ^ or $ in the punctuation. Probably need to look for unescaped ^ and $. Maybe ([^\\]*?^)([^\\]*?)(\$.*) would work.
    # Get the lexical unit and before and after punctuation
    match = re.match(r'(.*?\^)(.*?)(\$.*)', outStr, re.DOTALL)

    if match:

        beforePunc = match.group(1)
        middle = match.group(2)
        afterPunc = match.group(3)
    else:
        return outStr

    # Split into tokens where we have a > followed by a character other than $ or < (basically a lexeme)
    # this makes ^room1.1<n>service1.1<n>number1.1<n>$ into ['^room1.1<n', '>s', 'ervice1.1<n', '>n', 'umber1.1<n>$']
    toks = reDataStream.split(middle)

    # If there is only one token returned from the split, we don't have multiple words just
    # return the input string
    if len(toks) > 1:
        middle = ''

        # Every odd token will be the delimeter that was matched in the split operation
        # Insert $^ between the > and letter of the 2-char delimeter.
        for i,tok in enumerate(toks):
            # if we have an odd numbered index
            if i&1:
                tok = tok[0]+"$^"+tok[1]
            middle+=tok

    return f'{beforePunc}{middle}{afterPunc}'

# Convert . (dot) to _ (underscore)
def underscores(inStr):
    return re.sub(r'\.', r'_', inStr)

def openProject(report, DBname):

    myDB = FLExProject()

    try:
        myDB.OpenProject(DBname, True)
    except: #FDA_DatabaseError, e:
        if report:
            report.Error(_translate("Utils", "There was an error opening project: {DBname}. Perhaps the project is open and the sharing option under FieldWorks Project Properties has not been clicked.").format(DBname=DBname))
        return None

    return myDB

def openTargetProject(configMap, report):

    TargetDB = FLExProject()

    # Open the target database
    targetProj = MyReadConfig.getConfigVal(configMap, MyReadConfig.TARGET_PROJECT, report)
    if not targetProj:
        return

    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():
        if report:
            report.Error(_translate("Utils", "The target project does not exist. Please check the configuration file."))
        return
    
    try:
        TargetDB.OpenProject(targetProj, True)
    except:
        if report:
            report.Error(_translate("Utils", "There was an error opening target project: {targetProj}. Perhaps the project is open and the sharing option under FieldWorks Project Properties has not been clicked.").format(targetProj=targetProj))
        raise

    return TargetDB

# This is a recursive function to get all inflection subclasses
def get_sub_inflection_classes(mySubClasses):

    ic_list = []

    for ic in mySubClasses:

        icAbbr = as_string(ic.Abbreviation)
        icName = as_string(ic.Name)

        ic_list.append((icAbbr,icName))

        if ic.SubclassesOC and len(ic.SubclassesOC.ToArray()) > 0:

            icl = get_sub_inflection_classes(ic.SubclassesOC)
            ic_list.extend(icl)

    return ic_list

def get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=True):

    haveError = False
    dbList = [(DB, _translate("Utils", 'source'))]

    # Sometime the caller may just want source categories
    if TargetDB:

        dbList.append((TargetDB, _translate("Utils", 'target')))

    for dbTup in dbList:

        dbObj = dbTup[0]
        dbType = dbTup[1]

        # initialize a list of error counters to 0
        countList = [0]*len(catProbData)

        # loop through all database categories
        for pos in dbObj.lp.AllPartsOfSpeech:

            # save abbreviation and full name
            posAbbrStr = as_string(pos.Abbreviation)
            posFullNameStr = pos.ToString()

            # check for errors or warnings, pass in the error counter list which may have been incremented
            countList, posAbbrStr = check_for_cat_errors(report, dbType, posFullNameStr, posAbbrStr, countList, numCatErrorsToShow)

            # add a (possibly changed abbreviation string) to the map
            add_to_cat_map(posMap, posFullNameStr, posAbbrStr)

            # add inflection classes to the map if there are any.
            if addInflectionClasses:

                process_inflection_classes(posMap, pos)

            # check for serious error
            if countList[0] == 999:

                # Note we have the error, but keep going so tha we give all errors at once
                # reset error (warning) counter to zero
                countList[0] = 0
                haveError = True

    if haveError == True:
        return True
    else:
        return False

def add_to_cat_map(posMap, posFullNameStr, posAbbrStr):

    # add the pos category to a map
    if posAbbrStr not in posMap:

        posMap[posAbbrStr] = posFullNameStr
    else:
        # If we already have the abbreviation in the map and the full category name
        # is not the same as the source one, append the target one to the source one
        if posMap[posAbbrStr] != posFullNameStr:

            posMap[posAbbrStr] += ' / ' + posFullNameStr

def process_inflection_classes(posMap, pos):

    if pos.InflectionClassesOC and len(pos.InflectionClassesOC.ToArray()) > 0:

        # Get a list of abbreviation and name tuples
        AN_list = get_sub_inflection_classes(pos.InflectionClassesOC)

        for icAbbr, icName in AN_list:

            posMap[icAbbr] = icName

def check_for_cat_errors(report, dbType, posFullNameStr, posAbbrStr, countList, numCatErrorsToShow, myType=_translate("Utils", 'category')):

    haveError = False

    # loop through the possible invalid characters
    for i, outStrings in enumerate(catProbData):

        charName = outStrings[0]
        message = outStrings[1]
        replChar = outStrings[2]
        invalidCharCompiledRE = outStrings[3]

        # give a warning if we find an invalid character
        if invalidCharCompiledRE.search(posAbbrStr):

            # check for a fatal error
            if message == 'fatal':

                if report:
                    report.Error(_translate("Utils", "The abbreviation/name: '{posAbbrStr}' for {myType}: '{posFullNameStr}' can't have a {charName} in it. Could not complete, '+\
                                            'please correct this {myType} in the {dbType} project.").format(posAbbrStr=posAbbrStr, myType=myType, posFullNameStr=posFullNameStr, charName=charName, dbType=dbType))                
                    haveError = True

                # show all fatal errors
                continue

            oldAbbrStr = posAbbrStr

            # do the conversion
            posAbbrStr = invalidCharCompiledRE.sub(replChar, posAbbrStr)

            # If we are under the max errors to show number, give a warning
            if countList[i] < numCatErrorsToShow:

                if report:
                    report.Warning(_translate("Utils", "The abbreviation/name: '{oldAbbrStr}' for {myType}: '{posFullNameStr}' in the {dbType} project can't have a {charName} in it. The {charName} '+\
                                              'has been {message}, forming {posAbbrStr}. Keep this in mind when referring to this {myType} in transfer rules.").
                                              format(oldAbbrStr=oldAbbrStr, myType=myType, posFullNameStr=posFullNameStr, dbType=dbType, charName=charName, message=message, posAbbrStr=posAbbrStr))

            # Give suppressing message when we go 1 beyond the max
            elif countList[i] == numCatErrorsToShow:

                if report:
                    report.Info(_translate("Utils", "Suppressing further warnings of this type."))

            countList[i] += 1

    if haveError:
        countList[0] = 999
        return countList, posAbbrStr

    return countList, posAbbrStr

def getSourceTextList(DB, matchingContentsObjList=None):

    sourceList = []
    for interlinText in DB.ObjectsIn(ITextRepository):

        sourceList.append(as_string(interlinText.Name).strip())

        # if the caller wants to get a list of contents objects, add to the provided list
        if matchingContentsObjList != None:

            matchingContentsObjList.append(interlinText.ContentsOA)

    return sourceList

def loadSourceTextList(widget, sourceText, sourceTextList):

    # Add items and when we find the one that matches the config file. Set that one to be displayed.
    for i, itemStr in enumerate(sorted(sourceTextList, key=str.casefold)):

        widget.addItem(itemStr)

        if itemStr == sourceText:

            widget.setCurrentIndex(i)

def hasRtl(text):

    for char in text:

        if unicodedata.bidirectional(char) in ('R', 'AL'):

            return True

    return False

# Eventually make this function locale sensitive. So if we are using Turkish locale we will do the right thing.
def capitalizeString(inStr, capitalizeCode, useCurrentLocaleRules=False):

    if capitalizeCode == '2':

        return inStr.upper()

    elif capitalizeCode == '1':

        return inStr.capitalize()

    elif capitalizeCode == '3':

        return inStr.title()

    return inStr

def processErrorList(error_list, report):

    fatal = False

    for msg in error_list:

        # See if there is extra info to pass to the error reporter
        if len(msg) > 2:
            infoStr = msg[2]
        else:
            infoStr = ''

        # msg is a pair -- string & code & optional url
        if msg[1] == 0:
            report.Info(msg[0], infoStr)
        elif msg[1] == 1:
            report.Warning(msg[0], infoStr)
        else: # error=2
            report.Error(msg[0], infoStr)
            fatal = True

    return None if fatal else 1

def checkForFatalError(errorList, report):

    fatal = False
    retMsgList = []

    for triplet in errorList:

        msg = triplet[0]

        if triplet[1] == 2:

            fatal = True
            retMsgList.append(msg)

            if report == None:
                continue
            else:
                report.Error(msg)

    return fatal, '\n'.join(retMsgList)

def getTargetSenseInfo(entry, DB, TargetDB, mySense, tgtEquivUrl, senseNumField, report, remove1dot1Bool=False, rewriteEntryLinkAsSense=False, preGuidStr='', senseEquivField=None):

    retVal = (None, None, None)

    senseNumStr = '1'

    # If not sense num custom field, that's ok
    if senseNumField:

        senseNumStr = DB.LexiconGetFieldText(mySense.Hvo, senseNumField)

        # If no sense number, assume it is 1
        if senseNumStr == None or not senseNumStr.isdigit():

            senseNumStr = '1'

    senseNum = int(senseNumStr)

    try:
        # Get the guid from the url
        u = tgtEquivUrl.index('guid')
        guidSubStr = tgtEquivUrl[u+7:u+7+36]

        # Look up the entry in the trgt project by guid
        repo = TargetDB.project.ServiceLocator.GetService(ICmObjectRepository)

        guid = Guid(String(guidSubStr))
        targetObj = repo.GetObject(guid)
    except:
        headWord = getHeadwordStr(entry)
        if report:
            report.Error(_translate("Utils", "Invalid url link or url not found in the target project while processing source headword: {headWord}.").format(headWord=headWord),
            DB.BuildGotoURL(entry))
        return retVal

    if targetObj:

        # See if this guid was for an entry or a sense. The old method was an entry with a given sense num.
        if targetObj.ClassName == LEX_ENTRY:

            targetEntry = ILexEntry(targetObj)

            if senseNum <= len(targetEntry.SensesOS.ToArray()):

                targetSense = targetEntry.SensesOS.ToArray()[senseNum-1]

                # If requested, rewrite entry link as sense link
                if rewriteEntryLinkAsSense:

                    myStyle = getHyperLinkStyle(DB)

                    if myStyle != None: # style 'hyperlink' doesn't exist

                        urlStr = preGuidStr + targetSense.Guid.ToString() + '%26tag%3d'

                        writeSenseHyperLink(DB, TargetDB, mySense, targetEntry, targetSense, senseEquivField, urlStr, myStyle)

                        # If the sense number field is None, we aren't using it
                        if senseNumField:

                            DB.LexiconSetFieldText(mySense, senseNumField, '')
            else:
                targetSense = None
        else:
            targetSense = ILexSense(targetObj)
            targetEntry = targetSense.Entry

            # Find which sense number this is
            for i, mySense in enumerate(targetEntry.SensesOS):

                if mySense == targetSense:
                    break

            senseNum = i+1

        # Make the lemma in the form x.x (but remove if 1.1)
        lem = fixupLemma(targetEntry, senseNum, remove1dot1Bool)

    return (targetSense, lem, senseNum)

def remove1dot1(lem):

    return re.sub('1\.1', '', lem)

def fixupLemma(entry, senseNum, remove1dot1Bool=False):

    lem = getHeadwordStr(entry)
    lem = add_one(lem)
    lem = lem + '.' + str(senseNum) # add sense number

    # If the lemma ends with 1.1, remove it (for optics)
    if remove1dot1Bool:

        return remove1dot1(lem)
    else:
        return lem

def removeLemmaOnePointSomething(lemmaStr):

    # Remove everything following the dot and optionally the 1 if it's there
    # So 2.1 or 2.2 would turn into 2, 3.1 -> 3
    # Basically we want to show the non-1 homograph numbers
    return re.sub(r'1*\..+', '', lemmaStr)

def getTargetEquivalentUrl(DB, senseObj, senseEquivField):

    equivStr = None

    # Get tsString with the custom field contents
    tsEquiv = DB.GetCustomFieldValue(senseObj.Hvo, senseEquivField)

    if tsEquiv.Text:

        # Initialize a builder object
        bldr = TsStringUtils.MakeStrBldr()
        bldr.ReplaceTsString(bldr.Length, bldr.Length, tsEquiv)

        # Get the properties of the string at position 0
        textPropObj = bldr.get_Properties(0)

        # The embedded object property is value 6
        urlStr = textPropObj.GetStrPropValue(6)

        if urlStr:

            # Discard the first character which is the ID
            equivStr = urlStr[1:]
        else:

            # No hyperlink, use the link directly
            # the Text member of the tsString holds the character string
            equivStr = tsEquiv.Text

    return equivStr

def writeSenseHyperLink(DB, TargetDB, sourceSense, targetEntry, targetSense, senseEquivField, urlStr, myStyle):

    # This headword should have a number if there is more than one of them
    headWordStr = getHeadwordStr(targetEntry)

    # Add a fake .1 so we can remove any 1.Xs
    headWordStr = removeLemmaOnePointSomething(headWordStr + '.1')
    glossStr = as_string(targetSense.Gloss)

    # Put the string we want for the link name into a tsString
    linkName = _translate("Utils", "linked to entry: {headWordStr}, sense: {glossStr} in the {projectName} project.").format(headWordStr=headWordStr, glossStr=glossStr, projectName=TargetDB.ProjectName())

    # Make the string in the analysis writing system
    tss = TsStringUtils.MakeString(linkName, DB.project.DefaultAnalWs)

    # We use a builder object to set the hyperlink, initialize it with tss
    bldr = TsStringUtils.MakeStrBldr()
    bldr.ReplaceTsString(bldr.Length, bldr.Length, tss)

    # Set the hyperlink to cover the whole string (0-length), using the above url and 'hyperlink' style
    StringServices.MarkTextInBldrAsHyperlink(bldr, 0, len(linkName), urlStr, myStyle)

    # Extract the changed tsString
    tss = bldr.GetString()

    # Call the set string function directly instead of using the FlexTools function since we need the hyperlink
    # This is a bit riskier, because it bypasses checks, but we assume it's a text field and not a multi WS string
    DB.project.DomainDataByFlid.SetString(sourceSense.Hvo, senseEquivField, tss)

def getHyperLinkStyle(DB):

    if globalStyle == STYLE_NOT_SET:

        # Find the hyperlink style
        for Style in DB.ObjectsIn(IStStyleRepository):

            if Style.Name == STYLE_HYPERLINK:
                break

        # If it wasn't found, set the style to None
        if Style.Name != STYLE_HYPERLINK:
            Style = None
    else:
        Style = globalStyle

    return Style

def getLemmasForFeature(DB, report, configMap, gramCategoryAbbrev, featureCategoryAbbrev):

    myList = [] # [('el1.1','m'),('la1.1','f')]
    sourceMorphNames = MyReadConfig.getConfigVal(configMap, MyReadConfig.SOURCE_MORPHNAMES, report)

    # Loop through all entries/senses and collect lemmas that match get given grammatical category and feature
    for entry_cnt, srcEntry in enumerate(DB.LexiconAllEntries()):

        # Don't process affixes, clitics
        if srcEntry.LexemeFormOA and srcEntry.LexemeFormOA.ClassName == MO_STEM_ALLOMORPH and \
            srcEntry.LexemeFormOA.MorphTypeRA and as_string(srcEntry.LexemeFormOA.MorphTypeRA.Name) in sourceMorphNames:

            if srcEntry.LexemeFormOA.IsAbstract:
                continue

            # Loop through senses
            for i, mySense in enumerate(srcEntry.SensesOS):

                # Make sure we have a valid analysis object
                if mySense.MorphoSyntaxAnalysisRA:

                    # Get the POS abbreviation for the current sense, assuming we have a stem
                    if mySense.MorphoSyntaxAnalysisRA.ClassName == MO_STEM_MSA:

                        msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)

                        if msa.PartOfSpeechRA:

                            abbrev = as_string(msa.PartOfSpeechRA.Abbreviation)

                            if abbrev != gramCategoryAbbrev:
                                break
                            else:
                                # Check for a match on the feature
                                if msa.MsFeaturesOA:

                                    feat_abbr_list = []

                                    # The features might be complex, make a recursive function call to find all leaf features
                                    get_feat_abbr_list(msa.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)

                                    # loop through feature groups and abbreviations
                                    for grpName, abb in feat_abbr_list:

                                        if featureCategoryAbbrev == grpName:

                                            # Get the headword string
                                            headWord = getHeadwordStr(srcEntry)

                                            # If there is not a homograph # at the end, make it 1
                                            headWord = add_one(headWord)
                                            headWord += '.'+str(i+1)

                                            myList.append((headWord, abb))
                                            break
    return myList

def getAffixGlossesForFeature(DB, report, configMap, gramCategoryAbbrev, featureCategoryAbbrev):

    myList = [] #[('MASC_a','m'),('FEM_a','f')]

    # Loop through all the entries
    for entry in DB.LexiconAllEntries():

        # Check that the objects we need are valid
        if not entry.LexemeFormOA:
            continue

        if entry.LexemeFormOA.IsAbstract:
            continue

        if not entry.LexemeFormOA.MorphTypeRA or not entry.LexemeFormOA.MorphTypeRA.Name:
            continue

        if entry.SensesOS.Count > 0: # Entry with senses

            # Loop through senses
            for _, mySense in enumerate(entry.SensesOS):

                # Process only affixes
                if mySense.MorphoSyntaxAnalysisRA and  mySense.MorphoSyntaxAnalysisRA.ClassName == MO_INFL_AFF_MSA:

                    senseMsa = IMoInflAffMsa(mySense.MorphoSyntaxAnalysisRA)

                    # Check if this affix matches the desired grammatical category
                    if senseMsa.PartOfSpeechRA:

                        abbrev = as_string(senseMsa.PartOfSpeechRA.Abbreviation)

                        ok = False
                        if isinstance(gramCategoryAbbrev, str):
                            ok = (abbrev == gramCategoryAbbrev)
                        elif isinstance(gramCategoryAbbrev, set):
                            ok = (abbrev in gramCategoryAbbrev)

                        if not ok:
                            continue
                        else:
                            # Check for a match on the feature
                            if senseMsa.InflFeatsOA:

                                feat_abbr_list = []

                                # The features might be complex, make a recursive function call to find all leaf features
                                get_feat_abbr_list(senseMsa.InflFeatsOA.FeatureSpecsOC, feat_abbr_list)

                                # loop through feature groups and abbreviations
                                for grpName, abb in feat_abbr_list:

                                    if featureCategoryAbbrev == grpName:

                                        gloss = as_string(mySense.Gloss)
                                        myList.append((gloss, abb))
                                        break
    return myList

def getAffixSlotCategories(slot, gramCategoryAbbrev):
    feat_abbr_list = []
    for affix in slot.Affixes:
        abbrev = as_string(affix.PartOfSpeechRA.Abbreviation)
        if abbrev != gramCategoryAbbrev or not affix.InflFeatsOA:
            continue
        get_feat_abbr_list(affix.InflFeatsOA.FeatureSpecsOC, feat_abbr_list)
    return tuple(sorted(set([feat[0] for feat in feat_abbr_list])))

def getAffixTemplates(DB, gramCategoryAbbrev):
    templates = set()
    for pos in DB.lp.AllPartsOfSpeech:
        if gramCategoryAbbrev != as_string(pos.Abbreviation):
            continue
        for template in pos.AffixTemplatesOS:
            slots = []
            for slot in template.PrefixSlotsRS:
                slots.append((getAffixSlotCategories(slot, gramCategoryAbbrev), 'prefix'))
            for slot in template.SuffixSlotsRS:
                slots.append((getAffixSlotCategories(slot, gramCategoryAbbrev), 'suffix'))
            if not slots:
                continue
            cats, types = list(zip(*slots))
            for prod in itertools.product(*cats):
                templates.add(tuple(zip(prod, types)))
    return sorted(templates)

def getStemFeatures(DB, report, configMap, gramCategoryAbbrev):
    features = set()
    sourceMorphNames = MyReadConfig.getConfigVal(configMap, MyReadConfig.SOURCE_MORPHNAMES, report)

    for entry in DB.LexiconAllEntries():
        LF = entry.LexemeFormOA
        if not LF or LF.IsAbstract or LF.ClassName != MO_STEM_ALLOMORPH:
            continue
        if not LF.MorphTypeRA or as_string(LF.LexemeFormOA.MorphTypeRA.Name) not in sourceMorphNames:
            continue

        for sense in entry.SensesOS:
            msara = sense.MorphoSyntaxAnalysisRA
            if not msara or msara.ClassName != MO_STEM_MSA:
                continue
            msa = IMoStemMsa(msara)
            if not msa.PartOfSpeechRA:
                continue
            abbrev = as_string(msa.PartOfSpeechRA.Abbreviation)
            if abbrev != gramCategoryAbbrev:
                continue
            if msa.MsFeaturesOA:
                abbr_list = []
                get_feat_abbr_list(msa.MsFeaturesOA.FeatureSpecsOC, abbr_list)
                features.update([name for name, abb in abbr_list])
    return sorted(features)

def getAllStemFeatures(DB, report, configMap):
    features = defaultdict(set)
    sourceMorphNames = MyReadConfig.getConfigVal(configMap, MyReadConfig.SOURCE_MORPHNAMES, report)

    for entry in DB.LexiconAllEntries():
        LF = entry.LexemeFormOA
        if not LF or LF.IsAbstract or LF.ClassName != MO_STEM_ALLOMORPH:
            continue
        if not LF.MorphTypeRA or as_string(LF.MorphTypeRA.Name) not in sourceMorphNames:
            continue

        for sense in entry.SensesOS:
            msara = sense.MorphoSyntaxAnalysisRA
            if not msara or msara.ClassName != MO_STEM_MSA:
                continue
            msa = IMoStemMsa(msara)
            if not msa.PartOfSpeechRA:
                continue
            abbrev = as_string(msa.PartOfSpeechRA.Abbreviation)
            if msa.MsFeaturesOA:
                abbr_list = []
                get_feat_abbr_list(msa.MsFeaturesOA.FeatureSpecsOC, abbr_list)
                features[abbrev].update([name for name, abb in abbr_list])
    return features

def getAllInflectableFeatures(DB):
    ret = defaultdict(set)
    for pos in DB.lp.AllPartsOfSpeech:
        abbr = as_string(pos.Abbreviation)
        for infl in pos.InflectableFeatsRC:
            # TODO: are there other possibilities?
            if infl.ClassName == FS_COMPLEX_FEATURE:
                for feat in IFsComplexFeature(infl).TypeRA.FeaturesRS:
                    ret[abbr].add(as_string(feat.Name))
            elif infl.ClassName == FS_CLOSED_FEATURE:
                ret[abbr].add(as_string(infl.Name))
    return ret

def getPossibleFeatureValues(DB, featureName):
    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):
        if as_string(feature.Name) == featureName:
            return sorted(as_tag(val) for val in feature.ValuesOC)
    return []

def getCategoryHierarchy(DB):
    SEP = '\ufffc' # Object Replacement Character
    ret = {}
    for pos in DB.lp.AllPartsOfSpeech:
        abbr = as_string(pos.Abbreviation)
        ret[abbr] = pos.AbbrevHierarchyString.split(SEP)
    return ret

def unescapeReservedApertChars(inStr):

    return reApertReservedEscaped.sub(r'\1', inStr)

def escapeReservedApertChars(inStr):
    
    # Escape special characters that are not already escaped
    inStr = reApertReserved.sub(r'\\\1', inStr)

    # Now escape backslashes that are not already escaped and aren't being used to escape a special char
    inStr = re.sub(rf'(?<!\\)\\([^{APERT_RESERVED}\\]|$)', r'\\\\\1', inStr)

    return inStr

def getInflectionTags(MSAobject):
    '''Take a IMoStemMsa object and return a list of tags'''

    symbols = []
    if MSAobject.InflectionClassRA:
        symbols.append(as_tag(MSAobject.InflectionClassRA))

    if MSAobject.MsFeaturesOA:

        featureAbbrList = []

        # The features might be complex, make a recursive function call to find all leaf features
        get_feat_abbr_list(MSAobject.MsFeaturesOA.FeatureSpecsOC, featureAbbrList)

        symbols += [underscores(abb) for grpName, abb in sorted(featureAbbrList)]

    return symbols

def containsInvalidLemmaChars(myStr):

    return True if reInvalidLemmaChars.search(myStr) else False

def getPathRelativeToWorkProjectsDir(fullPath):
    '''Get the path relative to the work projects directory.
       If WorkProjects isn't found in the path, return the full path.'''
    
    # Look for 'WorkProjects' in the path
    index = fullPath.find('WorkProjects')
    if index == -1:
        return fullPath
        
    # Return the path starting from 'WorkProjects'
    return "..."+fullPath[index:]

def loadTranslations(libList, translatorsList, loadBase=False):

    if loadBase:

        # Load the Qt base translation for standard dialogs
        qt_translator = QTranslator()
        qt_translator.load(f"qtbase_{getInterfaceLangCode()}", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        QCoreApplication.installTranslator(qt_translator)
        translatorsList.append(qt_translator) # Keep this instance around to avoid garbage collection and the object being deleted

    # Load translations (libraries, for the windows and this file.)
    for lib in libList:

        translator = QTranslator()

        if translator.load(f"{lib}_{getInterfaceLangCode()}.qm", FTPaths.TRANSL_DIR):

            QCoreApplication.installTranslator(translator)
            translatorsList.append(translator) # Keep this instance around to avoid garbage collection and the object being deleted

class LocalizedDateTimeFormatter:

    def __init__(self):
        self.localeCache = {}
    
    def getLocale(self, langCode):
        """Get QLocale object for language code with caching"""

        if langCode not in self.localeCache:

            localeMap = {
                'de': QLocale(QLocale.German, QLocale.Germany),
                'es': QLocale(QLocale.Spanish, QLocale.Spain),
                'en': QLocale(QLocale.English, QLocale.UnitedStates),
            }
            self.localeCache[langCode] = localeMap.get(langCode, QLocale())
        
        return self.localeCache[langCode]
    
    def formatDateTime(self, datetimeObj, formatType="d MMM yyyy hh:mm:ss"):
        """Format datetime according to language locale"""

        locale = self.getLocale(getInterfaceLangCode())
        return locale.toString(datetimeObj, formatType)
    
def getInterfaceLangCode():

    return FTConfig.UILanguage 
