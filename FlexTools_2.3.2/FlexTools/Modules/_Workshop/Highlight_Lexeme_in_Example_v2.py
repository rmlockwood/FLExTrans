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

docs = {FTM_Name       : "Highlight lexeme in example (set emphasised)",
        FTM_Version    : 2,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Highlight the lexeme in example sentences.",
        FTM_Help       : None,
        FTM_Description:
"""
Highlight the lexeme as Emphasized Text in example sentences. 
Requires an exact match of the lexeme (no affixes).
Warning: this will clear any other formatting in the field.
"""
}

#----------------------------------------------------------------


#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    def BuildStringWithEmph(text, start, end):

        tisb = TsStringUtils.MakeIncStrBldr() 
        tisb.SetIntPropValues(FwTextPropType.ktptWs.value__, FwTextPropVar.ktpvDefault.value__, wsv)

        if start > 0:
            tisb.Append(text[:start])
            
        tisb.SetStrPropValue(FwTextPropType.ktptNamedStyle.value__, "Deleted Text") 
        tisb.Append(text[start:end])
        
        if end < len(text):
            tisb.SetStrPropValue(FwTextPropType.ktptNamedStyle.value__, None)
            tisb.Append(text[end:])

        return tisb.GetString() 
        
    wsf = project.project.WritingSystemFactory
    wsv = project.project.DefaultVernWs 
    wsa = project.project.DefaultAnalWs

    for entry in project.LexiconAllEntries():
        lexeme = project.LexiconGetLexemeForm(entry)
        report.Info(lexeme, project.BuildGotoURL(entry))
        for sense in entry.SensesOS:
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    report.Info(f"  Example: {exampleSentence}")
                    report.Info(f"  ({example.Example.get_String(wsv).RunCount} runs)")
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
                        tss = BuildStringWithEmph(exampleSentence, start, end)
                        if modifyAllowed:
                            example.Example.set_String(wsv, tss)
                        

#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
