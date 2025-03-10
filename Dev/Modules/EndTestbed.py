#
#   EndTestbed
#
#   Ron Lockwood
#   SIL International
#   6/15/2018
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
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
#   earlier version history removed on 3/10/25
#
#   Conclude a the testbed log result. Put the results for each test into the 
#   log and start the log viewer. Put in an end time in the log.
#

from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         

from flextoolslib import *                                                 

import ReadConfig
from Testbed import *

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "End Testbed",
        FTM_Version    : "3.13",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Conclude a testbed log result.",
        FTM_Help   : "",
        FTM_Description:  
"""
Conclude a testbed log result..
""" }

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the synthesis file name
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not outFileVal:
        return
    
    # Open the synthesis file
    try:
        f_out = open(outFileVal, encoding='utf-8')
    except IOError:
        report.Error('There is a problem with the Synthesis Output File path: '+outFileVal+'. Please check the configuration file setting.')
        return
    
    
    # Create an object for the testbed results file and get the associated
    # XML object
    resultsFileObj = FlexTransTestbedResultsFile(report)
    resultsXMLObj = resultsFileObj.getResultsXMLObj()
    
    # Extract the results from the myText.syn file
    count = resultsXMLObj.extractResults(f_out)
    f_out.close()
    
    # If we were successful write the end date-time and save the file
    if count > 0:
        resultsXMLObj.endTest()
        resultsFileObj.write()
    
    # Let the user know how many valid/invalid test were dumped
    report.Info(str(count) + ' results extracted.')
               
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

