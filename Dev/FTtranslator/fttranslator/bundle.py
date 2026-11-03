#
#   fttranslator/bundle
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Exports the source lexicon data Extract Source Text needs, and the source HermitCrab parser, for a translator that runs without FieldWorks.
#
#   OVERVIEW (AI generated, then edited)
#
#   The first piece of the offline translation bundle: a snapshot of a work project that a translator with no FieldWorks (eventually a phone app) can translate from. This file writes the part
#   Extract Source Text needs from the source lexicon. Everything Extract Source Text looks up in LCModel for a word - headwords, sense numbers, grammatical categories, inflection classes, stem
#   features, variant-to-main-entry resolution and complex forms - is fixed for a given lexicon, so it is worked out here once, by calling the same FLExTrans Utils functions Extract Source Text
#   calls. The strings in the bundle are therefore exactly the strings FLExTrans would produce. What depends on the text itself (punctuation, capitalization, sentence and paragraph breaks, which
#   complex forms are substituted) is left to the runtime that reads the bundle.
#
#   WHAT IT WRITES
#
#   In the output folder (by default <work project>\Output\ftt_bundle): parser.xml and parser.json, the source project's HermitCrab parser for hcparse (see parserexport.py);
#   tokenizer.json (exportTokenizerData()), what tokenizer.py needs to split text as FLEx does; guesser.json, what analysisguess.py needs to file parses and guess (see guessexport.py); the
#   apertium folder, the bilingual lexicon and rules as Run Apertium gives them to the tools (see transferexport.py); the synthesis folder, the target affix list, complex form and variant cache
#   and HermitCrab.config that HermitCrab synthesis reads (see synthexport.py); and:
#    - manifest.json: the format version, when and from which work project and source project the bundle was made, the target project's name, the record counts, and the FlexTrans.config values Extract Source Text reads, keyed by their setting names.
#      The values are read with InterlinData.initInterlinParams(), so they are parsed exactly as Extract Source Text parses them. The config section also holds the values synthesis.py reads, and
#      interfaceLanguage is the language code FLExTrans hands HCSynthByGloss.
#    - lexicon.json: three tables keyed by GUID.
#        entries  headword (Utils.getHeadwordStr, with the homograph number), clitic ("proclitic", "enclitic" or null), the top-level senses in order, resolvesTo for a variant with no senses
#                 (the entry Utils.GetEntryWithSensePlusFeat reaches and the irregularly inflected form's feature abbreviations), and complexForms: one item per complex-form entry ref of each
#                 complex form this entry is part of, with the complex entry, its components in order, and its complex-form type names.
#        senses   the owning entry, the gloss (affix and clitic tags come from it) and the msa.
#        msas     whether it is a stem msa, and for a stem msa the grammatical category (after Utils.convertProblemChars), the inflection class and the sorted stem feature abbreviations. sense is
#                 the sense the msa's entry uses it for (parse_priority's senseForMsa): a parser analysis has an msa but no sense, and the runtime fills the sense in from here, as fillSenses() does.
#
#   HOW THE RUNTIME USES THE KEYS
#
#   Extract Source Text starts each morph bundle from the entry that owns the bundle's morph (bundle.MorphRA.Owner), not from the sense's entry, and resolves variants from there. So the runtime
#   looks a bundle up by three GUIDs - the morph's entry, the sense and the msa - which is what the text dump (the step after this one) records for each bundle. The sense number in a lemma such as
#   maison1.2 is the position of the bundle's sense in the resolved entry's top-level senses, which is why entries keep their senses in order. A subsense is not among them, and gets no number,
#   just as in Extract Source Text. After resolution, everything about the word is read from the resolved entry, not the morph's own entry: the headword, the clitic check, the complex forms
#   it is part of (and the cache findComplexForms() keeps them in) and the component matching. Only the affix-or-stem test (the bundle's msa) and an affix's gloss (the bundle's sense) are not.
#   golden.py writes the texts' side of this: each occurrence and its bundles' three GUIDs, next to what Extract Source Text really produced.
#
#   TRAPS
#
#    - Everything is exported raw rather than pre-filtered by the configured complex-form types. findComplexForms() keeps one item per matching type, in loop order, and caches an entry after the
#      first types list that finds anything for it; the runtime has to repeat that loop to give the same results, so it needs the unfiltered refs.
#    - A component of a complex form can be a sense rather than an entry. Its GUID is exported as is; it never equals an entry's GUID, so it never matches, as on the desktop.
#    - Feature lists are sorted by feature name (stably), as TextWord.getFeatures() sorts them, before they are written.
#    - An msa's stemFeatures is null when it has no feature structure and [] when it has an empty one. TextWord.getStemFeatures() caches the first non-empty list it finds for the whole word,
#      and returns that cache for any later root that has a structure, even an empty one, but [] for a root with none. The runtime needs the difference to give the same tags.
#    - FieldWorks text is NFD. It is written unchanged; the runtime must not normalize it.
#
#   WHAT IS NOT SUPPORTED
#
#   The TreeTran path (a FlexTrans.config with a TreeTran output file) needs PC-PATR and TreeTran, so a project set up for it is refused. A configuration whose discontiguous complex types differ
#   from the inflection-on-first-element types makes Extract Source Text stop with an error (TextParagraph has no findDiscontiguousComplexForms()), so that gets a warning.
#
#   CODE STRUCTURE
#
#   supportedParams() checks the configuration and returns Extract Source Text's settings; golden.py uses it too. exportBundle() calls it, then exportLexicon(), parserexport.exportParser(),
#   exportTokenizerData(), guessexport.exportGuesserData(), transferexport.exportTransfer() and synthexport.exportSynthesis(), and writes the files; the export-bundle command in cli.py calls it. exportLexicon() walks every entry and builds the three tables with entryRecord(), senseRecord() and msaRecord().
#   _complexForms() collects an entry's complex-form refs for entryRecord(). _sortedAbbrevs() is a helper, and guidOf() and writeJson() are shared with golden.py and parserexport.py.
#

