#
#   AdHocConstrForCluster
#
#   Ron Lockwood
#   SIL International
#   12/12/24
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.5 - 2/7/25 - Ron Lockwood
#    Reworked to use guid strings as the things that get saved in combo box data.
#
#   Version 3.12.4 - 1/17/25 - Ron Lockwood
#    Give an error if the user didn't used the auto-complete value.
#
#   Version 3.12.3 - 1/11/25 - Ron Lockwood
#    Added logic to find a morpheme msa object if we don't have a guid match.
#
#   Version 3.12.2 - 1/15/25 - Ron Lockwood
#    Add gloss to the end of the string identifying the morpheme/allomorph.
#
#   Version 3.12.1 - 1/9/25 - Ron Lockwood
#    First working version.
#
#   Version 3.12 - 12/17/24 - Ron Lockwood
#    Initial version.
#
#
# This module adds an ad hoc coocurrence constraint to multiple 
# projects at once. 


import os
import re
import sys
from unicodedata import normalize

from System import Guid   # type: ignore
from System import String # type: ignore
from flextoolslib import *                                                 
from flexlibs import AllProjectNames
from SIL.LCModel import ( # type: ignore
    IMoAdhocProhibGrRepository, 
    IMoStemMsa, 
    IMoUnclassifiedAffixMsa, 
    IMoDerivAffMsa, 
    IMoInflAffMsa,
    IMoAlloAdhocProhibFactory,
    IMoMorphAdhocProhibFactory,
    IMoAdhocProhibGrFactory,
    IMoAdhocProhibGr,
    ICmObjectRepository,
    ILexEntry,
    IMoMorphSynAnalysis,
    IMoForm,
    )
from SIL.LCModel.Core.Text import TsStringUtils         # type: ignore
from SIL.LCModel.Core.KernelInterfaces import ITsString # type: ignore

from fuzzywuzzy import fuzz
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter, QInputDialog, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
from fuzzywuzzy import fuzz

from ClusterAdHoc import Ui_AdHocMainWindow
from ComboBox import CheckableComboBox
import FTPaths
import ReadConfig
import Utils

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Add Ad Hoc Constraint for a Cluster",
        FTM_Version    : "3.13.1",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Add an ad hoc constraint to multiple cluster projects.",    
        FTM_Help   : "",
        FTM_Description: 
"""
Add an ad hoc constraint to multiple cluster projects. 
""" }

adjacencyMap = {
    'anywhere around':  0,
    'somewhere after':  1,
    'somewhere before': 2,
    'adjacent after':   3,
    'adjacent before':  4,
}

glossPOSMap = {}

SIMILARITY_THRESHOLD = 75
EM_SPACE = '\u2003'

class GroupInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Group Input")

        layout = QVBoxLayout(self)

        self.explanatoryLabel = QLabel("This new group name will be created in all the selected cluster projects.")
        layout.addWidget(self.explanatoryLabel)

        self.groupNameLabel = QLabel("Group Name:")
        self.groupNameEdit = QLineEdit(self)
        layout.addWidget(self.groupNameLabel)
        layout.addWidget(self.groupNameEdit)

        self.groupDescLabel = QLabel("Group Description:")
        self.groupDescEdit = QLineEdit(self)
        layout.addWidget(self.groupDescLabel)
        layout.addWidget(self.groupDescEdit)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def getInputs(self):
        return self.groupNameEdit.text(), self.groupDescEdit.text()

