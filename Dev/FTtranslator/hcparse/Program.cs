// Program.cs - HCParse
//
// Ron Lockwood
// SIL International
// 11/3/26
//
// Version 3.17 - 11/3/26 - Ron Lockwood
//  Initial version. FieldWorks' HermitCrab word parsing (HCParser) without FieldWorks, for .NET 8 on Linux.
//
// OVERVIEW (AI generated, then edited)
//
// Parses words the way FLEx's HermitCrab parser does, from files instead of an open project. FieldWorks' HCParser (Src/LexText/ParserCore/HCParser.cs) builds a HermitCrab Language from the
// project, runs SIL.Machine's Morpher on a word, and turns each result into the project's objects: the allomorph (MoForm), the msa and the inflection type of every morph. Here the Language comes
// from parser.xml and the objects are GUIDs from parser.json, both written by FTtranslator's export-bundle from the HCParser the desktop actually uses. The Morpher gets the same settings, and
// ParseWord(), GetMorphs() and ProcessParseException() below follow HCParser's line for line, with its LCModel lookups (IMoFormRepository and so on) replaced by lookups in parser.json.
//
// USAGE
//
//   dotnet HCParse.dll parser.xml parser.json < words.txt > results.jsonl
//
// One word per input line (already prepared as FLEx prepares it: NFD, spaces as '.'); one JSON object per output line, written as soon as the word is parsed, so a caller can keep one process
// running and feed it words. Each object is {"word", "error", "analyses"}: error is HCParser's message when the parse threw, else null; analyses is a list of analyses, each a list of morphs
// {"form", "entry", "msa", "inflType", "guessed"} (GUIDs, with inflType and guessed null when absent). An empty list means the word got no parses.
//
// TRAPS
//
//  - The HC property keys are HCParser's: "ID" is both FormID (on an allomorph) and MsaID (on a morpheme), "ID2" is FormID2 (the suffix part of a circumfix) and "InflTypeID" is on a morpheme.
//    After the XML round trip a property may come back as a string rather than an int, so ReadInt() accepts both.
//  - An analysis whose objects aren't all in parser.json is dropped, as HCParser drops one whose objects it can't find in the project.
//
// CODE STRUCTURE
//
// Main() loads the files and runs the read-parse-write loop. ParserData holds parser.json. ParseWord(), GetMorphs() and ProcessParseException() are the ports; ReadInt() reads a property.
//

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using HCSynthByGloss;
using SIL.Machine.Annotations;
using SIL.Machine.Morphology.HermitCrab;
using SIL.Machine.Morphology.HermitCrab.MorphologicalRules;
using SIL.Machine.Rules;

namespace FTtranslator.HCParse
{
	// parser.json, as export-bundle writes it
	class ParserSettings
	{
		public int DeletionReapplications { get; set; }
		public int MaxStemCount { get; set; } = 2;
		public bool MergeEquivalentAnalyses { get; set; }
		public int MaxAlternatives { get; set; }
		public bool AlwaysEnforceFinalTemplates { get; set; }
		public bool GuessRoots { get; set; }
	}

	class FormInfo
	{
		public string Guid { get; set; }
		public string Entry { get; set; }
		public string MorphType { get; set; }
	}

	class ParserData
	{
		public ParserSettings Settings { get; set; }
		public Dictionary<int, FormInfo> Forms { get; set; }
		public Dictionary<int, string> Msas { get; set; }
		public Dictionary<int, string> InflTypes { get; set; }
	}

	class MorphInfo
	{
		public FormInfo Form;
		public string GuessedString;
		public string Msa;
		public string InflType;
		public bool IsCircumfix;
	}

	static class Program
	{
		// MoMorphTypeTags GUIDs
		const string MorphCircumfix = "d7f713df-e8cf-11d3-9764-00c04f186933";
		const string MorphInfix = "d7f713da-e8cf-11d3-9764-00c04f186933";
		const string MorphInfixingInterfix = "18d9b1c3-b5b6-4c07-b92c-2fe1d2281bd4";

		// HCParser's property keys
		const string FormID = "ID";
		const string FormID2 = "ID2";
		const string MsaID = "ID";
		const string InflTypeID = "InflTypeID";

		// ParserCoreStrings
		const string ksHCInvalidWordform = "There is at least one undefined phoneme in the word '{0}'. The following phonemes were parsed: '{3}'.  The problem begins with character/diacritic number {1} – that is, in the part of the word '{2}'.  Please make sure all phonemes in the word have been defined.";
		const string ksMaxAlternativesExceeded = "MaxAlternatives exceeded";
		const string ksHCDefaultErrorMsg = "The parser gave the following cryptic message (you may need to contact FieldWorks support to know what it means): {0}";

		static ParserData s_data;

		static int Main(string[] args)
		{
			if (args.Length != 2)
			{
				Console.Error.WriteLine("Usage: HCParse parser.xml parser.json < words.txt > results.jsonl");
				return 1;
			}

			var jsonOptions = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
			s_data = JsonSerializer.Deserialize<ParserData>(File.ReadAllText(args[1], Encoding.UTF8), jsonOptions);
			Language language = XmlLanguageLoader.Load(args[0]);
			ParserSettings settings = s_data.Settings;

			// As HCParser.LoadParser(), with tracing off
			var morpher = new Morpher(new HcXmlTraceManager { IsTracing = false }, language)
			{
				DeletionReapplications = settings.DeletionReapplications,
				MaxStemCount = settings.MaxStemCount,
				MergeEquivalentAnalyses = settings.MergeEquivalentAnalyses,
				MaxAlternatives = settings.MaxAlternatives,
				AlwaysEnforceFinalTemplates = settings.AlwaysEnforceFinalTemplates,
			};

			var input = new StreamReader(Console.OpenStandardInput(), new UTF8Encoding(false));
			var output = new StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false)) { AutoFlush = true };
			string line;

