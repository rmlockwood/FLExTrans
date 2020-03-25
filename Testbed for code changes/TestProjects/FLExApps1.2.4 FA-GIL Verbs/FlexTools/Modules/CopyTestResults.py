#
#   CopyTestResults
#
#   Ron Lockwood
#   SIL International
#   2/11/16
#
#   Using the configuration file, copy the generated files after running 
#   FLExTrans to a Results folder.
#
from __future__ import unicode_literals

from FTModuleClass import *

import subprocess 
import os
import shutil 
import ReadConfig
import tempfile
import re

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Copy Test Results",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Copy the results from one testbed project run.",
        FTM_Help       : None,
        FTM_Description:
"""
Copy the results from one testbed project run.
""" }

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    testbedRootFolder = 'C:\\Data\\FLExTrans\\Testbed\\'
    resultFiles = []
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get target database name
    tgtProject = ReadConfig.getConfigVal(configMap, 'TargetProject', report)
    
    # Get various full paths
    srcFileVal = ReadConfig.getConfigVal(configMap, 'AnalyzedTextOutputFile', report)
    resultFiles.append(srcFileVal)
    tgtFileVal = ReadConfig.getConfigVal(configMap, 'TargetTranferResultsFile', report)
    resultFiles.append(tgtFileVal)
    bilFileVal = ReadConfig.getConfigVal(configMap, 'BilingualDictOutputFile', report)
    resultFiles.append(bilFileVal)
    anaFileVal = ReadConfig.getConfigVal(configMap, 'TargetOutputANAFile', report)
    resultFiles.append(anaFileVal)
    synFileVal = ReadConfig.getConfigVal(configMap, 'TargetOutputSynthesisFile', report)
    resultFiles.append(synFileVal)
    pfxFileVal = ReadConfig.getConfigVal(configMap, 'TargetPrefixGlossListFile', report)
    resultFiles.append(pfxFileVal)
    
    # Add dictionary files from the temp file which are named by the target project name
    resultFiles.append(tempfile.gettempdir()+'\\'+tgtProject+'_if.dic')
    resultFiles.append(tempfile.gettempdir()+'\\'+tgtProject+'_sf.dic')
    resultFiles.append(tempfile.gettempdir()+'\\'+tgtProject+'_pf.dic')
    resultFiles.append(tempfile.gettempdir()+'\\'+tgtProject+'_rt.dic')
    
    # Get current Project folder
    os.chdir('..')
    path = os.getcwd()
    (head, projectFolder) = os.path.split(path)
    os.chdir('FlexTools')

    # Read a string out of a file that keeps the current name of the test run
    f = open(testbedRootFolder+'Results\\CurrentTestRunName.txt') 
    currentTestRun = f.read()
    
    # Create the project folder under results
    try:
        os.mkdir(testbedRootFolder+'Results\\'+currentTestRun+'\\'+projectFolder)
    except:
        report.Error("Couldn't create the results folder. Maybe the folder: "+testbedRootFolder+'Results\\'+currentTestRun+'\\'+projectFolder+" already exists.")
        return
    
    # Set the folder to copy to
    toFolder = testbedRootFolder+'Results\\'+currentTestRun+'\\'+projectFolder

    # Loop through all files
    for resultFile in resultFiles:
        
        # copy the files to the results folder
       	shutil.copy2(resultFile, toFolder)
        
    report.Info(str(len(resultFiles))+' files copied to '+toFolder+'.')

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
