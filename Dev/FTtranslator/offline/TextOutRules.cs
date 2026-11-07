// TextOutRules.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/textout.py in C#: applies a bundle's Text Out rules to the synthesized text.
//
// OVERVIEW (AI generated, then edited)
//
// The last step of an offline translation, ported from fttranslator/textout.py (itself a copy of the rule-applying part of TextInOutUtils.py) so the phone gets the same text the desktop's Collect
// Output gives. The rules file (text_out_rules.xml in the bundle) is a list of search and replace rules, applied in document order, each to the result of the one before; inactive ones are skipped
// and aren't counted in the "N Text Out rules applied." message. A failing rule stops them all with the desktop's message naming the rule.
//
// PYTHON'S REGEX MODULE IN .NET
//
// The desktop applies regular expression rules with Python's third-party regex module. On 11/6/26 every one of the 212 distinct rules in the 90 rules files on Ron's machine gave .NET's
// result identical to Python's on 69 real target texts, once the differences below were handled (tests/make_textout_cases.py and ftoffline check-textout). Regex is made with CultureInvariant,
// so case-insensitive parts don't depend on the phone's language. What differs, and how it is handled here:
//  - \w: Python's takes letters, all marks, digits, connector punctuation, letter numbers (Ⅻ), the zero-width joiner and non-joiner and the circled letters; .NET's only letters, nonspacing
//    marks, digits and connectors, so a ZWNJ inside a Persian word, or a Devanagari vowel sign (a spacing mark), would end a word. PythonPattern() rewrites \w, \W, \b and \B with Python's set,
//    and \Z (end of text in Python, before a final newline too in .NET) as \z. Inside a character class only \w is widened; a \W there ([^\W\d]) keeps .NET's narrower meaning.
//  - .NET matches by UTF-16 code unit, Python by code point: a character outside the BMP (𝐀, Adlam, Osage) is two units to .NET, so . and \w see half of it. No rule or text in the
//    projects checked has one; a project in such a script would need checking.
//  - Syntax only Python's regex module has fails here as a bad rule would: (?P<name>...), possessive a++, \X, \h, \R, \K, \N{NAME}, [[:alpha:]], \p{Greek}. None of the rules use them.
//  - Case changes in replacements (\u \l \U \L): Python's str.upper()/lower() use Unicode's full mappings (ß becomes SS, ﬁ becomes FI), .NET's ToUpperInvariant() the simple ones; FullCase
//    below adds the full ones and Greek final sigma, so \U on German or Greek text gives what Python gives.
//  - A plain (non-regex) rule with an empty search string: Python's str.replace("", x) puts x between every character and at both ends, .NET's string.Replace throws; ReplaceAll() does what
//    Python does.
//
// SPEED
//
// .NET's usual (backtracking) engine can be far slower than Python's regex module on rules of the form ([^.?;:!]+?)MARKER(...): it starts a match at every position and scans to the next
// punctuation mark each time, where Python's looks for the marker first. On a Toma-Zialo text with no sentence punctuation left, one such rule took a second (0.3 s compiled) against Python's
// millisecond. So each rule uses RegexOptions.NonBacktracking, which has no such worst case and finds the same matches, whenever its pattern allows (no look-arounds, back-references or atomic
// groups, which includes the look-arounds PythonPattern() writes for \b); the rest use the backtracking engine. The Regex is made once per rule and kept.
//
// TRAPS (the same as textout.py's)
//
//  - Before each rule the text and the search string are put in NFD; the replacement is not normalized.
//  - The replacement is read by Replacer, not by Regex.Replace's own syntax ($1), so \1 to \9 and \0 are the backreferences and \u \l \U \L \E change case, as in regex101. Any other backslash
//    is kept as typed, so a replacement "ćh" means "uppercase the next character, then 0107h", exactly as on the desktop.
//  - XML whitespace counts: a rule "  " ⭢ " " searches for two spaces, so the file is read with whitespace preserved.
//
// CODE STRUCTURE
//
// SearchReplaceRule is one rule, read by FromElement(), with ToDisplayString() (buildRuleString) and its Printable() alias table. TextOutRules holds one bundle's parsed file: Load() reads it
// (null when the bundle has none), Apply() runs the rules (applyRulesToString and applySearchReplaceRules) and returns the new text and the desktop's message, with PythonPattern() giving each
// regular expression Python's meaning. ReplaceAll() is Python's str.replace(). Replacer is create_replacer(); FullCase.cs gives it Python's upper() and lower().
//

using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace FTtranslator.Offline;

