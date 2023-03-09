#
#   DoHermitCrabSynthesis.py
#
#   Ron Lockwood
#   SIL International
#   3/8/23
#
#   Version 3.8 - 3/8/23 - Ron Lockwood
#    Initial version.
#
#   Synthesize using Hermit Crab.
#

import os
import sys
import re 
import tempfile
from subprocess import call
from datetime import datetime

from System import Guid
from System import String

import ReadConfig
import Utils

from FTModuleClass import *                                                 
from SIL.LCModel import *                                                   
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
from flexlibs import FLExProject, AllProjectNames

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Synthesize Text with HermitCrab",
        FTM_Version    : "3.8",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Uses target lexicon and HermitCrab rules to create a target text.",
        FTM_Help       :"",
        FTM_Description:  
"""
This extracts the target lexicon from the target FLEx project and HermitCrab settings in the form of a HermitCrab configuration file.
It then runs HermitCrab against a list of target parses to produce surface forms. These forms are then used to create the target text.
NOTE: Messages and the task bar will show the SOURCE database as being used. Actually the target database is being used.
""" }


def extractHermitCrabConfig(DB, configMap, fwdataPath, HCconfigPath, report=None, useCacheIfAvailable=False):

    errorList = []

    # Run the HermitCrab config generator
    call(['GenerateHCConfigForFLExTrans.exe', fwdataPath, HCconfigPath])

    
    return errorList

def produceSynthesisFile():
    
    # Open target text
    
    # Read unique parses file and the surface forms file
    
    # Create a map from one to the other (zip??)
    
    # Loop through the map
    
        # substitute the Apertium parse for the surface form throughout the target text 
            
def synthesizeWithHermitCrab(configMap, HCconfigPath, synFile, report):
    
    # Turn target text into file of unique parses
    
    # Turn unique parses file into a parses file for HermitCrab. Prefixes in front of the root
    
    # Call HCSynthesis to produce surface forms
    
    # Produce synthesis file
    
def MainFunction(DB, report, modifyAllowed):

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get config settings we need.
    #targetANA = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)

    # Get the HCconfig file path
    HCconfigPath = '.'
    
    #if not (targetANA and targetSynthesis):
    #    return 

    synFile = Utils.build_path_default_to_temp(targetSynthesis)
    
    # Get fwdata file path
    fwdataPath = 'xyz.fwdata'
        
    # Extract the target lexicon
    errorList = extractHermitCrabConfig(DB, configMap, fwdataPath, HCconfigPath, report, useCacheIfAvailable=True)

    # Synthesize the new target text
    errList = synthesizeWithHermitCrab(configMap, HCconfigPath, synFile, report)
    errorList.extend(errList)
    
    # output info, warnings, errors
    for triplet in errorList:
        msg = triplet[0]
        code = triplet[1]
        
        # sometimes we'll have a url to output in the error/warning
        if len(triplet) == 3:
            url = triplet[2]
        else:
            url = None
            
        if code == 0:
            report.Info(msg, url)
        elif code == 1:
            report.Warning(msg, url)
        else: # error=2
            report.Error(msg, url)
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
# If your data doesn't match your system encoding (in the console) then
# redirect the output to a file: this will make it utf-8.
## BUT This doesn't work in IronPython!!
import codecs
if sys.stdout.encoding == None:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
