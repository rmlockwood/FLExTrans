# FTOffline: FTtranslator's offline translation in C#

FTOffline translates a text from an FTtranslator bundle (export-bundle's `Output\ftt_bundle`) with no Python, FieldWorks or FLExTrans: tokenizing, HermitCrab parsing, filing and guessing,
Extract Source Text, the Apertium transfer, HermitCrab synthesis and the Text Out rules, all in one .NET 8 process. It is a step-by-step port of the Python offline translator
(`fttranslator/offlineserver.py` and the steps it runs) and is checked against it, step by step, so a bundle translates the same way on a phone as on the Railway server. It is the
engine the phone app (`../phone`) calls: `new OfflineTranslator(bundleFolder).Translate(text)`.

## Layout

| Path | What |
|---|---|
| `FTOffline.csproj`, `*.cs` | The library, `FTtranslator.Offline.dll` |
| `cli/` | `ftoffline`, the command line |
| `tests/` | Unit tests (`dotnet test`), their fixtures, and the scripts that record the Python translator's steps |

The library compiles in hcparse's parser (`../hcparse/HcWordParser.cs`) and HCSynthByGlossDll with the FieldWorks shims (`../hcsynth`), and references FTApertium (`../apertium`), so each
step runs the same code the Python translator runs as a program or DLL. SIL.Machine is pinned to 3.9.5, as in hcparse and hcsynth.

| Step | C# | Ports |
|---|---|---|
| Import Text | `Tokenizer.cs` | `tokenizer.py` |
| Parse Words | `HcWordParser` (hcparse), `Guesser.ParseAndFile()` | hcparse, `analysisguess.py` |
| Approve Guesses | `Guesser.ApplyGuesses()` | `analysisguess.py` |
| Extract Source Text | `ExtractSourceText.cs`, `Lexicon.cs` | `bundleextract.py` |
| Run Apertium | FTApertium's `ApertiumTransfer` | `transfer.py` with the DLL |
| Synthesize Text | `Synthesis.cs` with HCSynthByGlossDll | `synthesis.py`'s DLL branch |
| Apply Text Out Rules | `TextOutRules.cs` | `textout.py` |
| the run record | `OfflineTranslator.cs` | `offlineserver.py`'s `OfflineTranslator` |

`PyStr.cs` and `FullCase.cs` give the ports Python's string behaviour where .NET's differs (`isspace()`, `splitlines()`, `title()`, full case mappings such as ß to SS), `TextDump.cs` is
the data the steps pass along, and `StageCheck.cs` is the comparison with the Python translator. Each file's header explains it.

## Build and use

```
dotnet build -c Release                 (the library, in bin/Release/net8.0)
dotnet build cli -c Release             (ftoffline, in cli/bin/Release/net8.0)
dotnet test tests -c Release            (the unit tests)
```

```
ftoffline translate <bundle> [text file] [--record]        the translation, or with --record the run record as JSON
ftoffline check <bundle> <stages folder> [differences]     compare every step with the Python translator's (see below)
ftoffline check-textout <cases.json>                       compare every Text In/Out rule found with textout.py's results
```

From C#: `using var translator = new OfflineTranslator(bundleFolder);` then `RunResult result = translator.Translate(text);`. The constructor loads everything once (about half a
second for FTT-Scratch, a second or two for Mato-Uma); `Translate()` is locked, since the parser and synthesizer are one per translator. A transfer rules error throws
`InvalidOperationException("FTApertium transfer failed: ...")`, as the Python raises; a synthesis or Text Out failure gives `Ok == false` with the message.

## How it is checked

**Step by step against the Python translator.** `tests/make_stages.py <bundle> <out folder> <texts or golden folder>` runs the Python offline translator over texts and saves every step's
result (tokens, each parse, the guessed text dump, source stream, target stream, the synthesis work files, the synthesized text, every message and the run record), one JSON per text, outside
the repo. `ftoffline check <bundle> <that folder>` translates the same texts and compares every step. On 11/6/26:

