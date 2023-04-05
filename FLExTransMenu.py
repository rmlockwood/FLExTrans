#
#   Custom menu functions for FLExTrans
#

from System.Windows.Forms import (
    Shortcut,
    MessageBox, MessageBoxButtons, MessageBoxIcon,
    )
    
    
#-----------------------------------------------------------
import SettingsGUI

def RunSettings(sender, event):
    MessageBox.Show("Settings dialog could be launched here", "Settings",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning)
    # TODO - This doesn't work because it needs the source project to be supplied.
    # SettingsGUI.py is on the path (being in the Modules directory); but it
    # could be moved into this folder, if it makes sense to access the settings through the menu.
    #SettingsGUI.MainFunction(None, None)
          
#----------------------------------------------------------- 
from FTPaths import HELP_DIR
import os

def RunHelp(sender, event):
    HelpFile = os.path.join(HELP_DIR, "UserDoc.htm")
    os.startfile(HelpFile)

#----------------------------------------------------------- 
import Version

def RunAbout(sender, event):
    MessageBox.Show(f"{Version.Name} version {Version.Version}", "About FLExTrans",
                    MessageBoxButtons.OK)
          
#----------------------------------------------------------- 

customMenu = ("FLExTrans",
              [(RunHelp, 
                "Help", 
                Shortcut.CtrlH,
                None),
               (RunAbout,
                "About", 
                None,
                "About FLExTrans")])

