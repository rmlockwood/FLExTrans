// TransferRules.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. A .t1x, .t2x or .t3x read for apertium-transfer, -interchunk or -postchunk, without apertium-preprocess-transfer.
//
// OVERVIEW (AI generated, then edited)
//
// FLExTrans' transfer rules without Apertium: a .t1x (apertium-transfer -b), .t2x (apertium-interchunk) or .t3x (apertium-postchunk) read directly, with no apertium-preprocess-transfer and
// no .bin, ready for TransferRun to run a stream through. Ported from Apertium main after 2025-07 (the build FLExTrans ships; its -t trace has the "Matched rule / Applied rule" lines added
// then): transfer.cc, interchunk.cc, postchunk.cc, transfer_base.cc, transfer_word.cc, interchunk_word.cc, trx_reader.cc and transfer_regex.cc. Checked byte for byte, output and trace,
// against the Windows tools; see README.md.
//
// THE PATTERN MATCHER
//
// trx_reader.cc compiles every rule's pattern into one automaton: for each pattern item '^', the category's cat-items, '$', with an optional ' ' between items; the state after the last item
// is final for that rule. A cat-item is its lemma's characters (lowercase as written; '*' or an empty lemma = one or more of any character) followed by its tags ('*' = one or more of any tag).
// lttoolbox determinizes and minimizes it; here it stays nondeterministic and is run as a set of states, which reaches the same finals. A word is fed in as Transfer::applyWord does: '^', its
// source side's characters lowercased (each also as any_char), its tags (each also as any_tag; a tag no cat-item names only as any_tag), '$'. Each blank is fed in as ' '.
//
// THE MAIN LOOP (Transfer::transfer)
//
// Tokens (blanks and words) go into a buffer. After each token the lowest-numbered rule whose pattern is complete is remembered with the buffer position. When the matcher dies, the remembered
// rule runs on the words read so far and reading restarts just after its last word; with no rule, the first word's target side is written as it is and reading restarts after it. The quirks are
// kept (for example, the rule sees every word read, not only the matched ones), since the point is byte-identical output.
//
// THE INTERPRETER
//
// Expressions are compiled once per XML element (evalStringCache in Apertium) and actions are walked as XML, as Apertium walks libxml2's tree. Variables keep their values from one rule to the
// next for the whole stream. A macro call swaps in its parameter words.
//
// CODE STRUCTURE
//
// MatchNode is a pattern automaton state. TransferRules.Load() reads the sections and builds the automaton (InsertCatItem(), SplitEscaped()); OptimizeRegex() with
// AddChar() and Unbuild() turns each def-attr into its regular expression; Line() gives libxml2's line numbers. TransferRun runs the result.
//

using System.Text;
using System.Text.RegularExpressions;
using System.Xml;
using System.Xml.Linq;

namespace FTtranslator.Apertium;

public class TransferException : Exception
{
	public TransferException(string message) : base(message) { }
}

class MatchNode
{
	public readonly Dictionary<int, List<MatchNode>> Transitions = new();
	public int Rule;

	public MatchNode Add(int symbol, MatchNode? to = null)
	{
		to ??= new MatchNode();

		if (!Transitions.TryGetValue(symbol, out List<MatchNode>? list))
		{
			list = new List<MatchNode>();
			Transitions[symbol] = list;
		}

		list.Add(to);

		return to;
	}
}

public class TransferRules
{
	public const int AnyChar = -1;
	public const int AnyTag = -2;

	internal readonly MatchNode Initial = new();
	internal readonly Dictionary<string, int> TagSymbols = new();
	internal readonly Dictionary<string, Regex?> AttrItems = new();
	internal readonly Dictionary<string, string> VariableDefaults = new();
	internal readonly Dictionary<string, HashSet<string>> Lists = new();
	internal readonly Dictionary<string, HashSet<string>> ListsLow = new();
	internal readonly Dictionary<string, XElement> Macros = new();
	internal readonly List<XElement?> RuleActions = new();
	internal readonly List<int> RuleLines = new();
	internal bool DefaultChunk;

	// transfer (.t1x), interchunk (.t2x) or postchunk (.t3x): the root element's name
	public string Mode = "transfer";

	// The built-in parts (TransferData's constructor), in ICU syntax, which .NET reads the same way for these
	static readonly Dictionary<string, string> BuiltinAttrs = new()
	{
		["lem"] = "^(([^<]|\"\\<\")+)",
		["lemq"] = "\\#[- _][^<]+",
		["lemh"] = "^(([^<#]|\"\\<\"|\"\\#\")+)",
		["whole"] = "(.+)",
		["tags"] = "((<[^>]+>)+)",
		["chname"] = "(\\{([^/]+)\\/)",
		["chcontent"] = "(\\{.+)",
		["content"] = "(\\{.+)",
	};

