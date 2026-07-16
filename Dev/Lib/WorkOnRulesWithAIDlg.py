#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.22 - 7/16/26 - Ron Lockwood
#    The preview pane's right-click context menu is disabled (the rendered rule is read-only, so the browser Back/Reload/Save menu doesn't apply); the QWebEngineView is now built in one
#    shared createPreviewView helper that sets the zoom and the NoContextMenu policy.
#
#   Version 3.16.21 - 7/16/26 - Ron Lockwood
#    Macro support: the Modify/Explain tab now has Rules and Macros sub-tabs (two lists; macros can be modified and explained like rules), and the Create tab gained a "Create a macro
#    instead of a rule" checkbox. Macros a rule/macro calls, and macros the user's description names (partial match), are sent with the prompt; a named macro that isn't found blocks the
#    send with a message listing the file's macros. Clicking another rule/macro, or switching the Rules/Macros sub-tabs, now offers to approve an unwritten draft first (like tab switches).
#
#   Version 3.16.20 - 7/10/26 - Ron Lockwood
#    Dropped the transfer.dtd dependency: neither Open-in-XXE (XXE resolves the DOCTYPE via its own addon DTD) nor the validation loop (apertium-preprocess-transfer needs no DTD) required it,
#    so the dtdPath constructor parameter and the beside-the-temp-file copy are gone.
#
#   Version 3.16.19 - 7/10/26 - Ron Lockwood
#    The dialog now always opens on the Create tab, set explicitly in code (pyuic had baked in the Modify tab as the startup tab because it was the active tab when the .ui was last saved).
#
#   Version 3.16.18 - 7/10/26 - Ron Lockwood
#    Switching tabs with an unwritten rule (either a new rule made on the Create tab or a modified rule made on the Modify/Explain tab) now offers to approve and write it first, in either
#    direction, so the draft isn't silently discarded. onRuleSelected now ignores the row the list auto-selects when it gains focus during a tab switch (that spurious selection was nulling
#    the pending draft before the offer could be made). The Explain "approve before explaining" prompt is now Yes/No (the Cancel button was removed).
#
#   Version 3.16.17 - 7/9/26 - Ron Lockwood
#    The interface-language names now come from UILanguages.py (the new single authoritative UI-language list) instead of a local UI_LANG_NAMES dict.
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
import UILanguages
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
    '''Create, modify, or explain one Apertium transfer rule or macro with AI assistance. Two tabs: "Create new rule" (describe it, then Create - with a checkbox to create a macro
    instead) and "Modify or explain an existing rule or macro" (pick a rule or macro from the Rules/Macros sub-tabs - its preview shows at once on the left - then Modify with a
    description, or Explain in a chosen language). The layout comes from WorkOnRulesWithAIWindow.ui (pyuic).'''

    def __init__(self, transferPath, ruleNames, ruleXmlByComment, macroNames, macroXmlByName, systemInstruction, defsSummary, projectData, engine, compilerExe, parent=None):

        super().__init__(parent)

        # Everything the generation needs, injected by the caller.
        self.transferPath = transferPath
        self.ruleNames = ruleNames
        # {comment: rule-XML} for every rule in the file, so clicking a rule in the picker renders its preview from memory instead of re-reading and re-parsing the whole transfer file
        # each time. Rebuilt from the file whenever the list is reloaded (Refresh Rules / after an approve).
        self.ruleXmlByComment = ruleXmlByComment or {}
        # Same idea for macros: the names fill the Macros list, and {name: def-macro-XML} renders a picked macro's preview and supplies macro definitions for the prompt.
        self.macroNames = macroNames or []
        self.macroXmlByName = macroXmlByName or {}
        self.systemInstruction = systemInstruction
        self.defsSummary = defsSummary
        self.projectData = projectData
        self.engine = engine
        self.compilerExe = compilerExe

        # Draft/preview state. currentTask names what the preview currently shows ('create'/'modify'/'explain'/'select'); currentRuleXml and currentTargetComment describe the rule or
        # macro selected in the modify/explain lists (for a macro, currentTargetComment holds its n name); currentIsMacro says whether the selection/draft is a macro rather than a rule;
        # ruleResult holds a generated create/modify draft; draftWritten marks it approved so Explain doesn't re-offer to write it.
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.currentTask = 'create'
        self.currentIsMacro = False
        self.draftWritten = False
        self.genThread = None
        self.worker = None

        # True from the moment a tab is clicked until onTabChanged finishes. While set, onRuleSelected ignores the rule the Modify/Explain list auto-selects when it receives focus during
        # the switch - that spurious selection would otherwise null the pending draft (self.ruleResult) before onTabChanged can offer to write it. See onTabBarClicked / onRuleSelected.
        self.switchingTabs = False

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

        # Always open on the Create tab. Don't rely on the .ui for this: pyuic bakes in whichever tab was active when the .ui was last saved in Qt Designer, so a later Designer edit could
        # silently reopen us on the Modify tab. Setting it here (before the currentChanged signal is connected below, so onTabChanged doesn't fire) makes the starting tab explicit and stable.
        self.ui.modeTabs.setCurrentIndex(0)

        if FTPaths:
            self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        # The preview should get the bulk of the window. Keep the tab area from claiming more vertical space than its controls need (Maximum policy) and send every extra pixel to the
        # preview pane below it (stretch 0 for the tabs, 1 for the preview). The initial split is set to the tab area's minimum height in showEvent, once the real size hints are known.
        self.ui.modeTabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.ui.mainSplitter.setStretchFactor(0, 0)
        self.ui.mainSplitter.setStretchFactor(1, 1)
        self.splitterSized = False

        self.ui.ruleList.addItems(self.ruleNames)
        self.ui.macroList.addItems(self.macroNames)

        # Start with no rule or macro selected: the preview shows its placeholder until the user actually picks one (or creates/modifies/explains one) - we don't auto-select a first row.
        self.ui.ruleList.setCurrentRow(-1)
        self.ui.macroList.setCurrentRow(-1)

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
        self.ui.macroList.currentItemChanged.connect(self.onMacroSelected)
        self.ui.modeTabs.currentChanged.connect(self.onTabChanged)
        # tabBarClicked fires on the click, before the tab actually changes (and before the list's focus-driven auto-select), so it's where we mark that a switch is starting. The same
        # applies to the Rules/Macros sub-tabs on the Modify/Explain tab.
        self.ui.modeTabs.tabBarClicked.connect(self.onTabBarClicked)
        self.ui.listTabs.currentChanged.connect(self.onListTabChanged)
        self.ui.listTabs.tabBarClicked.connect(self.onListTabBarClicked)
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

    def createPreviewView(self):
        '''Create the preview QWebEngineView, applying the remembered zoom and disabling the right-click context menu. The preview is a read-only rendering of the rule, so the default
        browser menu (Back / Reload / Save / View source) is meaningless here; NoContextMenu suppresses it. Shared by warmUpPreview and ensurePreview so the view is always built the same way.'''

        view = QWebEngineView()
        view.setZoomFactor(self.previewZoomFactor)
        view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        return view

    def warmUpPreview(self):
        '''Construct the QWebEngineView ahead of time (paying the Chromium start-up cost) but leave it out of the window until a preview is actually rendered (ensurePreview adds it),
        so it can't steal arrow keys from the description boxes before it's needed.'''

        if self.preview is None:
            self.preview = self.createPreviewView()

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
        '''The interface language as an English language name (e.g. "German"), the default explanation language when the user hasn't typed one in the Explanation-language box.'''

        return UILanguages.englishNameForCode(self.interfaceLangCode())

    def explanationLanguage(self) -> str:
        '''The language to write an explanation in: what the user typed in the Explanation-language box, or the interface language when that box is blank.'''

        typed = self.ui.explainLangEdit.text().strip()
        return typed or self.interfaceLanguageName()

    # --- rule list -------------------------------------------------------

    def selectedRuleComment(self):

        item = self.ui.ruleList.currentItem()
        return item.text() if item else None

    def selectedMacroName(self):

        item = self.ui.macroList.currentItem()
        return item.text() if item else None

    def activeListIsMacros(self) -> bool:
        '''Whether the Macros sub-tab (rather than Rules) is the one showing on the Modify/Explain tab.'''

        return self.ui.listTabs.currentWidget() is self.ui.macrosTab

    def offerToWritePendingDraft(self) -> bool:
        '''If a generated rule/macro draft hasn't been written to the file yet, offer to approve and write it before the caller discards it (switching tabs, switching the Rules/Macros
        sub-tabs, clicking another rule or macro, or explaining over a modified draft). Returns False only when the user asked for the write and it failed (the caller should then stop
        rather than discard the draft); True otherwise. The list-selection handlers are suppressed while the write reloads the lists, so the reload's re-selection can't re-enter here.'''

        if not (self.ruleResult and self.ruleResult.valid and not self.draftWritten and self.currentTask in ('create', 'modify')):
            return True

        if self.currentIsMacro:

            title = _translate('WorkOnRulesWithAI', 'Unapproved macro')
            message = _translate('WorkOnRulesWithAI', 'You have a macro that has not been written to the transfer file. Approve and write it before continuing?')
        else:

            title = _translate('WorkOnRulesWithAI', 'Unapproved rule')
            message = _translate('WorkOnRulesWithAI', 'You have a rule that has not been written to the transfer file. Approve and write it before continuing?')

        answer = QMessageBox.question(self, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

        if answer != QMessageBox.StandardButton.Yes:
            return True

        # approveDraft reloads the lists, which re-fires the selection signals; switchingTabs makes onRuleSelected/onMacroSelected ignore those synthetic re-selections (restored to its
        # prior value afterwards, since a tab-switch caller may still be mid-switch).
        prior = self.switchingTabs
        self.switchingTabs = True

        try:
            return self.approveDraft()

        finally:
            self.switchingTabs = prior

    def onTabBarClicked(self, index):
        '''The user clicked a tab. This fires before the tab actually changes and before the Modify/Explain list's focus-driven auto-select, so it's our chance to mark that a switch is
        starting - which tells onRuleSelected to ignore that spurious auto-select and so preserve any pending draft for onTabChanged's save offer. A click on the current tab is not a
        switch, so it clears the flag rather than setting it (otherwise it could stay set and suppress a later genuine rule click).'''

        self.switchingTabs = index != self.ui.modeTabs.currentIndex()

    def onTabChanged(self, index):
        '''Switching tabs starts fresh: blank the preview and drop any pending draft, so a rule shown on one tab isn't left over on another. On the Create tab it simply stays blank; on
        the Modify/Explain tab we also clear the rule list and keep focus out of it, so nothing is previewed until the user actually clicks a rule (see clearRuleSelection for why).'''

        # If a generated rule/macro hasn't been written to the file yet, switching tabs would discard it below. Offer to approve and write it first so the work isn't lost. This covers
        # both directions - a draft made on the Create tab and one made on the Modify/Explain tab (currentTask tells approveDraft which) - and mirrors the offer Explain makes.
        self.offerToWritePendingDraft()

        self.blankPreview()
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.currentIsMacro = False
        self.draftWritten = False
        self.currentTask = 'create' if self.ui.modeTabs.widget(index) is self.ui.createTab else 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)
        self.ui.statusLabel.setText('')

        # The switch is over; a rule the user now clicks in the list is a genuine selection again, so stop suppressing onRuleSelected.
        self.switchingTabs = False

        if self.ui.modeTabs.widget(index) is self.ui.modifyTab:

            # A QListWidget auto-selects (and so previews) its first row when the tab switch moves keyboard focus into it. That runs synchronously as part of the tab change, so undo it on
            # the next event-loop turn: clear the selection and move the cursor to the description box, leaving the list unselected until the user deliberately clicks a rule.
            QTimer.singleShot(0, self.clearRuleSelection)

    def onListTabBarClicked(self, index):
        '''A click on the Rules/Macros sub-tabs, before the switch happens: same spurious-auto-select suppression as the main tabs (see onTabBarClicked).'''

        self.switchingTabs = index != self.ui.listTabs.currentIndex()

    def onListTabChanged(self, index):
        '''Switching between the Rules and Macros lists starts fresh, like a main tab switch: offer to write a pending draft first, then blank the preview and clear both selections so
        nothing stale is left showing.'''

        self.offerToWritePendingDraft()

        self.blankPreview()
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.currentIsMacro = False
        self.draftWritten = False
        self.currentTask = 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)
        self.ui.statusLabel.setText('')

        # The switch is over; a rule/macro the user now clicks is a genuine selection again.
        self.switchingTabs = False

        # Undo the automatic first-row selection the newly shown list makes when focus lands on it, the same way a switch to the Modify/Explain tab does.
        QTimer.singleShot(0, self.clearRuleSelection)

    def clearRuleSelection(self):
        '''Leave the rule and macro lists with nothing selected and the preview blank, and put the cursor in the change-description box so focus doesn't sit on a list (which would
        re-select its first row). Runs just after a switch to the Modify/Explain tab (or between the Rules/Macros sub-tabs) to cancel the automatic first-row selection Qt makes when
        focus lands on a list.'''

        self.ui.ruleList.setCurrentRow(-1)
        self.ui.macroList.setCurrentRow(-1)
        self.currentRuleXml = None
        self.currentTargetComment = None
        self.blankPreview()
        self.ui.modifyDescriptionEdit.setFocus()

    def onRuleSelected(self, current=None, previous=None):
        '''A rule was picked in the modify/explain Rules list: fetch its XML, show it immediately in the left preview pane, and discard any pending draft (a previously shown before/after
        or explanation no longer applies to the newly selected rule) - after offering to write that draft, so clicking another rule can't silently lose generated work.'''

        # Ignore the row the list auto-selects when it gains focus during a tab switch. It isn't a real pick, and acting on it would null the pending draft (below) before onTabChanged can
        # offer to write it. clearRuleSelection, scheduled by onTabChanged, then leaves the list unselected. A rule the user clicks after the switch has settled comes through normally.
        if self.switchingTabs:
            return

        comment = self.selectedRuleComment()

        if not comment:
            return

        # Clicking a different rule discards the pending draft below, so make the same offer to approve and write it that a tab switch makes.
        self.offerToWritePendingDraft()

        self.currentTargetComment = comment
        self.currentRuleXml = self.ruleXmlByComment.get(comment)
        self.currentIsMacro = False

        # A newly selected rule invalidates any pending draft.
        self.ruleResult = None
        self.draftWritten = False
        self.currentTask = 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)

        if self.currentRuleXml:

            self.ensurePreview().setHtml(TransferPreview.renderRulePreviewHtml(self.currentRuleXml, lang=self.interfaceLangCode()))
            self.ui.statusLabel.setText('')

    def onMacroSelected(self, current=None, previous=None):
        '''A macro was picked in the modify/explain Macros list: the def-macro counterpart of onRuleSelected - show its preview at once and (after the write offer) discard any pending draft.'''

        if self.switchingTabs:
            return

        name = self.selectedMacroName()

        if not name:
            return

        self.offerToWritePendingDraft()

        self.currentTargetComment = name
        self.currentRuleXml = self.macroXmlByName.get(name)
        self.currentIsMacro = True

        # A newly selected macro invalidates any pending draft.
        self.ruleResult = None
        self.draftWritten = False
        self.currentTask = 'select'
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)

        if self.currentRuleXml:

            self.ensurePreview().setHtml(TransferPreview.renderRulePreviewHtml(self.currentRuleXml, lang=self.interfaceLangCode()))
            self.ui.statusLabel.setText('')

    def reloadRules(self):
        '''Re-read the transfer file so the rule and macro pickers and the definition summary sent to the AI reflect the current on-disk state. Called after a rule/macro is approved (the
        new/changed one must appear in its list) and by the Refresh Rules button (the user may have edited the file in another window). Each picker's current selection is preserved when
        it still exists.'''

        try:
            defs = AIRules.extractExistingDefs(self.transferPath)

        except Exception as err:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Refresh Rules'), _translate('WorkOnRulesWithAI', 'Could not re-read the transfer rules file: {err}').format(err=err))
            return

        self.ruleNames = defs['ruleNames']
        self.ruleXmlByComment = defs['ruleXml']
        self.macroNames = defs['macros']
        self.macroXmlByName = defs['macroXml']
        self.defsSummary = defs['summaryText']

        previousRule = self.selectedRuleComment()
        previousMacro = self.selectedMacroName()

        self.ui.ruleList.clear()
        self.ui.ruleList.addItems(self.ruleNames)
        self.ui.macroList.clear()
        self.ui.macroList.addItems(self.macroNames)

        # Restore the visible list's previous selection if that rule/macro still exists (this re-fires onRuleSelected/onMacroSelected, re-previewing it). Only the visible list is
        # restored: re-selecting the hidden one too would fire its handler as well, and whichever ran last would steal the current-selection state from the list the user is looking at.
        if previousMacro and self.activeListIsMacros():

            matches = self.ui.macroList.findItems(previousMacro, Qt.MatchFlag.MatchExactly)

            if matches:
                self.ui.macroList.setCurrentItem(matches[0])

        elif previousRule and not self.activeListIsMacros():

            matches = self.ui.ruleList.findItems(previousRule, Qt.MatchFlag.MatchExactly)

            if matches:
                self.ui.ruleList.setCurrentItem(matches[0])

    def onRefreshRules(self):

        self.reloadRules()
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rule list refreshed ({n} rules, {m} macros).').format(n=len(self.ruleNames), m=len(self.macroNames)))

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

    def gatherMacrosForPrompt(self, description: str, xmlText) -> tuple:
        '''Collect the macro definitions to send with a request: every macro the rule/macro being worked on calls (recursively), plus any macro the description names (partial,
        case-insensitive match) along with what those call in turn. Returns (macrosText, missingTokens): macrosText is the blank-line-joined XML of the macros found, and missingTokens
        are description tokens that clearly name a macro but match none in the file - the caller warns and does not send the prompt.'''

        # The macro being modified/explained is itself already in the prompt as CURRENT MACRO, so it is excluded from the reference list.
        excludeNames = [self.currentTargetComment] if self.currentIsMacro and self.currentTargetComment else []

        names = AIRules.collectCalledMacros(xmlText, self.macroXmlByName, excludeNames) if xmlText else []

        found, missing = AIRules.findMacroMentions(description, list(self.macroXmlByName)) if description else ([], [])

        # A macro named in the description is included too - and so is whatever it calls, so the model sees the whole chain.
        for name in found:

            if name not in names and name not in excludeNames:
                names.append(name)

            names.extend(AIRules.collectCalledMacros(self.macroXmlByName.get(name, ''), self.macroXmlByName, excludeNames + names))

        macrosText = '\n\n'.join(self.macroXmlByName[name] for name in names if name in self.macroXmlByName)
        return macrosText, missing

    def warnMissingMacros(self, missing) -> None:
        '''Tell the user which macro name(s) in their description matched nothing in the rule file (and what macros the file does have), so they can fix the description. The prompt was
        not sent.'''

        available = ', '.join(self.macroNames) if self.macroNames else _translate('WorkOnRulesWithAI', '(none)')

        QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Macro not found'),
                            _translate('WorkOnRulesWithAI', 'Your description mentions a macro that is not in the transfer rules file: {missing}\n\nMacros in the file: {names}\n\nNothing was sent to the AI. Correct the macro name and try again.').format(missing=', '.join(missing), names=available))

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

        isMacro = self.ui.createMacroCheckbox.isChecked()

        # If the description names a macro, its definition is sent along; a name that matches nothing blocks the send so the user can correct it.
        macrosText, missing = self.gatherMacrosForPrompt(description, None)

        if missing:

            self.warnMissingMacros(missing)
            return

        self.currentRuleXml = None
        self.currentTargetComment = None
        userContent = AIRules.buildUserContent('create', description, self.defsSummary, self.projectData, None, 'English', self.sourceDataText, self.targetDataText, isMacro=isMacro, macrosText=macrosText)
        self.startRuleGeneration('create', userContent, None, isMacro)

    def onModify(self):

        if not self.currentRuleXml:

            if self.activeListIsMacros():
                QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No macro selected'), _translate('WorkOnRulesWithAI', 'Please select a macro to modify.'))
            else:
                QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to modify.'))

            return

        description = self.ui.modifyDescriptionEdit.toPlainText().strip()

        if not description:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the change you want.'))
            return

        # Send along the macros this rule/macro calls and any the description names; a named macro that matches nothing blocks the send so the user can correct it.
        macrosText, missing = self.gatherMacrosForPrompt(description, self.currentRuleXml)

        if missing:

            self.warnMissingMacros(missing)
            return

        userContent = AIRules.buildUserContent('modify', description, self.defsSummary, self.projectData, self.currentRuleXml, 'English', self.sourceDataText, self.targetDataText, isMacro=self.currentIsMacro, macrosText=macrosText)
        self.startRuleGeneration('modify', userContent, self.currentTargetComment, self.currentIsMacro)

    def onExplain(self):

        if not self.currentRuleXml:

            if self.activeListIsMacros():
                QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No macro selected'), _translate('WorkOnRulesWithAI', 'Please select a macro to explain.'))
            else:
                QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to explain.'))

            return

        # If an unapproved draft is showing on the right, the explanation would replace it - offer to write it to the file first so the work isn't lost. A False return means the user
        # asked for the write and it failed (the error was already shown); don't discard the draft by explaining over it.
        if not self.offerToWritePendingDraft():
            return

        # The macros this rule/macro calls go into the prompt so the explanation can say what each call actually does.
        macrosText = self.gatherMacrosForPrompt('', self.currentRuleXml)[0]

        explainLang = self.explanationLanguage()
        userContent = AIRules.buildUserContent('explain', '', self.defsSummary, self.projectData, self.currentRuleXml, explainLang, self.sourceDataText, self.targetDataText, isMacro=self.currentIsMacro, macrosText=macrosText)

        self.currentTask = 'explain'
        self.startWorker(AIRules.explainRule, {'engine': self.engine, 'systemInstruction': self.systemInstruction, 'userContent': userContent}, _translate('WorkOnRulesWithAI', 'Explaining…'))

    def startRuleGeneration(self, mode: str, userContent: str, targetComment, isMacro: bool = False):
        '''Kick off a create or modify generation (generateValidatedRule) on the worker thread, remembering the target rule/macro so a later Approve writes to the right place.'''

        # The authorship-stamp sentences, localized to the FLExTrans UI language. Whole sentences (with a {when} placeholder) so they translate cleanly regardless of word order.
        authorshipComments = {
            'added':         _translate('WorkOnRulesWithAI', 'The AI Assistant added this rule on {when}.'),
            'modified':      _translate('WorkOnRulesWithAI', 'The AI Assistant modified this rule on {when}.'),
            'addedMacro':    _translate('WorkOnRulesWithAI', 'The AI Assistant added this macro on {when}.'),
            'modifiedMacro': _translate('WorkOnRulesWithAI', 'The AI Assistant modified this macro on {when}.'),
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
            'mode': mode,
            'targetComment': targetComment,
            'compilerExe': self.compilerExe,
            'authorshipComments': authorshipComments,
            'whenStr': whenStr,
            'isMacro': isMacro,
        }

        self.currentTask = mode
        self.currentTargetComment = targetComment
        self.currentIsMacro = isMacro
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
            self.preview = self.createPreviewView()

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

            if self.currentIsMacro:
                self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Valid macro generated (attempt {n}). {expl}').format(n=result.attempts, expl=result.explanation))
            else:
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
        '''Write the current create/modify draft (a rule or a macro) to the transfer file after backing it up. Returns True on success. Shared by the Approve button and the "approve
        before continuing" offers. The window stays open; Approve disables until the next generation so the same draft can't be written twice, and the lists are re-read so the
        new/changed rule or macro shows.'''

        if not (self.ruleResult and self.ruleResult.valid):
            return False

        mode = 'modify' if self.currentTask == 'modify' else 'create'
        targetComment = self.currentTargetComment if mode == 'modify' else None

        try:
            backupPath = AIRules.applyRule(self.transferPath, self.ruleResult, mode, targetComment, self.currentIsMacro)

        except Exception as err:

            QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error writing rule'), str(err))
            return False

        self.draftWritten = True
        self.ui.approveButton.setEnabled(False)
        self.reloadRules()

        # This rule/macro is done; if example data was given for it, the next create Generate will ask whether to keep that data for the next one.
        if self.sourceDataText or self.targetDataText:
            self.askAboutDataOnNextGenerate = True

        if self.currentIsMacro:
            self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Macro written to the transfer file (backup: {backup}). Generate or select another rule or macro to continue.').format(backup=os.path.basename(backupPath)))
        else:
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
        # No need to drop a transfer.dtd beside the temp file: XXE resolves the DOCTYPE against the copy in its own ApertiumTransfer addon (dtds/transfer.dtd), so the file's relative DTD
        # reference is satisfied without a local copy. (The AI validation loop still copies the DTD into its own scratch dir, because apertium-preprocess-transfer resolves it relative to the file.)
        tempPath = AIRules.spliceIntoTemp(self.transferPath, self.ruleResult.ruleXml, self.ruleResult.newDefs, mode, targetComment, workDir, self.currentIsMacro)

        try:
            os.startfile(tempPath)   # Windows: open with the registered handler (XXE)

        except Exception:
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Open in XXE'), _translate('WorkOnRulesWithAI', 'A copy with your rule was written to:\n{path}\n\nOpen it in XXE to review.').format(path=tempPath))
