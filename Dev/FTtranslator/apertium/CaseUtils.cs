// CaseUtils.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. lttoolbox's case functions as Apertium's transfer tools use them.
//
// OVERVIEW (AI generated, then edited)
//
// lttoolbox's StringUtils case functions as apertium-transfer uses them: tolower/toupper (ICU full mappings; .NET's invariant ones are simple mappings, the same for everything but a few
// characters like ß), totitle (ICU's u_strToTitle with the default word breaks: each word's first cased letter up, the rest down), getcase and copycase. getcase/copycase decide "all caps"
// from the first and the LAST character, not the second.
//
// CODE STRUCTURE
//
// ToLower(), ToUpper(), ToTitle() (with IsWordChar() and IsMidWord() for word breaks), GetCase() and CopyCase().
//

using System.Globalization;
using System.Text;

namespace FTtranslator.Apertium;

public static class CaseUtils
{
	public static string ToLower(string s) => s.ToLowerInvariant();

	public static string ToUpper(string s) => s.ToUpperInvariant();

	static bool IsUpper(string s, int index) => Rune.TryGetRuneAt(s, index, out Rune r) && Rune.IsUpper(r);

	static int LastRuneIndex(string s) => s.Length >= 2 && char.IsLowSurrogate(s[^1]) ? s.Length - 2 : s.Length - 1;

	// UAX #29 word characters, simplified: letters, digits and marks, plus ' ’ . : · between two of them
	static bool IsWordChar(char c)
	{
		UnicodeCategory cat = char.GetUnicodeCategory(c);

		return char.IsLetterOrDigit(c) || cat == UnicodeCategory.NonSpacingMark || cat == UnicodeCategory.SpacingCombiningMark || cat == UnicodeCategory.ConnectorPunctuation && c == '_';
	}

	static bool IsMidWord(char c) => c == '\'' || c == '’' || c == '.' || c == ':' || c == '·';

	public static string ToTitle(string s)
	{
		var sb = new StringBuilder(s.Length);
		int i = 0;

		while (i < s.Length)
		{

			if (!IsWordChar(s[i]))
			{
				sb.Append(s[i]);
				i++;
				continue;
			}

			// A word: up to the first character that isn't a word character or a mid-word one between word characters
			int start = i;

			while (i < s.Length && (IsWordChar(s[i]) || IsMidWord(s[i]) && i + 1 < s.Length && IsWordChar(s[i + 1]) && i > start))
				i++;

			string word = s.Substring(start, i - start);
			int firstCased = -1;

			for (int k = 0; k < word.Length; k++)
			{

				if (char.IsUpper(word[k]) || char.IsLower(word[k]) || char.GetUnicodeCategory(word[k]) == UnicodeCategory.TitlecaseLetter)
				{
					firstCased = k;
					break;
				}
			}

			if (firstCased < 0)
			{
				sb.Append(word);
			}
			else
			{
				sb.Append(word, 0, firstCased);
				sb.Append(char.ToUpperInvariant(word[firstCased]));
				sb.Append(word.Substring(firstCased + 1).ToLowerInvariant());
			}
		}

		return sb.ToString();
	}

	public static string GetCase(string s)
	{

		if (s.Length == 0)
			return "aa";

		if (!IsUpper(s, 0))
			return "aa";

		int last = LastRuneIndex(s);

		if (last > 0 && IsUpper(s, last))
			return "AA";

		return "Aa";
	}

	public static string CopyCase(string source, string target)
	{

		if (source.Length == 0 || target.Length == 0)
			return target;

		bool firstUpper = IsUpper(source, 0);
		int last = LastRuneIndex(source);
		bool uppercase = firstUpper && last > 0 && IsUpper(source, last);

		if (firstUpper)
			return uppercase ? ToUpper(target) : ToTitle(target);

		return ToLower(target);
	}
}
