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
import xml.etree.ElementTree as ET

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

FLEXDATA          = "FLExData" 
SOURCEDATA        = "SourceData"
TARGETDATA        = "TargetData"
CATEGORIES        = "Categories"
FLEXCATEGORY      = "FLExCategory"
FEATURES          = "Features"
FLEXFEATURE       = "FLExFeature"
VALUES            = "Values"
FLEXFEATUREVALUE  = "FLExFeatureValue"

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

    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the FLEx info. for source & target projects that the Rule Assistant font-end needs
    GetRuleAssistantStartData()

    # Write the data to an XML file
    writeXMLData(DB, TargetDB, catList, featureList)
    



    # Start the Rule Assistant GUI

    CreateApertiumRules.CreateRules(TargetDB, report, configMap, ruleAssistantFile, tranferRulePath)

def writeXMLData(srcDB, tgtDB, catList, featureList):

    rootNode = ET.Element(FLEXDATA)
    srcNode = ET.SubElement(rootNode, SOURCEDATA)
    srcNode.attrib['name'] = srcDBname
    srcCats = ET.SubElement(srcNode, CATEGORIES)

    for cat in catList:

        srcCat = ET.SubElement(srcCats, FLEXCATEGORY)
        srcCat.attrib['abbr'] = cat

    srcFeats = ET.SubElement(srcNode, FEATURES)

    for feat in featList:

        srcFeat = ET.SubElement(srcFeats, FLEXFEATURE)
        srcFeat.attrib['name'] = featname

        srcValues = ET.SubElement(srcValues, VALUES)

        for valueStr in featValues:

            srcValue = ET.SubElement(srcValues, FLEXFEATUREVALUE)
            srcValue.attrib['abbr'] = valueStr

    # Do same for target



#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
