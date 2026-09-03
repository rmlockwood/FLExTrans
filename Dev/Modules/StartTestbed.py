#
#   StartTestbed
#
#   Ron Lockwood
#   SIL International
#   6/9/2018
#
#   Version 3.17.2 - 9/2/26 - Ron Lockwood
#    Save a copy of every phase's transfer rules in Output\rule-file-history through RuleFileHistory, and convert a leftover rule-history folder from an earlier version.
#
#   Version 3.17.1 - 9/1/26 - Ron Lockwood
#    Added a code description block at the top with an overview, key features and code structure.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.1 - 6/30/26 - Ron Lockwood
#    Fixes #1397. Shortened file paths shown in user messages with Utils.shortenPathForDisplay().
#
#   Version 3.16 - 6/9/26 - Laerke
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
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
#
#   2023 version history removed on 2/6/26
#
#   OVERVIEW (AI generated, then edited)
#
#   This module begins a testbed run. The testbed is an XML file of tests - each one a handful of source lexical units paired with the target text they are expected to produce - built up over time
#   with the Add to Testbed button in the Live Rule Tester or possibly manual edits to the testbed file. Running the testbed means feeding those tests through the normal FLExTrans machinery instead 
#   of feeding a real source text through it, so this module takes the place of Extract Source Text: it writes the tests out as the analyzed text file and starts a new result in the testbed log. 
#   The user then runs the rest of the chain (Run Apertium ... Synthesis) as usual and finishes with End Testbed, which reads the synthesized output back and records what each test actually produced.
#
#   WHAT IT WRITES
#
#   Two files get written, both named by settings:
#    - The testbed results file (Testbed Results File setting) gets a new testbedResult element holding a copy of the testbed as it stands right now, stamped with a start date-time and an empty end
#      date-time. Results are kept newest first, so the new one goes on the top. The empty end date-time is what marks the run as still in progress: End Testbed looks for it to know which result to
#      fill in, and the log viewer skips a result that still has it.
#    - The analyzed text file (Analyzed Text Output File setting, typically source_text.aper in the Build folder) gets the source lexical units of every test, one test per line. A dummy EOL lexical
#      unit goes on the end of each line so that a transfer rule matching at the end of one test can't run on into the next test.
#
#   Along the way a copy of every transfer rules file this project has is saved in Output\rule-file-history, each named after the rules file with the date, the time and the tag testbed_run added on.
#   That leaves a record of exactly which rules produced a given run's results, since the rules file itself will have moved on by the time the user looks back at the log. An advanced project's
#   interchunk and postchunk files are saved too, because the testbed text goes through all of those phases. Every other part of FLExTrans that changes or records the rules - the Live Rule Tester,
#   the Rule Assistant, AI Rule Studio and Set Up Transfer Rule Categories - saves into that same folder with a tag of its own, so the whole history of a project's rules is one sorted listing.
#
#   TEMPORARY (old rule history conversion) - this paragraph and the one call to OldRuleHistoryConversion.convert() in MainFunction go together, and both come out when that module does.
#   This module is one of the two places where a project last used with version 3.17 or earlier gets brought forward; the Live Rule Tester is the other. See Lib/OldRuleHistoryConversion.py.
#
#   VALIDATION
#
#   Before anything is dumped, every test in the testbed is validated against the source FLEx project by TestbedValidator: each lexical unit's headword and sense number, its grammatical category and
#   its other tags all have to still exist there. A test with even one bad lexical unit is marked invalid in the testbed file along with the reason why, and the testbed file is rewritten if any of
#   those marks changed. Invalid tests still get dumped, but the log viewer shows them with a yellow triangle and no actual result rather than as a pass or a fail. This matters because the source
#   project changes underneath the testbed - a sense gets renumbered, a category renamed - and without the check those tests would simply look like failures.
#
#   CODE STRUCTURE
#
#   init_new_result() does the testbed side: it opens the testbed file, validates it, and initializes the new result in the results file, returning the results XML object or None if there is no
#   testbed to run. MainFunction() does the rest - reads the settings, opens the analyzed text file, calls init_new_result(), dumps the tests into that file, saves a rule file history copy of each
#   phase's rules, and reports how many tests were prepared. The XML classes it works through (FlexTransTestbedFile, FlexTransTestbedResultsFile and the XML objects under them) live in
#   Lib/Testbed.py.
#

