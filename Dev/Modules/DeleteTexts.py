#
#   DeleteTexts
#
#   Ron Lockwood
#   SIL International
#   9/9/26
#
#   Version 3.17 - 9/9/26 - Ron Lockwood
#    Initial version.
#
#   OVERVIEW (AI generated, then edited)
#
#   This module lets the user delete one or more interlinear texts from a FLEx project. Texts pile up over time - Paratext chapters imported again and again, test texts, drafts, and the " - Copy"
#   duplicates that the Paratext import makes when a text of the same name already exists - and without this module the only way to clear them out is to open FLEx and delete them one at a time.
#   The window is a project picker over a plain multi-select list of that project's texts; whatever is selected when OK is pressed gets deleted, after a confirmation.
#
#   WHICH PROJECT
#
#   The picker offers every FLEx project on the machine and starts on the configured target project, not on the source project FlexTools has open. That default is deliberate: the texts people want
#   to clear out are usually the ones FLExTrans inserted into the target project, not the source texts they are translating from. It falls back to the source project when no target is configured.
#
#   Only one project is ever open per name. The source project is already open by FlexTools and is reused through the DB handle we were given - reopening it would fail on its own lock file. Any
#   other project the user visits is opened write-enabled on first selection, cached, and closed at the end, which is both what saves the deletions and what releases the lock for FLEx. Because
#   the IText objects stay valid only while their project is open, that close has to happen after the deletions, so it lives in a finally clause around the delete step.
#
#   WHAT THE LIST SHOWS
#
#   Every IText in the project, sorted case-insensitively by name. This is deliberately not the same set that FLEx's own Interlinear Texts list shows: FLEx filters that list by per-user settings
#   (excluded texts, genre checkboxes) that live in the user's FLEx configuration rather than in the project data, so FLExTrans cannot see them. The list here can therefore legitimately show more
#   texts than FLEx does. Scripture books do not appear at all - those are IScrBook objects living in FLEx's Scripture area, not ITexts.
#
#   The row for the text that FLExTrans is currently configured to translate (the SourceTextName setting) is marked so the user doesn't delete it by accident. It is not blocked, though - if it does
#   get deleted, the setting is blanked out afterwards and the FlexTools status bar is refreshed, so nothing downstream is left pointing at a text that no longer exists. That marking and clearing
#   only apply while the source project is the one on show: SourceTextName names a text in the source project, so a same-named text in some other project is unrelated to it.
#
#   Each row carries the IText object itself, not just its name. That matters because the marked row's displayed text is not the text's real name, and because the whole repository is pulled into a
#   list up front: walking the repository iterator while deleting out of it would invalidate the iterator part way through.
#
#   One more ordering trap: Qt's selectedItems() hands back the rows in the order the user Ctrl-clicked them, not in row order, so the selection is re-sorted by name on the way out of the window.
#   Without that, the confirmation box and the report pane would both list the texts in click order, which reads as random.
#
#   CODE STRUCTURE
#
#   MainWindow - the QMainWindow holding the project combo, the multi-select text list and the OK/Cancel buttons. getProjectDB() opens (and caches) a project on demand, loadTextsForCurrentProject()
#   fills the list from whichever project the combo shows, and okButtonClicked() stores the (name, object) pairs from the selected rows plus the project they came from, setting returnVal so
#   MainFunction can pick them up after the event loop ends. closeOpenedProjects() closes everything getProjectDB() opened.
#   ConfirmDeleteDlg / confirmDeletion() - the point-of-no-return dialog, shown once with the names of everything about to be deleted; confirmDeletion() returns True only on Yes. It is a fixed-size
#   dialog wrapped around one scrollable list rather than a message box, because a message box grows to fit its text and would run off the bottom of the screen somewhere past fifty names. Being
#   fixed-size, it also looks the same whether the user is deleting three texts or five hundred, and no name is ever hidden behind a disclosure button.
#   MainFunction() - the entry point FlexTools calls. Checks modify mode, reads the configuration, works out the project list and the starting project, shows the window, and then guarantees the
#   opened projects get closed around the call to deleteSelectedTexts().
#   deleteSelectedTexts() - confirms, deletes each selected text and reports what happened. Clears the source text setting if the text it named was one of the ones deleted from the source project.
#

import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QComboBox, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QDialog, QDialogButtonBox, QStyle
from PyQt6.QtCore import QCoreApplication, Qt

from flextoolslib import * # type: ignore
from flexlibs import AllProjectNames

