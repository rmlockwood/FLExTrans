#
#   List Examples
#

from flextoolslib import *

from SIL.LCModel import IMultiString, IMultiUnicode

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "List Examples (tuple)",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "List all the example sentences in the project.",
        FTM_Help       : None,
        FTM_Description: 
"""
Illustrates failure when trying to use sorted() with no lambda function
for the sort key.
""" }

#----------------------------------------------------------------

def Main(project, report, modifyAllowed):

    # Version 1
    allExamples = []

    for e in project.LexiconAllEntries():
        hw = e.HeadWord
        for sense in e.SensesOS:
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    # Use a tuple to store the sentence and the example object.
                    allExamples.append((exampleSentence, example))

    report.Info(f"{len(allExamples)} example sentences")
    for ex, exampleObj in allExamples[:5]:
        report.Info("  :" + ex, project.BuildGotoURL(exampleObj))
    
    report.Blank()
    
    # for ex, exampleObj in sorted(allExamples)[:5]:
        # report.Info("  :" + ex, project.BuildGotoURL(exampleObj))

    # report.Blank()
    
    for ex, exampleObj in sorted(allExamples, key = lambda t: t[0])[:5]:
        report.Info("  :" + ex, project.BuildGotoURL(exampleObj))
        

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
