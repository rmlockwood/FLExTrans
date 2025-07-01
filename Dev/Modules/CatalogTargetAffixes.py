#
#   CatalogTargetAffixes.py
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.2 - 3/3/25 - Ron Lockwood
#    Fixes #915. More checks for invalid chars in lemmas or affixes.
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
#   Version 3.10.1 - 2/23/24 - Ron Lockwood
#    Fixes #567 Fixes crash in Catalog Target Affixes when a lexeme form is null.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9.2 - 7/24/23 - Ron Lockwood
#    Allow glosses to be identical (no warning) when they are two different senses in the same 
#    entry and have the same morph type.
#
#   Version 3.9.1 - 7/21/23 - Ron Lockwood
#    Fixes #482. Affix allomorphs were skipped when the main form was a stem
#    because new guid lookup of morphname was using the entry object instead of the allomorph object.
#
#   earlier version history removed on 3/1/25
#
#   Go through the database and extract the gloss field and morpheme type
#   for each affix. Do this per sense. Write one gloss and morphtype per line.
#

import os
import re
import sys
from datetime import datetime

from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtWidgets import QApplication

from SIL.LCModel import * # type: ignore

from flextoolslib import *
from flexlibs import FLExProject

import Mixpanel
import ReadConfig
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'CatalogTargetAffixes'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Catalog Target Affixes",
        FTM_Version    : "3.14",        
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("CatalogTargetAffixes", "Creates a list of all the affix glosses and morpheme types in the target project."),
        FTM_Help  : "",
        FTM_Description: _translate("CatalogTargetAffixes", 
"""This module creates a file which has a list of all the affix glosses and morpheme types in the target project. 
This list is used in subsequent FLExTrans modules to do conversions and synthesize the target text.
NOTE: messages in the output window will show the SOURCE project
as being used. Actually the target project is being used.
The catalog will be created in the file specified by the Target Affix Gloss List File setting.
This is typically called target_affix_glosses.txt and is usually in the Build folder.""")}

app.quit()
del app


#----------------------------------------------------------------

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_affix_file_out_of_date(DB, affixFile):
    
    # Build a DateTime object with the FLEx DB last modified date
    flexDate = DB.GetDateLastModified()
    dbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
    
    # Get the date of the cache file
    try:
        mtime = os.path.getmtime(affixFile)
    except OSError:
        mtime = 0
    affixFileDateTime = datetime.fromtimestamp(mtime)
    
    if dbDateTime > affixFileDateTime: # FLEx DB is newer
        return True 
    else: # affix file is newer
        return False

