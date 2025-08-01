#
#   Count_POS
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from collections import defaultdict


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Count POS (working)",
        FTM_Version    : 2,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Report the number of senses assigned to each POS.",
        FTM_Help       : None,
        FTM_Description:
"""
This module reports the number of senses in the project by POS. 
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    report.Info("Counting the number of senses assigned to each POS...")
    POSCount = defaultdict(int)
   
    for entry in project.LexiconAllEntries():
        # Ignore affixes
        if entry.LexemeFormOA.MorphTypeRA.IsAffixType:
            continue
            
        for sense in entry.SensesOS:
            POS = sense.MorphoSyntaxAnalysisRA.ShortName
            POSCount[POS] += 1

    for POS in sorted(POSCount):
        report.Info(f"{POS} is used in {POSCount[POS]} senses")


#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
