#
#   fttranslator/steps/flextrans
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.1 - 10/27/26 - Ron Lockwood
#    Delete the previous transfer output before Run Apertium, so make can't skip the transfer when runs finish within the same second.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The FLExTrans drafting steps, and running any other FlexTools module from the collection.
#
#   OVERVIEW (AI generated, then edited)
#
#   The middle of the pipeline is the work project's collection. This file supplies the steps for its entries in two ways.
#
#   BUILT-IN STEPS
#
#   The seven standard drafting modules are run by calling each module's core function directly, the same calls FLExTrans' TranslateText.py makes. That skips the FlexTools-only parts of each
#   module's MainFunction: loading Qt translators, logging to Mixpanel and re-reading the configuration. builtins() keys each step both by its module file stem and by its FTM_Name, lowercased,
#   because those are the two ways a collection .ini can name a module (see pipeline.entryKey()). Insert Target Text stays in the collection but skips itself unless --insert was given.
#
#   MAKE AND FAST RUNS
#
#   Run Apertium runs make, which skips the transfer when target_text-aper.txt is not older than the source file. File times only go to the second, so a run that finishes within the same second
#   as the one before (easy once the projects stay open, as in the interactive command) would have its transfer skipped and the previous run's output synthesized again. runApertium() therefore deletes the
#   transfer output, and the intermediate target_text0-2.txt files of Makefile.advanced, before running make. make still reuses bilingual.bin and the compiled rules when they are current.
#
#   CUSTOM MODULES
#
#   Any other collection entry is loaded as a FlexTools module and run through its FlexToolsModule.Run(), so a team adds custom code the same way as in FlexTools. modulePath() resolves the entry
#   as FlexTools does - a path relative to the Modules folder, or '<subfolder>.<FTM_Name>' - and also accepts a path relative to the work project's Config folder (or an absolute one), so a
#   profile can carry its own modules. A module that declares FTM_ModifiesDB runs inside a flexicon UndoableOperation, since the source project is open undoable and writes need a unit of work.
#
#   IMPORT ORDER
#
#   FLExTrans modules can only be imported after env.bootstrap(), so every FLExTrans module is imported by name when a step runs (_lib()), never at the top of this file.
#
#   CODE STRUCTURE
#
#   _lib() imports a FLExTrans module by name. The seven built-in step functions follow in pipeline order, then _DRAFTING (stem, name, function) and builtins(), which Translator.steps() hands to
#   pipeline.build(). Last come the custom-module functions: _findByName() and modulePath() find the file, and loadFlexToolsModule() loads it and wraps it in a Step.
#

import importlib
import importlib.util
import os
import re

from ..pipeline import Step
from . import ingest

def _lib(name):
    '''Import a FLExTrans module by name. Done when a step runs, since FLExTrans can only be imported after env.bootstrap().'''

    return importlib.import_module(name)

def extractSourceText(ctx):

    ok = _lib("ExtractSourceText").doExtractSourceText(ctx.ftDb, ctx.configMap, ctx.report)

    # The extracted file is all the rest of the pipeline needs from the source analyses, so the guessed approvals can go now
    ingest.releaseApprovals(ctx)

    return bool(ok)

def buildBilingualLexicon(ctx):

    errorList = _lib("ExtractBilingualLexicon").extract_bilingual_lex(ctx.ftDb, ctx.configMap, ctx.report, useCacheIfAvailable=True)
    return bool(_lib("Utils").processErrorList(errorList, ctx.report))

def runApertium(ctx):

    ReadConfig = _lib("ReadConfig")
    FTPaths = _lib("FTPaths")

    # Delete the transfer output, and the advanced makefile's intermediate files, so make has to run the transfer again. See MAKE AND FAST RUNS above.
    staleFiles = [ctx.config(ReadConfig.TRANSFER_RESULTS_FILE, required=False)] + [os.path.join(FTPaths.BUILD_DIR, f"target_text{stage}.txt") for stage in range(3)]

    for path in staleFiles:

        if path and os.path.isfile(path):

            os.remove(path)

    return bool(_lib("RunApertium").runApertium(ctx.ftDb, ctx.configMap, ctx.report))

def catalogTargetAffixes(ctx):

    ReadConfig = _lib("ReadConfig")
    outFile = ctx.config(ReadConfig.TARGET_AFFIX_GLOSS_FILE)

    if not outFile:

        return False

    errorList = _lib("CatalogTargetAffixes").catalog_affixes(ctx.ftDb, ctx.configMap, outFile, ctx.report, useCacheIfAvailable=True)
    return bool(_lib("Utils").processErrorList(errorList, ctx.report))

def convertToSynthesizerFormat(ctx):

    return bool(_lib("ConvertTextToSTAMPformat").convertToSynthesizerFormat(ctx.ftDb, ctx.configMap, ctx.report))

