# FLExTrans — Developer Onboarding

Welcome! This guide gets you from a fresh machine to running and debugging FLExTrans
from source in VSCode. It assumes you use **GitHub** and **VSCode**, and that you open
the `GitHub\FLExTrans` folder as your workspace.

> The original, prose onboarding doc lives here (request access if needed):
> https://docs.google.com/document/d/1t7_JL3rWsA7oHGPMgTKjmVfu8lXFnGk-aWGD6cRPp-o/edit
> This file is the quick, repo-local version of the same material.

---

## 1. What FLExTrans is (and how the pieces fit)

FLExTrans is linguist-friendly machine translation built on **FLEx** (FieldWorks
Language Explorer), **Apertium**, **STAMP**, and **HermitCrab**. The code in this repo
is a set of **FlexTools modules** — it does not run standalone; it runs inside a
**FlexTools deployment**.

Key idea you must understand before anything else:

- **`GitHub\FLExTrans\Dev\`** holds the *source code* (what you edit).
- A separate **deployment folder** (created by the installer) holds a *working
  FlexTools install* with folders like `FlexTools`, `WorkProjects`, etc.
- You develop by making the deployment's Python files **point back at your repo
  source** — either via **symbolic links** (`create_links.bat`) or by **copying**
  files in before each debug run (a VSCode task). You then launch/debug the
  deployment, but your breakpoints land in the repo source.

```
GitHub\FLExTrans\Dev\           <-- you edit here
  Lib\ , Lib\Windows\ , Modules\ , TopLevel\ , CompiledTranslations\
        |  (symlinks or copy)
        v
<deployment>\FlexTools\        <-- runs here (FLExTrans.py is the entry point)
  Modules\FLExTrans\ , Modules\FLExTrans\Lib\ , ...
```

---

## 2. Prerequisites

Install these first:

1. **FieldWorks (FLEx)** — FLExTrans integrates with FLEx via `flexlibs`/`flextoolslib`.
   Install Language Explorer and have at least one source and one target project.
2. **A FlexTools/FLExTrans deployment** — run the FLExTrans **installer** once to get a
   complete, working install (FlexTools host, Apertium binaries, sample projects). This
   is the "deployment folder" you'll later link your source into. (Build the installer
   from `Installer\CreateInstaller.bat`, or use an existing released installer.)
3. **Python 3.13** (64-bit). Match the version FlexTools ships with.
   - Note: `wildebeest-nlp` does not work on 3.13 — it's intentionally left out.
4. **Git** and a **GitHub** account (with access to this repo).
5. **VSCode** with these extensions:
   - **Python** (ms-python.python) + **Pylance**
   - **Python Debugger** (`debugpy`)
   - **GitHub Copilot** and **GitHub Copilot Chat** (see §10)

---

## 3. Clone the repo

```powershell
cd C:\Users\<you>\GitHub
git clone https://github.com/rmlockwood/FLExTrans.git
code FLExTrans
```

Open the `FLExTrans` folder in VSCode. The committed `.vscode\settings.json` already
adds the source folders to Pylance's analysis path, so imports resolve in the editor.

---

## 4. Python environment & dependencies

Create a virtual environment in the repo and install the runtime dependencies. The
canonical list lives in `Installer\InstallerResources\requirements.txt`:

```powershell
cd C:\Users\<you>\GitHub\FLExTrans
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r Installer\InstallerResources\requirements.txt
```

Current runtime dependencies:

```
flextoolslib==2026.5.4
fuzzywuzzy
Levenshtein
mixpanel
PyQt6==6.10.2
PyQt6-WebEngine==6.10.0
regex
pygetwindow
tomli_w
```

In VSCode, select this interpreter: **Ctrl+Shift+P → Python: Select Interpreter →
`.venv`**.

---

## 5. Install `pyside6-designer` (for editing the `.ui` files)

The Rule Assistant and other windows are laid out in Qt Designer `.ui` files. We
**edit** them with Qt Designer (shipped with PySide6) but the app **runs** on PyQt6, and
we **compile** `.ui → .py` with PyQt6's `pyuic` (see §8).

Install PySide6 (it provides the `pyside6-designer` launcher):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install PySide6-Essentials      # or full: pip install PySide6
pyside6-designer                               # launches Qt Designer
```

Then open e.g. `Dev\Lib\Windows\RuleAssistantWindow.ui`.

