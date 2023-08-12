#
#   SetUpTransferRuleGramCat.py
#
#   Ron Lockwood
#   SIL International
#   2/22/18
#
#   Version 3.9.1 - 8/12/23 - Ron Lockwood
#    Changes to support FLEx 9.1.22 and FlexTools 2.2.3 for Pythonnet 3.0.
#
#   Version 3.9 - 7/19/23 - Ron Lockwood
#    Bumped version to 3.9
#
#   Version 3.8.2 - 5/9/23 - Ron Lockwood
#    Don't warn if a category name has a space. When writing the corresponding
#    inflection class, convert the spaces to underscores.
#
#   Version 3.8.1 - 4/20/23 - Ron Lockwood
#    Reworked import statements
#
#   Version 3.8 - 4/18/23 - Ron Lockwood
#    Description grammatical correction.
#
#   Version 3.7.2 - 1/5/23 - Ron Lockwood
#    Fixes #229. Slots, features and classes now converted to attributes in the
#    transfer rule file. The user can choose which one and whether to override.
#
#   Version 3.7.1 - 12/28/22 - Ron Lockwood
#    Adds categories to the categories section from FLEx. This capability
#    is referenced in issue #229.
#
#   Version 3.7 - 12/13/22 - Ron Lockwood
#    Bumped version number for FLExTrans 3.7
#
#   Version 3.6 - 8/29/22 - Ron Lockwood
#    Renamed module
#
#   Version 3.5.1 - 6/24/22 - Ron Lockwood
#    Call CloseProject() for FlexTools2.1.1 fixes #159
#
#   Version 3.5 - 6/21/22 - Ron Lockwood
#    Bump version number for FlexTools 3.5
#
#   Version 3.4.1 - 3/22/22 - Ron Lockwood
#    Fixed bug #99. Give an error if the file isn't in the format that XXE
#    makes the xml file. Otherwise it's hard to find the right section of the
#    transfer rules file to make the changes.
#
#   Version 3.4 - 2/17/22 - Ron Lockwood
#    Use ReadConfig file constants.
#
#   Version 3.3.1 - 1/27/22 - Ron Lockwood
#    Major overhaul of the Setup Transfer Rule Grammatical Categories Tool.
#    Now the setup tool and the bilingual lexicon uses common code for getting
#    the grammatical categories from each lexicon. Categories are 'repaired' as 
#    needed in the process. E.g. space > underscore, etc. Fixes #50.
#
#   Version 3.3 - 1/8/22 - Ron Lockwood
#    Bump version number for FLExTrans 3.3
#
#   Version 3.2 - 10/22/21 - Ron Lockwood
#    Bump version number for FlexTools 3.2
#
#   Version 3.0 - 1/25/21 - Ron Lockwood
#    Changes for python 3 conversion
#
#   Version 2.0 - 12/2/19 - Ron Lockwood
#    Bump version number for FlexTools 2.0
#
#   Version 1.0.1 - 2/28/18 - Ron Lockwood
#    Write the DOCTYPE.
#
#   Version 1.0 - 2/22/18 - Ron Lockwood
#    Initial version.
#
#   Take the grammatical categories from the bilingual lexicon file and put them
#   into the transfer rule file as tags of an attribute called a_gram_cat. It is
#   helpful to use the categories from the bilingual lexicon file because the 
#   list created there is the synthesis of unique grammatical categories from 
#   both the source and target lexicons.
#

import os
import shutil
import re
import sys

from SIL.LCModel import (
    IFsClosedFeature,
    FsClosedFeatureTags,
    IMoInflAffixSlotRepository,
    IMoInflAffMsa,
    )
from SIL.LCModel.Core.KernelInterfaces import ITsString

from flextoolslib import *                                          

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication

import FTPaths
import Utils
import ReadConfig
from RuleCatsAndAttribs import Ui_MainWindow

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Set Up Transfer Rule Categories and Attributes",
        FTM_Version    : "3.9.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : 'Set up the transfer rule file with categories and attributes from souce and target FLEx projects.' ,
        FTM_Help   : "",
        FTM_Description: 
"""
This module first goes through both the source and target FLEx databases and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.
"""}

slot2AffixListMap = {}
GRAM_CAT = 'a_gram_cat'

