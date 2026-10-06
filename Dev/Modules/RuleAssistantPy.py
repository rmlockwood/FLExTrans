#
#   RuleAssistantPy
#
#   Ron Lockwood
#   SIL International
#   9/11/23
#
#   Version 3.17.1 - 9/29/26 - Ron Lockwood
#    Fixes #1334. Stop if the target project can't be opened, and always close it before returning. Added the code description block.
#
#   Version 3.17 - 8/26/26 - Ron Lockwood
#    Bumped version.
#
#   Version 3.16.9 - 8/24/26 - Ron Lockwood
#    Fixes #1449. Don't launch a nested Live Rule Tester when the Test in LRT button is used from a Rule Assistant that the tester itself started.
#
#   Version 3.16.8 - 6/26/26 - Ron Lockwood
#    Prevent the module from starting in one-project mode.
#
#   Version 3.16.7 - 6/17/26 - Ron Lockwood
#    Cleared up lint issues.
#
#   Version 3.16.6 - 6/17/26 - Ron Lockwood
#    Require both source text and bilingual dictionary before generating test data (fixes a None-arg crash).
#
#   Version 3.16.5 - 6/17/26 - Ron Lockwood
#    Remove dead _HAS_PYTHON_RA flag; the library import is unconditional.
#
#   Version 3.16.4 - 6/16/26 - Ron Lockwood
#    Apply coding conventions; camelCase naming.
#
#   Version 3.16.3 - 6/15/26 - Ron Lockwood
#    Remove logging code.
#
#   Version 3.16.2 - 6/15/26 - Ron Lockwood
#    Refactored: widgets/layout now live in .ui files and logid separated to controler files.
#
#   Version 3.16.1 - 6/15/26 - Ron Lockwood
#    Fixes to not rely on the old RuleAssistantLib folder.
#
#   Version 3.16 - April 2026 - Claude AI Port
#    Python/PyQt6 port of Rule Assistant from Java/JavaFX
#    Calls Python version instead of Java EXE
#
#   OVERVIEW (AI generated, then edited)
#
#   This is the FlexTools module that runs the Rule Assistant, a window in which the user describes transfer rules at a linguistic level (categories, features, affixes, agreement) instead of
#   writing Apertium XML by hand. When the user saves, the described rules are turned into real Apertium transfer rules and written into the transfer rules file. The Rule Assistant started life as
#   a Java/JavaFX program (github.com/AndyBlack/ftrulegen) that the old RuleAssistant.py module launched as an external EXE. In version 3.16 it was ported to Python/PyQt6 and now runs in-process;
#   this module replaced RuleAssistant.py (v3.15.1) and kept its shape. The window itself lives in Lib (RuleAssistantMainWindow plus its controller files), and the port uses snake_case heavily
#   to mirror the Java names - that is expected, leave it alone.
#
#   This file is the glue around that window. It gathers what the window needs to know about the two FLEx projects, writes that into files in the build folder, starts the window, and when the
#   window closes with a save, hands the Rule Assistant rules file to CreateApertiumRules.CreateRules(), which does the actual rule generation.
#
#   THE FILES INVOLVED
#
#   The window never reads FLEx directly - everything it knows comes in through files. That is a leftover of the Java design where the tool was a separate program, and it is still handy.
#    - The GUI input file (Utils.RA_GUI_INPUT_FILE in the build folder). A <FLExData> document with a <SourceData> and a <TargetData> section, each listing the project's categories, its closed
#      features with their values, and for each category the features valid for it tagged stem, prefix or suffix. It is rewritten from scratch on every run by StartData.write().
#    - The Rule Assistant rules file (the Rule Assistant File setting, defaulting to RuleAssistantRules.xml in the build folder). This holds the user's rule descriptions; the module reads and
#      saves it, and this module only passes the path along and later hands it to CreateRules().
#    - The transfer rules file (the Transfer Rules File setting). CreateRules() writes the generated Apertium rules into it, saving a history copy of the prior version first. If this setting is
#      empty the module returns without doing anything.
#    - The test data HTML (Utils.RULE_ASSISTANT_DISPLAY_DATA_FILE). A preview of the source text shown in the window; see TEST DATA below.
#
#   CATEGORY NAMES AND FEATURE ORIGINS
#
#   Category abbreviations go through Utils.get_categories(), which replaces characters Apertium can't handle, so the names in the input file match what the bilingual lexicon and the rules use.
#   GetStartData() then deliberately walks DB.lp.AllPartsOfSpeech again for the per-category features rather than reusing that category list: it needs the raw FLEx abbreviation to look up stem
#   features and affix templates, and only converts the name (Utils.convertProblemChars) for the dictionary key. Features found in affix templates carry the side they were found on, while the
#   inflectable features of a category get both prefix and suffix since the side isn't known. WorkOnRulesWithAI imports GetRuleAssistantStartData() to ground its AI prompts in this same project
#   data, so a change to that output affects both tools.
#
#   TEST DATA
#
#   To give the user something concrete to look at, GetTestDataFile() takes the source text named in the settings, writes its interlinear data out in Apertium stream format, compiles the bilingual
#   dictionary with lt-comp and runs the text through it with lt-proc, then writes the first 30 non-blank lines as colored source → target lexical units in HTML. This is best effort only: if the
#   source text or bilingual dictionary setting is missing, the dictionary hasn't been built, the text isn't found, or anything fails while writing, a "No test data available." page is written
#   instead and the Rule Assistant still runs. ProcessLine() is a small hand-written parser of the lt-proc output that yields each lexical unit's source reading paired with its first target reading.
#
#   TARGET PROJECT AND ONE PROJECT MODE
#
#   The target project is opened with Utils.openTargetProject(), the single shared routine that accepts either a bare project name or the full path of a .fwdata file (issue #1334). It reports its
#   own error and returns None when the project can't be opened, in which case this module simply stops. Otherwise it is closed in a finally clause before MainFunction returns or launches the
#   Live Rule Tester, so it is never left locked. The module does not handle One project mode at all: when the Two Project Mode setting is 'n' it reports that it only works in Two Project mode
#   and returns before logging or opening anything. Unlike the Replacement Editor or the Sense Linker, it never reuses the source project as the target. A missing Two Project Mode setting is
#   treated as two project mode.
#
#   RUNNING WITH THE LIVE RULE TESTER
#
#   The window's Test in LRT button asks for the Live Rule Tester to be run after the save. When the Rule Assistant was started from FlexTools, MainFunction() launches the tester itself at the end.
#   When the tester started us (it calls MainFunction() with fromLRT=True and uses the returned rule count), StartRuleAssistant() drops that flag, because the tester restarts itself as soon as we
#   return and launching another would nest a second tester on top of it (issue #1449).
#
#   CODE STRUCTURE
#
#   After the docs dictionary and the element and attribute name constants for the input file come the two dataclasses: DBStartData (one project's categories, features and per-category features,
#   with toXml()) and StartData (the source/target pair, with write()). Then the data gathering functions: getFeatureData() lists the closed features, GetStartData() builds one DBStartData, and
#   GetRuleAssistantStartData() calls it for both projects. The test data side follows: ProcessLine() and ReadingToHTML() are helpers for GenerateTestDataFile(), which GetTestDataFile() wraps with
#   the fallback page. StartRuleAssistant() makes sure a QApplication exists, shows RuleAssistantWindow, runs the event loop and returns a (saved, rule index, launch LRT) tuple.
#
#   Control flow: FlexTools calls MainFunction(), which loads translations, reads the settings, refuses One project mode, works out the rules file and transfer rules paths, opens the target
#   project, writes the GUI input file and the test data, and runs StartRuleAssistant(). If the user saved, it calls CreateApertiumRules.CreateRules() for just the rule the window returned (Save
#   Current) or for all rules when that index is None (Save/Create All), then optionally runs the Live Rule Tester, and returns the number of rules created (None if nothing was saved).
#

