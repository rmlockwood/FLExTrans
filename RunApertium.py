#
#   RunApertium
#
#   Runs the makefile that calls Apertium using the Windows Subsystem for Linux (WSL)
#
#   Version 1.1 1/9/2018 - Ron Lockwood
#      Use absolute paths and moved most of the code into Utils.
#
#   Version 1.0 10/10/2017 - Marc Penner
#      Extracted call to run Apertium commands
#
#

from FTModuleClass import FlexToolsModuleClass
import time
from subprocess import call
from FTModuleClass import FlexToolsModuleClass
import os
import platform
import subprocess
import re
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Run Apertium commands."
docs = {'moduleName'       : "Run Apertium",
        'moduleVersion'    : '1.1',
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : descr,
        'moduleDescription': descr}
                 
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Run the makefile to run Apertium tools to do the transfer
    # component of FLExTrans. Pass in the folder of the bash
    # file to run. The current directory is FlexTools
    ret = Utils.run_makefile('Output')
    
    if ret:
        report.error('An error happened when running the Apertium tools.')
   

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
