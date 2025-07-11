#
#   Publications.Reset_Publications
# 
#   Clear all the PublishIn values to reset the project to exclude
#   all entries from all publications.
#
#   The PublishIn fields for headwords, senses, pronunciations, examples, 
#   and pictures are reset to remove any custom configuration.
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Reset Publications (entry only)",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Clear all the PublishIn values",
        FTM_Help       : None,
        FTM_Description: 
"""
Clear all the PublishIn values to reset the project to exclude
all entries from all publications.

The PublishIn fields for headwords, senses, pronunciations, examples, 
and pictures are reset to remove any custom configuration.
""" 
}


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):
    
    piCount = 0
    for e in project.LexiconAllEntries():
        hw = project.LexiconGetHeadword(e)

        if e.PublishIn.Count > 0:
            piCount += 1
            if modifyAllowed:
                e.PublishIn.Clear()
                
    # TODO: headwords, senses, pronunciations, examples, pictures
    
        
    if modifyAllowed:
        report.Info(f"Publish In field cleared in {piCount} entries.")
    else:
        report.Info(f"{piCount} entries are in one or more publications.")
        report.Info(f"Run this module again with Modify to remove all entries from all publications.")
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