| Project | Texts | Identical at every step |
|---|---|---|
| FTT-Scratch (golden texts) | 13 | 13 |
| Mato-Uma (golden texts) | 130 | 130 (14 of them fail in transfer, the same way in both: Mato-Uma's rules error, see apertium/README.md) |

**The Text Out rules, wider.** `tests/make_textout_cases.py` finds every Text In/Out rules file under `C:\Data\FLExTrans` and the TOFT work projects and every synthesized target text, and
applies each distinct rule, and each distinct file as a whole, with `textout.py`; `ftoffline check-textout` does the same in C#. On 11/6/26: 212 distinct rules (83 regular expressions)
from 90 files (21 distinct) over 73 texts, 17,009 applications, all identical.

**Unit tests** (`dotnet test` in `tests/`): five FTT-Scratch texts translated from `../deploy/bundle` and compared step by step, a Text Out rules file written to hit what the port has to get
right (`\w` with a ZWNJ, `\b`, `\Z`, ß, Greek final sigma, an inactive rule, a failing rule), and Python's string behaviour. `tests/make_fixtures.py` makes their expected output with the
Python translator; run it again after changing a fixture, `deploy/bundle` or the Python translator, and commit what it writes.

## What the port turned up

- **The offline translator could translate the same text two ways.** HermitCrab gives a word's parses in a different order from run to run. Parses that match no existing analysis
  become new analyses, numbered in parse order, and when two of them tie on everything else the guesser takes the lower number, so the guess depended on the order. Mato-Uma's "Hainga"
  changed between two Python runs, and the translation with it. Both translators now file a word's parses in a fixed order (`parseSortKey()` in `analysisguess.py`, `ParseOrder` in
  `Guesser.cs`). The desktop isn't affected the same way: FieldWorks gives a new analysis a random GUID once, and keeps it.
- **Python's `\w` is wider than .NET's.** Python's regex module counts spacing marks (Devanagari vowel signs), letter numbers, the zero-width joiner and non-joiner and circled letters as
  word characters; .NET doesn't. One real target text had a ZWNJ inside words. `TextOutRules.PythonPattern()` rewrites `\w`, `\W`, `\b`, `\B` (and `\Z`, which in .NET also matches before
  a final newline) with Python's meaning.
- **.NET's regex engine can be slow on a common rule shape.** `([^.?;:!]+?)MARKER(...)` took a second on a 9 KB Toma-Zialo text (Python: a millisecond), since .NET starts a match at every
  position and scans to the next punctuation each time. Rules now use .NET's non-backtracking engine where the pattern allows (under a millisecond, same matches); the whole Text Out check went
  from over an hour to two seconds.
- **Limits that no project hits yet:** .NET matches by UTF-16 code unit, so in a script outside the BMP (Adlam, Osage) `.` and `\w` see half a character; and the regex module's own syntax
  (`(?P<name>...)`, possessive `a++`, `\X`, `\N{...}`, `[[:alpha:]]`, `\p{Greek}`) fails as a bad rule would. No rule on this machine uses either.
- **HCSynthByGloss lists an ambiguous word's forms in a different order from run to run** (`%2%sulen%sulin%` or `%2%sulin%sulen%`), on the desktop too, and the order shows in the
  translation and in which form the run record's unsynthesized words list. It is upstream (FieldWorks' HCSynthByGloss), so the port leaves it; `ftoffline check` compares those forms as a set.
- **Where the time goes:** in SIL.Machine's HermitCrab, parsing and synthesis. FTT-Scratch: about 0.3 s a text. Mato-Uma's golden texts are whole chapters with a thousand-odd distinct words:
  27 s a text (median; 0.8 to 72 s) on this PC, nearly all of it parsing, and synthesis about 3 s of that. The Python translator takes as long. A phone will be slower, so long texts will
  need parsing results kept between texts, or the app limited to a verse or paragraph at a time.

## Not ported

The parts of the Python translator only the server needs (the bundle folder, uploads, the web API and its password) stay in Python; a phone app would hold its bundles itself. Synthesis
uses HCSynthByGlossDll only (the Python can also run the HCSynthByGloss program), and transfer FTApertium only.
