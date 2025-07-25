#
#   Export.Export_All_Publications_To_Files
#    - A FlexTools Module -
#
#   Export all headwords from each publication to a file. 
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

from _Exporters import Export_Publication

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export All Publications To Files",
        FTM_Version     : 3,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export all headwords from each publication to a file.",
        FTM_Description :
"""
Export all headwords from each publication to a file (one file for each publication). 
""" 
}
   
   
#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    for pubName in project.GetPublications():
        Export_Publication(project, report, pubName)

    report.Info("Total lexical entries in project = {}".format(
                project.LexiconNumberOfEntries()))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
    