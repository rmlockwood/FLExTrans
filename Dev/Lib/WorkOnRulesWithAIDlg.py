#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.16 - 7/9/26 - Ron Lockwood
#    Moved the Source Data / Target Data buttons off the bottom row and up beside the action buttons on both tabs (next to Create, and next to Modify/Explain); both copies share the same
#    global example data and check-mark state.
#
#   Version 3.16.15 - 7/9/26 - Ron Lockwood
#    Added Zoom +/- buttons to the preview pane header (like the Live Rule Tester) so the user can magnify or reduce the rendered rule text; the chosen zoom persists across re-renders.
#
#   Version 3.16.14 - 7/7/26 - Ron Lockwood
#    Review fixes: Open-in-XXE scratch folders are tracked and removed when the dialog closes (were leaking per click); a modify that can't load the original rule now says so instead of
#    silently showing only the new rule with no comparison.
#
#   Version 3.16.13 - 7/7/26 - Ron Lockwood
#    On the Modify/Explain tab the rule list (left column) and the change-description box (right column) now expand to fill their columns instead of being capped at a fixed height.
#
#   Version 3.16.12 - 7/7/26 - Ron Lockwood
#    The "Create new rule" tab is now selected initially, and the tab area shrinks to its minimum height (the preview pane below it absorbs the rest) so the rule preview is larger.
#    Switching to the Modify/Explain tab no longer auto-previews a rule (the list starts unselected; a preview appears only when a rule is clicked), and returning to Create blanks the preview.
#
#   Version 3.16.11 - 7/7/26 - Ron Lockwood
#    Faster, less surprising preview: the web view is warmed up just after the window opens (so the first rule click isn't delayed by Chromium start-up); rule XML is cached in memory
#    ({comment: XML}) so picking a rule no longer re-parses the whole file; no rule is auto-selected, so the preview stays blank until the user actually picks (or creates/modifies) one.
#
#   Version 3.16.10 - 7/7/26 - Ron Lockwood
#    Reorganized into two tabs: "Create new rule", and "Modify or explain an existing rule" (rule list on the left, change description on the right). Clicking a rule shows its preview at
#    once on the left; Modify puts the changed rule on the right, Explain puts the explanation there. Generate became separate Modify and Explain buttons; the preview area is now larger.
#    Clicking Explain while an unapproved modified rule is showing offers to approve and write it first.
#
#   Version 3.16.9 - 7/6/26 - Ron Lockwood
#    PasteDataDlg UI moved to separate Windows/PasteDataWindow.ui file compiled with pyuic; translations split into Windows/translations/PasteDataWindow*.ts files.
#
#   Version 3.16.8 - 7/6/26 - Ron Lockwood
#    After approving a rule that used example data, the next create Generate asks once whether to keep that data for the new rule (No clears both sides); reopening the data grids
#    disarms the question.
#
#   Version 3.16.7 - 7/6/26 - Ron Lockwood
#    Source Data / Target Data buttons open a paste grid (PasteDataDlg, the paste-to-grid tool with OK/Cancel/Clear) for interlinearized tab-separated example data; saved data is
#    re-displayed on reopen, marked with a check on the button, and sent to the AI with every request.
#
#   Version 3.16.6 - 7/6/26 - Ron Lockwood
#    The explain mode gained an Explanation-language box: type any language (e.g. Spanish, Swahili) to get the explanation in it; blank uses the FLExTrans interface language.
#
#   Version 3.16.5 - 7/5/26 - Ron Lockwood
#    New Explain existing rule mode: pick a rule (no description needed) and the AI gives a thorough plain-language explanation, shown beside the rendered rule; Approve and Open-in-XXE
#    stay disabled in this mode. Switching modes now also invalidates any pending candidate so a rule generated in one mode can't be written under another.
#
#   Version 3.16.4 - 7/4/26 - Ron Lockwood
#    Reworked the dialog to stay open for successive edits: Cancel became Close (only Close and the window X end it); Approve and Open-temp no longer close it; Approve disables itself
#    after a write until the next rule is generated (no duplicate saves); approving re-reads the rule file; added a Refresh Rules button; success is now reported in the status line.
#
#   Version 3.16.3 - 7/4/26 - Ron Lockwood
#    Also localize the authorship-stamp date/time to the interface language (Utils.LocalizedDateTimeFormatter with a custom spelled-out-month format), passed to the generator as whenStr.
#
#   Version 3.16.2 - 7/4/26 - Ron Lockwood
#    Pass the localized authorship-stamp sentences (whole sentences, so they translate cleanly across word orders) to the generator so the "AI Assistant added/modified this rule"
#    comment follows the UI language.
#
#   Version 3.16.1 - 7/3/26 - Ron Lockwood
#    The dialog layout now comes from WorkOnRulesWithAIWindow.ui compiled with pyuic (like the other module windows), and the status label word-wraps so a long explanation no longer
#    forces the dialog wide.
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. The dialog for the "Work on Rules with AI" module: choose to create a new rule or modify an existing one, describe the change, generate with the configured AI provider
#    (on a background thread), preview the result rendered like XXE, and Approve / Open in XXE / Cancel. Inputs are injected so the dialog can be exercised standalone; MainFunction
#    supplies the real FLEx-derived data later.

