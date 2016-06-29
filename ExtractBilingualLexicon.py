#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
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
import tempfile
import shutil
import ReadConfig

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Extract Bilingual Lexicon",
        'moduleVersion'    : "1.3.3",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Creates an Apertium-style bilingual lexicon.",
        'moduleDescription'   :
u"""
The source database should be chosen for this module. This module will create a bilingual 
lexicon for two projects. The
database that FlexTools is set to is your source project. Set the TargetProject
property in the FlexTrans.config file to the name of your target project.
FlexTrans.config should be in the FlexTools folder. This module requires
two sense-level custom fields in your source project. They should be simple text fields.
One is to link to an entry in the target project and the other is to indicate a sense
number number in that entry. Set the FlexTrans.config file properties 
SourceCustomFieldForEntryLink
and SourceCustomFieldForSenseNum to the corresponding custom field names. 
The link field should contain a hyperlink to the target entry. Use the menu
option Edit->Copy Location as Hyperlink in the target project to put the 
hyperlink on the clipboard. The sense number field should correspond to the target 
sense number. The sense number defaults to one if the field is left blank. 
If no link is present in the 
link field, the source entry will be used for the target entry as well. 
Leaving the link field blank is appropriate when the source and target entries
are identical. The kind of root entries that are processed is determined by the configuration 
file property SourceMorphNamesCountedAsRoots. Set this to a comma separated list of the morphnames to 
include. 

The bilingual lexicon will be outputted to the file defined in the BilingualDictOutputFile 
property in the FlexTrans.config file.

You can make custom changes to the bilingual lexicon. To do this, set the FLExTrans.config 
property BilingualDictReplacementFile to the name of a file that contains the custom changes.
A sample file called replace.dix is provided in the installation of FLExTrans. It has three
sections. A section for new lines which will be added to the bilingual lexicon. A section for 
replacing existing lines that are in the bilingual lexicon and a section for adding symbol 
definitions for any of the symbols you are using in the additional or replacement lines. When 
this module is run, the original bilingual lexicon before additions or replacements were made 
is stored 
in the file named according to the BilingualDictReplacementFile property plus ".old".
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

# Use the replacement file specified by BilingualDictReplacmentFile in the
# configuration file to replace lines in the bilingual dictionary.    
# Two types of lines are in the replacement file, <sdef> lines which need to be added to the
# symbol definition section and lemma lines which are inserted and the old lemma lines are
# commented out.
def do_replacements(configMap, report, fullPathBilingFile):

    # See if we need to do replacements
    # See if the config setting is there or if it has valid info.
    if 'BilingualDictOutputFile' not in configMap or configMap['BilingualDictOutputFile'] == '':
        return
    
    #biling = os.path.join(tempfile.gettempdir(), configMap['BilingualDictOutputFile'])
    
    replFile = ReadConfig.getConfigVal(configMap, 'BilingualDictReplacementFile', report)
    if not replFile:
        return
    
    shutil.copy2(fullPathBilingFile, fullPathBilingFile+'.old')
    f_a = open(fullPathBilingFile+'.old')
    f_b = open(fullPathBilingFile,'w')
    try:
        f_r = open(replFile)
    except IOError:
        report.Error('There is a problem with the Bilingual Dictionary Replacement File: '+replFile+'. Please check the configuration file setting.')
        return
    
    replMap = {}
    s_lines = []
    append_lines = []
    insertion_not_done = True
    do_append = False
    
    # First read the replacement file. Comment lines are ignored.
    # Read the additional sdef lines into a list.
    # Read the replacement lines into a map with the lemma as the key
    for line_r in f_r:
        line_r = unicode(line_r, 'utf-8')
        
        g = re.search(r'lines to be appended',line_r)
        if g:
            do_append = True
            
        g = re.search(r'<sdef ',line_r)
        if g:
            s_lines.append(line_r)
            continue
            
        g = re.search(r'<[li]>(.+?)<s',line_r) # get the lemma which is between <l> or <i> and <s...>
        if g:
            if do_append == True:
                append_lines.append(line_r)
            else: # replacement lines
                replMap[g.group(1)] = line_r
    
    # Read through the bilingual dictionary
    for line in f_a:
        line = unicode(line, 'utf-8')
        
        # if we find the first sdef line, insert the ones from the replace file here
        g = re.search(r'<sdef ',line)
        if insertion_not_done and g:
            insertion_not_done = False
            # Leave comments before and after the inserted lines
            f_b.write('<!-- Inserted sdef lines from replace file -->\n')
            for sdef_line in s_lines:
                f_b.write(sdef_line.encode('utf-8'))
            f_b.write('<!-- end of insertion -->\n')
            
        # get current lemma
        g = re.search(r'<[li]>(.+?)<s',line)
        if g:
            # we we match on the current lemma, do the replacement
            if g.group(1) in replMap:
                # Leave a comment before the old line 
                f_b.write('<!-- This line replaced with the one below it from the file ' + replFile + ' -->\n')
                line = line.rstrip()
                # Comment out the old line
                f_b.write('<!-- '+line.encode('utf-8')+'-->\n')
                f_b.write(replMap[g.group(1)].encode('utf-8'))
                continue

        # find the end of the section
        g = re.search(r'/section',line)
        if g:
            # Append the new lines now
            f_b.write('<!-- Custom lines appended below. -->\n')
            for new_line in append_lines:
                f_b.write(new_line.encode('utf-8'))
            
        f_b.write(line.encode('utf-8'))
        
def get_sub_ics(mySubClasses):
    ic_list = []
    for ic in mySubClasses:
        icAbbr = ITsString(ic.Abbreviation.BestAnalysisAlternative).Text
        icName = ITsString(ic.Name.BestAnalysisAlternative).Text
        ic_list.append((icAbbr,icName))
        if ic.SubclassesOC and len(ic.SubclassesOC.ToArray())>0:
            icl = get_sub_ics(ic.SubclassesOC)
            ic_list.extend(icl)
            
    return ic_list

def get_feat_abbr_list(SpecsOC, feat_abbr_list):
    
    for spec in SpecsOC:
        if spec.ClassID == 53: # FsComplexValue
            get_feat_abbr_list(spec.ValueOA.FeatureSpecsOC, feat_abbr_list)
        else: # FsClosedValue - I don't think the other types are in use
            
            featGrpName = ITsString(spec.FeatureRA.Name.BestAnalysisAlternative).Text
            abbValue = ITsString(spec.ValueRA.Abbreviation.BestAnalysisAlternative).Text
            feat_abbr_list.append((featGrpName, abbValue))
    return
            
def MainFunction(DB, report, modifyAllowed):
    # Constants for building the output lines in the dictionary file.
    s1 = '    <e><p><l>'
    s1i ='    <e><i>'
    s2 = '<s n="'
    s3 = '"/></l><r>'
    s4 = '"/></r></p></e>'
    s4a ='"/>'
    s4b='</r></p></e>'
    s4i ='"/></i></e>'

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    catSub = ReadConfig.getConfigVal(configMap, 'CategoryAbbrevSubstitutionList', report)
    linkField = ReadConfig.getConfigVal(configMap, 'SourceCustomFieldForEntryLink', report)
    senseNumField = ReadConfig.getConfigVal(configMap, 'SourceCustomFieldForSenseNum', report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, 'SourceMorphNamesCountedAsRoots', report)
    sentPunct = ReadConfig.getConfigVal(configMap, 'SentencePunctuation', report)
    if not (linkField and senseNumField and sourceMorphNames and sentPunct):
        return
    
    # Transform the straight list of category abbreviations to a list of tuples
    catSubList = []
    if catSub:
        try:
            for i in range(0,len(catSub),2):
                catSubList.append((catSub[i],catSub[i+1]))
        except:
            report.Error('Ill-formed property: "CategoryAbbrevSubstitutionList". Expected pairs of categories.')
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

    # Set objects for the two custom fields. Report errors if they don't exist in the source project.
    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    senseSenseNumField = DB.LexiconGetSenseCustomFieldNamed(senseNumField)
    
    if not (senseEquivField):
        report.Error(linkField + " field doesn't exist. Please read the instructions.")
        return

    if not (senseSenseNumField):
        report.Error(senseNumField + " field doesn't exist. Please read the instructions.")
        return

    bilingFile = ReadConfig.getConfigVal(configMap, 'BilingualDictOutputFile', report)
    if not bilingFile:
        return
    
    fullPathBilingFile = bilingFile
    #fullPathBilingFile = os.path.join(tempfile.gettempdir(), bilingFile)
    #f_out = open(fullPathBilingFile, 'w')
    
    try:
        f_out = open(fullPathBilingFile, 'w')
    except IOError as e:
        report.Error('There was a problem creating the Bilingual Dictionary Output File: '+fullPathBilingFile+'. Please check the configuration file setting.')

    report.Info("Outputing category information...")
    
    f_out.write('<dictionary>\n')
    f_out.write('  <alphabet/>\n')
    f_out.write('  <sdefs>\n')
    f_out.write('    <sdef n="sent" c="Sentence marker"/>\n')
    
    posMap = {}
    abbrevError = False
    
    # loop through all source categories
    for pos in DB.lp.AllPartsOfSpeech:

        # save abbreviation
        posAbbr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text
        posMap[posAbbr] = pos.ToString()
        
        # give an error if there is a space in the category abbreviation, STAMP can't handle it.
        if re.search(r'\s', posAbbr):
            report.Error("The abbreviation: '"+posAbbr+"' for category: '"+pos.ToString()+"' can't have a space in it. Please correct this in the source database.")
            abbrevError = True
    
    # loop through all target categories
    for pos in TargetDB.lp.AllPartsOfSpeech:

        # save abbreviation
        posAbbr = ITsString(pos.Abbreviation.BestAnalysisAlternative).Text

        # give an error if there is a space in the category abbreviation, STAMP can't handle it.
        if re.search(r'\s', posAbbr):
            report.Error("The abbreviation: '"+posAbbr+"' for category: '"+pos.ToString()+"' can't have a space in it. Please correct this in the target database.")
            abbrevError = True
            
        if posAbbr not in posMap:
            posMap[posAbbr] = pos.ToString()
        else:
            # If we already have the abbreviation in the map and the full category name
            # is not the same as the source one, append the target one to the source one
            if posMap[posAbbr] != pos.ToString():
                posMap[posAbbr] += ' / ' + pos.ToString()

        # save inflection classes, save them along with pos's since they also need to go into the symbol definition section
        if pos.InflectionClassesOC and len(pos.InflectionClassesOC.ToArray())>0:
            AN_list = get_sub_ics(pos.InflectionClassesOC)
            for icAbbr, icName in AN_list:
                posMap[icAbbr] = icName
    
    # Exit after showing all abbreviation errors            
    if abbrevError:
        return
    
    # save target features so they can go in the symbol definition section
    for feat in TargetDB.lp.MsFeatureSystemOA.FeaturesOC:
        if feat.ClassID == 50: # FsClosedFeature
            for val in feat.ValuesOC:
                featAbbr = ITsString(val.Abbreviation.BestAnalysisAlternative).Text
                featName = ITsString(val.Name.BestAnalysisAlternative).Text
                posMap[featAbbr] = featName
            
    # build string for the xml pos section
    for pos_abbr, pos_name in sorted(posMap.items(), key=lambda(k, v): (k.lower(),v)):
        cat_str = '    <sdef n="'
        # output abbreviation
        cat_str += pos_abbr
        cat_str += '" c="'
        
        # output full category name
        cat_str += pos_name
        cat_str += '"/>\n'
        f_out.write(cat_str.encode('utf-8'))
    
    f_out.write('  </sdefs>\n\n')
    f_out.write('  <section id="main" type="standard">\n')
    
    report.Info("Building the bilingual dictionary...")
    records_dumped_cnt = 0
    report.ProgressStart(DB.LexiconNumberOfEntries())
  
    # Loop through all the entries
    for entry_cnt,e in enumerate(DB.LexiconAllEntries()):
    
        report.ProgressUpdate(entry_cnt)
        
        # Don't process affixes, clitics
        if e.LexemeFormOA and \
           e.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           e.LexemeFormOA.MorphTypeRA and ITsString(e.LexemeFormOA.\
           MorphTypeRA.Name.BestAnalysisAlternative).Text in sourceMorphNames:
        
            # Set the headword value and the homograph #
            headWord = re.sub(r' ', r'<b/>',ITsString(e.HeadWord).Text)
            
            # If there is not a homograph # at the end, make it 1
            if not re.search('(\d$)', headWord):
                headWord += '1'
            
            # Loop through senses
            for i, mySense in enumerate(e.SensesOS):
                
                trgtFound = False
                
                # Make sure we have a valid analysis object
                if mySense.MorphoSyntaxAnalysisRA:
                
                    # Get the POS abbreviation for the current sense, assuming we have a stem
                    if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                        
                        if mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:            
                            abbrev = ITsString(mySense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                  Abbreviation.BestAnalysisAlternative).Text
                        else:
                            report.Warning('Skipping sense because the POS is unknown: '+\
                                           ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                            #abbrev = 'unk'
                                                  
                        # If we have a link to a target entry, process it
                        equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
                        if equiv != None:
                            
                            # Parse the link to get the guid
                            u = equiv.index('guid')
                            myGuid = equiv[u+7:u+7+36]
                            
                            # Look up the entry in the trgt project
                            repo = TargetDB.db.ServiceLocator.GetInstance(ILexEntryRepository)
                            guid = Guid(String(myGuid))
    
                            try:
                                targetEntry = repo.GetObject(guid)
                            except:
                                report.Error('Skipping sense because the link to the target entry is invalid: '+\
                                             ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                                continue
                            
                            if targetEntry:
                                
                                # Set the target headword value and the homograph #
                                targetHeadWord = re.sub(r' ', r'<b/>',ITsString(targetEntry.HeadWord).Text)
                                
                                # If there is not a homograph # at the end, make it 1
                                if not re.search('(\d$)', targetHeadWord):
                                    targetHeadWord += '1'
                                
                                # An empty sense number means default to sense 1
                                senseNum = DB.LexiconGetFieldText(mySense.Hvo, senseSenseNumField)
                                if senseNum == None:
                                    trgtSense = 1
                                elif is_number(senseNum):
                                    trgtSense = int(senseNum)
                                else:
                                    report.Warning('Sense number: '+trgtSense+\
                                                   ' is not valid for target headword: '+\
                                                   ITsString(targetEntry.HeadWord).Text+\
                                                   ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                                
                                # Make sure that sense number is valid    
                                if targetEntry.SensesOS and trgtSense <= targetEntry.SensesOS.Count:
                                
                                    # Get the POS abbreviation for the target sense, assuming we have a stem
                                    targetSense = targetEntry.SensesOS.ToArray()[trgtSense-1]
                                    if targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                                        
                                        trgtFound = True
                                        # Get target pos abbreviation
                                        trgtAbbrev = ITsString(targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                              Abbreviation.BestAnalysisAlternative).Text
                                        
                                        # Get target inflection class
                                        trgtInflCls =''
                                        if targetSense.MorphoSyntaxAnalysisRA.InflectionClassRA:
                                            trgtInflCls = s2+ITsString(targetSense.MorphoSyntaxAnalysisRA.InflectionClassRA.\
                                                                  Abbreviation.BestAnalysisAlternative).Text+s4a         
                                        
                                        # Get target features                                                     
                                        featStr = ''
                                        if targetSense.MorphoSyntaxAnalysisRA.MsFeaturesOA:
                                            feat_abbr_list = []
                                            # The features might be complex, make a recursive function call to find all leaf features
                                            get_feat_abbr_list(targetSense.MorphoSyntaxAnalysisRA.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
                                            
                                            # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                            for grpName, abb in sorted(feat_abbr_list, key=lambda x: x[0]):
                                                featStr += s2 + abb + s4a
                                        
                                        # output the bilingual dictionary line (the sX is xml stuff)
                                        out_str = s1+headWord+'.'+str(i+1)+s2+abbrev+s3+targetHeadWord+'.'+\
                                                  str(trgtSense)+s2+trgtAbbrev+s4a+trgtInflCls+featStr+s4b+'\n'
                                        f_out.write(out_str.encode('utf-8'))
                                        records_dumped_cnt += 1
                                    else:
                                        report.Warning('Skipping sense because it is of this class: '+targetSense.MorphoSyntaxAnalysisRA.ClassName+\
                                                       ' for target headword: '+ITsString(targetEntry.HeadWord).Text+\
                                                       ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                                else:
                                    if targetEntry.SensesOS == None:
                                        report.Warning('No sense found for the target headword: '+ITsString(targetEntry.HeadWord).Text+\
                                                       ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                                    elif trgtSense > targetEntry.SensesOS.Count:
                                        report.Warning('Sense number: '+str(trgtSense)+\
                                                       ' is not valid. That many senses do not exist for target headword: '+\
                                                       ITsString(targetEntry.HeadWord).Text+\
                                                       ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                            else:
                                report.Warning('Target entry not found. This target GUID does not exist: '+myGuid+\
                                               ' while processing headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                        else:
                            pass
                            # Don't report this. Most of the time the equivalent field will be empty.
                            #report.Warning('Target language equivalent field is null while processing headword: '+ITsString(e.HeadWord).Text)
                    else:
                        report.Warning('Skipping sense that is of class: '+mySense.MorphoSyntaxAnalysisRA.ClassName+\
                                       ' for headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                else:
                    report.Warning('Skipping sense, no analysis object'\
                                       ' for headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
                if not trgtFound:
                    # output the bilingual dictionary line -- source and target are the same
                    
                    # do substitutions of categories. This is for standard substitutions where 
                    # the target category name is different even though essentially the categories are equivalent.
                    out_str = ''
                    for tup in catSubList:
                        if tup[0] == abbrev:
                            temp_str = headWord + '.'+str(i+1)
                            out_str = s1+temp_str+s2+tup[0]+s3+temp_str+s2+tup[1]+s4+'\n'
                            break
                        
                    if out_str == '':
                        out_str = headWord+'.'+str(i+1)+s2+abbrev        
                        out_str = s1i+out_str+s4i+'\n'
                        
                    f_out.write(out_str.encode('utf-8')) 
                    records_dumped_cnt += 1   
                    
        else:
            if e.LexemeFormOA == None:
                report.Warning('No lexeme form. Skipping. Headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
            elif e.LexemeFormOA.ClassName != 'MoStemAllomorph':
                # We've documented that affixes are skipped. Don't report this
                #report.Warning('Skipping entry since the lexeme is of type: '+e.LexemeFormOA.ClassName)
                pass
            elif e.LexemeFormOA.MorphTypeRA == None:
                report.Warning('No Morph Type. Skipping.'+ITsString(e.HeadWord).Text+' Best Vern: '+ITsString(e.LexemeFormOA.Form.BestVernacularAlternative).Text, DB.BuildGotoURL(e))
            elif ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text not in ('stem','bound stem','root','phrase'):
                # Don't report this. We've documented it.
                #report.Warning('Skipping entry because the morph type is: '+\
                               #ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text, DB.BuildGotoURL(e))
                pass
       
    f_out.write('    <!-- SECTION: Punctuation -->\n')
    
    # Create a regular expression string for the punctuation characters
    # Note that we have to escape ? + * | if they are found in the sentence-final punctuation
    reStr = re.sub(r'([+?|*])',r'\\\1',sentPunct)
    reStr = '['+reStr+']+'
    
    # This notation in Apertium basically means that any combination of the given punctuation characters
    # with the tag <sent> will be substituted with the same thing plus the <sent> tag.
    f_out.write('   <e><re>' + reStr + '</re><p><l><s n="sent"/></l><r><s n="sent"/></r></p></e>\n')
    f_out.write('  </section>\n')
    f_out.write('</dictionary>\n')
    f_out.close()
    
    # As a last step, replace certain parts of the bilingual dictionary
    if do_replacements(configMap, report, fullPathBilingFile) == False:
        return
        
    report.Info('Creation complete to the file: '+fullPathBilingFile+'.')
    report.Info(str(records_dumped_cnt)+' records created in the bilingual dictionary.')
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
