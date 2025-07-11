#
#   Publications.Import_Publication_Lists
#
#   Import lists of headwords and set the entry Publish In field
#   to match each Publication-List set. Does not touch the other
#   Publish In fields (in Sense, Pronuciation, Example, Picture).
#
#   Craig Farrow
#   July 2024
#

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Import Publication Lists (hardwired)",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Import lists of headwords and set the entry Publish In field to match",
        FTM_Help       : None,
        FTM_Description: 
"""
Import lists of headwords and set the entry Publish In field
to match each Publication-List set. Does not touch the other
Publish In fields (in Sense, Pronuciation, Example, Picture).
""" }

FNAME_SUFFIX = "_Headwords.txt"

DICTIONARY_NAME = "Tiny Dictionary"


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):
        
    fname = DICTIONARY_NAME + FNAME_SUFFIX
    try:
        with open(fname, encoding='utf-8') as f:
            headwords = f.read().splitlines()
    except FileNotFoundError:
        report.Error(f"{fname} not found!")
        return

    report.Info(f"{fname} found")
    report.Info(f"    {len(headwords)} headwords in file.")
    
    report.Info(f"Adding entries to {DICTIONARY_NAME}...")
    
    pubType = project.PublicationType(DICTIONARY_NAME)
    if not pubType:
        report.Error(f"{DICTIONARY_NAME} isn't in the list of publications for this project:")
        report.Info("   " + ", ".join(project.GetPublications()))
        return

    toAdd = 0
    for e in project.LexiconAllEntries():
        hw = project.LexiconGetHeadword(e)
        
        if hw in headwords:
            if modifyAllowed:
                report.Info(f"Adding {hw} to publication")
                e.PublishIn.Add(pubType)
            else:
                report.Info(f"{hw} to be added to publication.")
                
            toAdd += 1 
            
    if modifyAllowed:
        report.Info(f"{DICTIONARY_NAME} added to {toAdd} entries")
    else:
        report.Info(f"{DICTIONARY_NAME} to be added to {toAdd} entries.")
        report.Info(f"Run this module again with Modify to make the changes.")
        
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
