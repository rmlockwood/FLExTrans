#
#   RestoreFLExProjects
#
#   Ron Lockwood
#   SIL International
#   3/7/2025
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
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QListWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QFileDialog, QSpacerItem, QSizePolicy
import pygetwindow as gw

from flextoolslib import *

import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Restore Multiple FLEx Projects",
        FTM_Version    : "3.12",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Select one or more FLEx backup files and automatically restore them one by one.",
        FTM_Help       :"",
        FTM_Description:  
f"""
Select one or more FLEx backup files and automatically restore them one by one. The tool waits until one project is open before restoring the next.
""" }

# Maximum time to wait for a project to open before exiting
LIMIT_SECS = 90

class MainWindow(QMainWindow):
    def __init__(self, default_folder):
        super().__init__()
        self.selected_folder = default_folder  # Class variable to store the selected folder
        self.initUI()
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.returnVal = False

    def initUI(self):
        self.setWindowTitle('Select FLEx Projects')
        self.setGeometry(100, 100, 400, 400)  # Set the window width to be wide enough

        # Create a central widget and set a layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Create a label to show the selected folder
        self.folderLabel = QLabel(f'Selected Folder: {self.selected_folder}')
        layout.addWidget(self.folderLabel)

        # Create a horizontal layout for the browse button
        browseLayout = QHBoxLayout()
        spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.browseButton = QPushButton('Browse for Folder')
        self.browseButton.setFixedWidth(200)  # Set the button width to a third of the space
        browseLayout.addItem(spacer1)
        browseLayout.addWidget(self.browseButton)
        browseLayout.addItem(spacer2)
        layout.addLayout(browseLayout)

        # Create a label and list widget for project names
        projectLabel = QLabel('FLEx project backup files (multi-select):')
        layout.addWidget(projectLabel)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.listWidget)

        # Create OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons to their respective slots
        self.browseButton.clicked.connect(self.browseForFolder)
        self.okButton.clicked.connect(self.okButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

        # Populate the list widget with .fwbackup files from the default folder
        self.populateListWidget(self.selected_folder)

    def populateListWidget(self, folder):
        self.listWidget.clear()
        for file_name in os.listdir(folder):
            if file_name.endswith('.fwbackup'):
                self.listWidget.addItem(file_name)

    def browseForFolder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder', self.selected_folder)
        if folder:
            self.selected_folder = folder  # Update the selected folder
            self.folderLabel.setText(f'Selected Folder: {folder}')
            self.populateListWidget(folder)

    def okButtonClicked(self):
        selectedItems = self.listWidget.selectedItems()
        selectedBackups = [item.text() for item in selectedItems]
        self.selectedBackups = selectedBackups
        self.returnVal = True
        self.close()

    def cancelButtonClicked(self):
        self.selectedBackups = []
        self.close()

def is_flex_open(projName):
    # Check if a window with the project name is open
    windows = gw.getWindowsWithTitle(f'{projName} - Fieldworks')
    return len(windows) > 0

def extract_proj_name(backup_name):
    # Regular expression to match the pattern and capture the projName
    match = re.match(r'^(.*?) \d{4}-\d{2}-\d{2} \d{4}(?: .*)?\.fwbackup$', backup_name)
    if match:
        return match.group(1)
    return None

def MainFunction(DB, report, modifyAllowed):

    default_folder = FTPaths.SAMPLE_PROJECTS_DIR

    if not Path(default_folder).is_dir():
        report.Error(f"Could not find the sample projects folder: {default_folder}.")
        return

    app = QApplication(sys.argv)
    mainWindow = MainWindow(default_folder)
    mainWindow.show()
    app.exec_()

    # Get the Fieldworks folder path
    fieldworksDir = os.getenv('FIELDWORKSDIR')
    flexExe = os.path.join(fieldworksDir, 'flex.exe')

    if mainWindow.returnVal:

        # Loop through selected backups and restore them
        for i, backupName in enumerate(mainWindow.selectedBackups):

            proj = extract_proj_name(backupName)
            if not proj:
                report.Info(f"Could not extract project name from {backupName}. Skipping.")
                continue
            
            if is_flex_open(proj):
                report.Info(f"The {proj} project is already open. Skipping. Close the project and try again.")
                continue

            backup_path = os.path.join(mainWindow.selected_folder, backupName)  # Append backupName to the selected folder path
            process = Popen([flexExe, '-restore', backup_path], creationflags=DETACHED_PROCESS)

            secs = 0
            while not is_flex_open(proj):
                time.sleep(1)  # Check every second if the project is fully opened
                secs += 1

                if secs >= LIMIT_SECS:
                    report.Info(f"Couldn't detect the {proj} project as open after {str(secs)} seconds. Skipping.")
                    break

            if secs < LIMIT_SECS:
                report.Info(f'The {proj} project took about {str(secs)} seconds to open.')
                time.sleep(2)  # Give a little more time to finish opening.
        
        report.Info(f'{str(i+1)} projects processed.')
    else:
        report.Info('No projects selected or window cancelled.')

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()