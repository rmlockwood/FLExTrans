// ApertiumTransfer.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. FLExTrans' Run Apertium step in one object: bilingual lookup and one to three rules stages, loaded once.
//
// OVERVIEW (AI generated, then edited)
//
// The entry point FTtranslator uses (fttranslator/transfer.py loads this assembly with pythonnet) and the ftapertium command line runs. It does what Run Apertium's makefile does with the
// Apertium tools: lt-proc -b -N1 -L1 with the bilingual lexicon, then apertium-transfer -b -t with the .t1x and, for advanced transfer, apertium-interchunk -t with the .t2x and
// apertium-postchunk -t with the .t3x. The lexicon and rules are read when the object is made, so each Transfer() call only runs the stream through them.
//
// WHAT IT DOESN'T DO
//
// Run Apertium's own changes to the files and the result stay in Python, where they are now: the bundle's apertium folder already holds the files as Run Apertium hands them to the tools
// (see transferexport.py), and transfer.py collapses the result's double newlines as Run Apertium does.
//
// THREADS
//
// Not thread-safe underneath (the lexicon's alphabet grows with unknown tags, as lttoolbox's does), so Transfer() takes a lock; the offline server can call it from several threads.
//
// CODE STRUCTURE
//
// ApertiumTransfer: the constructor loads the files; Transfer() runs a stream and leaves the stages' -t traces in Log.
//

using System.Text;

namespace FTtranslator.Apertium;

public class ApertiumTransfer
{
	readonly BilingualDictionary dictionary;
	readonly List<TransferRules> stages = new();
	readonly object locker = new();

	// The rules stages' -t traces from the last Transfer() (what FLExTrans keeps in apertium_log.txt)
	public string Log { get; private set; } = "";

	// apertiumDir holds bilingual.dix and the rules files; rulesFiles names them in stage order: tr.t1x, or tr.t1x, tr.t2x, tr.t3x
	public ApertiumTransfer(string apertiumDir, params string[] rulesFiles)
	{
		dictionary = BilingualDictionary.Load(Path.Combine(apertiumDir, "bilingual.dix"));

		foreach (string rulesFile in rulesFiles)
			stages.Add(TransferRules.Load(Path.Combine(apertiumDir, rulesFile)));
	}

	// Run a source stream (Extract Source Text's output) through the lookup and the rules stages. Throws TransferException where an Apertium tool would stop with an error.
	public string Transfer(string stream)
	{

		lock (locker)
		{
			string output = dictionary.Process(stream);
			var log = new StringBuilder();

			try
			{

				foreach (TransferRules rules in stages)
				{
					var run = new TransferRun(rules, output);

					try
					{
						run.Run();
					}
					finally
					{
						log.Append(run.Trace);
					}

					output = run.Output.ToString();
				}
			}
			finally
			{
				Log = log.ToString();
			}

			return output;
		}
	}
}
