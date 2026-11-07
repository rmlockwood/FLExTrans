// Tokenizer.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/tokenizer.py in C#: FLEx's splitting of a paragraph into segments, words and punctuation.
//
// OVERVIEW (AI generated, then edited)
//
// The Import Text step of an offline translation, ported line for line from fttranslator/tokenizer.py, which itself ports what FieldWorks' ParagraphParser (liblcm, DomainServices/ITextUtils.cs)
// does to a new paragraph of plain text: WordMaker for the words, CollectSegmentForms() and CreatePunctAnnotations() for the occurrences, and CreateOrReuseAnnotation(), TryCreatePhrase() and
// FindOrCreateWordform() for which wordform a word becomes. The result is a TextDump, the same occurrences the Python tokenizer gives, so the guesser and Extract Source Text see the same text.
// The names follow the Python's so the two can be read side by side.
//
// SENTENCES
//
// As in tokenizer.py (Ron's decision of 2026-11-03): a sentence ends at the whitespace right after a sentence-end character (SentenceEndChars, FLEx's list plus the section sign) and nowhere
// else. That is simpler than FLEx's SegmentBreaker, so segments can differ from the desktop's; words, punctuation and wordforms don't.
//
// WHICH WORDFORM A WORD BECOMES
//
// Most words become the wordform with exactly their form. A word that starts one of the project's phrases (a multi-word wordform) is joined with the words after it when they match the phrase,
// ignoring case; the longest phrase wins. The first word of the paragraph (offset 0 or 1, to allow a leading quote) falls back to the existing lowercase wordform when there is none with its
// exact form. A word with no wordform gets a new one, which exists for the rest of the text, so "dit-il" in one paragraph makes "il" and a later sentence-initial "Il" becomes "il".
//
// TRAPS
//
//  - Python indexes strings by code point, so the scanning here works on an array of code points (CodePoints), and the offsets written out are converted to UTF-16 code units, as FieldWorks
//    counts them. The two only differ after a character outside the BMP.
//  - Character classes come from .NET's Unicode data (15.0 in .NET 8), where the Python asks unicodedata (15.1) and FieldWorks ICU; they only disagree on characters whose properties changed.
//  - Numbers count as word-forming inside words (WordMaker.IsWordforming, LT-10746), so "3.5" is one word. Python's unicodedata.numeric() also knows the Unihan numeric values of a few CJK
//    ideographs, which .NET's GetNumericValue() doesn't, but those are letters (Lo) and word-forming anyway.
//  - Lowercasing is Python's str.lower() (PyStr.Lower), with the Turkish and Azeri dotted and dotless i handled as ICU's locale rules would; isspace(), strip() and splitlines() are Python's too.
//
// CODE STRUCTURE
//
// Tokenizer holds tokenizer.json (Load()). Its character tests come first (IsWordForming(), IsWordformingInWord(), IsWhite()), then Segments(), NextWord(), MatchesWordInText(),
// TryCreatePhrase() and WordformFor(), then TokenizeParagraph(), which puts them together, and TokenizeText(), which splits a text into paragraphs as FTtranslator's Import Text does and returns
// a TextDump. CodePoints is the code point array with its UTF-16 offsets.
//

using System.Globalization;
using System.Text;
using System.Text.Json;

namespace FTtranslator.Offline;

// A string as Python sees it: an array of code points, with each one's UTF-16 offset (and the end's) for the offsets FieldWorks gives
sealed class CodePoints
{
	public readonly int[] Values;
	public readonly int[] Utf16;

	public CodePoints(string s)
	{
		var values = new List<int>(s.Length);

		foreach (Rune rune in s.EnumerateRunes())
		{
			values.Add(rune.Value);
		}

		Values = values.ToArray();
		Utf16 = new int[Values.Length + 1];

		for (int i = 0; i < Values.Length; i++)
		{
			Utf16[i + 1] = Utf16[i] + (Values[i] > 0xFFFF ? 2 : 1);
		}
	}