public sealed class SearchReplaceRule
{
	public string Search { get; init; } = "";
	public string Replace { get; init; } = "";
	public bool IsRegex { get; init; }
	public bool IsInactive { get; init; }
	public string Comment { get; init; } = "";

	Regex? regex;

	// The rule's regular expression, made the first time it is used and kept, since a bundle's rules apply to every text (see SPEED above). The pattern is the NFD search string.
	internal Regex GetRegex(string nfdSearch)
	{

		if (regex == null)
		{
			string pattern = TextOutRules.PythonPattern(nfdSearch);

			// The non-backtracking engine where the pattern allows it; one with look-arounds or back-references throws NotSupportedException and gets the backtracking engine. A bad pattern
			// throws ArgumentException from both, which fails the rule as on the desktop.
			try
			{
				regex = new Regex(pattern, RegexOptions.CultureInvariant | RegexOptions.NonBacktracking);
			}
			catch (NotSupportedException)
			{
				regex = new Regex(pattern, RegexOptions.CultureInvariant);
			}
		}

		return regex;
	}

	// The rule's search and replace strings are its first two child elements, whatever they are called (getRuleFromElement)
	public static SearchReplaceRule FromElement(XElement element)
	{
		var children = element.Elements().ToList();

		return new SearchReplaceRule
		{
			Search = children.Count > 0 ? ElementText(children[0]) : "",
			Replace = children.Count > 1 ? ElementText(children[1]) : "",
			IsRegex = (string?)element.Attribute("RegEx") == "yes",
			IsInactive = (string?)element.Attribute("Inactive") == "yes",
			Comment = (string?)element.Attribute("Comment") ?? "",
		};
	}

	// ElementTree's .text: the text before the first child element
	static string ElementText(XElement element)
	{
		var sb = new StringBuilder();

		foreach (XNode node in element.Nodes())
		{

			if (node is XElement)
			{
				break;
			}

			if (node is XText text)
			{
				sb.Append(text.Value);
			}
		}

		return sb.ToString();
	}

	// The rule as the desktop shows it: search ⭢ replace, then the RegEx, inactive and comment markers (buildRuleString)
	public string ToDisplayString()
	{
		string regExStr = IsRegex ? " (✓ RegEx)" : "";
		string inactiveStr = IsInactive ? "🚫" : "";
		string commentStr = Comment.Length > 0 ? " - " + Comment : "";

		return $"{Printable(Search)} ⭢ {Printable(Replace)}{regExStr}{inactiveStr}{commentStr}";
	}

	// Invisible characters by their bracketed aliases (getPrintableString with TextInOutUtils.py's replacementsMap)
	static string Printable(string s)
	{
		var sb = new StringBuilder();

		foreach (char c in s)
		{
			sb.Append(Aliases.TryGetValue(c, out string? alias) ? alias : c.ToString());
		}

		return sb.ToString();
	}

	static readonly Dictionary<char, string> Aliases = BuildAliases();

	static Dictionary<char, string> BuildAliases()
	{
		string[] control = { "NUL", "SOH", "STX", "ETX", "EOT", "ENQ", "ACK", "BEL", "BS", "TAB", "NL", "VT", "FF", "CR", "SO", "SI", "DLE", "DC1", "DC2", "DC3", "DC4", "NAK", "SYN", "ETB",
			"CAN", "EOM", "SUB", "ESC", "FS", "GS", "RS", "US" };
		string[] c1 = { "PAD", "HOP", "BPH", "NBH", "IND", "NEL", "SSA", "ESA", "HTS", "HTJ", "VTS", "PLD", "PLU", "RI", "SS2", "SS3", "DCS", "PU1", "PU2", "STS", "CCH", "MW", "SPA", "EPA",
			"SOS" };
		var map = new Dictionary<char, string>();

		for (int i = 0; i < control.Length; i++)
		{
			map[(char)i] = $"[{control[i]}]";
		}

		for (int i = 0; i < c1.Length; i++)
		{
			map[(char)(0x80 + i)] = $"[{c1[i]}]";
		}

		map[' '] = "[SP]";
		map['\u007F'] = "[DEL]";
		map['\u200B'] = "[ZWSP]";
		map['\u200C'] = "[ZWNJ]";
		map['\u200D'] = "[ZWJ]";
		map['\u200E'] = "[LRM]";
		map['\u200F'] = "[RLM]";
		map['\u202A'] = "[LRE]";
		map['\u202B'] = "[RLE]";
		map['\u202C'] = "[PDF]";
		map['\u202D'] = "[LRO]";
		map['\u202E'] = "[RLO]";
		map['\u202F'] = "[NNBSP]";
		map['\u205F'] = "[MMSP]";
		map['\u2060'] = "[WJ]";
		map['\u2066'] = "[LRI]";
		map['\u2067'] = "[RLI]";
		map['\u2068'] = "[FSI]";
		map['\u2069'] = "[PDI]";

		return map;
	}
}

