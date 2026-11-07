// Lexicon.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. A bundle's lexicon.json plus the Extract Source Text settings from its manifest.json, ported from fttranslator/bundleextract.py's Lexicon.
//
// OVERVIEW (AI generated, then edited)
//
// The source lexicon as an offline translation sees it: the three GUID-keyed tables bundle.py writes to lexicon.json (entries, senses, msas), and the FlexTrans.config values Extract Source Text
// reads, which bundle.py puts in the config section of manifest.json. ExtractSourceText.cs builds lexical units from it, and the guesser and the run record look senses and msas up in it too.
// The methods are bundleextract.py's Lexicon methods with the same names, so the two can be read side by side.
//
// THE THREE TABLES (see bundle.py's WHAT IT WRITES and TRAPS for the full story)
//
//  - Entries: headword (with the homograph number), clitic ("proclitic", "enclitic" or null), the top-level senses in order (a lemma's sense number is a position in this list), resolvesTo for
//    a variant with no senses of its own (the entry Utils.GetEntryWithSensePlusFeat reaches and the irregular form's feature abbreviations) and complexForms (one item per complex-form ref of
//    each complex form the entry is part of, unfiltered by type).
//  - Senses: the owning entry, the gloss (affix and clitic tags come from it) and the msa.
//  - Msas: whether it is a stem msa, the sense the msa's entry uses it for, and for a stem msa the category (pos), inflection class and sorted stem feature abbreviations.
//
// NULL VERSUS EMPTY
//
// Several fields mean different things when null and when empty, and the extraction relies on it: an msa's Pos is null when there is no category (UNK and a warning) but "" when the category's
// abbreviation is empty (an empty tag); StemFeatures is null when there is no feature structure and empty when there is an empty one (see Word.GetStemFeatures()); InflClass is null when there is
// no class but "" for a class with an empty abbreviation (a blank tag). A non-stem msa has no pos, inflClass or stemFeatures keys at all, which reads as null here, as Python's get() gives None.
//
// THE CONFIG VALUES
//
// manifest.json holds them as InterlinData.initInterlinParams() parsed them: SentencePunctuation is a string (Python joins it with ''.join(), so a list of strings would work there too, and is
// accepted here), the complex-type and category settings are lists, and NoWarningForUnanalyzedProperNouns is a bool (read with Python's truthiness if it is anything else).
//
// CODE STRUCTURE
//
// The record classes EntryRecord (with ResolvesToRecord and ComplexFormRecord), SenseRecord and MsaRecord, nested in Lexicon so their names can't clash with the rest of FTOffline. Then
// Lexicon: its tables and config values, Load() (reads the two files), and Resolve(), Headword(), IsClitic(), IsEnclitic() and SenseMsa(), the lookups ExtractSourceText.cs uses. The config
// readers (ReadString(), ReadList(), ReadTruthy()) come last.
//

using System.Text.Json;
using System.Text.Json.Serialization;

namespace FTtranslator.Offline;

public sealed class Lexicon
{
	public sealed class ResolvesToRecord
	{
		[JsonPropertyName("entry")] public string Entry { get; set; } = "";
		[JsonPropertyName("inflFeatures")] public List<string> InflFeatures { get; set; } = new();
	}

	public sealed class ComplexFormRecord
	{
		[JsonPropertyName("entry")] public string Entry { get; set; } = "";
		[JsonPropertyName("components")] public List<string> Components { get; set; } = new();
		[JsonPropertyName("types")] public List<string> Types { get; set; } = new();
	}

	public sealed class EntryRecord
	{
		[JsonPropertyName("headword")] public string Headword { get; set; } = "";
		[JsonPropertyName("clitic")] public string? Clitic { get; set; }
		[JsonPropertyName("senses")] public List<string> Senses { get; set; } = new();

		// Only for a variant with no senses of its own
		[JsonPropertyName("resolvesTo")] public ResolvesToRecord? ResolvesTo { get; set; }

		// Only for an entry that is part of some complex form; Python reads it with get("complexForms", [])
		[JsonPropertyName("complexForms")] public List<ComplexFormRecord>? ComplexForms { get; set; }
	}

	public sealed class SenseRecord
	{
		[JsonPropertyName("entry")] public string? Entry { get; set; }
		[JsonPropertyName("gloss")] public string? Gloss { get; set; }
		[JsonPropertyName("msa")] public string? Msa { get; set; }
	}

	public sealed class MsaRecord
	{
		[JsonPropertyName("stem")] public bool Stem { get; set; }
		[JsonPropertyName("sense")] public string? Sense { get; set; }

		// Stem msas only; see NULL VERSUS EMPTY above
		[JsonPropertyName("pos")] public string? Pos { get; set; }
		[JsonPropertyName("inflClass")] public string? InflClass { get; set; }
		[JsonPropertyName("stemFeatures")] public List<string>? StemFeatures { get; set; }
	}

	// The lexicon.json file as a whole
	sealed class LexiconFile
	{
		[JsonPropertyName("entries")] public Dictionary<string, EntryRecord> Entries { get; set; } = new();
		[JsonPropertyName("senses")] public Dictionary<string, SenseRecord> Senses { get; set; } = new();
		[JsonPropertyName("msas")] public Dictionary<string, MsaRecord> Msas { get; set; } = new();
	}

