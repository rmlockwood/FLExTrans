#
#   DoSynthesis.py
#
#   Ron Lockwood
#   SIL International
#   7/19/23
#
#   Version 3.13.1 - 3/20/25 - Ron Lockwood
#    Move the Mixpanel logging to the main function. Callers should do it.
# 
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Initial version.
#
#   Synthesize using either Hermit Crab or STAMP depending on the setting.
#   This is just a shell to call the respective modules to do the work.
#   The advantage of having this module in a collection, is that the user can
#   switch synthesizing methods quickly. 
#

from flextoolslib import *                                                 

import ReadConfig
import DoHermitCrabSynthesis
import DoStampSynthesis

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Synthesize Text",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Synthesizes the target text with either STAMP or HermitCrab.",
        FTM_Help       :"",
        FTM_Description:  
f"""
This module synthesizes the target text. If in the settings you select 'Yes' for 'Use HermitCrab synthesis?',
then the following information from the {DoHermitCrabSynthesis.docs[FTM_Name]} module applies:
""" + DoHermitCrabSynthesis.description + f"""
If in the settings you select 'No' for 'Use HermitCrab synthesis?',
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

        # Log the start of this module on the analytics server if the user allows logging.
        import Mixpanel
        Mixpanel.LogModuleStarted(configMap, report, DoHermitCrabSynthesis.docs[FTM_Name], DoHermitCrabSynthesis.docs[FTM_Version])

        report.Info('Using HermitCrab for synthesis.')
        DoHermitCrabSynthesis.doHermitCrab(DB, report, configMap)
    else:
        # Log the start of this module on the analytics server if the user allows logging.
        import Mixpanel
        Mixpanel.LogModuleStarted(configMap, report, DoStampSynthesis.docs[FTM_Name], DoStampSynthesis.docs[FTM_Version])

        report.Info('Using STAMP for synthesis.')
        DoStampSynthesis.doStamp(DB, report, configMap)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
