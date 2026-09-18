#
#   TextInRules.py
#
#   Ron Lockwood
#   SIL International
#   7/6/24
#
#   Version 3.17.1 - 8/28/26 - Ron Lockwood
#    Replaced the description at the top with a short code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
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
#   Version 3.14.2 - 8/13/25 - Ron Lockwood
#    Translate module name.
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
#   OVERVIEW (AI generated)
#
#   This module lets the user define and test the search and replace rules that fix up the text coming out of Paratext. A rule is a search string paired with a replacement string, optionally
#   treated as a regular expression. The rules are stored in the XML file named by the Text In Rules File setting, and ImportFromParatext is what actually applies them during an import.
#
#   This file is only the wrapper FlexTools sees. It reads the configuration file, logs the module start for analytics, and opens TextInOutUtils.TextInOutRulesWindow with textIn=True and the
#   Text In Rules File setting - the same window Text Out Rules uses, with the other setting. The rules format, the search and replace logic, the window itself and cluster project support all live
#   in Lib/TextInOutUtils.py, and the code description at the top of that file covers them.
#

from flextoolslib import * # type: ignore

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

import Mixpanel
import Utils
import ReadConfig
import TextInOutUtils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TextInRules'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'TextInOut', 'TextInOutUtils'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("TextInRules", "Text In Rules"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("TextInRules", 'Define and test a set of Paratext-import search and replace operations.') ,
        FTM_Help       : "",
        FTM_Description: _translate("TextInRules",
"""This module is used to define and test a set of search and replace operations to be used to fix up the text that comes out of 
Paratext. Regular expressions and Wildebeest normalization can be used if desired.""")}

#app.quit()
#del app

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
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

    # Show the window to get the options the user wants
    window = TextInOutUtils.TextInOutRulesWindow(DB, report, configMap, ReadConfig.TEXT_IN_RULES_FILE, textIn=True, winTitle=docs[FTM_Name])
    
    if window.retVal:
        window.show()
        app.exec()
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
