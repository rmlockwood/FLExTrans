// OfflineTranslator.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/offlineserver.py's OfflineTranslator in C#: translates a text from a bundle alone, every step in this process.
//
// OVERVIEW (AI generated, then edited)
//
// The entry point of FTOffline: a bundle (FTtranslator's export-bundle folder) loaded for translating, and Translate(), which runs the whole FieldWorks-free chain on a text and returns the run
// record the React page and the desktop show. It ports OfflineTranslator from fttranslator/offlineserver.py, with each step now C# in this process instead of Python plus programs:
//
//   Import Text          Tokenizer.cs (tokenizer.py)
//   Parse Words          HcWordParser (hcparse's own code) and Guesser.ParseAndFile() (analysisguess.py)
//   Approve Guesses      Guesser.ApplyGuesses() (analysisguess.py)
//   Extract Source Text  ExtractSourceText.cs (bundleextract.py)
//   Run Apertium         FTApertium's ApertiumTransfer (transfer.py with the DLL)
//   Synthesize Text      Synthesis.cs (synthesis.py's DLL branch) with HCSynthByGlossDll
//   Apply Text Out Rules TextOutRules.cs (textout.py)
//
// Each step is checked against the Python one on FTT-Scratch's and Mato-Uma's golden texts, stage by stage (see README.md), so a bundle translates the same on a phone as on the server.
//
// WHAT IS SET UP ONCE
//
// The constructor loads everything a translation needs: the lexicon, the tokenizer data, the guesser data, the bilingual lexicon's unlinked senses, the parser (parser.xml into SIL.Machine),
// the Apertium files (into FTApertium), the synthesis data (with HermitCrab.config loaded into HCSynthByGlossDll) and the Text Out rules. That is the slow part, a second or two for a big
// lexicon; after it a text takes what its parsing and synthesis take.
//
// EACH TRANSLATION STARTS FROM THE BUNDLE
//
// Each text gets a fresh Guesser made from the bundle's guesser data, so one text's parses and guesses never affect the next. The synthesizer always cleans up unknown target words
// (CleanUpUnknownTargetWords=y), whatever the bundle says, since a reader wants text, not diagnostics; the failed words still go in the run record, read from the surface forms file, which cleanup
// doesn't touch. See CLEANUP and TEXT OUT RULES in offlineserver.py.
//
// THE RUN RECORD
//
// RunResult has pipeline.RunResult's fields and JSON names: the approved words with the analysis as morph:gloss pairs and the category, the words with no parse or no analysis, the
// untranslated and unsynthesized words found as steps\finish.py finds them, the messages, and each step's time. The title is "FTT <date and time> <first three words>", as on the desktop.
//
// STAGES
//
// StageObserver, when set, gets each step's result as it finishes, under the names the Python recorder (tests/make_stages.py) uses: tokens, parse (each word), guessed, source,
// extractMessages, target, master, parsesFile, surface, synthesized and synthMessages. ftoffline check uses it to compare every step with the Python translator's on the same texts. The text dump
// is passed as the live object, which later steps change, so an observer that keeps it must copy it at once.
//
// TRAPS
//
//  - Not thread-safe: SIL.Machine's Morpher, HCSynthByGlossDll and the synthesis work files are one per translator, so Translate() takes a lock.
//  - A transfer error (a rules file Apertium would stop on) is thrown as InvalidOperationException("FTApertium transfer failed: ..."), the RuntimeError transfer.py raises.
//  - FTApertium's output gets transfer.py's \n\n to \n fix before synthesis.
//
// CODE STRUCTURE
//
// RunResult, StepTiming and RunMessage are the record. OfflineTranslator: the constructor (WHAT IS SET UP ONCE), Translate() with its Step() timer, then ApprovedWords(), Describe() and
// Untranslated() for the record, and the helpers Lemma(), Unique() and FirstWords() (copies of steps\finish.py's and steps\ingest.py's). Dispose() removes the synthesis work folder.
//

using System.Diagnostics;
using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using FTtranslator.Apertium;
using FTtranslator.HCParse;

