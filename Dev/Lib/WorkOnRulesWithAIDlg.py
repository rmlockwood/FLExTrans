#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
#
#   Version 3.16 - 7/2/26 - Ron Lockwood
#    Prototype. The dialog for the "Work on Rules with AI" module: choose to create a new rule or modify an existing one, describe the change, generate with the configured AI provider
#    (on a background thread), preview the result rendered like XXE, and Approve / Open in XXE / Cancel. Inputs are injected so the dialog can be exercised standalone; MainFunction
#    supplies the real FLEx-derived data later.

import os

from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QListWidget, QPlainTextEdit, QPushButton, QLabel, QMessageBox, QApplication, QWidget, QInputDialog, QLineEdit)
from PyQt6.QtWebEngineWidgets import QWebEngineView

import AIRules
import TransferPreview

# FTPaths is only available inside the full FLExTrans install; tolerate its absence so the dialog can run standalone.
try:
    import FTPaths
except ImportError:
    FTPaths = None

_translate = QCoreApplication.translate

def promptForApiKey(provider, parent=None):
    '''Ask the user for an API key and store it in the OS credential vault (not a project file). `provider` is used only for the display name and key URL in the prompt. Returns the key,
    or None if cancelled/empty. Shows an error and returns None if the vault is unavailable.'''

    label = _translate('WorkOnRulesWithAI', 'Enter your {provider} API key. It is stored securely in the credential vault (Windows Credential Manager), not in any project file.\n\nGet a key at:\n{url}').format(provider=provider.displayName, url=provider.keyUrl)

    key, ok = QInputDialog.getText(parent, _translate('WorkOnRulesWithAI', 'API key'), label, QLineEdit.EchoMode.Normal)
    key = (key or '').strip()

    if not ok or not key:
        return None

    try:
        AIRules.setStoredApiKey(key)

    except Exception as err:

        QMessageBox.warning(parent, _translate('WorkOnRulesWithAI', 'API key'),
                            _translate('WorkOnRulesWithAI', 'Could not save the key to the credential vault: {err}').format(err=err))
        return None

    return key

class GenerateWorker(QObject):
    '''Runs the (slow) generate + validate loop off the UI thread.'''

    finished = pyqtSignal(object)   # AIRules.RuleResult
    failed = pyqtSignal(str)
    rateLimited = pyqtSignal(str)   # friendly "try again in N s" message

    def __init__(self, params: dict):

        super().__init__()
        self.params = params

    def run(self):

        try:
            result = AIRules.generateValidatedRule(**self.params)
            self.finished.emit(result)

        except AIRules.RateLimitError as err:
            self.rateLimited.emit(str(err))

        except Exception as err:
            self.failed.emit(str(err))

