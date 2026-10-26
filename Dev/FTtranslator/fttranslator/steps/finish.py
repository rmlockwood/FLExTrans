"""
Reading the translation and the words that failed along the way.

  * source_text-aper.txt: ^word<UNK>$ is a word that had no analysis
  * target_text-aper.txt: ^@lemma...$ is a word with no bilingual lexicon entry
  * bilingual.dix: <e><i>lemma…</i></e> is a source sense with no link to a
    target sense; it passes through untranslated
  * the synthesis output: @word is an untranslated word passed through;
    STAMP writes %n%form% for a word it could not synthesize
"""

import importlib
import os
import re

from ..pipeline import Step

LU = re.compile(r"\^(.*?)\$")
STAMP_FAILURE = re.compile(r"%\d+%([^%]*)%")
IDENTITY = re.compile(r"<e[^>]*>\s*<i>([^<]*)")


def _read(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _lemma(unit):
    return unit.lstrip("@*#").split("<", 1)[0]


def _unique(items):
    return list(dict.fromkeys(items))


def collect_output(ctx):
    ReadConfig = importlib.import_module("ReadConfig")
    TextInOutUtils = importlib.import_module("TextInOutUtils")

    source = _read(ctx.config(ReadConfig.ANALYZED_TEXT_FILE, required=False)) or ""
    transfer = _read(ctx.config(ReadConfig.TRANSFER_RESULTS_FILE, required=False)) or ""
    bilingual = _read(ctx.config(ReadConfig.BILINGUAL_DICTIONARY_FILE, required=False)) or ""
    unlinked = set(IDENTITY.findall(bilingual))
    ctx.result.untranslated = _unique(
        [_lemma(u) for u in LU.findall(transfer) if u.startswith("@")] +
        [_lemma(u) for u in LU.findall(source) if _lemma(u) in unlinked])

    synth_file = ctx.config(ReadConfig.TARGET_SYNTHESIS_FILE)
    text = _read(synth_file)
    if text is None:
        ctx.report.Error(f"No synthesis output at {synth_file}")
        return False
    ctx.result.unsynthesized = _unique(STAMP_FAILURE.findall(text))
    # The same user-defined fix-up rules InsertTargetText applies.
    text = TextInOutUtils.applyTextOutRulesFromConfig(text, ctx.config_map, ctx.report, "Text Out")
    if text is None:
        return False
    ctx.result.translation = text.strip()
    return True


STEPS = [Step("Collect Output", collect_output, "ftt")]
