// StageCheck.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. Compares every step of the C# translator with the Python translator's recorded steps, and the Text Out rules with textout.py's results.
//
// OVERVIEW (AI generated, then edited)
//
// The Python offline translator is FTOffline's reference, and these are the comparisons that keep the port honest; ftoffline check and check-textout run them, and the unit tests run them on the
// FTT-Scratch fixtures. Run() takes a folder of recorded stages (tests/make_stages.py: one JSON per text with every step's result from the Python translator), translates each text with an
// OfflineTranslator, records the C# steps through its StageObserver, and compares them step by step, so a difference points at the step that made it. RunTextOut() takes the cases file
// tests/make_textout_cases.py writes (every Text In/Out rule found, applied to real target texts by textout.py) and applies the same rules here.
//
// WHAT IS COMPARED
//
// The tokens, every parse (a word's analyses as a set: HermitCrab gives them in a different order from run to run, in both translators), the text dump after Approve Guesses, the source and
// target streams, the synthesis work files, the synthesized text, all the messages, and the run record without its title, timings and times. Three things are normalized: the work folder
// in synthesis's "put in the file:" message, the title at the start of each approved word's location (it holds the time of the run), and the order of an ambiguous word's forms in the
// surface forms, the synthesized text and the translation (%2%sulen%sulin% or %2%sulin%sulen%: HCSynthByGloss gives them in a different order from run to run, on the desktop too, which
// also changes which form the run record's unsynthesized words list). A text the Python translator failed on (an "error" key) passes when the C# one fails with the same message.
//
// CODE STRUCTURE
//
// StageCheck holds the result (counts per step, AllIdentical). Run() goes through the texts with Record() (the C# steps of one text), and puts both sides in comparable form with Canonical(),
// SortAmbiguities(), NormalizeMessages() and NormalizeRecord(); Excerpt() shortens a difference for printing. RunTextOut() is the Text Out comparison.
//

using System.Diagnostics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using FTtranslator.HCParse;

namespace FTtranslator.Offline;

public sealed class StageCheck
{
	// The steps compared, under make_stages.py's names, in the order they happen
	public static readonly string[] StageNames = { "tokens", "parses", "guessed", "source", "extractMessages", "target", "master", "parsesFile", "surface", "synthesized", "synthMessages", "result" };

	static readonly Regex WorkFolderMessage = new Regex("(put in the file: ).*$");

	public Dictionary<string, int> Identical { get; } = StageNames.ToDictionary(s => s, s => 0);
	public Dictionary<string, int> Differ { get; } = StageNames.ToDictionary(s => s, s => 0);
	public int Texts { get; private set; }
	public int TextsIdentical { get; private set; }
	public bool AllIdentical => Texts == TextsIdentical;

	// Translate every text in the stages folder and compare each step with the Python one, writing a line per text, the first showDiffs differences and a summary
	public static StageCheck Run(OfflineTranslator translator, string stagesDir, TextWriter writer, int showDiffs = 5)
	{
		var check = new StageCheck();
		int shown = 0;

		foreach (string file in Directory.GetFiles(stagesDir, "*.json").OrderBy(f => f, StringComparer.Ordinal))
		{
			JsonNode expected = JsonNode.Parse(File.ReadAllBytes(file))!;
			string name = Path.GetFileNameWithoutExtension(file);
			var textStarted = Stopwatch.StartNew();
			Dictionary<string, JsonNode?> actual = Record(translator, (string)expected["input"]!, out string? error);
			bool allSame = true;
			check.Texts++;

			// A failure must be the same failure
			string? expectedError = (string?)expected["error"];

			if (expectedError != null || error != null)
			{
				bool same = expectedError == error;
				allSame &= same;

				if (!same && shown++ < showDiffs)
				{
					writer.WriteLine($"{name}: the Python translator {(expectedError == null ? "succeeded" : "failed: " + expectedError)}, the C# one {(error == null ? "succeeded" : "failed: " + error)}");
				}
			}

			foreach (string stage in StageNames)
			{
				JsonNode? e = expected[stage];
				JsonNode? a = actual.GetValueOrDefault(stage);

				// A stage the failure stopped before is in neither
				if (e == null && a == null)
				{
					continue;
				}

				if (stage == "parses")
				{
					e = Canonical(e);
					a = Canonical(a);
				}
				else if (stage == "tokens" || stage == "guessed")
				{
					e = e?["occurrences"];
					a = a?["occurrences"];
				}
				else if (stage == "extractMessages" || stage == "synthMessages")
				{
					e = NormalizeMessages(e);
					a = NormalizeMessages(a);
				}
				else if (stage == "surface" || stage == "synthesized")
				{
					e = e == null ? null : JsonValue.Create(SortAmbiguities((string?)e));
					a = a == null ? null : JsonValue.Create(SortAmbiguities((string?)a));
				}
				else if (stage == "result")
				{
					e = e == null ? null : NormalizeRecord(e, (string?)expected["surface"]);
					a = a == null ? null : NormalizeRecord(a, (string?)actual.GetValueOrDefault("surface"));
				}

				bool same = JsonNode.DeepEquals(e, a);
				(same ? check.Identical : check.Differ)[stage]++;
				allSame &= same;

				if (!same && shown++ < showDiffs)
				{
					writer.WriteLine($"{name} {stage}: differs\n  Python {Excerpt(e)}\n  C#     {Excerpt(a)}");
				}
			}

			if (allSame)
			{
				check.TextsIdentical++;
			}

			writer.WriteLine($"{name}: {(allSame ? "identical" : "DIFFERS")} ({textStarted.Elapsed.TotalSeconds:F2} s)");
		}

		writer.WriteLine($"\n{check.TextsIdentical} of {check.Texts} texts identical at every step.");

		foreach (string stage in StageNames)
		{
			writer.WriteLine($"  {stage,-16} {check.Identical[stage],4} identical, {check.Differ[stage],4} differ");
		}

		return check;
	}

