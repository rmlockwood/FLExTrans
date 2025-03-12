#
#   FixFLExProjects
#
#   Ron Lockwood
#   SIL International
#   3/3/25
#
#   Version 3.13.1 - 3/12/25 - Ron Lockwood
#    Fixes #929. Changed to list all FLEx projects.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 3/3/25 - Ron Lockwood
#    Initial version.
#
#   Run the Find and Fix utility on the cluster projects you choose.
#   This uses FLEx's built-in utility.
#

import os.path
import sys
import clr

from flextoolslib import *
from flexlibs import FWProjectsDir
from flexlibs import AllProjectNames

clr.AddReference("FixFWDataDll")

clr.AddReference("SIL.LCModel.FixData")
from SIL.LCModel.FixData import FwDataFixer # type: ignore

clr.AddReference("SIL.LCModel")
from SIL.LCModel import LcmFileHelper # type: ignore

clr.AddReference("SIL.LCModel.Utils")
from SIL.LCModel.Utils import IProgress  # type: ignore

from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QListWidget, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PyQt5 import QtGui

import ReadConfig
import FTPaths

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "Fix FLEx Projects",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Run the Find and Fix utility on the FLEx projects you choose.",
        FTM_Help       : None,
        FTM_Description: 
"""
Run the Find and Fix utility on the FLEx projects you choose. This the same utility that is available in FLEx. 
You cannot run this utility on a project that is currently open in FLEx or on the current source project even if
it is not open. Fixed errors are logged to the report pane.
""" }

#----------------------------------------------------------------
# Dummy progress class to pass to FwDataFixer(). 
#
# Note: python.net doesn't automatically make a class derived from a 
# C# interface, a C# class (it is just a Python class). The __namespace__
# assignment is required to make it a C# class.
# (See https://github.com/pythonnet/pythonnet/issues/1774#issuecomment-1111178445)
#
# Note: the use of __namespace__ creates a problem in FlexTools because
# the name of the class is no longer automatically deleted when this 
# module is re-loaded. This generates an error, viz, 'TypeError: 
# Duplicate type name within an assembly.'
# The workaround for this is to try importing it, and don't redefine the
# task if the import succeeds.
# (See https://github.com/pythonnet/pythonnet/issues/520#issuecomment-1961353677)

try:
    from FixFLExProjects import NullProgress
    
except ImportError:

    class NullProgress(IProgress):
        __namespace__ = 'FixFWProject'
        
        def __init__(self):
            self._canceling = None
            self._title = None
            self._message = None
            self._position = 0
            self._step_size = 0
            self._minimum = 0
            self._maximum = 0
            self._synchronize_invoke = None
            self._is_indeterminate = False
            self._allow_cancel = False

        def get_Canceling(self):
            return self._canceling

        def set_Canceling(self, value):
            self._canceling = value

        def Step(self, amount):
            pass

        def get_Title(self):
            return self._title

        def set_Title(self, value):
            self._title = value

        def get_Message(self):
            return self._message

        def set_Message(self, value):
            self._message = value
            print(value)

        def get_Position(self):
            return self._position

        def set_Position(self, value):
            self._position = value

        def get_StepSize(self):
            return self._step_size

        def set_StepSize(self, value):
            self._step_size = value

        def get_Minimum(self):
            return self._minimum

        def set_Minimum(self, value):
            self._minimum = value

        def get_Maximum(self):
            return self._maximum

        def set_Maximum(self, value):
            self._maximum = value

        def get_SynchronizeInvoke(self):
            return self._synchronize_invoke

        def set_SynchronizeInvoke(self, value):
            self._synchronize_invoke = value

        def get_IsIndeterminate(self):
            return self._is_indeterminate

        def set_IsIndeterminate(self, value):
            self._is_indeterminate = value

        def get_AllowCancel(self):
            return False

        def set_AllowCancel(self, value):
            pass

class Main(QMainWindow):

    def __init__(self, project_names):
        super().__init__()
        self.initUI(project_names)
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        self.returnVal = False

    def initUI(self, project_names):
        self.setWindowTitle('Fix FLEx Projects')
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

# ------------------------------------------------------- 
errorsOccurred = False
errorCount     = 0

def MainFunction(DB, report, modifyAllowed=True):
    global errorsOccurred
    global errorCount
    
    def __logger(description, errorFixed):
        global errorsOccurred
        global errorCount
        report.Info(description)
        errorsOccurred = True
        if errorFixed:
            errorCount += 1

    def __counter():
        global errorCount
        return errorCount

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Show the window to get the options the user wants
    app = QApplication(sys.argv)
    window = Main(AllProjectNames())
    window.show()
    app.exec_()
    
    if window.returnVal:

        # Loop through all the projects selected by the user
        for projName in window.selectedProjects:

            errorsOccurred = False
            errorCount     = 0
            report.Info(f"Fixing {projName}...")
            progress = NullProgress()
        
            # Build a file name
            projectFileName = os.path.join(FWProjectsDir, projName, LcmFileHelper.GetXmlDataFileName(projName))

            # Build lock file name
            lockFileName = projectFileName + ".lock"

            # Check if the project is open (has a lock file)
            if os.path.exists(lockFileName):

                report.Warning(f"{projName}: Project is open. Skipping.")
                continue
            try:
                df = FwDataFixer(projectFileName, progress, FwDataFixer.ErrorLogger(__logger), FwDataFixer.ErrorCounter(__counter))
                df.FixErrorsAndSave()

            except Exception as e:

                report.Error(f"{projName}: Skipping. {str(e)}")

            if errorsOccurred:
                report.Warning(f"{projName}: {errorCount} errors fixed.")
            else:
                report.Info(f"{projName}: No errors found")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
