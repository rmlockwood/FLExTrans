#
#   DisambiguateText.py
#
#   Ron Lockwood
#   SIL International
#   7/27/26
#
#   Version 3.16.1 - 7/27/26 - Ron Lockwood
#    Added a Settings dialog with live preview: font face and size via the standard font dialog, and the two highlight colors via the standard color dialog. The settings
#    and the window size persist in TOML format in Config/DisambiguateTextSettings.txt. Word boxes use theme palette colors so dark mode works.
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
import tomllib
import unicodedata

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QColorDialog, QFontDialog, QWidget, QLabel, QComboBox, QLayout, QSizePolicy
from PyQt6.QtCore import Qt, QCoreApplication, QSize, QRect

from flextoolslib import *                                                  # type: ignore

import Mixpanel
import ReadConfig
import Utils
import FTPaths
from Disambiguator import Ui_DisambiguatorWindow
from DisambiguatorSettings import Ui_DisambiguatorSettings
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
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'Disambiguator', 'DisambiguatorSettings']

#----------------------------------------------------------------
# Documentation that the user sees:
description = _translate("DisambiguateText", """This module lets you resolve ambiguities in the synthesized text that the {synthesisModule} module produced.
When STAMP finds more than one way to synthesize a word, it puts all the alternatives into the text in the form %2%word1%word2%.
This module shows the whole text in a scrollable window with each ambiguous word highlighted. Choose the correct alternative for
each ambiguity from its drop-down box, then click Save or Save and Close. A backup copy of the synthesized text file is made
before your choices are saved. Note: this module only applies when the STAMP method of synthesis is being used.""").format(synthesisModule=synthesisDocs[FTM_Name])

docs = {FTM_Name       : _translate("DisambiguateText", "Disambiguate Synthesized Text"),
        FTM_Version    : "3.16.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("DisambiguateText", "Manually resolve ambiguous words in the synthesized text."),
        FTM_Help       : "",
        FTM_Description: description}

#----------------------------------------------------------------

# Style for the unambiguous word boxes: the theme's default text-box background and text colors (palette(base)/palette(text)),
# so the boxes look right in dark mode as well as light mode.
PLAIN_WORD_STYLE = 'QLabel {background-color: palette(base); color: palette(text); padding: 2px;}'

# Default settings for the word box display. Ambiguous words get a yellow combo box and once the user has chosen a specific
# alternative the combo box turns green so it's easy to see which ambiguities are left to do. The colors and font can all be
# changed in the Settings dialog and are stored in a TOML file in the project's Config folder.
DEFAULT_AMBIGUOUS_COLOR = '#ffff00'
DEFAULT_RESOLVED_COLOR = '#98fb98'
DEFAULT_FONT_SIZE = 11

def makeComboStyle(color):

    # Build the stylesheet for an ambiguity combo box with the given background color. The text is black or white, whichever
    # contrasts better with the background, so any user-chosen color stays readable in light or dark mode. Only the colors are
    # styled - the combo box is otherwise stock, so Qt lays out the text and the drop-down arrow natively in both LTR and RTL.
    textColor = 'black' if color.lightness() > 127 else 'white'

    return f'QComboBox {{background-color: {color.name()}; color: {textColor};}}'

# How many strong directional characters to sample when detecting the text flow direction
DIRECTION_SAMPLE_SIZE = 1000

# Matches the %N% marker that starts a STAMP ambiguity cluster, capturing N, the number of alternatives that follow
AMBIGUITY_MARKER_RE = re.compile(r'%(\d+)%')

