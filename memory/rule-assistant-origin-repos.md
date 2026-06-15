---
name: rule-assistant-origin-repos
description: Where the Rule Assistant (ftrulegen) tool came from before the Python port in FLExTrans
metadata:
  type: reference
---

The Rule Assistant tool's source lineage before it was ported into FLExTrans:

- Original Java/JavaFX version: https://github.com/AndyBlack/ftrulegen
- Re-port work referencing it: https://github.com/MattGyverLee/ftrulegen (branch `re-port`)

That work became the Python/PyQt6 port now in this repo (rmlockwood/FLExTrans):
`Dev/Modules/RuleAssistantPy.py` + `Dev/Lib/RAutils.py` + `Dev/Lib/Windows/`. The
old `Dev/Modules/RuleAssistantLib/` folder from the port was deleted (see
[[rule-assistant-restructure-0597346d]]).
