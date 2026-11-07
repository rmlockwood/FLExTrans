# HC Spike: HermitCrab parsing in a .NET MAUI app (throwaway)

Answers one question before any phone-app work: does SIL.Machine's HermitCrab parser load and parse on a phone? Android only so far; iOS needs a Mac.

The app compiles hcparse's parser unchanged (`../hcparse/HcWordParser.cs`; the results below were measured when it was still private in `Program.cs` and reached through reflection, before
the parser was made a public class for FTOffline), loads FTT-Scratch's `parser.xml` and `parser.json` from
`../deploy/bundle`, and parses the 102 wordforms in `Resources/Raw/words.txt` (the words of the desktop `golden` run). It runs once on start and logs a `HCSPIKE` line to logcat.

## Results (2026-11-06, Galaxy S9 SM-G960F, Android 10, arm64; SIL.Machine 3.9.6)

| Build | Result | Load | Parse 102 words |
|---|---|---|---|
| Debug | 102 of 102 words identical to Windows and to FLEx's golden parses | 2.3 s | 8.7 s |
| Release (default partial trimming, profiled AOT) | 102 of 102 identical | 0.95 s | 3.6 to 3.9 s |
| Release, `TrimMode=full` | Crashes at start-up in MAUI's own `Microsoft.Extensions.Logging` before any spike code runs | | |

Windows, for comparison: the whole `hcparse` process (start, load, 102 words) takes about 2.5 s. Comparisons treat each word's analyses as a set.

Findings:
- None of the 42 trim warnings in the full-trim build come from SIL.Machine; they're all from the spike's reflection and hcparse's reflection-based `System.Text.Json`. A real app would
  make `ParseWord` callable directly and use source-generated JSON.
- SIL.Machine pulls in two native libraries. `Mono.Unix` ships Android and iOS builds. `PCRE.NET` ships none, and the build packs its desktop-Linux arm64 library, which can't load on
  Android; parsing never touched it here. Both are flagged as not built for Android 16's 16 KB pages.

## Build and run

```
dotnet build -f net10.0-android -c Release -p:AndroidSdkDirectory=%LOCALAPPDATA%\Android\Sdk
adb install -r bin/Release/net10.0-android/org.sil.fttranslator.hcspike-Signed.apk
adb shell am start -n org.sil.fttranslator.hcspike/crc640468a447078f6aed.MainActivity
adb logcat -d | grep HCSPIKE
adb exec-out cat /sdcard/Android/data/org.sil.fttranslator.hcspike/files/results.jsonl > phone.jsonl
```

A Debug APK installed with `adb install` needs `-p:EmbedAssembliesIntoApk=true`; otherwise it expects fast deployment and exits at start. In Git Bash, set `MSYS_NO_PATHCONV=1` for the
`/sdcard/...` path.
