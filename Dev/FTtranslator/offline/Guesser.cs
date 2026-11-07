// Guesser.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/analysisguess.py in C#: FTtranslator's Parse Words and Approve Guesses steps without FieldWorks.
//
// OVERVIEW (AI generated, then edited)
//
// On the desktop, FTtranslator gets a text's analyses in three steps: Import Text (FLEx splits the text into words), Parse Words (HermitCrab parses each word and FieldWorks' ParseFiler files
// the results as the word's analyses) and Approve Guesses (FLEx's analysis guesser, liblcm's AnalysisGuessServices, picks one analysis per word). This file does the last two from the bundle's
// guesser.json, ported line for line from fttranslator/analysisguess.py with the same names, so the phone picks the analyses the Python translator picks. Parsing is HcWordParser (hcparse's own
// code, compiled in) called directly instead of through a running hcparse program.
//
// FILING
//
// Guesser.File() follows ParseFiler: every analysis loses its parser opinion; each parse approves the analyses it matches (same allomorphs, the same msas after the parser's merging of
// equivalent msas, the same inflection types), or becomes a new parser-approved analysis; then analyses a text uses get the user's approval, and any analysis the parser didn't approve is
// deleted if the user has no opinion of it, and otherwise disapproved by the parser (but not after a parse error). ParseAndFile() chooses the words as FTtranslator's Parse Words does: each
// word once, ignoring case, as first spelled; a capitalized word that gets no parses is parsed in lowercase; a word whose parse fails is left alone.
//
// GUESSING
//
// Guesser.BestGuess() follows AnalysisGuessServices.GetBestGuess(): the candidates are the analyses of the word's wordform, of the wordform with the word's own spelling, and, for the first
// word of a segment, of its lowercase form. Each analysis a text uses counts with priority 7, also under its neighbours (the context); every other analysis counts once with its approval's
// priority (human 6, parser 5, computer 4, none 3, parser-disapproved 2; human-disapproved ones are left out). The best is the one with the highest context score (the share of its counts next
// to this word's neighbours, before plus after), then priority, then count, then not from the lowercase form, then the lowest GUID. A wordform with no analyses first gets a computer-approved
// one from a matching single-morpheme entry, if there is one. All guesses are taken before any is applied, and an approved analysis's morphs without a sense get the sense of their msa.
//
// TRAPS
//
//  - The Python keys its count tables by context with None for "no context"; here that is NullContext, a string no real context key can be.
//  - The context score is a sum of fractions; the counts are summed in the tables' insertion order, as Python's dicts do, so a tie between two floating point sums comes out the same.
//  - Several lookups create a wordform as a side effect (Python's setdefault()), which changes later guesses in the same text: _wordform(), _wordformIfNeeded() and _generateEntryGuess() keep that.
//  - A new analysis gets a GUID that sorts after every real one, in parse order (FieldWorks would give it a random one, so a GUID tie can't be broken as on the desktop). HermitCrab gives
//    a word's parses in a different order from run to run, so File() takes them in a fixed order (ParseOrder, analysisguess.py's parseSortKey()); otherwise two new analyses tied on
//    everything else would swap GUIDs between runs and a text could be translated two ways.
//  - string.CompareOrdinal() compares UTF-16 code units where Python compares code points; they only disagree between a character outside the BMP and one in U+E000-U+FFFF, which GUIDs
//    and the Latin-script forms compared here never are.
//  - The capitalization tests use Python's str.isupper()/lower() (PyStr), and a morph with no text is described as "None:gloss", as the Python's f-string writes it.
//
// CODE STRUCTURE
//
// The guesser.json records first (GuessMorph, GuessAnalysis, GuessWordform, MonomorphemicEntry), then ParseOrder, CountEntry and ContextCounts; GuesserData reads guesser.json once. Guesser holds the data: File() and its helpers, the counting
// (AnalysisCounts(), AddCount(), FreshCounts(), ContextCounts()), the candidates (WordformIfNeeded(), MonomorphemicMatch(), GenerateEntryGuess()), and BestGuess() with Compare(). The steps
// ParseAndFile() and ApplyGuesses() are last; ParserForm() prepares a word for the parser.
//

