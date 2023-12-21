#
#   RuleAssistant
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.9.3 - 12/20/23 - Ron Lockwood
#    Use data classes to pass around category and feature lists.
#
#   Version 3.9.2 - 12/19/23 - Ron Lockwood
#    Add a function to start the Rule Assistant program.
#
#   Version 3.9.1 - 12/6/23 - Ron Lockwood
#    Build an XML file with category and feature data for source and target databases
#    which will be used by the rule assistant GUI.
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
import subprocess
import re
from flextoolslib import *
import FTPaths
import xml.etree.ElementTree as ET
from dataclasses import dataclass

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

RA_GUI_INPUT_FILE = 'ruleAssistantGUIinput.xml'

# Element names in the rule assistant gui input file
FLEXDATA          = "FLExData" 
SOURCEDATA        = "SourceData"
TARGETDATA        = "TargetData"
CATEGORIES        = "Categories"
FLEXCATEGORY      = "FLExCategory"
FEATURES          = "Features"
FLEXFEATURE       = "FLExFeature"
VALUES            = "Values"
FLEXFEATUREVALUE  = "FLExFeatureValue"

# Attribute names in the rule assistant gui input file
NAME   = 'name'
ABBREV = 'abbr'

@dataclass
class DBStartData:
 
    categoryList: list
    featureList: list
 
@dataclass
class StartData:
 
    src: DBStartData
    tgt: DBStartData

# Trying to get something like this:
#
# <?xml version="1.0" encoding="UTF-8"?>
# <FLExData>
#  <SourceData name="Spanish-FLExTrans-Exp4">
#   <Categories>
#    <FLExCategory abbr="adj"/>
#    <FLExCategory abbr="adv"/>
#    ...
#   </Categories>
#   <Features>
#    <FLExFeature name="number">
#     <Values>
#      <FLExFeatureValue abbr="pl"/>
#      <FLExFeatureValue abbr="sg"/>
#     </Values>
#    </FLExFeature>
#    <FLExFeature name="person">
#     <Values>
#      <FLExFeatureValue abbr="1"/>
#      <FLExFeatureValue abbr="2"/>
#      <FLExFeatureValue abbr="3"/>
#     </Values>
#    </FLExFeature>
#    ...
#   </Features>
#  </SourceData>
#  <TargetData name="French-FLExTrans-Exp4">
#   similar to above ...
#  </TargetData>
# </FLExData>
def writeXMLData(srcDB, tgtDB, startData):

    # Create a full path to the Rule Assistant GUI input file.
    ruleAssistGUIinputXMLfile = os.path.join(FTPaths.BUILD_DIR, RA_GUI_INPUT_FILE)

    # Start an XML object with root FLExData
    rootNode = ET.Element(FLEXDATA)

    # Add all the sub-element data to the root element
    createElements(srcDB, rootNode, SOURCEDATA, startData.src)
    createElements(tgtDB, rootNode, TARGETDATA, startData.tgt)

    # Create an Element Tree object and write the xml file.
    tree = ET.ElementTree(rootNode)
    tree.write(ruleAssistGUIinputXMLfile, encoding='utf-8', xml_declaration=True)

    return ruleAssistGUIinputXMLfile

def getFeatureData(DB, myFeatureList):

    # Loop through all closed features in the database. Closed features are ones that don't embed other feature structures
    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        # Get the feature name in the best analysis language (typically English)
        featName = ITsString(feature.Name.BestAnalysisAlternative).Text
        featValueList = []

        # Loop through possible feature values and save the abbreviation
        for value in feature.ValuesOC:

            abbr = ITsString(value.Abbreviation.BestAnalysisAlternative).Text
            abbr = re.sub(r'\.', '_', abbr) # change underscores to periods
            featValueList.append(abbr)

        # Sort the values
        featValueList.sort()

        # Add the name and the value list as a tuple to main list
        myFeatureList.append((featName, featValueList))

    # Sort the main list. By default sort uses the first tuple element for sorting.    
    myFeatureList.sort()

def GetRuleAssistantStartData(report, DB, TargetDB):

    posMap = {}
    srcFeatureList = []
    tgtFeatureList = []

    # Get categories. They end up in the posMap which is a dict. 
    Utils.get_categories(DB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)

    # Turn them into a sorted list.
    srcCatList = sorted(posMap.keys())

    # Same for the target database
    Utils.get_categories(TargetDB, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)
    tgtCatList = sorted(posMap.keys())

    # Get features. They come back sorted.
    getFeatureData(DB, srcFeatureList)
    getFeatureData(TargetDB, tgtFeatureList)

    myStartData = StartData(DBStartData(srcCatList, srcFeatureList), DBStartData(tgtCatList, tgtFeatureList))

    return myStartData

def createElements(myDB, rootNode, dataElemStr, dbStartData):

    # Create the Source/TargetData element and set the name to the FLEx project name
    dataElement = ET.SubElement(rootNode, dataElemStr)
    dataElement.attrib[NAME] = myDB.ProjectName()

    # Create the Categories element
    myCats = ET.SubElement(dataElement, CATEGORIES)

    # Add all the FLExCategory elements 
    for catStr in dbStartData.categoryList:

        myCat = ET.SubElement(myCats, FLEXCATEGORY)
        myCat.attrib[ABBREV] = catStr

    # Proceed if we have at least one feature
    if len(dbStartData.featureList) > 0:

        # Create the Features element
        myFeats = ET.SubElement(dataElement, FEATURES)

        # Loop through features
        for featName, valueList in dbStartData.featureList:

            # Create the FLExFeature element
            myFeat = ET.SubElement(myFeats, FLEXFEATURE)
            myFeat.attrib[NAME] = featName

            # Create the Values element
            myValues = ET.SubElement(myFeat, VALUES)

            # Add all the FLExFeatureValue sub-elements
            for valueStr in valueList:

                myValue = ET.SubElement(myValues, FLEXFEATUREVALUE)
                myValue.attrib[ABBREV] = valueStr

def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile):

    # Call the rule assistant gui program 
    try:
        fullRApath = os.path.join(os.environ['PROGRAMFILES'], FTPaths.RULE_ASSISTANT_DIR, FTPaths.RULE_ASSISTANT)
        
        params = [fullRApath, ruleAssistantFile, ruleAssistGUIinputfile]

        result = subprocess.run(params, capture_output=True, check=True)

        if result.returncode != 0:

            report.Error(f'An error happened when running the Rule Assistant tool: {e.output.decode("utf-8")}')
            return True

    except subprocess.CalledProcessError as e:

        report.Error(f'An error happened when running the Rule Assistant tool: {e.output.decode("utf-8")}')
        return True
    
    return False

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR

    ruleAssistantFile = os.path.join(buildFolder, 'RuleAssistantRules.xml')

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)
    if not tranferRulePath:
        return

    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the FLEx info. for source & target projects that the Rule Assistant font-end needs
    startData = GetRuleAssistantStartData(report, DB, TargetDB)

    # Write the data to an XML file
    ruleAssistGUIinputfile = writeXMLData(DB, TargetDB, startData)
    
    # Start the Rule Assistant GUI
    if StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile) == True:
        return

    CreateApertiumRules.CreateRules(TargetDB, report, configMap, ruleAssistantFile, tranferRulePath)

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
