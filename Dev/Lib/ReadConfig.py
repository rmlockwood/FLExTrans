#
#   ReadConfig
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.14.5 - 12/15/25 - Ron Lockwood
#    Fixes #1149. Support alternate Paratext folder setting.
#    Also check for absolute paths using pathlib. Instead of looking for ':'.
#
#   Version 3.14.4 - 9/19/25 - Ron Lockwood
#    Fixes #1074. Support inflection on the first element of a complex form.
#
#   Version 3.14.3 - 9/3/25 - Ron Lockwood
#    Fixes #1059. Support user-defined tests and morpheme properties for STAMP synthesis.
#
#   Version 3.14.2 - 8/17/25 - Ron Lockwood
#    Fixes #1042. Use settings to determine if production mode output is to FLEx or Paratext.
#
#   Version 3.14.1 - 8/8/25 - Ron Lockwood
#   Fixes #1017. Support cluster projects in TextInOut.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 12/13/24 - Ron Lockwood
#    Added projects to treat in a cluster.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.3 - 9/11/24 - Ron Lockwood
#    Use new write config parameter to create setting if missing.
#
#   Version 3.11.2 - 9/6/24 - Ron Lockwood
#    Support mixpanel usage statistics.
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
#   2023 version history removed on 2/6/26
#
#   Functions for reading a configuration file

import re
import os
import pathlib
import unicodedata

from FTPaths import CONFIG_PATH, WORK_DIR, TRANSL_DIR

CONFIG_FILE = 'FlexTrans.config'

ANALYZED_TEXT_FILE = 'AnalyzedTextOutputFile'
ANALYZED_TREETRAN_TEXT_FILE = 'AnalyzedTextTreeTranOutputFile'
ALT_PARATEXT_FOLDER = 'AlternateParatextFolder'
BILINGUAL_DICTIONARY_FILE = 'BilingualDictOutputFile'
BILINGUAL_DICT_REPLACEMENT_FILE = 'BilingualDictReplacementFile'
CATEGORY_ABBREV_SUB_LIST = 'CategoryAbbrevSubstitutionList'
CACHE_DATA = 'CacheData'
CLEANUP_UNKNOWN_WORDS = 'CleanUpUnknownTargetWords'
CLUSTER_PROJECTS = 'ClusterProjects'
COMPOSED_CHARACTERS = 'UseComposedCharacters'
HERMIT_CRAB_CONFIG_FILE = 'HermitCrabConfigFile'
HERMIT_CRAB_PARSES_FILE = 'HermitCrabParsesFile'
HERMIT_CRAB_MASTER_FILE = 'HermitCrabMasterFile'
HERMIT_CRAB_SURFACE_FORMS_FILE = 'HermitCrabSurfaceFormsFile'
HERMIT_CRAB_SYNTHESIS = 'HermitCrabSynthesis'
LINKER_SEARCH_ANYTHING_BY_DEFAULT = 'LinkerSearchAnythingByDefault'
LOG_STATISTICS = 'LogStatistics'
LOG_STATISTICS_USER_ID = 'LogStatisticsUserID'
LOG_STATISTICS_OPT_OUT_QUESTION = 'LogStatisticsOptOutQuestionAsked'
NO_PROPER_NOUN_WARNING = 'NoWarningForUnanalyzedProperNouns'
PROPER_NOUN_CATEGORY = 'ProperNounCategory'
PROD_MODE_OUTPUT_FLEX = 'ProductionModeOutputFlex'
SENTENCE_PUNCTUATION = 'SentencePunctuation'
SOURCE_FORMS_INFLECTION_1ST = 'SourceComplexFormsWithInflectionOn1stElement'
SOURCE_COMPLEX_TYPES = 'SourceComplexTypes' # This the setting for source complex forms with inflection on the second/last element, but for historical reasons it is named this way.
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
TARGET_XAMPLE_CUSTOM_ENTRY_FIELD = 'TargetXampleCustomEntryField'
TARGET_XAMPLE_CUSTOM_ALLOMORPH_FIELD = 'TargetXampleCustomAllomorphField'
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

# DM: ADDING NEW CONFIGS FOR GENSTC
GENSTC_ANALYZED_GLOSS_TEXT_FILE = 'AnalyzedTextOutputFileForGloss'

GEN_STC_SEM_CUSTOMFIELD = 'GenStcCustomField'
GEN_STC_LIMIT_STEM_COUNT = 'GenStcLimitStemCount'

GEN_STC_LIMIT_LEMMA_N = 'GenStcLimitLemmaN'
GEN_STC_LIMIT_POS_N = 'GenStcLimitPosN'
GEN_STC_LIMIT_SEMANTIC_DOMAIN_N = 'GenStcLimitSemDomainN'

GEN_STC_LIMIT_LEMMA_1 = 'GenStcLimitLemma1'
GEN_STC_LIMIT_POS_1 = 'GenStcLimitPos1'
GEN_STC_LIMIT_SEMANTIC_DOMAIN_1 = 'GenStcLimitSemDomain1'

GEN_STC_LIMIT_LEMMA_2 = 'GenStcLimitLemma2'
GEN_STC_LIMIT_POS_2 = 'GenStcLimitPos2'
GEN_STC_LIMIT_SEMANTIC_DOMAIN_2 = 'GenStcLimitSemDomain2'


