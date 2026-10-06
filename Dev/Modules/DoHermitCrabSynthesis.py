#
#   DoHermitCrabSynthesis.py
#
#   Ron Lockwood
#   SIL International
#   3/8/23
#
#   Version 3.17.1 - 9/29/26 - Ron Lockwood
#    Fixes #1334. Open the target with Utils.openTargetProject and take its .fwdata path from the opened project, so a target stored elsewhere works. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.2 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16.1 - 6/26/26 - Ron Lockwood
#    One project mode: generate the HermitCrab config from a temporary copy of the project whose default vernacular WS is the chosen target writing system, so the live project is never modified.
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.3 - 5/4/26 - Ron Lockwood
#    Fixes #1262. Pass the extra language code to HC tools.
#
#   Version 3.15.2 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15.1 - 2/11/26 - Ron Lockwood
#    Fixes #1199. Add error handling around the call to produce the synthesis file 
#    so if there is an error we can report it instead of crashing.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.3 - 8/16/25 - Ron Lockwood
#    Fixes #1040. Use lemma and category in our saved catalog for mapping capitalized
#    words to lowercase words.
#
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14.1 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.3 - 6/2/25 - Ron Lockwood
#    Improved exception handling around use of the HermitCrab DLL.
# 
#   Version 3.13.2 - 3/20/25 - Ron Lockwood
#    Move the Mixpanel logging to the main function. Callers should do it.
# 
#   Version 3.13.1 - 3/19/25 - Ron Lockwood
#    Use abbreviated path when telling user what file was used.
#    Updated module description.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.7 - 2/12/25 - Ron Lockwood
#    Fixes #888. Show better error when there is a Fatal error from HermitCrab tools in the LRT.
#
#   Version 3.12.6 - 1/10/25 - Ron Lockwood
#    Fixes #843. Fix bug of setting the HC dll's config file when it did not exist.
#
#   Version 3.12.5 - 1/2/25 - Ron Lockwood
#    Fix decode error when outputting Synthesis errors.
#
#   Version 3.12.4 - 1/2/25 - Ron Lockwood
#    Fixes problem with HC synthesis where title-cased phrases were not coming out in the write case.
#
#   Version 3.12.3 - 12/4/24 - Ron Lockwood
#    Filter out the GenerateHC message 'Checking for duplicates', so the user doesn't see a warning.
#
#   Version 3.12.2 - 11/27/24 - Ron Lockwood
#    Fixes #818. Call a dll for HC synthesis to speed up the process.
#
#   Version 3.12.1 - 11/22/24 - Ron Lockwood
#    Fixes #812. Capitalize a word before sending it to synthesis if it is capitalized in the target
#    lexicon. We can quickly read the target lexicon by loading the HCconfig file.
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
#   Version 3.10.1 - 1/12/24 - Ron Lockwood
#    Fixes #538. Escape brackets in the pre or post punctuation.
#
#   Version 3.10 - 1/2/24 - Ron Lockwood
#    Fixes #531. When replacing sentence punctuation lexical units with only the punctuation,
#    account for the fact that failed synthesis words will also have ^ in the string. Fixed the regex.
#
#   2023 version history removed on 2/6/26
#
#   OVERVIEW (AI generated, then edited)
#
#   This module is the HermitCrab alternative to STAMP for the last step of FLExTrans: turning the target parses that come out of the Apertium transfer rules into real target words. HermitCrab (HC)
#   is one of the morphological engines built into FLEx. FLExTrans drives it through two external tools: one exports the whole target project (lexicon, rules and settings) as an XML HermitCrab.config file,
#   and the other synthesizes surface forms from gloss-style parses using that CML HermitCrab.config. This module prepares the inputs for those tools, runs them, and stitches the surface forms back into the
#   transfer results to produce the file named by the Target Output Synthesis File setting.
#
#   The module can be run on its own from FlexTools, but most of its use is from other code. DoSynthesis (when Use HermitCrab Synthesis is on) and TranslateText call doHermitCrab(). The Live Rule
#   Tester calls extractHermitCrabConfig() and synthesizeWithHermitCrab() directly, with its own file names (HermitCrabMaster.txt, HermitCrabParses.txt, etc.) and a loaded HC DLL object for speed.
#   Keep those callers in mind when changing a function signature or the (message, level) error-list convention every function here returns.
#
#   THE FILES, IN THE ORDER THEY ARE USED
#
#    - Master file (target_words-HC.txt, or HermitCrabMaster.txt in the LRT). Written earlier by the Convert Text to Synthesizer Format module, not by this one. One line per UNIQUE parse, in the
#      form X,Y. X is the Apertium lexical unit ^...$. Y is A|B|...|G, where A is Q;N - Q is the parse in HC order (<pfx1>...<pfxN>root<cat><sfx1>...<sfxN>, built by consulting the affix list
#      file) and N is the capitalization code, which may be empty. B through G have the same form as A and are the further words of a phrase.
#    - HermitCrab.config (in the Build folder). Generated here from the target project by the Generate HC Config tool. It is a full target lexicon plus all the rules, and it takes a while to build.
#    - Parses file (target_words-parses.txt, or HermitCrabParses.txt in the LRT). Written here from the master file: one line per master line holding the Q parses as consecutive ^...$ units, with
#      lemmas restored to their case in the config. This is what HC synthesizes.
#    - Surface forms file (target_words-surface.txt, or HermitCrabSurfaceForms.txt in the LRT). Written by HC, one line per parses line; the words of a phrase are separated by commas.
#    - Transfer results file (target_text-aper.txt). This is the input file, and the synthesis file (target_text-syn.txt, or myText.txt in the LRT) is the output. Every lexical unit in the transfer results 
#      is replaced by its surface form.
#
#   WHERE THE TARGET PROJECT COMES FROM
#
#   In Two project mode Utils.openTargetProject opens the TargetProject setting, which may be a bare project name or the full path of a .fwdata file outside the standard FLEx Projects folder
#   (#1334). The Generate HC Config tool needs the path of the .fwdata file, so it is taken from the opened project with Utils.projectOpenName() rather than rebuilt from the Projects folder plus the
#   name, which would point at a file that doesn't exist for a project kept elsewhere. (projectOpenName() falls back to the bare name if LCM won't give the path, so a failure there shows up as a
#   Generate HC Config error, not here.) If the target can't be opened, openTargetProject adds the reason to the error list and doHermitCrab() returns it.
#
#   In One project mode there is no target project; the source project holds the target writing system. This module always synthesizes in the project's default vernacular writing system, so
#   buildTempProjectInTargetWS() copies the project folder (minus LinkedFiles and lock files) to a temp folder, moves the target WS to the front of the <CurVernWss> element in the copy's .fwdata, and the config
#   is generated from the copy. The live project is never modified, and the copy is deleted in a finally block whether generation worked or not.
#
#   CACHING
#
#   Regenerating the XML config file is slow, so it is skipped when the following is true: 1) the CacheData FLExTrans setting is set to 'y', 2) the caller asked for the cache (doHermitCrab always does; 
#   the LRT does unless the user forces a refresh), and 3) the config file is newer than the target project's last-modified date (configFileOutOfDate()). 
#   When a DLL object is in use it must still be pointed at the config file even on a cache hit, because a freshly created DLL object has no config loaded yet.
#
#   THINGS THAT LOOK ODD BUT MATTER
#
#    - This module's FlexTools messages say the source project is being used. It is really the target project; FlexTools doesn't know about the target project.
#    - Capitalization: for a word with a capitalization code, the lemma in the master file may not have the case the target lexicon uses (a proper noun, say), and HC would not find the entry.
#      getCapitalLemmas() reads every capitalized lemma from the XML config (the entry's Gloss element) keyed on lowercase lemma + category name (#1040), and capitalize() restores it before synthesis.
#      Without the category in the key, a word could be capitalized just because a proper noun shares its spelling. The capitalization code itself (sentence-initial, all caps, ...) is applied
#      separately, to the surface form, in produceSynthesisFile().
#    - @ words (unknown to the target lexicon) are written to the parses file as blank lines and are not added to luInfoList. produceSynthesisFile() drops blank surface form lines before it checks
#      that the surface form count equals the lexical unit count, and it is that pairing that keeps line i of the surface forms matched to entry i of luInfoList. Change one side and not the other
#      and every word after the first @ word gets the wrong surface form.
#    - Each lexical unit is substituted into the transfer results with a global re.sub, which is why the master file holds only unique parses: one surface form replaces every occurrence.
#    - A failed word comes back as %0%^parse$% plus an error. The sentence punctuation regex in produceSynthesisFile() is careful not to treat the ^ inside such a string as the start of a <sent>
#      unit. fixUpText() later strips these markers, sense numbers, @ signs and tags only when the Cleanup Unknown Words setting is on (or the LRT's "do not clean up" box isn't checked).
#    - With a DLL object, synthesizeWithHermitCrab() never passes the surface forms file name to HC (only the exe gets it on the command line),
#      so the caller must already have set the DLL's output to that file before calling.
#
#   CODE STRUCTURE
#
#   After the docs dictionary: configFileOutOfDate() is the cache test, buildTempProjectInTargetWS() makes the One project mode copy, and generateHCConfigFile() runs the Generate HC Config tool and
#   (re)loads the result into the DLL object. extractHermitCrabConfig() is the lexicon step and ties those three together: it opens the target project (or reuses the source DB), gets the .fwdata
#   path, and either uses the cached config or generates a new one. gatherWarnings() turns the generator's stdout into warnings.
#
#   The synthesis side follows. produceSynthesisFile() does the substitution into the transfer results, createHermitCrabParsesFile() writes the parses file and fills luInfoList, capitalize() and
#   extractRootAndFirstTag() restore lemma case, fixUpText() does the optional clean up, and getCapitalLemmas() builds the capitalization map from the config. synthesizeWithHermitCrab() is the
#   synthesis step and calls them in the order getCapitalLemmas(), createHermitCrabParsesFile(), HC (DLL or exe), produceSynthesisFile(), fixUpText().
#
#   Control flow: FlexTools calls MainFunction(), which loads translations, reads the settings, logs to Mixpanel and calls doHermitCrab(). doHermitCrab() calls extractHermitCrabConfig() and then
#   synthesizeWithHermitCrab() and reports the collected error list. The FlexToolsModule declaration is at the very bottom.
#

