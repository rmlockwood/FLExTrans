#
#   CatalogTargetPrefixes
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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
#   for each affix. Do this per sense. Write one gloss and type per line.
#

import sys
import re 
import os
import ReadConfig
import Utils

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "Catalog Target Prefixes",
        'moduleVersion'    : "1.6",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Creates a text file with all the affix glosses and morphtypes of the target database.",
        'moduleDescription'   :
u"""
The target database set in the configuration file will be used. This module will output all 
the gloss and morphtype fields for the best analysis writing system for all affixes. 
NOTE: messages and the task bar will show the SOURCE database
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
    
def catalog_affixes(DB, configMap, filePath, report=None):
    
    error_list = []
    
    morphNames = ReadConfig.getConfigVal(configMap, 'TargetMorphNamesCountedAsRoots', report)

    if not morphNames:
        error_list.append(('Problem reading the configuration file for the property: TargetMorphNamesCountedAsRoots', 2))
        return error_list
    
    # Allow the affix file to not be in the temp folder if a slash is present
    myPath = Utils.build_path_default_to_temp(filePath)
    try:
        f_out = open(myPath, 'w') 
    except IOError as e:
        error_list.append(('There was a problem creating the Target Prefix Gloss List File: '+myPath+'. Please check the configuration file setting.', 2))# 0=info,1=warn.,2=error
        return error_list
    
    TargetDB = FLExDBAccess()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            error_list.append(('Problem accessing the target project.', 2))
            return error_list
        TargetDB.OpenDatabase(targetProj, verbose = True)
    except FDA_DatabaseError, e:
        error_list.append(('There was an error opening target database: '+targetProj+'.', 2))
        error_list.append((e.message, 2))
        return error_list
    
    error_list.append(('Using: '+targetProj+' as the target database.', 0))

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
               (e.LexemeFormOA and e.LexemeFormOA.ClassName == 'MoStemAllomorph' and e.LexemeFormOA.MorphTypeRA and morphType <> None and morphType not in morphNames):
    
                processIt = True
            
            # If main form isn't an affix or non-root look in allomorphs. This is because you can have for example a
            # clitic allomorph of a stem.
            if processIt == False:
                for allomorph in e.AlternateFormsOS:
                    
                    morphType = ITsString(allomorph.MorphTypeRA.Name.BestAnalysisAlternative).Text
                    if (allomorph and allomorph.ClassName == 'MoAffixAllomorph' and allomorph.MorphTypeRA) or \
                       (allomorph and allomorph.ClassName == 'MoStemAllomorph' and allomorph.MorphTypeRA and morphType <> None and morphType not in morphNames):
            
                        processIt = True
                        break
                
            # Process affixes or clitics (stems that aren't in the morphNames list)
            if processIt:
            
                # Loop through senses
                for i, mySense in enumerate(e.SensesOS):
                    
                    count += 1
                    
                    # Convert dots to underscores in the affix gloss
                    myGloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
                    myGloss = re.sub(r'\.', r'_', myGloss)
                    
                    # Write out the gloss and morph type
                    f_out.write(myGloss +'|'+ morphType)
                    f_out.write('\n')
    
    error_list.append((str(count)+' affixes/clitics exported to the catalog.', 0))
    return error_list

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)

    if not outFileVal:
        return
    
    error_list = catalog_affixes(DB, configMap, outFileVal, report)
    
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

