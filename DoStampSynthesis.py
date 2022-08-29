#
#   DoStampSynthesis.py
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.6 - 8/20/22 - Ron Lockwood
#    Renamed this module.
#
#   Version 3.5.5 - 7/14/22 - Ron Lockwood
#    More CloseProject() calls for FlexTools2.1.1
#
#   Version 3.5.4 - 7/13/22 - Ron Lockwood
#    More CloseProject() calls for FlexTools2.1.1
#
#   Version 3.5.3 - 7/9/22 - Ron Lockwood
#    Use a new config setting for using cache. Fixes #115.
#
#   Version 3.5.2 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5 - 4/1/22 - Ron Lockwood
#    Added a parameter useCacheIfAvailable and default it to false so that the
#    LiveRuleTester can force the rebuild of the lexicon files.  Fixes #56.
#
#   Version 3.4.2 - 3/11/22 - Ron Lockwood
#    Less Information outputted to FlexTools.
#
#   Version 3.4.1 - 3/10/22 - Ron Lockwood
#    Allow variants with sense information to be put into the STAMP root dictionary.
#    Fixes #84.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Bump version number for FlexTools 3.2
#
#   Version 3.0.1 - 7/8/21 - Ron Lockwood
#    Handle slash in category name
# 
#   Version 3.0 - 1/26/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.6.2 - 4/4/19 - Ron Lockwood
#    Check for the root lexicon file being out of date compared to the target database
#    before going through all target entries. This improves performance.
#
#   Version 1.6.1 - 3/27/19 - Ron Lockwood
#    Bugfix for null MSA and for null PartOfSpeech. Give sensible errors in these
#    situations and skip the sense. 
#
#   Version 1.6 - 3/30/18 - Ron Lockwood
#    Made the main function minimal and separated the main logic into two main functions 
#    one for extracting the target lexicon and one for running the synthesis. Also 
#    modularized a lot more of the code.
#
#   Version 1.3.8 - 01/19/18 - Ron Lockwood
#    Skip natural classes that are related to phonological features (PhNCFeatures)
#
#   Version 1.3.7 - 10/10/17 - Marc
#    Extracted call to do_make_direct.sh to RunApertium.py
#
#   Version 1.3.6 - 10/6/17 - Marc
#    Added call to do_make_direct.sh to use Windows Subsystem for Linux and to avoid
#    the use of VirtualBox for Apertium.
#
#   Version 1.3.5 - 1/18/17 - Ron
#    Use BestAnalysisAlternative instead of AnalysisDefault.
#    Change the spaces to underscores and remove periods in
#    grammatical categories.
#
#   Version 1.3.4 - 10/21/16 - Ron
#    Allow the affix and ana files to not be in the temp folder if a slash is present.
#
#   Version 1.3.3 - 5/7/16 - Ron
#    Give a more helpful message when the target database is not found.
#    If the gloss is None for an affix, skip it and give a warning message.
#
#   Version 1.3.2 - 4/23/16 - Ron
#    Check for a non-null natural class name.
#
#   Version 1.3.1 - 4/15/16 - Ron
#    Handle allomorphs of circumfixes.
#    Don't assume one prefix and one suffix allomorph. Put all prefix 
#    allomorphs in the prefix file and likewise for suffix allomorphs.
#
#   Version 1.3.0 - 4/13/16 - Ron
#    Handle infixes and circumfixes.
#    For infixes write new information to the infix dictionary that is specific
#    to infixes. Namely the location field which we get from FLEx's 
#    InfixPositions field. The STAMP sfm mapping file for infixes gets \l
#    mapped to \L. Circumfixes get processed by writing the 1st allomorph to
#    the prefix file and the 2nd allomorph to the suffix file.
#
#   Version 1.2.0 - 1/29/16 - Ron
#    No changes to this module.
#
#   Version 3 - 7/24/15 - Ron
#    Preserve case in words. 
#    Convert the head word for the root dictionaries to lower case. Use the
#    add_one utility.
#
#   Version 2 - 7/16/15 - Ron
#    Support handling of irregularly inflected forms. Allow variants to be put
#    into the root dictionary if they they are inflectional variants. Add a new
#    POS '_variant_' to the list. If there are no senses for an entry see if it
#    is an infl. variant and if so write it to the root dictionary.
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
import sys
import re 
import tempfile
from subprocess import call
from datetime import datetime

