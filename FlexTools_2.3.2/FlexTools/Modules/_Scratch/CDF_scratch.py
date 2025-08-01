#
#   <Module name>
#
#   <Module description>
#
#   <Author>
#   <Date>
#

from flextoolslib import *

from SIL.LCModel import IMultiString, IMultiUnicode
from SIL.LCModel import ILexExampleSentenceFactory

from SIL.LCModel import (
    IFsClosedFeatureRepository,
    IMoAffixAllomorph,
    IMoInflAffMsa,
    IFsFeatStruc,
    IFsClosedFeature,
    IFsClosedValue,
    )


import logging

logger = logging.getLogger(__name__)

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "CDF Scratch",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "<description>",
        FTM_Help       : None,
        FTM_Description: 
"""
<more detail here>
""" }


class Example(str):
    pass

#----------------------------------------------------------------
import fnmatch, os           

def Main(project, report, modifyAllowed):

    def __reportObject(obj):
        report.Info(f"{type(obj)}")
        report.Info(f"{obj}")
        if isinstance(obj, (IMultiUnicode, IMultiString)):
            report.Info(f"{project.BestStr(obj)}")
            report.Info(f"{type(obj.BestAnalysisVernacularAlternative)}")
            report.Info(f"{obj.BestAnalysisVernacularAlternative}")
            report.Info(f"{dir(obj.BestAnalysisVernacularAlternative)}")
        else:
            report.Info(f"{obj.Text}")
    
    
    
    # Version 1
    allExamples = []

    for e in project.LexiconAllEntries():
        hw = e.HeadWord
        report.Info(f"{hw}: {e.Guid}")
        for sense in e.SensesOS:
            if modifyAllowed:
                newex = project.project.ServiceLocator.GetInstance(ILexExampleSentenceFactory).Create()
                sense.ExamplesOS.Add(newex)
                project.LexiconSetExample(newex, "Once upon a time far far away.")
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    report.Info(exampleSentence)
            return

    report.Info(f"{len(allExamples)} example sentences")
    for e, exampleObj in sorted(allExamples)[:3]:
        report.Info("  :" + e, project.BuildGotoURL(exampleObj))
        
    
    # entry = next(project.LexiconAllEntries())
    # report.Info(f"Found entry '{entry.HeadWord}'})
    

    
    counter = 0
    numWithInflectionFeatures = 0
   
    # Version 2
    allExamples = []
    dnpiCount = 0
    for e in project.LexiconAllEntries():
        MorphType = e.LexemeFormOA.MorphTypeRA
        if not (MorphType.IsPrefixishType and e.NumberOfSensesForEntry == 1):
            continue
                        
        for msa in e.MorphoSyntaxAnalysesOC:
            if msa.ClassName != "MoInflAffMsa":
                continue
                
            msa = IMoInflAffMsa(msa)       
            if msa.InflFeatsOA:
                numWithInflectionFeatures += 1
                # The Inflection Features:
                for fs in msa.InflFeatsOA.FeatureSpecsOC:
                    if fs.ClassName == "FsClosedValue":
                        cv = IFsClosedValue(fs)
                        feature = IFsClosedFeature(cv.FeatureRA)
                        featureName = project.BestStr(feature.Name)
                        valueName = project.BestStr(cv.ValueRA.Name)
                        report.Info(f"    Feature: {featureName} [{valueName}]")


        continue


        if e.DoNotPublishInRC.Count > 0:
            report.Info(f"DoNotPublishInRC.Count = {e.DoNotPublishInRC.Count}")
            dnpiCount+=1
            for dnpi in e.DoNotPublishInRC:
                report.Info(f"{project.BestStr(dnpi.Name)}")
                report.Info(dnpi.Owner)
                report.Info(dnpi.Owner.ClassName)
                report.Info(dnpi.Owner.Owner)
                report.Info(dnpi.Owner.Owner.ClassName)
            break
        # try:
            # pubs = publicationListByHeadword[hw]
        # except KeyError:
            # report.Warning(f"{hw} not in publications list")
            # continue
        # report.Info(f"--> Setting publications as {pubs}")
            
        for sense in e.SensesOS:
            
            for example in sense.ExamplesOS:
                exampleSentence = project.LexiconGetExample(example)
                if exampleSentence:
                    exampleSentence = Example(exampleSentence)
                    exampleSentence.FWObject = example
                    allExamples.append(exampleSentence)

    report.Info(f"The project has {counter} Verb Subject prefixes")
    report.Info(f"    {numWithInflectionFeatures} have Inflection Features defined.")
    report.Blank()

    report.Info(f"{len(allExamples)} example sentences")
    for ex in sorted(allExamples)[:3]:
        report.Info("  :" + ex, project.BuildGotoURL(ex.FWObject))
        
    report.Info(f"DNPI count = {dnpiCount}")
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
