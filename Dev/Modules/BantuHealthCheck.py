
import re
from collections import defaultdict

from SIL.LCModel import (# type: ignore
    IFsComplexValue, 
    IFsFeatStruc, 
    IFsClosedValue, 
    IPartOfSpeech, 
    IMoStemMsa, 
    IMoInflAffMsa, 
    IMoInflAffixSlot,
)

from flextoolslib import * # type: ignore

import Mixpanel
import ReadConfig
import Utils
import FTPaths

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, QTranslator

# Define _translate for convenience
_translate = QCoreApplication.translate
TRANSL_TS_NAME = 'BantuHealthCheck'

translators = []
app = QApplication.instance()

if app is None:
    app = QApplication([])

# This is just for translating the docs dictionary below
Utils.loadTranslations([TRANSL_TS_NAME], translators)

# libraries that we will load down in the main function
librariesToTranslate = ['ReadConfig', 'Utils', 'Mixpanel'] 

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {
    FTM_Name        : _translate("BantuHealthCheck", "Bantu Health Check"),
    FTM_Version     : 5,
    FTM_ModifiesDB  : False,
    FTM_Synopsis    : _translate("BantuHealthCheck", "Flags various issues having to do with gender features in Bantu projects."),
    FTM_Description : 
_translate("BantuHealthCheck", """
Bantu Health Check:
1. Identifies Noun 'roots' (bound root, bound stem, discontiguous phrase, 
   particle, phrase, root, stem) and verifies that they have exactly two
   inflection feature values defined. (Skips nouns with 0 features).
2. Identifies prefixes in the 'NC' slot and verifies that they have 
   exactly one inflection feature defined.

Issues are grouped by morphological type (roots, then prefixes, then suffixes).
Warnings use a gentler tone (primarily lowercase, "problem" instead of "fail").
""")
}

import sys
import os
import tomllib
import tomli_w 
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox, QApplication, QLabel, QComboBox, QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt

#----------------------------------------------------------------
# Constants
BANTU_SETTINGS_FILE = "BantuSettings.toml"

# TARGET_POS = "Noun"
# TARGET_SLOT = "NC"

# ROOT_MORPH_TYPES = [
#     "bound root",
#     "bound stem",
#     "discontiguous phrase",
#     "particle",
#     "phrase",
#     "root",
#     "stem"
# ]

#----------------------------------------------------------------
# Helper Functions

def numeric_sort_key(s):
    """
    Sort key to handle numeric prefixes in strings (e.g., '9pl' before '14pl').
    """
    match = re.search(r'(\d+)', s)
    if match:
        return (int(match.group(1)), s)
    return (float('inf'), s)


def missing_nc_sort_key(issue):
    msg = issue[0]
    match = re.search(r"missing prefix in '([^']+)' NC slot for feature '([^']+)'", msg)
    if match:
        pos_name = match.group(1)
        feature = match.group(2)
        return (pos_name, numeric_sort_key(feature))
    return (msg,)


def as_string(project, obj):
    if not obj: return ""
    return project.BestStr(obj)

def get_feat_abbr_list(project, SpecsOC, feat_abbr_list):
    """
    Recursive function to traverse feature structures.
    """
    for spec in SpecsOC:
        if spec.ClassName == "FsComplexValue":
            spec_complex = IFsComplexValue(spec)
            if spec_complex.ValueOA:
                # ValueOA returns a generic IFsAbstractStructure. 
                # We MUST cast to IFsFeatStruc to access FeatureSpecsOC.
                value_fs = IFsFeatStruc(spec_complex.ValueOA)
                get_feat_abbr_list(project, value_fs.FeatureSpecsOC, feat_abbr_list)
        elif spec.ClassName == "FsClosedValue":
            spec_closed = IFsClosedValue(spec)
            
            featGrpName = Utils.as_string(spec_closed.FeatureRA.Name) if spec_closed.FeatureRA else "ERR"
            abbValue = Utils.as_string(spec_closed.ValueRA.Abbreviation) if spec_closed.ValueRA else "ERR"
                
            feat_abbr_list.append((featGrpName, abbValue))
    return

