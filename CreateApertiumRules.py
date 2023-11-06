#
#   CreateApertiumRules
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.9.x - 11/06/23 - Matthew Fort
#    First draft version of reading in, checking, writing
#
#   Version 3.9 - 9/11/23 - Ron Lockwood
#    Initial version
#
#   Given an xml file defining the rules, create Apertium-style rules

import Utils

import re
import os
import unicodedata
import shutil
import time
import xml.etree.ElementTree as ET

# TODO: Build a new .t1x file if needed
# NOTE: perhaps this function will be expanded to include actual translation of the rules themselves
def CreateNewApertiumTree():
    attributes = ['section-def-cats', 'section-def-attrs', 'section-def-vars', 'section-def-macros', 'section-rules']

    root = ET.Element('transfer')
    
    # Build the generic structure of the new Apertium .t1x file
    for attribute in attributes:
        tmpAttribute = ET.Element(attribute)
        root.append(tmpAttribute)

    return ET.ElementTree(root)

# Check categories and attributes referenced in the ruleAssistantFiles
# TODO: check on attribute and category values 
def CheckXML(report, apertiumTree, assistantTree):
    apertiumRoot = apertiumTree.getroot()

    apertiumTreeAttributes = []
    apertiumTreeCategories = []
    assistantTreeAttributes = []
    assistantTreeCategories = []

    # Get the attributes from the Apertium transfer file
    for attribute in apertiumRoot.iter('cat-item'):
        apertiumTreeAttributes.append(attribute.attrib['tags'])

    # Get the categories from the Apertium trasnfer file
    for category in apertiumRoot.iter('attr-item'):
        apertiumTreeCategories.append(category.attrib['tags'])

    # Get the attributes from the RuleAssistant file
    # TODO: ensure this is the correct info
    for attribute in assistantTree.findall('.//FLExTransRules/FLExTransRule/Target/Phrase/Words/Word/Features/Feature'):
        assistantTreeAttributes.append(attribute.attrib['label'])

    # Get the category from the RuleAssistant file
    # TODO: ensure this is the correct info
    for category in assistantTree.findall('.//FLExTransRules/FLExTransRule/Source/Phrase/Words/Word'):
        assistantTreeCategories.append(category.attrib['category'])

    # Check to see if there's a category or attribute in the RuleAssistant File
    # which isn't in the Apertium transfer file
    # TODO: Ensure the compared categories and features are truly the ones needed
    # if (list(set(assistantTreeCategories) - set(apertiumTreeCategories))) \
    #     or (list(set(assistantTreeAttributes) - set(apertiumTreeAttributes))):
    #     return -1

    return 0

def CreateRules(DB, report, configMap, ruleAssistantFile, transferRulePath):

    # If there is a trasnfer rule file, read it in
    if (os.path.exists(transferRulePath)):
        # TODO check for proper reading mode ("w" or "wb")
        with open(transferRulePath, "r") as apertiumFile:
            apertiumTree = ET.parse(apertiumFile)
    # If there isn't a transfer rule file, create one
    else:
        apertiumTree = CreateNewApertiumTree()
        # with open(transferRulePath, "wb") as newApertiumFile:
        #     apertiumTree.write(newApertiumFile) 

    # make an Apertium transfer rule backup
    # TODO change to more informative name
    shutil.copy(transferRulePath, transferRulePath + "." + str(int(time.time())) + ".bak")

    # TODO check for proper reading mode ("w" or "wb")
    try:
        with open(ruleAssistantFile, "r") as rulesAssistant:
            assistantTree = ET.parse(rulesAssistant)
    except:
        report.Error("No Rule Assistant file found, please run the Set Up Transfer Rule Categories and Attributes tool")
        return -1

    # Check to make sure the attributes and features listed in the files match  
    if CheckXML(report, apertiumTree, assistantTree):
        report.Error("Please run the Set Up Transfer Rule Categories and Attributes tool")
        return -1

    # TODO: Build next functions to complete rule transfer
    # Read in name of rule
    ruleName = assistantTree.find('.//FLExTransRules/FLExTransRule').get('name')
    
    # Check if name of rule already exists in t1x file, and update rule name accordingly
    # TODO: Clarify this process

    # Read Source Phrase into a list of dictionaries
    sourcePhrase = []
    for word in assistantTree.findall('.//FLExTransRules/FLExTransRule/Source/Phrase/Words/Word'):
        sourcePhrase.append(word.attrib)

    # Read Target Phrase into a list of dictionaries
    targetPhrase = []
    for word in assistantTree.findall('.//FLExTransRules/FLExTransRule/Target/Phrase/Words/Word'):
        # Need to read in the features contained in the 'Word' tag and in the 'Feature' tag, so we combine the two attribute dicts
        tmpWordFeatures = word.attrib
        tmpWordFeatures.update(word.find('.//Features/Feature').attrib)
        targetPhrase.append(tmpWordFeatures)

    # TODO: Using the above lists, construct the Apertium transfer rules for the specific rule

    gramCategory= 'def'
    featureAbbrev = 'gender'
    
    # Use this function to get a list of tuples (lemma, featureValue) for this category that have this feature assigned. 
    # An empty list is returned if there are errors.
    lemmaList = Utils.getLemmasForFeature(DB, report, configMap, gramCategory, featureAbbrev)

    gramCategory= 'adj'

    # Use this function to get a list of tuples (gloss, featureValue) for this category that have this feature assigned. 
    # An empty list is returned if there are errors.
    glossList = Utils.getAffixGlossesForFeature(DB, report, configMap, gramCategory, featureAbbrev)

    report.Info(str(glossList))
    report.Info(str(lemmaList))

    # report.Info(f'lemma list: {", ".join(lemmaList[0])} ; {", ".join(lemmaList[1])}')

    # report.Info(f'gloss list: {", ".join(glossList[0])} ; {", ".join(glossList[1])}')

    return True