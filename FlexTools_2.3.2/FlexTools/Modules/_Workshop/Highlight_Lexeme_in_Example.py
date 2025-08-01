#
#   Highlight_Lexeme_in_Example
#    - A FlexTools Module -
#
#
#   C D Farrow
#

from flextoolslib import *

from SIL.LCModel.Core.KernelInterfaces import (
    ITsString, ITsTextProps, 
    ITsStrFactory, ITsPropsFactory, 
    ITsStrBldr, ITsIncStrBldr, ITsPropsBldr, 
    ITsMultiString, 
    FwTextPropType, FwTextPropVar 
    ) 

from SIL.LCModel.Core.Text import TsStringUtils, TsIncStrBldr 


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Highlight lexeme in example (find #1)",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Highlight the lexeme in example sentences.",
        FTM_Help       : None,
        FTM_Description:
"""
Highlight the lexeme as Emphasized Text in example sentences. 
Requires an exact match of the lexeme (no affixes).
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    wsf = project.project.WritingSystemFactory
    wsv = project.project.DefaultVernWs 
    wsa = project.project.DefaultAnalWs

    for e in project.LexiconAllEntries():
        lexeme = project.LexiconGetLexemeForm(e)
        report.Info(lexeme, project.BuildGotoURL(e))
        for sense in e.SensesOS:
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    report.Info(f"  Example: {exampleSentence}")
                    # Make a TsString, since lexeme is a MultiUnicode
                    lfTSS = TsStringUtils.MakeString(lexeme, wsv)
                    result, start, end = TsStringUtils.FindTextInString(
                                            lfTSS,
                                            example.Example.get_String(wsv),
                                            wsf,
                                            True,
                                            0,0)
                    if result:
                        report.Info(f"  >> Found lexeme form at {start}-{end}!",
                                    project.BuildGotoURL(example))

#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
