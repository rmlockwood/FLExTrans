#
#   TextInRules.py
#
#   Ron Lockwood
#   SIL International
#   7/6/24
#
#   Version 3.14.1 - 8/8/25 - Ron Lockwood
#   Fixes #1017. Support cluster projects.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 11/12/24 - Ron Lockwood
#    Use default path if settings has no path to the xml file.
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
#   Version 3.10.5 - 7/6/24 - Ron Lockwood
#    Initial version.
#
#   Define and test a set of search and replace operations to be used to fix up the text that comes out of 
#   Paratext. Regular expression can be used if desired.
#

from flextoolslib import *                                          

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

import Mixpanel
import Utils
import ReadConfig
import TextInOutUtils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TextInRules'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'TextInOut', 'TextInOutUtils'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Text In Rules",
        FTM_Version    : "3.14.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("TextInRules", 'Define and test a set of Paratext-import search and replace operations.') ,
        FTM_Help   : "",
        FTM_Description: _translate("TextInRules",
"""This module is used to define and test a set of search and replace operations to be used to fix up the text that comes out of 
Paratext. Regular expressions and Wildebeest normalization can be used if desired.""")}

app.quit()
del app

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
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

    # Show the window to get the options the user wants
    window = TextInOutUtils.TextInOutRulesWindow(DB, report, configMap, ReadConfig.TEXT_IN_RULES_FILE, textIn=True, winTitle=docs[FTM_Name])
    
    if window.retVal:
        window.show()
        app.exec_()
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