from System import Guid
from System import String

import ReadConfig
import Utils

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from flexlibs import FLExProject, AllProjectNames

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Synthesize Text with STAMP",
        FTM_Version    : "3.6",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Extracts the target lexicon, then synthesizes the target text.",
        FTM_Help       :"",
        FTM_Description:  
"""
This module will creates target language lexicons files. One for
roots, prefixes, suffixes and infixes. They are in the CARLA format
which are suitable for input to STAMP for synthesis. They use the standard
format marker type of formatting.
This module also creates other files STAMP needs and then runs STAMP to create the
synthesized text. NOTE: Messages and the task bar will show the SOURCE database
as being used. Actually the target database is being used.
""" }

DONT_CACHE = False

#----------------------------------------------------------------

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

def output_allomorph(morph, envList, f_handle, e, report, TargetDB):
    amorph = ITsString(morph.Form.VernacularDefaultWritingSystem).Text
    
    # If there is nothing for any WS we get ***
    if amorph == '***' or amorph == None:
        # Suppress this warning for now. 
        #report.Warning('No allomorph found. Skipping 1 allomorph for Headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
        return
    
    # Convert spaces between words to underscores, these have to be removed later.
    amorph = re.sub(r' ', r'_', amorph)
    f_handle.write('\\a '+amorph+' ')
    
    # Write out negated environments from previous allomorphs
    for prevEnv in envList:
        f_handle.write('~'+prevEnv+' ') 
        
    for env in morph.PhoneEnvRC:
        envStr = ITsString(env.StringRepresentation).Text
        f_handle.write(envStr+' ')
        envList.append(envStr)
    f_handle.write('\n')

# A circumfix has two parts a prefix part and a suffix part
# Write the 1st allomorph to the prefix file and the 2nd to the suffix file
# Modify the glosses for each using the convention used in the module ConvertTextToSTAMPformat
# GLOSS_cfx_part_X where X is a or b
def process_circumfix(e, f_pf, f_sf, myGloss, report, myType, TargetDB):
    
    # Convert dots to underscores in the gloss if it's not a root/stem
    if (myType == 'non-stem'):
        myGloss = re.sub(r'\.', r'_', myGloss)

    # Output gloss
    if myGloss:
        f_pf.write('\\g ' + myGloss+'_cfx_part_a' + '\n')
    else:
        f_pf.write('\\g \n')
    
    # 1st allomorph for the prefix file
    allEnvs = []
    for i, allomorph in enumerate(e.AlternateFormsOS):
        if ITsString(allomorph.MorphTypeRA.Name.BestAnalysisAlternative).Text == 'prefix':
            output_allomorph(allomorph, allEnvs, f_pf, e, report, TargetDB)
    
    f_pf.write('\n')
    
    # Output gloss
    if myGloss:
        f_sf.write('\\g ' + myGloss+'_cfx_part_b' + '\n')
    else:
        f_sf.write('\\g \n')
    
    # 2nd allomorph for the suffix file
    allEnvs = []
    for i, allomorph in enumerate(e.AlternateFormsOS):
        if ITsString(allomorph.MorphTypeRA.Name.BestAnalysisAlternative).Text == 'suffix':
            output_allomorph(allomorph, allEnvs, f_sf, e, report, TargetDB)
    
    f_sf.write('\n')

