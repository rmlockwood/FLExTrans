#
#   fttranslator/transferexport
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Exports the files the Apertium tools read in FLExTrans' Run Apertium step, for transfer without FieldWorks (transfer.py).
#
#   OVERVIEW (AI generated, then edited)
#
#   FLExTrans' transfer step (Run Apertium) doesn't hand the Apertium tools the user's files as they are. The bilingual lexicon is made by Build Bilingual Lexicon from both projects, and the
#   rules file is cut down and escaped (stripRulesFile()), and both get the same substitutions for characters that are illegal in Apertium symbols (fixProblemChars() and subProbSymbols()). This
#   file makes those files with Run Apertium's and Build Bilingual Lexicon's own functions and puts them in the bundle's apertium folder, so transfer.py only has to compile and run them.
#
#   WHAT IT WRITES
#
#   In <bundle>\apertium: bilingual.dix (after the symbol substitutions), tr.t1x and, for advanced (three-phase) transfer, tr.t2x and tr.t3x - each exactly as Run Apertium leaves it in the Build
#   folder before it runs make. exportTransfer() returns the list of rules files for the manifest.
#
#   TRAPS
#
#    - Build Bilingual Lexicon reads the target project, so it must be closed in FLEx. It is run with its cache allowed, so an up-to-date bilingual.dix is reused rather than rebuilt.
#    - Run Apertium substitutes problem symbols in tr.t1x only, not in tr.t2x or tr.t3x; this does the same.
#    - The work project's own Build\bilingual.dix is copied, never changed.
#
#   CODE STRUCTURE
#
#   exportTransfer() does it all; bundle.exportBundle() calls it.
#

import os
import shutil

APERTIUM_DIR = "apertium"
BILINGUAL_FILE = "bilingual.dix"

def exportTransfer(project, configMap, outDir, report):
    '''Write the Apertium inputs into outDir\\apertium. Returns the names of the rules files written (tr.t1x first), or None if something is missing (reported).'''

    import ExtractBilingualLexicon  # FLExTrans modules, only importable after env.bootstrap()
    import ReadConfig
    import RunApertium
    import Utils

    from .translator import flexlibsView

    apertiumDir = outDir / APERTIUM_DIR
    apertiumDir.mkdir(parents=True, exist_ok=True)

    # The bilingual lexicon, rebuilt only if the projects have changed since the last build
    errorList = ExtractBilingualLexicon.extract_bilingual_lex(flexlibsView(project), configMap, report, useCacheIfAvailable=True)

    if not Utils.processErrorList(errorList, report):

        return None

    dictionaryPath = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)

    if not dictionaryPath or not os.path.exists(dictionaryPath):

        report.Error("There is no bilingual lexicon to export.")
        return None

    bundleDictionary = apertiumDir / BILINGUAL_FILE
    shutil.copyfile(dictionaryPath, bundleDictionary)

    # The rules files, cut down and escaped as Run Apertium does
    rulesFiles = []

    for setting, strippedName in ((ReadConfig.TRANSFER_RULES_FILE, RunApertium.STRIPPED_RULES), (ReadConfig.TRANSFER_RULES_FILE2, RunApertium.STRIPPED_RULES2), (ReadConfig.TRANSFER_RULES_FILE3, RunApertium.STRIPPED_RULES3)):

        rulesPath = ReadConfig.getConfigVal(configMap, setting, report, giveError=False)

        if not rulesPath:

            continue

        if not os.path.exists(rulesPath) or RunApertium.stripRulesFile(report, str(apertiumDir), rulesPath, strippedName) == True:

            report.Error(f"The transfer rules file {rulesPath} could not be prepared.")
            return None

        rulesFiles.append(strippedName)

    if not rulesFiles or rulesFiles[0] != RunApertium.STRIPPED_RULES:

        report.Error("There is no transfer rules file to export.")
        return None

    # The symbol substitutions, in the lexicon and the first rules file; fixProblemChars() leaves a backup copy, which isn't needed here
    subPairs = RunApertium.fixProblemChars(str(bundleDictionary))
    os.remove(str(bundleDictionary) + ".before_fix")
    RunApertium.subProbSymbols(str(apertiumDir), RunApertium.STRIPPED_RULES, subPairs)

    return rulesFiles
