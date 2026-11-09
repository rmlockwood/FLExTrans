// MainPage.xaml.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17.5 - 11/8/26 - Ron Lockwood
//  The earlier translations' cards lay out a right-to-left source or translation right to left, as the text box and answer do.
//
// Version 3.17.4 - 11/8/26 - Ron Lockwood
//  A Language menu item chooses the UI language, for phones without a per-app language setting; the page builds itself again in the new language.
//
// Version 3.17.3 - 11/7/26 - Ron Lockwood
//  The UI text comes from AppResources (English, Spanish, French, German), in the phone's language; the trace stays in English.
//
// Version 3.17.2 - 11/7/26 - Ron Lockwood
//  Switching to another bundle clears the text box and the current translation.
//
// Version 3.17.1 - 11/7/26 - Ron Lockwood
//  The text box and the answer flow right to left, aligned right, when the bundle's source or target language is right to left.
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
// Switching loads the bundle (TranslatorService keeps one loaded at a time), and the status line says so meanwhile. Switching and adding wait while a translation runs. Switching to another pair
// clears the text box and the answer panel, since the text is in the other pair's source language, and the new pair's translations are all shown as earlier ones until the next translation.
// Choosing the remembered bundle at start-up isn't a switch: its newest translation is current again, as it was when the app closed.
//
// UPDATING A BUNDLE
//
// A zip of a work project the phone already has is an update: after an export-bundle of a changed project, the new zip replaces the old bundle and keeps its history. The page asks first,
// giving both bundles' export times, and warns when the zip is the older one, so an old zip opened by mistake doesn't quietly undo an update. The updated bundle is loaded again at once.
//
// REMOVING A BUNDLE
//
// "Remove a bundle…" lists the bundles, asks, and deletes the one chosen with its history (a removed pair's translations would otherwise sit unseen in the history's 500). One bundle must stay,
// since the page has nothing to translate with otherwise. Removing the chosen bundle switches to another first, so the removed one is never the one loaded.
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
// RIGHT-TO-LEFT LANGUAGES
//
// When the bundle's source language is written right to left (the manifest's sourceRightToLeft), the text box flows right to left and its text is aligned right, and so is the answer panel's
// copy of the source; when the target is, the answer does the same (targetRightToLeft). SetDirections() sets each control's FlowDirection when a bundle is chosen: with a right-to-left flow,
// a control's Start alignment is its right edge. The earlier translations' cards follow the same rule line by line: MakeItem() gives each TranslationItem the bundle's two directions, and
// the card's source and translation labels bind to them. Only those controls change; the error line, the status line and the trace stay left to right, since their text is in the app's UI language
// (English, Spanish, French or German, all left to right) or, for the trace, always English.
//
// THE UI LANGUAGE
//
// Every word the page shows, except the trace, comes from AppResources (Resources/Strings/AppResources*.resx), in the language chosen with the menu's Language item, or else the phone's (or
// the app's own on phones that let each app have one); anything else falls back to English. App.xaml.cs sets the language before the page is built.
//
// The XAML uses {x:Static}, so the page reads its words once, when it's built. Choosing another language (OnLanguageClicked()) therefore builds a new page and puts it in the window, carrying
// over the text box. The new page loses nothing else because what lasts is shared, not the page's own: the history list and the translator are static, so the new page shows the same history
// (not one read back from the file before the last save had landed) and finds the bundle already loaded. The Language item has a globe before it, so someone who chose a language they can't
// read can still find the way back; the list names each language in itself. The strings are whole sentences with {0}-style
// placeholders rather than pieces joined in code, since word order differs between languages. Counts get two strings, one and many (RemoveQuestionOne/Many, ClearHistoryOne/Many): that is the
// whole plural rule in all four languages, since a count of zero never reaches those questions. The trace and FTOffline's messages stay English (see TranslationItem.cs), and so does a
// failed translation's reason: with trace mode off a failed translation says, translated, that it failed and to turn on trace mode to see why.
//
// THE STATUS LINE AND TRANSLATE
//
// Left of Translate: "Loading Mato → Uma…" while a bundle loads, then the language pair with a ▾ to say it can be tapped ("French → Spanish", or the project names for a bundle exported without
// language names), briefly "Copied" after a tap, and the error if the bundle didn't load. While a translation runs, Translate says "Translating…" (with the seconds so far in trace mode) and the
// old answer is dimmed. Translate is enabled once there is text, a bundle and no translation running. It doesn't wait for the bundle to load: a translation asked for meanwhile waits for it.
//
// CODE STRUCTURE
//
// The constructor reads the history and calls StartUp(), which unpacks the built-in bundles and picks the remembered one. SwitchTo() chooses a bundle, SetDirections() sets the text box's and
// answer's directions for it, and ShowHistory() shows its translations;
// OnLanguagePairClicked() and OnAddBundleClicked() are the ways to switch, and OnRemoveBundleClicked() removes one. OnTranslateClicked() translates, with the button's timer, and makes the result current (AddEntry()). ShowCurrent(),
// UpdateAnswerTrace() and UpdateAnswerSource() fill the answer panel. Then the taps and swipes (OnAnswerTapped(), OnTranslationTapped(), Copy(), OnReuseInvoked(), OnDeleteInvoked()), the menu's
// other items (OnLanguageClicked(), OnTraceModeClicked(), OnClearHistoryClicked()) and the helpers (SetTraceMode(), SaveHistory(), ShowStatus(), UpdateTranslateButton()).
//

