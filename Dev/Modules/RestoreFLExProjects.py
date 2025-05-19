#
#   RestoreFLExProjects
#
#   Ron Lockwood
#   SIL International
#   3/7/2025
#
#   Version 3.13.2 - 5/18/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/12/25 - Ron Lockwood
#    Add Mixpanel logging.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 3/7/2025 - Ron Lockwood
#    Initial version.
#
#   Restore multiple FLEx projects. 
#

import os
import re
from pathlib import Path
from subprocess import Popen, DETACHED_PROCESS
import sys
import time
import pygetwindow as gw

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QListWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFileDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QCoreApplication

from flextoolslib import *

import Mixpanel
import FTPaths
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RestoreFLExProjects'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Restore Multiple FLEx Projects",
        FTM_Version    : "3.13.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RestoreFLExProjects", "Select one or more FLEx backup files and automatically restore them one by one."),
        FTM_Help       :"",
        FTM_Description: _translate("RestoreFLExProjects", 
f"""Select one or more FLEx backup files and automatically restore them one by one. You have to click OK on the 
window that comes up to complete the restore. 
The tool waits until one project is open before restoring the next.""")}

app.quit()
del app

# Maximum time to wait for a project to open before exiting
LIMIT_SECS = 45

BROWSE_BUT_PCT = 0.33

class MainWindow(QMainWindow):
    def __init__(self, defaultFolder):
        super().__init__()
        self.selectedFolder = defaultFolder  # Class variable to store the selected folder
        self.initUI()
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.returnVal = False

    def initUI(self):
        self.setWindowTitle('Restore Multiple FLEx Projects')
        self.setGeometry(100, 100, 400, 300)  # Set the initial window width

        # Create a central widget and set a layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Create a label to show the selected folder
        self.folderLabel = QLabel(_translate("RestoreFLExProjects", "Backup Folder: ") + os.path.normpath(self.selectedFolder))
        layout.addWidget(self.folderLabel)

        # Create a horizontal layout for the browse button
        browseLayout = QHBoxLayout()
        spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.browseButton = QPushButton(_translate("RestoreFLExProjects", "Browse for Folder"))
        self.browseButton.setFixedWidth(int(self.width() * BROWSE_BUT_PCT))  # Set the button width to X% of the window width
        browseLayout.addItem(spacer1)
        browseLayout.addWidget(self.browseButton)
        browseLayout.addItem(spacer2)
        layout.addLayout(browseLayout)

        # Add vertical space below the browse button
        layout.addSpacing(20)

        # Create a label and list widget for project names
        projectLabel = QLabel(_translate("RestoreFLExProjects", "FLEx project backup files (multi-select):"))
        layout.addWidget(projectLabel)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.listWidget)

        # Create OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton(_translate("RestoreFLExProjects", "OK"))
        self.cancelButton = QPushButton(_translate("RestoreFLExProjects", "Cancel"))
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons to their respective slots
        self.browseButton.clicked.connect(self.browseForFolder)
        self.okButton.clicked.connect(self.okButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

        self.adjustWindowWidth(self.selectedFolder)

        # Populate the list widget with .fwbackup files from the default folder
        self.populateListWidget(self.selectedFolder)

    def populateListWidget(self, folder):
        self.listWidget.clear()
        for fileName in os.listdir(folder):
            if fileName.endswith('.fwbackup'):
                self.listWidget.addItem(fileName)

    def browseForFolder(self):
        folder = QFileDialog.getExistingDirectory(self, _translate("RestoreFLExProjects", "Select Folder"), self.selectedFolder)
        if folder:
            self.selectedFolder = folder  # Update the selected folder
            self.folderLabel.setText(_translate("RestoreFLExProjects", "Selected Folder: ") + folder)
            self.adjustWindowWidth(folder)
            self.populateListWidget(folder)

    def adjustWindowWidth(self, folder):
        # Calculate the required width based on the folder path length
        fontMetrics = self.fontMetrics()
        textWidth = fontMetrics.horizontalAdvance(_translate("RestoreFLExProjects", "Selected Folder: ") + folder)
        margin = 20  # Add some margin
        newWidth = textWidth + margin

        # Set the new width if it's greater than the current width
        if newWidth > self.width():
            self.setFixedWidth(newWidth)

        # Adjust the browse button width to X% of the new window width
        self.browseButton.setFixedWidth(int(self.width() * BROWSE_BUT_PCT))

    def okButtonClicked(self):
        selectedItems = self.listWidget.selectedItems()
        selectedBackups = [item.text() for item in selectedItems]
        self.selectedBackups = selectedBackups
        self.returnVal = True
        self.close()

    def cancelButtonClicked(self):
        self.selectedBackups = []
        self.close()

def isFlexOpen(projName):
    # Check if a window with the project name is open
    windows = gw.getWindowsWithTitle(f'{projName} - Fieldworks')
    return len(windows) > 0

def extractProjName(backupName):
    # Regular expression to match the pattern and capture the projName
    match = re.match(r'^(.*?) \d{4}-\d{2}-\d{2} \d{4}(?: .*)?\.fwbackup$', backupName)
    if match:
        return match.group(1)
    return None

def mainFunction(DB, report, modifyAllowed):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    defaultFolder = FTPaths.SAMPLE_PROJECTS_DIR

    if not Path(defaultFolder).is_dir():
        report.Error(_translate("RestoreFLExProjects", "Could not find the sample projects folder: {defaultFolder}.").format(defaultFolder=defaultFolder))
        return

    mainWindow = MainWindow(defaultFolder)
    mainWindow.show()
    app.exec_()

    # Get the Fieldworks folder path
    fieldworksDir = os.getenv('FIELDWORKSDIR')
    flexExe = os.path.join(fieldworksDir, 'flex.exe')

    if mainWindow.returnVal:

        # Loop through selected backups and restore them
        for i, backupName in enumerate(mainWindow.selectedBackups):

            proj = extractProjName(backupName)
            if not proj:
                report.Info(_translate("RestoreFLExProjects", "Could not extract project name from {backupName}. Skipping.").format(backupName=backupName))
                continue
            
            if isFlexOpen(proj):
                report.Info(_translate("RestoreFLExProjects", "The {proj} project is already open. Skipping. Close the project and try again.").format(proj=proj))
                continue

            backupPath = os.path.join(mainWindow.selectedFolder, backupName)  # Append backupName to the selected folder path
            process = Popen([flexExe, '-restore', backupPath], creationflags=DETACHED_PROCESS)

            secs = 0
            while not isFlexOpen(proj):
                time.sleep(1)  # Check every second if the project is fully opened
                secs += 1

                if secs >= LIMIT_SECS:
                    report.Info(_translate("RestoreFLExProjects", "Couldn't detect the {proj} project as open after {secs} seconds. Skipping.").format(proj=proj, secs=str(secs)))
                    break

            if secs < LIMIT_SECS:
                report.Info(_translate("RestoreFLExProjects", "The {proj} project took about {secs} seconds to open.").format(proj=proj, secs=str(secs)))
                time.sleep(2)  # Give a little more time to finish opening.
        
        report.Info(_translate("RestoreFLExProjects", "{count} projects processed.").format(count=str(i+1)))
    else:
        report.Info(_translate("RestoreFLExProjects", "No projects selected or window cancelled."))

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = mainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()