import os
import re
import subprocess
import shutil
import tempfile
from datetime import datetime
import xml.etree.ElementTree as ET

from SIL.LCModel import *                                                    # type: ignore

from flextoolslib import * # type: ignore

from PyQt6.QtCore import QCoreApplication, QTranslator
from PyQt6.QtWidgets import QApplication

import Mixpanel
import ReadConfig
import Utils
import FTPaths
from RunApertium import docs as RunApertDocs

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'DoHermitCrabSynthesis'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("DoHermitCrabSynthesis", "Synthesize Text with HermitCrab"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("DoHermitCrabSynthesis", "Synthesizes the target text with the tool HermitCrab."),
        FTM_Help       :"",
        FTM_Description: _translate("DoHermitCrabSynthesis", 
"""This module runs HermitCrab to create the
synthesized text. The results are put into the file designated in the Settings as Target Output Synthesis File.
This will default to something like 'target_text-syn.txt'. 
Before creating the synthesized text, this module extracts the target language lexicon in the form of a HermitCrab
configuration file. 
It is named 'HermitCrab.config' and will be in the 'Build' folder. 
NOTE: Messages will say the source project
is being used. Actually the target project is being used.
Advanced Information: This module runs HermitCrab against a list of target parses ('target_words-parses.txt') to
produce surface forms ('target_words-surface.txt'). 
These forms are then used to create the target text.""")}