namespace FTtranslator.Offline;

public sealed class StepTiming
{
	[JsonPropertyName("step")] public string Step { get; set; } = "";
	[JsonPropertyName("seconds")] public double Seconds { get; set; }
}

public sealed class RunMessage
{
	[JsonPropertyName("level")] public string Level { get; set; } = "";
	[JsonPropertyName("message")] public string Message { get; set; } = "";
	[JsonPropertyName("ref")] public string? Ref { get; set; }
}

public sealed class ApprovedWord
{
	[JsonPropertyName("word")] public string Word { get; set; } = "";
	[JsonPropertyName("location")] public string Location { get; set; } = "";
	[JsonPropertyName("analysis")] public string Analysis { get; set; } = "";
	[JsonPropertyName("basis")] public string Basis { get; set; } = "";
}

// pipeline.RunResult: one translation's outcome, with the run record's names
public sealed class RunResult
{
	[JsonPropertyName("title")] public string? Title { get; set; }
	[JsonPropertyName("source")] public string Source { get; set; } = "";
	[JsonPropertyName("translation")] public string? Translation { get; set; }
	[JsonPropertyName("ok")] public bool Ok { get; set; }
	[JsonPropertyName("steps")] public List<string> Steps { get; set; } = new();
	[JsonPropertyName("approved")] public List<ApprovedWord> Approved { get; set; } = new();
	[JsonPropertyName("unparsed")] public List<string> Unparsed { get; set; } = new();
	[JsonPropertyName("unanalysed")] public List<string> Unanalysed { get; set; } = new();
	[JsonPropertyName("untranslated")] public List<string> Untranslated { get; set; } = new();
	[JsonPropertyName("unsynthesized")] public List<string> Unsynthesized { get; set; } = new();
	[JsonPropertyName("messages")] public List<RunMessage> Messages { get; set; } = new();
	[JsonPropertyName("timings")] public List<StepTiming> Timings { get; set; } = new();
	[JsonPropertyName("totalSeconds")] public double? TotalSeconds { get; set; }
}

public sealed class OfflineTranslator : IDisposable
{
	// What a new text's title starts with, as the default profile's title prefix does on the desktop
	const string TitlePrefix = "FTT";

	// steps\finish.py's patterns: a lexical unit, a synthesis failure (%0%^word<tags>$%), and a source sense with no link to the target (an identity entry in the bilingual lexicon)
	static readonly Regex LexicalUnit = new Regex(@"\^(.*?)\$", RegexOptions.CultureInvariant);
	static readonly Regex StampFailure = new Regex(@"%\d+%([^%]*)%", RegexOptions.CultureInvariant);
	static readonly Regex IdentityEntry = new Regex(@"<e[^>]*>\s*<i>([^<]*)", RegexOptions.CultureInvariant);

	readonly object translateLock = new object();
	readonly Lexicon lexicon;
	readonly Tokenizer tokenizer;
	readonly GuesserData guesserData;
	readonly HashSet<string> unlinked;
	readonly HcWordParser parser;
	readonly ApertiumTransfer transfer;
	readonly Synthesizer synthesizer;
	readonly TextOutRules? textOutRules;

	public string BundleDir { get; }
	public JsonElement Manifest { get; }

	// Called with each step's result as the step finishes, for checking a step against the Python one (ftoffline check); null normally. See STAGES above.
	public Action<string, object?>? StageObserver { get; set; }

	void Observe(string stage, object? value)
	{
		StageObserver?.Invoke(stage, value);
	}

	// A work file as Python's read_text() gives it: text mode turns \r\n and a lone \r into \n
	static string ReadTextMode(string path)
	{
		return File.Exists(path) ? File.ReadAllText(path, new UTF8Encoding(false)).Replace("\r\n", "\n").Replace('\r', '\n') : "";
	}

