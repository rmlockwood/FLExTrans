# RuleAssistant Python Port – Change Summary
**Branch:** `claude/investigate-issues-KplqK`  
**Base:** `rule-assistant-python`  
**Date:** 2026-05-01

---

## 1. Directory Cleanup

### Deleted files
| File | Reason |
|------|--------|
| `Dev/Modules/RuleAssistantLib/_window_launcher.py` | Replaced by standard entry in `RuleAssistant.py` |
| `Dev/Modules/RuleAssistantLib/flextrans_integration.py` | Duplicate integration shim; unused |

### Moved / consolidated – model, flexmodel, service → `Dev/Lib/RAutils.py`
All 20+ classes from the three sub-packages were merged into a single file so that the `Dev/Lib/Windows/` view files can import them with a simple `from RAutils import …` (matching the FLExTrans convention for library modules).

Class order in `RAutils.py` (dependency-safe):
1. Constants / enums (`PhraseType`, `HeadValue`, `PermutationsValue`, `ApplicationPreferences`)
2. FLEx metadata (`FLExCategory`, `FLExFeature`, `FLExFeatureValue`, `FLExData`, `FLExDataSource`)
3. Rule constituents (`RuleConstituent`, `Category`, `Feature`, `Affix`, `Phrase`, `Source`, `Target`, `Word`)
4. Disjoint features (`DisjointFeatureValuePairing`, `DisjointFeatureSet`)
5. Top-level rule (`FLExTransRule`, `FLExTransRuleGenerator`)
6. Services (`XMLBackEndProvider`, `XMLFLExDataBackEndProvider`, `RuleIdentifierAndParentSetter`, `ConstituentFinder`, `ValidityChecker`, `WebPageProducer`, `WebPageInteractor`)

### Moved CSS files to `Dev/Lib/`
| Old location | New location |
|---|---|
| `Dev/Modules/RuleAssistantLib/assets/rulegen.css` | `Dev/Lib/rulegen.css` |
| `Dev/Modules/RuleAssistantLib/assets/treeflex.css` | `Dev/Lib/treeflex.css` |

`WebPageProducer` in `RAutils.py` resolves these via `Path(__file__).parent` (i.e. `Dev/Lib/`).

### New view files in `Dev/Lib/Windows/`
Each view was moved from `Dev/Modules/RuleAssistantLib/view/` to `Dev/Lib/Windows/` with a PascalCase name and a matching Qt Designer `.ui` file:

| Old path | New `.py` | New `.ui` |
|---|---|---|
| `view/category_chooser.py` | `Dev/Lib/Windows/CategoryChooser.py` | `Dev/Lib/Windows/CategoryChooser.ui` |
| `view/feature_value_chooser.py` | `Dev/Lib/Windows/FeatureValueChooser.py` | `Dev/Lib/Windows/FeatureValueChooser.ui` |
| `view/disjoint_features_editor.py` | `Dev/Lib/Windows/DisjointFeaturesEditor.py` | `Dev/Lib/Windows/DisjointFeaturesEditor.ui` |
| `view/main_window.py` | `Dev/Lib/Windows/RuleAssistantWindow.py` | `Dev/Lib/Windows/RuleAssistantWindow.ui` |

---

## 2. UI Layout Fix (25% / 75% split)

**File:** `Dev/Lib/Windows/RuleAssistantWindow.py`  
**Also in:** `Dev/Modules/RuleAssistantLib/view/main_window.py`

The vertical splitter between the test-data pane (top) and the rule-tree diagram (bottom) was not being sized, so the top pane consumed most of the window.

**Fix:** after constructing the `QSplitter`, call `setSizes([250, 750])`:
```python
self.v_splitter = QSplitter(Qt.Orientation.Vertical)
# ... add top and bottom widgets ...
self.v_splitter.setSizes([250, 750])   # 25% top / 75% diagram
```

---

## 3. Crash: Right-click → "Add New Rule"

**File:** `Dev/Lib/Windows/RuleAssistantWindow.py`  
**Also in:** `Dev/Modules/RuleAssistantLib/view/main_window.py`

Calling `Source()` and `Target()` without passing a `phrase=` argument caused a `TypeError` because `Phrase` (the default) requires initialisation. 

**Fix:**
```python
# Before (crashes):
new_rule.source = Source()
new_rule.target = Target()

# After:
new_rule.source = Source(phrase=Phrase())
new_rule.target = Target(phrase=Phrase())
```

---

## 4. Disjoint Features Editor – Multiple Fixes

