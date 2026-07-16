# Adding a new user-interface language to FLExTrans

The set of UI languages FLExTrans supports is defined in **one authoritative place**: [`Dev/Lib/UILanguages.py`](Lib/UILanguages.py). Runtime code (`Utils.py`, `WorkOnRulesWithAIDlg.py`) and
Python build tools (`derive_preview_specs.py`) import that module directly. Everything that cannot import Python gets its language lists from files **generated** from it by
[`Dev/updateLanguageFiles.py`](updateLanguageFiles.py):

| Generated file | Consumed by |
|---|---|
| `Dev/lang_codes.bat` | `Installer/CreateInstaller.bat` and all the translation-processing `.bat` scripts (they `call` it to get `LANG_CODES`) |
| `Installer/InstallerResources/LangForInstallerScript/languages.nsh` | `FLExTrans-installer.nsi` (MUI registrations, per-language includes, language-picker / langcode / addon-zip macros) |
| `crowdin.yml` | Crowdin translation sync |

The generated files are committed to the repo, and `CreateInstaller.bat` reruns the generator on every installer build, so they cannot drift from `UILanguages.py`. Never edit them by hand.

## Checklist: adding language XX (two-letter ISO 639-1 code)

1. **Add the language to the authoritative list.** In `Dev/Lib/UILanguages.py`, add one `UILang(...)` line to `LANGUAGES`: the two-letter `code`, the `englishName` (e.g. `Portuguese`), the
   `nativeName` (what the installer's language picker shows, e.g. `Português`), the `localeName` for date/time formatting (e.g. `pt_BR`), the NSIS language-file name `nsisName` (e.g.
   `Portuguese` — see `C:\Program Files (x86)\NSIS\Contrib\Language files` for the valid names), and `crowdinId` only if Crowdin's id for the language differs from the two-letter code
   (as with Spanish, `es-ES`). The position of the line in `LANGUAGES` is the position in the installer's language-picker dialog. In the same file, also add the language's entries to
   `MACRO_NOUNS`, `MACRO_NAMING_WORDS`, and `MACRO_STOP_WORDS` — respectively the word for "macro", the fillers a description might use when naming one ("the macro **called** m_x"), and the
   common function words that can sit next to "macro" in prose without being a name ("the macro **that** …") — which the Work on Rules with AI module uses to spot macro references and to
   avoid mistaking prose for a mistyped macro name; a missing entry doesn't break anything, it only means less accurate macro-reference detection for descriptions written in that language.

2. **Translate the installer strings.** Copy `Installer/InstallerResources/LangForInstallerScript/en.nsh` to `XX.nsh` in the same folder and make these three edits, then translate all the
   string values (including the five collection-tab `LangString`s) and set `XX_DISPLAY_NAME` to the same native name you put in `UILanguages.py`:
   - Change every `EN_` prefix to `XX_` (e.g. `EN_LANGCODE` → `SV_LANGCODE`) — these are the `!define` lines.
   - Change every `${LANG_ENGLISH}` to `${LANG_<NSISNAME>}` on the five `LangString` lines. `<NSISNAME>` is the uppercase of the `nsisName` you set in step 1 — NSIS itself defines this
     constant when the generated `languages.nsh` registers the language with `!insertmacro MUI_LANGUAGE "<nsisName>"`, so you don't invent the name. For `nsisName='Swedish'` it is
     `${LANG_SWEDISH}` (compare `de.nsh`, which uses `${LANG_GERMAN}`).
   - Set `XX_LANGCODE` to the two-letter `code` from step 1 (e.g. `"sv"`).

3. **Run the generator:** `python Dev/updateLanguageFiles.py`. This regenerates the three files in the table above; commit them along with your other changes. Nothing in
   `FLExTrans-installer.nsi`, the `.bat` scripts, or `crowdin.yml` needs hand-editing.

4. **Add the translated XXE addon.** Of the seven XXE addons, only `ApertiumTransferXMLmind` is localized. Create
   `Installer/InstallerResources/XXEaddon/translations/XX/ApertiumTransferXMLmind/` containing translated copies of exactly these **five files** (start from the master addon's copies —
   everything else in the addon is language-neutral and comes from the base English addon at install time):

   | File | What to translate |
   |---|---|
   | `configuration/menus.xml` | The XXE menu labels (e.g. `Set reference`, `Show FLExTrans User Documentation`) |
   | `configuration/commands.xml` | The prompts/parameters of the pick-dialog commands (e.g. `Attribute`, `Category`, `List`, `Macro`) |
   | `configuration/elementTemplates.xml` | The element-template names shown in XXE's insert lists (e.g. `and_equal_2`) |
   | `css/transfer.css` | The on-screen labels XXE renders around rule elements (keep selectors/colors; translate only the generated label text) |
   | `transfer.sch` | The Schematron validation error messages |

   At install time the installer unzips the base (English) addon first and then overlays the language zip for the chosen `$LANGCODE`, so the five translated files shadow their English
   counterparts. Everything downstream is automatic: `CreateInstaller.bat` zips every `translations/<code>` folder it finds in `LANG_CODES` into `AddOnsForXMLmind_<code><version>.zip`,
   the generated `languages.nsh` bundles each zip into the installer, and `derive_preview_specs.py` (also run by `CreateInstaller.bat`) derives `Dev/Lib/AI/preview_spec_XX.json` from the
   translated `transfer.css` for the in-app rule preview (it prints a SKIP and the preview falls back to English until the translated CSS exists).

