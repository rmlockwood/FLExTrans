# FLExTrans — Developer Onboarding

Welcome! This guide gets you from a fresh machine to running and debugging FLExTrans
from source in VSCode. It assumes you will use **GitHub** and **VSCode**, and that you open
the `GitHub\FLExTrans` folder as your workspace.


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
- You develop by pointing the deployment's Python files at your repo source with
  **symbolic links** (`create_links.bat`), then launch/debug the deployment so your
  breakpoints land in the repo source. (One debug setup instead *copies* the files in on
  each run — that's a debug-time choice, see §8, not a different way to link.)

```
GitHub\FLExTrans\Dev\           <-- you edit here
  Lib\ , Lib\Windows\ , Modules\ , TopLevel\ , CompiledTranslations\
        |  (symbolic links, via create_links.bat)
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
   complete, working install (FlexTools host, Python dependencies, Apertium binaries,
   sample projects). This is the "deployment folder" you'll later link your source into.
   Normally you just use a released installer. If you need to *build* the installer
   yourself from this repo, see **Appendix A**.
3. **Python 3.13** (64-bit). Match the version FlexTools ships with (currently 3.13.12).
4. **Git** and a **GitHub** account (with access to this repo).
5. **VSCode** and its extensions — see §3.

---

## 3. Install VSCode and its extensions

### 3a. Install VSCode

1. Download from <https://code.visualstudio.com/> and run the installer.
2. On the *Select Additional Tasks* page, tick **"Add to PATH"** and **"Open with
   Code"** (handy for right-clicking a folder → *Open with Code*).
3. Launch VSCode.

### 3b. Install the extensions

Open the **Extensions** view (the square icon in the left bar, or **Ctrl+Shift+X**),
type each name in the search box, and click **Install**:

- **Python** (publisher: Microsoft, id `ms-python.python`) — also pulls in **Pylance**.
- **Python Debugger** (`ms-python.debugpy`).
- **GitHub Copilot** (`GitHub.copilot`).
- **GitHub Copilot Chat** (`GitHub.copilot-chat`).

Or install them all from the integrated terminal (**Ctrl+`**):

```powershell
code --install-extension ms-python.python
code --install-extension ms-python.debugpy
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

After installing Copilot, click the **Accounts** icon (bottom-left) and **sign in** with
a GitHub account that has Copilot access (see §14).

---

## 4. Clone the repo and open it in VSCode

```powershell
cd C:\Users\<you>\GitHub
git clone https://github.com/rmlockwood/FLExTrans.git
```

Now **open the repo's root folder in VSCode** — do this before any of the steps below:

```powershell
code C:\Users\<you>\GitHub\FLExTrans
```

(or **File → Open Folder…** and choose `GitHub\FLExTrans`). Everything that follows
assumes the **workspace is the repo root**: the committed `.vscode\settings.json`,
`launch.json`, and `tasks.json`, and all the `Dev\...` relative paths, only resolve when
the root folder is open. The settings file already adds the source folders to Pylance's
analysis path, so imports resolve in the editor.

---

## 5. Python dependencies (mostly handled for you)

**You normally don't pip-install anything by hand.** When you install FLExTrans
(Appendix A or a released installer), its `requirements.txt` is installed into the
deployment's Python automatically. The runtime dependencies, listed for reference
(`Installer\InstallerResources\requirements.txt`):

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

For **editor IntelliSense and the debugger**, point VSCode at a Python 3.13 interpreter
that can see these packages — either the deployment's Python, or a local virtual
environment where you've installed the list above:

```powershell
cd C:\Users\<you>\GitHub\FLExTrans
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r Installer\InstallerResources\requirements.txt
```

Select it in VSCode: **Ctrl+Shift+P → Python: Select Interpreter**.

---

## 6. Install `pyside6-designer` (for editing the `.ui` files)

The Rule Assistant and other windows are laid out in Qt Designer `.ui` files. We
**edit** them with Qt Designer (shipped with PySide6) but the app **runs** on PyQt6, and
we **compile** `.ui → .py` with PyQt6's `pyuic` (see §9). PySide6 is only a design-time
tool here and is not part of the FLExTrans runtime dependencies.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install PySide6-Essentials      # or full: pip install PySide6
pyside6-designer                               # launches Qt Designer
```

As an example, try opening `Dev\Lib\Windows\RuleAssistantWindow.ui`.

> Tip: if you'd rather keep PySide6 out of your runtime venv, install it in a separate
> venv and launch `pyside6-designer` from there. Installing PySide6 also gives you
> `pyside6-lupdate`/`pyside6-lrelease`, handy for translations (§10).

