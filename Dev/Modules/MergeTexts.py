#
#   MergeTexts
#
#   Ron Lockwood
#   SIL International
#   9/9/26
#
#   Version 3.17.1 - 9/11/26 - Ron Lockwood
#    Fixes #1560. Say 'multiple texts' instead of 'several texts' in the module synopsis, description and the window's intro label, since a merge can be of just two texts.
#
#   Version 3.17 - 9/9/26 - Ron Lockwood
#    Initial version.
#
#   OVERVIEW (AI generated, then edited)
#
#   This module combines several interlinear texts into one, without losing any of the interlinear work that has been done on them. Bible material arrives in FLEx one chapter at a time - "Matthew
#   01", "Matthew 02", "Matthew 03-04" and so on - but every FLExTrans module that consumes a text works on one text at a time, so drafting a whole book means running the pipeline once per chapter.
#   Merging the chapters into a single "Matthew 01-28" lets the whole book be drafted, tested and exported in one pass.
#
#   WHY MOVING PARAGRAPHS IS THE ONLY SAFE MERGE
#
#   This is the invariant the whole module exists to protect, and the thing a later reader is most likely to "simplify" and thereby break. FLEx keeps interlinear information in two places. The
#   wordforms, analyses and glosses themselves are project-global, living in the wordform inventory, so a merge cannot touch them. What belongs to the text is the CHOICE made for each occurrence:
#   every IStTxtPara owns its ISegment objects, and a segment's AnalysesRS is an ordered REFERENCE sequence naming the analysis or gloss that was approved for each word of that sentence. The
#   segment also owns its free translation, its literal translation and its notes.
#
#   So moving the paragraph objects themselves carries all of that along for free: the segments are owned by the paragraph and travel with it, and the AnalysesRS entries are references that stay
#   valid wherever the paragraph ends up. Nothing is re-parsed and nothing is recomputed. The tempting alternative - create paragraphs in the new text and copy the baseline text across - is exactly
#   what destroys the work, because FLEx re-parses a new paragraph and every word comes back unanalyzed. That is why nothing in this module reads or writes a paragraph's Contents.
#
#   The move itself is ILcmOwningSequence.MoveTo, which is what FLEx uses for cross-owner paragraph moves. Two traps around it are worth knowing. Its iStart/iEnd are INCLUSIVE, and an empty source
#   text would give iEnd of -1 and raise. And it must not be confused with ParagraphsOS.Add(): Add does not detach an object from its previous owner (only Insert does), so adding an already-owned
#   paragraph would leave it double-owned rather than moved. Every paragraph of one source text is moved in a single MoveTo call, which also avoids iterating a sequence the move is emptying.
#
#   WHAT IS LOST
#
#   A paragraph move carries the paragraphs and everything they own. It does not carry what belongs to the TEXT, and the module is explicit about each case rather than letting it happen quietly:
#   text tags live on the StText and are re-attached to the merged text when the user leaves that option on; media files belong to the IText, so a text that has them is never deleted. The dialog
#   carries the warnings about all of this - see MergeTextsDlg.py.
#
#   Discourse charts get a treatment of their own, and the reasoning is in THE CHARTS in MergeTextsDlg.py. In short: a chart names its text through BasedOnRA, but FLEx creates a chart shell the
#   moment the Discourse view is opened, so most charts on a chapter hold no words and mean nothing. The dialog sorts them out and hands the word-less ones over in MergeInfo.emptyChartList; this
#   module deletes those along with their texts and says how many went. A chart that really does hold words is left alone, after the dialog has warned the user it will be stranded.
#
#   As a safety net, the number of analysis occurrences is counted across the source texts before the merge and across the merged text afterwards. The two numbers must match. If they ever do not,
#   something moved that should not have, and the user is told to restore their backup. The counts are not reported when they agree - the user has no use for them.
#
#   NOT UNDOABLE
#
#   There is no unit-of-work code anywhere in FLExTrans. flexlibs opens a write-enabled project inside a single non-undoable task and pairs it with a save when the project is closed, so nothing
#   done here lands on an undo stack. Once the merge has run it cannot be backed out in FLExTrans or in FLEx. That is why the dialog says so twice, the confirmation defaults to No, and the module
#   description tells the user to back up the project first.
#
#   CODE STRUCTURE
#
#   MainFunction() - the entry point FlexTools calls. Checks modify mode, reads the configuration, shows the dialog, and calls doMerge with what it comes back with.
#   doMerge() - creates the merged text, moves every source text's paragraphs into it in the user's order, deletes the empty charts and then the emptied source texts, verifies the occurrence count
#   and reports.
#   moveParagraphs() - the one MoveTo call, per source text, with the empty-text guard.
#   moveTextTags() - re-owns the StText's text tags onto the merged text, since they do not travel with a paragraph move.
#   countAnalyses() - the before/after occurrence count, using the same navigator InterlinData uses.
#   copyTextMetaData() - gives the merged text the first source text's classification rather than stamping it as FLExTrans output.
#   deleteEmptyCharts() / deleteSourceText() - the guarded deletes, charts first so that nothing is left referring to a text that has gone.
#   repointSourceTextSetting() - moves the FLExTrans source text setting onto the merged text when the text it named was merged away.
#

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from SIL.LCModel import ( # type: ignore
    ITextFactory,
    IStTextFactory,
)
from SIL.LCModel.Core.Text import TsStringUtils  # type: ignore
from SIL.LCModel.DomainServices import SegmentServices  # type: ignore

