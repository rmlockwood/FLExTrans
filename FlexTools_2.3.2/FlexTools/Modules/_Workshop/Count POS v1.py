#
#   Count_POS
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from collections import defaultdict


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Count POS (shell)",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Report the number of entries assigned to each POS.",
        FTM_Help       : None,
        FTM_Description:
"""
This module reports the number of senses in the project by POS. 
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    report.Info("About to do cool stuff!")
    

#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
