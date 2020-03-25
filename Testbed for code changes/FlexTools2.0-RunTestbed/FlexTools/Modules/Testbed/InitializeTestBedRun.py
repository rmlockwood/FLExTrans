#
#   InitializeTestBedRun
#
#   Ron Lockwood
#   SIL International
#   2/12/16
#
#   Set a value in a text file that indicates the name of the current
#   test. Also put this name as a new entry in the testbed results log.
#

from __future__ import unicode_literals

from FTModuleClass import *

import re
from types import *
from time import strftime
import os
import shutil
#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Initialize Testbed Run",
        FTM_Version    : "1.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Initializes things for a testbed run.",
        FTM_Help       : None,
        FTM_Description:
"""
Initializes things for a testbed run.
""" }

   
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    testbedRootFolder = 'C:\\Data\\FLExTrans\\Testbed\\'
    
    # Set text file value with current date and time which serves
    # as the name of the testbed run
    f = open(testbedRootFolder+'Results\\CurrentTestRunName.txt','w')
 
    timeStr = strftime("%Y-%m-%d %H%M")
    f.write(timeStr)
    f.close()
    
    xmlFile = testbedRootFolder+'Results\\TestbedLog.xml'
    
    # Create the parent results folder named after the TestRun date/time
    os.mkdir(testbedRootFolder+'Results\\'+timeStr)
    
    # Save a copy of our xml file
    shutil.copy2(xmlFile, xmlFile+'.old')

    # Add elements to the xml log for this new testbed run
    f = open(xmlFile)
    lines = []
    for line in f:
        line = unicode(line,'utf-8')
        lines.append(line)
    #lines = f.readlines()
    f.close()
    
    f = open(xmlFile, "w")
    for line in lines:
        f.write(line.encode('utf-8'))
        if line == "<testbed-log>\n":
            f.write('  <test n="'+timeStr+'">\n')
            f.write('  </test>\n')
    f.close()            
    report.Info('Test run initialized with the name: '+timeStr+'.')
    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
