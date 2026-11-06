// ReferenceCheck.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. Checks the port against reference output made with the Windows Apertium tools.
//
// OVERVIEW (AI generated, then edited)
//
// How FTApertium is kept honest: a reference folder holds one folder per case, made by running the Apertium tools FLExTrans ships (see tests/make_fixtures.py and README.md), and this runs the
// port over the same inputs and reports, per stage, how many streams come out byte-identical. ftapertium check runs it on any reference folder (such as one made from real projects, which
// stays out of the repo), and the unit tests run it on tests/fixtures.
//
// THE CASE FOLDER
//
// Each stage reads the TOOL's output of the stage before, so a difference points at one stage:
//   lookup:     bilingual.dix + NNN.source.txt    -> NNN.biltrans.txt                                 (lt-proc -b -N1 -L1)
//   transfer:   tr.t1x + NNN.biltrans.txt         -> NNN.transfer.txt, NNN.trace.txt                  (apertium-transfer -b -t)
//   interchunk: tr.t2x + NNN.transfer.txt         -> NNN.interchunk.txt, NNN.interchunk-trace.txt     (apertium-interchunk -t)
//   postchunk:  tr.t3x + NNN.interchunk.txt       -> NNN.postchunk.txt, NNN.postchunk-trace.txt       (apertium-postchunk -t)
// Where a tool failed (NNN.exitcode.txt, NNN.<stage>-exitcode.txt), the port must fail with the same last message. Folders starting with _ and folders holding a SKIP-* file are passed over.
//
// CODE STRUCTURE
//
// ReferenceCheck.Run() walks the case folders, runs the lookup itself and each rules stage through CheckRulesStage(), and prints the coverage and a results table; FirstDiff() shows where
// two streams part. AllIdentical says whether every stream and trace matched.
//

using System.Diagnostics;
using System.Text;

namespace FTtranslator.Apertium;

public class ReferenceCheck
{
	static readonly string[] Stages = { "lookup", "transfer", "interchunk", "postchunk" };
	static readonly UTF8Encoding Utf8 = new(false);

	readonly TextWriter writer;
	readonly Dictionary<string, int> runs = Stages.ToDictionary(s => s, _ => 0);
	readonly Dictionary<string, int> same = Stages.ToDictionary(s => s, _ => 0);
	readonly Dictionary<string, int> traces = Stages.ToDictionary(s => s, _ => 0);
	readonly Dictionary<string, int> failsTool = Stages.ToDictionary(s => s, _ => 0);
	readonly Dictionary<string, int> failsAgreed = Stages.ToDictionary(s => s, _ => 0);
	readonly Dictionary<string, double> time = Stages.ToDictionary(s => s, _ => 0.0);
	int reported;

	// True when every stream (and trace) matched and every tool failure was reproduced
	public bool AllIdentical { get; private set; } = true;

	ReferenceCheck(TextWriter writer)
	{
		this.writer = writer;
	}

	public static ReferenceCheck Run(string root, string? only, TextWriter writer)
	{
		var check = new ReferenceCheck(writer);
		TransferRun.CollectCoverage = true;

		foreach (string caseDir in Directory.GetDirectories(root).OrderBy(d => d))
		{
			string name = Path.GetFileName(caseDir);

			if (only != null && name != only)
				continue;

			if (name.StartsWith('_') || Directory.GetFiles(caseDir, "SKIP-*").Length > 0)
				continue;

			check.RunCase(caseDir, name);
		}

		check.Summarize();

		return check;
	}

	void Report(string caseName, string line)
	{
		AllIdentical = false;

		if (reported++ < 40)
			writer.WriteLine($"  {caseName}: {line}");
	}

	static string Read(string path) => File.ReadAllText(path, Utf8);

	// The first differing lexical unit of two streams, for the report
	static string FirstDiff(string what, string expected, string actual)
	{
		int i = 0;

		while (i < actual.Length && i < expected.Length && actual[i] == expected[i])
			i++;

		int from = Math.Max(0, expected.LastIndexOf('^', Math.Max(0, Math.Min(i, expected.Length - 1))));
		string Clip(string s) => s.Substring(Math.Min(from, s.Length), Math.Min(240, Math.Max(0, s.Length - from))).ReplaceLineEndings("\\n");

		return $"{what} at char {i}:\n      tool: {Clip(expected)}\n      C#:   {Clip(actual)}";
	}

	TransferRules? Load(string caseName, string path)
	{

		if (!File.Exists(path))
			return null;

		try
		{
			return TransferRules.Load(path);
		}
		catch (Exception e)
		{
			Report(caseName, $"can't load {Path.GetFileName(path)}: {e.Message}");
			return null;
		}
	}

