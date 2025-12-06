#
#   Reset Publications
# 
#   Clear all the Publish In values to reset the project to exclude
#   all entries from all publications.
#
#   The Publish In fields for headwords, senses, pronunciations, examples, 
#   and pictures are reset to remove any custom configuration.
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Reset Publications (+ other fields)",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Reset all the Publish In settings",
        FTM_Help       : None,
        FTM_Description: 
"""
Clear all the Publish In settings to reset the project to exclude
all entries from all publications.

The Publish In fields for headwords, senses, pronunciations, examples, 
and pictures are reset to remove any custom configuration.
""" 
}


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):
    
    piEntries = 0
    for e in project.LexiconAllEntries():
        hw = project.LexiconGetHeadword(e)

        if e.PublishIn.Count > 0:
            piEntries += 1
            if modifyAllowed:
                e.PublishIn.Clear()
                
    # TODO: headwords, senses, pronunciations, examples, pictures
    
        
    if modifyAllowed:
        report.Info(f"Publish In field cleared in {piEntries} entries.")
    else:
        report.Info(f"{piEntries} entries are in one or more publications.")
        report.Info(f"Run this module again with Modify to remove all entries from all publications.")
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
