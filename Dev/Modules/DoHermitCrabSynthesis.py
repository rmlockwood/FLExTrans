#
#   DoHermitCrabSynthesis.py
#
#   Ron Lockwood
#   SIL International
#   3/8/23
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
#   Version 3.9.3 - 7/26/23 - Ron Lockwood
#    Give warnings from GenerateHCConfig. 
#
#   Version 3.9.2 - 7/19/23 - Ron Lockwood
#    Fixes #464. Support a new module that does either kind of synthesis by calling 
#    the appropriate module. 
#
#   Version 3.9.1 - 6/26/23 - Ron Lockwood
#    Updated module description. Also output the name of the created synthesis file.
#
#   Version 3.9 - 6/2/23 - Ron Lockwood
#    Support tracing of HermitCrab synthesis
#
#   Version 3.8.4 - 5/3/23 - Ron Lockwood
#    Better error handling.
#
#   Version 3.8.3 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8.2 - 4/18/23 - Ron Lockwood
#    Fixes #117. Common function to handle collected errors.
#
#   Version 3.8.1 - 4/8/23 - Ron Lockwood
#    Handle synthesis errors in multi-word results.
#
#   Version 3.8 - 3/8/23 - Ron Lockwood
#    Initial version.
#
#   Synthesize using Hermit Crab.
#
# Basic Design:
#
# Create HermitCrabMaster.txt file - this file holds each word parse on a line the parse is in a couple different formats in the form X,Y. 
#  This file is created in the Convert Text to Synthesizer Format module. It is a file that contains only unique parses. 
#  X is the Apertium representation of the parse ^...$
#  Y holds one or more parses in the form the HC needs. Y is in the form A|B...|C
#  A is in the form Q;N where Q is the parse and N is the capitalization code N can be null
#  Q is in the form <pfx1>...<pfxN>root<cat><sfx1>...<sfxN> the code goes from X form to Q form by consulting the affix list file
#
# The rest happens in the Do HermitCrab Synthesis module
# Extract the HermitCrab config file - this config file is actually a full target lexicon in an XML format along with all rules and settings needed for HC. This takes a bit of time.
# Create an internal map of the lowercase version of all lemmas in the HC config file to the original cased version.
# Create the HC parses file - this is the file that we will send to HC for synthesizing.
#  The parses are in HC order, like Q above.
#  The file is created by iterating through the Master file. Lemmas are restored to their
#   cased forms as in the HC config file using the internal map from above.
#  Phrases of the form A|B in the master file come out as consecutive LUs, e.g. ^...$^...$
#  The list of LUs gets saved for use below.
# Now HC is called to convert the parses file into a surface forms file (using the HC config file info)
#  In this surface forms file, multiple words are separated by commas (R,T)
# Next we produce the synthesized text using the previous generated Apertium results file
#  (which is the output from apply Apertium rules to the source file) and the surface forms and the saved LU list.
#  The code iterates through the surface forms and using the original LU, substitutes every #   every LU in the Apertium results file with the matched surface form. 
#   In the loop, the code applies the need capitalization for the word before substitution.

import os
import re 
import subprocess
from datetime import datetime

from SIL.LCModel import *                                                    # type: ignore

from flextoolslib import *                                                 
from flexlibs import FLExProject, FWProjectsDir

from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtWidgets import QApplication

