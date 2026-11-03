#
#   fttranslator/parserexport
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Exports the source project's HermitCrab parser for the FieldWorks-free parser (hcparse) and captures the desktop parser's results to check it against.
#
#   OVERVIEW (AI generated, then edited)
#
#   The bundle's parser files. On Linux, source words are parsed by hcparse (a .NET 8 port of FieldWorks' HCParser.ParseWord), which needs the HermitCrab grammar and a way to turn what
#   HermitCrab returns into the project's objects. Both come from here, taken from the HCParser that flexicon's project.Parser holds - the parser FLEx and FTtranslator really use - so the
#   exported grammar is the one the desktop parses with, built by FieldWorks' own HCLoader with the project's parser parameters, rather than a second load that could drift from it.
#
#   WHAT IT WRITES
#
#    - parser.xml: HCParser's Language (its private m_language), written with SIL.Machine's XmlLanguageWriter, the same writer GenerateHCConfig uses.
#    - parser.json: settings - the Morpher's settings and HCParser's guessRoots flag, read from the live objects - and three maps from hvo to GUID: forms (each MoForm with its owning entry
#      and morph type), msas and inflTypes. HermitCrab's properties hold hvos (database handles), which are only meaningful in the process that loaded the project, so the maps are made in the
#      same process that writes parser.xml. hcparse looks hvos up here and writes GUIDs.
#   captureParses() is the check: it parses words with the desktop parser and records the results as GUIDs, which, unlike hvos, mean the same thing in any process.
#
#   TRAPS
#
#    - m_language, m_morpher and m_guessRoots are private to HCParser, so they are read by reflection. A FieldWorks release that renames them makes exportParser() fail loudly rather than
#      export something wrong.
#    - The parser is current only after a parse; exportParser() parses one word first, through flexicon, which reloads a stale grammar.
#
#   CODE STRUCTURE
#
#   exportParser() writes the two files; bundle.exportBundle() calls it. _privateField() does the reflection. captureParses() records desktop parses for golden.py, using _resultRecord().
#

import json

from . import bundle

PARSER_XML_FILE = "parser.xml"
PARSER_DATA_FILE = "parser.json"
PARSES_FILE = "parses.jsonl"

def _privateField(obj, name):
    '''Read a private instance field of a .NET object. See TRAPS above.'''

    from System.Reflection import BindingFlags  # type: ignore  # only importable once FieldWorks is initialized

    field = obj.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance)

    if field is None:

        raise RuntimeError(f"{obj.GetType().Name} has no field {name}; this FieldWorks version may have changed its parser.")

    return field.GetValue(obj)

def exportParser(project, outDir):
    '''Write parser.xml and parser.json for the open source project (a flexicon project) into outDir. Returns the number of forms, msas and inflection types mapped.'''

    import clr  # type: ignore  # pythonnet

    from SIL.LCModel import ILexEntryInflTypeRepository, IMoFormRepository, IMoMorphSynAnalysisRepository  # type: ignore  # only importable once FieldWorks is initialized

    # A parse makes flexicon load (or reload) the grammar; then its HCParser holds the Language. See TRAPS above.
    project.Parser.ParseWord("a")

    # ParserCore has loaded SIL.Machine's HermitCrab assembly by now, but pythonnet only offers its namespace once it is referenced by name
    clr.AddReference("SIL.Machine.Morphology.HermitCrab")  # type: ignore  # pythonnet's clr module has no type stubs, so its members are unknown to pyright
    from SIL.Machine.Morphology.HermitCrab import XmlLanguageWriter  # type: ignore
    hcParser = project.Parser._CurrentHandle()
    language = _privateField(hcParser, "m_language")
    morpher = _privateField(hcParser, "m_morpher")

    XmlLanguageWriter.Save(language, str(outDir / PARSER_XML_FILE))

    serviceLocator = project.project.ServiceLocator
    forms = {}

    for form in serviceLocator.GetService(IMoFormRepository).AllInstances():

        forms[str(form.Hvo)] = {"guid": bundle.guidOf(form), "entry": bundle.guidOf(form.Owner), "morphType": bundle.guidOf(form.MorphTypeRA) if form.MorphTypeRA else None}

    msas = {str(msa.Hvo): bundle.guidOf(msa) for msa in serviceLocator.GetService(IMoMorphSynAnalysisRepository).AllInstances()}
    inflTypes = {str(inflType.Hvo): bundle.guidOf(inflType) for inflType in serviceLocator.GetService(ILexEntryInflTypeRepository).AllInstances()}

    settings = {
        "deletionReapplications": morpher.DeletionReapplications,
        "maxStemCount": morpher.MaxStemCount,
        "mergeEquivalentAnalyses": morpher.MergeEquivalentAnalyses,
        "maxAlternatives": morpher.MaxAlternatives,
        "alwaysEnforceFinalTemplates": morpher.AlwaysEnforceFinalTemplates,
        "guessRoots": bool(_privateField(hcParser, "m_guessRoots")),
    }

    bundle.writeJson(outDir / PARSER_DATA_FILE, {"formatVersion": bundle.BUNDLE_FORMAT_VERSION, "settings": settings, "forms": forms, "msas": msas, "inflTypes": inflTypes})

    return len(forms), len(msas), len(inflTypes)

def captureParses(project, words, outPath):
    '''Parse each word (already prepared with parsing.parserForm()) with the desktop parser and write one JSON line per word to outPath, in hcparse's format. Returns how many were written.'''

    with open(outPath, "w", encoding="utf-8", newline="\n") as fOut:

        for word in words:

            fOut.write(json.dumps(_resultRecord(word, project.Parser.ParseWord(word)), ensure_ascii=False) + "\n")

    return len(words)

def _resultRecord(word, parseResult):
    '''A ParseResult as hcparse writes one: the error message, or the analyses with each morph as GUIDs.'''

    if parseResult.ErrorMessage:

        return {"word": word, "error": parseResult.ErrorMessage, "analyses": []}

    analyses = []

    for analysis in parseResult.Analyses:

        analyses.append([{"form": bundle.guidOf(morph.Form), "entry": bundle.guidOf(morph.Form.Owner), "msa": bundle.guidOf(morph.Msa), "inflType": bundle.guidOf(morph.InflType) if morph.InflType else None, "guessed": morph.GuessedString} for morph in analysis.Morphs])

    return {"word": word, "error": None, "analyses": analyses}
