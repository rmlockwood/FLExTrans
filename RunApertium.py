#
#   RunApertium
#
#   Runs the makefile that calls Apertium using the Windows Subsystem for Linux (WSL)
#
#   Version 3.5.1 - 6/13/22 - Ron Lockwood
#    Changes to support the Windows version of the Apertium tools. Fixes #143.
#    Run a function called stripRulesFile to remove DocType from the transfer 
#    rules file before applying aperitum tools.
#
#   Version 3.5 - 5/10/22 - Ron Lockwood
#    Support multiple projects in one FlexTools folder. Folders rearranged.
#
#   Version 3.4.1 - 3/5/22 - Ron Lockwood
#    Use a config file setting for the transfer rules file. Make it an 
#    environment variable that the makefile can use.
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

import Utils
import ReadConfig
import os
from FTModuleClass import *
from FTPaths import CONFIG_PATH

#----------------------------------------------------------------
# Documentation that the user sees:
descr = "Run Apertium commands."
docs = {FTM_Name       : "Run Apertium",
        FTM_Version    : "3.5",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : descr,
        FTM_Help  : "",  
        FTM_Description:    descr}     
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = os.path.join(os.path.dirname(os.path.dirname(CONFIG_PATH)), Utils.BUILD_FOLDER)

    # Create stripped down transfer rules file that doesn't have the DOCTYPE stuff
    Utils.stripRulesFile(report, buildFolder)
    
    # Run the makefile to run Apertium tools to do the transfer component of FLExTrans. 
    ret = Utils.run_makefile(buildFolder, report)
    
    if ret:
        report.Error('An error happened when running the Apertium tools. The contents of apertium_error.txt is:')
        try:
            f = open(os.path.join(buildFolder, Utils.APERTIUM_ERROR_FILE), encoding='utf-8')
            lines = f.readlines()
            report.Error('\n'.join(lines))
        except:
            pass

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
