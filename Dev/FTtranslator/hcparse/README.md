# HCParse: HermitCrab parsing for .NET 8

FTtranslator parses source words with FLEx's HermitCrab parser (FieldWorks' `HCParser`), which needs an open FieldWorks project and so only runs on Windows. HCParse does the same parse from
files, for .NET 8 on Linux.

## How it works

- **The grammar** is the HermitCrab `Language` that FieldWorks' `HCParser` builds from the project with `HCLoader`, using the project's parser parameters. `export-bundle` takes it from the
  `HCParser` that flexicon holds and writes it as `parser.xml`, so it's exactly the grammar the desktop parses with (see `fttranslator/parserexport.py`).
- **The project's objects:** HermitCrab results name the allomorph, msa and inflection type by hvo (a database handle). `export-bundle` writes `parser.json`, which maps those hvos to GUIDs
  in the same process that wrote `parser.xml`, plus the `Morpher` settings the desktop parser uses.
- **The parse:** `Program.cs` ports `HCParser.ParseWord()`, `GetMorphs()` and `ProcessParseException()` from FieldWorks' `Src/LexText/ParserCore/HCParser.cs`. The LCModel lookups become
  lookups in `parser.json`. The trace manager and FieldWorks shims are shared with `../hcsynth`. SIL.Machine is pinned to 3.9.5, the version FieldWorks 9.3.12 installs.

## Build and run

```
dotnet publish HCParse.Net8.csproj -c Release -o out
dotnet out/HCParse.dll parser.xml parser.json < words.txt > results.jsonl
```

Words go in one per line, prepared as FLEx prepares them (NFD, spaces as `.`). Each word gives one JSON line, written right away, so one process can stay running and parse words on demand:
`{"word", "error", "analyses"}`, where each analysis is a list of morphs `{"form", "entry", "msa", "inflType", "guessed"}` (GUIDs).

## How it was checked

`golden` (without `--text`) parses every wordform in the source project with the desktop parser and writes `parses.jsonl` in the same format. On 2026-11-03, for FTT-Scratch's 102 wordforms
(94 with parses, 2 parser errors), HCParse gave the same results on Windows and on Linux (WSL Ubuntu 22.04). Four words listed their analyses in a different order, which isn't
meaningful, so comparisons treat a word's analyses as a set.
