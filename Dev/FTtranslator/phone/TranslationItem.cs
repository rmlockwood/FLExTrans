// TranslationItem.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17.2 - 11/8/26 - Ron Lockwood
//  SourceDirection and TranslationDirection, so a card lays out a right-to-left source or translation right to left.
//
// Version 3.17.1 - 11/7/26 - Ron Lockwood
//  With trace mode off, a failed translation says, in the UI language, that it failed; the English reason shows in trace mode.
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. One translation in the list, as the screen shows it, plain or traced.
//
// OVERVIEW (AI generated, then edited)
//
// A translation as the main page shows it, made from a HistoryEntry: the current translation (under the text box) and each card of the history below it are one each. Normally that is just the
// source, small, and the translation, or in red that it failed. In trace mode each also has a trace section (TraceView.xaml) laid out like the web page's result card (web/src/ResultCard.tsx):
//
//   the header line           the bundle and when, then the total time and an OK badge, or "Failed after <step>" in red
//   problem words             the run record's four lists (no parse, no analysis, not linked, not synthesized) as chips, each list under the web page's label
//   Analyses chosen (n)       a table of each word, its guessed analysis, and why (the only analysis, or the best guess)
//   Messages                  every message, warnings and errors coloured (the web page's "Show all messages" is always on here)
//   Step times                each step's seconds with a bar scaled to the longest, the time outside the steps, and the total
//   Apertium streams          the source stream Extract Source Text wrote and the target stream Run Apertium made from it (kept only for translations made in trace mode); not on the web page
//   Exception                 for a step that threw, the whole exception
//
// Each of the last five is a Section that folds open and closed, as the web page's <details> do. The trace itself opens and closes too: the current translation's starts open, the history's
// closed (a whole chapter's trace is long).
//
// THE UI LANGUAGE
//
// The trace is always English: its headings, labels and badge here and in TraceView.xaml, and the messages, step names and errors FTOffline writes, so those are plain strings, not AppResources.
// Only the plain view is translated, and its one string is a failed translation's red line: with trace mode off, Error is AppResources.TranslationFailed ("The translation failed. Turn on trace
// mode to see why."); in trace mode it's the reason itself, in English, as the history stores it. So Error changes with TraceMode and is raised with it.
//
// RIGHT-TO-LEFT LANGUAGES
//
// SourceDirection and TranslationDirection are the source's and the translation's flow directions, from the chosen bundle's manifest (sourceRightToLeft, targetRightToLeft), so a history card
// lays out each line as the text box and the answer panel do. The red error line keeps the default direction, since it's in the UI language.
//
// TRAPS
//
//  - The rows are worked out once, when the item is made; only trace mode and the open/closed states change afterwards, and they raise PropertyChanged.
//  - The translation is tidied as the web page tidies it: each paragraph on its own line, with the synthesizer's runs of spaces made single. Copying takes the tidied text.
//  - A step-time bar's width is a fraction of BarWidth, the bar column's width in TraceView.xaml; change both together.
//
// CODE STRUCTURE
//
// Section, ProblemGroup, AnalysisRow, MessageRow and StepRow are what TraceView.xaml binds to. TranslationItem: the plain view's properties, then the trace state (TraceMode, IsTraceOpen), then the
// trace's parts, made by the constructor with the helpers Problems(), Steps() and Seconds().
//

using System.ComponentModel;
using System.Globalization;

using FTtranslator.Offline;
using FTtranslator.Phone.Resources.Strings;

namespace FTtranslator.Phone;

// A part of the trace that folds open and closed, as a <details> on the web page
public sealed class Section : INotifyPropertyChanged
{
	readonly string title;
	bool isOpen;

	public event PropertyChangedEventHandler? PropertyChanged;

	public Section(string title, bool isOpen)
	{
		this.title = title;
		this.isOpen = isOpen;
	}

	public bool IsOpen
	{
		get => isOpen;
		set
		{

			if (isOpen == value)
			{
				return;
			}

			isOpen = value;
			PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(IsOpen)));
			PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Header)));
		}
	}

	public string Header => (isOpen ? "▾ " : "▸ ") + title;
}

