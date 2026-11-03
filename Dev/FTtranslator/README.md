# FTtranslator

FTtranslator translates a text from end to end with FLEx and FLExTrans, without FlexTools. You give it source text and it prints the target text.

It lives in the FLExTrans repo at `Dev\FTtranslator`. Run the commands from that folder.

```
> python -m fttranslator translate "…\WorkProjects\French-Spanish Demo" "Les filles mangent des bonbons."
Los niños comen de los caramelos.
```

The translation goes to stdout. Progress and the words that failed go to stderr.

## How it works

A **profile** is an ordinary FLExTrans work project:
- `Config\flextools.ini` (`currentproject`) names the source project.
- `Config\FlexTrans.config` holds the rest (target project, rules, file paths).
- `Config\Collections\Drafting.ini` gives the steps.

The pipeline:

| # | Step | What it does |
|---|---|---|
| 1 | Import Text | Adds the text to the source project as a new text, titled `FTT <date time> <first three words>` |
| 2 | Parse Words | Parses each word with HermitCrab and files the results, as FLEx's *Parse Words in Text* does |
| 3 | Approve Guesses | Approves the guesser's most likely analysis for each word in context, as *Approve All* does (`AnalysisGuessServices`, see [parse_priority_README.md](parse_priority_README.md)). Each morph is given a sense, as FLEx does when a parse is confirmed |
| 4… | the collection | Each entry of the Drafting collection, in order. The standard FLExTrans modules run their core functions directly, the same calls `TranslateText.py` makes. Any other entry runs as a FlexTools module |
| last | Collect Output | Reads the synthesis output and applies the Text Out rules. It lists unanalysed words, words with no link to the target lexicon, and words that failed to synthesize |

**Approvals are temporary by default.** The guesser counts in-text analyses most, so approved mistakes would reinforce themselves in later translations. After Extract Source Text, FTtranslator undoes the approvals. The new text stays in the source project with its words unapproved. FLEx shows the same guesses there, and when someone confirms them in FLEx they become part of the corpus. Use `--keep-approvals` to keep them, as FLExTrans users normally do.