class DisambiguationPreferences():

    # The display settings for the disambiguation window (font, highlight colors, window size). They are stored in a TOML-formatted
    # file in the project's Config folder, following the same pattern as the Rule Assistant's ApplicationPreferences in RAutils.py.
    FONT_FAMILY = 'fontFamily'
    FONT_SIZE = 'fontSize'
    AMBIGUOUS_COLOR = 'ambiguousColor'
    RESOLVED_COLOR = 'resolvedColor'
    WINDOW_WIDTH = 'windowWidth'
    WINDOW_HEIGHT = 'windowHeight'

    SETTINGS_FILENAME = 'DisambiguateTextSettings.txt'

    def __init__(self):

        self.filePath = os.path.join(FTPaths.CONFIG_DIR, self.SETTINGS_FILENAME)
        self.data = self.load()

    def load(self):

        # Read the TOML settings file into a flat dict; a missing or unreadable file just means "use defaults"
        try:

            with open(self.filePath, 'rb') as f:

                return tomllib.load(f)

        except (FileNotFoundError, OSError, tomllib.TOMLDecodeError):

            return {}

    def getFontFamily(self):

        # An empty string means no font has been chosen yet, so the application default font is used
        return str(self.data.get(self.FONT_FAMILY, ''))

    def setFontFamily(self, fontFamily):

        self.data[self.FONT_FAMILY] = fontFamily

    def getFontSize(self):

        return int(self.data.get(self.FONT_SIZE, DEFAULT_FONT_SIZE))

    def setFontSize(self, fontSize):

        self.data[self.FONT_SIZE] = int(fontSize)

    def getColor(self, key, default):

        # Validate the stored color string and fall back to the default if it isn't a valid color
        colorStr = str(self.data.get(key, default))

        return colorStr if QtGui.QColor(colorStr).isValid() else default

    def getAmbiguousColor(self):

        return self.getColor(self.AMBIGUOUS_COLOR, DEFAULT_AMBIGUOUS_COLOR)

    def setAmbiguousColor(self, colorStr):

        self.data[self.AMBIGUOUS_COLOR] = colorStr

    def getResolvedColor(self):

        return self.getColor(self.RESOLVED_COLOR, DEFAULT_RESOLVED_COLOR)

    def setResolvedColor(self, colorStr):

        self.data[self.RESOLVED_COLOR] = colorStr

    # The window size defaults (0) mean "not saved yet", in which case the size designed into the .ui file is kept
    def getWindowWidth(self):

        return int(self.data.get(self.WINDOW_WIDTH, 0))

    def getWindowHeight(self):

        return int(self.data.get(self.WINDOW_HEIGHT, 0))

    def setWindowSize(self, width, height):

        self.data[self.WINDOW_WIDTH] = int(width)
        self.data[self.WINDOW_HEIGHT] = int(height)

    def sync(self):

        # Persist the current settings to the TOML file, creating the Config folder if it doesn't exist yet.
        # Import here (not at module load) so the module can be imported without tomli_w present.
        import tomli_w

        os.makedirs(os.path.dirname(self.filePath), exist_ok=True)

        with open(self.filePath, 'wb') as f:

            tomli_w.dump(self.data, f)

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

