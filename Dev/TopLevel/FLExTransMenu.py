#
#   Custom menu functions for FLExTrans
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Fixes #1207. Bring the main form back to the foreground after closing the settings dialog.
#
#   Version 3.14.1 - 7/11/25 - Ron Lockwood
#    Use new shortcuts system.
#
#   Version 3.14 - 5/9/25 - Ron Lockwood
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
from PyQt5.QtCore import QCoreApplication
from System.Windows.Forms import (  # type: ignore
    Keys,
    MessageBox,
    MessageBoxButtons,
)

import os
from subprocess import call

import SettingsGUI
from FTPaths import HELP_DIR
import Version
import ReadConfig
import Utils

import ctypes
user32 = ctypes.windll.user32

def RunSettings(sender, event):
    form = sender.OwnerItem.Owner.Parent

    form.Enabled = False
    SettingsGUI.MainFunction(None, None)
    form.Enabled = True

    # Bring the form back to the foreground after the settings dialog is closed
    # Same code as in Flexlibs - UIMain.py
    user32.keybd_event(0,0,0,0)
    hwnd = form.Handle.ToInt32()
    user32.SetForegroundWindow(hwnd)
    
# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'FLExTransMenu'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig'] 

def RunEditTransferRules(sender, event):

    translators = []
    app = QApplication.instance()

    if app is None:
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
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=False)
    
    MessageBox.Show(
        _translate("FLExTransMenu", "{name} version {version}\n\nBuild {build}, {build_date}\n\nsoftware.sil.org/flextrans").format(name=Version.Name, version=Version.Version, build=Version.Build, build_date=Version.BuildDate),
        _translate("FLExTransMenu", "About FLExTrans"),
        MessageBoxButtons.OK)



customMenu = (
    "FLExTrans",
    [
        (RunHelp, _translate("FLExTransMenu", "Help"), Keys.Control | Keys.H, None),
        (RunSettings, _translate("FLExTransMenu", "Settings"), Keys.Control | Keys.S, None),
        (RunEditTransferRules, _translate("FLExTransMenu", "Edit Transfer Rules"), Keys.Control | Keys.T, None),
        (RunAbout, _translate("FLExTransMenu", "About"), None, _translate("FLExTransMenu", "About FLExTrans")),
    ],
)

#app.quit()
#del app

