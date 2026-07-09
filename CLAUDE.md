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