def find_slot_recursive(project, pos, target_name):
    """
    Recursively search for an affix slot by name or abbreviation.
    """
    pos_concrete = IPartOfSpeech(pos) # CastingOperations.cast_to_concrete(pos)
    if hasattr(pos_concrete, "AffixSlotsOC"):
        for slot in pos_concrete.AffixSlotsOC:
            name = project.BestStr(slot.Name)
            abbr = ""
            if hasattr(slot, "Abbreviation"):
                abbr = project.BestStr(slot.Abbreviation)
            if name == target_name or abbr == target_name:
                return slot
    if hasattr(pos_concrete, "SubPossibilitiesOS"):
        for sub in pos_concrete.SubPossibilitiesOS:
            result = find_slot_recursive(project, sub, target_name)
            if result:
                return result
    return None

def get_all_slots(project, pos, slots_list):

    pos_concrete = IPartOfSpeech(pos) 

    if hasattr(pos_concrete, "AffixSlotsOC"):

        for slot in pos_concrete.AffixSlotsOC:

            name = project.BestStr(slot.Name)
            slots_list.append(name)
    return

class BantuConfigDialog(QDialog):
    def __init__(self, current_data, pos_options, slot_options, feature_options):
        super().__init__()
        self.setWindowTitle("Bantu Feature Configuration")
        self.resize(400, 550)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.all_slot_options = slot_options
        self.current_data = current_data

        # 1. POS Noun Name
        main_layout.addWidget(QLabel("Name for POS Noun:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(pos_options)
        main_layout.addWidget(self.pos_combo)

        # 2. Single Noun Slot (Combo Box)
        main_layout.addWidget(QLabel("Slot containing noun class affix (Noun POS only):"))
        self.noun_slot_combo = QComboBox()
        main_layout.addWidget(self.noun_slot_combo)

        # 3. Other Slots (Multi-select, excluding Noun POS slots)
        main_layout.addWidget(QLabel("Other Slots with Noun Class Affixes (Non-Noun POS):"))
        self.general_slot_list = QListWidget()
        self.general_slot_list.setFixedHeight(180)
        main_layout.addWidget(self.general_slot_list)

        # 4. Features
        main_layout.addWidget(QLabel("Feature containing singular gender values:"))
        self.sg_combo = QComboBox()
        self.sg_combo.addItems(feature_options)
        main_layout.addWidget(self.sg_combo)

        main_layout.addWidget(QLabel("Feature containing plural gender values:"))
        self.pl_combo = QComboBox()
        self.pl_combo.addItems(feature_options)
        main_layout.addWidget(self.pl_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Connect signals and initialize
        self.pos_combo.currentTextChanged.connect(self.update_ui_filtering)
        self.set_initial_values(pos_options, feature_options)
        self.update_ui_filtering()

    def update_ui_filtering(self):
        """Filters widgets based on the selected Noun POS."""
        selected_noun_pos = self.pos_combo.currentText()
        
        self.noun_slot_combo.blockSignals(True)
        self.noun_slot_combo.clear()
        self.general_slot_list.clear()

        # Get saved values from TOML
        saved_primary_slot = self.current_data.get("noun_class_slot", "")
        saved_others = self.current_data.get("slots_with_noun_class_affixes", [])
        
        # Flatten other slots for easy checkbox matching
        other_lookup = []
        for entry in saved_others:
            p = entry.get("POS", "")
            for s in entry.get("slots", []):
                other_lookup.append(f"{p} - {s}".lower())

        # Distribute options
        for opt in self.all_slot_options:
            pos_name, slot_name = opt['POS'], opt['slot']
            
            if pos_name == selected_noun_pos:
                self.noun_slot_combo.addItem(slot_name)
            else:
                display_text = f"{pos_name} - {slot_name}"
                item = QListWidgetItem(display_text)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                is_checked = display_text.lower() in other_lookup
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
                self.general_slot_list.addItem(item)

        # Restore the primary slot selection
        idx = self.noun_slot_combo.findText(saved_primary_slot)
        if idx >= 0:
            self.noun_slot_combo.setCurrentIndex(idx)

        self.noun_slot_combo.blockSignals(False)

    def set_initial_values(self, pos_options, feature_options):
        def set_val(combo, val):
            index = combo.findText(val)
            if index >= 0: combo.setCurrentIndex(index)

        set_val(self.pos_combo, self.current_data.get("name_for_POS_noun", ""))
        set_val(self.sg_combo, self.current_data.get("bantu_singular_feature_name", ""))
        set_val(self.pl_combo, self.current_data.get("bantu_plural_feature_name", ""))

    def get_results(self):
        """Prepares dictionary for TOML saving."""
        selected_noun_pos = self.pos_combo.currentText()
        
        # Group general checkboxes by POS
        grouped_others = {}
        for i in range(self.general_slot_list.count()):
            item = self.general_slot_list.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                pos, slot = item.text().split(" - ")
                grouped_others.setdefault(pos, []).append(slot)
        
        others_list = [{"POS": k, "slots": v} for k, v in grouped_others.items()]
        
        return {
            "bantu_info": {
                "name_for_POS_noun": selected_noun_pos,
                "noun_class_slot": self.noun_slot_combo.currentText(), # Explicitly saved
                "slots_with_noun_class_affixes": others_list,
                "bantu_singular_feature_name": self.sg_combo.currentText(),
                "bantu_plural_feature_name": self.pl_combo.currentText()
            }
        }
    

def save_dialog_data(dialog, file_path):
    # 1. Extract the dictionary from the dialog
    # This should return: {"bantu_info": {...}}
    updated_data = dialog.get_results()

    try:
        # 2. Open file in 'wb' (write binary) mode
        # TOML requires UTF-8, and tomli_w handles this via binary streams
        with open(file_path, "wb") as f:
            # 3. Convert dict to TOML string and encode to bytes
            toml_string = tomli_w.dumps(updated_data,)
            f.write(toml_string.encode("utf-8"))
            
        print(f"Successfully saved to {file_path}")
        return True
    #----------------------------------------------------------------
    
    except Exception as e:
        print(f"Failed to save TOML file: {e}")
        return False
            
# The main processing function
def Main(project, report, modifyAllowed):
    
    entries = list(project.LexiconAllEntriesSorted())
    total_roots_checked = 0
    total_prefixes_checked = 0
    total_suffixes_checked = 0
    total_affixes_val_checked = 0

    # Read the configuration file.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return 
    
    # Log the start of this module on the analytics server if the user allows logging.
    Mixpanel.LogModuleStarted(configMap, report, docs[FTM_Name], docs[FTM_Version])

    morphNames = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_MORPHNAMES, report)
    if not morphNames:
        report.error(_translate("BantuHealthCheck", "Configuration file problem."))
        return 
    
    report.Info(_translate("BantuHealthCheck", "Starting Bantu language health check..."))

    # Master Lists 
    posMap = {}
    all_possible_slots = []
    features = []

    # Get POS
    Utils.get_categories(project, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=False)
    pos_names = list(posMap.values())

    # Get Features
    feature_objects = project.lp.MsFeatureSystemOA.FeaturesOC

    for feature in feature_objects:

        feat_name = project.BestStr(feature.Name)
        features.append(feat_name)

    # Get POS with associated slots
    for pos in project.lp.AllPartsOfSpeech:

        slots_list = list()
        get_all_slots(project, pos, slots_list)
        
        if slots_list:
            pos_name = project.BestStr(pos.Name)

            for slot_name in slots_list:
                all_possible_slots.append({"POS": pos_name, "slot": slot_name})

    # all_possible_slots = [
    #     {"POS": "Noun", "slot": "NC"},
    #     {"POS": "Demonstrative", "slot": "demNC"},
    #     {"POS": "Verb", "slot": "objNC"},
    #     {"POS": "Verb", "slot": "sbjNC"}
    # ]
    # features = ["BantuSg", "BantuPl", "Number", "Gender"]

    # Load existing TOML data
    settingsPath = os.path.join(os.path.dirname(FTPaths.CONFIG_PATH), BANTU_SETTINGS_FILE)

    current_data = {}
    if os.path.exists(settingsPath):

        with open(settingsPath, "rb") as f:
            try:                                            
                full_config = tomllib.load(f)
                current_data = full_config.get("bantu_info", {})

            except Exception as e:
                print(f"Error reading TOML: {e}")

    # Launch Dialog to get Bantu settings from user
    dialog = BantuConfigDialog(current_data, pos_names, all_possible_slots, features)

    if dialog.exec():

        save_dialog_data(dialog, settingsPath)
    else:
        report.Info(_translate("BantuHealthCheck", "Bantu Health Check cancelled by user."))
        return

    # Store issues to report them grouped by type
    issues = {
        "roots": [], 
        "prefixes": [], 
        "suffixes": [], 
        "affix_gloss": [],
        "duplicates": [],
        "spaces": []
    }
    
    # Store unique features for summary
    global_noun_features = defaultdict(set)
    
    # Check 4: Store glosses to find duplicates
    affix_glosses = defaultdict(list) # gloss -> list of (lexeme, sourceURL)

    # Check 6: Track found features for all NC slots
    # pos_name -> set of feature values
    found_nc_prefix_features = defaultdict(set)
    # Track POS that actually have an NC slot
    pos_with_nc_slot = set()

    # 1. Find the NC slot for prefix checking (Noun specific)
    #posOps = POSOperations(project)
    #noun_pos_obj = posOps.Find(TARGET_POS)

    # This should return: {"bantu_info": {...}}
    bantuData = dialog.get_results()
    nameForPOSNoun = bantuData["bantu_info"]["name_for_POS_noun"]
    nounClassSlotName = bantuData["bantu_info"]["noun_class_slot"] # This is the saved combo box value
    slots_list = bantuData["bantu_info"]["slots_with_noun_class_affixes"]

    # 1. Get all possible slot names (as a flat list)
    allNCslotNames = []

    for row in slots_list:

        allNCslotNames.extend(row['slots'])
        pos_with_nc_slot.add(row['POS'])

    # 2. Create a mapping for reverse lookup (Slot -> POS)
    slot_to_pos_map = {}

    for row in slots_list:

        current_pos = row['POS']

        for slot in row['slots']:

            slot_to_pos_map[slot] = current_pos

    noun_pos_obj = None
    pos_list = []

    for pos in project.lp.AllPartsOfSpeech:

        posName = Utils.as_string(pos.Name)
        pos_list.append(pos)

        if posName == nameForPOSNoun:

            noun_pos_obj = pos
            break

    if not noun_pos_obj:

        report.Warning(_translate("BantuHealthCheck", "Could not find POS named '{pos}' in the project.".format(pos=nameForPOSNoun)))
        return

    for entry in entries:

        # Get Morph Type (MorphTypeRA.Name)
        morph_type = ""

        if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:

            morph_type = project.BestStr(entry.LexemeFormOA.MorphTypeRA.Name)
            morphGuidStr = entry.LexemeFormOA.MorphTypeRA.Guid.ToString()
            
        lexeme_form = project.LexiconGetLexemeForm(entry)
        
        # --- CHECK 1: Noun Roots (Inflection Features) ---
        if morph_type in morphNames:

            for sense in entry.SensesOS:

                msa = sense.MorphoSyntaxAnalysisRA
                if not msa: continue
                
                msa_concrete = IMoStemMsa(msa) #CastingOperations.cast_to_concrete(msa)
                
                pos_name = ""
                if hasattr(msa_concrete, "PartOfSpeechRA") and msa_concrete.PartOfSpeechRA:
                    pos_name = project.BestStr(msa_concrete.PartOfSpeechRA.Name)
                
                if pos_name == nameForPOSNoun:

                    total_roots_checked += 1
                    
                    fs = getattr(msa_concrete, "MsFeaturesOA", None) or getattr(msa_concrete, "InflFeatsOA", None)
                    
                    features_found = []
                    if fs and fs.FeatureSpecsOC:
                        get_feat_abbr_list(project, fs.FeatureSpecsOC, features_found)
                    
                    # Reduce this list to just the features in the chosen Bantu Sg and Pl feature groups
                    features_found = [(grp, val) for grp, val in features_found if grp in [bantuData["bantu_info"]["bantu_singular_feature_name"], bantuData["bantu_info"]["bantu_plural_feature_name"]]]

                    # Collect for summary
                    for grp, val in features_found:

                        global_noun_features[grp].add(val)
                    
                    if len(features_found) != 2 and len(features_found) > 0:

                        gloss = project.LexiconGetSenseGloss(sense)
                        sourceURL = project.BuildGotoURL(sense)
                        
                        msg = "root problem: only {} feature found (expected 2). lex: '{}', gloss: '{}'".format(len(features_found), lexeme_form, gloss)
                        
                        details = []

                        for grp, val in features_found:

                            details.append("    - {}: {}".format(grp, val))
                            
                        issues["roots"].append((msg, sourceURL, details))

        # --- AFFIX DATA EXTRACTION (Features & NC slots) ---
        in_noun_nc_slot = False
        in_any_nc_slot = False
        pos_owning_nc_slot = ""
        current_features_details = []
        entry_feat_abbrs = set()
        is_noun_attaching = False
        target_pos_abbr = ""

        if morphGuidStr == Utils.morphTypeReverseMap['prefix'] or morphGuidStr == Utils.morphTypeReverseMap['suffix']:

            for msa in entry.MorphoSyntaxAnalysesOC:

                if msa.ClassName != "MoInflAffMsa":
                    continue

                msa_c = IMoInflAffMsa(msa) 

                # General NC Tracking
                if hasattr(msa_c, "SlotsRC"):

                    for slot in msa_c.SlotsRC:

                        slot_name = project.BestStr(slot.Name)

                        if slot_name in allNCslotNames:

                            in_any_nc_slot = True

                            if hasattr(slot, "Owner") and slot.Owner and slot.Owner.ClassName == "PartOfSpeech":

                                pos_owning_nc_slot = project.BestStr(IPartOfSpeech(slot.Owner).Name)

                        # Specific Noun NC Slot tracking
                        if slot_name == nounClassSlotName:

                            in_noun_nc_slot = True

                # Feature Extraction
                fs = getattr(msa_c, "InflFeatsOA", None) or getattr(msa_c, "MsFeaturesOA", None)

                if fs and fs.FeatureSpecsOC:

                    fs_list = []
                    get_feat_abbr_list(project, fs.FeatureSpecsOC, fs_list)

                    for cat, val in fs_list:

                        entry_feat_abbrs.add(val.lower())
                        current_features_details.append("    - {}: {}".format(cat, val))

            if in_any_nc_slot and pos_owning_nc_slot:

                for f_val in entry_feat_abbrs:

                    found_nc_prefix_features[pos_owning_nc_slot].add(f_val)

            # Determine Target POS and Noun-attaching status (from Senses)
            for sense in entry.SensesOS:

                msa = sense.MorphoSyntaxAnalysisRA

                if msa:

                    if msa.ClassName != "MoInflAffMsa":
                        continue
                    
                    msa_c = IMoInflAffMsa(msa)  
                    pos_obj = None

                    if hasattr(msa_c, "SlotsRC") and msa_c.SlotsRC.Count > 0:

                        slot_c = IMoInflAffixSlot(msa_c.SlotsRC.ToArray()[0]) 

                        if hasattr(slot_c, "Owner") and slot_c.Owner and slot_c.Owner.ClassName == "PartOfSpeech":

                            pos_obj = IPartOfSpeech(slot_c.Owner)

                    elif hasattr(msa_c, "PartOfSpeechRA") and msa_c.PartOfSpeechRA:

                        pos_obj = msa_c.PartOfSpeechRA

                    elif hasattr(msa_c, "PartOfSpeech") and msa_c.PartOfSpeech:

                        pos_obj = msa_c.PartOfSpeech
                    
                    if pos_obj:

                        target_pos_abbr = project.BestStr(pos_obj.Abbreviation).lower()

                        if project.BestStr(pos_obj.Name) == nameForPOSNoun:

                            is_noun_attaching = True

        # --- CHECK 2: Noun NC-slot Prefixes (Inflection Features) ---
        if in_noun_nc_slot:

            total_prefixes_checked += 1
            feature_count = len(entry_feat_abbrs)

            if feature_count != 1:

                sourceURL = project.BuildGotoURL(entry)
                gloss = project.LexiconGetSenseGloss(entry.SensesOS[0]) if entry.SensesOS.Count > 0 else ""
                msg = "prefix problem: {} inflection features (expected exactly 1) for Noun NC-slot prefix '{}' with gloss: '{}'".format(feature_count, lexeme_form, gloss)
                issues["prefixes"].append((msg, sourceURL, current_features_details))

        # --- CHECKS 3, 4, 5: Affix Validation ---
        if morphGuidStr == Utils.morphTypeReverseMap['prefix'] or morphGuidStr == Utils.morphTypeReverseMap['suffix']:

            total_affixes_val_checked += 1
            
            # Feature Count Problem (Max 1, skip if Noun-attaching)
            if not is_noun_attaching and len(entry_feat_abbrs) > 1:

                sourceURL = project.BuildGotoURL(entry)
                msg = "affix problem: lex: '{}' has {} inflection features assigned (expected max 1)".format(lexeme_form, len(entry_feat_abbrs))
                issues["affix_gloss"].append((msg, sourceURL, current_features_details))

            for sense in entry.SensesOS:

                gloss = project.LexiconGetSenseGloss(sense)
                sourceURL = project.BuildGotoURL(sense)
                
                # Check 4: Duplicates
                affix_glosses[gloss].append((lexeme_form, sourceURL))
                
                # Check 5: No Spaces
                if " " in gloss:

                    msg = "affix problem: gloss contains spaces: '{}' for lex: '{}'".format(gloss, lexeme_form)
                    issues["spaces"].append((msg, sourceURL, []))

                # CHECK 3: Gloss Format and Alignment
                # Get the gender feature then the rest of the gloss
                match = re.match(r'^([0-9]+[a-z]*)\.(.+)', gloss)

                if not match:

                    # Ignore Noun NC prefixes for format check
                    if not in_noun_nc_slot:
                        msg = "affix problem: does not match expected 'n.xyz' format (found '{}') for lex: '{}'".format(gloss, lexeme_form)
                        issues["affix_gloss"].append((msg, sourceURL, []))
                else:
                    g_feat = match.group(1).lower()
                    g_rest = match.group(2).lower()
                    
                    problem_details = []

                    if g_feat not in entry_feat_abbrs:

                        problem_details.append("    - gloss feature '{}' not in entry features {}".format(g_feat, ", ".join(sorted(list(entry_feat_abbrs)))))

                    if target_pos_abbr and target_pos_abbr not in g_rest:

                        problem_details.append("    - POS '{}' not found in gloss '{}'".format(target_pos_abbr, gloss))
                    
                    if problem_details:

                        msg = "affix problem: consistency issue for lex: '{}' gloss: '{}'".format(lexeme_form, gloss)
                        issues["affix_gloss"].append((msg, sourceURL, problem_details))

    # Post-loop Check 4: Duplicate Affix Glosses
    for gloss, entries_list in affix_glosses.items():

        if len(entries_list) > 1:

            lexemes = sorted(list(set(e[0] for e in entries_list)))

            if len(lexemes) > 1:

                msg = "affix problem: duplicate gloss '{}' shared by: {}".format(gloss, ", ".join("'{}'".format(l) for l in lexemes))
                issues["duplicates"].append((msg, entries_list[0][1], []))

    # Check 6: Missing NC Affixes for any POS with an NC slot
    # Master reference list from the global_noun_features (union of all categories)
    master_features = set()

    for cat in global_noun_features:

        for val in global_noun_features[cat]:

            master_features.add(val.lower())
    
    issues["missing_nc"] = []

    if master_features:

        for pos_name in sorted(list(pos_with_nc_slot)):

            found_features = found_nc_prefix_features[pos_name]

            for m_feat in sorted(list(master_features), key=numeric_sort_key):

                if m_feat not in found_features and "na" not in m_feat.lower(): # Don't flag missing features that are explicitly marked as "NA"

                    msg = "slot problem: missing prefix in '{}' NC slot for feature '{}'".format(pos_name, m_feat)
                    issues["missing_nc"].append((msg, None, []))

    # --- REPORTING ---
    
    report.Info("Detailed Problem Reports:")
    report.Info("---------------------------------------")

    # Detailed Root Problems
    if issues["roots"]:
        report.Info("Roots (Check 1): Found {} nouns with missing or extra features:".format(len(issues["roots"])))
        for msg, url, details in issues["roots"]:
            report.Warning(msg, url)
            for detail in details:
                report.Info(detail)
        report.Blank()

    # Detailed Prefix Problems
    if issues["prefixes"]:
        report.Info("Prefixes (Check 2): Found {} noun NC-slot prefixes with missing or extra features:".format(len(issues["prefixes"])))
        for msg, url, details in issues["prefixes"]:
            report.Warning(msg, url)
            for detail in details:
                report.Info(detail)
        report.Blank()

    # Detailed Affix Gloss Problems
    if issues["affix_gloss"]:
        report.Info("Affixes (Check 3): Found {} affixes with gloss consistency issues:".format(len(issues["affix_gloss"])))
        for msg, url, details in issues["affix_gloss"]:
            report.Warning(msg, url)
            for detail in details:
                report.Info(detail)
        report.Blank()

    # Detailed Duplicate Gloss Problems
    if issues["duplicates"]:
        report.Info("Duplicates (Check 4): Found {} duplicate affix glosses:".format(len(issues["duplicates"])))
        for msg, url, details in issues["duplicates"]:
            report.Warning(msg, url)
        report.Blank()

    # Detailed Space Problems
    if issues["spaces"]:
        report.Info("Spaces (Check 5): Found {} affix glosses containing spaces:".format(len(issues["spaces"])))
        for msg, url, details in issues["spaces"]:
            report.Warning(msg, url)
        report.Blank()

    if not any(issues.values()):
        report.Info("No health check problems found!")
        report.Blank()

    # Detailed Missing NC Affixes (Check 6)
    if issues["missing_nc"]:
        issues["missing_nc"] = sorted(issues["missing_nc"], key=missing_nc_sort_key)
        report.Info("Missing Affixes (Check 6): Found {} instances of missing features in NC slots:".format(len(issues["missing_nc"])))
        for msg, url, details in issues["missing_nc"]:
            report.Warning(msg, url)
        report.Blank()

    # --- NOUN FEATURE SUMMARY ---
    if global_noun_features:
        report.Info("Noun Feature Value Summary (Sorted Numerically):")
        report.Info("-----------------------------------------------------------------------------")
        for grp in sorted(global_noun_features.keys()):
            values = sorted(list(global_noun_features[grp]), key=numeric_sort_key)
            report.Info("- {}: {}".format(grp, ", ".join(values)))
        report.Blank()

    # --- BANTU HEALTH CHECK SUMMARY ---
    report.Info("Bantu Health Check Summary:")
    report.Info("---------------------------------------------")
    
    # Check 1 Summary
    report.Info("Check 1: Noun roots (expected exactly 2 features)")
    report.Info("- Checked: {}".format(total_roots_checked))
    report.Info("- Problems: {}".format(len(issues["roots"])))
    report.Blank()

    # Check 2 Summary
    report.Info("Check 2: Noun NC-slot Prefixes (expected exactly 1 feature)")
    report.Info("- Checked: {}".format(total_prefixes_checked))
    report.Info("- Problems: {}".format(len(issues["prefixes"])))
    report.Blank()

    # Check 3 Summary
    report.Info("Check 3: Affixes Consistency (Format/Alignment)")
    report.Info("- Checked: {}".format(total_affixes_val_checked))
    report.Info("- Problems: {}".format(len(issues["affix_gloss"])))
    report.Blank()

    # Check 4 Summary
    report.Info("Check 4: Duplicate Affix Glosses")
    report.Info("- Checked: {}".format(total_affixes_val_checked))
    report.Info("- Problems: {}".format(len(issues["duplicates"])))
    report.Blank()

    # Check 5 Summary
    report.Info("Check 5: Spaces in Affix Glosses")
    report.Info("- Checked: {}".format(total_affixes_val_checked))
    report.Info("- Problems: {}".format(len(issues["spaces"])))
    report.Blank()

    # Check 6 Summary
    report.Info("Check 6: Missing NC Affixes across all POS")
    num_pos_nc = len(pos_with_nc_slot)
    report.Info("- Checked: {} Parts of Speech with NC slots".format(num_pos_nc))
    report.Info("- Problems: {}".format(len(issues["missing_nc"])))
    report.Blank()

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
