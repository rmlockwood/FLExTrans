// FullCase.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. Python's str.upper() and str.lower() in C#, for the Text Out rules' \u \l \U \L.
//
// OVERVIEW (AI generated, then edited)
//
// Python's str.upper() and str.lower() use Unicode's full case mappings; .NET's ToUpperInvariant() and ToLowerInvariant() use the simple ones. On 11/6/26 (Python 3.13, Unicode 15.1, against
// .NET 8) the two differed in 103 characters for upper and one for lower, plus Greek final sigma, and nowhere else; this file adds exactly those, so a Text Out replacement with \U gives the
// desktop's text. The differences are SpecialCasing.txt's unconditional mappings (ß to SS, the ﬁ ligatures to FI, Armenian ligatures, Greek letters with ypogegrammeni, ŉ, ǰ), dotless ı to I
// and İ to i plus a combining dot, which .NET's invariant casing leaves alone.
//
// FINAL SIGMA
//
// Python lowercases Σ to ς at the end of a word: when a cased letter comes before it and none after it, skipping case-ignorable characters (marks, format characters, modifier letters, and the
// word-internal punctuation ' . : · ’) on both sides. Only the string passed in counts, which is also true of Python, so the Text Out replacer's split of first character and rest behaves the same.
// "Cased" is Python's (PyStr.IsCased()). The case-ignorable test is by category plus the common word-internal punctuation, a little short of Unicode's full Case_Ignorable list.
//
// CODE STRUCTURE
//
// Upper() and Lower() walk the string by Rune, with UpperRune() and AppendLower() doing one character (PyStr.cs uses those two as well); UpperSpecial holds the full upper-case mappings that
// differ, built from UpperTable. IsCased() and IsCaseIgnorable() serve FinalSigma().
//

using System.Globalization;
using System.Text;

namespace FTtranslator.Offline;

public static class FullCase
{
	// code point = the code points of its full upper-case mapping, for every character where Python's upper() differs from .NET's ToUpperInvariant() (see OVERVIEW)
	const string UpperTable =
		"00DF=0053 0053;0131=0049;0149=02BC 004E;01F0=004A 030C;0390=0399 0308 0301;03B0=03A5 0308 0301;0587=0535 0552;1E96=0048 0331;1E97=0054 0308;1E98=0057 030A;1E99=0059 030A;" +
		"1E9A=0041 02BE;1F50=03A5 0313;1F52=03A5 0313 0300;1F54=03A5 0313 0301;1F56=03A5 0313 0342;1F80=1F08 0399;1F81=1F09 0399;1F82=1F0A 0399;1F83=1F0B 0399;1F84=1F0C 0399;" +
		"1F85=1F0D 0399;1F86=1F0E 0399;1F87=1F0F 0399;1F88=1F08 0399;1F89=1F09 0399;1F8A=1F0A 0399;1F8B=1F0B 0399;1F8C=1F0C 0399;1F8D=1F0D 0399;1F8E=1F0E 0399;1F8F=1F0F 0399;" +
		"1F90=1F28 0399;1F91=1F29 0399;1F92=1F2A 0399;1F93=1F2B 0399;1F94=1F2C 0399;1F95=1F2D 0399;1F96=1F2E 0399;1F97=1F2F 0399;1F98=1F28 0399;1F99=1F29 0399;1F9A=1F2A 0399;" +
		"1F9B=1F2B 0399;1F9C=1F2C 0399;1F9D=1F2D 0399;1F9E=1F2E 0399;1F9F=1F2F 0399;1FA0=1F68 0399;1FA1=1F69 0399;1FA2=1F6A 0399;1FA3=1F6B 0399;1FA4=1F6C 0399;1FA5=1F6D 0399;" +
		"1FA6=1F6E 0399;1FA7=1F6F 0399;1FA8=1F68 0399;1FA9=1F69 0399;1FAA=1F6A 0399;1FAB=1F6B 0399;1FAC=1F6C 0399;1FAD=1F6D 0399;1FAE=1F6E 0399;1FAF=1F6F 0399;1FB2=1FBA 0399;" +
		"1FB3=0391 0399;1FB4=0386 0399;1FB6=0391 0342;1FB7=0391 0342 0399;1FBC=0391 0399;1FC2=1FCA 0399;1FC3=0397 0399;1FC4=0389 0399;1FC6=0397 0342;1FC7=0397 0342 0399;" +
		"1FCC=0397 0399;1FD2=0399 0308 0300;1FD3=0399 0308 0301;1FD6=0399 0342;1FD7=0399 0308 0342;1FE2=03A5 0308 0300;1FE3=03A5 0308 0301;1FE4=03A1 0313;1FE6=03A5 0342;" +
		"1FE7=03A5 0308 0342;1FF2=1FFA 0399;1FF3=03A9 0399;1FF4=038F 0399;1FF6=03A9 0342;1FF7=03A9 0342 0399;1FFC=03A9 0399;FB00=0046 0046;FB01=0046 0049;FB02=0046 004C;" +
		"FB03=0046 0046 0049;FB04=0046 0046 004C;FB05=0053 0054;FB06=0053 0054;FB13=0544 0546;FB14=0544 0535;FB15=0544 053B;FB16=054E 0546;FB17=0544 053D";

