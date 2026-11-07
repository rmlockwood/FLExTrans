// MainPage.xaml.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. The app's one page: translate, the current translation, the earlier ones, switching bundles, trace mode.
//
// OVERVIEW (AI generated, then edited)
//
// Type a sentence, tap Translate, and the translation appears right under the text box, in large type on a tinted panel, so it's the first thing the eye finds. Below the language pair and
// Translate come the earlier translations, newest first. That's the whole normal screen. Trace mode, turned on from the menu and remembered, adds a "Trace" section under the current translation
// and on each earlier one (see TranslationItem.cs), shows the seconds on Translate while a translation runs, and keeps each new translation's Apertium streams (TranslatorService).
//
// BUNDLES
//
// The phone can hold several bundles, one per language pair (Bundles.cs). The chosen one is remembered; tapping the language pair, or the menu's "Language pair…", lists them to switch, and
// "Add or update a bundle…" opens a bundle zip from the phone's files. Each pair has its own history: the page shows only the chosen bundle's translations, so switching shows that pair's.
// Switching loads the bundle (TranslatorService keeps one loaded at a time), and the status line says so meanwhile. Switching and adding wait while a translation runs.
//
// UPDATING A BUNDLE
//
// A zip of a work project the phone already has is an update: after an export-bundle of a changed project, the new zip replaces the old bundle and keeps its history. The page asks first,
// giving both bundles' export times, and warns when the zip is the older one, so an old zip opened by mistake doesn't quietly undo an update. The updated bundle is loaded again at once.
//
// THE CURRENT TRANSLATION AND THE EARLIER ONES
//
// The history (History.cs) is one list of every bundle's translations, newest first. Of the chosen bundle's, the first is the current translation, shown in the answer panel, and the rest are
// the earlier ones, in EarlierList. A new translation becomes the current one and the old current one moves to the top of the earlier ones, with its trace closed. The whole page is one
// ScrollView, so a long trace scrolls with the page rather than pushing the earlier translations off a fixed screen. It isn't a CollectionView with the box and answer as its header: on Android
// that header kept the height it was first measured at, so the earlier translations ended up far below the screen. The history is at most 500 translations, which don't need a CollectionView's
// recycling. It's saved in the background after each change.
//
// THE TEXT BOX
//
// The text stays in the box after translating, as on the web page, so a sentence can be changed a little and translated again without retyping it on a phone keyboard; swiping an earlier
// translation right puts its source back in the box. Each line of the box is a paragraph of the text. The keyboard is put away when a translation starts, so the answer isn't hidden behind it.
// The answer panel shows its source only when the box doesn't hold it (after a restart, or once the box is changed), so the answer is never shown without what it translates.
//
// THE STATUS LINE AND TRANSLATE
//
// Left of Translate: "Loading Mato → Uma…" while a bundle loads, then the language pair with a ▾ to say it can be tapped ("French → Spanish", or the project names for a bundle exported without
// language names), briefly "Copied" after a tap, and the error if the bundle didn't load. While a translation runs, Translate says "Translating…" (with the seconds so far in trace mode) and the
// old answer is dimmed. Translate is enabled once there is text, a bundle and no translation running. It doesn't wait for the bundle to load: a translation asked for meanwhile waits for it.
//
// CODE STRUCTURE
//
// The constructor reads the history and calls StartUp(), which unpacks the built-in bundles and picks the remembered one. SwitchTo() chooses a bundle and ShowHistory() shows its translations;
// OnLanguagePairClicked() and OnAddBundleClicked() are the ways to switch. OnTranslateClicked() translates, with the button's timer, and makes the result current (AddEntry()). ShowCurrent(),
// UpdateAnswerTrace() and UpdateAnswerSource() fill the answer panel. Then the taps and swipes (OnAnswerTapped(), OnTranslationTapped(), Copy(), OnReuseInvoked(), OnDeleteInvoked()), the menu's
// other items (OnTraceModeClicked(), OnClearHistoryClicked()) and the helpers (SetTraceMode(), SaveHistory(), ShowStatus(), UpdateTranslateButton()).
//

using System.Collections.ObjectModel;

namespace FTtranslator.Phone;

public partial class MainPage : ContentPage
{
	// Where trace mode and the chosen bundle are remembered
	const string TraceModeKey = "traceMode";
	const string BundleKey = "bundle";
	const string AddBundleChoice = "Add or update a bundle…";

