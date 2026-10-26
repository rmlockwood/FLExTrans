#
#   parse_priority/textedit
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Edits texts - assigning analyses and adding sentences - so the guesser's counts change.
#
#   OVERVIEW (AI generated, then edited)
#
#   The guesser's ranking comes entirely from what is in the texts, so changing the texts is how to change the ranking. Two kinds of edit move the counts:
#    - Assigning an analysis to an occurrence already in a text, which is what a user does by confirming a guess or picking a parse in FLEx's Analyze or Gloss tab (assign(), approveGuesses()).
#    - Adding new sentences in which the word is analysed a particular way (addSentence()). FTtranslator also uses addSentence(), with no assignments, to import its source text.
#
#   UNITS OF WORK
#
#   Every function here changes the project, so it must run inside a unit of work. Callers wrap them in project.UndoableOperation(), which also lets a whole run be undone - the parse_priority
#   commands undo unless --commit is given, and FTtranslator undoes its approvals once the text is extracted.
#
#   APPROVING
#
#   When a user confirms an analysis, FLEx also records a human-approved evaluation on it. _approve() does the same, so the guesser treats an assigned analysis exactly as one a user confirmed.
#   The analysis may be a WfiGloss; the evaluation goes on the analysis that owns it.
#
#   CODE STRUCTURE
#
#   assign() and _approve() first, then approveGuesses() and its helper _class(). getOrCreateText() and addSentence() add text; trainingSentence() builds the sentence the demo command repeats.
#

from . import fw
from .guesser import formOf, iterTexts

def assign(project, occurrence, analysis, approve=True):
    '''Set an occurrence's analysis, as confirming a parse in FLEx does. approve also records it as human-approved.'''

    occurrence.segment.AnalysesRS[occurrence.index] = analysis

    if approve:

        _approve(project, analysis)

def _approve(project, analysis):
    '''Record a human-approved evaluation on the analysis (or on the analysis that owns it, for a gloss). See APPROVING above.'''

    from SIL.LCModel import Opinions  # type: ignore  # only importable once FieldWorks is initialized

    langProject = project.project.LangProject
    fw.lcm.IWfiAnalysis(analysis.Analysis).SetAgentOpinion(langProject.DefaultUserAgent, Opinions.approves)

def approveGuesses(ranker, occurrences):
    '''Approve the guesser's top choice for every occurrence that has a guess, as FLEx's Approve All does. All the guesses are taken first and then applied, so earlier approvals don't
       change later guesses. A guess may be a gloss (when the analysis has one); it is stored as it is. Returns [(occurrence, guess, basis)] for the approved ones.'''

    planned = []

    for occurrence in occurrences:

        # Already glossed
        if occurrence.analysis.ClassName not in ("WfiWordform", "WfiAnalysis"):

            continue

        guess = ranker.bestGuess(occurrence)

        # No guess, or the guess is what the occurrence already has
        if _class(guess) not in ("WfiAnalysis", "WfiGloss") or guess.Hvo == occurrence.analysis.Hvo:

            continue

        planned.append((occurrence, guess, ranker.basis(occurrence)))

    for occurrence, guess, _ in planned:

        occurrence.segment.AnalysesRS[occurrence.index] = guess
        _approve(ranker.project, guess)

    return planned

def _class(obj):
    '''The object's LCM class name, or None for a NullWAG (the guesser's "no guess"), which has none.'''

    try:
        return obj.ClassName

    except Exception:

        return None

def getOrCreateText(project, title):
    '''Return the text with this title, creating it if there is none.'''

    for _, text in iterTexts(project, title):

        return text

    return project.Texts.Create(title)

def addSentence(project, textTitle, sentence, assignments, approve=True):
    '''Append sentence as a new paragraph of the text titled textTitle (created if missing), break it into segments and wordforms the way FLEx does, then set analyses: assignments maps a
       lowercase word to an IWfiAnalysis and is applied to every occurrence of that word in the new paragraph. Returns (number of occurrences assigned, the new paragraph).'''

    lcm = fw.lcm
    text = getOrCreateText(project, textTitle)
    para = lcm.IStTxtPara(project.Paragraphs.Create(text, sentence))
    lcm.ParagraphParser.ParseParagraph(para, True, True)
    assignedCount = 0

    for segment in para.SegmentsOS:

        for index in range(segment.AnalysesRS.Count):

            analysis = segment.AnalysesRS[index]
            target = assignments.get(formOf(analysis).lower())

            if target is None:

                continue

            segment.AnalysesRS[index] = target

            if approve:

                _approve(project, target)

            assignedCount += 1

    return assignedCount, para

def trainingSentence(occurrence):
    '''Build '<previous> <word> <next>.' from an occurrence's own neighbours, for the demo command's training sentences.'''

    words = []
    previousWord = occurrence.neighbour(True)
    nextWord = occurrence.neighbour(False)

    if previousWord != "<edge>":

        words.append(formOf(previousWord))

    words.append(formOf(occurrence.analysis))

    if nextWord != "<edge>":

        words.append(formOf(nextWord))

    sentence = " ".join(words)

    # Close the sentence so each training sentence is its own segment
    if not sentence.endswith((".", "!", "?")):

        sentence += "."

    return sentence
