# FTtranslator without Windows: session handoff (2026-10-30 to 11-04)

This Claude session started with "can FTtranslator run on a server like Railway?" and ended with FTtranslator translating on Railway with no Windows, FieldWorks or FLExTrans at run
time, the first milestone toward an offline phone app. The general FTtranslator handover (the desktop pipeline, `serve`, the coding decisions) is in [HANDOVER.md](HANDOVER.md).
Branch: `bundle-F-data-for-phone-use`.

## Session timeline

1. **Hosting on Railway (10/30).** Railway runs only Linux containers, and FTtranslator needed Windows throughout (FieldWorks/LCModel through pythonnet, `make.exe`, STAMP, the
   HermitCrab `.exe`s). Options given: a Windows machine you control behind a tunnel (Tailscale or Cloudflare), a Windows cloud VM, or porting. The React page can't run anything on its
   own; it only calls the Python server's `/api`. Splitting page (Railway) and API (Windows) was judged not worth it. Not acted on.
2. **Offline phone app (11/3).** Nothing in the stack runs on a phone, so the plan became: the desktop exports a **bundle**, and a slimmed-down pipeline runs on it. HermitCrab is in
   SIL.Machine (.NET Standard), so .NET MAUI hosting the existing React build is the natural phone shell. A Windows VM or Wine on a phone was judged impractical (x64 emulation inside a VM,
   FieldWorks never reliable under Wine, impossible on iOS).
3. **Extract Source Text port, planned and built.** Step 1, the lexicon export (`export-bundle`): checked against every lexical unit in Mato-Uma's real output (1,716 of 1,716 stem tags
   matched). Step 0, golden pairs (`golden`). Step 3, the port itself (`bundleextract.py`, `check-golden`): byte-identical on Mato, Toma and FTT-Scratch.
4. **Detours while testing the export.** Farsi-Team3-FW9 was dropped because it uses TreeTran (and turned up a likely FLExTrans bug, below). Toma-Zialo was tested through tod-flex1 via a
   scratch copy of its Config folder; 503 of 566 units matched an older `source_text-aper.txt` that looks hand-edited, and the golden pairs later matched 24 of 24.
5. **Review and a design question.** The review found a relative `--out` resolving under Config (fixed) and stale HANDOVER text (fixed). Ron asked whether the bundle could use the
   fwdata lexicon or the HermitCrab lexicon as is, so nothing could be missed. Answer: no. Much of what Extract Source Text reads is computed by LCModel (headwords, complex-form
   back-references, writing-system fallback), so using fwdata would move the risk into a reimplementation; the HermitCrab lexicon lacks complex forms, sense order and stable keys (its ids are
   hvos). The JSON export, built by calling FLExTrans' own `Utils`, was kept.
6. **"First get a Windows-free version working that I can take to Railway."** STAMP was ruled out (Ron: HermitCrab synthesis only; a Linux STAMP build attempt was stopped). Ported, each
   verified in turn: HermitCrab synthesis (.NET 8 build of FieldWorks' HCSynthByGloss), HermitCrab parsing (`hcparse`), the tokenizer, parse filing and guessing, transfer, and the
   synthesis steps after Apertium (done by a subagent).
7. **WSL couldn't reach the internet** (every outbound connection timed out, so `apt install apertium` failed). Ron chose to test the Linux Apertium tools on Railway instead.
8. **Server and deployment (11/3 to 11/4).** `serve-offline` written and tested locally; Dockerfile and `railway.toml` added; four Railway failures fixed (below); then cleanup made
   permanent on the server. Ron committed the work himself along the way.

## The idea in one paragraph

The desktop exports a **bundle**: a snapshot of everything translation needs from the work project, worked out by FieldWorks and FLExTrans' own code. Each pipeline step was then ported so it
runs from the bundle alone, and each port was checked against the desktop's real output (golden comparisons) rather than assumed. The chain is: tokenize → HermitCrab parse → file parses
and guess analyses → Extract Source Text → Apertium transfer → Convert to Synthesizer Format → HermitCrab synthesis. Python does the glue; the two HermitCrab pieces are .NET 8 programs
built from FieldWorks' source.

## Ron's decisions

- **HermitCrab synthesis only**, no STAMP. Export refuses a project with `HermitCrabSynthesis` not `y`, and One project mode.
- **Test pair: FTT-Scratch** (French-PP-FTT → Spanish-FTT-Scratch), switched to HermitCrab synthesis.
- **HermitCrab parsing was ported in milestone 1**, from the FieldWorks repo (it replaced an earlier "look up existing analyses" plan).
- **Sentence breaking is simplified:** break at the whitespace after a sentence-end character. The list is FLEx's `IsEndOfSentenceChar` code points (so other scripts' equivalents, such
  as the right-to-left question mark, count) plus `§` (U+00A7).