from SIL.LCModel import * # type: ignore
from flextoolslib import * # type: ignore

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from Testbed import *
import Mixpanel
import ReadConfig
import Utils
import RuleFileHistory
import OldRuleHistoryConversion  # TEMPORARY (old rule history conversion)

# Define _translate for convenience
_translate = QCoreApplication.translate

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['StartTestbed'], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Testbed', 'TestbedValidator', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name: _translate("StartTestbed", "Start Testbed"),
        FTM_Version: "3.17.2",
        FTM_ModifiesDB: False,
        FTM_Synopsis: _translate("StartTestbed", "Initialize the testbed log and create source text from the testbed."),
        FTM_Help: "",
        FTM_Description: _translate(
        "StartTestbed",
        """
        Initialize the testbed log and create source text from the testbed.
        """
    ),
}

#app.quit()
#del app

def init_new_result(DB, report):
    # should this clean up result nodes that have no data?

    # Create an object for the testbed file
    testbedFileObj = FlexTransTestbedFile(None, report)

    # We can't do anything if there is no testbed
    if testbedFileObj.exists() == False:
        report.Error(_translate("StartTestbed", "Testbed does not exist. Please add tests to the testbed."))
        return None

    # Validate the source lexical units in the testbed XML file and write the changes if needed
    testbedFileObj.validate(DB, report)

    # Get the testbed XML object
    testbedXMLObj = testbedFileObj.getFLExTransTestbedXMLObject()

    # Create an object for the testbed results file
    resultsFileObj = FlexTransTestbedResultsFile(report)

    # Initialize the testbed run
    resultsXMLObj = resultsFileObj.getResultsXMLObj()
    resultsXMLObj.initTestResult(testbedXMLObj)

    resultsFileObj.write()

    return resultsXMLObj

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modifyAllowed):
    
    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + ['StartTestbed'], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Get the output file name
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)
    if not outFileVal:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Open the output file
    try:
        f_out = open(outFileVal, 'w', encoding="utf-8")
    except IOError:
        report.Error(
            _translate(
                "StartTestbed",
                "There is a problem with the Analyzed Text Output File path: {outFileVal}. Please check the configuration file setting."
            ).format(outFileVal=Utils.shortenPathForDisplay(outFileVal))
        )
        return

    # Initialize a new test in the test log XML file
    resultsXMLObj = init_new_result(DB, report)
    if resultsXMLObj == None:
        return

    # Dump testbed source lexical units into the source_text.aper file
    count = resultsXMLObj.dump(f_out)
    f_out.close()

    OldRuleHistoryConversion.convert(report)  # TEMPORARY (old rule history conversion) - delete this line, the import, and the marked paragraph above when Lib/OldRuleHistoryConversion.py goes.

    # Save a copy of every transfer rules file this project has, so there is a record of exactly which rules produced this run's results - the rules file itself will have moved on by the time the
    # user looks back at the log. An advanced project's interchunk and postchunk files are saved too, since the testbed text goes through all of those phases and not just the first one.
    _, errorMsg = RuleFileHistory.saveHistoryCopies(ReadConfig.getTransferRuleFiles(configMap, report), RuleFileHistory.TAG_TESTBED_RUN)

    if errorMsg:

        report.Warning(_translate("StartTestbed", "The rule file history folder could not be updated. The error was: {errorText}").format(errorText=errorMsg))

    # Let the user know how many valid/invalid tests were dumped
    report.Info(
        _translate("StartTestbed", "{count} tests prepared for testing.").format(count=count)
    )



#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction=MainFunction, docs=docs)

#---------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()



