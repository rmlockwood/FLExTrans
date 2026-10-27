# FTtranslator: handover

Status as of 2026-10-26. This is for whoever picks up the work next, whether a person or a Claude session. For usage, see [README.md](README.md). This file covers the current state, the decisions behind it, and the next steps.

## Goal

FTtranslator does end-to-end translation with FLEx and FLExTrans (FT), with no FlexTools and no windows:

1. The source text goes in as a new text in the source FLEx project.
2. HermitCrab parses it.
3. The analysis guesser picks the most likely parse for each word in context, and that parse is approved.
4. FT's drafting steps produce the target text.

The phone app is the long-term goal. A CLI comes first, and a web app may come later. Teams should be able to insert custom code part-way through the pipeline, the way FlexTools modules allow. The code reuses FT's own code and configuration so maintenance stays low.

## Status

**Phase 0 (spike) and Phase 1 (MVP CLI) are done. Most of Phase 2 (extensibility and diagnostics) is done.** Everything below was verified on scratch projects (see [Test setup](#test-setup)):

- `translate` runs the whole Drafting collection and prints the target text on stdout. Messages go to stderr.
- **Equivalence:** FT's own `TranslateText.py`, run as a custom FlexTools module inside the pipeline, gave byte-identical output to the built-in steps.
- **Approval release:** by default, the guessed approvals are undone after extraction, and the saved text has only unanalysed `WfiWordform`s. `--keep-approvals` keeps them as `WfiGloss`es.
- `--insert` puts the translation into the target project.
- **Custom code:** a FlexTools module in the collection (`[Modules\FixNina.py]`, in the work project's Config folder) changed the transfer output mid-pipeline. A Python hook from `fttranslator.ini` also ran.
- The `steps`, `check` and `runs` commands work. Each run writes a JSON record to `<work project>\Output\ftt_runs\`.
- Unit tests (9, no FieldWorks needed) pass: `python -m unittest discover -s tests`.
- **Coding standards:** on 2026-10-26 all the Python was brought into line with the FLExTrans repo's `CLAUDE.md` (camelCase names, version-history headers, description blocks, blank-line rules, one-line calls). The `steps`, `check` and `translate` output and the run record were identical before and after, and pyright is clean. Hook files see the camelCase `Context` attributes (`ctx.ftDb`, `ctx.configMap`); the `.ini` keys, CLI flags and run-record JSON keys did not change.

Not started:
- Upstream FT changes.
- A service or web app.
- The phone apps.

## How to run

FTtranslator lives in the FLExTrans repo at `Dev\FTtranslator`, on the `FTtranslator` branch. On 2026-10-26 it moved there from its own folder, `C:\Users\rlboo\GitHub\FTtranslator`, which is now empty.

Run the commands from `Dev\FTtranslator`, so that `fttranslator` and `parse_priority` can be imported:

```
cd C:\Users\rlboo\GitHub\FLExTrans\Dev\FTtranslator
python -m fttranslator check     "C:\Users\rlboo\Documents\FLExTransTOFT\WorkProjects\FTT-Scratch"
python -m fttranslator translate "C:\Users\rlboo\Documents\FLExTransTOFT\WorkProjects\FTT-Scratch" "Le garçon mange des bonbons."
```

The environment is Python 3.13, flexlibs 1.2.8, pyflexicon 4.13, flextoolslib 2026.5.4, pythonnet 3.0.5 and PyQt6. FT is installed at `C:\Users\rlboo\Documents\FLExTransTOFT`.

## Code map

| File | Role |
|---|---|
| `fttranslator/cli.py` | argparse commands. Redirects file descriptor 1 to stderr during a run (`stdoutToStderr`) |
| `fttranslator/env.py` | `bootstrap()`: makes FT importable and runnable headless (see gotchas) |
| `fttranslator/profile.py` | Work project + optional `Config\fttranslator.ini` (collection, title_prefix, source_project, `[hooks]`; the `.ini` keys keep their underscores, the Python attributes are camelCase). Imports neither FT nor FieldWorks |
| `fttranslator/pipeline.py` | `Options`, `RunResult`, `Context`, `Step`. `build()` turns the collection .ini into steps and adds hooks. `run()` runs them in order |
| `fttranslator/translator.py` | `Translator` API (also meant for a future service). `flexlibsView()`. `_configOverride()` |
| `fttranslator/steps/ingest.py` | Import Text, Parse Words, Approve Guesses (+ `fillSenses`), `releaseApprovals` |
| `fttranslator/steps/flextrans.py` | Built-in wrappers around FT's core functions. Loader for custom FlexTools modules |
| `fttranslator/steps/finish.py` | Collect Output: translation + Text Out rules + failed-word diagnostics |
| `parse_priority/` | Earlier tool: guesser (`Ranker`), HermitCrab parse + `Filer`, `textedit.approveGuesses`/`addSentence`. Used as a library, and has its own CLI |
| `tests/test_pipeline.py` | Profile, pipeline build, hooks and the run loop, tested with stub steps |

Pipeline order:
1. Import Text
2. Parse Words
3. Approve Guesses
4. The collection entries, in .ini order (built-in or FlexTools module)
5. Collect Output

Hooks wrap any of these steps by name.

## Key decisions (and why)

1. **FT is imported, not forked.**
   - The user chose this.
   - `env.py` puts the installed `FlexTools\Modules\FLExTrans` (+ `Lib`) on `sys.path`. `--modules dev` uses this repo's own `Dev\Modules` + `Dev\Lib` instead. On 2026-10-26 it gave the same output as the installed modules.
2. **Built-in steps call FT's core functions directly, as `TranslateText.py` does, not `MainFunction`.** This skips the Qt translators, Mixpanel, and the config re-read.
3. **A collection entry that isn't one of the 7 standard modules runs through `FlexToolsModule.Run()`.**
   - If the module declares `FTM_ModifiesDB`, it is wrapped in a flexicon `UndoableOperation`.
   - Collection paths can also be relative to the work project's `Config` folder, which is an addition to FlexTools.
4. **The source project is opened with flexicon (`undoable=True`), and FT gets a flexlibs view of the same open cache.**
   - flexlibs opens with a session-long non-undoable task, and the approvals need Undo.
   - FT is written against flexlibs, and flexicon differs in places: `LexiconGetSenseCustomFieldNamed(None)` raises in flexicon instead of returning None.
   - Never call `CloseProject()` on the view.
5. **Approvals are temporary by default.**
   - The user chose "keep the text, mark it for review". In-text analyses get the guesser's top priority (7), so auto-approved mistakes would reinforce themselves.
   - The approvals are undone right after Extract Source Text. They are kept only if the undo-stack depth (`ActionHandlerAccessor.UndoableSequenceCount`) shows that another step has written to the source since, in which case a warning is given.
   - The text stays in the project, titled `FTT <timestamp> <first three words>`, for review in FLEx.
6. **`fillSenses`: HermitCrab-filed analyses have an msa but no sense on each bundle,** and FT then reports "No sense found". When approving, each bundle's `SenseRA` is set from its msa, as FLEx does when a parse is confirmed.
7. **The config is never written.**
   - `SourceTextName` is set in the run's `configMap` only.
   - `_configOverride` patches `ReadConfig.readConfig` for the duration of a run, so FT code that re-reads the config sees this run's values. That includes `RunApertium.run_makefile` and custom modules' `MainFunction`.
8. **Output goes to stdout and is inserted only with `--insert`.** The user chose this. The Insert Target Text entry stays in the collection and skips itself.

## Gotchas found

- Bootstrap must `chdir` to `<work project>\Config` **before** any FT or flextoolslib import. Both read the working directory when they are imported.
- **FieldWorks start-up order:** `flexlibs.FLExInitialize()` must come **before** flexicon's. In the other order you get "SLDR has already been initialized".
- `FTReporter` lives in `flextoolslib.code.FTReport`. It is not exported from `flextoolslib`.
- FT modules create a `QApplication` when they are imported. `QT_QPA_PLATFORM=offscreen` keeps it headless. `Mixpanel.LogModuleStarted` is replaced with a no-op, because it can show a modal dialog.
- FT writes **NFD** text. Custom steps that search the intermediate files must normalize their strings to NFD.
- Source senses with no target link don't produce `@` markers. They appear as identity `<e><i>lemma</i></e>` entries in `bilingual.dix` and pass through untranslated. `finish.py` detects them from there.
- make and STAMP print to the console. That is why `cli.py` redirects file descriptor 1 during a run.
- Filing parser results (`Filer`) can't be undone, the same as in FLEx. It runs outside any unit of work.
- Windows console code pages: quick ad-hoc scripts that print vernacular text need `PYTHONIOENCODING=utf-8`.

## Test setup

Use only the scratch copies (also recorded in Claude memory as `ftt-scratch-test-setup`):

- **Work project:** `C:\Users\rlboo\Documents\FLExTransTOFT\WorkProjects\FTT-Scratch`, a copy of "French-Spanish Demo".
  - Its `flextools.ini` has `currentproject = 'French-PP-FTT'`.
  - Its `FlexTrans.config` has `TargetProject=Spanish-FTT-Scratch`.
  - STAMP synthesis.
- **Source:** `French-PP-FTT`, a copy of `French-ParsePriority`. The user said it is set up for HermitCrab, and its active parser is HC.
- **Target:** `Spanish-FTT-Scratch`, a copy of `Spanish-FLExTrans-TOFT2026`. The French "Target Equivalent" links resolve by GUID.
- **Extra collections in FTT-Scratch:**
  - `FTT Test.ini`: the Drafting steps, plus `[Modules\FixNina.py]` after Run Apertium and `[FLExTrans.Synthesize Text]` written as a name.
  - `FT TranslateText.ini`: only `[FLExTrans\TranslateText.py]`, used as the equivalence reference.
- **Selecting a collection:** `Config\fttranslator.ini` picks the collection and is currently set to `Drafting`. The `ftt_test_hooks.py` hook file is in `Config`, but no hook is currently enabled.
- **Leftover texts:** earlier test runs left several `FTT …` texts in French-PP-FTT and `FTT keep test` in Spanish-FTT-Scratch.
- **Recreating copies:** `python -m parse_priority copy SRC NEW`.

Typical test sentence and current output:

```
Le garçon mange des bonbons. Les filles jouent avec une longue voiture.
El niño come de los caramelos. Los niñas %0%jouer1.1an% avec1.1 una voiture1.1 long1.1a.
```

jouer, avec, long and voiture have no target link in the test data. "Los niñas" is a transfer-rule issue. Neither is a pipeline bug.

## Known limitations / open questions

- **Speed:** each FT step opens and closes the target project itself, so a run takes roughly 15 s. A service would need FT to accept an already open target project.
- **Input handling:** each input line becomes one paragraph. There is no chapter or verse handling, and no Paratext export path (`ProductionModeOutputFlex=n` is ignored; insert is the only target).
- **Inbox texts:** these are marked only by the title prefix, not by a genre or tag. Something like a genre would make review lists easier.
- **Synthesis-failure detection** only knows STAMP's `%n%form%` marker. HermitCrab synthesis has not been tested (`HermitCrabSynthesis=y`; it needs the HC exes on PATH).
- **One-project mode** (`TwoProjectMode=n`) has not been tested. Insert is wrapped in an undoable operation for that case.
- **Undo stack after filing:** it is unverified whether `ParseFiler`'s non-undoable tasks ever clear the undo stack. The depth check in `releaseApprovals` would catch that case and keep the approvals.
- **`check`** doesn't yet verify that the collection's custom modules import cleanly. It only checks that the pipeline resolves, which does import them.

## Next steps (from the plan)

1. **Upstream FT PRs (Phase 3):**
   - `RunApertium.run_makefile` should take `configMap` rather than calling `readConfig()`.
   - Move the Qt and Mixpanel imports into the functions that use them.
   - Let the core functions accept an open `TargetDB`, so each step doesn't open and close the target.
2. **Speed:** keep both projects open across translations. Check the effect of `CacheData=y` (already on in the scratch config).
3. **Service (Phase 4):**
   - A long-running Windows host (for example FastAPI) built on `Translator`, keeping the projects open.
   - Endpoints for translate, runs and fixes. A web app on top.
4. **Phone apps (Phase 5):**
   - A translator client.
   - A companion review app built from the `ftt_runs` JSON. It would list unparsed, unlinked and unsynthesized words and send fixes to FLEx through the service: add an entry or sense, link a target sense, confirm a parse.
   - LCM and the FT tools are Windows/.NET, so phones are clients only.
5. **Smaller items:**
   - A review command that lists inbox texts still unapproved.
   - Optionally, a genre tag for inbox texts.
   - Tests for `finish.py`'s file scanners using sample files.

The full plan is at `C:\Users\rlboo\.claude\plans\help-me-plan-the-purring-hummingbird.md`.