from RuleAssistantMainWindow import RuleAssistantWindow

import os
import subprocess
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import cast

from flextoolslib import * # type: ignore

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

import Mixpanel
import InterlinData
import Utils
import ReadConfig
import CreateApertiumRules
import FTPaths
from RunApertium import docs as RunApertDocs
from TextClasses import TextEntirety

from SIL.LCModel import ( # type: ignore
    IFsClosedFeatureRepository, ITextRepository,
    )

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RuleAssistant'

translators = []
# Note: QApplication initialization moved to MainFunction (not module load time)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'CreateApertiumRules', 'TextClasses', 'InterlinData',
                        'RAutils', 'RuleAssistantWindow', 'RuleAssistantMainWindow',
                        'DisjointFeaturesEditor', 'DisjointFeaturesEditorDlg']

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("RuleAssistant", """This module runs a tool which let's you create transfer rules.""")
docs = {FTM_Name       : _translate("RuleAssistant", "Rule Assistant"),
        FTM_Version    : "3.17.1",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RuleAssistant", "Runs a tool for creating transfer rules."),
        FTM_Help       : "",
        FTM_Description:    descr}

#app.quit()
#del app

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

                ET.SubElement(group, 'ValidFeature', name=feat, type='|'.join(sorted(types)))

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

    return StartData(GetStartData(report, DB, configMap), GetStartData(report, TargetDB, configMap))

