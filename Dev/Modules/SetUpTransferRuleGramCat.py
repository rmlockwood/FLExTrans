#
#   SetUpTransferRuleGramCat.py
#
#   Ron Lockwood
#   SIL International
#   2/22/18
#
#   Version 3.14.1 - 6/18/25 - Ron Lockwood
#    Fixes #998. Use ElementTree to parse the transfer rules file.
#
#   Version 3.14 - 5/28/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.2 - 6/04/25 - Sara Mason
#    fixed a typo in the FTM_Synopsis
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    use as string & as vern string functions
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11 - 8/20/24 - Ron Lockwood
#    Bumped to 3.11.
#
#   Version 3.10 - 1/18/24 - Ron Lockwood
#    Bumped to 3.10.
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
#   earlier version history removed on 3/10/25
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
import xml.etree.ElementTree as ET

from SIL.LCModel import ( # type: ignore
    IFsClosedFeature,
    FsClosedFeatureTags,
    IMoInflAffixSlotRepository,
    IMoInflAffMsa,
    )

from flextoolslib import *                                          

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QCoreApplication

import Mixpanel
import FTPaths
import Utils
import ReadConfig
from RuleCatsAndAttribs import Ui_CatsAndAttribsWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'SetUpTransferRuleGramCat'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'RuleCatsAndAttribs'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : "Set Up Transfer Rule Categories and Attributes",
        FTM_Version    : "3.14.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("SetUpTransferRuleGramCat", 'Set up the transfer rule file with categories and attributes from source and target FLEx projects.') ,
        FTM_Help   : "",
        FTM_Description: _translate("SetUpTransferRuleGramCat", 
"""This module first goes through both the source and target FLEx databases and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.""")}

app.quit()
del app
                 
slot2AffixListMap = {}
GRAM_CAT = 'a_gram_cat'

class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_CatsAndAttribsWindow()
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

def sortChildren(parentElement, childElementName):

    # Group elements with preceding comments
    groups = []
    currentGroup = []

    for child in list(parentElement):

        if isinstance(child.tag, str) and child.tag == childElementName:

            currentGroup.append(child)
            groups.append(list(currentGroup))
            currentGroup = []
        else:
            # Comment or processing instruction
            currentGroup.append(child)

    # Sort groups by the 'n' attribute of the element
    def getSortKey(group):

        for el in group:

            if isinstance(el.tag, str) and el.tag == childElementName:

                return el.get('n', '').lower()

        return ''

    groupsSorted = sorted(groups, key=getSortKey)

    # Remove all children
    for child in list(parentElement):

        parentElement.remove(child)

    # Re-append in sorted order
    for group in groupsSorted:

        for el in group:

            parentElement.append(el)

def processDefCat(sectionDefCats, srcPOSmap):

    ## Process the categories, adding them to the cat definitions. Don't change existing categories.
    ## Keep the categories in alphabetical order.
    
    i = 0

    for tag in srcPOSmap:
            
        def_cat = sectionDefCats.find(f"./def-cat[@n='c_{tag}']")

        if def_cat is None:

            def_cat = ET.SubElement(sectionDefCats, 'def-cat', n=f'c_{tag}')
            def_cat_item1 = ET.SubElement(def_cat, 'cat-item', tags=tag)
            def_cat_item2 = ET.SubElement(def_cat, 'cat-item', tags=f'{tag}.*') 
            # sectionDefCats.append(def_cat)
            i += 1

    sortChildren(sectionDefCats, 'def-cat')

    return i+1  # return the number of categories added

def processGramCat(sectionDefAttrs, POSmap, nameStr):

    # Delete the deff-attr labeled a_gram_cat
    def_attr = sectionDefAttrs.find(f"./def-attr[@n='{nameStr}']")

    if def_attr is not None:

        sectionDefAttrs.remove(def_attr)

    # Create a new def-attr for a_gram_cat
    def_attr = ET.SubElement(sectionDefAttrs, 'def-attr', n=nameStr)

    # Loop through all of the category abbreviations and names in alphabetical order
    for pos_abbr, pos_name in sorted(list(POSmap.items()), key=lambda k_v: (k_v[0].lower(), k_v[1])):

        def_attr_item = ET.SubElement(def_attr, 'attr-item', c=pos_name, tags=Utils.underscores(pos_abbr))
        # def_attr.append(def_attr_item)

    return
        
def formatAttrib(attrib, thingType):
    
    attrib = re.sub(' ', '_', attrib)
    return f'a_{attrib}_{thingType}'