class WorkOnRulesWithAIDlg(QDialog):
    '''Create or modify one Apertium transfer rule with AI assistance.'''

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

        # Populated once a candidate is generated.
        self.result = None
        self.currentRuleXml = None
        self.thread = None
        self.worker = None

        self.setWindowTitle(_translate('WorkOnRulesWithAI', 'Work on Rules with AI'))

        if FTPaths:
            self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.resize(1000, 750)
        self.buildUi()
        self.onModeChanged()

    def buildUi(self):

        layout = QVBoxLayout(self)

        # Mode: create vs modify.
        modeRow = QHBoxLayout()
        self.createRadio = QRadioButton(_translate('WorkOnRulesWithAI', 'Create new rule'))
        self.modifyRadio = QRadioButton(_translate('WorkOnRulesWithAI', 'Modify existing rule'))
        self.createRadio.setChecked(True)

        self.modeGroup = QButtonGroup(self)
        self.modeGroup.addButton(self.createRadio)
        self.modeGroup.addButton(self.modifyRadio)
        self.createRadio.toggled.connect(self.onModeChanged)

        modeRow.addWidget(self.createRadio)
        modeRow.addWidget(self.modifyRadio)
        modeRow.addStretch()
        layout.addLayout(modeRow)

        # Rule picker (shown only in modify mode).
        self.pickerLabel = QLabel(_translate('WorkOnRulesWithAI', 'Rule to modify:'))
        layout.addWidget(self.pickerLabel)

        self.ruleList = QListWidget()
        self.ruleList.addItems(self.ruleNames)
        self.ruleList.setMaximumHeight(160)
        layout.addWidget(self.ruleList)

        # Description of the desired rule / change.
        layout.addWidget(QLabel(_translate('WorkOnRulesWithAI', 'Describe the rule you want:')))
        self.descriptionEdit = QPlainTextEdit()
        self.descriptionEdit.setPlaceholderText(
            _translate('WorkOnRulesWithAI', 'e.g. Make adjectives agree in gender and number with the noun they modify.'))
        self.descriptionEdit.setMaximumHeight(110)
        layout.addWidget(self.descriptionEdit)

        # Generate button and status.
        genRow = QHBoxLayout()
        self.generateButton = QPushButton(_translate('WorkOnRulesWithAI', 'Generate'))
        self.generateButton.clicked.connect(self.onGenerate)
        self.statusLabel = QLabel('')
        genRow.addWidget(self.generateButton)
        genRow.addWidget(self.statusLabel)
        genRow.addStretch()
        layout.addLayout(genRow)

        # Preview (single rule for create, side-by-side for modify). The QWebEngineView is created lazily on first use: an embedded Chromium view installs input hooks that can steal
        # arrow/navigation keys from sibling text widgets, so we keep it out of the window until a preview is needed.
        layout.addWidget(QLabel(_translate('WorkOnRulesWithAI', 'Preview:')))
        self.previewContainer = QWidget()
        self.previewLayout = QVBoxLayout(self.previewContainer)
        self.previewLayout.setContentsMargins(0, 0, 0, 0)
        self.previewPlaceholder = QLabel(_translate('WorkOnRulesWithAI', 'The generated rule will appear here after you click Generate.'))
        self.previewLayout.addWidget(self.previewPlaceholder)
        layout.addWidget(self.previewContainer, 1)
        self.preview = None

        # Action buttons.
        buttonRow = QHBoxLayout()
        self.approveButton = QPushButton(_translate('WorkOnRulesWithAI', 'Approve && Write'))
        self.approveButton.clicked.connect(self.onApprove)
        self.approveButton.setEnabled(False)

        self.xxeButton = QPushButton(_translate('WorkOnRulesWithAI', 'Open in XXE'))
        self.xxeButton.clicked.connect(self.onOpenInXxe)
        self.xxeButton.setEnabled(False)

        self.cancelButton = QPushButton(_translate('WorkOnRulesWithAI', 'Cancel'))
        self.cancelButton.clicked.connect(self.reject)

        # A utility action (left side): change the stored API key at any time.
        self.changeKeyButton = QPushButton(_translate('WorkOnRulesWithAI', 'Change API key…'))
        self.changeKeyButton.clicked.connect(self.onChangeApiKey)

        buttonRow.addWidget(self.changeKeyButton)
        buttonRow.addStretch()
        buttonRow.addWidget(self.xxeButton)
        buttonRow.addWidget(self.cancelButton)
        buttonRow.addWidget(self.approveButton)
        layout.addLayout(buttonRow)

    def isModify(self) -> bool:

        return self.modifyRadio.isChecked()

    def onModeChanged(self):

        modify = self.isModify()
        self.pickerLabel.setVisible(modify)
        self.ruleList.setVisible(modify)

    def selectedRuleComment(self):

        item = self.ruleList.currentItem()
        return item.text() if item else None

    def onGenerate(self):

        description = self.descriptionEdit.toPlainText().strip()

        if not description:
            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Missing description'), _translate('WorkOnRulesWithAI', 'Please describe the rule you want.'))
            return

        mode = 'modify' if self.isModify() else 'create'
        targetComment = None
        self.currentRuleXml = None

        if mode == 'modify':

            targetComment = self.selectedRuleComment()

            if not targetComment:
                QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'No rule selected'), _translate('WorkOnRulesWithAI', 'Please select a rule to modify.'))
                return

            self.currentRuleXml = AIRules.getRuleXmlByComment(self.transferPath, targetComment)

        userContent = AIRules.buildUserContent(mode, description, self.defsSummary, self.projectData, self.currentRuleXml)

        params = {
            'engine': self.engine,
            'systemInstruction': self.systemInstruction,
            'userContent': userContent,
            'transferPath': self.transferPath,
            'dtdPath': self.dtdPath,
            'mode': mode,
            'targetComment': targetComment,
            'compilerExe': self.compilerExe,
        }

        # Disable controls and run generation on a worker thread.
        self.setBusy(True)
        self.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generating…'))

        self.thread = QThread()
        self.worker = GenerateWorker(params)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.onGenerateFinished)
        self.worker.failed.connect(self.onGenerateFailed)
        self.worker.rateLimited.connect(self.onRateLimited)
        self.thread.start()

    def setBusy(self, busy: bool):

        self.generateButton.setEnabled(not busy)
        self.createRadio.setEnabled(not busy)
        self.modifyRadio.setEnabled(not busy)
        self.ruleList.setEnabled(not busy)
        self.descriptionEdit.setEnabled(not busy)

    def cleanupThread(self):

        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.worker = None

    def ensurePreview(self):
        '''Create the QWebEngineView on first use and swap out the placeholder.'''

        if self.preview is None:
            self.preview = QWebEngineView()
            self.previewLayout.addWidget(self.preview)
            self.previewPlaceholder.hide()

        return self.preview

    def showEvent(self, event):

        super().showEvent(event)
        self.descriptionEdit.setFocus()

    def onGenerateFinished(self, result):

        self.cleanupThread()
        self.setBusy(False)
        self.result = result

        # Render the preview: single rule for create, before/after for modify. The label
        # language follows the language of the user's request, as reported by the model.
        if self.isModify() and self.currentRuleXml:
            html = TransferPreview.renderComparisonHtml(self.currentRuleXml, result.ruleXml, lang=result.language)
        else:
            html = TransferPreview.renderRuleHtml(result.ruleXml, result.newDefs, lang=result.language)

        self.ensurePreview().setHtml(html)
        self.xxeButton.setEnabled(True)

        if result.valid:
            self.approveButton.setEnabled(True)
            self.statusLabel.setText(
                _translate('WorkOnRulesWithAI', 'Valid rule generated (attempt {n}). {expl}').format(
                    n=result.attempts, expl=result.explanation))
        else:
            self.approveButton.setEnabled(False)
            self.statusLabel.setText(
                _translate('WorkOnRulesWithAI', 'Could not produce a valid rule after {n} attempts. See errors; you can still open it in XXE.').format(
                    n=result.attempts))
            QMessageBox.warning(self, _translate('WorkOnRulesWithAI', 'Validation failed'), result.errors)

    def onGenerateFailed(self, message):

        self.cleanupThread()
        self.setBusy(False)
        self.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generation failed.'))
        QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error'), message)

    def onRateLimited(self, message):

        self.cleanupThread()
        self.setBusy(False)
        self.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Rate limited - try again shortly.'))
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

        if not (self.result and self.result.valid):
            return

        mode = 'modify' if self.isModify() else 'create'
        targetComment = self.selectedRuleComment() if mode == 'modify' else None

        try:
            backupPath = AIRules.applyRule(self.transferPath, self.result, mode, targetComment)

        except Exception as err:
            QMessageBox.critical(self, _translate('WorkOnRulesWithAI', 'Error writing rule'), str(err))
            return

        QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Rule written'), _translate('WorkOnRulesWithAI', 'The rule was written to the transfer file.\n\nBackup saved to:\n{path}').format(path=backupPath))
        self.accept()

    def onOpenInXxe(self):

        if not self.result:
            return

        import tempfile

        mode = 'modify' if self.isModify() else 'create'
        targetComment = self.selectedRuleComment() if mode == 'modify' else None

        workDir = tempfile.mkdtemp(prefix='airules_xxe_')
        import shutil
        shutil.copyfile(self.dtdPath, os.path.join(workDir, 'transfer.dtd'))
        tempPath = AIRules.spliceIntoTemp(self.transferPath, self.result.ruleXml, self.result.newDefs, mode, targetComment, workDir)

        try:
            os.startfile(tempPath)   # Windows: open with the registered handler (XXE)

        except Exception:
            QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Open in XXE'), _translate('WorkOnRulesWithAI', 'A copy with your rule was written to:\n{path}\n\nOpen it in XXE to review.').format(path=tempPath))
