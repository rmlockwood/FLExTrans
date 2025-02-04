#
#   Custom menu functions for FLExTrans
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
    
import SettingsGUI
from FTPaths import HELP_DIR
import os
import Version

def RunSettings(sender, event):
    SettingsGUI.MainFunction(None, None)

def RunHelp(sender, event):
    HelpFile = os.path.join(HELP_DIR, "UserDoc.htm")
    os.startfile(HelpFile)

def RunAbout(sender, event):
    MessageBox.Show(f"{Version.Name} version {Version.Version}\n\nsoftware.sil.org/flextrans", "About FLExTrans",
                    MessageBoxButtons.OK)
          
customMenu = ("FLExTrans",
              [(RunHelp, "Help", Shortcut.CtrlH, None),
               (RunSettings, "Settings", Shortcut.CtrlS, None),
               (RunAbout, "About", None, "About FLExTrans")])