from flextoolslib import * # type: ignore

import FTPaths
import MergeTextsDlg
import Mixpanel
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'MergeTexts'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'MergeTextsDlg', 'MergeTextsWindow']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("MergeTexts", "Merge Texts"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("MergeTexts", "Combine multiple texts into one, keeping all of the interlinear analyses."),
        FTM_Help       : "",
        FTM_Description: _translate("MergeTexts",
"""Combine multiple texts into one new text. This is meant for Bible books that were imported one chapter at a time - texts named
Matthew 01, Matthew 02, Matthew 03-04 and so on get merged into a single text named for the range of chapters, e.g. Matthew 01-28.
The module suggests these groups by looking at the text names, and you can also choose the texts yourself and put them in any order.
No interlinear work is lost. Each word keeps the analysis and gloss that was approved for it, and each sentence keeps its free
translation and notes.
The texts you merge are deleted, so the module asks you
to confirm. Merging this way CANNOT be undone, in FLExTrans or in FLEx, so back up your FLEx project first. Before running it, make
sure you are not in the Texts & Words section of FLEx.""")}

def countAnalyses(stTextObj):

    # The same navigator InterlinData uses to size its progress bar. Counting the occurrences before and after the merge is the cheap end-to-end proof that nothing was lost.
    navigator = SegmentServices.StTextAnnotationNavigator(stTextObj)

    return sum(1 for _occurrence in navigator.GetAnalysisOccurrencesAdvancingInStText())

def copyTextMetaData(firstSourceText, mergedText):

    # The merged text is the same material as its sources, so it inherits their classification. Deliberately NOT ChapterSelection.setTextMetaData(), which stamps Source as 'FLExTrans' and
    # IsTranslated as True - right for a synthesized target text, wrong here, and mislabelling IsTranslated would change how the Paratext tools treat the text.
    mergedText.Source.AnalysisDefaultWritingSystem = firstSourceText.Source.AnalysisDefaultWritingSystem
    mergedText.IsTranslated = firstSourceText.IsTranslated

    # GenresRC is a reference collection, so adding the same possibility objects is all that is needed - nothing is copied or duplicated.
    for genre in firstSourceText.GenresRC:

        mergedText.GenresRC.Add(genre)

    # Abbreviation and Comment are deliberately left empty: a single chapter's abbreviation would be wrong for a whole book. The closing report reminds the user to fill them in.
    if firstSourceText.ContentsOA is not None and mergedText.ContentsOA is not None:

        mergedText.ContentsOA.RightToLeft = firstSourceText.ContentsOA.RightToLeft

def moveParagraphs(sourceStText, mergedStText, paraCount, sourceName, report):

    """Move every paragraph of one source text onto the end of the merged text. Returns how many were moved."""

    # An empty source text would make iEnd -1, and MoveTo raises ArgumentOutOfRangeException on that, so skip it and say so.
    if paraCount == 0:

        report.Warning(_translate("MergeTexts", 'The text "{sourceName}" has no paragraphs. Skipping it.').format(sourceName=sourceName))
        return 0

    # Read the insertion point before the move, since the move is what changes it. Appending at the destination's Count is legal and is what puts this text after the ones already moved.
    destStart = mergedStText.ParagraphsOS.Count

    # MoveTo reparents the paragraphs, and their owned Segments travel with them - which is what keeps every word's analysis, gloss, free translation and note intact. See WHY MOVING PARAGRAPHS IS
    # THE ONLY SAFE MERGE at the top of this file. iStart and iEnd are INCLUSIVE, hence paraCount - 1.
    sourceStText.ParagraphsOS.MoveTo(0, paraCount - 1, mergedStText.ParagraphsOS, destStart)

    return paraCount

