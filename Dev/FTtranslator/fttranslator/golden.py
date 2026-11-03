#
#   fttranslator/golden
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Captures golden pairs: each text's analyses as JSON, next to what Extract Source Text really produced from them, and the desktop parser's results for every wordform.
#
#   OVERVIEW (AI generated, then edited)
#
#   The test data for the offline translator. A bundle runtime (see bundle.py) has to turn a text's analyses and the bundle's lexicon into exactly what FLExTrans' Extract Source Text writes.
#   This file captures, for each text in the source project, the two sides of that test: the input, as the runtime will see it (every occurrence in the text with its offsets, and each word's
#   morph bundles as GUIDs into the bundle's lexicon), and the expected output, made by running the real doExtractSourceText() on the same text. Because the analyses come straight from FLEx,
#   a difference between the runtime and the expected file can only come from the runtime or the lexicon export - not from parsing or guessing, which get their own tests.
#
#   WHAT IT WRITES
#
#   In the output folder (by default <work project>\Output\ftt_golden), for the Nth text:
#    - NNN.text.json: the title and the occurrences in the order SegmentServices.StTextAnnotationNavigator yields them, which is the order getInterlinData() walks them. Each has para and seg
#      (the paragraph's and segment's index in the text), beg and end (the offsets in the paragraph), and either punct (a punctuation form's text) or a word: surface (the paragraph text sliced
#      with those offsets, exactly as getInterlinData() slices it), baseline (the occurrence's BaselineText, which the lemma's capitalization is copied from), kind (the analysis class:
#      WfiAnalysis, WfiGloss or WfiWordform) and, for an analysis or gloss, wordform (the wordform's form, the fallback lemma) and bundles: one {morphEntry, sense, msa} per morph bundle, null
#      where the bundle lacks that object. morphEntry is the entry owning the bundle's morph, which is where Extract Source Text starts resolving variants (see bundle.py).
#    - NNN.expected.txt: what doExtractSourceText() wrote for the text, unchanged.
#    - index.json: for each text its title, file stem, whether Extract Source Text succeeded, and the messages it reported.
#   File names are numbers rather than titles, since titles can hold characters a file name can't.
#
#   Each text dump also has paragraphs (the paragraphs' text), and a word with no analysis has wordform (the form of the wordform it is), for checking the tokenizer.
#
#   TOKENIZER PAIRS
#
#   captureTokens() (the --tokens option) gives FieldWorks' ParagraphParser a list of paragraphs to parse as new paragraphs of a scratch text, exactly as Import Text adds them, records the
#   occurrences with dumpText() and undoes everything, so the project is left as it was. tokenizer.py must give the same occurrences for the same paragraphs. The source project is opened for
#   writing for this, so use it only on a project you can afford to have written to (the undo has to succeed).
#
#   PARSER PAIRS
#
#   When every text is captured (no --text), parses.jsonl is written too: each distinct wordform in the project, prepared as the parser gets it (parse_priority's parserForm()), with the desktop
#   HermitCrab parser's result in the format hcparse writes (see parserexport.py). Running hcparse on the same words with the bundle's parser.xml and parser.json must give the same results.
#
#   TRAPS
#
#    - The offsets are FieldWorks' (UTF-16 code units), and surface is Python slicing a Python string with them, as getInterlinData() does. Outside the BMP the two disagree; surface records
#      what Extract Source Text actually used, so the runtime gets the same word even where the slice is "wrong".
#    - para and seg are indexes, standing in for the paragraph and segment objects. getInterlinData() spots a new paragraph by the offsets going backwards and a new sentence by the segment
#      changing, so the runtime needs the offsets as they are and only needs seg to tell segments apart.
#    - The expected file is written in text mode, so its line ends are \r\n on Windows. Compare after normalizing line ends.
#    - Extract Source Text finds a text by its title, and the first match wins. A title shared by two texts (including "***", which several untitled texts can share) can't be captured
#      reliably, so such texts are skipped with a warning.
#    - Only configurations a bundle supports are captured (bundle.supportedParams()), so a TreeTran project is refused here too.
#
#   CODE STRUCTURE
#
#   captureGolden() picks the texts, and for each calls dumpText() for the input and runExtract() for the expected output, then writes index.json; the golden command in cli.py calls it, and then
#   captureParserGolden() for the parser pairs. captureTokens() makes the tokenizer pairs.
#   dumpText() walks one text, using _wordRecord() and _bundleRecord() for the words. The files are written with bundle.writeJson() and GUIDs with bundle.guidOf(), so they match the bundle's.
#

import io

