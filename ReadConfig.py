#
#   ReadConfig
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.11.1 - 6/29/24 - Ron Lockwood
#    Support text in/out.
#
#   Version 3.11 - 6/21/24 - Ron Lockwood
#    Use Setting for location and name of the Rule Assistant rules file.
#
#   Version 3.10.2 - 3/20/24 - Ron Lockwood
#    Fixes #572. Allow user to ignore unanalyzed proper nouns.
#
#   Version 3.10.1 - 3/2/24 - Ron Lockwood
#    Fixes #561. Handle commas in settings values that aren't lists. Do this by having a 
#    list of properties that must take a list.
#
#   Version 3.10 - 2/29/24 - Ron Lockwood
#    Fixes #571. Setting to determine if filter by all fields is checked.
#
#   Version 3.9.2 - 7/19/23 - Ron Lockwood
#    Fixes #465. Ignore blank lines. Also, just warn and continue if no = or multiple =s.
#
#   Version 3.9.1 - 6/20/23 - Ron Lockwood
#    Removed LOOKUP/lookup from constants to match SettingsGUI.
#
#   Version 3.9 - 6/2/23 - Ron Lockwood
#    Fixes #443. Synthesis test settings added. 
#
#   Version 3.8.1 - 4/8/23 - Ron Lockwood
#    Use WORK_DIR in paths.
#
#   Version 3.8 - 4/4/23 - Ron Lockwood
#    Support HermitCrab Synthesis.
#
#   Version 3.7.2 - 1/30/23 - Ron Lockwood
#    Official support for creating a vocabulary list of unlinked senses. The tool creates an html file
#    with a table containing source headword, gloss and category plus blank cells for the target
#    language and a comment. Also below this info. is the sentence where the sense was found with the
#    word marked in bold type. A new setting for ProperNoun abbrev. added.
#
#   Version 3.7.1 - 11/7/22 - Ron Lockwood
#    Treat a setting as a file or folder if it's anywhere in the description.
#    Not just at the end.
#
#   Version 3.7 - 11/5/22 - Ron Lockwood
#    New function writeConfigValue to write one config value change. The rest of
#    the lines don't change.
#
#   Version 3.5.3 - 8/8/22 - Ron Lockwood
#    Don't allow two equals signs in the config file.
#
#   Version 3.5.2 - 7/14/22 - Ron Lockwood
#    New constants for cacheing data, treetran rules file and lexicon folder. Fixes #184
#    Also check for Folder at the end of the setting name and if so return a path.
#
#   Version 3.5.1 - 6/22/22 - Ron Lockwood
#    Error message fix.
#
#   Version 3.5 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.4.3 - 3/17/22 - Ron Lockwood
#    Allow for a user configurable Testbed location. Issue #70.
#
#   Version 3.4.2 - 3/5/22 - Ron Lockwood
#    Use a config file setting for the transfer rules file.
#
#   Version 3.4.1 - 3/3/22 - Ron Lockwood
#    Find the config file one level up, i.e. top the top installed folder.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use defined config file constants for key values
#
#   Version 3.3.1 - 1/27/22 - Ron Lockwood
#    Convert config file values to decomposed Unicode.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Bump version number for FlexTools 3.2
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.1 - 3/7/18 - Ron Lockwood
#    Give an error only if the report object is not None
#
#   Functions for reading a configuration file

import re
import os
import unicodedata

from FTPaths import CONFIG_PATH, WORK_DIR

CONFIG_FILE = 'FlexTrans.config'