import json
from datetime import datetime

from . import tokenizer

# Bump when the layout of the files changes, so a runtime can refuse a bundle it doesn't understand
BUNDLE_FORMAT_VERSION = 1

MANIFEST_FILE = "manifest.json"
LEXICON_FILE = "lexicon.json"

# LexEntryRef.RefType for a complex form (0 is a variant)
COMPLEX_FORM_REF_TYPE = 1

def supportedParams(configMap, report):
    '''Return the Extract Source Text settings, parsed the same way it parses them (InterlinData.initInterlinParams()), or None if the configuration can't be bundled. See WHAT IS NOT
       SUPPORTED above. golden.py uses it too, so golden pairs are only made for configurations a bundle can serve.'''

    import InterlinData  # FLExTrans Lib, only importable after env.bootstrap()
    import ReadConfig

    # The TreeTran path needs desktop programs
    if ReadConfig.getConfigVal(configMap, ReadConfig.ANALYZED_TREETRAN_TEXT_FILE, report, giveError=False):

        report.Error(f"The bundle doesn't support TreeTran. Clear the {ReadConfig.ANALYZED_TREETRAN_TEXT_FILE} setting to export one.")
        return None

    params = InterlinData.initInterlinParams(configMap, report, None)

    if params is None:

        return None

    if params.discontigTypesList and params.discontigPOSList and (params.typesInfl1stList or params.typesInfl2ndList) and params.typesInfl1stList != params.discontigTypesList:

        report.Warning("The discontiguous complex types differ from the complex types with inflection on the first element. Extract Source Text stops with an error on this configuration.")

    return params

