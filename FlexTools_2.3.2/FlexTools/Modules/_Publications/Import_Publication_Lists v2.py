#
#   Publications.Import_Publication_Lists
#
#   Import lists of headwords and set the entry Publish In field
#   to match each publication list. Does not touch the other
#   Publish In fields (in Sense, Pronuciation, Example, Picture).
#
#   Craig Farrow
#   July 2024
#

import os
import fnmatch

from flextoolslib import *

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Import Publication Lists (find files)",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Import lists of headwords and set the entry Publish In field to match",
        FTM_Help       : None,
        FTM_Description: 
"""
Import lists of headwords and set the entry Publish In field
to match each publication list. Does not touch the other
Publish In fields (in Sense, Pronuciation, Example, Picture).
""" 
}

FNAME_SUFFIX = "_Headwords.txt"

#----------------------------------------------------------------

def Main(project, report, modifyAllowed):
    
    pubNames = fnmatch.filter(os.listdir(), "*"+FNAME_SUFFIX)

    report.Info(f"Publication files: {pubNames}")
    
    for fname in pubNames:
        pubName = fname.rstrip(FNAME_SUFFIX)
        
        report.Info(f"Importing headword list from {fname}")
        report.Info(f"   Configuring {pubName}...")
        
        with open(fname, encoding='utf-8') as f:
            headwords = f.read().splitlines()

        report.Info(f"   {len(headwords)} headwords in file.")
        
        pubType = project.PublicationType(pubName)
        if not pubType:
            report.Error(f"{pubName} isn't in the list of publications for this project:")
            report.Info("   " + ", ".join(project.GetPublications()))
            continue
            
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
            report.Info(f"{pubName} added to {toAdd} entries")
        else:
            report.Info(f"{pubName} to be added to {toAdd} entries.")
            report.Info(f"Run this module again with Modify to make the changes.")
        
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