ANALYZED_TEXT_FILE = 'AnalyzedTextOutputFile'
ANALYZED_TREETRAN_TEXT_FILE = 'AnalyzedTextTreeTranOutputFile'
BILINGUAL_DICTIONARY_FILE = 'BilingualDictOutputFile'
BILINGUAL_DICT_REPLACEMENT_FILE = 'BilingualDictReplacementFile'
CATEGORY_ABBREV_SUB_LIST = 'CategoryAbbrevSubstitutionList'
CACHE_DATA = 'CacheData'
CLEANUP_UNKNOWN_WORDS = 'CleanUpUnknownTargetWords'
COMPOSED_CHARACTERS = 'UseComposedCharacters'
HERMIT_CRAB_CONFIG_FILE = 'HermitCrabConfigFile'
HERMIT_CRAB_PARSES_FILE = 'HermitCrabParsesFile'
HERMIT_CRAB_MASTER_FILE = 'HermitCrabMasterFile'
HERMIT_CRAB_SURFACE_FORMS_FILE = 'HermitCrabSurfaceFormsFile'
HERMIT_CRAB_SYNTHESIS = 'HermitCrabSynthesis'
LINKER_SEARCH_ANYTHING_BY_DEFAULT = 'LinkerSearchAnythingByDefault'
NO_PROPER_NOUN_WARNING = 'NoWarningForUnanalyzedProperNouns'
PROPER_NOUN_CATEGORY = 'ProperNounCategory'
SENTENCE_PUNCTUATION = 'SentencePunctuation'
SOURCE_COMPLEX_TYPES = 'SourceComplexTypes'
SOURCE_CUSTOM_FIELD_ENTRY = 'SourceCustomFieldForEntryLink'
SOURCE_CUSTOM_FIELD_SENSE_NUM = 'SourceCustomFieldForSenseNum'
SOURCE_DISCONTIG_TYPES = 'SourceDiscontigousComplexTypes'
SOURCE_DISCONTIG_SKIPPED = 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'
SOURCE_MORPHNAMES = 'SourceMorphNamesCountedAsRoots'
SOURCE_TEXT_NAME = 'SourceTextName'
REBUILD_BILING_LEX_BY_DEFAULT = 'RebuildBilingualLexiconByDefaultInSenseLinker'
RULE_ASSISTANT_FILE = 'RuleAssistantRulesFile'
SYNTHESIS_TEST_LIMIT_POS = 'SynthesisTestLimitPOS'
SYNTHESIS_TEST_LIMIT_STEM_COUNT = 'SynthesisTestLimitStemCount'
SYNTHESIS_TEST_LIMIT_LEXEME = 'SynthesisTestLimitLexeme'
SYNTHESIS_TEST_PARSES_OUTPUT_FILE = 'SynthesisTestParsesOutputFile'
SYNTHESIS_TEST_SIGMORPHON_OUTPUT_FILE = 'SynthesisTestSigmorphonOutputFile'
SYNTHESIS_TEST_LOG_FILE = 'SynthesisTestLogFile'
TARGET_AFFIX_GLOSS_FILE = 'TargetAffixGlossListFile'
TARGET_ANA_FILE = 'TargetOutputANAFile'
TARGET_FORMS_INFLECTION_1ST = 'TargetComplexFormsWithInflectionOn1stElement'
TARGET_FORMS_INFLECTION_2ND = 'TargetComplexFormsWithInflectionOn2ndElement'
TARGET_LEXICON_FILES_FOLDER = 'TargetLexiconFilesFolder'
TARGET_MORPHNAMES = 'TargetMorphNamesCountedAsRoots'
TARGET_PROJECT = 'TargetProject'
TARGET_SYNTHESIS_FILE = 'TargetOutputSynthesisFile'
TESTBED_FILE = 'TestbedFile'
TESTBED_RESULTS_FILE = 'TestbedResultsFile'
TEXT_OUT_RULES_FILE = 'TextOutRulesFile'
TEXT_IN_RULES_FILE = 'TextInRulesFile'
TRANSFER_RESULTS_FILE = 'TargetTranferResultsFile'
TRANSFER_RULES_FILE = 'TransferRulesFile'
TRANSFER_RULES_FILE2 = 'TransferRulesFile2'
TRANSFER_RULES_FILE3 = 'TransferRulesFile3'
TREETRAN_INSERT_WORDS_FILE = 'TreeTranInsertWordsFile'
TREETRAN_RULES_FILE = 'TreeTranRulesFile'

