#
#   RuleAssistant
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.9 - 9/11/23 - Ron Lockwood
#    Initial version
#
#   Runs the Rule Assistant to create Apertium transfer rules. 
#

import Utils
import ReadConfig
import CreateApertiumRules
import os
from flextoolslib import *
import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:
descr = """This module runs the Rule Assistant tool which let's you create transfer rules.
"""
docs = {FTM_Name       : "Rule Assistant",
        FTM_Version    : "3.9",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Runs the Rule Assistant tool.",
        FTM_Help  : "",  
        FTM_Description:    descr}     

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR

    ruleAssistantFile = os.path.join(buildFolder, 'ruleAssistantRules.xml')

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return True

    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)
    if not tranferRulePath:
        return True

    CreateApertiumRules.CreateRules(DB, report, ruleAssistantFile, tranferRulePath)

    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