	public int Length => Values.Length;

	public int this[int index] => Values[index];

	// text[start:limit]
	public string Slice(int start, int limit)
	{
		var sb = new StringBuilder();

		for (int i = start; i < limit; i++)
		{
			sb.Append(char.ConvertFromUtf32(Values[i]));
		}

		return sb.ToString();
	}
}

public sealed class Tokenizer
{
	public const string TokenizerFile = "tokenizer.json";

	// The characters a sentence can end with: FLEx's list (liblcm TsStringUtils.IsEndOfSentenceChar()) plus the section sign. See SENTENCES above.
	static readonly HashSet<int> SentenceEndChars = new HashSet<int> { 0x0021, 0x002E, 0x003F, 0x055C, 0x055E, 0x0589, 0x061F, 0x06D4, 0x0700, 0x0701, 0x0702, 0x0964, 0x0965, 0x104A, 0x104B,
		0x1362, 0x1367, 0x1368, 0x166E, 0x1803, 0x1809, 0x1944, 0x1945, 0x17D4, 0x17D5, 0x203C, 0x203D, 0x2047, 0x2048, 0x2049, 0x3002, 0xFE52, 0xFE56, 0xFE57, 0xFF01, 0xFF0E, 0xFF1F, 0xFF61,
		0x00A7 };

	const int ZeroWidthSpace = 0x200B;

	readonly string wsId;
	readonly HashSet<int> overrides;
	readonly HashSet<string> wordforms;
	readonly Dictionary<string, List<string>> phrases;

	public Tokenizer(string wsId, IEnumerable<int> overrides, IEnumerable<string> wordforms, Dictionary<string, List<string>> phrases)
	{
		this.wsId = wsId;
		this.overrides = new HashSet<int>(overrides);
		this.wordforms = new HashSet<string>(wordforms, StringComparer.Ordinal);
		this.phrases = phrases;
	}

	public static Tokenizer Load(string bundleDir)
	{
		using JsonDocument doc = JsonDocument.Parse(File.ReadAllBytes(Path.Combine(bundleDir, TokenizerFile)));
		JsonElement root = doc.RootElement;
		var phrases = new Dictionary<string, List<string>>(StringComparer.Ordinal);

		foreach (JsonProperty property in root.GetProperty("phrases").EnumerateObject())
		{
			phrases[property.Name] = property.Value.EnumerateArray().Select(p => p.GetString() ?? "").ToList();
		}

		var overrides = root.GetProperty("wordFormingOverrides").EnumerateArray().Select(o => o.GetInt32());
		var wordforms = root.GetProperty("wordforms").EnumerateArray().Select(w => w.GetString() ?? "");

		return new Tokenizer(root.GetProperty("wsId").GetString() ?? "", overrides, wordforms, phrases);
	}

	// CaseFunctions.ToLower() for the vernacular writing system
	public string ToLower(string text)
	{
		string language = wsId.Split('-')[0];

		if (language == "tr" || language == "az")
		{
			text = text.Replace("I", "ı").Replace("İ", "i");
		}

		return PyStr.Lower(text);
	}

	static readonly HashSet<UnicodeCategory> WordFormingCategories = new HashSet<UnicodeCategory> { UnicodeCategory.UppercaseLetter, UnicodeCategory.LowercaseLetter,
		UnicodeCategory.TitlecaseLetter, UnicodeCategory.ModifierLetter, UnicodeCategory.OtherLetter, UnicodeCategory.NonSpacingMark, UnicodeCategory.SpacingCombiningMark,
		UnicodeCategory.ModifierSymbol };

	// The writing system's word-forming test (CoreWritingSystemDefinition.get_IsWordForming())
	public bool IsWordForming(int ch)
	{
		return overrides.Contains(ch) || WordFormingCategories.Contains(CharUnicodeInfo.GetUnicodeCategory(ch));
	}