using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using FTtranslator.HCParse;

namespace FTtranslator.Offline;

// One morph of an analysis in guesser.json
public sealed class GuessMorph
{
	public string? Form { get; set; }
	public string? Entry { get; set; }
	public string? Msa { get; set; }
	public string? Sense { get; set; }
	public string? InflType { get; set; }
	public string? Text { get; set; }

	public GuessMorph Clone() => (GuessMorph)MemberwiseClone();
}

// One analysis of a wordform, with its opinions: human/parser/computer/user are "approves", "disapproves" or null
public sealed class GuessAnalysis
{
	public string Guid { get; set; } = "";
	public string? Human { get; set; }
	public string? Parser { get; set; }
	public string? Computer { get; set; }
	public string? User { get; set; }
	public bool Used { get; set; }
	public List<GuessMorph> Bundles { get; set; } = new();

	public GuessAnalysis Clone()
	{
		var copy = (GuessAnalysis)MemberwiseClone();
		copy.Bundles = Bundles.Select(b => b.Clone()).ToList();

		return copy;
	}
}

// One wordform: its analyses and the contexts its analyses were used in, as (analysis GUID, previous key, next key)
public sealed class GuessWordform
{
	public string? Guid { get; set; }
	public List<GuessAnalysis> Analyses { get; set; } = new();
	public List<(string Guid, string PreviousKey, string NextKey)> Contexts { get; set; } = new();

	public GuessWordform Clone()
	{
		return new GuessWordform { Guid = Guid, Analyses = Analyses.Select(a => a.Clone()).ToList(), Contexts = new List<(string, string, string)>(Contexts) };
	}
}

public sealed class MonomorphemicEntry
{
	public string Form { get; set; } = "";
	public string? Morph { get; set; }
	public string? Entry { get; set; }
	public string? Msa { get; set; }
	public string? Sense { get; set; }
}

// analysisguess.py's parseSortKey() order: morph by morph, by form, entry, msa, inflection type and guessed text (missing ones as ""), compared by code point; a parse that is a prefix of
// another comes first, as Python compares lists
sealed class ParseOrder : IComparer<List<HcMorph>>
{
	public static readonly ParseOrder Instance = new ParseOrder();

	public int Compare(List<HcMorph>? x, List<HcMorph>? y)
	{

		for (int i = 0; i < Math.Min(x!.Count, y!.Count); i++)
		{
			string?[] a = { x[i].Form, x[i].Entry, x[i].Msa, x[i].InflType, x[i].Guessed };
			string?[] b = { y[i].Form, y[i].Entry, y[i].Msa, y[i].InflType, y[i].Guessed };

			for (int j = 0; j < a.Length; j++)
			{
				int compared = string.CompareOrdinal(a[j] ?? "", b[j] ?? "");

				if (compared != 0)
				{
					return compared;
				}
			}
		}

		return x.Count.CompareTo(y.Count);
	}
}

sealed class CountEntry
{
	public int Priority;
	public int Count;
	public bool Lowercased;
}

// GetContextCounts()'s result: the counts by context before and after the word, and the wordform's own (the "no context" counts)
sealed class ContextCounts
{
	public Dictionary<string, Dictionary<string, CountEntry>> Previous = new();
	public Dictionary<string, Dictionary<string, CountEntry>> Next = new();
	public Dictionary<string, CountEntry> Wordform = new();
}

// guesser.json as read once per bundle; each text gets its own Guesser copy of it (see EACH TRANSLATION STARTS FROM THE BUNDLE in OfflineTranslator.cs)
public sealed class GuesserData
{
	public const string GuesserFile = "guesser.json";

	public Dictionary<string, GuessWordform> Wordforms { get; } = new(StringComparer.Ordinal);
	public Dictionary<string, string?> RepMsas { get; } = new(StringComparer.Ordinal);
	public List<MonomorphemicEntry> Monomorphemic { get; } = new();