description = docs[FTM_Description]

#app.quit()
#del app

SUCCESS = 'Success!'

def configFileOutOfDate(targetDB, HCconfigPath):

    # Build a DateTime object with the FLEx DB last modified date
    flexDate = targetDB.GetDateLastModified()
    tgtDbDateTime = datetime(flexDate.get_Year(),flexDate.get_Month(),flexDate.get_Day(),flexDate.get_Hour(),flexDate.get_Minute(),flexDate.get_Second())
    
    # Get the date of the cache file
    try:
        mtime = os.path.getmtime(HCconfigPath)

    except OSError:

        mtime = 0

    HCconfigFileDateTime = datetime.fromtimestamp(mtime)
    
    if tgtDbDateTime > HCconfigFileDateTime: # FLEx DB is newer

        return True 
    
    else: # affix file is newer

        return False

# Build a temporary copy of the project whose default vernacular writing system is the chosen target WS, so the external HermitCrab
# config generator (which reads the default vernacular WS from the .fwdata file) produces a config in the target WS WITHOUT
# modifying the live project. Returns (tempFwdataPath, tempRootDir); the caller deletes tempRootDir when done. (None, None) on failure.
def buildTempProjectInTargetWS(sourceFwdataPath, projName, targetWSTag, report):

    sourceProjFolder = os.path.dirname(sourceFwdataPath)
    tempRoot = tempfile.mkdtemp(prefix='FLExTransHC_')
    tempProjFolder = os.path.join(tempRoot, projName)

    try:
        # Copy the project, skipping media and lock files which the config generator does not need.
        shutil.copytree(sourceProjFolder, tempProjFolder, ignore=shutil.ignore_patterns('LinkedFiles', '*.lock'))

    except Exception as e:

        shutil.rmtree(tempRoot, ignore_errors=True)

        if report:

            report.Error(_translate("DoHermitCrabSynthesis", 'Could not copy the project for One project mode synthesis. Error: {e}').format(e=e))

        return (None, None)

    tempFwdata = os.path.join(tempProjFolder, projName + '.fwdata')

    # Read the fwdata file.
    with open(tempFwdata, encoding='utf-8') as f:

        lines = f.readlines()

    for i, line in enumerate(lines):

        if re.search(r'<CurVernWss>', line):

            # The next line has the writing system tags. Find the tags
            tagStr = re.search(r'<Uni>(.*?)</Uni>', lines[i+1])

            # Put the tags in a list
            tags = tagStr.group(1).split() if tagStr else []

            # Put the target WS first in the list, keeping any others after it.
            reordered = [targetWSTag] + [tag for tag in tags if tag != targetWSTag]

            # old tags with the new reordered tags
            newLine = re.sub(r'(<Uni>)(.*?)(</Uni>)', r'\1' + ' '.join(reordered) + r'\3', lines[i+1])
            lines[i+1] = newLine
            break

    # Write the lines back to the temporary .fwdata file
    with open(tempFwdata, 'w', encoding='utf-8') as f:

        f.writelines(lines)

    return (tempFwdata, tempRoot)