	// Load a bundle. See WHAT IS SET UP ONCE above.
	public OfflineTranslator(string bundleDir, string? workDir = null)
	{
		BundleDir = bundleDir;

		using (JsonDocument manifestDoc = JsonDocument.Parse(File.ReadAllBytes(Path.Combine(bundleDir, "manifest.json"))))
		{
			Manifest = manifestDoc.RootElement.Clone();
		}

		lexicon = Lexicon.Load(bundleDir);
		tokenizer = Tokenizer.Load(bundleDir);
		guesserData = GuesserData.Load(bundleDir);

		// The files the manifest names, with export-bundle's names as the defaults
		JsonElement files = Manifest.GetProperty("files");
		string parserXml = Path.Combine(bundleDir, files.TryGetProperty("parser", out JsonElement p) ? p.GetString()! : "parser.xml");
		string parserJson = Path.Combine(bundleDir, files.TryGetProperty("parserData", out JsonElement pd) ? pd.GetString()! : "parser.json");
		JsonElement apertium = files.GetProperty("apertium");
		string apertiumDir = Path.Combine(bundleDir, apertium.TryGetProperty("dir", out JsonElement d) ? d.GetString()! : "apertium");
		string[] rulesFiles = apertium.GetProperty("rules").EnumerateArray().Select(r => r.GetString()!).ToArray();

		// Source senses with no link to a target sense: steps\finish.py's identity entries in the bilingual lexicon
		string bilingualText = File.ReadAllText(Path.Combine(apertiumDir, "bilingual.dix"), new UTF8Encoding(false));
		unlinked = new HashSet<string>(IdentityEntry.Matches(bilingualText).Select(m => m.Groups[1].Value), StringComparer.Ordinal);

		parser = new HcWordParser(parserXml, parserJson);
		transfer = new ApertiumTransfer(apertiumDir, rulesFiles);

		// Always clean up, whatever the bundle's CleanUpUnknownTargetWords says. See EACH TRANSLATION STARTS FROM THE BUNDLE above.
		synthesizer = new Synthesizer(bundleDir, workDir) { Clean = "y" };

		textOutRules = TextOutRules.Load(bundleDir, Manifest);
	}

	public void Dispose()
	{
		synthesizer.Dispose();
	}

	// Translate a text with the whole chain and return its run record. Throws when a step fails outright (a transfer rules error, say); a synthesis or Text Out failure gives ok = false.
	public RunResult Translate(string text, string? title = null)
	{

		lock (translateLock)
		{
			return TranslateLocked(text, title);
		}
	}