def moveTextTags(sourceStText, mergedStText):

    """Re-own the source text's text tags onto the merged text. Returns how many were moved."""

    # TagsOC belongs to the StText, not to the paragraphs, so tags do NOT travel with a paragraph move. Their BeginSegmentRA/EndSegmentRA still point at the segments that just moved, so re-owning
    # the tags keeps the tagging intact. Snapshot to a Python list first: Add() re-owns each tag, which mutates the very collection we would otherwise be iterating.
    tagList = list(sourceStText.TagsOC)

    for textTag in tagList:

        mergedStText.TagsOC.Add(textTag)

    return len(tagList)

def deleteSourceText(sourceText, sourceName, report):

    """Delete one emptied source text, tolerating the two ways a delete can legitimately fail. Returns True when it was deleted."""

    # A text could have gone stale if it was deleted in FLEx while the window was open, and LCM can refuse a delete outright. Report either case rather than throwing. By this point the paragraphs
    # have already been re-owned by the merged text, so an undeletable shell is untidy rather than a loss.
    if not sourceText.IsValidObject:

        report.Warning(_translate("MergeTexts", 'The text "{sourceName}" no longer exists in the project, so it could not be deleted.').format(sourceName=sourceName))
        return False

    if not sourceText.CanDelete:

        report.Warning(_translate("MergeTexts", 'The text "{sourceName}" is now empty but could not be deleted. Delete it in FLEx.').format(sourceName=sourceName))
        return False

    sourceText.Delete()

    return True

def deleteEmptyCharts(emptyChartList, report):

    """Delete the word-less discourse charts the dialog found on the texts being merged. Returns how many went."""

    deletedCount = 0

    for chart in emptyChartList:

        # The dialog decided these were word-less only moments ago, in this same session with no chance for anything to be added to them, so there is nothing to re-check. But a chart is still an
        # object that LCM can refuse to delete, and the same guards DeleteTexts.py uses on a text apply here: report either case rather than throwing.
        if not chart.IsValidObject:

            continue

        if not chart.CanDelete:

            report.Warning(_translate("MergeTexts", "An empty discourse chart could not be deleted. Delete it in the FLEx Discourse area."))
            continue

        chart.Delete()
        deletedCount += 1

    return deletedCount

def repointSourceTextSetting(report, configMap, sourceNameList, targetName):

    """If the text FLExTrans is set up to translate was merged away, point the setting at the merged text instead and refresh the status bar that shows it."""

    activeTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report, giveError=False)

    if not activeTextName or activeTextName not in sourceNameList:

        return

    # DeleteTexts clears this setting when the text it named is deleted. Here there is a better answer: the merged text is what that text has become, and pointing the setting at it is almost
    # certainly what the user wants next, since having one text to translate is the whole reason for merging.
    ReadConfig.writeConfigValue(report, ReadConfig.SOURCE_TEXT_NAME, targetName)
    FTPaths.CURRENT_SRC_TEXT = targetName # type: ignore
    refreshStatusbar()

    report.Info(_translate("MergeTexts", 'The source text setting was "{activeTextName}", which has been merged away, so it now names the merged text "{targetName}".').format(activeTextName=activeTextName, targetName=targetName))