public sealed class TextOutRules
{
	// The rules file's name in the bundle, as bundle.py writes it
	public const string RulesFile = "text_out_rules.xml";

	const string ModuleName = "Text Out";

	public IReadOnlyList<SearchReplaceRule> Rules { get; }

	public TextOutRules(IReadOnlyList<SearchReplaceRule> rules)
	{
		Rules = rules;
	}

	public static TextOutRules Parse(string xml)
	{
		XDocument doc = XDocument.Parse(xml, LoadOptions.PreserveWhitespace);
		XElement? rulesElement = doc.Root?.Element("SearchReplaceRules");

		// The desktop would fail on a file with no rules element; here, as in textout.py, it simply has no rules
		var rules = rulesElement == null ? new List<SearchReplaceRule>() : rulesElement.Elements().Select(SearchReplaceRule.FromElement).ToList();

		return new TextOutRules(rules);
	}

	// The bundle's rules, or null when it has none (a bundle made before rules were exported has no textOutRules entry in its manifest)
	public static TextOutRules? Load(string bundleDir, JsonElement manifest)
	{

		if (!manifest.TryGetProperty("files", out JsonElement files) || !files.TryGetProperty("textOutRules", out JsonElement name) || name.GetString() is not string fileName || fileName.Length == 0)
		{
			return null;
		}

		string path = Path.Combine(bundleDir, fileName);

		if (!File.Exists(path))
		{
			return null;
		}

		return Parse(File.ReadAllText(path));
	}

	public int ActiveCount => Rules.Count(r => !r.IsInactive);

	// Apply the rules. Returns the new text and the desktop's message; on a failure the text is null and the message is the error naming the rule.
	public (string? Text, string Message, bool Ok) Apply(string text)
	{
		string newStr = text;

		for (int i = 0; i < Rules.Count; i++)
		{
			SearchReplaceRule rule = Rules[i];

			if (rule.IsInactive)
			{
				continue;
			}

			// FLEx stores text decomposed, but the user may not have typed the rule decomposed
			newStr = newStr.Normalize(NormalizationForm.FormD);
			string search = rule.Search.Normalize(NormalizationForm.FormD);

			// The desktop catches everything here; a bad regular expression is the usual cause
			try
			{

				if (rule.IsRegex)
				{
					var replacer = new Replacer(rule.Replace);
					newStr = rule.GetRegex(search).Replace(newStr, replacer.Evaluate);
				}
				else
				{
					newStr = ReplaceAll(newStr, search, rule.Replace);
				}
			}
			catch (Exception)
			{
				return (null, $"Applying Text In/Out rules stopped because of a failure of rule {i + 1}: {rule.ToDisplayString()}", false);
			}
		}

		return (newStr, $"{ActiveCount} {ModuleName} rules applied.", true);
	}

	// Python's regex module's word characters (see PYTHON'S REGEX MODULE IN .NET above): letters, all marks, decimal digits, connector punctuation, letter numbers, the joiners, and the circled
	// letters (Other_Alphabetic symbols) of the BMP
	const string WordClassBody = @"\p{L}\p{M}\p{Nd}\p{Pc}\p{Nl}\u200C\u200D\u24B6-\u24E9";
	const string WordClass = "[" + WordClassBody + "]";
	const string NotWordClass = "[^" + WordClassBody + "]";
	const string WordBoundary = "(?:(?<=" + WordClass + ")(?!" + WordClass + ")|(?<!" + WordClass + ")(?=" + WordClass + "))";
	const string NotWordBoundary = "(?:(?<=" + WordClass + ")(?=" + WordClass + ")|(?<!" + WordClass + ")(?!" + WordClass + "))";

