#
#   LinkAllSensesAsDup
#
#   Ron Lockwood
#   SIL International
#   7/24/23
#
#
#   Version 3.12.1 - 1/21/25 - Ron Lockwood
#    Fixes #841. Use new method to get an object repository. This fixes the crash.
#
#   Version 3.12 - 11/11/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.10.5 - 8/1/24 - Ron Lockwood
#    Add TargetDB to the list of parameters to write SenseHyperLink function
#
#   Version 1.0 - 7/24/23 - Ron Lockwood
#    Initial version
#

import re

from System import Guid # type: ignore
from System import String # type: ignore

from SIL.LCModel import ICmObjectRepository, ILexSense # type: ignore

from flextoolslib import *                                                 

import ReadConfig
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Link All Senses As Duplicate",
        FTM_Version    : "3.12.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Link all senses to the same guid in the target.",
        FTM_Help       : "",
        FTM_Description:  
"""
This module will link all senses to the same guid in the target. CAUTION: This will 
overwrite all senses in the source project!
This assumes the source was copied from the target and all the senses have the same
unique identifier (guid).
""" }
                 
def MainFunction(DB, report, modify=False):

    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    configMap = ReadConfig.readConfig(report)
        
    haveConfigError = False
    
    # Get need configuration file properties
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    linkField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)

    if not sourceTextName:
        
        report.Error('No Source Text Name has been set. Please go to Settings and fix this.')
        haveConfigError = True
    
    if not linkField:
        
        report.Error('No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.')
        haveConfigError = True
    
    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    
    # Give an error if there are no morphnames
    if not sourceMorphNames or len(sourceMorphNames) < 1:
        
        report.Error('No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.')
        haveConfigError = True
    
    if haveConfigError:
        return 
    
    TargetDB = Utils.openTargetProject(configMap, report)
    myStyle = Utils.getHyperLinkStyle(DB)

    preGuidStr = 'silfw://localhost/link?database%3d'
    preGuidStr += re.sub('\s','+', targetProj)
    preGuidStr += '%26tool%3dlexiconEdit%26guid%3d'

    # Loop through all the source entries
    for entryIndex, entryObj in enumerate(DB.LexiconAllEntries()):
    
        # Don't process affixes, clitics
        if entryObj.LexemeFormOA and entryObj.LexemeFormOA.ClassName == 'MoStemAllomorph' and \
           entryObj.LexemeFormOA.MorphTypeRA and Utils.morphTypeMap[entryObj.LexemeFormOA.MorphTypeRA.Guid.ToString()] in sourceMorphNames:
        
            # Loop through senses
            for mySense in entryObj.SensesOS:

                # Skip empty MSAs
                if mySense.MorphoSyntaxAnalysisRA == None:
                    continue
                
                # Make guid url string
                guidSubStr = mySense.Guid.ToString()
                urlStr = preGuidStr + guidSubStr + '%26tag%3d'

                # Get target sense from the guid
                guid = Guid(String(guidSubStr))
                repo = TargetDB.project.ServiceLocator.GetService(ICmObjectRepository)

                try:
                    targetSense = ILexSense(repo.GetObject(guid))
                except:
                    report.Warning(f'Skipped this guid that was not found: {guidSubStr}.')
                    continue

                # write the hyperlink
                Utils.writeSenseHyperLink(DB, TargetDB, mySense, targetSense.Entry, targetSense, senseEquivField, urlStr, myStyle) 

    report.Info(f'{str(entryIndex)} entries processed.')
    TargetDB.CloseProject()

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