	static readonly Dictionary<int, string> UpperSpecial = BuildUpperSpecial();

	static Dictionary<int, string> BuildUpperSpecial()
	{
		var map = new Dictionary<int, string>();

		foreach (string entry in UpperTable.Split(';'))
		{
			string[] parts = entry.Split('=');
			string mapped = string.Concat(parts[1].Split(' ').Select(hex => char.ConvertFromUtf32(int.Parse(hex, NumberStyles.HexNumber))));
			map[int.Parse(parts[0], NumberStyles.HexNumber)] = mapped;
		}

		return map;
	}

	const int CapitalSigma = 0x03A3;

	public static string Upper(string s)
	{
		var sb = new StringBuilder(s.Length);

		foreach (Rune rune in s.EnumerateRunes())
		{
			sb.Append(UpperRune(rune));
		}

		return sb.ToString();
	}

	public static string Lower(string s)
	{
		var sb = new StringBuilder(s.Length);
		Rune[] runes = s.EnumerateRunes().ToArray();

		for (int i = 0; i < runes.Length; i++)
		{
			AppendLower(runes, i, sb);
		}

		return sb.ToString();
	}

	// The lower case of runes[i], in the context of the whole string (Python's lower_ucs4(), which PyStr's Title() and Capitalize() use too)
	internal static void AppendLower(Rune[] runes, int i, StringBuilder sb)
	{
		int cp = runes[i].Value;

		// İ: i plus a combining dot above
		if (cp == 0x0130)
		{
			sb.Append("i̇");
		}
		else if (cp == CapitalSigma)
		{
			sb.Append(FinalSigma(runes, i) ? 'ς' : 'σ');
		}
		else
		{
			sb.Append(Rune.ToLowerInvariant(runes[i]).ToString());
		}
	}

	// The full upper case of one rune
	internal static string UpperRune(Rune rune)
	{
		return UpperSpecial.TryGetValue(rune.Value, out string? mapped) ? mapped : Rune.ToUpperInvariant(rune).ToString();
	}

	// Unicode's Final_Sigma condition, as Python's lower() tests it (see FINAL SIGMA above)
	static bool FinalSigma(Rune[] runes, int index)
	{
		int j = index - 1;

		while (j >= 0 && IsCaseIgnorable(runes[j]))
		{
			j--;
		}

		if (j < 0 || !IsCased(runes[j]))
		{
			return false;
		}

		j = index + 1;

		while (j < runes.Length && IsCaseIgnorable(runes[j]))
		{
			j++;
		}

		return j == runes.Length || !IsCased(runes[j]);
	}

	static bool IsCased(Rune rune) => PyStr.IsCased(rune.Value);

	static bool IsCaseIgnorable(Rune rune)
	{
		UnicodeCategory cat = Rune.GetUnicodeCategory(rune);

		if (cat == UnicodeCategory.NonSpacingMark || cat == UnicodeCategory.EnclosingMark || cat == UnicodeCategory.Format || cat == UnicodeCategory.ModifierLetter || cat == UnicodeCategory.ModifierSymbol)
		{
			return true;
		}

		int cp = rune.Value;

		return cp == '\'' || cp == '.' || cp == ':' || cp == '·' || cp == '’' || cp == 0x00AD;
	}
}
