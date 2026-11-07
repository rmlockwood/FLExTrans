#
#   offline/tests/make_stages
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Records every step of the Python offline translator on a bundle's texts, for ftoffline check.
#
#   OVERVIEW (AI generated, then edited)
#
#   FTOffline is a C# port of the Python offline translator (fttranslator/offlineserver.py and the steps it runs), and the Python is the reference. This runs the Python's OfflineTranslator over
#   texts, with each step wrapped so its result is saved, and writes one JSON per text; ftoffline check <bundle> <folder> then runs the C# translator over the same texts and compares every
#   step, so a difference points at the step that made it.
#
#   WHAT IT SAVES
#
#   input (the text), tokens (the text dump after Import Text), parses (each word given to hcparse with its result), guessed (the text dump after Approve Guesses), source and extractMessages
#   (Extract Source Text), target (Run Apertium), master, parsesFile and surface (the synthesis work files as Python's text mode reads them), synthesized and synthMessages (Synthesize Text), and
#   result (the run record without its title, timings and total time). A text the translator fails on (Mato-Uma's rules stop apertium-transfer on 12 texts) gets error and the steps before it.
#
#   THE TEXTS
#
#   Text files, and golden folders (a work project's Output\ftt_golden, from golden.py): each NNN.text.json there is one text, its paragraphs joined with newlines. Older golden files have no
#   paragraphs, so those are rebuilt from the occurrences' offsets, with spaces in the gaps.
#
#   KEEP THE OUTPUT OUT OF THE REPO
#
#   The stages hold the project's texts and analyses, and the repository is public: write them somewhere else.
#
#   TRAPS
#
#    - The Python translator must be the one the C# is compared with: the run uses hcparse, FTApertium and HCSynthByGloss.dll from their Release builds in this repo (build them first), and
#      always cleans up unknown target words, as the server does.
#    - Parsing Mato-Uma's texts takes about half a minute each in the Python translator (hcparse is fed one word at a time), so 130 texts take an hour.
#
#   CODE STRUCTURE
#
#   readTexts() gathers the texts; the recording*() wrappers replace the translator's steps for the run and save each result into stages; main() runs the texts.
#

import argparse
import copy
import json
import sys
from pathlib import Path

FTT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FTT))

from fttranslator import analysisguess, bundleextract, offlineserver

HCPARSE = ["dotnet", str(FTT / "hcparse" / "bin" / "Release" / "net8.0" / "HCParse.dll")]
HCSYNTH_DLL = str(FTT / "hcsynth" / "bin" / "Release" / "net8.0" / "HCSynthByGloss.dll")
APERTIUM_DLL = str(FTT / "apertium" / "bin" / "Release" / "net8.0" / "FTtranslator.Apertium.dll")

def readTexts(paths):
    '''(name, text) for each text file, and for each NNN.text.json in a golden folder. See THE TEXTS above.'''

    texts = []

    for arg in paths:

        path = Path(arg)

        if not path.is_dir():

            texts.append((path.stem, path.read_text(encoding="utf-8-sig")))
            continue

        for textJson in sorted(path.glob("*.text.json")):

            dump = json.loads(textJson.read_text(encoding="utf-8"))
            paragraphs = dump.get("paragraphs")

            # Older dumps have no paragraphs: rebuild them from the occurrences' offsets
            if paragraphs is None:

                rebuilt = {}

                for occurrence in dump["occurrences"]:

                    chars = rebuilt.setdefault(occurrence["para"], [])
                    piece = occurrence.get("punct") or occurrence.get("baseline") or occurrence.get("surface") or ""

                    while len(chars) < occurrence["beg"]:

                        chars.append(" ")

                    chars[occurrence["beg"]:occurrence["beg"] + len(piece)] = list(piece)

                paragraphs = ["".join(rebuilt[key]) for key in sorted(rebuilt)]

            texts.append((textJson.name.split(".")[0], "\n".join(paragraphs)))

    return texts

def main():

    parser = argparse.ArgumentParser(description="Record every step of the Python offline translator, for 'ftoffline check'. Keep the output out of the repo.")
    parser.add_argument("bundle", help="the bundle folder (a work project's Output\\ftt_bundle)")
    parser.add_argument("out", help="the folder to write one JSON per text to")
    parser.add_argument("texts", nargs="+", help="text files, or golden folders (Output\\ftt_golden)")
    args = parser.parse_args()

    outDir = Path(args.out)
    outDir.mkdir(parents=True, exist_ok=True)
    translator = offlineserver.OfflineTranslator(Path(args.bundle), HCPARSE, None, hcsynthDll=HCSYNTH_DLL, apertiumDll=APERTIUM_DLL)
    stages = {}

    # Each step is wrapped so its result goes into stages; the text dump is copied, since later steps change it
    realParse = translator.parser.parse
    realTokenize = translator.tokenizer.tokenizeText
    realApply = analysisguess.applyGuesses
    realExtract = bundleextract.extractText
    realTransfer = translator.transfer.transfer
    realSynth = translator.synthesizer.synthesize

    def recordingParse(word):

        result = realParse(word)
        stages["parses"].append([word, result])

        return result

    def recordingTokenize(text, title=""):

        dump = realTokenize(text, title)
        stages["tokens"] = copy.deepcopy(dump)

        return dump

    def recordingApply(textDump, guesser):

        planned = realApply(textDump, guesser)
        stages["guessed"] = copy.deepcopy(textDump)

        return planned

    def recordingExtract(textDump, lexicon):

        stream, messages = realExtract(textDump, lexicon)
        stages["source"] = stream
        stages["extractMessages"] = messages

        return stream, messages

    def recordingTransfer(stream):

        target = realTransfer(stream)
        stages["target"] = target

        return target

    def recordingSynth(stream):

        text, messages = realSynth(stream)
        synthesizer = translator.synthesizer
        stages["master"] = synthesizer.masterFile.read_text(encoding="utf-8")
        stages["parsesFile"] = synthesizer.parsesFile.read_text(encoding="utf-8") if synthesizer.parsesFile.exists() else None
        stages["surface"] = synthesizer.surfaceFormsFile.read_text(encoding="utf-8-sig")
        stages["synthesized"] = text
        stages["synthMessages"] = messages

        return text, messages

    translator.parser.parse = recordingParse
    translator.tokenizer.tokenizeText = recordingTokenize
    analysisguess.applyGuesses = recordingApply
    bundleextract.extractText = recordingExtract
    translator.transfer.transfer = recordingTransfer
    translator.synthesizer.synthesize = recordingSynth

    try:
        for name, text in readTexts(args.texts):

            stages.clear()
            stages["input"] = text
            stages["parses"] = []

            # A failure is recorded with the steps before it
            try:
                result = translator.translate(text)

            except Exception as e:

                stages["error"] = str(e)
                (outDir / f"{name}.json").write_text(json.dumps(stages, ensure_ascii=False, indent=1), encoding="utf-8")
                print(name, "failed:", e, flush=True)

                continue

            record = result.toDict()

            for key in ("title", "timings", "totalSeconds"):

                record.pop(key, None)

            stages["result"] = record
            (outDir / f"{name}.json").write_text(json.dumps(stages, ensure_ascii=False, indent=1), encoding="utf-8")
            print(name, "ok" if result.ok else "not ok", flush=True)

    finally:
        translator.close()

if __name__ == "__main__":

    main()
