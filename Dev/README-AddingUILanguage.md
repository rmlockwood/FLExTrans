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
   (as with Spanish, `es-ES`). The position of the line in `LANGUAGES` is the position in the installer's language-picker dialog.

2. **Translate the installer strings.** Copy `Installer/InstallerResources/LangForInstallerScript/en.nsh` to `XX.nsh` in the same folder, change every `EN_` prefix to `XX_`, translate all
   the string values (including the five collection-tab `LangString`s), and set `XX_DISPLAY_NAME` to the same native name you put in `UILanguages.py`.

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
   the generated `languages.nsh` bundles each zip into the installer, and `derive_preview_specs.py` (also run by `CreateInstaller.bat`) derives `Dev/Lib/preview_spec_XX.json` from the
   translated `transfer.css` for the in-app rule preview (it prints a SKIP and the preview falls back to English until the translated CSS exists).

5. **Add the language-specific transfer-rules files** (e.g. `transfer_rules-Swedish_XX.t1x`) to `Installer/InstallerResources/TransferRules/`. The installer copies them by `$LANGCODE` at
   install time — no script changes needed.

6. **Create the UI translations.** Add `<module>_XX.ts` files for every module/library that has translations (see the `translations/` folders under `Dev/Lib`, `Dev/Lib/Windows`,
   `Dev/Modules`, `Dev/TopLevel`), translate them (Crowdin picks the new language up from the regenerated `crowdin.yml`), and compile them to `.qm` with the `compile_transl*.bat` /
   `process*.bat` scripts — those already loop over the generated `LANG_CODES`, so they include the new language automatically.

7. **Rule Assistant strings.** If the Rule Assistant properties files are in use (`Dev/RuleGen_{en,de,es,fr}.properties`), add a `RuleGen_XX.properties` translation as well.