// One of the run record's lists of failed words, with the web page's label
public sealed record ProblemGroup(string Label, List<string> Words);

public sealed record AnalysisRow(string Word, string Analysis, string Basis);

// A message, coloured by its level: the normal text colour for info (a null colour left Android's grey), amber for a warning, red for an error; lighter shades on a dark background
public sealed record MessageRow(string Text, string Level)
{
	public Color TextColor => (Level, Application.Current?.RequestedTheme == AppTheme.Dark) switch
	{
		("error", false) => Color.FromArgb("#C62828"),
		("error", true) => Color.FromArgb("#EF9A9A"),
		("warning", false) => Color.FromArgb("#8A5300"),
		("warning", true) => Color.FromArgb("#FFCC80"),
		(_, false) => Color.FromArgb("#212121"),
		(_, true) => Colors.White,
	};
}

// A step's time, with its bar's width (a fraction of TranslationItem.BarWidth). A bar under a pixel isn't drawn, as on the web page, rather than showing as a sliver.
public sealed record StepRow(string Step, string Seconds, double BarWidthRequest)
{
	public bool HasBar => BarWidthRequest >= 1;
}

public sealed class TranslationItem : INotifyPropertyChanged
{
	// The width of the step-time bars' column in TraceView.xaml. See TRAPS above.
	public const double BarWidth = 90;

	// The run record's lists of failed words, with the web page's labels
	static readonly (string Label, Func<RunResult, List<string>> Words)[] ProblemLists =
	{
		("No parse", record => record.Unparsed),
		("No analysis", record => record.Unanalysed),
		("Not linked", record => record.Untranslated),
		("Not synthesized", record => record.Unsynthesized),
	};

	bool traceMode;
	bool isTraceOpen;

	public event PropertyChangedEventHandler? PropertyChanged;

	public HistoryEntry Entry { get; }

	public TranslationItem(HistoryEntry entry, bool traceMode, bool isTraceOpen)
	{
		Entry = entry;
		this.traceMode = traceMode;
		this.isTraceOpen = isTraceOpen;
		Translation = Tidy(entry.Translation);
		RunResult? record = entry.Record;

		// The header line: the bundle and when on the left, the time and the outcome on the right
		HeaderText = entry.Bundle.Length > 0 ? $"{entry.Bundle} · {entry.When.ToString("g", CultureInfo.CurrentCulture)}" : entry.When.ToString("g", CultureInfo.CurrentCulture);
		TotalText = record?.TotalSeconds is double total ? Seconds(total) : "";
		Ok = record?.Ok ?? false;
		BadgeText = Ok ? "OK" : record == null ? "Failed" : $"Failed after {record.Steps.LastOrDefault() ?? "the start"}";

		if (record != null)
		{
			ProblemGroups = Problems(record);
			Analyses = record.Approved.Select(approved => new AnalysisRow(approved.Word, approved.Analysis, approved.Basis)).ToList();
			Messages = record.Messages.Select(message => new MessageRow(message.Message.Trim(), message.Level)).ToList();
			(Steps, OutsideText) = StepRows(record);
		}

		AnalysesSection = new Section($"Analyses chosen ({Analyses.Count})", true);
		MessagesSection = new Section("Messages", true);
		StepsSection = new Section("Step times", true);
		StreamsSection = new Section("Apertium streams", false);
		ExceptionSection = new Section("Exception", true);
	}

	// The plain view

	public string Source => Entry.Source.Trim();
	public string Translation { get; }

	// Each line's direction: right to left for a right-to-left language, from the bundle's manifest. Set by MainPage when it makes the item; the item's bundle is always the chosen one.
	public FlowDirection SourceDirection { get; init; } = FlowDirection.LeftToRight;
	public FlowDirection TranslationDirection { get; init; } = FlowDirection.LeftToRight;
	public bool HasTranslation => Translation.Length > 0;
	public bool HasError => !string.IsNullOrEmpty(Entry.Error);