import os
import shutil
import tempfile
import unicodedata

from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QCoreApplication, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QDialog, QInputDialog, QLineEdit, QMessageBox, QSizePolicy, QTableWidgetItem)
from PyQt6.QtWebEngineWidgets import QWebEngineView

import AIRules
import TransferPreview
from WorkOnRulesWithAIWindow import Ui_WorkOnRulesWithAI # type: ignore
from PasteDataWindow import Ui_PasteDataDialog # type: ignore

# FTPaths is only available inside the full FLExTrans install; tolerate its absence so the dialog can run standalone.
try:
    import FTPaths

except ImportError:
    FTPaths = None  # type: ignore[assignment]

_translate = QCoreApplication.translate

# Multiplier applied to the preview's zoom factor on each click of the +/- buttons (matches the Live Rule Tester's zoom step). QWebEngineView clamps the usable zoom to roughly
# 0.25x-5.0x, so we clamp to that range in setPreviewZoom before applying it.
ZOOM_FACTOR_STEP = 1.15
MIN_PREVIEW_ZOOM = 0.25
MAX_PREVIEW_ZOOM = 5.0

def promptForApiKey(provider, parent=None):
    '''Ask the user for an API key and store it in `provider`'s slot in the OS credential vault (not a project file). Each provider has its own slot, so a key entered here does not
    overwrite another provider's key. Returns the key, or None if cancelled/empty. Shows an error and returns None if the vault is unavailable.'''

    label = _translate('WorkOnRulesWithAI', 'Enter your {provider} API key. It is stored securely in the credential vault (Windows Credential Manager), not in any project file.\n\nGet a key at:\n{url}').format(provider=provider.displayName, url=provider.keyUrl)

    # Pre-fill with the key currently in effect for this provider (vault, or an env-var fallback) so "Change API key" shows the existing key rather than a blank box. Empty on first entry.
    currentKey = AIRules.resolveApiKey(provider) or ''

    key, ok = QInputDialog.getText(parent, _translate('WorkOnRulesWithAI', 'API key'), label, QLineEdit.EchoMode.Normal, currentKey)
    key = (key or '').strip()

    if not ok or not key:
        return None

    try:
        AIRules.setStoredApiKey(provider, key)

    except Exception as err:

        QMessageBox.warning(parent, _translate('WorkOnRulesWithAI', 'API key'),
                            _translate('WorkOnRulesWithAI', 'Could not save the key to the credential vault: {err}').format(err=err))
        return None

    return key

