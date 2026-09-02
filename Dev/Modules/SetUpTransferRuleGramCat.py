#
#   SetUpTransferRuleGramCat.py
#
#   Ron Lockwood
#   SIL International
#   2/22/18
#
#   Version 3.17.2 - 9/2/26 - Ron Lockwood
#    Added the code description block at the top with an overview, what it writes and code structure.
#
#   Version 3.17.1 - 9/2/26 - Ron Lockwood
#    The backup of the prior transfer rules now goes in Output\rule-file-history through RuleFileHistory instead of the single .old file beside the rules file.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.1 - 6/28/26 - Ron Lockwood
#    One project mode: the target is the same as the source project, so don't open or gather data from a separate target project.
#
#   Version 3.16 - 4/30/26 - Ron Lockwood
#    Bump to version 3.16.
#
#   Version 3.15.1 - 3/6/26 - Ron Lockwood
#    Upgraded to PyQt6 and Python 3.13.
#
#   Version 3.15 - 2/6/26 - Ron Lockwood
#    Bumped to 3.15.
#
#   Version 3.14.3 - 1/20/26 - Ron Lockwood
#    Added missing transl() around module name.
#
#   Version 3.14.2 - 7/28/25 - Ron Lockwood
#    Reference module names by docs variable.
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
#   2023 version history removed on 2/6/26
#
#   earlier version history removed on 3/10/25
#
#   OVERVIEW (AI generated, then edited)
#
#   Transfer rules are written in terms of categories and attributes - a rule matches a c_verb, tests an a_gender_feature, sets an a_tense_feature - and all of those have to be defined at the top of
#   the transfer rules file before any rule can use them. This module is what fills that part of the file in, taking the definitions from the FLEx projects so that the user doesn't have to type them
#   or keep them up to date by hand. It rewrites the categories and attributes sections of the transfer rules file and touches nothing else, so it can be run again whenever a project gains a
#   category or a feature.
#
#   WHAT IT WRITES
#
#   Three kinds of thing go into the file:
#    - A def-cat named c_<category> for every grammatical category in the SOURCE project, holding a cat-item for the bare tag and one for tag.* so that the category matches a word whether or not it
#      carries further tags. A category already in the file is left exactly as it is, since the user may have hand-tuned it; only missing ones are added.
#    - The a_gram_cat attribute, which is the list of every category name a rule can compare against. This one is deleted and rebuilt from scratch on each run, from the categories of BOTH projects
#      merged and de-duplicated - the same synthesis the bilingual lexicon is built from, which is what lets a rule name a target category as well as a source one.
#    - An attribute per inflection feature, inflection class and template slot, named a_<name>_<kind>, holding that thing's possible values: the values of a closed feature, the abbreviations of a
#      part of speech's inflection classes, or the glosses of the affixes that fill a slot. Which of the three kinds get written, and whether an attribute that already exists is overwritten or left
#      alone, is what the checkboxes in the window shown at the start decide.
#
#   Names coming out of FLEx are put through the same conventions the bilingual lexicon uses - spaces become underscores, periods and slashes are dropped - and anything that had to be corrected is
#   reported as a warning, so the user can see why a name in the rules file doesn't look quite like the one in FLEx. Both sections are sorted alphabetically on the way out, with each element's
#   preceding XML comments carried along with it so that a comment never ends up attached to the wrong definition.
#
#   Because the whole file is rewritten, a copy of the prior version is saved first in Output\rule-file-history, tagged before_cat_setup. That is the same folder the Live Rule Tester, Start Testbed,
#   the Rule Assistant and AI Rule Studio save into, so the whole history of a project's rules is one sorted listing. If that copy can't be made, the module stops without writing anything.
#
#   CODE STRUCTURE
#
#   Main is the small window of checkboxes shown before any work happens; MainFunction reads what it was set to and drives the rest. getThings() is the gathering half - it walks the source project
#   and, unless the project is in One project mode (where the target is the same project), the target project too, calling processFeatures(), processClassesForPos() or processSlots() on each item to
#   build up masterAttribList, a map of name to AttribInfo holding the values, the kind and whether to override. getSlot2AffixListMap() is the extra pass that slots need, since a slot's values are
#   the glosses of the affixes that go in it rather than anything on the slot itself. fillOutDefCat(), fillOutGramCat() and fillOutDefAttr() are the writing half, and sortChildren() is the
#   comment-aware sort they finish with.
#

import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

from SIL.LCModel import ( # type: ignore
    IFsClosedFeature,
    FsClosedFeatureTags,
    IMoInflAffixSlotRepository,
    IMoInflAffMsa,
    )

from flextoolslib import * # type: ignore

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QCoreApplication

import Mixpanel
import FTPaths
import Utils
import ReadConfig
import RuleFileHistory
from RuleCatsAndAttribs import Ui_CatsAndAttribsWindow

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'SetUpTransferRuleGramCat'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication(['FLExTrans'])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'RuleCatsAndAttribs'] 

