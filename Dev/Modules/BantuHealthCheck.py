from flextoolslib import *
#from flexlibs2 import POSOperations
import re
from collections import defaultdict

# Import raw LibLCM interfaces for casting
from Modules.FLExTrans.Lib import Utils
from SIL.LCModel import IFsComplexValue, IFsFeatStruc, IFsClosedValue, IPartOfSpeech, IMoStemMsa, IMoInflAffMsa, IMoInflAffixSlot

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {
    FTM_Name        : "Bantu Health Check",
    FTM_Version     : 5,
    FTM_ModifiesDB  : False,
    FTM_Synopsis    : "Flags Bantu Noun roots without 2 features and NC prefixes without features.",
    FTM_Description : 
"""
Bantu Health Check:
1. Identifies Noun 'roots' (bound root, bound stem, discontiguous phrase, 
   particle, phrase, root, stem) and verifies that they have exactly two
   inflection feature values defined. (Skips nouns with 0 features).
2. Identifies prefixes in the 'NC' slot and verifies that they have 
   exactly one inflection feature defined.

Issues are grouped by morphological type (roots, then prefixes, then suffixes).
Warnings use a gentler tone (primarily lowercase, "problem" instead of "fail").
"""
}

#----------------------------------------------------------------
# Constants

TARGET_POS = "Noun"
TARGET_SLOT = "NC"

ROOT_MORPH_TYPES = [
    "bound root",
    "bound stem",
    "discontiguous phrase",
    "particle",
    "phrase",
    "root",
    "stem"
]

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

def as_string(project, obj):
    if not obj: return ""
    return project.BestStr(obj)

def as_tag(project, possibility):
    if not possibility: return ""
    return project.BestStr(possibility.Abbreviation)

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
            
            featGrpName = as_string(project, spec_closed.FeatureRA.Name) if spec_closed.FeatureRA else "ERR"
            abbValue = as_tag(project, spec_closed.ValueRA) if spec_closed.ValueRA else "ERR"
                
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

#----------------------------------------------------------------
# The main processing function

