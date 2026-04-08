#
#   RuleAssistantPy
#
#   Python/PyQt6 version of Rule Assistant
#   Replaces Java EXE with in-process Qt application
#
#   Version 1.0.0 - April 2026 - Claude AI Port
#    Python/PyQt6 port of Rule Assistant from Java/JavaFX
#    Calls Python version instead of Java EXE
#
#   Based on RuleAssistant.py v3.15.1
#   Maintains same interface and structure as RuleAssistant.py
#
#   Runs the Python version of the Rule Assistant to create Apertium transfer rules.
#

import os
import sys
import subprocess
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
import logging
import tempfile
from datetime import datetime

# Fallback crash log - writes directly to file if logging fails
_crash_log = os.path.join(tempfile.gettempdir(), 'RuleAssistantPy_CRASH.log')

def _write_crash_log(msg):
    """Direct file write as fallback if logging fails"""
    try:
        with open(_crash_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")
            f.flush()
    except:
        pass

_write_crash_log(f"[INIT] RuleAssistantPy module loading at {datetime.now()}")

# Setup logging for debugging - robust version that works even if logging already initialized
_log_file = os.path.join(tempfile.gettempdir(), 'RuleAssistantPy.log')

# Always set up our own logger with file handler (don't rely on basicConfig)
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplicates
for handler in _logger.handlers[:]:
    _logger.removeHandler(handler)

# Add file handler
_file_handler = logging.FileHandler(_log_file, mode='w')
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_logger.addHandler(_file_handler)

# Add console handler
_console_handler = logging.StreamHandler(sys.stderr)
_console_handler.setLevel(logging.DEBUG)
_console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_logger.addHandler(_console_handler)

# Also propagate to parent to catch any root logger messages
_logger.propagate = True

_logger.info("=" * 80)
_logger.info("RuleAssistantPy.py loaded")
_logger.info(f"Log file: {_log_file}")
_logger.info("=" * 80)

from flextoolslib import *

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

_logger.info("PyQt6 imports successful")

# LAZY IMPORTS: Do NOT import QWebEngine at module load time
# It causes crashes when imported by FlexTools before proper Qt initialization
# Import only when needed in StartRuleAssistant()

import Mixpanel
import InterlinData
import Utils
import ReadConfig
import CreateApertiumRules
import FTPaths
from RunApertium import docs as RunApertDocs

from SIL.LCModel import ( # type: ignore
    IFsClosedFeatureRepository, ITextRepository,
    )

# Add RuleAssistantLib to path
_ra_lib_path = Path(__file__).parent / 'RuleAssistantLib'
if _ra_lib_path.exists():
    sys.path.insert(0, str(_ra_lib_path))
    # Note: flextrans_integration is imported lazily in StartRuleAssistant
    _HAS_PYTHON_RA = _ra_lib_path.exists()
else:
    _HAS_PYTHON_RA = False

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'RuleAssistant'

translators = []
# Note: QApplication initialization moved to MainFunction (not module load time)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel', 'CreateApertiumRules', 'TextClasses', 'InterlinData']

#----------------------------------------------------------------
# Documentation that the user sees:
descr = _translate("RuleAssistant", """This module runs a tool which let's you create transfer rules.""")
docs = {FTM_Name       : _translate("RuleAssistant", "Rule Assistant (Python)"),
        FTM_Version    : "1.0.0",
        FTM_ModifiesDB : False,
        FTM_Synopsis   : _translate("RuleAssistant", "Runs the Python/PyQt6 version of the tool for creating transfer rules."),
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
    bidixDix = ReadConfig.getConfigVal(configMap, ReadConfig.BILINGUAL_DICTIONARY_FILE, report)
    bidixBin = os.path.join(FTPaths.BUILD_DIR, 'bilingual.bin')

    if not (sourceText or bidixDix):
        return False

    if not os.path.isfile(bidixDix):

        report.Warning(_translate('RuleAssistant', 'Bilingual dictionary not found. Build the bilingual dictionary to see test data in the {ruleAssistant}.').format(ruleAssistant=docs[FTM_Name]))
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

        with open(fhtml, 'w', encoding='utf-8') as fout:

            fout.write(_translate('RuleAssistant', '<html><body><p>No test data available.</body></html>\n'))

    return fhtml


def StartRuleAssistant(report, ruleAssistantFile, ruleAssistGUIinputfile,
                       testDataFile, fromLRT=False):
    """Launch the Python/PyQt6 Rule Assistant GUI.

    This function calls the Python version of the Rule Assistant (no fallback to Java).

    Args:
        report: FLEx report object for logging
        ruleAssistantFile: Path to rule XML file
        ruleAssistGUIinputfile: Path to FLEx metadata XML file
        testDataFile: Path to test data file
        fromLRT: Whether launched from Live Rule Tester

    Returns:
        Tuple of (saved: bool, rule_index: Optional[int], launch_lrt: bool)
    """

    _write_crash_log("[START] StartRuleAssistant() called")
    _logger.info("StartRuleAssistant() called")
    _logger.info(f"  ruleAssistantFile: {ruleAssistantFile}")
    _logger.info(f"  ruleAssistGUIinputfile: {ruleAssistGUIinputfile}")
    _logger.info(f"  testDataFile: {testDataFile}")
    _logger.info(f"  fromLRT: {fromLRT}")

    if not _HAS_PYTHON_RA:
        error_msg = "Python Rule Assistant library not found at expected location"
        _logger.error(error_msg)
        report.Error(_translate('RuleAssistant', 'An error happened when running the {ruleAssistant} tool: {error}').format(error=error_msg, ruleAssistant=docs[FTM_Name]))
        return (False, None, False)

    try:
        _logger.info("About to import flextrans_integration")
        # LAZY IMPORT: Import only when actually needed (not at module load time)
        # This prevents Qt initialization issues when imported by FlexTools
        try:
            from RuleAssistantLib.flextrans_integration import start_rule_assistant
            _logger.info("Imported start_rule_assistant from RuleAssistantLib.flextrans_integration")
        except ImportError as e:
            _logger.warning(f"Failed to import from RuleAssistantLib: {e}, trying fallback")
            # Fallback for when RuleAssistantLib is in sys.path
            from flextrans_integration import start_rule_assistant
            _logger.info("Imported start_rule_assistant from flextrans_integration (fallback)")

        # Get interface language from FLEx
        try:
            lang_code = Utils.getInterfaceLangCode()
            _logger.info(f"Got interface language code: {lang_code}")
        except Exception as e:
            _logger.warning(f"Failed to get interface language code: {e}")
            lang_code = "en"

        _logger.info("About to call start_rule_assistant()")
        # Launch the Python Rule Assistant
        saved, rule_index, launch_lrt = start_rule_assistant(
            rule_file=ruleAssistantFile,
            flex_data_file=ruleAssistGUIinputfile,
            test_data_file=testDataFile,
            came_from_lrt=fromLRT,
            ui_lang_code=lang_code,
        )
        _logger.info(f"start_rule_assistant() returned: saved={saved}, rule_index={rule_index}, launch_lrt={launch_lrt}")

        return (saved, rule_index, launch_lrt)

    except Exception as e:
        import traceback
        error_msg = str(e)
        _logger.error(f"Exception in StartRuleAssistant: {error_msg}")
        _logger.error(traceback.format_exc())
        print(f"Python Rule Assistant error: {error_msg}")
        report.Error(_translate('RuleAssistant', 'An error happened when running the {ruleAssistant} tool: {error}').format(error=error_msg, ruleAssistant=docs[FTM_Name]))
        return (False, None, False)

#----------------------------------------------------------------
# The main processing function
def MainFunction(DB, report, modify=True, fromLRT=False):
    _write_crash_log("[MAIN] MainFunction() called")
    _logger.info("=" * 80)
    _logger.info("MainFunction() called - FLExTrans Rule Assistant module entry point")
    _logger.info("=" * 80)

    translators = []
    _logger.info("About to get or create QApplication")
    app = QApplication.instance()
    _logger.info(f"QApplication.instance() returned: {app}")

    if app is None:
        _logger.info("Creating new QApplication")
        app = QApplication([])
        _logger.info("QApplication created successfully")
    else:
        _logger.info("Reusing existing QApplication")

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
