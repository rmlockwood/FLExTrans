# -*- coding: utf-8 -*-
#
#   <Module name>
#
#   <Module description>
#
#   <Author>
#   <Date>
#
#   Platforms: Python .NET and IronPython
#

from flextoolslib import *

from SIL.LCModel import ITextRepository

def S(MUA):
    return str(MUA.get_AnalysisDefaultWritingSystem())


#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "<Module name>",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "<description>",
        FTM_Help       : None,
        FTM_Description: 
"""
<more detail here>
""" }


#----------------------------------------------------------------
# The main processing function

def MainFunction(project, report, modifyAllowed):
    """
    This is the main processing function.
    
    """
    for text in project.ObjectsIn(ITextRepository):
        report.Info("Text %s has %d paragraphs" %
            (project.BestStr(text.Name),
             text.ContentsOA.ParagraphsOS.Count))

    for e in project.LexiconAllEntries():
        report.Info(f"{project.LexiconGetHeadword(e)} HomographNumber = {e.HomographNumber}")
        # if e.DoNotUseForParsing

      #report.Info("Starting")
    #report.Warning("The sky is falling!")
    #report.Error("Failed to ...")
    

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

