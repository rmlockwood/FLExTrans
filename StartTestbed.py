#
#   StartTestbed
#
#   Ron Lockwood
#   SIL International
#   6/9/2018
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
#   Version 3.0 - 1/25/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
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

import ReadConfig
import Utils

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Start Testbed",
        FTM_Version    : "3.5",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Initialize the testbed log and create source text from the testbed.",
        FTM_Help   : "",
        FTM_Description:  
"""
Initialize the testbed log and create source text from the testbed.
""" }

def init_new_result(DB, report):
    
    # should this clean up result nodes that have no data?
    
    # Create an object for the testbed file
    testbedFileObj = Utils.FlexTransTestbedFile(None, report)
    
    # We can't do anything if there is no testbed
    if testbedFileObj.exists() == False:
        report.Error('Testbed does not exist. Please add tests to the testbed.')
        return None
    
    # Validate the source lexical units in the testbed XML file and write the changes if needed
    testbedFileObj.validate(DB, report)
    
    # Get the testbed XML object
    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()
    
    # Create an object for the testbed results file
    resultsFileObj = Utils.FlexTransTestbedResultsFile(report)
    
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
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not outFileVal:
        return
    
    # Open the output file
    try:
        f_out = open(outFileVal, 'w', encoding="utf-8")
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

