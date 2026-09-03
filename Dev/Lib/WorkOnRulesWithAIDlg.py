#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.31 - 9/3/26 - Ron Lockwood
#    Added an Open Rule File button, which opens the transfer rules file in the XML editor for a hand edit. It offers to write a pending draft first (an outside edit would leave that draft
#    unwritable) and asks for Refresh Rules afterwards, since nothing here can tell when the editor is done. It sits with Open a Temporary Version in XXE in a new right-aligned row across the
#    top of the window, which is also where that button moved to, keeping the bottom row short. The three buttons that act on files - both of those and Approve & Write to Rule File - now carry
#    tooltips saying what they open or write, and that the previous version of the rule file is saved first. Every widget added here now lives in WorkOnRulesWithAIWindow.ui rather than being
#    built in code, so the whole window can be maintained in a widget designer.
#
#   Version 3.16.30 - 9/3/26 - Ron Lockwood
#    Added the code description block at the top with an overview, the tabs, draft protection, threading, the preview and code structure, replacing the stub description.
#
#   Version 3.16.29 - 9/3/26 - Ron Lockwood
#    The bottom row now says which AI service the requests go to and carries an editable Model picker, so a request can be retried on a different model without closing the window and paying
#    the FLEx start-up again. The choice is applied when a request is sent (a model belonging to another provider is refused there), and a model the provider actually accepted becomes the
#    AIRulesModel default for next time - written only after a reply comes back, so a typo or a retired name never reaches the settings file.
#
#   Version 3.16.28 - 9/3/26 - Ron Lockwood
#    A model the provider no longer serves (HTTP 404) now gets its own plain-language dialog naming the model and pointing at the AI Model setting, instead of the SDK's raw "model does not
#    exist" error: the worker relays AIRules.UnknownModelError through a new unknownModel signal so the sentence can be shown in the interface language.
#
#   Version 3.16.27 - 8/21/26 - Ron Lockwood
#    Starting a new rule now offers to save an unapproved rule preview first.
#
#   Version 3.16.26 - 7/28/26 - Ron Lockwood
#    The Modify/Explain tab's Rules and Macros lists now get a minimum height sized to show at least three rows (the collapsed tab area had left room for only two); ensureListsShowThreeRows
#    sets it in showEvent, just before the tab area is collapsed to its minimum-size hint. Lexical units in an AI explanation are now color-coded (via TransferPreview / Testbed) like the viewer.
#
#   Version 3.16.25 - 7/27/26 - Ron Lockwood
#    Fixes #1470. A rule that fails validation no longer confronts the user with the raw parser text (e.g. expat's baffling "mismatched tag: line N, column M"): the dialog now leads with a
#    plain-language summary of what went wrong plus a "rephrase as one clear sentence and try again" nudge, and tucks the raw parser/compiler errors behind the message box's "Show Details" button.
#
#   Version 3.16.24 - 7/27/26 - Ron Lockwood
#    Closing the window now offers to approve and write an unapproved create/modify draft first (the same offer a tab switch or rule click makes), so the draft isn't silently discarded;
#    if the write is requested and fails, the window stays open so the draft can be retried rather than lost.
#
#   Version 3.16.23 - 7/22/26 - Ron Lockwood
#    Fixes #1459. The Create/Modify descriptions are cleaned before being sent to the AI: line endings are unified and blank lines (including a stray one left by pressing Enter before clicking Create)
#    are dropped, so that empty trailing line no longer pushes the model into malformed output and its baffling "XML is not well-formed" validation error.
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
#
#   OVERVIEW (AI generated, then edited)
#
#   This is the whole user interface of the AI Rule Studio module - the window the user actually works in. AIRules.py does the thinking (prompts, provider calls, validation, writing the
#   transfer file) and knows nothing about Qt; this file does the talking: it collects what the user wants, hands it to AIRules on a background thread, renders what came back, and asks the
#   questions that keep work from being lost. The split is deliberate and worth preserving - it is why AIRules can be unit-tested with no Qt, no FLEx and no network, and why every
#   user-visible sentence is translatable here rather than baked into the engine.
#
#   Everything the window needs is injected by MainFunction (rule and macro names, their XML, the system instruction, the definition summary, the project data, the Engine, the compiler
#   path), so the dialog can also be exercised standalone with hand-made data. It stays open across successive edits: only Close and the window's X end it, and each generation leaves the
#   window ready for the next one.
#
#   THE TABS
#
#   "Create new rule" takes a description (plus a checkbox to make a macro instead). "Modify or explain an existing rule or macro" has Rules and Macros sub-tabs; clicking an entry previews
#   it at once from the injected {comment: XML} / {name: XML} maps - no re-reading the transfer file - and then Modify (with a description) or Explain (in a chosen language) acts on it.
#   currentTask ('create'/'modify'/'explain'/'select') records what the preview is currently showing, and currentIsMacro whether a macro rather than a rule is in play; nearly every handler
#   branches on those two.
#
#   PROTECTING AN UNAPPROVED DRAFT
#
#   A generated rule exists only in memory until Approve writes it, so anything that would replace the preview first calls offerToWritePendingDraft: switching tabs, switching the
#   Rules/Macros sub-tabs, clicking another rule or macro, explaining over a modified draft, and closing the window. It returns False only when the user asked for the write and the write
#   failed, which tells the caller to stop rather than throw the draft away.
#
#   The switchingTabs flag guards a trap here. A QListWidget auto-selects its first row when a tab switch moves keyboard focus into it, synchronously, as part of the tab change - and that
#   spurious selection would null the pending draft before onTabChanged could offer to save it. So tabBarClicked (which fires before the switch) sets the flag, the selection handlers ignore
#   selections while it is set, and a QTimer.singleShot(0) undoes the auto-selection on the next event-loop turn. It looks like defensive clutter; it isn't.
#
#   THREADING
#
#   A provider call takes many seconds, so GenerateWorker runs it on a QThread and reports back through four signals: finished, failed, rateLimited, and unknownModel. The last two exist so
#   the two provider errors that a user can actually act on get a plain-language dialog instead of raw SDK text - a 429 says how long to wait, a 404 on the model name says which model is
#   missing and which setting to change. unknownModel carries the model and provider names rather than a finished sentence, because the sentence has to be composed here to be translatable
#   (AIRules is Qt-free and can only produce the English one). Everything else arrives on `failed` and is shown as-is.
#
#   PROVIDER AND MODEL
#
#   The button row says which service the requests go to and lets the model be changed. The split is deliberate: switching provider would mean a different API key, a different SDK and a fresh
#   consent question (the consent the user gave names the service), so the provider stays a readout and lives in the FLExTrans settings, while the model - the thing worth varying, since retrying
#   a request on a stronger model is the usual reason to want a change mid-session - is editable here. Editable rather than a fixed list, so a model released after this FLExTrans can be typed in.
#
#   Two rules keep that honest. The choice is applied in startWorker, not when the box changes, so what gets sent is whatever the box says at the moment the user clicks Create/Modify/Explain, and
#   a model that belongs to a different provider is refused there (it could only draw a 404). And the AIRulesModel setting is rewritten only once a reply has actually come back - see
#   rememberWorkingModel - so a model the provider accepted becomes the default for next time while a typo, which dies at the 404, never reaches the settings file.
#
#   THE PREVIEW
#
#   The preview is a QWebEngineView rendering HTML from TransferPreview - one rule for a create, a side-by-side before/after for a modify, the rule beside its prose for an explain. Two
#   things about it are not obvious. It is constructed lazily and kept out of the window until a preview is actually shown, because an embedded Chromium view installs input hooks that steal
#   arrow keys from the description boxes; and because constructing it is slow, showEvent warms it up on the next idle moment so the first preview isn't held up by Chromium starting. The
#   zoom factor is remembered on the dialog, not just on the view, so it survives re-rendering and view rebuilds.
#
#   CODE STRUCTURE
#
#   promptForApiKey asks for a key and stores it in the provider's credential-vault slot (used both on first run and by the Change API key button). PasteDataDlg is the paste-and-review grid
#   for interlinearized example data, bolding record-start rows and the label column and laying out right-to-left scripts accordingly. GenerateWorker is the background-thread wrapper
#   described above.
#
#   Two buttons at the top right open the XML editor and are easy to confuse. Open a Temporary Version in XXE opens a throw-away copy in a temp folder with the current draft spliced in, for
#   inspecting a rule the AI produced (the folder is cleaned up on close); Open Rule File opens the project's real transfer file for a hand edit. The second offers to write a pending draft first,
#   because an outside edit moves the text spans applyRule matches against and would leave that draft unwritable.
#
#   Every widget in this window is defined in WorkOnRulesWithAIWindow.ui and reached through self.ui, including the provider readout and the model picker in the bottom row - nothing is
#   constructed in code here. That is deliberate and worth keeping: it means the layout can be opened in a widget designer and rearranged without reading this file, and the labels and tooltips
#   are extracted for translation from the generated WorkOnRulesWithAIWindow.py. Only text that depends on a run-time value (the provider's display name, the model list) is set here.
#
#   WorkOnRulesWithAIDlg is the rest of the file, roughly in this order: __init__ (inject state, build the pyuic widgets, wire the signals, add the provider/model readout), showEvent and the
#   list/splitter sizing, the preview view helpers (createPreviewView, warmUpPreview, ensurePreview, blankPreview, the zoom trio), closeEvent (which offers to write a pending draft and
#   cleans up the Open-in-XXE temp folders), the small selection accessors, offerToWritePendingDraft, the tab and list-selection handlers, reloadRules, the Source/Target Data handlers, the
#   prompt helpers (cleanDescription, gatherMacrosForPrompt, warnMissingMacros), the three action handlers (onCreate, onModify, onExplain) which all funnel into startRuleGeneration ->
#   startWorker, then the result handlers (onGenerateFinished, showValidationFailed, onGenerateFailed, onRateLimited, onUnknownModel), the model-picker trio (populateModelCombo,
#   applyModelChoice, rememberWorkingModel), onChangeApiKey, and finally approveDraft (the only thing here that causes the real transfer file to be written - through AIRules.applyRule, which
#   backs it up first), onOpenRuleFile and onOpenInXxe.
#

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
    unknownModel = pyqtSignal(str, str)   # (model, provider display name) - the two fields the localized "model not available" message needs

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

        # The fields travel instead of the message text so the dialog can say it in the interface language (AIRules stays Qt-free and can only produce the English sentence).
        except AIRules.UnknownModelError as err:
            self.unknownModel.emit(err.model, err.providerDisplay)

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
        self.ui.openRuleFileButton.clicked.connect(self.onOpenRuleFile)
        self.ui.zoomIncreaseButton.clicked.connect(self.onZoomIncrease)
        self.ui.zoomDecreaseButton.clicked.connect(self.onZoomDecrease)

        # Which AI service the requests go to, and which of its models. The provider is a fixed readout: switching it would mean a different API key, a different SDK and a fresh consent
        # question (the consent the user gave names the service), so it stays in the FLExTrans settings. The model IS changeable here, because retrying the same request on a stronger model
        # is the usual reason to want a change mid-session, and closing the window to visit the settings would mean paying the slow start-up - re-opening the target FLEx project and
        # re-gathering the project data - all over again. The widgets themselves (providerLabel, modelLabel, modelCombo) come from the .ui; only the text that depends on run-time values is
        # set here.
        self.ui.providerLabel.setText(_translate('WorkOnRulesWithAI', 'Provider: {provider}').format(provider=self.engine.provider.displayName))
        self.populateModelCombo()

        # The model the settings asked for, so a switch can be told from a non-switch. It moves forward only once a model has actually worked - see rememberWorkingModel.
        self.configuredModel = self.engine.model

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

            # Give the Rules/Macros lists enough height to show at least three rows before the tab area is collapsed to its minimum height below. Done here (not __init__) so the per-row
            # measurement is taken once the widgets are laid out, and before the setSizes call so the taller lists are already reflected in the tab area's minimum-size hint it reads.
            self.ensureListsShowThreeRows()

            self.ui.mainSplitter.setSizes([self.ui.modeTabs.minimumSizeHint().height(), self.height()])
            self.splitterSized = True

        # Warm up the (slow-to-construct) web view once the window is on screen, so the first preview isn't held up by Chromium starting. singleShot(0) lets the window paint first, then
        # builds the view during the next idle moment - by the time the user navigates to a rule the engine is ready. warmUpPreview is idempotent, so repeated shows don't rebuild it.
        QTimer.singleShot(0, self.warmUpPreview)

    def ensureListsShowThreeRows(self, rowsToShow=3):
        '''Give the Modify/Explain tab's Rules and Macros lists a minimum height tall enough to show at least `rowsToShow` rows at once. The tab area is sized to its minimum-size hint (see
        showEvent), and with no floor on the list height that hint left room for only two rows. The per-row height comes from the list's own row size hint (falling back to the font height
        when the list is empty), so this stays correct across fonts and screen scaling; a QTabWidget wraps each list, so the raised minimum flows up through it into the tab area's hint.'''

        for listWidget in (self.ui.ruleList, self.ui.macroList):

            rowHeight = listWidget.sizeHintForRow(0) if listWidget.count() else listWidget.fontMetrics().height()

            # sizeHintForRow returns -1 for an empty list on some styles; fall back to the font height so we still have a sensible per-row figure.
            if rowHeight <= 0:
                rowHeight = listWidget.fontMetrics().height()

            # The row heights, plus the list's frame on top and bottom and a few pixels of slack, so the requested number of rows are fully visible rather than clipped at the last one.
            listWidget.setMinimumHeight(rowHeight * rowsToShow + listWidget.frameWidth() * 2 + 6)

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
        '''Close (the Close button and the window's X both route here). If a generated rule/macro hasn't been written to the file yet, offer to approve and write it first so closing the
        window doesn't silently discard the draft (the same offer a tab switch or rule click makes). If the user asked for the write and it failed, keep the window open so the draft isn't
        lost. Then, if a generation is still running, wait for it to finish first so the worker thread isn't destroyed mid-run - which would crash - when the dialog is garbage-collected
        after the event loop returns.'''

        # Offer to write a pending draft before the close discards it. A False return means the user asked for the write and it failed (the error was already shown); leave the window open
        # so they can retry rather than lose the draft.

        if not self.offerToWritePendingDraft():

            event.ignore()
            return

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

    def cleanDescription(self, text: str) -> str:
        '''Normalize a description the user typed before it is sent to the AI: unify line endings, strip trailing whitespace from each line, and drop every blank line (leading, trailing,
        and interior). Pressing Enter before clicking Create - a natural mistake, since the Create button looks focused - leaves a stray empty line in the box; that blank line can push the
        model into malformed output whose "XML is not well-formed" validation error is baffling to an ordinary user, so we clean it out here rather than let it reach the AI.'''

        # Unify Windows (\r\n) and old-Mac (\r) line endings to a plain '\n' so splitting and re-joining below behaves the same on every platform.
        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

        # Strip trailing whitespace from each line, then keep only the lines that actually carry content - this removes blank lines at the top and bottom as well as any blank line in the middle.
        lines = [line.rstrip() for line in lines if line.strip()]

        return '\n'.join(lines)

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

        description = self.cleanDescription(self.ui.descriptionEdit.toPlainText())

        if not description:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the rule you want.'))
            return

        # Creating a new rule replaces the current preview and draft, so offer to write an unapproved one before continuing. Whether the user says Yes or No, go ahead and go on.
        self.offerToWritePendingDraft()

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

        description = self.cleanDescription(self.ui.modifyDescriptionEdit.toPlainText())

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
        '''Disable the controls and run `fn(**params)` on a background thread, reporting `statusText` while it runs. The model the picker names is applied first - params carries the Engine
        itself, so setting the model on it here is what the request will use - and a model this provider cannot run stops the run before anything is disabled or sent.'''

        if not self.applyModelChoice():
            return

        self.setBusy(True)
        self.ui.statusLabel.setText(statusText)

        self.genThread = QThread()
        self.worker = GenerateWorker(fn, params)
        self.worker.moveToThread(self.genThread)
        self.genThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.onGenerateFinished)
        self.worker.failed.connect(self.onGenerateFailed)
        self.worker.rateLimited.connect(self.onRateLimited)
        self.worker.unknownModel.connect(self.onUnknownModel)
        self.genThread.start()

    def setBusy(self, busy: bool):
        '''Disable input while a generation runs. Close stays enabled (its closeEvent waits for the thread). Approve/XXE are only turned back on by the result handlers, not here.'''

        # Disabling the tab widget also disables everything inside it, so the Create/Modify/Explain buttons and both tabs' Source/Target Data buttons (which now live inside the tabs) are
        # covered here without touching them individually.
        self.ui.modeTabs.setEnabled(not busy)
        self.ui.changeKeyButton.setEnabled(not busy)
        self.ui.modelCombo.setEnabled(not busy)
        self.ui.openRuleFileButton.setEnabled(not busy)

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

        # A reply came back, so this model works: make it the default for next time. Done for the explain task too - it is the same provider call.
        self.rememberWorkingModel()

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
            self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Could not build a valid rule after {n} attempts. You can still open it in XXE to inspect it.').format(n=result.attempts))
            self.showValidationFailed(result.errors)

    def showValidationFailed(self, errors):
        '''Explain a failed validation in plain language. The raw parser/compiler text (e.g. expat's baffling "mismatched tag: line N, column M") is kept out of the main message - it goes
        behind the "Show Details" button - so an ordinary user reads what went wrong and what to try next, while the technical detail stays one click away for a bug report.'''

        # Lead with a non-technical sentence describing the failure, chosen the same way AIRules.friendlyValidationSummary classifies it, but translated to the interface language here.
        text = errors or ''

        if 'XML is not well-formed' in text:
            summary = _translate('WorkOnRulesWithAI', "The AI's rule wasn't put together correctly - its XML tags didn't match up - so FLExTrans couldn't use it.")

        elif 'apertium-preprocess-transfer failed' in text:
            summary = _translate('WorkOnRulesWithAI', "The AI's rule didn't fit the transfer-rule format FLExTrans requires, so it couldn't be used.")

        else:
            summary = _translate('WorkOnRulesWithAI', "The AI couldn't build a valid rule from this request.")

        # Actionable next step. Odd or contradictory wording is the usual trigger, so steer the user toward a single, plain sentence and trying again.
        guidance = _translate('WorkOnRulesWithAI', 'Try rephrasing your description as a single, clear sentence and generate again.')

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(_translate('WorkOnRulesWithAI', 'Could not build a valid rule'))
        box.setText(summary + '\n\n' + guidance)

        # Keep the raw errors available for a bug report or a technical user, but collapsed behind "Show Details" so they don't confront the average user with parser jargon.
        if text:
            box.setDetailedText(text)

        box.exec()

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

    def onUnknownModel(self, model, providerDisplay):
        '''The provider answered 404 for the configured model name - nearly always a model retired since the AI Model setting was chosen. Say that in plain words and name the setting to
        change, rather than showing the SDK's raw "the model does not exist or you do not have access to it" text, which tells an ordinary user nothing about what to do next.'''

        self.cleanupThread()
        self.setBusy(False)
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generation failed.'))

        summary = _translate('WorkOnRulesWithAI', '{provider} has no model named {model}. It may have been retired, or your API key may not have access to it.').format(provider=providerDisplay, model=model)
        guidance = _translate('WorkOnRulesWithAI', 'Choose a different model in the Model box at the bottom of this window, then try again.')

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(_translate('WorkOnRulesWithAI', 'Model not available'))
        box.setText(summary + '\n\n' + guidance)
        box.exec()

    def populateModelCombo(self):
        '''Fill the model picker with the current provider's models, keeping the model in use selectable even when it is not one of them - a hand-entered name, or one from a config written
        by a newer FLExTrans - exactly as the Settings tool's model combo does. The list is only a convenience; what gets sent is whatever text the box holds when a request is made.'''

        models = list(self.engine.provider.models)

        if self.engine.model and self.engine.model not in models:
            models.append(self.engine.model)

        self.ui.modelCombo.clear()
        self.ui.modelCombo.addItems(models)
        self.ui.modelCombo.setCurrentText(self.engine.model or '')

    def applyModelChoice(self) -> bool:
        '''Point the engine at whatever model the picker now names, checked the way the Settings tool checks the pairing: a model belonging to a *different* provider is refused, since this
        provider could only answer 404 for it, while a name no provider claims is allowed through - it may simply be newer than this release's lists. Returns False when the request must not
        be sent, having already said why. Called from startWorker, so every create, modify and explain goes through it.'''

        model = self.ui.modelCombo.currentText().strip()

        if not model:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No model'), _translate('WorkOnRulesWithAI', 'Choose or type the model to use in the Model box.'))
            return False

        owner = AIRules.findModelOwner(model)

        if owner is not None and owner is not self.engine.provider:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Wrong provider for this model'),
                                _translate('WorkOnRulesWithAI', '{model} is a {owner} model, so {provider} cannot run it. Choose one of the {provider} models in the Model box.').format(model=model, owner=owner.displayName, provider=self.engine.provider.displayName))
            return False

        self.engine.model = model
        return True

    def rememberWorkingModel(self):
        '''Make the model that just worked the default for the next run. Only a model the provider has actually accepted is written: reaching here means a reply came back, so the name
        exists and this key can use it, while a typo or a retired name raises the 404 instead and never reaches the settings file. Nothing is written when the model still matches the
        settings, so an unchanged run leaves the file alone (and a blank AIRulesModel stays blank until the user picks something). writeConfigValue rewrites only the AIRulesModel line, so
        no other setting can be disturbed. ReadConfig is imported here rather than at the top because it needs FTPaths, whose absence the dialog deliberately tolerates so it can be run
        standalone; a write failure is swallowed for the same reason the write waits for success - it must never break a generation that has already worked.'''

        if not self.engine.model or self.engine.model == self.configuredModel:
            return

        try:
            import ReadConfig

            if ReadConfig.writeConfigValue(None, ReadConfig.AI_RULES_MODEL, self.engine.model, createIfMissing=True):
                self.configuredModel = self.engine.model

        except Exception:
            pass

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

    def onOpenRuleFile(self):
        '''Open the real transfer rules file in the XML editor so the user can make a change by hand. Two things are done first. A pending draft is offered for writing, because this window holds
        the file's text spans from when the draft was generated: an outside edit would leave applyRule matching against a file that has since moved, and it refuses rather than guess where the
        rule now is - so the draft would be stuck. And the lists are left alone deliberately: nothing here can tell when the editor is finished, so the status line asks for Refresh Rules rather
        than pretending to know. os.startfile hands the file to whatever is registered for .t1x (XXE) instead of hunting for xxe.exe, matching onOpenInXxe and keeping this window responsive
        while the editor is open.'''

        if not self.offerToWritePendingDraft():
            return

        if not os.path.isfile(self.transferPath):

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Not found'),
                                _translate('WorkOnRulesWithAI', 'The transfer rules file is not there: {path}').format(path=self.transferPath))
            return

        try:
            os.startfile(self.transferPath)   # Windows: open with the registered handler (XXE)

        except Exception as err:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Could not open the editor'),
                                _translate('WorkOnRulesWithAI', 'The transfer rules file could not be opened for editing ({err}). Open it yourself from: {path}').format(err=err, path=self.transferPath))
            return

        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Opened the transfer rules file in the XML editor. After you save there, click Refresh Rules so this window picks up your changes.'))

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