# Run the external HermitCrab config generator on genFwdataPath, writing HCconfigPath, then (re)load it into the DLL object. Errors
# and warnings are appended to errorList. projName is only used for the KeyNotFoundException hint message.
def generateHCConfigFile(genFwdataPath, HCconfigPath, projName, DLLobj, errorList):

    try:
        result = subprocess.run([FTPaths.GENERATE_HC_CONFIG, genFwdataPath, HCconfigPath], capture_output=True)

        if result.returncode == 0:

            gatherWarnings(result, errorList)
            errorList.append((_translate("DoHermitCrabSynthesis", "Generated the HermitCrab config. file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(HCconfigPath)), 0))
        else:
            errorList.append((_translate("DoHermitCrabSynthesis", "An error happened when running the Generate HermitCrab Configuration tool."), 2))

            # Check for KeyNotFoundException from FLEx
            if re.search('KeyNotFoundException', result.stderr.decode()):

                errorList.append((_translate("DoHermitCrabSynthesis", "The error contains a 'KeyNotFoundException' and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} project.").format(projectName=projName), 2))
                errorList.append((_translate("DoHermitCrabSynthesis", "The full error message is:"), 2))

            errorList.append((result.stderr.decode(), 2))
            return

        # Reload the config file into the dll object.
        if DLLobj:

            try:
                if (ret := DLLobj.SetHcXmlFile(HCconfigPath)) != SUCCESS:

                    errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)'), 2))
                    return

            except Exception as e:

                errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}').format(e=e), 2))
                return

    except subprocess.CalledProcessError as e:

        errorList.append((_translate("DoHermitCrabSynthesis", "An error happened when running the Generate HermitCrab Configuration tool."), 2))
        errorList.append((e.stderr.decode(), 2))

def extractHermitCrabConfig(DB, configMap, HCconfigPath, report=None, useCacheIfAvailable=False, DLLobj=None):

    errorList = []

    # In One project mode there is no separate target project: the HermitCrab config is generated from a temporary copy of the
    # source project whose default vernacular WS is the chosen target WS (done in the generation branch below), so the live
    # project is never touched. Reuse the source DB and remember the target WS tag. Otherwise open the configured target project.
    oneProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) == 'n'
    targetWSTag = None

    if oneProjectMode:

        TargetDB = DB
        targetWSTag = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_WRITING_SYSTEM, report, giveError=False)
    else:

        # Open the target database. openTargetProject adds the problem to errorList if it can't.
        TargetDB = Utils.openTargetProject(configMap, report, errorList)

        if TargetDB is None:

            return errorList

    # Get fwdata file path from the opened project rather than building it from the name, since the project may be outside the standard FLEx Projects folder.
    fwdataPath = Utils.projectOpenName(TargetDB)
        
    cacheData = ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report)

    if not cacheData:
        errorList.append((_translate("DoHermitCrabSynthesis", "A value for {cacheData} not found in the configuration file.").format(cacheData=ReadConfig.CACHE_DATA), 2))
        return errorList
    
    if cacheData == 'y':
        
        DONT_CACHE = False
    else:
        DONT_CACHE = True
    
    # If the target FLEx project hasn't changed and useCache is true than don't run HermitCrab, just return
    if not DONT_CACHE and useCacheIfAvailable and not configFileOutOfDate(TargetDB, HCconfigPath):

        if DLLobj:
            
            try:
                xmlFile = DLLobj.get_HcXmlFile()

                if (ret := DLLobj.SetHcXmlFile(HCconfigPath)) != SUCCESS:

                    errorList.append((_translate("DoHermitCrabSynthesis", "An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)"), 2))
            
            except Exception as e:

                errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}').format(e=e), 2))
                return errorList

            if xmlFile == '':

                try:
                    if (ret := DLLobj.SetHcXmlFile(HCconfigPath)) != SUCCESS:

                        errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)'), 2))
                        return errorList
    
                except Exception as e:

                    errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}').format(e=e), 2))
                    return errorList

        errorList.append((_translate("DoHermitCrabSynthesis", "The HermitCrab configuration file is up to date."), 0))
        return errorList
    else:
        # In One project mode, generate from a temporary copy of the project whose default vernacular writing system is the chosen
        # target WS, so the live project is never modified. In Two project mode, generate from the target project's file directly.
        tempRoot = None
        genFwdataPath = fwdataPath

        if oneProjectMode and targetWSTag:

            genFwdataPath, tempRoot = buildTempProjectInTargetWS(fwdataPath, TargetDB.ProjectName(), targetWSTag, report)

            if genFwdataPath is None:

                errorList.append((_translate("DoHermitCrabSynthesis", "Could not prepare a temporary copy of the project for One project mode synthesis."), 2))
                return errorList

        try:
            generateHCConfigFile(genFwdataPath, HCconfigPath, TargetDB.ProjectName(), DLLobj, errorList)

        finally:

            # Always remove the temporary project copy (if we made one).
            if tempRoot:

                shutil.rmtree(tempRoot, ignore_errors=True)

    return errorList

