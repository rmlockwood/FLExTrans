// PyStr.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. Python's str methods in C#, for the ports of the offline translator's Python files.
//
// OVERVIEW (AI generated, then edited)
//
// The Python files FTOffline ports lean on str methods whose .NET look-alikes differ at the edges: Python's isspace() takes the \x1c-\x1f separators, which .NET's char.IsWhiteSpace() doesn't;
// splitlines() breaks at \v, \f, \x1c-\x1e, \x85 and the Unicode line and paragraph separators as well as \r and \n; isupper() and islower() use Unicode's Uppercase and Lowercase properties,
// wider than the Lu and Ll categories (Roman numerals, circled letters, modifier letters); title() and capitalize() use title case, which .NET has no mapping for (ǆ becomes ǅ, ß becomes Ss,
// Georgian letters stay as they are). Each function here does what Python's does, so a ported line can call it and give the same answer.
//
// WHERE THE TABLES COME FROM
//
// The constants below were generated on 11/6/26 from Python 3.13 (Unicode 15.1) with a script that lists, for every code point, where title() differs from upper() and where isupper() and
// islower() differ from the Lu and Ll categories; the rest is .NET's own Unicode data (Unicode 15.0 in .NET 8), which agrees with Python's elsewhere. Python's upper() and lower() are in
// FullCase.cs.
//
// INDEXES
//
// Python indexes strings by code point, .NET by UTF-16 code unit; they differ only after a character outside the BMP. These functions take and return .NET strings, so callers that index
// must keep that in mind (the tokenizer ports work on code point arrays for that reason).
//
// CODE STRUCTURE
//
// The tables and their parsed sets first; then the character tests (IsSpace(), IsUppercase(), IsLowercase(), IsTitlecase(), IsCased()), the string tests (IsUpper(), IsLower()), the case
// changes (Upper(), Lower(), Title(), Capitalize(), TitleRune()), and the splitting (Strip(), LStrip(), RStrip(), Split(), SplitLines()).
//

using System.Globalization;
using System.Text;

namespace FTtranslator.Offline;

public static class PyStr
{
	// Characters whose title case is themselves although their upper case isn't (Georgian Mkhedruli, the Dž-type digraphs, Greek with prosgegrammeni)
	const string TitleIsSelf =
		"01C5 01C8 01CB 01F2 10D0-10FA 10FD-10FF 1F88-1F8F 1F98-1F9F 1FA8-1FAF 1FBC 1FCC 1FFC";

	// Characters whose title case differs from their upper case, and isn't themselves
	const string TitleMapped =
		"00DF=0053 0073;01C4=01C5;01C6=01C5;01C7=01C8;01C9=01C8;01CA=01CB;01CC=01CB;01F1=01F2;01F3=01F2;0587=0535 0582;1F80=1F88;1F81=1F89;1F82=1F8A;1F83=1F8B;1F84=1F8C;1F85=1F8D;1F86=1F8E;" +
		"1F87=1F8F;1F90=1F98;1F91=1F99;1F92=1F9A;1F93=1F9B;1F94=1F9C;1F95=1F9D;1F96=1F9E;1F97=1F9F;1FA0=1FA8;1FA1=1FA9;1FA2=1FAA;1FA3=1FAB;1FA4=1FAC;1FA5=1FAD;1FA6=1FAE;1FA7=1FAF;" +
		"1FB2=1FBA 0345;1FB3=1FBC;1FB4=0386 0345;1FB7=0391 0342 0345;1FC2=1FCA 0345;1FC3=1FCC;1FC4=0389 0345;1FC7=0397 0342 0345;1FF2=1FFA 0345;1FF3=1FFC;1FF4=038F 0345;1FF7=03A9 0342 0345;" +
		"FB00=0046 0066;FB01=0046 0069;FB02=0046 006C;FB03=0046 0066 0069;FB04=0046 0066 006C;FB05=0053 0074;FB06=0053 0074;FB13=0544 0576;FB14=0544 0565;FB15=0544 056B;FB16=054E 0576;" +
		"FB17=0544 056D";

	// Uppercase and Lowercase beyond Lu and Ll (Unicode's Other_Uppercase and Other_Lowercase)
	const string OtherUppercase =
		"2160-216F 24B6-24CF 1F130-1F149 1F150-1F169 1F170-1F189";

	const string OtherLowercase =
		"00AA 00BA 02B0-02B8 02C0-02C1 02E0-02E4 0345 037A 10FC 1D2C-1D6A 1D78 1D9B-1DBF 2071 207F 2090-209C 2170-217F 24D0-24E9 2C7C-2C7D A69C-A69D A770 A7F2-A7F4 A7F8-A7F9 AB5C-AB5F AB69 " +
		"10780 10783-10785 10787-107B0 107B2-107BA 1E030-1E06D";

	// Python's isspace(): bidirectional class WS, B or S, or category Zs
	const string Spaces = "0009-000D 001C-0020 0085 00A0 1680 2000-200A 2028 2029 202F 205F 3000";

	// Where splitlines() breaks
	const string LineBreaks = "000A-000D 001C-001E 0085 2028 2029";

	static readonly HashSet<int> TitleSelfSet = ParseRanges(TitleIsSelf);
	static readonly HashSet<int> OtherUpperSet = ParseRanges(OtherUppercase);
	static readonly HashSet<int> OtherLowerSet = ParseRanges(OtherLowercase);
	static readonly HashSet<int> SpaceSet = ParseRanges(Spaces);
	static readonly HashSet<int> LineBreakSet = ParseRanges(LineBreaks);
	static readonly Dictionary<int, string> TitleMap = ParseMap(TitleMapped);