def process_allomorphs(e, f_handle, myGloss, report, myType, TargetDB):
    
    # Convert dots to underscores in the gloss if it's not a root/stem
    if (myType == 'non-stem'):
        myGloss = re.sub(r'\.', r'_', myGloss)

    # Output gloss
    if myGloss:
        f_handle.write('\\g ' + myGloss + '\n')
    else:
        f_handle.write('\\g \n')
    
    # For infixes, we need to output the infix positions field
    if ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text == 'infix':
        # AMPLE's ANA spec. says you need to specify the morpheme type that the
        # infix applies to, FLEx doesn't restrict the infix to just one type,
        # so use all three types when building the position field for the
        # ANA file. 
        morphTypesStr = 'prefix suffix root ' 
        f_handle.write('\\l ' + morphTypesStr)
        for position in e.LexemeFormOA.PositionRS:
            positionStr = ITsString(position.StringRepresentation).Text
            f_handle.write(positionStr+' ')
        f_handle.write('\n')
        
    # Loop through all the allomorphs
    allEnvs = []
    for allomorph in e.AlternateFormsOS:
        output_allomorph(allomorph, allEnvs, f_handle, e, report, TargetDB)
    
    # Now process the lexeme form which is the default allomorph
    output_allomorph(e.LexemeFormOA, allEnvs, f_handle, e, report, TargetDB)
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
        if i != 3: # only for affixes
            f_sycd.write(r'\ch "\o" "O"'+'\n') 
        if i == 0: # only for infixes
            f_sycd.write(r'\ch "\l" "L"'+'\n') # This is the infix location field
    f_sycd.close()

    # Create the blank files we need
    for b in blankFileNameList:
        f = open(b,'w', encoding="utf-8")
        f.close()
    
    return cmdFileName

def output_cat_info(TargetDB, f_dec):
    
    # loop through all target categories and write them to the dec file
    for pos in TargetDB.lp.AllPartsOfSpeech:

        # get abbreviation
        posAbbr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
        
        # change spaces to underscores
        posAbbr = re.sub('\s', '_', posAbbr)

        # remove periods
        posAbbr = re.sub('\.', '', posAbbr)

        # change / to |
        posAbbr = re.sub('/', '|', posAbbr)

        f_dec.write('\\ca ' + posAbbr + '\n')
    f_dec.write('\\ca _variant_\n') # for variant entries
    f_dec.write('\n')
    
    return

def output_nat_class_info(TargetDB, f_dec):
    err_list = []
    
    # Write out all the natural classes and the graphemes that they are made up of
    # Loop through all natural classes
    for natClass in TargetDB.lp.PhonologicalDataOA.NaturalClassesOS:
        
        # Get the natural class name and write it out
        natClassName = ITsString(natClass.Abbreviation.BestAnalysisAlternative).Text
        
        # Make sure we have a valid class name and that it is not a Natural Class of Features which we are not concerned with
        if natClassName and natClass.ClassName != 'PhNCFeatures':
            f_dec.write('\\scl '+natClassName+'\n')
        
            # Loop through all the segments in the class
            for seg in natClass.SegmentsRC:
    
                # Loop through all the graphemes for each segment
                for graph in seg.CodesOS:
                    # Write out the grapheme string one after another on the line
                    grapheme = ITsString(graph.Representation.VernacularDefaultWritingSystem).Text
                    if not grapheme:
                        err_list.append(('Null grapheme found for natural class: '+natClassName+'. Skipping.', 1))
                        continue
                    else:
                        f_dec.write(' '+grapheme)
            f_dec.write('\n')
    f_dec.close()
    
    return err_list