def ProcessLine(line):

    readings = []
    loc = 'blank'
    esc = False
    curReading = []
    curString = ''

    for c in line:

        if esc:

            esc = False

            if loc != 'blank':

                curString += c

        elif c == '\\':

            esc = True

        elif loc == 'blank' and c == '^' and not esc:

            loc = 'lu'

        elif loc == 'lu' and c == '$' and not esc:

            loc = 'blank'
            curReading.append(curString)
            curString = ''
            readings.append(curReading)
            curReading = []

            if len(readings) >= 2:

                yield ([p for p in readings[0] if p], [p for p in readings[1] if p])

            readings = []

        elif loc == 'lu' and c == '/' and not esc:

            curReading.append(curString)
            curString = ''
            readings.append(curReading)
            curReading = []

        elif loc == 'lu':

            if c == '<':

                loc = 'tag'
                curReading.append(curString)
                curString = ''
            else:
                curString += c

        elif loc == 'tag':

            if c == '>':

                loc = 'lu'
                curReading.append(curString)
                curString = ''
            else:
                curString += c

readingNumberRegex = re.compile(r'(\d+\.\d+)$')

def ReadingToHTML(reading):

    pieces = [
        readingNumberRegex.sub(r'<span class="num">\1</span>', reading[0]),
        '<span class="pos">'+reading[1]+'</span>',
    ] + ['<span class="tag">'+tag+'</span>' for tag in reading[2:]]

    return '<span class="lu">'+''.join(pieces)+'</span>'

def GenerateTestDataFile(report, DB, configMap, fhtml):

    sourceText = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    bidixDix = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)

    # Both are required: sourceText to locate the text to interlinearize, and bidixDix to compile the bilingual dictionary below. Bail (no test data) if either is
    # missing - this also narrows bidixDix to a non-None str for the subprocess call further down.
    if not (sourceText and bidixDix):

        return False

    if not os.path.isfile(bidixDix):

        report.Warning(_translate('RuleAssistant', 'Bilingual dictionary not found. Build the bilingual dictionary to see test data in the {ruleAssistant}.').format(ruleAssistant=docs[FTM_Name]))
        return False

    bidixBin = os.path.join(FTPaths.BUILD_DIR, 'bilingual.bin')
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

    # getInterlinData is dynamically typed (returns object), so cast to its real type for the .write() call below.
    text = cast(TextEntirety, InterlinData.getInterlinData(DB, report, params))

    fsrc = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_SOURCE_TEST_DATA_FILE)

    with open(fsrc, 'w', encoding='utf-8') as fout:

        text.write(fout)

    # Compile the bilingual dictionary
    subprocess.run([os.path.join(FTPaths.TOOLS_DIR, 'lt-comp.exe'), 'lr', bidixDix, bidixBin], capture_output=True)

    if not os.path.isfile(bidixBin):

        report.Warning(_translate('RuleAssistant', 'Compiled bilingual dictionary not found. There was an error compiling the bilingual dictionary.'))
        return False

    ftgt = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_TARGET_TEST_DATA_FILE)
    subprocess.run([os.path.join(FTPaths.TOOLS_DIR, 'lt-proc.exe'), '-b', bidixBin, fsrc, ftgt], capture_output=True)

    try:
        with open(ftgt, encoding='utf-8') as fin, open(fhtml, 'w', encoding='utf-8') as fout:

            fout.write('''<html><head><style>
.lu { margin-left: 5px; font-size: 75%; }
.pos { color: blue; margin-left: 5px; }
.tag { color: green; margin-left: 5px; }
.num { vertical-align: sub; font-size: 50%; }
</style></head><body>
''')
            fout.write(_translate('RuleAssistant', '<p><b>Source Text:</b> ')+sourceText+'</p>\n')
            lineCount = 0

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
                lineCount += 1

                if lineCount >= 30:

                    break

            fout.write('</body></html>\n')

    except Exception as e:

        return False

    return True

