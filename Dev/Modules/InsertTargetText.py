#
#   InsertTargetText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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

import ChapterSelection
from SIL.LCModel import ( # type: ignore
    ITextFactory,
    IStTextFactory,
    IStTxtParaFactory,
)
from SIL.LCModel.Core.Text import TsStringUtils  # type: ignore

from flextoolslib import *                                                 
from flexlibs import FLExProject

import ReadConfig
import Utils

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Insert Target Text",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Insert a translated text into the target FLEx project.",
        FTM_Help       : "",
        FTM_Description:
"""
The target database set in the configuration file will be used. This module will take
the results of the synthesis process (Create Target Dictionaries and Synthesize module)
and insert the text into the target FLEx project. The SourceTextName property in 
the FlexTrans.config file will be used for the text name in the target project. NOTE: A message window
will be displayed asking if you want to make changes to the SOURCE project. This is not true. This module
will only change the target database as specified in the configuration file.
""" }
                 
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
        report.Error('Failed to open the target database.')
        raise

    report.Info('Using: '+targetProj+' as the target database.')

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
        report.Error('The Synthesize Text module must be run before this one. Could not open the synthesis file: "'+synFile+'".')
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

    report.Info('Text: "'+sourceTextName+'" created in the '+targetProj+' project.')
    TargetDB.CloseProject()

    return 1

def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    insertTargetText(DB, configMap, report)
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
