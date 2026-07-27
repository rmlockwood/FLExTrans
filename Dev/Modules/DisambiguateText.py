#
#   DisambiguateText.py
#
#   Ron Lockwood
#   SIL International
#   7/27/26
#
#   Version 3.16 - 7/27/26 - Ron Lockwood
#    Initial version, based on a prototype by Beth Bryson.
#
#   Let the user resolve ambiguities in the text that STAMP synthesis produced. When STAMP finds more than one way to
#   synthesize a word, it writes all the alternatives into the synthesized text in the form %N%alt1%alt2%...% where N is
#   the number of alternatives. For more information on how to cause STAMP to produce ambiguities, see the documentation.
#   This module shows the whole synthesized text in a scrollable window, one box per word,
#   with a highlighted combo box for each ambiguous word. The user picks the correct alternative for each ambiguity and
#   saves. Before any changes are saved, a backup copy of the synthesized text file is made. The layout direction of the
#   window (left-to-right or right-to-left) is determined automatically from a sample of the text in the file.
#
#   This module only applies to the STAMP method of synthesis. HermitCrab synthesis doesn't produce ambiguities.
#

import os
import re
import shutil
import unicodedata

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QLabel, QComboBox, QLayout, QSizePolicy
from PyQt6.QtCore import Qt, QCoreApplication, QSize, QRect

from flextoolslib import *                                                  # type: ignore

import Mixpanel
import ReadConfig
import Utils
import FTPaths
from Disambiguator import Ui_DisambiguatorWindow
from DoStampSynthesis import docs as synthesisDocs

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'DisambiguateText'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'Disambiguator']

#----------------------------------------------------------------
# Documentation that the user sees:
description = _translate("DisambiguateText", """This module lets you resolve ambiguities in the synthesized text that the {synthesisModule} module produced.
When STAMP finds more than one way to synthesize a word, it puts all the alternatives into the text in the form %2%word1%word2%.
This module shows the whole text in a scrollable window with each ambiguous word highlighted. Choose the correct alternative for
each ambiguity from its drop-down box, then click Save or Save and Close. A backup copy of the synthesized text file is made
before your choices are saved. Note: this module only applies when the STAMP method of synthesis is being used.""").format(synthesisModule=synthesisDocs[FTM_Name])

docs = {FTM_Name       : _translate("DisambiguateText", "Disambiguate Synthesized Text"),
        FTM_Version    : "3.16",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("DisambiguateText", "Manually resolve ambiguous words in the synthesized text."),
        FTM_Help       : "",
        FTM_Description: description}

#----------------------------------------------------------------

# Styles for the word boxes. Unambiguous words get a box in the theme's default text-box color (palette(base), so dark mode works),
# ambiguous words get a yellow combo box and once the user has chosen a specific alternative the combo box turns green so it's easy
# to see which ambiguities are left to do. The highlighted boxes force black text so they stay readable in dark mode too. The combo
# box styles are format templates: {arrowSide} gets filled in with 'right' or 'left' so there's extra padding between the text and
# the drop-down arrow, which sits on the right in a left-to-right text and on the left in a right-to-left one.
PLAIN_WORD_STYLE = 'QLabel {background-color: palette(base); padding: 2px;}'
AMBIGUOUS_STYLE = 'QComboBox {{background-color: yellow; color: black; padding: 2px; padding-{arrowSide}: 14px;}}'
RESOLVED_STYLE = 'QComboBox {{background-color: palegreen; color: black; padding: 2px; padding-{arrowSide}: 14px;}}'

# Point size for the text in the word boxes
WORD_POINT_SIZE = 11

# How many strong directional characters to sample when detecting the text flow direction
DIRECTION_SAMPLE_SIZE = 1000

# Matches the %N% marker that starts a STAMP ambiguity cluster, capturing N, the number of alternatives that follow
AMBIGUITY_MARKER_RE = re.compile(r'%(\d+)%')