class SettingsDialog(QDialog):

    # Dialog for changing the display settings: font face and size, and the highlight colors for ambiguous and
    # resolved words. A preview area shows sample word boxes rendered with the current choices, updating as they change.
    # OK writes the choices back into the preferences object; Cancel leaves it untouched.
    def __init__(self, parent, prefs, rightToLeft):

        QDialog.__init__(self, parent)
        self.prefs = prefs
        self.rightToLeft = rightToLeft

        self.ui = Ui_DisambiguatorSettings()
        self.ui.setupUi(self)

        # Initialize the controls from the stored settings
        self.chosenFont = QtGui.QFont(prefs.getFontFamily() or self.font().family(), prefs.getFontSize())
        self.ambiguousColor = QtGui.QColor(prefs.getAmbiguousColor())
        self.resolvedColor = QtGui.QColor(prefs.getResolvedColor())

        # Build the preview: a plain word box, an ambiguous combo box and a resolved combo box, just like the main window shows
        self.previewLabel = QLabel(_translate("DisambiguateText", "word"))
        self.previewAmbiguousCombo = QComboBox()
        self.previewAmbiguousCombo.addItem(_translate("DisambiguateText", "%2%big%large%"))
        self.previewResolvedCombo = QComboBox()
        self.previewResolvedCombo.addItem(_translate("DisambiguateText", "chosen"))

        # The preview combo boxes are just for show: make them ignore the mouse and keyboard so clicking doesn't open a popup.
        # This keeps them painted like the real thing, unlike disabling them, which would gray out the colors being previewed.
        for previewCombo in (self.previewAmbiguousCombo, self.previewResolvedCombo):

            previewCombo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            previewCombo.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # For a right-to-left text the combo boxes in the main window have their arrow on the left, so make the preview match
        if self.rightToLeft:

            self.previewAmbiguousCombo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.previewResolvedCombo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Align the sample boxes vertically centered so they keep their natural height instead of stretching to fill the group box
        self.ui.previewLayout.addWidget(self.previewLabel, 0, Qt.AlignmentFlag.AlignVCenter)
        self.ui.previewLayout.addWidget(self.previewAmbiguousCombo, 0, Qt.AlignmentFlag.AlignVCenter)
        self.ui.previewLayout.addWidget(self.previewResolvedCombo, 0, Qt.AlignmentFlag.AlignVCenter)
        self.ui.previewLayout.addStretch(1)

        self.ui.fontButton.clicked.connect(self.chooseFont)
        self.ui.ambiguousColorButton.clicked.connect(self.chooseAmbiguousColor)
        self.ui.resolvedColorButton.clicked.connect(self.chooseResolvedColor)
        self.ui.okButton.clicked.connect(self.accept)
        self.ui.cancelButton.clicked.connect(self.reject)

        self.updateFontButton()
        self.updateColorSwatches()
        self.updatePreview()

    def chooseFont(self):

        # Let the user pick the font face and size with the standard font dialog
        (font, ok) = QFontDialog.getFont(self.chosenFont, parent=self)

        if ok:

            self.chosenFont = font
            self.updateFontButton()
            self.updatePreview()

    def updateFontButton(self):

        # Show the chosen face and size on the font button, e.g. "Charis SIL, 11"
        self.ui.fontButton.setText(f'{self.chosenFont.family()}, {self.chosenFont.pointSize()}')

    def chooseAmbiguousColor(self):

        color = QColorDialog.getColor(self.ambiguousColor, self, _translate("DisambiguateText", "Choose the ambiguous word color"))

        if color.isValid():

            self.ambiguousColor = color
            self.updateColorSwatches()
            self.updatePreview()

    def chooseResolvedColor(self):

        color = QColorDialog.getColor(self.resolvedColor, self, _translate("DisambiguateText", "Choose the resolved word color"))

        if color.isValid():

            self.resolvedColor = color
            self.updateColorSwatches()
            self.updatePreview()

    def updateColorSwatches(self):

        # Show each chosen color as the background of its Choose... button, with contrasting text
        for button, color in ((self.ui.ambiguousColorButton, self.ambiguousColor), (self.ui.resolvedColorButton, self.resolvedColor)):

            textColor = 'black' if color.lightness() > 127 else 'white'
            button.setStyleSheet(f'QPushButton {{background-color: {color.name()}; color: {textColor};}}')

    def updatePreview(self):

        # Render the sample word boxes with the currently chosen font and colors
        previewFont = QtGui.QFont(self.chosenFont)

        self.previewLabel.setFont(previewFont)
        self.previewLabel.setStyleSheet(PLAIN_WORD_STYLE)
        self.previewAmbiguousCombo.setFont(previewFont)
        self.previewAmbiguousCombo.setStyleSheet(makeComboStyle(self.ambiguousColor))
        self.previewResolvedCombo.setFont(previewFont)
        self.previewResolvedCombo.setStyleSheet(makeComboStyle(self.resolvedColor))

    def accept(self):

        # OK was clicked, so write the choices back into the preferences object. The caller applies and saves them.
        self.prefs.setFontFamily(self.chosenFont.family())
        self.prefs.setFontSize(self.chosenFont.pointSize())
        self.prefs.setAmbiguousColor(self.ambiguousColor.name())
        self.prefs.setResolvedColor(self.resolvedColor.name())

        QDialog.accept(self)