class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))
        
        self.ui.OKButton.clicked.connect(self.OKClicked)
        self.ui.CancelButton.clicked.connect(self.CancelClicked)
        self.ui.PopulateFeaturesCheckbox.clicked.connect(self.FeatBoxClicked)
        self.ui.PopulateClassesCheckbox.clicked.connect(self.ClassBoxClicked)
        self.ui.PopulateSlotsCheckbox.clicked.connect(self.SlotBoxClicked)
        
    def FeatBoxClicked(self):
        
            if self.ui.PopulateFeaturesCheckbox.isChecked():
                
                self.ui.overrideFeaturesCheckbox.setEnabled(True)
                
            else:
                self.ui.overrideFeaturesCheckbox.setEnabled(False)
                
    def ClassBoxClicked(self):
        
            if self.ui.PopulateClassesCheckbox.isChecked():
                
                self.ui.overrideClassesCheckbox.setEnabled(True)
                
            else:
                self.ui.overrideClassesCheckbox.setEnabled(False)
                
    def SlotBoxClicked(self):
        
            if self.ui.PopulateSlotsCheckbox.isChecked():
                
                self.ui.overrideSlotsCheckbox.setEnabled(True)
                
            else:
                self.ui.overrideSlotsCheckbox.setEnabled(False)
                
    def CancelClicked(self):
        self.retVal = False
        self.close()
        
    def OKClicked(self):

        self.doFeat = self.ui.PopulateFeaturesCheckbox.isChecked()
        self.doClass = self.ui.PopulateClassesCheckbox.isChecked()
        self.doSlot = self.ui.PopulateSlotsCheckbox.isChecked()
        self.overrideFeat = self.ui.overrideFeaturesCheckbox.isChecked()
        self.overrideClass = self.ui.overrideClassesCheckbox.isChecked()
        self.overrideSlot = self.ui.overrideSlotsCheckbox.isChecked()
        self.retVal = True
        self.close()

def processDefCat(defCatLines, srcPOSmap, tr_out_f):

    ## Process the categories, adding them to the cat definitions. Don't change existing categories.
    ## Keep the categories in alphabetical order.
    
    existCatMap = {}
    existCatList = []
    i = 0
    
    # Process the existing category list
    while i < len(defCatLines):
        
        # here's the start of the cat definition
        if re.search('><def-cat', defCatLines[i]):
            
            start = i
            i += 1
            
            # capture the category name
            matchObj = re.search('n="(.+)"', defCatLines[i])
        
            if not matchObj:
                continue
            else:
                catName = matchObj.group(1)
            
            # Save the name    
            existCatList.append(catName)
            
            # Loop through all remaining lines for this category
            while True:
                
                i += 1
                
                # See if we hit the end of the def-cat
                if re.search('></def-cat', defCatLines[i]):
                    break
            
            # map the category name to all the lines that make up the definition
            existCatMap[catName] = defCatLines[start:i+1]
            
        i += 1
                
    # For comparison, strip the c_ from the existing categories
    strippedList = [re.sub('c_', '', tok) for tok in existCatList]
    
    # Use set subtraction to get all the FLEx categories that aren't in the existing category list
    reducedFLExList = list(set(list(srcPOSmap.keys())) - set(strippedList))
    
    # Combine the existing list with the FLEx list so we can loop through it in alphabetical order
    # Create a tuple list with the 2nd element identifying which list the category came from
    combinedList = [(cat, 'existList') for cat in existCatList]
    combinedList.extend([('c_' + cat, 'flexList') for cat in reducedFLExList])
    
    for cat, myType in sorted(combinedList, key=lambda k_v: (k_v[0], k_v[1])):
        
        if myType == 'existList':
            
            for catLine in existCatMap[cat]:
            
                tr_out_f.write(catLine)
                
        else: # flexList
            
            # write out the begin def-cat element
            tr_out_f.write('><def-cat\n')
            tr_out_f.write('n="' + cat + '"\n')
            
            # write out two tags elements, plain and with .* added.
            tr_out_f.write('><cat-item\n')
            tr_out_f.write('tags="' + cat[2:] + '"\n')
            tr_out_f.write('></cat-item\n')
            
            tr_out_f.write('><cat-item\n')
            tr_out_f.write('tags="' + cat[2:] + '.*"\n')
            tr_out_f.write('></cat-item\n')
            
            # write out the end def-cat element
            tr_out_f.write('></def-cat\n')

    # close out the category section
    tr_out_f.write('></section-def-cats\n')
            
    return len(reducedFLExList)