def doMerge(DB, report, configMap, mergeInfo):

    """Create the merged text and move every selected text's paragraphs into it, in the order the user approved."""

    # Snapshot everything needed BEFORE the first move. Once paragraphs start moving, the source ParagraphsOS sequences shrink underneath us, so nothing may be recomputed from them mid-loop.
    sourceTripleList = [(Utils.as_string(sourceText.Name).strip(), sourceText, sourceText.ContentsOA) for sourceText in mergeInfo.sourceTextList]
    paraCountList = [contentsObj.ParagraphsOS.Count if contentsObj is not None else 0 for _sourceName, _sourceText, contentsObj in sourceTripleList]

    report.ProgressStart(len(sourceTripleList) + 2, _translate("MergeTexts", "Counting the interlinear analyses..."))

    wordsBefore = sum([countAnalyses(contentsObj) for _sourceName, _sourceText, contentsObj in sourceTripleList if contentsObj is not None])

    report.ProgressUpdate(1)

    # Create the merged text. textFactory.Create() alone puts the text in the project - there is no text list to add it to.
    textFactory = DB.project.ServiceLocator.GetService(ITextFactory)
    stTextFactory = DB.project.ServiceLocator.GetService(IStTextFactory)

    mergedText = textFactory.Create()
    mergedStText = stTextFactory.Create()
    mergedText.ContentsOA = mergedStText
    mergedText.Name.AnalysisDefaultWritingSystem = TsStringUtils.MakeString(mergeInfo.targetName, DB.project.DefaultAnalWs)

    copyTextMetaData(sourceTripleList[0][1], mergedText)

    tagsMoved = 0

    for i, (sourceName, _sourceText, contentsObj) in enumerate(sourceTripleList):

        if contentsObj is None:

            report.Warning(_translate("MergeTexts", 'The text "{sourceName}" has no contents and was skipped.').format(sourceName=sourceName))
            continue

        movedCount = moveParagraphs(contentsObj, mergedStText, paraCountList[i], sourceName, report)

        if mergeInfo.moveTags:

            tagsMoved += moveTextTags(contentsObj, mergedStText)

        if movedCount:

            report.Info(_translate("MergeTexts", 'Moved {paraCount} paragraph(s) from "{sourceName}".').format(paraCount=movedCount, sourceName=sourceName))

        report.ProgressUpdate(i + 2)

    # Delete the word-less discourse charts the dialog found on these texts. FLEx makes a chart shell as soon as somebody opens the Discourse view, so these are usually leftovers that mean nothing
    # to the user; leaving them behind would strand them on a text that is about to go. Charts that really do have words in them were warned about in the dialog and are left alone.
    chartsDeleted = deleteEmptyCharts(mergeInfo.emptyChartList, report)

    # The sources are now empty shells. Deleting happens strictly after every move, so a failure part way through can never orphan paragraphs. A text with media files is kept, because the media
    # belongs to the text and would be destroyed with it.
    deletedCount = 0
    keptForMediaList = []

    for sourceName, sourceText, _contentsObj in sourceTripleList:

        if sourceText.MediaFilesOA is not None:

            keptForMediaList.append(sourceName)
            continue

        if deleteSourceText(sourceText, sourceName, report):

            deletedCount += 1

    wordsAfter = countAnalyses(mergedStText)

    report.ProgressUpdate(len(sourceTripleList) + 2)
    report.ProgressStop()

    if keptForMediaList:

        report.Warning(_translate("MergeTexts", "These texts were not deleted because they have media files, which belong to the text rather than to its paragraphs: {nameList}.").format(nameList=', '.join(keptForMediaList)))

    if tagsMoved:

        report.Info(_translate("MergeTexts", "{count} text tag(s) were moved to the merged text.").format(count=tagsMoved))

    # The safety net. These two counts come from the same navigator over the same paragraphs, so they must agree; if they ever do not, something moved that should not have.
    if wordsAfter != wordsBefore:

        report.Error(_translate("MergeTexts", "Something went wrong: the source texts had {wordsBefore} analyzed word(s) but the merged text has {wordsAfter}. Restore your backup of the FLEx project and report this.").format(wordsBefore=wordsBefore, wordsAfter=wordsAfter))
        return

    report.Info(_translate("MergeTexts", 'Text "{targetName}" created in the {projectName} project from {textCount} text(s).').format(
                targetName=mergeInfo.targetName, projectName=DB.ProjectName(), textCount=len(sourceTripleList)), DB.BuildGotoURL(mergedText))

    report.Info(_translate("MergeTexts", "{count} source text(s) were deleted.").format(count=deletedCount))

    if chartsDeleted:

        report.Info(_translate("MergeTexts", "{count} empty discourse chart(s) were deleted along with their texts.").format(count=chartsDeleted))

    repointSourceTextSetting(report, configMap, [sourceName for sourceName, _sourceText, _contentsObj in sourceTripleList], mergeInfo.targetName)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modifyAllowed):

    translators = []
    thisApp = QApplication.instance()

    if thisApp is None:
        thisApp = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True)

    # This module is useless without write access. FlexTools forces modifyAllowed to False unless FTM_ModifiesDB is True, so this catches a mis-declared docs dictionary as well as the user not
    # having turned modify mode on.
    if not modifyAllowed:

        report.Error(_translate("MergeTexts", 'You need to run this module in "modify mode."'))
        return

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)

    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Merging needs at least two texts, so there is no point opening the window on a project that cannot have any candidates.
    if DB.TextsNumberOfTexts() < 2:

        report.Error(_translate("MergeTexts", "The {projectName} project has fewer than two texts, so there is nothing to merge.").format(projectName=DB.ProjectName()))
        return

    # Which text FLExTrans is currently set up to translate, so the window can mark it. Don't complain if the setting is missing - it just means no row gets marked.
    activeTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report, giveError=False)

    # FlexTools has no running Qt event loop, so the window is shown and the loop started here. Calling exec() on the dialog alone would flash it and close.
    dlg = MergeTextsDlg.MergeTextsDlg(DB, report, activeTextName)
    dlg.show()
    thisApp.exec()

    if not dlg.retVal or dlg.mergeInfo is None:

        report.Info(_translate("MergeTexts", "No texts were merged."))
        return

    doMerge(DB, report, configMap, dlg.mergeInfo)

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
