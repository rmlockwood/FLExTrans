#
#   Custom menu functions for FLExTrans
#
#   Version 3.12 - 2/9/25 - Ron Lockwood
#    Fixes #878. Menu option for editing transfer rules.
#
#   Version 3.9 - 7/25/23 - Ron Lockwood
#    no https in the address for RunAbout
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Settings are now launched from the menu

from System.Windows.Forms import (
    Shortcut,
    MessageBox, MessageBoxButtons, MessageBoxIcon,
    )
    
import os
from subprocess import call

import SettingsGUI
from FTPaths import HELP_DIR
import Version
import ReadConfig

def RunSettings(sender, event):
    SettingsGUI.MainFunction(None, None)

def RunEditTransferRules(sender, event):
        
    configMap = ReadConfig.readConfig(None)

    if not configMap:
        return

    # Get the path to the transfer rules file
    xferRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report=None, giveError=True)

    if not xferRulesFile or os.path.exists(xferRulesFile) == False:

        MessageBox.Show(f'Transfer rule file: {xferRulesFile} does not exist.', 'Not Found Error', MessageBoxButtons.OK)
        return

    progFilesFolder = os.environ['ProgramFiles(x86)']
    xxe = progFilesFolder + '\\XMLmind_XML_Editor\\bin\\xxe.exe'
    call([xxe, xferRulesFile])

def RunHelp(sender, event):

    HelpFile = os.path.join(HELP_DIR, "UserDoc.htm")
    os.startfile(HelpFile)

def RunAbout(sender, event):

    MessageBox.Show(f"{Version.Name} version {Version.Version}\n\nsoftware.sil.org/flextrans", "About FLExTrans", MessageBoxButtons.OK)
          
customMenu = ("FLExTrans",
              [(RunHelp, "Help", Shortcut.CtrlH, None),
               (RunSettings, "Settings", Shortcut.CtrlS, None),
               (RunEditTransferRules, "Edit Transfer Rules", Shortcut.CtrlT, None),
               (RunAbout, "About", None, "About FLExTrans"),
               ])

