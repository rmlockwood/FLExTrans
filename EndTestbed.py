#
#   EndTestbed
#
#   Ron Lockwood
#   SIL International
#   6/15/2018
#
#   Version 1.0 - 6/16/18 - Ron Lockwood
#    Initial version.
#
#   Conclude a the testbed log result. Put the results for each test into the 
#   log and start the log viewer. Put in an end time in the log.
#

import sys
import re 
import os
import ReadConfig
import Utils

from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport

from FTModuleClass import FlexToolsModuleClass

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {'moduleName'       : "End Testbed",
        'moduleVersion'    : "1.0",
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : "Conclude a testbed log result.",
        'moduleDescription'   :
u"""
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
    outFileVal = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)
    if not outFileVal:
        return
    
    # Open the synthesis file
    try:
        f_out = open(outFileVal)
    except IOError:
        report.Error('There is a problem with the Synthesis Output File path: '+outFileVal+'. Please check the configuration file setting.')
        return
    
    
    # Create an object for the testbed results file and get the associated
    # XML object
    resultsFileObj = Utils.FlexTransTestbedResultsFile()
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

