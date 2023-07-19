#
#   DoSynthesis.py
#
#   Ron Lockwood
#   SIL International
#   7/19/23
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Initial version.
#
#   Synthesize using either Hermit Crab or STAMP depending on the setting.
#   This is just a shell to call the respective modules to do the work.
#   The advantage of having this module in a collection, is that the user can
#   switch synthesizing methods quickly. 
#

import os
import sys
import re 
import subprocess
from datetime import datetime

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         

from flextoolslib import *                                                 
from flexlibs import FLExProject, AllProjectNames, FWProjectsDir

import ReadConfig
import DoHermitCrabSynthesis
import DoStampSynthesis

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Synthesize Text",
        FTM_Version    : "3.9",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Synthesizes the target text with the either STAMP or HermitCrab.",
        FTM_Help       :"",
        FTM_Description:  
f"""
This module synthesizes the target text. If in the settings you select 'Yes' for 'Use HermitCrab Synthesis?',
then the following information from the {DoHermitCrabSynthesis.docs[FTM_Name]} module applies:
""" + DoHermitCrabSynthesis.description + f"""
If in the settings you select 'No' for 'Use HermitCrab Synthesis?',
then the following information from the {DoStampSynthesis.docs[FTM_Name]} module applies:
""" + DoStampSynthesis.description + """
""" }

def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=True)

    if hermitCrabSynthesisYesNo == 'y':

        report.Info('Using HermitCrab for synthesis.')
        DoHermitCrabSynthesis.doHermitCrab(DB, report, configMap)
    else:
        report.Info('Using STAMP for synthesis.')
        DoStampSynthesis.doStamp(DB, report, configMap)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