class FlowLayout(QLayout):

    # A layout that lays its child widgets out left to right (or right to left) and wraps to a new line when the row is
    # full, like words in a paragraph. Based on the standard Qt FlowLayout example, with right-to-left support added.
    def __init__(self, parent=None, margin=4, spacing=6):

        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):

        self.itemList.append(item)

    def count(self):

        return len(self.itemList)

    def itemAt(self, index):

        if 0 <= index < len(self.itemList):

            return self.itemList[index]

        return None

    def takeAt(self, index):

        if 0 <= index < len(self.itemList):

            return self.itemList.pop(index)

        return None

    def expandingDirections(self):

        return Qt.Orientation(0)

    def hasHeightForWidth(self):

        return True

    def heightForWidth(self, width):

        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):

        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):

        return self.minimumSize()

    def minimumSize(self):

        size = QSize()

        for item in self.itemList:

            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

        return size

    def doLayout(self, rect, testOnly):

        # Lay out the items as if left-to-right, then mirror the x coordinate at the end if the widget is right-to-left. Items are
        # gathered a line at a time and placed once the line is complete, because the line's height (which the taller combo boxes set)
        # has to be known before the items can be vertically centered within it so label text and combo box text line up.
        margins = self.contentsMargins()
        effectiveRect = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        parentWidget = self.parentWidget()
        rightToLeft = parentWidget is not None and parentWidget.layoutDirection() == Qt.LayoutDirection.RightToLeft
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        lineItemList = []

        for item in self.itemList:

            itemWidth = item.sizeHint().width()
            itemHeight = item.sizeHint().height()

            # Wrap to the next line if this item doesn't fit on the current one (unless the line is still empty)
            if x + itemWidth > effectiveRect.right() + 1 and lineHeight > 0:

                if not testOnly:

                    self.placeLineItems(lineItemList, y, lineHeight, effectiveRect, rightToLeft)

                lineItemList = []
                x = effectiveRect.x()
                y += lineHeight + self.spacing()
                lineHeight = 0

            lineItemList.append((item, x, itemWidth, itemHeight))
            x += itemWidth + self.spacing()
            lineHeight = max(lineHeight, itemHeight)

        # Place the last (possibly only) line
        if not testOnly:

            self.placeLineItems(lineItemList, y, lineHeight, effectiveRect, rightToLeft)

        return y + lineHeight - rect.y() + margins.bottom()

    def placeLineItems(self, lineItemList, y, lineHeight, effectiveRect, rightToLeft):

        # Place the items of one completed line, each vertically centered within the line's height
        for item, itemX, itemWidth, itemHeight in lineItemList:

            itemY = y + (lineHeight - itemHeight) // 2

            if rightToLeft:

                # Mirror the position so the first item is at the right edge and the line grows leftward
                item.setGeometry(QRect(effectiveRect.right() - (itemX - effectiveRect.x()) - itemWidth + 1, itemY, itemWidth, itemHeight))
            else:
                item.setGeometry(QRect(itemX, itemY, itemWidth, itemHeight))

class TextSegment():

    # A run of unambiguous text between ambiguities. It is kept verbatim so that saving reproduces the original text
    # exactly wherever the user made no choice, including all the original spacing and punctuation.
    def __init__(self, text):

        self.text = text

    def isAmbiguous(self):

        return False

    def currentText(self):

        return self.text

class AmbiguitySegment():

    # One STAMP ambiguity, e.g. %2%word1%word2%. origText is the whole cluster as it appears in the file, and
    # alternativeList holds the N alternatives. The combo box for choosing gets attached after the widgets are built.
    def __init__(self, origText, alternativeList):

        self.origText = origText
        self.alternativeList = alternativeList
        self.comboBox = None

    def isAmbiguous(self):

        return True

    def currentText(self):

        # Index 0 is the combined entry showing all the alternatives, which means the user hasn't chosen yet. In that
        # case keep the original ambiguity cluster in the file so the user can come back to it in a later session.
        if self.comboBox is None or self.comboBox.currentIndex() == 0:

            return self.origText

        return self.alternativeList[self.comboBox.currentIndex() - 1]

def parseAmbiguities(line):

    # Break one line of the synthesized text into a list of TextSegment and AmbiguitySegment objects. STAMP writes an
    # ambiguity as %N%alt1%alt2%...% where N is the number of alternatives. The alternatives can contain spaces, so we
    # scan for the %N% marker and then take exactly N %-terminated chunks rather than trying to match it all with one regex.
    segmentList = []
    lastEnd = 0
    searchPos = 0

    while True:

        match = AMBIGUITY_MARKER_RE.search(line, searchPos)

        if not match:
            break

        # Collect the N alternatives that follow the %N% marker, each one terminated by a % sign
        alternativeCount = int(match.group(1))
        alternativeList = []
        scanPos = match.end()

        for _ in range(alternativeCount):

            nextPercent = line.find('%', scanPos)

            if nextPercent == -1:
                break

            alternativeList.append(line[scanPos:nextPercent])
            scanPos = nextPercent + 1

        # If we didn't find all N alternatives, or there aren't at least two, this isn't a well-formed ambiguity.
        # Treat the marker as plain text and keep scanning after it.
        if len(alternativeList) != alternativeCount or alternativeCount < 2:

            searchPos = match.end()
            continue

        # Save the plain text that came before this ambiguity
        if match.start() > lastEnd:

            segmentList.append(TextSegment(line[lastEnd:match.start()]))

        segmentList.append(AmbiguitySegment(line[match.start():scanPos], alternativeList))
        lastEnd = scanPos
        searchPos = scanPos

    # Save any plain text after the last ambiguity
    if lastEnd < len(line):

        segmentList.append(TextSegment(line[lastEnd:]))

    return segmentList

