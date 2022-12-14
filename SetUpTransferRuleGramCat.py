#
#   SetUpTransferRuleGramCat.py
#
#   Ron Lockwood
#   SIL International
#   2/22/18
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 8/29/22 - Ron Lockwood
#    Renamed module
#
#   Version 3.5.1 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5 - 6/21/22 - Ron Lockwood
#    Bump version number for FlexTools 3.5
#
#   Version 3.4.1 - 3/22/22 - Ron Lockwood
#    Fixed bug #99. Give an error if the file isn't in the format that XXE
#    makes the xml file. Otherwise it's hard to find the right section of the
#    transfer rules file to make the changes.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.1 - 1/27/22 - Ron Lockwood
#    Major overhaul of the Setup Transfer Rule Grammatical Categories Tool.
#    Now the setup tool and the bilingual lexicon uses common code for getting
#    the grammatical categories from each lexicon. Categories are 'repaired' as 
#    needed in the process. E.g. space > underscore, etc. Fixes #50.
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
import re
import xml.etree.ElementTree as ET
from FTModuleClass import *                                          
from SIL.LCModel import *                                            
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
import Utils
import ReadConfig

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Set Up Transfer Rule Categories and Attributes",
        FTM_Version    : "3.7",
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
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the path to the transfer rules file
    transfer_rules_file = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)

    # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the Output folder.
    if not transfer_rules_file:
        transfer_rules_file = 'Output\\transfer_rules.t1x'
    
    posMap = {}
    
    # Get all source and target categories
    if Utils.get_categories(DB, TargetDB, report, posMap, numCatErrorsToShow=99, addInflectionClasses=False) == True:
        TargetDB.CloseProject()
        return

    TargetDB.CloseProject()
    
    # Make a backup copy of the transfer rule file
    try:
        shutil.copy2(transfer_rules_file, transfer_rules_file+'.old')
    except:
        report.Error('There was a problem finding the transfer rules file. Check your configuration.')
        return
    
    savedLines = []
    defAttrFound = False
    gramCatfound = False
    endFound = False
    gramCatElementMissing = False
    
    tr_f = open(transfer_rules_file+'.old', encoding='utf-8')

    # Check to see that we have the def-attr section in the format that XXE saves files in. Otherwise give an error.
    linesList = tr_f.readlines()
    
    if '><def-attr' not in ''.join(linesList):
        
        report.Error('The transfer rules file has not yet been saved with the XML Mind editor. Change the file in the editor and then run this tool again.')
        tr_f.close()
        return 
    
    tr_out_f = open(transfer_rules_file, 'w', encoding='utf-8')
    
    # Read and write the 1st part of the transfer rule file -- until we get to the beginning of grammatical categories.
    # After that, skip the old grammatical category lines and then after those, save the rest of the lines to be written later.
    # Or if there is no gram_cat attribute, stop writing at the end of the attribute section
    # Note: we are not using elementTree because it doesn't preserve comments
    for line in linesList:
        
        if  re.search('><def-attr', line):
            
            defAttrFound = True
            
        if re.search('n="a_gram_cat"', line) and defAttrFound:
            
            # write this line
            tr_out_f.write(line)
            gramCatfound = True
            
        if re.search('></def-attr', line) and gramCatfound:
            
            endFound = True
        
        # check for end of the attribute section
        if re.search('></section-def-attrs', line) and not gramCatfound:
            
            endFound = True
            gramCatElementMissing = True
            tr_out_f.write('><def-attr\n')
            tr_out_f.write('n="a_gram_cat"\n')
            
        if not gramCatfound and not endFound:
            
            tr_out_f.write(line)
            
        if endFound:
            
            savedLines.append(line)
            
    count = 0

    # Loop through all of the category abbreviations and names
    for pos_abbr, pos_name in sorted(list(posMap.items()), key=lambda k_v: (k_v[0].lower(),k_v[1])):
        
        tr_out_f.write('><attr-item\n')
        tr_out_f.write('c="' + pos_name + '"\n')
        tr_out_f.write('tags="' + pos_abbr + '"\n')
        tr_out_f.write('></attr-item\n')
        
        count += 1

    if gramCatElementMissing == True:
        
        tr_out_f.write('></def-attr\n')
        
    # Write out the rest of the lines after the grammatical category section
    for line in savedLines:
        
        tr_out_f.write(line)
        
    tr_out_f.close()
    
    report.Info(str(count) + ' categories created for the a_gram_cat attribute.')
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