def catalog_affixes(DB, configMap, filePath, report=None, useCacheIfAvailable=False):
    
    error_list = []
    
    morphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)

    if not morphNames:
        error_list.append((_translate("CatalogTargetAffixes", "Problem reading the configuration file for the property: {property}").format(property=ReadConfig.TARGET_MORPHNAMES), 2))
        return error_list
    
    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
        if not targetProj:
            error_list.append((_translate("CatalogTargetAffixes", "Problem accessing the target project."), 2))
            return error_list
        TargetDB.OpenProject(targetProj, True)
    except: 
        error_list.append((_translate("CatalogTargetAffixes", "Problem opening the target project."), 2))
        raise
    
    # Allow the affix file to not be in the temp folder if a slash is present
    myPath = filePath

    # Get cache data setting
    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        error_list.append((_translate("CatalogTargetAffixes", "Configuration file problem with {property}.").format(property=ReadConfig.CACHE_DATA), 2))
        TargetDB.CloseProject()
        return error_list

    # If the target database hasn't changed since we created the affix file, don't do anything.
    if useCacheIfAvailable and cacheData == 'y' and is_affix_file_out_of_date(TargetDB, myPath) == False:
        TargetDB.CloseProject()
        error_list.append((_translate("CatalogTargetAffixes", "Affix list is up to date."), 0))
        return error_list
    
    # Open the file for writing.
    try:
        f_out = open(myPath, 'w', encoding='utf-8') 
    except IOError as e:
        TargetDB.CloseProject()
        error_list.append((_translate("CatalogTargetAffixes", "There was a problem creating the Target Prefix Gloss List File: {filePath}. Please check the configuration file setting.").format(filePath=myPath), 2))# 0=info,1=warn.,2=error
        TargetDB.CloseProject()
        return error_list
    
    glossAndTypeList = []
    
    count = 0
    if report is not None:
        report.ProgressStart(TargetDB.LexiconNumberOfEntries())
  
    # Loop through all the entries
    for i,entry in enumerate(TargetDB.LexiconAllEntries()):
    
        if report is not None:
            report.ProgressUpdate(i)
        
        processIt = False
        
        # Make sure we have a valid MorphType object
        if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:
          
            # Use the English morphtype as a standard when we write it out.
            engMorphType = Utils.morphTypeMap[entry.LexemeFormOA.MorphTypeRA.Guid.ToString()]
            morphType = Utils.as_string(entry.LexemeFormOA.MorphTypeRA.Name)
            
            # Check if either the main form or any allomorphs are affixes or non-roots (e.g. clitics)
            
            # First the main form. If we have an affix or stem type that is anything other than the ones counted 
            # as roots according to the config file (morphNames), e.g. clitic, enclitic, proclitic, etc.
            if (entry.LexemeFormOA and entry.LexemeFormOA.ClassName == 'MoAffixAllomorph' and entry.LexemeFormOA.MorphTypeRA) or \
               (entry.LexemeFormOA and entry.LexemeFormOA.ClassName == 'MoStemAllomorph' and entry.LexemeFormOA.MorphTypeRA and morphType != None and morphType not in morphNames):
    
                processIt = True
            
            # If main form isn't an affix or non-root look in allomorphs. This is because you can have for example a
            # clitic allomorph of a stem.
            if processIt == False:

                for allomorph in entry.AlternateFormsOS:
                    
                    # Use the English morphtype as a standard when we write it out.
                    engMorphType = Utils.morphTypeMap[allomorph.MorphTypeRA.Guid.ToString()]
                    morphType = Utils.as_string(allomorph.MorphTypeRA.Name)

                    if (allomorph and allomorph.ClassName == 'MoAffixAllomorph' and allomorph.MorphTypeRA) or \
                       (allomorph and allomorph.ClassName == 'MoStemAllomorph' and allomorph.MorphTypeRA and morphType != None and morphType not in morphNames):
            
                        processIt = True
                        break
                
            # Process affixes or clitics (entries that aren't in the morphNames list)
            if processIt:
            
                myGlossAndTypes = []

                # Loop through senses
                for i, mySense in enumerate(entry.SensesOS):
                    
                    count += 1
                    myGloss = Utils.as_string(mySense.Gloss)

                    # Check for invalid characters
                    if Utils.containsInvalidLemmaChars(myGloss):

                        if report:
                            report.Error(_translate("CatalogTargetAffixes", "Invalid characters in the affix: {gloss}. The following characters are not allowed: {invalidChars}").format(gloss=myGloss, invalidChars=Utils.RAW_INVALID_LEMMA_CHARS), DB.BuildGotoURL(entry))

                    # Convert dots to underscores in the affix gloss
                    myGloss = Utils.underscores(myGloss)
                    
                    # Save the gloss and morph type (allow the same gloss and morphtype within an entry, i.e. don't add again causing a warning)
                    if (engMorphType, myGloss) not in myGlossAndTypes:

                        myGlossAndTypes.append((engMorphType, myGloss))

                glossAndTypeList.extend(myGlossAndTypes)
                    
    seen = set()
    
    TargetDB.CloseProject()
    
    # Sort by type and then by gloss
    for tupType, tupGloss in sorted(glossAndTypeList):

        f_out.write(tupGloss +'|'+ tupType + '\n')
        
        # Check for duplicates and give a warning.
        if tupGloss not in seen:

            seen.add(tupGloss)
        else:
            error_list.append((_translate("CatalogTargetAffixes", "Found duplicate affix/clitic with gloss: {gloss}. Use of this affix/clitic could produce unexpected results.").format(gloss=re.sub("_", ".", tupGloss)), 1))

    error_list.append((_translate("CatalogTargetAffixes", "Catalog created in the file: {filePath}.").format(filePath=Utils.getPathRelativeToWorkProjectsDir(filePath)), 0))
    error_list.append((_translate("CatalogTargetAffixes", "{count} affixes/clitics exported to the catalog.").format(count=str(count)), 0))

    return error_list

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet

    if not outFileVal:
        
        # Try the old config value name
        outFileVal = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
        
        if not outFileVal:
            return
    
    error_list = catalog_affixes(DB, configMap, outFileVal, report, useCacheIfAvailable=True)
    
    # output info, warnings, errors and url links
    Utils.processErrorList(error_list, report)


                 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