def gatherWarnings(result, errorList):

    # Convert the byte stdout to a list of output lines. We expect Carriage return & Line feeds
    try:
        outputLines = re.split(r'\r*\n', result.stdout.decode('utf-8'))
    except UnicodeDecodeError:
        outputLines = re.split(r'\r*\n', result.stdout.decode('latin-1'))

    for outputLine in outputLines:

        # if an output line isn't about loading or writing, show it to the user as a warning (1)
        if outputLine and not re.search('Loading|Writing|Checking', outputLine):

            errorList.append((outputLine.strip(), 1))

def produceSynthesisFile(luInfoList, surfaceFormsFile, transferResultsFile, synFile):
    
    errorList = []

    # Open the surface forms file
    try:
        fSurfaceForms = open(surfaceFormsFile, encoding='utf-8-sig')

    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'There was an error opening the HermitCrab surface forms file.'), 2))
        return errorList

   # Open the transfer results file
    try:
        fResults = open(transferResultsFile, encoding='utf-8')

    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'The file: {transferResultsFile} was not found. Did you run the {runApertium} module?').format(transferResultsFile=Utils.shortenPathForDisplay(transferResultsFile), runApertium=RunApertDocs[FTM_Name]), 2))
        return errorList
    
    # Read the results file into a string
    resultsFileStr = fResults.read()

    # Read in the surface forms
    surfaceFormsList = fSurfaceForms.readlines()

    # Remove blank lines
    surfaceFormsList = [line for line in surfaceFormsList if line.strip()]

    # Do a sanity check to see if the number of surface forms matches the number of Lexical unit strings
    if len(surfaceFormsList) != len(luInfoList):

        errorList.append((_translate("DoHermitCrabSynthesis", 'The number of surface forms does not match the number of Lexical Units.'), 2))
        return errorList

    # Loop through the surface forms file. Some lines will have multiple surface forms
    for i, line in enumerate(surfaceFormsList):

        line = line.strip()

        # parse multiple surface forms
        surfaceStrList = re.split(',', line)
            
        (originalLUStr, capCodeList) = luInfoList[i]

        newSurfaceList = []

        # Loop through possible multiple surface forms
        for j, surfaceStr in enumerate(surfaceStrList):

            # See if we have an error E.g. %0%^iba1.1<n><PC.1Sg>$%
            if surfaceStr[0:3] == '%0%':

                # Everything left of the last % is what we are saving for the surface string
                saveStr = surfaceStr[:surfaceStr.rindex('%')+1]

                # Save the error. Everthing to the right of the last %
                # Make this a warning, code = 1
                errStr = surfaceStr[surfaceStr.rindex('%')+1:]

                if errStr.strip() == '':

                    errStr = _translate("DoHermitCrabSynthesis", 'Synthesis failed. ({saveStr})').format(saveStr=saveStr)

                errorList.append((errStr, 1))
                surfaceStr = saveStr

            surfaceStr = Utils.capitalizeString(surfaceStr, capCodeList[j])
            newSurfaceList.append(surfaceStr)

        # substitute the Apertium parse with the surface form throughout the target text 
        resultsFileStr = re.sub(re.escape(originalLUStr), " ".join(newSurfaceList), resultsFileStr)

    # Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x
    # This regex looks for a non-% or beg. of string followed by a ^ in order to find the sentence lexical unit. The reason why we need the non-% is because
    # some of the words may not have synthesized and the error string in the form of %0%^iba1.1<n><PC.1Sg>$% may be there so we don't want to start the string
    # to replace with the ^ that's right after the % in the error string. Also there might be an error string right before the sentence punc. so allow $%^.
    resultsFileStr = re.sub(r'([^%]|^|\$%)\^(.+?)<sent>\$', r'\1\2', resultsFileStr)
            
    # Open the synthesis file
    try:
        fSyn = open(synFile, "w", encoding='utf-8')
        fSyn.write(resultsFileStr)

    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'Error writing the file: {synFile}.').format(synFile=Utils.shortenPathForDisplay(synFile)), 2))

    fSyn.close()
    fSurfaceForms.close()
    fResults.close()
    return errorList

def createHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap):

    errorList = []

    # Open master file
    try:
        fMaster = open(masterFile, encoding='utf-8')

    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'There was an error opening the HermitCrab master file. Do you have the setting "Use HermitCrab Synthesis" turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}').format(parsesFile=Utils.shortenPathForDisplay(parsesFile)), 2))
        return errorList

    # Open parses file
    try:
        fParses = open(parsesFile, 'w', encoding='utf-8')

    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'There was an error opening the HermitCrab parses file.'), 2))
        return errorList

    # Parse each line - format: LU,HCparse1;capitalizationCode|HCparse2;capitalizationCode|...
    for line in fMaster:

        line = line.rstrip()

        if len(line) == 0:
            continue

        # Get the lexical unit (expect exactly one comma separating LU and parses)
        parts = re.split(',', line)

        if len(parts) != 2:
            errorList.append((_translate("DoHermitCrabSynthesis", 'Malformed Lexical Unit in HermitCrab master file skipping this line: {line}').format(line=line), 2))
            continue
        luStr, HCparseStr = parts

        # skip @ words. They have the form: ^@...
        if HCparseStr[1] == '@':

            fParses.write('\n')
            continue

        # Get the parses
        HCparsesList = re.split(r'\|', HCparseStr)
        capCodeList = []

        # Get the parse and capitalization code pair
        for hcparseCombo in HCparsesList:

            hcParse, capCode = re.split(';', hcparseCombo)
            capCodeList.append(capCode)

            # Capitalize if necessary
            if capCode:
                hcParse = capitalize(hcParse, HCcapitalLemmasMap)

            # Write the parse to the parses file
            fParses.write('^' + hcParse + '$')
        
        fParses.write('\n')
        luInfoList.append((luStr, capCodeList))

    fMaster.close()
    fParses.close()
    return errorList

def capitalize(hcParse, HCcapitalLemmasMap):

    root, posName = extractRootAndFirstTag(hcParse)

    if root is None or posName is None:

        return hcParse  # fallback

    key = root.lower() + (posName if posName else "")
    rootCap = HCcapitalLemmasMap.get(key, root)

    # Replace only the first occurrence of root with rootCap
    rebuilt = hcParse.replace(root, rootCap, 1)
    return rebuilt

import re

def extractRootAndFirstTag(hcParse):
    """
    Returns (root, firstTagAfterRoot) from a HermitCrab parse string.
    Example: <2s.S2>tang1.1<v><3sg><obj> -> ('tang1.1', 'v')
    """

    # Find all tags. There should be at least one tag - the POS
    tagMatches = list(re.finditer(r'<([^>]+)>', hcParse))
    root = None
    firstTagAfterRoot = None

    # If there are no tags, the whole string is the root
    if not tagMatches:

        return hcParse, None

    # Find the root: the text between the last '>' and the next '<'
    for i, match in enumerate(tagMatches):

        # No tags before the root
        if i == 0 and match.start() > 0:

            root = hcParse[0:match.start()]

            # The first tag will this 0th match
            firstTagAfterRoot = match.group(1)
            return root, firstTagAfterRoot
        
        # Root must be after a prefix
        elif i > 0:

            prev = tagMatches[i-1]

            # The root will be found where there is a gap between tags
            if prev.end() < match.start():

                root = hcParse[prev.end():match.start()]

                # The first tag will be the ith match (the one after the gap)
                firstTagAfterRoot = match.group(1)
                return root, firstTagAfterRoot

    # If no root found in the loop, check after the last tag
    lastTag = tagMatches[-1]

    if lastTag.end() < len(hcParse):

        root = hcParse[lastTag.end():]
        return root, None

    # Fallback: no root found
    return None, None