	// The FlexTrans.config settings the manifest carries (ReadConfig's names)
	const string SENTENCE_PUNCTUATION = "SentencePunctuation";
	const string SOURCE_FORMS_INFLECTION_1ST = "SourceComplexFormsWithInflectionOn1stElement";
	const string SOURCE_COMPLEX_TYPES = "SourceComplexTypes";
	const string SOURCE_DISCONTIG_TYPES = "SourceDiscontigousComplexTypes";
	const string SOURCE_DISCONTIG_SKIPPED = "SourceDiscontigousComplexFormSkippedWordGrammaticalCategories";
	const string NO_PROPER_NOUN_WARNING = "NoWarningForUnanalyzedProperNouns";

	public Dictionary<string, EntryRecord> Entries { get; }
	public Dictionary<string, SenseRecord> Senses { get; }
	public Dictionary<string, MsaRecord> Msas { get; }

	// SentencePunctuation, already joined into one string as extractText() joins it
	public string SentPunct { get; }
	public List<string> TypesInfl1stList { get; }
	public List<string> TypesInfl2ndList { get; }
	public List<string> DiscontigTypesList { get; }
	public List<string> DiscontigPOSList { get; }
	public bool NoWarningProperNoun { get; }

	Lexicon(LexiconFile lexiconData, JsonElement config)
	{
		Entries = lexiconData.Entries;
		Senses = lexiconData.Senses;
		Msas = lexiconData.Msas;
		SentPunct = ReadString(config, SENTENCE_PUNCTUATION);
		TypesInfl1stList = ReadList(config, SOURCE_FORMS_INFLECTION_1ST);
		TypesInfl2ndList = ReadList(config, SOURCE_COMPLEX_TYPES);
		DiscontigTypesList = ReadList(config, SOURCE_DISCONTIG_TYPES);
		DiscontigPOSList = ReadList(config, SOURCE_DISCONTIG_SKIPPED);
		NoWarningProperNoun = ReadTruthy(config, NO_PROPER_NOUN_WARNING);
	}

	// Read a bundle folder's lexicon.json and manifest.json
	public static Lexicon Load(string bundleDir)
	{
		using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(bundleDir, "manifest.json")));
		string lexiconName = manifest.RootElement.GetProperty("files").GetProperty("lexicon").GetString() ?? throw new InvalidDataException("manifest.json names no lexicon file.");
		LexiconFile lexiconData = JsonSerializer.Deserialize<LexiconFile>(File.ReadAllText(Path.Combine(bundleDir, lexiconName))) ?? throw new InvalidDataException("lexicon.json is empty.");

		// Clone, so the config outlives the JsonDocument
		return new Lexicon(lexiconData, manifest.RootElement.GetProperty("config").Clone());
	}

	// Utils.GetEntryWithSensePlusFeat(): the entry a sense-less variant leads to, and the irregularly inflected form's feature abbreviations (already sorted). Other entries are their own.
	public (string Entry, List<string> InflFeatures) Resolve(string entryGuid)
	{
		ResolvesToRecord? resolvesTo = Entries[entryGuid].ResolvesTo;

		if (resolvesTo != null)
		{
			return (resolvesTo.Entry, new List<string>(resolvesTo.InflFeatures));
		}

		return (entryGuid, new List<string>());
	}

	public string Headword(string entryGuid)
	{
		return Entries[entryGuid].Headword;
	}

	public bool IsClitic(string entryGuid)
	{
		return Entries[entryGuid].Clitic != null;
	}

	public bool IsEnclitic(string entryGuid)
	{
		return Entries[entryGuid].Clitic == "enclitic";
	}

	// The msa record of a sense, or null if it has none (Python's {}: every get() on it gives None)
	public MsaRecord? SenseMsa(string senseGuid)
	{
		string? msaGuid = Senses[senseGuid].Msa;

		// "if msaGuid" in Python: an empty GUID counts as none too
		if (string.IsNullOrEmpty(msaGuid))
		{
			return null;
		}

		return Msas.TryGetValue(msaGuid, out MsaRecord? msa) ? msa : null;
	}

	// A string setting; a list of strings is joined, as ''.join() would
	static string ReadString(JsonElement config, string name)
	{
		JsonElement value = config.GetProperty(name);

		if (value.ValueKind == JsonValueKind.Array)
		{
			return string.Concat(value.EnumerateArray().Select(item => item.GetString()));
		}

		return value.GetString() ?? "";
	}

	static List<string> ReadList(JsonElement config, string name)
	{
		return config.GetProperty(name).EnumerateArray().Select(item => item.GetString() ?? "").ToList();
	}

	// Python's truthiness of a JSON value
	static bool ReadTruthy(JsonElement config, string name)
	{
		JsonElement value = config.GetProperty(name);

		switch (value.ValueKind)
		{
			case JsonValueKind.True:
				return true;
			case JsonValueKind.String:
				return value.GetString()!.Length > 0;
			case JsonValueKind.Number:
				return value.GetDouble() != 0;
			case JsonValueKind.Array:
				return value.GetArrayLength() > 0;
			case JsonValueKind.Object:
				return value.EnumerateObject().Any();
			default:
				return false;
		}
	}
}
