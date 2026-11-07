# FTtranslator for phones

Type a sentence, tap Translate, get the translation. It's translated on the phone by FTOffline (`../offline`), from a bundle on the phone, so no network is needed (the app asks for no
permissions). The phone can hold several bundles, one per language pair, and switch between them. Android only so far; iOS needs a Mac.

## The screen

The normal screen is only the translation and the history:

- A text box at the top. Each line in the box is a paragraph. The text stays in the box after translating, so it can be changed a little and translated again.
- Right under the box, the current translation, in large type on a tinted panel so it's easy to find. Tap it to copy it.
- Then the language pair (`French → Spanish ▾`) and Translate. While a translation runs, the button says "Translating…" and the old answer is dimmed. Tap the language pair to switch
  bundles (see **Bundles** below).
- Below that, the earlier translations, newest first. Each card shows the source in small grey type and the translation under it, or in red why it failed. Tap a card to copy its
  translation. Swipe it right to put its source back in the box, or left to delete it.
- Each language pair has its own history, kept between runs (the last 500 translations, all pairs together). **⋮ → Clear history** deletes the current pair's.

The language names come from the bundle's manifest (`sourceLanguage` and `targetLanguage`, written by export-bundle from each project's default vernacular writing system). A bundle
exported before export-bundle wrote them shows the project names instead.

**Trace mode** (**⋮ → Trace mode**, remembered) counts the seconds on Translate while a translation runs (once a second: see below), and adds a **Trace** section under the current translation
(open) and on each earlier one (tap **▸ Trace** to open it). It's laid out like the result card on the web page:

- a header line: the bundle and when, the total time, and an **OK** badge (or **Failed after** the step, in red);
- the problem words as chips: no parse, no analysis, not linked, not synthesized;
- **Analyses chosen**: a table of each word, its analysis and why it was chosen;
- **Messages**: every message (no "Show all" checkbox), warnings and errors coloured;
- **Step times**: each step with a bar, the time outside the steps, and the total;
- and two the web page doesn't have: **Apertium streams** (the source and target streams; closed at first) and the **Exception** when a step threw one.

Each section folds open and closed with a tap on its ▾ heading.

Every translation records all of this except the streams, so turning trace mode on also shows the trace of translations made with it off. The streams are kept only for translations made in
trace mode: a chapter's run to tens of KB, and the whole history file is rewritten after each translation.

**What trace mode costs.** Capturing the trace costs nothing measurable: the same Mato-Uma sentence on a Galaxy S9 took 4.0–4.8 s with trace mode on or off, and the run-to-run spread
(about ±0.5 s) is far bigger than the capture. The seconds counter did cost: updated ten times a second, it made the phone lay the whole page out again each time, and the sentence took 6.1 s
on average instead of 4.2 s. It now updates once a second, which costs nothing measurable either (4.2–4.9 s). The trace's step times are the exact figures.

## Bundles

A bundle is one language pair's translation data: export-bundle's `Output\ftt_bundle` folder. The phone keeps each in its own folder, named after its work project. A bundle of a work project
the phone already has is an **update** of it.

- **Switch** with a tap on the language pair, or **⋮ → Language pair…**. The app remembers the choice. Only one bundle is loaded at a time (a big one takes a lot of memory), so switching takes
  the few seconds a load takes.
- **Add or update** with **⋮ → Add or update a bundle…**, which opens a zip from the phone's files (Downloads, Drive and so on). The zip can hold the bundle's files at its top level (the zip
  `upload-bundle` sends the Railway server) or the `ftt_bundle` folder (Windows' **Send to > Compressed folder** on it). For an update the app asks first, giving both export times, and warns
  when the zip is older than the bundle on the phone. An updated bundle keeps its history and is loaded again at once.
- **Remove** with **⋮ → Remove a bundle…**, which asks first; the pair's history goes with it. One bundle must stay. Removing the pair you're using switches to another.
- **Built in:** the build zips the bundle folders you name into the app (FTT-Scratch's `../deploy/bundle` unless you name others), and the app unpacks them the first time it runs, and again
  when an installed build carries a changed one. A built-in bundle never replaces a newer one you added, and one you removed stays removed until a build carries a changed copy of it.

## Build and install

```
dotnet build -f net10.0-android -c Release -p:AndroidSdkDirectory=%LOCALAPPDATA%\Android\Sdk
dotnet build -f net10.0-android -c Release -p:AndroidSdkDirectory=%LOCALAPPDATA%\Android\Sdk "-p:BundleDirs=\"<ftt_bundle folder>;<another>\""
adb install -r bin/Release/net10.0-android/org.sil.fttranslator-Signed.apk
```

Quote a `BundleDirs` list as shown: MSBuild otherwise reads the `;` as the start of another property.

Use Release on a phone; the HC spike's Release build parsed more than twice as fast as Debug (`../maui-spike/README.md`). A Debug APK installed with `adb install` needs
`-p:EmbedAssembliesIntoApk=true`.

| Code | What it does |
|---|---|
| `MainPage.xaml`, `MainPage.xaml.cs` | The one page |
| `TranslationItem.cs` | One translation as the page shows it, plain or traced |
| `TraceView.xaml`, `TraceView.xaml.cs` | The trace section, under the current translation and on each earlier one |
| `History.cs` | The history and its file |
| `Bundles.cs` | The bundles on the phone: built in, added and updated |
| `TranslatorService.cs` | Loads the chosen bundle and translates in the background |

Each file's header explains it.

On the phone the app keeps its files in its own storage: `bundles/<work project>/` (each bundle), `bundles/.packaged/` (which built-in zips are unpacked) and `history.json`. The synthesis work
files go in its cache folder.

## On a phone (Galaxy S9, 11/7/26)

FTT-Scratch (French → Spanish): about 0.5 s a sentence. Mato-Uma: about 4–5 s a sentence (parsing about 2 s, synthesis about 2 s), the same translations as the PC, which takes about 1.5 s.
Synthesis takes about 2 s even for three words, so it has a fixed cost per translation worth finding.

## Not done yet

- **Downloading a bundle from the Railway server,** instead of copying a zip to the phone.
- **Long texts.** On a PC a Mato-Uma chapter takes about 27 s, nearly all of it parsing (`../offline/README.md`), and a phone is slower. A verse or a paragraph at a time is the use this screen
  is built for.
- **Untested:** right-to-left targets, though Android lays out each label's text by its first strong character.
