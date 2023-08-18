#
#   ExtractBilingualLexicon
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 3.9.8 - 8/18/23 - Ron Lockwood
#    More changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.7 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9.6 - 7/17/23 - Ron Lockwood
#    Fixes #66. Use human-readable hyperlinks in the target equivalent custom field.
#
#   Version 3.9.5 - 7/4/23 - Ron Lockwood
#    Don't give an error if the sense custom field link setting is not there.
#
#   Version 3.9.4 - 7/3/23 - Ron Lockwood
#    Fixes #326. Use sense guids in links while maintaining backward compatibility with entry guids.
#
#   Version 3.9.3 - 6/19/23 - Ron Lockwood
#    Fixes #439. Error check after searching for the id 'replacement' or 'append'
#
#   Version 3.9.2 - 6/19/23 - Ron Lockwood
#    Fixes #387. If a replacement entry has a space, turn that into a </b> in the bilingual lexicon.
#    It's expected the user will use a normal space when needed for a lemma in the replacement file.
#
#   Version 3.9.1 - 6/3/23 - Ron Lockwood
#    Fixes #441. Catch a exception when writing the bilingual lexicon with ElementTree.
#
#   Version 3.8.4 - 5/5/23 - Ron Lockwood
#    Change Fatal error to Warning.
#
#   Version 3.8.3 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.2 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8.1 - 4/7/23 - Ron Lockwood
#    Change module name from Extract... to Build...
#
#   Version 3.8 - 4/7/23 - Ron Lockwood
#    Don't give the full path of the replacement file in the xml comment of the bilingual lexicon file.
#
#   Version 3.7.5 - 2/7/23 - Ron Lockwood
#    Fixes #390. Words that are linked to **none** now get a blank mapping in the bilingual
#    dictionary. This allows them to be deleted by default, or they can be overridden by 
#    replacement file entries.
#
#   Version 3.7.4 - 2/6/23 - Ron Lockwood
#    Use flags=re.RegexFlag.A, without flags it won't do what we expect
#
#   Version 3.7.3 - 1/18/23 - Ron Lockwood
#    Fixed bug where report was None in the do_replacements function and a warning was
#    attempted to be outputted. Have LinkSenseTool call extract_bilingual_lex with a report object.
#
#   Version 3.7.2 - 1/7/23 - Ron Lockwood
#    Fixes #214. Give a warning for replacement file entries that couldn't be
#    found in the bilingual lexicon.
#
#   Version 3.7.1 - 12/25/22 - Ron Lockwood
#    Added RegexFlag before re constants
#
#   Version 3.7 - 12/12/22 - Ron Lockwood
#    Skip entries that are mapped to the 'none' headword
#
#   Version 3.6.3 - 9/1/22 - Ron Lockwood
#    Fixes #254. Convert * to _ in stems.
#
#   Version 3.6.2 - 8/26/22 - Ron Lockwood
#    Fixes #215 Check morpheme type against guid in the object instead of
#    the analysis writing system so we aren't dependent on an English WS.
#
#   Version 3.6.1 - 8/19/22 - Ron Lockwood
#    Use new new function getXMLEntryText which should be more efficient.
#
#   Version 3.6 - 8/11/22 - Ron Lockwood
#    Fixes #65. Decompose the replacement file before combining with bilingual lexicon.
#
#   Version 3.5.4 - 8/8/22 - Ron Lockwood
#    Fixes #142. Warn when entries start with a space.
#
#   Version 3.5.3 - 7/9/22 - Ron Lockwood
#    Use a new config setting for using cache. Fixes #115.
#
#   Version 3.5.2 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.1 - 6/22/22 - Ron Lockwood
#    Change in FlexTools 2.1 means that an empty string gets returned now from
#    a custom field that has nothing in it. Before it was None. Fixes #156
#
#   Version 3.5 - 4/1/22 - Ron Lockwood
#    Put the code that does the main work into its own function so it can be
#    called by the Live Rule Tester. This means that a possible null report 
#    object is passed in. Also use an error list in the new function instead of
#    report object. Output collected errors at the end. Fixes #37
#
#   Version 3.4.2 - 3/11/22 - Ron Lockwood
#    Give errors if biling lex file or replacement file values not found in the
#    configuration file.
#    Fixed bug where the old style replacement file wasn't doing the append section
#    correctly.
#
#   Version 3.4.1 - 3/4/22 - Ron Lockwood
#    Set abbrev variable in the main loop to prevent crash shown in issue #79.
#    Also put out UNK as a symbol in the symbol definitions for the
#    bilingual.dix file. Simplified building the sdef string.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.3 - 2/4/22 - Ron Lockwood
#    Changed replacement file to a different format for improved editing. Handle
#    either the old format or the new which uses new elements <leftdata> <rightdata>
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
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