def create_stamp_dictionaries(TargetDB, f_rt, f_pf, f_if, f_sf, morphNames, report):
    err_list = []
        
    if report is not None:
        report.ProgressStart(TargetDB.LexiconNumberOfEntries())
    
    pf_cnt = sf_cnt = if_cnt = rt_cnt = 0
    
    # Loop through all the entries
    for i,e in enumerate(TargetDB.LexiconAllEntries()):
    
        if report is not None:
            report.ProgressUpdate(i)
            
        morphType = ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text
        
        # Process inflectional variants even if they have senses.
        if True:
            
            got_one = False
            
            # Process roots
            # Don't process clitics in this block
            if e.LexemeFormOA and \
               e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
               e.LexemeFormOA.MorphTypeRA and morphType in morphNames:
            
                for entryRef in e.EntryRefsOS:
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
                    headWord = ITsString(e.HeadWord).Text
                    headWord = Utils.add_one(headWord)
                    headWord = headWord.lower()
                    # change spaces to underscores
                    headWord = re.sub('\s', '_', headWord)
    
                    # Write out morphname field (no sense number for variants)
                    f_rt.write('\\m '+headWord+'\n')
                    f_rt.write('\\c '+"_variant_"+'\n')

                    # Process all allomorphs and their environments
                    process_allomorphs(e, f_rt, "", report, 'stem', TargetDB)
                    rt_cnt +=1

        if e.SensesOS.Count > 0: # Entry with senses
            # Loop through senses
            for i, mySense in enumerate(e.SensesOS):
                
                gloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
                
                # Process roots
                # Don't process clitics in this block
                if e.LexemeFormOA and \
                   e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
                   e.LexemeFormOA.MorphTypeRA and morphType in morphNames:
                
                    # Set the headword value and the homograph #, if necessary
                    headWord = ITsString(e.HeadWord).Text
                    headWord = Utils.add_one(headWord)
                    headWord = headWord.lower()
                    
                    # change spaces to underscores
                    headWord = re.sub('\s', '_', headWord)

                    if mySense.MorphoSyntaxAnalysisRA:
                        
                        # Get the POS abbreviation for the current sense, assuming we have a stem
                        if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                            
                            if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:            
                                abbrev = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                      Abbreviation.BestAnalysisAlternative).Text
                            else:
                                err_list.append(('Skipping sense because the POS is unknown: '+\
                                               ' while processing target headword: '+ITsString(e.HeadWord).Text, 1, TargetDB.BuildGotoURL(e)))
                                continue
                                                      
                        else:
                            err_list.append(('Skipping sense that is of class: '+mySense.MorphoSyntaxAnalysisRA.ClassName+\
                                           ' for headword: '+ITsString(e.HeadWord).Text, 1, TargetDB.BuildGotoURL(e)))
                            continue
                    else:
                        err_list.append(('Skipping sense that has no Morpho-syntax analysis.'+\
                                       ' Headword: '+ITsString(e.HeadWord).Text, 1, TargetDB.BuildGotoURL(e)))
                        continue
    
                    # Write out morphname field
                    f_rt.write('\\m '+headWord+'.'+str(i+1)+'\n')
                    
                    abbrev = Utils.convertProblemChars(abbrev)
                    
                    f_rt.write('\\c '+abbrev+'\n')
                    
                    # Process all allomorphs and their environments 
                    process_allomorphs(e, f_rt, gloss, report, 'stem', TargetDB)
                    rt_cnt +=1

                # Now process non-roots
                else:
                    if gloss == None:
                        err_list.append(('No gloss. Skipping. Headword: '+ITsString(e.HeadWord).Text, 1, TargetDB.BuildGotoURL(e)))
                    elif e.LexemeFormOA == None:
                        err_list.append(('No lexeme form. Skipping. Headword: '+ITsString(e.HeadWord).Text, 1, TargetDB.BuildGotoURL(e)))
                    elif e.LexemeFormOA.MorphTypeRA == None:
                        err_list.append(('No Morph Type. Skipping.'+ITsString(e.HeadWord).Text+' Best Vern: '+\
                                       ITsString(e.LexemeFormOA.Form.VernacularDefaultWritingSystem).Text, 1, TargetDB.BuildGotoURL(e)))
                    elif e.LexemeFormOA.ClassName != 'MoStemAllomorph':
                        if e.LexemeFormOA.ClassName == 'MoAffixAllomorph':
                            if morphType in ['prefix', 'prefixing interfix']:
                                process_allomorphs(e, f_pf, gloss, report, 'non-stem', TargetDB)
                                pf_cnt += 1
                            elif morphType in ['suffix', 'suffixing interfix']:
                                process_allomorphs(e, f_sf, gloss, report, 'non-stem', TargetDB)
                                sf_cnt += 1
                            elif morphType in ['infix', 'infixing interfix']:
                                process_allomorphs(e, f_if, gloss, report, 'non-stem', TargetDB)
                                if_cnt += 1
                            elif morphType == 'circumfix':
                                process_circumfix(e, f_pf, f_sf, gloss, report, 'non-stem', TargetDB)
                                pf_cnt += 1
                                sf_cnt += 1
                            else:
                                err_list.append(('Skipping entry because the morph type is: ' + morphType, 1, TargetDB.BuildGotoURL(e)))
                        else:
                            err_list.append(('Skipping entry since the lexeme is of type: '+e.LexemeFormOA.ClassName, 1, TargetDB.BuildGotoURL(e)))
                    elif morphType not in morphNames:
                        if morphType == 'proclitic':
                            process_allomorphs(e, f_pf, gloss, report, 'non-stem', TargetDB)
                            pf_cnt += 1
                        elif morphType == 'enclitic':
                            process_allomorphs(e, f_sf, gloss, report, 'non-stem', TargetDB)
                            sf_cnt += 1
                        else:
                            err_list.append(('Skipping entry because the morph type is: ' + morphType, 1, TargetDB.BuildGotoURL(e)))
    
    err_list.append((f'STAMP dictionaries created. {str(rt_cnt)} roots, {str(pf_cnt)} prefixes, {str(sf_cnt)} suffixes and {str(if_cnt)} infixes.', 0))
    
    return err_list
    
