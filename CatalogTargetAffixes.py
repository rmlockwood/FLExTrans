#
#   CatalogTargetAffixes.py
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 8/20/22 - Ron Lockwood
#    Renamed this module.
#
#   Version 3.5.4 - 8/8/22 - Ron Lockwood
#    Error message fix.
#
#   Version 3.5.3 - 7/13/22 - Ron Lockwood
#    More CloseProject() calls for FlexTools2.1.1
#
#   Version 3.5.2 - 7/9/22 - Ron Lockwood
#    Use a new config setting for using cache. Fixes #115.
#    Also more calls to CloseProject when there's an error.
#
#   Version 3.5.1 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5 - 4/1/22 - Ron Lockwood
#    Added a parameter useCacheIfAvailable and default it to false so that the
#    LiveRuleTester can force the rebuild of the affix list.
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
#   Version 3.0 - 1/26/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.6.2 - 4/3/19 - Ron Lockwood
#    Check for the affix file being out of date compared to the target database
#    before going through all target entries. This improves performance.
#
#   Version 1.6.1 - 8/4/18 - Ron Lockwood
#    Give a warning for affixes or clitics that are duplicate. Also sort the
#    affixes before outputing to the file.
#
#   Version 1.6 - 2/7/18 - Ron Lockwood
#    Made the main function minimal and separated the main logic into a another
#    that can be called by the Live Rule Tester.
#
#   Version 1.3.4 - 1/18/17 - Ron
#    Use BestAnalysisAlternative instead of AnalysisDefault.
#    Check for empty morphType.
#
#   Version 1.3.3 - 10/21/16 - Ron
#    Allow the affix file to not be in the temp folder if a slash is present.
#
#   Version 1.3.2 - 4/23/16 - Ron
#    Use | as the separator between affix name and mopheme type.
#
#   Version 1.3.1 - 4/15/16 - Ron
#    No changes to this module.
#
#   Version 1.3.0 - 4/13/16 - Ron
#    Handle infixes and circumfixes.
#    Instead of just outputting prefixes, output all affix glosses and their
#    corresponding morphtype. Also convert dots to underscores in the glosses.
#    Process all allomorphs of an entry to see if there are affixes/clitics.
#
#   Version 1.2.1 - 2/11/16 - Ron
#    Error checking when opening the prefix file.
#
#   Version 1.2.0 - 1/29/16 - Ron
#    No changes to this module.
#
#   Go through the database and extract the gloss field and morpheme type
#   for each affix. Do this per sense. Write one gloss and morphtype per line.
#

import os
from System import Guid
from System import String
from datetime import datetime

import ReadConfig
import Utils

from FTModuleClass import *
from SIL.LCModel import *
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr   
from flexlibs import FLExProject

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Catalog Target Affixes",
        FTM_Version    : "3.7",
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
    for i,e in enumerate(TargetDB.LexiconAllEntries()):
    
        if report is not None:
            report.ProgressUpdate(i)
        
        processIt = False
        
        # Make sure we have a valid MorphType object
        if e.LexemeFormOA.MorphTypeRA:
          
            morphType = ITsString(e.LexemeFormOA.MorphTypeRA.Name.BestAnalysisAlternative).Text
            
            # Check if either the main form or any allomorphs are affixes or non-roots (e.g. clitics)
            
            # First the main form. If we have an affix or stem type that is anything other than the ones counted 
            # as roots according to the config file (morphNames), e.g. clitic, enclitic, proclitic, etc.
            if (e.LexemeFormOA and e.LexemeFormOA.ClassName == 'MoAffixAllomorph' and e.LexemeFormOA.MorphTypeRA) or \
               (e.LexemeFormOA and e.LexemeFormOA.ClassName == 'MoStemAllomorph' and e.LexemeFormOA.MorphTypeRA and morphType != None and morphType not in morphNames):
    
                processIt = True
            
            # If main form isn't an affix or non-root look in allomorphs. This is because you can have for example a
            # clitic allomorph of a stem.
            if processIt == False:
                for allomorph in e.AlternateFormsOS:
                    
                    morphType = ITsString(allomorph.MorphTypeRA.Name.BestAnalysisAlternative).Text
                    if (allomorph and allomorph.ClassName == 'MoAffixAllomorph' and allomorph.MorphTypeRA) or \
                       (allomorph and allomorph.ClassName == 'MoStemAllomorph' and allomorph.MorphTypeRA and morphType != None and morphType not in morphNames):
            
                        processIt = True
                        break
                
            # Process affixes or clitics (stems that aren't in the morphNames list)
            if processIt:
            
                # Loop through senses
                for i, mySense in enumerate(e.SensesOS):
                    
                    count += 1
                    
                    # Convert dots to underscores in the affix gloss
                    myGloss = Utils.underscores(ITsString(mySense.Gloss.BestAnalysisAlternative).Text)
                    
                    # Save the gloss and morph type
                    glossAndTypeList.append((morphType, myGloss))
                    
    seen = set()
    
    TargetDB.CloseProject()
    
    # Sort by type and then by gloss
    for tupType, tupGloss in sorted(glossAndTypeList):
        f_out.write(tupGloss +'|'+ tupType + '\n')
        
        # Check for duplicates and give a warning.
        if tupGloss not in seen:
            seen.add(tupGloss)
        else:
            error_list.append((f'Found duplicate affix/clitic with gloss: {tupGloss}. Use of this affix/clitic could produce unexpected results.', 1))

    error_list.append((str(count)+' affixes/clitics exported to the catalog.', 0))
    return error_list

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet

    if not outFileVal:
        
        # Try the old config value name
        outFileVal = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
        
        if not outFileVal:
            return
    
    error_list = catalog_affixes(DB, configMap, outFileVal, report, useCacheIfAvailable=True)
    
    # output info, warnings, errors
    for msg in error_list:
        
        # msg is a pair -- string & code
        if msg[1] == 0:
            report.Info(msg[0])
        elif msg[1] == 1:
            report.Warning(msg[0])
        else: # error=2
            report.Error(msg[0])
                
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

