#
#   EndTestbed
#
#   Ron Lockwood
#   SIL International
#   6/15/2018
#
#   Version 3.17.2 - 9/1/26 - Ron Lockwood
#    Added a code description block at the top with an overview, key features and code structure.
#
#   Version 3.17.1 - 8/31/26 - Ron Lockwood
#    Store on each test which transfer rules fired for which of its lexical units, read out of the Apertium transfer log, so the testbed log viewer can show them.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.4 - 8/21/26 - Ron Lockwood
#    Fixes #1502. Remove test rule numbers from the testbed results.
#
#   Version 3.16.3 - 7/8/26 - Ron Lockwood
#    Fixes #1392. Optionally apply the Text Out rules to the synthesis before extracting testbed results, controlled by the new ApplyTextOutRulesInTestbed setting.
#
#   Version 3.16.2 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16.1 - 6/9/26 - Laerke
#    Testbed improvements phase 1. Comment can now be added for a test.
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.1 - 8/13/25 - Ron Lockwood
#    Translate module name.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
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
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   earlier version history removed on 3/10/25
#
#   OVERVIEW (AI generated, then edited)
#
#   This module finishes a testbed run that Start Testbed began. Start Testbed dumped the testbed's tests into the analyzed text file, one test per line, and the rest of the FLExTrans chain then
#   transferred and synthesized them like it would any other text. This module reads that synthesized output back, one line per test in the same order the tests were dumped, and records what each
#   test actually produced next to what it was expected to produce. It also notes which transfer rules fired for which test, stamps the result with an end date-time and writes the testbed results
#   file, at which point the Testbed Log Viewer can show the run.
#
#   WHAT IT READS AND WRITES
#
#   The synthesis output file (Target Output Synthesis File setting) is read whole into memory rather than being handed straight to the extraction, because it may first need the Text Out (Fix Up
#   Synthesis Text) rules run over it. Those are the rules Insert Target Text and Export to Paratext apply to the final output, so running them here too means the testbed compares against the same
#   text the user would actually see. That is optional and controlled by the Apply Text Out Rules In Testbed setting, since a user may well prefer to test the raw synthesis.
#
#   Extraction walks the topmost result in the testbed results file - the one Start Testbed created and left with an empty end date-time - and reads one line of synthesized text for each test that
#   result holds, trimming off the dummy EOL lexical unit and normalizing to decomposed unicode before storing the line as that test's actual result. Nothing is written back unless at least one
#   result came out of that.
#
#   WHICH RULES FIRED FOR WHICH TEST
#
#   recordAppliedRules() is what lets the log viewer show, underneath a test, the transfer rules that fired for it. The raw material is apertium_log.txt in the Build folder, where the makefile sends
#   apertium-transfer's trace. That trace lists the rules in the order they fired along with the lexical units each one saw, but it can't tell us which test a rule application belongs to: the "line"
#   number it reports is a line of the rules file, not a line of the text being translated.
#
#   So the log and the tests are walked forward together. Transfer works through the tests in the order they were dumped, so the log and the test list only ever move forward, and each rule
#   application can be placed by its first lexical unit: find the first test, from the one we are on onward, that still has that lexical unit ahead of where the previous rule left off. The window of
#   lexical units the log prints has to be trimmed first, because apertium reads one word past a match to find out that the match is over and prints that word along with the matched ones - the
#   rule's own pattern length, read out of the copy of the rules file that was compiled for this run, says how many words the rule really took. Comparisons are forgiving about unicode composition
#   and case, since a word carries whatever capitalization it had in the text it came from. When the log runs past the end of the tests, whatever is left in it belongs to some other run of the
#   Apertium tools and is dropped.
#
#   Each test then gets the list of (rule number, rule comment, lexical units) that was collected for it, or an empty list if no rule fired for it - which also clears out anything an earlier
#   extraction of this same result left behind. The rule is named by number and comment together because the number on its own would go stale as soon as a rule is added to or removed from the file.
#
#   CODE STRUCTURE
#
#   Top to bottom the file goes: the docs dictionary FlexTools displays, the three small helpers the rule matching needs (getTestLexicalUnits, normalizeForCompare and findLexicalUnit),
#   recordAppliedRules(), MainFunction(), and the FlexToolsModule declaration at the very bottom that FlexTools looks for. MainFunction() reads the settings, reads and optionally rule-adjusts the
#   synthesis text, extracts the results, records the applied rules, ends the result and writes the file. The log parsing itself (parseAppliedRulesLog), the rules file reading (getTransferRuleInfo)
#   and all of the testbed XML classes live in Lib/Testbed.py.
#