# Remove @ signs at the beginning of words and N.N at the end of words if so desired in the settings.
# Also symbols and ^%0%...%$
def fixUpText(synFile, cleanUpText):
    
    # Read the contents
    f_s = open(synFile, encoding="utf-8")
    synFileContents = f_s.read()
    f_s.close()

    # Make replacements
    f_s = open(synFile, 'w', encoding="utf-8")

    if cleanUpText:

        # Remove n.n on lemmas
        synFileContents = re.sub(r'\d+\.\d+', '', synFileContents, flags=re.RegexFlag.A) # re.A=ASCII-only match
        
        # Remove at signs
        synFileContents = re.sub('@', '', synFileContents)

        # Remove symbols, i.e. <xyz>
        synFileContents = re.sub('<.*?>', '', synFileContents)

        # Remove the ^%0%...%$ (^ and $ are optional which is the case for unknown punctuation)
        synFileContents = re.sub(r'%0%\^{0,1}(.*?)\${0,1}%', r'\1', synFileContents)

    # Un-escape punctuation text that was escaped before running apertium tools. E.g. convert \] to ]
    synFileContents = Utils.unescapeReservedApertChars(synFileContents)

    f_s.write(synFileContents)
    f_s.close()

def getCapitalLemmas(HCconfigPath):

    # Create a dictionary to store the extracted lemmas
    HCcapitalLemmasMap = {}

    # Read the contents of the file
    try:
        # Parse the HermitCrab.config XML file
        tree = ET.parse(HCconfigPath)
        root = tree.getroot()
    except:
        return None

    # Find the PartsOfSpeech element
    partsOfSpeechElem = root.find('.//PartsOfSpeech')

    # Build a dictionary mapping part of speech id to name
    partOfSpeechMap = {}

    if partsOfSpeechElem is not None:

        for posElem in partsOfSpeechElem.findall('PartOfSpeech'):

            posId = posElem.get('id')
            nameElem = posElem.find('Name')

            if posId and nameElem is not None and nameElem.text:

                partOfSpeechMap[posId] = nameElem.text

    # Iterate over all LexicalEntry elements
    for lexEntry in root.findall('.//LexicalEntry'):
        
        glossElem = lexEntry.find('Gloss')
        posId = lexEntry.get('partOfSpeech')
        
        # Only proceed if both gloss and partOfSpeech are present and valid
        if glossElem is not None and glossElem.text and posId in partOfSpeechMap:

            glossText = glossElem.text
            posName = partOfSpeechMap[posId]
            
            # Only add if any letter in the gloss is uppercase
            if any(char.isupper() for char in glossText):

                # Build a key for the map of gloss name + POS
                key = (glossText.lower() + posName)
                HCcapitalLemmasMap[key] = glossText

    return HCcapitalLemmasMap