##### IMPORTANT #####
# If you are adding a new property that will have multiple values, add it to this list variable
PROPERTIES_THAT_ARE_LISTS = [SOURCE_MORPHNAMES,
                             TARGET_MORPHNAMES,
                             SOURCE_FORMS_INFLECTION_1ST,
                             SOURCE_COMPLEX_TYPES,
                             SOURCE_DISCONTIG_TYPES,
                             SOURCE_DISCONTIG_SKIPPED,
                             TARGET_FORMS_INFLECTION_1ST,
                             TARGET_FORMS_INFLECTION_2ND,
                             SYNTHESIS_TEST_LIMIT_POS,
                             CATEGORY_ABBREV_SUB_LIST, 
                             GEN_STC_LIMIT_POS_N,
                             GEN_STC_LIMIT_POS_1,
                             GEN_STC_LIMIT_POS_2, 
                             GEN_STC_LIMIT_SEMANTIC_DOMAIN_N,
                             GEN_STC_LIMIT_SEMANTIC_DOMAIN_1,
                             GEN_STC_LIMIT_SEMANTIC_DOMAIN_2,
                             CLUSTER_PROJECTS,
                             ]



from PyQt5.QtCore import QCoreApplication

# Define _translate for convenience
_translate = QCoreApplication.translate

def getInterfaceLangCode():
    return 'de'

def openConfigFile(report, info):
    
    try:
        # CONFIG_PATH holds the full path to the flextools.ini file which should be in the WorkProjects/xyz/Config folder. That's where we find FLExTools.config
        # Get the parent folder of flextools.ini, i.e. Config and add FLExTools.config
        myPath = os.path.join(os.path.dirname(CONFIG_PATH), CONFIG_FILE)
        
        return open(myPath, info, encoding='utf-8')
    
    except:
        if report is not None:
            
            report.Error(_translate("ReadConfig", 'Error reading the file: "{path}/{file}". Check that it exists.').format(path=os.path.dirname(CONFIG_PATH), file=CONFIG_FILE))
            
        return None

def writeConfigValue(report, settingName, settingValue, createIfMissing=False):
    
    f_handle = openConfigFile(report, 'r')
    
    if f_handle is None:
        return False

    myLines = f_handle.readlines()
    f_handle.close()
    
    f_outHandle = openConfigFile(report, 'w')
    
    found = False
    
    for line in myLines:

        # If we find a match at the beg. of the line, change the setting
        if re.match(settingName+'=', line):
            
            f_outHandle.write(f'{settingName}={settingValue}\n')
            found = True
        else:
            f_outHandle.write(line)
    
    if not found:
        
        if createIfMissing:
 
            f_outHandle.write(f'{settingName}={settingValue}\n') 

        else:
            if report is not None:
                
                report.Error(_translate("ReadConfig", 'Setting: "{setting}" not found in the configuration file.').format(setting=settingName))
            
            f_outHandle.close()
            return False
            
    f_outHandle.close()
    return True
    
def readConfig(report):
    
    f_handle = openConfigFile(report, 'r')
    
    if f_handle is None:
        
        return None
    
    return getConfigMap(f_handle, report)

def getConfigMap(f_handle, report):

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

                report.Warning(_translate("ReadConfig", 'Problem reading the file: "{file}". A line without "=" was found.').format(file=CONFIG_FILE))

            continue
        
        try:
            (prop, value) = line.split('=')

        except:
            if report is not None:

                report.Warning(_translate("ReadConfig", 'Problem reading the file: "{file}". A line with more than one "=" was found.').format(file=CONFIG_FILE))

            continue
        
        value = value.rstrip()
        
        # if the value has commas and it is in the set of properties that can have multiple values, save it as a list
        if re.search(',', value) and prop in PROPERTIES_THAT_ARE_LISTS:

            my_list = value.split(',')
            my_map[prop] = my_list
        else:
            my_map[prop] = value

    return my_map

def getConfigVal(my_map, key, report, giveError=True, basePath=None):

    if key not in my_map:

        if report is not None:

            if giveError:

                report.Error(_translate("ReadConfig", 'Error in the file: "{file}". A value for "{key}" was not found.').format(file=CONFIG_FILE, key=key))
        
        return None
    else:
        # If the key value has the word 'File' or 'Folder then change the path accordingly.
        # Also the key must have a value, otherwise ignore it.
        if (re.search('File', key) or re.search('Folder', key)) and key in my_map and my_map[key]:
            
            # if we don't have an absolute path (e.g. c:\...) we need to fix up the path. FLExTrans is shipped with relative paths to the work project subfolder ('e.g. German-Swedish')
            if not pathlib.Path(my_map[key]).is_absolute():
                
                # Return the parent folder of the Config folder + the relative file path.
                # E.g. the resulting path would be something like ...\German-Swedish\Build\target_text.txt
                if basePath:
                    return os.path.join(basePath, my_map[key])
                else:
                    return os.path.join(WORK_DIR, my_map[key])
      
        return my_map[key]

def configValIsList(my_map, key, report):

    if isinstance(my_map[key], list) is False:

        if report is not None:

            report.Error(_translate("ReadConfig", 'Error in the file: "{file}". The value for "{key}" is supposed to be a comma separated list. For a single value, end it with a comma.').format(file=CONFIG_FILE, key=key))
        
        return False
    else:
        return True