import io
import os
import re
import unicodedata

from SIL.LCModel import * # type: ignore
from flextoolslib import * # type: ignore

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from Testbed import *
import Mixpanel
import ReadConfig
import TextInOutUtils
import TextOutRules
import Utils
import FTPaths

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'EndTestbed'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Testbed', 'TestbedValidator', 'Mixpanel', 'TextInOutUtils']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("EndTestbed", "End Testbed"),
        FTM_Version    : "3.17.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("EndTestbed", "Conclude a testbed log result."),
        FTM_Help       : "",
        FTM_Description: _translate("EndTestbed",  
"""Conclude a testbed log result.""")}

#app.quit()
#del app

# The source lexical units of one test, as plain Apertium strings without the ^ and $ around them, in the order the transfer rules saw them. The dummy EOL lexical unit that the testbed dump adds
# to the end of every test line is one of the units the rules saw, so it belongs on the end of the list too.
def getTestLexicalUnits(testObj):

    luList = re.findall(r'\^(.*?)\$', testObj.getApertiumString())
    luList.append(EOL_LEXICAL_UNIT)

    return luList

# Lexical units from the log and from the testbed XML both come from the same dump, but compare them forgivingly all the same: same Unicode composition and same case, since a word carries whatever
# capitalization it had in the text it came from.
def normalizeForCompare(luStr):

    return unicodedata.normalize('NFD', luStr).lower()

# Where luToFind sits in luList at or after startAt, or -1 if it isn't there.
def findLexicalUnit(luList, luToFind, startAt):

    try:
        return luList.index(luToFind, startAt)

    except ValueError:
        return -1