- **Guess ties between new parser analyses:** keep parse order ("option 1"). FLEx breaks these ties with random GUIDs, so the desktop's own choice there is random.
- **Linux Apertium tools were tested on Railway**, not WSL (WSL had no network to install them).
- **Deploy from git, this branch.** The FTT-Scratch bundle is committed in `deploy/bundle` for this test pair only; the repo is public, so a real project's bundle needs another route.
- **The server always cleans up unknown target words** (`CleanUpUnknownTargetWords=y`), whatever the project's setting.

## What was built, and how each piece was verified

| Piece | Files | Verified |
|---|---|---|
| Bundle export | `bundle.py`, `parserexport.py`, `guessexport.py`, `transferexport.py`, `synthexport.py`; `export-bundle` | The data each port below reads; all comparisons below use it |
| Extract Source Text | `bundleextract.py`; `golden`, `check-golden` (`golden.py`) | Byte-identical stream and messages on Mato-Uma (130 texts), Toma-Zialo (24), FTT-Scratch (9). A deliberately altered bundle made 93 Mato texts fail, so the check works |
| HermitCrab parser | `hcparse/` (.NET 8 port of FieldWorks' `HCParser.ParseWord`/`GetMorphs`) | Same parses as FLEx for all 6,729 Mato-Uma wordforms and 102 FTT-Scratch ones, on Windows and Linux (WSL), apart from analysis order |
| Tokenizer | `tokenizer.py` (port of liblcm's `ParagraphParser`/`WordMaker`) | Same words, punctuation and wordforms as FLEx on 15 tricky paragraphs (`golden --tokens`); Arabic, Devanagari and Ethiopic sentence ends tested |
| Parse filing + guesser | `analysisguess.py` (ports of `ParseFiler` and `AnalysisGuessServices`) | FTT-Scratch text 1: source stream byte-identical to the desktop. Edge-case text: 11 of 17 lines identical; the other 6 are the random-GUID ties above |
| Transfer | `transfer.py` (the makefiles' commands, without make) | Target stream byte-identical to the desktop with the Windows tools. Runs on Railway with Debian's tools; not byte-compared there |
| Synthesis | `synthesis.py` (HermitCrab half of `convert_to_STAMP` + `DoHermitCrabSynthesis`), `hcsynth/` (FieldWorks' HCSynthByGloss, unmodified, built for .NET 8) | From the same target stream, master, parses and surface files and the synthesized text identical to the desktop on two texts. `tests/test_synthesis.py` covers complex forms, clitics and variants, which FTT-Scratch lacks. hcsynth matched the Windows build on 15,720 Mato lines except the (random) order of alternative forms |
| Offline server | `offlineserver.py`; `serve-offline` | Same React page and API as `serve`. Locally, FTT-Scratch text 1 translated identically to the desktop, about 1.7 s |
| Synthesis DLL (11/4) | `synthesis.py` `loadHCSynthDll()`; `--hcsynth-dll` | `HCSynthByGlossDll` loaded once with pythonnet (CoreCLR), as Live Rule Tester does; config read once. Same surface file as the exe on Windows and Linux (WSL). Synthesis step 0.45 s → 0.06 s a request on FTT-Scratch |
| Text Out rules (11/4) | `textout.py` (port of TextInOutUtils' rule-applying code); `bundle.py` copies `TextOutRulesFile` as `text_out_rules.xml` | Applied after synthesis by `serve-offline` and `offline-stream --synthesize`. `tests/test_textout.py` runs the port beside the desktop's own functions (taken from its source with `ast`); on Mato-Uma's 46 real rules over 14 of its Build/Output files, identical. Not yet compared end to end on a HermitCrab project with rules (FTT-Scratch has none) |
| Deployment | `Dockerfile`, `railway.toml`, `.dockerignore`, `deploy/bundle/` | Builds and runs on Railway; translates FTT-Scratch |

Unit tests: `python -m unittest discover -s tests` (24 pass, no FieldWorks needed). Pyright is clean on the new files, also when checked as Python 3.11 (the image's version).

## Commands

Run from `Dev\FTtranslator`. The .NET 8 SDK is installed per-user in `%USERPROFILE%\.dotnet` (not on PATH); build hcparse and hcsynth with `dotnet publish -c Release` in each folder.

```
python -m fttranslator export-bundle WORKDIR [--out DIR]
python -m fttranslator golden WORKDIR [--text T] [--tokens FILE]
python -m fttranslator check-golden WORKDIR
python -m fttranslator offline-stream WORKDIR "Le garçon mange un bonbon." --hcparse "dotnet hcparse\bin\Release\net8.0\HCParse.dll" --synthesize --hcsynth "dotnet hcsynth\bin\Release\net8.0\HCSynthByGloss.dll" --tools "C:\Users\rlboo\Documents\FLExTransTOFT\FlexTools\Tools"
python -m fttranslator serve-offline --bundle deploy\bundle --hcparse "dotnet ...\HCParse.dll" --hcsynth-dll ...\HCSynthByGloss.dll --tools "...\FlexTools\Tools" --port 8799
```

`export-bundle` and `golden` need FieldWorks and read both projects (close them in FLEx or turn sharing on). Everything else needs neither.

## The bundle

Written to `<work project>\Output\ftt_bundle` (about 580 KB for FTT-Scratch):
- `manifest.json`: format version, date, work/source/target project names, record counts, the config values the runtime reads, the interface language passed to HCSynthByGloss.
- `lexicon.json`: entries, senses and msas keyed by GUID, with the strings Extract Source Text would build.
- `parser.xml` + `parser.json`: the source HermitCrab grammar (`XmlLanguageWriter`) and the FieldWorks ids hcparse maps results back to.
- `tokenizer.json`: word-forming characters, existing wordforms, phrases.
- `guesser.json`: each wordform's analyses with their approvals and contexts, representative msas, single-morpheme entries.
- `apertium/`: `bilingual.dix` and `tr.t1x` (and `t2x`/`t3x` for advanced transfer), as Run Apertium hands them to the tools.
- `synthesis/`: target affix gloss list, the conversion cache, the target `HermitCrab.config`.
- `text_out_rules.xml`: a copy of the Text Out rules file, when the project has one (the manifest's `files.textOutRules`; absent in older bundles, which then get no rules).

**To update Railway after changing the projects (11/4, later):** run `export-bundle`, then `upload-bundle WORKDIR --url https://….up.railway.app` with `FTT_PASSWORD` set. The server
holds several bundles in `/data/bundles/<work project>/` on a Railway volume (mount path `/data`), and the page has a drop-down to choose one. `deploy\bundle` (FTT-Scratch) is only the seed
copied in at start-up when the volume has no FTT-Scratch. See README's *Deploying to Railway* and SEVERAL BUNDLES in `offlineserver.py`.

## Railway

Service settings: **Root Directory** `/Dev/FTtranslator` (exactly; a trailing period broke one build). Optionally, **Config file path** `/Dev/FTtranslator/railway.toml` for the
`/api/health` health check and the watch path. Generate a public domain; the server listens on `$PORT`. **Variables:** set `FTT_PASSWORD`; every path but `/api/health` needs it
(HTTP Basic Auth, any user name), and the server won't start on `0.0.0.0` without it.

The image: .NET 8 SDK builds hcparse and hcsynth; Node 20 builds the page; the final stage is the .NET 8 runtime (Debian 12) with `python3`, pythonnet (pip), `apertium`, `lttoolbox` and
`lttoolbox-dev`. A build step checks that pythonnet can load HCSynthByGloss.dll, and the server runs with `--hcsynth-dll`.

Problems hit on the way, in order:
1. *Railpack could not determine how to build the app*: the Dockerfile was in `deploy/`, and Railway only reads `railway.toml` at the repo root unless its path is set. Fixed by moving
   the Dockerfile to `Dev/FTtranslator/`, where Railway finds it by name.
2. *directory …/Dev/FTtranslator. does not exist*: a trailing period in the Root Directory setting.
3. *No such file or directory: 'lt-comp'*: Debian's `lttoolbox` has only `lt-proc`; `lt-comp` is in `lttoolbox-dev`. The build now checks for every tool `transfer.py` runs.
4. *Nouns came out as `%0%^caramelo1.1<n><SG>$%`*: not a port bug. The desktop failed identically (see its `target_words-surface.txt`), but the Test Projects copy of FTT-Scratch has
   cleanup on, which hid it. Ron then fixed the Spanish project ("project tweaks for SG") and re-exported, and nouns now synthesize. The server now always cleans up.

**The page password (`FTT_PASSWORD`) is the only access control**, and translations reveal the lexicon. Anyone with it can use every bundle on the server, and upload or delete bundles
unless `FTT_UPLOAD_PASSWORD` is also set.

## Traps worth knowing

- **Two FTT-Scratch work projects exist:** `C:\Users\rlboo\Documents\FLExTransTOFT\WorkProjects\FTT-Scratch` (used for the comparisons; `CleanUpUnknownTargetWords=n`) and
  `C:\Data\FLExTrans\Dev\Test Projects\WorkProjects\FTT-Scratch` (`=y`). They share the FLEx projects. Check which one a result came from.
- **Desktop `translate` writes to the source project** (adds texts, files parses). Only run it on scratch projects, never on Mato-Uma.
- **HCSynthByGloss's order of alternative forms (`%2%a%b%`) is random** run to run, on Windows and Linux. Compare with that in mind.
- **New analyses get GUIDs `ffffffff-ffff-ffff-ffff-<n>`** so they sort after every real one; GUID string order equals .NET's `Guid.CompareTo` order.
- **`@` (unknown) words still go to HCSynthByGloss** (an off-by-one in FLExTrans' `createHermitCrabParsesFile()`); kept to match the desktop.
- **The Apertium transfer output has `\n\n` collapsed to `\n`**, as Run Apertium's unfix does.
- **Each request starts from the bundle**: one translation never affects the next. Run records are kept in memory only (last 200) and are lost on restart.
- **Never put Python in a Bash heredoc** in this environment (it hangs); write a script file and run it.

## Findings about FLExTrans and the projects themselves

- **Likely FLExTrans bug, worked out from the code but not run:** a config that sets `SourceDiscontigousComplexTypes` (and the skipped categories) but leaves
  `SourceComplexFormsWithInflectionOn1stElement` empty, as fa-bcc and fa-taj do, makes `processDiscontiguousComplexForms` call `par.findDiscontiguousComplexForms(...)`
  ([TextClasses.py](../Lib/TextClasses.py)), which doesn't exist anywhere in the repo. Extract Source Text should then fail with an AttributeError. `export-bundle` warns about this configuration.
- **Mato-Uma's `PHRASAL VERB` complex-form type contains a non-breaking space,** in FLEx and in `FlexTrans.config` alike, so they match. Retyping the setting with a normal space would
  silently stop phrasal verbs being substituted, on the desktop too.
- **Toma-Zialo's `Build\source_text-aper.txt` looks hand-edited** (`^zunu1.1<zzz><wknr><def>$`, one word with two inflection classes in one run). Don't use it as a reference.
- **HCSynthByGloss appends "Duplicate gloss(es) found …" to forms that did synthesize,** and FLExTrans leaves that text in the output.

## Not done / open items

- **Linux Apertium output not byte-compared** with the desktop's. Worth one comparison of a target stream from Railway against `Build\target_text-aper.txt`.
- **HCSynthByGloss and duplicate glosses:** the SG and PL glosses sat on 4 rules each (likely one affix in four template slots, so one entry), yet synthesis failed. Ron fixed the project
  instead; why HCSynthByGloss failed was not investigated.
- **Synthesis text 2:** one word differed in the full offline chain ("entre" guessed 1SG offline, 3SG on the desktop), upstream of synthesis. Not investigated.
- **Not exercised by any project:** discontiguous complex forms; TreeTran projects are refused.
- **The desktop `serve` still listens on localhost only.** Reaching it from other machines (a tunnel plus authentication) was discussed at the start but not done; the offline
  server took its place for Railway.
- **Real projects' bundles:** done (11/4) with a volume and `upload-bundle`. Still open: everyone with the page password sees every bundle (no per-bundle access), and the volume itself has
  to be added to the Railway service by hand.
- **Toward the phone:** port the Python runtime to C# against the same golden pairs (inside .NET MAUI hosting the React page), or package the Python + .NET pieces; the Apertium tools
  would need building for Android/iOS. HANDOVER.md's Phase 5 has the plan.

## Data outside the repo that this session changed

- FTT-Scratch (Documents copy) `Config\FlexTrans.config`: `HermitCrabSynthesis=y`.
- The .NET 8 SDK installed per-user in `%USERPROFILE%\.dotnet` (it also created an untrusted local HTTPS development certificate), and the .NET 8 runtime in WSL's `~/.dotnet`.
- A scratch work project for Toma-Zialo (a copy of its Config folder pointed at tod-flex1) in the session scratchpad; the real Toma-Zialo work project wasn't touched.
- French-PP-FTT has accumulated filed parses and `FTT …` texts from desktop comparison runs.
- Golden pairs and bundles live in each work project's `Output\ftt_golden` and `Output\ftt_bundle` (never committed, except `deploy/bundle`).
- Scratch scripts used for the comparisons are in this session's temp scratchpad and are not needed to reproduce anything; the commands above are.
