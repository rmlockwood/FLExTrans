#
#   OpenFLExProjects.py
#
#   Ron Lockwood
#   SIL International
#   2/20/2025
#
#   Version 3.12 - 2/20/2025 - Ron Lockwood
#    Initial version.
#
#   Open multiple FLEx projects. 
#

import os
from subprocess import Popen, DETACHED_PROCESS
import sys
import time
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QListWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout
import pygetwindow as gw

from flextoolslib import *
from flexlibs import AllProjectNames

import FTPaths

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Open Multiple FLEx Projects",
        FTM_Version    : "3.12",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Select one or more FLEx project and automatically open them one by one.",
        FTM_Help       :"",
        FTM_Description:  
f"""
Select one or more FLEx project and automatically open them one by one. The tool waits unit one project is open before opening the next.
""" }

LIMIT_SECS = 40

class MainWindow(QMainWindow):
    def __init__(self, project_names):
        super().__init__()
        self.initUI(project_names)
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.returnVal = False

    def initUI(self, project_names):
        self.setWindowTitle('Select FLEx Projects')
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set a layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Create a label and list widget for project names
        projectLabel = QLabel('FLEx project names (multi-select):')
        layout.addWidget(projectLabel)

        self.listWidget = QListWidget()
        self.listWidget.addItems(project_names)
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
        self.okButton.clicked.connect(self.okButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

    def okButtonClicked(self):
        selectedItems = self.listWidget.selectedItems()
        selectedProjects = [item.text() for item in selectedItems]
        self.selectedProjects = selectedProjects
        self.returnVal = True
        self.close()

    def cancelButtonClicked(self):
        self.selectedProjects = []
        self.close()

def is_flex_open(projName):

    # Check if a window with the project name is open
    windows = gw.getWindowsWithTitle(f'{projName} - Fieldworks')
    return len(windows) > 0

def MainFunction(DB, report, modifyAllowed):

    app = QApplication(sys.argv)
    mainWindow = MainWindow(AllProjectNames())
    mainWindow.show()
    app.exec_()

    # Get the Fieldworks folder path
    fieldworksDir = os.getenv('FIELDWORKSDIR')
    flexExe = os.path.join(fieldworksDir, 'flex.exe')

    if mainWindow.returnVal:

        # Loop through selected projects and open them
        for proj in mainWindow.selectedProjects:

            if is_flex_open(proj):

                report.Info(f"The {proj} project is already open. Skipping.")
                continue

            process = Popen([flexExe, '-db', proj], creationflags=DETACHED_PROCESS)

            secs = 0
            while not is_flex_open(proj):

                time.sleep(1)  # Check every second if the project is fully opened
                secs += 1

                if secs >= LIMIT_SECS:

                    report.Info(f"Couldn't detect the {proj} project as open after {str(secs)} seconds. Skipping.")
                    break

            if secs < LIMIT_SECS:

                report.Info(f'The {proj} project took about {str(secs)} seconds to open.')
                time.sleep(2) # Give a little more time to finish opening.

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()