class Main(QMainWindow):

    def __init__(self, lineSegmentsList, origText, synFile):

        QMainWindow.__init__(self)
        self.lineSegmentsList = lineSegmentsList
        self.origText = origText
        self.synFile = synFile
        self.dirty = False
        self.skipSavePrompt = False
        self.wordLabelList = []
        self.rowWidgetList = []

        # Load the display settings (font, highlight colors) from the settings file in the Config folder
        self.prefs = DisambiguationPreferences()

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.ui = Ui_DisambiguatorWindow()
        self.ui.setupUi(self)

        # Restore the window size from the last session, if one was saved
        if self.prefs.getWindowWidth() > 0 and self.prefs.getWindowHeight() > 0:

            self.resize(self.prefs.getWindowWidth(), self.prefs.getWindowHeight())

        self.ui.saveButton.clicked.connect(self.saveClicked)
        self.ui.saveCloseButton.clicked.connect(self.saveCloseClicked)
        self.ui.settingsButton.clicked.connect(self.settingsClicked)
        self.ui.cancelButton.clicked.connect(self.cancelClicked)

        # Set the layout direction of the text area based on a sample of the text. The flow layouts below lay the word
        # boxes out according to this direction, so RTL texts start at the right edge and wrap leftward.
        self.rightToLeft = textIsRightToLeft(origText)

        if self.rightToLeft:

            self.ui.scrollAreaWidgetContents.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.updateStyles()

        self.buildWordBoxes()

    def updateStyles(self):

        # Build the combo box stylesheets from the currently set highlight colors
        self.ambiguousStyle = makeComboStyle(QtGui.QColor(self.prefs.getAmbiguousColor()))
        self.resolvedStyle = makeComboStyle(QtGui.QColor(self.prefs.getResolvedColor()))

    def currentWordFont(self):

        # The font for the word boxes: the chosen face (or the application default if none has been chosen yet) at the chosen size
        wordFont = self.font()

        if self.prefs.getFontFamily():

            wordFont.setFamily(self.prefs.getFontFamily())

        wordFont.setPointSizeF(self.prefs.getFontSize())

        return wordFont

    def buildWordBoxes(self):

        wordFont = self.currentWordFont()

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
                        self.wordLabelList.append(wordLabel)
                        rowLayout.addWidget(wordLabel)

            self.rowWidgetList.append(rowWidget)
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

    def settingsClicked(self):

        # Show the settings dialog. On OK the dialog has written the new values into the preferences object, so apply them
        # to the word boxes and save them to the settings file.
        dialog = SettingsDialog(self, self.prefs, self.rightToLeft)

        if dialog.exec():

            self.updateStyles()
            self.applyDisplaySettings()

            try:
                self.prefs.sync()

            except OSError:

                QMessageBox.warning(self, _translate("DisambiguateText", "File Error"), _translate("DisambiguateText", "There was a problem writing the settings file: {filePath}.").format(filePath=Utils.shortenPathForDisplay(self.prefs.filePath)))

    def applyDisplaySettings(self):

        # Re-render all the word boxes with the current font and colors
        wordFont = self.currentWordFont()

        for wordLabel in self.wordLabelList:

            wordLabel.setFont(wordFont)
            wordLabel.setStyleSheet(PLAIN_WORD_STYLE)

        for segmentList in self.lineSegmentsList:

            for segment in segmentList:

                if segment.isAmbiguous() and segment.comboBox:

                    segment.comboBox.setFont(wordFont)
                    segment.comboBox.setStyleSheet(self.ambiguousStyle if segment.comboBox.currentIndex() == 0 else self.resolvedStyle)

        # A font change changes the word box sizes, so make each row lay its words out again
        for rowWidget in self.rowWidgetList:

            rowLayout = rowWidget.layout()

            if rowLayout:

                rowLayout.invalidate()

            rowWidget.updateGeometry()

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

        # Remember the window size for the next session. Failing to write the settings file shouldn't hold up closing the window.
        self.prefs.setWindowSize(self.width(), self.height())

        try:
            self.prefs.sync()

        except OSError:
            pass

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
