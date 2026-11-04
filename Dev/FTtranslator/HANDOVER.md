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
- **Offline bundle (2026-11-03/04):** the whole chain now runs without Windows or FieldWorks and is deployed on Railway. [HANDOFF-offline.md](HANDOFF-offline.md) is the full handoff for
  that work; the notes below are the history.
  - `export-bundle` writes the source lexicon data Extract Source Text needs (`bundle.py`). On Mato-Uma (3,710 entries) its stem tags matched all 1,716 lexical units in FT's real output files.
  - `golden` captures test data (`golden.py`): each text's occurrences and morph bundles as JSON, next to what the real Extract Source Text wrote for it. On Mato-Uma: 130 texts, about 130,000
    occurrences, Extract Source Text succeeded on all, and every GUID in the dumps resolves in the bundle's lexicon.
  - `check-golden` runs `bundleextract.py`, a FieldWorks-free port of Extract Source Text, on the golden pairs. Output and messages are byte-identical on all of Mato-Uma (130 texts),
    Toma-Zialo (24 texts, source project tod-flex1, through a scratch copy of the Config folder) and FTT-Scratch (9 texts). Together they exercise about 4,800 irregularly inflected variants,
    55 complex-form substitutions, 5,200 enclitics and stem features. Changing one category in a copied bundle made 93 Mato texts differ, so the check does fail when it should.
  - `hcsynth/` builds FieldWorks' HCSynthByGloss (unmodified source at `bd0608da7f`, plus a small shim file) for .NET 8, so HermitCrab synthesis can run on Linux. On 15,720 generated
    Mato-Uma lines it matched the installed Windows build except for the order of alternative forms (`%2%a%b%`), which is random run to run in both builds. See `hcsynth/README.md`.
    The .NET 8 SDK is installed per-user in `%USERPROFILE%\.dotnet` (not on PATH).
  - Windows-free plan (2026-11-03, Ron's choices): HermitCrab synthesis only (no STAMP); first milestone parses source words by looking up existing analyses (HermitCrab parsing later);
    test pair FTT-Scratch, switched to `HermitCrabSynthesis=y`. Its Spanish target has duplicate affix glosses (PL, SG), so nouns don't synthesize; Ron chose to proceed as-is, since the
    Linux version only has to match the desktop. Also noticed: HCSynthByGloss appends its "Duplicate gloss(es)" warning to forms that did synthesize, and FLExTrans leaves it in the output.
  - HermitCrab parsing without FieldWorks: `hcparse/` (.NET 8 port of `HCParser.ParseWord()`), with the grammar exported from flexicon's live `HCParser` (`parserexport.py`). Same results as
    FLEx's parser for all 6,729 Mato-Uma wordforms and all 102 FTT-Scratch ones (also on Linux/WSL), apart from the order of analyses.
  - Tokenizer without FieldWorks (`tokenizer.py`): FLEx's word, punctuation and wordform logic; sentences break at the whitespace after FLEx's sentence-end characters (Ron's rule, simpler
    than FLEx's). Same words, punctuation and wordforms as FLEx's ParagraphParser on 15 tricky French paragraphs (`golden --tokens`).
  - Parse filing and guessing without FieldWorks (`analysisguess.py`, data from `guessexport.py`), and the chain `offline-stream`: text to Apertium stream with no FieldWorks. On FTT-Scratch,
    byte-identical to the desktop's `source_text-aper.txt` for a two-paragraph text. On the 15 edge-case paragraphs, 6 of 17 lines differ, all at the same kind of spot: a capitalized `Le`/`La`
    whose two new parser analyses tie, which FLEx breaks by its new analyses' random GUIDs (so the desktop's own choice there is random).
  - Transfer without make (`transfer.py`, data from `transferexport.py`): the makefiles' Apertium commands. On FTT-Scratch the target stream was byte-identical to the desktop's with the
    Windows tools. The Linux (Debian) tools are untested; Ron chose to test them on Railway.
  - HermitCrab synthesis without FieldWorks (`synthesis.py`, data from `synthexport.py`): Convert Text to Synthesizer Format (HermitCrab half) and Synthesize Text. From the same target stream,
    the master, parses and surface files and the synthesized text were identical to the desktop's on two FTT-Scratch texts; `tests/test_synthesis.py` covers complex forms, clitics and
    variants, which FTT-Scratch lacks. Known quirk kept from FLExTrans: `@` (unknown) words still go to HCSynthByGloss.
  - `serve-offline` (`offlineserver.py`): the React page translating from a bundle alone. Run locally on Windows on FTT-Scratch's text 1, its translation was identical to the desktop's.
    Packaged for Railway by `Dockerfile` and `railway.toml`; the FTT-Scratch bundle is committed in `deploy/bundle` (Ron's choice for the test pair). The first Railway build used Railpack because the Dockerfile was in `deploy/`; it was moved to the service root so Railway finds it by name.
    Text Out rules are exported into the bundle and applied after synthesis (`textout.py`, a port of TextInOutUtils' rule code; `tests/test_textout.py` runs it beside the original).
  - Not exercised by any project: discontiguous complex forms (only fa-bcc and fa-taj are set up for them, and they use TreeTran).
  - Not supported: TreeTran projects (refused), which rules out fa-bcc and fa-taj.
- **Coding standards:** on 2026-10-26 all the Python was brought into line with the FLExTrans repo's `CLAUDE.md` (camelCase names, version-history headers, description blocks, blank-line rules, one-line calls). The `steps`, `check` and `translate` output and the run record were identical before and after, and pyright is clean. Hook files see the camelCase `Context` attributes (`ctx.ftDb`, `ctx.configMap`); the `.ini` keys, CLI flags and run-record JSON keys did not change.

Not started:
- Upstream FT changes.
- Reaching the service (`serve`) from other machines.
- The phone apps, beyond the offline bundle's first pieces.

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
| `fttranslator/translator.py` | `Translator` API (also meant for a future service). Keeps the projects open across runs; `close()`. `flexlibsView()`. `_configOverride()` |
| `fttranslator/server.py` | `serve`: stdlib single-threaded `HTTPServer` driven by `handle_request()` on the main thread (FieldWorks thread affinity, runs can't overlap). JSON API + serves `web\dist`. Localhost-only, JSON-only POST, Host check |
| `fttranslator/bundle.py` | `export-bundle`: the offline bundle's source lexicon data (`manifest.json`, `lexicon.json`): entries, senses and msas keyed by GUID, with the strings Extract Source Text would build, worked out by FT's own `Utils` |
| `fttranslator/bundleextract.py` | Extract Source Text with no FieldWorks or FT imports: bundle + text dump in, Apertium stream and messages out. Line-for-line port; `compareGolden()` is `check-golden` |
| `fttranslator/golden.py` | `golden`: golden pairs for testing a bundle runtime, `NNN.text.json` (occurrences, morph bundles as GUIDs) + `NNN.expected.txt` (real Extract Source Text output) + `index.json` |
| `web/` | React front end (Vite 6 + TypeScript). `npm install` + `npm run build` → `web\dist`; `npm run dev` proxies `/api` to port 8765 |
| `fttranslator/sharedtarget.py` | `SharedTarget`: opens the target once and hands FT's modules a view of it through patched flexlibs `OpenProject`/`CloseProject`; `save()` after each run |
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

- **Speed:** `Translator` keeps both projects open from the first `translate()` to `close()`. FT's own steps still open and close the target themselves, so `sharedtarget.py` patches flexlibs' `OpenProject`/`CloseProject` during each run to hand them the one open target. In an `interactive` session, the first sentence takes about 5 s and each later one about 0.5 s. A one-shot `translate` still pays about 3 s to start, about 2 s to close, and a few seconds more when the process exits.
- **make and same-second runs:** Run Apertium's make skips the transfer when `target_text-aper.txt` isn't older than the source file, and file times only go to the second. The built-in Run Apertium step deletes the transfer output (and `Makefile.advanced`'s `target_text0-2.txt`) first.
- **Projects held open:** while a `Translator` is open, FLEx can't open its projects unless sharing is on, and edits made in FLEx meanwhile may not be seen.
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
   - Started 2026-10-30: `serve` is a local host built on `Translator`. It keeps the projects open and has endpoints for status, translate and runs, with a React page on top. It uses the
     standard library rather than FastAPI, since runs can't overlap anyway.
   - Still to do: endpoints for fixes, and a way to reach it from other machines. That needs authentication before it listens anywhere but localhost.
   - `web/` pins Vite 6.4.4. 6.4.5 fixes a moderate dev-server advisory (GHSA-8g5g-mxqh-grgj) but was too new on 2026-10-30. Bump it once it is two weeks old. The built page isn't affected.
4. **Phone apps (Phase 5):**
   - A translator client.
   - A companion review app built from the `ftt_runs` JSON. It would list unparsed, unlinked and unsynthesized words and send fixes to FLEx through the service: add an entry or sense, link a target sense, confirm a parse.
   - LCM and the FT tools are Windows/.NET, so a phone can't run the pipeline as it is. A client of the service is one route. The other is an **offline translator**: the desktop exports a
     bundle (a snapshot of what translation needs) and the phone runs a slimmed-down pipeline on it. The plan, in order:
     1. `export-bundle` (done): the source lexicon data for Extract Source Text.
     2. `golden` (done): golden pairs of each text's analyses and Extract Source Text's real output.
     3. `bundleextract.py` + `check-golden` (done): a Python port of Extract Source Text that gives byte-identical output on the golden pairs. Its description block lists the quirks a
        further port has to keep, e.g. `getStemFeatures()` caching the first root's features for the whole word, and complex forms being looked up on the variant-resolved entry.
     4. Port the runtime to C# against the same golden pairs (use a stable sort, e.g. `OrderBy`, where Python's `sort` is relied on), inside a .NET MAUI app hosting the React front end.
     5. The rest of the pipeline on the phone: HermitCrab parsing and synthesis (SIL.Machine), the guesser, and Apertium (compiled `bilingual.bin` and transfer rules).
   - An alternative worth a spike: running liblcm itself on the phone, which would avoid reimplementing what LCModel computes. Unproven on Android and iOS.
5. **Smaller items:**
   - A review command that lists inbox texts still unapproved.
   - Optionally, a genre tag for inbox texts.
   - Tests for `finish.py`'s file scanners using sample files.

The full plan is at `C:\Users\rlboo\.claude\plans\help-me-plan-the-purring-hummingbird.md`.
