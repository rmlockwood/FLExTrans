# CLAUDE.md — Coding guidance for FLExTrans

Guidance for working in this repo. Keep changes consistent with the surrounding
code; match the conventions below rather than introducing new patterns.

## Readability is the top priority
Readable, maintainable code matters more than compactness. Maintainability is a
high priority — follow these rules even when they make the code longer.

### Blank lines (breathe around blocks)
Surround blocks of code with blank lines so they're easy to scan. See
`Dev/Lib/InterlinData.py` lines 170–193 for the canonical example.
- Blank line **after** a `def` or `class` line.
- **Condition-bearing headers** (`if`/`elif`/`for`/`while`, and `except <Type>...`
  that names something) get a blank line **before and after** the header line. The
  continuation forms `elif` and `except <Type>` get the before-blank too — it ends
  the preceding block.
- **Keyword-only headers** (`else`/`try`/`finally`, and bare `except:`) get **no**
  blank line after them (they hug their body). `else`/`finally` also have no blank
  line before them (they hug the preceding block).
- Blank line **before** and **after** a block. (If the block is preceded by a
  comment, the blank line goes before the comment, not between the comment and the
  statement.)
- A statement that **dedents** out of a block gets a blank line before it — e.g. a
  `return` after an `if`/`for` body, or two consecutive `return`s at different
  indent levels, must have a blank line between them.
- Blank line **before every comment.**
- **Never two blank lines in a row** anywhere — use a single blank line to separate
  blocks, functions, and classes (not the PEP 8 double blank).
