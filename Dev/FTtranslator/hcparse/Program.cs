// Program.cs - HCParse
//
// Ron Lockwood
// SIL International
// 11/3/26
//
// Version 3.17.1 - 11/6/26 - Ron Lockwood
//  The parsing moved to HcWordParser.cs, so FTOffline can use it; this file is now only the read-parse-write loop. The output is unchanged.
//
// Version 3.17 - 11/3/26 - Ron Lockwood
//  Initial version. FieldWorks' HermitCrab word parsing (HCParser) without FieldWorks, for .NET 8 on Linux.
//
// OVERVIEW (AI generated, then edited)
//
// The hcparse program: FieldWorks' HermitCrab word parsing from parser.xml and parser.json, a word at a time, for FTtranslator's Python (analysisguess.py's HCParseProcess). The parsing itself
// is in HcWordParser.cs (see its header), which FTOffline also compiles in, so the program and the phone's translator parse alike.
//
// USAGE
//
//   dotnet HCParse.dll parser.xml parser.json < words.txt > results.jsonl
//
// One word per input line (already prepared as FLEx prepares it: NFD, spaces as '.'); one JSON object per output line (see THE RESULT in HcWordParser.cs), written as soon as the word is
// parsed, so a caller can keep one process running and feed it words.
//
// CODE STRUCTURE
//
// Main() loads the files into an HcWordParser and runs the read-parse-write loop.
//

using System;
using System.IO;
using System.Text;

namespace FTtranslator.HCParse
{
	static class Program
	{
		static int Main(string[] args)
		{
			if (args.Length != 2)
			{
				Console.Error.WriteLine("Usage: HCParse parser.xml parser.json < words.txt > results.jsonl");
				return 1;
			}

			var parser = new HcWordParser(args[0], args[1]);
			var input = new StreamReader(Console.OpenStandardInput(), new UTF8Encoding(false));
			var output = new StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false)) { AutoFlush = true };
			string line;

			while ((line = input.ReadLine()) != null)
			{
				output.WriteLine(HcWordParser.ToJson(parser.Parse(line)));
			}

			return 0;
		}
	}
}