	// The C# steps of one text, under make_stages.py's names, with the run record as "result"; error is the message of a failure
	static Dictionary<string, JsonNode?> Record(OfflineTranslator translator, string text, out string? error)
	{
		var stages = new Dictionary<string, JsonNode?>();
		var parses = new JsonArray();
		stages["parses"] = parses;

		static JsonNode? Messages(object? value) => new JsonArray(((List<(string Level, string Message)>)value!).Select(m => (JsonNode?)new JsonArray(m.Level, m.Message)).ToArray());

		translator.StageObserver = (stage, value) =>
		{

			switch (stage)
			{
				case "parse":
					(string word, HcParseResult parse) = ((string, HcParseResult))value!;
					parses.Add(new JsonArray(word, JsonSerializer.SerializeToNode(parse)));
					break;

				case "extractMessages":
				case "synthMessages":
					stages[stage] = Messages(value);
					break;

				// Serializing copies the text dump now, before later steps change it
				default:
					stages[stage] = JsonSerializer.SerializeToNode(value, value?.GetType() ?? typeof(object));
					break;
			}
		};

		error = null;

		try
		{
			stages["result"] = JsonSerializer.SerializeToNode(translator.Translate(text));
		}
		catch (Exception e)
		{
			error = e.Message;
		}
		finally
		{
			translator.StageObserver = null;
		}

		return stages;
	}

	// Parses with each word's analyses as a sorted set (see WHAT IS COMPARED above)
	static JsonNode Canonical(JsonNode? parses)
	{
		var result = new JsonArray();

		foreach (JsonNode? item in parses?.AsArray() ?? new JsonArray())
		{
			JsonNode? parse = item![1];
			var analyses = parse!["analyses"]!.AsArray().Select(a => a!.ToJsonString()).OrderBy(s => s, StringComparer.Ordinal).Select(s => (JsonNode?)JsonValue.Create(s)).ToArray();
			result.Add(new JsonArray(item[0]!.DeepClone(), parse["error"]?.DeepClone(), new JsonArray(analyses)));
		}

		return result;
	}

	static JsonNode? NormalizeMessages(JsonNode? messages)
	{

		if (messages == null)
		{
			return null;
		}

		var copy = messages.DeepClone().AsArray();

		foreach (JsonNode? message in copy)
		{
			JsonArray pair = message!.AsArray();
			pair[1] = WorkFolderMessage.Replace((string)pair[1]!, "$1<work folder>");
		}

		return copy;
	}

	static readonly Regex AmbiguityStart = new Regex(@"%([2-9]|[1-9][0-9]+)%");
	static readonly Regex StampFailure = new Regex(@"%\d+%([^%]*)%");