	// WordMaker.IsWordforming(): word-forming, or a number. See TRAPS above.
	public bool IsWordformingInWord(int ch)
	{
		return IsWordForming(ch) || CharUnicodeInfo.GetNumericValue(char.ConvertFromUtf32(ch), 0) != -1;
	}

	public static bool IsWhite(int ch)
	{
		return CharUnicodeInfo.GetUnicodeCategory(ch) == UnicodeCategory.SpaceSeparator || ch == ZeroWidthSpace;
	}

	// The (start, limit) of each segment, in code points. See SENTENCES above.
	List<(int Start, int Limit)> Segments(CodePoints text)
	{
		var segments = new List<(int, int)>();
		int start = 0;

		for (int i = 1; i < text.Length; i++)
		{

			if (SentenceEndChars.Contains(text[i - 1]) && PyStr.IsSpace(text[i]))
			{
				segments.Add((start, i));
				start = i;
			}
		}

		if (start < text.Length)
		{
			segments.Add((start, text.Length));
		}

		return segments;
	}

	// WordMaker.NextWord(): the next word at or after pos, as (start, limit), or null
	(int Start, int Limit)? NextWord(CodePoints text, int pos)
	{
		int? start = null;

		for (int i = pos; i < text.Length; i++)
		{
			bool wordForming = IsWordformingInWord(text[i]);

			if (wordForming && start == null)
			{
				start = i;
			}
			else if (!wordForming && start != null)
			{
				return (start.Value, i);
			}
		}

		if (start != null)
		{
			return (start.Value, text.Length);
		}

		return null;
	}

	// WordMaker.MatchesWordInText(): the phrase is in the text at ichMin, ignoring case, and ends where a word ends
	bool MatchesWordInText(CodePoints text, string phrase, int ichMin)
	{
		int phraseLength = new CodePoints(phrase).Length;
		int ichLim = ichMin + phraseLength;

		if (phrase.Length == 0 || ichLim > text.Length)
		{
			return false;
		}

		if (ichLim < text.Length && IsWordformingInWord(text[ichLim]))
		{
			return false;
		}

		string found = text.Slice(ichMin, ichLim);

		return found == phrase || ToLower(found) == ToLower(phrase);
	}

	// ParagraphParser.TryCreatePhrase(): the longest of the project's phrases that starts with this word and is in the text here, or null
	string? TryCreatePhrase(CodePoints text, string word, int ichMin)
	{
		string best = word;
		int wordLength = new CodePoints(word).Length;

		if (!phrases.TryGetValue(ToLower(word), out List<string>? candidates))
		{
			return null;
		}

		foreach (string phrase in candidates)
		{
			int phraseLength = new CodePoints(phrase).Length;

			if (phraseLength <= wordLength || new CodePoints(best).Length > phraseLength || !MatchesWordInText(text, phrase, ichMin))
			{
				continue;
			}

			best = phrase;
		}

		return new CodePoints(best).Length > wordLength ? best : null;
	}

	// FindOrCreateWordform(): the form of the wordform a word becomes. created holds the wordforms made earlier in the same text, and a new one is added to it.
	string WordformFor(string form, bool isFirstWord, HashSet<string> created)
	{

		if (wordforms.Contains(form) || created.Contains(form))
		{
			return form;
		}

		string lowered = ToLower(form);

		if (isFirstWord && (wordforms.Contains(lowered) || created.Contains(lowered)))
		{
			return lowered;
		}

		created.Add(form);

		return form;
	}

