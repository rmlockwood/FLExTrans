// TextDump.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. The text dump the offline steps pass along: a text's paragraphs and its occurrences (words and punctuation) with their analyses.
//
// OVERVIEW (AI generated, then edited)
//
// The data that goes from step to step in an offline translation, as the Python translator's dicts carry it (golden.py's dumpText() format): the tokenizer makes the occurrences, the guesser
// gives the words their analyses, and Extract Source Text reads them. The JSON names are the Python keys, so a text dump the Python translator recorded can be read straight into these classes
// for checking one C# step against the Python one.
//
// AN OCCURRENCE
//
// Either punctuation (Punct set: a run of non-white, non-word characters) or a word (Surface, Baseline, Wordform set, Kind "WfiWordform"). Approve Guesses turns a word into an analysed one:
// Kind becomes "WfiAnalysis", Wordform the form of the wordform the analysis belongs to (which can be the lowercase one), Analysis the analysis GUID and Bundles its morphs. Para and Seg number
// paragraphs and segments (sentences) from 0 across the whole text, and Beg and End are offsets within the paragraph in UTF-16 code units, as FieldWorks counts them.
//
// CODE STRUCTURE
//
// MorphBundle, Occurrence and TextDump, with IsPunct and IsWord helpers on Occurrence.
//

using System.Text.Json.Serialization;

namespace FTtranslator.Offline;

public sealed class MorphBundle
{
	[JsonPropertyName("morphEntry")] public string? MorphEntry { get; set; }
	[JsonPropertyName("sense")] public string? Sense { get; set; }
	[JsonPropertyName("msa")] public string? Msa { get; set; }
}

public sealed class Occurrence
{
	public const string KindWordform = "WfiWordform";
	public const string KindAnalysis = "WfiAnalysis";
	public const string KindGloss = "WfiGloss";

	[JsonPropertyName("para")] public int Para { get; set; }
	[JsonPropertyName("seg")] public int Seg { get; set; }
	[JsonPropertyName("beg")] public int Beg { get; set; }
	[JsonPropertyName("end")] public int End { get; set; }

	// Punctuation only
	[JsonPropertyName("punct")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Punct { get; set; }

	// Words only
	[JsonPropertyName("surface")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Surface { get; set; }
	[JsonPropertyName("baseline")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Baseline { get; set; }
	[JsonPropertyName("kind")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Kind { get; set; }
	[JsonPropertyName("wordform")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Wordform { get; set; }

	// Analysed words only (Kind "WfiAnalysis"): the analysis GUID and its morphs
	[JsonPropertyName("analysis")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public string? Analysis { get; set; }
	[JsonPropertyName("bundles")] [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] public List<MorphBundle>? Bundles { get; set; }

	[JsonIgnore] public bool IsPunct => Punct != null;
}

public sealed class TextDump
{
	[JsonPropertyName("title")] public string Title { get; set; } = "";
	[JsonPropertyName("paragraphs")] public List<string> Paragraphs { get; set; } = new();
	[JsonPropertyName("occurrences")] public List<Occurrence> Occurrences { get; set; } = new();
}
