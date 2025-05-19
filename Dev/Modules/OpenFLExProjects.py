#
#   OpenFLExProjects
#
#   Ron Lockwood
#   SIL International
#   2/20/2025
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
from PyQt5.QtCore import QCoreApplication
import pygetwindow as gw

from flextoolslib import *
from flexlibs import AllProjectNames

import Mixpanel
import FTPaths
import ReadConfig
import Utils

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'OpenFLExProjects'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Open Multiple FLEx Projects",
        FTM_Version    : "3.13.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("OpenFLExProjects", "Select one or more FLEx project and automatically open them one by one."),
        FTM_Help       :"",
        FTM_Description: _translate("OpenFLExProjects", 
f"""Select one or more FLEx project and automatically open them one by one. The tool waits until one project is open before opening the next.""")}

app.quit()
del app

LIMIT_SECS = 40

class MainWindow(QMainWindow):
    def __init__(self, project_names):
        super().__init__()
        self.initUI(project_names)
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.returnVal = False

    def initUI(self, project_names):
        self.setWindowTitle('Open Multiple FLEx Projects')
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set a layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Create a label and list widget for project names
        projectLabel = QLabel(_translate("OpenFLExProjects", "FLEx project names (multi-select):"))
        layout.addWidget(projectLabel)

        self.listWidget = QListWidget()
        self.listWidget.addItems(project_names)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.listWidget)

        # Create OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        self.okButton = QPushButton(_translate("OpenFLExProjects", "OK"))
        self.cancelButton = QPushButton(_translate("OpenFLExProjects", "Cancel"))
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

def isFLExOpen(projName):

    # Check if a window with the project name is open
    windows = gw.getWindowsWithTitle(f'{projName} - Fieldworks')
    return len(windows) > 0

def MainFunction(DB, report, modifyAllowed):

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

    mainWindow = MainWindow(AllProjectNames())
    mainWindow.show()
    app.exec_()

    # Get the Fieldworks folder path
    fieldworksDir = os.getenv('FIELDWORKSDIR')
    flexExe = os.path.join(fieldworksDir, 'flex.exe')

    if mainWindow.returnVal:

        # Loop through selected projects and open them
        for proj in mainWindow.selectedProjects:

            if isFLExOpen(proj):

                report.Info(_translate("OpenFLExProjects", "The {proj} project is already open. Skipping.").format(proj=proj))
                continue

            process = Popen([flexExe, '-db', proj], creationflags=DETACHED_PROCESS)

            secs = 0
            while not isFLExOpen(proj):

                time.sleep(1)  # Check every second if the project is fully opened
                secs += 1

                if secs >= LIMIT_SECS:
                    report.Info(_translate("OpenFLExProjects", "Couldn't detect the {proj} project as open after {secs} seconds. Skipping.").format(proj=proj, secs=str(secs)))
                    break

            if secs < LIMIT_SECS:
                report.Info(_translate("OpenFLExProjects", "The {proj} project took about {secs} seconds to open.").format(proj=proj, secs=str(secs)))
                time.sleep(2)  # Give a little more time to finish opening.

#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()