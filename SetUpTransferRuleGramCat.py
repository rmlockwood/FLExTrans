#
#   SetUpTransferRuleGramCat.py
#
#   Ron Lockwood
#   SIL International
#   2/22/18
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

import shutil
import re
import sys
import xml.etree.ElementTree as ET
from FTModuleClass import *                                          
from SIL.LCModel import *                                            
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr
import Utils
import ReadConfig

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFontDialog, QMessageBox, QMainWindow, QApplication

from RuleCatsAndAttribs import Ui_MainWindow

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Set Up Transfer Rule Categories and Attributes",
        FTM_Version    : "3.7.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : 'Set up the transfer rule file with all grammatical categories needed.' ,
        FTM_Help   : "",
        FTM_Description: 
"""
This module goes through both the source and target FLEx databases and extracts
the grammatical category lists. It will replace what is currently listed for the
tags of the a_gram_cat attribute with the lists extracted. Duplicate categories
will be discarded. Also naming conventions will be followed like in the bilingual
lexicon. I.e. spaces are converted to underscores, periods and slashes are removed.
"""}

class Main(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setWindowIcon(QtGui.QIcon('FLExTransWindowIcon.ico'))
        
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

def processDefAttr(defAttrLines, POSmap, masterAttribList, tr_out_f):  
      
    count = 0
    gramCatfound = False
    endFound = False
    gramCatElementMissing = False
    savedLines = []
    
    for line in defAttrLines:
        
        if re.search('n="a_gram_cat"', line):
            
            gramCatfound = True
            tr_out_f.write(line)
            
        if re.search('></def-attr', line) and gramCatfound:
            
            endFound = True
            
        # check for end of the attribute section
        if re.search('></section-def-attrs', line) and not gramCatfound:
            
            endFound = True
            gramCatElementMissing = True
            tr_out_f.write('><def-attr\n')
            tr_out_f.write('n="a_gram_cat"\n')
        
        if not gramCatfound and not endFound:
            
            tr_out_f.write(line)

        if endFound:
            
            savedLines.append(line)

    # Loop through all of the category abbreviations and names
    for pos_abbr, pos_name in sorted(list(POSmap.items()), key=lambda k_v: (k_v[0].lower(), k_v[1])):
        
        tr_out_f.write('><attr-item\n')
        tr_out_f.write('c="' + pos_name + '"\n')
        tr_out_f.write('tags="' + pos_abbr + '"\n')
        tr_out_f.write('></attr-item\n')
        
        count += 1

    if gramCatElementMissing == True:
        
        tr_out_f.write('></def-attr\n')
        
    # Write out the rest of the lines after the grammatical category section
    for line in savedLines:
        
        tr_out_f.write(line)
        
    return count
        
#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True):
    
    masterAttribList = []
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return
    
    # Show the window
    app = QApplication(sys.argv)

    window = Main()
    
    window.show()
    
    app.exec_()
    
    if window.retVal == True:
        
        if window.doFeat:
            
            getFeatures(masterAttribList, window.overrideFeat)

        elif window.doClass:
            
            getClasses(masterAttribList, window.overrideClass)

        elif window.doSlot:
            
            getSlots(masterAttribList, window.overrideSlot)

    return 





    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the path to the transfer rules file
    transfer_rules_file = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)

    # If we don't find the transfer rules setting (from an older FLExTrans install perhaps), assume the transfer rules are in the Output folder.
    if not transfer_rules_file:
        transfer_rules_file = 'Output\\transfer_rules.t1x'
    
    POSmap = {}
    
    # Get all source and target categories
    if Utils.get_categories(DB, report, POSmap, TargetDB, numCatErrorsToShow=99, addInflectionClasses=False) == True:
        
        TargetDB.CloseProject()
        return

    TargetDB.CloseProject()
    
    srcPOSmap = {}
    
    # Get just source categories
    if Utils.get_categories(DB, report, srcPOSmap, TargetDB=None, numCatErrorsToShow=99, addInflectionClasses=False) == True:

        return
        
    # Make a backup copy of the transfer rule file
    try:
        shutil.copy2(transfer_rules_file, transfer_rules_file+'.old')
    except:
        report.Error('There was a problem finding the transfer rules file. Check your configuration.')
        return

    tr_f = open(transfer_rules_file+'.old', encoding='utf-8')

    # Check to see that we have the def-attr section in the format that XXE saves files in. Otherwise give an error.
    linesList = tr_f.readlines()
    
    if '><def-attr' not in ''.join(linesList):
        
        report.Error('The transfer rules file has not yet been saved with the XML Mind editor. Change the file in the editor and then run this tool again.')
        tr_f.close()
        return 
    
    defCatStart = defAttrStart = sectDefAttrEnd = 0
    
    # Read and save the 1st part of the transfer rule file -- until we get to the beginning of grammatical categories (initial lines).
    # Then read the grammatical category lines (def cat lines)
    # After that, read attribute lines, but skip the old grammatical category lines and then after those, save the rest of the lines to be written later (remain lines).
    # Or if there is no gram_cat attribute, stop writing at the end of the attribute section
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
        defAttrLines = linesList[defAttrStart:sectDefAttrEnd]
        remainLines = linesList[sectDefAttrEnd:]
    except:
        report.Error('The transfer rules file is malformed.')
        return 

    tr_out_f = open(transfer_rules_file, 'w', encoding='utf-8')
    
    # Write the initial lines
    for line in initialLines:
        
        tr_out_f.write(line)
    
    # Process categories
    catCount = processDefCat(defCatLines, srcPOSmap, tr_out_f)
    
    # Process attributes
    attrCount = processDefAttr(defAttrLines, POSmap, masterAttribList, tr_out_f)
    
    # Write the remaining lines
    for line in remainLines:
        
        tr_out_f.write(line)
    
    tr_out_f.close()
    
    report.Info(str(catCount) + ' categories added to the categories section.')
    report.Info(str(attrCount) + ' categories created for the a_gram_cat attribute.')

#----------------------------------------------------------------
# define the FlexToolsModule
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