	public static GuesserData Load(string bundleDir)
	{
		var data = new GuesserData();
		JsonNode root = JsonNode.Parse(File.ReadAllBytes(Path.Combine(bundleDir, GuesserFile)))!;

		foreach (var (form, node) in root["wordforms"]!.AsObject())
		{
			var wordform = new GuessWordform { Guid = (string?)node!["guid"] };

			foreach (JsonNode? analysisNode in node["analyses"]!.AsArray())
			{
				var analysis = new GuessAnalysis { Guid = (string)analysisNode!["guid"]!, Human = (string?)analysisNode["human"], Parser = (string?)analysisNode["parser"], Computer = (string?)analysisNode["computer"], User = (string?)analysisNode["user"], Used = (bool?)analysisNode["used"] ?? false };

				foreach (JsonNode? bundleNode in analysisNode["bundles"]!.AsArray())
				{
					analysis.Bundles.Add(new GuessMorph { Form = (string?)bundleNode!["form"], Entry = (string?)bundleNode["entry"], Msa = (string?)bundleNode["msa"], Sense = (string?)bundleNode["sense"], InflType = (string?)bundleNode["inflType"], Text = (string?)bundleNode["text"] });
				}

				wordform.Analyses.Add(analysis);
			}

			foreach (JsonNode? context in node["contexts"]!.AsArray())
			{
				JsonArray triple = context!.AsArray();
				wordform.Contexts.Add(((string)triple[0]!, (string?)triple[1] ?? Guesser.NullContext, (string?)triple[2] ?? Guesser.NullContext));
			}

			data.Wordforms[form] = wordform;
		}

		foreach (var (msa, rep) in root["repMsas"]!.AsObject())
		{
			data.RepMsas[msa] = (string?)rep;
		}

		foreach (JsonNode? entry in root["monomorphemic"]!.AsArray())
		{
			data.Monomorphemic.Add(new MonomorphemicEntry { Form = (string)entry!["form"]!, Morph = (string?)entry["morph"], Entry = (string?)entry["entry"], Msa = (string?)entry["msa"], Sense = (string?)entry["sense"] });
		}

		return data;
	}
}

public sealed class Guesser
{
	public const string EmptyContext = "<edge>";

	// Python's None as a context key; no real key starts with a NUL. See TRAPS above.
	public const string NullContext = "\u0000null";

	readonly Lexicon lexicon;
	readonly Dictionary<string, string?> repMsas;
	readonly List<MonomorphemicEntry> monomorphemic;
	int newCount;

	public Dictionary<string, GuessWordform> Wordforms { get; }

	// Each analysis's wordform, by GUID
	public Dictionary<string, string> Owner { get; } = new(StringComparer.Ordinal);

	public Guesser(GuesserData data, Lexicon lexicon)
	{
		this.lexicon = lexicon;
		Wordforms = new Dictionary<string, GuessWordform>(StringComparer.Ordinal);

		foreach (var (form, wordform) in data.Wordforms)
		{
			Wordforms[form] = wordform.Clone();
		}

		repMsas = data.RepMsas;
		monomorphemic = data.Monomorphemic;

		foreach (var (form, wordform) in Wordforms)
		{

			foreach (GuessAnalysis analysis in wordform.Analyses)
			{
				Owner[analysis.Guid] = form;
			}
		}
	}

	public Lexicon Lexicon => lexicon;

	GuessWordform WordformRecord(string form)
	{

		if (!Wordforms.TryGetValue(form, out GuessWordform? wordform))
		{
			wordform = new GuessWordform();
			Wordforms[form] = wordform;
		}

		return wordform;
	}