def synthesizeWithHermitCrab(configMap, HCconfigPath, synFile, parsesFile, masterFile, surfaceFormsFile, transferResultsFile, report=None, trace=False, DLLobj=None, overrideClean=False):
    
    errorList = []
    luInfoList = []

    HCcapitalLemmasMap = getCapitalLemmas(HCconfigPath)

    if HCcapitalLemmasMap is None:

        errorList.append((_translate("DoHermitCrabSynthesis", 'Unable to open the HC master file.'), 2))
        return errorList

    errorList = createHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap)

    for triplet in errorList:

        if triplet[1] == 2: # error

            return errorList

    # Call HCSynthesis to produce surface forms. 
    try:
        # Do the operation with a dll differently than with the normal exe.
        if DLLobj:

            DLLobj.LocaleCode = Utils.getInterfaceLangCode()

            if trace:
                DLLobj.DoTracing = True
                DLLobj.ShowTracing = True
            else:
                DLLobj.DoTracing = False
                DLLobj.ShowTracing = False

            try:
                if (ret := DLLobj.SetGlossFile(parsesFile)) != SUCCESS:

                    errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).'), 2))
                    return errorList

            except Exception as e:

                errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}').format(e=e), 2))
                return errorList
            
            try:
                if (ret := DLLobj.Process()) != SUCCESS:

                    errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).'), 2))
                    return errorList
            
            except Exception as e:

                errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e}').format(e=e), 2))
                return errorList
        else:
            params = [FTPaths.HC_SYNTHESIZE, Utils.getInterfaceLangCode(), '-h', HCconfigPath, '-g', parsesFile, '-o', surfaceFormsFile]

            # We could add a Settings option to allow tracing
            # If we are to trace the HC synthesis, we need the -t -s parameters
            if trace:
                params.extend(['-t', '-s'])
                
            result = subprocess.run(params, capture_output=True, check=True)

            if result.returncode != 0:
                
                errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when running the HermitCrab Synthesize By Gloss tool.'), 2))
                errorList.append((result.stderr.decode(), 2))
                return errorList

    except subprocess.CalledProcessError as e:

        errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when running the HermitCrab Synthesize By Gloss tool.'), 2))
        errorList.append((e.stderr.decode(), 2))
        return errorList

    # Count the # of lexical units
    try:
        with open(parsesFile, encoding='utf-8') as f:

            lines = f.readlines()
            nonEmptyLines = [line for line in lines if line.strip()]
            LUsCount = len(nonEmptyLines)
    except:

        errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when trying to open the file: {parsesFile}').format(parsesFile=Utils.shortenPathForDisplay(parsesFile)), 2))
        return errorList
    
    errorList.append((_translate("DoHermitCrabSynthesis", 'Processing {LUsCount} unique lexical units.').format(LUsCount=LUsCount), 0))

    # Produce synthesis file
    errList = produceSynthesisFile(luInfoList, surfaceFormsFile, transferResultsFile, synFile)
    errorList.extend(errList)

    # check for fatal errors
    fatal, _ = Utils.checkForFatalError(errorList, report)
    
    if fatal:
        return errorList

    clean = ReadConfig.getConfigVal(configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, report)

    if not clean: 
        errorList.append((_translate("DoHermitCrabSynthesis", 'Configuration file problem with the value: {val}.').format(val=ReadConfig.CLEANUP_UNKNOWN_WORDS), 2))
        return errorList
    
    if clean[0].lower() == 'y':
        cleanUpText = True
    else:
        cleanUpText = False

    # If the caller wants to turn off cleaning up the text, set the boolean to False
    if overrideClean:
        cleanUpText = False

    fixUpText(synFile, cleanUpText)

    # Tell the user which file was created
    errorList.append((_translate("DoHermitCrabSynthesis", 'The synthesized target text is in the file: {file}.').format(file=Utils.shortenPathForDisplay(synFile)), 0))
    errorList.append((_translate("DoHermitCrabSynthesis", 'Synthesis complete.'), 0))
    
    return errorList

def doHermitCrab(DB, report, configMap=None):

    # Read the configuration file.
    if not configMap:

        # Read the configuration file.
        configMap = ReadConfig.readConfig(report)
        if not configMap:
            return None

    # Get config settings we need.
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    HCconfigPath = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_CONFIG_FILE, report)

    if not (HCconfigPath and targetSynthesis):
        return None

    # Extract the target lexicon. In One project mode extractHermitCrabConfig generates the config from a temporary copy of the
    # project (with the target writing system as the default vernacular WS), so the live project is never modified here.
    errorList = extractHermitCrabConfig(DB, configMap, HCconfigPath, report, useCacheIfAvailable=True)

    # check for fatal errors
    fatal, _ = Utils.checkForFatalError(errorList, report)
   
    if fatal:
        return None

    # Get HermitCrab file names
    parsesFile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_PARSES_FILE, report)
    masterFile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_MASTER_FILE, report)
    surfaceFormsFile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE, report)
    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)

    if not (parsesFile and surfaceFormsFile and surfaceFormsFile and transferResultsFile):

        errorList.append((_translate("DoHermitCrabSynthesis",
        '{master} or {parses} or {surface} or {transfer} not found in the configuration file.').format(
            master=ReadConfig.HERMIT_CRAB_MASTER_FILE,
            parses=ReadConfig.HERMIT_CRAB_PARSES_FILE,
            surface=ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE,
            transfer=ReadConfig.TRANSFER_RESULTS_FILE
        ), 2))
        return None

    # Synthesize the new target text
    errList = synthesizeWithHermitCrab(configMap, HCconfigPath, targetSynthesis, parsesFile, masterFile, surfaceFormsFile, transferResultsFile, report)
    errorList.extend(errList)
    
    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return None   
    
    return 1
    
def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return 
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    doHermitCrab(DB, report, configMap)



#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
