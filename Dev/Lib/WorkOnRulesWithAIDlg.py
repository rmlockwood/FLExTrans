#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16.9 - 7/6/26 - Ron Lockwood
#    PasteDataDlg UI moved to separate Windows/PasteDataWindow.ui file compiled with pyuic; translations split into Windows/translations/PasteDataWindow*.ts files.
#
#   Version 3.16.8 - 7/6/26 - Ron Lockwood
#    After approving a rule that used example data, the next create-mode Generate asks once whether to keep that data for the new rule (No clears both sides); reopening the data grids
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
import unicodedata

from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QDialog, QInputDialog, QLineEdit, QMessageBox, QTableWidgetItem)
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
    '''Create or modify one Apertium transfer rule with AI assistance. The widget layout comes from WorkOnRulesWithAIWindow.ui (compiled to WorkOnRulesWithAIWindow.py with pyuic).'''

    def __init__(self, transferPath, ruleNames, systemInstruction, defsSummary, projectData, engine, dtdPath, compilerExe, parent=None):

        super().__init__(parent)

        # Everything the generation needs, injected by the caller.
        self.transferPath = transferPath
        self.ruleNames = ruleNames
        self.systemInstruction = systemInstruction
        self.defsSummary = defsSummary
        self.projectData = projectData
        self.engine = engine
        self.dtdPath = dtdPath
        self.compilerExe = compilerExe

        # Populated once a candidate is generated. currentTask remembers which mode the running/last generation was for ('create'/'modify'/'explain').
        self.ruleResult = None
        self.currentRuleXml = None
        self.currentTask = 'create'
        self.genThread = None
        self.worker = None

        # Interlinearized example data the user pastes via the Source/Target Data buttons; sent with every request when non-empty. After a rule is approved, the next create-mode
        # Generate asks whether to keep the (possibly no longer relevant) data - askAboutDataOnNextGenerate arms that one-time question.
        self.sourceDataText = ''
        self.targetDataText = ''
        self.askAboutDataOnNextGenerate = False

        # Build the widgets from the pyuic-generated class.
        self.ui = Ui_WorkOnRulesWithAI()
        self.ui.setupUi(self)

        if FTPaths:
            self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.ui.ruleList.addItems(self.ruleNames)

        # The preview QWebEngineView is created lazily on first use (see ensurePreview): an embedded Chromium view installs input hooks that can steal arrow/navigation keys from
        # sibling text widgets, so we keep it out of the window until a preview is needed.
        self.preview = None

        # Hook up the widgets. The window stays open across successive rule edits: only Close (and the window's X) end it; Generate / Open temp / Approve all leave it open.
        # Connect all three mode radios: switching between modify and explain leaves the create radio untoggled, so connecting create alone would miss that switch and leave the wrong
        # widgets showing. Each switch toggles two radios, so onModeChanged runs twice, which is harmless (it's idempotent).
        self.ui.createRadio.toggled.connect(self.onModeChanged)
        self.ui.modifyRadio.toggled.connect(self.onModeChanged)
        self.ui.explainRadio.toggled.connect(self.onModeChanged)
        self.ui.sourceDataButton.clicked.connect(self.onSourceData)
        self.ui.targetDataButton.clicked.connect(self.onTargetData)
        self.ui.generateButton.clicked.connect(self.onGenerate)
        self.ui.approveButton.clicked.connect(self.onApprove)
        self.ui.xxeButton.clicked.connect(self.onOpenInXxe)
        self.ui.refreshButton.clicked.connect(self.onRefreshRules)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.changeKeyButton.clicked.connect(self.onChangeApiKey)

        self.onModeChanged()

    def isModify(self) -> bool:

        return self.ui.modifyRadio.isChecked()

    def isExplain(self) -> bool:

        return self.ui.explainRadio.isChecked()

    def currentMode(self) -> str:

        if self.isExplain():
            return 'explain'

        return 'modify' if self.isModify() else 'create'

    def onModeChanged(self):

        # Both the modify and explain modes pick from the rule list; only create/modify take a description. The picker label follows the mode.
        mode = self.currentMode()

        self.ui.pickerLabel.setVisible(mode in ('modify', 'explain'))
        self.ui.ruleList.setVisible(mode in ('modify', 'explain'))
        self.ui.pickerLabel.setText(_translate('WorkOnRulesWithAI', 'Rule to explain:') if mode == 'explain' else _translate('WorkOnRulesWithAI', 'Rule to modify:'))
        self.ui.describeLabel.setVisible(mode != 'explain')
        self.ui.descriptionEdit.setVisible(mode != 'explain')

        # The Explanation-language box replaces the description box in explain mode (create/modify infer the language from the request text instead).
        self.ui.explainLangEdit.setVisible(mode == 'explain')

        # Switching modes invalidates any pending candidate: a rule generated for one mode must not be approvable (or openable in XXE) under another, e.g. a created rule silently
        # overwriting whichever rule happens to be selected after switching to modify.
        self.ruleResult = None
        self.ui.approveButton.setEnabled(False)
        self.ui.xxeButton.setEnabled(False)

    def selectedRuleComment(self):

        item = self.ui.ruleList.currentItem()
        return item.text() if item else None

    def reloadRules(self):
        '''Re-read the transfer file so the rule picker and the definition summary sent to the AI reflect the current on-disk state. Called after a rule is approved (a new/changed rule
        must appear in the list) and by the Refresh Rules button (the user may have edited the file in another window). The current picker selection is preserved when it still exists.'''

        try:
            defs = AIRules.extractExistingDefs(self.transferPath)

        except Exception as err:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Refresh Rules'), _translate('WorkOnRulesWithAI', 'Could not re-read the transfer rules file: {err}').format(err=err))
            return

        self.ruleNames = defs['ruleNames']
        self.defsSummary = defs['summaryText']

        previous = self.selectedRuleComment()

        self.ui.ruleList.clear()
        self.ui.ruleList.addItems(self.ruleNames)

        # Restore the previous selection if that rule still exists.
        if previous:

            matches = self.ui.ruleList.findItems(previous, Qt.MatchFlag.MatchExactly)

            if matches:
                self.ui.ruleList.setCurrentItem(matches[0])

    def onRefreshRules(self):

        self.reloadRules()
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rule list refreshed ({n} rules).').format(n=len(self.ruleNames)))

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
        '''A check mark at the end of a data button's label shows that data has been given on that side.'''

        self.ui.sourceDataButton.setText(_translate('WorkOnRulesWithAI', 'Source Data…') + (' ✓' if self.sourceDataText else ''))
        self.ui.targetDataButton.setText(_translate('WorkOnRulesWithAI', 'Target Data…') + (' ✓' if self.targetDataText else ''))

    # The FLExTrans interface languages, mapped to the English language name we put in the prompt when the user leaves the Explanation-language box blank.
    UI_LANG_NAMES = {'en': 'English', 'de': 'German', 'es': 'Spanish', 'fr': 'French'}

    def interfaceLanguageName(self) -> str:
        '''The FLExTrans interface language as a language name (e.g. "German"), used as the default explanation language when the user hasn't typed one. Falls back to English when
        Utils/FTConfig aren't available (standalone runs) or the code isn't one we have a name for.'''

        try:
            import Utils
            code = Utils.getInterfaceLangCode() or 'en'

        except Exception:
            code = 'en'

        return self.UI_LANG_NAMES.get(code, 'English')

    def explanationLanguage(self) -> str:
        '''The language to write an explanation in: what the user typed in the Explanation-language box, or the interface language when that box is blank.'''

        typed = self.ui.explainLangEdit.text().strip()
        return typed or self.interfaceLanguageName()

    def onGenerate(self):

        mode = self.currentMode()
        description = self.ui.descriptionEdit.toPlainText().strip()

        # A description is required to create or modify; the explain mode needs only a picked rule.
        if mode != 'explain' and not description:

            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the rule you want.'))
            return

        # Starting a new rule after approving the previous one: the example data given for that rule may not fit this one, so ask once whether to keep it. Regenerating while iterating
        # on the same rule doesn't ask, and neither does a user who just reopened the data grids (onSourceData/onTargetData disarm the question).
        if mode == 'create' and self.askAboutDataOnNextGenerate and (self.sourceDataText or self.targetDataText):

            answer = QMessageBox.question(self, _translate('WorkOnRulesWithAI', 'Example language data'), _translate('WorkOnRulesWithAI', 'Do you want to keep the example language data you provided for the previous rule?'), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)

            if answer == QMessageBox.StandardButton.No:

                self.sourceDataText = ''
                self.targetDataText = ''
                self.updateDataButtons()

            self.askAboutDataOnNextGenerate = False

        targetComment = None
        self.currentRuleXml = None

        if mode in ('modify', 'explain'):

            targetComment = self.selectedRuleComment()

            if not targetComment:

                if mode == 'explain':
                    QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to explain.'))
                else:
                    QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to modify.'))

                return

            self.currentRuleXml = AIRules.getRuleXmlByComment(self.transferPath, targetComment)

        # The explain language matters only in explain mode; it's harmlessly ignored for create/modify (which infer the language from the request text).
        explainLang = self.explanationLanguage() if mode == 'explain' else 'English'
        userContent = AIRules.buildUserContent(mode, description, self.defsSummary, self.projectData, self.currentRuleXml, explainLang, self.sourceDataText, self.targetDataText)

        if mode == 'explain':

            # Explaining makes one plain call - no validation loop, no authorship stamp, nothing written.
            fn = AIRules.explainRule
            params = {
                'engine': self.engine,
                'systemInstruction': self.systemInstruction,
                'userContent': userContent,
            }
        else:

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

            fn = AIRules.generateValidatedRule
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

        # Remember which task this run is for, so onGenerateFinished knows how to interpret and render the result (the mode radios are disabled while busy, so it can't change mid-run).
        self.currentTask = mode

        # Disable controls and run the call on a worker thread.
        self.setBusy(True)
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generating…'))

        self.genThread = QThread()
        self.worker = GenerateWorker(fn, params)
        self.worker.moveToThread(self.genThread)
        self.genThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.onGenerateFinished)
        self.worker.failed.connect(self.onGenerateFailed)
        self.worker.rateLimited.connect(self.onRateLimited)
        self.genThread.start()

    def setBusy(self, busy: bool):

        self.ui.generateButton.setEnabled(not busy)
        self.ui.createRadio.setEnabled(not busy)
        self.ui.modifyRadio.setEnabled(not busy)
        self.ui.explainRadio.setEnabled(not busy)
        self.ui.ruleList.setEnabled(not busy)
        self.ui.descriptionEdit.setEnabled(not busy)
        self.ui.explainLangEdit.setEnabled(not busy)
        self.ui.sourceDataButton.setEnabled(not busy)
        self.ui.targetDataButton.setEnabled(not busy)
        self.ui.refreshButton.setEnabled(not busy)

    def cleanupThread(self):

        if self.genThread:

            self.genThread.quit()
            self.genThread.wait()
            self.genThread = None
            self.worker = None

    def ensurePreview(self):
        '''Create the QWebEngineView on first use and swap out the placeholder.'''

        if self.preview is None:

            self.preview = QWebEngineView()
            self.ui.previewLayout.addWidget(self.preview)
            self.ui.previewPlaceholder.hide()

        return self.preview

    def showEvent(self, event):

        super().showEvent(event)
        self.ui.descriptionEdit.setFocus()

    def closeEvent(self, event):
        '''Close (the Close button and the window's X both route here). If a generation is still running, wait for it to finish first so the worker thread isn't destroyed mid-run - which
        would crash - when the dialog is garbage-collected after the event loop returns.'''

        self.cleanupThread()
        super().closeEvent(event)

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

        # Render the preview: single rule for create, before/after for modify. The label language follows the language of the user's request, as reported by the model.
        if self.isModify() and self.currentRuleXml:
            html = TransferPreview.renderComparisonHtml(self.currentRuleXml, result.ruleXml, lang=result.language)
        else:
            html = TransferPreview.renderRuleHtml(result.ruleXml, result.newDefs, lang=result.language)

        self.ensurePreview().setHtml(html)
        self.ui.xxeButton.setEnabled(True)

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

    def onApprove(self):

        if not (self.ruleResult and self.ruleResult.valid):
            return

        mode = 'modify' if self.isModify() else 'create'
        targetComment = self.selectedRuleComment() if mode == 'modify' else None

        try:
            backupPath = AIRules.applyRule(self.transferPath, self.ruleResult, mode, targetComment)

        except Exception as err:

            QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error writing rule'), str(err))
            return

        # The window stays open for the next edit. Disable Approve until a new rule is generated so the same rule can't be written twice, and re-read the file so the picker and the
        # definition summary include the rule just written. Report success in the status line rather than a modal box, which would be tedious across many successive edits.
        self.ui.approveButton.setEnabled(False)
        self.reloadRules()

        # This rule is done; if example data was given for it, the next create-mode Generate will ask whether to keep that data for the next rule.
        if self.sourceDataText or self.targetDataText:
            self.askAboutDataOnNextGenerate = True

        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rule written to the transfer file (backup: {backup}). Generate or select another rule to continue.').format(backup=os.path.basename(backupPath)))

    def onOpenInXxe(self):

        if not self.ruleResult:
            return

        import shutil
        import tempfile

        mode = 'modify' if self.isModify() else 'create'
        targetComment = self.selectedRuleComment() if mode == 'modify' else None

        workDir = tempfile.mkdtemp(prefix='airules_xxe_')
        shutil.copyfile(self.dtdPath, os.path.join(workDir, 'transfer.dtd'))
        tempPath = AIRules.spliceIntoTemp(self.transferPath, self.ruleResult.ruleXml, self.ruleResult.newDefs, mode, targetComment, workDir)

        try:
            os.startfile(tempPath)   # Windows: open with the registered handler (XXE)

        except Exception:
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Open in XXE'), _translate('WorkOnRulesWithAI', 'A copy with your rule was written to:\n{path}\n\nOpen it in XXE to review.').format(path=tempPath))