from . import bundle
from .report import makeReporter, messages

GOLDEN_INDEX_FILE = "index.json"

def captureGolden(ftDb, configMap, outDir, report, textNames=None, verbose=False):
    '''Write a golden pair for each text in the open source project (or only those named in textNames) into outDir, plus index.json. ftDb is a flexlibs view of the project, as Extract
       Source Text expects. Returns True if any pair was written. See WHAT IT WRITES above.'''

    import Utils  # FLExTrans Lib, only importable after env.bootstrap()

    if bundle.supportedParams(configMap, report) is None:

        return False

    contentsList = []
    textList = []
    titles = Utils.getSourceTextList(ftDb, contentsList, textList)

    # A shared title can't be captured reliably. See TRAPS above.
    duplicates = {title for title in titles if titles.count(title) > 1}

    for title in sorted(duplicates):

        report.Warning(f"Skipping the {titles.count(title)} texts titled '{title}': Extract Source Text can only find the first of them.")

    if textNames:

        missing = [name for name in textNames if name not in titles]

        for name in missing:

            report.Error(f"There is no text titled '{name}'.")

        if missing:

            return False

    outDir.mkdir(parents=True, exist_ok=True)
    index = []

    for title, contents in zip(titles, contentsList):

        if title in duplicates or (textNames and title not in textNames):

            continue

        stem = f"{len(index) + 1:03d}"
        textDump = dumpText(contents, title)
        bundle.writeJson(outDir / f"{stem}.text.json", textDump)

        # Each text gets its own reporter, so its messages can be saved with it. They are only printed with --verbose; index.json has them all.
        textReport = makeReporter(verbose, None if verbose else io.StringIO())
        ok = runExtract(ftDb, configMap, title, outDir / f"{stem}.expected.txt", textReport)

        index.append({"title": title, "stem": stem, "ok": ok, "occurrences": len(textDump["occurrences"]), "messages": messages(textReport)})

        if not ok:

            report.Warning(f"Extract Source Text failed on '{title}'; see {GOLDEN_INDEX_FILE}.")

    bundle.writeJson(outDir / GOLDEN_INDEX_FILE, {"formatVersion": bundle.BUNDLE_FORMAT_VERSION, "texts": index})
    report.Info(f"Captured {len(index)} golden pair(s) in {outDir}.")

    return len(index) > 0

def captureParserGolden(project, outDir, report):
    '''Parse every wordform in the project with the desktop HermitCrab parser and write the results to parses.jsonl, to check hcparse against. See PARSER PAIRS above.'''

    from SIL.LCModel import IWfiWordformRepository  # type: ignore  # only importable once FieldWorks is initialized
    from parse_priority.parsing import parserForm

    from . import parserexport

    # Each distinct wordform once, prepared as the parser gets it, in a fixed order
    words = set()

    for wordform in project.project.ServiceLocator.GetService(IWfiWordformRepository).AllInstances():

        text = wordform.Form.VernacularDefaultWritingSystem.Text

        if text:

            words.add(parserForm(text))

    count = parserexport.captureParses(project, sorted(words), outDir / parserexport.PARSES_FILE)
    report.Info(f"Parsed {count} wordform(s) with the desktop parser into {parserexport.PARSES_FILE}.")

def runExtract(ftDb, configMap, title, outPath, report):
    '''Run the real Extract Source Text on the titled text, writing its output to outPath. Returns True if it succeeded. The configuration is copied, never changed.'''

    import ExtractSourceText  # FLExTrans module, only importable after env.bootstrap()
    import ReadConfig

    runConfig = dict(configMap)
    runConfig[ReadConfig.SOURCE_TEXT_NAME] = title
    runConfig[ReadConfig.ANALYZED_TEXT_FILE] = str(outPath)

    return bool(ExtractSourceText.doExtractSourceText(ftDb, runConfig, report))