def synthesizeText(ctx):

    ReadConfig = _lib("ReadConfig")

    # The same choice DoSynthesis makes: HermitCrab synthesis if the setting is on, otherwise STAMP
    if ctx.config(ReadConfig.HERMIT_CRAB_SYNTHESIS) == "y":

        return bool(_lib("DoHermitCrabSynthesis").doHermitCrab(ctx.ftDb, ctx.report, ctx.configMap))

    return bool(_lib("DoStampSynthesis").doStamp(ctx.ftDb, ctx.report, ctx.configMap))

def insertTargetText(ctx):

    if not ctx.options.insert:

        ctx.report.Info("Not inserting into the target project (use --insert).")
        return True

    ReadConfig = _lib("ReadConfig")
    insert = _lib("InsertTargetText").insertTargetText

    # One-project mode writes into the source project, which needs a unit of work
    if ctx.config(ReadConfig.TWO_PROJECT_MODE, required=False) == "n":

        with ctx.db.UndoableOperation("FTtranslator: insert target text"):

            return bool(insert(ctx.ftDb, ctx.configMap, ctx.report))

    return bool(insert(ctx.ftDb, ctx.configMap, ctx.report))

# The standard drafting modules: file stem, FTM_Name and the step function. Keyed by both (lowercased) in builtins(), the two ways a collection .ini can name a module.
_DRAFTING = [
    ("ExtractSourceText", "Extract Source Text", extractSourceText),
    ("ExtractBilingualLexicon", "Build Bilingual Lexicon", buildBilingualLexicon),
    ("RunApertium", "Run Apertium", runApertium),
    ("CatalogTargetAffixes", "Catalog Target Affixes", catalogTargetAffixes),
    ("ConvertTextToSTAMPformat", "Convert Text to Synthesizer Format", convertToSynthesizerFormat),
    ("DoSynthesis", "Synthesize Text", synthesizeText),
    ("InsertTargetText", "Insert Target Text", insertTargetText),
]

def builtins():
    '''Return the built-in steps, keyed by module file stem and by FTM_Name, both lowercased.'''

    table = {}

    for stem, name, func in _DRAFTING:

        step = Step(name, func, "builtin", f"FLExTrans\\{stem}.py")
        table[stem.lower()] = table[name.lower()] = step

    return table

def _findByName(folder, name):
    '''Return the module file in folder whose docs give it the FTM_Name name, or None. The name may be wrapped in _translate(), as FLExTrans modules do.'''

    pattern = re.compile(r"FTM_Name\s*:\s*(?:_translate\([^,]+,\s*)?[\"']" + re.escape(name) + r"[\"']")

    for fileName in sorted(os.listdir(folder)):

        if fileName.endswith(".py") and not fileName.startswith("__"):

            path = os.path.join(folder, fileName)

            with open(path, encoding="utf-8", errors="replace") as moduleFile:

                if pattern.search(moduleFile.read()):

                    return path

    return None

def modulePath(env, entry):
    '''Resolve a collection entry to a module file, or None. See CUSTOM MODULES above for the forms an entry can take.'''

    normalized = entry.replace("/", "\\")

    # A path: relative to the Modules folder, then to the work project's Config folder. os.path.join() keeps an absolute path as it is.
    if normalized.lower().endswith(".py"):

        for baseDir in (env.modulesRoot, env.configDir):

            path = os.path.join(baseDir, *normalized.split("\\"))

            if os.path.exists(path):

                return path

        return None

    # '<subfolder>.<FTM_Name>'
    subfolder, _, name = normalized.partition(".")
    folder = os.path.join(env.modulesRoot, subfolder)

    return _findByName(folder, name) if os.path.isdir(folder) else None

def loadFlexToolsModule(env, entry):
    '''Load the FlexTools module a collection entry names and return a Step that runs it.'''

    path = modulePath(env, entry)

    if not path:

        raise SystemExit(f"Collection entry '{entry}' is not a module under {env.modulesRoot}")

    # Load it under a name of its own, so it can't clash with a FLExTrans module of the same file name
    spec = importlib.util.spec_from_file_location("ftt_custom_" + re.sub(r"\W", "_", os.path.basename(path)[:-3]), path)

    if spec is None or spec.loader is None:

        raise SystemExit(f"'{path}' could not be loaded as a Python module")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    flexToolsModule = getattr(module, "FlexToolsModule", None)

    if flexToolsModule is None:

        raise SystemExit(f"'{path}' has no FlexToolsModule")

    from flextoolslib import FTM_Name, FTM_ModifiesDB

    modifiesDb = bool(flexToolsModule.docs.get(FTM_ModifiesDB))

    def runModule(ctx):

        # A module that writes needs a unit of work, since the source project is open undoable
        if modifiesDb:

            with ctx.db.UndoableOperation(f"FTtranslator: {flexToolsModule.docs[FTM_Name]}"):

                flexToolsModule.Run(ctx.ftDb, ctx.report, True)
        else:
            flexToolsModule.Run(ctx.ftDb, ctx.report, False)

        return True

    return Step(flexToolsModule.docs[FTM_Name], runModule, "flextools", entry)