def processDefAttr(sectionDefAttrs, POSmap, masterAttribList): 
    
    count = 0
    
    # go through the master list 
    for attrib in masterAttribList.keys():
        
        thingType = masterAttribList[attrib][2] # third part of the tuple is the thing type, e.g. feat, class or slot
        
        # Skip the attribute if we are not supposed to override it
        if not masterAttribList[attrib][0]:

            continue # 1st part of the tuple is the override flag

        def_attr = sectionDefAttrs.find(f"./def-attr[@n='a_{attrib}_{thingType}']")

        # Skip the attribute if it already exists
        if def_attr:

            continue
        else:
            # If the attribute doesn't exist, we need to create it.
            def_attr = ET.SubElement(sectionDefAttrs, 'def-attr', n=f'a_{attrib}_{thingType}')

            # Create attr-item elements for each value in the list
            for val in masterAttribList[attrib][1]:

                def_attr_item = ET.SubElement(def_attr, 'attr-item', tags=Utils.underscores(val))

            count += 1
                
    # Process a_gram_cat
    processGramCat(sectionDefAttrs, POSmap, GRAM_CAT)

    sortChildren(sectionDefAttrs, 'def-attr')
                    
    return count

def processClassesForPos(masterAttribList, overrideClass, pos, dbType, report, countList, thingType):
    
    posFullNameStr = pos.ToString()
        
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
        featureGroupName = Utils.as_string(feat.Name)
        
        # Correct issues (like spaces or dots, etc.) in the POS full name. Also show warnings for each issue.
        countList, featureGroupName = Utils.check_for_cat_errors(report, dbType, featureGroupName, featureGroupName, countList, 1, thingType) # 1 for numCatErrorsToShow
        
        featList = []
        
        for val in feat.ValuesOC:
            
            featAbbr = Utils.as_string(val.Abbreviation)
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
    
    slotName = Utils.as_string(slot.Name)
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
                
                gloss = Utils.as_string(mySense.Gloss)
                
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
    
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    masterAttribList = {}
    srcPOSmap = {}
    POSmap = {}
    # defCatStart = defAttrStart = sectDefAttrEnd = 0
    
    window = Main()
    window.show()
    app.exec_()
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

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
    transferRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=True)

    # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the Output folder.
    if not transferRulesFile:
        TargetDB.CloseProject()
        return
    
    # Make a backup copy of the transfer rule file
    try:
        shutil.copy2(transferRulesFile, transferRulesFile+'.old')
    except:
        report.Error(_translate("SetUpTransferRuleGramCat", 'There was a problem finding the transfer rules file. Check your configuration.'))
        TargetDB.CloseProject()
        return

    # Parse the XML file using ElementTree
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(transferRulesFile, parser=parser)
        root = tree.getroot()

    except Exception as e:

        report.Error(_translate("SetUpTransferRuleGramCat", 'The transfer rules file is malformed or not valid XML.'))
        TargetDB.CloseProject()
        return
    
    # Find the section-def-cats and section-def-attrs elements
    sectionDefCats = root.find('section-def-cats')
    sectionDefAttrs = root.find('section-def-attrs')

    if sectionDefCats is None or sectionDefAttrs is None:

        report.Error(_translate("SetUpTransferRuleGramCat", 'The transfer rules file is missing required sections.'))
        TargetDB.CloseProject()
        return

    # Get just source categories
    if Utils.get_categories(DB, report, srcPOSmap, TargetDB=None, numCatErrorsToShow=99, addInflectionClasses=False) == True:

        TargetDB.CloseProject()
        return

    # Process categories
    catCount = processDefCat(sectionDefCats, srcPOSmap)
    
    # Get all source and target categories
    if Utils.get_categories(DB, report, POSmap, TargetDB, numCatErrorsToShow=99, addInflectionClasses=False) == True:
        
        TargetDB.CloseProject()
        return

    TargetDB.CloseProject()
    
    # Process attributes
    attrCount = processDefAttr(sectionDefAttrs, POSmap, masterAttribList)

    # Write the xml tree back to the transfer rules file
    try:
        with open(transferRulesFile, 'wb') as fout:
            fout.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf-8'))
            fout.write('<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN" "transfer.dtd">\n'.encode('utf-8'))
            ET.indent(root)
            fout.write(ET.tostring(root, encoding='utf-8'))

    except Exception as e:

        report.Error(_translate("SetUpTransferRuleGramCat", 'There was a problem writing the transfer rules file: {error}').format(error=str(e)))
        return
    
    report.Info(_translate("SetUpTransferRuleGramCat", '{attrCount} attributes added to the attributes section.').format(attrCount=attrCount))
    report.Info(_translate("SetUpTransferRuleGramCat", '{num} categories created for the a_gram_cat attribute.').format(num=len(POSmap)))
    report.Info(_translate("SetUpTransferRuleGramCat", '{catCount} categories added to the categories section.').format(catCount=catCount))

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
