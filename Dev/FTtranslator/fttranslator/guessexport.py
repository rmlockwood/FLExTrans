#
#   fttranslator/guessexport
#
#   Ron Lockwood
#   SIL International
#   11/3/26
#
#   Version 3.17 - 11/3/26 - Ron Lockwood
#    Initial version. Exports what the FieldWorks-free guesser (analysisguess.py) needs from the source project.
#
#   OVERVIEW (AI generated, then edited)
#
#   FLEx's analysis guesser (liblcm's AnalysisGuessServices) picks a word's analysis from counts it takes from the project every time: which analyses each wordform has and who approved them,
#   and which analyses the texts use next to which neighbouring words. FTtranslator's Parse Words step changes some of that first (the parse filer approves, disapproves and deletes parser
#   analyses). This file writes guesser.json with everything both need, so analysisguess.py can do the filing and the guessing without the project.
#
#   WHAT IT WRITES
#
#   guesser.json:
#    - wordforms: by form (in the default vernacular writing system), each with its analyses and contexts.
#        analyses   guid; human, parser and computer opinions as AnalysisGuessServices reads them ("approves", "disapproves" or null); user, the default user agent's own opinion, which the
#                   filer reads; used, whether a text uses the analysis or one of its glosses (the filer then gives it the user's approval); and bundles, each morph's form (allomorph),
#                   entry (the allomorph's owner), msa, sense, inflType and text (the bundle's own form, which a guessed morph is compared on).
#        contexts   one [analysis guid, previous, next] for each place a text uses one of the wordform's analyses or glosses: the neighbours as context keys (see below).
#    - repMsas: msa guid to representative msa guid, from the HCParser's merging of equivalent msas, which the filer uses to match a parse with an existing analysis.
#    - monomorphemic: the stem allomorphs whose entry is a single morpheme, in the order liblcm's MonomorphemicMorphData() gives them, each with the main entry, sense and msa the guesser's
#      generated analysis would use. A wordform left with no analyses gets one from the first of these whose form matches it.
#   A context key is "<edge>" at a segment edge, "w:" and the wordform's form for a word (whatever it is analysed as), or "p:" and the text for punctuation.
#
#   TRAPS
#
#    - The opinions are read with AnalysisGuessServices' own IsHumanApproved() and so on, so they mean exactly what the guesser means by them, including which human agent counts.
#    - repMsas and monomorphemic come from internal FieldWorks members, read by reflection; a FieldWorks release that changes them makes the export fail rather than write something wrong.
#
#   CODE STRUCTURE
#
#   exportGuesserData() builds guesser.json's contents; bundle.exportBundle() calls it. _analysisRecord() describes one analysis, _contextKey() one neighbour, _representativeMsas() reads the
#   HCParser's merged msas and _monomorphemic() the generated-guess candidates.
#

from . import bundle

GUESSER_FILE = "guesser.json"
EMPTY_CONTEXT = "<edge>"

def exportGuesserData(project):
    '''Return guesser.json's contents for the open source project (a flexicon project whose parser has been loaded). See WHAT IT WRITES above.'''

    from SIL.LCModel import IWfiWordformRepository, IWfiAnalysis, IWfiGloss, Opinions  # type: ignore  # only importable once FieldWorks is initialized
    from SIL.LCModel.DomainServices import AnalysisGuessServices  # type: ignore

    cache = project.project
    vernWs = cache.DefaultVernWs
    guesser = AnalysisGuessServices(cache, False)
    userAgent = cache.LangProject.DefaultUserAgent
    wordforms = {}

    for wordform in cache.ServiceLocator.GetService(IWfiWordformRepository).AllInstances():

        form = wordform.Form.get_String(vernWs).Text

        if not form:

            continue

        # Every analysis or gloss a text uses, for the filer's 'used' test
        usedObjects = set()

        for segment in wordform.OccurrencesBag:

            usedObjects.update(analysis.Hvo for analysis in segment.AnalysesRS)

        analyses = []

        for analysis in wordform.AnalysesOC:

            analysis = IWfiAnalysis(analysis)
            used = analysis.Hvo in usedObjects or any(gloss.Hvo in usedObjects for gloss in analysis.MeaningsOC)
            analyses.append(_analysisRecord(analysis, guesser, userAgent, used, vernWs, Opinions))

        # The texts' uses of the wordform's analyses, with their neighbours (AnalysisGuessServices.GetAnalysisCounts())
        contexts = []
        seenSegments = set()

        for segment in wordform.OccurrencesInTexts:

            if not segment.IsValidObject or segment.Hvo in seenSegments:

                continue

            seenSegments.add(segment.Hvo)
            segmentAnalyses = list(segment.AnalysesRS)

            for index, occurrenceAnalysis in enumerate(segmentAnalyses):

                if occurrenceAnalysis.Wordform is None or occurrenceAnalysis.Wordform.Hvo != wordform.Hvo or occurrenceAnalysis.ClassName not in ("WfiAnalysis", "WfiGloss"):

                    continue

                usedAnalysis = IWfiGloss(occurrenceAnalysis).Analysis if occurrenceAnalysis.ClassName == "WfiGloss" else occurrenceAnalysis
                previous = _contextKey(segmentAnalyses[index - 1], vernWs) if index > 0 else EMPTY_CONTEXT
                following = _contextKey(segmentAnalyses[index + 1], vernWs) if index < len(segmentAnalyses) - 1 else EMPTY_CONTEXT
                contexts.append([bundle.guidOf(usedAnalysis), previous, following])

        wordforms[form] = {"guid": bundle.guidOf(wordform), "analyses": analyses, "contexts": contexts}

    return {"formatVersion": bundle.BUNDLE_FORMAT_VERSION, "wordforms": wordforms, "repMsas": _representativeMsas(project), "monomorphemic": _monomorphemic(cache, vernWs)}