def exportBundle(project, configMap, outDir, report, sourceProjectName, workProjectName):
    '''Write manifest.json and lexicon.json for the open source project into outDir. Returns True if they were written; problems go to report. See WHAT IT WRITES above.'''

    import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

    params = supportedParams(configMap, report)

    if params is None:

        return False

    from . import parserexport

    lexicon = exportLexicon(project)
    outDir.mkdir(parents=True, exist_ok=True)

    # The source project's HermitCrab parser, for hcparse (see parserexport.py), and what the tokenizer needs (see tokenizer.py)
    parserForms, parserMsas, parserInflTypes = parserexport.exportParser(project, outDir)
    tokenizerData = exportTokenizerData(project)
    writeJson(outDir / tokenizer.TOKENIZER_FILE, tokenizerData)

    # What the guesser and the parse filer need (see guessexport.py)
    from . import guessexport

    guesserData = guessexport.exportGuesserData(project)
    writeJson(outDir / guessexport.GUESSER_FILE, guesserData)

    # The Apertium inputs, as Run Apertium hands them to the tools (see transferexport.py)
    from . import transferexport

    rulesFiles = transferexport.exportTransfer(project, configMap, outDir, report)

    if rulesFiles is None:

        return False

    # What HermitCrab synthesis reads from the target project, made current as the drafting steps make it (see synthexport.py)
    from . import synthexport

    synthesisExport = synthexport.exportSynthesis(project, configMap, outDir, report)

    if synthesisExport is None:

        return False

    synthesisFiles, synthesisConfig, interfaceLanguage = synthesisExport

    manifest = {
        "formatVersion": BUNDLE_FORMAT_VERSION,
        "created": datetime.now().isoformat(timespec="seconds"),
        "workProject": workProjectName,
        "sourceProject": sourceProjectName,
        "targetProject": ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False) or "",
        "files": {"lexicon": LEXICON_FILE, "parser": parserexport.PARSER_XML_FILE, "parserData": parserexport.PARSER_DATA_FILE, "tokenizer": tokenizer.TOKENIZER_FILE, "guesser": guessexport.GUESSER_FILE,
                  "apertium": {"dir": transferexport.APERTIUM_DIR, "rules": rulesFiles}, "synthesis": synthesisFiles},
        "interfaceLanguage": interfaceLanguage,
        "counts": {**{table: len(lexicon[table]) for table in ("entries", "senses", "msas")}, "parserForms": parserForms, "parserMsas": parserMsas, "parserInflTypes": parserInflTypes,
                   "wordforms": len(tokenizerData["wordforms"]), "phrases": sum(len(phrases) for phrases in tokenizerData["phrases"].values())},
        "config": {
            ReadConfig.SENTENCE_PUNCTUATION: params.sentPunct,
            ReadConfig.SOURCE_FORMS_INFLECTION_1ST: params.typesInfl1stList,
            ReadConfig.SOURCE_COMPLEX_TYPES: params.typesInfl2ndList,
            ReadConfig.SOURCE_DISCONTIG_TYPES: params.discontigTypesList,
            ReadConfig.SOURCE_DISCONTIG_SKIPPED: params.discontigPOSList,
            ReadConfig.NO_PROPER_NOUN_WARNING: params.noWarningProperNoun,
            **synthesisConfig,
        },
    }

    writeJson(outDir / LEXICON_FILE, lexicon)
    writeJson(outDir / MANIFEST_FILE, manifest)

    report.Info(f"Exported {manifest['counts']['entries']} entries, {manifest['counts']['senses']} senses and {manifest['counts']['msas']} msas to {outDir}.")
    return True

def exportTokenizerData(project):
    '''Return what tokenizer.py needs: the default vernacular writing system's id and word-forming overrides, every wordform's form, and the phrases by their lowercased first word.'''

    from SIL.LCModel import IWfiWordformRepository  # type: ignore  # only importable once FieldWorks is initialized
    from System.Reflection import BindingFlags  # type: ignore

    cache = project.project
    vernWs = cache.DefaultVernWs
    writingSystem = cache.ServiceLocator.WritingSystemManager.Get(vernWs)

    # CoreWritingSystemDefinition takes its overrides from the "main" character set; pythonnet returns TryGet's out value with its result
    overrides = []
    found, mainSet = writingSystem.CharacterSets.TryGet("main", None)

    if found and mainSet is not None:

        overrides = sorted({ord(chars[0]) for chars in mainSet.Characters if chars})

    repository = cache.ServiceLocator.GetService(IWfiWordformRepository)
    wordforms = sorted({wordform.Form.get_String(vernWs).Text for wordform in repository.AllInstances() if wordform.Form.get_String(vernWs).Text})

    # The repository's own phrase table, which ParagraphParser uses. It is on an internal interface, so it is found by reflection.
    phrases = {}
    phraseProperty = next((prop for prop in repository.GetType().GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic) if prop.Name.endswith("FirstWordToPhrases")), None)

    if phraseProperty is None:

        raise RuntimeError("The wordform repository has no FirstWordToPhrases; this FieldWorks version may have changed it.")

    for pair in phraseProperty.GetValue(repository):

        phrases[pair.Key] = [phrase.Text for phrase in pair.Value]

    return {"formatVersion": BUNDLE_FORMAT_VERSION, "wsId": writingSystem.Id, "wordFormingOverrides": overrides, "wordforms": wordforms, "phrases": phrases}

def exportLexicon(project):
    '''Return the entries, senses and msas tables for every entry in the open project.'''

    from SIL.LCModel import ILexEntryRepository  # type: ignore  # only importable once FieldWorks is initialized

    entries = {}
    senses = {}
    msas = {}

    repository = project.project.ServiceLocator.GetService(ILexEntryRepository)

    for entry in repository.AllInstances():

        entries[guidOf(entry)] = entryRecord(entry)

        # AllSenses includes subsenses, which a morph bundle can point to too
        for sense in entry.AllSenses:

            senses[guidOf(sense)] = senseRecord(sense)

        for msa in entry.MorphoSyntaxAnalysesOC:

            msas[guidOf(msa)] = msaRecord(msa)

    return {"formatVersion": BUNDLE_FORMAT_VERSION, "entries": entries, "senses": senses, "msas": msas}