	static HashSet<int> ParseRanges(string ranges)
	{
		var set = new HashSet<int>();

		foreach (string part in ranges.Split(' ', StringSplitOptions.RemoveEmptyEntries))
		{
			string[] ends = part.Split('-');
			int first = int.Parse(ends[0], NumberStyles.HexNumber);
			int last = ends.Length > 1 ? int.Parse(ends[1], NumberStyles.HexNumber) : first;

			for (int cp = first; cp <= last; cp++)
			{
				set.Add(cp);
			}
		}

		return set;
	}

	static Dictionary<int, string> ParseMap(string table)
	{
		var map = new Dictionary<int, string>();

		foreach (string entry in table.Split(';'))
		{
			string[] parts = entry.Split('=');
			map[int.Parse(parts[0], NumberStyles.HexNumber)] = string.Concat(parts[1].Split(' ').Select(hex => char.ConvertFromUtf32(int.Parse(hex, NumberStyles.HexNumber))));
		}

		return map;
	}

	static UnicodeCategory Category(int cp) => CharUnicodeInfo.GetUnicodeCategory(cp);

	public static bool IsSpace(int cp) => SpaceSet.Contains(cp);

	public static bool IsUppercase(int cp) => Category(cp) == UnicodeCategory.UppercaseLetter || OtherUpperSet.Contains(cp);

	public static bool IsLowercase(int cp) => Category(cp) == UnicodeCategory.LowercaseLetter || OtherLowerSet.Contains(cp);

	public static bool IsTitlecase(int cp) => Category(cp) == UnicodeCategory.TitlecaseLetter;

	// Unicode's Cased property: Uppercase, Lowercase or Lt
	public static bool IsCased(int cp) => IsUppercase(cp) || IsLowercase(cp) || IsTitlecase(cp);

	// str.isupper(): at least one cased character, and none lowercase or title case
	public static bool IsUpper(string s)
	{
		bool cased = false;

		foreach (Rune rune in s.EnumerateRunes())
		{

			if (IsLowercase(rune.Value) || IsTitlecase(rune.Value))
			{
				return false;
			}

			if (IsUppercase(rune.Value))
			{
				cased = true;
			}
		}

		return cased;
	}

	// str.islower(): at least one cased character, and none uppercase or title case
	public static bool IsLower(string s)
	{
		bool cased = false;

		foreach (Rune rune in s.EnumerateRunes())
		{

			if (IsUppercase(rune.Value) || IsTitlecase(rune.Value))
			{
				return false;
			}

			if (IsLowercase(rune.Value))
			{
				cased = true;
			}
		}

		return cased;
	}

	public static string Upper(string s) => FullCase.Upper(s);

	public static string Lower(string s) => FullCase.Lower(s);

	// The full title case of one character
	public static string TitleRune(Rune rune)
	{

		if (TitleSelfSet.Contains(rune.Value))
		{
			return rune.ToString();
		}

		return TitleMap.TryGetValue(rune.Value, out string? mapped) ? mapped : FullCase.UpperRune(rune);
	}

	// str.title(): a character after a cased one is lowered, any other is title-cased
	public static string Title(string s)
	{
		Rune[] runes = s.EnumerateRunes().ToArray();
		var sb = new StringBuilder(s.Length);
		bool previousIsCased = false;

		for (int i = 0; i < runes.Length; i++)
		{

			if (previousIsCased)
			{
				FullCase.AppendLower(runes, i, sb);
			}
			else
			{
				sb.Append(TitleRune(runes[i]));
			}

			previousIsCased = IsCased(runes[i].Value);
		}

		return sb.ToString();
	}

	// str.capitalize(): the first character title-cased, the rest lowered
	public static string Capitalize(string s)
	{
		Rune[] runes = s.EnumerateRunes().ToArray();
		var sb = new StringBuilder(s.Length);

		for (int i = 0; i < runes.Length; i++)
		{

			if (i == 0)
			{
				sb.Append(TitleRune(runes[i]));
			}
			else
			{
				FullCase.AppendLower(runes, i, sb);
			}
		}

		return sb.ToString();
	}

	static bool IsSpaceAt(string s, int i) => IsSpace(s[i]);

	// str.strip() with no argument
	public static string Strip(string s) => RStrip(LStrip(s));

	public static string LStrip(string s)
	{
		int start = 0;

		while (start < s.Length && IsSpaceAt(s, start))
		{
			start++;
		}

		return s[start..];
	}

	public static string RStrip(string s)
	{
		int end = s.Length;

		while (end > 0 && IsSpaceAt(s, end - 1))
		{
			end--;
		}

		return s[..end];
	}

	// str.split() with no argument: runs of whitespace separate, and there are no empty pieces
	public static List<string> Split(string s)
	{
		var pieces = new List<string>();
		int i = 0;

		while (i < s.Length)
		{

			while (i < s.Length && IsSpaceAt(s, i))
			{
				i++;
			}

			int start = i;

			while (i < s.Length && !IsSpaceAt(s, i))
			{
				i++;
			}

			if (i > start)
			{
				pieces.Add(s[start..i]);
			}
		}

		return pieces;
	}

	// str.splitlines() without the line ends: \r\n is one break, and a final line end doesn't make an empty last line
	public static List<string> SplitLines(string s)
	{
		var lines = new List<string>();
		int start = 0;
		int i = 0;

		while (i < s.Length)
		{

			if (LineBreakSet.Contains(s[i]))
			{
				lines.Add(s[start..i]);
				i += s[i] == '\r' && i + 1 < s.Length && s[i + 1] == '\n' ? 2 : 1;
				start = i;
			}
			else
			{
				i++;
			}
		}

		if (start < s.Length)
		{
			lines.Add(s[start..]);
		}

		return lines;
	}
}