	// ApertiumRE::compile: UREGEX_DOTALL | UREGEX_CASE_INSENSITIVE
	static Regex Compile(string pattern) => new(pattern, RegexOptions.Singleline | RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

	int TagSymbol(string tag)
	{

		if (!TagSymbols.TryGetValue(tag, out int id))
		{
			id = -3 - TagSymbols.Count;
			TagSymbols[tag] = id;
		}

		return id;
	}

	string[] sourceLines = Array.Empty<string>();

	// libxml2's node->line, which Apertium reports: the line where the start tag ENDS (its '>'), not where it begins, as .NET reports it. They differ for a start tag split over lines.
	internal int Line(XElement e)
	{
		var info = (IXmlLineInfo)e;
		int line = info.LineNumber;
		int col = info.LinePosition - 1;
		char quote = '\0';

		while (line - 1 < sourceLines.Length)
		{
			string text = sourceLines[line - 1];

			for (; col < text.Length; col++)
			{
				char c = text[col];

				if (quote != '\0')
				{

					if (c == quote)
						quote = '\0';
				}
				else if (c == '"' || c == '\'')
				{
					quote = c;
				}
				else if (c == '>')
				{
					return line;
				}
			}

			line++;
			col = 0;
		}

		return info.LineNumber;
	}

	public static TransferRules Load(string path)
	{
		var rules = new TransferRules();
		rules.sourceLines = File.ReadAllText(path).Split('\n');
		XElement root = XDocument.Load(path, LoadOptions.SetLineInfo).Root!;
		rules.DefaultChunk = (string?)root.Attribute("default") == "chunk";
		rules.Mode = root.Name.LocalName;

		if (rules.Mode is not ("transfer" or "interchunk" or "postchunk"))
			throw new TransferException($"Unexpected root element <{rules.Mode}>");

		foreach ((string name, string re) in BuiltinAttrs)
			rules.AttrItems[name] = Compile(re);

		var cats = new Dictionary<string, List<(string Lemma, string Tags)>>();

		foreach (XElement defCat in root.Element("section-def-cats")?.Elements("def-cat") ?? Enumerable.Empty<XElement>())
		{
			var items = new List<(string, string)>();

			foreach (XElement item in defCat.Elements("cat-item"))
			{
				string tags = (string?)item.Attribute("tags") ?? "";

				if (tags.Length > 0)
					items.Add(((string?)item.Attribute("lemma") ?? "", tags));
				else
					items.Add(((string?)item.Attribute("name") ?? "", ""));
			}

			cats[(string)defCat.Attribute("n")!] = items;
		}

		foreach (XElement defAttr in root.Element("section-def-attrs")?.Elements("def-attr") ?? Enumerable.Empty<XElement>())
			rules.AttrItems[(string)defAttr.Attribute("n")!] = Compile(OptimizeRegex(defAttr.Elements("attr-item").Select(a => (string?)a.Attribute("tags") ?? "").ToList()));

		foreach (XElement defVar in root.Element("section-def-vars")?.Elements("def-var") ?? Enumerable.Empty<XElement>())
			rules.VariableDefaults[(string)defVar.Attribute("n")!] = (string?)defVar.Attribute("v") ?? "";

		foreach (XElement defList in root.Element("section-def-lists")?.Elements("def-list") ?? Enumerable.Empty<XElement>())
		{
			string n = (string)defList.Attribute("n")!;
			var set = rules.Lists.TryGetValue(n, out var s) ? s : rules.Lists[n] = new HashSet<string>(StringComparer.Ordinal);
			var low = rules.ListsLow.TryGetValue(n, out var l) ? l : rules.ListsLow[n] = new HashSet<string>(StringComparer.Ordinal);

			foreach (XElement item in defList.Elements("list-item"))
			{
				string v = (string?)item.Attribute("v") ?? "";
				set.Add(v);
				low.Add(CaseUtils.ToLower(v));
			}
		}

		foreach (XElement macro in root.Element("section-def-macros")?.Elements() ?? Enumerable.Empty<XElement>())
			rules.Macros[(string)macro.Attribute("n")!] = macro;

		// TRXReader::procRules: patterns share states for shared prefixes of pattern-item names; a repeated pattern is skipped (with a warning, as there)
		var states = new Dictionary<(MatchNode, string), MatchNode>();
		var seen = new HashSet<MatchNode>();
		int count = 0;

		foreach (XElement rule in root.Element("section-rules")?.Elements("rule") ?? Enumerable.Empty<XElement>())
		{
			count++;
			rules.RuleActions.Add(rule.Element("action"));
			rules.RuleLines.Add(rules.Line(rule));
			MatchNode state = rules.Initial;

			foreach (XElement item in rule.Element("pattern")?.Elements("pattern-item") ?? Enumerable.Empty<XElement>())
			{
				string catName = (string)item.Attribute("n")!;

				if (states.TryGetValue((state, catName), out MatchNode? next))
				{
					state = next;
					continue;
				}

				if (!cats.TryGetValue(catName, out var catItems))
					throw new TransferException($"Undefined cat-item '{catName}'");

				MatchNode wordStart = state.Add('^');

				if (state != rules.Initial)
					state.Add(' ').Add('^', wordStart);

				MatchNode wordEnd = new();

				foreach ((string lemma, string tags) in catItems)
					rules.InsertCatItem(wordStart, lemma, tags).Add('$', wordEnd);

				states[(state, catName)] = wordEnd;
				state = wordEnd;
			}

			if (seen.Add(state))
				state.Rule = count;
		}

		return rules;
	}

	// TRXReader::insertCatItem
	MatchNode InsertCatItem(MatchNode from, string lemma, string tags)
	{
		MatchNode state = from;

		if (lemma.Length == 0)
		{
			state = state.Add(AnyChar);
			state.Add(AnyChar, state);
		}
		else
		{

			for (int i = 0; i < lemma.Length; i++)
			{

				if (lemma[i] == '\\')
				{
					state = state.Add('\\');
					i++;
					state = state.Add(lemma[i]);
				}
				else if (lemma[i] == '*')
				{
					state = state.Add(AnyChar);
					state.Add(AnyChar, state);
				}
				else
				{
					state = state.Add(lemma[i]);
				}
			}
		}

		foreach (string tag in SplitEscaped(tags, '.'))
		{

			if (tag == "*")
			{
				state = state.Add(AnyTag);
				state.Add(AnyTag, state);
			}
			else
			{
				state = state.Add(TagSymbol($"<{tag}>"));
			}
		}

		return state;
	}

	internal static List<string> SplitEscaped(string str, char delim)
	{
		var result = new List<string>();
		int start = 0;

		for (int i = 0; i < str.Length; i++)
		{

			if (str[i] == '\\')
			{
				i++;
				continue;
			}

			if (str[i] == delim)
			{

				if (i > start)
					result.Add(str.Substring(start, i - start));

				start = i + 1;
			}
		}

		if (start < str.Length)
			result.Add(str.Substring(start));

		return result;
	}

	// transfer_regex.cc: the attr-items as one regular expression, built from a trie of their characters with '.' as "><"
	class TrieNode
	{
		public char C;
		public bool End;
		public readonly List<TrieNode> Next = new();
	}

	static TrieNode AddChar(TrieNode root, char c)
	{

		foreach (TrieNode node in root.Next)
		{

			if (node.C == c)
				return node;
		}

		var t = new TrieNode { C = c };
		root.Next.Add(t);

		return t;
	}

	static string Unbuild(TrieNode root)
	{
		var single = new StringBuilder("[");
		var groups = new List<string>();
		int singleCount = 0;

		foreach (TrieNode it in root.Next)
		{

			if (it.End && it.Next.Count == 0)
			{

				if (it.C is '+' or '*' or '?' or '.')
					single.Append('\\');

				single.Append(it.C);
				singleCount++;
			}
			else
			{
				groups.Add(Unbuild(it));
			}
		}

		if (singleCount > 0)
		{

			if (singleCount == 1)
				groups.Add(single.ToString(1, single.Length - 1));
			else
				groups.Add(single.Append(']').ToString());
		}

		var ret = new StringBuilder();

		if (root.C is '+' or '*' or '?' or '.')
			ret.Append('\\');

		ret.Append(root.C);

		if (groups.Count == 1)
		{

			if (root.End && groups[0].Length > 1 && groups[0][0] != '(')
				ret.Append("(?:").Append(groups[0]).Append(')');
			else
				ret.Append(groups[0]);
		}
		else if (groups.Count > 1)
		{
			ret.Append("(?:").Append(string.Join("|", groups)).Append(')');
		}

		if (root.End && groups.Count > 0)
			ret.Append('?');

		return ret.ToString();
	}

	static string OptimizeRegex(List<string> options)
	{
		var root = new TrieNode { C = '<' };

		foreach (string s in options)
		{
			TrieNode cur = root;
			bool escape = false;

			foreach (char c in s)
			{

				if (!escape)
				{

					if (c == '\\')
					{
						escape = true;
						continue;
					}

					if (c == '.')
					{
						cur = AddChar(cur, '>');
						cur = AddChar(cur, '<');
						continue;
					}
				}

				escape = false;
				cur = AddChar(cur, c);
			}

			cur.End = true;
		}

		return "(" + Unbuild(root) + ">)";
	}
}