def textIsRightToLeft(text):

    # Determine the flow of the text from a sample of the file contents. Count strong right-to-left characters (Unicode
    # bidirectional classes R and AL) versus strong left-to-right characters (class L) and let the majority decide.
    rtlCount = 0
    ltrCount = 0

    for char in text:

        direction = unicodedata.bidirectional(char)

        if direction in ('R', 'AL'):

            rtlCount += 1

        elif direction == 'L':

            ltrCount += 1

        if rtlCount + ltrCount >= DIRECTION_SAMPLE_SIZE:
            break

    return rtlCount > ltrCount

class Main(QMainWindow):

    def __init__(self, lineSegmentsList, origText, synFile):

        QMainWindow.__init__(self)
        self.lineSegmentsList = lineSegmentsList
        self.origText = origText
        self.synFile = synFile
        self.dirty = False
        self.skipSavePrompt = False

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.ui = Ui_DisambiguatorWindow()
        self.ui.setupUi(self)

        self.ui.saveButton.clicked.connect(self.saveClicked)
        self.ui.saveCloseButton.clicked.connect(self.saveCloseClicked)
        self.ui.cancelButton.clicked.connect(self.cancelClicked)

        # Set the layout direction of the text area based on a sample of the text. The flow layouts below lay the word
        # boxes out according to this direction, so RTL texts start at the right edge and wrap leftward.
        rightToLeft = textIsRightToLeft(origText)

        if rightToLeft:

            self.ui.scrollAreaWidgetContents.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Fill in the combo box style templates. Stylesheet padding is physical (not flipped for RTL), so pad whichever side the
        # drop-down arrow is on for this text direction to keep the arrow from crowding the text.
        arrowSide = 'left' if rightToLeft else 'right'
        self.ambiguousStyle = AMBIGUOUS_STYLE.format(arrowSide=arrowSide)
        self.resolvedStyle = RESOLVED_STYLE.format(arrowSide=arrowSide)

        self.buildWordBoxes()

    def buildWordBoxes(self):

        # Use a bigger font than the default for the word boxes so the text is easy to read
        wordFont = self.font()
        wordFont.setPointSize(WORD_POINT_SIZE)

        # Build one flow-layout row per line of the file so paragraph breaks are preserved on screen and in the output
        for segmentList in self.lineSegmentsList:

            rowWidget = QWidget()
            rowLayout = FlowLayout(rowWidget)

            # Let the vertical layout ask the row for its height at a given width, so wrapped rows get enough room
            rowPolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            rowPolicy.setHeightForWidth(True)
            rowWidget.setSizePolicy(rowPolicy)

            for segment in segmentList:

                if segment.isAmbiguous():

                    comboBox = QComboBox()
                    comboBox.setFont(wordFont)

                    # The first item shows all the alternatives together and means "not chosen yet"
                    comboBox.addItem('%'.join(segment.alternativeList))

                    for alternative in segment.alternativeList:

                        comboBox.addItem(alternative)

                    comboBox.setStyleSheet(self.ambiguousStyle)
                    comboBox.setToolTip(_translate("DisambiguateText", "Choose one of the alternatives. Keeping the first entry selected leaves the word ambiguous."))
                    comboBox.currentIndexChanged.connect(self.choiceChanged)
                    segment.comboBox = comboBox
                    rowLayout.addWidget(comboBox)

                else:
                    # Split the plain text into words just for display. The segment itself is kept verbatim for saving.
                    for word in segment.text.split():

                        wordLabel = QLabel(word)
                        wordLabel.setFont(wordFont)
                        wordLabel.setStyleSheet(PLAIN_WORD_STYLE)
                        rowLayout.addWidget(wordLabel)

            self.ui.textVerticalLayout.addWidget(rowWidget)

        # Push all the rows to the top of the scroll area
        self.ui.textVerticalLayout.addStretch(1)

    def choiceChanged(self):

        self.dirty = True

        # Recolor the combo box: green once a specific alternative is chosen, back to yellow if the user returns to the combined entry
        comboBox = self.sender()

        if not isinstance(comboBox, QComboBox):

            return

        if comboBox.currentIndex() == 0:

            comboBox.setStyleSheet(self.ambiguousStyle)

        else:
            comboBox.setStyleSheet(self.resolvedStyle)

    def getCurrentText(self):

        # Rebuild the text from the segments. Plain segments come through verbatim, ambiguity segments produce either the
        # chosen alternative or the original ambiguity cluster if the user hasn't chosen yet.
        return '\n'.join(''.join(segment.currentText() for segment in segmentList) for segmentList in self.lineSegmentsList)

    def writeFile(self, text):

        try:

            with open(self.synFile, 'w', encoding='utf-8') as f:

                f.write(text)

        except IOError:

            QMessageBox.warning(self, _translate("DisambiguateText", "File Error"), _translate("DisambiguateText", "There was a problem writing the file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(self.synFile)))
            return False

        return True

    def saveClicked(self):

        if self.writeFile(self.getCurrentText()):

            self.dirty = False

    def saveCloseClicked(self):

        self.saveClicked()
        self.skipSavePrompt = True
        self.close()

    def cancelClicked(self):

        # Cancel restores the file to what it was when the window opened, discarding anything saved during this session
        self.writeFile(self.origText)
        self.skipSavePrompt = True
        self.close()

    def closeEvent(self, event):

        # If the user closes the window with unsaved choices (e.g. with the X button), offer to save them first
        if self.dirty and not self.skipSavePrompt:

            answer = QMessageBox.question(self, _translate("DisambiguateText", "Save Choices"), _translate("DisambiguateText", "Do you want to save your disambiguation choices before closing?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

            if answer == QMessageBox.StandardButton.Cancel:

                event.ignore()
                return

            if answer == QMessageBox.StandardButton.Yes:

                self.saveClicked()

        QMainWindow.closeEvent(self, event)

def MainFunction(DB, report, modify=True):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME],
                           translators, loadBase=True)

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # This module only applies to the STAMP method of synthesis. HermitCrab doesn't produce ambiguities.
    hermitCrabSynthesisYesNo = ReadConfig.getConfigVal(configMap, ReadConfig.HERMIT_CRAB_SYNTHESIS, report, giveError=False)

    if hermitCrabSynthesisYesNo == 'y':

        report.Warning(_translate("DisambiguateText", "This module only applies when the STAMP method of synthesis is being used. The Settings indicate that HermitCrab synthesis is being used."))
        return

    # Get the path to the synthesized text file.
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)

    if not targetSynthesis:
        return

    synFile = Utils.build_path_default_to_temp(targetSynthesis)

    if not os.path.exists(synFile):

        report.Error(_translate("DisambiguateText", "The {moduleName} module must be run before this module. The file: {filePath} does not exist.").format(moduleName=synthesisDocs[FTM_Name], filePath=Utils.shortenPathForDisplay(synFile)))
        return

    try:

        with open(synFile, encoding='utf-8') as f:

            origText = f.read()

    except IOError:

        report.Error(_translate("DisambiguateText", "There was a problem reading the synthesis file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(synFile)))
        return

    # Parse each line of the text into plain and ambiguity segments
    lineSegmentsList = [parseAmbiguities(line) for line in origText.split('\n')]

    # If there are no ambiguities in the text, there is nothing for the user to do
    if not any(segment.isAmbiguous() for segmentList in lineSegmentsList for segment in segmentList):

        report.Info(_translate("DisambiguateText", "No ambiguities were found in the synthesized text file: {filePath}. There is nothing to disambiguate.").format(filePath=Utils.shortenPathForDisplay(synFile)))
        return

    # Make a backup copy of the synthesized text file before the user changes anything
    backupFile = synFile + '.bak'

    try:
        shutil.copy2(synFile, backupFile)

    except OSError:

        report.Error(_translate("DisambiguateText", "Could not create the backup file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(backupFile)))
        return

    report.Info(_translate("DisambiguateText", "A backup of the synthesized text was saved to the file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(backupFile)))

    window = Main(lineSegmentsList, origText, synFile)

    window.show()
    app.exec()

    report.Info(_translate("DisambiguateText", "The disambiguated text is in the file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(synFile)))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
