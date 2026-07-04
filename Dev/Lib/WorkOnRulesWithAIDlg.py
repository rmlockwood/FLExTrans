#
#   WorkOnRulesWithAIDlg
#
#   Ron Lockwood
#   SIL International
#   7/2/26
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

from PyQt6.QtCore import QThread, QObject, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QMessageBox, QInputDialog, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView

import AIRules
import TransferPreview
from WorkOnRulesWithAIWindow import Ui_WorkOnRulesWithAI

# FTPaths is only available inside the full FLExTrans install; tolerate its absence so the dialog can run standalone.
try:
    import FTPaths

except ImportError:
    FTPaths = None  # type: ignore[assignment]

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

        # Populated once a candidate is generated.
        self.ruleResult = None
        self.currentRuleXml = None
        self.genThread = None
        self.worker = None

        # Build the widgets from the pyuic-generated class.
        self.ui = Ui_WorkOnRulesWithAI()
        self.ui.setupUi(self)

        if FTPaths:
            self.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.ui.ruleList.addItems(self.ruleNames)

        # The preview QWebEngineView is created lazily on first use (see ensurePreview): an embedded Chromium view installs input hooks that can steal arrow/navigation keys from
        # sibling text widgets, so we keep it out of the window until a preview is needed.
        self.preview = None

        # Hook up the widgets.
        self.ui.createRadio.toggled.connect(self.onModeChanged)
        self.ui.generateButton.clicked.connect(self.onGenerate)
        self.ui.approveButton.clicked.connect(self.onApprove)
        self.ui.xxeButton.clicked.connect(self.onOpenInXxe)
        self.ui.cancelButton.clicked.connect(self.reject)
        self.ui.changeKeyButton.clicked.connect(self.onChangeApiKey)

        self.onModeChanged()

    def isModify(self) -> bool:

        return self.ui.modifyRadio.isChecked()

    def onModeChanged(self):

        modify = self.isModify()
        self.ui.pickerLabel.setVisible(modify)
        self.ui.ruleList.setVisible(modify)

    def selectedRuleComment(self):

        item = self.ui.ruleList.currentItem()
        return item.text() if item else None

    def onGenerate(self):

        description = self.ui.descriptionEdit.toPlainText().strip()

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
        self.ui.statusLabel.setText(_translate('WorkOnRulesWithAI', 'Generating…'))

        self.genThread = QThread()
        self.worker = GenerateWorker(params)
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
        self.ui.ruleList.setEnabled(not busy)
        self.ui.descriptionEdit.setEnabled(not busy)

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

    def onGenerateFinished(self, result):

        self.cleanupThread()
        self.setBusy(False)
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

        QMessageBox.information(self, _translate('WorkOnRulesWithAI', 'Rule written'), _translate('WorkOnRulesWithAI', 'The rule was written to the transfer file.\n\nBackup saved to:\n{path}').format(path=backupPath))
        self.accept()

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
