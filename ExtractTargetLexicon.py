#
#   ExtractTargetLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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

import sys
import re 
import os
import tempfile
import ReadConfig
import Utils

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport
from subprocess import call
from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Extract Target Lexicon",
        'moduleVersion'    : "1.3.4",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Extracts STAMP-style lexicons for the target language, then runs STAMP",
        'moduleDescription'   :
u"""
The target database set in the configuration file will be used. This module will create a three target language lexicons. One for
roots, one for prefixes and one for suffixes. They are in the CARLA style
which is suitable for input to STAMP for synthesis. They use the standard
format marker type of formatting.
This module then creates the STAMP declaration file which contains the grammatical
category names and the natural classes for the target language. These are
extracted from the FLEx database.
Lastly this module creates other files STAMP needs and runs STAMP to create the
synthesized text. NOTE: messages and the task bar will show the SOURCE database
as being used. Actually the target database is being used.
""" }


#----------------------------------------------------------------
# The main processing function
from SIL.FieldWorks.Common.COMInterfaces import ITsString
from SIL.FieldWorks.FDO import ITextRepository
from SIL.FieldWorks.FDO import IStText
from SIL.FieldWorks.FDO import IWfiGloss, IWfiWordform, IWfiAnalysis
from SIL.FieldWorks.FDO import ILexEntryRepository

from SIL.FieldWorks.FDO.DomainServices import SegmentServices

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