	// The occurrences of one paragraph and the number of segments. segOffset numbers the segments on from earlier paragraphs, and created holds the wordforms earlier paragraphs made.
	public (List<Occurrence> Occurrences, int SegmentCount) TokenizeParagraph(string paragraph, int paraIndex = 0, int segOffset = 0, HashSet<string>? created = null)
	{
		created ??= new HashSet<string>(StringComparer.Ordinal);

		var text = new CodePoints(paragraph);
		var occurrences = new List<Occurrence>();
		List<(int Start, int Limit)> segments = Segments(text);
		int pos = 0;
		int ichLimLast = 0;
		(int Start, int Limit)? pendingWord = null;
		int[] utf16 = text.Utf16;

		// CreatePunctAnnotations(): each run of non-white characters is one occurrence
		void Punctuation(int ichMin, int ichLim, int seg)
		{
			int? start = null;

			for (int i = ichMin; i < ichLim; i++)
			{

				if (IsWhite(text[i]))
				{

					if (start != null)
					{
						occurrences.Add(new Occurrence { Para = paraIndex, Seg = seg, Beg = utf16[start.Value], End = utf16[i], Punct = text.Slice(start.Value, i) });
						start = null;
					}
				}
				else if (start == null)
				{
					start = i;
				}
			}

			if (start != null)
			{
				occurrences.Add(new Occurrence { Para = paraIndex, Seg = seg, Beg = utf16[start.Value], End = utf16[ichLim], Punct = text.Slice(start.Value, ichLim) });
			}
		}

		for (int segIndex = 0; segIndex < segments.Count; segIndex++)
		{
			int segLim = segments[segIndex].Limit;
			int seg = segOffset + segIndex;
			(int Start, int Limit)? word;

			// CollectSegmentForms(), which starts where the word scanner stopped; a word found past the last segment's end is this segment's first
			if (pendingWord != null)
			{
				word = pendingWord;
				pendingWord = null;
			}
			else
			{
				word = NextWord(text, pos);

				if (word != null)
				{
					pos = word.Value.Limit;
				}
			}

			while (true)
			{

				if (word == null)
				{
					// No more words: the rest of the segment is punctuation, marked as done so the next segment doesn't repeat it
					Punctuation(ichLimLast, segLim, seg);
					ichLimLast = Math.Max(ichLimLast, segLim);
					break;
				}

				(int ichMin, int ichLim) = word.Value;

				if (ichLimLast != ichMin)
				{
					Punctuation(ichLimLast, Math.Min(ichMin, segLim), seg);

					if (ichMin >= segLim)
					{
						pendingWord = word;
						ichLimLast = segLim;
						break;
					}
				}

				// A phrase, the exact wordform, or the first word's lowercase wordform
				string wordText = text.Slice(ichMin, ichLim);
				string? phrase = phrases.Count > 0 ? TryCreatePhrase(text, wordText, ichMin) : null;
				string annotationForm = phrase ?? wordText;
				string wordform = WordformFor(annotationForm, ichMin < 2, created);

				if (phrase != null)
				{
					ichLimLast = ichMin + new CodePoints(phrase).Length;
					pos = ichLimLast;
				}
				else
				{
					ichLimLast = ichLim;
				}

				string surface = text.Slice(ichMin, ichLimLast);
				occurrences.Add(new Occurrence { Para = paraIndex, Seg = seg, Beg = utf16[ichMin], End = utf16[ichLimLast], Surface = surface, Baseline = surface, Kind = Occurrence.KindWordform, Wordform = wordform });

				word = NextWord(text, pos);

				if (word != null)
				{
					pos = word.Value.Limit;
				}
			}
		}

		return (occurrences, segments.Count);
	}

	// Split a text into paragraphs as Import Text does (each non-blank line, stripped) and tokenize them
	public TextDump TokenizeText(string text, string title = "")
	{
		var dump = new TextDump { Title = title };
		dump.Paragraphs = PyStr.SplitLines(text).Select(PyStr.Strip).Where(line => line.Length > 0).ToList();
		int segOffset = 0;
		var created = new HashSet<string>(StringComparer.Ordinal);

		for (int paraIndex = 0; paraIndex < dump.Paragraphs.Count; paraIndex++)
		{
			(List<Occurrence> paraOccurrences, int segCount) = TokenizeParagraph(dump.Paragraphs[paraIndex].Normalize(NormalizationForm.FormD), paraIndex, segOffset, created);
			dump.Occurrences.AddRange(paraOccurrences);
			segOffset += segCount;
		}

		return dump;
	}
}