def createAttrLines(attrib, valList, thingType):
    
    myAttrList = []

    myAttrList.append('><def-attr\n')
    myAttrList.append(f'n="' + formatAttrib(attrib, thingType) + '"\n')
        
    for val in sorted(valList):
        
        # Convert periods to underscores
        val = Utils.underscores(val)
        
        myAttrList.append('><attr-item\n')
        myAttrList.append(f'tags="{val}"\n')
        myAttrList.append('></attr-item\n')
        
    myAttrList.append('></def-attr\n')

    return myAttrList
    
def processGramCat(POSmap, nameStr):  

    linesList = []
    
    linesList.append('><def-attr\n')
    linesList.append(f'n="{nameStr}"\n')

    # Loop through all of the category abbreviations and names
    for pos_abbr, pos_name in sorted(list(POSmap.items()), key=lambda k_v: (k_v[0].lower(), k_v[1])):
        
        linesList.append('><attr-item\n')
        linesList.append('c="' + pos_name + '"\n')
        linesList.append('tags="' + pos_abbr + '"\n')
        linesList.append('></attr-item\n')

    linesList.append('></def-attr\n')
    
    return linesList
        
def formatAttrib(attrib, thingType):
    
    attrib = re.sub(' ', '_', attrib)
    return f'a_{attrib}_{thingType}'

def processDefAttr(defAttrLines, POSmap, masterAttribList, tr_out_f): 
    
    count = 0
    name2LinesMap = {}
    attrLines = []
    
    startLine = defAttrLines.pop(0)
    
    for line in defAttrLines:
        
        if re.search('><def-attr', line):
            
            attrLines = list()
            
        elif re.search('n=', line):
            
            matchObj = re.search('n="(.+)"', line)
            
            if matchObj:
                
                attrName = matchObj.group(1)
                name2LinesMap[attrName] = attrLines
     
        attrLines.append(line)
        
    endLine = attrLines.pop()
    
    # go through the master list and add needed attributes to the names2LinesMap
    for attrib in masterAttribList.keys():
        
        thingType = masterAttribList[attrib][2] # third part of the tuple is the thing type, e.g. feat, class or slot
        
        # Skip the attribute if it already exists and we are not supposed to override it
        if formatAttrib(attrib, thingType) in name2LinesMap and not masterAttribList[attrib][0]: # 1st part of the tuple is the override flag
            
            continue
        else:
            # produce the xml lines for the def-attr element
            newList = createAttrLines(attrib, masterAttribList[attrib][1], thingType) # 2nd part is the list of values
            name2LinesMap[formatAttrib(attrib, thingType)] = newList

            count += 1
                
    # Process a_gram_cat
    name2LinesMap[GRAM_CAT] = processGramCat(POSmap, GRAM_CAT)
                    
    # Write the lines to the file
    tr_out_f.write(startLine)
               
    for attrib in sorted(name2LinesMap.keys(), key=lambda s: s.lower()):
        
        for line in name2LinesMap[attrib]:
            
            tr_out_f.write(line)

    tr_out_f.write(endLine) 
        
    return count

def processClassesForPos(masterAttribList, overrideClass, pos, dbType, report, countList, thingType):
    
    posFullNameStr = pos.ToString()
        
    # Correct issues (like spaces or dots, etc.) in the POS full name. Also show warnings for each issue.
    #countList, posFullNameStr = Utils.check_for_cat_errors(report, dbType, posFullNameStr, posFullNameStr, countList, 1, thingType) # 1 for numCatErrorsToShow

    if pos.InflectionClassesOC and len(pos.InflectionClassesOC.ToArray()) > 0:
        
        # Get a list of abbreviation and name tuples
        AN_list = Utils.get_sub_inflection_classes(pos.InflectionClassesOC)
        
        classAbbrList = []
        
        for icAbbr, _ in AN_list: # 2nd part is name which we don't need
            
            classAbbrList.append(icAbbr)
    
        # add the pos full name to the map along with the inflection class abbreviations that go with it
        if posFullNameStr not in masterAttribList:
            
            masterAttribList[posFullNameStr] = (overrideClass, classAbbrList, thingType)
            
        # add any new inflection class abbreviations
        else:
            existinglist = masterAttribList[posFullNameStr][1] # 2nd part of the tuple
            newList = list(set(classAbbrList).union(set(existinglist)))
            masterAttribList[posFullNameStr] = (overrideClass, newList, thingType)

