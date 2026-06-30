
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
    IFsClosedFeature,
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
    FTM_Version     : 10,
    FTM_ModifiesDB  : False,
    FTM_Synopsis    : _translate("BantuHealthCheck", "Flags various issues having to do with gender features in Bantu projects."),
    FTM_Description :
_translate("BantuHealthCheck", """
Bantu Health Check runs the following checks:
1. Noun roots have exactly one singular and one plural gender value defined, with an optional 'many' value. (Skips nouns with 0 features.)
2. Each affix in the noun-class slot has exactly one gender feature.
3. Affix glosses match the expected 'n.xyz' format and align with their features/POS (e.g. 19.num). Noun-class slot affixes may use a bare class number (e.g. '5') unless the sub-option to enforce the full format is on.
4. No two different affixes share the same gloss.
5. Affix glosses contain no spaces.
6. Every gender value in use has an affix in each part of speech's noun-class slot.
7. No value abbreviation is defined in more than one feature group (e.g. 19 cannot be in both the singular and plural groups).
8. No affix slot name is used by more than one part of speech.

A configuration dialog lets you choose which of these checks to run; your selection is remembered between runs.
""")
}

import os
import tomllib
import tomli_w 
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QDialogButtonBox, QApplication, QLabel, QComboBox, QCheckBox, QGroupBox, QFrame, QListWidget, QListWidgetItem, QDialogButtonBox, QMessageBox
from PyQt6.QtCore import Qt

#----------------------------------------------------------------
# Constants
BANTU_SETTINGS_FILE = "BantuSettings.toml"

# The health checks, in run/report order. Each tuple is (key, short title, one-line description).
# The key matches the issues[] bucket the check fills and is what gets saved to / loaded from the settings file.
CHECKS = [
    ("roots",       "Check 1: Noun roots",              "Each noun root has exactly one singular and one plural gender value (optional 'many')."),
    ("prefixes",    "Check 2: Noun-class slot affixes", "Each affix in the noun-class slot has exactly one gender feature."),
    ("affix_gloss", "Check 3: Affix gloss consistency", "Affix glosses match the expected 'n.xyz' format and align with their features/POS. E.g. 19.num"),
    ("duplicates",  "Check 4: Duplicate glosses",       "No two different affixes share the same gloss."),
    ("spaces",      "Check 5: Spaces in glosses",       "Affix glosses contain no spaces."),
    ("missing_nc",  "Check 6: Missing NC affixes",      "Every gender value in use has an affix in each part of speech's noun-class slot."),
    ("dup_abbr",    "Check 7: Duplicate value abbrevs", "No value abbreviation is defined in more than one feature group. E.g. 19 can't be in the singular and plural groups."),
    ("dup_slots",   "Check 8: Duplicate slot names",    "No affix slot name is used by more than one part of speech."),
]

#----------------------------------------------------------------
# Helper Functions

def numeric_sort_key(s):

    """
    Sort key to handle numeric prefixes in strings (e.g., '9pl' before '14pl').
    Values that do not start with a number (e.g. 'NAsg') sort after all
    numerical values, alphabetically among themselves.
    """
    match = re.match(r'(\d+)', s)

    if match:

        return (0, int(match.group(1)), s)

    return (1, float('inf'), s)

