#
#   LinkAllSensesAsDup
#
#   Ron Lockwood
#   SIL International
#   7/24/23
#
#
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 5/27/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.3 - 3/2/25 - Ron Lockwood
#    Fixes #914. Set the morphtype to be from the analysis writing system instead of English.
#    This is needed now that we let non-English morphtype names be used in the settings.
#
#   Version 3.12.2 - 1/30/25 - Ron Lockwood
#    Corrected module description.
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

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from System import Guid # type: ignore
from System import String # type: ignore

from SIL.LCModel import ICmObjectRepository, ILexSense # type: ignore
from flextoolslib import *                                                 

import Mixpanel
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'LinkAllSensesAsDup'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("LinkAllSensesAsDup", "Link All Senses As Duplicate"),
        FTM_Version    : "3.14.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("LinkAllSensesAsDup", "Link all senses to the same ID in the target."),
        FTM_Help       : "",
        FTM_Description: _translate("LinkAllSensesAsDup", 
"""This module will link all senses to the same ID in the target. CAUTION: This will 
overwrite all senses in the source project!
This assumes the target project was copied from the source and all the senses have the same
unique identifier (guid).""")}

#app.quit()
#del app

def MainFunction(DB, report, modify=False):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    if not modify:
        report.Error(_translate("LinkAllSensesAsDup", 'You need to run this module in "modify mode."'))
        return
    
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])
        
    haveConfigError = False
    
    # Get need configuration file properties
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    linkField = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_CUSTOM_FIELD_ENTRY, report)
    sourceMorphNames = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_MORPHNAMES, report)
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)

    if not sourceTextName:
        
        report.Error(_translate("LinkAllSensesAsDup", 'No Source Text Name has been set. Please go to Settings and fix this.'))
        haveConfigError = True
    
    if not linkField:
        
        report.Error(_translate("LinkAllSensesAsDup", 'No Source Custom Field for Entry Link has been set. Please go to Settings and fix this.'))
        haveConfigError = True
    
    senseEquivField = DB.LexiconGetSenseCustomFieldNamed(linkField)
    
    # Give an error if there are no morphnames
    if not sourceMorphNames or len(sourceMorphNames) < 1:
        
        report.Error(_translate("LinkAllSensesAsDup", 'No Source Morpheme Types Counted As Roots have been selected. Please go to Settings and fix this.'))
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
           entryObj.LexemeFormOA.MorphTypeRA and Utils.as_string(entryObj.LexemeFormOA.MorphTypeRA.Name) in sourceMorphNames:
        
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
                    report.Warning(_translate("LinkAllSensesAsDup", 'Skipped this guid that was not found: {guidSubStr}.').format(guidSubStr=guidSubStr))
                    continue

                # write the hyperlink
                Utils.writeSenseHyperLink(DB, TargetDB, mySense, targetSense.Entry, targetSense, senseEquivField, urlStr, myStyle)

    report.Info(_translate("LinkAllSensesAsDup", '{entryIndex} entries processed.').format(entryIndex=entryIndex))
    TargetDB.CloseProject()

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