def processFeatures(masterAttribList, overrideFeat, feat, dbType, report, countList, thingType):
    
    # Only process closed features, i.e. features that don't have sub-features
    
    if feat.ClassID == FsClosedFeatureTags.kClassId:
    
        feat = IFsClosedFeature(feat)
        featureGroupName = ITsString(feat.Name.BestAnalysisAlternative).Text
        
        # Correct issues (like spaces or dots, etc.) in the POS full name. Also show warnings for each issue.
        countList, featureGroupName = Utils.check_for_cat_errors(report, dbType, featureGroupName, featureGroupName, countList, 1, thingType) # 1 for numCatErrorsToShow
        
        featList = []
        
        for val in feat.ValuesOC:
            
            featAbbr = ITsString(val.Abbreviation.BestAnalysisAlternative).Text
            featList.append(featAbbr)

        # add the feature group name to the map along with the inflection feature abbreviations that go with it
        if featureGroupName not in masterAttribList:
            
            masterAttribList[featureGroupName] = (overrideFeat, featList, thingType)
            
        # add any new inflection feature abbreviations
        else:
            existinglist = masterAttribList[featureGroupName][1] # 2nd part of the tuple
            newList = list(set(featList).union(set(existinglist)))
            masterAttribList[featureGroupName] = (overrideFeat, newList, thingType)
            
def processSlots(masterAttribList, override, slot, dbType, report, countList, thingType):
    
    slotName = ITsString(slot.Name.BestAnalysisAlternative).Text
    slotGuid = slot.Guid.ToString()
    
    # Correct issues (like spaces or dots, etc.) in the POS full name. Also show warnings for each issue.
    countList, slotName = Utils.check_for_cat_errors(report, dbType, slotName, slotName, countList, 1, thingType) # 1 for numCatErrorsToShow
    
    if slotGuid in slot2AffixListMap:
        
        affList = slot2AffixListMap[slotGuid]
    else:
        return
    
    # add the slot name to the map along with the affix glosses that go with it. 
    # if the slot name already exists, we skip it
    if slotName not in masterAttribList:
        
        masterAttribList[slotName] = (override, affList, thingType)
        
def getSlot2AffixListMap(DB):
            
    # Loop through all the entries
    for entry in DB.LexiconAllEntries():
    
        # Check that the objects we need are valid
        if not entry.LexemeFormOA:
            
            continue
            
        if not entry.LexemeFormOA.MorphTypeRA or not entry.LexemeFormOA.MorphTypeRA.Name:
            
            continue
            
        if entry.SensesOS.Count > 0: # Entry with senses
            
            # Loop through senses
            for _, mySense in enumerate(entry.SensesOS):
                
                gloss = ITsString(mySense.Gloss.BestAnalysisAlternative).Text
                
                # Process only affixes
                if mySense.MorphoSyntaxAnalysisRA and  mySense.MorphoSyntaxAnalysisRA.ClassName == 'MoInflAffMsa' and gloss:
                    
                    senseMsa = IMoInflAffMsa(mySense.MorphoSyntaxAnalysisRA)

                    for slot in senseMsa.Slots: 
                        
                        # Build the slot name
                        slotGuid = slot.Guid.ToString()
                     
                        # If the slotGuid is not in the map yet, initialize it
                        if slotGuid not in slot2AffixListMap:
                            
                            slot2AffixListMap[slotGuid] = [gloss]
                        
                        else:   
                            # Otherwise find the list of affixes associated with this slot and add to it.
                            existingAffixList = slot2AffixListMap[slotGuid]
                            
                            # Add to the gloss list if we 
                            if gloss not in existingAffixList:
                                
                                existingAffixList.append(gloss)
    
    return
    
def getThings(masterAttribList, override, DB, TargetDB, report, processFunc, thingType):        
        
    haveError = False
    
    dbList = [(DB, 'source'), (TargetDB, 'target')]
    
    for dbTup in dbList:
        
        dbObj = dbTup[0]
        dbType = dbTup[1]

        # initialize a list of error counters to 0
        countList = [0]*len(Utils.catProbData)
    
        if thingType == 'class':
            
            listToIterate = dbObj.lp.AllPartsOfSpeech
            
        elif thingType == 'feature':
        
            listToIterate = dbObj.lp.MsFeatureSystemOA.FeaturesOC

        elif thingType == 'slot':
        
            getSlot2AffixListMap(dbObj)
            listToIterate = dbObj.ObjectsIn(IMoInflAffixSlotRepository)

        # Go through all the closed features in the current DB
        for thing in listToIterate:

            processFunc(masterAttribList, override, thing, dbType, report, countList, thingType)
            
            # check for serious error
            if countList[0] == 999:
                
                # Note we have the error, but keep going so that we give all errors at once
                # reset error (warning) counter to zero
                countList[0] = 0
                haveError = True
    
    if haveError == True:
        return True
    else:
        return False

