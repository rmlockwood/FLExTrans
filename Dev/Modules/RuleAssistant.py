#
#   RuleAssistant
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.14 - 5/21/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13.1 - 3/24/25 - Ron Lockwood
#    Reorganized to thin out Utils code.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12.1 - 1/6/25 - Ron Lockwood
#    Fixes #835. Don't crash when Apertium data is missing as Rule Assistant test data. Just don't show test data.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.3 - 10/9/24 - Ron Lockwood
#    Handle fixed up category names.
#
#   Version 3.11.2 - 9/13/24 - Ron Lockwood
#    Added mixpanel logging.
#
#   Version 3.11.1 - 6/21/24 - Ron Lockwood
#    Use Setting for location and name of the Rule Assistant rules file.
#
#   Version 3.11 - 5/14/24 - Ron Lockwood
#    Connect to the now functioning CreateRules routine.
#    Rearrange the logic for the return code from the GUI program. Pretty print the GUIinput xml.
#
#   Version 3.9.3 - 12/20/23 - Ron Lockwood
#    Use data classes to pass around category and feature lists.
#
#   Version 3.9.2 - 12/19/23 - Ron Lockwood
#    Add a function to start the Rule Assistant program.
#
#   Version 3.9.1 - 12/6/23 - Ron Lockwood
#    Build an XML file with category and feature data for source and target databases
#    which will be used by the rule assistant GUI.
#
#   Version 3.9 - 9/11/23 - Ron Lockwood
#    Initial version
#
#   Runs the Rule Assistant to create Apertium transfer rules.
#

import os
import subprocess
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from flextoolslib import *

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

import Mixpanel
import InterlinData
import Utils
import ReadConfig
import CreateApertiumRules
import FTPaths

from SIL.LCModel import ( # type: ignore
    IFsClosedFeatureRepository, ITextRepository,
    )

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RuleAssistant'

translators = []
app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'CreateApertiumRules', 'TextClasses', 'InterlinData'] 

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("RuleAssistant", """This module runs the Rule Assistant tool which let's you create transfer rules.""")
docs = {FTM_Name       : "Rule Assistant",
        FTM_Version    : "3.13.2",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RuleAssistant", "Runs the Rule Assistant tool."),
        FTM_Help  : "",
        FTM_Description:    descr}

app.quit()
del app

# Element names in the rule assistant gui input file
FLEXDATA          = "FLExData"
SOURCEDATA        = "SourceData"
TARGETDATA        = "TargetData"
CATEGORIES        = "Categories"
FLEXCATEGORY      = "FLExCategory"
FEATURES          = "Features"
FLEXFEATURE       = "FLExFeature"
VALUES            = "Values"
FLEXFEATUREVALUE  = "FLExFeatureValue"

# Attribute names in the rule assistant gui input file
NAME   = 'name'
ABBREV = 'abbr'

@dataclass
class DBStartData:

    projectName: str
    categoryList: list
    featureList: list
    categoryFeatures: dict

    def toXml(self, root, tag):

        parent = ET.SubElement(root, tag, {NAME: self.projectName})

        catsEl = ET.SubElement(parent, CATEGORIES)

        for cat in self.categoryList:

            elem = ET.SubElement(catsEl, FLEXCATEGORY, {ABBREV: cat})
            dct = self.categoryFeatures.get(cat)

            if not dct:
                continue

            group = ET.SubElement(elem, 'ValidFeatures')

            for feat, types in sorted(dct.items()):

                ET.SubElement(group, 'ValidFeature', name=feat,
                              type='|'.join(sorted(types)))

        if not self.featureList:
            return

        featsEl = ET.SubElement(parent, FEATURES)

        for name, values in self.featureList:

            featEl = ET.SubElement(featsEl, FLEXFEATURE, {NAME: name})
            group = ET.SubElement(featEl, VALUES)

            for val in values:

                ET.SubElement(group, FLEXFEATUREVALUE, {ABBREV: val})

@dataclass
class StartData:

    src: DBStartData
    tgt: DBStartData

    def write(self, fileName):

        root = ET.Element(FLEXDATA)
        self.src.toXml(root, SOURCEDATA)
        self.tgt.toXml(root, TARGETDATA)

        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(fileName, encoding='utf-8', xml_declaration=True)