	// Add an analysis the desktop would create. Its GUID sorts after every real one; see TRAPS above.
	GuessAnalysis NewAnalysis(string form, List<GuessMorph> bundles, string? computer = null)
	{
		newCount++;
		var analysis = new GuessAnalysis { Guid = $"ffffffff-ffff-ffff-ffff-{newCount:x12}", Bundles = bundles, Computer = computer };
		WordformRecord(form).Analyses.Add(analysis);
		Owner[analysis.Guid] = form;

		return analysis;
	}

	// ParseFiler: file a parse result against the wordform. See FILING above.
	public void File(string form, HcParseResult parseResult)
	{
		GuessWordform wordform = WordformRecord(form);

		foreach (GuessAnalysis analysis in wordform.Analyses)
		{
			analysis.Parser = null;
		}

		if (parseResult.Error != null)
		{
			SetUnsuccessfulParseEvals(wordform, null);
			return;
		}

		// In a fixed order, since HermitCrab's changes from run to run and decides the new analyses' GUIDs (see TRAPS above)
		foreach (List<HcMorph> parse in parseResult.Analyses.OrderBy(p => p, ParseOrder.Instance))
		{
			List<GuessAnalysis> matches = wordform.Analyses.Where(analysis => Matches(parse, analysis)).ToList();

			if (matches.Count == 0)
			{
				List<GuessMorph> bundles = parse.Select(morph => new GuessMorph { Form = morph.Form, Entry = morph.Entry, Msa = morph.Msa, Sense = null, InflType = morph.InflType, Text = morph.Guessed }).ToList();
				matches = new List<GuessAnalysis> { NewAnalysis(form, bundles) };
			}

			foreach (GuessAnalysis analysis in matches)
			{
				analysis.Parser = "approves";
			}
		}

		SetUnsuccessfulParseEvals(wordform, "disapproves");
	}

	// ParseAnalysis.MatchesIWfiAnalysis()
	bool Matches(List<HcMorph> parse, GuessAnalysis analysis)
	{
		List<GuessMorph> bundles = analysis.Bundles;

		if (bundles.Count != parse.Count)
		{
			return false;
		}

		for (int i = 0; i < bundles.Count; i++)
		{
			GuessMorph morphBundle = bundles[i];
			HcMorph morph = parse[i];

			// repMsas.get(msa, msa): an msa with no representative stands for itself (and so does None)
			string? representative = morphBundle.Msa != null && repMsas.TryGetValue(morphBundle.Msa, out string? rep) ? rep : morphBundle.Msa;

			if (morphBundle.Form != morph.Form || representative != morph.Msa || morphBundle.InflType != morph.InflType)
			{
				return false;
			}

			if (morph.Guessed != null && morphBundle.Text != morph.Guessed)
			{
				return false;
			}
		}

		return true;
	}

	static void SetUnsuccessfulParseEvals(GuessWordform wordform, string? opinion)
	{

		foreach (GuessAnalysis analysis in wordform.Analyses.ToList())
		{

			// A used analysis gets the user's (human) approval
			if (analysis.Used)
			{
				analysis.User = "approves";
				analysis.Human = "approves";
			}

			if (analysis.Parser == null)
			{

				if (analysis.User == null)
				{
					wordform.Analyses.Remove(analysis);
				}
				else if (opinion != null)
				{
					analysis.Parser = opinion;
				}
			}
		}
	}

	// AnalysisGuessServices.AddAnalysisCount(): a count under its context, and under the null (no context) entry too
	static void AddCount(Dictionary<string, Dictionary<string, CountEntry>> counts, string context, string guid, int priority, bool lowercased)
	{

		if (context != NullContext)
		{
			AddCount(counts, NullContext, guid, priority, lowercased);
		}

		if (!counts.TryGetValue(context, out Dictionary<string, CountEntry>? byGuid))
		{
			byGuid = new Dictionary<string, CountEntry>(StringComparer.Ordinal);
			counts[context] = byGuid;
		}

		if (!byGuid.TryGetValue(guid, out CountEntry? entry))
		{
			entry = new CountEntry();
			byGuid[guid] = entry;
		}

		if (entry.Priority > priority)
		{
			return;
		}

		if (entry.Priority < priority)
		{
			entry.Priority = priority;
			entry.Lowercased = lowercased;
			entry.Count = 0;
		}

		entry.Count++;
	}