def extract_target_lex(DB, configMap, report=None, useCacheIfAvailable=False):
    error_list = []
        
    morphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)
    if not morphNames: 
        error_list.append(('Configuration file problem.', 2))
        return error_list
    
    # Create a path to the temporary folder + project name
#    partPath = os.path.join(tempfile.gettempdir(), targetProject)

    # Get the target project name
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
    if not targetProj:
        error_list.append(('Configuration file problem with TargetProject.', 2))
        return error_list
    
    # Get lexicon files folder setting
    lexFolder = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report)
    if not lexFolder:
        error_list.append((f'Configuration file problem with {ReadConfig.TARGET_LEXICON_FILES_FOLDER}.', 2))
        return error_list

    # Check that we have a valid folder
    if os.path.isdir(lexFolder) == False:
        error_list.append((f'Lexicon files folder: {ReadConfig.TARGET_LEXICON_FILES_FOLDER} does not exist.', 2))
        return error_list

    # Have all files start with targetProject
    partPath = os.path.join(lexFolder, targetProj)
    
    # Get cache data setting
    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        error_list.append((f'Configuration file problem with {ReadConfig.CACHE_DATA}.', 2))
        return error_list

    TargetDB = FLExProject()

    # See if the target project is a valid database name.
    if targetProj not in AllProjectNames():
        error_list.append(('The Target Database does not exist. Please check the configuration file.', 2))
        return error_list

    try:
        # Open the target database
        if not targetProj:
            error_list.append(('Problem accessing the target project.', 2))
            return error_list
        TargetDB.OpenProject(targetProj, True)
    except: #FDA_DatabaseError, e:
        report.Error('Failed to open the target database.')
        raise

    error_list.append(('Using: '+targetProj+' as the target database.', 0))

    # If the target database hasn't changed since we created the root databse file, don't do anything.
    if useCacheIfAvailable and cacheData == 'y' and is_root_file_out_of_date(TargetDB, partPath+'_rt.dic') == False:
        TargetDB.CloseProject()
        error_list.append(('Target lexicon files are up to date.', 0))
        return error_list

    # Create the dictionary files in a temp folder
    (f_pf, f_if, f_sf, f_rt, f_dec) = create_dictionary_files(partPath)

    # Output category info.
    #error_list.append(('Outputting category information...', 0))
    output_cat_info(TargetDB, f_dec)
    
    # Output natural class info.
    #error_list.append(('Outputting natural class information...', 0))
    err_list = output_nat_class_info(TargetDB, f_dec)
    error_list.extend(err_list)
    
    # Put data into the STAMP dictionaries
    #error_list.append(('Making the STAMP dictionaries...', 0))
    err_list = create_stamp_dictionaries(TargetDB, f_rt, f_pf, f_if, f_sf, morphNames, report)
    error_list.extend(err_list)
    
    f_pf.close() 
    f_if.close() 
    f_sf.close() 
    f_rt.close() 
    f_dec.close()

    TargetDB.CloseProject()
    
    return error_list