	RunResult TranslateLocked(string text, string? title)
	{
		var started = Stopwatch.StartNew();
		var result = new RunResult { Source = text };
		List<string> paragraphs = PyStr.SplitLines(text).Select(PyStr.Strip).Where(line => line.Length > 0).ToList();
		result.Title = title ?? $"{TitlePrefix} {DateTime.Now.ToString("yyyy-MM-dd HHmmss", CultureInfo.InvariantCulture)} {FirstWords(paragraphs, 3)}";
		var messages = new List<(string Level, string Message)>();

		// Each step is timed as pipeline.run() times the desktop's
		T Step<T>(string name, Func<T> func)
		{
			var stepStarted = Stopwatch.StartNew();
			T value = func();
			result.Steps.Add(name);
			result.Timings.Add(new StepTiming { Step = name, Seconds = Math.Round(stepStarted.Elapsed.TotalSeconds, 3) });

			return value;
		}

		var guesser = new Guesser(guesserData, lexicon);
		TextDump textDump = Step("Import Text", () => tokenizer.TokenizeText(text, result.Title));
		Observe("tokens", textDump);

		// Each parse is passed on to the observer too
		HcParseResult Parse(string word)
		{
			HcParseResult parse = parser.Parse(word);
			Observe("parse", (word, parse));

			return parse;
		}

		result.Unparsed = Step("Parse Words", () => Guesser.ParseAndFile(textDump, guesser, Parse));
		var planned = Step("Approve Guesses", () => Guesser.ApplyGuesses(textDump, guesser));
		Observe("guessed", textDump);
		(result.Approved, result.Unanalysed) = ApprovedWords(textDump, planned, guesser, result.Title);
		(string sourceStream, List<(string Level, string Message)> extractMessages) = Step("Extract Source Text", () => ExtractSourceText.ExtractText(textDump, lexicon));
		Observe("source", sourceStream);
		Observe("extractMessages", extractMessages);
		messages.AddRange(extractMessages);
		string targetStream = Step("Run Apertium", () => Transfer(sourceStream));
		Observe("target", targetStream);
		result.Untranslated = Untranslated(sourceStream, targetStream);
		(string? translation, List<(string Level, string Message)> synthMessages) = Step("Synthesize Text", () => synthesizer.Synthesize(targetStream));

		// The synthesis work files, read as the Python check reads them
		if (StageObserver != null)
		{
			Observe("master", ReadTextMode(synthesizer.MasterFile));
			Observe("parsesFile", File.Exists(synthesizer.ParsesFile) ? ReadTextMode(synthesizer.ParsesFile) : null);
			Observe("surface", ReadTextMode(synthesizer.SurfaceFormsFile).TrimStart('\uFEFF'));
			Observe("synthesized", translation);
			Observe("synthMessages", synthMessages);
		}

		messages.AddRange(synthMessages);

		// The user's fix-ups, after cleanup, as Collect Output applies them. A failing rule leaves translation null.
		if (translation != null && textOutRules != null)
		{
			(string? fixedText, string textOutMessage, bool ok) = Step("Apply Text Out Rules", () => textOutRules.Apply(translation));
			messages.Add((ok ? "info" : "error", textOutMessage));
			translation = fixedText;
		}

		if (translation != null)
		{

			// Cleanup has taken the failure markers out of the translation, so the failed words come from the surface forms file, which still has them
			string surfaceForms = File.ReadAllText(synthesizer.SurfaceFormsFile, Encoding.UTF8).TrimStart('\uFEFF').Replace("\r\n", "\n");
			result.Translation = PyStr.Strip(translation);
			result.Unsynthesized = Unique(StampFailure.Matches(surfaceForms).Select(m => m.Groups[1].Value));
			result.Ok = true;
		}

		result.Messages = messages.Select(m => new RunMessage { Level = m.Level, Message = m.Message }).ToList();
		result.TotalSeconds = Math.Round(started.Elapsed.TotalSeconds, 3);

		return result;
	}

	// Run Apertium: the lookup and rules stages, with transfer.py's \n\n fix and its error message
	string Transfer(string sourceStream)
	{
		string output;

		try
		{
			output = transfer.Transfer(sourceStream);
		}
		catch (TransferException e)
		{
			throw new InvalidOperationException($"FTApertium transfer failed: {e.Message}", e);
		}

		return output.Replace("\n\n", "\n");
	}

	// The approved words as {word, location, analysis, basis}, and the words left without an analysis, as the Approve Guesses step records them on the desktop
	(List<ApprovedWord>, List<string>) ApprovedWords(TextDump textDump, List<(Occurrence Occurrence, GuessAnalysis Guess)> planned, Guesser guesser, string title)
	{

		// Each word's position: its paragraph, its sentence within the paragraph and its place in the sentence (punctuation counts, as in FLEx's segments), all from 1
		var positions = new Dictionary<Occurrence, string>(ReferenceEqualityComparer.Instance);
		var segmentCounts = new Dictionary<int, int>();
		var firstSegs = new Dictionary<int, int>();

		foreach (Occurrence occurrence in textDump.Occurrences)
		{
			firstSegs.TryAdd(occurrence.Para, occurrence.Seg);
			segmentCounts[occurrence.Seg] = segmentCounts.GetValueOrDefault(occurrence.Seg) + 1;
			positions[occurrence] = $"{title} ¶{occurrence.Para + 1} s{occurrence.Seg - firstSegs[occurrence.Para] + 1} w{segmentCounts[occurrence.Seg]}";
		}

		var approved = new List<ApprovedWord>();
		var approvedOccurrences = new HashSet<Occurrence>(ReferenceEqualityComparer.Instance);

		foreach ((Occurrence occurrence, GuessAnalysis guess) in planned)
		{
			int choices = guesser.Wordforms.TryGetValue(guesser.Owner[guess.Guid], out GuessWordform? wordform) ? wordform.Analyses.Count : 0;
			approved.Add(new ApprovedWord { Word = occurrence.Baseline!, Location = positions[occurrence], Analysis = Describe(guess), Basis = choices < 2 ? "only analysis" : "best guess" });
			approvedOccurrences.Add(occurrence);
		}

		List<string> unanalysed = textDump.Occurrences.Where(o => !o.IsPunct && !approvedOccurrences.Contains(o)).Select(o => o.Baseline!).ToList();

		return (approved, unanalysed);
	}

