// TranslationItem.cs - FTtranslator for phones
//
// Ron Lockwood
// SIL International
// 11/7/26
//
// Version 3.17 - 11/7/26 - Ron Lockwood
//  Initial version. One translation in the list, as the screen shows it, plain or traced.
//
// OVERVIEW (AI generated, then edited)
//
// A translation as the main page shows it, made from a HistoryEntry: the current translation (under the text box) and each card of the history below it are one each. Normally that is just the
// source, small, and the translation, or the error in red. In trace mode each also has a trace section (TraceView.xaml) with what the web page's result card shows folded away, plus what only a
// trace needs:
//
//   the outcome and time      OK or the step it failed after, the total seconds, the bundle and when
//   problem words             the words with no parse, no analysis, no link to the target, or that didn't synthesize (the run record's four lists, labelled as the web page labels them)
//   step times                each step's seconds
//   analyses chosen           each word's guessed analysis and why it was chosen (the only analysis, or the best guess)
//   messages                  every message, info included, with its level
//   the Apertium streams      the source stream Extract Source Text wrote and the target stream Run Apertium made from it
//   the exception             for a step that threw, the whole exception
//
// The current translation's trace starts open, the history's closed (a whole chapter's trace is long); tapping "Trace" opens or closes one.
//
// TRAPS
//
//  - The trace texts are worked out once, when the item is made; only trace mode and the open/closed state change afterwards, and they raise PropertyChanged.
//  - The translation is tidied as the web page tidies it: each paragraph on its own line, with the synthesizer's runs of spaces made single. Copying takes the tidied text.
//
// CODE STRUCTURE
//
// TranslationItem: the plain view's properties, then the trace state (TraceMode, IsTraceOpen and the toggle's text), then the trace texts, made by the constructor with the
// helpers Summary(), Problems(), Timings(), Analyses() and Messages().
//

using System.ComponentModel;
using System.Globalization;
using System.Runtime.CompilerServices;
using System.Text;

using FTtranslator.Offline;

namespace FTtranslator.Phone;

public sealed class TranslationItem : INotifyPropertyChanged
{
	// The run record's lists of failed words, with the web page's labels
	static readonly (string Label, Func<RunResult, List<string>> Words)[] ProblemGroups =
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
		TraceSummary = Summary(entry);

		if (entry.Record != null)
		{
			TraceProblems = Problems(entry.Record);
			TraceTimings = Timings(entry.Record);
			TraceAnalyses = Analyses(entry.Record);
			TraceMessages = Messages(entry.Record);
		}
	}

	// The plain view

	public string Source => Entry.Source.Trim();
	public string Translation { get; }
	public bool HasTranslation => Translation.Length > 0;
	public string Error => Entry.Error ?? "";
	public bool HasError => Error.Length > 0;

	// Trace state

	public bool TraceMode
	{
		get => traceMode;
		set => Set(ref traceMode, value, nameof(TraceMode));
	}

	public bool IsTraceOpen
	{
		get => isTraceOpen;
		set => Set(ref isTraceOpen, value, nameof(IsTraceOpen), nameof(TraceToggleText));
	}

	public string TraceToggleText => isTraceOpen ? "▾ Trace" : "▸ Trace";

	// Trace texts, each empty when there's nothing to show

	public string TraceSummary { get; }
	public string TraceProblems { get; } = "";
	public string TraceTimings { get; } = "";
	public string TraceAnalyses { get; } = "";
	public string TraceMessages { get; } = "";
	public string SourceStream => Entry.SourceStream ?? "";
	public string TargetStream => Entry.TargetStream ?? "";
	public string ErrorDetail => Entry.ErrorDetail ?? "";
	public bool HasTraceProblems => TraceProblems.Length > 0;
	public bool HasTraceTimings => TraceTimings.Length > 0;
	public bool HasTraceAnalyses => TraceAnalyses.Length > 0;
	public bool HasTraceMessages => TraceMessages.Length > 0;
	public bool HasSourceStream => SourceStream.Length > 0;
	public bool HasTargetStream => TargetStream.Length > 0;
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

	// 'OK · 0.84 s · FTT-Scratch · 11/7/26 14:02', or the step it failed after
	static string Summary(HistoryEntry entry)
	{
		var parts = new List<string>();
		RunResult? record = entry.Record;

		if (record == null)
		{
			parts.Add("Failed");
		}
		else
		{
			parts.Add(record.Ok ? "OK" : $"Failed after {record.Steps.LastOrDefault() ?? "the start"}");

			if (record.TotalSeconds != null)
			{
				parts.Add(Seconds(record.TotalSeconds.Value));
			}
		}

		if (entry.Bundle.Length > 0)
		{
			parts.Add(entry.Bundle);
		}

		parts.Add(entry.When.ToString("g", CultureInfo.CurrentCulture));

		return string.Join(" · ", parts);
	}

	static string Seconds(double seconds)
	{
		return seconds < 10 ? $"{seconds:F2} s" : $"{seconds:F1} s";
	}

	// 'No parse: a, b' and so on, a line for each list that has words, each word once
	static string Problems(RunResult record)
	{
		var lines = new List<string>();

		foreach ((string label, Func<RunResult, List<string>> words) in ProblemGroups)
		{
			List<string> unique = words(record).Distinct(StringComparer.Ordinal).ToList();

			if (unique.Count > 0)
			{
				lines.Add($"{label}: {string.Join(", ", unique)}");
			}
		}

		return string.Join("\n", lines);
	}

	// Each step's time in a column, then the time outside the steps and the total
	static string Timings(RunResult record)
	{

		if (record.Timings.Count == 0)
		{
			return "";
		}

		int width = record.Timings.Max(timing => timing.Step.Length) + 2;
		var text = new StringBuilder();

		foreach (StepTiming timing in record.Timings)
		{
			text.Append(timing.Step.PadRight(width)).Append(Seconds(timing.Seconds).PadLeft(8)).Append('\n');
		}

		if (record.TotalSeconds != null)
		{
			double outside = Math.Max(record.TotalSeconds.Value - record.Timings.Sum(timing => timing.Seconds), 0);
			text.Append("Other".PadRight(width)).Append(Seconds(outside).PadLeft(8)).Append('\n');
			text.Append("Total".PadRight(width)).Append(Seconds(record.TotalSeconds.Value).PadLeft(8));
		}

		return text.ToString().TrimEnd('\n');
	}

	// 'word → analysis (only analysis)', one a line
	static string Analyses(RunResult record)
	{
		return string.Join("\n", record.Approved.Select(approved => $"{approved.Word} → {approved.Analysis} ({approved.Basis})"));
	}

	// '[warning] message', one a line, info messages included
	static string Messages(RunResult record)
	{
		return string.Join("\n", record.Messages.Select(message => $"[{message.Level}] {message.Message}"));
	}
}