class AdHocMain(QMainWindow):

    def __init__(self, report, DB, composed, projects):

        QMainWindow.__init__(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.report = report
        self.sourceDB = DB
        self.composed = composed
        self.origSourceDB = DB
        self.clusterProjects = projects
        self.isNewGroup = False
        self.newGroupName = ''
        self.newGroupDesc = ''
        self.ui = Ui_AdHocMainWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        self.autoCompleteWidgets = [
            self.ui.KeyMorphAllomorphLineEdit,
            self.ui.otherMorphsAllomorphsLineEdit1,
            self.ui.otherMorphsAllomorphsLineEdit2,
            self.ui.otherMorphsAllomorphsLineEdit3,
            self.ui.otherMorphsAllomorphsLineEdit4,
            self.ui.otherMorphsAllomorphsLineEdit5,
        ]

        self.ui.feedbackLabel.setText('')

        # Setup the checkable combo box for cluster projects. Replace the one from the designer tool.
        geom = self.ui.clusterProjectsComboBox.geometry() # same as old control
        self.ui.clusterProjectsComboBox.hide()
        self.ui.clusterProjectsComboBox = CheckableComboBox(self.ui.centralwidget)
        self.ui.clusterProjectsComboBox.setGeometry(geom)
        self.ui.clusterProjectsComboBox.setObjectName("clusterProjectsComboBox")
        self.ui.clusterProjectsComboBox.addItems([pj for pj in self.clusterProjects if pj])

        # Check all of them at the start
        for projectName in self.clusterProjects:

            self.ui.clusterProjectsComboBox.check(projectName)

        # Initialize the types combo
        self.ui.adHocTypeComboBox.addItems(['(Choose Type)', 'Morpheme', 'Allomorph'])

        # Load the source project combo
        self.ui.sourceProjectComboBox.addItems(AllProjectNames())

        # Default to current source project if it exists.
        index = self.ui.sourceProjectComboBox.findText(self.sourceDB.ProjectName()) 
        if index >= 0:      

            self.ui.sourceProjectComboBox.setCurrentIndex(index)

        # Initialize adjacency combo
        for desc, value in sorted(adjacencyMap.items(), key=lambda item: item[1]):

            self.ui.cannotOccurComboBox.addItem(desc, value)

        # Initialize groups, morphs, and allomorphs
        self.sourceProjectChanged(0)

        self.ui.sourceProjectComboBox.currentIndexChanged.connect(self.sourceProjectChanged)
        self.ui.addButton.clicked.connect(self.AddClicked)
        self.ui.closeButton.clicked.connect(self.closeIt)
        self.ui.newGroupButton.clicked.connect(self.promptUserForGroupDetails)
        self.ui.adHocTypeComboBox.currentIndexChanged.connect(self.typeChanged)
        self.ui.adHocGroupComboBox.currentIndexChanged.connect(self.groupChanged)

    def groupChanged(self):
        
        #if self.newGroupName == '':

        self.isNewGroup = False

    def promptUserForGroupDetails(self):

        dialog = GroupInputDialog()
        result = dialog.exec_()
        
        if result == QDialog.Accepted:

            self.newGroupName, self.newGroupDesc = dialog.getInputs()

            #adHocObj = self.createGroupObject(self.sourceDB, groupName, groupDesc)

            # Add the new group name to the list and select it
            # The group object will get created later.
            self.ui.adHocGroupComboBox.addItem(self.newGroupName, None)
            self.ui.adHocGroupComboBox.setCurrentIndex(self.ui.adHocGroupComboBox.count() - 1)
            self.isNewGroup = True

    def createGroupObject(self, DB, groupName, groupDesc):

        # Create group object and add it to the Morphological Data object
        adHocObj = DB.project.ServiceLocator.GetService(IMoAdhocProhibGrFactory).Create()
        DB.lp.MorphologicalDataOA.AdhocCoProhibitionsOC.Add(adHocObj)

        # Set the properties
        adHocObj.Name.AnalysisDefaultWritingSystem = TsStringUtils.MakeString(groupName, DB.project.DefaultAnalWs)

        if groupDesc and groupDesc != '***':
            adHocObj.Description.AnalysisDefaultWritingSystem = TsStringUtils.MakeString(groupDesc, DB.project.DefaultAnalWs)

        return adHocObj
    
    def closeIt(self):

        # Close the source project if necessary
        if self.sourceDB.ProjectName() != self.origSourceDB.ProjectName():

            self.sourceDB.CloseProject()

        self.close()
    
    def typeChanged(self):

        selectedType = self.ui.adHocTypeComboBox.currentText()
        
        if selectedType == 'Morpheme':

            completer = QCompleter(sorted(list(self.morphGuidMap.keys()), key=lambda x: x.lower()))

        elif selectedType == 'Allomorph':
        
            completer = QCompleter(sorted(list(self.allomorphGuidMap.keys()), key=lambda x: x.lower()))
        else:
            return # still on (Choose Type)
        
        completer.setCaseSensitivity(Qt.CaseInsensitive)

        for widget in self.autoCompleteWidgets:
            
            # Set the completer for the QLineEdit
            widget.clear()
            widget.setCompleter(completer)
            widget.setReadOnly(False)

        self.ui.addButton.setEnabled(True)

    def getGroupList(self, DB):

        groupList = []

        # Load the group names
        for groupObj in DB.ObjectsIn(IMoAdhocProhibGrRepository):

            groupName = Utils.as_string(groupObj.Name)
            groupList.append((groupName, groupObj))

        # Sort on the group name, ignoring '-' and making it case insensitive
        groupList.sort(key=lambda x: x[0].replace('-', '').lower())

        return groupList
    
    def updateGroups(self, DB):

        groupList = []
        self.ui.adHocGroupComboBox.clear()

        groupList = self.getGroupList(DB)

        # Load the group names
        for name, grpObj in groupList:

            self.ui.adHocGroupComboBox.addItem(name, grpObj.Guid.ToString())
        
    def sourceProjectChanged(self, index):
        
        selectedProject = self.ui.sourceProjectComboBox.currentText()

        # Show hourglass cursor 
        QApplication.setOverrideCursor(Qt.WaitCursor) 

        # If we had opened a different project from our main FlexTools project, close it
        if self.sourceDB.ProjectName() != self.origSourceDB.ProjectName():

            self.sourceDB.CloseProject()

        if selectedProject != self.origSourceDB.ProjectName():

            self.sourceDB = Utils.openProject(self.report, selectedProject)
        else:
            self.sourceDB = self.origSourceDB

        # Reload the groups combo box.
        self.updateGroups(self.sourceDB)

        # Reset maps
        self.morphGuidMap = self.getMorphs(self.sourceDB)
        self.allomorphGuidMap = self.getAllomorphs(self.sourceDB)

        # Clear and disable the line edits
        for widget in self.autoCompleteWidgets:

            widget.clear()
            widget.setReadOnly(True)

        self.ui.addButton.setEnabled(False)

        # Set the type back to (choose)
        index = self.ui.adHocTypeComboBox.findText('(Choose Type)') 
        if index >= 0:      

            self.ui.adHocTypeComboBox.setCurrentIndex(index)

        self.ui.feedbackLabel.setText('')

        # Revert back to the default cursor 
        QApplication.restoreOverrideCursor()       
                   
    def AddClicked(self):

        # Don't add anything if the key morph and 1st other morph are blank
        if self.ui.KeyMorphAllomorphLineEdit.text() == '' or self.ui.otherMorphsAllomorphsLineEdit1.text() == '':

            self.ui.feedbackLabel.setText('You need to set the key field and at least the 1st other field!')
            return

        feedbackStr = ''

        # Show hourglass cursor 
        QApplication.setOverrideCursor(Qt.WaitCursor) 

        # Determine the type of ad hoc rule
        selectedType = self.ui.adHocTypeComboBox.currentText()
                    
        guidMap = self.morphGuidMap if selectedType == 'Morpheme' else self.allomorphGuidMap

        # Lookup the msa/or allomorph for the key item
        key = self.ui.KeyMorphAllomorphLineEdit.text()

        try:
            keyGuid = origKeyGuid = guidMap[key]

        except KeyError:
            QApplication.restoreOverrideCursor()       
            QMessageBox.critical(self, 'Ad Hoc Rules', f'It looks like you may not have used the Auto Complete values. "{key}" by itself cannot be found. Type the morpheme/allomorph in the vernacular and select the auto-completed value.')
            return

        otherGuidList = []
        origOtherGuidList = []
        
        # Get the list of msa guids/allomorph guids for the other morpheme/allomorph fields
        for widget in self.autoCompleteWidgets[1:]: # skip the first one which is the key line edit

            # If we have a value, add it to the list
            if otherStr := widget.text():

                try:
                    otherGuidList.append((guidMap[otherStr], otherStr))  

                except KeyError:
                    QApplication.restoreOverrideCursor()       
                    QMessageBox.critical(self, 'Ad Hoc Rules', f'It looks like you may not have used the Auto Complete values. "{otherStr}" by itself cannot be found. Type the morpheme/allomorph in the vernacular and select the auto-completed value.')
                    return
        
        # Duplicate the list to save it for later
        origOtherGuidList = otherGuidList.copy()  

        # Loop through all projects
        for proj in self.ui.clusterProjectsComboBox.currentData():

            problemFound = False
            isSourceProject = (proj == self.sourceDB.ProjectName())
            isOrigSourceProject = (proj == self.origSourceDB.ProjectName())

            # Open the project (if not the current source project or the original source - these are already open)
            # if isOrigSourceProject:

            #     myDB = self.origSourceDB

            # elif isSourceProject:

            #     myDB = self.sourceDB
            # else:
            #     myDB = Utils.openProject(self.report, proj)

            #     if not myDB:
            #         continue
            
            myDB = Utils.openProject(self.report, proj)

            if not myDB:
                continue

            # Get the object repository
            repo = myDB.project.ServiceLocator.GetService(ICmObjectRepository)

            # Restore stuff in case it got changed below
            keyGuid = origKeyGuid
            otherGuidList = origOtherGuidList.copy()

            # If we aren't on the source project get the equivalent msa in this project
            # We try at first to see if the same guid exists which may work most of the time because the FLEx projects
            # were copied from each other. If that doesn't work, find the equivalent msa in other ways.
            if not isSourceProject:
            
                # Check if this key object exists in the project.
                try:
                    _ = repo.GetObject(Guid(String(origKeyGuid)))
                except:
                    # If it's a morpheme we can try finding the msa other ways. 
                    if selectedType == 'Morpheme':

                        keyGuid = self.findObject(self.sourceDB, myDB, origKeyGuid, key)

                        if not keyGuid:

                            feedbackStr += f'The {selectedType} {key} could not be found in the project {proj}. If the morpheme was a stem, it could be the link url to that stem was not valid.\n'
                            problemFound = True
                    
                    # We can't reliably locate allomorphs by looking for links, or glosses and POSs, so don't do find Object, just give an error.
                    else:
                        feedbackStr += f'The {selectedType} {otherStr} with the same ID does not exist in the project {proj}.\n'
                        problemFound = True

                # Loop through all the other values
                for i, (othGuid, otherStr) in enumerate(otherGuidList):

                    # Verify this other object exists in the project
                    try:
                        _ = repo.GetObject(Guid(String(othGuid)))
                    except:
                        if selectedType == 'Morpheme':

                            newGuid = self.findObject(self.sourceDB, myDB, othGuid, otherStr)

                            if not newGuid:
                                feedbackStr += f'The {selectedType} {otherStr} could not be found in the project {proj}. If the morpheme was a stem, it could be the link url to that stem was not valid.\n'
                                problemFound = True
                            
                            # Replace this object in the list
                            otherGuidList[i] = (newGuid, otherStr)

                        # Again, give up if it's an allomorph
                        else:
                            feedbackStr += f'The {selectedType} {otherStr} with the same ID does not exist in the project {proj}.\n'
                            problemFound = True

            if not problemFound:

                if selectedType == 'Morpheme':

                    # Get a factory for the ad hoc rule object and add the object 
                    adHocObj = myDB.project.ServiceLocator.GetService(IMoMorphAdhocProhibFactory).Create()
                    myDB.lp.MorphologicalDataOA.AdhocCoProhibitionsOC.Add(adHocObj)

                    # Set the properties
                    myObj = repo.GetObject(Guid(String(keyGuid)))
                    adHocObj.FirstMorphemeRA = IMoMorphSynAnalysis(myObj)

                    # Loop through all the other values
                    for othGuid, _ in otherGuidList:
                        myObj = repo.GetObject(Guid(String(othGuid)))
                        adHocObj.RestOfMorphsRS.Add(IMoMorphSynAnalysis(myObj))

                else: # selectedType == 'Allomorph':
                    
                    adHocObj = myDB.project.ServiceLocator.GetService(IMoAlloAdhocProhibFactory).Create()
                    myDB.lp.MorphologicalDataOA.AdhocCoProhibitionsOC.Add(adHocObj)

                    # Set the properties
                    adHocObj.FirstAllomorphRA = IMoForm(repo.GetObject(Guid(String(keyGuid))))

                    # Loop through all the other values
                    for othGuid, _ in otherGuidList:

                        adHocObj.RestOfAllosRS.Add(IMoForm(repo.GetObject(Guid(String(othGuid)))))

                adHocObj.Adjacency = self.ui.cannotOccurComboBox.currentData()
                feedbackStr += f'Added ad hoc rule to project {proj}.\n'
                
                validGroup = False
                groupGuid = self.ui.adHocGroupComboBox.currentData()

                # If we have a user created new group, add it to the current project and add the rule
                if self.isNewGroup or groupGuid is None: # Could be None if new group created, then switch away from it, then back

                    groupObj = self.createGroupObject(myDB, self.newGroupName, self.newGroupDesc)
                    
                    if groupObj:

                        if isSourceProject:

                            self.ui.adHocGroupComboBox.setItemData(self.ui.adHocGroupComboBox.currentIndex(), groupObj.Guid.ToString())

                        validGroup = True

                # Otherwise, try and find the group in the project or prompt the user for one
                else:
                    
                    # If it's the source project and we know it's an existing group, get the group object
                    if isSourceProject :

                        groupObj = IMoAdhocProhibGr(repo.GetObject(Guid(String(self.ui.adHocGroupComboBox.currentData()))))

                        if groupObj:

                            validGroup = True
                    else:
                        sourceGroupName = self.ui.adHocGroupComboBox.currentText()

                        # Get the group list for this project
                        groupList = self.getGroupList(myDB)

                        # See if we get an exact match on the group name
                        for groupName, groupObj in groupList:

                            if groupName == sourceGroupName:

                                validGroup = True
                                break

                        # If not, filter the list to 75% near matches
                        if not validGroup:

                            filteredGroupNames = [name for name, _ in groupList if fuzz.ratio(sourceGroupName, name) >= SIMILARITY_THRESHOLD]
                            filteredGroupNames.append(f'NEW: {sourceGroupName}')

                            # Revert back to the default cursor 
                            QApplication.restoreOverrideCursor()       

                            # Prompt the user to select a group from a list 
                            selectedGroupName = self.promptUserForGroupName(filteredGroupNames, proj)

                            # Show hourglass cursor 
                            QApplication.setOverrideCursor(Qt.WaitCursor) 

                            # Create a new group named the same as the source one when the user chooses NEW ...
                            if selectedGroupName == f'NEW: {sourceGroupName}':

                                try:
                                    desc = Utils.as_string(IMoAdhocProhibGr(repo.GetObject(Guid(String(self.ui.adHocGroupComboBox.currentData())))).Description)
                                except:
                                    desc = ''

                                groupObj = self.createGroupObject(myDB, sourceGroupName, desc)
                                validGroup = True

                            # Otherwise use the group they selected
                            else:
                                for groupName, groupObj in groupList:

                                    if groupName == selectedGroupName:

                                        validGroup = True
                                        break
                if validGroup:

                    groupObj.MembersOC.Add(adHocObj)
                    
            # Close the project (if not the default one or the current source project)
            # if not isOrigSourceProject and not isSourceProject:

            #     myDB.CloseProject()

            myDB.CloseProject()

        self.isNewGroup = False

        # Revert back to the default cursor 
        QApplication.restoreOverrideCursor()       

        # Give some feedback
        QMessageBox.information(self, 'Ad Hoc Rules', feedbackStr)

    def findObject(self, sourceDB, targetDB, myGuidStr, keyStr):

        retVal = None
        repo = sourceDB.project.ServiceLocator.GetService(ICmObjectRepository)
        msaObj = repo.GetObject(Guid(String(myGuidStr)))

        # Get the entry and sense objects from this msa object
        entryObj = ILexEntry(msaObj.Owner)
        senseObj = self.getSenseForMsa(msaObj)

        if not senseObj:
            return retVal

        # If we have a stem that is not a clitic get the link that likely exists to the appropriate sense
        if msaObj.ClassName == 'MoStemMsa' and not Utils.isClitic(entryObj):

            # Get a list of custom fields at the sense level
            idAndLabelList = sourceDB.LexiconGetSenseCustomFields()

            # Go through the labels and check the link urls until we match the project name
            for id, _ in idAndLabelList:
                
                customFieldUrl = Utils.getTargetEquivalentUrl(sourceDB, senseObj, id)
                
                if customFieldUrl and re.search(proj := targetDB.ProjectName(), re.sub(r'\+', ' ', customFieldUrl)):

                    targetSense, targetLemma, senseNum = Utils.getTargetSenseInfo(entryObj, sourceDB, targetDB, senseObj, customFieldUrl, \
                                                                                  senseNumField=None, report=None)
                    # If the url led us to a valid target sense, return that sense's msa
                    if targetSense:
                        retVal = targetSense.MorphoSyntaxAnalysisRA
                    
                    break

        # If we have an affix or clitic, find the sense by gloss and POS
        elif msaObj.ClassName == 'MoInflAffMsa' or msaObj.ClassName == 'MoDerivAffMsa' or Utils.isClitic(entryObj):

            # Parse the key string of entry/sense info. into lemma, pos and gloss
            # This is the same string that the user sees in the text boxes.
            lemma, pos, gloss = re.split(EM_SPACE, keyStr)

            # See if we have a match on the gloss and POS in our saved map for this DB, if so, return the msa
            # In theory, two senses of an entry could have identical gloss and pos, but then the msa would be the same.
            if desiredMSA := glossPOSMap.get(gloss+pos+targetDB.ProjectName(), None):

                retVal = desiredMSA
            else:
                # Loop through all entries
                for entry in targetDB.LexiconAllEntries():

                    # Skip stems
                    if entry.LexemeFormOA and entry.LexemeFormOA.ClassName == 'MoStemAllomorph':
                        continue

                    # Loop through all senses for an entry
                    for sense in entry.SensesOS:

                        # Get gloss, msa and pos
                        currGloss = Utils.as_string(sense.Gloss)
                        myMSA = self.createMSA(sense.MorphoSyntaxAnalysisRA) # Cast to the right class
                        currPOS = self.setPOS(myMSA)

                        # Save the gloss and POS with associated msa into a saved map for the current DB
                        glossPOSMap[currGloss+currPOS+targetDB.ProjectName()] = myMSA

                        # If we have a match on POS and gloss
                        if not desiredMSA and currGloss == gloss and currPOS == pos:

                            # Save the msa
                            retVal = myMSA
                            break

        if retVal:

            retVal = retVal.Guid.ToString()

        return retVal
    
    def getSenseForMsa(self, msaObj):

        # Get the entry object from this msa object
        entryObj = ILexEntry(msaObj.Owner)

        # Go through senses until we match the msa guid
        for senseObj in entryObj.SensesOS:
            
            if senseObj.MorphoSyntaxAnalysisRA.Guid == msaObj.Guid:

                return senseObj
            
        return None

    def promptUserForGroupName(self, groupNames, projectName):

        # Create an input dialog with a list of group names
        item, ok = QInputDialog.getItem(None, "Select Group", f"Similar groups in {projectName}:", groupNames, 0, False)
        
        # If the user made a selection, return the selected item
        if ok and item:
            
            return item
        else:
            # If the user didn't make a selection, return an empty string
            return ""

    def getMorphs(self, DB, composed=True):

        repo = DB.project.ServiceLocator.GetService(ICmObjectRepository)

        if composed:
            def norm(s): return normalize('NFC', s) if s else s
        else:
            def norm(s): return s

        lemmas = {}

        for entry in DB.LexiconAllEntries():

            headWord = ITsString(entry.HeadWord).Text
            headWord = Utils.add_one(headWord)
            headWord = norm(headWord)

            lastGuidStr = ''
            for i, sense in enumerate(entry.SensesOS, 1):

                if not sense.MorphoSyntaxAnalysisRA:
                    continue
                                    
                guidStr = sense.MorphoSyntaxAnalysisRA.Guid.ToString()
                #msa = self.createMSA(sense.MorphoSyntaxAnalysisRA)

                # Only keep unique MSAs
                if guidStr != lastGuidStr:

                    pos = self.setPOS(repo.GetObject(Guid(String(guidStr))))
                    gloss = Utils.as_string(sense.Gloss)

                    lemmas[f'{headWord}.{i}{EM_SPACE}{pos}{EM_SPACE}{gloss}'] = guidStr
                    lastGuidStr = guidStr

        return lemmas
    
    def getAllomorphs(self, DB, composed=True):

        if composed:
            def norm(s): return normalize('NFC', s) if s else s
        else:
            def norm(s): return s

        lemmas = {}

        for entry in DB.LexiconAllEntries():

            pos = ''
            gloss = ''

            if entry.LexemeFormOA and not entry.LexemeFormOA.IsAbstract:

                headWord = ITsString(entry.HeadWord).Text
                headWord = Utils.add_one(headWord)
                headWord = norm(headWord)

                mainAllomorphStr = ITsString(entry.LexemeFormOA.Form.VernacularDefaultWritingSystem).Text
                mainAllomorphStr = norm(mainAllomorphStr)

                for sense in entry.SensesOS:

                    if not sense.MorphoSyntaxAnalysisRA:
                        continue
                        
                    msa = self.createMSA(sense.MorphoSyntaxAnalysisRA)
                    pos = self.setPOS(msa)
                    gloss = Utils.as_string(sense.Gloss)

                    # Just want the first POS
                    break

                lemmas[f'{mainAllomorphStr}{EM_SPACE}({pos}):{EM_SPACE}{headWord}{EM_SPACE}{gloss}'] = entry.LexemeFormOA.Guid.ToString()
                #lemmas[f'{mainAllomorphStr}{EM_SPACE}({pos}):{EM_SPACE}{headWord}{EM_SPACE}{gloss}'] = entry.LexemeFormOA

            # Now get any allomorphs
            for allom in entry.AlternateFormsOS:

                if not allom.IsAbstract:

                    allomorphStr = ITsString(allom.Form.VernacularDefaultWritingSystem).Text
                    allomorphStr = norm(allomorphStr)
                    lemmas[f'{allomorphStr}{EM_SPACE}({pos}):{EM_SPACE}{headWord}{EM_SPACE}{gloss}'] = allom.Guid.ToString()
                    #lemmas[f'{allomorphStr}{EM_SPACE}({pos}):{EM_SPACE}{headWord}{EM_SPACE}{gloss}'] = allom

        return lemmas
    
    def setPOS(self, msa):

        pos = ''

        if msa.ClassName == 'MoDerivAffMsa':

            msa = IMoDerivAffMsa(msa)
            pos = Utils.as_string(msa.FromPartOfSpeechRA.Abbreviation) if msa.FromPartOfSpeechRA else '***'
            pos += ' > '
            pos += Utils.as_string(msa.ToPartOfSpeechRA.Abbreviation) if msa.ToPartOfSpeechRA else '***'
        else:
            if msa.ClassName == 'MoStemMsa':

                msa = IMoStemMsa(msa) 

            elif msa.ClassName == 'MoInflAffMsa':

                msa = IMoInflAffMsa(msa)
            else:
                return pos

            pos = Utils.as_string(msa.PartOfSpeechRA.Abbreviation) if msa.PartOfSpeechRA else '***'

        return pos

    def createMSA(self, msa):

        if msa.ClassName == 'MoInflAffMsa':

            return IMoInflAffMsa(msa)
        
        elif msa.ClassName == 'MoDerivAffMsa':

            return IMoDerivAffMsa(msa)
        
        elif msa.ClassName == 'MoUnclassifiedAffixMsa':
            
            return IMoUnclassifiedAffixMsa(msa)
        
        elif msa.ClassName == 'MoStemMsa':
            
            return IMoStemMsa(msa)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    import Mixpanel
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the cluster projects
    projects = ReadConfig.getConfigVal(configMap, ReadConfig.CLUSTER_PROJECTS, report)
    if not projects:
        report.Info("No cluster projects found. Define them in Settings.")
        return
        
    composed = ReadConfig.getConfigVal(configMap, ReadConfig.COMPOSED_CHARACTERS, report)
    composed = (composed == 'y')

    # Show the window
    app = QApplication(sys.argv)

    window = AdHocMain(report, DB, composed, projects)
    
    window.show()
    app.exec_()
    
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
