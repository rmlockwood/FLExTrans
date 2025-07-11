#
#   Incomplete_Analyses
#    - A FlexTools Module -
#
#   C D Farrow
#   June 2014
#
#   Platforms: Python.NET and IronPython
#

from flextoolslib import *

from SIL.LCModel import (
    ISegmentRepository,
    PunctuationFormTags,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr

from collections import defaultdict

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Incomplete Analyses",
        FTM_Version    : 2,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Report on analyses that have missing Morphs or Senses.",
        FTM_Help       : None,
        FTM_Description:
"""
This module reports all the words in the corpus that haven't been
fully analysed, so the user can easily find gaps in their analysis.
"""
}
                 
#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    report.ProgressStart(project.ObjectCountFor(ISegmentRepository))

    for seg_num, seg in enumerate(project.ObjectsIn(ISegmentRepository)):
        report.ProgressUpdate(seg_num)

        for analysis in seg.AnalysesRS:
            if analysis.Analysis:
                for mb in analysis.Analysis.MorphBundlesOS:
                    if not mb.MorphRA or not mb.SenseRA:
                        report.Warning("%s: Missing morphs or senses"
                                       % analysis.Analysis.ShortNameTSS,
                                       project.BuildGotoURL(analysis))
            else:                
                # Skip punctuation
                if analysis.ClassID == PunctuationFormTags.kClassId:
                    continue
                # TODO - some with ??? - what are they (Parser-experiments)
                # report.Warning("%s: not analysed" % ITsString(analysis.ChooserNameTS).Text,
                report.Warning("%s - %s: not analysed" % (seg.BaselineText,
                               ITsString(analysis.ChooserNameTS).Text),
                               project.BuildGotoURL(analysis))


#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:

FlexToolsModule = FlexToolsModuleClass(runFunction = Main,
                                       docs = docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
