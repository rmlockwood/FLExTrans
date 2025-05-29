#
#   Custom menu functions for FLExTrans
#
#   Version 3.13.1 - 5/9/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 2/9/25 - Ron Lockwood
#    Fixes #878. Menu option for editing transfer rules.
#
#   Version 3.9 - 7/25/23 - Ron Lockwood
#    no https in the address for RunAbout
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Settings are now launched from the menu

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication, QTranslator
from System.Windows.Forms import (  # type: ignore
    Shortcut,
    MessageBox,
    MessageBoxButtons,
)

import os
from subprocess import call

import SettingsGUI
from FTPaths import HELP_DIR, TRANSL_DIR
import Version
import ReadConfig
import Utils

def RunSettings(sender, event):

    SettingsGUI.MainFunction(None, None)

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'FLExTransMenu'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig'] 

def RunEditTransferRules(sender, event):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=False)
    
    configMap = ReadConfig.readConfig(None)

    if not configMap:
        return

    # Get the path to the transfer rules file
    xferRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report=None, giveError=True)

    if not xferRulesFile or os.path.exists(xferRulesFile) == False:

        MessageBox.Show(_translate("FLExTransMenu", "Transfer rule file: {xferRulesFile} does not exist.").format(xferRulesFile=xferRulesFile),
                        _translate("FLExTransMenu", "Not Found Error"),
                        MessageBoxButtons.OK)
        return

    progFilesFolder = os.environ["ProgramFiles(x86)"]
    xxe = progFilesFolder + "\\XMLmind_XML_Editor\\bin\\xxe.exe"
    call([xxe, xferRulesFile])



def RunHelp(sender, event):

    HelpFile = os.path.join(HELP_DIR, "UserDoc.htm")
    os.startfile(HelpFile)

def RunAbout(sender, event):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=False)
    
    MessageBox.Show(
        _translate("FLExTransMenu", "{name} version {version}\n\nsoftware.sil.org/flextrans").format(name=Version.Name, version=Version.Version),
        _translate("FLExTransMenu", "About FLExTrans"),
        MessageBoxButtons.OK)



customMenu = (
    "FLExTrans",
    [
        (RunHelp, _translate("FLExTransMenu", "Help"), Shortcut.CtrlH, None),
        (RunSettings, _translate("FLExTransMenu", "Settings"), Shortcut.CtrlS, None),
        (RunEditTransferRules, _translate("FLExTransMenu", "Edit Transfer Rules"), Shortcut.CtrlT, None),
        (RunAbout, _translate("FLExTransMenu", "About"), None, _translate("FLExTransMenu", "About FLExTrans")),
    ],
)

app.quit()
del app

