#
#   InsertTargetText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 9/3/22 - Ron Lockwood
#    Bump version number.
#
#   Version 3.5.3 - 7/13/22 - Ron Lockwood
#    More CloseProject() calls for FlexTools2.1.1
#
#   Version 3.5.2 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    import change for flexlibs for FlexTools2.1
#
#   Version 3.5 - 5/5/22 - Ron Lockwood
#    Moved logic for creating unique title to Utils.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 5/12/21 - Ron Lockwood
#    Bug fix related to python 3 conversion for name of new text with copy (X)
#
#   Version 3.0 - 1/26/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.3.2 - 10/21/16 - Ron
#    Allow the synthesis file to not be in the temp folder if a slash is present
#
#   Version 1.3.1 - 4/15/16 - Ron
#    No changes to this module.
#
#   Version 1.2.0 - 1/29/16 - Ron
#    No changes to this module.
#
#   Take the text in the synthesis file and put it into a new text
#   in the target database. If the name of the text already exists
#   give it a new unique name.
#

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.Text import TsStringUtils

from flextoolslib import *                                                 
from flexlibs import FLExProject

import ReadConfig
import Utils

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Insert Target Text",
        FTM_Version    : "3.12.2",
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
        f = open(synFile, encoding='utf-8')
        fullText = f.read()
    except:
        TargetDB.CloseProject()
        report.Error('Could not open the file: "'+synFile+'".')
        return None

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
    Utils.insertParagraphs(TargetDB, fullText, m_stTxtParaFactory, stText)

    # Set the title of the text
    tss = TsStringUtils.MakeString(sourceTextName, TargetDB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    # Set metadata for the text
    Utils.setTextMetaData(DB, text)

    report.Info('Text: "'+sourceTextName+'" created in the '+targetProj+' project.')
    TargetDB.CloseProject()
    f.close()

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