def getFeatureData(DB):

    myFeatureList = []

    # Loop through all closed features in the database. Closed features are ones that don't embed other feature structures
    for feature in DB.ObjectsIn(IFsClosedFeatureRepository):

        # Get the feature name in the best analysis language (typically English)
        featName = Utils.as_string(feature.Name)
        # Loop through possible feature values and save the abbreviation
        featValueList = sorted([Utils.as_tag(val) for val in feature.ValuesOC])

        # Add the name and the value list as a tuple to main list
        myFeatureList.append((featName, featValueList))

    # Sort the main list. By default sort uses the first tuple element for sorting.
    myFeatureList.sort()
    return myFeatureList

def GetStartData(report, DB, configMap):

    posMap = {}

    # Put categories in posMap
    Utils.get_categories(DB, report, posMap, TargetDB=None,
                         numCatErrorsToShow=1, addInflectionClasses=False)
    catList = sorted(posMap.keys())

    featureList = getFeatureData(DB)

    inflFeatures = Utils.getAllInflectableFeatures(DB)
    stemFeatures = Utils.getAllStemFeatures(DB, report, configMap)

    catFeatures = {}

    # Don't use the above catList since it will have been modified for invalid characters
    for pos in DB.lp.AllPartsOfSpeech:

        flexCat = Utils.as_string(pos.Abbreviation)

        # For the catFeatures dictionary use the modified category string
        cat = Utils.convertProblemChars(flexCat, Utils.catProbData)
        catFeatures[cat] = {feat: {'stem'} for feat in stemFeatures[flexCat]}
        templates = Utils.getAffixTemplates(DB, flexCat)

        for tmpl in templates:

            for feat, side in tmpl:

                if feat not in catFeatures[cat]:

                    catFeatures[cat][feat] = set()

                catFeatures[cat][feat].add(side)

        for feat in inflFeatures[flexCat]:

            if feat not in catFeatures[cat]:

                catFeatures[cat][feat] = set()

            catFeatures[cat][feat].add('prefix')
            catFeatures[cat][feat].add('suffix')

    return DBStartData(DB.ProjectName(), catList, featureList, catFeatures)

def GetRuleAssistantStartData(report, DB, TargetDB, configMap):

    return StartData(GetStartData(report, DB, configMap),
                     GetStartData(report, TargetDB, configMap))

def ProcessLine(line):

    readings = []
    loc = 'blank'
    esc = False
    cur_reading = []
    cur_string = ''

    for c in line:

        if esc:

            esc = False

            if loc != 'blank':

                cur_string += c

        elif c == '\\':

            esc = True

        elif loc == 'blank' and c == '^' and not esc:

            loc = 'lu'

        elif loc == 'lu' and c == '$' and not esc:

            loc = 'blank'
            cur_reading.append(cur_string)
            cur_string = ''
            readings.append(cur_reading)
            cur_reading = []

            if len(readings) >= 2:

                yield ([p for p in readings[0] if p],
                       [p for p in readings[1] if p])
            readings = []

        elif loc == 'lu' and c == '/' and not esc:

            cur_reading.append(cur_string)
            cur_string = ''
            readings.append(cur_reading)
            cur_reading = []

        elif loc == 'lu':

            if c == '<':

                loc = 'tag'
                cur_reading.append(cur_string)
                cur_string = ''
            else:
                cur_string += c

        elif loc == 'tag':

            if c == '>':

                loc = 'lu'
                cur_reading.append(cur_string)
                cur_string = ''
            else:
                cur_string += c

readingNumberRegex = re.compile(r'(\d+\.\d+)$')

def ReadingToHTML(reading):

    pieces = [
        readingNumberRegex.sub(r'<span class="num">\1</span>', reading[0]),
        '<span class="pos">'+reading[1]+'</span>',
    ] + ['<span class="tag">'+tag+'</span>' for tag in reading[2:]]

    return '<span class="lu">'+''.join(pieces)+'</span>'

