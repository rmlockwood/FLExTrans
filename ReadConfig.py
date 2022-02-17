#
#   ReadConfig
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
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
import unicodedata

CONFIG_FILE = 'FlexTrans.config'

ANALYZED_TEXT_FILE = 'AnalyzedTextOutputFile'
ANALYZED_TREETRAN_TEXT_FILE = 'AnalyzedTextTreeTranOutputFile'
BILINGUAL_DICTIONARY_FILE = 'BilingualDictOutputFile'
BILINGUAL_DICT_REPLACEMENT_FILE = 'BilingualDictReplacementFile'
CATEGORY_ABBREV_SUB_LIST = 'CategoryAbbrevSubstitutionList'
CLEANUP_UNKNOWN_WORDS = 'CleanUpUnknownTargetWords'
SENTENCE_PUNCTUATION = 'SentencePunctuation'
SOURCE_COMPLEX_TYPES = 'SourceComplexTypes'
SOURCE_CUSTOM_FIELD_ENTRY = 'SourceCustomFieldForEntryLink'
SOURCE_CUSTOM_FIELD_SENSE_NUM = 'SourceCustomFieldForSenseNum'
SOURCE_DISCONTIG_TYPES = 'SourceDiscontigousComplexTypes'
SOURCE_DISCONTIG_SKIPPED = 'SourceDiscontigousComplexFormSkippedWordGrammaticalCategories'
SOURCE_MORPHNAMES = 'SourceMorphNamesCountedAsRoots'
SOURCE_TEXT_NAME = 'SourceTextName'
TARGET_AFFIX_GLOSS_FILE = 'TargetAffixGlossListFile'
TARGET_ANA_FILE = 'TargetOutputANAFile'
TARGET_FORMS_INFLECTION_1ST = 'TargetComplexFormsWithInflectionOn1stElement'
TARGET_FORMS_INFLECTION_2ND = 'TargetComplexFormsWithInflectionOn2ndElement'
TARGET_MORPHNAMES = 'TargetMorphNamesCountedAsRoots'
TARGET_PROJECT = 'TargetProject'
TARGET_SYNTHESIS_FILE = 'TargetOutputSynthesisFile'
TRANSFER_RESULTS_FILE = 'TargetTranferResultsFile'
TREETRAN_INSERT_WORDS_FILE = 'TreeTranInsertWordsFile'

def readConfig(report):
    try:
        f_handle = open(CONFIG_FILE, encoding='utf-8')
    except:
        if report is not None:
            report.Error('Error reading the file: "' + CONFIG_FILE + '". Check that it is in the FlexTools folder.')
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
        (prop, value) = line.split('=')
        value = value.rstrip()
        # if the value has commas, save it as a list
        if re.search(',', value):
            my_list = value.split(',')
            my_map[prop] = my_list
        else:
            my_map[prop] = value

    return my_map

def getConfigVal(my_map, key, report):
    if key not in my_map:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". A value for "'+key+'" was not found.')
        return None
    else:
        return my_map[key]

def configValIsList(my_map, key, report):
    if isinstance(my_map[key], list) is False:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". The value for "'+key+'" is supposed to be a comma separated list. For a single value, end it with a comma.')
        return False
    else:
        return True