	readonly TranslatorService translator = new TranslatorService();
	readonly HistoryStore historyStore = new HistoryStore();
	readonly List<HistoryEntry> history;
	readonly ObservableCollection<TranslationItem> earlier = new ObservableCollection<TranslationItem>();
	List<BundleInfo> bundles = new List<BundleInfo>();
	BundleInfo? bundle;
	TranslationItem? current;
	bool traceMode;
	bool busy;

	// What the status line shows when nothing else is: the language pair once the bundle has loaded
	string idleStatus = "Loading…";

	public MainPage()
	{
		InitializeComponent();
		traceMode = Preferences.Default.Get(TraceModeKey, false);
		history = historyStore.Load();
		BindableLayout.SetItemsSource(EarlierList, earlier);
		SetTraceMode(traceMode);
		ShowCurrent();
		ShowStatus(idleStatus);
		StartUp();
	}

	// Unpack the built-in bundles and switch to the remembered one, or the first
	async void StartUp()
	{

		try
		{
			await Task.Run(BundleStore.InstallPackagedAsync);
		}
		catch (Exception ex)
		{
			await DisplayAlertAsync("Bundles", $"The app's bundles couldn't be unpacked: {ex.Message}", "OK");
		}

		bundles = BundleStore.List();

		if (bundles.Count == 0)
		{
			idleStatus = "No bundle: tap to add one";
			ShowStatus(idleStatus);

			return;
		}

		string remembered = Preferences.Default.Get(BundleKey, "");
		await SwitchTo(bundles.FirstOrDefault(info => info.Id == remembered) ?? bundles[0]);
	}

	// Choose a bundle: show its history and load it. reload loads it again after its files were replaced. See BUNDLES above.
	async Task SwitchTo(BundleInfo chosen, bool reload = false)
	{
		bundle = chosen;
		Preferences.Default.Set(BundleKey, chosen.Id);
		ShowHistory();
		UpdateTranslateButton();
		idleStatus = $"{chosen.LanguagePair} ▾";
		ShowStatus($"Loading {chosen.LanguagePair}…");

		try
		{
			await translator.LoadAsync(chosen, reload);
		}
		catch (Exception ex)
		{
			idleStatus = $"{chosen.LanguagePair} didn't load: {ex.Message}";
		}

		// Another bundle may have been chosen meanwhile, and a translation may be running
		if (bundle == chosen && !busy)
		{
			ShowStatus(idleStatus);
		}
	}

	// The chosen bundle's translations: the newest is current, with its trace open, the rest are the earlier ones
	void ShowHistory()
	{
		List<HistoryEntry> mine = history.Where(entry => entry.Bundle == bundle?.Id).ToList();
		current = mine.Count > 0 ? new TranslationItem(mine[0], traceMode, true) : null;
		earlier.Clear();

		foreach (HistoryEntry entry in mine.Skip(1))
		{
			earlier.Add(new TranslationItem(entry, traceMode, false));
		}

		ShowCurrent();
	}

	// List the bundles to switch to, with a way to add one. See BUNDLES above.
	async void OnLanguagePairClicked(object? sender, EventArgs e)
	{

		if (busy)
		{
			return;
		}

		// Two bundles with the same languages are told apart by their work projects
		string Label(BundleInfo info)
		{
			string label = bundles.Count(other => other.LanguagePair == info.LanguagePair) > 1 ? $"{info.LanguagePair} ({info.WorkProject})" : info.LanguagePair;

			return info == bundle ? $"{label} ✓" : label;
		}

		string[] choices = bundles.Select(Label).Append(AddBundleChoice).ToArray();
		string? choice = await DisplayActionSheetAsync("Language pair", "Cancel", null, choices);
		int index = choice == null ? -1 : Array.IndexOf(choices, choice);

		if (choice == AddBundleChoice)
		{
			OnAddBundleClicked(sender, e);
		}
		else if (index >= 0 && index < bundles.Count && bundles[index] != bundle)
		{
			await SwitchTo(bundles[index]);
		}
	}