# Check to see that we have the def-attr section in the format that XXE saves files in. Otherwise give an error.
def checkFormat(linesList, report):
            
    if '><def-attr' not in ''.join(linesList):
        
        report.Error('The transfer rules file has not yet been saved with the XML Mind editor. Change the file in the editor and then run this tool again.')
        return True
    
    return False
    
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    masterAttribList = {}
    srcPOSmap = {}
    POSmap = {}
    defCatStart = defAttrStart = sectDefAttrEnd = 0
    
    # Show the window to get the options the user wants
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Open the target database
    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the different kinds of attributes
    if window.retVal == False:
    
        return
        
    if window.doFeat:
        
        if getThings(masterAttribList, window.overrideFeat, DB, TargetDB, report, processFeatures, 'feature') == True:
        
            TargetDB.CloseProject()
            return

    if window.doClass:
        
        if getThings(masterAttribList, window.overrideClass, DB, TargetDB, report, processClassesForPos, 'class') == True:
            
            TargetDB.CloseProject()
            return

    if window.doSlot:
        
        if getThings(masterAttribList, window.overrideSlot, DB, TargetDB, report, processSlots, 'slot') == True:
            
            TargetDB.CloseProject()
            return

    # Get the path to the transfer rules file
    transfer_rules_file = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=True)

    # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the Output folder.
    if not transfer_rules_file:
        TargetDB.CloseProject()
        return
    
    # Make a backup copy of the transfer rule file
    try:
        shutil.copy2(transfer_rules_file, transfer_rules_file+'.old')
    except:
        report.Error('There was a problem finding the transfer rules file. Check your configuration.')
        TargetDB.CloseProject()
        return

    # Read in the lines of the transfer rule file
    tr_f = open(transfer_rules_file, encoding='utf-8')
    linesList = tr_f.readlines()
    tr_f.close()

    # Check for an incorrect format
    if checkFormat(linesList, report) == True:
        TargetDB.CloseProject()
        return 
    
    # Divide the lines of the file into chunks. Category lines, attribute lines and the rest
    # Note: we are not using elementTree because it doesn't preserve comments
    for i, line in enumerate(linesList):
        
        # start of categories
        if re.search('><def-cat', line) and defCatStart == 0:
            
            defCatStart = i
        
        # start of attributes
        elif re.search('><section-def-attrs', line) and defAttrStart == 0:
            
            defAttrStart = i
            
        elif re.search('></section-def-attrs', line):
            
            sectDefAttrEnd = i
            
    try:
        initialLines = linesList[0:defCatStart]
        defCatLines = linesList[defCatStart:defAttrStart]
        defAttrLines = linesList[defAttrStart:sectDefAttrEnd+1]
        remainLines = linesList[sectDefAttrEnd+1:]
        
    except:
        report.Error('The transfer rules file is malformed.')
        TargetDB.CloseProject()
        return 

    # Open the transfer file for writing
    tr_out_f = open(transfer_rules_file, 'w', encoding='utf-8')
    
    # Write the initial lines
    for line in initialLines:
        
        tr_out_f.write(line)
    
    # Get just source categories
    if Utils.get_categories(DB, report, srcPOSmap, TargetDB=None, numCatErrorsToShow=99, addInflectionClasses=False) == True:

        tr_out_f.close()
        return
        
    # Process categories
    catCount = processDefCat(defCatLines, srcPOSmap, tr_out_f)
    
    # Get all source and target categories
    if Utils.get_categories(DB, report, POSmap, TargetDB, numCatErrorsToShow=99, addInflectionClasses=False) == True:
        
        TargetDB.CloseProject()
        tr_out_f.close()
        return

    TargetDB.CloseProject()
    
    # Process attributes
    attrCount = processDefAttr(defAttrLines, POSmap, masterAttribList, tr_out_f)
    
    # Write the remaining lines
    for line in remainLines:
        
        tr_out_f.write(line)
    
    tr_out_f.close()
    
    report.Info(str(attrCount) + ' attributes added to the attributes section.')
    report.Info(str(len(POSmap)) + ' categories created for the a_gram_cat attribute.')
    report.Info(str(catCount) + ' categories added to the categories section.')

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