	// The red line of a failed translation: translated with trace mode off, the English reason with it on. See THE UI LANGUAGE above.
	public string Error => !HasError ? "" : traceMode ? Entry.Error! : AppResources.TranslationFailed;

	// Trace state

	public bool TraceMode
	{
		get => traceMode;
		set => Set(ref traceMode, value, nameof(TraceMode), nameof(Error));
	}

	public bool IsTraceOpen
	{
		get => isTraceOpen;
		set => Set(ref isTraceOpen, value, nameof(IsTraceOpen), nameof(TraceToggleText));
	}

	public string TraceToggleText => isTraceOpen ? "▾ Trace" : "▸ Trace";

	// The trace's parts. See the OVERVIEW above.

	public string HeaderText { get; }
	public string TotalText { get; }
	public bool Ok { get; }
	public bool Failed => !Ok;
	public string BadgeText { get; }
	public List<ProblemGroup> ProblemGroups { get; } = new List<ProblemGroup>();
	public List<AnalysisRow> Analyses { get; } = new List<AnalysisRow>();
	public List<MessageRow> Messages { get; } = new List<MessageRow>();
	public List<StepRow> Steps { get; } = new List<StepRow>();
	public string OutsideText { get; } = "";
	public string SourceStream => Entry.SourceStream ?? "";
	public string TargetStream => Entry.TargetStream ?? "";
	public string ErrorDetail => Entry.ErrorDetail ?? "";
	public Section AnalysesSection { get; }
	public Section MessagesSection { get; }
	public Section StepsSection { get; }
	public Section StreamsSection { get; }
	public Section ExceptionSection { get; }
	public bool HasProblems => ProblemGroups.Count > 0;
	public bool HasAnalyses => Analyses.Count > 0;
	public bool HasMessages => Messages.Count > 0;
	public bool HasSteps => Steps.Count > 0;
	public bool HasStreams => SourceStream.Length > 0 || TargetStream.Length > 0;
	public bool HasErrorDetail => ErrorDetail.Length > 0;

	void Set(ref bool field, bool value, params string[] names)
	{

		if (field == value)
		{
			return;
		}

		field = value;

		foreach (string name in names)
		{
			PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
		}
	}

	// Each paragraph on its own line, with runs of spaces made single. See TRAPS above.
	static string Tidy(string? translation)
	{
		IEnumerable<string> lines = (translation ?? "").Split('\n').Select(line => string.Join(" ", line.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries))).Where(line => line.Length > 0);

		return string.Join("\n", lines);
	}

	// The web page's formatting: two decimals under ten seconds, one above
	static string Seconds(double seconds)
	{
		return seconds < 10 ? $"{seconds:F2} s" : $"{seconds:F1} s";
	}

	// The lists that have words, each word once
	static List<ProblemGroup> Problems(RunResult record)
	{
		var groups = new List<ProblemGroup>();

		foreach ((string label, Func<RunResult, List<string>> words) in ProblemLists)
		{
			List<string> unique = words(record).Distinct(StringComparer.Ordinal).ToList();

			if (unique.Count > 0)
			{
				groups.Add(new ProblemGroup(label, unique));
			}
		}

		return groups;
	}

	// Each step with its bar, scaled to the longest step as the web page scales them, and the time outside the steps
	static (List<StepRow>, string) StepRows(RunResult record)
	{

		if (record.Timings.Count == 0)
		{
			return (new List<StepRow>(), "");
		}

		double longest = Math.Max(record.Timings.Max(timing => timing.Seconds), 0.001);
		List<StepRow> rows = record.Timings.Select(timing => new StepRow(timing.Step, Seconds(timing.Seconds), Math.Max(BarWidth * timing.Seconds / longest, 0))).ToList();
		string outside = record.TotalSeconds is double total ? Seconds(Math.Max(total - record.Timings.Sum(timing => timing.Seconds), 0)) : "";

		return (rows, outside);
	}
}
