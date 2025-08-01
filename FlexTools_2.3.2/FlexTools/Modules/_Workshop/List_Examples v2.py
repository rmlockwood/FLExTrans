#
#   List Examples
#

from flextoolslib import *

from SIL.LCModel import IMultiString, IMultiUnicode

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "List Examples (class)",
        FTM_Version    : 2,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "List all the example sentences in the project.",
        FTM_Help       : None,
        FTM_Description: 
"""
Illustrates use of a wrapper class to store the extra FW object pointer;
sorted() works without a lambda fucntion for the sort key.
""" }


class Example(str):
    pass

#----------------------------------------------------------------

def Main(project, report, modifyAllowed):       
        
    # Version 2
    allExamples = []

    for e in project.LexiconAllEntries():
        hw = e.HeadWord
        for sense in e.SensesOS:
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    exampleSentence = Example(exampleSentence)
                    exampleSentence.FWObject = example
                    allExamples.append(exampleSentence)

    report.Info(f"{len(allExamples)} example sentences")
    for ex in sorted(allExamples)[:5]:
        report.Info("  :" + ex, project.BuildGotoURL(ex.FWObject))
        

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
