#
#   fttranslator/synthexport
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Exports what FLExTrans' HermitCrab synthesis steps read from the target project, for synthesis without FieldWorks (synthesis.py).
#
#   OVERVIEW (AI generated, then edited)
#
#   After Run Apertium, FLExTrans' drafting collection runs three steps that read the target project: Catalog Target Affixes writes the target affix gloss list, Convert Text to Synthesizer Format
#   (ConvertTextToSTAMPformat.py) finds the target complex forms and irregularly inflected variants through its ConversionData class, and Synthesize Text (DoHermitCrabSynthesis.py) generates the
#   target HermitCrab.config that HCSynthByGloss synthesizes from. Each of them can reuse a cached result, and the cached results are plain files. This file makes those files current with
#   FLExTrans' own functions - the same calls, with the cache allowed, that a desktop run makes - and copies them into the bundle's synthesis folder, so synthesis.py only has to read them.
#
#   WHAT IT WRITES
#
#   In <bundle>\synthesis:
#    - target_affix_glosses.txt: the Target Affix Gloss List File, one gloss|morphtype per line, made current with CatalogTargetAffixes.catalog_affixes().
#    - conversion_to_STAMP_cache2.txt: ConversionData's cache of the target complex forms and variants (in the Target Lexicon Files Folder it is <target project>_conversion_to_STAMP_cache2.txt).
#      ConversionData() itself decides whether its cache is current, loads or rebuilds it, and with CacheData=y saves it; the saved file is then copied. With CacheData=n ConversionData doesn't save,
#      so its saveToCache() is pointed at the bundle instead, which writes the same data in the same format without touching the work project.
#    - HermitCrab.config: the target project's HermitCrab configuration, made current with DoHermitCrabSynthesis.extractHermitCrabConfig() and copied.
#   exportSynthesis() returns the manifest's files entry for the folder, the FlexTrans.config values the synthesis reads (the target complex-form type lists and CleanUpUnknownTargetWords; the
#   SentencePunctuation value is already in the manifest for Extract Source Text), and the interface language code FLExTrans passes to HCSynthByGloss (it chooses the language of HC's messages,
#   which end up in the synthesized text of a word that fails).
#
#   TRAPS
#
#    - The order matters. ConversionData counts its cache as out of date only when the affix gloss file is newer than it, so the affix file is made current first, as in the drafting collection.
#    - Catalog Target Affixes, ConversionData (when its cache is out of date) and extractHermitCrabConfig() all open the target project, so it must be closed in FLEx.
#    - Two error paths in ConversionData.__init__ return a value, which raises a TypeError; that is caught here and the error list reported.
#    - The work project's own files are copied, never changed. Only One project mode and STAMP synthesis are refused: synthesis.py ports the two project HermitCrab path only.
#
#   CODE STRUCTURE
#
#   exportSynthesis() does it all, in the order of the drafting collection; bundle.exportBundle() calls it. _complexFormTypes() reads and checks a complex-form type list as convert_to_STAMP() does.
#

import os
import shutil

SYNTHESIS_DIR = "synthesis"
AFFIX_GLOSS_FILE = "target_affix_glosses.txt"
CONVERSION_CACHE_FILE = "conversion_to_STAMP_cache2.txt"
HERMIT_CRAB_CONFIG_FILE = "HermitCrab.config"

