#
#   TranslateText
#
#   Ron Lockwood
#   SIL International
#   12/31/24
#
#   Version 3.13 - 3/19/25 - Ron Lockwood
#    Info messages added and some blank lines.
#    Also, do Export to Paratext as the default last step.
#
#   Version 3.12 - 12/31/24 - Ron Lockwood
#    Initial version.
#
#
# This module does everything in the Drafting collection in one go. 


import os

from flextoolslib import *                                                 

from Modules.FLExTrans import ConvertTextToSTAMPformat, DoHermitCrabSynthesis, DoStampSynthesis, InsertTargetText, ExportToParatext, ExtractBilingualLexicon, CatalogTargetAffixes, RunApertium
import ReadConfig
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Translate Text",
        FTM_Version    : "3.13",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Translate the current source text.",    
        FTM_Help   : "",
        FTM_Description: 
"""
Translate the current source text.
""" }

FINAL_MODULE_IS_EXPORT_TO_PARATEXT = True # Otherwise, the last module is Insert Target Text

def extractSourcText(DB, configMap, report):

    # Build an output path using the system temp directory.
    fullPathTextOutputFile = ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TEXT_FILE, report)

    if not fullPathTextOutputFile:
        return None
    
    abbrPath = Utils.getPathRelativeToWorkProjectsDir(fullPathTextOutputFile)
    
    try:
        f_out = open(fullPathTextOutputFile, 'w', encoding='utf-8')
    except IOError:
        report.Error('There is a problem with the Analyzed Text Output File path: '+fullPathTextOutputFile+'. Please check the configuration file setting.')
        return None
    
    # Find the desired text
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)

    if not sourceTextName:
        return None
    
    matchingContentsObjList = []

    # Create a list of source text names
    sourceTextList = Utils.getSourceTextList(DB, matchingContentsObjList)
    
    if sourceTextName not in sourceTextList:
        
        report.Error('The text named: '+sourceTextName+' not found.')
        return None
    else:
        contents = matchingContentsObjList[sourceTextList.index(sourceTextName)]
    
    # Get various bits of data for the get interlinear function
    interlinParams = Utils.initInterlinParams(configMap, report, contents)

    # Check for an error
    if interlinParams == None:
        return None

    # Get interlinear data. A complex text object is returned.
    myText = Utils.getInterlinData(DB, report, interlinParams)
        
    # Write out all the words
    myText.write(f_out)
    totalStr = str(myText.getSentCount())
    #endstr = 's' if totalStr != '1' else ''
    report.Info(f"Exported {totalStr} sentence(s) to {abbrPath}.")
    
    f_out.close()

    report.Info("Export of " + sourceTextName + " complete.")

    return 1

def convertToSynthesizerFormat(DB, configMap, report):

    targetANAFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_ANA_FILE, report)
    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet
    
    # Verify that the affix file exist.
    if not os.path.exists(affixFile):
        
        report.Error(f'The Catalog Target Affixes module must be run before this module. The {ReadConfig.TARGET_AFFIX_GLOSS_FILE}: {affixFile} does not exist.')
        return None
    
    transferResultsFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RESULTS_FILE, report)
    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False)

    doHermitCrabSynthesis = True if hermitCrabSynthesisYesNo == 'y' else False
    HCmasterFile = None
    
    # Get the master file name
    if doHermitCrabSynthesis:

        HCmasterFile = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_MASTER_FILE, report)

        if not HCmasterFile:

            report.Error(f'Configuration file problem with: {ReadConfig.HERMIT_CRAB_MASTER_FILE}.')
            return  None
    
    errorList = ConvertTextToSTAMPformat.convert_to_STAMP(DB, configMap, targetANAFile, affixFile, transferResultsFile, doHermitCrabSynthesis, HCmasterFile, report)

    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return None
    
    return 1

# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    ## Extract the source text
    report.Blank()
    report.Info('Exporting source text...')
    if not extractSourcText(DB, configMap, report):
        return

    ## Build the bilingual lexicon
    report.Blank()
    report.Info('Building the bilingual lexicon...')
    errorList = ExtractBilingualLexicon.extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=True)

    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return

    ## Run Apertium
    report.Blank()
    report.Info('Running the Apertium transfer engine...')
    if not RunApertium.runApertium(DB, configMap, report):
        return
    
    ## Catalog Target Affixes

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet

    if not outFileVal:
        return
    
    report.Blank()
    report.Info('Cataloging target affixes...')
    errorList = CatalogTargetAffixes.catalog_affixes(DB, configMap, outFileVal, report, useCacheIfAvailable=True)
    
    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return
    
    ## Convert to Synthesizer Format
    report.Blank()
    report.Info('Converting target words to synthesizer format...')
    if not convertToSynthesizerFormat(DB, configMap, report):
        return
    
    ## Synthesize Text
    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=True)

    report.Blank()
    report.Info('Synthesizing target text...')
    if hermitCrabSynthesisYesNo == 'y':

        report.Info('Using HermitCrab for synthesis.')
        if not DoHermitCrabSynthesis.doHermitCrab(DB, report, configMap):
            return
    else:
        report.Info('Using STAMP for synthesis.')
        if not DoStampSynthesis.doStamp(DB, report, configMap):
            return
    
    if FINAL_MODULE_IS_EXPORT_TO_PARATEXT:

        ## Export to Paratext
        report.Blank()
        report.Info('Exporting to Paratext...')
        if not ExportToParatext.doExportToParatext(DB, configMap, report):
            return
    else:
        ## Insert Target Text
        report.Blank()
        report.Info('Inserting text into the target project...')
        if not InsertTargetText.insertTargetText(DB, configMap, report):
            return
    
    report.Blank()
    report.Info('Translation complete.')

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