	// GetAnalysisCounts(): the counts for one wordform, added to counts
	Dictionary<string, Dictionary<string, CountEntry>> AnalysisCounts(string form, bool lowercased, bool previous, Dictionary<string, Dictionary<string, CountEntry>> counts)
	{

		if (!Wordforms.TryGetValue(form, out GuessWordform? wordform))
		{
			return counts;
		}

		foreach ((string guid, string previousKey, string nextKey) in wordform.Contexts)
		{
			AddCount(counts, previous ? previousKey : nextKey, guid, 7, lowercased);
		}

		foreach (GuessAnalysis analysis in wordform.Analyses)
		{

			// Human-disapproved analyses are left out
			if (analysis.Human == "disapproves")
			{
				continue;
			}

			int priority = analysis.Human == "approves" ? 6 : analysis.Parser == "approves" ? 5 : analysis.Parser == "disapproves" ? 2 : analysis.Computer == "approves" ? 4 : 3;
			AddCount(counts, NullContext, analysis.Guid, priority, lowercased);
		}

		return counts;
	}

	static Dictionary<string, CountEntry> NoContext(Dictionary<string, Dictionary<string, CountEntry>> counts)
	{
		return counts.TryGetValue(NullContext, out Dictionary<string, CountEntry>? byGuid) ? byGuid : new Dictionary<string, CountEntry>(StringComparer.Ordinal);
	}

	ContextCounts FreshCounts(string form, bool lowercased = false)
	{
		var previous = AnalysisCounts(form, lowercased, true, new());
		var following = AnalysisCounts(form, lowercased, false, new());

		return new ContextCounts { Previous = previous, Next = following, Wordform = NoContext(previous) };
	}

	// GetContextCounts(): the counts for the word's wordform, with its original-case and lowercase wordforms' counts added
	ContextCounts GetContextCounts(string form, string? originalCase, string? lowercase)
	{

		if (lowercase == form)
		{

			if (originalCase != null)
			{
				(form, originalCase) = (originalCase, null);
			}
			else
			{
				lowercase = null;
			}
		}

		if (originalCase == form)
		{
			originalCase = null;
		}

		ContextCounts counts = FreshCounts(form);
		bool hasOriginal = originalCase != null && FreshCounts(originalCase).Wordform.Count > 0;
		bool hasLowercase = lowercase != null && FreshCounts(lowercase).Wordform.Count > 0;

		if (hasOriginal || hasLowercase)
		{

			foreach ((string? variant, bool lowercased) in new[] { (originalCase, false), (lowercase, true) })
			{

				if (variant != null && FreshCounts(variant).Wordform.Count > 0)
				{
					AnalysisCounts(variant, lowercased, true, counts.Previous);
					AnalysisCounts(variant, lowercased, false, counts.Next);
				}
			}

			counts.Wordform = NoContext(counts.Previous);
		}

		return counts;
	}

	// GetWordformIfNeeded(): the wordform with this form if there is one, or a new one if a single-morpheme entry matches it; else null
	string? WordformIfNeeded(string form)
	{

		if (Wordforms.ContainsKey(form))
		{
			return form;
		}

		if (MonomorphemicMatch(form) != null)
		{
			WordformRecord(form);
			return form;
		}

		return null;
	}

	MonomorphemicEntry? MonomorphemicMatch(string form)
	{
		string normalized = form.Normalize(NormalizationForm.FormD);

		return monomorphemic.FirstOrDefault(candidate => candidate.Form.Normalize(NormalizationForm.FormD) == normalized);
	}

	// GenerateEntryGuesses(): a wordform with no analyses gets a computer-approved one from a matching single-morpheme entry
	void GenerateEntryGuess(string? form)
	{

		if (form == null || WordformRecord(form).Analyses.Count > 0)
		{
			return;
		}

		MonomorphemicEntry? match = MonomorphemicMatch(form);

		if (match != null)
		{
			NewAnalysis(form, new List<GuessMorph> { new GuessMorph { Form = match.Morph, Entry = match.Entry, Msa = match.Msa, Sense = match.Sense, InflType = null, Text = null } }, "approves");
		}
	}