---

## 7. Link your source into the deployment

Use **symbolic links** so the deployment runs your repo code: edit a file in the repo and
it's instantly live in the deployment.

### 7a. Symbolic links — `Utilities\create_links.bat`

1. **Copy** `Utilities\create_links.bat` into your deployment at
   `<deployment>\FlexTools\Modules\FLExTrans\`, and edit/run **that copy** — so your
   machine-specific path edits never dirty the version in the repo.
2. Open the copied `create_links.bat` and set the two paths at the top:
   ```bat
   set git_repo=C:\Users\<you>\GitHub\FLExTrans
   set testing_folder=C:\Coding\TestProjects\FLExTrans
   ```
   - `git_repo` = this repo (contains `Dev`, `Doc`, …).
   - `testing_folder` = your deployment (contains `FlexTools`, `WorkProjects`, …).
   - **No spaces** in either path, or `mklink` fails.
3. Run it **as Administrator** (right-click → Run as administrator), or enable Windows
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

### 7b. (Optional) Apertium binaries — `Utilities\create_apertium_links.bat`

Only needed when **testing a newer Apertium version** than the one the installer placed.
It links the Apertium/Make executables and DLLs into the deployment's `FlexTools\Tools`
folder from `Installer\InstallerResources\`. Copy/edit the paths at the top to match your
machine, then run as Administrator. For normal development you can skip this — the
installer already put working binaries in place.

---

## 8. Debugging in VSCode (`.vscode\launch.json`)

FLExTrans launches as a debugpy program: it runs the deployment's `FLExTrans.py` with a
project's `flextools.ini` as its argument, and `pathMappings` map the deployment files
back to your repo `Dev\` folders so breakpoints work.

Below are the **two debug options**. Both run the same way; they differ only in how the
deployment got your latest source. Adapt the absolute paths to your machine and add them
to `.vscode\launch.json` under `"configurations"`.

```jsonc
{
  "version": "0.2.0",
  "configurations": [

    // ── Option 1: Debug in the deployment folder (symlink-based) ──────────────
    // Use after running create_links.bat (§7a). The deployment's files are links to
    // your repo source, so you just edit in GitHub\FLExTrans and hit F5 — no copy step.
    {
      "name": "Deploy: German-Swedish",
      "type": "debugpy",
      "request": "launch",
      "cwd": "C:/Coding/TestProjects/FLExTrans/FlexTools",
      "program": "C:/Coding/TestProjects/FLExTrans/FlexTools/FLExTrans.py",
      "args": ["C:/Coding/TestProjects/FLExTrans/WorkProjects/German-Swedish/Config/flextools.ini"],
      "pathMappings": [
        { "localRoot": "${workspaceFolder}/Dev/Lib",         "remoteRoot": "C:/Coding/TestProjects/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Lib/Windows", "remoteRoot": "C:/Coding/TestProjects/FLExTrans/FlexTools/Modules/FLExTrans/Lib" },
        { "localRoot": "${workspaceFolder}/Dev/Modules",     "remoteRoot": "C:/Coding/TestProjects/FLExTrans/FlexTools/Modules/FLExTrans" },
        { "localRoot": "${workspaceFolder}/Dev/TopLevel",    "remoteRoot": "C:/Coding/TestProjects/FLExTrans/FlexTools" }
      ],
      "console": "integratedTerminal"
    },

    // ── Option 2: Debug in the Documents\FLExTrans folder (copy-based) ─────────
    // No symlinks: a preLaunchTask xcopies your repo source into the deployment right
    // before launch. Handy when you can't use symlinks (no admin / no Developer Mode).
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

The copy task referenced by **Option 2** lives in `.vscode\tasks.json`. It `xcopy`s
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

Press **F5** (or the Run & Debug panel), pick a configuration, and the FLExTrans tool
window opens; breakpoints in `Dev\` will hit.

---

## 9. Editing `.ui` files → compiling to `.py`

1. Edit the `.ui` in `pyside6-designer` (§6).
2. Compile it to Python with PyQt6's `pyuic` via `Dev\Lib\Windows\convert_ui_py.bat`:
   ```powershell
   cd Dev\Lib\Windows
   .\convert_ui_py.bat RuleAssistantWindow      # name without extension
   ```
   (Internally: `py -m PyQt6.uic.pyuic <name>.ui -o <name>.py`.) There's also a VSCode
   task **"Convert active UI to Python"** that runs this on the currently open file.
3. **Never hand-edit the generated `*.py`** (e.g. `RuleAssistantWindow.py`) — your
   changes are lost on the next compile. Edit the `.ui` instead (see conventions, §13).

---

## 10. Translating user-facing strings

All user-facing text is localized through Qt's translation system into German (`de`),
Spanish (`es`), and French (`fr`). The workflow is: **mark strings → extract to `.ts` →
translate → compile to `.qm`**.

### 10a. Tools you need

The translation batch files call **`pylupdate5`** (extract) and **`lrelease`** (compile):

- `pylupdate5` ships with **PyQt5**: `pip install PyQt5` puts `pylupdate5.exe` in your
  Python `Scripts` folder.
- `lrelease` comes from the Qt Linguist tooling: `pip install pyqt5-tools`, **or** use the
  `pyside6-lrelease` you already have from PySide6 (§6).
- Make sure the chosen tools are on your **PATH**.

> **Why not the PyQt6/PySide6 tools?** `pylupdate6` (PyQt6) and `pyside6-lupdate`
> (PySide6) exist, but **do not migrate the extract step to them.** Our code writes
> nearly every string as `_translate("Context", "…")` (with
> `_translate = QCoreApplication.translate`). Only **`pylupdate5` follows that alias** —
> `pylupdate6` and `pyside6-lupdate` only recognize a fully-qualified
> `QCoreApplication.translate(...)` call, so they **silently drop the `_translate(...)`
> strings** (and would delete them from the `.ts` with `--no-obsolete`). They also differ
> in CLI and `.ts` formatting. So use **`pylupdate5`** to extract. (The compile step is
> safe either way — `lrelease`/`pyside6-lrelease` only read the `.ts` and write the
> `.qm`; they never modify the `.ts`.)

### 10b. Mark strings in code with `_translate()`

Each file aliases `_translate = QCoreApplication.translate` and wraps user-facing strings:

```python
_translate = QCoreApplication.translate
...
self.saveButton.setText(_translate("RuleAssistantWindow", "Save"))
```

The first argument is the **context** (a label, independent of the filename; contexts
with the same name merge across loaded `.qm` files at runtime). The second is the English
**source** string — that's what the translation is keyed on. To show a literal `&` use
`&&` (a single `&` is a Qt mnemonic).

### 10c. Extract strings into `.ts` — `local_pylup.bat`

From `Dev\Modules\`, run the extractor on a file (name without extension):

```powershell
cd Dev\Modules
.\local_pylup.bat RuleAssistantPy
```

This runs `pylupdate5` to pull the marked strings out of `RuleAssistantPy.py` into
`translations\RuleAssistantPy_de.ts`, `_es.ts`, `_fr.ts`, and copies the `_fr.ts` to a
base `RuleAssistantPy.ts`. (`local_pylup_drop_obsolete.bat` does the same but also drops
strings that no longer appear in the code.) A `.ts` lives in a `translations\` folder
beside the `.py` whose strings it holds, named after that `.py`.

### 10d. Translate

Edit the new/changed `<translation>` entries in each `_de/_es/_fr.ts` (by hand or with Qt
Linguist). Aim for **0 unfinished**. For Rule Assistant UI, English source strings
originate from `Dev\RuleGen_{en,de,es,fr}.properties` — pull wording from there.

### 10e. Compile to `.qm` — `local_lreal.bat`

```powershell
cd Dev\Modules
.\local_lreal.bat RuleAssistantPy
```

This runs `lrelease` to compile each `_de/_es/_fr.ts` into a `.qm`. **Edit the output
path inside `local_lreal.bat` to point at *your* deployment's translations folder**, e.g.
`...\FlexTools\Modules\FLExTrans\translations\` — out of the box it points at one
developer's deployment. (If you used symlinks in §7, you can instead compile into
`Dev\CompiledTranslations\` and let the link carry it into the deployment.)

---

## 11. Authoring the user documentation (XLingPaper)

The user guide is written in **XLingPaper** (an XML markup for linguistic documents) and
edited in the **XMLmind XML Editor (XXE)**. The source is
`Installer\InstallerResources\Doc\UserDoc.xml`; you generate `UserDoc.htm` from it, and
that `.htm` is what the installer bundles into the deployment's *FLExTrans Documentation*.

### 11a. Get XLingPaper (XMLmind is already installed)

You don't need to download or install XMLmind separately: it's **already installed with
FLExTrans** (XMLmind is the editor used for transfer rules), and XLingPaper bundles
XMLmind built in anyway. So you only need **XLingPaper**:

1. Download and install XLingPaper from <https://software.sil.org/xlingpaper/> — its
   download includes XMLmind, pre-configured for XLingPaper.
2. Open an XLingPaper document and you'll see the **XLingPaper** menu.

### 11b. Edit and produce the HTML

1. Open `Installer\InstallerResources\Doc\UserDoc.xml` in XMLmind.
2. Make your edits.
3. Run **XLingPaper → Produce Web Page** (shortcut **F7**). This regenerates
   `UserDoc.htm` next to the `.xml`.
4. Commit both `UserDoc.xml` and the regenerated `UserDoc.htm` — the `.htm` is the file
   that actually ships.

---

## 12. Unit tests

Tests live in `Dev\unit_tests\` and use Python's built-in `unittest`. Run them all with:

```powershell
cd Dev
.\run_unit_tests.bat
```

(That's just `py -3.13 -m unittest discover -s unit_tests`.) You can also run a single
file from the VSCode Test Explorer or with
`py -3.13 -m unittest unit_tests.test_escapeReserved`.

### Adding a test

Create `Dev\unit_tests\test_<thing>.py`. Because the library modules expect the .NET/SIL
environment, import the provided **`net_stubs`** first (it mocks those before `Utils` and
friends load), then add `Dev\Lib` to the path and import what you're testing. Model it on
the existing tests:

```python
import unittest
import sys
import os

import net_stubs  # noqa: F401 — mock .NET/SIL before the libs load

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Lib')))

import Utils

class TestEscapeReserved(unittest.TestCase):

    def test_right_brackets(self):
        self.assertEqual(Utils.escapeReservedApertChars(">>"), "\\>\\>")

if __name__ == "__main__":
    unittest.main()
```

`discover` finds any file named `test_*.py` automatically, so no registration is needed.
Keep tests fast and free of FLEx-database dependencies (stub what you must).

---

## 13. Coding conventions (from `CLAUDE.md`)

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

## 14. Using GitHub Copilot

Extensions and sign-in are covered in §3b. Day-to-day:

- **Inline completions:** start typing; **Tab** accepts, **Esc** dismisses,
  **Alt+]/Alt+[** cycles suggestions.
- **Copilot Chat:** open with **Ctrl+Alt+I** (or the chat icon). Useful commands:
  - `/explain` — explain the selected code.
  - `/fix` — propose a fix for selected code or a diagnostic.
  - `/tests` — draft tests.
  - `#file` / `#selection` add context; `@workspace` asks about the whole repo.
- **Teach Copilot our conventions:** create `.github/copilot-instructions.md` and paste
  the conventions from §13 (and `CLAUDE.md`). Copilot Chat picks up that file
  automatically so suggestions match house style (camelCase, blank-line rules,
  ~200-char lines, version-history headers, etc.).
- **Watch out:** by default Copilot suggests `snake_case`, PEP 8 double blank lines, and
  80-col wrapping. Review against §13.

---

## 15. Git workflow

- Branch off `master` for changes; open a PR back into `master`.
- Don't commit machine-specific paths: keep your edited `create_links.bat` (now living in
  the deployment), `create_apertium_links.bat`, `launch.json`, and `tasks.json` paths
  local. `.venv\` should not be committed.

---

## 16. Suggestions / things easy to miss

- **Get a deployment first.** You need a real FlexTools deployment before symlinks make
  sense — `create_links.bat` overlays source onto an existing install, it doesn't create
  one. (Build one via Appendix A, or unzip a released installer's image.)
- **Admin / Developer Mode for `mklink`.** Symlink creation needs elevation or Windows
  Developer Mode. If links silently fail, this is usually why.
- **No spaces in paths** used by the link scripts (a hard requirement).
- **FLEx must be installed and have projects** matching the `flextools.ini` you pass as
  the debug argument; otherwise the tool can't open the source/target databases.
- **Build the bilingual dictionary** for a project so the Rule Assistant shows test data.
- **Interpreter mismatch** is the most common "runs but won't debug" cause — confirm
  VSCode is using a Python 3.13 interpreter that can see the dependencies.
- **`.qm` files are build artifacts** — after editing a `.ts`, recompile (§10e) and, for
  the copy-based debug option, make sure the task copies the updated `.qm`.
- **Consider `.github/copilot-instructions.md`** (see §14) so AI assistance respects the
  house style automatically.

---

## Appendix A. Building the FLExTrans installer locally

You only need this to **cut a release** (produce the installer `.exe` and the
FlexTools-with-FLExTrans zip). For day-to-day development you don't build the installer —
you just need a deployment to link into (§7).

### A.1 Tools to install

- **NSIS (Unicode)** — the installer compiler. Get it from
  <https://nsis.sourceforge.io/> (or <https://sourceforge.net/projects/nsis/>). Use the
  Unicode build.
- **nsisunz plugin** (Unicode) — the installer unzips at runtime, so it needs this plugin.
  Download from <https://nsis.sourceforge.io/Nsisunz_plug-in>, take the **Unicode**
  version, and put `nsisunz.dll` in `C:\Program Files (x86)\NSIS\Plugins\x86-unicode`.
- **7-Zip** (`7z` on your PATH) — used by `CreateInstaller.bat` to zip the image and the
  XMLmind XXE add-ons.
- *(Optional)* **HM NIS Edit** (<http://hmne.sourceforge.net/>) — a GUI editor that can
  scaffold NSIS scripts; not required to build.

### A.2 The two resource locations the build needs

The `.nsi` references files from two places:

1. **`GIT_FOLDER`** — your repo. Everything in `Installer\InstallerResources\` lives in
   git and is pulled from here: `DialogImages` (icons), `INI`, `Makefiles`,
   `TransferRules`, `VBS`, `replace.dix`, `Apertium4Windows`, `Make4Windows`,
   `Sample Projects`, `Doc`, etc.
2. **`RESOURCE_FOLDER`** — a folder you create that holds the **large third-party
   installers** that are *not* in git. From the `.nsi` defines, it must contain:
   - **`python-3.13.12-amd64.exe`** — the Python installer (matches `PYTHON_VERSION`).
   - **`xxe-perso-8_2_0-setup.exe`** — XMLmind XML Editor Personal Edition installer.

   Download both from the FLExTrans installer-resources Drive folder:
   <https://drive.google.com/drive/folders/1mlA09EcUNkdnbAMpNk8G1zQEF-fxmYIQ?usp=drive_link>
   (If you bump the Python or XXE version in the `.nsi`, drop the matching installer here
   and update the `!define`s.)

### A.3 What `Installer\CreateInstaller.bat` does

1. Sets `FLEXTRANS_VERSION` (top of the file) and wipes `Installer\InstallerImageFolder`.
2. Builds the deployment image under `InstallerImageFolder\FLExTrans\` (`FlexTools\`,
   `WorkProjects\` [German-Swedish, TemplateProject], `SampleFLExProjects\`,
   `FLExTrans Documentation\`).
3. Copies your repo source into the image: `..\Dev\TopLevel\*.py`, `..\Dev\Modules\*.py`,
   `..\Dev\Lib\*.py` + `*.css`, `..\Dev\Lib\Windows\*.py`,
   `..\Dev\CompiledTranslations\*.qm`, plus Apertium/Make tools, docs, and sample
   projects.
4. Zips the XXE add-ons and the `FLExTrans` folder, then runs
   `makensis ... FLExTrans-installer.nsi` to produce the installer.

### A.4 Running the build

`Installer\CreateInstaller.bat` picks its `makensis` command by computer name:
`if %COMPUTERNAME% == RONS-XPS (...) else (...)`. The simplest path is to **make that
first branch yours**:

1. Find your computer name: `echo %COMPUTERNAME%`.
2. In `CreateInstaller.bat`, change `RONS-XPS` in the `if %COMPUTERNAME% == RONS-XPS`
   line to your own computer name.
3. In that same branch, set the paths to yours: `-DGIT_FOLDER=<your repo>`,
   `-DRESOURCE_FOLDER=<your RESOURCE_FOLDER from A.2>`, and
   `-DOUT_FOLDER=<where to write the .exe>`. Leave `-DBUILD_NUM=99` as-is (you don't need
   a build number), and note this branch doesn't code-sign, so no certificate is needed.
4. From an Administrator prompt:
   ```powershell
   cd Installer
   .\CreateInstaller.bat
   ```

Alternatively, compile in the **MakeNSISW** GUI: open `Installer\FLExTrans-installer.nsi`,
click **Settings**, set `GIT_FOLDER` (and `RESOURCE_FOLDER`/`OUT_FOLDER`), and compile.

The result is `FLExToolsWithFLExTrans<ver>.zip` and the installer `.exe`. Unzip that zip
into your test location (e.g. `C:\Coding\TestProjects\FLExTrans`) to get a deployment, then
link your source into it (§7).

### A.5 Publishing a release (maintainers)

Per the installer ReadMe: upload the new `FLExTrans<ver>.exe` and an updated
`.download_info` file to the SIL FTP site (`upload_areas/flextrans`, via FileZilla with
the ssh key) — that makes it the current download and moves older ones to *Previous
Versions* — then post a release blog article and announce on the FLEx list.