			while ((line = input.ReadLine()) != null)
			{
				output.WriteLine(ParseWord(morpher, line, settings.GuessRoots));
			}

			return 0;
		}

		// HCParser.ParseWord()
		static string ParseWord(Morpher morpher, string word, bool guessRoots)
		{
			IEnumerable<Word> wordAnalyses;

			try
			{
				wordAnalyses = morpher.ParseWord(word, out _, guessRoots).ToList();
			}
			catch (Exception e)
			{
				return JsonSerializer.Serialize(new { word, error = ProcessParseException(e), analyses = new List<object>() });
			}

			var analyses = new List<List<object>>();

			foreach (Word wordAnalysis in wordAnalyses)
			{
				List<MorphInfo> morphs;

				if (GetMorphs(wordAnalysis, out morphs))
				{
					analyses.Add(morphs.Select(mi => (object) new { form = mi.Form.Guid, entry = mi.Form.Entry, msa = mi.Msa, inflType = mi.InflType, guessed = mi.GuessedString }).ToList());
				}
			}

			return JsonSerializer.Serialize(new { word, error = (string) null, analyses });
		}

		// HCParser.GetMorphs(), with the repository lookups done in parser.json
		static bool GetMorphs(Word ws, out List<MorphInfo> result)
		{
			var morphs = new Dictionary<Morpheme, MorphInfo>();

			var aprCircumfixes = new List<int>();
			bool isSuffixPortionOfAprCircumfix = false;

			result = new List<MorphInfo>();
			foreach (Annotation<ShapeNode> morph in ws.Morphs)
			{
				Allomorph allomorph = ws.GetAllomorph(morph);
				var formID = ReadInt(allomorph.Properties, FormID);
				if (formID == 0)
					continue;

				isSuffixPortionOfAprCircumfix = false;
				var formID2 = ReadInt(allomorph.Properties, FormID2);
				if (formID2 == 0 && allomorph is AffixProcessAllomorph)
				{
					// An affix process rule marked as a circumfix in FLEx appears twice, before and after what it attaches to (LT-21447)
					FormInfo circumForm;
					if (!s_data.Forms.TryGetValue(formID, out circumForm))
					{
						result = null;
						return false;
					}
					if (circumForm.MorphType == MorphCircumfix)
					{
						if (aprCircumfixes.Contains(formID))
						{
							isSuffixPortionOfAprCircumfix = true;
						}
						else
						{
							aprCircumfixes.Add(formID);
						}
					}
				}

				string formStr = ws.Shape.GetNodes(morph.Range).ToString(ws.Stratum.CharacterDefinitionTable, false);
				int curFormID;
				MorphInfo morphInfo;
				if (!morphs.TryGetValue(allomorph.Morpheme, out morphInfo) || isSuffixPortionOfAprCircumfix)
				{
					curFormID = formID;
				}
				else if (formID2 > 0)
				{
					// circumfix
					curFormID = formID2;
				}
				else
				{
					continue;
				}

				FormInfo form;
				if (!s_data.Forms.TryGetValue(curFormID, out form))
				{
					result = null;
					return false;
				}

				var msaID = ReadInt(allomorph.Morpheme.Properties, MsaID);
				string msa;
				if (!s_data.Msas.TryGetValue(msaID, out msa))
				{
					result = null;
					return false;
				}

				var inflTypeID = ReadInt(allomorph.Morpheme.Properties, InflTypeID);
				string inflType = null;
				if (inflTypeID > 0 && !s_data.InflTypes.TryGetValue(inflTypeID, out inflType))
				{
					result = null;
					return false;
				}

				morphInfo = new MorphInfo
					{
						Form = form,
						GuessedString = allomorph.Guessed ? formStr : null,
						Msa = msa,
						InflType = inflType,
						IsCircumfix = formID2 > 0
					};

				morphs[allomorph.Morpheme] = morphInfo;

				switch (form.MorphType)
				{
					case MorphInfix:
					case MorphInfixingInterfix:
						if (result.Count == 0)
							result.Add(morphInfo);
						else
							result.Insert(result.Count - 1, morphInfo);
						break;

					default:
						result.Add(morphInfo);
						break;
				}
			}
			return true;
		}

		// HCParser.ProcessParseException(); ICU's non-spacing-mark test becomes .NET's, which agree for the BMP characters a word holds
		static string ProcessParseException(Exception e)
		{
			var ise = e as InvalidShapeException;
			if (ise != null)
			{
				string phonemesFoundSoFar = ise.String.Substring(0, ise.Position);
				string rest = ise.String.Substring(ise.Position);
				if (rest.Length > 0 && CharUnicodeInfo.GetUnicodeCategory(rest[0]) == UnicodeCategory.NonSpacingMark)
				{
					// A diacritic first would show on top of the quote in the message; a space keeps it apart
					rest = " " + rest;
				}
				return string.Format(ksHCInvalidWordform, ise.String, ise.Position + 1, rest, phonemesFoundSoFar);
			}
			if (e is MaxAlternativesExceededException)
			{
				return ksMaxAlternativesExceeded;
			}

			return string.Format(ksHCDefaultErrorMsg, e.Message);
		}

		// A property as an int: 0 when it's missing; the XML round trip may make it a string. See TRAPS above.
		static int ReadInt(IDictionary<string, object> properties, string key)
		{
			object value;

			if (properties == null || !properties.TryGetValue(key, out value) || value == null)
				return 0;

			if (value is int i)
				return i;

			int parsed;

			return int.TryParse(value.ToString(), NumberStyles.Integer, CultureInfo.InvariantCulture, out parsed) ? parsed : 0;
		}
	}
}