# Work out which transfer rules fired for which test and store that on each test of the run that just finished, so the testbed log viewer can show, underneath a test, the lexical units a rule
# matched and which rule it was. The Apertium transfer log lists the rules in the order they fired along with the lexical units each one saw, but it can't tell us which test a rule application
# belongs to: the "line" number it reports is a line of the rules file, which FLExTrans writes all on one line. So we walk the log and the tests forward together, placing each rule application by
# its first lexical unit - transfer works through the tests in the order they were dumped, so the log and the test list only ever move forward.
def recordAppliedRules(resultsXMLObj):

    logEntries = parseAppliedRulesLog(os.path.join(FTPaths.BUILD_DIR, APERTIUM_LOG_FILE))
    resultObjList = resultsXMLObj.getTestbedResultXMLObjectList()

    if not logEntries or not resultObjList:
        return

    # Take the rule information from the copy of the rules file that was compiled for this run, so the numbers in the log, the comments stored alongside them and the pattern lengths used to trim
    # the windows below all come from one and the same file.
    ruleInfo = getTransferRuleInfo(os.path.join(FTPaths.BUILD_DIR, Utils.STRIPPED_RULES))

    # The tests of the run that just finished - results are kept newest first - in the order they were dumped into the source file, which is the order transfer ran through them.
    testList = []

    for testbedXMLObj in resultObjList[0].getFLExTransTestbedXMLObjectList():

        testList.extend(testbedXMLObj.getTestXMLObjectList())

    testLUlists = [[normalizeForCompare(lu) for lu in getTestLexicalUnits(testObj)] for testObj in testList]

    appliedRulesByTest = {}
    testIndex = 0
    luIndex = 0

    for ruleNum, luList in logEntries:

        ruleComment, patternLength = ruleInfo.get(ruleNum, ('', 0))

        # Keep only the words the rule actually took. Apertium reads one word past a match to find out that the match is over and prints that word along with the matched ones, but the rule did
        # nothing to it - it is usually the first word of the next rule's match - so showing it to the user would misrepresent what the rule did. The rule's own pattern says how many words it
        # takes, and the rule consumes exactly those, which also tells us where the next rule can start looking.
        if patternLength:

            luList = luList[:patternLength]
            wordsTaken = len(luList)

        # With no rules file to consult there is no telling the matched words from the one that ended the match, so keep the window whole and leave its last word where the next rule can still find it.
        else:
            wordsTaken = max(1, len(luList) - 1)

        firstLU = normalizeForCompare(luList[0])
        luPosition = -1

        # Find the test this rule application belongs to: the first test, from the one we are on onward, that still has this lexical unit ahead of where the previous rule left off.
        while testIndex < len(testLUlists):

            luPosition = findLexicalUnit(testLUlists[testIndex], firstLU, luIndex)

            if luPosition >= 0:
                break

            testIndex += 1
            luIndex = 0

        # We have run off the end of the tests, so whatever is left in the log belongs to some other run of the Apertium tools than the one that produced these results.
        if luPosition < 0:
            break

        appliedRulesByTest.setdefault(testIndex, []).append((ruleNum, ruleComment, luList))

        # Step over the words this rule took, so the next rule is looked for after them.
        luIndex = luPosition + wordsTaken

    # Store what was found on each test. A test no rule fired for gets an empty list, which also clears out anything an earlier extraction of this same result left behind.
    for testNum, testObj in enumerate(testList):

        testObj.setAppliedRules(appliedRulesByTest.get(testNum, []))

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + ['EndTestbed'], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the synthesis file name
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not outFileVal:
        return
    
    # Read the whole synthesis file into memory. We read it up front (rather than passing the file object straight to extractResults) so we can optionally
    # run the Text Out rules over it first. Those rules are what Insert Target Text and Export to Paratext apply to the final output.
    try:
        with open(outFileVal, encoding='utf-8') as f_out:
            synFileContents = f_out.read()

    except IOError:
        report.Error(_translate("EndTestbed", "There is a problem with the Synthesis Output File path: {outFileVal}. Please check the configuration file setting.").format(outFileVal=Utils.shortenPathForDisplay(outFileVal)))
        return

    # Optionally apply the Text Out (Fix Up Synthesis Text) rules so the testbed compares against the same text the user would see in their final output.
    applyTextOut = ReadConfig.getConfigVal(configMap, ReadConfig.APPLY_TEXT_OUT_RULES_IN_TESTBED, report, giveError=False)

    if applyTextOut == 'y':

        synFileContents = TextInOutUtils.applyTextOutRulesFromConfig(synFileContents, configMap, report, TextOutRules.docs[FTM_Name])

        # A fatal error while applying the rules returns None; bail out rather than extracting from bad data.
        if synFileContents is None:
            return

    # Create an object for the testbed results file and get the associated
    # XML object
    resultsFileObj = FlexTransTestbedResultsFile(report)
    resultsXMLObj = resultsFileObj.getResultsXMLObj()

    # Extract the results from the (possibly rule-adjusted) synthesis text. extractResults reads line by line, so wrap the string in a StringIO.
    count = resultsXMLObj.extractResults(io.StringIO(synFileContents))
    
    # If we were successful write the end date-time and save the file
    if count > 0:

        # Note on each test which transfer rules fired for which of its words, so the testbed log viewer can show them under the test.
        recordAppliedRules(resultsXMLObj)

        resultsXMLObj.endTest()
        resultsFileObj.write()
    
    # Let the user know how many valid/invalid test were dumped
    report.Info(_translate("EndTestbed", "{count} results extracted.").format(count=count))



#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()