#----------------------------------------------------------------
# Documentation that the user sees:
docs = {FTM_Name       : _translate("SetUpTransferRuleGramCat", "Set Up Transfer Rule Categories and Attributes"),
        FTM_Version    : "3.17.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("SetUpTransferRuleGramCat", 'Set up the transfer rule file with categories and attributes from source and target FLEx projects.') ,
        FTM_Help   : "",
        FTM_Description: _translate("SetUpTransferRuleGramCat", 
"""This module first goes through both the source and target FLEx projects and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
This module will also populate the categories section of the transfer rule file with
grammatical categories from the source FLEx project. This module will also create
attributes in the transfer rule file from FLEx inflection features, inflection classes
and template slots. You can decide which of these are used and whether existing attributes
should be overwritten.""")}

#app.quit()
#del app
                 
slot2AffixListMap = {}
GRAM_CAT = 'a_gram_cat'

@dataclass
class AttribInfo:
    override: bool
    abbrList: List[str]
    thingType: str  # 'feat', 'class' or 'slot'

class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_CatsAndAttribsWindow()
        self.ui.setupUi(self)
        self.retVal = False
        
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

def fillOutDefCat(sectionDefCats, srcPOSmap):

    ## Process the categories, adding them to the cat definitions. Don't change existing categories.
    ## Keep the categories in alphabetical order.
    
    count = 0

    for tag in srcPOSmap:
            
        def_cat = sectionDefCats.find(f"./def-cat[@n='c_{tag}']")

        if def_cat is None:

            def_cat = ET.SubElement(sectionDefCats, 'def-cat', n=f'c_{tag}')
            def_cat_item1 = ET.SubElement(def_cat, 'cat-item', tags=tag)
            def_cat_item2 = ET.SubElement(def_cat, 'cat-item', tags=f'{tag}.*') 
            count += 1

    sortChildren(sectionDefCats, 'def-cat')
    return count  # return the number of categories added

def fillOutGramCat(sectionDefAttrs, POSmap, nameStr):

    # Delete the deff-attr labeled a_gram_cat
    def_attr = sectionDefAttrs.find(f"./def-attr[@n='{nameStr}']")

    if def_attr is not None:

        sectionDefAttrs.remove(def_attr)

    # Create a new def-attr for a_gram_cat
    def_attr = ET.SubElement(sectionDefAttrs, 'def-attr', n=nameStr)

    # Loop through all of the category abbreviations and names in alphabetical order
    for pos_abbr, pos_name in sorted(list(POSmap.items()), key=lambda k_v: (k_v[0].lower(), k_v[1])):

        # We are setting the c (comment) attribute even though it doesn't get displayed in XXE.
        def_attr_item = ET.SubElement(def_attr, 'attr-item', c=pos_name, tags=Utils.underscores(pos_abbr))

    return
        
def fillOutDefAttr(sectionDefAttrs, POSmap, masterAttribList): 
    
    count = 0
    
    # go through the master list 
    for attrib in masterAttribList.keys():

        thingType = masterAttribList[attrib].thingType 
        def_attr = sectionDefAttrs.find(f"./def-attr[@n='a_{attrib}_{thingType}']")

        # Skip the attribute if it already exists and we are not supposed to override it
        if def_attr and not masterAttribList[attrib].override:

            continue
        else:
            # If the attribute doesn't exist, we need to create it.
            if not def_attr:

                def_attr = ET.SubElement(sectionDefAttrs, 'def-attr', n=f'a_{attrib}_{thingType}')
            else:
                # If it does exist, we need to clear its children so we can add new ones
                for child in list(def_attr):

                    def_attr.remove(child)

            # Create attr-item elements for each value in the list
            for val in masterAttribList[attrib].abbrList:  

                def_attr_item = ET.SubElement(def_attr, 'attr-item', tags=Utils.underscores(val))

            count += 1
                
    # Process the special attribute a_gram_cat
    fillOutGramCat(sectionDefAttrs, POSmap, GRAM_CAT)
    sortChildren(sectionDefAttrs, 'def-attr')
                    
    return count

