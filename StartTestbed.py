#
#   StartTestbed
#
#   Ron Lockwood
#   SIL International
#   6/9/2018
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.0 - 6/15/18 - Ron Lockwood
#    Initial version.
#
#   Initialize the testbed log and create a source text from the testbed. The
#   source text can be fed into the normal FLExTrans process.
#

import sys
import re 
import os
import ReadConfig
import Utils

from flexlibs.FLExDBAccess import *                                         
from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Start Testbed",
        FTM_Version    : "1.7",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Initialize the testbed log and create source text from the testbed.",
        FTM_Help   : "",
        FTM_Description:  
u"""
Initialize the testbed log and create source text from the testbed.
""" }

def init_new_result(DB, report):
    
    # should this clean up result nodes that have no data?
    
    # Create an object for the testbed file
    testbedFileObj = Utils.FlexTransTestbedFile(None)
    
    # We can't do anything if there is no testbed
    if testbedFileObj.exists() == False:
        report.Error('Testbed does not exist. Please add tests to the testbed.')
        return None
    
    # Validate the source lexical units in the testbed XML file and write the changes if needed
    testbedFileObj.validate(DB, report)
    
    # Get the testbed XML object
    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
    
    # Create an object for the testbed results file
    resultsFileObj = Utils.FlexTransTestbedResultsFile()
    
    # Initialize the testbed run
    resultsXMLObj = resultsFileObj.getResultsXMLObj()
    resultsXMLObj.initTestResult(testbedXMLObj)
    
    resultsFileObj.write()
    
    return resultsXMLObj

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Get the output file name
    outFileVal = ReadConfig.getConfigVal(configMap, 'AnalyzedTextOutputFile', report)
    if not outFileVal:
        return
    
    # Open the output file
    try:
        f_out = open(outFileVal, 'w')
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: '+outFileVal+'. Please check the configuration file setting.')
        return
    
    # Initialize a new test in the test log XML file
    resultsXMLObj = init_new_result(DB, report)
    if resultsXMLObj == None:
        return

    # Dump testbed source lexical units into the source_text.aper file
    count = resultsXMLObj.dump(f_out)
    f_out.close()
    
    # Let the user know how many valid/invalid test were dumped
    report.Info(str(count) + ' tests prepared for testing.')
               
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

