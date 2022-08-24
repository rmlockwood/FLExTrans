#
#   ReadConfig
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
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

from FTPaths import CONFIG_PATH

CONFIG_FILE = 'FlexTrans.config'

ANALYZED_TEXT_FILE = 'AnalyzedTextOutputFile'
ANALYZED_TREETRAN_TEXT_FILE = 'AnalyzedTextTreeTranOutputFile'
BILINGUAL_DICTIONARY_FILE = 'BilingualDictOutputFile'
BILINGUAL_DICT_REPLACEMENT_FILE = 'BilingualDictReplacementFile'
CATEGORY_ABBREV_SUB_LIST = 'CategoryAbbrevSubstitutionList'
CACHE_DATA = 'CacheData'
CLEANUP_UNKNOWN_WORDS = 'CleanUpUnknownTargetWords'
COMPOSED_CHARACTERS = 'UseComposedCharacters'
SENTENCE_PUNCTUATION = 'SentencePunctuation'
SOURCE_CIRCUMFIXES = 'SourceMorphNamesCountedAsCircumfixes'
SOURCE_COMPLEX_TYPES = 'SourceComplexTypes'
SOURCE_CUSTOM_FIELD_ENTRY = 'SourceCustomFieldForEntryLink'
SOURCE_CUSTOM_FIELD_SENSE_NUM = 'SourceCustomFieldForSenseNum'
SOURCE_DISCONTIG_TYPES = 'SourceDiscontigousComplexTypes'
SOURCE_DISCONTIG_SKIPPED = 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'
SOURCE_INFIXES = 'SourceMorphNamesCountedAsInfixes' 
SOURCE_MORPHNAMES = 'SourceMorphNamesCountedAsRoots'
SOURCE_PREFIXES = 'SourceMorphNamesCountedAsPrefixes' 
SOURCE_SUFFIXES = 'SourceMorphNamesCountedAsSuffixes' 
SOURCE_TEXT_NAME = 'SourceTextName'
TARGET_AFFIX_GLOSS_FILE = 'TargetAffixGlossListFile'
TARGET_ANA_FILE = 'TargetOutputANAFile'
TARGET_CIRCUMFIXES = 'TargetMorphNamesCountedAsCircumfixes'
TARGET_FORMS_INFLECTION_1ST = 'TargetComplexFormsWithInflectionOn1stElement'
TARGET_FORMS_INFLECTION_2ND = 'TargetComplexFormsWithInflectionOn2ndElement'
TARGET_INFIXES = 'TargetMorphNamesCountedAsInfixes' 
TARGET_LEXICON_FILES_FOLDER = 'TargetLexiconFilesFolder'
TARGET_MORPHNAMES = 'TargetMorphNamesCountedAsRoots'
TARGET_PREFIXES = 'TargetMorphNamesCountedAsPrefixes' 
TARGET_SUFFIXES = 'TargetMorphNamesCountedAsSuffixes' 
TARGET_PROJECT = 'TargetProject'
TARGET_SYNTHESIS_FILE = 'TargetOutputSynthesisFile'
TESTBED_FILE = 'TestbedFile'
TESTBED_RESULTS_FILE = 'TestbedResultsFile'
TRANSFER_RESULTS_FILE = 'TargetTranferResultsFile'
TRANSFER_RULES_FILE = 'TransferRulesFile'
TREETRAN_INSERT_WORDS_FILE = 'TreeTranInsertWordsFile'
TREETRAN_RULES_FILE = 'TreeTranRulesFile'

def readConfig(report):
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), CONFIG_FILE)
        
        f_handle = open(myPath, encoding='utf-8')
    except:
        if report is not None:
            report.Error('Error reading the file: "' + CONFIG_PATH+ '/' + CONFIG_FILE + '". Check that it exists.')
        return None

    my_map = {}
    for line in f_handle:
        
        # decompose any composed characters. FLEx stores strings this way.
        line = unicodedata.normalize('NFD', line)
        if len(line) < 2:
            if report is not None:
                report.Error('Error reading the file: "' + CONFIG_FILE + '". No blank lines allowed.')
            return
        # Skip commented lines
        if line[0] == '#':
            continue
        # We expect lines in the form -- property=value
        if not re.search('=', line):
            if report is not None:
                report.Error('Error reading the file: "' + CONFIG_FILE + '". A line without "=" was found.')
            return
        
        try:
            (prop, value) = line.split('=')
        except:
            report.Error('Error reading the file: "' + CONFIG_FILE + '". A line without more than one "=" was found.')
            return
        
        value = value.rstrip()
        # if the value has commas, save it as a list
        if re.search(',', value):
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
        # If the key value ends with 'File' then change the path accordingly.
        # Also the key must have a value, otherwise ignore it.
        if (re.search('File$', key) or re.search('Folder$', key)) and key in my_map and my_map[key]:
            
            # if we don't have an absolute path (e.g. c:\...) we need to fix up the path. FLExTrans is shipped with relative paths to the work project subfolder ('e.g. German-Swedish')
            if not re.search(':', my_map[key]):
                
                # Return the parent folder of the Config folder + the relative file path. E.g. ...\German-Swedish\target_text.aper
                return os.path.join(os.path.dirname(os.path.dirname(CONFIG_PATH)), my_map[key])
      
        return my_map[key]

def configValIsList(my_map, key, report):
    if isinstance(my_map[key], list) is False:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". The value for "'+key+'" is supposed to be a comma separated list. For a single value, end it with a comma.')
        return False
    else:
        return True