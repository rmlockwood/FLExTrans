#
#   DoStampSynthesis.py
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13.2 - 3/20/25 - Ron Lockwood
#    Move the Mixpanel logging to the main function. Callers should do it.
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
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10.5 - 7/23/24 - Ron Lockwood
#    Fixes #671. Handle outputting the default inflection class for categories that have them.
#
#   Version 3.10.4 - 5/8/24 - Ron Lockwood
#    Fixes crash where sense's MorphoSyntaxAnalysis RA object is None. Check for that now.
#
#   Version 3.10.3 - 5/3/24 - Ron Lockwood
#    Fixes #611 where crash occurred after refreshing the lexicon. Reset global list and map
#    each time main synthesis function is called.
#
#   Version 3.10.2 - 3/7/24 - Ron Lockwood
#    Fixes #582. (correct #?) References were mistakenly getting deleted. Like \x 23.5.
#    Only remove N.N for clean up step when it follows a lemma.
#
#   Version 3.10.1 - 3/5/24 - Ron Lockwood
#    Fixes #580. Correctly form the circumfix affix for HermitCrab.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9.4 - 11/22/23 - Ron Lockwood
#    Ignore allomorphs marked as abstract. Also big changes to support required
#    features which are treated kind of like stem names. Look through all affixes to
#    see if required features are used and save unique sets of them. For each affix allomoprh
#    that matches a required features set, label with a morpheme property. Lastly,
#    affix allomoprhs that have the required features get environments with the morpheme property.
#    this change also required saving all affixes to a list for later processing after the rest of
#    the entries. Fixes #507 and #516.
#
#   Version 3.9.3 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.2 - 7/19/23 - Ron Lockwood
#    Fixes #464. Support a new module that does either kind of synthesis by calling 
#    the appropriate module. 
#
#   Version 3.9.1 - 6/26/23 - Ron Lockwood
#    Updated module description. Also output the name of the created synthesis file.
#
#   Version 3.9 - 6/19/23 - Ron Lockwood
#    Fixes #444. Skip Affix Process 'allomorphs'. They are only for HermitCrab.
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.7.4 - 2/6/23 - Ron Lockwood
#    Handle inflection sub-classes. List them all in the .dec file and add all sub-classes
#    as environments for an affix when the parent class applies.
#
#   Version 3.7.3 - 1/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#    Also fix for circumfix - needed to check for 'suffix' not SUFFIX_TYPE
#
#   earlier version history removed on 3/1/25
#
#   Create the target dictionaries that STAMP needs. These are in the 
#   AMPLE-style sfm format. Also at the end of the module, create the files that 
#   STAMP needs (such as config files) and then run STAMP to create the
#   Synthesis file and fix it up by removing underscores. (Underscores were used
#   in the dictionaries instead of spaces so that STAMP could handle them.)
#
#   As we write out entries in the dictionaries, some entries or allomorphs have
#   environment constraints. We have to order these properly and negate the environments
#   of the previous allomorph(s).
#

import os
import re 
from subprocess import call
from datetime import datetime