def processClassesForPos(masterAttribList, overrideClass, pos, dbType, report, countList, thingType):
    
    posFullNameStr = pos.ToString()
        
    if pos.InflectionClassesOC and len(pos.InflectionClassesOC.ToArray()) > 0:
        
        # Get a list of abbreviation and name tuples
        AN_list = Utils.get_sub_inflection_classes(pos.InflectionClassesOC)
        
        classAbbrList = [an[0] for an in AN_list]  # Get the first part of the tuple, which is the abbreviation
        
        # add the pos full name to the map along with the inflection class abbreviations that go with it
        if posFullNameStr not in masterAttribList:
            
            masterAttribList[posFullNameStr] = AttribInfo(overrideClass, classAbbrList, thingType)
            
        # add any new inflection class abbreviations
        else:
            existinglist = masterAttribList[posFullNameStr].abbrList  
            newList = list(set(classAbbrList).union(set(existinglist)))
            masterAttribList[posFullNameStr] = AttribInfo(overrideClass, newList, thingType)

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
            
            masterAttribList[featureGroupName] = AttribInfo(overrideFeat, featList, thingType)
            
        # add any new inflection feature abbreviations
        else:
            existinglist = masterAttribList[featureGroupName].abbrList 
            newList = list(set(featList).union(set(existinglist)))
            masterAttribList[featureGroupName] = AttribInfo(overrideFeat, newList, thingType)
            
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
        
        masterAttribList[slotName] = AttribInfo(override, affList, thingType)
        
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
    dbList = [(DB, 'source')]

    # In One project mode the target is the same as the source project (TargetDB is None), so don't gather the same data twice.
    if TargetDB is not None:

        dbList.append((TargetDB, 'target'))

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
    
    return not haveError

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    translators = []
    app = QApplication.instance()

    if app is None:
        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    masterAttribList = {}
    srcPOSmap = {}
    POSmap = {}
    
    window = Main()
    window.show()
    app.exec()
    
    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # In One project mode the target is the same as the source project, so there is no separate target project to open or read
    # data from. Use None for the target; getThings and get_categories then gather only the (shared) source data.
    oneProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) == 'n'

    if oneProjectMode:

        TargetDB = None
    else:

        # Open the target database
        TargetDB = Utils.openTargetProject(configMap, report)

    # Close the target project if we opened one (nothing to close in One project mode).
    def closeTarget():

        if TargetDB:

            TargetDB.CloseProject()

    # Get the different kinds of attributes
    if window.retVal == False:
    
        return
        
    if window.doFeat:
        
        if not getThings(masterAttribList, window.overrideFeat, DB, TargetDB, report, processFeatures, 'feature'):
        
            closeTarget()
            return

    if window.doClass:
        
        if not getThings(masterAttribList, window.overrideClass, DB, TargetDB, report, processClassesForPos, 'class'):
            
            closeTarget()
            return

    if window.doSlot:
        
        if not getThings(masterAttribList, window.overrideSlot, DB, TargetDB, report, processSlots, 'slot'):
            
            closeTarget()
            return

    # Get the path to the transfer rules file
    transferRulesFile = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=True)

    # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the Output folder.
    if not transferRulesFile:

        closeTarget()
        return
    
    # This tool rewrites the transfer rules file, so a copy of the prior version has to be in hand before it does. That copy goes in the one rule file history folder the other rule-changing tools
    # save into, dated, instead of the single .old file beside the rules file that earlier versions overwrote each run. Only the main rules file is saved; this tool writes no other phase.
    if not os.path.isfile(transferRulesFile):

        report.Error(_translate("SetUpTransferRuleGramCat", 'There was a problem finding the transfer rules file. Check your configuration.'))
        closeTarget()
        return

    _, errorMsg = RuleFileHistory.saveHistoryCopy(transferRulesFile, RuleFileHistory.TAG_BEFORE_CAT_SETUP)

    if errorMsg:

        report.Error(_translate("SetUpTransferRuleGramCat", 'The transfer rules file could not be saved to the rule file history folder, so it was left unchanged. The error was: {errorText}').format(errorText=errorMsg))
        closeTarget()
        return

    # Parse the XML file using ElementTree
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(transferRulesFile, parser=parser)
        root = tree.getroot()

    except Exception as e:

        report.Error(_translate("SetUpTransferRuleGramCat", 'The transfer rules file is malformed or not valid XML.'))
        closeTarget()
        return
    
    # Find the section-def-cats and section-def-attrs elements
    sectionDefCats = root.find('section-def-cats')
    sectionDefAttrs = root.find('section-def-attrs')

    if sectionDefCats is None or sectionDefAttrs is None:

        report.Error(_translate("SetUpTransferRuleGramCat", 'The transfer rules file is missing required sections.'))
        closeTarget()
        return

    # Get just source categories
    if Utils.get_categories(DB, report, srcPOSmap, TargetDB=None, numCatErrorsToShow=99, addInflectionClasses=False) == True:

        closeTarget()
        return

    # Process source categories
    catCount = fillOutDefCat(sectionDefCats, srcPOSmap)
    
    # Get all source and target categories
    if Utils.get_categories(DB, report, POSmap, TargetDB, numCatErrorsToShow=99, addInflectionClasses=False) == True:
        
        closeTarget()
        return

    closeTarget()
    
    # Process attributes
    attrCount = fillOutDefAttr(sectionDefAttrs, POSmap, masterAttribList)

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