using System.Collections.ObjectModel;

using FTtranslator.Phone.Resources.Strings;

namespace FTtranslator.Phone;

public partial class MainPage : ContentPage
{
	// Where trace mode and the chosen bundle are remembered
	const string TraceModeKey = "traceMode";
	const string BundleKey = "bundle";

	// Shared by every page the app builds, since choosing a language builds a new one. See THE UI LANGUAGE above.
	static readonly TranslatorService translator = new TranslatorService();
	static readonly HistoryStore historyStore = new HistoryStore();
	static List<HistoryEntry>? loadedHistory;

	readonly List<HistoryEntry> history;
	readonly ObservableCollection<TranslationItem> earlier = new ObservableCollection<TranslationItem>();
	List<BundleInfo> bundles = new List<BundleInfo>();
	BundleInfo? bundle;
	TranslationItem? current;
	bool traceMode;
	bool busy;

	// What the status line shows when nothing else is: the language pair once the bundle has loaded
	string idleStatus = AppResources.Loading;

	public MainPage()
	{
		InitializeComponent();
		LanguageItem.Text = $"🌐 {AppResources.MenuLanguage}";
		traceMode = Preferences.Default.Get(TraceModeKey, false);

		// Read from the file only by the first page; a page built for a new language takes the same list
		loadedHistory ??= historyStore.Load();
		history = loadedHistory;
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
			await DisplayAlertAsync(AppResources.BundlesTitle, string.Format(AppResources.PackagedUnpackFailed, ex.Message), AppResources.Ok);
		}

		bundles = BundleStore.List();

		if (bundles.Count == 0)
		{
			idleStatus = AppResources.NoBundle;
			ShowStatus(idleStatus);

			return;
		}