5. **Add the language-specific transfer-rules files** (e.g. `transfer_rules-Swedish_XX.t1x`) to `Installer/InstallerResources/TransferRules/`. The installer copies them by `$LANGCODE` at
   install time — no script changes needed.

6. **Create the UI translations.** Add `<module>_XX.ts` files for every module/library that has translations (see the `translations/` folders under `Dev/Lib`, `Dev/Lib/Windows`,
   `Dev/Modules`, `Dev/TopLevel`), translate them (Crowdin picks the new language up from the regenerated `crowdin.yml`), and compile them to `.qm` with the `compile_transl*.bat` /
   `process*.bat` scripts — those already loop over the generated `LANG_CODES`, so they include the new language automatically.

## Maintaining the XXE rule-preview stylesheet (`transfer.css`)

The in-app rule preview (the "Work on Rules with AI" module and anywhere `TransferPreview` renders a rule) does **not** read the XXE `transfer.css` at runtime. Instead a build tool,
[`Dev/derive_preview_specs.py`](derive_preview_specs.py), parses each `transfer.css` into a compact `Dev/Lib/AI/preview_spec_<code>.json` that `TransferPreview` loads. Each spec captures, per rule
element, the label text, the attribute chips shown on it, and the chip colours (the colours come from the stylesheet's `@property-value` declarations, so the preview's box colours match XXE).

**When to run it:** any time an XXE `transfer.css` changes — a colour edit, a new element rule, a changed label — and after adding a new language's translated stylesheet (step 4 above).

**How to run it:** `python Dev/derive_preview_specs.py`. It rewrites `preview_spec_<code>.json` for every language in `UILanguages.py`; a language whose translated `transfer.css` doesn't exist yet
is printed as `SKIP` and its preview falls back to English. `CreateInstaller.bat` runs this automatically on every build, so the shipped specs always match the current CSS — you only need to
run it by hand when you want to see a CSS change reflected in the preview during development. Commit the regenerated `preview_spec_<code>.json` files with your CSS change.

### The master and translated stylesheets

There are N copies of `transfer.css`, one per UI language (English's copy is the master):

- the master (English): `Installer/InstallerResources/XXEaddon/ApertiumTransferXMLmind/css/transfer.css`
- one per translation language: `Installer/InstallerResources/XXEaddon/translations/<code>/ApertiumTransferXMLmind/css/transfer.css`

The translated copies are **structurally identical** to the master — same selectors, same `text-field`/`combo-box`/colour definitions, same `@property-value` colours — and differ **only** in the
quoted label strings inside `content:` (e.g. `" action: "` → `" Aktion: "`). So a structural change to the master (a new element rule, a colour change, a new/renamed field) must be mirrored into
every translated copy, keeping its translated label text. [`Dev/syncTransferCss.py`](syncTransferCss.py) does this for you — don't hand-edit the translated copies for structural changes.

### Syncing the translated stylesheets after editing the master

After you change the **master** `transfer.css`, run:

```
python Dev/syncTransferCss.py
```

It rebuilds each translated copy from the master, re-applying that copy's existing translations (matched by selector and position) so every structural change is carried over automatically. Any
English string in the master that a translated copy has no translation for is left in English **and reported**, so you can see exactly what still needs translating, e.g.:

```
  de: updated (...\translations\de\...\transfer.css, cp1252)
    1 string(s) still in English (need translation in de):
      " negate: "
```

Then hand-translate only the reported strings in the affected files. `CreateInstaller.bat` runs this tool just before `derive_preview_specs.py`, so a build never ships a translated stylesheet
that has drifted from the master. Notes: only translate the **master**; the translated copies are regenerated. Comments and everything outside the quoted label strings come from the master, so a
translated copy's CSS comments are reset to English (they aren't user-visible). Each translated file keeps the encoding it is stored in (currently cp1252). A language whose translated
`transfer.css` doesn't exist yet is skipped — create it first (step 4 above).

**Rewording an existing label.** The tool matches translations to master strings **by position** (which rule, which field), not by the English text. So if you only reword a label that is
already there — e.g. change `" action: "` to `" step: "` on an otherwise-unchanged rule — the tool keeps the existing translation at that position and does **not** flag it. If the reword is
just cosmetic (same meaning), that's fine, nothing more to do. If the meaning changed, update that label's translation in each `translations/<code>/…/transfer.css` yourself — or blank that one
string there (`content: "";`) and re-run the sync, which will then leave it English and list it as needing translation, back in the normal flow above.

