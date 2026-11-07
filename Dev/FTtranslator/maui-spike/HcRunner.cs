// HcRunner.cs - HC Spike (throwaway)
//
// Loads parser.xml/parser.json into hcparse's own HcWordParser (compiled in from hcparse/HcWordParser.cs, the class hcparse's Main() uses) and parses each word with it, writing the
// line hcparse would write.

using System.Diagnostics;
using System.Text;
using FTtranslator.HCParse;

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
		var parser = new HcWordParser(Path.Combine(dir, "parser.xml"), Path.Combine(dir, "parser.json"));

		result.LoadSeconds = watch.Elapsed.TotalSeconds;
		watch.Restart();

		var output = new StringBuilder();

		foreach (string word in File.ReadAllLines(Path.Combine(dir, "words.txt"), Encoding.UTF8))
		{

			if (word.Length == 0)
				continue;

			string line = HcWordParser.ToJson(parser.Parse(word));
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