- Never modify pyuic-generated `.py` files (they're regenerated from `.ui`); these
  formatting rules don't apply to them.

### Naming
- Use **camelCase** for variables and functions (e.g. `ruleAssistantFile`,
  `getFeatureData`), not snake_case.
- This applies to **new code**. Leave existing snake_case alone (the Rule Assistant
  port uses it heavily) unless Ron explicitly asks to refactor a file.

### Imports
Group imports into these blocks, in this order, separated by a single blank line:
1. Standard Python library imports.
2. PyQt imports.
3. `flextoolslib` / `flexlibs` (and SIL.LCModel) imports.
4. Imports from within this project.

### Comments
- Use comments **liberally** — they're a maintainability investment, not clutter.
  Explain what a block does and why, not just tricky lines.

### Line length
- **No 80-character limit.** Lines may run up to ~200 characters before wrapping.
  This applies to **comments too** — don't wrap a comment at 80; let it run to ~200.
- **Multi-line comments should fill the width.** When a comment spans more than one
  line, make each line run close to the ~200 char limit rather than wrapping early.
  If it's only two lines and the total is a bit over 200, split it roughly in half so
  the two lines are balanced rather than one full line and one short stub. Always
  break at a point that makes sense linguistically (e.g. between clauses or
  sentences, not mid-phrase) so each line still reads naturally.
- **Keep function calls / signatures on one line** even if long. Do not split
  arguments across multiple lines — single-line calls are faster to step through
  in a debugger.

### Other
- Match the style of the file you're editing (indentation, naming, import order).
  Don't reformat code you aren't changing.
- When adding a setting-name constant to the block of uppercase config variables
  in `Dev/Lib/ReadConfig.py`, insert it in **alphabetical order** by variable name
  (e.g. `LOG_STATISTICS` sorts before `LOWERCASE_UPPERCASE_PAIRS`).

## Widgets belong in the `.ui` file
- **Never build a widget in Python when the window has a `.ui`.** Add it in the `.ui` (Qt Designer, or by hand in the XML), regenerate the companion `.py`, and reach the widget through
  `self.ui.<objectName>`. Creating widgets in code — `QPushButton(...)` plus `layout.insertWidget(...)` — splits one window's layout across two files, so the next person cannot see the real
  window in a designer and cannot rearrange it without reading the Python. `Dev/Lib/WorkOnRulesWithAIDlg.py` with `Dev/Lib/Windows/WorkOnRulesWithAIWindow.ui` is the pattern to follow.
- **Regenerate with the same tool and version** that produced the file's header (`pyuic6 <name>.ui -o <name>.py` from the folder holding the `.ui`), so the diff shows only your change. Don't
  hand-edit the generated `.py` — see **Blank lines** above.
- **Set only run-time text in code.** Static labels, button captions, tooltips, placeholder text, `editable`, size policies and the like are `.ui` properties. Python sets what depends on a value
  only known at run time, e.g. `self.ui.providerLabel.setText(_translate(...).format(provider=...))`.
- **Translations follow the file the string lives in.** A caption moved into the `.ui` is extracted from the generated `.py`, so its entry moves from `translations/<Dialog>.ts` to the generated
  window's `<Window>.ts` (e.g. `Dev/Lib/Windows/translations/WorkOnRulesWithAIWindow_de.ts`). Delete the entry from the file it left, add it to the one it joined, and recompile both `.qm`s.
  Because pyuic uses the top-level widget's object name as the Qt context, both files usually share one context and merge at run time.

## File description blocks
- Below the version history, every module/lib file should carry a **description block**: `#` comment lines explaining what the file is for and how it hangs together, so someone opening it cold
  doesn't have to reverse-engineer it. `Dev/Modules/LinkSenseTool.py` is the canonical example; `Dev/Lib/Testbed.py`, `Dev/Lib/AIRules.py` and `Dev/Modules/StartTestbed.py` are others.
- **Shape.** An `OVERVIEW (AI generated, then edited)` heading, a blank `#` line, then a paragraph or two saying what the file does and why it exists. After that, as many sections as the file
  actually needs, each under a short all-caps heading — `WHAT IT WRITES`, `COLOR CODING`, `OBJECTS`, `THE TWO FILES`, and so on. Don't force a fixed set of headings; pick the ones that answer the
  questions this particular file raises. Finish with a `CODE STRUCTURE` section that names the main classes and functions in the order they appear and says what calls what. Close the block with a
  bare `#` line, then a blank line, then the imports.
- **Write for someone who has never seen the file.** Explain the why and the shape of things — what a class models, why two files are involved, what invariant a check is protecting — not a
  paraphrase of the code. Mention the traps: the thing that looks redundant but isn't, the ordering that matters, the case that would silently corrupt data if it were done differently.
- **When to write one.** In the course of fixing a bug or adding a feature, if the file you touched has no description block, write one. Older files often carry a one- or two-line stub description
  at the end of the version history instead; replace that stub with a real block rather than leaving both.
- **When to modify one.** If your change makes something in the block wrong or out of date, fix that part in the same edit — a stale description is worse than none. If the block is already good and
  still accurate, leave it alone; it doesn't need rewriting just because you edited the file.
- The `~200` character line-length rule applies to these blocks too, and multi-line paragraphs should fill that width (see **Line length** above).
- Not for pyuic-generated `.py` files.
- A description-only change still gets a version-history line (see **Versioning** below); `Added the code description block at the top with an overview, <the other sections> and code structure.` is
  the usual description, or `Updated the code description block ...` when revising one.

## Lint pass before finalizing
- **Before calling a code change done, make a lint pass over it.** "Lint" here means the editor's type checker (Pylance/Pyright) — there is no linter config or CI lint step in the repo, so the
  warnings to clear are the ones VS Code shows on the file. Report what you found and fixed; if you can't run a checker, say so rather than claiming the file is clean.
- **Scope the pass to the code you touched**, plus anything your change made newly warn. Cleaning up a whole file's pre-existing warnings is worthwhile but is its own change — ask before folding
  it in, so the diff stays reviewable.
- **Fix the warning without changing behavior.** The common ones are `None`-safety on XML lookups (`find()` returns `Optional`) and on Qt getters the stubs type as `Optional` (`header()`,
  `layout()`). Prefer a real guard that returns or errors when the value genuinely can be `None`; use an `assert` only where it can't be, and add a comment saying why. See
  `Dev/Modules/ExportFlexToParatext.py` for the established pattern of commenting a narrowing or a cast.
- Don't silence warnings with a blanket `# type: ignore`. The existing ones on `SIL.LCModel` and `flextoolslib` imports are deliberate — those packages ship no stubs — but a new one needs a reason
  in a comment.
- A lint-only change still gets a version-history line (see below); `Lint fixes.` is the usual description.

## Versioning
- Each module/lib file starts with a version-history header block:
  `# Version X.Y.Z - M/D/YY - Ron Lockwood` followed by an indented one-line
  description.
- **When you change a file, add a new history line** at the top of the block:
  bump the version (usually a patch bump, e.g. `3.16` → `3.16.1`), use today's
  date, and keep the description to a single brief line. Ron will correct the
  version number if needed.
- **The new version must be at least as high as `Version` in
  `Dev/TopLevel/Version.py`.** Check that file first. If the file's current
  header is below it (e.g. file at `3.15.3` while `Version.py` is `3.16`), bump
  straight to the `Version.py` value (`3.16`) rather than doing a patch bump
  from the old header (`3.15.4`).
- **When the file is a module with an `FTM_Version` value in its `docs`
  dictionary, bump that value to match the new header version too.** The header
  version and `FTM_Version` should stay in sync.
- **When the change fixes a GitHub issue, start the new header's description with
  `Fixes #NNNN.`** (the issue number), then the one-line description of the fix.

## Translations (Qt .ts → .qm pipeline)
- A `.ts` lives in a `translations/` folder beside the `.py` whose strings it
  holds, and is named after that `.py` (e.g. `Dev/Lib/translations/RAutils_de.ts`).
- User-facing strings go through `QCoreApplication.translate("<Context>", "...")`.
  The Qt context is independent of the filename; contexts with the same name merge
  across loaded `.qm` files at runtime.
- English source strings for Rule Assistant UI originate from
  `Dev/RuleGen_{en,de,es,fr}.properties`. Pull translations from there.
- Compile with `lrelease <file>.ts -qm CompiledTranslations/<file>_<lang>.qm`.
- Add new strings to all of `_de`, `_es`, `_fr`; aim for 0 unfinished.
- The authoritative UI-language list is `Dev/Lib/UILanguages.py`. `Dev/lang_codes.bat`,
  `LangForInstallerScript/languages.nsh`, and `crowdin.yml` are GENERATED from it by
  `Dev/updateLanguageFiles.py` — never edit those three by hand. To add a UI language,
  follow `Dev/README-AddingUILanguage.md`.
