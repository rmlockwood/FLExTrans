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
python -m fttranslator steps     WORKDIR     # the pipeline that would run
python -m fttranslator check     WORKDIR     # projects, tools, active parser
python -m fttranslator runs      WORKDIR     # earlier runs and their failed words
```

- If neither TEXT nor `--file` is given, the text is read from stdin. Each line becomes a paragraph.
- `--timing` prints how long each step took and the total time, on stderr. `-v` prints them too.
- `--insert` also runs Insert Target Text, which puts the translation into the target project. Otherwise that collection step is skipped.
- `--modules` points at a FLExTrans modules folder. The default is the installed `…\FlexTools\Modules\FLExTrans` next to the work project. `--modules dev` uses this repo's own `Dev\Modules`. Any other path to a modules folder also works.

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
- `fttranslator/translator.py`: the `Translator` API, which the CLI uses and which a service or web app can use too.
- `parse_priority/`: the parser and guesser tools that the ingest steps are built on.
- `tests/`: `python -m unittest discover -s tests`. These tests don't need FieldWorks.