class PasteDataDlg(QDialog):
    '''Paste-and-review grid for interlinearized, tab-separated example data. The user pastes rows copied from FLEx, sees them aligned in a grid (record-start rows and the row-label
    column bolded, right-to-left scripts laid out right to left), can edit cells, and OKs the data back to the caller, who re-supplies it as initialText to re-display it next time.'''

    def __init__(self, title, initialText, parent=None):

        super().__init__(parent)

        # Build the widgets from the pyuic-generated class.
        self.ui = Ui_PasteDataDialog()
        self.ui.setupUi(self)

        self.setWindowTitle(title)

        # Hook up button signals to methods.
        self.ui.pasteButton.clicked.connect(self.onPaste)
        self.ui.clearButton.clicked.connect(self.onClear)

        if initialText:
            self.populateFromText(initialText)

    def onPaste(self):

        clipboard = QApplication.clipboard()
        self.populateFromText(clipboard.text() if clipboard else '')

    def onClear(self):

        self.ui.table.setRowCount(0)
        self.ui.table.setColumnCount(0)

    def populateFromText(self, text: str):
        '''Break the tab-separated text into the grid and apply the display niceties: blanked header labels, bolding of record-start rows and the row-label column, right-to-left
        layout for right-to-left scripts, and sizing the window to show the whole table.'''

        rows = [line.split('\t') for line in text.strip().split('\n') if line]

        if not rows:

            self.onClear()
            return

        # If any character on the first row belongs to a right-to-left script (detected via Unicode's bidirectional category rather than hard-coded ranges), lay the table out right
        # to left; otherwise use the normal left-to-right direction.
        firstRowIsRtl = any(unicodedata.bidirectional(ch) in ('R', 'AL') for cell in rows[0] for ch in cell)
        self.ui.table.setLayoutDirection(Qt.LayoutDirection.RightToLeft if firstRowIsRtl else Qt.LayoutDirection.LeftToRight)

        numRows = len(rows)
        numCols = max(len(row) for row in rows)
        self.ui.table.setRowCount(numRows)
        self.ui.table.setColumnCount(numCols)

        # Populate the grid (missing trailing cells become empty items so every cell is editable and serializes cleanly).
        for rowIdx, row in enumerate(rows):

            for colIdx in range(numCols):
                self.ui.table.setItem(rowIdx, colIdx, QTableWidgetItem(row[colIdx].strip() if colIdx < len(row) else ''))

        # Keep the headers visible but blank out the automatic numbering.
        self.ui.table.setVerticalHeaderLabels([''] * numRows)
        self.ui.table.setHorizontalHeaderLabels([''] * numCols)

        self.applyBoldFormatting(rows, numCols)

        # Resize columns after bolding, so the wider bold text is accounted for.
        self.ui.table.resizeColumnsToContents()
        self.resizeWindowToFitTable()

    def applyBoldFormatting(self, rows, numCols: int):
        '''Look for a "new record" indicator column: one that's blank on some rows (continuation rows of a record) and filled on others (the row that starts a new record). A column
        like this signals a grouped layout of row-labeled data blocks; plain rectangular data won't have one, and gets no bold formatting.'''

        indicatorCol = next((col for col in range(numCols) if any(col >= len(row) or not row[col].strip() for row in rows) and any(col < len(row) and row[col].strip() for row in rows)), None)

        if indicatorCol is None:
            return

        # Bold every row where the indicator column starts a new record.
        for rowIdx, row in enumerate(rows):

            if indicatorCol < len(row) and row[indicatorCol].strip():

                for colIdx in range(numCols):
                    self.setBold(rowIdx, colIdx)

        # The "row header" column is the first fully-populated column after the indicator - e.g. the repeated "Word" / "Morphemes" / "Lex. Entries" labels on every row of a record.
        headerCol = next((col for col in range(indicatorCol + 1, numCols) if all(col < len(row) and row[col].strip() for row in rows)), None)

        if headerCol is not None:

            for rowIdx in range(len(rows)):
                self.setBold(rowIdx, headerCol)

    def setBold(self, row: int, col: int):

        item = self.ui.table.item(row, col)

        if item:

            font = item.font()
            font.setBold(True)
            item.setFont(font)

    def resizeWindowToFitTable(self):

        table = self.ui.table

        width = sum(table.columnWidth(col) for col in range(table.columnCount()))
        height = sum(table.rowHeight(row) for row in range(table.rowCount()))

        # The (blanked but still visible) headers take up their own space, which the column/row sums above don't include - add the vertical header's width and the horizontal header's
        # height, or the table has no room for them and shows scrollbars instead.
        vHeader = table.verticalHeader()
        hHeader = table.horizontalHeader()

        if vHeader and vHeader.isVisible():
            width += vHeader.width()

        if hHeader and hHeader.isVisible():
            height += hHeader.height()

        # The frame border, plus a couple of extra pixels to absorb any rounding between the column-width sum and what Qt actually needs to render without a scrollbar.
        width += table.frameWidth() * 2 + 2
        height += table.frameWidth() * 2 + 2

        # Require the table to be exactly this size, let the dialog's layout grow to fit it, then drop the minimum back down so the window stays freely resizeable.
        table.setMinimumSize(width, height)
        self.adjustSize()
        table.setMinimumSize(0, 0)

    def dataText(self) -> str:
        '''Serialize the grid back to tab-separated text (including any in-cell edits), dropping trailing empty cells on each row and dropping empty rows. Empty grid -> empty string,
        which the caller treats as "no data given".'''

        lines = []

        for row in range(self.ui.table.rowCount()):

            cells = []

            for col in range(self.ui.table.columnCount()):

                item = self.ui.table.item(row, col)
                cells.append(item.text() if item else '')

            line = '\t'.join(cells).rstrip('\t')

            if line.strip():
                lines.append(line)

        return '\n'.join(lines)

class GenerateWorker(QObject):
    '''Runs a slow AIRules call off the UI thread: `fn` (generateValidatedRule for the create/modify modes, explainRule for the explain mode) is called with `params`.'''

    finished = pyqtSignal(object)   # AIRules.RuleResult, or (explanation, language) for the explain task
    failed = pyqtSignal(str)
    rateLimited = pyqtSignal(str)   # friendly "try again in N s" message

    def __init__(self, fn, params: dict):

        super().__init__()
        self.fn = fn
        self.params = params

    def run(self):

        try:
            result = self.fn(**self.params)
            self.finished.emit(result)

        except AIRules.RateLimitError as err:
            self.rateLimited.emit(str(err))

        except Exception as err:
            self.failed.emit(str(err))

