#
#   SetUpTransferRuleGramCat
#
#   Ron Lockwood
#   SIL International
#   2/22/18
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
#   Version 1.0.1 - 2/28/18 - Ron Lockwood
#    Write the DOCTYPE.
#
#   Version 1.0 - 2/22/18 - Ron Lockwood
#    Initial version.
#
#   Take the grammatical categories from the bilingual lexicon file and put them
#   into the transfer rule file as tags of an attribute called a_gram_cat. It is
#   helpful to use the categories from the bilingual lexicon file because the 
#   list created there is the synthesis of unique grammatical categories from 
#   both the source and target lexicons.
#

import shutil
import xml.etree.ElementTree as ET
from FTModuleClass import *                                          
from SIL.LCModel import *                                            
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
import Utils
import ReadConfig

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Set Up Transfer Rule Grammatical Categories",
        FTM_Version    : "3.3",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : 'Set up the transfer rule file with all grammatical categories needed.' ,
        FTM_Help   : "",
        FTM_Description: 
"""
This module goes through both the source and target FLEx databases and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
"""}

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    transFile = Utils.TRANSFER_RULE_FILE_PATH
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    TargetDB = Utils.openTargetProject(configMap, report)

    posMap = {}
    
    # Get all source and target categories
    Utils.get_categories(DB, TargetDB, report, posMap, numCatErrorsToShow=99, addInflectionClasses=False)

    # Get the path to the bilingual file
    if 'BilingualDictOutputFile' not in configMap or configMap['BilingualDictOutputFile'] == '':
        report.Error('Did not find the entry BilingualDictOutputFile in the configuration file')
        return
    
    bilingFile = ReadConfig.getConfigVal(configMap, 'BilingualDictOutputFile', report)
    
    # Make a backup copy of the transfer rule file
    shutil.copy2(transFile, transFile+'.old')
    
    # Read in the transfer rule file
    try:
        transEtree = ET.parse(transFile)
    except IOError:
        report.Error('There is a problem with the Transfr Rule File: '+transFile+'.')
        return
    
    transRoot = transEtree.getroot()
    
    # Find the section-def-attrs (attribute definition section) in the transfer rules file
    section_def_attrs = transRoot.find("section-def-attrs")
    
    # See if a def-attr (attribute definition) element exists that is called a_gram_cat
    def_attr = transRoot.find(".//*[@n='a_gram_cat']")

    # If it doesn't exist create it and add it to section-def-attrs
    if def_attr is None:
        
        def_attr = ET.Element('def-attr')
        def_attr.attrib['n'] = 'a_gram_cat'
        section_def_attrs.append(def_attr)
        
    else: # delete existing sub-elements
        def_attr.clear()
        
    # Loop through all of the category abbreviations and names
    for pos_abbr, pos_name in sorted(list(posMap.items()), key=lambda k_v: (k_v[0].lower(),k_v[1])):
        
        # Create an attr-item element
        new_attr_item = ET.Element('attr-item')
        
        # Set its c and tags attributes
        new_attr_item.attrib['c'] = pos_name
        new_attr_item.attrib['tags'] = pos_abbr
        
        # Append the attr-item element to the gram cat def_attr
        def_attr.append(new_attr_item)
        
    # Write the transfer rule file (it's XML)
    transEtree.write(transFile, 'utf-8')
    
    # Prepend the lines for a proper XML file (XML Editor needs this)
    newLines = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN"\n"transfer.dtd">\n'

    f2 = open(transFile, encoding='utf-8')
    data = f2.read()
    f2.close()
    f3 = open(transFile, 'w', encoding='utf-8')
    f3.write(newLines + data)
    f3.close()
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