	// GetBestGuess() for a word of the new text: its wordform, its baseline text, its index in its segment and its neighbours' context keys. Returns an analysis or null.
	public GuessAnalysis? BestGuess(string form, string baseline, int indexInSegment, string previousKey, string nextKey)
	{
		string? originalCase = WordformIfNeeded(baseline);
		string? lowercase = null;

		// The lowercase form is only tried for the first word of a segment: initial capital first, then all capitals
		if (indexInSegment == 0 && baseline.Length > 0)
		{
			Rune first = Rune.GetRuneAt(baseline, 0);

			if (PyStr.IsUpper(first.ToString()))
			{
				lowercase = WordformIfNeeded(PyStr.Lower(first.ToString()) + baseline[first.Utf16SequenceLength..]);
			}

			if (lowercase == null && baseline.EnumerateRunes().All(ch => PyStr.IsUpper(ch.ToString())))
			{
				lowercase = WordformIfNeeded(PyStr.Lower(baseline));
			}
		}

		foreach (string? variant in new[] { originalCase, lowercase, form })
		{
			GenerateEntryGuess(variant);
		}

		ContextCounts counts = GetContextCounts(form, originalCase, lowercase);
		string? best = null;

		foreach (string guid in counts.Wordform.Keys)
		{

			if (best == null || Compare(guid, best, counts, previousKey, nextKey) < 0)
			{
				best = guid;
			}
		}

		if (best == null)
		{
			return null;
		}

		return Wordforms[Owner[best]].Analyses.First(analysis => analysis.Guid == best);
	}

	static double ContextScore(string guid, ContextCounts counts, string previousKey, string nextKey)
	{
		double score = 0.0;

		foreach ((string key, Dictionary<string, Dictionary<string, CountEntry>> table) in new[] { (previousKey, counts.Previous), (nextKey, counts.Next) })
		{

			if (table.TryGetValue(key, out Dictionary<string, CountEntry>? byGuid) && byGuid.TryGetValue(guid, out CountEntry? entry))
			{
				int total = 0;

				foreach (CountEntry other in byGuid.Values)
				{
					total += other.Count;
				}

				if (total > 0)
				{
					score += (double)entry.Count / total;
				}
			}
		}

		return score;
	}

	// ComparePriorityCounts(): negative if a1 is the better guess
	static int Compare(string a1, string a2, ContextCounts counts, string previousKey, string nextKey)
	{
		double score1 = ContextScore(a1, counts, previousKey, nextKey);
		double score2 = ContextScore(a2, counts, previousKey, nextKey);

		if (score1 != score2)
		{
			return score1 > score2 ? -1 : 1;
		}

		var empty = new CountEntry();
		CountEntry entry1 = counts.Wordform.TryGetValue(a1, out CountEntry? e1) ? e1 : empty;
		CountEntry entry2 = counts.Wordform.TryGetValue(a2, out CountEntry? e2) ? e2 : empty;

		if (entry1.Priority != entry2.Priority)
		{
			return entry1.Priority > entry2.Priority ? -1 : 1;
		}

		if (entry1.Count != entry2.Count)
		{
			return entry1.Count > entry2.Count ? -1 : 1;
		}

		if (entry1.Lowercased != entry2.Lowercased)
		{
			return entry1.Lowercased ? 1 : -1;
		}

		// A GUID's string order is .NET's Guid.CompareTo() order
		return Math.Sign(string.CompareOrdinal(a1, a2));
	}

	// parse_priority's parserForm(): what the parser is given for a word
	public static string ParserForm(string word)
	{
		return word.Replace(" ", ".").Normalize(NormalizationForm.FormD);
	}