def dumpText(contents, title):
    '''Return the input side of a golden pair for one text: its occurrences in getInterlinData()'s order. See WHAT IT WRITES above.'''

    from SIL.LCModel import IPunctuationForm, IStTxtPara  # type: ignore  # only importable once FieldWorks is initialized
    from SIL.LCModel.Core.KernelInterfaces import ITsString  # type: ignore
    from SIL.LCModel.DomainServices import SegmentServices  # type: ignore

    import InterlinData  # FLExTrans Lib, only importable after env.bootstrap()

    paragraphIndexes = {}
    segmentIndexes = {}
    occurrences = []

    for occurrence in SegmentServices.StTextAnnotationNavigator(contents).GetAnalysisOccurrencesAdvancingInStText():

        begOffset = occurrence.GetMyBeginOffsetInPara()
        endOffset = occurrence.GetMyEndOffsetInPara()

        # Indexes in order of first appearance stand in for the paragraph and segment objects
        record = {"para": paragraphIndexes.setdefault(occurrence.Paragraph.Hvo, len(paragraphIndexes)), "seg": segmentIndexes.setdefault(occurrence.Segment.Hvo, len(segmentIndexes)), "beg": begOffset, "end": endOffset}

        if occurrence.Analysis.ClassName == InterlinData.PUNCTUATION_FORM:

            record["punct"] = ITsString(IPunctuationForm(occurrence.Analysis).Form).Text
        else:
            record.update(_wordRecord(occurrence, begOffset, endOffset))

        occurrences.append(record)

    # The paragraphs' text, so the tokenizer can be checked against these occurrences
    paragraphs = [ITsString(IStTxtPara(paragraph).Contents).Text or "" for paragraph in contents.ParagraphsOS]

    return {"formatVersion": bundle.BUNDLE_FORMAT_VERSION, "title": title, "paragraphs": paragraphs, "occurrences": occurrences}

def captureTokens(project, paragraphs, outPath):
    '''Have FieldWorks' ParagraphParser parse each paragraph as a new paragraph of a scratch text, as Import Text does, record the occurrences with dumpText(), and undo it all. Writes
       {"paragraphs", "occurrences"} to outPath and returns the number of occurrences. See TOKENIZER PAIRS above.'''

    from parse_priority import textedit

    title = "FTtranslator tokenizer check"

    with project.UndoableOperation("FTtranslator: tokenizer check"):

        for paragraph in paragraphs:

            textedit.addSentence(project, title, paragraph, {}, approve=False)

    # Read the result before undoing it; the text is the last one with this title
    try:
        text = textedit.getOrCreateText(project, title)
        textDump = dumpText(text.ContentsOA, title)
    finally:
        project.Undo()

    bundle.writeJson(outPath, {"formatVersion": bundle.BUNDLE_FORMAT_VERSION, "paragraphs": paragraphs, "occurrences": textDump["occurrences"]})

    return len(textDump["occurrences"])

def _wordRecord(occurrence, begOffset, endOffset):
    '''The word part of an occurrence's record, read the way getInterlinData() and getAnalysisObject() read it.'''

    from SIL.LCModel import IWfiAnalysis, IWfiWordform  # type: ignore  # only importable once FieldWorks is initialized
    from SIL.LCModel.Core.KernelInterfaces import ITsString  # type: ignore

    import InterlinData  # FLExTrans Lib, only importable after env.bootstrap()
    import Utils

    analysis = occurrence.Analysis
    record = {"surface": ITsString(occurrence.Paragraph.Contents).Text[begOffset:endOffset], "baseline": ITsString(occurrence.BaselineText).Text, "kind": analysis.ClassName}

    # As getAnalysisObject(): a gloss stands for the analysis that owns it, and a bare wordform (or anything else) has no analysis
    if analysis.ClassName == InterlinData.WFI_ANALYSIS:

        wfiAnalysis = IWfiAnalysis(analysis)

    elif analysis.ClassName == InterlinData.WFI_GLOSS:

        wfiAnalysis = IWfiAnalysis(analysis.Analysis)

    # A bare wordform: which one it is (the tokenizer has to pick the same one)
    elif analysis.ClassName == InterlinData.WFI_WORD_FORM:

        record["wordform"] = Utils.as_vern_string(IWfiWordform(analysis).Form)
        return record
    else:
        return record

    # The fallback lemma when the analysis has no root (addLemmaFromObj()), which only applies when the analysis belongs to a wordform
    owner = wfiAnalysis.Owner
    record["wordform"] = Utils.as_vern_string(IWfiWordform(owner).Form) if owner.ClassName == InterlinData.WFI_WORD_FORM else None
    record["bundles"] = [_bundleRecord(morphBundle) for morphBundle in wfiAnalysis.MorphBundlesOS]

    return record

def _bundleRecord(morphBundle):
    '''A morph bundle as the three GUIDs Extract Source Text starts from, with null for whatever the bundle lacks (it checks for each).'''

    return {"morphEntry": bundle.guidOf(morphBundle.MorphRA.Owner) if morphBundle.MorphRA else None, "sense": bundle.guidOf(morphBundle.SenseRA) if morphBundle.SenseRA else None, "msa": bundle.guidOf(morphBundle.MsaRA) if morphBundle.MsaRA else None}