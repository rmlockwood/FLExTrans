#
#   RunApertium
#
#   Runs the makefile that calls Apertium using the Windows Subsystem for Linux (WSL)
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

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Run Apertium commands."
docs = {'moduleName'       : "Run Apertium",
        'moduleVersion'    : '1.0',
        'moduleModifiesDB' : False,
        'moduleSynopsis'   : descr,
        'moduleDescription': descr}
                 
from FLExDBAccess import FLExDBAccess, FDA_DatabaseError

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Run the makefile to run Apertium

    is32bit = (platform.architecture()[0] == '32bit')
    system32 = os.path.join(os.environ['SystemRoot'],
                            'SysNative' if is32bit else 'System32')
    bash = os.path.join(system32, 'bash.exe')

    subprocess.call('"%s" -c "Output/do_make_direct.sh"' % bash)

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
