#
#   Export.Export_Publication_To_File
#    - A FlexTools Module -
#
#   Export all headwords from a certain publication to a file. The
#   publication name is defined in this module.
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

from _Exporters import Export_Publication

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name        : "Export Publication To File (hardwired)",
        FTM_Version     : 1,
        FTM_ModifiesDB  : False,
        FTM_Synopsis    : "Export headwords from one publication to a file.",
        FTM_Description :
"""
Export all headwords from a certain publication to a file. The
publication name is defined in this module.
""" 
}

DICTIONARY_NAME = "M-Words Dictionary"


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    Export_Publication(project, report, DICTIONARY_NAME)   

    report.Info("Total lexical entries in project = {}".format(
                project.LexiconNumberOfEntries()))

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
    