def missing_nc_sort_key(issue):

    msg = issue[0]
    match = re.search(r"missing affix in '([^']+)' NC slot for feature '([^']+)'", msg)

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

                # ValueOA returns a generic IFsAbstractStructure. We MUST cast to IFsFeatStruc to access FeatureSpecsOC.
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
        self.resize(800, 560)

        # Outer layout: a row of two columns (config | checks) on top, the OK/Cancel buttons spanning the bottom.
        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        columns_layout = QHBoxLayout()
        outer_layout.addLayout(columns_layout)

        # Left column holds the existing configuration widgets.
        main_layout = QVBoxLayout()
        columns_layout.addLayout(main_layout, 1)

        self.all_slot_options = slot_options
        self.current_data = current_data

        # 1. POS Noun Name
        main_layout.addWidget(QLabel("Name for POS Noun:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(pos_options)
        noun_index = self.pos_combo.findText("Noun")

        if noun_index >= 0:

            self.pos_combo.setCurrentIndex(noun_index)

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
        main_layout.addWidget(QLabel("Feature containing singular noun class values:"))
        self.sg_combo = QComboBox()
        self.sg_combo.addItems(feature_options)

        # MatchContains matches any item that contains the word (e.g. "Bantu Singular") and is case-insensitive, so no separate lowercase lookup is needed.
        my_index = self.sg_combo.findText("Singular", Qt.MatchFlag.MatchContains)

        if my_index >= 0:

            self.sg_combo.setCurrentIndex(my_index)

        main_layout.addWidget(self.sg_combo)

        main_layout.addWidget(QLabel("Feature containing plural noun class values:"))
        self.pl_combo = QComboBox()
        self.pl_combo.addItems(feature_options)

        # MatchContains matches any item that contains the word (e.g. "Bantu Plural") and is case-insensitive.
        my_index = self.pl_combo.findText("Plural", Qt.MatchFlag.MatchContains)

        if my_index >= 0:

            self.pl_combo.setCurrentIndex(my_index)

        main_layout.addWidget(self.pl_combo)

        # Optional 'many' feature: blank is a valid (default) choice.
        main_layout.addWidget(QLabel("Feature containing many noun class values (optional):"))
        self.many_combo = QComboBox()
        self.many_combo.addItems([""] + feature_options)

        # MatchContains matches any item that contains the word (e.g. "Bantu Many") and is case-insensitive.
        my_index = self.many_combo.findText("Many", Qt.MatchFlag.MatchContains)

        if my_index >= 0:

            self.many_combo.setCurrentIndex(my_index)

        main_layout.addWidget(self.many_combo)

        main_layout.addStretch(1)

        # Right column holds the list of checks the user can enable/disable.
        columns_layout.addLayout(self.build_checks_panel(), 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer_layout.addWidget(buttons)

        # Connect signals and initialize
        self.pos_combo.currentTextChanged.connect(self.update_ui_filtering)
        self.set_initial_values(pos_options, feature_options)
        self.update_ui_filtering()

    def build_checks_panel(self):

        """Builds the right-hand panel listing every check with a checkbox and a
        one-line description. Returns a layout to add to the dialog."""
        panel_layout = QVBoxLayout()

        group = QGroupBox("Checks to run")
        group_layout = QVBoxLayout()
        group.setLayout(group_layout)

        # Which checks were enabled last time. Default to all checks enabled when nothing has been saved yet.
        saved_enabled = self.current_data.get("checks_to_run", None)

        self.check_all_box = QCheckBox("Check / Uncheck all")
        self.check_all_box.clicked.connect(self.on_check_all_clicked)
        group_layout.addWidget(self.check_all_box)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        group_layout.addWidget(line)

        self.check_boxes = {}   # check key -> QCheckBox

        for key, title, desc in CHECKS:

            row = QHBoxLayout()

            cb = QCheckBox()

            if saved_enabled is None:

                cb.setChecked(True)
            else:
                cb.setChecked(key in saved_enabled)

            cb.stateChanged.connect(self.sync_check_all)

            label = QLabel("<b>{}</b><br>{}".format(title, desc))
            label.setWordWrap(True)

            row.addWidget(cb, 0, Qt.AlignmentFlag.AlignTop)
            row.addWidget(label, 1)
            group_layout.addLayout(row)

            self.check_boxes[key] = cb

            # Check 3 carries an indented sub-option: optionally enforce the 'n.xyz' gloss format on noun-class
            # slot affixes too (off by default, since bare class numbers like '5' are normally allowed there).
            if key == "affix_gloss":

                group_layout.addLayout(self.build_nc_format_suboption())

        group_layout.addStretch(1)
        panel_layout.addWidget(group)

        self.sync_check_all()

        return panel_layout

    def on_check_all_clicked(self, checked):

        """User toggled the master checkbox: apply to every check."""

        for cb in self.check_boxes.values():

            cb.setChecked(checked)

    def sync_check_all(self):

        """Keep the master checkbox in sync with the individual checks."""
        states = [cb.isChecked() for cb in self.check_boxes.values()]
        self.check_all_box.blockSignals(True)
        self.check_all_box.setChecked(bool(states) and all(states))
        self.check_all_box.blockSignals(False)

    def build_nc_format_suboption(self):

        """Indented sub-option under Check 3. When checked, noun-class slot affixes must also match the 'n.xyz' gloss format (e.g. '5.n');
        when unchecked (the default) a bare class number like '5' is accepted for the noun slot, and it only applies when Check 3 is enabled."""

        row = QHBoxLayout()

        # Indent so the sub-option visually reads as belonging to Check 3.
        row.addSpacing(30)

        saved = self.current_data.get("enforce_noun_slot_gloss_format", False)

        self.nc_format_box = QCheckBox()
        self.nc_format_box.setChecked(saved)

        label = QLabel("Also require 'n.xyz' format for noun-class slot affixes (e.g. '5.n'); otherwise a bare class number like '5' is allowed there.")
        label.setWordWrap(True)

        row.addWidget(self.nc_format_box, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(label, 1)

        # The sub-option is meaningless when Check 3 is off, so grey it out in step with Check 3.
        self.check_boxes["affix_gloss"].stateChanged.connect(self.sync_nc_format_enabled)
        self.sync_nc_format_enabled()

        return row

    def sync_nc_format_enabled(self):

        """Enable the noun-slot format sub-option only while Check 3 is checked."""
        self.nc_format_box.setEnabled(self.check_boxes["affix_gloss"].isChecked())

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

            # An empty val means nothing was saved, so leave the auto-selected default in place rather than snapping to the blank entry.
            if not val:

                return

            index = combo.findText(val)

            if index >= 0: combo.setCurrentIndex(index)

        set_val(self.pos_combo, self.current_data.get("name_for_POS_noun", ""))
        set_val(self.sg_combo, self.current_data.get("bantu_singular_feature_name", ""))
        set_val(self.pl_combo, self.current_data.get("bantu_plural_feature_name", ""))
        set_val(self.many_combo, self.current_data.get("bantu_many_feature_name", ""))

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

        # The checks the user wants to run (preserves CHECKS order).
        checks_to_run = [key for key, _, _ in CHECKS if self.check_boxes[key].isChecked()]

        return {
            "bantu_info": {
                "name_for_POS_noun": selected_noun_pos,
                "noun_class_slot": self.noun_slot_combo.currentText(), # Explicitly saved
                "slots_with_noun_class_affixes": others_list,
                "bantu_singular_feature_name": self.sg_combo.currentText(),
                "bantu_plural_feature_name": self.pl_combo.currentText(),
                "bantu_many_feature_name": self.many_combo.currentText(),
                "checks_to_run": checks_to_run,
                "enforce_noun_slot_gloss_format": self.nc_format_box.isChecked()
            }
        }

def save_dialog_data(dialog, file_path):

    # 1. Extract the dictionary from the dialog This should return: {"bantu_info": {...}}
    updated_data = dialog.get_results()

    try:
        # 2. Open file in 'wb' (write binary) mode TOML requires UTF-8, and tomli_w handles this via binary streams
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
        "spaces": [],
        "dup_abbr": [],
        "dup_slots": []
    }

    # Store unique features for summary
    global_noun_features = defaultdict(set)

    # Check 4: Store glosses to find duplicates
    affix_glosses = defaultdict(list) # gloss -> list of (lexeme, sourceURL)

    # Check 6: Track found features for all NC slots pos_name -> set of feature values
    found_nc_prefix_features = defaultdict(set)

    # Track POS that actually have an NC slot
    pos_with_nc_slot = set()

    # 1. Find the NC slot for affix checking (Noun specific)
    # This should return: {"bantu_info": {...}}
    bantuData = dialog.get_results()
    nameForPOSNoun = bantuData["bantu_info"]["name_for_POS_noun"]
    nounClassSlotName = bantuData["bantu_info"]["noun_class_slot"] # This is the saved combo box value
    slots_list = bantuData["bantu_info"]["slots_with_noun_class_affixes"]

    # Configured gender feature groups (Many is optional / may be blank).
    sgFeatName = bantuData["bantu_info"]["bantu_singular_feature_name"]
    plFeatName = bantuData["bantu_info"]["bantu_plural_feature_name"]
    manyFeatName = bantuData["bantu_info"].get("bantu_many_feature_name", "")

    relevant_groups = [sgFeatName, plFeatName]

    if manyFeatName:

        relevant_groups.append(manyFeatName)

    # Which checks the user enabled. Default to all checks if the setting is absent (e.g. an older settings file). enabled[key] gates both detection and reporting for each check.
    checks_to_run = bantuData["bantu_info"].get("checks_to_run", [key for key, _, _ in CHECKS])
    enabled = {key: (key in checks_to_run) for key, _, _ in CHECKS}

    # Sub-option of Check 3: when on, noun-class slot affixes must also match the 'n.xyz' gloss format rather than
    # being allowed a bare class number like '5'. Defaults off to preserve the traditional bare-number convention.
    enforceNounSlotGlossFormat = bantuData["bantu_info"].get("enforce_noun_slot_gloss_format", False)

    if not any(enabled.values()):

        report.Warning(_translate("BantuHealthCheck", "No checks selected - nothing to do."))

        return

    # 1. Get all possible slot names (as a flat list)
    allNCslotNames = []

    for row in slots_list:

        allNCslotNames.extend(row['slots'])
        pos_with_nc_slot.add(row['POS'])

    # 2. Create a mapping for reverse lookup (Slot -> POS)
    slot_to_pos_map = {}

    # POS -> list of its configured NC slot names (for reporting which slot an affix is missing from in Check 6).
    pos_to_slots_map = defaultdict(list)

    for row in slots_list:

        current_pos = row['POS']

        for slot in row['slots']:

            slot_to_pos_map[slot] = current_pos
            pos_to_slots_map[current_pos].append(slot)

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

                    if enabled["roots"]:

                        total_roots_checked += 1

                    fs = getattr(msa_concrete, "MsFeaturesOA", None) or getattr(msa_concrete, "InflFeatsOA", None)

                    features_found = []

                    if fs and fs.FeatureSpecsOC:

                        get_feat_abbr_list(project, fs.FeatureSpecsOC, features_found)

                    # Reduce this list to just the features in the chosen Bantu Sg, Pl and (optional) Many feature groups.
                    features_found = [(grp, val) for grp, val in features_found if grp in relevant_groups]

                    # Collect for summary
                    for grp, val in features_found:

                        global_noun_features[grp].add(val)

                    # A valid noun root has exactly one singular and one plural value, plus an optional (at most one) 'many' value. Check all nouns.
                    if True: #features_found:

                        sg_count = sum(1 for grp, val in features_found if grp == sgFeatName)
                        pl_count = sum(1 for grp, val in features_found if grp == plFeatName)
                        many_count = sum(1 for grp, val in features_found if manyFeatName and grp == manyFeatName)

                        problems = []

                        if sg_count != 1:

                            problems.append("expected 1 singular feature, found {}".format(sg_count))

                        if pl_count != 1:

                            problems.append("expected 1 plural feature, found {}".format(pl_count))

                        if many_count > 1:

                            problems.append("expected at most 1 many feature, found {}".format(many_count))

                        if problems and enabled["roots"]:

                            gloss = project.LexiconGetSenseGloss(sense)
                            sourceURL = project.BuildGotoURL(sense)

                            msg = "root problem: ({}). lex: '{}', gloss: '{}'".format("; ".join(problems), lexeme_form, gloss)

                            details = ["Features found for '{}':".format(lexeme_form)]

                            for grp, val in features_found:

                                details[0] += " - {}: {}".format(grp, val)

                            issues["roots"].append((msg, sourceURL, details))

        # --- AFFIX DATA EXTRACTION (Features & NC slots) ---
        in_noun_nc_slot = False
        in_any_nc_slot = False
        pos_owning_nc_slot = ""
        current_features_details = []
        entry_feat_abbrs = set()

        # Values belonging only to the gender feature groups designated in the UI (singular / plural / many). Used by Check 2, which ignores other features.
        entry_gender_feat_abbrs = set()
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

                        # Include affix-borne gender values (e.g. an NC-prefix class) in the summary even when no noun root carries that value.
                        if cat in relevant_groups:

                            global_noun_features[cat].add(val)
                            entry_gender_feat_abbrs.add(val.lower())

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

        # --- CHECK 2: Noun NC-slot Affixes (Inflection Features) ---
        if enabled["prefixes"] and in_noun_nc_slot:

            total_prefixes_checked += 1

            # Only count the designated gender features (singular / plural / many); other inflection features are ignored for this check.
            feature_count = len(entry_gender_feat_abbrs)

            if feature_count != 1:

                sourceURL = project.BuildGotoURL(entry)
                gloss = project.LexiconGetSenseGloss(entry.SensesOS[0]) if entry.SensesOS.Count > 0 else ""
                msg = "affix problem: {} gender features (expected exactly 1) for Noun NC-slot affix '{}' with gloss: '{}'".format(feature_count, lexeme_form, gloss)
                issues["prefixes"].append((msg, sourceURL, current_features_details))

        # --- CHECKS 3, 4, 5: Affix Validation ---
        if (enabled["affix_gloss"] or enabled["duplicates"] or enabled["spaces"]) and \
           (morphGuidStr == Utils.morphTypeReverseMap['prefix'] or morphGuidStr == Utils.morphTypeReverseMap['suffix']):

            total_affixes_val_checked += 1

            # Feature Count Problem (Max 1, skip if Noun-attaching) [Check 3]
            if enabled["affix_gloss"] and not is_noun_attaching and len(entry_feat_abbrs) > 1:

                sourceURL = project.BuildGotoURL(entry)
                msg = "affix problem: lex: '{}' has {} inflection features assigned (expected max 1)".format(lexeme_form, len(entry_feat_abbrs))
                issues["affix_gloss"].append((msg, sourceURL, current_features_details))

            for sense in entry.SensesOS:

                gloss = project.LexiconGetSenseGloss(sense)
                sourceURL = project.BuildGotoURL(sense)

                # Check 4: Duplicates
                if enabled["duplicates"]:

                    affix_glosses[gloss].append((lexeme_form, sourceURL))

                # Check 5: No Spaces
                if enabled["spaces"] and " " in gloss:

                    msg = "affix problem: gloss contains spaces: '{}' for lex: '{}'".format(gloss, lexeme_form)
                    issues["spaces"].append((msg, sourceURL, []))

                # CHECK 3: Gloss Format and Alignment
                if not enabled["affix_gloss"]:

                    continue

                # Get the gender feature then the rest of the gloss
                match = re.match(r'^([0-9]+[a-z]*)\.(.+)', gloss)

                if not match:

                    # Noun NC prefixes are conventionally glossed with a bare class number (e.g. '5'), so by default they are exempt from the
                    # 'n.xyz' format check. The Check 3 sub-option forces the full format on them too, in which case a bare number is flagged.
                    if not in_noun_nc_slot or enforceNounSlotGlossFormat:

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

    # Check 6: Missing NC Affixes for any POS with an NC slot. Master reference list from the global_noun_features (union of all categories)
    master_features = set()

    for cat in global_noun_features:

        for val in global_noun_features[cat]:

            master_features.add(val.lower())

    issues["missing_nc"] = []

    if enabled["missing_nc"] and master_features:

        for pos_name in sorted(list(pos_with_nc_slot)):

            found_features = found_nc_prefix_features[pos_name]

            # Name the configured NC slot(s) for this POS so the user knows where the affix is missing.
            slot_names = pos_to_slots_map.get(pos_name, [])
            slot_label = ", ".join("'{}'".format(s) for s in slot_names) if slot_names else "(unknown)"

            for m_feat in sorted(list(master_features), key=numeric_sort_key):

                if m_feat not in found_features and "na" not in m_feat.lower(): # Don't flag missing features that are explicitly marked as "NA"

                    msg = "slot problem: missing affix in '{}' Noun Class slot {} for feature '{}'".format(pos_name, slot_label, m_feat)
                    issues["missing_nc"].append((msg, None, []))

    # Enumerate the *defined* value abbreviations for each configured feature group, regardless of whether any
    # entry uses them. Used both for the "all possible values" summary and the Check 7 duplicate test below.
    defined_feature_values = defaultdict(set)   # group name -> set of value abbreviations

    for feature in feature_objects:

        grp_name = project.BestStr(feature.Name)

        if grp_name not in relevant_groups or feature.ClassName != "FsClosedFeature":

            continue

        closed = IFsClosedFeature(feature)

        for val in closed.ValuesOC:

            abbr = project.BestStr(val.Abbreviation)

            if abbr and abbr != "***":

                defined_feature_values[grp_name].add(abbr)

    # Check 7: Duplicate value abbreviations across feature groups, based on the feature *definitions* (independent of usage). It is an error
    # for the same abbreviation (e.g. '19') to be defined in more than one configured feature group. The '?' placeholder value is ignored.
    abbr_to_groups = defaultdict(set)   # abbr (lower) -> set of group names
    abbr_display = {}                   # abbr (lower) -> original abbr text

    for grp, vals in defined_feature_values.items():

        for val in vals:

            if val == "?":

                continue

            key = val.lower()
            abbr_to_groups[key].add(grp)
            abbr_display.setdefault(key, val)

    if enabled["dup_abbr"]:

        for key in sorted(abbr_to_groups.keys(), key=numeric_sort_key):

            groups = abbr_to_groups[key]

            if len(groups) > 1:

                msg = "feature problem: value '{}' is defined in multiple feature groups: {}".format(
                    abbr_display[key], ", ".join(sorted(groups)))
                issues["dup_abbr"].append((msg, None, []))

    # Check 8: Duplicate slot names. Slot matching in this module is name-based (see the SlotsRC / allNCslotNames checks above), so two affix
    # slots sharing the same name make that matching ambiguous. Warn for any slot name that occurs more than once across all parts of speech.
    slot_name_to_pos = defaultdict(list)   # slot name -> list of POS names

    if enabled["dup_slots"]:

        for pos in project.lp.AllPartsOfSpeech:

            pos_slot_names = []
            get_all_slots(project, pos, pos_slot_names)

            pos_name = project.BestStr(IPartOfSpeech(pos).Name)

            for sn in pos_slot_names:

                slot_name_to_pos[sn].append(pos_name)

        for sn in sorted(slot_name_to_pos.keys()):

            pos_names = slot_name_to_pos[sn]

            if len(pos_names) > 1:

                msg = "slot problem: duplicate slot name '{}' defined {} times in: {}".format(
                    sn, len(pos_names), ", ".join(sorted(pos_names)))
                issues["dup_slots"].append((msg, None, []))

    # --- REPORTING ---

    report.Info("Detailed Problem Reports:")
    report.Info("---------------------------------------")

    # Detailed Root Problems
    if issues["roots"]:

        report.Info("Roots (Check 1): Found {} nouns with missing or extra features:".format(len(issues["roots"])))

        for msg, url, details in issues["roots"]:

            for detail in details:

                report.Info(detail)

            report.Warning(msg, url)

        report.Blank()

    # Detailed Prefix Problems
    if issues["prefixes"]:

        report.Info("Affixes (Check 2): Found {} noun NC-slot affixes with missing or extra features:".format(len(issues["prefixes"])))

        for msg, url, details in issues["prefixes"]:

            report.Warning(msg, url)

            for detail in details:

                report.Info(detail)

        report.Blank()

    # Detailed Affix Gloss Problems
    if issues["affix_gloss"]:

        report.Info("Affixes (Check 3): Found {} affixes with gloss consistency issues:".format(len(issues["affix_gloss"])))

        for msg, url, details in issues["affix_gloss"]:

            for detail in details:

                report.Info(detail)

            report.Warning(msg, url)

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

    # Detailed Duplicate Abbreviation Problems (Check 7)
    if issues["dup_abbr"]:

        report.Info("Duplicate Values (Check 7): Found {} value abbreviations shared across feature groups:".format(len(issues["dup_abbr"])))

        for msg, url, details in issues["dup_abbr"]:

            report.Warning(msg, url)

        report.Blank()

    # Detailed Duplicate Slot Name Problems (Check 8)
    if issues["dup_slots"]:

        report.Info("Duplicate Slots (Check 8): Found {} slot names used by more than one part of speech:".format(len(issues["dup_slots"])))

        for msg, url, details in issues["dup_slots"]:

            report.Warning(msg, url)

        report.Blank()

    # --- NOUN FEATURE SUMMARY ---
    if global_noun_features:

        report.Info("Noun Feature Value Summary - Values In Use:")
        report.Info("-----------------------------------------------------------------------------")

        for grp in sorted(global_noun_features.keys()):

            values = sorted(list(global_noun_features[grp]), key=numeric_sort_key)
            report.Info("- {}: {}".format(grp, ", ".join(values)))

        report.Blank()

    # All possible values defined for each configured feature group, whether or
    # not any entry uses them.
    if defined_feature_values:

        report.Info("Noun Feature Value Summary - All Possible Values:")
        report.Info("-----------------------------------------------------------------------------")

        for grp in sorted(defined_feature_values.keys()):

            values = sorted(list(defined_feature_values[grp]), key=numeric_sort_key)
            report.Info("- {}: {}".format(grp, ", ".join(values)))

        report.Blank()

    # --- BANTU HEALTH CHECK SUMMARY ---
    report.Info("Bantu Health Check Summary:")
    report.Info("---------------------------------------------")

    # Check 1 Summary
    if enabled["roots"]:

        report.Info("Check 1: Noun roots (expected 1 singular + 1 plural, optional 1 many)")
        report.Info("- Checked: {}".format(total_roots_checked))
        report.Info("- Problems: {}".format(len(issues["roots"])))
        report.Blank()

    # Check 2 Summary
    if enabled["prefixes"]:

        report.Info("Check 2: Noun Noun Class-slot Affixes (expected exactly 1 feature)")
        report.Info("- Checked: {}".format(total_prefixes_checked))
        report.Info("- Problems: {}".format(len(issues["prefixes"])))
        report.Blank()

    # Check 3 Summary
    if enabled["affix_gloss"]:

        report.Info("Check 3: Affixes Consistency (Format/Alignment)")
        report.Info("- Checked: {}".format(total_affixes_val_checked))
        report.Info("- Problems: {}".format(len(issues["affix_gloss"])))
        report.Blank()

    # Check 4 Summary
    if enabled["duplicates"]:

        report.Info("Check 4: Duplicate Affix Glosses")
        report.Info("- Checked: {}".format(total_affixes_val_checked))
        report.Info("- Problems: {}".format(len(issues["duplicates"])))
        report.Blank()

    # Check 5 Summary
    if enabled["spaces"]:

        report.Info("Check 5: Spaces in Affix Glosses")
        report.Info("- Checked: {}".format(total_affixes_val_checked))
        report.Info("- Problems: {}".format(len(issues["spaces"])))
        report.Blank()

    # Check 6 Summary
    if enabled["missing_nc"]:

        report.Info("Check 6: Missing Noun Class Affixes across all POS")
        num_pos_nc = len(pos_with_nc_slot)
        report.Info("- Checked: {} Parts of Speech with Noun Class slots".format(num_pos_nc))
        report.Info("- Problems: {}".format(len(issues["missing_nc"])))
        report.Blank()

    # Check 7 Summary
    if enabled["dup_abbr"]:

        report.Info("Check 7: Duplicate value abbreviations across feature groups")
        report.Info("- Checked: {} distinct value abbreviations".format(len(abbr_to_groups)))
        report.Info("- Problems: {}".format(len(issues["dup_abbr"])))
        report.Blank()

    # Check 8 Summary
    if enabled["dup_slots"]:

        report.Info("Check 8: Duplicate slot names across parts of speech")
        report.Info("- Checked: {} distinct slot names".format(len(slot_name_to_pos)))
        report.Info("- Problems: {}".format(len(issues["dup_slots"])))
        report.Blank()

#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)

#----------------------------------------------------------------
if __name__ == '__main__':

    print(FlexToolsModule.Help())
