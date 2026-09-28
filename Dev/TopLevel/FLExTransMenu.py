#
#   Custom menu functions for FLExTrans
#
#   Version 3.17.2 - 9/28/26 - Ron Lockwood
#    Fixes #1570. Added an Open Target Project menu item that starts FLEx with the target project from the settings and reports to the FlexTools output area.
#
#   Version 3.17.1 - 8/28/26 - Ron Lockwood
#    Show the FLExTrans icon in the About box by using a Qt message box and make the web address a clickable link.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.15.2 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15.1 - 3/4/26 - Ron Lockwood
#    Fixes #1255. Error checking for the XXE program and successfully opening the transfer rules file in XXE.
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

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QIcon, QPixmap
from System.Windows.Forms import (  # type: ignore
    Keys,
    MessageBox,
    MessageBoxButtons,
)

import os
import subprocess
from subprocess import Popen, DETACHED_PROCESS

import SettingsGUI
from FTPaths import HELP_DIR, TOOLS_DIR
import Version
import ReadConfig
import Utils

import ctypes
user32 = ctypes.windll.user32

from flextoolslib import lockUI
from flextoolslib.code import FLExTools as FTMain

def RunSettings(sender, event):
    lockUI(True)
    SettingsGUI.MainFunction(None, None)
    lockUI(False)
    
# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'FLExTransMenu'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig'] 

def RunEditTransferRules(sender, event):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

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

    if not os.path.exists(xxe):

        MessageBox.Show(_translate("FLExTransMenu", "XMLmind XML Editor not found at expected location: {xxe}").format(xxe=xxe),
                        _translate("FLExTransMenu", "Not Found Error"),
                        MessageBoxButtons.OK)
        return

    try:
        result = subprocess.run([xxe, xferRulesFile], capture_output=True)

    except Exception as e:

        MessageBox.Show(_translate("FLExTransMenu", "Error occurred while trying to open transfer rules file: {e}").format(e=e),
                        _translate("FLExTransMenu", "Error"),
                        MessageBoxButtons.OK)

def RunOpenTargetProject(sender, event):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + ['Utils', TRANSL_TS_NAME], translators, loadBase=False)

    # Write to the FlexTools output area, the same place FlexTools' own "Open project in FieldWorks" menu item reports to. flextoolslib doesn't export its main form, but keeps
    # it in the module global FLExTools.mainForm (that's what lockUI uses). A menu item can only be clicked once the main form exists, so it is never None here.
    assert FTMain.mainForm is not None
    reportWindow = FTMain.mainForm.UIPanel.reportWindow
    report = reportWindow.Reporter

    configMap = ReadConfig.readConfig(report)

    if not configMap:
        return

    # Get the name of the target project from the settings
    targetProj = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report=None, giveError=False)

    if not targetProj:

        report.Error(_translate("FLExTransMenu", "No target project is set in the settings."))
        return

    # Get the path to the FLEx executable the same way the Open Multiple FLEx Projects module does. The helper reports an error and returns None if FIELDWORKSDIR isn't set.
    flexExe = Utils.getFlexExePath(report)

    if not flexExe:
        return

    if not os.path.isfile(flexExe):

        report.Error(_translate("FLExTransMenu", "Could not find the FLEx executable: {flexExe}.").format(flexExe=Utils.shortenPathForDisplay(flexExe)))
        return

    # Plain text line, matching what FlexTools shows when it opens the current project
    reportWindow.Report(_translate("FLExTransMenu", "Opening project '{proj}' in FieldWorks...").format(proj=targetProj))

    # Start FLEx on the target project. Detach it so that FLEx keeps running independently of FlexTools. If the project is already open, FLEx just brings that window forward.
    try:
        Popen([flexExe, '-db', targetProj], creationflags=DETACHED_PROCESS)

    except OSError as e:

        report.Error(_translate("FLExTransMenu", "Error occurred while trying to open the {proj} project: {e}").format(proj=targetProj, e=e))

def RunHelp(sender, event):

    HelpFile = os.path.join(HELP_DIR, "UserDoc.htm")
    os.startfile(HelpFile)

def RunAbout(sender, event):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=False)
    
    # Use a Qt message box rather than the plain Windows one so that we can show the FLExTrans logo. The small icon goes in the title bar and a 64x64 version of the logo goes in
    # the body of the box, where a standard information/warning icon would normally go.
    flexTransIcon = QIcon(os.path.join(TOOLS_DIR, 'FLExTransWindowIcon.ico'))
    flexTransLogo = QPixmap(os.path.join(TOOLS_DIR, 'FLExTransIcon64.png'))

    msgBox = QMessageBox()
    msgBox.setWindowIcon(flexTransIcon)
    msgBox.setIconPixmap(flexTransLogo)
    msgBox.setWindowTitle(_translate("FLExTransMenu", "About FLExTrans"))

    # Build the message as simple HTML so the web address can be a clickable link. The address is not part of the translatable string since it never changes from one language to the next.
    aboutUrl = 'https://software.sil.org/flextrans'
    aboutText = _translate("FLExTransMenu", "{name} version {version}\n\nBuild {build}, {build_date}").format(name=Version.Name, version=Version.Version, build=Version.Build, build_date=Version.BuildDate)

    # A QMessageBox text label already follows links out to the browser, all we have to do is tell it that the text is HTML. Newlines mean nothing in HTML, so they become line breaks.
    msgBox.setTextFormat(Qt.TextFormat.RichText)
    msgBox.setText(aboutText.replace('\n', '<br>') + f'<br><br><a href="{aboutUrl}">{aboutUrl}</a>')
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok)
    msgBox.exec()



customMenu = (
    "FLExTrans",
    [
        (RunHelp, _translate("FLExTransMenu", "Help"), Keys.Control | Keys.H, None),
        (RunSettings, _translate("FLExTransMenu", "Settings"), Keys.Control | Keys.S, None),
        (RunEditTransferRules, _translate("FLExTransMenu", "Edit Transfer Rules"), Keys.Control | Keys.T, None),
        (RunOpenTargetProject, _translate("FLExTransMenu", "Open Target Project"), Keys.Control | Keys.Shift | Keys.T, _translate("FLExTransMenu", "Open the target project in FLEx")),
        (RunAbout, _translate("FLExTransMenu", "About"), None, _translate("FLExTransMenu", "About FLExTrans")),
    ],
)

#app.quit()
#del app

