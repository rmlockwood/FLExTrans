#
#   InsertTargetText
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/5/14
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

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from SIL.LCModel.Core.Text import TsStringUtils
from flexlibs.FLExProject import FLExProject, GetProjectNames
import ReadConfig
import Utils

#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Insert Target Text",
        FTM_Version    : "3.0",
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

textNameList = []

def findTextName(TargetDB, myTextName):
    foundText = False
    
    if len(textNameList) == 0:
        for text in TargetDB.ObjectsIn(ITextRepository):
            tName = ITsString(text.Name.BestVernacularAnalysisAlternative).Text
            textNameList.append(tName)
            if myTextName == tName:
                foundText = True
    else:
        if myTextName in textNameList:
            foundText = True
            
    return foundText

def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    TargetDB = FLExProject()

    try:
        # Open the target database
        targetProj = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
        if not targetProj:
            return
        TargetDB.OpenProject(targetProj, True)
    except: 
        raise

    report.Info('Using: '+targetProj+' as the target database.')

    sourceTextName = ReadConfig.getConfigVal(configMap, 'SourceTextName', report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)
    if not (sourceTextName and targetSynthesis):
        return
    
    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    synFile = Utils.build_path_default_to_temp(targetSynthesis)

    try:
        f = open(synFile, encoding='utf-8')
    except:
        report.Error('Could not open the file: "'+synFile+'".')

    # Figure out the naming of the text file. Use the source text name by default,
    # but if it exists create a different name. E.g. War & Peace, War & Peace - Copy, War & Peace - Copy (2)
    if findTextName(TargetDB, sourceTextName):
        sourceTextName += ' - Copy'
        if findTextName(TargetDB, sourceTextName): 
            done = False
            i = 2
            while not done: 
                tryName = sourceTextName + ' (' + bytes(str(i)) + ')'
                if not findTextName(TargetDB, tryName): 
                    sourceTextName = tryName
                    done = True 
                i += 1
 
    # Create the text objects
    m_textFactory = TargetDB.project.ServiceLocator.GetInstance(ITextFactory)
    m_stTextFactory = TargetDB.project.ServiceLocator.GetInstance(IStTextFactory)
    m_stTxtParaFactory = TargetDB.project.ServiceLocator.GetInstance(IStTxtParaFactory)

    # Start an Undo Task
#    TargetDB.db.MainCacheAccessor.BeginNonUndoableTask()  
    
    # Create a text and add it to the project      
    text = m_textFactory.Create()           
    stText = m_stTextFactory.Create()
    
    # Set StText object as the Text contents
    text.ContentsOA = stText  
    
    # Add paragraphs from the synthesized file
    for line in f:
        # Create paragraph object
        stTxtPara = m_stTxtParaFactory.Create()
        
        # Add it to the stText object
        stText.ParagraphsOS.Add(stTxtPara)       
        
        # Create a TS String to hold the line of text. Use the default vern. writing system
        tss = TsStringUtils.MakeString(line, TargetDB.project.DefaultVernWs)
        
        # Set the paragraph contents to the TS String
        stTxtPara.Contents = tss             
    
    # Set the title of the text
    tss = TsStringUtils.MakeString(sourceTextName, TargetDB.project.DefaultAnalWs)
    text.Name.AnalysisDefaultWritingSystem = tss
    
    report.Info('Text: "'+sourceTextName+'" created in the '+targetProj+' project.')
 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
