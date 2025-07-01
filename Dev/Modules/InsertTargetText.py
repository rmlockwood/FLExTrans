#
#   InsertTargetText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
#
#   Version 3.14.2 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14.1 - 7/25/25 - Ron Lockwood
#    Fixes #324. Build a URL to the text involved so the user can double click to go to it.
#
#   Version 3.14 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.3 - 3/5/25 - Ron Lockwood
#   Fixes #909. Error messages when files don't exist.
#
#   Version 3.12.2 - 12/30/24 - Ron Lockwood
#   Fixes #742. Set the IsTranslated and Source metadata fields for the new text.
#
#   Version 3.12.1 - 12/4/24 - Ron Lockwood
#    Fixes #823. Use the same logic that's in the Import from Ptx module to mark sfms as analysis writing system.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/15/24 - Ron Lockwood
#    Support FLEx Alpha 9.2.2 which no longer supports Get Instance, use Get Service instead.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   earlier version history removed on 3/5/25
#
#   Take the text in the synthesis file and put it into a new text
#   in the target database. If the name of the text already exists
#   give it a new unique name.
#

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from SIL.LCModel import ( # type: ignore
    ITextFactory,
    IStTextFactory,
    IStTxtParaFactory,
)
from SIL.LCModel.Core.Text import TsStringUtils  # type: ignore

from flextoolslib import *                                                 
from flexlibs import FLExProject

import ChapterSelection
import Mixpanel
import ReadConfig
import Utils
from DoSynthesis import docs as DoSynthesisDocs

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'InsertTargetText'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'ChapterSelection'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Insert Target Text",
        FTM_Version    : "3.14.2",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("InsertTargetText", "Insert a translated text into the target FLEx project."),
        FTM_Help       : "",
        FTM_Description: _translate("InsertTargetText", 
"""The target project specified in the settings will be used. This module will take
the results of the {doSynthModule} module
and insert the text into the target FLEx project. The Source Text Name setting
will be used for the text name in the target project. An existing text of the 
same name will not be overwritten. A copy will be created.""").format(doSynthModule=DoSynthesisDocs[FTM_Name])}

app.quit()
del app

#----------------------------------------------------------------
# The main processing function

def insertTargetText(DB, configMap, report):

    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)
        if not targetProj:
            return None
        TargetDB.OpenProject(targetProj, True)
    except: 
        report.Error(_translate("InsertTargetText", 'Failed to open the target project.'))
        raise

    report.Info(_translate("InsertTargetText", 'Using: {targetProj} as the target project.').format(targetProj=targetProj))

    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)

    if not (sourceTextName and targetSynthesis):
        TargetDB.CloseProject()
        return None
    
    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    synFile = Utils.build_path_default_to_temp(targetSynthesis)

    try:
        with open(synFile, encoding='utf-8') as f:

            fullText = f.read()
    except:
        TargetDB.CloseProject()
        report.Error(_translate("InsertTargetText", 'The Synthesize Text module must be run before this one. Could not open the synthesis file: "') + synFile + '".')
        return

    # Figure out the naming of the text file. Use the source text name by default,
    # but if it exists create a different name. E.g. War & Peace, War & Peace - Copy, War & Peace - Copy (2)
    sourceTextName = Utils.createUniqueTitle(TargetDB, sourceTextName)
 
    # Create the text objects
    m_textFactory = TargetDB.project.ServiceLocator.GetService(ITextFactory)
    m_stTextFactory = TargetDB.project.ServiceLocator.GetService(IStTextFactory)
    m_stTxtParaFactory = TargetDB.project.ServiceLocator.GetService(IStTxtParaFactory)

    # Create a text and add it to the project      
    text = m_textFactory.Create()           
    stText = m_stTextFactory.Create()
    
    # Set StText object as the Text contents
    text.ContentsOA = stText  

    # Insert text into the target DB while marking sfms as analysis writing system
    ChapterSelection.insertParagraphs(TargetDB, fullText, m_stTxtParaFactory, stText)

    # Set the title of the text
    tss = TsStringUtils.MakeString(sourceTextName, TargetDB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    # Set metadata for the text
    ChapterSelection.setTextMetaData(DB, text)

    report.Info(_translate("InsertTargetText", 'Text: "{sourceTextName} created in the {targetProj} project.').format(sourceTextName=sourceTextName, targetProj=targetProj), 
                TargetDB.BuildGotoURL(text))
    TargetDB.CloseProject()

    return 1

def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error(_translate("InsertTargetText", 'You need to run this module in "modify mode."'))
        return
    
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

    insertTargetText(DB, configMap, report)
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