Every run is saved as JSON in `<work project>\Output\ftt_runs\`. The file holds the source and translation, each word's chosen analysis and why it was chosen (context, priority, count or a GUID tie), the failed words, all messages, and how long each step took. Use `runs` to list them. This is the start of the loop for improving the translator.

## Commands

```
python -m fttranslator translate WORKDIR [TEXT] [--file F] [--title T] [--insert] [--keep-approvals] [--json OUT] [--modules] [--timing] [-v]
python -m fttranslator interactive WORKDIR [--insert] [--keep-approvals] [--timing] [-v]
python -m fttranslator serve     WORKDIR [--port N] [--no-browser] [-v]
python -m fttranslator steps     WORKDIR     # the pipeline that would run
python -m fttranslator check     WORKDIR     # projects, tools, active parser
python -m fttranslator runs      WORKDIR     # earlier runs and their failed words
python -m fttranslator export-bundle WORKDIR [--out DIR] [-v]
python -m fttranslator golden    WORKDIR [--text T]... [--out DIR] [-v]
python -m fttranslator check-golden WORKDIR [--bundle DIR] [--golden DIR] [--show N]
python -m fttranslator offline-stream WORKDIR [TEXT] [--file F] [--bundle DIR] --hcparse CMD [--transfer] [--tools DIR] [--synthesize --hcsynth CMD] [--synth-dir DIR]
python -m fttranslator serve-offline --bundle DIR --hcparse CMD --hcsynth CMD [--tools DIR] [--host H] [--port N] [-v]
```

- If neither TEXT nor `--file` is given, the text is read from stdin. Each line becomes a paragraph.
- `--timing` prints how long each step took and the total time, on stderr. `-v` prints them too.
- `interactive` waits at a `>` prompt. Type a sentence and press Enter to get its translation, then type the next. Each sentence becomes its own text. Only the answer and any failed words are shown; `-v` also shows the tools' output. The projects stay open for the whole session, so the first sentence takes about 5 s and each later one about 0.5 s. Press Ctrl+C (or Ctrl+Z then Enter) to stop. Ctrl+C during a translation stops once that translation is finished, so the projects are saved and closed.
- `serve` does the same as `interactive`, but in the browser. It starts a local web server at `http://localhost:8765/` and opens the page there. Type a sentence and press Enter. Each result
  shows the translation, the failed words, and, folded away, the analyses chosen, the messages and the step times. A **Saved runs** tab lists the run records. The projects stay open until you
  press Ctrl+C in the console. The page has to be built once first; see [The web front end](#the-web-front-end).
- `--insert` also runs Insert Target Text, which puts the translation into the target project. Otherwise that collection step is skipped.
- `export-bundle` writes the offline translation bundle, a snapshot of the work project for a translator that runs without FieldWorks (on a Linux server now, eventually a phone app): the
  source lexicon data, the source HermitCrab parser, the tokenizer and guesser data, the bilingual lexicon and transfer rules, and the target synthesis data. It goes to
  `<work project>\Output\ftt_bundle\` or to `--out`. It reads the source and target projects; only HermitCrab synthesis is supported.
- `offline-stream` translates a text from the bundle alone, with no FieldWorks or FLExTrans, and prints the Apertium stream; `--transfer` prints the target stream and `--synthesize` the
  synthesized text. `--hcparse` and `--hcsynth` are the commands that run the .NET 8 builds in `hcparse\` and `hcsynth\` (e.g. `"dotnet ...\HCParse.dll"`). `--tools` is the folder with the
  Apertium tools (`FlexTools\Tools` on Windows; on Linux they are found on PATH).
- `serve-offline` is `serve` from a bundle alone: the same page, translating with the `offline-stream --synthesize` chain. It writes to no project. See [Deploying to Railway](#deploying-to-railway).
- `golden` captures test data for a translator that reads the bundle. For each text (or each `--text` title) it saves the text's analyses as `NNN.text.json` and what Extract Source Text
  really produced from them as `NNN.expected.txt`, with an `index.json` listing the titles and messages. It writes to `<work project>\Output\ftt_golden\` or to `--out`, and also only reads the
  source project. TreeTran projects are refused by both commands.
- `check-golden` runs FTtranslator's own Extract Source Text, which works from the bundle and needs no FieldWorks, on every golden pair. It reports how many texts give identical output
  and messages, and shows where the first few differences are. It exits with 1 if any output differs.
- `--modules` points at a FLExTrans modules folder. The default is the installed `…\FlexTools\Modules\FLExTrans` next to the work project. `--modules dev` uses this repo's own `Dev\Modules`. Any other path to a modules folder also works.

## The web front end

The page is a React app in `web\`. It needs Node.js 20 or later to build, but not to run. Build it once, and again after changing it:

```
cd web
npm install
npm run build
```

This writes `web\dist`, which `serve` serves. Neither `web\dist` nor `web\node_modules` is committed.

To work on the page, run `serve` and `npm run dev` side by side. Open the address Vite prints (`http://localhost:5173/`). It reloads on every edit and passes `/api` requests to the server on
port 8765. Set `FTT_PORT` if the server is on another port.

The server's API (`fttranslator/server.py`):

| Request | What it does |
|---|---|
| `GET /api/status` | Work project, source and target projects, whether the projects are open yet, and how many texts this session has translated |
| `POST /api/translate` | Body `{text, insert, keepApprovals}`. Translates the text and returns `{result, record}`: the run record and where it was saved |
| `GET /api/runs?limit=N` | The saved run records, newest first |

The server listens on 127.0.0.1 only. It answers one request at a time, on the thread that opened the projects. A POST must send `Content-Type: application/json`, and the `Host` header
must be `localhost` or `127.0.0.1`. These checks stop other web pages open in the browser from starting a translation, which writes to the FLEx projects.

## Deploying to Railway

`deploy\Dockerfile` builds a Linux image that runs `serve-offline`: the .NET 8 SDK builds hcparse and hcsynth, Node builds the page, and the final image is the .NET 8 runtime with Python 3
and Debian's `apertium` and `lttoolbox` packages. The bundle it serves is `deploy\bundle\`, a copy of a work project's `Output\ftt_bundle\`. It is committed for the FTT-Scratch test pair only,
since a bundle holds the project's lexicon and the repository is public.

In Railway, create a service from this repository and branch, then in its settings:
- **Root Directory:** `/Dev/FTtranslator`
- **Config file path:** `/Dev/FTtranslator/railway.toml` (Railway doesn't look under the root directory for it). It selects the Dockerfile, rebuilds only when `Dev/FTtranslator` changes,
  and uses `/api/status` as the health check.
- **Networking:** generate a public domain. The server listens on Railway's `$PORT`.

To update the translations after changing the projects, run `export-bundle` again, copy `Output\ftt_bundle\` over `deploy\bundle\`, and push. Anyone with the address can translate, so
deploy only a bundle that may be public.

## Customizing

Optional `Config\fttranslator.ini`:

```ini
[fttranslator]
collection = Drafting        ; which collection to run
title_prefix = FTT
source_project =             ; override flextools.ini

[hooks]
; Python callables run before/after a step (by name or module file):  func(ctx) -> bool
after: Run Apertium = my_fixups:adjust_transfer_output
```

You can add custom code in two ways:
- **FlexTools module.** Add it to the collection, as in FlexTools. The entry can be a path relative to `FlexTools\Modules` or to the work project's `Config` folder (for example `[Modules\MyStep.py]`), or `Folder.FTM_Name`. The module gets the source project (a flexlibs `FLExProject`) and the report, and `ReadConfig.readConfig()` returns this run's configuration.
- **Hook.** A function in a `.py` file in `Config` (or anywhere on `sys.path`). It gets the whole `Context`: `ctx.db` (flexicon, undoable), `ctx.ftDb` (flexlibs), `ctx.configMap`, `ctx.result` and `ctx.state`.

Steps pass data to each other through FLExTrans' usual files (`Build\source_text-aper.txt`, `Build\target_text-aper.txt`, …). A custom step usually reads or rewrites one of these files.

## Requirements

- Windows, FieldWorks 9.3+, Python 3.13.
- An installed FLExTrans: the modules plus `FlexTools\Tools`, which holds make, Apertium and STAMP. The HermitCrab synthesis exes must be on PATH if you use them.
- `flexlibs`, `pyflexicon`, `flextoolslib`, `pythonnet` and `PyQt6`. Qt runs offscreen, so no window opens.
- The source project's active parser should be HermitCrab. Run `check` to confirm.
- Both projects must be closed in FLEx, or sharing must be turned on.

## Layout

- `fttranslator/env.py`: makes FLExTrans run outside FlexTools. It sets the working directory, `sys.path`, Qt offscreen, FieldWorks initialisation, and turns Mixpanel off.
- `fttranslator/profile.py`: work project + `fttranslator.ini`.
- `fttranslator/pipeline.py`: `Context`, `Step`, building from the collection, running.
- `fttranslator/steps/`: `ingest.py` (import, parse, approve, release), `flextrans.py` (drafting steps, FlexTools modules), `finish.py` (output and failed words).
- `fttranslator/translator.py`: the `Translator` API, which the CLI uses and which a service or web app can use too. It keeps both projects open from the first `translate()` until `close()` (or the end of a `with` block).
- `fttranslator/sharedtarget.py`: hands every FLExTrans module that opens the target project the one copy that is already open.
- `fttranslator/server.py`: the `serve` command's web server and JSON API, around one `Translator`.
- `fttranslator/bundle.py`: the `export-bundle` command's exporter. It writes the source lexicon data that Extract Source Text needs, worked out with FLExTrans' own `Utils` functions.
- `fttranslator/golden.py`: the `golden` command's capture of test pairs: each text's analyses next to Extract Source Text's real output.
- `fttranslator/bundleextract.py`: Extract Source Text without FieldWorks or FLExTrans, from a bundle and a text's analyses. A line-for-line port and the reference for a C# version. `check-golden` runs it.
- `web/`: the React front end (Vite + TypeScript). `src/App.tsx` is the page, `src/ResultCard.tsx` shows one translation, and `src/api.ts` calls the server.
- `parse_priority/`: the parser and guesser tools that the ingest steps are built on.
- `tests/`: `python -m unittest discover -s tests`. These tests don't need FieldWorks. `test_bundleextract.py` covers `bundleextract.py` on a small made-up lexicon.
