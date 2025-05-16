#
#   NewEntryDlg
#
#   Ron Lockwood
#   SIL International
#   12/30/24
#
#   Version 3.13.3 - 5/15/25 - Ron Lockwood
#    Fixes crash when no cluster projects are defined in the settings file and you
#    attempt to add a new entry.
#
#   Version 3.13.2 - 4/28/25 - Ron Lockwood
#    Fixes #975. Initialize the return value to False.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.3 - 12/30/24 - Ron Lockwood
#    Handle missing project.
#
#   Version 3.12.2 - 12/30/24 - Ron Lockwood
#    Support for cluster projects. Moved from LinkSenseTool.py
#
#   Allow the user to add a new entry.

import json
import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QDialog, QLineEdit

from System import Guid   # type: ignore
from System import String # type: ignore
from SIL.LCModel import ( # type: ignore
    ILexEntryFactory,
    IMoStemAllomorphFactory,
    IMoStemMsaFactory,
    ILexSenseFactory,
    ICmObjectRepository,
    ICmPossibility
    )

import FTPaths
import Utils
import ClusterUtils
from NewEntry import Ui_Dialog

STEM_MORPH_GUID = 'd7f713e8-e8cf-11d3-9764-00c04f186933'
NEW_ENTRY_SETTINGS_FILE = 'NewEntrySettings.json'
MORPHEME_TYPE = 'morphemeType'
GRAMM_CAT = 'grammaticalCategory'
SELECTED_CLUSTER_PROJECTS = 'selectedClusterProjects'

