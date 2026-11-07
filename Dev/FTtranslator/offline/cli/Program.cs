// Program.cs - ftoffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. The command line for FTOffline: translate a text from a bundle, or check the port against the Python translator.
//
// OVERVIEW (AI generated, then edited)
//
// Three commands. translate runs OfflineTranslator on a text and prints the translation (and, with --record, the run record as JSON), so a bundle can be tried without the phone app. check and
// check-textout are the developer's comparisons with the Python translator, in StageCheck.cs: check compares every step on the texts tests/make_stages.py recorded, and check-textout every
// Text In/Out rule found on the machine on the cases tests/make_textout_cases.py wrote.
//
// CODE STRUCTURE
//
// Main() dispatches; Translate() is the translate command, and the checks are StageCheck.Run() and StageCheck.RunTextOut().
//

using System.Diagnostics;
using System.Text.Encodings.Web;
using System.Text.Json;
using FTtranslator.Offline;

static class Program
{
	static readonly JsonSerializerOptions JsonOptions = new JsonSerializerOptions { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping, WriteIndented = true };

	static int Main(string[] args)
	{
		Console.OutputEncoding = new System.Text.UTF8Encoding(false);

		if (args.Length >= 2 && args[0] == "translate")
		{
			return Translate(args[1], args.Skip(2).ToList());
		}

		if (args.Length >= 3 && args[0] == "check")
		{
			var started = Stopwatch.StartNew();
			using var translator = new OfflineTranslator(args[1]);
			Console.WriteLine($"Loaded {args[1]} in {started.Elapsed.TotalSeconds:F1} s");

			return StageCheck.Run(translator, args[2], Console.Out, args.Length > 3 ? int.Parse(args[3]) : 5).AllIdentical ? 0 : 1;
		}

		if (args.Length >= 2 && args[0] == "check-textout")
		{
			return StageCheck.RunTextOut(args[1], Console.Out) == 0 ? 0 : 1;
		}

		Console.Error.WriteLine("Usage:\n  ftoffline translate <bundle> [text file] [--record]     (the text from stdin without a file)\n  ftoffline check <bundle> <stages folder> [differences to show]\n  ftoffline check-textout <cases.json>");

		return 1;
	}

	static int Translate(string bundleDir, List<string> rest)
	{
		bool record = rest.Remove("--record");
		string text = rest.Count > 0 ? File.ReadAllText(rest[0]) : Console.In.ReadToEnd();
		using var translator = new OfflineTranslator(bundleDir);
		RunResult result = translator.Translate(text.TrimStart('\uFEFF'));

		if (record)
		{
			Console.WriteLine(JsonSerializer.Serialize(result, JsonOptions));
		}
		else
		{
			Console.WriteLine(result.Translation);

			foreach (RunMessage message in result.Messages)
			{
				Console.Error.WriteLine($"{message.Level.ToUpperInvariant()}: {message.Message}");
			}
		}

		return result.Ok ? 0 : 1;
	}
}
