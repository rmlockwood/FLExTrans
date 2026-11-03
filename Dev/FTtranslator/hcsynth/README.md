# HCSynthByGloss for .NET 8

FLExTrans's HermitCrab synthesis runs `HCSynthByGloss`, which comes with FieldWorks and targets .NET Framework 4.8, so it only runs on Windows. This folder builds the same program for .NET 8,
so FTtranslator can synthesize on Linux (for example in a Docker image on Railway).

## What's here

- `upstream/`: FieldWorks' `Src/Utilities/HCSynthByGloss` source at commit `bd0608da7f46a7ba084d93fabca61a99dae5f0da` (2026-10-08), **unmodified**. That is the latest change before the
  `HCSynthByGlossDll.dll` installed with FieldWorks 9.3.12 was built (2026-10-13). The only later change (2026-10-21) is to tracing. The source is LGPL 2.1 or later, as its headers say.
- `FieldWorksShims.cs`: stands in for the two FieldWorks pieces the source uses: four `HCParser` string constants and `XmlUtils.CreateTransform()`, which is only used to show a trace as HTML
  (`-t`) and throws here.
- `HCSynthByGloss.Net8.csproj`: builds `upstream/` and the shims against SIL.Machine 3.9.5, the HermitCrab engine version that FieldWorks 9.3.12 installs.

## Build and run

```
dotnet publish HCSynthByGloss.Net8.csproj -c Release -o out
dotnet out/HCSynthByGloss.dll en -h HermitCrab.config -g parses.txt -o surface.txt
```

The arguments are the same as the Windows `HCSynthByGloss.exe` takes. The HermitCrab config is the one FLExTrans's Generate HC Config writes into the work project's `Build` folder.
Generating it needs FieldWorks, so it's made on the desktop and copied over. Only reading it happens here.

## How it was checked

Both builds were run on the same config and parses files (2026-11-03):

- FTT-Scratch (12 words) and Mato-Uma's last run: identical output.
- 15,720 generated lines from Mato-Uma's target config (every lexical entry, alone and with up to four affixes its category accepts, 2,610 of them failing): 15,709 lines identical. The other
  11 are words with two possible forms (`%2%a%b%`) listed in a different order.

That order isn't stable in the Windows build either: three runs of the original on the 23 ambiguous words gave three different orders, and so did three runs of this build. So output
comparisons must treat the forms in a `%n%...%` group as a set.