	void RunCase(string caseDir, string name)
	{
		// Lookup
		var watch = Stopwatch.StartNew();
		BilingualDictionary? dict = null;

		try
		{
			dict = BilingualDictionary.Load(Path.Combine(caseDir, "bilingual.dix"));
		}
		catch (Exception e)
		{
			writer.WriteLine($"  {name}: lookup skipped, can't load bilingual.dix: {e.Message}");
		}

		if (dict != null)
		{

			foreach (string sourcePath in Directory.GetFiles(caseDir, "*.source.txt").OrderBy(p => p))
			{
				string stem = Path.GetFileName(sourcePath)[..3];
				string expected = Read(Path.Combine(caseDir, $"{stem}.biltrans.txt"));
				string actual = dict.Process(Read(sourcePath));
				runs["lookup"]++;

				if (actual == expected)
					same["lookup"]++;
				else
					Report(name, FirstDiff($"{stem} lookup", expected, actual));
			}
		}

		time["lookup"] += watch.Elapsed.TotalMilliseconds;

		// The rules stages
		TransferRules? t1 = Load(name, Path.Combine(caseDir, "tr.t1x"));
		TransferRules? t2 = Load(name, Path.Combine(caseDir, "tr.t2x"));
		TransferRules? t3 = Load(name, Path.Combine(caseDir, "tr.t3x"));

		foreach (string bilPath in Directory.GetFiles(caseDir, "*.biltrans.txt").OrderBy(p => p))
		{
			string stem = Path.Combine(caseDir, Path.GetFileName(bilPath)[..3]);

			if (t1 != null)
				CheckRulesStage(name, "transfer", t1, bilPath, $"{stem}.transfer.txt", $"{stem}.trace.txt", $"{stem}.exitcode.txt");

			if (t2 != null)
				CheckRulesStage(name, "interchunk", t2, $"{stem}.transfer.txt", $"{stem}.interchunk.txt", $"{stem}.interchunk-trace.txt", $"{stem}.interchunk-exitcode.txt");

			if (t3 != null)
				CheckRulesStage(name, "postchunk", t3, $"{stem}.interchunk.txt", $"{stem}.postchunk.txt", $"{stem}.postchunk-trace.txt", $"{stem}.postchunk-exitcode.txt");
		}
	}

	// One rules stage over one stream, against the tool's output, trace and exit status
	void CheckRulesStage(string caseName, string stage, TransferRules rules, string inputPath, string expectedPath, string tracePath, string exitPath)
	{

		if (!File.Exists(inputPath) || !File.Exists(expectedPath))
			return;

		runs[stage]++;
		string expectedTrace = Read(tracePath).Replace("\r\n", "\n");
		bool toolFailed = File.Exists(exitPath);
		var run = new TransferRun(rules, Read(inputPath));
		string? error = null;
		var watch = Stopwatch.StartNew();

		try
		{
			run.Run();
		}
		catch (TransferException e)
		{
			error = e.Message;
		}

		time[stage] += watch.Elapsed.TotalMilliseconds;

		if (toolFailed)
			failsTool[stage]++;

		if (toolFailed || error != null)
		{

			if (toolFailed && error != null && expectedTrace.TrimEnd().EndsWith(error))
				failsAgreed[stage]++;
			else
				Report(caseName, $"{stage}: tool {(toolFailed ? "failed: " + expectedTrace.TrimEnd().Split('\n')[^1] : "succeeded")}; C# {(error != null ? "failed: " + error : "succeeded")}");

			return;
		}

		string actual = run.Output.ToString();
		string expected = Read(expectedPath);

		if (actual == expected)
			same[stage]++;
		else
			Report(caseName, FirstDiff(stage, expected, actual));

		if (run.Trace.ToString() == expectedTrace)
			traces[stage]++;
		else if (actual == expected)
			Report(caseName, FirstDiff(stage + " trace", expectedTrace, run.Trace.ToString()));
	}

	void Summarize()
	{
		writer.WriteLine("COVERAGE (times each ran):");

		foreach ((string what, int n) in TransferRun.Coverage.OrderBy(kv => kv.Key))
			writer.WriteLine($"  {n,9}  {what}");

		writer.WriteLine("RESULTS:");

		foreach (string s in Stages)
			writer.WriteLine($"  {s,-10}  {runs[s],4} streams: {same[s]} identical{(s == "lookup" ? "" : $", traces {traces[s]}, tool failed on {failsTool[s]} and C# reproduced {failsAgreed[s]}")}  ({time[s] / 1000:F1} s)");
	}
}
