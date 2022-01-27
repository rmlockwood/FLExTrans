#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.3.2 - 1/27/22 - Ron Lockwood
#    Major overhaul of the Setup Transfer Rule Grammatical Categories Tool.
#    Now the setup tool and the bilingual lexicon uses common code for getting
#    the grammatical categories from each lexicon. Fixes #50.
#
#   Version 3.3.1 - 1/25/22 - Ron Lockwood
#    Fixed crash when grammatical category not set for a word.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2.1 - 11/30/21 - Ron Lockwood
#    Report when the bilingual lexicon is up to date (taken from cache).
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Put underscores in target feature abbreviations if necessary.
#
#   Version 3.0.5 - 7/8/21 - Ron Lockwood
#    Handle slash in category name
# 
#   Version 3.0.4 - 7/1/21 - Ron Lockwood
#    Instead of just using the text in the <l> element as the key for finding 
#    lines in the bilingual file, use everything between <l>
#    and </l> including </b>, but remove any <s> elements. This is because sometimes
#    we have a phrase in the replacement file that has a space (/b) and before we would
#    only pick up the text before the space.
#
#   Version 3.0.3 - 4/30/21 - Ron Lockwood
#    Just give one warning for spaces in categories and likewise one warning for
#    periods in categories. Make the "suppressing" message just info. not a warning
#    This cuts down on the number of warning you always have
#    to see if these warnings are prevalent.
#
#   Version 3.0.2 - 2/26/21 - Ron Lockwood
#    Check if the bilingual file is older than the replacement file and if so
#    process everything.
#
#   Version 3.0.1 - 2/15/21 - Ron Lockwood
#    Always process the replacement file, even if the biling file is up-to-date.
#    This will allow changes there to be seen in results every time.
#
#   Version 3.0 - 1/27/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0.2 - 2/4/20 - Ron Lockwood
#    give an error when the target db open fails.
#
#   Version 2.0.1 - 1/22/20 - Ron Lockwood
#    Only do replacement file if the dictionary is out of date.
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.6.2 - 4/5/19 - Ron Lockwood
#    Check if the bilingual dictionary is out of date in respect to the source 
#    and target databases. If not, just process the replacement file. Don't do
#    anything else. This helps performance.
#
#   Version 1.6.1 - 3/27/19 - Ron Lockwood
#    Limit the number of warnings shown for pos abbreviations in the wrong format.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.3.7 - 12/24/17 - Ron Lockwood
#    When processing replacements, don't add symbols that already exist in the
#    bilingual dictionary. Add new lines at then end of comment elements to get
#    multiple lines.
# 
#   Version 1.3.6 - 12/24/17 - Ron
#    Changed the way the replacement file is processed since it is now a fully
#    valid XML file with two section elements for replacing or appending. We 
#    now process both the replacement file and the bilingual file with 
#    ElementTree & Element objects. Loop through objects in both XML files and
#    replace or add entries from the replacement file in the bilingual dic. file.
#
#   Version 1.3.5 - 7/28/17 - Ron
#    Check that there is a valid target POS before processing the POS names and 
#    abbreviations.
#
#   Version 1.3.4 - 1/18/17 - Ron
#    Give a warning if there is a space or an period in a grammatical category.
#    Change the space to an underscore and remove periods.
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
import copy
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

from System import Guid
from System import String

import ReadConfig
import Utils

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from flexlibs.FLExProject import FLExProject, GetProjectNames


DONT_CACHE = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Extract Bilingual Lexicon",
        FTM_Version    : "3.3.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Creates an Apertium-style bilingual lexicon.",               
        FTM_Help   : "",
        FTM_Description:
"""
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

def biling_file_out_of_date(sourceDB, targetDB, bilingFile):
    
    # Build a DateTime object with the FLEx DB last modified date
    flexDate = sourceDB.GetDateLastModified()
    srcDbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
    
    # Build a DateTime object with the FLEx DB last modified date
    flexDate = targetDB.GetDateLastModified()
    tgtDbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
    
    # Get the date of the cache file
    try:
        mtime = os.path.getmtime(bilingFile)
    except OSError:
        mtime = 0
    bilingFileDateTime = datetime.fromtimestamp(mtime)
    
    if srcDbDateTime > bilingFileDateTime or tgtDbDateTime > bilingFileDateTime: # FLEx DB is newer
        return True 
    else: # affix file is newer
        return False

def repl_file_out_of_date(bilingFile, replFile):
    
    # Get the date of the files
    try:
        mtime = os.path.getmtime(bilingFile)
    except OSError:
        mtime = 0
    bilingFileDateTime = datetime.fromtimestamp(mtime)

    try:
        mtime = os.path.getmtime(replFile)
    except OSError:
        mtime = 0
    replFileDateTime = datetime.fromtimestamp(mtime)
    
    if replFileDateTime > bilingFileDateTime: # replacement file is newer
        return True 
    else: 
        return False

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Use the replacement file specified by BilingualDictReplacmentFile in the
# configuration file to replace or add entries in or to the bilingual dictionary.    
# Two types of entries are in the replacement file, replacement entries and append entries.
# These are found in two different section elements. For the replacement entries, the 
# matching lemma in the bilingual file is found and replaced. The old lemma is shown in 
# a comment along with an info. comment that says there was a replacement made there.
# For append entries, they are just added at the end of the section element of the bilingual
# dictionary. For the replacement file to be valid, it has to have all the symbols defined
# in its symbol definition section <sdefs>. This function takes all those symbol definitions
# and adds them to the <sdefs> of the bilingual dictionary. A comment is also added to 
# indicate where the new <sdef> elements start.
def do_replacements(configMap, report, fullPathBilingFile, replFile):

    # See if we need to do replacements
    # See if the config setting is there or if it has valid info.
    if 'BilingualDictOutputFile' not in configMap or configMap['BilingualDictOutputFile'] == '':
        return
    
    # Save a copy of the bilingual dictionary
    shutil.copy2(fullPathBilingFile, fullPathBilingFile+'.old')

    # Parse the replacement file as XML
    try:
        replEtree = ET.parse(replFile)
    except IOError:
        report.Error('There is a problem with the Bilingual Dictionary Replacement File: '+replFile+'. Please check the configuration file setting.')
        return
    
    replMap = {}
    replRoot = replEtree.getroot()
    
    ## Put the replacement entries into a map
    # Get the replacement entries section
    repl_sec = replRoot.find(".//*[@id='replacement']")
    
    # Loop through the entries in this section
    for entry in repl_sec:
        # Get the <l> text which is under the <p> which is under the <e>
        left = entry.find('p/l')
#        replMap[left.text] = entry

        keyLeft = copy.deepcopy(left)

        # remove any symbol elements so we are left with just <l>abcN.N</l> or possibly something with a space <l>abc</b>xyzN.N</l>
        symbolElements = keyLeft.findall('s')
        
        for symb in symbolElements:
            
            keyLeft.remove(symb)
        
        key = ET.tostring(keyLeft, encoding='unicode')
        
        # remove the <l> and </l>
        key = key[3:-4]
    
        replMap[key] = entry
          
    # Read in the bilingual xml file
    try:
        bilingEtree = ET.parse(fullPathBilingFile)
    except IOError:
        report.Error('There is a problem reading the Bilingual Dictionary File: '+fullPathBilingFile+'.')
        return
    
    ## Add in new symbol definitions from the replacement file
    
    bilingRoot = bilingEtree.getroot()
    
    # Get symbol definitions element (sdefs)
    bilingSdefs = bilingRoot.find('sdefs')
    replSdefs = replRoot.find('sdefs')
    
    # Create a map of all the symbol abbreviations in the bilingual dictionary
    sdfMap={}
    for mySdef in bilingSdefs:
        sdfMap[mySdef.attrib['n']]=1
        
    # Add a comment before the new sdefs get added
    comment = ET.Comment('Inserted symbol definitions from replacement file')
    bilingSdefs.append(comment)
    
    # Loop through the replacement sdefs
    for symbol_def in replSdefs:
        
        # if the symbol abbreviation doesn't already exist, add it
        if symbol_def.attrib['n'] not in sdfMap:
            # add the sdef element from repl file to the end of the biling sdefs list
            bilingSdefs.append(symbol_def)
        
    ## Find entries that match replacement entries, comment out the old and insert the new
    
    # Get the section element
    biling_section = bilingRoot.find('section')
    
    # Create a new section element to replace the old
    new_biling_section = ET.Element('section')
    new_biling_section.attrib = biling_section.attrib
    
    # Loop through all the bilingual entries
    for entry in biling_section:
        # Get the left lemma text
        left = entry.find('p/l')
        
        # If we can't find it, use the identity text <e> should either have <p><l></l><r></r></p>) or <i>
        if left == None:
            left = entry.find('i')
        
        # Create string with the old contents of the entry. 
        s = ET.tostring(left, encoding='unicode')
        
        keyLeft = copy.deepcopy(left)

        # remove any symbol elements so we are left with just <l>abcN.N</l> or possibly something with a space <l>abc</b>xyzN.N</l> (same as above)
        symbolElements = keyLeft.findall('s')
        
        for symb in symbolElements:
            
            keyLeft.remove(symb)

        # create the key string
        key = ET.tostring(keyLeft, encoding='unicode')
        
        # remove the <l> and </l>
        key = key[3:-4]
    
        # See if we have a match for replacing the entry
        if key in replMap:
            
            # Create a comment containing the old entry and a note and insert them into the entry list
            comment1 = ET.Comment('This entry was replaced with the one below it from the file ' + replFile + '.\n')
            
#             if left.tag == 'i':
#                 s = 'identity: ' + left.text + ' (' + left.find('s').attrib['n'] + ')'
#             else:
#                 s = 'left: ' + left.text + ' (' + left.find('s').attrib['n'] + ')'
#                 s += ', right: ' + entry.find('p/r').text + ' (' + entry.find('p/r/s').attrib['n'] + ')'
                
            comment2 = ET.Comment(s+'\n')
            
            new_biling_section.append(comment1)
            new_biling_section.append(comment2)
            
            # Insert the new entry from the replacement file map
            new_biling_section.append(replMap[key])
            
        else: # copy the old entry to the new
            new_biling_section.append(entry)
    
    ## Add the entries from the replacement file marked as 'append'
    
    # Get the append entries section
    append_sec = replRoot.find(".//*[@id='append']")
    
    # Make a comment and adds it
    comment = ET.Comment('Custom entries appended below from the file ' + replFile + '.\n')
    new_biling_section.append(comment)
    
    # Loop through these entries
    for entry in append_sec:
        # add them to the list of bilingual entries
        new_biling_section.append(entry)
        
    # Remove the old entries list and add the new
    bilingRoot.remove(biling_section)
    bilingRoot.append(new_biling_section)
    
    # Give whitespace indent TODO: this will only work in python 3.9+
#    ET.indent(bilingEtree)
    
    bilingEtree.write(fullPathBilingFile, encoding='utf-8', xml_declaration=True)
    
    # Insert the DOCTYPE as the 2nd line of the file.
    f = open(fullPathBilingFile, "r", encoding="utf-8")
    contents = f.readlines()
    f.close()
    contents.insert(1, '<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
    f = open(fullPathBilingFile, 'w', encoding="utf-8")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    
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

    TargetDB = Utils.openTargetProject(configMap, report)

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
    
    replFile = ReadConfig.getConfigVal(configMap, 'BilingualDictReplacementFile', report)
    if not replFile:
        return
    
    # If the target database hasn't changed since we created the affix file, don't do anything.
    if not DONT_CACHE and biling_file_out_of_date(DB, TargetDB, bilingFile) == False and repl_file_out_of_date(bilingFile, replFile) == False:
        
        report.Info("The bilingual dictionary is up to date.")
        pass
        
    else: # build the file
        try:
            f_out = open(fullPathBilingFile, 'w', encoding="utf-8")
        except IOError as e:
            report.Error('There was a problem creating the Bilingual Dictionary Output File: '+fullPathBilingFile+'. Please check the configuration file setting.')
    
        report.Info("Outputing category information...")
        
        f_out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f_out.write('<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
        f_out.write('<dictionary>\n')
        f_out.write('  <alphabet/>\n')
        f_out.write('  <sdefs>\n')
        f_out.write('    <sdef n="sent" c="Sentence marker"/>\n')
        
        posMap = {}
        
        # Get all source and target categories
        if Utils.get_categories(DB, TargetDB, report, posMap) == True:
            return

        # save target features so they can go in the symbol definition section
        for feat in TargetDB.lp.MsFeatureSystemOA.FeaturesOC:
            if feat.ClassID == 50: # FsClosedFeature
                for val in feat.ValuesOC:
                    featAbbr = ITsString(val.Abbreviation.BestAnalysisAlternative).Text
                    featName = ITsString(val.Name.BestAnalysisAlternative).Text
                    posMap[Utils.underscores(featAbbr)] = featName
                
        # build string for the xml pos section
        for pos_abbr, pos_name in sorted(list(posMap.items()), key=lambda k_v: (k_v[0].lower(),k_v[1])):
            cat_str = '    <sdef n="'
            # output abbreviation
            cat_str += pos_abbr
            cat_str += '" c="'
            
            # output full category name
            cat_str += pos_name
            cat_str += '"/>\n'
            f_out.write(cat_str)
        
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
                if not re.search('\d$', headWord, re.A): # re.A means ASCII-only matching so that we don't match, for example, a Persian number
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
                                abbrev = 'UNK'
                                                      
                            # If we have a link to a target entry, process it
                            equiv = DB.LexiconGetFieldText(mySense.Hvo, senseEquivField)
                            if equiv != None:
                                
                                # Parse the link to get the guid
                                u = equiv.index('guid')
                                myGuid = equiv[u+7:u+7+36]
                                
                                # Look up the entry in the trgt project
                                repo = TargetDB.project.ServiceLocator.GetInstance(ILexEntryRepository)
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
                                    if not re.search('\d$', targetHeadWord, re.A): # re.A means ASCII-only matching so that we don't match, for example, a Persian number
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
                                            
                                            if targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA:
                                                trgtFound = True
                                                # Get target pos abbreviation
                                                trgtAbbrev = ITsString(targetSense.MorphoSyntaxAnalysisRA.PartOfSpeechRA.\
                                                                      Abbreviation.BestAnalysisAlternative).Text
                                                
                                                # Convert spaces to underscores and remove periods and convert slash to bar
                                                trgtAbbrev = re.sub(r'\s', '_', trgtAbbrev)
                                                trgtAbbrev = re.sub(r'\.', '', trgtAbbrev)
                                                trgtAbbrev = re.sub(r'/', '|', trgtAbbrev)
                                                
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
                                                        featStr += s2 + Utils.underscores(abb) + s4a
                                                
                                                # output the bilingual dictionary line (the sX is xml stuff)
                                                out_str = s1+headWord+'.'+str(i+1)+s2+abbrev+s3+targetHeadWord+'.'+\
                                                          str(trgtSense)+s2+trgtAbbrev+s4a+trgtInflCls+featStr+s4b+'\n'
                                                f_out.write(out_str)
                                                records_dumped_cnt += 1
                                        
                                            else:
                                                report.Warning('Skipping sense because the target POS is undefined '+\
                                                               ' for target headword: '+ITsString(targetEntry.HeadWord).Text+\
                                                               ' while processing source headword: '+ITsString(e.HeadWord).Text, DB.BuildGotoURL(e))
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
                            
                        f_out.write(out_str) 
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
    
        report.Info('Creation complete to the file: '+fullPathBilingFile+'.')
        report.Info(str(records_dumped_cnt)+' records created in the bilingual dictionary.')

        # TODO: Check if the replacement file is out of date        
        # As a last step, replace certain parts of the bilingual dictionary
        if do_replacements(configMap, report, fullPathBilingFile, replFile) == False:
            return
        
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