	// The forms of each ambiguous word (%2%a%b%) in sorted order, since HCSynthByGloss gives them in a different order from run to run (see WHAT IS COMPARED above)
	public static string? SortAmbiguities(string? text)
	{

		if (text == null)
		{
			return null;
		}

		var sb = new StringBuilder();
		int pos = 0;
		Match match = AmbiguityStart.Match(text);

		while (match.Success)
		{
			int count = int.Parse(match.Groups[1].Value);
			var forms = new List<string>();
			int end = match.Index + match.Length;

			// The group is complete only if the count's forms, each ended by %, follow
			while (forms.Count < count)
			{
				int next = text.IndexOf('%', end);

				if (next < 0)
				{
					break;
				}

				forms.Add(text[end..next]);
				end = next + 1;
			}

			if (forms.Count == count)
			{
				sb.Append(text, pos, match.Index + match.Length - pos);
				sb.Append(string.Join("%", forms.OrderBy(f => f, StringComparer.Ordinal))).Append('%');
				pos = end;
			}

			match = AmbiguityStart.Match(text, Math.Max(end, match.Index + 1));
		}

		sb.Append(text, pos, text.Length - pos);

		return sb.ToString();
	}

	// The run record without what changes from run to run (see WHAT IS COMPARED above). The unsynthesized words are worked out again from the surface forms with their ambiguities sorted,
	// as OfflineTranslator works them out from the file, so the first form of an ambiguous word is the same on both sides.
	static JsonNode NormalizeRecord(JsonNode record, string? surface)
	{
		var copy = record.DeepClone().AsObject();

		foreach (string key in new[] { "title", "timings", "totalSeconds" })
		{
			copy.Remove(key);
		}

		if (copy["translation"] is JsonNode translation)
		{
			copy["translation"] = SortAmbiguities((string?)translation);
		}

		if (surface != null && copy["ok"] is JsonNode ok && (bool)ok)
		{
			var seen = new HashSet<string>(StringComparer.Ordinal);
			copy["unsynthesized"] = new JsonArray(StampFailure.Matches(SortAmbiguities(surface)!).Select(m => m.Groups[1].Value).Where(seen.Add).Select(w => (JsonNode?)JsonValue.Create(w)).ToArray());
		}

		foreach (JsonNode? approved in copy["approved"]!.AsArray())
		{
			string location = (string)approved!["location"]!;
			approved["location"] = location[location.IndexOf(" ¶", StringComparison.Ordinal)..];
		}

		foreach (JsonNode? message in copy["messages"]!.AsArray())
		{
			message!["message"] = WorkFolderMessage.Replace((string)message["message"]!, "$1<work folder>");
		}

		return copy;
	}

	static string Excerpt(JsonNode? node)
	{
		string text = node?.ToJsonString(new JsonSerializerOptions { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping }) ?? "(none)";

		return text.Length > 400 ? text[..400] + "..." : text;
	}

	// Apply every rule and rules file in a cases file (tests/make_textout_cases.py) to its texts and compare the results' hashes and messages with textout.py's. Returns the number that differ.
	public static int RunTextOut(string casesFile, TextWriter writer)
	{
		JsonNode root = JsonNode.Parse(File.ReadAllBytes(casesFile))!;
		List<string> texts = root["texts"]!.AsArray().Select(t => (string)t!).ToList();
		int total = 0;
		int differ = 0;
		var differing = new List<string>();

		foreach (JsonNode? testCase in root["cases"]!.AsArray())
		{
			TextOutRules rules = TextOutRules.Parse((string)testCase!["xml"]!);
			JsonArray expected = testCase["results"]!.AsArray();
			string kind = (string)testCase["kind"]!;
			int caseDiffers = 0;

			for (int i = 0; i < texts.Count; i++)
			{
				(string? text, string message, bool _) = rules.Apply(texts[i]);
				string? hash = text == null ? null : Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();
				total++;

				if (hash != (string?)expected[i]![0] || message != (string)expected[i]![1]!)
				{
					caseDiffers++;
				}
			}

			if (caseDiffers > 0)
			{
				differ += caseDiffers;
				string what = kind == "rule" && rules.Rules.Count > 0 ? $"rule {rules.Rules[0].ToDisplayString()}" : kind;
				differing.Add($"  {caseDiffers,4} text(s)  {what}");
			}
		}

		writer.WriteLine($"{total} rule applications, {total - differ} identical to textout.py, {differ} differ.");
		differing.ForEach(writer.WriteLine);

		return differ;
	}
}
