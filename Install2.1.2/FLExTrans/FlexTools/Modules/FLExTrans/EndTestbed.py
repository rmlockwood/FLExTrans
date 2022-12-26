#
#   EndTestbed
#
#   Ron Lockwood
#   SIL International
#   6/15/2018
#
#   Version 3.7.1 - 12/25/22 - Ron Lockwood
#    Moved text and testbed classes to separate files TextClasses.py and Testbed.py
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 9/3/22 - Ron Lockwood
#    Bump version number.
#
#   Version 3.5 - 6/21/22 - Ron Lockwood
#    Bump version number for FlexTools 3.5
#
#   Version 3.4.1 - 3/17/22 - Ron Lockwood
#    Allow for a user configurable Testbed location. Issue #70.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Bump version number for FlexTools 3.2
#
#   Version 3.0 - 1/26/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.7 - 12/2/19 - Ron Lockwood
#    Import FlexProject instead of DBAcess
#
#   Version 1.0 - 6/16/18 - Ron Lockwood
#    Initial version.
#
#   Conclude a the testbed log result. Put the results for each test into the 
#   log and start the log viewer. Put in an end time in the log.
#

import ReadConfig
from Testbed import *

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "End Testbed",
        FTM_Version    : "3.7.1",
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