import Mixpanel
import FTPaths
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'DeleteTexts'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel']

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("DeleteTexts", "Delete Texts"),
        FTM_Version    : "3.17",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : _translate("DeleteTexts", "Delete one or more texts from a FLEx project."),
        FTM_Help       : "",
        FTM_Description: _translate("DeleteTexts",
"""Choose a FLEx project, then select one or more of its texts and delete them. Hold Ctrl or Shift to select more than one text.
The project list starts on your target project, since the texts you usually want to clear out are the ones FLExTrans inserted
there, but you can pick any FLEx project, including your source project. 
Deleting a text this way CANNOT be undone, in FLExTrans or in FLEx, so the module asks you to confirm and
lists what it is about to delete. Before running it, make sure you are not in the Texts & Words section of FLEx, otherwise FLEx
may be left holding on to a text that no longer exists. If you delete the text that FLExTrans is currently set up to translate, 
the source text setting is cleared and you will need
to choose a new source text in the FLExTrans Settings.""")}

class MainWindow(QMainWindow):

    def __init__(self, DB, report, projectNameList, startProjectName, activeTextName):

        super().__init__()

        # DB is the project FlexTools already has open. It is the one project we must never open or close ourselves - FlexTools owns its lifetime.
        self.DB = DB
        self.report = report
        self.activeTextName = activeTextName

        # Projects this window opened itself, keyed by name, so switching back to one already visited doesn't reopen it and so MainFunction can close them all at the end.
        self.openedProjects = {}

        self.selectedTextPairs = []
        self.selectedProjectName = None
        self.returnVal = False

        self.initUI(projectNameList, startProjectName)
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

    def initUI(self, projectNameList, startProjectName):

        self.setWindowTitle(_translate("DeleteTexts", "Delete Texts"))
        self.setGeometry(100, 100, 500, 440)

        # Create a central widget and set a layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Which FLEx project to delete from. This defaults to the target project rather than the source, because the texts people want to clear out are usually the ones FLExTrans inserted into
        # the target project, not the source texts they are translating from.
        projectLayout = QHBoxLayout()
        projectLayout.addWidget(QLabel(_translate("DeleteTexts", "FLEx project:")))

        self.projectComboBox = QComboBox()
        self.projectComboBox.addItems(projectNameList)
        projectLayout.addWidget(self.projectComboBox, 1)
        layout.addLayout(projectLayout)

        self.textLabel = QLabel()
        layout.addWidget(self.textLabel)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Alternating row colors make a long list easier to scan, and the style sheet forces white text on the selected row instead of the dark
        # color the Win11 style leaves it. Matches the other FLExTrans lists.
        self.listWidget.setAlternatingRowColors(True)
        self.listWidget.setStyleSheet("QListWidget { outline: 0; } QListWidget::item { border: 0; } QListWidget::item:selected { background-color: palette(highlight); color: white; }")
        layout.addWidget(self.listWidget, 1)

        # Say both how to select more than one text and that there is no undo. This window is the last calm place to say it before the confirmation box.
        hintLabel = QLabel(_translate("DeleteTexts", "Hold Ctrl or Shift to select more than one text. Deleting a text cannot be undone."))
        hintLabel.setWordWrap(True)
        layout.addWidget(hintLabel)

        # Create OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton(_translate("DeleteTexts", "OK"))
        self.cancelButton = QPushButton(_translate("DeleteTexts", "Cancel"))
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons to their respective slots
        self.okButton.clicked.connect(self.okButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

        # Select the starting project and load its texts. Setting the combo before connecting the signal would skip the load, so connect first and let setCurrentText do the work; if the start
        # project is already the combo's current item, setCurrentText fires nothing, so load explicitly afterwards.
        self.projectComboBox.currentTextChanged.connect(self.projectChanged)

        if startProjectName and startProjectName in projectNameList:

            self.projectComboBox.setCurrentText(startProjectName)

        self.loadTextsForCurrentProject()

    def getProjectDB(self, projectName):

        """The open FLExProject for projectName, opening it if this is the first time it has been asked for. Returns None if it could not be opened."""

        # The source project is already open by FlexTools. Opening it a second time would fail on its own lock file, so reuse the handle we were given.
        if projectName == self.DB.ProjectName():

            return self.DB

        if projectName in self.openedProjects:

            return self.openedProjects[projectName]

        # Utils.openProject opens write-enabled and already reports a helpful error (including the "project is open in FLEx" case) before returning None.
        projectDB = Utils.openProject(self.report, projectName)

        if projectDB is None:

            return None

        self.openedProjects[projectName] = projectDB

        return projectDB

    def loadTextsForCurrentProject(self):

        """Fill the list with the texts of whichever project the combo is showing."""

        projectName = self.projectComboBox.currentText()

        self.listWidget.clear()

        projectDB = self.getProjectDB(projectName)

        if projectDB is None:

            self.textLabel.setText(_translate("DeleteTexts", "The {projectName} project could not be opened. See the report pane.").format(projectName=projectName))
            return

        # Pull the whole repository into a list now, before anything is deleted - walking the repository iterator while deleting out of it would invalidate the iterator part way through.
        textObjList = []
        textNameList = Utils.getSourceTextList(projectDB, textObjList=textObjList)

        if not textNameList:

            self.textLabel.setText(_translate("DeleteTexts", "The {projectName} project has no texts.").format(projectName=projectName))
            return

        self.textLabel.setText(_translate("DeleteTexts", "Texts in the {projectName} project (multi-select):").format(projectName=projectName))

        # The SourceTextName setting names a text in the source project, so only mark the row when that is the project actually on show.
        markActiveText = projectName == self.DB.ProjectName()

        # Sort by name, case-insensitively, the way source text lists are sorted elsewhere in FLExTrans.
        textPairList = sorted(zip(textNameList, textObjList), key=lambda textPair: textPair[0].casefold())

        # Each row displays the text name but carries the (name, IText object) pair under UserRole. The delete loop uses that pair, not the
        # row's text, because the marked row's text isn't the real name.
        for textName, textObj in textPairList:

            if markActiveText and textName == self.activeTextName:

                displayName = _translate("DeleteTexts", "{textName}  [current FLExTrans source text]").format(textName=textName)
            else:
                displayName = textName

            item = QListWidgetItem(displayName)
            item.setData(Qt.ItemDataRole.UserRole, (textName, textObj))
            self.listWidget.addItem(item)

    def projectChanged(self, _projectName):

        self.loadTextsForCurrentProject()

    def closeOpenedProjects(self):

        """Close (and thereby save) every project this window opened. Must be called after the deletions, since the IText objects stay valid only while their project is open."""

        for projectDB in self.openedProjects.values():

            projectDB.CloseProject()

        self.openedProjects = {}

    def okButtonClicked(self):

        # Hand back the (name, IText object) pairs stashed on the selected rows. selectedItems() returns them in the order the user clicked them, not in row order, so sort by name the same
        # case-insensitive way the list itself is sorted. That keeps the confirmation box and the report pane alphabetical instead of showing whatever order the clicking happened in.
        selectedPairList = [item.data(Qt.ItemDataRole.UserRole) for item in self.listWidget.selectedItems()]

        self.selectedTextPairs = sorted(selectedPairList, key=lambda textPair: textPair[0].casefold())

        # Record which project the selection came from. The combo can no longer be changed once the window closes, but MainFunction needs the name for its messages and to decide whether the
        # SourceTextName setting is affected.
        self.selectedProjectName = self.projectComboBox.currentText()
        self.returnVal = True
        self.close()

    def cancelButtonClicked(self):

        self.selectedTextPairs = []
        self.returnVal = False
        self.close()

class ConfirmDeleteDlg(QDialog):

    def __init__(self, textNameList, parent=None):

        super().__init__(parent)

        self.setWindowTitle(_translate("DeleteTexts", "Deleting FLEx Texts"))
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.setModal(True)

        # A fixed size is the point of this dialog: the list scrolls instead of the window growing, so confirming three texts and confirming five hundred look the same. A plain message box would
        # have grown to fit its text and run off the bottom of the screen somewhere past fifty names.
        self.resize(500, 430)

        layout = QVBoxLayout(self)

        # Warning triangle beside the question, so this still reads as destructive at a glance the way the standard warning message box does.
        headerLayout = QHBoxLayout()
        iconLabel = QLabel()
        style = self.style()

        # style() is typed as Optional; a realized widget always has one, but fall back to simply not showing the icon rather than crashing the confirmation.
        if style is not None:

            iconLabel.setPixmap(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning).pixmap(32, 32))

        iconLabel.setAlignment(Qt.AlignmentFlag.AlignTop)
        headerLayout.addWidget(iconLabel)

        headerLabel = QLabel(_translate("DeleteTexts", "Delete these {count} text(s) from the FLEx project?").format(count=len(textNameList)))
        headerLabel.setWordWrap(True)
        headerLayout.addWidget(headerLabel, 1)
        layout.addLayout(headerLayout)

        # Every selected name, in one scrollable list. Selection and focus are switched off so it reads as a read-only display of what is about to happen rather than something to click on.
        nameListWidget = QListWidget()
        nameListWidget.addItems(textNameList)
        nameListWidget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        nameListWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nameListWidget.setAlternatingRowColors(True)
        layout.addWidget(nameListWidget, 1)

        warningLabel = QLabel(_translate("DeleteTexts", "This CANNOT be undone. If FLEx is open, make sure you are NOT in the Texts & Words section of FLEx."))
        warningLabel.setWordWrap(True)
        layout.addWidget(warningLabel)

        # Yes/No rather than OK/Cancel, and their captions come from Qt's own translations. Yes carries AcceptRole and No RejectRole, which is what accepted/rejected below hang off.
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        yesButton = buttonBox.button(QDialogButtonBox.StandardButton.Yes)
        noButton = buttonBox.button(QDialogButtonBox.StandardButton.No)

        # Make No the default and give it focus, so pressing Enter or Space out of habit cancels rather than destroying texts. This has to happen after the box is in the layout and it has to demote
        # Yes explicitly: a QDialogButtonBox hands the default to its accept-role button as it is laid out, which silently undoes a setDefault() made any earlier.
        if yesButton is not None:

            yesButton.setAutoDefault(False)
            yesButton.setDefault(False)

        if noButton is not None:

            noButton.setAutoDefault(True)
            noButton.setDefault(True)
            noButton.setFocus()

