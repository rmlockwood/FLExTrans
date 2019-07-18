#
#   RunApertium
#
#   Runs the makefile that calls Apertium using the Windows Subsystem for Linux (WSL)
#
#   Version 1.7 - 4/19/19 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.6 - 5/23/18 - Ron Lockwood
#    Bump the version number.
#
#   Version 1.1.1 2/28/2018 - Ron Lockwood
#      Fixed typo. Use report.Error instead of report.error
#
#   Version 1.1 1/9/2018 - Ron Lockwood
#      Use absolute paths and moved most of the code into Utils.
#
#   Version 1.0 10/10/2017 - Marc Penner
#      Extracted call to run Apertium commands
#
#

import time
from subprocess import call
from FTModuleClass import FlexToolsModuleClass
import os
import platform
import subprocess
import re
import Utils
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError
import FTReport


#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Run Apertium commands."
docs = {'moduleName'       : "Run Apertium",
        'moduleVersion'    : '1.7',
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : descr,
        'moduleDescription': descr}
                 
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Run the makefile to run Apertium tools to do the transfer
    # component of FLExTrans. Pass in the folder of the bash
    # file to run. The current directory is FlexTools
    ret = Utils.run_makefile('Output')
    
    if ret:
        report.Error('An error happened when running the Apertium tools.')
   

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