def Main(project, report, modifyAllowed):
    report.Info("Starting Bantu language health check...")
    
    entries = list(project.LexiconAllEntriesSorted())
    total_roots_checked = 0
    total_prefixes_checked = 0
    total_suffixes_checked = 0
    total_affixes_val_checked = 0
    
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
    #noun_pos_raw = posOps.Find(TARGET_POS)

    for pos in project.lp.AllPartsOfSpeech:
        abbr = Utils.as_string(pos.Abbreviation)
        if abbr == 'n':
            break

    noun_pos_raw = pos if abbr == 'n' else None


    # posMap = {}
    # Utils.get_categories(project, report, posMap, TargetDB=None, numCatErrorsToShow=1, addInflectionClasses=True)
    # noun_pos_raw = posMap.get(TARGET_POS, None)

    nc_slot = None
    if noun_pos_raw:
        nc_slot = find_slot_recursive(project, noun_pos_raw, TARGET_SLOT)
                    
    if not nc_slot:
        report.Warning("Could not find slot '{}' owned by '{}' in the project. Skipping NC prefix check (Check 2).".format(TARGET_SLOT, TARGET_POS))

    # Identify all POS that have an NC slot (For Check 6)
    def scan_pos_recursive(pos_obj):
        p_concrete = IPartOfSpeech(pos_obj) #  CastingOperations.cast_to_concrete(pos_obj)
        p_name = project.BestStr(pos_obj.Name)
        has_nc = False
        if hasattr(p_concrete, "AffixSlotsOC"):
            for s in p_concrete.AffixSlotsOC:
                s_name = project.BestStr(s.Name)
                s_abbr = project.BestStr(s.Abbreviation) if hasattr(s, "Abbreviation") else ""
                if "NC" in s_name or "NC" in s_abbr:
                    has_nc = True
                    break
        if has_nc:
            pos_with_nc_slot.add(p_name)
        
        if hasattr(p_concrete, "SubPossibilitiesOS"):
            for sub in p_concrete.SubPossibilitiesOS:
                scan_pos_recursive(sub)

    pos_list = []
    try:
        for p_obj in project.lp.AllPartsOfSpeech:
            pos_list.append(p_obj)
    except:
        pass

    for pos in pos_list:
        scan_pos_recursive(pos)

    for entry in entries:
        # Get Morph Type (MorphTypeRA.Name)
        morph_type = ""
        if entry.LexemeFormOA and entry.LexemeFormOA.MorphTypeRA:
            morph_type = project.BestStr(entry.LexemeFormOA.MorphTypeRA.Name)
            
        lexeme_form = project.LexiconGetLexemeForm(entry)
        
        # --- CHECK 1: Noun Roots (Inflection Features) ---
        if morph_type in ROOT_MORPH_TYPES:
            for sense in entry.SensesOS:
                msa = sense.MorphoSyntaxAnalysisRA
                if not msa: continue
                
                msa_concrete = IMoStemMsa(msa) #CastingOperations.cast_to_concrete(msa)
                
                pos_name = ""
                if hasattr(msa_concrete, "PartOfSpeechRA") and msa_concrete.PartOfSpeechRA:
                    pos_name = project.BestStr(msa_concrete.PartOfSpeechRA.Name)
                
                if pos_name == "Noun":
                    total_roots_checked += 1
                    
                    fs = getattr(msa_concrete, "MsFeaturesOA", None) or getattr(msa_concrete, "InflFeatsOA", None)
                    
                    features_found = []
                    if fs and fs.FeatureSpecsOC:
                        get_feat_abbr_list(project, fs.FeatureSpecsOC, features_found)
                    
                    # Collect for summary
                    for grp, val in features_found:
                        global_noun_features[grp].add(val)
                    
                    if len(features_found) != 2 and len(features_found) > 0:
                        gloss = project.LexiconGetSenseGloss(sense)
                        sourceURL = project.BuildGotoURL(sense)
                        
                        msg = "root problem: only {} feature found (expected 2). lex: '{}', gloss: '{}'".format(
                             len(features_found), lexeme_form, gloss)
                        
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

        if morph_type == "prefix" or morph_type == "suffix":
            for msa in entry.MorphoSyntaxAnalysesOC:
                if msa.ClassName != "MoInflAffMsa":
                    continue
                msa_c = IMoInflAffMsa(msa) # CastingOperations.cast_to_concrete(msa)
                # General NC Tracking
                if hasattr(msa_c, "SlotsRC"):
                    for s in msa_c.SlotsRC:
                        s_name = project.BestStr(s.Name)
                        s_abbr = project.BestStr(s.Abbreviation) if hasattr(s, "Abbreviation") else ""

                        if "NC" in s_name or "NC" in s_abbr:
                        #if s_name == "NC" or s_abbr == "NC":
                            in_any_nc_slot = True
                            if hasattr(s, "Owner") and s.Owner and s.Owner.ClassName == "PartOfSpeech":
                                pos_owning_nc_slot = project.BestStr(IPartOfSpeech(s.Owner).Name)
                        # Specific Noun NC Slot tracking
                        if nc_slot and s.Hvo == nc_slot.Hvo:
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
                    msa_c = IMoInflAffMsa(msa) # CastingOperations.cast_to_concrete(msa)
                    pos_obj = None
                    if hasattr(msa_c, "SlotsRC") and msa_c.SlotsRC.Count > 0:
                        slot_c = IMoInflAffixSlot(msa_c.SlotsRC.ToArray()[0]) #CastingOperations.cast_to_concrete(msa_c.SlotsRC.ToArray()[0])
                        if hasattr(slot_c, "Owner") and slot_c.Owner and slot_c.Owner.ClassName == "PartOfSpeech":
                            pos_obj = IPartOfSpeech(slot_c.Owner)
                    elif hasattr(msa_c, "PartOfSpeechRA") and msa_c.PartOfSpeechRA:
                        pos_obj = msa_c.PartOfSpeechRA
                    elif hasattr(msa_c, "PartOfSpeech") and msa_c.PartOfSpeech:
                        pos_obj = msa_c.PartOfSpeech
                    
                    if pos_obj:
                        target_pos_abbr = project.BestStr(pos_obj.Abbreviation).lower()
                        if project.BestStr(pos_obj.Name) == TARGET_POS:
                            is_noun_attaching = True

        # --- CHECK 2: Noun NC-slot Prefixes (Inflection Features) ---
        if in_noun_nc_slot:
            total_prefixes_checked += 1
            feature_count = len(entry_feat_abbrs)
            if feature_count != 1:
                sourceURL = project.BuildGotoURL(entry)
                gloss = project.LexiconGetSenseGloss(entry.SensesOS[0]) if entry.SensesOS.Count > 0 else ""
                msg = "prefix problem: {} inflection features (expected exactly 1) for Noun NC-slot prefix '{}' with gloss: '{}'".format(
                    feature_count, lexeme_form, gloss)
                issues["prefixes"].append((msg, sourceURL, current_features_details))

        # --- CHECKS 3, 4, 5: Affix Validation ---
        if morph_type == "prefix" or morph_type == "suffix":
            total_affixes_val_checked += 1
            
            # Feature Count Problem (Max 1, skip if Noun-attaching)
            if not is_noun_attaching and len(entry_feat_abbrs) > 1:
                sourceURL = project.BuildGotoURL(entry)
                msg = "affix problem: lex: '{}' has {} inflection features assigned (expected max 1)".format(
                    lexeme_form, len(entry_feat_abbrs))
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
                match = re.match(r'^([0-9]+[a-z]*)\.([a-z/]+)', gloss)
                if not match:
                    # Ignore Noun NC prefixes for format check
                    if not in_noun_nc_slot:
                        msg = "affix problem: does not match expected 'n.xyz' format (found '{}') for lex: '{}'".format(gloss, lexeme_form)
                        issues["affix_gloss"].append((msg, sourceURL, []))
                else:
                    g_feat = match.group(1).lower()
                    g_pos = match.group(2).lower()
                    
                    problem_details = []
                    if g_feat not in entry_feat_abbrs:
                        problem_details.append("    - gloss feature '{}' not in entry features {}".format(g_feat, ", ".join(sorted(list(entry_feat_abbrs)))))
                    if target_pos_abbr and g_pos != target_pos_abbr:
                        problem_details.append("    - gloss POS extension '{}' does not match target POS '{}'".format(g_pos, target_pos_abbr))
                    
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
            for m_feat in sorted(list(master_features)):
                if m_feat not in found_features:
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