from System import Guid
from System import String

from SIL.LCModel import (
    IMoStemMsa,
    IFsClosedFeature,
    FsClosedFeatureTags,
    ILexEntry,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString         

from flextoolslib import *                                                 

import ReadConfig
import Utils

DONT_CACHE = True

DICTIONARY = 'dictionary'
REPLDICTIONARY = 'repldictionary'

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Build Bilingual Lexicon",
        FTM_Version    : "3.9.8",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Builds an Apertium-style bilingual lexicon.",               
        FTM_Help   : "",
        FTM_Description:
"""
This module will build a bilingual 
lexicon for two projects. The
database that FlexTools is set to is your source project. Set the Target Project
in Settings to the name of your target project.
This module builds the bilingual lexicon based on the links from source senses to target senses
that are in your source project. Use the Sense Linker Module to create these link.

You can make custom changes to the bilingual lexicon by using a replacement file. See the help
document for more details.
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

def get_repl_entry_key(left, newDocType):
    
    if newDocType == True:
        
        key = ''
        
        # Build a key from leftdata text and possible space (<b />) elements (symbol <s> elements get skipped)
        for myElement in left:
            
            if myElement.tag == 'leftdata':
                
                key += myElement.text
                
            elif myElement.tag == 'b':
                
                key += ET.tostring(myElement, encoding='unicode')
    else:
        
        # Get just the text part of the left entry. Note: it's not as easy as left.text
        key = Utils.getXMLEntryText(left)
            
    return key

def doWeHaveNewDocType(tmpReplFile, report, replFile):
        
    newDocType = True
    
    f = open(tmpReplFile, encoding='utf-8')
    
    # Read two lines
    f.readline()
    line = f.readline()
    f.close()
    
    # Remove the temp file
    os.remove(tmpReplFile)
    
    toks = line.split()

    if len(toks) < 1:
        if report:
            report.Error('There is a problem with the Bilingual Dictionary Replacement File: '+replFile+'. No DOCTYPE found.')
        return True, newDocType

    if toks[1] == REPLDICTIONARY:
        
        newDocType = True
        
    elif toks[1] == DICTIONARY:
    
        newDocType = False
        
    else:
        if report:
            
            report.Error('There is a problem with the Bilingual Dictionary Replacement File: '+replFile+'. No DOCTYPE found.')
            
        return True, newDocType
    
    return False, newDocType
        
def createReplMap(repl_sec, newDocType):    
    
    replMap = {}
    
    # Loop through the entries in this section
    for entry in repl_sec:
        
        # Get the <l> text which is under the <p> which is under the <e>
        left = entry.find('p/l')
        
        key = get_repl_entry_key(left, newDocType)
        
        replMap[key] = entry
        
    return replMap
          
def addNewSymbols(bilingRoot, replRoot):
        
    # Get symbol definitions element (sdefs)
    bilingSdefs = bilingRoot.find('sdefs')
    replSdefs = replRoot.find('sdefs')
    
    # Create a map of all the symbol abbreviations in the bilingual dictionary
    sdfMap={}
    
    for mySdef in bilingSdefs:
        
        sdfMap[mySdef.attrib['n']] = 1
        
    # Add a comment before the new sdefs get added
    comment = ET.Comment('Inserted symbol definitions from replacement file')
    bilingSdefs.append(comment)
    
    # Loop through the replacement sdefs
    for symbol_def in replSdefs:
        
        # if the symbol abbreviation doesn't already exist, add it
        if symbol_def.attrib['n'] not in sdfMap:
            
            # add the sdef element from repl file to the end of the biling sdefs list
            bilingSdefs.append(symbol_def)

def processReplacementEntries(biling_section, replMap, newDocType, replFile, report):
        
    # Create a new section element to replace the old
    new_biling_section = ET.Element('section')
    new_biling_section.attrib = biling_section.attrib
    
    foundKeys = []
    
    # Loop through all the bilingual entries
    for entry in biling_section:
        
        # Get the left lemma text
        left = entry.find('p/l')
        
        # If we can't find it, use the identity text <e> should either have <p><l></l><r></r></p>) or <i>
        if left == None:
            
            left = entry.find('i')
        
        # Create string with the old contents of the entry. 
        oldEntryStr = ET.tostring(entry, encoding='unicode')
        
        # Get just the text part of the left entry. Note: it's not as easy as left.text
        key = Utils.getXMLEntryText(left)
                
        # See if we have a match for replacing the entry
        if key in replMap:
            
            # Create a comment containing the old entry and a note and insert them into the entry list
            comment1 = ET.Comment('This entry was replaced with the one below it from the file: ' + os.path.basename(replFile) + '.\n')
            
            comment2 = ET.Comment(oldEntryStr+'\n')
            
            new_biling_section.append(comment1)
            new_biling_section.append(comment2)
            
            if newDocType:
                replEntry = convert_to_biling_style_entry(replMap[key])
            else:
                replEntry = replMap[key]
                
            # Insert the new entry from the replacement file map
            new_biling_section.append(replEntry)
            
            # Keep a list of the ones we found in the replacement file map so we can give warnings for replacement file keys that weren't found
            foundKeys.append(key)
            
        else: # copy the old entry to the new
            new_biling_section.append(entry)
    
    # Give a warning for keys in the replacement file that weren't found
    for key in list(set(replMap.keys()) - set(foundKeys)):
        
        # Ignore the default entry that gets installed
        if key != 'SourceWord1.1':
        
            if report: # could be None
            
                report.Warning(f'The replacement file entry {key} was not found in the bilingual lexicon.')
        
    return new_biling_section
    
def processAppendEntries(new_biling_section, replFile, replRoot, newDocType):
        
    # Make a comment and adds it
    comment = ET.Comment('Custom entries appended below from the file ' + os.path.basename(replFile) + '.\n')
    new_biling_section.append(comment)
    
    # Get the append entries section
    append_sec = replRoot.find(".//*[@id='append']")

    if append_sec == None:

        return True
    
    # Loop through append entries
    for entry in append_sec:
        
        # add them to the list of bilingual entries
        if newDocType:
            new_biling_section.append(convert_to_biling_style_entry(entry))
        else:
            new_biling_section.append(entry)
        
def insertDocType(fullPathBilingFile):
        
    f = open(fullPathBilingFile, "r", encoding="utf-8")
    contents = f.readlines()
    f.close()
    
    contents.insert(1, '<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
    
    f = open(fullPathBilingFile, 'w', encoding="utf-8")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    
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
        
        return True
    
    # Save a copy of the bilingual dictionary
    shutil.copy2(fullPathBilingFile, fullPathBilingFile+'.old')

    # Make a temporary copy of the replacement file so we can decompose it
    tmpReplFile = replFile+'.tmp'
    shutil.copy2(replFile, tmpReplFile)

    # Convert the replacement file to decomposed (NFD)
    Utils.decompose(tmpReplFile)
    
    # Parse the replacement file as XML
    try:
        replEtree = ET.parse(tmpReplFile)
        
    except IOError:
        
        if report:
            
            report.Error('There is a problem with the Bilingual Dictionary Replacement File: '+replFile+'. Please check the configuration file setting.')
            
        return True
    
    # Determine the Doctype. The old type was dictionary the new is repldictionary
    haveErr, newDocType = doWeHaveNewDocType(tmpReplFile, report, replFile)
    
    if haveErr:
        return

    # Get the replacement entries section
    replRoot = replEtree.getroot()
    repl_sec = replRoot.find(".//*[@id='replacement']")

    if repl_sec == None:

        report.Error(f'Could not find the id "replacement" in the Replacement File: {replFile}')
        return True
    
    # Put the replacement entries into a map
    replMap = createReplMap(repl_sec, newDocType)
    
    # Read in the bilingual xml file
    try:
        bilingEtree = ET.parse(fullPathBilingFile)
        
    except IOError:
        
        if report:
            
            report.Error('There is a problem reading the Bilingual Dictionary File: '+fullPathBilingFile+'.')
            
        return True
    
    # Add in new symbol definitions from the replacement file
    bilingRoot = bilingEtree.getroot()
    addNewSymbols(bilingRoot, replRoot)

    # Get the section element
    biling_section = bilingRoot.find('section')
    
    # Find entries that match replacement entries, comment out the old and insert the new
    new_biling_section = processReplacementEntries(biling_section, replMap, newDocType, replFile, report)

    # Add the entries from the replacement file marked as 'append'
    processAppendEntries(new_biling_section, replFile, replRoot, newDocType)

    # Remove the old entries list and add the new
    bilingRoot.remove(biling_section)
    bilingRoot.append(new_biling_section)
    
    # Give whitespace indent TODO: this will only work in python 3.9+
#    ET.indent(bilingEtree)
    
    try:
        bilingEtree.write(fullPathBilingFile, encoding='utf-8', xml_declaration=True)
    except:

        if report:
            
            report.Error('There is a problem writing the Bilingual Dictionary File: '+fullPathBilingFile+'.')
            
        return True
    
    # Insert the DOCTYPE as the 2nd line of the file.
    insertDocType(fullPathBilingFile)
    
    return False

# convert from a <e> element that has <leftdata> and <rightdata> under <l> and <r> to one that doesn't have these
# <b /> elements could be between multiple <leftdata> or <rightdata> elements and should come out something like
# <l>source<b />word1.1<s n="v"></s></l> same kind of thing for <r>
def convert_to_biling_style_entry(replStyleEntry):
    
    newEntry = ET.Element('e')
    pEl = ET.Element('p')
    lEl = ET.Element('l')
    rEl = ET.Element('r')
    
    newEntry.append(pEl)
    pEl.append(lEl)
    pEl.append(rEl)
    
    newSide = [lEl, rEl]
    
    replP = replStyleEntry.find('p')
    
    if replP:
        
        replL = replP.find('l')
        replR = replP.find('r')
        
        if replL and replR:
            
            # put both <l> and <r> in a list so we can process them the same
            for i, side in enumerate([replL, replR]): 
                
                firstData = True
                
                for myElem in side:
                    
                    if myElem.tag == 'b':
                        
                        bEl = ET.Element('b')
                        newSide[i].append(bEl)
                        
                    elif re.search('data', myElem.tag):
                        
                        if firstData:
                            
                            # See if there's a space in the data
                            if myElem.text and re.search(r'\s+', myElem.text):

                                # Get the tokens on each side of the spaces
                                tokens = re.split(r'\s+', myElem.text)

                                # Loop through the tokens
                                for j, token in enumerate(tokens):

                                    # First token, set the l or r text attribute
                                    if j == 0:
                                        newSide[i].text = token
                                    
                                    # Subsequent tokens, create a <b> element and set its tail to the token
                                    else:
                                        bEl2 = ET.Element('b')
                                        newSide[i].append(bEl2)
                                        bEl2.tail = token
                            else:
                                newSide[i].text = myElem.text

                            firstData = False
                        else:
                            bEl.tail = myElem.text
                    
                    # other elements (like <s>)
                    else:
                        newSide[i].append(myElem)
    return newEntry
    
def processSpaces(headWord, DB, srcEntry, error_list):
    
    # Check for preceding or ending spaces
    strippedHeadword = headWord.strip()
    
    if strippedHeadword != headWord.strip():
        
        # Give a warning if there were spaces, but use the stripped version
        error_list.append(('Found an entry with preceding or trailing spaces while processing source headword: '\
                           + ITsString(srcEntry.HeadWord).Text +'. The spaces were removed, but please correct this in the lexicon', 1, DB.BuildGotoURL(srcEntry)))
    
    # Substitute any medial spaces with <b/> (blank space element)    
    headWord = re.sub(r' ', r'<b/>', strippedHeadword)
    
    return headWord

def extract_bilingual_lex(DB, configMap, report=None, useCacheIfAvailable=False):
    
    error_list = []
    
    # Constants for building the output lines in the dictionary file.
    s1 = '    <e><p><l>'
    s1i ='    <e><i>'
    s2 = '<s n="'
    s3 = '"/></l><r>'
    s4 = '"/></r></p></e>'
    s4a ='"/>'
    s4b='</r></p></e>'
    s4i ='"/></i></e>'

    catSub           = ReadConfig.getConfigVal(configMap, ReadConfig.CATEGORY_ABBREV_SUB_LIST, report)
    linkField        = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    senseNumField    = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_SENSE_NUM, report, giveError=False)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)
    sentPunct        = ReadConfig.getConfigVal(configMap, ReadConfig.SENTENCE_PUNCTUATION, report)
    
    if not (linkField and sourceMorphNames and sentPunct):
        return error_list
    
    # Transform the straight list of category abbreviations to a list of tuples
    catSubList = []
    if catSub:
        try:
            for i in range(0,len(catSub),2):
                catSubList.append((catSub[i],catSub[i+1]))
        except:
            error_list.append(('Ill-formed property: "CategoryAbbrevSubstitutionList". Expected pairs of categories.', 2))
            return error_list

    # Set objects for the two custom fields. Report errors if they don't exist in the source project.
    custSenseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    custSenseNumField = DB.LexiconGetSenseCustomFieldNamed(senseNumField)
    
    if not (custSenseEquivField):
        error_list.append((f"Custom field: {linkField} doesn't exist. Please read the instructions.", 2))
        return error_list

    bilingFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not bilingFile:
        error_list.append((f'A value for {ReadConfig.BILINGUAL_DICTIONARY_FILE} not found in the configuration file.', 2))
        return error_list
    
    fullPathBilingFile = bilingFile
    
    replFile = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE, report)
    if not replFile:
        error_list.append((f'A value for {ReadConfig.BILINGUAL_DICT_REPLACEMENT_FILE} not found in the configuration file.', 2))
        return error_list
    
    TargetDB = Utils.openTargetProject(configMap, report)

    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        error_list.append((f'A value for {ReadConfig.CACHE_DATA} not found in the configuration file.', 2))
        return error_list
    
    if cacheData == 'y':
        
        DONT_CACHE = False
    else:
        DONT_CACHE = True
    
    # If the target database hasn't changed since we created the affix file, don't do anything.
    if not DONT_CACHE and useCacheIfAvailable and biling_file_out_of_date(DB, TargetDB, bilingFile) == False and repl_file_out_of_date(bilingFile, replFile) == False:
        
        error_list.append(("The bilingual dictionary is up to date.", 0))
        pass
        
    else: # build the file
        try:
            f_out = open(fullPathBilingFile, 'w', encoding="utf-8")
        except IOError as err:
            error_list.append(('There was a problem creating the Bilingual Dictionary Output File: '+fullPathBilingFile+'. Please check the configuration file setting.', 2))
    
        error_list.append(("Outputing category information...", 0))
        
        f_out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f_out.write('<!DOCTYPE dictionary PUBLIC "-//XMLmind//DTD dictionary//EN" "dix.dtd">\n')
        f_out.write('<dictionary>\n')
        f_out.write('  <alphabet/>\n')
        f_out.write('  <sdefs>\n')
        f_out.write('    <sdef n="sent" c="Sentence marker"/>\n')
        
        posMap = {}
        
        # Get all source and target categories
        if Utils.get_categories(DB, report, posMap, TargetDB) == True:
            
            error_list.append(('Error retrieving categories.'), 2)
            TargetDB.CloseProject()
            return error_list

        # save target features so they can go in the symbol definition section
        for feat in TargetDB.lp.MsFeatureSystemOA.FeaturesOC:
            if feat.ClassID == FsClosedFeatureTags.kClassId: # FsClosedFeature
                for val in IFsClosedFeature(feat).ValuesOC:
                    featAbbr = ITsString(val.Abbreviation.BestAnalysisAlternative).Text
                    featName = ITsString(val.Name.BestAnalysisAlternative).Text
                    posMap[Utils.underscores(featAbbr)] = featName
                
        # build string for the xml pos section
        for pos_abbr, pos_name in sorted(list(posMap.items()), key=lambda k_v: (k_v[0].lower(),k_v[1])):
            
            # output abbreviation and full category name
            cat_str = f'    <sdef n="{pos_abbr}" c="{pos_name}"/>\n'
            f_out.write(cat_str)
        
        # write symbol for UNK
        cat_str = '    <sdef n="UNK" c="Unknown"/>\n'
        f_out.write(cat_str)
        
        f_out.write('  </sdefs>\n\n')
        f_out.write('  <section id="main" type="standard">\n')
        
        error_list.append(("Building the bilingual dictionary...", 0))
        records_dumped_cnt = 0
        if report:
            report.ProgressStart(DB.LexiconNumberOfEntries())
      
        # Loop through all the entries
        for entry_cnt,srcEntry in enumerate(DB.LexiconAllEntries()):
        
            if report:
                report.ProgressUpdate(entry_cnt)
            
            # Don't process affixes, clitics
            if srcEntry.LexemeFormOA and srcEntry.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
               srcEntry.LexemeFormOA.MorphTypeRA and Utils.morphTypeMap[srcEntry.LexemeFormOA.MorphTypeRA.Guid.ToString()] in sourceMorphNames:
            
                # Get the headword string
                headWord = ITsString(srcEntry.HeadWord).Text
                
                # Deal with spaces in the headword
                headWord = processSpaces(headWord, DB, srcEntry, error_list)
                
                # If there is not a homograph # at the end, make it 1
                headWord = Utils.add_one(headWord)
                
                # Convert problem chars in the headWord
                headWord = Utils.convertProblemChars(headWord, Utils.lemmaProbData)
                
                # Loop through senses
                for i, mySense in enumerate(srcEntry.SensesOS):
                    
                    trgtFound = False
                    abbrev = 'UNK'
                    
                    # Make sure we have a valid analysis object
                    if mySense.MorphoSyntaxAnalysisRA:
                    
                        # Get the POS abbreviation for the current sense, assuming we have a stem
                        if mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                            msa = IMoStemMsa(mySense.MorphoSyntaxAnalysisRA)
                            if msa.PartOfSpeechRA:            
                                abbrev = ITsString(msa.PartOfSpeechRA.\
                                                      Abbreviation.BestAnalysisAlternative).Text
                                                      
                                abbrev = Utils.convertProblemChars(abbrev, Utils.catProbData)
                            else:
                                error_list.append(('Skipping sense because the POS is unknown: '+\
                                               ' while processing source headword: '+ITsString(srcEntry.HeadWord).Text, 1, DB.BuildGotoURL(srcEntry)))
                                abbrev = 'UNK'
                                                      
                            # If we have a link to a target entry, process it
#                            equiv = DB.LexiconGetFieldText(mySense.Hvo, custSenseEquivField)

                            equivStr = Utils.getTargetEquivalentUrl(DB, mySense, custSenseEquivField)
                            
                            # handle a sense mapped intentionally to nothing. Skip it.
                            if equivStr == Utils.NONE_HEADWORD:
                                
                                # output the bilingual dictionary line with a blank target (<r>) side
                                out_str = s1+headWord+'.'+str(i+1)+s2+abbrev+s3+s4b+'\n'
                                trgtFound = True
                            
                                f_out.write(out_str)
                                records_dumped_cnt += 1
                                
                            elif equivStr:
                                
                                targetSense, targetLemma, senseNum = Utils.getTargetSenseInfo(srcEntry, DB, TargetDB, mySense, equivStr, \
                                                                    custSenseNumField, report, remove1dot1Bool=False)
                                if targetSense:
                                    
                                    # If there's a space, replace it with <b/>
                                    targetLemma = re.sub(r' ', r'<b/>', targetLemma)
                                    
                                    if targetSense.MorphoSyntaxAnalysisRA and targetSense.MorphoSyntaxAnalysisRA.ClassName == 'MoStemMsa':
                                        
                                        targetMsa = IMoStemMsa(targetSense.MorphoSyntaxAnalysisRA)
                                        if targetMsa.PartOfSpeechRA:
                                            
                                            trgtFound = True
                                            
                                            # Get target pos abbreviation
                                            trgtAbbrev = ITsString(targetMsa.PartOfSpeechRA.Abbreviation.BestAnalysisAlternative).Text
                                            
                                            # Deal with problem characters like spaces, periods, and slashes
                                            trgtAbbrev = Utils.convertProblemChars(trgtAbbrev, Utils.catProbData)
                                            
                                            # Get target inflection class
                                            trgtInflCls =''
                                            if targetMsa.InflectionClassRA:
                                                
                                                trgtInflCls = s2+ITsString(targetMsa.InflectionClassRA.\
                                                                        Abbreviation.BestAnalysisAlternative).Text+s4a         
                                            # Get target features                                                     
                                            featStr = ''
                                            if targetMsa.MsFeaturesOA:
                                                
                                                feat_abbr_list = []
                                                
                                                # The features might be complex, make a recursive function call to find all leaf features
                                                Utils.get_feat_abbr_list(targetMsa.MsFeaturesOA.FeatureSpecsOC, feat_abbr_list)
                                                
                                                # This sort will keep the groups in order e.g. 'gender' features will come before 'number' features 
                                                for grpName, abb in sorted(feat_abbr_list, key=lambda x: x[0]):
                                                    
                                                    featStr += s2 + Utils.underscores(abb) + s4a
                                            
                                            # output the bilingual dictionary line (the sX is xml stuff)
                                            out_str = s1+headWord+'.'+str(i+1)+s2+abbrev+s3+targetLemma+s2+trgtAbbrev+s4a+trgtInflCls+featStr+s4b+'\n'
                                                        
                                            f_out.write(out_str)
                                            records_dumped_cnt += 1
                                    
                                        else:
                                            error_list.append(('Skipping sense because the target POS is undefined '+\
                                                            ' for target headword: '+ITsString(ILexEntry(targetSense.Entry).HeadWord).Text+\
                                                            ' while processing source headword: '+ITsString(srcEntry.HeadWord).Text, 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                    else:
                                        error_list.append(('Skipping sense because it is of this class: '+targetMsa.ClassName+\
                                                        ' for target headword: '+ITsString(ILexEntry(targetSense.Entry).HeadWord).Text+\
                                                        ' while processing source headword: '+ITsString(srcEntry.HeadWord).Text, 1, TargetDB.BuildGotoURL(ILexEntry(targetSense.Entry))))
                                else:
                                    # Error already reported
                                    pass
                            else:
                                # Don't report this. Most of the time the equivalent field will be empty.
                                pass
                        else:
                            error_list.append(('Skipping sense that is of class: '+mySense.MorphoSyntaxAnalysisRA.ClassName+\
                                           ' for headword: '+ITsString(srcEntry.HeadWord).Text, 1, DB.BuildGotoURL(srcEntry)))
                    else:
                        error_list.append(('Skipping sense, no analysis object'\
                                           ' for headword: '+ITsString(srcEntry.HeadWord).Text, 1, DB.BuildGotoURL(srcEntry)))
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
                if srcEntry.LexemeFormOA == None:
                    
                    error_list.append(('No lexeme form. Skipping. Headword: '+ITsString(srcEntry.HeadWord).Text, 1, DB.BuildGotoURL(srcEntry)))
                    
                elif srcEntry.LexemeFormOA.ClassName != 'MoStemAllomorph':
                    
                    # We've documented that affixes are skipped. Don't report this
                    pass
                
                elif srcEntry.LexemeFormOA.MorphTypeRA == None:
                    
                    error_list.append(('No Morph Type. Skipping.'+ITsString(srcEntry.HeadWord).Text+' Best Vern: '+ITsString(srcEntry.LexemeFormOA.Form.BestVernacularAlternative).Text, 1, DB.BuildGotoURL(srcEntry)))
                
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
    
        error_list.append(('Creation complete to the file: '+fullPathBilingFile+'.', 0))
        error_list.append((str(records_dumped_cnt)+' records created in the bilingual dictionary.', 0))

        # As a last step, replace certain parts of the bilingual dictionary
        if do_replacements(configMap, report, fullPathBilingFile, replFile) == True:
            
            error_list.append(('Error processing the replacement file.', 2))
            TargetDB.CloseProject()
            return error_list
    
    TargetDB.CloseProject()
    return error_list

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Call the main function
    error_list = extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=True)
        
    # output info, warnings, errors and url links
    Utils.processErrorList(error_list, report)
                
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