**File:** `Dev/Lib/Windows/DisjointFeaturesEditor.py`  
**Also in:** `Dev/Modules/RuleAssistantLib/view/disjoint_features_editor.py`

Four bugs were fixed:

### 4a. Value combo boxes not populated
`_populate_value_combo()` was not being called when a co-feature was selected.  
**Fix:** Added `_populate_value_combo(combo, co_feature_name)` and called it from `_on_cofeature_changed()` and `_rebuild_pairing_rows()`.

```python
def _populate_value_combo(self, combo: QComboBox, co_feature_name: str) -> None:
    combo.clear()
    if not self.flex_data or not co_feature_name:
        return
    values: set[str] = set()
    for feature in self.flex_data.source_data.features:
        if feature.name == co_feature_name:
            for v in feature.values:
                values.add(v.abbreviation)
    combo.addItems(sorted(values))
```

### 4b. Signal connections used wrong loop index (closure bug)
Lambda slots inside a `for i in range(n)` loop all captured the same final value of `i`.  
**Fix:** Bind `row=i` as a default argument:
```python
feature_combo.currentIndexChanged.connect(
    lambda _idx, row=i: self._on_pairing_feature_changed(row))
value_combo.currentIndexChanged.connect(
    lambda _idx, row=i: self._on_pairing_value_changed(row))
```

### 4c. Changes not saved back to the model
`_on_pairing_feature_changed` and `_on_pairing_value_changed` were not writing back to `self._current_set.pairings`.  
**Fix:** Both handlers now update the relevant `DisjointFeatureValuePairing` fields directly.

### 4d. Slider minimum set to 2 instead of 3
The Java version enforces a minimum of 3 pairings.  
**Fix:**
```python
self.pairing_slider.setMinimum(3)   # was 2
```

---

## 5. i18n – Qt Translation Files

**New files:** `Dev/Modules/translations/RuleAssistantLib.ts` (English template) and `_de.ts`, `_es.ts`, `_fr.ts`

Converted from the existing Java `.properties` files in `Dev/RuleGen_*.properties` using a Python conversion script (latin-1 encoding to handle the `©` character).

**Wired into the loader:**  
`Dev/Modules/RuleAssistant.py` line ~101:
```python
librariesToTranslate = [
    'ReadConfig', 'Utils', 'Mixpanel', 'CreateApertiumRules',
    'TextClasses', 'InterlinData',
    'RuleAssistantLib',   # ← added
]
```

The `.ts` files need to be compiled to `.qm` with `lrelease` before they take effect. The `Utils.loadTranslations()` call in `RuleAssistant.py` will pick them up automatically once compiled.

---

## Summary of files changed

| File | Status |
|------|--------|
| `Dev/Lib/RAutils.py` | **New** – consolidates model + flexmodel + service |
| `Dev/Lib/rulegen.css` | **New** – moved from assets/ |
| `Dev/Lib/treeflex.css` | **New** – moved from assets/ |
| `Dev/Lib/Windows/CategoryChooser.py` | **New** – moved + renamed |
| `Dev/Lib/Windows/CategoryChooser.ui` | **New** |
| `Dev/Lib/Windows/FeatureValueChooser.py` | **New** – moved + renamed |
| `Dev/Lib/Windows/FeatureValueChooser.ui` | **New** |
| `Dev/Lib/Windows/DisjointFeaturesEditor.py` | **New** – moved + renamed + fixed |
| `Dev/Lib/Windows/DisjointFeaturesEditor.ui` | **New** |
| `Dev/Lib/Windows/RuleAssistantWindow.py` | **New** – moved + renamed + fixed |
| `Dev/Lib/Windows/RuleAssistantWindow.ui` | **New** |
| `Dev/Modules/RuleAssistant.py` | **Modified** – added RuleAssistantLib to translation loader |
| `Dev/Modules/RuleAssistantLib/view/main_window.py` | **Modified** – crash fix + layout fix |
| `Dev/Modules/RuleAssistantLib/view/disjoint_features_editor.py` | **Modified** – 4 bug fixes |
| `Dev/Modules/translations/RuleAssistantLib.ts` | **New** |
| `Dev/Modules/translations/RuleAssistantLib_de.ts` | **New** |
| `Dev/Modules/translations/RuleAssistantLib_es.ts` | **New** |
| `Dev/Modules/translations/RuleAssistantLib_fr.ts` | **New** |
| `Dev/Modules/RuleAssistantLib/_window_launcher.py` | **Deleted** |
| `Dev/Modules/RuleAssistantLib/flextrans_integration.py` | **Deleted** |
