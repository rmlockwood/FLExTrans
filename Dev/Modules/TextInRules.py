#
#   TextInRules.py
#
#   Ron Lockwood
#   SIL International
#   7/6/24
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

import os
import shutil
import sys
import xml.etree.ElementTree as ET

from flextoolslib import *                                          

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator

from FTPaths import TRANSL_DIR
import ReadConfig
import TextInOutUtils

app = QApplication(sys.argv)

# Load translations
translator = QTranslator()
langCode = 'es'
if translator.load(TRANSL_DIR+f"/TextInOut_{langCode}.qm"):
    QCoreApplication.installTranslator(translator)

# Define _translate for convenience
_translate = QCoreApplication.translate

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Text In Rules",
        FTM_Version    : "3.13",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("TextInOut", 'Define and test a set of Paratext-import search and replace operations.') ,
        FTM_Help   : "",
        FTM_Description: _translate("TextInOut",
"""This module is used to define and test a set of search and replace operations to be used to fix up the text that comes out of 
Paratext. Regular expressions and Wildebeest normalization can be used if desired.""")}

app.quit()
del app

DEFAULT_PATH_TEXT_IN = 'Output\\fixup_paratext_rules.xml'

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the search-replace rules file
    textInRulesFile = TextInOutUtils.getPath(report, configMap, ReadConfig.TEXT_IN_RULES_FILE, DEFAULT_PATH_TEXT_IN)

    app = QApplication(sys.argv)

    # Load translations
    langCode = 'es'
    translator = QTranslator()

    if translator.load(TRANSL_DIR+f"/TextInOut_{langCode}.qm"):

        QCoreApplication.installTranslator(translator)
    try:
        # Check if the file exists, if not, create it.
        if os.path.exists(textInRulesFile) == False:

            # Set a string for an empty rules list
            xmlString = f"<?xml version='1.0' encoding='utf-8'?><{TextInOutUtils.FT_SEARCH_REPLACE_ELEM}><{TextInOutUtils.SEARCH_REPLACE_RULES_ELEM}/></{TextInOutUtils.FT_SEARCH_REPLACE_ELEM}>"

            fOut = open(textInRulesFile, 'w', encoding='utf-8')
            fOut.write(xmlString)
            fOut.close()
        else:
            # Make a backup copy of the search-replace rule file
            shutil.copy2(textInRulesFile, textInRulesFile+'.bak')
    except:
        report.Error(QCoreApplication.translate('TextInOut', 'There was a problem creating or backing up the rules file. Check your configuration.'))
        return

    # Show the window to get the options the user wants
    window = TextInOutUtils.TextInOutRulesWindow(textInRulesFile, textIn=True, winTitle=docs[FTM_Name])
    window.show()
    app.exec_()
    
#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