def confirmDeletion(textNameList):

    dlg = ConfirmDeleteDlg(textNameList)

    return dlg.exec() == QDialog.DialogCode.Accepted

def MainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True)

    # This module is useless without write access. FlexTools forces modifyAllowed to False unless FTM_ModifiesDB is True, so this catches a mis-declared docs dictionary as well as the user not
    # having turned modify mode on.
    if not modifyAllowed:

        report.Error(_translate("DeleteTexts", 'You need to run this module in "modify mode."'))
        return

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)

    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Which text FLExTrans is currently set up to translate. Don't complain if the setting is missing - it just means no row gets marked.
    activeTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report, giveError=False)

    # Every FLEx project on the machine is offered, the same way the Open/Fix FLEx Projects tools do it, so texts can be cleared out of whichever project has accumulated them.
    projectNameList = sorted(AllProjectNames(), key=str.casefold)

    if not projectNameList:

        report.Error(_translate("DeleteTexts", "No FLEx projects were found."))
        return

    # Start on the target project: the texts people want to delete are usually the ones FLExTrans inserted into the target, not the source texts they translate from. Fall back to the source
    # project if no target is configured or the configured one no longer exists.
    targetProjectName = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False)

    if targetProjectName and targetProjectName in projectNameList:

        startProjectName = targetProjectName
    else:
        startProjectName = DB.ProjectName()

    # Show the window to get the project and the texts the user wants to delete.
    window = MainWindow(DB, report, projectNameList, startProjectName, activeTextName)
    window.show()
    app.exec()

    # Whatever happens from here, every project this window opened has to be closed - that is what writes the deletions to disk, and it also releases the lock so FLEx can open the project again.
    try:
        deleteSelectedTexts(window, DB, report, activeTextName)

    finally:
        window.closeOpenedProjects()

