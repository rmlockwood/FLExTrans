#
#   StartTestbed
#
#   Ron Lockwood
#   SIL International
#   6/9/2018
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
#   Initialize the testbed log and create a source text from the testbed. The
#   source text can be fed into the normal FLExTrans process.
#

from SIL.LCModel import * # type: ignore
from flextoolslib import *                                                 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

from Testbed import *
import Mixpanel
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations(['StartTestbed'], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Testbed', 'TestbedValidator', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name: _translate("StartTestbed", "Start Testbed"),
        FTM_Version: "3.15",
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
        app = QApplication([])

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
            ).format(outFileVal=outFileVal)
        )
        return

    # Initialize a new test in the test log XML file
    resultsXMLObj = init_new_result(DB, report)
    if resultsXMLObj == None:
        return

    # Dump testbed source lexical units into the source_text.aper file
    count = resultsXMLObj.dump(f_out)
    f_out.close()

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