def GetTestDataFile(report, DB, configMap):

    fhtml = os.path.join(FTPaths.BUILD_DIR, Utils.RULE_ASSISTANT_DISPLAY_DATA_FILE)

    if not GenerateTestDataFile(report, DB, configMap, fhtml):

        with open(fhtml, 'w', encoding='utf-8') as fout:

            fout.write(_translate('RuleAssistant', '<html><body><p>No test data available.</body></html>\n'))

    return fhtml

def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile, testDataFile, fromLRT=False):

    """Launch the Python/PyQt6 Rule Assistant GUI.

    This function calls the Python version of the Rule Assistant.

    Args:
        report: FLEx report object for logging
        ruleAssistantFile: Path to rule XML file
        ruleAssistGUIinputfile: Path to FLEx metadata XML file
        testDataFile: Path to test data file
        fromLRT: Whether launched from Live Rule Tester

    Returns:
        Tuple of (saved: bool, rule_index: Optional[int], launch_lrt: bool)
    """

    try:
        # Get interface language from FLEx
        try:
            langCode = Utils.getInterfaceLangCode()

        except Exception:

            langCode = "en"

        if not langCode:

            langCode = "en"

        # Ensure QApplication exists before creating window (QWebEngineView needs it)
        app = QApplication.instance()

        if app is None:

            app = QApplication(['RuleAssistant'])

        # Application-wide icon so every window, dialog and message box (including
        # parentless ones) shows the FLExTrans icon in its title bar.
        QApplication.setWindowIcon(QIcon(os.path.join(FTPaths.TOOLS_DIR, 'FLExTransWindowIcon.ico')))

        window = RuleAssistantWindow(ruleFile=ruleAssistantFile, flexDataFile=ruleAssistGUIinputfile, testDataFile=testDataFile, cameFromLrt=fromLRT, uiLangCode=langCode)

        # Show and run
        window.show()

        if app:

            app.exec()

        # Get and save result
        result = window.getResult()

        # The Test in LRT button is live even when we were started from the Live Rule Tester (issue #1449), but there we are already running inside the Live Rule Tester which re-runs itself as soon
        # as we return. Drop the launch flag in that case so the user simply lands back in the tester they came from instead of getting a second, nested one on top of it.
        launchLrt = result.launchLrt and not fromLRT

        return (result.saved, result.ruleIndex, launchLrt)

    except Exception as e:

        errorMsg = str(e)
        report.Error(_translate('RuleAssistant', 'An error happened when running the {ruleAssistant} tool: {error}').format(error=errorMsg, ruleAssistant=docs[FTM_Name]))
        return (False, None, False)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True, fromLRT=False):

    translators = []
    app = QApplication.instance()

    if app is None:

        app = QApplication(['FLExTrans'])

    Utils.loadTranslations(librariesToTranslate + [TRANSL_TS_NAME], translators, loadBase=True)

    configMap = ReadConfig.readConfig(report)

    if not configMap:

        return

    twoProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False)
    if twoProjectMode == 'n':
        report.Error(_translate("RuleAssistant", "This module only works in Two Project mode."))
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

    # openTargetProject reports the problem if it can't open the target project.
    TargetDB = Utils.openTargetProject(configMap, report)

    if TargetDB is None:

        return

    # Close the target project however we leave this block, so it isn't left locked. The Live Rule Tester can run the Rule Assistant many times in a row, and it is launched below only after
    # the target is closed.
    try:
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
    finally:
        TargetDB.CloseProject()

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