	// Add a bundle from a zip in the phone's files, or update one the phone has (asking first), and switch to it. See UPDATING A BUNDLE above.
	async void OnAddBundleClicked(object? sender, EventArgs e)
	{

		if (busy)
		{
			return;
		}

		FileResult? file = await FilePicker.Default.PickAsync(new PickOptions { PickerTitle = "Choose a bundle zip" });

		if (file == null)
		{
			return;
		}

		ShowStatus("Reading the bundle…");
		StagedBundle staged;

		try
		{
			staged = await Task.Run(async () =>
			{
				using Stream zip = await file.OpenReadAsync();

				return BundleStore.Stage(zip);
			});
		}
		catch (Exception ex)
		{
			ShowStatus(idleStatus);
			await DisplayAlertAsync("Add or update a bundle", ex.Message, "OK");

			return;
		}

		// An update replaces the phone's bundle of the same work project, so ask, saying which is newer
		BundleInfo? existing = BundleStore.Find(staged.Info.Id);

		if (existing != null)
		{
			BundleInfo incoming = staged.Info;
			string question = existing.IsNewerThan(incoming)
				? $"This {incoming.LanguagePair} bundle (exported {incoming.CreatedText}) is older than the one on the phone (exported {existing.CreatedText}). Replace it anyway?"
				: $"Update {incoming.LanguagePair}? The bundle on the phone was exported {existing.CreatedText}; this one was exported {incoming.CreatedText}.";

			if (!await DisplayAlertAsync("Update a bundle", question, "Replace", "Cancel"))
			{
				BundleStore.Discard();
				ShowStatus(idleStatus);

				return;
			}
		}

		try
		{
			BundleInfo added = await Task.Run(() => BundleStore.Commit(staged));
			bundles = BundleStore.List();

			// An updated bundle's files have been replaced, so it's loaded again even when it's the one chosen
			await SwitchTo(bundles.First(info => info.Id == added.Id), reload: true);
		}
		catch (Exception ex)
		{
			ShowStatus(idleStatus);
			await DisplayAlertAsync("Add or update a bundle", ex.Message, "OK");
		}
	}

	async void OnTranslateClicked(object? sender, EventArgs e)
	{
		string text = (SourceEditor.Text ?? "").Trim();

		if (text.Length == 0 || busy || bundle == null)
		{
			return;
		}

		busy = true;
		UpdateTranslateButton();

		// Unfocus() alone leaves Android's keyboard up, over the answer
		_ = SourceEditor.HideSoftInputAsync(CancellationToken.None);
		SourceEditor.Unfocus();
		AnswerPanel.Opacity = 0.4;

		// The button says what's happening; in trace mode it counts the seconds too, once a second. Each change of the button's text lays the whole page out again, and ten a second made a Mato
		// sentence take 40% longer on a Galaxy S9 (6.1 s against 4.2 s), as the layout work competed with the translation. The trace's step times are the exact figures.
		DateTime started = DateTime.Now;
		IDispatcherTimer timer = Dispatcher.CreateTimer();
		timer.Interval = TimeSpan.FromSeconds(1);
		timer.Tick += (_, _) =>
		{

			if (traceMode)
			{
				TranslateButton.Text = $"Translating… {(DateTime.Now - started).TotalSeconds:F0} s";
			}
		};

		TranslateButton.Text = "Translating…";
		timer.Start();

		try
		{
			HistoryEntry entry = await translator.TranslateAsync(text, traceMode);
			AddEntry(entry);
		}
		finally
		{
			timer.Stop();
			busy = false;
			TranslateButton.Text = "Translate";
			AnswerPanel.Opacity = 1;
			ShowStatus(idleStatus);
			UpdateTranslateButton();
		}
	}

	// Make a new translation the current one, move the old current one to the top of the earlier ones, and save the history
	void AddEntry(HistoryEntry entry)
	{
		history.Insert(0, entry);

		if (history.Count > HistoryStore.MaxEntries)
		{
			history.RemoveRange(HistoryStore.MaxEntries, history.Count - HistoryStore.MaxEntries);
		}

		if (current != null)
		{
			current.IsTraceOpen = false;
			earlier.Insert(0, current);
		}

		current = new TranslationItem(entry, traceMode, true);

		// Translations dropped from the history go from the page too
		while (earlier.Count > 0 && !history.Contains(earlier[^1].Entry))
		{
			earlier.RemoveAt(earlier.Count - 1);
		}

		ShowCurrent();
		SaveHistory();
	}

