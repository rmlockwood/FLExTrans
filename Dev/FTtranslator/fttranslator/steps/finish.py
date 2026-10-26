#
#   fttranslator/steps/finish
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The last step: read the translation and find the words that failed along the way.
#
#   OVERVIEW (AI generated, then edited)
#
#   Collect Output is the last step of every run. It reads the synthesis output, applies the user's Text Out rules (the same fix-ups Insert Target Text applies), and puts the result in the run
#   result as the translation. It also reads the files the earlier steps left in the Build folder to list the words that failed, so the user can see what to fix in FLEx.
#
#   WHAT EACH FILE SHOWS
#
#    - source_text-aper.txt (the analyzed text): ^word<UNK>$ is a word that had no analysis.
#    - target_text-aper.txt (the transfer results): ^@lemma...$ is a word with no bilingual lexicon entry.
#    - bilingual.dix: <e><i>lemma...</i></e> is a source sense with no link to a target sense. It is an identity entry, so the word passes through untranslated without an @ marker, and has to be
#      found here rather than in the transfer results.
#    - The synthesis output: STAMP writes %n%form% for a word it could not synthesize. HermitCrab synthesis has its own markers, which aren't detected yet.
#
#   FLExTrans writes these files in NFD, so the words found here are NFD too.
#
#   CODE STRUCTURE
#
#   The patterns come first, then the small helpers _read(), _lemma() and _unique(), then collectOutput() itself. STEPS lists the step for Translator.steps().
#

import importlib
import os
import re

from ..pipeline import Step

# A lexical unit in an Apertium stream (^...$), a STAMP synthesis failure (%n%form%), and an identity entry in bilingual.dix (<e><i>lemma...)
LEXICAL_UNIT = re.compile(r"\^(.*?)\$")
STAMP_FAILURE = re.compile(r"%\d+%([^%]*)%")
IDENTITY_ENTRY = re.compile(r"<e[^>]*>\s*<i>([^<]*)")

def _read(path):
    '''Return the contents of a UTF-8 file, or None if there is no path or no file.'''

    if not path or not os.path.exists(path):

        return None

    with open(path, encoding="utf-8") as inputFile:

        return inputFile.read()

def _lemma(unit):
    '''The lemma of a lexical unit, without the @, * or # marker and the tags.'''

    return unit.lstrip("@*#").split("<", 1)[0]

def _unique(items):
    '''The items without repeats, in their first-seen order.'''

    return list(dict.fromkeys(items))

def collectOutput(ctx):
    '''Set the run result's translation from the synthesis output, and list the untranslated and unsynthesized words. See WHAT EACH FILE SHOWS above.'''

    ReadConfig = importlib.import_module("ReadConfig")
    TextInOutUtils = importlib.import_module("TextInOutUtils")

    # Untranslated words: marked with @ in the transfer results, or passed through by an identity entry in the bilingual lexicon
    sourceText = _read(ctx.config(ReadConfig.ANALYZED_TEXT_FILE, required=False)) or ""
    transferText = _read(ctx.config(ReadConfig.TRANSFER_RESULTS_FILE, required=False)) or ""
    bilingualText = _read(ctx.config(ReadConfig.BILINGUAL_DICTIONARY_FILE, required=False)) or ""
    unlinked = set(IDENTITY_ENTRY.findall(bilingualText))

    noEntry = [_lemma(unit) for unit in LEXICAL_UNIT.findall(transferText) if unit.startswith("@")]
    noLink = [_lemma(unit) for unit in LEXICAL_UNIT.findall(sourceText) if _lemma(unit) in unlinked]
    ctx.result.untranslated = _unique(noEntry + noLink)

    synthesisFile = ctx.config(ReadConfig.TARGET_SYNTHESIS_FILE)
    text = _read(synthesisFile)

    if text is None:

        ctx.report.Error(f"No synthesis output at {synthesisFile}")
        return False

    ctx.result.unsynthesized = _unique(STAMP_FAILURE.findall(text))

    # The same user-defined fix-up rules InsertTargetText applies
    text = TextInOutUtils.applyTextOutRulesFromConfig(text, ctx.configMap, ctx.report, "Text Out")

    if text is None:

        return False

    ctx.result.translation = text.strip()
    return True

STEPS = [Step("Collect Output", collectOutput, "ftt")]
