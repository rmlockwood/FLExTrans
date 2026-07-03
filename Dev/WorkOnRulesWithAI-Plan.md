# Plan — "Work on Rules with AI" module

A FLExTrans module that uses an AI provider (Anthropic Claude by default, with Google Gemini selectable) to **create a new Apertium transfer rule** or **modify an existing one** in the project's
`transfer_rules.t1x`, with human review and approval before anything is written.

This document is a plan for review. Nothing is built yet, and per project convention no feature code is committed until Ron OKs it.

---

## 1. Scope

**v1 (this plan): direct-XML only.**
- The AI provider generates Apertium `<rule>` XML directly (plus any supporting `<def-cat>`/`<def-attr>`/`<def-var>`/`<def-macro>` it needs). Apertium is open-source and well represented in training
  data, so the model already knows the format; we ground it with the project's real categories/features and the house conventions.
- Two operations: **modify an existing rule** (rule picker) or **create a new rule**. Both driven by a free-text description box.
- Every candidate rule is validated before the user sees it, previewed in a styled read-only view (never as raw markup), and only written on explicit approval, with a file backup.

**Deliberately out of scope for v1:**
- The RuleGenerator hybrid (routing agreement-type requests through the existing structured path in `CreateApertiumRules.py`).
- Conversational / multi-turn refinement.
- Auto-apply. Rules are always human-approved.
- Org-sponsored credits / backend proxy (see §3).

**Later phases:**
- Hybrid: detect requests that fit the Rule Assistant (e.g. phrase agreement) and route them through `RuleGenerator`; fall back to direct-XML for logic beyond RA's capabilities.
- Org proxy for sponsored credits; multi-turn refine-in-place; batch/multiple rules; diff highlighting in the preview if not done in v1.

---

## 2. What this leans on (already in the codebase)

- **`Dev/Lib/CreateApertiumRules.py`** — `RuleGenerator` already loads an existing `.t1x`, tracks used IDs, creates definitions, inserts `<rule>` elements at the right spot, renames on collision, and
  writes back with a DOCTYPE referencing `transfer.dtd`. Reuse its `ProcessExistingTransferFile` XML-with-comments parse for reading the current rules.
- **`Dev/Modules/RuleAssistant.py`** — `GetStartData` / `GetRuleAssistantStartData` already extract every POS, feature, feature-value, and affix from both FLEx projects. This is the grounding data the
  AI needs to use real categories/tags.
- **Module skeleton** — `FlexToolsModuleClass(runFunction, docs)`, `MainFunction(DB, report)`, `ReadConfig`, translations, `Mixpanel` logging.
- **`Dev/Lib/Mixpanel.py`** — models the one-time opt-in/consent pattern for sending data to an external service. Reuse that pattern for AI consent.
- **`QWebEngineView`** — already used in `Dev/Lib/RuleAssistantMainWindow.py` (import at line 81), so the dependency for a high-fidelity preview is already in the bundle.
- **Validation tools** — `transfer.dtd` (the DOCTYPE `CreateApertiumRules` writes) and `apertium-preprocess-transfer` (already used in the test harness,
  `Dev/TestRuleAssistant/test_rule_assistant.py:102`).
- **`transfer.css`** — the XXE display stylesheet at `Installer/InstallerResources/XXEaddon/ApertiumTransferXMLmind/css/transfer.css`. Its palette and labels are the spec for our preview reskin (see
  §7). Note it cannot be used verbatim outside XXE — it relies on XMLmind CSS extensions (`text-field()`, `combo-box()`, `collapser()`, etc.) that Chromium ignores.

---

## 3. API key / credits model

The engine is **pluggable** (a small provider layer in `AIRules.py`). **Anthropic Claude** (`claude-opus-4-8`) is the default; **Google Gemini** (`gemini-2.5-flash`) is selectable, and other providers
can be added by implementing `makeClient()` + `generate()` and registering them. Selection is a config setting (`AIRulesProvider`); each provider knows its own env var(s) and default model. Every
provider's API is key-based; the request bills to the account that owns the key. Options:

1. **Bring-your-own-key (BYOK)** — each user supplies their own key for the chosen provider (Anthropic Console, or Google AI Studio which has a **free tier** — the answer to the earlier "can users get
   free usage" question, and a reason to keep Gemini easy to switch to). Zero cost/liability for SIL, scales, no infrastructure; downside is signup friction.
2. **Org-sponsored via a proxy** — SIL holds the key behind an SIL-hosted proxy that meters per-user usage and enforces quotas. Users need no account, but a shared key **cannot** be shipped in the
   desktop app (trivially extractable/abusable), so this requires building and operating a backend plus SIL absorbing usage cost.
3. **Per-user keys with limits** — feasible for a small known pilot group, not for public distribution.

**v1 decision: BYOK**, with the key sourced per-provider by a single resolver:

```
resolveApiKey(provider):  provider env var(s)  →  config AIRulesApiKey  →  None (prompt user)
      anthropic → ANTHROPIC_API_KEY      gemini → GEMINI_API_KEY / GOOGLE_API_KEY
```

Keeping key resolution and client construction behind the provider layer means a future org-proxy is a drop-in (point the client at the proxy and swap the auth) without touching the rest of the
module.

---

## 4. Files (new / changed)

| File | Purpose |
|---|---|
| `Dev/Modules/WorkOnRulesWithAI.py` | Module entry: `docs`, `FlexToolsModuleClass`, `MainFunction(DB, report)`, consent gate, orchestration. |
| `Dev/Lib/AIRules.py` | Pluggable provider layer (Anthropic default, Gemini selectable), prompt assembly, validation-retry loop, key resolution. No Qt. |
| `Dev/Lib/TransferPreview.py` | XML→HTML renderer (element→div, displayed attributes→colored spans) + before/after diff-marking; inlines `transfer_preview.css`. No raw markup ever shown to the user. |
| `Dev/Lib/Windows/transfer_preview.css` | Standard-CSS reskin of `transfer.css` (palette / `:before` labels / indentation), static and read-only. |
| `Dev/Lib/Windows/WorkOnRulesWithAI.ui` (+ generated `.py`) | Dialog layout: mode toggle, rule-picker list, description box, preview area, buttons. |
| `Dev/Lib/Windows/WorkOnRulesWithAIDlg.py` | Hand-written dialog logic wrapping the pyuic'd `.py`. |
| `translations/*.ts` (de/es/fr) beside each new `.py` | New UI strings; aim for 0 unfinished, compile `.qm`. Crowdin syncs from master. |
| `Dev/Lib/ReadConfig.py` | New config constants, inserted in alphabetical order in the uppercase block. |
| (no menu edit) | FlexTools auto-discovers modules in `Dev/Modules`, so dropping the file in is enough — no `FLExTransMenu.py` change needed. |
| install / requirements | Add the `anthropic` dependency (and `google-genai` if the Gemini provider is used). |

---

## 5. Config keys (ReadConfig, alphabetical)

- `AI_RULES_PROVIDER` — which provider to use: `anthropic` (default) or `gemini`.
- `AI_RULES_API_KEY` — optional; the key itself, or blank to use the provider's env var (`ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` / `GOOGLE_API_KEY`).
- `AI_RULES_MODEL` — optional; overrides the provider's default model.
- `AI_RULES_CONSENT` and `AI_RULES_CONSENT_ASKED` — the consent flag and whether-asked flag, mirroring the Mixpanel opt-in constant pattern, since this sends data externally.
- Provider defaults live in `AIRules.py`: Anthropic → `claude-opus-4-8`, Gemini → `gemini-2.5-flash` (free-tier friendly; Pro needs a paid key).

If any Doc-subfolder `FlexTrans.config` template needs the new setting, update all copies, not just the main one.

---

## 6. Orchestration (`WorkOnRulesWithAI.MainFunction`)

1. `Utils.loadTranslations(...)`, `ReadConfig.readConfig(report)`.
2. `Mixpanel.LogModuleStarted(...)`, matching other modules.
3. Consent gate (one-time opt-in dialog in the Mixpanel style): state clearly what is sent to Google Gemini — rule text, categories, feature/affix data — and let the user opt out.
4. Resolve the API key (§3). If missing, show a dialog explaining BYOK with a link to Google AI Studio, then abort cleanly.
5. Get the `TRANSFER_RULES_FILE` path; open the target project (`Utils.openTargetProject`).
6. Parse existing rules (reuse `CreateApertiumRules.ProcessExistingTransferFile` parsing) → list of `(comment, element)` for the picker, plus the existing def-cat / def-attr / def-var / def-macro
   names.
7. Gather project grounding via `RuleAssistant.GetStartData` (POS, features, values, affixes) for source and target.
8. Launch the dialog. On Approve, write the file with a `shutil` backup (same pattern `CreateApertiumRules` uses). Optionally offer to launch the Live Rule Tester (`LiveRuleTesterTool`).

---

## 7. Preview & comparison (§ key: no raw markup shown)

**Rendering pipeline (all internal):** `rule XML → HTML transform → QWebEngineView`. The generated HTML and the raw XML are never displayed as text anywhere in the FLExTrans UI. The only place a user
sees markup is inside XXE, via the "Open in XXE" button.

- **`TransferPreview.py`** transforms the rule XML to HTML: each Apertium element → a `<div class="…">`; each displayed attribute → a colored `<span>` (e.g. `clip` → `item: [1]  side: [tl]  part:
  [a_gender]`). It mirrors the display mapping that `transfer.css` already documents, so that CSS is effectively the spec.
- **`transfer_preview.css`** is a standard-CSS reskin authored from `transfer.css`: same palette (wheat / lightpink / paleblue / etc.), same `:before` label text, same indentation; static and
  read-only (no collapsers or editable widgets). It is **inlined** into the generated HTML's `<style>` so there is no base-URL / asset-loading problem in `QWebEngineView`.

**Create new rule:** one `QWebEngineView` showing the single generated rule, rendered.

**Modify existing rule:** **side-by-side before/after** — two `QWebEngineView` panes, left = current rule rendered, right = AI-modified rule rendered, styled identically. No text diff and no markup
shown.
- *Enhancement (attempt in v1):* the transform walks both trees, tags changed / added / removed elements with a CSS class, and tints them in the rendered panes so the user sees what changed at a
  glance, still fully styled. If tree-diffing proves fiddly, v1 falls back to plain side-by-side and highlighting is added later.

**Buttons:** **Approve** (writes, with backup) / **Cancel** (discards) / **Open in XXE** (writes the candidate — or the full updated file — to disk and points the user to open it in XXE for
full-fidelity, editable review).

---

## 8. Provider layer (`AIRules.py`)

A provider abstraction keeps the rest of the module provider-agnostic. Each provider implements `makeClient(apiKey)` and `generate(client, model, systemInstruction, userContent) → (rule_xml, new_defs,
explanation)`, and is registered in `PROVIDERS`. `buildEngine(providerName, apiKey, model)` returns an `Engine` (provider + client + model) that flows through `generateRule` / `generateValidatedRule`.
SDKs are imported lazily inside each provider, so only the selected provider's SDK must be installed.

- **Anthropic (default):** `anthropic`, `client.messages.create(model="claude-opus-4-8", …)`, **forced tool use** (`tool_choice` → the `submit_rule` tool) for structured output, adaptive thinking, and
  the system instruction wrapped in a `cache_control` block for prompt caching. Handles `stop_reason == "refusal"`.
- **Gemini:** `google-genai`, `client.models.generate_content(model="gemini-2.5-flash", …)`, **structured output** (`response_mime_type="application/json"` + `response_schema=RULE_SCHEMA`),
  `json.loads` the response. Guards a blocked/empty response (surfacing `prompt_feedback`).
- **Shared:** both return the same `(rule_xml, new_defs, explanation)` tuple.
- **System instruction:** the "how we write Apertium rules" conventions doc + one or two real sample rules from the file, concatenated by `buildSystemInstruction`. The `transfer.dtd` is deliberately
  NOT included — the model already knows the Apertium format, so it was ~5k low-value tokens (and counts against Gemini free-tier input quotas); the validation-retry loop is the authoritative check.
  The prefix is identical across requests (Anthropic caches it via the breakpoint; Gemini 2.5 reuses it via implicit caching).
- **Per-request content:** the project's real categories/features/tags, the existing definition *names* (so it reuses `a_gender_feature` etc. rather than inventing), the current rule XML when
  modifying, and the user's description.
- `max_tokens` / `max_output_tokens` ~16000; non-streaming is fine for a single rule.

### 8a. Adding a new AI provider

The rest of the module (dialog, validation loop, preview, config, key handling, rate-limit UI) is provider-agnostic — everything flows through the `Engine` — so adding a provider is small. You
touch two places in `AIRules.py` (plus optionally requirements/config), and nothing else changes.

1. **Write a provider class** with these class attributes and two methods (model on `AnthropicProvider` / `GeminiProvider`):
   - `name` — the value users put in the `AIRulesProvider` config setting (e.g. `'openai'`).
   - `displayName` — shown in the consent dialog and error messages (e.g. `'OpenAI'`).
   - `defaultModel` — used when `AIRulesModel` isn't set.
   - `envVars` — a tuple of env var name(s) `resolveApiKey` checks (e.g. `('OPENAI_API_KEY',)`).
   - `keyUrl` — where to get a key; shown in the "no key" dialog.
   - `makeClient(self, apiKey)` — **import the SDK lazily inside this method** (so only the selected provider's SDK must be installed) and return the client.
   - `generate(self, client, model, systemInstruction, userContent)` — call the API and **return exactly the tuple `(rule_xml: str, new_defs: list[str], explanation: str)`**. Use whatever the SDK
     offers for structured output: a forced tool/function call (like Anthropic) or JSON-schema mode (like Gemini). Parse the response and return.

   ```python
   class MyProvider:
       name = 'myprovider'
       displayName = 'My Provider'
       defaultModel = 'some-model-id'
       envVars = ('MYPROVIDER_API_KEY',)
       keyUrl = 'https://.../keys'

       def makeClient(self, apiKey):
           import myprovider_sdk                     # lazy import
           return myprovider_sdk.Client(api_key=apiKey)

       def generate(self, client, model, systemInstruction, userContent):
           # ...call the API for structured output...
           return rule_xml, new_defs, explanation    # (str, list[str], str)
   ```

2. **Register it** in the `PROVIDERS` dict (the only other change):
   ```python
   PROVIDERS = {
       AnthropicProvider.name: AnthropicProvider(),
       GeminiProvider.name: GeminiProvider(),
       MyProvider.name: MyProvider(),                # ← add this line
   }
   ```

**Two behaviours `generate()` should preserve** so the new provider acts like the others:
- On **HTTP 429**, `raise RateLimitError(self.displayName, retryAfterSeconds_or_None)` — the dialog then shows the clean "try again in N s" message instead of a raw dump.
- On a **blocked / empty / refused** response, `raise RuntimeError(...)` with a readable message (the dialog surfaces it via the "failed" path).

**Outside `AIRules.py`:** add the SDK to `requirements.txt` (both copies; can be optional/documented since imports are lazy). No config or conventions-doc changes are needed — `AIRulesProvider`, `AIRulesModel`,
and `AIRulesApiKey` already work generically, and the system instruction is provider-independent.

---

## 9. Validation-retry loop (the safety net)

```
for attempt in range(3):
    candidate = engine.generate(...)      # rule_xml + new_defs
    splice into a temp copy of the .t1x   # defs into correct sections, rule into <section-rules>
    ok, errors = validate(temp_file)
    if ok:
        return candidate
    add errors to the next prompt          # "your rule failed validation: <errors>; fix it"
return last candidate + surface errors to the user
```

`validate()`:
1. `elementtree` parse of the temp file to check well-formed xml.
2. Run `apertium-preprocess-transfer` on the temp copy (real compile check), capture stderr.

Both must pass. This is what makes direct-XML generation trustworthy.

---

## 10. Conventions to honor (from CLAUDE.md)

- **camelCase** for new functions/variables.
- Version-history header block at the top of each new module/lib file. New module's `FTM_Version` must be ≥ the value in `Dev/TopLevel/Version.py` (currently **3.16**), so start at `3.16`. Keep the
  header version and `FTM_Version` in sync.
- Import grouping: stdlib / PyQt / flextoolslib+flexlibs+SIL.LCModel / project.
- Blank-line "breathe" rules; comment liberally; ~200-char lines; keep function calls/signatures on one line.
- New user-facing strings go through `QCoreApplication.translate`; add to the base `.ts`, translate de/es/fr, compile `.qm`.
- Never hand-edit pyuic-generated `.py` files.

---

## 11. Risks

- **Privacy:** FLExTrans serves minority/endangered-language communities. The consent copy must state exactly what is sent (rule text + POS/feature/affix data — not the full lexicon unless we
  deliberately include glosses).
- **Non-determinism:** rules are always human-reviewed and validated; never auto-applied.
- **Cost:** low per rule with caching; surface it if credits are ever sponsored.
- **Dependency:** adds `anthropic` (and optionally `google-genai` for the Gemini provider) to the install/bundle — confirm acceptable.

---

## 12. First concrete artifacts to draft next

1. **`transfer_preview.css`** — the standard-CSS reskin mapped from `transfer.css` (palette + labels + indentation).
2. **The "how we write Apertium rules" conventions doc** — the cached system-prompt content that most determines output quality and is not derivable from code.

---

## 13. Future: "Modify one or more rules" (batch mode)

Not built. A design to revisit — a third mode that applies one change across several rules at once (e.g. a spelling/tag/attribute rename, or refactoring common logic into a shared macro). Open design
decisions (rule-selection mechanism, whether macro-extraction is in the first cut) are deliberately left open for when this is picked up.

**Third mode.** A "Modify one or more rules" radio alongside Create / Modify.

**Rule selection** (candidate mechanisms):
- **Manual multi-select** — the rule picker becomes multi-select. Most reliable.
- **All rules** — a checkbox targeting the whole `section-rules` (global edits).
- **Assisted scope** — user describes the change; we `grep` the rule bodies for the affected token to propose a candidate set the user confirms. Cheap, safe as a filter; the model + validation refine
  it.

**Context sent to the model.** The full XML of every in-scope rule (single-rule modify sends only one body). This is the scale concern: "all rules" on a large file (e.g. fa-bcc ~12k lines) is tens of
thousands of tokens — feasible on large-context models but slow/costly, so keep scope tight via selection.

**Structured output** — a batch instead of one rule:
```
{
  "changed_rules": [ { "target_comment": "<existing rule name>", "rule_xml": "<full new <rule>>" }, ... ],
  "new_defs":      [ "<def-macro …>", "<def-attr …>", ... ],   // e.g. an extracted macro
  "explanation":   "…"
}
```
`target_comment` locates the existing rule each edit replaces (the new `rule_xml` may carry a renamed comment). Macro-refactor: the shared macro goes in `new_defs` and each affected rule is rewritten
to `<call-macro>` in `changed_rules`.

**Validation** — batched: splice all `new_defs` + all `changed_rules` into one temp copy (`spliceManyIntoTemp`), run DTD + `apertium-preprocess-transfer` once, feed errors back, retry. Many rewritten
rules can exceed the 16k output cap, so batch mode needs a higher `max_tokens` and probably streaming.

**Preview** (no raw markup) — one scrollable `QWebEngineView` document with a section per changed rule (before/after via `renderComparisonHtml`), the new definitions rendered as additions, and a
header summary ("7 rules changed, 1 macro added").

**Apply** — `applyRules`: one timestamped backup, insert `new_defs` before their section closes, then surgically regex-replace each rule by `target_comment` (the single-rule mechanism in a loop). Each
changed rule gets the "modified by the AI Assistant on …" provenance comment.

**Guardrails** — big blast radius: show every change in the preview, surface the count before applying, rely on the single backup for revert, keep everything human-approved.

**Phasing** — Phase 1: manual multi-select (+ "all rules"), uniform edits and macro extraction, batched validate/preview/apply. Phase 2: assisted grep-scoping. Phase 3: deletion/rename of shared
definitions.