##### IMPORTANT #####
# If you are adding a new property that will have multiple values, add it to this list variable
PROPERTIES_THAT_ARE_LISTS = [SOURCE_MORPHNAMES,
                             TARGET_MORPHNAMES,
                             SOURCE_COMPLEX_TYPES,
                             SOURCE_DISCONTIG_TYPES,
                             SOURCE_DISCONTIG_SKIPPED,
                             TARGET_FORMS_INFLECTION_1ST,
                             TARGET_FORMS_INFLECTION_2ND,
                             SYNTHESIS_TEST_LIMIT_POS,
                             CATEGORY_ABBREV_SUB_LIST]

def openConfigFile(report, info):
    
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), CONFIG_FILE)
        
        return open(myPath, info, encoding='utf-8')
    
    except:
        if report is not None:
            
            report.Error('Error reading the file: "' + CONFIG_PATH+ '/' + CONFIG_FILE + '". Check that it exists.')
            
        return None

def writeConfigValue(report, settingName, settingValue):
    
    f_handle = openConfigFile(report, 'r')
    
    if f_handle is None:
        return False

    myLines = f_handle.readlines()
    f_handle.close()
    
    f_outHandle = openConfigFile(report, 'w')
    
    found = False
    
    for line in myLines:

        # If we find a match at the beg. of the line, change the setting
        if re.match(settingName, line):
            
            f_outHandle.write(f'{settingName}={settingValue}\n')
            found = True
        else:
            f_outHandle.write(line)
    
    f_outHandle.close()
    
    if not found:
        
        if report is not None:
            
            report.Error(f'Setting: {settingName} not found in the configuration file.')
        
        return False
            
    return True
    
def readConfig(report):
    
    f_handle = openConfigFile(report, 'r')
    
    if f_handle is None:
        return 
    
    my_map = {}
    for line in f_handle:
        
        # decompose any composed characters. FLEx stores strings this way.
        line = unicodedata.normalize('NFD', line)

        # Skip malformed or blank lines
        if len(line) < 4:
            continue

        # Skip commented lines
        if line[0] == '#':
            continue

        # We expect lines in the form -- property=value
        if not re.search('=', line):

            if report is not None:
                report.Warning('Problem reading the file: "' + CONFIG_FILE + '". A line without "=" was found.')
            continue
        
        try:
            (prop, value) = line.split('=')
        except:
            if report is not None:
                report.Warning('Problem reading the file: "' + CONFIG_FILE + '". A line without more than one "=" was found.')
            continue
        
        value = value.rstrip()
        
        # if the value has commas and it is in the set of properties that can have multiple values, save it as a list
        if re.search(',', value) and prop in PROPERTIES_THAT_ARE_LISTS:
            my_list = value.split(',')
            my_map[prop] = my_list
        else:
            my_map[prop] = value

    return my_map

def getConfigVal(my_map, key, report, giveError=True):
    if key not in my_map:
        if report is not None:
            if giveError:
                report.Error('Error in the file: "' + CONFIG_FILE + '". A value for "'+key+'" was not found.')
        return None
    else:
        # If the key value has the word 'File' or 'Folder then change the path accordingly.
        # Also the key must have a value, otherwise ignore it.
        if (re.search('File', key) or re.search('Folder', key)) and key in my_map and my_map[key]:
            
            # if we don't have an absolute path (e.g. c:\...) we need to fix up the path. FLExTrans is shipped with relative paths to the work project subfolder ('e.g. German-Swedish')
            if not re.search(':', my_map[key]):
                
                # Return the parent folder of the Config folder + the relative file path.
                # E.g. the resulting path would be something like ...\German-Swedish\Build\target_text.txt
                return os.path.join(WORK_DIR, my_map[key])
      
        return my_map[key]

def configValIsList(my_map, key, report):
    if isinstance(my_map[key], list) is False:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". The value for "'+key+'" is supposed to be a comma separated list. For a single value, end it with a comma.')
        return False
    else:
        return True