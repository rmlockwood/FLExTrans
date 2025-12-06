#
#   Create_Example
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from SIL.LCModel import ILexExampleSentenceFactory

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Create Example",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Create an example sentence in the first LexEntry.",
        FTM_Help       : None,
        FTM_Description:
"""
Create an example sentence in the first LexEntry.
This is for demonstration purposes only.
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    e = next(project.LexiconAllEntries())
    hw = e.HeadWord
    report.Info(f"{hw}: {e.Guid}")
    for sense in e.SensesOS:
        if modifyAllowed:
            newex = project.project.ServiceLocator.GetInstance(ILexExampleSentenceFactory).Create()
            sense.ExamplesOS.Add(newex)
            project.LexiconSetExample(newex, "Once upon a time, far far away.")
        for example in sense.ExamplesOS:
            exampleSentence = project.LexiconGetExample(example)
            if exampleSentence:
                report.Info(exampleSentence)       
    

#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
