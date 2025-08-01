#
#   Reports.Lexical_Relations
#   
#    - A FlexTools Module
#


from flextoolslib import *

from SIL.LCModel import LexEntryTags
from SIL.LCModel import ILexEntry, ILexSense

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Lexical Relations",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "List all the lexical relations in the project",
        FTM_Help       : None,
        FTM_Description:
"""
List all the lexical relations in the project.
""" 
}


#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    report.Info("The following lexical relations are used in this project:")   
    
    LRTUsed = 0
    LRCount = 0
    for lrt in project.GetLexicalRelationTypes():
        if (lrt.MembersOC.Count > 0):
            # TODO - improve output: show the other entry gloss, too.
            if lrt.ReverseName:
                report.Info(f"Lexical relation: {lrt} <> {project.BestStr(lrt.ReverseName)}")
            else:
                report.Info(f"Lexical relation: {lrt}")
            LRTUsed += 1
            for lr in lrt.MembersOC:
                for target in lr.TargetsRS:
                    LRCount += 1
                    if target.ClassID == LexEntryTags.kClassId:
                        entry = ILexEntry(target)
                        report.Info("    Entry: %s" % 
                                (project.LexiconGetLexemeForm(entry)),
                                 project.BuildGotoURL(entry))
                    else: # Relations have only LexEntry or LexSense
                        sense = ILexSense(target)
                        report.Info("    Sense: %s [%s]" % 
                                (project.BestStr(sense.Gloss),
                                 project.LexiconGetSensePOS(sense)),
                                 project.BuildGotoURL(sense))
                report.Blank()
     
    report.Info(f"{LRTUsed} lexical relation type{'' if LRTUsed==1 else 's'} used.")
    report.Info(f"{LRCount} lexical relation{'' if LRCount==1 else 's'} defined.")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