		string remembered = Preferences.Default.Get(BundleKey, "");
		await SwitchTo(bundles.FirstOrDefault(info => info.Id == remembered) ?? bundles[0]);
	}

	// Choose a bundle: show its history and load it. reload loads it again after its files were replaced. Switching from another bundle clears the text box and the answer panel; choosing
	// one at start-up keeps the last translation as the current one. See BUNDLES above.
	async Task SwitchTo(BundleInfo chosen, bool reload = false)
	{
		bool switching = bundle != null && bundle.Id != chosen.Id;
		bundle = chosen;
		Preferences.Default.Set(BundleKey, chosen.Id);
		SetDirections(chosen);

		// The text and the answer were the other pair's, so they go; the new pair's translations are all earlier ones
		if (switching)
		{
			SourceEditor.Text = "";
		}

		ShowHistory(withCurrent: !switching);
		UpdateTranslateButton();
		idleStatus = $"{chosen.LanguagePair} ▾";
		ShowStatus(string.Format(AppResources.LoadingPair, chosen.LanguagePair));

		try
		{
			await translator.LoadAsync(chosen, reload);
		}
		catch (Exception ex)
		{
			idleStatus = string.Format(AppResources.PairDidNotLoad, chosen.LanguagePair, ex.Message);
		}

		// Another bundle may have been chosen meanwhile, and a translation may be running
		if (bundle == chosen && !busy)
		{
			ShowStatus(idleStatus);
		}
	}

	// Lay out the text box and the answer's source in the source language's direction, and the answer in the target's. See RIGHT-TO-LEFT LANGUAGES above.
	void SetDirections(BundleInfo chosen)
	{
		FlowDirection sourceDirection = chosen.SourceRightToLeft ? FlowDirection.RightToLeft : FlowDirection.LeftToRight;
		FlowDirection targetDirection = chosen.TargetRightToLeft ? FlowDirection.RightToLeft : FlowDirection.LeftToRight;

		SourceEditor.FlowDirection = sourceDirection;
		AnswerSourceLabel.FlowDirection = sourceDirection;
		AnswerLabel.FlowDirection = targetDirection;
	}

	// A history entry as the page shows it, with its source and translation in the chosen bundle's directions (an entry shown is always the chosen bundle's). See RIGHT-TO-LEFT LANGUAGES above.
	TranslationItem MakeItem(HistoryEntry entry, bool isTraceOpen)
	{
		return new TranslationItem(entry, traceMode, isTraceOpen)
		{
			SourceDirection = bundle?.SourceRightToLeft == true ? FlowDirection.RightToLeft : FlowDirection.LeftToRight,
			TranslationDirection = bundle?.TargetRightToLeft == true ? FlowDirection.RightToLeft : FlowDirection.LeftToRight,
		};
	}

	// The chosen bundle's translations: with withCurrent the newest is current, with its trace open, and the rest are the earlier ones; without it, there's no current one and all are earlier
	void ShowHistory(bool withCurrent = true)
	{
		List<HistoryEntry> mine = history.Where(entry => entry.Bundle == bundle?.Id).ToList();
		current = withCurrent && mine.Count > 0 ? MakeItem(mine[0], true) : null;
		earlier.Clear();

		foreach (HistoryEntry entry in mine.Skip(current == null ? 0 : 1))
		{
			earlier.Add(MakeItem(entry, false));
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

		// The last choice is the menu item's text, read here rather than kept in a static field, which would keep the language the app started in after another was chosen
		string addBundleChoice = AppResources.MenuAddBundle;
		string[] choices = bundles.Select(Label).Append(addBundleChoice).ToArray();
		string? choice = await DisplayActionSheetAsync(AppResources.LanguagePairTitle, AppResources.Cancel, null, choices);
		int index = choice == null ? -1 : Array.IndexOf(choices, choice);

		if (choice == addBundleChoice)
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

		FileResult? file = await FilePicker.Default.PickAsync(new PickOptions { PickerTitle = AppResources.ChooseBundleZip });

		if (file == null)
		{
			return;
		}

		ShowStatus(AppResources.ReadingBundle);
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
			await DisplayAlertAsync(AppResources.AddBundleTitle, ex.Message, AppResources.Ok);

			return;
		}

		// An update replaces the phone's bundle of the same work project, so ask, saying which is newer
		BundleInfo? existing = BundleStore.Find(staged.Info.Id);

		if (existing != null)
		{
			BundleInfo incoming = staged.Info;
			string question = existing.IsNewerThan(incoming)
				? string.Format(AppResources.UpdateOlderQuestion, incoming.LanguagePair, incoming.ExportedText, existing.ExportedText)
				: string.Format(AppResources.UpdateNewerQuestion, incoming.LanguagePair, existing.ExportedText, incoming.ExportedText);

			if (!await DisplayAlertAsync(AppResources.UpdateBundleTitle, question, AppResources.Replace, AppResources.Cancel))
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
			await DisplayAlertAsync(AppResources.AddBundleTitle, ex.Message, AppResources.Ok);
		}
	}

	// Remove a bundle and its history, after asking; never the last one. Removing the chosen bundle switches to another first. See REMOVING A BUNDLE above.
	async void OnRemoveBundleClicked(object? sender, EventArgs e)
	{

		if (busy)
		{
			return;
		}

		if (bundles.Count < 2)
		{
			await DisplayAlertAsync(AppResources.RemoveBundleTitle, AppResources.OneBundleMustStay, AppResources.Ok);

			return;
		}

		string[] choices = bundles.Select(info => info.LanguagePair).ToArray();
		string? choice = await DisplayActionSheetAsync(AppResources.RemoveBundleTitle, AppResources.Cancel, null, choices);
		int index = choice == null ? -1 : Array.IndexOf(choices, choice);

		if (index < 0)
		{
			return;
		}

		BundleInfo doomed = bundles[index];
		int translations = history.Count(entry => entry.Bundle == doomed.Id);

		// A whole sentence for each count rather than a note added on, so each language can word it its own way. See THE UI LANGUAGE above.
		string questionFormat = translations switch
		{
			0 => AppResources.RemoveQuestion,
			1 => AppResources.RemoveQuestionOne,
			_ => AppResources.RemoveQuestionMany,
		};

		string question = string.Format(questionFormat, doomed.LanguagePair, doomed.ExportedText, translations);

		if (!await DisplayAlertAsync(AppResources.RemoveBundleTitle, question, AppResources.Remove, AppResources.Cancel))
		{
			return;
		}

		// Off the chosen bundle first, so it isn't the one loaded when its folder goes
		if (doomed.Id == bundle?.Id)
		{
			await SwitchTo(bundles.First(info => info.Id != doomed.Id));
		}

		try
		{
			await Task.Run(() => BundleStore.Remove(doomed));
		}
		catch (Exception ex)
		{
			await DisplayAlertAsync(AppResources.RemoveBundleTitle, ex.Message, AppResources.Ok);
		}

		bundles = BundleStore.List();
		history.RemoveAll(entry => entry.Bundle == doomed.Id);
		SaveHistory();
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
				TranslateButton.Text = string.Format(AppResources.TranslatingSeconds, (DateTime.Now - started).TotalSeconds.ToString("F0"));
			}
		};

		TranslateButton.Text = AppResources.Translating;
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
			TranslateButton.Text = AppResources.Translate;
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

		current = MakeItem(entry, true);

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
		ShowStatus(AppResources.Copied);
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

	// Choose the UI language, or the phone's, and build the page again in it, keeping the text box. See THE UI LANGUAGE above.
	async void OnLanguageClicked(object? sender, EventArgs e)
	{

		if (busy)
		{
			return;
		}

		string chosenCode = App.UILanguageCode;

		string Label(string name, bool chosen)
		{
			return chosen ? $"{name} ✓" : name;
		}

		string[] choices = UILanguages.All.Select(language => Label(language.NativeName, language.Code == chosenCode)).Prepend(Label(AppResources.SameAsPhone, chosenCode.Length == 0)).ToArray();
		string? choice = await DisplayActionSheetAsync(AppResources.LanguageTitle, AppResources.Cancel, null, choices);
		int index = choice == null ? -1 : Array.IndexOf(choices, choice);

		if (index < 0)
		{
			return;
		}

		// The first choice is the phone's language; the rest are UILanguages.All in order
		string code = index == 0 ? "" : UILanguages.All[index - 1].Code;

		if (code == chosenCode || Window == null)
		{
			return;
		}

		App.SetUILanguage(code);
		var page = new MainPage();
		page.SourceEditor.Text = SourceEditor.Text;
		Window.Page = new NavigationPage(page);
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

		string question = count == 1 ? string.Format(AppResources.ClearHistoryOne, bundle.LanguagePair) : string.Format(AppResources.ClearHistoryMany, count, bundle.LanguagePair);

		if (!await DisplayAlertAsync(AppResources.ClearHistory, question, AppResources.Delete, AppResources.Cancel))
		{
			return;
		}

		history.RemoveAll(entry => entry.Bundle == bundle.Id);
		current = null;
		earlier.Clear();
		ShowCurrent();
		SaveHistory();
	}

	// Show or hide every trace, tick the menu item, and switch a failed translation's line between the translated "it failed" and the English reason (see THE UI LANGUAGE above)
	void SetTraceMode(bool on)
	{
		traceMode = on;
		TraceModeItem.Text = on ? $"{AppResources.MenuTraceMode} ✓" : AppResources.MenuTraceMode;

		if (current != null)
		{
			current.TraceMode = on;
		}

		AnswerErrorLabel.Text = current?.Error ?? "";
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