from SIL.LCModel import ( # type: ignore
    IMoStemMsa,
    IMoInflAffMsa,
    IMoStemAllomorph,
    IMoAffixAllomorph,
    IMoAffixProcess,
    IPhNCSegments,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString                     # type: ignore

from flextoolslib import *                                                  # type: ignore
from flexlibs import FLExProject, AllProjectNames

import Mixpanel
import ReadConfig
import Utils
import FTPaths

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'DoStampSynthesis'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
description = _translate("DoStampSynthesis", """This module runs STAMP to create the
synthesized text.
Before creating the synthesized text, this module extracts the target language lexicon files, one each for
roots, prefixes, suffixes and infixes. They are in the STAMP format for synthesis. The lexicon files
are put into the folder designated in the Settings as Target Lexicon Files Folder. Usually this is the 'Build' folder.
The synthesized text will be stored in the file specified by the Target Output Synthesis File setting.
This is typically called target_text-syn.txt and is usually in the Output folder.
NOTE: Messages will say the source project is being used. Actually the target project is being used.""")

docs = {FTM_Name       : _translate("DoStampSynthesis", "Synthesize Text with STAMP"),
        FTM_Version    : "3.14.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("DoStampSynthesis", "Synthesizes the target text with the tool STAMP."),
        FTM_Help       : "",
        FTM_Description: description}

app.quit()
del app

DONT_CACHE = False
CATEGORY_STR = 'category'
FEATURES_STR= 'features'
STEM_STR = 'stemString'
AFFIX_STR = 'Affix'
PREFIX_TYPE = 'prefixType'
SUFFIX_TYPE = 'suffixType'
INFIX_TYPE = 'infixType'
STEM_TYPE = 'stemType'

stemNameList = []
reqFeaturesMap = {}

#----------------------------------------------------------------

# Recursive function to save an inflection class and all sub-classes
def saveInflClass(inflClassList, myInflClass):
    
    if myInflClass.Abbreviation:

        inflClassStr = Utils.as_string(myInflClass.Abbreviation)
        
        inflClassList.append(inflClassStr)
        
        # save subclasses
        for subClass in myInflClass.SubclassesOC:
            
            saveInflClass(inflClassList, subClass)
        
def is_root_file_out_of_date(DB, rootFile):
    
    if DONT_CACHE == True:
        return True
    
    # Build a DateTime object with the FLEx DB last modified date
    flexDate = DB.GetDateLastModified()
    dbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
    
    # Get the date of the cache file
    try:
        mtime = os.path.getmtime(rootFile)
    except OSError:
        mtime = 0
    rootFileDateTime = datetime.fromtimestamp(mtime)
    
    if dbDateTime > rootFileDateTime: # FLEx DB is newer
        return True 
    else: # affix file is newer
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def isFeatureSetASubsetofB(specsA, specsB):
    
    featAbbrListA = []
    featAbbrListB = []
    
    Utils.get_feat_abbr_list(specsA, featAbbrListA)
    Utils.get_feat_abbr_list(specsB, featAbbrListB)
    
    return set(featAbbrListA).issubset(set(featAbbrListB))
    
def output_final_allomorph_info(f_handle, sense, morphCategory):
    
    ## Now put out the one-time stuff for the entry

    # We will only process inflectional affixes and stems (i.e. not derrivational affixes, etc.)
    if sense is None or sense.MorphoSyntaxAnalysisRA is None:
        return
    if sense.MorphoSyntaxAnalysisRA.ClassName == 'MoInflAffMsa':
        msa = IMoInflAffMsa(sense.MorphoSyntaxAnalysisRA)
    elif sense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
        msa = IMoStemMsa(sense.MorphoSyntaxAnalysisRA)
    else:
        return
        
    # Skip clitics which we are giving a category of SUFFIX or PREFIX, but the class name is Stem
    if sense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa' and morphCategory != STEM_TYPE:
        
        return
    
    if msa:
        
        if morphCategory != STEM_TYPE: # non-stems only

            # Deal with affix stem name stuff.
            # A stem name goes on an affix only if the stem name category matches the category of this msa object
            # Also the msa's inflection set has to match one of the inflection sets defined in the stem name definition (Grammar > Category)
            for stemName in stemNameList:
                
                if msa.PartOfSpeechRA == stemName[CATEGORY_STR]:
                    
                    for featureSet in stemName[FEATURES_STR]:
                        
                        # The stem name feature list just has to be a subset of the features for this current morpheme
                        if msa.InflFeatsOA and isFeatureSetASubsetofB(featureSet.FeatureSpecsOC, msa.InflFeatsOA.FeatureSpecsOC):
                            
                            f_handle.write(f'\\mp {stemName[STEM_STR]}{AFFIX_STR}\n')
                            break

            # Deal with required features stuff
            for reqFeatures in reqFeaturesMap.values():
                
                for featureSet in reqFeatures[FEATURES_STR]:
                    
                    # The required features feature list just has to be a subset of the features for this current morpheme
                    if msa.InflFeatsOA and isFeatureSetASubsetofB(featureSet.FeatureSpecsOC, msa.InflFeatsOA.FeatureSpecsOC):
                        
                        f_handle.write(f'\\mp {reqFeatures[STEM_STR]}{AFFIX_STR}\n')
                        break
    
        # Write out inflection class as a morpheme property if we have a stem
        else: # stems only
            
            if msa.InflectionClassRA:
                
                inflClassStr = Utils.as_string(msa.InflectionClassRA.Abbreviation)
                f_handle.write(f'\\mp {inflClassStr}\n')
            
            # If there is not infl. class assigned, but there is a default inflection class for this POS, write it.
            elif msa.PartOfSpeechRA.DefaultInflectionClassRA:

                inflClassStr = Utils.as_string(msa.PartOfSpeechRA.DefaultInflectionClassRA.Abbreviation)
                f_handle.write(f'\\mp {inflClassStr}\n')

def gather_allomorph_data(morph, masterAlloList, morphCategory):
    
    stemName = ''
    environList = []
    inflClassList = []
    
    amorph = ITsString(morph.Form.VernacularDefaultWritingSystem).Text
    
    # If there is nothing for any WS we get ***
    # Also return if we have a Affix process
    if amorph == '***' or amorph == None or morph.ClassName == 'MoAffixProcess':
        
        return
    
    # Skip allomorphs that are marked "Is Abstract Form"
    if morph.IsAbstract:
        return

    # Save the stem name if we have a stem
    if morphCategory == STEM_TYPE: # stems only
        
        # If we have an affix that is an allomorph of a stem, skip it
        if morph.ClassName == 'MoAffixAllomorph':
            
            return

        morph = IMoStemAllomorph(morph)
        if morph.StemNameRA and morph.StemNameRA.Abbreviation:
            
            stemName = Utils.as_string(morph.StemNameRA.Abbreviation)
            
    else: # non-stems only
        
        # clitics, even though we treat them as affixes, have FLEx type MoStemAllomorph
        # and won't have inflection classes so don't try to process them
        if morph.ClassName != 'MoStemAllomorph':
            
            if morph.ClassName == 'MoAffixAllomorph':

                morph = IMoAffixAllomorph(morph)    

                # See if we need reqFeatures environment
                if morph.MsEnvFeaturesOA:

                    myFeatAbbrList = []
                    Utils.get_feat_abbr_list(morph.MsEnvFeaturesOA.FeatureSpecsOC, myFeatAbbrList)

                    if tuple(myFeatAbbrList) in reqFeaturesMap:

                        requiredFeatInnerMap = reqFeaturesMap[tuple(myFeatAbbrList)]

                        # call it the stemName just so it gets put out the same way
                        stemName = requiredFeatInnerMap[STEM_STR]

            elif morph.ClassName == 'MoAffixProcess':
                morph = IMoAffixProcess(morph)
            
            if morph.InflectionClassesRC:
                
                # Save each inflection class 
                for inflClass in morph.InflectionClassesRC:
                    
                    saveInflClass(inflClassList, inflClass)
        else:
            morph = IMoStemAllomorph(morph)

    # Save each phonological environment 
    if morph.ClassName == 'MoAffixAllomorph' or morph.ClassName == 'MoStemAllomorph':

        for env in morph.PhoneEnvRC:
            
            envStr = ITsString(env.StringRepresentation).Text
            environList.append(envStr)

    masterAlloList.append((amorph, stemName, environList, inflClassList, morphCategory))

def output_all_allomorphs(masterAlloList, f_handle):
    
    # Loop through all the allomorphs we saved
    for currAllomNum, (amorph, stemName, environList, inflClassList, morphCategory) in enumerate(masterAlloList):
        
        # Handle documented ways to do null morphemes in FLEx
        if amorph == '^0' or amorph == '&0' or amorph == '*0' or amorph == '\u2205':
            
            amorph ='0'
    
        # Convert spaces between words to underscores, these have to be removed later.
        amorph = re.sub(r' ', r'_', amorph)
        f_handle.write('\\a '+amorph+' ')
        
        # Write out stem name stuff if we have a stem
        if stemName:
    
            mp = f'{{{stemName}{AFFIX_STR}}}' # {{ means one { i.e. we want the string to be {xyzAffix}
            env1 = f'+/ {mp} ... _ '
            env2 = f'+/ _ ... {mp} '
            f_handle.write(f'{env1}{env2}') 
                
        # Write out inflection class stuff
        for inflClassStr in inflClassList:
            
            if morphCategory == PREFIX_TYPE or morphCategory == INFIX_TYPE:
                
                f_handle.write(f'+/ _ ... {{{inflClassStr}}} ') # {{ means one {
                
            else:
                f_handle.write(f'+/ {{{inflClassStr}}} ... _ ')
                
        # Write out each phonological environment constraints
        for envStr in environList:
            
            if envStr is not None:
                
                f_handle.write(envStr+' ')
        
        ## Write out negated environments from previous allomorphs if necessary
        
        # If we have at least one current inflection class
        if len(inflClassList) > 0:
        
            didIt = False
            
            # Loop through all inflection classes for all allmorphs except the current ones
            for j, (_, _, _, myInflClList, _) in enumerate(masterAlloList):
                
                if currAllomNum != j: 
                    
                    for myInflCl in myInflClList:
                        
                        # If current inflection class matches an inflection class from any other allomorph
                        if myInflCl in inflClassList:
            
                            # Generate negative environments
                            writeNegEnvironments(f_handle, currAllomNum, environList, masterAlloList)
                            didIt = True
                            break
                    
                    if didIt:
                        break
                        
        # If we have a current stem name
        elif len(stemName) > 0:
            
            # Loop through all stem names from previous allomorphs
            for j, (_, myStemName, _, _, _) in enumerate(masterAlloList):
                
                if currAllomNum != j:
                    
                    # If current stem name matches a stem name from a previous allomorph
                    if myStemName == stemName:
                        
                        # Generate negative environments
                        writeNegEnvironments(f_handle, currAllomNum, environList, masterAlloList)
                        break
        
        # Otherwise if we don't have an current inflection class or stem name
        else:
            
            # Generate negative environments
            writeNegEnvironments(f_handle, currAllomNum, environList, masterAlloList)
        
        f_handle.write('\n')

def writeNegEnvironments(f_handle, currAllomNum, currEnvironList, masterAlloList):   
    
    # If the current environment string doesn't match an environment string from another allomorph negate that other environment
    for n, (_, _, environList, _, _) in enumerate(masterAlloList):    
        
        # We only write negative environments for the previous allomorphs
        if n < currAllomNum:
            
            for envirStr in environList:
                
                if envirStr not in currEnvironList:
                    
                    f_handle.write(f'~{envirStr} ')
            
# A circumfix has two parts a prefix part and a suffix part
# Write the 1st allomorph to the prefix file and the 2nd to the suffix file
# Modify the glosses for each using the convention used in the module DoStampSynthesis
# GLOSS_cfx_part_X where X is a or b
def process_circumfix(e, f_pf, f_sf, myGloss, sense):
    
    # Convert dots to underscores in the gloss if it's not a root/stem
    myGloss = Utils.underscores(myGloss)

    # Output gloss
    if myGloss:
        
        f_pf.write('\\g ' + myGloss+Utils.CIRCUMFIX_TAG_A + '\n')
    else:
        f_pf.write('\\g \n')
    
    masterAlloList = []

    # 1st allomorph for the prefix file
    for allomorph in e.AlternateFormsOS:
        
        morphGuidStr = allomorph.MorphTypeRA.Guid.ToString()
        affixGuidStr = Utils.morphTypeReverseMap['prefix']
            
        if morphGuidStr == affixGuidStr:
            
            gather_allomorph_data(allomorph, masterAlloList, PREFIX_TYPE)
    
    # Write the data
    output_all_allomorphs(masterAlloList, f_pf)

    output_final_allomorph_info(f_pf, sense, PREFIX_TYPE)
    
    f_pf.write('\n')
    
    # Output gloss
    if myGloss:
        f_sf.write('\\g ' + myGloss+Utils.CIRCUMFIX_TAG_B + '\n')
    else:
        f_sf.write('\\g \n')
    
    
    masterAlloList = []

    # 2nd allomorph for the suffix file
    for allomorph in e.AlternateFormsOS:
        
        morphGuidStr = allomorph.MorphTypeRA.Guid.ToString()
        affixGuidStr = Utils.morphTypeReverseMap['suffix']
            
        if morphGuidStr == affixGuidStr:

            gather_allomorph_data(allomorph, masterAlloList, SUFFIX_TYPE)

    # Write the data
    output_all_allomorphs(masterAlloList, f_sf)

    output_final_allomorph_info(f_sf, sense, SUFFIX_TYPE)
    
    f_sf.write('\n')

def process_allomorphs(e, f_handle, myGloss, myType, sense):
    
    # Convert dots to underscores in the gloss if it's not a root/stem
    if (myType != STEM_TYPE):
        
        myGloss = Utils.underscores(myGloss)

    # Output gloss
    if myGloss:
        
        f_handle.write('\\g ' + myGloss + '\n')
    else:
        f_handle.write('\\g \n')
    
    # For infixes, we need to output the infix positions field
    if myType == INFIX_TYPE:
        
        # AMPLE's ANA spec. says you need to specify the morpheme type that the
        # infix applies to, FLEx doesn't restrict the infix to just one type,
        # so use all three types when building the position field for the
        # ANA file. 
        morphTypesStr = 'prefix suffix root ' 
        f_handle.write('\\l ' + morphTypesStr)
        
        allom = IMoAffixAllomorph(e.LexemeFormOA)
        
        for position in allom.PositionRS:
            
            positionStr = ITsString(position.StringRepresentation).Text
            f_handle.write(positionStr+' ')
            
        f_handle.write('\n')
        
    # Loop through all the allomorphs
    masterAlloList = []
    
    for allomorph in e.AlternateFormsOS:
        
        gather_allomorph_data(allomorph, masterAlloList, myType)
    
    # Now process the lexeme form which is the default allomorph
    gather_allomorph_data(e.LexemeFormOA, masterAlloList, myType)

    # Write the data
    output_all_allomorphs(masterAlloList, f_handle)
    
    output_final_allomorph_info(f_handle, sense, myType)
    
    f_handle.write('\n')

def define_some_names(partPath):
    dicFileNameList = [partPath+'_pf.dic',partPath+'_if.dic',partPath+'_sf.dic',partPath+'_rt.dic']
    decFileName = partPath+'_stamp.dec'
    
    return (dicFileNameList, decFileName)

def create_dictionary_files(partPath):

    (dicFileNameList, decFileName) = define_some_names(partPath)
    
    # Open the dictionary files we are going to create
    f_pf = open(dicFileNameList[0], 'w', encoding="utf-8") # prefixes
    f_if = open(dicFileNameList[1], 'w', encoding="utf-8") # infixes
    f_sf = open(dicFileNameList[2], 'w', encoding="utf-8") # suffixes
    f_rt = open(dicFileNameList[3], 'w', encoding="utf-8") # roots
    f_dec = open(decFileName, 'w', encoding="utf-8") # categories and string (natural) classes 
    
    # need a blank line at the top
    f_pf.write('\n\n') 
    f_if.write('\n\n') 
    f_sf.write('\n\n') 
    f_rt.write('\n\n') 
    f_dec.write('\n') # blank line
    
    return (f_pf, f_if, f_sf, f_rt, f_dec)
    
def create_synthesis_files(partPath):

    (dicFileNameList, decFileName) = define_some_names(partPath)

    blankFileNameList = [partPath+'_XXXtr.chg',partPath+'_synt.chg',partPath+'_outtx.ctl']
    sycdFileName = partPath+'_sycd.chg'
    cmdFileName = partPath+'_ctrl_files.txt'
    
    # Command file
    f_cmd = open(cmdFileName, 'w', encoding="utf-8")
    f_cmd.write(decFileName+'\n')
    f_cmd.write(blankFileNameList[0]+'\n')
    f_cmd.write(blankFileNameList[1]+'\n')
    f_cmd.write(sycdFileName+'\n')
    f_cmd.write('\n') # need a blank line here
    for d in dicFileNameList:
        f_cmd.write(d+'\n')
    f_cmd.write('\n') # need a blank line here
    f_cmd.write(blankFileNameList[2]+'\n')
    f_cmd.close()
    
    # Synthesis codes file
    f_sycd = open(sycdFileName, 'w', encoding="utf-8")
    firstLineList = ['\\infix \\g','\\prefix \\g','\\suffix \\g','\\root \\m']
    for i, f in enumerate(firstLineList):
        f_sycd.write('\n') # blank line
        f_sycd.write(f+'\n')
        f_sycd.write(r'\ch "\a" "A"'+'\n')
        f_sycd.write(r'\ch "\c" "C"'+'\n')
        if i == 3:
            f_sycd.write(r'\ch "\m" "M"'+'\n') # Morpheme is the \m line for the case of roots
        else:
            f_sycd.write(r'\ch "\g" "M"'+'\n')
        f_sycd.write(r'\ch "\mp" "P"'+'\n')
        f_sycd.write(r'\ch "\mcc" "Z"'+'\n')
        f_sycd.write(r'\ch "\!" "!"'+'\n')
        if i != 3: # only for AFFIX_STRes
            f_sycd.write(r'\ch "\o" "O"'+'\n') 
        if i == 0: # only for infixes
            f_sycd.write(r'\ch "\l" "L"'+'\n') # This is the infix location field
    f_sycd.close()

    # Create the blank files we need
    for b in blankFileNameList:
        if not os.path.isfile(b):
            f = open(b,'w', encoding="utf-8")
            f.close()
    
    return cmdFileName


def output_cat_info(TargetDB, f_dec):
    
    inflClassList = []
        
    # loop through all target categories and write them to the dec file
    for pos in TargetDB.lp.AllPartsOfSpeech:
        
        # get abbreviation
        posAbbr = Utils.as_string(pos.Abbreviation)
        
        # change spaces to underscores
        posAbbr = re.sub(r'\s', '_', posAbbr)

        # remove periods
        posAbbr = re.sub(r'\.', '', posAbbr)

        # change / to |
        posAbbr = re.sub('/', '|', posAbbr)

        f_dec.write('\\ca ' + posAbbr + '\n')

        # get stem name info.
        for stemNameObj in pos.StemNamesOC:
            
            if stemNameObj.Abbreviation and stemNameObj.RegionsOC:
                
                stemNameMap = {}
            
                stemNameMap[CATEGORY_STR] = pos
                stemNameMap[STEM_STR] = Utils.as_string(stemNameObj.Abbreviation)
                stemNameMap[FEATURES_STR] = stemNameObj.RegionsOC # list of feature sets
        
                stemNameList.append(stemNameMap)
            
        # get inflection class info.
        for inflClassObj in pos.InflectionClassesOC:
            
            saveInflClass(inflClassList, inflClassObj)

    f_dec.write('\\ca _variant_\n') # for variant entries
    
    # write stem names as \mp's (morpheme properties)
    for myStemNameMap in stemNameList:
        
        f_dec.write(f'\\mp {myStemNameMap[STEM_STR]}{AFFIX_STR}\n')
        
    # write inflection classes as \mp's (morpheme properties)
    for myInflClass in inflClassList:
        
        f_dec.write(f'\\mp {myInflClass}\n')
        
    f_dec.write('\n')
    
    return

def ouput_req_feature_info(f_dec):

    # write required features names as \mp's (morpheme properties)
    for reqFeatures in reqFeaturesMap.values():
        
        f_dec.write(f'\\mp {reqFeatures[STEM_STR]}{AFFIX_STR}\n')
        
def output_nat_class_info(TargetDB, f_dec):
    err_list = []
    
    # Write out all the natural classes and the graphemes that they are made up of
    # Loop through all natural classes
    for natClass in TargetDB.lp.PhonologicalDataOA.NaturalClassesOS:
        
        # Get the natural class name and write it out
        natClassName = Utils.as_string(natClass.Abbreviation)
        
        # Make sure we have a valid class name and that it is not a Natural Class of Features which we are not concerned with
        if natClassName and natClass.ClassName != 'PhNCFeatures':
            f_dec.write('\\scl '+natClassName+'\n')
        
            natClass = IPhNCSegments(natClass)
            
            # Loop through all the segments in the class
            for seg in natClass.SegmentsRC:
    
                # Loop through all the graphemes for each segment
                for graph in seg.CodesOS:
                    # Write out the grapheme string one after another on the line
                    grapheme = ITsString(graph.Representation.VernacularDefaultWritingSystem).Text
                    if not grapheme:
                        err_list.append((_translate("DoStampSynthesis", "Null grapheme found for natural class: {natClassName}. Skipping.").format(natClassName=natClassName), 1))
                        continue
                    else:
                        f_dec.write(' '+grapheme)
            f_dec.write('\n')
    
    return err_list

def create_stamp_dictionaries(TargetDB, f_rt, f_pf, f_if, f_sf, morphNames, report):
    err_list = []
    allAffixesList = []

    if report is not None:
        report.ProgressStart(TargetDB.LexiconNumberOfEntries())
    
    pf_cnt = sf_cnt = if_cnt = rt_cnt = 0
    
    # Loop through all the entries
    for i,entry in enumerate(TargetDB.LexiconAllEntries()):
    
        if report is not None:
            report.ProgressUpdate(i)
            
        # Check that the objects we need are valid
        if not entry.LexemeFormOA:
            
            if entry.HeadWord:
                
                err_list.append((_translate("DoStampSynthesis", "Skipping sense because the lexeme form is unknown: while processing target headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                
            continue
            
        if not entry.LexemeFormOA.MorphTypeRA or not entry.LexemeFormOA.MorphTypeRA.Name:
            
            if entry.HeadWord:
                
                err_list.append((_translate("DoStampSynthesis", "Skipping sense because the morpheme type is unknown: while processing target headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                
            continue
            
        # See if we have the right morph type
        morphType = Utils.as_string(entry.LexemeFormOA.MorphTypeRA.Name)
        
        # Process inflectional variants even if they have senses.
        got_one = False
        
        # Process roots
        # Don't process clitics in this block
        if entry.LexemeFormOA and entry.LexemeFormOA.ClassName == 'MoStemAllomorph' and entry.LexemeFormOA.MorphTypeRA and morphType in morphNames:
        
            # Check for an inflectional variant
            for entryRef in entry.EntryRefsOS:
                
                if entryRef.RefType == 0: # we have a variant
                    
                    # we only are going to output inflectional variants
                    for varType in entryRef.VariantEntryTypesRS:
                        
                        if varType.ClassName == "LexEntryInflType":
                            
                            got_one = True
                            break
                    
                    if got_one:
                        break
            
            if got_one:                
                
                # Set the headword value and the homograph #, if necessary
                headWord = ITsString(entry.HeadWord).Text
                headWord = Utils.add_one(headWord)
                headWord = headWord.lower()
                # change spaces to underscores
                headWord = re.sub(r'\s', '_', headWord)

                # Write out morphname field (no sense number for variants)
                f_rt.write('\\m '+headWord+'\n')
                f_rt.write('\\c '+"_variant_"+'\n')

                # Process all allomorphs and their environments
                process_allomorphs(entry, f_rt, "", STEM_TYPE, sense=None)
                rt_cnt +=1

        if entry.SensesOS.Count > 0: # Entry with senses
            
            # Loop through senses
            for i, mySense in enumerate(entry.SensesOS):
                
                gloss = Utils.as_string(mySense.Gloss)
                
                # Process roots
                # Don't process clitics in this block
                if entry.LexemeFormOA and entry.LexemeFormOA.ClassName == 'MoStemAllomorph' and entry.LexemeFormOA.MorphTypeRA and morphType in morphNames:
                
                    # Set the headword value and the homograph #, if necessary
                    headWord = ITsString(entry.HeadWord).Text
                    headWord = Utils.add_one(headWord)
                    headWord = headWord.lower()
                    
                    # change spaces to underscores
                    headWord = re.sub(r'\s', '_', headWord)

                    if mySense.MorphoSyntaxAnalysisRA:
                        
                        # Get the POS abbreviation for the current sense, assuming we have a stem
                        if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                            msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                            if msa.PartOfSpeechRA:  
                                          
                                abbrev = Utils.as_string(msa.PartOfSpeechRA.Abbreviation)
                            else:
                                err_list.append((_translate("DoStampSynthesis", "Skipping sense because the POS is unknown: while processing target headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                                continue
                        else:
                            err_list.append((_translate("DoStampSynthesis", "Skipping sense that is of class: {className} for headword: {headword}.").format(className=msa.ClassName, headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                            continue
                    else:
                        err_list.append((_translate("DoStampSynthesis", "Skipping sense that has no Morpho-syntax analysis. Headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                        continue
    
                    # Write out morphname field
                    f_rt.write('\\m '+headWord+'.'+str(i+1)+'\n')
                    
                    abbrev = Utils.convertProblemChars(abbrev, Utils.catProbData)
                    
                    f_rt.write('\\c '+abbrev+'\n')
                    
                    # Process all allomorphs and their environments 
                    process_allomorphs(entry, f_rt, gloss, STEM_TYPE, mySense)
                    rt_cnt +=1

                # Now process non-roots
                else:
                    if gloss == None:
                        
                        err_list.append((_translate("DoStampSynthesis", "No gloss. Skipping. Headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                        
                    elif entry.LexemeFormOA == None:
                        
                        err_list.append((_translate("DoStampSynthesis", "No lexeme form. Skipping. Headword: {headword}.").format(headword=ITsString(entry.HeadWord).Text), 1, TargetDB.BuildGotoURL(entry)))
                        
                    elif entry.LexemeFormOA.MorphTypeRA == None:
                        
                        err_list.append((_translate("DoStampSynthesis", "No Morph Type. Skipping. {headword} Best Vern: {vernacular}.").format(headword=ITsString(entry.HeadWord).Text, vernacular=ITsString(entry.LexemeFormOA.Form.VernacularDefaultWritingSystem).Text), 1, TargetDB.BuildGotoURL(entry)))
                        
                    elif entry.LexemeFormOA.ClassName != 'MoStemAllomorph':
                        
                        if entry.LexemeFormOA.ClassName == 'MoAffixAllomorph':
                            
                            # Add the entry and sense and other stuff to a list for processing later
                            allAffixesList.append((entry, gloss, mySense, morphType))

                        else:
                            err_list.append((_translate("DoStampSynthesis", "Skipping entry since the lexeme is of type: {className}.").format(className=entry.LexemeFormOA.ClassName), 1, TargetDB.BuildGotoURL(entry)))
                            
                    elif morphType not in morphNames:
                        
                        morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()

                        if morphGuidStr == Utils.morphTypeReverseMap['proclitic']:
                            
                            process_allomorphs(entry, f_pf, gloss, PREFIX_TYPE, mySense)
                            pf_cnt += 1
                            
                        elif morphGuidStr == Utils.morphTypeReverseMap['enclitic']:
                            
                            process_allomorphs(entry, f_sf, gloss, SUFFIX_TYPE, mySense)
                            sf_cnt += 1
                        else:
                            err_list.append((_translate("DoStampSynthesis", "Skipping entry because the morph type is: {morphType}.").format(morphType=morphType), 1, TargetDB.BuildGotoURL(entry)))

    getRequiredFeaturesInfo(allAffixesList)   

    pf_cnt, sf_cnt, if_cnt = outputAllAffixes(allAffixesList, TargetDB, err_list, f_pf, f_if, f_sf, pf_cnt, sf_cnt, if_cnt) 

    err_list.append((_translate("DoStampSynthesis", "STAMP dictionaries created. {roots} roots, {prefixes} prefixes, {suffixes} suffixes and {infixes} infixes.").format(roots=str(rt_cnt), prefixes=str(pf_cnt), suffixes=str(sf_cnt), infixes=str(if_cnt)), 0))
    
    return err_list

def getRequiredFeaturesInfo(allAffixesList):

    # Loop through all affixes and check for required features
    for e, gloss, mySense, morphType in allAffixesList:

        num = 1

        # Check all allomorphs
        for allomorph in e.AllAllomorphs:

            # MsEnvFeaturesOA is where the required features are stored
            if allomorph.ClassName == 'MoAffixAllomorph': 
            
                allomorph = IMoAffixAllomorph(allomorph)

                if allomorph.MsEnvFeaturesOA and allomorph.MsEnvFeaturesOA.FeatureSpecsOC:
                
                    # See if we have encountered this combination of features before, if so skip it
                    myFeatAbbrList = []
                    Utils.get_feat_abbr_list(allomorph.MsEnvFeaturesOA.FeatureSpecsOC, myFeatAbbrList)

                    if tuple(myFeatAbbrList) not in reqFeaturesMap:

                        requiredFeatInnerMap = {}
                    
                        requiredFeatInnerMap[CATEGORY_STR] = 'N/A'
                        requiredFeatInnerMap[STEM_STR] = f'reqFeatsBundleName{num}'
                        num += 1
                        requiredFeatInnerMap[FEATURES_STR] = [allomorph.MsEnvFeaturesOA] # list of feature sets (make it a list to be consistent with stem name list)
                
                        reqFeaturesMap[tuple(myFeatAbbrList)] = requiredFeatInnerMap

def outputAllAffixes(allAffixesList, TargetDB, err_list, f_pf, f_if, f_sf, pf_cnt, sf_cnt, if_cnt):

    # Loop through all the affixes and process them
    for e, gloss, mySense, morphType in allAffixesList:

        morphGuidStr = e.LexemeFormOA.MorphTypeRA.Guid.ToString()
        
        if morphGuidStr in [Utils.morphTypeReverseMap['prefix'], Utils.morphTypeReverseMap['prefixing interfix']]:
            
            process_allomorphs(e, f_pf, gloss, PREFIX_TYPE, mySense)
            pf_cnt += 1
            
        elif morphGuidStr in [Utils.morphTypeReverseMap['suffix'], Utils.morphTypeReverseMap['suffixing interfix']]:
            
            process_allomorphs(e, f_sf, gloss, SUFFIX_TYPE, mySense)
            sf_cnt += 1
            
        elif morphGuidStr in [Utils.morphTypeReverseMap['infix'], Utils.morphTypeReverseMap['infixing interfix']]:
            
            process_allomorphs(e, f_if, gloss, INFIX_TYPE, mySense)
            if_cnt += 1
            
        elif morphGuidStr == Utils.morphTypeReverseMap['circumfix']:
            
            process_circumfix(e, f_pf, f_sf, gloss, mySense)
            pf_cnt += 1
            sf_cnt += 1
        else:
            err_list.append((_translate("DoStampSynthesis", "Skipping entry because the morph type is: {morphType}.").format(morphType=morphType), 1, TargetDB.BuildGotoURL(e)))

    return pf_cnt, sf_cnt, if_cnt

def extract_target_lex(DB, configMap, report=None, useCacheIfAvailable=False):
    error_list = []
        
    morphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)
    if not morphNames:
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem."), 2))
        return error_list
    
    # Get the target project name
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
    if not targetProj:
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem with TargetProject."), 2))
        return error_list
    
    # Get lexicon files folder setting
    lexFolder = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report)
    if not lexFolder:
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem with {folder}.").format(folder=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
        return error_list

    # Check that we have a valid folder
    if os.path.isdir(lexFolder) == False:
        error_list.append((_translate("DoStampSynthesis", "Lexicon files folder: {folder} does not exist.").format(folder=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
        return error_list

    # Have all files start with targetProject
    partPath = os.path.join(lexFolder, targetProj)
    
    # Get cache data setting
    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem with {cacheData}.").format(cacheData=ReadConfig.CACHE_DATA), 2))
        return error_list

    TargetDB = FLExProject()

    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():
        error_list.append((_translate("DoStampSynthesis", "The target project does not exist. Please check the configuration file."), 2))
        return error_list
    try:
        # Open the target project
        if not targetProj:
            error_list.append((_translate("DoStampSynthesis", 'Problem accessing the target project.'), 2))
            return error_list
        TargetDB.OpenProject(targetProj, True)
    except: #FDA_DatabaseError, e:
        if report:
            report.Error(_translate("DoStampSynthesis", 'Failed to open the target project.'))
        raise

    # If the target project hasn't changed since we created the root databse file, don't do anything.
    if useCacheIfAvailable and cacheData == 'y' and is_root_file_out_of_date(TargetDB, partPath+'_rt.dic') == False:
        TargetDB.CloseProject()
        error_list.append((_translate("DoStampSynthesis", "Target lexicon files are up to date."), 0))
        return error_list

    # Create the dictionary files in a temp folder
    (f_pf, f_if, f_sf, f_rt, f_dec) = create_dictionary_files(partPath)

    # Output category info.
    output_cat_info(TargetDB, f_dec)
    
    # Output natural class info.
    err_list = output_nat_class_info(TargetDB, f_dec)
    error_list.extend(err_list)
    
    # Put data into the STAMP dictionaries
    err_list = create_stamp_dictionaries(TargetDB, f_rt, f_pf, f_if, f_sf, morphNames, report)
    error_list.extend(err_list)

    # Output required features info to the definition file
    # This info gets created in the create stamp dictionaries function
    ouput_req_feature_info(f_dec)
    
    f_pf.close() 
    f_if.close() 
    f_sf.close() 
    f_rt.close() 
    f_dec.close()

    TargetDB.CloseProject()
    
    return error_list

# Remove @ signs at the beginning of words and N.N at the end of words if so desired in the configuration file.
def fix_up_text(synFile, cleanUpText):

    f_s = open(synFile, encoding="utf-8")
    line_list = []

    for line in f_s:
        line_list.append(line)

    f_s.close()
    f_s = open(synFile, 'w', encoding="utf-8")

    for line in line_list:
        line = re.sub('_', ' ', line)
        
        if cleanUpText:

            # Remove N.N that is attached to a word (looking for non-whitespace before the N). 
            # N.N by itself can cause problems because some references use dot between chapter and verse. Assume a space before these references.
            # [^\s\d] means neither a space nor a number, i.e. a letter or symbol. () to capture the letter
            # then look for one or more numbers the dot then one or more numbers
            line = re.sub(r'([^\s\d])\d+\.\d+', r'\1', line, flags=re.RegexFlag.A) # re.A=ASCII-only match

            # Remove at signs. Those indicate a words that weren't found.
            line = re.sub('@', '', line)

        f_s.write(line)
    f_s.close()

def synthesize(configMap, anaFile, synFile, report=None, overrideClean=False):
    error_list = []

    global stemNameList
    global reqFeaturesMap
    stemNameList = []
    reqFeaturesMap = {}

    targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
    clean = ReadConfig.getConfigVal(configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, report)
    if not (targetProject and clean):
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem."), 2))
        return error_list
    
    if clean[0].lower() == 'y':
        cleanUpText = True
    else:
        cleanUpText = False

    # If the caller wants to turn off cleaning up the text, set the boolean to False
    if overrideClean:
        cleanUpText = False

    # Get lexicon files folder setting
    lexFolder = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report)
    if not lexFolder:
        error_list.append((_translate("DoStampSynthesis", "Configuration file problem with {folder}.").format(folder=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
        return error_list
    
    # Check that we have a valid folder
    if os.path.isdir(lexFolder) == False:
        error_list.append((_translate("DoStampSynthesis", "Lexicon files folder: {folder} does not exist.").format(folder=ReadConfig.TARGET_LEXICON_FILES_FOLDER), 2))
        return error_list

    # Have all files start with targetProject
    partPath = os.path.join(lexFolder, targetProject)
    
    # Create other files we need for STAMP
    cmdFileName = create_synthesis_files(partPath)

    # run STAMP to synthesize the results. E.g. stamp32" -f ggg-Thesis_ctrl_files. txt -i ppp_verbs.ana -o ppp_verbs.syn
    # this assumes stamp32.exe is in the current working directory.
    
    call([FTPaths.STAMP_EXE, '-f', cmdFileName, '-i', anaFile, '-o', synFile])

    # Replace underscores with spaces in the Synthesized file
    # Underscores were added for multiword entries that contained a space
    fix_up_text(synFile, cleanUpText)
    error_list.append((_translate("DoStampSynthesis", "The synthesized target text is in the file: {filePath}.").format(filePath=Utils.getPathRelativeToWorkProjectsDir(synFile)), 0))
    error_list.append((_translate("DoStampSynthesis", "Synthesis complete."), 0))
    return error_list

def doStamp(DB, report, configMap=None):

    # Read the configuration file.
    if not configMap:

        # Read the configuration file.
        configMap = ReadConfig.readConfig(report)
        if not configMap:
            return None

    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    
    if not (targetANA and targetSynthesis):

        return None
    
    if not os.path.exists(targetANA):

        report.Error(_translate("DoStampSynthesis", "The Convert Text to STAMP Format module must be run before this module. The {fileType}: {filePath} does not exist.").format(fileType=ReadConfig.TARGET_ANA_FILE, filePath=targetANA))
        return None
    
    anaFile = Utils.build_path_default_to_temp(targetANA)
    synFile = Utils.build_path_default_to_temp(targetSynthesis)
    error_list = extract_target_lex(DB, configMap, report, useCacheIfAvailable=True)
    err_list = synthesize(configMap, anaFile, synFile, report)
    error_list.extend(err_list)

    if not Utils.processErrorList(error_list, report):

        return None   
    
    return 1

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return 
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    doStamp(DB, report, configMap)


    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
