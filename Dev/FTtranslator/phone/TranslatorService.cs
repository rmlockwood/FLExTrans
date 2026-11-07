// TranslatorService.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. Loads the chosen bundle and translates with FTOffline off the UI thread.
//
// OVERVIEW (AI generated, then edited)
//
// Everything between the page and FTOffline. The page chooses a bundle (Bundles.cs keeps them) and LoadAsync() loads it into an OfflineTranslator in the background, which takes a second or two
// on a PC and several on a phone for a big lexicon; a translation asked for before it finishes waits for it.
//
// ONE BUNDLE LOADED AT A TIME
//
// Switching bundles loads the new one and drops the old one (its synthesizer is disposed once its load has finished). A big bundle takes a lot of memory once loaded (Mato-Uma's guesser data
// alone is 23 MB of JSON), so keeping every bundle loaded would cost more on a phone than the few seconds a switch takes. Each bundle's synthesis work files go in its own folder in the cache
// (synthesis/<id>), which Android may clear; they are rewritten for every translation anyway.
//
// WHAT A TRANSLATION RECORDS
//
// Every translation gives a HistoryEntry: the bundle, the source, the translation or the error, and the run record (built by every translation anyway, and small). In trace mode the Apertium
// streams are kept too (the source text as Extract Source Text writes it, and the target text Run Apertium makes from it), from OfflineTranslator's StageObserver. Outside trace mode the
// observer is left off: that skips reading the synthesis work files back, and keeps the history file small, since a chapter's streams run to tens of KB.
//
// TRAPS
//
//  - OfflineTranslator translates one text at a time (it locks), and the page never starts a second translation or switches bundles while one runs, so the stream fields are never shared.
//  - A failed load (a broken bundle) is not kept: the next LoadAsync() of that bundle tries again, and a translation asked for meanwhile gets the load's error, so the user sees why.
//  - LoadAsync() of the bundle already loaded returns that load, unless reload says the bundle's files have been replaced (a newer zip of the same work project was added).
//
// CODE STRUCTURE
//
// TranslatorService: LoadAsync() and Load() (ONE BUNDLE LOADED AT A TIME), then TranslateAsync() (WHAT A TRANSLATION RECORDS) and Observe(), its stage observer.
//

using FTtranslator.Offline;

namespace FTtranslator.Phone;

public sealed class TranslatorService
{
	readonly object loadLock = new object();
	Task<OfflineTranslator>? loading;

	// The streams of the translation in progress, filled by Observe() in trace mode. See TRAPS above.
	string? sourceStream;
	string? targetStream;

	// The bundle chosen, loaded or loading
	public BundleInfo? Bundle { get; private set; }

	// Load a bundle, dropping the one loaded before; or return its load when it is already loaded or loading. See ONE BUNDLE LOADED AT A TIME and TRAPS above.
	public Task<OfflineTranslator> LoadAsync(BundleInfo bundle, bool reload = false)
	{

		lock (loadLock)
		{

			if (!reload && Bundle?.Id == bundle.Id && loading is { IsFaulted: false, IsCanceled: false })
			{
				return loading;
			}

			// The old translator's synthesizer is disposed once its load is done, whether or not it has finished yet
			loading?.ContinueWith(previous =>
			{

				if (previous.IsCompletedSuccessfully)
				{
					previous.Result.Dispose();
				}
			});

			Bundle = bundle;
			loading = Task.Run(() => Load(bundle));

			return loading;
		}
	}

	static OfflineTranslator Load(BundleInfo bundle)
	{
		return new OfflineTranslator(bundle.Dir, Path.Combine(FileSystem.CacheDirectory, "synthesis", bundle.Id));
	}

	// Translate a text in the background with the chosen bundle; in trace mode keep the Apertium streams too. Never throws: a failure, the bundle's load included, comes back as the entry's
	// error. See WHAT A TRANSLATION RECORDS above.
	public async Task<HistoryEntry> TranslateAsync(string text, bool trace)
	{
		var entry = new HistoryEntry { When = DateTime.Now, Source = text, Bundle = Bundle?.Id ?? "" };
		Task<OfflineTranslator>? load;

		lock (loadLock)
		{
			load = loading;
		}

		try
		{

			if (load == null)
			{
				throw new InvalidOperationException("There's no bundle to translate with. Add one from the menu.");
			}

			OfflineTranslator translator = await load;
			sourceStream = null;
			targetStream = null;
			translator.StageObserver = trace ? Observe : null;
			RunResult record = await Task.Run(() => translator.Translate(text));
			entry.Record = record;
			entry.Translation = record.Translation;

			// A synthesis or Text Out failure: the record's last error says why
			if (!record.Ok)
			{
				entry.Error = record.Messages.LastOrDefault(message => message.Level == "error")?.Message ?? $"The translation stopped after {record.Steps.LastOrDefault() ?? "the start"}.";
			}
		}
		catch (Exception ex)
		{
			entry.Error = ex.Message;
			entry.ErrorDetail = ex.ToString();
		}

		entry.SourceStream = sourceStream;
		entry.TargetStream = targetStream;

		return entry;
	}

	// The stage observer in trace mode: keeps the two Apertium streams
	void Observe(string stage, object? value)
	{

		if (stage == "source")
		{
			sourceStream = value as string;
		}
		else if (stage == "target")
		{
			targetStream = value as string;
		}
	}
}