from collections import defaultdict
from System import Guid
from System import String

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
        report.Warning('No allomorph found. Skipping 1 allomorph for Headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
        return
    
    # Convert spaces between words to underscores, these have to be removed later.
    amorph = re.sub(r' ', r'_', amorph)
    f_handle.write('\\a '+amorph.encode('utf-8')+' ')
    
    # Write out negated environments from previous allomorphs
    for prevEnv in envList:
        f_handle.write('~'+prevEnv.encode('utf-8')+' ') 
        
    for env in morph.PhoneEnvRC:
        envStr = ITsString(env.StringRepresentation).Text
        f_handle.write(envStr.encode('utf-8')+' ')
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
        f_pf.write('\\g ' + myGloss.encode('utf-8')+'_cfx_part_a' + '\n')
    else:
        f_pf.write('\\g \n')
    
    # 1st allomorph for the prefix file
    allEnvs = []
    for i, allomorph in enumerate(e.AlternateFormsOS):
        if ITsString(allomorph.MorphTypeRA.Name.AnalysisDefaultWritingSystem).Text == 'prefix':
            output_allomorph(allomorph, allEnvs, f_pf, e, report, TargetDB)
    
    f_pf.write('\n')
    
    # Output gloss
    if myGloss:
        f_sf.write('\\g ' + myGloss.encode('utf-8')+'_cfx_part_b' + '\n')
    else:
        f_sf.write('\\g \n')
    
    # 2nd allomorph for the suffix file
    allEnvs = []
    for i, allomorph in enumerate(e.AlternateFormsOS):
        if ITsString(allomorph.MorphTypeRA.Name.AnalysisDefaultWritingSystem).Text == 'suffix':
            output_allomorph(allomorph, allEnvs, f_sf, e, report, TargetDB)
    
    f_sf.write('\n')

def process_allomorphs(e, f_handle, myGloss, report, myType, TargetDB):
    
    # Convert dots to underscores in the gloss if it's not a root/stem
    if (myType == 'non-stem'):
        myGloss = re.sub(r'\.', r'_', myGloss)

    # Output gloss
    if myGloss:
        f_handle.write('\\g ' + myGloss.encode('utf-8') + '\n')
    else:
        f_handle.write('\\g \n')
    
    # For infixes, we need to output the infix positions field
    if ITsString(e.LexemeFormOA.MorphTypeRA.Name.AnalysisDefaultWritingSystem).Text == 'infix':
        # AMPLE's ANA spec. says you need to specify the morpheme type that the
        # infix applies to, FLEx doesn't restrict the infix to just one type,
        # so use all three types when building the position field for the
        # ANA file. 
        morphTypesStr = 'prefix suffix root ' 
        f_handle.write('\\l ' + morphTypesStr)
        for position in e.LexemeFormOA.PositionRS:
            positionStr = ITsString(position.StringRepresentation).Text
            f_handle.write(positionStr.encode('utf-8')+' ')
        f_handle.write('\n')
        
    # Loop through all the allomorphs
    allEnvs = []
    for allomorph in e.AlternateFormsOS:
        output_allomorph(allomorph, allEnvs, f_handle, e, report, TargetDB)
    
    # Now process the lexeme form which is the default allomorph
    output_allomorph(e.LexemeFormOA, allEnvs, f_handle, e, report, TargetDB)
    f_handle.write('\n')
        
def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    TargetDB = FLExDBAccess()

    # Open the target database
    targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
    if not targetProj:
        return
    
    # See if the target project is a valid database name.
    if targetProj not in DB.GetDatabaseNames():
        report.Error('The Target Database does not exist. Please check the configuration file.')
        return

    try:
        TargetDB.OpenDatabase(targetProj, verbose = True)
    except FDA_DatabaseError, e:
        report.Error(e.message)
        print "FDO Cache Create failed!"
        print e.message
        return
        
    report.Info('Using: '+targetProj+' as the target database.')

    targetProject = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
    targetANA = ReadConfig.getConfigVal(configMap, 'TargetOutputANAFile', report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)
    morphNames = ReadConfig.getConfigVal(configMap, 'TargetMorphNamesCountedAsRoots', report)
    clean = ReadConfig.getConfigVal(configMap, 'CleanUpUnknownTargetWords', report)
    if not (targetProject and targetANA and targetSynthesis and morphNames and clean):
        return
    
    if clean[0].lower() == 'y':
        cleanUpText = True
    else:
        cleanUpText = False

    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    synFile = Utils.build_path_default_to_temp(targetSynthesis)
    anaFile = Utils.build_path_default_to_temp(targetANA)
    
    # All other supporting files will be in the temp folder 
    partPath = os.path.join(tempfile.gettempdir(), targetProject)
    
    cmdFileName = partPath+'_ctrl_files.txt'
    decFileName = partPath+'_stamp.dec'
    dicFileNameList = [partPath+'_pf.dic',partPath+'_if.dic',partPath+'_sf.dic',partPath+'_rt.dic']
    blankFileNameList = [partPath+'_XXXtr.chg',partPath+'_synt.chg',partPath+'_outtx.ctl']
    sycdFileName = partPath+'_sycd.chg'
    
    ## Create other files we need for STAMP
    
    # Command file
    f_cmd = open(cmdFileName, 'w')
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
    f_sycd = open(sycdFileName, 'w')
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
        f = open(b,'w')
        f.close()
        
    # Open the dictionary files we are going to create
    f_pf = open(dicFileNameList[0], 'w') # prefixes
    f_if = open(dicFileNameList[1], 'w') # infixes
    f_sf = open(dicFileNameList[2], 'w') # suffixes
    f_rt = open(dicFileNameList[3], 'w') # roots
    f_dec = open(decFileName, 'w') # categories and string (natural) classes 
    
    # need a blank line at the top
    f_rt.write('\n\n') 
    f_pf.write('\n\n') 
    f_if.write('\n\n') 
    f_sf.write('\n\n') 
    f_dec.write('\n') 
    
    #vernWS = TargetDB.GetDefaultVernacularWS()
    #analyWS = TargetDB.GetDefaultAnalysisWS()

    report.Info("Outputting category information...")
    
    # loop through all target categories
    for pos in TargetDB.lp.AllPartsOfSpeech:

        # get abbreviation
        posAbbr = ITsString(pos.Abbreviation.AnalysisDefaultWritingSystem).Text
        f_dec.write('\\ca ' + posAbbr + '\n')
    f_dec.write('\\ca _variant_\n') # for variant entries
    f_dec.write('\n')
    
    report.Info("Outputting natural class information...")
    
    # Write out all the natural classes and the graphemes that they are made up of
    # Loop through all natural classes
    for natClass in TargetDB.lp.PhonologicalDataOA.NaturalClassesOS:
        
        # Get the natural class name and write it out
        natClassName = ITsString(natClass.Abbreviation.AnalysisDefaultWritingSystem).Text
        
        if natClassName:
            f_dec.write('\\scl '+natClassName.encode('utf-8')+'\n')
        
            # Loop through all the segments in the class
            for seg in natClass.SegmentsRC:
    
                # Loop through all the graphemes for each segment
                for graph in seg.CodesOS:
                    # Write out the grapheme string one after another on the line
                    grapheme = ITsString(graph.Representation.VernacularDefaultWritingSystem).Text
                    if not grapheme:
                        report.Warning('Null grapheme found for natural class: '+natClassName+'. Skipping.')
                        continue
                    else:
                        f_dec.write(' '+grapheme.encode('utf-8'))
            f_dec.write('\n')
    f_dec.close()
    
    report.Info("Creating the STAMP dictionaries...")
    
    report.ProgressStart(TargetDB.LexiconNumberOfEntries())
    
    pf_cnt = sf_cnt = if_cnt = rt_cnt = 0
    # Loop through all the entries
    for i,e in enumerate(TargetDB.LexiconAllEntries()):
    
        report.ProgressUpdate(i)
        morphType = ITsString(e.LexemeFormOA.MorphTypeRA.Name.AnalysisDefaultWritingSystem).Text
        
        # If no senses, check if this entry is an inflectional variant and output it
        if e.SensesOS.Count == 0:
            
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
                    f_rt.write('\\m '+headWord.encode('utf-8')+'\n')
                    f_rt.write('\\c '+"_variant_"+'\n')

                    # Process all allomorphs and their environments
                    process_allomorphs(e, f_rt, "", report, 'stem', TargetDB)
                    rt_cnt +=1

        else: # Entry with senses
            # Loop through senses
            for i, mySense in enumerate(e.SensesOS):
                
                gloss = ITsString(mySense.Gloss.AnalysisDefaultWritingSystem).Text
                
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

                
                    # Get the POS abbreviation for the current sense, assuming we have a stem
                    if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        
                        if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:            
                            abbrev = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                  Abbreviation.AnalysisDefaultWritingSystem).Text
                        else:
                            report.Warning('Skipping sense because the POS is unknown: '+\
                                           ' while processing target headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
                            #abbrev = 'unk'
                            continue
                                                  
                    else:
                        report.Warning('Skipping sense that is of class: '+mySense.MorphoSyntaxAnalysisRA.ClassName+\
                                       ' for headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
                    
                    
    
                    # Write out morphname field
                    f_rt.write('\\m '+headWord.encode('utf-8')+'.'+str(i+1)+'\n')
                    f_rt.write('\\c '+abbrev+'\n')
                    
                    # Process all allomorphs and their environments
                    process_allomorphs(e, f_rt, gloss, report, 'stem', TargetDB)
                    rt_cnt +=1
                # Now process non-roots
                else:
                    if gloss == None:
                        report.Warning('No gloss Skipping. Headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
                    elif e.LexemeFormOA == None:
                        report.Warning('No lexeme form. Skipping. Headword: '+ITsString(e.HeadWord).Text, TargetDB.BuildGotoURL(e))
                    elif e.LexemeFormOA.MorphTypeRA == None:
                        report.Warning('No Morph Type. Skipping.'+ITsString(e.HeadWord).Text+' Best Vern: '+\
                                       ITsString(e.LexemeFormOA.Form.VernacularDefaultWritingSystem).Text, TargetDB.BuildGotoURL(e))
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
                                report.Warning('Skipping entry because the morph type is: ' + morphType, TargetDB.BuildGotoURL(e))
                        else:
                            report.Warning('Skipping entry since the lexeme is of type: '+e.LexemeFormOA.ClassName, TargetDB.BuildGotoURL(e))
                    elif morphType not in morphNames:
                        if morphType == 'proclitic':
                            process_allomorphs(e, f_pf, gloss, report, 'non-stem', TargetDB)
                            pf_cnt += 1
                        elif morphType == 'enclitic':
                            process_allomorphs(e, f_sf, gloss, report, 'non-stem', TargetDB)
                            sf_cnt += 1
                        else:
                            report.Warning('Skipping entry because the morph type is: ' + morphType, TargetDB.BuildGotoURL(e))

    f_pf.close() 
    f_if.close() 
    f_sf.close() 
    f_rt.close() 
    f_dec.close()
    
    report.Info("STAMP dictionaries created.")
    report.Info(str(pf_cnt)+' prefixes in the prefix dictionary.')
    report.Info(str(sf_cnt)+' suffixes in the suffix dictionary.')
    report.Info(str(if_cnt)+' infixes in the infix dictionary.')
    report.Info(str(rt_cnt)+' roots in the root dictionary.')
    report.Info("Synthesizing the target text...")

    # run STAMP to sythesize the results. E.g. stamp32" -f Gilaki-Thesis_ctrl_files. txt -i pes_verbs.ana -o pes_verbs.syn
    # this assumes stamp32.exe is in the current working directory.
    call(['stamp32.exe', '-f', cmdFileName, '-i', anaFile, '-o', synFile])
    
    report.Info("Fixing up the target text...")
    
    # Replace underscores with spaces in the Synthesized file
    # Also remove @ signs at the beginning of words and N.N at the end of words if so desired in the configuration file.
    f_s = open(synFile)
    line_list = []
    for line in f_s:
        line_list.append(line)

    f_s.close()
    f_s = open(synFile, 'w')
    for line in line_list:
        line = re.sub('_', ' ', line)
        
        if cleanUpText:
            line = re.sub('\d+\.\d+', '', line)
            line = re.sub('@', '', line)
        f_s.write(line)
    f_s.close()
    
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
