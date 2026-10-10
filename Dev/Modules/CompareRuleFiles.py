#
#   CompareRuleFiles
#
#   Ron Lockwood
#   SIL International
#   10/10/26
#
#   Version 3.17 - 10/10/26 - Ron Lockwood
#    Initial version. Shows two versions of the transfer rules file side by side - by default the current file and its newest saved copy - with the differences highlighted.
#
#   OVERVIEW (AI generated, then edited)
#
#   A Tools-collection module that helps the user see what has changed between versions of their transfer rules. FLExTrans saves a copy of the rules file in Output\rule-file-history whenever
#   something is about to change it or wants a record of it (the Live Rule Tester, Start Testbed, the Rule Assistant, AI Rule Studio, Set Up Transfer Rule Categories). This module opens a window
#   that compares any two of those versions, or the current file against any rules file the user browses to, side by side with removed, added and changed parts coloured.
#
#   All of the work is in Lib/CompareRuleFilesDlg.py; this file only reads the transfer rules file setting, checks the file is there, and shows the window. Other modules that want the same window
#   (the Testbed Log Viewer, for one) call CompareRuleFilesDlg.showRuleFileComparison directly rather than going through this module.
#
#   CODE STRUCTURE
#
#   MainFunction reads the settings, logs the start, and shows CompareRuleFilesDlg under the Qt application loop - FlexTools has no loop running, so a bare exec() would return at once (the same
#   pattern as AI Rule Studio and the Live Rule Tester).
#

import os

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from flextoolslib import FlexToolsModuleClass, FTM_Name, FTM_Version, FTM_ModifiesDB, FTM_Synopsis, FTM_Help, FTM_Description  # type: ignore

import Mixpanel
import Utils
import ReadConfig

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'CompareRuleFiles'

translators = []
app = QApplication.instance()

if app is None:

    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# Libraries whose strings we load when the module runs. The window logic and its pyuic-generated window file each have their own .ts/.qm, and TransferPreview draws the comparison.
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'CompareRuleFilesDlg', 'CompareRuleFilesWindow', 'TransferPreview']

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("CompareRuleFiles", """This module shows two versions of your transfer rules side by side, with what was removed, added, or changed highlighted, so you can see what has changed between them. FLExTrans saves a copy of the rules file whenever a tool is about to change it, and you can compare the current file with any of those copies, compare two copies, or browse to any other rules file. The arrow buttons take you from one change to the next.""")
docs = {FTM_Name       : _translate("CompareRuleFiles", "Compare Rule Files"),
        FTM_Version    : "3.17",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("CompareRuleFiles", "See what has changed between two versions of your transfer rules."),
        FTM_Help       : "",
        FTM_Description : descr}

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):

    thisApp = QApplication.instance()

    if thisApp is None:

        thisApp = QApplication(['FLExTrans'])

    localTranslators = []
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], localTranslators, loadBase=True)

    configMap = ReadConfig.readConfig(report)

    if not configMap:

        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    transferPath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report)

    if not transferPath:

        return

    if not os.path.isfile(transferPath):

        report.Error(_translate('CompareRuleFiles', 'Transfer rules file not found: {path}').format(path=Utils.shortenPathForDisplay(transferPath)))
        return

    # Imported here rather than at the top so that FlexTools listing the module doesn't load the web view.
    from CompareRuleFilesDlg import CompareRuleFilesDlg

    dlg = CompareRuleFilesDlg(transferPath)
    dlg.show()
    thisApp.exec()

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction, docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':

    FlexToolsModule.Help()
