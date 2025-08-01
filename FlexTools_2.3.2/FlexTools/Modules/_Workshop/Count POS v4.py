#
#   Count_POS
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from collections import defaultdict

from SIL.LCModel import ILexEntry

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Count POS (debugging)",
        FTM_Version    : 4,
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
   
    report.ProgressStart(project.LexiconNumberOfEntries())
   
    for entryNumber, entry in enumerate(project.LexiconAllEntries()):
        report.ProgressUpdate(entryNumber)

        # Ignore affixes
        # if entry.LexemeFormOA.MorphTypeRA.IsAffixType:
            # continue
            
        for sense in entry.SensesOS:
            if not sense.MorphoSyntaxAnalysisRA:
                Gloss = project.LexiconGetSenseGloss(sense)
                report.Warning(f"Sense '{Gloss}' has no POS",
                               project.BuildGotoURL(sense))
                continue

            POS = sense.MorphoSyntaxAnalysisRA.ShortName
            POSCount[POS] += 1

        # report.Info(repr(type(entry)))
        # report.Info(entry.ClassName)
        # report.Info(repr(dir(ILexEntry)))
        # report.Info(repr(POSCount))
        # break

    for POS in sorted(POSCount):
        report.Info(f"{POS} is used in {POSCount[POS]} senses")


#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