	// An analysis as 'mang:eat + e:PRS.3SG [v]', as parse_priority's describe() shows one: each morph with its gloss, then the stem's category
	string Describe(GuessAnalysis analysis)
	{
		var parts = new List<string>();
		string category = "";

		foreach (GuessMorph morphBundle in analysis.Bundles)
		{
			lexicon.Msas.TryGetValue(morphBundle.Msa ?? "", out Lexicon.MsaRecord? msa);
			string senseGuid = (morphBundle.Sense is { Length: > 0 } ? morphBundle.Sense : null) ?? (msa?.Sense is { Length: > 0 } ? msa.Sense : null) ?? "";
			lexicon.Senses.TryGetValue(senseGuid, out Lexicon.SenseRecord? sense);
			string gloss = sense?.Gloss is { Length: > 0 } g ? g : "?";

			// Python's f-string writes a missing text as None
			parts.Add($"{morphBundle.Text ?? "None"}:{gloss}");

			if (msa != null && msa.Stem && !string.IsNullOrEmpty(msa.Pos) && category.Length == 0)
			{
				category = $" [{msa.Pos}]";
			}
		}

		return (parts.Count > 0 ? string.Join(" + ", parts) : "(no morphemes)") + category;
	}

	// Words marked @ in the transfer results, then source words whose sense has no link to the target lexicon, as steps\finish.py's collectOutput() lists them
	List<string> Untranslated(string sourceStream, string targetStream)
	{
		var noEntry = LexicalUnit.Matches(targetStream).Select(m => m.Groups[1].Value).Where(unit => unit.StartsWith('@')).Select(Lemma);
		var noLink = LexicalUnit.Matches(sourceStream).Select(m => Lemma(m.Groups[1].Value)).Where(unlinked.Contains);

		return Unique(noEntry.Concat(noLink));
	}

	// The lemma of a lexical unit, without the @, * or # marker and the tags
	static string Lemma(string unit)
	{
		return unit.TrimStart('@', '*', '#').Split('<', 2)[0];
	}

	// The items without repeats, in their first-seen order
	static List<string> Unique(IEnumerable<string> items)
	{
		var seen = new HashSet<string>(StringComparer.Ordinal);

		return items.Where(seen.Add).ToList();
	}

	// The first count words of the text, without the punctuation that ends the last one (steps\ingest.py's firstWords())
	static string FirstWords(List<string> paragraphs, int count)
	{
		string snippet = string.Join(" ", PyStr.Split(string.Join(" ", paragraphs)).Take(count));

		while (snippet.Length > 0)
		{
			int last = char.IsLowSurrogate(snippet[^1]) && snippet.Length > 1 ? snippet.Length - 2 : snippet.Length - 1;
			UnicodeCategory category = CharUnicodeInfo.GetUnicodeCategory(snippet, last);

			if (category is not (UnicodeCategory.ConnectorPunctuation or UnicodeCategory.DashPunctuation or UnicodeCategory.OpenPunctuation or UnicodeCategory.ClosePunctuation or UnicodeCategory.InitialQuotePunctuation or UnicodeCategory.FinalQuotePunctuation or UnicodeCategory.OtherPunctuation))
			{
				break;
			}

			snippet = snippet[..last];
		}

		return snippet;
	}
}
