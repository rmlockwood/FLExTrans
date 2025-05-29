#
#   TranslateText
#
#   Ron Lockwood
#   SIL International
#   12/31/24
#
#   Version 3.13.1 - 3/20/25 - Ron Lockwood
#    Modularized the main functions to make it easy to call from other modules.
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

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from flextoolslib import *                                                 

import Mixpanel
import DoHermitCrabSynthesis
import DoStampSynthesis
import InsertTargetText
import ExportToParatext
import ExtractBilingualLexicon
import CatalogTargetAffixes
import RunApertium
import ExtractSourceText
import ConvertTextToSTAMPformat
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'TranslateText'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'DoHermitCrabSynthesis', 'DoStampSynthesis', 'InsertTargetText', 'ExportToParatext', 'ExtractBilingualLexicon', 'CatalogTargetAffixes', 
                        'RunApertium', 'ExtractSourceText', 'ConvertTextToSTAMPformat', 'ChapterSelection', 'ParatextChapSelectionDlg', 'ChapterSelection', 'InterlinData', 'TextClasses']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Translate Text",
        FTM_Version    : "3.14",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("TranslateText", "Translate the current source text."),    
        FTM_Help   : "",
        FTM_Description: _translate("TranslateText", 
"""Translate the current source text.""")}

app.quit()
del app

FINAL_MODULE_IS_EXPORT_TO_PARATEXT = True # Otherwise, the last module is Insert Target Text

# The main processing function
def MainFunction(DB, report, modify=True):
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    ## Extract the source text
    report.Blank()
    report.Info(_translate("TranslateText", 'Exporting source text...'))
    if not ExtractSourceText.doExtractSourceText(DB, configMap, report):
        return

    ## Build the bilingual lexicon
    report.Blank()
    report.Info(_translate("TranslateText", 'Building the bilingual lexicon...'))
    errorList = ExtractBilingualLexicon.extract_bilingual_lex(DB, configMap, report, useCacheIfAvailable=True)

    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return

    ## Run Apertium
    report.Blank()
    report.Info(_translate("TranslateText", 'Running the Apertium transfer engine...'))
    if not RunApertium.runApertium(DB, configMap, report):
        return
    
    ## Catalog Target Affixes

    # Build an output path using the system temp directory.
    outFileVal = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) # don't give error yet

    if not outFileVal:
        return
    
    report.Blank()
    report.Info(_translate("TranslateText", 'Cataloging target affixes...'))
    errorList = CatalogTargetAffixes.catalog_affixes(DB, configMap, outFileVal, report, useCacheIfAvailable=True)
    
    # output info, warnings, errors and url links
    if not Utils.processErrorList(errorList, report):
        return
    
    ## Convert to Synthesizer Format
    report.Blank()
    report.Info(_translate("TranslateText", 'Converting target words to synthesizer format...'))
    if not ConvertTextToSTAMPformat.convertToSynthesizerFormat(DB, configMap, report):
        return
    
    ## Synthesize Text
    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=True)

    report.Blank()
    report.Info(_translate("TranslateText", 'Synthesizing target text...'))
    if hermitCrabSynthesisYesNo == 'y':

        report.Info(_translate("TranslateText", 'Using HermitCrab for synthesis.'))
        if not DoHermitCrabSynthesis.doHermitCrab(DB, report, configMap):
            return
    else:
        report.Info(_translate("TranslateText", 'Using STAMP for synthesis.'))
        if not DoStampSynthesis.doStamp(DB, report, configMap):
            return
    
    if FINAL_MODULE_IS_EXPORT_TO_PARATEXT:

        ## Export to Paratext
        report.Blank()
        report.Info(_translate("TranslateText", 'Exporting to Paratext...'))

        # Delete the app so that we can export to Paratext without any issues. Export to Paratext creates a new app.
        app.quit()
        del app

        if not ExportToParatext.doExportToParatext(DB, configMap, report):
            return
        
        # Reload the translations after Export to Paratext
        translators = []
        app = QApplication([])
        Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                               translators, loadBase=False)
    else:
        ## Insert Target Text
        report.Blank()
        report.Info(_translate("TranslateText", 'Inserting text into the target project...'))
        if not InsertTargetText.insertTargetText(DB, configMap, report):
            return
    
    report.Blank()
    report.Info(_translate("TranslateText", 'Translation complete.'))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
