#
#   RunApertium
#
#   Ron Lockwood
#   SIL International
#   1/1/17
#
#   Version 3.14 - 5/27/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.2 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 3/5/25 - Ron Lockwood
#   Fixes #909. Error messages when files don't exist.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.1 - 5/1/23 - Ron Lockwood
#    Set the modified date of the internally used tr1.t1x file to be the same as
#    the transfer_rules.t1x (or whatever the user specified) so that the transfer rules are
#    only recompiled when the rules are out of date.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.7.1 - 2/25/23 - Ron Lockwood
#    Fixes #389. Don't recreate the rule file unless something changes with the rule list.
#
#   earlier version history removed on 3/5/25
#
#   Runs the makefile that calls Apertium 
#

import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import re
import unicodedata

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from flextoolslib import *

import Mixpanel
import Utils
import ReadConfig
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RunApertium'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("RunApertium", """This module executes lexical transfer based on links from source to target sense 
you have established and then executes structural transfer which
runs the transfer rules you have made to transform source morphemes into target morphemes.
The results of this module are found in the file you specified in the Target Transfer Results File.
This is typically called target_text-aper.txt and is usually in the Build folder.""")

docs = {FTM_Name       : "Run Apertium",
        FTM_Version    : "3.14",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RunApertium", "Run the Apertium transfer engine."),
        FTM_Help  : "",  
        FTM_Description:    descr}     

app.quit()
del app

STRIPPED_RULES  = 'tr.t1x'
STRIPPED_RULES2 = 'tr.t2x'
STRIPPED_RULES3 = 'tr.t3x'
APERTIUM_ERROR_FILE = 'apertium_error.txt'
DO_MAKE_SCRIPT_FILE = 'do_make.bat'
MAKEFILE_DICT_VARIABLE = 'DICTIONARY_PATH'
MAKEFILE_SOURCE_VARIABLE = 'SOURCE_PATH'
MAKEFILE_TARGET_VARIABLE = 'TARGET_PATH'
MAKEFILE_FLEXTOOLS_VARIABLE = 'FLEXTOOLS_PATH'
GRAM_CAT_ATTRIBUTE = 'a_gram_cat'

reDoubleNewline = re.compile(r'\n\n')

bilingFixSymbProbData = []

bilingUnFixSymbProbData = [['double newline', 'converted to single newline', r'\n', reDoubleNewline]]

def fixProblemChars(fullDictionaryPath):

    # Save a copy of the bilingual dictionary
    shutil.copy2(fullDictionaryPath, fullDictionaryPath+'.before_fix')

    f = open(fullDictionaryPath, encoding='utf-8')
    contentsStr = f.read()
    f.close()

    subPairs = getListOfSymbolSubPairs(contentsStr, bilingFixSymbProbData)

    # Replace / with ||
    contentsStr = Utils.convertProblemChars(contentsStr, bilingFixSymbProbData)

    f = open(fullDictionaryPath, 'w', encoding='utf-8')
    f.write(contentsStr)
    f.close()

    return subPairs

def getListOfSymbolSubPairs(convertStr, problemDataList):

    masterList = []

    for probDataRow in problemDataList:

        foundList = probDataRow[3].findall(convertStr)

        # remove duplicates
        foundList = list(set(foundList))

        # Assume we are getting a tuple because of the capture elements
        if len(foundList) > 0 and isinstance(foundList[0], tuple) == False:
            return []

        for myItem in foundList:

            # join the tuple into a string
            trimmedItem = ''.join(myItem)

            replStr = probDataRow[3].sub(probDataRow[2], trimmedItem)
            masterList.append((trimmedItem, replStr))

    # return a list with duplicates removed
    return masterList

def unfixProblemCharsDict(fullDictionaryPath):

    # Restore original bilingual dictionary
    shutil.copy2(fullDictionaryPath+'.before_fix', fullDictionaryPath)

    # Delete the temporary dictionary file
    os.remove(fullDictionaryPath+'.before_fix')

def unfixProblemCharsRuleFile(fullTransferResultsPath):

    try:
        f = open(fullTransferResultsPath, encoding='utf-8')

        contentsStr = f.read()
        f.close()

        # Replace || with /
        contentsStr = Utils.convertProblemChars(contentsStr, bilingUnFixSymbProbData)

        f = open(fullTransferResultsPath, 'w', encoding='utf-8')
        f.write(contentsStr)
        f.close()

    except:
        pass

def subProbSymbols(buildFolder, ruleFile, subPairs):

    f = open(os.path.join(buildFolder, ruleFile), encoding='utf-8')

    contentsStr = f.read()
    f.close()

    # go through all problem symbols
    for pair in subPairs:

        # substitute all occurrences
        contentsStr = re.sub(pair[0], pair[1], contentsStr)

    f = open(os.path.join(buildFolder, ruleFile) ,"w", encoding='utf-8')
    f.write(contentsStr)
    f.close()

def stripRulesFile(report, buildFolder, transferRulePath, strippedRulesFileName):

    # Open the existing rule file
    try:
        # Note that by default this will strip comments and headers
        # (even though that is no longer necessary on newer versions
        # of apertium-transfer)
        tree = ET.parse(transferRulePath).getroot()
    except:
        report.Error(_translate("RunApertium", 'Error in opening the file: "{file}", check that it exists and that it is valid.').format(file=transferRulePath))
        return True

    # Lemmas in <cat-item> are not compared for string equality,
    # so we don't need to escape the other special characters,
    # but * will be treated as a glob matching any sequence of characters,
    # so we escape it here.
    # If any users do want the glob behavior, we'll have a problem, but
    # that strikes me as less likely.
    for cat in tree.findall('.//cat-item'):
        if 'lemma' in cat.attrib:
            cat.attrib['lemma'] = cat.attrib['lemma'].replace('*', '\\*')

    # If we're only doing one-stage transfer, then really we only need to
    # escape things when we're comparing against input (so .//test//lit),
    # but we might be doing multi-stage transfer and it doesn't hurt
    # anything to also escape the output (and it's less complicated).
    for tag in ['lit', 'list-item']:
        for node in tree.findall('.//test//'+tag):
            if 'v' in node.attrib:
                node.attrib['v'] = Utils.escapeReservedApertChars(node.attrib['v'])

    outPath = os.path.join(buildFolder, strippedRulesFileName)
    with open(outPath, 'w', encoding='utf-8') as fout:
        text = ET.tostring(tree, encoding='unicode')
        # Always write transfer rule data as decomposed
        text = unicodedata.normalize('NFD', text)
        fout.write(text)

    return False

def checkRuleAttributes(tranferRulePath):

    error_list = []

    # Verify we have a valid transfer file.
    try:
        rulesTree = ET.parse(tranferRulePath)
    except:
        error_list.append((_translate("RunApertium", 'Invalid File'), _translate("RunApertium", 'The transfer file: {file} is invalid.').format(file=tranferRulePath), 2))
        return error_list

    # Find the attributes element
    myRoot = rulesTree.getroot()

    func_err_list = checkRuleAttributesXML(myRoot)

    error_list.extend(func_err_list)

    return error_list

def checkRuleAttributesXML(myRoot):

    error_list = []

    def_attrs_element = myRoot.find('section-def-attrs')

    if def_attrs_element:

        gramCatSet = set()

        # Loop through each attribute definition
        for def_attr_el in def_attrs_element:

            # If we have the special attribute for grammatical categories, add them to a list
            if def_attr_el.attrib['n'] == GRAM_CAT_ATTRIBUTE:

                # Loop through each grammatical category
                for attr_item_el in def_attr_el:

                    # Add the next one to the list
                    gramCatSet.add(attr_item_el.attrib['tags'])

                # Once we found the grammatical category, stop
                break

        # Loop through each attribute definition
        for def_attr_el in def_attrs_element:

            # Loop through each attribute
            for attr_item_el in def_attr_el:

                attribStr = attr_item_el.attrib['tags']

                # If the attribute is the same as a grammatical category, give a warning. Of course don't check the gram cat attribute itself for this warning.
                if def_attr_el.attrib['n'] != GRAM_CAT_ATTRIBUTE:

                    if attribStr in gramCatSet:

                        error_list.append((_translate("RunApertium", 'The attribute: "{attribStr}" in "{attrName}" is the same as a gramm. cat. Your rules may not work as expected.').format(attribStr=attribStr, attrName=def_attr_el.attrib["n"]), 1))

                # Make sure there are no periods in the attribute, if there are give a warning
                if attribStr and re.search(r'\.', attribStr):

                    error_list.append((_translate("RunApertium", 'The attribute: "{attribStr}" in "{attrName}" has a period in it. It needs to be an underscore. Your rules may not work as expected.').format(attribStr=attribStr, attrName=def_attr_el.attrib["n"]), 1))
    return error_list

# Get relative path to the given build folder and file
def turnPathIntoEnvironPath(absPathToBuildFolder, myPath):

    # See if we have an absolute path
    if os.path.isabs(myPath):

        relPath = os.path.relpath(myPath, absPathToBuildFolder)

    # If it's not an absolute path, we assume it's relative to the work project subfolder (e.g. WorkProjects\German-Swedish)
    # So from doing the make from the Build folder, we need to add ..\ to all of the paths we get from the config file.
    else:
        relPath = os.path.join('..', myPath)

    return relPath

# Run the makefile to run Apertium tools to do the transfer
# component of FLExTrans. The makefile is run by invoking a
# bash file. Absolute paths seem to be necessary.
# relPathToBashFile is expected to be with Windows backslashes
def run_makefile(absPathToBuildFolder, report):

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return True

    # Get the path to the dictionary file
    dictionaryPath = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not dictionaryPath:
        return True

    dictionaryPath = turnPathIntoEnvironPath(absPathToBuildFolder, dictionaryPath)

    # Get the path to the source apertium file
    analyzedPath = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not analyzedPath:
        return True

    analyzedPath = turnPathIntoEnvironPath(absPathToBuildFolder, analyzedPath)

    # Get the path to the target apertium file
    transferResultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    if not transferResultsPath:
        return True

    transferResultsPath = turnPathIntoEnvironPath(absPathToBuildFolder, transferResultsPath)

    # Create the batch file which merely cds to the appropriate
    # directory and runs make.
    fullPathMake = os.path.join(absPathToBuildFolder, DO_MAKE_SCRIPT_FILE)
    f = open(fullPathMake, 'w', encoding='utf-8')

    # make a variable for where the bilingual dictionary file should be found
    outStr = f'set {MAKEFILE_DICT_VARIABLE}={dictionaryPath}\n'

    # make a variable for where the analyzed text file should be found
    outStr += f'set {MAKEFILE_SOURCE_VARIABLE}={analyzedPath}\n'

    # make a variable for where the transfer results file should be found
    outStr += f'set {MAKEFILE_TARGET_VARIABLE}={transferResultsPath}\n'

    # Get the current working directory which should be the FlexTools folder
    # cwd = os.getcwd()

    flexToolsPath = turnPathIntoEnvironPath(absPathToBuildFolder, FTPaths.TOOLS_DIR)

    # make a variable for where the apertium executable files and dlls are found
    outStr += f'set {MAKEFILE_FLEXTOOLS_VARIABLE}={flexToolsPath}\n'

    # set path to nothing
    outStr += f'set PATH=""\n'

    # Put quotes around the path in case there's a space
    outStr += f'cd "{absPathToBuildFolder}"\n'

    #fullPathErrFile = os.path.join(absPathToBuildFolder, APERTIUM_ERROR_FILE)
    outStr += f'"{FTPaths.MAKE_EXE}" 2>"{APERTIUM_ERROR_FILE}"\n'

    f.write(outStr)
    f.close()

    retVal = subprocess.call([fullPathMake])

    return retVal

def runApertium(DB, configMap, report):

    # Get parent folder of the folder flextools.ini is in and add \Build to it
    buildFolder = FTPaths.BUILD_DIR

    # Get the path to the dictionary file
    dictionaryPath = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    if not dictionaryPath:
        return None
    
    # See if the dictionary file exists.
    if not os.path.exists(dictionaryPath):
        report.Error(_translate("RunApertium", 'The bilingual dictionary file does not exist. You may need to run the Build Bilingual Lexicon module. The file should be: {file}').format(file=dictionaryPath))
        return True
    
    # Get the path to the analyzed text
    analyzedTextPath = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not analyzedTextPath:
        return True
    
    # See if the source text file exists.
    if not os.path.exists(analyzedTextPath):
        report.Error(_translate("RunApertium", 'The analyzed text file does not exist. You may need to run the Extract Source Text module. The file should be: {file}').format(file=analyzedTextPath))
        return True
    
    # Get the path to the target apertium file
    transferResultsPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    if not transferResultsPath:
        return None
    
    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)
    if not tranferRulePath:
        return None

    # Get the modification date of the transfer rule file.
    statResult = os.stat(tranferRulePath)

    # Escape some characters and write as NFD unicode.
    if stripRulesFile(report, buildFolder, tranferRulePath, STRIPPED_RULES) == True:
        return None
    
    ## Advanced transfer files
    
    # Get the path to the 2nd transfer rules file (could be blank)
    tranferRulePath2 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE2, report, giveError=False)
    if tranferRulePath2:

        # Escape some characters and write as NFD unicode.
        if stripRulesFile(report, buildFolder, tranferRulePath2, STRIPPED_RULES2) == True:
            return None

    # Get the path to the 3rd transfer rules file (could be blank)
    tranferRulePath3 = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE3, report, giveError=False)
    if tranferRulePath3:

        # Escape some characters and write as NFD unicode.
        if stripRulesFile(report, buildFolder, tranferRulePath3, STRIPPED_RULES3) == True:
            return None

    # Check if attributes are well-formed. Warnings will be reported in the function
    error_list = checkRuleAttributes(tranferRulePath)

    Utils.processErrorList(error_list, report)

    # Fix problem characters in symbols of the bilingual lexicon (making a backup copy of the original file)
    subPairs = fixProblemChars(dictionaryPath)
    
    # Substitute symbols with problem characters with fixed ones in the transfer file
    subProbSymbols(buildFolder, STRIPPED_RULES, subPairs)
    
    # Set the modification date to be the same as the original rules file so that the makefile that runs the Apertium tools
    # won't recompile the transfer_rules if they are not out of date.
    os.utime(os.path.join(buildFolder, STRIPPED_RULES), times=None, ns=(statResult.st_atime_ns, statResult.st_mtime_ns))

    # Run the makefile to run Apertium tools to do the transfer component of FLExTrans. 
    ret = run_makefile(buildFolder, report)
    
    if ret:
        report.Error(_translate("RunApertium", 'An error happened when running the Apertium tools. The contents of apertium_error.txt is:'))
        try:
            f = open(os.path.join(buildFolder, APERTIUM_ERROR_FILE), encoding='utf-8')
            lines = f.readlines()
            [report.Error(line) for line in lines]
        except:
            pass

    # Convert back the problem characters in the transfer results file back to what they were. Restore the backup biling. file
    unfixProblemCharsRuleFile(transferResultsPath)
    unfixProblemCharsDict(dictionaryPath)
    report.Info(_translate("RunApertium", 'Transferred text put in the file: {file}.').format(file=Utils.getPathRelativeToWorkProjectsDir(transferResultsPath)))
    report.Info(_translate("RunApertium", 'Apertium transfer complete.'))
    
    return 1
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    runApertium(DB, configMap, report)

    
#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
