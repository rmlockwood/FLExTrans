# parse-prioritizing

A Python tool for experimenting with FieldWorks' **analysis guesser**. The guesser picks which parse
(WfiAnalysis) FLEx proposes for an unanalysed word in a text. With this tool you can see its ranking
for each occurrence, change the texts, and watch the ranking change.

## What the "most likely parse" component actually is

It is `SIL.LCModel.DomainServices.AnalysisGuessServices` in **liblcm**, not in the FieldWorks repo
([source](https://github.com/sillsdev/liblcm/blob/master/src/SIL.LCModel/DomainServices/AnalysisGuessServices.cs)).
FieldWorks calls it from `Src/LexText/Interlinear/InterlinVc.cs` (guesses shown in texts) and from
`ChooseAnalysisHandler.cs` and `SandboxBase.ComboHandlers.cs` (the order of the parse dropdowns).

It is a count-based model. Nothing is trained or stored. Every time it is asked, it recounts from the texts:

1. **Context score** = P(analysis | previous word) + P(analysis | next word). The counts are analyses
   already set on *other* occurrences of the same wordform in texts, next to the same neighbouring
   wordform. Punctuation counts as a neighbour, and so does a segment edge.
2. On a tie, **priority**: used in a text (7) > human-approved (6) > parser-approved (5) >
   computer-approved (4) > no opinion (3) > parser-disapproved (2) > human-disapproved (1).
   Human-disapproved analyses are left out entirely, except in Parsing Development mode.
3. Then the **count** at that priority, then a non-lowercased form, then the **GUID**. The GUID rule
   means a tie is settled arbitrarily.

In **Parsing Development mode** (`--parser-mode`), parser approval is checked before everything else.

So the way to change the most likely parse for a word in a given context is to **edit the texts**.
Set analysis B on occurrences of the word that have the same neighbours, either by analysing
existing occurrences or by adding sentences.

## Requirements

- Windows, FieldWorks 9.3+ (the tool loads its `SIL.LCModel.dll`)
- Python whose bitness matches FieldWorks, with `pyflexicon` (4.13 tested) and `pythonnet`
- **The project must be closed in FLEx**, unless you work on a copy (see `copy` below)

## Usage

Run with `python -m parse_priority <command> ...` from this folder.

| Command | What it does |
|---|---|
| `copy SRC NEW` | Copy a project to a scratch project. This works even while SRC is open in FLEx. |
| `analyses PROJ WORD` | List the word's analyses with numbers, approval status and in-text use. |
| `rank PROJ WORD [-n N] [--text T]` | For each occurrence, show its context, the guess FLEx would display, and the full ranking with the numbers behind it. |
| `assign PROJ WORD -n N -a K` | Set occurrence N to analysis K, then re-rank the other occurrences. |
| `add PROJ --text T "sentence" --assign word=K` | Append a sentence to a text (the text is created if missing) and set analyses in it. |
| `parse PROJ [--text T] [--save]` | Run the HermitCrab parser on each distinct word and list the parses, marking each as already in the project or NEW. `--save` files the results the way FLEx's *Parse Words in Text* does. Saving **cannot be undone**: it creates parser-approved analyses and can delete analyses that are unapproved and unused in texts. The guesser counts these approvals only when the project's active parser is HermitCrab. |
| `approve PROJ --text T` | Approve the guesser's top parse for every word in the text, as FLEx's *Approve All* does. All guesses are taken before any is applied. Each line shows the rule that decided it: context, priority, count, or a GUID tie. |
| `demo PROJ WORD -n N --to K [--max M]` | Add training sentences that copy occurrence N's neighbours, with WORD analysed as K, until N's top guess flips. |

An analysis `K` can be its number from `analyses`, a GUID prefix, or a substring such as `DEF` or `pro`.

**Write commands are dry runs by default.** They make the change, show the result, and then undo it.
Add `--commit` to keep the change. Assigned analyses are also marked human-approved, as FLEx does;
`--no-approve` turns that off. `--ignore-self` leaves the occurrence's own analysis out of the counts.
Without it, an analysed occurrence votes for itself.

### Workflow: new text → parse → approve the top guesses

```
python -m parse_priority add     PROJ --text "New text" "Le garçon la mange. Les filles mangent des bonbons." --commit
python -m parse_priority parse   PROJ --text "New text" --save
python -m parse_priority approve PROJ --text "New text"            # dry run: shows what would be approved
python -m parse_priority approve PROJ --text "New text" --commit   # keep it
```

### Example (French-ParsePriority)

```
> python -m parse_priority copy French-ParsePriority French-ParsePriority-Scratch
> python -m parse_priority demo French-ParsePriority-Scratch le -n 1 --to DEF

BEFORE: #1 Demo 2 ¶1 s1 w1
    context : [le] garçon joue avec un long train .
    FLEx guess: le:3SG.MASC.ACC [pro]          <- wrong: the only in-text use of 'le' is a pronoun
Training sentence: "le garçon."  (with 'le' = le:DEF.M.SG [def])
  after 1 sentence(s): top = le:DEF.M.SG [def]
AFTER:  FLEx guess: le:DEF.M.SG [def]
    1    1.00+1.00=2.00  in-text       1  le:DEF.M.SG [def]
    2    0.00+0.00=0.00  in-text       1  le:3SG.MASC.ACC [pro]
Rolled back (dry run). Use --commit to keep the changes.
```

## Layout

- `parse_priority/fw.py`: opens and copies projects, and loads the LCM types (through flexicon)
- `parse_priority/guesser.py`: finds occurrences, wraps `AnalysisGuessServices`, and re-computes the scores so they can be shown
- `parse_priority/textedit.py`: assigns analyses and adds sentences (parsed with `ParagraphParser`)
- `parse_priority/cli.py`: the commands

The ranking printed is always the C# service's own. The score columns come from a Python
re-computation for display. It doesn't model how the guesser merges capitalised and lowercase
wordforms, so for a sentence-initial capitalised word the numbers can differ from the order shown.