class WorkOnRulesWithAIDlg(QDialog):
    '''Create, modify, or explain one Apertium transfer rule with AI assistance. Two tabs: "Create new rule" (describe it, then Create) and "Modify or explain an existing rule" (pick a
    rule - its preview shows at once on the left - then Modify with a description, or Explain in a chosen language). The layout comes from WorkOnRulesWithAIWindow.ui (pyuic).'''

    # The FLExTrans interface languages, mapped to the English language name we put in the prompt when the user leaves the Explanation-language box blank.
    UI_LANG_NAMES = {'en': 'English', 'de': 'German', 'es': 'Spanish', 'fr': 'French'}

    def __init__(self, transferPath, ruleNames, ruleXmlByComment, systemInstruction, defsSummary, projectData, engine, dtdPath, compilerExe, parent=None):

        super().__init__(parent)

        # Everything the generation needs, injected by the caller.
        self.transferPath = transferPath
        self.ruleNames = ruleNames
        # {comment: rule-XML} for every rule in the file, so clicking a rule in the picker renders its preview from memory instead of re-reading and re-parsing the whole transfer file
        # each time. Rebuilt from the file whenever the list is reloaded (Refresh Rules / after an approve).
        self.ruleXmlByComment = ruleXmlByComment or {}
        self.systemInstruction = systemInstruction
        self.defsSummary = defsSummary
        self.projectData = projectData
        self.engine = engine
        self.dtdPath = dtdPath
        self.compilerExe = compilerExe

        # Draft/preview state. currentTask names what the preview currently shows ('create'/'modify'/'explain'/'select'); currentRuleXml and currentTargetComment describe the rule
        # selected in the modify/explain list; ruleResult holds a generated create/modify draft; draftWritten marks it approved so Explain doesn't re-offer to write it.
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.currentTask = 'create'
        self.draftWritten = False
        self.genThread = None
        self.worker = None

        # Interlinearized example data pasted via the Source/Target Data buttons; sent with every request when non-empty. After a rule is approved, the next create Generate asks whether
        # to keep the (possibly no longer relevant) data.
        self.sourceDataText = ''
        self.targetDataText = ''
        self.askAboutDataOnNextGenerate = False

        # Temp directories created for Open-in-XXE. Each holds a candidate copy of the transfer file that XXE opens, so it must outlive the click; they're removed when the dialog closes.
        self.xxeTempDirs = []

        # Build the widgets from the pyuic-generated class.
        self.ui = Ui_WorkOnRulesWithAI()
        self.ui.setupUi(self)

        if FTPaths:
            self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        # The preview should get the bulk of the window. Keep the tab area from claiming more vertical space than its controls need (Maximum policy) and send every extra pixel to the
        # preview pane below it (stretch 0 for the tabs, 1 for the preview). The initial split is set to the tab area's minimum height in showEvent, once the real size hints are known.
        self.ui.modeTabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.ui.mainSplitter.setStretchFactor(0, 0)
        self.ui.mainSplitter.setStretchFactor(1, 1)
        self.splitterSized = False

        self.ui.ruleList.addItems(self.ruleNames)

        # Start with no rule selected: the preview shows its placeholder until the user actually picks a rule (or creates/modifies/explains one) - we don't auto-select the first rule.
        self.ui.ruleList.setCurrentRow(-1)

        # The preview QWebEngineView is created lazily (see ensurePreview) and only added to the window when a preview is actually shown: an embedded Chromium view installs input hooks
        # that can steal arrow/navigation keys from sibling text widgets. Constructing it is slow (Chromium starts up), so we warm it up just after the window appears - see warmUpPreview.
        self.preview = None

        # Current magnification of the preview text, driven by the Zoom +/- buttons. Remembered here (not just on the view) so it survives re-rendering and view rebuilds; applied to the
        # view whenever it's created or shown - see setPreviewZoom / ensurePreview.
        self.previewZoomFactor = 1.0

        # Hook up the widgets. The window stays open across successive edits: only Close (and the window's X) end it.
        self.ui.createButton.clicked.connect(self.onCreate)
        self.ui.modifyButton.clicked.connect(self.onModify)
        self.ui.explainButton.clicked.connect(self.onExplain)
        self.ui.ruleList.currentItemChanged.connect(self.onRuleSelected)
        self.ui.modeTabs.currentChanged.connect(self.onTabChanged)
        self.ui.refreshButton.clicked.connect(self.onRefreshRules)
        self.ui.approveButton.clicked.connect(self.onApprove)
        self.ui.xxeButton.clicked.connect(self.onOpenInXxe)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.changeKeyButton.clicked.connect(self.onChangeApiKey)
        self.ui.zoomIncreaseButton.clicked.connect(self.onZoomIncrease)
        self.ui.zoomDecreaseButton.clicked.connect(self.onZoomDecrease)

        # The Source/Target Data buttons appear once on each tab (Create and Modify/Explain), but the example data they edit is global - the same data is sent with every request. Group
        # each side's buttons so the check-mark label and the busy-time enable/disable can be kept in step across both copies (see updateDataButtons / setBusy).
        self.sourceDataButtons = [self.ui.createSourceDataButton, self.ui.modifySourceDataButton]
        self.targetDataButtons = [self.ui.createTargetDataButton, self.ui.modifyTargetDataButton]

        for button in self.sourceDataButtons:

            button.clicked.connect(self.onSourceData)

        for button in self.targetDataButtons:

            button.clicked.connect(self.onTargetData)

    def showEvent(self, event):

        super().showEvent(event)
        self.ui.descriptionEdit.setFocus()

        # Collapse the tab area to its minimum height the first time the window is shown, so the preview pane gets all the remaining vertical space. This is done here rather than in
        # __init__ because the widgets' real size hints aren't known until the window is laid out; the guard keeps a later re-show from undoing a splitter drag the user has since made.
        if not self.splitterSized:

            self.ui.mainSplitter.setSizes([self.ui.modeTabs.minimumSizeHint().height(), self.height()])
            self.splitterSized = True

        # Warm up the (slow-to-construct) web view once the window is on screen, so the first preview isn't held up by Chromium starting. singleShot(0) lets the window paint first, then
        # builds the view during the next idle moment - by the time the user navigates to a rule the engine is ready. warmUpPreview is idempotent, so repeated shows don't rebuild it.
        QTimer.singleShot(0, self.warmUpPreview)

    def warmUpPreview(self):
        '''Construct the QWebEngineView ahead of time (paying the Chromium start-up cost) but leave it out of the window until a preview is actually rendered (ensurePreview adds it),
        so it can't steal arrow keys from the description boxes before it's needed.'''

        if self.preview is None:
            self.preview = QWebEngineView()
            self.preview.setZoomFactor(self.previewZoomFactor)

    def closeEvent(self, event):
        '''Close (the Close button and the window's X both route here). If a generation is still running, wait for it to finish first so the worker thread isn't destroyed mid-run - which
        would crash - when the dialog is garbage-collected after the event loop returns.'''

        self.cleanupThread()

        # Best-effort removal of the Open-in-XXE scratch folders. ignore_errors covers the case where XXE still has a file open (Windows won't delete it then) - it's left behind rather
        # than raising, but that's the rare exception, not the norm.
        for workDir in self.xxeTempDirs:
            shutil.rmtree(workDir, ignore_errors=True)

        super().closeEvent(event)

    # --- interface language ----------------------------------------------

    def interfaceLangCode(self) -> str:
        '''The FLExTrans interface-language code ('en'/'de'/'es'/'fr'), used to localize the preview labels. Falls back to English when Utils/FTConfig aren't available (standalone runs).'''

        try:
            import Utils
            return Utils.getInterfaceLangCode() or 'en'

        except Exception:
            return 'en'

    def interfaceLanguageName(self) -> str:
        '''The interface language as a language name (e.g. "German"), the default explanation language when the user hasn't typed one in the Explanation-language box.'''

        return self.UI_LANG_NAMES.get(self.interfaceLangCode(), 'English')

    def explanationLanguage(self) -> str:
        '''The language to write an explanation in: what the user typed in the Explanation-language box, or the interface language when that box is blank.'''

        typed = self.ui.explainLangEdit.text().strip()
        return typed or self.interfaceLanguageName()

    # --- rule list -------------------------------------------------------

    def selectedRuleComment(self):

        item = self.ui.ruleList.currentItem()
        return item.text() if item else None

    def onTabChanged(self, index):
        '''Switching tabs starts fresh: blank the preview and drop any pending draft, so a rule shown on one tab isn't left over on another. On the Create tab it simply stays blank; on
        the Modify/Explain tab we also clear the rule list and keep focus out of it, so nothing is previewed until the user actually clicks a rule (see clearRuleSelection for why).'''

        self.blankPreview()
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.draftWritten = False
        self.currentTask = 'create' if self.ui.modeTabs.widget(index) is self.ui.createTab else 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)
        self.ui.statusLabel.setText('')

        if self.ui.modeTabs.widget(index) is self.ui.modifyTab:

            # A QListWidget auto-selects (and so previews) its first row when the tab switch moves keyboard focus into it. That runs synchronously as part of the tab change, so undo it on
            # the next event-loop turn: clear the selection and move the cursor to the description box, leaving the list unselected until the user deliberately clicks a rule.
            QTimer.singleShot(0, self.clearRuleSelection)

    def clearRuleSelection(self):
        '''Leave the rule list with nothing selected and the preview blank, and put the cursor in the change-description box so focus doesn't sit on the list (which would re-select its
        first row). Runs just after a switch to the Modify/Explain tab to cancel the automatic first-row selection Qt makes when focus lands on the list.'''

        self.ui.ruleList.setCurrentRow(-1)
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.blankPreview()
        self.ui.modifyDescriptionEdit.setFocus()

    def onRuleSelected(self, current=None, previous=None):
        '''A rule was picked in the modify/explain list: fetch its XML, show it immediately in the left preview pane, and discard any pending draft (a previously shown before/after or
        explanation no longer applies to the newly selected rule).'''

        comment = self.selectedRuleComment()

        if not comment:
            return

        self.currentTargetComment = comment
        self.currentRuleXml = self.ruleXmlByComment.get(comment)

        # A newly selected rule invalidates any pending draft.
        self.ruleResult = None
        self.draftWritten = False
        self.currentTask = 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)

        if self.currentRuleXml:

            self.ensurePreview().setHtml(TransferPreview.renderRulePreviewHtml(self.currentRuleXml, lang=self.interfaceLangCode()))
            self.ui.statusLabel.setText('')

    def reloadRules(self):
        '''Re-read the transfer file so the rule picker and the definition summary sent to the AI reflect the current on-disk state. Called after a rule is approved (a new/changed rule
        must appear in the list) and by the Refresh Rules button (the user may have edited the file in another window). The current picker selection is preserved when it still exists.'''

        try:
            defs = AIRules.extractExistingDefs(self.transferPath)

        except Exception as err:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Refresh Rules'), _translate('WorkOnRulesWithAI', 'Could not re-read the transfer rules file: {err}').format(err=err))
            return

        self.ruleNames = defs['ruleNames']
        self.ruleXmlByComment = defs['ruleXml']
        self.defsSummary = defs['summaryText']

        previous = self.selectedRuleComment()

        self.ui.ruleList.clear()
        self.ui.ruleList.addItems(self.ruleNames)

        # Restore the previous selection if that rule still exists (this re-fires onRuleSelected, re-previewing the rule).
        if previous:

            matches = self.ui.ruleList.findItems(previous, Qt.MatchFlag.MatchExactly)

            if matches:
                self.ui.ruleList.setCurrentItem(matches[0])

    def onRefreshRules(self):

        self.reloadRules()
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rule list refreshed ({n} rules).').format(n=len(self.ruleNames)))

    # --- example data ----------------------------------------------------

    def editData(self, title: str, currentText: str) -> str:
        '''Open the paste grid seeded with the currently saved data. OK returns the (possibly edited) grid serialized back to text; Cancel keeps what was saved before.'''

        dlg = PasteDataDlg(title, currentText, self)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.dataText()

        return currentText

    def onSourceData(self):

        self.sourceDataText = self.editData(_translate('WorkOnRulesWithAI', 'Source Language Data'), self.sourceDataText)
        self.updateDataButtons()

        # The user just looked at / refreshed the data deliberately, so don't second-guess them with the keep-the-data question on the next Generate.
        self.askAboutDataOnNextGenerate = False

    def onTargetData(self):

        self.targetDataText = self.editData(_translate('WorkOnRulesWithAI', 'Target Language Data'), self.targetDataText)
        self.updateDataButtons()
        self.askAboutDataOnNextGenerate = False

    def updateDataButtons(self):
        '''A check mark at the end of a data button's label shows that data has been given on that side. Both tabs' copies of each button carry the same label so the mark shows wherever
        the user looks.'''

        sourceLabel = _translate('WorkOnRulesWithAI', 'Source Data…') + (' ✓' if self.sourceDataText else '')
        targetLabel = _translate('WorkOnRulesWithAI', 'Target Data…') + (' ✓' if self.targetDataText else '')

        for button in self.sourceDataButtons:

            button.setText(sourceLabel)

        for button in self.targetDataButtons:

            button.setText(targetLabel)

    # --- the three actions -----------------------------------------------

    def onCreate(self):

        description = self.ui.descriptionEdit.toPlainText().strip()

        if not description:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the rule you want.'))
            return

        # Starting a new rule after approving the previous one: the example data given for that rule may not fit this one, so ask once whether to keep it. Reopening the data grids
        # disarms the question (onSourceData/onTargetData).
        if self.askAboutDataOnNextGenerate and (self.sourceDataText or self.targetDataText):

            answer = QMessageBox.question(self, _translate('WorkOnRulesWithAI', 'Example language data'), _translate('WorkOnRulesWithAI', 'Do you want to keep the example language data you provided for the previous rule?'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

            if answer == QMessageBox.StandardButton.No:

                self.sourceDataText = ''
                self.targetDataText = ''
                self.updateDataButtons()

            self.askAboutDataOnNextGenerate = False

        self.currentRuleXml = None
        self.currentTargetComment = None
        userContent = AIRules.buildUserContent('create', description, self.defsSummary, self.projectData, None, 'English', self.sourceDataText, self.targetDataText)
        self.startRuleGeneration('create', userContent, None)

    def onModify(self):

        if not self.currentRuleXml:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to modify.'))
            return

        description = self.ui.modifyDescriptionEdit.toPlainText().strip()

        if not description:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the change you want.'))
            return

        userContent = AIRules.buildUserContent('modify', description, self.defsSummary, self.projectData, self.currentRuleXml, 'English', self.sourceDataText, self.targetDataText)
        self.startRuleGeneration('modify', userContent, self.currentTargetComment)

    def onExplain(self):

        if not self.currentRuleXml:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to explain.'))
            return

        # If an unapproved modified rule is showing on the right, the explanation would replace it - offer to write it to the file first so the work isn't lost.
        if self.ruleResult and self.ruleResult.valid and not self.draftWritten and self.currentTask == 'modify':

            answer = QMessageBox.question(self, _translate('WorkOnRulesWithAI', 'Unapproved rule'), _translate('WorkOnRulesWithAI', 'You have a modified rule that has not been written to the transfer file. Approve and write it before explaining?'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel, QMessageBox.StandardButton.Yes)

            if answer == QMessageBox.StandardButton.Cancel:
                return

            if answer == QMessageBox.StandardButton.Yes and not self.approveDraft():

                # The write failed (approveDraft already showed the error); don't discard the draft by explaining over it.
                return

        explainLang = self.explanationLanguage()
        userContent = AIRules.buildUserContent('explain', '', self.defsSummary, self.projectData, self.currentRuleXml, explainLang, self.sourceDataText, self.targetDataText)

        self.currentTask = 'explain'
        self.startWorker(AIRules.explainRule, {'engine': self.engine, 'systemInstruction': self.systemInstruction, 'userContent': userContent}, _translate('WorkOnRulesWithAI', 'Explaining…'))

    def startRuleGeneration(self, mode: str, userContent: str, targetComment):
        '''Kick off a create or modify generation (generateValidatedRule) on the worker thread, remembering the target rule so a later Approve writes to the right place.'''

        # The authorship-stamp sentences, localized to the FLExTrans UI language. Whole sentences (with a {when} placeholder) so they translate cleanly regardless of word order.
        authorshipComments = {
            'added':    _translate('WorkOnRulesWithAI', 'The AI Assistant added this rule on {when}.'),
            'modified': _translate('WorkOnRulesWithAI', 'The AI Assistant modified this rule on {when}.'),
        }

        # Localize the stamp's date/time to the interface language the same way the testbed log does (Utils.LocalizedDateTimeFormatter). The custom Qt format gives a spelled-out,
        # localized month without the weekday/seconds/timezone the long format adds. If Utils/FTConfig aren't available (standalone runs), leave it None so AIRules uses its English fallback.
        whenStr = None

        try:
            import Utils
            from PyQt6.QtCore import QDateTime
            whenStr = Utils.LocalizedDateTimeFormatter().formatDateTime(QDateTime.currentDateTime(), 'd MMMM yyyy HH:mm')

        except Exception:
            pass

        params = {
            'engine': self.engine,
            'systemInstruction': self.systemInstruction,
            'userContent': userContent,
            'transferPath': self.transferPath,
            'dtdPath': self.dtdPath,
            'mode': mode,
            'targetComment': targetComment,
            'compilerExe': self.compilerExe,
            'authorshipComments': authorshipComments,
            'whenStr': whenStr,
        }

        self.currentTask = mode
        self.currentTargetComment = targetComment
        self.startWorker(AIRules.generateValidatedRule, params, _translate('WorkOnRulesWithAI', 'Generating…'))

    def startWorker(self, fn, params: dict, statusText: str):
        '''Disable the controls and run `fn(**params)` on a background thread, reporting `statusText` while it runs.'''

        self.setBusy(True)
        self.ui.statusLabel.setText(statusText)

        self.genThread = QThread()
        self.worker = GenerateWorker(fn, params)
        self.worker.moveToThread(self.genThread)
        self.genThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.onGenerateFinished)
        self.worker.failed.connect(self.onGenerateFailed)
        self.worker.rateLimited.connect(self.onRateLimited)
        self.genThread.start()

    def setBusy(self, busy: bool):
        '''Disable input while a generation runs. Close stays enabled (its closeEvent waits for the thread). Approve/XXE are only turned back on by the result handlers, not here.'''

        # Disabling the tab widget also disables everything inside it, so the Create/Modify/Explain buttons and both tabs' Source/Target Data buttons (which now live inside the tabs) are
        # covered here without touching them individually.
        self.ui.modeTabs.setEnabled(not busy)
        self.ui.changeKeyButton.setEnabled(not busy)

        if busy:

            self.ui.approveButton.setEnabled(False)
            self.ui.xxeButton.setEnabled(False)

    def cleanupThread(self):

        if self.genThread:

            self.genThread.quit()
            self.genThread.wait()
            self.genThread = None
            self.worker = None

    def ensurePreview(self):
        '''Return the QWebEngineView ready to render into, creating it if warmUpPreview hasn't yet, and adding it to the window (replacing the placeholder) the first time a preview is
        actually shown.'''

        if self.preview is None:
            self.preview = QWebEngineView()
            self.preview.setZoomFactor(self.previewZoomFactor)

        # The view is created unparented by warmUpPreview; addWidget reparents it into the preview area. Only do this once - after that it already lives in the layout.
        if self.preview.parent() is None:
            self.ui.previewLayout.addWidget(self.preview)

        # Show the view and hide the placeholder. Done every time (not just on the first add) because blankPreview hides the view and re-shows the placeholder when the preview is cleared.
        self.ui.previewPlaceholder.hide()
        self.preview.show()

        return self.preview

    def onZoomIncrease(self):
        '''Magnify the preview text one step (Zoom + button).'''

        self.setPreviewZoom(self.previewZoomFactor * ZOOM_FACTOR_STEP)

    def onZoomDecrease(self):
        '''Reduce the preview text one step (Zoom - button).'''

        self.setPreviewZoom(self.previewZoomFactor / ZOOM_FACTOR_STEP)

    def setPreviewZoom(self, factor):
        '''Clamp the requested zoom to the web view's supported range, remember it, and apply it to the view if it exists. Remembering it here means a preview rendered (or a view rebuilt)
        after the user has zoomed comes up at the chosen magnification rather than resetting to 1.0.'''

        self.previewZoomFactor = max(MIN_PREVIEW_ZOOM, min(MAX_PREVIEW_ZOOM, factor))

        if self.preview is not None:
            self.preview.setZoomFactor(self.previewZoomFactor)

    def blankPreview(self):
        '''Clear the preview area back to its placeholder text: hide the web view (if it exists) and show the placeholder. Used when switching tabs so no stale rule is left showing.'''

        if self.preview is not None:
            self.preview.hide()

        self.ui.previewPlaceholder.show()

    # --- results ---------------------------------------------------------

    def onGenerateFinished(self, result):

        self.cleanupThread()
        self.setBusy(False)

        # The explain task returns (explanation, language) and produces no rule: render the rule beside its explanation and leave Approve / Open-in-XXE disabled (there is nothing to
        # write or open).
        if self.currentTask == 'explain':

            explanation, language = result
            self.ruleResult = None

            self.ensurePreview().setHtml(TransferPreview.renderExplanationHtml(self.currentRuleXml or '', explanation, lang=language))
            self.ui.approveButton.setEnabled(False)
            self.ui.xxeButton.setEnabled(False)
            self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Explanation generated.'))
            return

        self.ruleResult = result
        self.draftWritten = False

        # Render the preview: the original rule on the left and the modified rule on the right for a modify; a single rule for a create. The label language follows the language of the
        # user's request, as reported by the model.
        comparisonMissing = self.currentTask == 'modify' and not self.currentRuleXml

        if self.currentTask == 'modify' and self.currentRuleXml:
            html = TransferPreview.renderComparisonHtml(self.currentRuleXml, result.ruleXml, lang=result.language)
        else:
            html = TransferPreview.renderRuleHtml(result.ruleXml, result.newDefs, lang=result.language)

        self.ensurePreview().setHtml(html)
        self.ui.xxeButton.setEnabled(True)

        # A modify with no original rule to compare against (shouldn't normally happen - the list selection supplies it) would otherwise silently drop the before/after and the change
        # highlighting, showing only the new rule. Say why, so the missing comparison isn't mistaken for "nothing changed".
        if comparisonMissing:
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Comparison unavailable'), _translate('WorkOnRulesWithAI', 'Could not load the original rule to show a side-by-side comparison, so only the modified rule is shown.'))

        if result.valid:

            self.ui.approveButton.setEnabled(True)
            self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Valid rule generated (attempt {n}). {expl}').format(n=result.attempts, expl=result.explanation))
        else:
            self.ui.approveButton.setEnabled(False)
            self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Could not produce a valid rule after {n} attempts. See errors; you can still open it in XXE.').format(n=result.attempts))
            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Validation failed'), result.errors)

    def onGenerateFailed(self, message):

        self.cleanupThread()
        self.setBusy(False)
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generation failed.'))
        QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error'), message)

    def onRateLimited(self, message):

        self.cleanupThread()
        self.setBusy(False)
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rate limited - try again shortly.'))
        QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Rate limited'), message)

    def onChangeApiKey(self):

        provider = self.engine.provider
        newKey = promptForApiKey(provider, self)

        if newKey:

            # Rebuild the client so the new key takes effect immediately, not just next run.
            self.engine.client = provider.makeClient(newKey)
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'API key'),
                                    _translate('WorkOnRulesWithAI', 'Your {provider} API key was updated.').format(provider=provider.displayName))

    # --- writing to the file ---------------------------------------------

    def onApprove(self):

        self.approveDraft()

    def approveDraft(self) -> bool:
        '''Write the current create/modify draft to the transfer file after backing it up. Returns True on success. Shared by the Approve button and the "approve before explaining"
        prompt. The window stays open; Approve disables until the next generation so the same rule can't be written twice, and the rule list is re-read so the new/changed rule shows.'''

        if not (self.ruleResult and self.ruleResult.valid):
            return False

        mode = 'modify' if self.currentTask == 'modify' else 'create'
        targetComment = self.currentTargetComment if mode == 'modify' else None

        try:
            backupPath = AIRules.applyRule(self.transferPath, self.ruleResult, mode, targetComment)

        except Exception as err:

            QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error writing rule'), str(err))
            return False

        self.draftWritten = True
        self.ui.approveButton.setEnabled(False)
        self.reloadRules()

        # This rule is done; if example data was given for it, the next create Generate will ask whether to keep that data for the next rule.
        if self.sourceDataText or self.targetDataText:
            self.askAboutDataOnNextGenerate = True

        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rule written to the transfer file (backup: {backup}). Generate or select another rule to continue.').format(backup=os.path.basename(backupPath)))
        return True

    def onOpenInXxe(self):

        if not self.ruleResult:
            return

        mode = 'modify' if self.currentTask == 'modify' else 'create'
        targetComment = self.currentTargetComment if mode == 'modify' else None

        # This temp file has to outlive the call (XXE opens it after we return), so we can't delete it here. Track its directory and clean it up when the dialog closes - bounding the
        # leak to one folder per Open-in-XXE click within a single session instead of forever.
        workDir = tempfile.mkdtemp(prefix='airules_xxe_')
        self.xxeTempDirs.append(workDir)
        shutil.copyfile(self.dtdPath, os.path.join(workDir, 'transfer.dtd'))
        tempPath = AIRules.spliceIntoTemp(self.transferPath, self.ruleResult.ruleXml, self.ruleResult.newDefs, mode, targetComment, workDir)

        try:
            os.startfile(tempPath)   # Windows: open with the registered handler (XXE)

        except Exception:
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Open in XXE'), _translate('WorkOnRulesWithAI', 'A copy with your rule was written to:\n{path}\n\nOpen it in XXE to review.').format(path=tempPath))
