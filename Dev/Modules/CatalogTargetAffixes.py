#
#   CatalogTargetAffixes.py
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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
from datetime import datetime

from SIL.LCModel import * # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString    # type: ignore

from flextoolslib import *
from flexlibs import FLExProject

import ReadConfig
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Catalog Target Affixes",
        FTM_Version    : "3.12.1",        
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Creates a list of all the affix glosses and morpheme types in the target database.",
        FTM_Help  : "",
        FTM_Description:
"""
This module creates the file target_affix_glosses.txt which has a list of all the affix glosses and morpheme types in the target database. 
This list is used in subsequent FLExTrans modules to do conversions and synthesize the target text.
NOTE: messages in the task bar will show the SOURCE database
as being used. Actually the target database is being used.
""" }


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
        error_list.append((f'Problem reading the configuration file for the property: {ReadConfig.TARGET_MORPHNAMES}', 2))
        return error_list
    
    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
        if not targetProj:
            error_list.append(('Problem accessing the target project.', 2))
            return error_list
        TargetDB.OpenProject(targetProj, True)
    except: 
        error_list.append(('Problem opening the target project.', 2))
        raise
    
    error_list.append(('Using: '+targetProj+' as the target database.', 0))

    # Allow the affix file to not be in the temp folder if a slash is present
#    myPath = Utils.build_path_default_to_temp(filePath)
    myPath = filePath

    # Get cache data setting
    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)
    if not cacheData:
        error_list.append((f'Configuration file problem with {ReadConfig.CACHE_DATA}.', 2))
        TargetDB.CloseProject()
        return error_list

    # If the target database hasn't changed since we created the affix file, don't do anything.
    if useCacheIfAvailable and cacheData == 'y' and is_affix_file_out_of_date(TargetDB, myPath) == False:
        TargetDB.CloseProject()
        error_list.append(('Affix list is up to date.', 0))
        return error_list
    
    # Open the file for writing.
    try:
        f_out = open(myPath, 'w', encoding='utf-8') 
    except IOError as e:
        TargetDB.CloseProject()
        error_list.append(('There was a problem creating the Target Prefix Gloss List File: '+myPath+'. Please check the configuration file setting.', 2))# 0=info,1=warn.,2=error
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
          
            morphType = Utils.as_string(entry.LexemeFormOA.MorphTypeRA.Name)
            morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
            
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
                    
                    # Convert dots to underscores in the affix gloss
                    myGloss = Utils.underscores(ITsString(mySense.Gloss.BestAnalysisAlternative).Text)
                    
                    # Use the English morphtype as a standard.
                    engMorphType = Utils.morphTypeMap[morphGuidStr]

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
            error_list.append((f'Found duplicate affix/clitic with gloss: {re.sub("_", ".", tupGloss)}. Use of this affix/clitic could produce unexpected results.', 1))

    error_list.append((str(count)+' affixes/clitics exported to the catalog.', 0))
    return error_list

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
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