def entryRecord(entry):
    '''The entries-table record for one entry. See WHAT IT WRITES above.'''

    import Utils  # FLExTrans Lib, only importable after env.bootstrap()

    record = {"headword": Utils.getHeadwordStr(entry), "clitic": None, "senses": [guidOf(sense) for sense in entry.SensesOS]}

    if Utils.isProclitic(entry):

        record["clitic"] = "proclitic"

    elif Utils.isEnclitic(entry):

        record["clitic"] = "enclitic"

    # A variant with no senses of its own: record where Extract Source Text ends up, and the features an irregularly inflected form adds on the way
    if entry.SensesOS.Count == 0:

        featurePairs = []
        resolved = Utils.GetEntryWithSensePlusFeat(entry, featurePairs)

        if guidOf(resolved) != guidOf(entry) or featurePairs:

            record["resolvesTo"] = {"entry": guidOf(resolved), "inflFeatures": _sortedAbbrevs(featurePairs)}

    complexForms = _complexForms(entry)

    if complexForms:

        record["complexForms"] = complexForms

    return record

def _complexForms(entry):
    '''The complex-form refs of every complex form the entry is part of, in the order TextSentence.findComplexForms() visits them, unfiltered by type. See TRAPS above.'''

    import Utils  # FLExTrans Lib, only importable after env.bootstrap()

    complexForms = []

    for complexEntry in entry.ComplexFormEntries:

        # A complex entry can also carry variant refs; only its complex-form refs with at least one type count
        for entryRef in complexEntry.EntryRefsOS:

            if entryRef.RefType == COMPLEX_FORM_REF_TYPE and entryRef.ComplexEntryTypesRS.Count > 0:

                complexForms.append({"entry": guidOf(complexEntry), "components": [guidOf(component) for component in entryRef.ComponentLexemesRS], "types": [Utils.as_string(complexType.Name) for complexType in entryRef.ComplexEntryTypesRS]})

    return complexForms

def senseRecord(sense):
    '''The senses-table record for one sense.'''

    import Utils  # FLExTrans Lib, only importable after env.bootstrap()

    msa = sense.MorphoSyntaxAnalysisRA

    return {"entry": guidOf(sense.Entry), "gloss": Utils.as_string(sense.Gloss), "msa": guidOf(msa) if msa else None}

def msaRecord(msa):
    '''The msas-table record for one msa. Only a stem msa has a grammatical category, inflection class and stem features; Extract Source Text reads them through IMoStemMsa.'''

    import Utils  # FLExTrans Lib, only importable after env.bootstrap()
    from SIL.LCModel import IMoStemMsa  # type: ignore  # only importable once FieldWorks is initialized
    from parse_priority.guesser import senseForMsa

    sense = senseForMsa(msa)
    record = {"stem": msa.ClassName == Utils.MO_STEM_MSA, "sense": guidOf(sense) if sense else None}

    if not record["stem"]:

        return record

    stemMsa = IMoStemMsa(msa)

    # As TextWord.getPOS(): no category means the runtime outputs UNK and warns, so None is kept distinct from an empty abbreviation
    if stemMsa.PartOfSpeechRA:

        record["pos"] = Utils.convertProblemChars(Utils.as_string(stemMsa.PartOfSpeechRA.Abbreviation) or "", Utils.catProbData)
    else:
        record["pos"] = None

    record["inflClass"] = Utils.as_string(stemMsa.InflectionClassRA.Abbreviation) if stemMsa.InflectionClassRA else None

    # As TextWord.getStemFeatures(): the features can be nested, and get_feat_abbr_list() flattens them. None (no feature structure) is kept distinct from an empty structure; see TRAPS above.
    if stemMsa.MsFeaturesOA:

        featurePairs = []
        Utils.get_feat_abbr_list(stemMsa.MsFeaturesOA.FeatureSpecsOC, featurePairs)
        record["stemFeatures"] = _sortedAbbrevs(featurePairs)
    else:
        record["stemFeatures"] = None

    return record

def _sortedAbbrevs(featurePairs):
    '''The abbreviations from (feature name, abbreviation) pairs, sorted by feature name. The same stable sort as TextWord.getFeatures(), so e.g. gender comes before number.'''

    return [abbrev for _, abbrev in sorted(featurePairs, key=lambda pair: pair[0])]

def guidOf(lcmObject):

    return str(lcmObject.Guid)

def writeJson(path, data):

    # sort_keys keeps the files the same from one export to the next, so two bundles can be compared with a diff
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
