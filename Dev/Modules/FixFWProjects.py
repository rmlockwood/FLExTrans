#
#   FixFWProject
#
#   <Module description>
#   Reference:
#   https://github.com/sillsdev/FieldWorks/blob/release/9.2/Src/Utilities/FixFwData/Program.cs
#
#   Craig Farrow
#   27 Feb 2025
#

import os.path
import sys

from flextoolslib import *
from flexlibs import FWProjectsDir

import clr

clr.AddReference("FixFWDataDll")
import ClusterUtils
import ReadConfig

clr.AddReference("SIL.LCModel.FixData")
from SIL.LCModel.FixData import FwDataFixer # type: ignore

clr.AddReference("SIL.LCModel")
from SIL.LCModel import LcmFileHelper # type: ignore

clr.AddReference("SIL.LCModel.Utils")
from SIL.LCModel.Utils import IProgress  # type: ignore

from FixClusterProjects import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui

import FTPaths

#----------------------------------------------------------------
# Documentation for the user:

docs = {FTM_Name       : "FixClusterProjects",
        FTM_Version    : 1,
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Run the Find and Fix utility on the cluster projects you choose.",
        FTM_Help       : None,
        FTM_Description: 
"""
Run the Find and Fix utility on the cluster projects you choose.
""" }


#----------------------------------------------------------------
# Dummy progress class to pass to FwDataFixer(). 
# TODO: link it with the FlexTools progress display.
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
    from FixFWProjects import NullProgress
    
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

    def __init__(self, clusterProjects):
        
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.clusterProjects = clusterProjects
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)

        # Load cluster projects
        if len(self.clusterProjects) > 0:

            ClusterUtils.initClusterProjects(self, self.clusterProjects, [], self) # load last used cluster projects here

    def OKClicked(self):

        self.selectedClusterProjects = self.ui.clusterProjectsComboBox.currentData()
        self.retVal = True
        self.close()

    def CancelClicked(self):
        self.retVal = False
        self.close()

    # This has to be here because init cluster projects above connects it to a changed event.
    def clusterSelectionChanged(self):
        pass

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

    # Get cluster projects from settings;
    clusterProjects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report)

    if not clusterProjects:

        clusterProjects = []
    else:
        # Remove blank ones
        clusterProjects = [x for x in clusterProjects if x]

    # Show the window to get the options the user wants
    app = QApplication(sys.argv)
    window = Main(clusterProjects)
    window.show()
    app.exec_()
    
    # d = FixErrorsDlg()
    # d.ShowDialog()
    # projectName = d.SelectedProject
    # projectFileName = os.path.join(FWProjectsDir,
    #                                projectName,
    #                                LcmFileHelper.GetXmlDataFileName(projectName))

    if window.retVal:

        # Loop through all the projects selected by the user
        for projName in window.selectedClusterProjects:

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

            df = FwDataFixer(projectFileName, progress, FwDataFixer.ErrorLogger(__logger), FwDataFixer.ErrorCounter(__counter))
            df.FixErrorsAndSave()

            if errorsOccurred:
                report.Warning(f"{projName}: {errorCount} errors fixed.")
            else:
                report.Info(f"{projName}: No errors found")

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
