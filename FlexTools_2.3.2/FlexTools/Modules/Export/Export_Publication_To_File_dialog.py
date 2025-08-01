#
#   Export.Export_Publication_To_File
#    - A FlexTools Module -
#
#   Export all headwords from a publication to a file. The
#   publication name is chosen from a dialog box.
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

from _Exporters import Export_Publication
from Dialog_Radiobuttons_4 import RadioChooserDialog

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export Publication To File (dialog)",
        FTM_Version     : 2,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export headwords from one publication to a file.",
        FTM_Description :
"""
Export all headwords from a publication to a file. The
publication name is chosen from a dialog box.
""" }

# TODO - Get the name from a dialog
DICTIONARY_NAME = "M-Words Dictionary"


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    dlg = RadioChooserDialog()
    dlg.ShowDialog()
    
    report.Info(f"Selected: {dlg.radioButton1.Text} {dlg.radioButton1.Checked}")
    report.Info(f"Selected: {dlg.radioButton2.Text} {dlg.radioButton2.Checked}")

    Export_Publication(project, report, DICTIONARY_NAME)   
    
    report.Info("Total lexical entries in project = {}".format(
                project.LexiconNumberOfEntries()))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
    