class NewEntryDlg(QDialog):

    def __init__(self, TargetDB, report, targetMorphNames, clusterProjects):
        
        QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.clusterProjects = clusterProjects
        self.ui.setupUi(self)
        self.TargetDB = TargetDB
        self.report = report
        self.sense = None
        self.lexemeForm = ''
        self.POS = ''
        self.gloss = ''
        self.retVal = False
        self.nonInitalLexemeFormChanged = False
        self.settingsMap = {}

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), NEW_ENTRY_SETTINGS_FILE)

        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)

        header1TextStr = "Target FLEx project name"
        header2TextStr = "Lexeme Form"

        # Set the top two widgets that need to be disabled
        self.topWidget1 = self.ui.lexemeFormEdit
        self.topWidget2 = self.ui.label

        # Create all the possible widgets we need for all the cluster projects
        ClusterUtils.initClusterWidgets(self, QLineEdit, self, header1TextStr, header2TextStr, 130)

        # Load saved settings
        try:
            with open(self.settingsPath, 'r') as f:

                self.settingsMap = json.load(f)
        except:
            pass

        # Load cluster projects
        if len(self.clusterProjects) > 0:

            ClusterUtils.initClusterProjects(self, self.clusterProjects, self.settingsMap.get(SELECTED_CLUSTER_PROJECTS, []), self) # load last used cluster projects here
        else:
            # Hide cluster project widgets
            widgetsToHide = [
                self.ui.clusterProjectsLabel,
                self.ui.clusterProjectsComboBox,
            ]
            for wid in widgetsToHide:

                wid.setVisible(False)

        # Add the list of morpheme types that the user has defined as a kind of root (e.g. root, stem, bound stem, ...)
        self.ui.morphemeTypeCombo.addItems(list(filter(lambda s: s, targetMorphNames)))
        
        morphTypeStr = self.settingsMap.get(MORPHEME_TYPE, '')

        # Default to 'stem' if we didn't save it in settings.
        if not morphTypeStr:

            # Get the analysis lang string for stem. We know stem is hard-coded as guid: d7f713e8-e8cf-11d3-9764-00c04f186933
            # We are doing this rigamarole in case the analysis writing system language is not English
            repo = TargetDB.project.ServiceLocator.GetService(ICmObjectRepository)
            guid = Guid(String(STEM_MORPH_GUID))
            morphType = repo.GetObject(guid)
            morphType = ICmPossibility(morphType)
            morphTypeStr = Utils.as_string(morphType.Name)

        index = self.ui.morphemeTypeCombo.findText(morphTypeStr) 
        
        if index >= 0:      

            self.ui.morphemeTypeCombo.setCurrentIndex(index)

        # Add the list of grammatical categories
        posMap = {}
        Utils.get_categories(TargetDB, report=None, posMap=posMap)
        self.ui.gramCatCombo.addItems(sorted(posMap.keys()))

        # See if we have a setting for gramm. cat.
        gramCatStr = self.settingsMap.get(GRAMM_CAT, '')

        # If not, try 'n' as the default
        if not gramCatStr:

            gramCatStr = 'n'

        index = self.ui.gramCatCombo.findText(gramCatStr)

        if index >= 0:

            self.ui.gramCatCombo.setCurrentIndex(index)

    def updateAllForms(self):

        # If no changes were made to other forms, make all forms the same as the first
        if not self.nonInitalLexemeFormChanged:

            for i in range(1, len(self.keyWidgetList)):

                self.keyWidgetList[i].setText(self.keyWidgetList[0].text())

    def markChanged(self):

        self.nonInitalLexemeFormChanged = True

    def CancelClicked(self):
        self.retVal = False
        self.close()

    def clusterSelectionChanged(self):

        ClusterUtils.showClusterWidgets(self)

        # Connect the first line edit widget to the updateAllForms slot, the rest to markChanged
        for i, widget in enumerate(self.keyWidgetList):

            if i == 0:
                widget.textChanged.connect(self.updateAllForms)
            else:
                widget.textEdited.connect(self.markChanged)

    def OKClicked(self):

        # Give an error if they didn't give a gloss
        if not self.ui.glossEdit.text():

            QMessageBox.warning(self, 'Error Check', "You must enter a Gloss.")
        
            self.retVal = False
            return

        # Save last used settings to a json file
        self.settingsMap = {}
        self.settingsMap[MORPHEME_TYPE] = self.ui.morphemeTypeCombo.currentText()
        self.settingsMap[GRAMM_CAT] = self.ui.gramCatCombo.currentText()
        self.settingsMap[SELECTED_CLUSTER_PROJECTS] = self.ui.clusterProjectsComboBox.currentData()

        with open(self.settingsPath, 'w') as f:
            json.dump(self.settingsMap, f, indent=4)

        if len(self.clusterProjects) > 0 and len(self.ui.clusterProjectsComboBox.currentData()) > 0:

            save = False

            # Give an error if they didn't choose the default target proj
            if self.TargetDB.ProjectName() not in self.ui.clusterProjectsComboBox.currentData():

                QMessageBox.warning(self, 'Cluster Project Selection Error', \
                f"You must at least select the default target project, {self.TargetDB.ProjectName()}, among your cluster projects.")
            
                self.retVal = False
                return
            
            selectedProjects = self.ui.clusterProjectsComboBox.currentData()

            # Give an error if they didn't give a lexeme form
            for i in range(len(selectedProjects)):

                if not self.keyWidgetList[i].text():

                    QMessageBox.warning(self, 'Error Check', "You must enter all the Lexeme Forms.")
                
                    self.retVal = False
                    return

            self.setCursor(QtCore.Qt.WaitCursor)

            # Loop through all of the cluster project lexeme form widgets
            for i, proj in enumerate(selectedProjects):

                # Open the project (if it's not the default target project)
                if proj == self.TargetDB.ProjectName():

                    myTargetDB = self.TargetDB
                    save = True
                else:
                    myTargetDB = Utils.openProject(self.report, proj)

                    if not myTargetDB:

                        QMessageBox.warning(self, 'Not Found Error', "Failed to open the project: " + proj)
                        self.unsetCursor()
                        self.retVal = False
                        return
                    save = False

                self.createEntry(myTargetDB, self.keyWidgetList[i].text(), save)

                # Close the project (if not the default)
                if proj != self.TargetDB.ProjectName():

                    myTargetDB.CloseProject()

            self.unsetCursor()
        else:

            lexemeFormStr = self.ui.lexemeFormEdit.text()

            # Give an error if they didn't give a lexeme form
            if not lexemeFormStr:

                QMessageBox.warning(self, 'Error Check', "You must enter a Lexeme Form.")
            
                self.retVal = False
                return

            self.createEntry(self.TargetDB, lexemeFormStr, save=True)

        self.retVal = True
        self.close()
        
    def createEntry(self, TargetDB, lexemeFormStr, save):
            
            # Create entry
            entry = TargetDB.project.ServiceLocator.GetService(ILexEntryFactory).Create()

            # Create MoStemAllomorph and add to entry LexemeForm
            stemAllo = TargetDB.project.ServiceLocator.GetService(IMoStemAllomorphFactory).Create()
            entry.LexemeFormOA = stemAllo

            if save:
                self.lexemeForm = lexemeFormStr

            # Set the lexeme form.
            stemAllo.Form.set_String(TargetDB.project.DefaultVernWs, lexemeFormStr)

            # Set the morph type.
            plist = TargetDB.lp.LexDbOA.MorphTypesOA
            stemAllo.MorphTypeRA = plist.FindPossibilityByName(plist.PossibilitiesOS, self.ui.morphemeTypeCombo.currentText(), TargetDB.project.DefaultAnalWs)

            # Create MoStemMsa and add to entry MorphoSyntaxAnalyses
            stemMsa = TargetDB.project.ServiceLocator.GetService(IMoStemMsaFactory).Create()
            entry.MorphoSyntaxAnalysesOC.Add(stemMsa)

            if save:
                self.POS = self.ui.gramCatCombo.currentText()

            # Set the gram. cat.
            plist = TargetDB.lp.PartsOfSpeechOA
            stemMsa.PartOfSpeechRA = plist.FindPossibilityByName(plist.PossibilitiesOS, self.ui.gramCatCombo.currentText(), TargetDB.project.DefaultAnalWs)

            # Create sense and add to entry and set the sense msa to the stemMsa above
            mySense = TargetDB.project.ServiceLocator.GetService(ILexSenseFactory).Create()

            if save:
                self.sense = mySense
            
            entry.SensesOS.Add(mySense)
            mySense.MorphoSyntaxAnalysisRA = stemMsa

            if save:
                self.gloss = self.ui.glossEdit.text()

            # Set the gloss
            mySense.Gloss.set_String(TargetDB.project.DefaultAnalWs, self.ui.glossEdit.text())