def GenerateTestDataFile(report, DB, configMap, fhtml):

    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    bidix = os.path.join(FTPaths.BUILD_DIR, 'bilingual.bin')

    if not sourceText:
        return False

    if not os.path.isfile(bidix):

        report.Warning(_translate('RuleAssistant', 'Compiled bilingual dictionary not found. Run the "Run Apertium" module to display test data in the Rule Assistant.'))
        return False

    content = None

    for text in DB.ObjectsIn(ITextRepository):

        if Utils.as_string(text.Name).strip() == sourceText:

            content = text.ContentsOA
            break
    else:
        report.Error(_translate('RuleAssistant', "The text named '%s' was not found.") % sourceText)
        return False

    params = InterlinData.initInterlinParams(configMap, report, content)

    if params is None:
        return False
    
    text = InterlinData.getInterlinData(DB, report, params)

    fsrc = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_SOURCE_TEST_DATA_FILE)

    with open(fsrc, 'w', encoding='utf-8') as fout:
        text.write(fout)

    ftgt = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_TARGET_TEST_DATA_FILE)
    subprocess.run([os.path.join(FTPaths.TOOLS_DIR, 'lt-proc.exe'),
                    '-b', bidix, fsrc, ftgt], capture_output=True)

    try:
        with open(ftgt, encoding='utf-8') as fin, open(fhtml, 'w', encoding='utf-8') as fout:

            fout.write('''<html><head><style>
.lu { margin-left: 5px; font-size: 75%; }
.pos { color: blue; margin-left: 5px; }
.tag { color: green; margin-left: 5px; }
.num { vertical-align: sub; font-size: 50%; }
</style></head><body>
''')
            fout.write('<p><b>Source Text:</b> '+sourceText+'</p>\n')
            line_count = 0

            for line in fin:

                if not line.strip():
                    continue

                srcLine = ''
                tgtLine = ''

                for src, tgt in ProcessLine(line):

                    if len(src) > 1 and len(tgt) > 1:

                        srcLine += ReadingToHTML(src)
                        tgtLine += ReadingToHTML(tgt)

                fout.write(f'<p>{srcLine} → {tgtLine}</p>\n')
                line_count += 1

                if line_count >= 30:
                    break

            fout.write('</body></html>\n')

    except Exception as e:
        return False
    
    return True

def GetTestDataFile(report, DB, configMap):

    fhtml = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_DISPLAY_DATA_FILE)

    if not GenerateTestDataFile(report, DB, configMap, fhtml):

        with open(fhtml, 'w') as fout:

            fout.write(_translate('RuleAssistant', '<html><body><p>No test data available.</body></html>\n'))

    return fhtml

def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile,
                       testDataFile, fromLRT=False):

    # Call the rule assistant gui program
    try:
        fullRApath = os.path.join(os.environ['PROGRAMFILES'], FTPaths.RULE_ASSISTANT_DIR, FTPaths.RULE_ASSISTANT)

        params = [fullRApath, ruleAssistantFile, ruleAssistGUIinputfile,
                  testDataFile, 'y' if fromLRT else 'n', Utils.getInterfaceLangCode()]

        result = subprocess.run(params, capture_output=True)

        output = result.stdout.decode('utf-8').strip().split()
        lrt = (not fromLRT) and ('LRT' in output)

        if not output or output[0] not in ['1', '2']:
            return (False, None, lrt)
        
        elif output[0] == '1':
            
            return (True, int(output[1]), lrt) # create single rule
        else:
            return (True, None, lrt) # create all rules

    except Exception as e:

        report.Error(_translate('RuleAssistant', f'An error happened when running the Rule Assistant tool: {e.output.decode("utf-8")}'))
        return (False, None, False)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True, fromLRT=False):

    translators = []
    app = QApplication([])
    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], 
                           translators, loadBase=True)

    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    # Get the path to the rule assistant rules file
    ruleAssistantFile = ReadConfig.getConfigVal(configMap, ReadConfig.RULE_ASSISTANT_FILE, report, giveError=False)

    if not ruleAssistantFile:

        # Get build folder
        buildFolder = FTPaths.BUILD_DIR

        ruleAssistantFile = os.path.join(buildFolder, 'RuleAssistantRules.xml')

    # Get the path to the transfer rules file
    tranferRulePath = ReadConfig.getConfigVal(configMap, ReadConfig.TRANSFER_RULES_FILE, report, giveError=False)

    if not tranferRulePath:
        return

    TargetDB = Utils.openTargetProject(configMap, report)

    # Get the FLEx info. for source & target projects that the Rule Assistant font-end needs
    startData = GetRuleAssistantStartData(report, DB, TargetDB, configMap)

    # Write the data to an XML file
    ruleAssistGUIinputfile = os.path.join(FTPaths.BUILD_DIR, Utils.RA_GUI_INPUT_FILE)
    startData.write(ruleAssistGUIinputfile)

    testData = GetTestDataFile(report, DB, configMap)

    # Start the Rule Assistant GUI
    saved, rule, lrt = StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile, testData, fromLRT=fromLRT)

    ruleCount = None

    if saved:
        ruleCount = CreateApertiumRules.CreateRules(DB, TargetDB, report, configMap, ruleAssistantFile, tranferRulePath, rule)
    else:
        report.Info(_translate('RuleAssistant', 'No rules created.'))

    if lrt:
        from LiveRuleTesterTool import MainFunction as LRT
        LRT(DB, report, modify, ruleCount=ruleCount)

    return ruleCount

#----------------------------------------------------------------
# define the FlexToolsModule

FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