> Tip: PySide6 is only a design-time tool here. If you prefer to keep it out of the
> runtime venv, install it in a separate venv and launch `pyside6-designer` from there.

---

## 6. Link your source into the deployment

You have two ways to make the deployment run your repo code. **Pick one** (symlinks are
the usual choice; the copy approach is built into debug option #2 below).

### 6a. Symbolic links — `Utilities\create_links.bat` (recommended)

This replaces the deployment's `.py`/`.qm` files with **symbolic links** that point back
to `Dev\`. Edit a file in the repo → it's instantly live in the deployment.

1. Open `Utilities\create_links.bat` and set the two paths at the top:
   ```bat
   set git_repo=C:\Users\<you>\GitHub\FLExTrans
   set testing_folder=C:\Users\<you>\Documents\FLExTrans
   ```
   - `git_repo` = this repo (contains `Dev`, `Doc`, …).
   - `testing_folder` = your deployment (contains `FlexTools`, `WorkProjects`, …).
   - **No spaces** in either path, or `mklink` fails.
2. Run it **as Administrator** (right-click → Run as administrator), or enable Windows
   **Developer Mode** (Settings → Privacy & security → For developers) so `mklink` works
   without admin.

What it links (deployment ⟵ repo):

| Deployment folder | ⟵ Repo source |
|---|---|
| `FlexTools\Modules\FLExTrans\` | `Dev\Modules\*.py` |
| `FlexTools\Modules\FLExTrans\Lib\` | `Dev\Lib\*.py` and `Dev\Lib\Windows\*.py` |
| `FlexTools\` | `Dev\TopLevel\*.py` |
| `FlexTools\Modules\FLExTrans\translations\` | `Dev\CompiledTranslations\*.qm` |

The script **deletes existing links in each folder before recreating them**, so re-run
it any time files are added/removed. (For the localized binaries, first create a
`FlexTools\Modules\FLExTrans\translations` folder, then re-run.)

### 6b. Apertium binaries — `Utilities\create_apertium_links.bat`

Links the Apertium/Make executables and DLLs into the deployment's `FlexTools\Tools`
folder from `Installer\InstallerResources\`. Edit the paths at the top to match your
machine, then run as Administrator. Needed for the transfer/synthesis steps.

---

## 7. Debugging in VSCode (`.vscode\launch.json`)

FLExTrans launches as a debugpy program: it runs the deployment's `FLExTrans.py` with a
project's `flextools.ini` as its argument, and `pathMappings` map the deployment files
back to your repo `Dev\` folders so breakpoints work.

Below are the **two distinctive configurations** — adapt the absolute paths to your
machine. Add both to `.vscode\launch.json` under `"configurations"`.

```jsonc
{
  "version": "0.2.0",
  "configurations": [

    // ── Option 1: Debug in the DEPLOYMENT folder (symlink-based) ──────────────
    // Use after running create_links.bat. The deployment's files are links to your
    // repo source, so you edit in GitHub\FLExTrans and just hit F5 — no copy step.
    {
      "name": "Deploy: German-Swedish",
      "type": "debugpy",
      "request": "launch",
      "cwd": "C:/Users/<you>/Documents/FLExTrans/FlexTools",
      "program": "C:/Users/<you>/Documents/FLExTrans/FlexTools/FLExTrans.py",
      "args": ["C:/Users/<you>/Documents/FLExTrans/WorkProjects/German-Swedish/Config/flextools.ini"],
      "pathMappings": [
        { "localRoot": "${workspaceFolder}/Dev/Lib",          "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Lib/Windows",  "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Modules",      "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans" },
        { "localRoot": "${workspaceFolder}/Dev/TopLevel",     "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools" }
      ],
      "console": "integratedTerminal"
    },

    // ── Option 2: Debug in the Documents\FLExTrans folder (copy-based) ─────────
    // No symlinks: a preLaunchTask xcopies your repo source into the deployment
    // right before launch. Handy when you can't use symlinks (no admin / no Dev Mode).
    {
      "name": "Docs: German-Swedish",
      "preLaunchTask": "Copy source files to Docs:German-Swedish",
      "type": "debugpy",
      "request": "launch",
      "cwd": "C:/Users/<you>/Documents/FLExTrans/FlexTools",
      "program": "C:/Users/<you>/Documents/FLExTrans/FlexTools/FLExTrans.py",
      "args": ["C:/Users/<you>/Documents/FLExTrans/WorkProjects/German-Swedish/Config/flextools.ini"],
      "pathMappings": [
        { "localRoot": "${workspaceFolder}/Dev/Lib",         "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Lib/Windows", "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Modules",     "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools/Modules/FLExTrans" },
        { "localRoot": "${workspaceFolder}/Dev/TopLevel",    "remoteRoot": "C:/Users/<you>/Documents/FLExTrans/FlexTools" }
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

The copy task referenced by option 2 lives in `.vscode\tasks.json`. It `xcopy`s
`Dev\Lib`, `Dev\Lib\Windows`, `Dev\Modules`, `Dev\TopLevel` (`.py`) and
`Dev\CompiledTranslations` (`.qm`) into the deployment. Adjust the paths to your machine:

```jsonc
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Copy source files to Docs:German-Swedish",
      "type": "shell",
      "command": "cmd.exe /c \"xcopy \"C:\\Users\\<you>\\GitHub\\FLExTrans\\Dev\\Lib\\*.py\" \"C:\\Users\\<you>\\Documents\\FLExTrans\\FlexTools\\Modules\\FLExTrans\\Lib\" /Y /S /I && xcopy \"C:\\Users\\<you>\\GitHub\\FLExTrans\\Dev\\Lib\\Windows\\*.py\" \"C:\\Users\\<you>\\Documents\\FLExTrans\\FlexTools\\Modules\\FLExTrans\\Lib\\Windows\" /Y /S /I && xcopy \"C:\\Users\\<you>\\GitHub\\FLExTrans\\Dev\\Modules\\*.py\" \"C:\\Users\\<you>\\Documents\\FLExTrans\\FlexTools\\Modules\\FLExTrans\" /Y /S /I && xcopy \"C:\\Users\\<you>\\GitHub\\FLExTrans\\Dev\\TopLevel\\*.py\" \"C:\\Users\\<you>\\Documents\\FLExTrans\\FlexTools\" /Y /S /I && xcopy \"C:\\Users\\<you>\\GitHub\\FLExTrans\\Dev\\CompiledTranslations\\*.qm\" \"C:\\Users\\<you>\\Documents\\FLExTrans\\FlexTools\\Modules\\FLExTrans\\translations\" /Y /S /I\"",
      "problemMatcher": []
    }
  ]
}
```

Press **F5** (or the Run & Debug panel) and pick the configuration. The FLExTrans tool
window opens; breakpoints in `Dev\` will hit.

> **When to use which:** symlinks (option 1) are zero-friction once set up — edit and
> run. The copy approach (option 2) is for when symlinks aren't available; remember it
> only refreshes files at launch via the preLaunchTask.

---

## 8. Editing `.ui` files → compiling to `.py`

1. Edit the `.ui` in `pyside6-designer` (§5).
2. Compile it to Python with PyQt6's `pyuic` via `Dev\Lib\Windows\convert_ui_py.bat`:
   ```powershell
   cd Dev\Lib\Windows
   .\convert_ui_py.bat RuleAssistantWindow      # name without extension
   ```
   (Internally: `py -m PyQt6.uic.pyuic <name>.ui -o <name>.py`.) There's also a VSCode
   task **"Convert active UI to Python"** that runs this on the currently open file.
3. **Never hand-edit the generated `*.py`** (e.g. `RuleAssistantWindow.py`) — your
   changes are lost on the next compile. Edit the `.ui` instead. (See conventions §11.)

---

## 9. Translations, tests, and other workflows

- **Translations (Qt `.ts` → `.qm`):** user-facing strings go through
  `QCoreApplication.translate("<Context>", "...")`. A `.ts` lives in a `translations/`
  folder beside the `.py` whose strings it holds. Compile with
  `lrelease <file>.ts -qm CompiledTranslations/<file>_<lang>.qm`. Batch helpers:
  `Dev\compile_transl.bat`, `Dev\process-compile_transl.bat`. Languages: `de`, `es`,
  `fr` (aim for 0 unfinished).
- **Unit tests:** `Dev\run_unit_tests.bat`; Rule Assistant tests:
  `Dev\TestRuleAssistant\run_tests.bat`.

---

## 10. Using GitHub Copilot

1. Install the **GitHub Copilot** and **GitHub Copilot Chat** extensions, then
   **sign in** (Accounts icon, bottom-left) with a GitHub account that has Copilot.
2. **Inline completions:** start typing; press **Tab** to accept, **Esc** to dismiss,
   **Alt+]/Alt+[** to cycle suggestions.
3. **Copilot Chat:** open with **Ctrl+Alt+I** (or the chat icon). Useful commands:
   - `/explain` — explain the selected code.
   - `/fix` — propose a fix for selected code or a diagnostic.
   - `/tests` — draft tests.
   - `#file` / `#selection` — add context; `@workspace` — ask about the whole repo.
4. **Teach Copilot our conventions:** create `.github/copilot-instructions.md` and paste
   the conventions from §11 (and `CLAUDE.md`). Copilot Chat automatically picks up that
   file so its suggestions match house style (camelCase, blank-line rules, ~200-char
   lines, version-history headers, etc.).
5. **Watch out:** Copilot doesn't know our rules by default — it will suggest
   `snake_case`, PEP 8 double blank lines, and 80-col wrapping. Review against §11.

---

## 11. Coding conventions (from `CLAUDE.md`)

Readable, maintainable code is the top priority — follow these even when they make code
longer. (Full text: `CLAUDE.md` at the repo root.)

**Blank lines (breathe around blocks)** — see `Dev\Lib\InterlinData.py` lines 170–193 for
the canonical example:
- Blank line **after** a `def`/`class` line.
- Condition-bearing headers (`if`/`elif`/`for`/`while`, `except <Type>`) get a blank line
  **before and after**.
- Keyword-only headers (`else`/`try`/`finally`, bare `except:`) get **no** blank line
  after (they hug their body); `else`/`finally` also hug the preceding block.
- A statement that **dedents** out of a block (e.g. a `return` after an `if`/`for`) gets a
  blank line before it.
- Blank line **before every comment**.
- **Never two blank lines in a row** (no PEP 8 double blanks).
- **Never modify pyuic-generated `.py` files** — these formatting rules don't apply to them.

**Naming** — **camelCase** for new variables/functions (`ruleAssistantFile`,
`getFeatureData`), not snake_case. Leave existing snake_case alone unless asked to refactor.

**Imports** — group in this order, separated by one blank line: (1) stdlib, (2) PyQt,
(3) `flextoolslib`/`flexlibs`/`SIL.LCModel`, (4) project imports.

**Comments** — use them liberally; explain what a block does and why.

**Line length** — no 80-char limit; lines (and comments) may run to ~200 chars. Keep
function calls/signatures on **one line** even if long (easier to step through in a
debugger).

**Match the file you're editing** — indentation, naming, import order. Don't reformat
code you aren't changing.

**Versioning** — each module/lib file starts with a version-history header:
`# Version X.Y.Z - M/D/YY - Ron Lockwood` plus a one-line description. **When you change a
file, add a new history line at the top of the block** (usually a patch bump, e.g.
`3.16 → 3.16.1`), today's date, one brief line.

---

## 12. Git workflow

- Branch off `master` for changes; open a PR back into `master`.
- Don't commit machine-specific paths: keep your edited `create_links.bat`,
  `create_apertium_links.bat`, `launch.json`, and `tasks.json` paths local (or use a
  branch you don't merge). `.venv\` should not be committed.

---

## 13. Suggestions / things easy to miss

- **Run the installer first.** You need a real FlexTools deployment before symlinks make
  sense — `create_links.bat` overlays source onto an existing install, it doesn't create
  one.
- **Admin / Developer Mode for `mklink`.** Symlink creation needs elevation or Windows
  Developer Mode. If links silently fail, this is usually why.
- **No spaces in paths** used by the link scripts (a hard requirement).
- **FLEx must be installed and have projects** matching the `flextools.ini` you pass as
  the debug argument; otherwise the tool can't open the source/target databases.
- **Apertium + Make binaries** (`create_apertium_links.bat`) are required for the
  transfer/synthesis pipeline, not just the GUI.
- **Re-run `create_links.bat` when files are added/removed** (it only links files that
  exist at run time, and it clears stale links first).
- **Build the bilingual dictionary** for a project so the Rule Assistant shows test data.
- **Interpreter mismatch** is the most common "it runs but won't debug" cause — confirm
  VSCode is using the `.venv` and that it's Python 3.13.
- **`.qm` files are build artifacts** — after editing a `.ts`, recompile with `lrelease`
  and (for the copy-based debug) make sure the task copies the updated `.qm`.
- **Consider `.github/copilot-instructions.md`** (see §10) so AI assistance respects the
  house style automatically.