def _opinion(approved, disapproved):

    return "approves" if approved else "disapproves" if disapproved else None

def _analysisRecord(analysis, guesser, userAgent, used, vernWs, Opinions):
    '''One analysis of a wordform. See WHAT IT WRITES above.'''

    userOpinion = analysis.GetAgentOpinion(userAgent)
    bundles = []

    for morphBundle in analysis.MorphBundlesOS:

        morph = morphBundle.MorphRA
        bundles.append({"form": bundle.guidOf(morph) if morph else None, "entry": bundle.guidOf(morph.Owner) if morph else None, "msa": bundle.guidOf(morphBundle.MsaRA) if morphBundle.MsaRA else None,
                        "sense": bundle.guidOf(morphBundle.SenseRA) if morphBundle.SenseRA else None, "inflType": bundle.guidOf(morphBundle.InflTypeRA) if morphBundle.InflTypeRA else None,
                        "text": morphBundle.Form.get_String(vernWs).Text})

    return {"guid": bundle.guidOf(analysis), "human": _opinion(guesser.IsHumanApproved(analysis), guesser.IsHumanDisapproved(analysis)),
            "parser": _opinion(guesser.IsParserApproved(analysis), guesser.IsParserDisapproved(analysis)), "computer": "approves" if guesser.IsComputerApproved(analysis) else None,
            "user": "approves" if userOpinion == Opinions.approves else "disapproves" if userOpinion == Opinions.disapproves else None, "used": used, "bundles": bundles}

def _contextKey(analysis, vernWs):
    '''A neighbour as a context key: the guesser reduces an analysed word to its wordform. See WHAT IT WRITES above.'''

    if analysis.ClassName == "PunctuationForm":

        from SIL.LCModel import IPunctuationForm  # type: ignore  # only importable once FieldWorks is initialized

        return "p:" + (IPunctuationForm(analysis).Form.Text or "")

    wordform = analysis.Wordform

    return "w:" + ((wordform.Form.get_String(vernWs).Text or "") if wordform else "")

def _representativeMsas(project):
    '''The HCParser's merged msas, as guid to representative guid (only those that differ).'''

    from . import parserexport

    hcParser = project.Parser._CurrentHandle()
    representatives = parserexport._privateField(hcParser, "m_representativeMSAs")

    if representatives is None:

        return {}

    return {bundle.guidOf(pair.Key): bundle.guidOf(pair.Value) for pair in representatives if pair.Key.Guid != pair.Value.Guid}

def _monomorphemic(cache, vernWs):
    '''The generated-guess candidates, in liblcm's order, each resolved to the main entry, sense and msa AnalysisGuessServices would use (GetMainEntryAndSense()).'''

    from System.Reflection import BindingFlags  # type: ignore  # only importable once FieldWorks is initialized
    from SIL.LCModel import IMoStemAllomorphRepository, ILexEntry, ILexSense, IMoStemMsa  # type: ignore
    from SIL.LCModel.DomainServices import DomainObjectServices  # type: ignore

    repository = cache.ServiceLocator.GetService(IMoStemAllomorphRepository)
    method = repository.GetType().GetMethod("MonomorphemicMorphData", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)

    if method is None:

        raise RuntimeError("The stem allomorph repository has no MonomorphemicMorphData(); this FieldWorks version may have changed it.")

    candidates = []

    for pair in method.Invoke(repository, None):

        morph = pair.Value
        entryOrVariant = ILexEntry(morph.Owner)
        sense = None

        # A variant leads to its main entry, or straight to a sense
        entryRef = DomainObjectServices.GetVariantRef(entryOrVariant, True)

        if entryRef is not None:

            component = entryRef.ComponentLexemesRS[0]

            if component.ClassName == "LexSense":

                sense = ILexSense(component)
                mainEntry = sense.Entry
            else:
                mainEntry = ILexEntry(component)
        else:
            mainEntry = entryOrVariant

        if sense is None:

            sense = next((s for s in mainEntry.SensesOS if s.MorphoSyntaxAnalysisRA is not None and s.MorphoSyntaxAnalysisRA.ClassName == "MoStemMsa"), None)

        msa = IMoStemMsa(sense.MorphoSyntaxAnalysisRA) if sense is not None else None
        candidates.append({"form": str(pair.Key.Item2), "morph": bundle.guidOf(morph), "entry": bundle.guidOf(morph.Owner), "sense": bundle.guidOf(sense) if sense else None, "msa": bundle.guidOf(msa) if msa else None})

    return candidates
