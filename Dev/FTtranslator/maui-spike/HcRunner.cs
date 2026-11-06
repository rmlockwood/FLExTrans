// HcRunner.cs - HC Spike (throwaway)
//
// Loads parser.xml/parser.json into a HermitCrab Morpher exactly as hcparse's Main() does, then parses each word with hcparse's own ParseWord(). ParseWord and the s_data field are private
// in Program.cs, which this spike compiles in unchanged, so they are reached through reflection rather than editing hcparse for a throwaway experiment.

using System.Diagnostics;
using System.Reflection;
using System.Text;
using System.Text.Json;
using FTtranslator.HCParse;
using HCSynthByGloss;
using SIL.Machine.Morphology.HermitCrab;

namespace HcSpike;

public class HcRunResult
{
	public string Lines { get; set; } = "";
	public int WordCount { get; set; }
	public int WithAnalyses { get; set; }
	public int WithErrors { get; set; }
	public double LoadSeconds { get; set; }
	public double ParseSeconds { get; set; }
	public string OutputPath { get; set; } = "";
}

public static class HcRunner
{
	public static async Task<HcRunResult> RunAsync()
	{
		// Copy the packaged files out to app storage, as a real app would keep downloaded bundles there
		string dir = Path.Combine(FileSystem.AppDataDirectory, "bundle");
		Directory.CreateDirectory(dir);

		foreach (string name in new[] { "parser.xml", "parser.json", "words.txt" })
		{
			using Stream src = await FileSystem.OpenAppPackageFileAsync(name);
			using FileStream dst = File.Create(Path.Combine(dir, name));
			await src.CopyToAsync(dst);
		}

		return await Task.Run(() => Run(dir));
	}

	static HcRunResult Run(string dir)
	{
		var result = new HcRunResult();
		var watch = Stopwatch.StartNew();

		// As hcparse's Main()
		var jsonOptions = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
		ParserData data = JsonSerializer.Deserialize<ParserData>(File.ReadAllText(Path.Combine(dir, "parser.json"), Encoding.UTF8), jsonOptions)!;
		Language language = XmlLanguageLoader.Load(Path.Combine(dir, "parser.xml"));
		ParserSettings settings = data.Settings;

		var morpher = new Morpher(new HcXmlTraceManager { IsTracing = false }, language)
		{
			DeletionReapplications = settings.DeletionReapplications,
			MaxStemCount = settings.MaxStemCount,
			MergeEquivalentAnalyses = settings.MergeEquivalentAnalyses,
			MaxAlternatives = settings.MaxAlternatives,
			AlwaysEnforceFinalTemplates = settings.AlwaysEnforceFinalTemplates,
		};

		// Program's private members
		Type program = typeof(ParserData).Assembly.GetType("FTtranslator.HCParse.Program")!;
		program.GetField("s_data", BindingFlags.NonPublic | BindingFlags.Static)!.SetValue(null, data);
		MethodInfo parseWord = program.GetMethod("ParseWord", BindingFlags.NonPublic | BindingFlags.Static)!;

		result.LoadSeconds = watch.Elapsed.TotalSeconds;
		watch.Restart();

		var output = new StringBuilder();

		foreach (string word in File.ReadAllLines(Path.Combine(dir, "words.txt"), Encoding.UTF8))
		{

			if (word.Length == 0)
				continue;

			string line = (string)parseWord.Invoke(null, new object[] { morpher, word, settings.GuessRoots })!;
			output.Append(line).Append('\n');
			result.WordCount++;

			// Count without a full parse of the line: an error is a non-null string, and analyses is non-empty when the line doesn't end with an empty list
			if (!line.Contains("\"error\":null"))
				result.WithErrors++;

			if (!line.EndsWith("\"analyses\":[]}"))
				result.WithAnalyses++;
		}

		result.ParseSeconds = watch.Elapsed.TotalSeconds;

		// Kept where adb can pull it: run-as org.sil.fttranslator.hcspike cat files/results.jsonl
		result.OutputPath = Path.Combine(FileSystem.AppDataDirectory, "results.jsonl");
		File.WriteAllText(result.OutputPath, output.ToString(), new UTF8Encoding(false));

#if ANDROID
		// Release builds aren't debuggable, so run-as can't read the file above; adb can read the app's external folder: /sdcard/Android/data/<app id>/files/results.jsonl
		string? external = Android.App.Application.Context.GetExternalFilesDir(null)?.AbsolutePath;

		if (external != null)
		{
			File.WriteAllText(Path.Combine(external, "results.jsonl"), output.ToString(), new UTF8Encoding(false));
		}

#endif

		result.Lines = output.ToString();

		return result;
	}
}
