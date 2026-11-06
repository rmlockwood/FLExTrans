# FTApertium: FLExTrans' Apertium transfer step in C#

FTApertium does what FLExTrans' Run Apertium does with the Apertium tools, without the tools: the bilingual lookup (`lt-proc -b -N1 -L1`) and the rules stages (`apertium-transfer -b -t`,
and for advanced transfer `apertium-interchunk -t` and `apertium-postchunk -t`). It reads `bilingual.dix` and the `.t1x`/`.t2x`/`.t3x` files directly, with no compile step, and is checked byte
for byte, output and `-t` trace, against the Windows tools FLExTrans ships (lttoolbox 3.8.3, and an Apertium build from after July 2025).

It is plain .NET 8, with no native code, ICU or libxml2, so the same transfer runs on Windows, in FTtranslator's Linux image (no Apertium packages) and, later, in a phone app.

## Layout

| Path | What |
|---|---|
| `FTApertium.csproj`, `*.cs` | The library, `FTtranslator.Apertium.dll` |
| `cli/` | `ftapertium`, the command line |
| `tests/` | Unit tests (`dotnet test`), their fixtures, and the scripts that make reference output with the Windows tools |

The library's files: `ApertiumTransfer.cs` (the entry point: lookup plus rules stages), `Bilingual.cs`, `LtStreamReader.cs` and `RegexBuilder.cs` (the lookup), `TransferRules.cs` and
`TransferRun.cs` (the rules stages), `CaseUtils.cs` (lttoolbox's case functions), and `ReferenceCheck.cs` (the comparison with the tools' output). Each file's header explains it.

## Build and use

```
dotnet build -c Release                 (the library, in bin/Release/net8.0)
dotnet build cli -c Release             (ftapertium, in cli/bin/Release/net8.0)
```

**From FTtranslator** (the normal way): `offline-stream --transfer` and `serve-offline` load `bin/Release/net8.0/FTtranslator.Apertium.dll` into Python with pythonnet, or the DLL named
with `--apertium-dll`; `--apertium-tools` goes back to the Apertium programs. See THE TWO WAYS in `fttranslator/transfer.py`.

**From the command line:**

```
ftapertium transfer <apertium folder> tr.t1x [tr.t2x tr.t3x]   < source stream > target stream     (traces on stderr)
ftapertium lookup <bilingual.dix>                              < source stream > bilingual stream
ftapertium check <reference folder> [case]
```

**From C#:** `new ApertiumTransfer(folder, "tr.t1x").Transfer(stream)`; `Log` holds the traces, and an error where an Apertium tool would stop is a `TransferException` with the tool's message.

## How it is checked

**Unit tests** (`dotnet test` in `tests/`, and `tests/test_transfer.py` on the Python side): the fixtures in `tests/fixtures` are small inputs written to exercise what the real projects
don't, with their expected output made by the Windows tools (`tests/make_fixtures.py`). They cover, among others, a key with two translations, weights, regular expressions, escaped
characters, `modify-case`, the `-list` tests, `case-of`, `link-to`, the `lemh`/`lemq`/`tags` parts, title-casing through `get-case-from`, chunks and their `<N>` tag references, `lu-count`,
and a rules error. Run `make_fixtures.py` again after adding or changing a fixture, and commit its output with it.

**Real projects:** `tests/make_reference.py` runs every distinct rules file under each work project (current file, rule history, backups, Live Rule Tester copies) over the project's source
stream with the Windows tools, into a folder outside the repo (it holds the projects' data); `ftapertium check <folder>` then compares. On 11/6/26, across Active Projects, Test Projects,
the TOFT work projects and the Testbed:

| Stage | Streams | Identical output | Identical trace |
|---|---|---|---|
| lookup | 281 | 281 | |
| transfer | 284 rules files, 75 projects | 284 | 284 |
| interchunk | 11 (kmr-zza-chunk, EN-SV VBox Jump) | 11 | 11 |
| postchunk | 11 | 11 | 11 |

Mato-Uma's 130 golden texts also match (lookup 130/130, transfer 118/118), and the 12 where `apertium-transfer` stops on Mato-Uma's rules fail the same way.

## How it works

**Lookup** (`Bilingual.cs`): the dictionary becomes an in-memory transducer (a trie of input:output symbols, plus fragments for `<re>`), and each word is stepped through it as lttoolbox's
`FSTProcessor::bilingual()` steps through the compiled one: an uppercase letter may also step as its lowercase form, which marks the path for recasing; the longest match wins, and the tags
after it are carried over; a word without tags only counts on a complete match; a word not found comes back as `source/@source`. With `-N1`, ties between translations go by file order, as the
tools' choice did on every case tested.

**Rules** (`TransferRules.cs`, `TransferRun.cs`): every rule's pattern goes into one automaton (`^`, the category's items, `$`, an optional blank between words), run as a set of states. The main
loop is a port of Apertium's, quirks included: rules are applied at the longest match and the input rewound after it, the lowest rule number wins a tie, and transfer hands a rule every
word read so far. Expressions are compiled once per XML element, and macro calls swap in their words. Interchunk and postchunk share the loop and most of the interpreter (see THE THREE MODES in
`TransferRun.cs`).

Not ported, since no FLExTrans file uses them (each stops with a clear error): `mlu`, `reject-current-rule`, `[[word-bound blanks]]`.

## What the port turned up

- **Advanced transfer drops or replaces word tags that start with a digit.** Postchunk treats any `<N...>` tag inside a chunk as a reference to the chunk's Nth tag, reading N with
  `sscanf("%d")`, so `<3sg_cond>` counts as `<3>`. In kmr-zza-chunk, `^ch_v<V>{^vîyartiş1.1<vpst><3sg_cond>$}$` comes out of postchunk as `^vîyartiş1.1<vpst>$` (the chunk has no 3rd tag),
  and `da1.1`'s `<3sg_cond>` became `<3sg_m>`. FTApertium does the same, as it must to match.
- **Mato-Uma's `tr.t1x` stops `apertium-transfer` on 12 of its 130 texts** ("unexpected expression: 'with-param'"). `mProcessNoun`, last changed by AI Rule Studio, calls
  `m_map_noun_lemma_by_genitive` with string arguments, and the macro reads them back with `<get-case-from pos="1"><with-param pos="1"/></get-case-from>`; Apertium macros only take matched
  words. `apertium-preprocess-transfer`, which AI Rule Studio's validation relies on, accepts the file. (`tests/fixtures/error` is the same mistake in small.)
- **The Windows `lt-proc` writes `\n` as `\r\n`**, a C runtime artifact the Linux build doesn't have. It never shows on FLExTrans' own streams, which already have `\r\n` on Windows; FTApertium
  keeps line ends as they come in.