def deleteSelectedTexts(window, DB, report, activeTextName):

    """Confirm and carry out the deletions the window came back with. Split out from MainFunction so that closing the projects it opened can be a single finally clause."""

    # Cancelled, or OK with nothing selected. Either way there is nothing to do.
    if not window.returnVal or not window.selectedTextPairs:
        return

    projectName = window.selectedProjectName
    selectedNameList = [textName for textName, _ in window.selectedTextPairs]

    if not confirmDeletion(selectedNameList):

        report.Info(_translate("DeleteTexts", "No texts were deleted."))
        return

    # The SourceTextName setting names a text in the source project, so deleting a same-named text out of some other project must not clear it.
    checkActiveText = projectName == DB.ProjectName()

    deletedCount = 0
    deletedActiveText = False

    for textName, textObj in window.selectedTextPairs:

        # A text could have gone stale if it was deleted in FLEx while this window was open, and LCM can refuse a delete outright. Report either case rather than throwing.
        if not textObj.IsValidObject:

            report.Warning(_translate("DeleteTexts", 'The text "{textName}" no longer exists in the project. Skipping.').format(textName=textName))
            continue

        if not textObj.CanDelete:

            report.Warning(_translate("DeleteTexts", 'The text "{textName}" cannot be deleted. Skipping.').format(textName=textName))
            continue

        # Delete() cascades to the text's contents (the StText) and its paragraphs. The change reaches disk when the project is closed.
        textObj.Delete()
        deletedCount += 1

        report.Info(_translate("DeleteTexts", 'Deleted the text "{textName}".').format(textName=textName))

        if checkActiveText and textName == activeTextName:
            deletedActiveText = True

    # If the text FLExTrans was pointed at is gone, clear the setting so nothing downstream goes looking for it, and refresh the status bar that displays it.
    if deletedActiveText:

        ReadConfig.writeConfigValue(report, ReadConfig.SOURCE_TEXT_NAME, '')
        FTPaths.CURRENT_SRC_TEXT = '' # type: ignore
        refreshStatusbar()

        report.Warning(_translate("DeleteTexts", "The source text setting was cleared because the text it named was deleted. Choose a new source text in the FLExTrans Settings."))

    report.Info(_translate("DeleteTexts", "{count} text(s) deleted from the {projectName} project.").format(count=deletedCount, projectName=projectName))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