	// A rule's pattern with Python's meaning for \w, \W, \b, \B and \Z in .NET's syntax. Escapes are kept whole, so \\w is still a backslash and a w; inside a character class only \w can be
	// widened (to the class's members), and \W keeps .NET's meaning there.
	public static string PythonPattern(string pattern)
	{
		var sb = new StringBuilder(pattern.Length);
		bool inClass = false;
		int i = 0;

		while (i < pattern.Length)
		{
			char c = pattern[i];

			if (c == '\\' && i + 1 < pattern.Length)
			{
				char next = pattern[i + 1];
				i += 2;

				if (inClass)
				{
					sb.Append(next == 'w' ? WordClassBody : "\\" + next);
				}
				else
				{
					sb.Append(next switch { 'w' => WordClass, 'W' => NotWordClass, 'b' => WordBoundary, 'B' => NotWordBoundary, 'Z' => @"\z", _ => "\\" + next });
				}

				continue;
			}

			if (!inClass && c == '[')
			{

				// A ] right after [ or [^ is a member, not the end
				inClass = true;
				sb.Append(c);
				i++;

				if (i < pattern.Length && pattern[i] == '^')
				{
					sb.Append('^');
					i++;
				}

				if (i < pattern.Length && pattern[i] == ']')
				{
					sb.Append(']');
					i++;
				}

				continue;
			}

			if (inClass && c == ']')
			{
				inClass = false;
			}

			sb.Append(c);
			i++;
		}

		return sb.ToString();
	}

	// Python's str.replace(): an empty search string puts the replacement between every character and at both ends
	public static string ReplaceAll(string s, string search, string replace)
	{

		if (search.Length > 0)
		{
			return s.Replace(search, replace, StringComparison.Ordinal);
		}

		var sb = new StringBuilder(replace);

		foreach (char c in s)
		{
			sb.Append(c).Append(replace);
		}

		return sb.ToString();
	}
}

// create_replacer(): reads a replacement as regex101 does. \0 to \9 insert a group, \u and \l change the case of the next character inserted, \U and \L that of everything up to \E (a \u or \l
// wins for its one character), and any other backslash sequence is passed through as typed.
public sealed class Replacer
{
	readonly string pattern;

	public Replacer(string pattern)
	{
		this.pattern = pattern;
	}

	public string Evaluate(Match match)
	{
		var result = new StringBuilder();
		string? caseMode = null;
		string? oneShotCase = null;
		int i = 0;

		// Append text with the current case treatment: the pending \u or \l affects the first character and the enclosing \U or \L the rest
		string ApplyCase(string text)
		{

			if (text.Length == 0)
			{
				return "";
			}

			// Python slices by code point, so a surrogate pair is one character
			int firstLength = char.IsHighSurrogate(text[0]) && text.Length > 1 && char.IsLowSurrogate(text[1]) ? 2 : 1;
			string firstChar = text[..firstLength];
			string restChars = text[firstLength..];

			if (oneShotCase == "upper")
			{
				firstChar = FullCase.Upper(firstChar);
				oneShotCase = null;
			}
			else if (oneShotCase == "lower")
			{
				firstChar = FullCase.Lower(firstChar);
				oneShotCase = null;
			}
			else if (caseMode == "upper")
			{
				firstChar = FullCase.Upper(firstChar);
			}
			else if (caseMode == "lower")
			{
				firstChar = FullCase.Lower(firstChar);
			}

			if (caseMode == "upper")
			{
				restChars = FullCase.Upper(restChars);
			}
			else if (caseMode == "lower")
			{
				restChars = FullCase.Lower(restChars);
			}

			return firstChar + restChars;
		}

		while (i < pattern.Length)
		{

			if (pattern[i] == '\\' && i + 1 < pattern.Length)
			{
				char nextChar = pattern[i + 1];

				// Python's str.isdigit() takes any Unicode decimal digit, but int() of one gives its value, so \٣ is group 3 as \3 is
				if (char.IsDigit(nextChar))
				{
					int group = (int)char.GetNumericValue(nextChar);

					// A group the pattern doesn't have makes Python's match.group() raise, which fails the rule
					if (group >= match.Groups.Count)
					{
						throw new ArgumentException($"invalid group reference {group}");
					}

					result.Append(ApplyCase(match.Groups[group].Success ? match.Groups[group].Value : ""));
					i += 2;
				}
				else if (nextChar == 'u' || nextChar == 'l')
				{
					oneShotCase = nextChar == 'u' ? "upper" : "lower";
					i += 2;
				}
				else if (nextChar == 'U' || nextChar == 'L')
				{
					caseMode = nextChar == 'U' ? "upper" : "lower";
					i += 2;
				}
				else if (nextChar == 'E')
				{
					caseMode = null;
					i += 2;
				}
				else
				{
					// The backslash goes in raw, so a pending \u or \l isn't used up on it
					result.Append(pattern[i]);
					i++;
				}
			}
			else
			{
				result.Append(ApplyCase(pattern[i].ToString()));
				i++;
			}
		}

		return result.ToString();
	}
}
