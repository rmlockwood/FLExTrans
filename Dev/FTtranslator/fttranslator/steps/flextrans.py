"""
The FLExTrans drafting steps, and running any other FlexTools module.

The built-in steps call each module's core function the way
FLExTrans' TranslateText.py does, skipping the FlexTools-only parts of
MainFunction (Qt translators, Mixpanel, re-reading the configuration).
They are imported lazily because FLExTrans modules can only be imported
after env.bootstrap().
"""

import importlib.util
import os
import re

from ..pipeline import Step
from . import ingest


def _lib(name):
    return importlib.import_module(name)


def extract_source_text(ctx):
    ok = _lib("ExtractSourceText").doExtractSourceText(ctx.ft_db, ctx.config_map, ctx.report)
    # The extracted file is all the rest of the pipeline needs from the source analyses.
    ingest.release_approvals(ctx)
    return bool(ok)


def build_bilingual_lexicon(ctx):
    errors = _lib("ExtractBilingualLexicon").extract_bilingual_lex(
        ctx.ft_db, ctx.config_map, ctx.report, useCacheIfAvailable=True)
    return bool(_lib("Utils").processErrorList(errors, ctx.report))


def run_apertium(ctx):
    return bool(_lib("RunApertium").runApertium(ctx.ft_db, ctx.config_map, ctx.report))


def catalog_target_affixes(ctx):
    ReadConfig = _lib("ReadConfig")
    out_file = ctx.config(ReadConfig.TARGET_AFFIX_GLOSS_FILE)
    if not out_file:
        return False
    errors = _lib("CatalogTargetAffixes").catalog_affixes(
        ctx.ft_db, ctx.config_map, out_file, ctx.report, useCacheIfAvailable=True)
    return bool(_lib("Utils").processErrorList(errors, ctx.report))


def convert_to_synthesizer_format(ctx):
    return bool(_lib("ConvertTextToSTAMPformat").convertToSynthesizerFormat(
        ctx.ft_db, ctx.config_map, ctx.report))


def synthesize_text(ctx):
    ReadConfig = _lib("ReadConfig")
    if ctx.config(ReadConfig.HERMIT_CRAB_SYNTHESIS) == "y":
        return bool(_lib("DoHermitCrabSynthesis").doHermitCrab(ctx.ft_db, ctx.report, ctx.config_map))
    return bool(_lib("DoStampSynthesis").doStamp(ctx.ft_db, ctx.report, ctx.config_map))


def insert_target_text(ctx):
    if not ctx.options.insert:
        ctx.report.Info("Not inserting into the target project (use --insert).")
        return True
    ReadConfig = _lib("ReadConfig")
    insert = _lib("InsertTargetText").insertTargetText
    if ctx.config(ReadConfig.TWO_PROJECT_MODE, required=False) == "n":
        # One-project mode writes into the source project, which needs a unit of work.
        with ctx.db.UndoableOperation("FTtranslator: insert target text"):
            return bool(insert(ctx.ft_db, ctx.config_map, ctx.report))
    return bool(insert(ctx.ft_db, ctx.config_map, ctx.report))


# Keyed by module file stem and by FTM_Name (lowercased), the two ways a
# collection .ini can name a module.
_DRAFTING = [
    ("ExtractSourceText", "Extract Source Text", extract_source_text),
    ("ExtractBilingualLexicon", "Build Bilingual Lexicon", build_bilingual_lexicon),
    ("RunApertium", "Run Apertium", run_apertium),
    ("CatalogTargetAffixes", "Catalog Target Affixes", catalog_target_affixes),
    ("ConvertTextToSTAMPformat", "Convert Text to Synthesizer Format", convert_to_synthesizer_format),
    ("DoSynthesis", "Synthesize Text", synthesize_text),
    ("InsertTargetText", "Insert Target Text", insert_target_text),
]


def builtins():
    table = {}
    for stem, name, func in _DRAFTING:
        step = Step(name, func, "builtin", f"FLExTrans\\{stem}.py")
        table[stem.lower()] = table[name.lower()] = step
    return table


# ---------------------------------------------------------------- custom modules

def _find_by_name(folder, name):
    """A module file in `folder` whose docs give it FTM_Name `name`."""
    pattern = re.compile(r"FTM_Name\s*:\s*(?:_translate\([^,]+,\s*)?[\"']" + re.escape(name) + r"[\"']")
    for fname in sorted(os.listdir(folder)):
        if fname.endswith(".py") and not fname.startswith("__"):
            path = os.path.join(folder, fname)
            with open(path, encoding="utf-8", errors="replace") as f:
                if pattern.search(f.read()):
                    return path
    return None


def module_path(env, entry):
    """Resolve a collection entry the way FlexTools does: a path relative to
    the Modules folder, or '<subfolder>.<FTM_Name>'. A path may also be
    relative to the work project's Config folder (or absolute), so a
    profile can carry its own modules."""
    e = entry.replace("/", "\\")
    if e.lower().endswith(".py"):
        for base in (env.modules_root, env.config_dir):
            path = os.path.join(base, *e.split("\\"))
            if os.path.exists(path):
                return path
        return None
    sub, _, name = e.partition(".")
    folder = os.path.join(env.modules_root, sub)
    return _find_by_name(folder, name) if os.path.isdir(folder) else None


def load_flextools_module(env, entry):
    path = module_path(env, entry)
    if not path:
        raise SystemExit(f"Collection entry '{entry}' is not a module under {env.modules_root}")
    spec = importlib.util.spec_from_file_location(
        "ftt_custom_" + re.sub(r"\W", "_", os.path.basename(path)[:-3]), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ftm = getattr(module, "FlexToolsModule", None)
    if ftm is None:
        raise SystemExit(f"'{path}' has no FlexToolsModule")
    from flextoolslib import FTM_Name, FTM_ModifiesDB
    modifies = bool(ftm.docs.get(FTM_ModifiesDB))

    def run(ctx):
        if modifies:
            with ctx.db.UndoableOperation(f"FTtranslator: {ftm.docs[FTM_Name]}"):
                ftm.Run(ctx.ft_db, ctx.report, True)
        else:
            ftm.Run(ctx.ft_db, ctx.report, False)
        return True

    return Step(ftm.docs[FTM_Name], run, "flextools", entry)