def exportSynthesis(project, configMap, outDir, report):
    '''Write the synthesis inputs into outDir\\synthesis. Returns (files entry, config values, interface language) for the manifest, or None if something is missing (reported).'''

    import CatalogTargetAffixes  # FLExTrans modules, only importable after env.bootstrap()
    import ConvertTextToSTAMPformat
    import DoHermitCrabSynthesis
    import ReadConfig
    import Utils

    from .translator import flexlibsView

    # Only the two project HermitCrab path is ported (see TRAPS above)
    if ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False) != "y":

        report.Error(f"The bundle only supports HermitCrab synthesis. Set {ReadConfig.HERMIT_CRAB_SYNTHESIS} to y to export one.")
        return None

    if ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) == "n":

        report.Error("The bundle doesn't support One project mode synthesis.")
        return None

    synthesisDir = outDir / SYNTHESIS_DIR
    synthesisDir.mkdir(parents=True, exist_ok=True)
    flexDb = flexlibsView(project)

    # 1. The target affix gloss list, as Catalog Target Affixes makes it (rewritten only if the target project changed). The old setting name is tried as convertToSynthesizerFormat() does.
    affixFile = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_AFFIX_GLOSS_FILE, report, giveError=False) or ReadConfig.getConfigVal(configMap, "TargetPrefixGlossListFile", report)

    if not affixFile:

        return None

    errorList = CatalogTargetAffixes.catalog_affixes(flexDb, configMap, affixFile, report, useCacheIfAvailable=True)

    if not Utils.processErrorList(errorList, report) or not os.path.exists(affixFile):

        report.Error("The target affix gloss list could not be made.")
        return None

    shutil.copyfile(affixFile, synthesisDir / AFFIX_GLOSS_FILE)

    # 2. The complex forms and variants. The type map is built as convert_to_STAMP() builds it, since ConversionData only looks for these types when it rebuilds its cache.
    complexForms1st = _complexFormTypes(configMap, ReadConfig.TARGET_FORMS_INFLECTION_1ST, report)
    complexForms2nd = _complexFormTypes(configMap, ReadConfig.TARGET_FORMS_INFLECTION_2ND, report)

    if complexForms1st is None or complexForms2nd is None:

        return None

    complexFormTypeMap = {}

    for cmplxType in complexForms1st:

        complexFormTypeMap[cmplxType] = 0  # 0 - inflection on first root

    for cmplxType in complexForms2nd:

        complexFormTypeMap[cmplxType] = 1  # 1 - inflection on last root

    errorList = []

    # ConversionData does all its work in __init__: load the cache if it is current, otherwise read the target project and (with CacheData=y) save the cache
    try:
        convData = ConvertTextToSTAMPformat.ConversionData(errorList, configMap, report, complexFormTypeMap, flexDb)

    # Two of its error paths 'return errorList' from __init__, which raises a TypeError after adding the error (see TRAPS above)
    except TypeError:

        Utils.processErrorList(errorList, report)
        return None

    if convData.haveError or not Utils.processErrorList(errorList, report):

        return None

    bundleCache = synthesisDir / CONVERSION_CACHE_FILE

    # With CacheData=y the cache file ConversionData uses is current now; copy it
    if ReadConfig.getConfigVal(configMap, ReadConfig.CACHE_DATA, report) == "y":

        shutil.copyfile(convData.getCacheFilePath(), bundleCache)
    else:
        # Without the cache, have ConversionData write its data into the bundle instead of into the work project. getCacheFilePath() puts the target project's name in front of the file name.
        convData.lexFolder = str(synthesisDir)
        convData.saveToCache()
        os.replace(convData.getCacheFilePath(), bundleCache)

    # 3. The target HermitCrab.config, regenerated only if the target project changed since it was made
    configPath = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_CONFIG_FILE, report)

    if not configPath:

        return None

    errorList = DoHermitCrabSynthesis.extractHermitCrabConfig(flexDb, configMap, configPath, report, useCacheIfAvailable=True)

    if not Utils.processErrorList(errorList, report) or not os.path.exists(configPath):

        report.Error("The target HermitCrab configuration could not be made.")
        return None

    shutil.copyfile(configPath, synthesisDir / HERMIT_CRAB_CONFIG_FILE)

    # The settings synthesis.py reads; the type lists are as checked above, and CleanUpUnknownTargetWords is kept raw, since synthesizeWithHermitCrab() reads its first letter
    cleanUp = ReadConfig.getConfigVal(configMap, ReadConfig.CLEANUP_UNKNOWN_WORDS, report)

    if not cleanUp:

        return None

    files = {"dir": SYNTHESIS_DIR, "affixGlosses": AFFIX_GLOSS_FILE, "conversionCache": CONVERSION_CACHE_FILE, "hermitCrabConfig": HERMIT_CRAB_CONFIG_FILE}
    config = {ReadConfig.TARGET_FORMS_INFLECTION_1ST: complexForms1st, ReadConfig.TARGET_FORMS_INFLECTION_2ND: complexForms2nd, ReadConfig.CLEANUP_UNKNOWN_WORDS: cleanUp}

    return files, config, Utils.getInterfaceLangCode()

def _complexFormTypes(configMap, setting, report):
    '''A target complex-form type list, checked as convert_to_STAMP() checks it: a value that isn't a list is an error (None); no value is an empty list.'''

    import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

    value = ReadConfig.getConfigVal(configMap, setting, report)

    if value and not ReadConfig.configValIsList(configMap, setting, report):

        report.Error(f"Configuration file problem with: {setting}.")
        return None

    return list(value) if value else []
