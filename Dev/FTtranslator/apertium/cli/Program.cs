// Program.cs - ftapertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. The command line for FTApertium.
//
// OVERVIEW (AI generated, then edited)
//
// Three commands:
//
//   ftapertium transfer <apertium folder> <rules file>...   < source stream > target stream
//      What Run Apertium's makefile does, in one process: the bilingual lookup with <apertium folder>\bilingual.dix, then each rules file in turn (tr.t1x, or tr.t1x tr.t2x tr.t3x). The
//      rules stages' -t traces go to standard error. Exits 1 with Apertium's message where an Apertium tool would stop.
//
//   ftapertium lookup <bilingual.dix>   < source stream > bilingual stream
//      The bilingual lookup alone, as lt-proc -b -N1 -L1 with the compiled lexicon.
//
//   ftapertium check <reference folder> [case]
//      Runs the port over reference output made with the Windows Apertium tools and reports per stage (see ReferenceCheck.cs). Exits 1 unless everything is identical.
//
// CODE STRUCTURE
//
// Top-level statements: Transfer(), Lookup() and Check(), one per command.
//

using System.Text;
using FTtranslator.Apertium;

var utf8 = new UTF8Encoding(false);

int Usage()
{
	Console.Error.WriteLine("Usage:\n  ftapertium transfer <apertium folder> <rules file>...   < source stream > target stream\n  ftapertium lookup <bilingual.dix>   < source stream > bilingual stream\n  ftapertium check <reference folder> [case]");

	return 2;
}

int Transfer(string apertiumDir, string[] rulesFiles)
{
	var transfer = new ApertiumTransfer(apertiumDir, rulesFiles);
	string stream;

	using (var input = new StreamReader(Console.OpenStandardInput(), utf8))
		stream = input.ReadToEnd();

	using var output = new StreamWriter(Console.OpenStandardOutput(), utf8);
	using var error = new StreamWriter(Console.OpenStandardError(), utf8);

	try
	{
		output.Write(transfer.Transfer(stream));

		return 0;
	}
	catch (TransferException e)
	{
		error.WriteLine(e.Message);

		return 1;
	}
	finally
	{
		error.Write(transfer.Log);
	}
}

int Lookup(string dixPath)
{
	BilingualDictionary dictionary = BilingualDictionary.Load(dixPath);
	string stream;

	using (var input = new StreamReader(Console.OpenStandardInput(), utf8))
		stream = input.ReadToEnd();

	using var output = new StreamWriter(Console.OpenStandardOutput(), utf8);
	output.Write(dictionary.Process(stream));

	return 0;
}

int Check(string root, string? only)
{
	ReferenceCheck check = ReferenceCheck.Run(root, only, Console.Out);

	return check.AllIdentical ? 0 : 1;
}

if (args.Length >= 3 && args[0] == "transfer")
	return Transfer(args[1], args[2..]);

if (args.Length == 2 && args[0] == "lookup")
	return Lookup(args[1]);

if (args.Length is 2 or 3 && args[0] == "check")
	return Check(args[1], args.Length == 3 ? args[2] : null);

return Usage();