	// FTtranslator's Parse Words: parse each distinct word (ignoring case, as first spelled) and file the result. Returns the words with no parse. See FILING above.
	public static List<string> ParseAndFile(TextDump textDump, Guesser guesser, Func<string, HcParseResult> parse)
	{
		var words = new List<string>();
		var seen = new HashSet<string>(StringComparer.Ordinal);

		foreach (Occurrence occurrence in textDump.Occurrences)
		{

			if (!occurrence.IsPunct && seen.Add(PyStr.Lower(occurrence.Wordform!)))
			{
				words.Add(occurrence.Wordform!);
			}
		}

		var unparsed = new List<string>();

		foreach (string word in words)
		{
			HcParseResult result = parse(ParserForm(word));

			// A capitalized word may fail only because of its capitals
			if (PyStr.Lower(word) != word && (result.Error != null || result.Analyses.Count == 0))
			{
				HcParseResult lowercaseResult = parse(ParserForm(PyStr.Lower(word)));

				if (lowercaseResult.Error == null && lowercaseResult.Analyses.Count > 0)
				{
					result = lowercaseResult;
				}
			}

			if (result.Error != null)
			{
				unparsed.Add(word);
				continue;
			}

			if (result.Analyses.Count == 0)
			{
				unparsed.Add(word);
			}

			guesser.File(word, result);
		}

		return unparsed;
	}

	// FTtranslator's Approve Guesses: take every word's guess, then apply them all, filling in senses from msas (fillSenses()). Changes the occurrences in place; returns the guesses taken.
	public static List<(Occurrence Occurrence, GuessAnalysis Guess)> ApplyGuesses(TextDump textDump, Guesser guesser)
	{

		// A word's neighbours within its segment, as context keys; segments in the order they first appear
		var segments = new Dictionary<int, List<Occurrence>>();

		foreach (Occurrence occurrence in textDump.Occurrences)
		{

			if (!segments.TryGetValue(occurrence.Seg, out List<Occurrence>? list))
			{
				list = new List<Occurrence>();
				segments[occurrence.Seg] = list;
			}

			list.Add(occurrence);
		}

		static string ContextKey(Occurrence occurrence) => occurrence.IsPunct ? "p:" + occurrence.Punct : "w:" + occurrence.Wordform;

		var planned = new List<(Occurrence, GuessAnalysis)>();

		foreach (List<Occurrence> segmentOccurrences in segments.Values)
		{

			for (int index = 0; index < segmentOccurrences.Count; index++)
			{
				Occurrence occurrence = segmentOccurrences[index];

				if (occurrence.IsPunct)
				{
					continue;
				}

				string previousKey = index > 0 ? ContextKey(segmentOccurrences[index - 1]) : EmptyContext;
				string nextKey = index < segmentOccurrences.Count - 1 ? ContextKey(segmentOccurrences[index + 1]) : EmptyContext;
				GuessAnalysis? guess = guesser.BestGuess(occurrence.Wordform!, occurrence.Baseline!, index, previousKey, nextKey);

				if (guess != null)
				{
					planned.Add((occurrence, guess));
				}
			}
		}

		foreach ((Occurrence occurrence, GuessAnalysis guess) in planned)
		{
			var bundles = new List<MorphBundle>();

			foreach (GuessMorph morphBundle in guess.Bundles)
			{
				string? sense = morphBundle.Sense;

				// fillSenses(): a parser-made morph has an msa but no sense
				if (sense == null && morphBundle.Msa != null)
				{
					sense = guesser.Lexicon.Msas.TryGetValue(morphBundle.Msa, out var msa) ? msa.Sense : null;
				}

				bundles.Add(new MorphBundle { MorphEntry = morphBundle.Entry, Sense = sense, Msa = morphBundle.Msa });
			}

			occurrence.Kind = Occurrence.KindAnalysis;
			occurrence.Wordform = guesser.Owner[guess.Guid];
			occurrence.Bundles = bundles;
			occurrence.Analysis = guess.Guid;
		}

		return planned;
	}
}
