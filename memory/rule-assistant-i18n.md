---
name: rule-assistant-i18n
description: How Rule Assistant UI translation works (context name, properties->ts->qm pipeline)
metadata:
  type: project
---

The Python Rule Assistant windows (`Dev/Lib/Windows/RuleAssistantWindow.py`,
`CategoryChooser.py`, `FeatureValueChooser.py`, `DisjointFeaturesEditor.py`) and the
model strings in `Dev/Lib/RAutils.py` are all localized under the single Qt context
**`RuleAssistantLib`** via `QCoreApplication.translate("RuleAssistantLib", ...)`.
`RuleAssistantPy.py`'s own module strings use a separate context `RuleAssistant`.
`loadTranslations(librariesToTranslate + ['RuleAssistant'])` loads both
`RuleAssistantLib_<lang>.qm` and `RuleAssistant_<lang>.qm` at runtime.

**Why:** translations weren't showing (issue #1345) because the window code never
called `_translate`; the strings were hardcoded.

**How to apply / regenerate:** UI strings originate from the Java ftrulegen repo
(see [[rule-assistant-origin-repos]]) as `Dev/RuleGen_{en,de,es,fr}.properties`
(issue #1360 = update to the latest of these). Do NOT use pylupdate for
RuleAssistantLib — it can't pull the localized text out of the .properties and would
orphan existing translations. Instead:
1. Edit/refresh `Dev/RuleGen_*.properties` (English value = the literal source string
   passed to `_translate`).
2. Run `python Dev/Modules/RuleGenPropsToTS.py` → regenerates
   `Dev/Modules/translations/RuleAssistantLib_{de,es,fr}.ts` (+ base `.ts`), keyed by
   property name, deduped by English source, with `\n` converted to real newlines.
3. Compile to `.qm` (`lrelease`, e.g. `Dev/Modules/local_lreal.bat RuleAssistantLib`)
   and deploy to the runtime `FTPaths.TRANSL_DIR`
   (`<ROOT>/FlexTools/Modules/FLExTrans/translations`). `compile_transl.bat` will NOT
   auto-build it because there is no `RuleAssistantLib.py`.