	// Fill the answer panel and its trace from the current translation, or hide them when there is none
	void ShowCurrent()
	{
		AnswerPanel.IsVisible = current != null;
		AnswerTrace.BindingContext = current;
		UpdateAnswerTrace();
		AnswerLabel.Text = current?.Translation ?? "";
		AnswerLabel.IsVisible = current?.HasTranslation ?? false;
		AnswerErrorLabel.Text = current?.Error ?? "";
		AnswerErrorLabel.IsVisible = current?.HasError ?? false;
		EarlierLabel.IsVisible = earlier.Count > 0;
		UpdateAnswerSource();
	}

	// The current translation's trace: the TraceView itself is hidden, not only what's in it, since on Android a ContentView with its content hidden still took the rest of the screen
	void UpdateAnswerTrace()
	{
		AnswerTrace.IsVisible = traceMode && current != null;
	}

	// The answer's source, shown only when the box doesn't hold it. See THE TEXT BOX above.
	void UpdateAnswerSource()
	{
		AnswerSourceLabel.Text = current?.Source ?? "";
		AnswerSourceLabel.IsVisible = current != null && current.Source != (SourceEditor.Text ?? "").Trim();
	}

	void OnAnswerTapped(object? sender, TappedEventArgs e)
	{
		Copy(current);
	}

	// Tapping an earlier translation copies it
	void OnTranslationTapped(object? sender, TappedEventArgs e)
	{
		Copy((sender as BindableObject)?.BindingContext as TranslationItem);
	}

	async void Copy(TranslationItem? item)
	{

		if (item == null || !item.HasTranslation)
		{
			return;
		}

		await Clipboard.Default.SetTextAsync(item.Translation);
		ShowStatus("Copied");
		await Task.Delay(1500);
		ShowStatus(idleStatus);
	}

	// Swiping an earlier translation right puts its source back in the box. See THE TEXT BOX above.
	void OnReuseInvoked(object? sender, EventArgs e)
	{

		if ((sender as BindableObject)?.BindingContext is TranslationItem item)
		{
			SourceEditor.Text = item.Entry.Source;
			SourceEditor.Focus();
		}
	}

	void OnDeleteInvoked(object? sender, EventArgs e)
	{

		if ((sender as BindableObject)?.BindingContext is TranslationItem item)
		{
			earlier.Remove(item);
			history.Remove(item.Entry);
			EarlierLabel.IsVisible = earlier.Count > 0;
			SaveHistory();
		}
	}

	void OnTraceModeClicked(object? sender, EventArgs e)
	{
		SetTraceMode(!traceMode);
		Preferences.Default.Set(TraceModeKey, traceMode);
	}

	// Clears the chosen language pair's history; the other pairs' stays
	async void OnClearHistoryClicked(object? sender, EventArgs e)
	{
		int count = earlier.Count + (current == null ? 0 : 1);

		if (count == 0 || bundle == null)
		{
			return;
		}

		if (!await DisplayAlertAsync("Clear history", $"Delete all {count} {bundle.LanguagePair} translations?", "Delete", "Cancel"))
		{
			return;
		}

		history.RemoveAll(entry => entry.Bundle == bundle.Id);
		current = null;
		earlier.Clear();
		ShowCurrent();
		SaveHistory();
	}

	// Show or hide every trace, and tick the menu item
	void SetTraceMode(bool on)
	{
		traceMode = on;
		TraceModeItem.Text = on ? "Trace mode ✓" : "Trace mode";

		if (current != null)
		{
			current.TraceMode = on;
		}

		UpdateAnswerTrace();

		foreach (TranslationItem item in earlier)
		{
			item.TraceMode = on;
		}
	}

	// Save in the background, from a copy, so the page never waits on a write and goes on changing its own list. See History.cs's TRAPS.
	void SaveHistory()
	{
		List<HistoryEntry> copy = history.ToList();
		_ = Task.Run(() => historyStore.Save(copy));
	}

	void ShowStatus(string text)
	{
		StatusLabel.Text = text;
	}

	void OnSourceTextChanged(object? sender, TextChangedEventArgs e)
	{
		UpdateTranslateButton();
		UpdateAnswerSource();
	}

	void UpdateTranslateButton()
	{
		TranslateButton.IsEnabled = !busy && bundle != null && !string.IsNullOrWhiteSpace(SourceEditor.Text);
	}
}
