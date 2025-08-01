#
#   Delete_Example
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from SIL.LCModel import ILexExampleSentenceFactory

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Delete Example",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Delete an example sentence in the first LexEntry.",
        FTM_Help       : None,
        FTM_Description:
"""
Delete any example sentence in the first LexEntry that begin with "DEL".
This is for demonstration purposes only.
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    e = next(project.LexiconAllEntries())
    hw = e.HeadWord
    report.Info(f"{hw}: {e.Guid}")
    for sense in e.SensesOS:
        for example in sense.ExamplesOS:
            exampleSentence = project.LexiconGetExample(example)
            if exampleSentence and exampleSentence.startswith("DEL"):
                report.Info(f"Deleting example sentence, '{exampleSentence}'")
                if modifyAllowed:
                    # Either of these lines will work:
                    # sense.ExamplesOS.Remove(example)
                    example.Delete()

#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
