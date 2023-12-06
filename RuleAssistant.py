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
import re
from flextoolslib import *
import FTPaths
import xml.etree.ElementTree as ET

from SIL.LCModel import (
    IFsClosedFeatureRepository,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString   

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

RA_GUI_INPUT = 'ruleAssistantGUIinput.xml'

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
    srcCatList, srcFeatureList, tgtCatList, tgtFeatureList = GetRuleAssistantStartData(report, DB, TargetDB)

    # Write the data to an XML file
    writeXMLData(DB, TargetDB, srcCatList, srcFeatureList, tgtCatList, tgtFeatureList)
    



    # Start the Rule Assistant GUI

    CreateApertiumRules.CreateRules(TargetDB, report, configMap, ruleAssistantFile, tranferRulePath)

def GetRuleAssistantStartData(report, DB, TargetDB):

    posMap = {}
    srcFeatureList = []
    tgtFeatureList = []

    # Get categories
    Utils.get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)
    srcCatList = sorted(posMap.keys())

    Utils.get_categories(TargetDB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)
    tgtCatList = sorted(posMap.keys())

    # Get features
    getFeatureData(DB, srcFeatureList)
    getFeatureData(TargetDB, tgtFeatureList)

    return srcCatList, srcFeatureList, tgtCatList, tgtFeatureList

def getFeatureData(DB, myFeatureList):

    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        featName = ITsString(feature.Name.BestAnalysisAlternative).Text
        featValueList = []

        for value in feature.ValuesOC:
            abbr = ITsString(value.Abbreviation.BestAnalysisAlternative).Text
            abbr = re.sub(r'\.', '_', abbr)
            featValueList.append(abbr)

        featValueList.sort()
        myFeatureList.append((featName, featValueList))
        
    myFeatureList.sort()

def writeXMLData(srcDB, tgtDB, srcCatList, srcFeatureList, tgtCatList, tgtFeatureList):

    ruleAssistGUIinputXMLfile = os.path.join(FTPaths.BUILD_DIR, RA_GUI_INPUT)
    rootNode = ET.Element(FLEXDATA)

    # Add all the sub-element data to the root element
    createElements(srcDB, rootNode, SOURCEDATA, srcCatList, srcFeatureList)
    createElements(tgtDB, rootNode, TARGETDATA, tgtCatList, tgtFeatureList)

    tree = ET.ElementTree(rootNode)

    tree.write(ruleAssistGUIinputXMLfile, encoding='utf-8', xml_declaration=True)

def createElements(myDB, rootNode, dataElemStr, catList, featureList):

    dataElement = ET.SubElement(rootNode, dataElemStr)
    dataElement.attrib['name'] = myDB.ProjectName()
    myCats = ET.SubElement(dataElement, CATEGORIES)

    for catStr in catList:

        myCat = ET.SubElement(myCats, FLEXCATEGORY)
        myCat.attrib['abbr'] = catStr

    if len(featureList) > 0:

        myFeats = ET.SubElement(dataElement, FEATURES)

    for featName, valueList in featureList:

        myFeat = ET.SubElement(myFeats, FLEXFEATURE)
        myFeat.attrib['name'] = featName

        myValues = ET.SubElement(myFeat, VALUES)

        for valueStr in valueList:

            myValue = ET.SubElement(myValues, FLEXFEATUREVALUE)
            myValue.attrib['abbr'] = valueStr

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