def fix_up_text(synFile, cleanUpText):
    # Also remove @ signs at the beginning of words and N.N at the end of words if so desired in the configuration file.
    f_s = open(synFile, encoding="utf-8")
    line_list = []
    for line in f_s:
        line_list.append(line)

    f_s.close()
    f_s = open(synFile, 'w', encoding="utf-8")
    for line in line_list:
        line = re.sub('_', ' ', line)
        
        if cleanUpText:
            line = re.sub('\d+\.\d+', '', line, re.A) # re.A=ASCII-only match
            line = re.sub('@', '', line)
        f_s.write(line)
    f_s.close()

def synthesize(configMap, anaFile, synFile, report=None):
    error_list = []
    
    targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
    clean = ReadConfig.getConfigVal(configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, report)

    if not (targetProject and clean): 
        error_list.append(('Configuration file problem.', 2))
        return error_list
    
    if clean[0].lower() == 'y':
        cleanUpText = True
    else:
        cleanUpText = False

    # Get lexicon files folder setting
    lexFolder = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_LEXICON_FILES_FOLDER, report)
    if not lexFolder:
        error_list.append((f'Configuration file problem with {ReadConfig.TARGET_LEXICON_FILES_FOLDER}.', 2))
        return error_list
    
    # Check that we have a valid folder
    if os.path.isdir(lexFolder) == False:
        error_list.append((f'Lexicon files folder: {ReadConfig.TARGET_LEXICON_FILES_FOLDER} does not exist.', 2))
        return error_list

    # Have all files start with targetProject
    partPath = os.path.join(lexFolder, targetProject)
    
    # Create other files we need for STAMP
    cmdFileName = create_synthesis_files(partPath)

    # Synthesize the target text
    error_list.append(('Synthesizing the target text...', 0))

    # run STAMP to synthesize the results. E.g. stamp32" -f Gilaki-Thesis_ctrl_files. txt -i pes_verbs.ana -o pes_verbs.syn
    # this assumes stamp32.exe is in the current working directory.
    call(['stamp32.exe', '-f', cmdFileName, '-i', anaFile, '-o', synFile])

    error_list.append(('Fixing up the target text...', 0))
    
    
    # Replace underscores with spaces in the Synthesized file
    # Underscores were added for multiword entries that contained a space
    fix_up_text(synFile, cleanUpText)
    
    return error_list

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not (targetANA and targetSynthesis):
        return 
    
    anaFile = Utils.build_path_default_to_temp(targetANA)
    synFile = Utils.build_path_default_to_temp(targetSynthesis)
    
    # Extract the target lexicon
    error_list = extract_target_lex(DB, configMap, report, useCacheIfAvailable=True)

    # Synthesize the new target text
    err_list = synthesize(configMap, anaFile, synFile, report)
    error_list.extend(err_list)
    
    # output info, warnings, errors
    for triplet in error_list:
        msg = triplet[0]
        code = triplet[1]
        
        # sometimes we'll have a url to output in the error/warning
        if len(triplet) == 3:
            url = triplet[2]
        else:
            url = None
            
        if code == 0:
            report.Info(msg, url)
        elif code == 1:
            report.Warning(msg, url)
        else: # error=2
            report.Error(msg, url)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
