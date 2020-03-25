#
#   LaunchFLExApps X
#
#   Ron Lockwood
#   SIL International
#   2/10/16
#
#   Launch FLExApps at the given path.
#

from __future__ import unicode_literals

from FTModuleClass import *

import re
from types import *
import os
import shutil
import subprocess
from System.Windows.Forms import (Application, BorderStyle, Button,
    Form, FormBorderStyle, Label,
    Panel, Screen, FixedPanel, Padding,
    MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult)

#----------------------------------------------------------------
# Configurables:

# Debugging for this module
DEBUG = False

PROJECT_NAME = 'FLExApps1.2.4 FA-GIL Verbs'
#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Launch FLEx Apps: "+PROJECT_NAME,
        FTM_Version    : "1.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Launch FLEx Apps: "+PROJECT_NAME,
        FTM_Help       : None,
        FTM_Description:
"""
Launches FLEx Apps.
""" }

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    root = 'C:\\Data\\FLExTrans\\Testbed'
    projects = root+'\\TestProjects\\'
    results = root+'\\TempResults'
    path = projects+PROJECT_NAME
    flextools = path+'\\FlexTools\\Output'
    vbs_file = 'FlexTools.vbs'
    
    # Remove all the files in the TempResults folder
    for ff in os.listdir(results):
        os.remove(results+'//'+ff)
        
    # Copy the static files to TempResults
    static_files = ['do_make.sh', 'fix.py']
    for static_file in static_files:
        shutil.copy2(root+'\\'+static_file,results)
    
    # Copy the transfer rule files
    transfer_rule_files = ['transfer_rules.t1x','transfer_rules.t2x','transfer_rules.t3x','transfer_rules_a.t1x']
    
    for rule_file in transfer_rule_files:
        if os.path.isfile(flextools+'\\'+rule_file):
            shutil.copy2(flextools+'\\'+rule_file, results)

    # Copy the Makefile
    shutil.copy2(flextools+'\\Makefile', results)
    
    # Start FlexTools at the given path
    os.chdir(path)
    process = subprocess.Popen('wscript.exe "' + path + '\\' + vbs_file + '"', stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    MessageBox.Show('After running the launched test project, click OK.',
                    "FLExTools: Waiting",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information)
 
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
