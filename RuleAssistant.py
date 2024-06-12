#
#   RuleAssistant
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.11 - 5/14/24 - Ron Lockwood
#    Connect to the now functioning CreateRules routine.
#    Rearrange the logic for the return code from the GUI program. Pretty print the GUIinput xml.
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
        FTM_Version    : "3.11",
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

    projectName: str
    categoryList: list
    featureList: list
    categoryFeatures: dict

    def toXml(self, root, tag):
        parent = ET.SubElement(root, tag, {NAME: self.projectName})

        catsEl = ET.SubElement(parent, CATEGORIES)

        for cat in self.categoryList:
            elem = ET.SubElement(catsEl, FLEXCATEGORY, {ABBREV: cat})
            dct = self.categoryFeatures.get(cat)
            if not dct:
                continue
            group = ET.SubElement(elem, 'ValidFeatures')
            for feat, types in sorted(dct.items()):
                ET.SubElement(group, 'ValidFeature', name=feat,
                              type='|'.join(sorted(types)))

        if not self.featureList:
            return

        featsEl = ET.SubElement(parent, FEATURES)

        for name, values in self.featureList:
            featEl = ET.SubElement(featsEl, FLEXFEATURE, {NAME: name})
            group = ET.SubElement(featEl, VALUES)
            for val in values:
                ET.SubElement(group, FLEXFEATUREVALUE, {ABBREV: val})

@dataclass
class StartData:
 
    src: DBStartData
    tgt: DBStartData

    def write(self, fileName):
        root = ET.Element(FLEXDATA)
        self.src.toXml(root, SOURCEDATA)
        self.tgt.toXml(root, TARGETDATA)

        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(fileName, encoding='utf-8', xml_declaration=True)

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

def getFeatureData(DB):

    myFeatureList = []

    # Loop through all closed features in the database. Closed features are ones that don't embed other feature structures
    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        # Get the feature name in the best analysis language (typically English)
        featName = Utils.as_string(feature.Name)
        # Loop through possible feature values and save the abbreviation
        featValueList = sorted([Utils.as_tag(val) for val in feature.ValuesOC])

        # Add the name and the value list as a tuple to main list
        myFeatureList.append((featName, featValueList))

    # Sort the main list. By default sort uses the first tuple element for sorting.    
    myFeatureList.sort()
    return myFeatureList

def GetStartData(report, DB, configMap):
    posMap = {}
    # Put categories in posMap
    Utils.get_categories(DB, report, posMap, TargetDB=None,
                         numCatErrorsToShow=1, addInflectionClasses=False)
    catList = sorted(posMap.keys())

    featureList = getFeatureData(DB)

    inflFeatures = Utils.getAllInflectableFeatures(DB)

    catFeatures = {}
    for cat in catList:
        stemFeats = Utils.getStemFeatures(DB, report, configMap, cat)
        catFeatures[cat] = {feat: {'stem'} for feat in stemFeats}
        templates = Utils.getAffixTemplates(DB, cat)
        for tmpl in templates:
            for feat, side in tmpl:
                if feat not in catFeatures[cat]:
                    catFeatures[cat][feat] = set()
                catFeatures[cat][feat].add(side)

        for feat in inflFeatures[cat]:
            if feat not in catFeatures[cat]:
                catFeatures[cat][feat] = set()
            catFeatures[cat][feat].add('prefix')
            catFeatures[cat][feat].add('suffix')

    return DBStartData(DB.ProjectName(), catList, featureList, catFeatures)

def GetRuleAssistantStartData(report, DB, TargetDB, configMap):

    return StartData(GetStartData(report, DB, configMap),
                     GetStartData(report, TargetDB, configMap))

def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile):

    # Call the rule assistant gui program 
    try:
        fullRApath = os.path.join(os.environ['PROGRAMFILES'], FTPaths.RULE_ASSISTANT_DIR, FTPaths.RULE_ASSISTANT)
        
        params = [fullRApath, ruleAssistantFile, ruleAssistGUIinputfile]

        result = subprocess.run(params, capture_output=True)

        output = result.stdout.decode('utf-8').strip().split()
        if not output or output[0] not in ['1', '2']:
            return (False, None)
        elif output[0] == '1':
            return (True, int(output[1])) # create single rule
        else:
            return (True, None) # create all rules

    except Exception as e:

        report.Error(f'An error happened when running the Rule Assistant tool: {e.output.decode("utf-8")}')
        return (False, None)
    
    return (False, None)

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
    startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)

    # Write the data to an XML file
    ruleAssistGUIinputfile = os.path.join(FTPaths.BUILD_DIR, RA_GUI_INPUT_FILE)
    startData.write(ruleAssistGUIinputfile)
    
    # Start the Rule Assistant GUI
    saved, rule = StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile)

    if saved:
        CreateApertiumRules.CreateRules(TargetDB, report, configMap, ruleAssistantFile, tranferRulePath, rule)
    else:
        report.Info('No rules created.')

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