import Mixpanel
import ReadConfig
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'DoHermitCrabSynthesis'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Synthesize Text with HermitCrab",
        FTM_Version    : "3.14",
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
NOTE: Messages will say the SOURCE database
is being used. Actually the target database is being used.
Advanced Information: This module runs HermitCrab against a list of target parses ('target_words-parses.txt') to
produce surface forms ('target_words-surface.txt'). 
These forms are then used to create the target text.""")}

description = docs[FTM_Description]

app.quit()
del app

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

def extractHermitCrabConfig(DB, configMap, HCconfigPath, report=None, useCacheIfAvailable=False, DLLobj=None):

    errorList = []

    # Get the target project name
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report)

    if not targetProj:
        errorList.append((_translate("DoHermitCrabSynthesis", "Configuration file problem with TargetProject."), 2))
        return errorList
    
    TargetDB = FLExProject()

    try:
        # Open the target database
        TargetDB.OpenProject(targetProj, True)

    except: #FDA_DatabaseError, e:

        errorList.append((_translate("DoHermitCrabSynthesis", "Failed to open the target database: {targetProj}.").format(targetProj=targetProj), 2))
        return errorList

    # Get fwdata file path
    fwdataPath = os.path.join(FWProjectsDir, TargetDB.ProjectName(), TargetDB.ProjectName() + '.fwdata')
        
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

                errorList.append((f'An exception happened when trying to get the HermitCrab XML file from the DLL object: {e}', 2))
                return errorList
            
            if xmlFile == '':

                try:
                    if (ret := DLLobj.SetHcXmlFile(HCconfigPath)) != SUCCESS:

                        errorList.append(('An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL)', 2))
                        return errorList
                
                except Exception as e:

                    errorList.append(('An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}'.format(e=e), 2))
                    return errorList

        errorList.append((_translate("DoHermitCrabSynthesis", "The HermitCrab configuration file is up to date."), 0))
        return errorList
    else:
        # Run the HermitCrab config generator
        try:
            result = subprocess.run([FTPaths.GENERATE_HC_CONFIG, fwdataPath, HCconfigPath], capture_output=True)

            if result.returncode == 0:

                gatherWarnings(result, errorList)
                errorList.append((_translate("DoHermitCrabSynthesis", "Generated the HermitCrab config. file: {filePath}.").format(filePath=Utils.getPathRelativeToWorkProjectsDir(HCconfigPath)), 0))
            else:
                errorList.append((_translate("DoHermitCrabSynthesis", "An error happened when running the Generate HermitCrab Configuration tool."), 2))
                
                # Check for KeyNotFoundException from FLEx
                if re.search('KeyNotFoundException', result.stderr.decode()):

                    errorList.append((_translate("DoHermitCrabSynthesis", "The error contains a 'KeyNotFoundException' and this often indicates that the FLEx Find and Fix utility should be run on the {projectName} database.").format(projectName=TargetDB.ProjectName()), 2))
                    errorList.append((_translate("DoHermitCrabSynthesis", "The full error message is:"), 2))

                errorList.append((result.stderr.decode(), 2))
                return errorList

            # Reload the config file into the dll object.
            if DLLobj:

                try:
                    if (ret := DLLobj.SetHcXmlFile(HCconfigPath)) != SUCCESS:

                        errorList.append((_translate("DoHermitCrabSynthesis", 'An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. This happened after the config file was generated. (DLL)'), 2))
                        return errorList
                
                except Exception as e:

                    errorList.append((_translate("DoHermitCrabSynthesis", 'An exception happened when trying to set the HermitCrab XML file in the DLL object. Error: {e}').format(e=e), 2))
                    return errorList

        except subprocess.CalledProcessError as e:

            errorList.append((_translate("DoHermitCrabSynthesis", "An error happened when running the Generate HermitCrab Configuration tool."), 2))
            errorList.append((e.stderr.decode(), 2))

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

        errorList.append((f'There was an error opening the HermitCrab surface forms file.', 2))
        return errorList
    
   # Open the transfer results file
    try:
        fResults = open(transferResultsFile, encoding='utf-8')

    except:

        errorList.append((f'The file: {transferResultsFile} was not found. Did you run the Run Apertium module?', 2))
        return errorList
    
    # Read the results file into a string
    resultsFileStr = fResults.read()

    # Read in the surface forms
    surfaceFormsList = fSurfaceForms.readlines()

    # Remove blank lines
    surfaceFormsList = [line for line in surfaceFormsList if line.strip()]

    # Do a sanity check to see if the number of surface forms matches the number of Lexical unit strings
    if len(surfaceFormsList) != len(luInfoList):

        errorList.append((f'The number of surface forms does not match the number of Lexical Units.', 2))
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

                    errStr = f'Synthesis failed. ({saveStr})'

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

        errorList.append((f'Error writing the file: {synFile}.', 2))

    fSyn.close()
    fSurfaceForms.close()
    fResults.close()
    return errorList

def createdHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap):

    errorList = []

    # Open master file
    try:
        fMaster = open(masterFile, encoding='utf-8')

    except:

        errorList.append((f'There was an error opening the HermitCrab master file. Do you have the setting "Use HermitCrab Synthesis" turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}', 2))
        return errorList

    # Open parses file
    try:
        fParses = open(parsesFile, 'w', encoding='utf-8')

    except:

        errorList.append((f'There was an error opening the HermitCrab parses file.', 2))
        return errorList

    # Parse each line - format: LU,HCparse1;capitalizationCode|HCparse2;capitalizationCode|...
    for line in fMaster:

        line = line.rstrip()

        if len(line) == 0:
            continue

        # Get the lexical unit
        luStr, HCparseStr = re.split(',', line)

        # skip @ words. They have the form: ^@...
        if HCparseStr[1] == '@':

            fParses.write('\n')
            continue

        # Get the parses
        HCparsesList = re.split('\|', HCparseStr)
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

    # Get the root - non > characters before a <
    match = re.search(r'(.*?)([^>]+?)(<.*)', hcParse)
    before = match.group(1)
    root   = match.group(2)
    after  = match.group(3)

    # Get the capitalized form if the lemma is capitalized in the target lexicon (it's in the capitalized lemmas map)
    # This is a map of lowercase forms to the original capitalized form.
    # The root could be a phrase with multiple words capitalized such as 'Arangga Nanuno'
    root = HCcapitalLemmasMap.get(root, root)

    return before+root+after

# Remove @ signs at the beginning of words and N.N at the end of words if so desired in the settings.
# Also symbols and ^%0%...%$
def fix_up_text(synFile, cleanUpText):
    
    # Read the contents
    f_s = open(synFile, encoding="utf-8")
    synFileContents = f_s.read()
    f_s.close()

    # Make replacements
    f_s = open(synFile, 'w', encoding="utf-8")

    if cleanUpText:

        # Remove n.n on lemmas
        synFileContents = re.sub('\d+\.\d+', '', synFileContents, flags=re.RegexFlag.A) # re.A=ASCII-only match
        
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
        with open(HCconfigPath, 'r', encoding='utf-8') as file:

            contents = file.read()
    except:
        return None

    # Use regex to find all strings between <Gloss> tags
    lemmas = re.findall(r'<Gloss>(.*?)</Gloss>', contents)

    # Iterate through the extracted lemmas
    for lemStr in lemmas:

        # Check any letter is capitalized
        if any(char.isupper() for char in lemStr):

            HCcapitalLemmasMap[lemStr.lower()] = lemStr

    return HCcapitalLemmasMap

def synthesizeWithHermitCrab(configMap, HCconfigPath, synFile, parsesFile, masterFile, surfaceFormsFile, transferResultsFile, report=None, trace=False, DLLobj=None, overrideClean=False):
    
    errorList = []
    luInfoList = []

    HCcapitalLemmasMap = getCapitalLemmas(HCconfigPath)

    if HCcapitalLemmasMap is None:

        errorList.append(('Unable to open the HC master file.', 2))
        return errorList

    errorList = createdHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap)

    for triplet in errorList:

        if triplet[1] == 2: # error

            return errorList

    # Call HCSynthesis to produce surface forms. 
    try:
        # Do the operation with a dll differently than with the normal exe.
        if DLLobj:

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
            params = [FTPaths.HC_SYNTHESIZE, '-h', HCconfigPath, '-g', parsesFile, '-o', surfaceFormsFile]

            # We could add a Settings option to allow tracing
            # If we are to trace the HC synthesis, we need the -t -s parameters
            if trace:
                params.extend(['-t', '-s'])
                
            result = subprocess.run(params, capture_output=True, check=True)

            if result.returncode != 0:
                
                errorList.append((f'An error happened when running the HermitCrab Synthesize By Gloss tool.', 2))
                errorList.append((result.stderr.decode(), 2))
                return errorList

    except subprocess.CalledProcessError as e:

        errorList.append((f'An error happened when running the HermitCrab Synthesize By Gloss tool.', 2))
        errorList.append((e.stderr.decode(), 2))
        return errorList

    # Count the # of lexical units
    try:
        with open(parsesFile, encoding='utf-8') as f:

            lines = f.readlines()
            nonEmptyLines = [line for line in lines if line.strip()]
            LUsCount = len(nonEmptyLines)
    except:
        errorList.append((f'An error happened when trying to open the file: {parsesFile}', 2))
        return errorList
    
    errorList.append((f'Processing {LUsCount} unique lexical units.', 0))

    # Produce synthesis file
    errList = produceSynthesisFile(luInfoList, surfaceFormsFile, transferResultsFile, synFile)
    errorList.extend(errList)

    # check for fatal errors
    fatal, _ = Utils.checkForFatalError(errorList, report)
    
    if fatal:
        return errorList

    clean = ReadConfig.getConfigVal(configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, report)

    if not clean: 
        errorList.append((f'Configuration file problem with the value: {ReadConfig.CLEANUP_UNKNOWN_WORDS}.', 2))
        return errorList
    
    if clean[0].lower() == 'y':
        cleanUpText = True
    else:
        cleanUpText = False

    # If the caller wants to turn off cleaning up the text, set the boolean to False
    if overrideClean:
        cleanUpText = False

    fix_up_text(synFile, cleanUpText)

    # Tell the user which file was created
    errorList.append((f'The synthesized target text is in the file: {Utils.getPathRelativeToWorkProjectsDir(synFile)}.', 0))
    errorList.append(('Synthesis complete.', 0))
    
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

    # Extract the target lexicon
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

        errorList.append((f'{ReadConfig.HERMIT_CRAB_MASTER_FILE} or {ReadConfig.HERMIT_CRAB_PARSES_FILE} \
                         or {ReadConfig.HERMIT_CRAB_SURFACE_FORMS_FILE} or {ReadConfig.TRANSFER_RESULTS_FILE} not found in the configuration file.', 2))
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
    app = QApplication([])
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
