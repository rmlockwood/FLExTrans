// TransferRun.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. The run-time of apertium-transfer -b, apertium-interchunk and apertium-postchunk.
//
// OVERVIEW (AI generated, then edited)
//
// One run of a stream through a rules file (see TransferRules.cs for the overview): apertium-transfer -b (.t1x), apertium-interchunk (.t2x) or apertium-postchunk (.t3x). The three tools share
// one main loop and most of the interpreter (transfer_base.cc); where they differ, the code below says which tool does what. Writes the result to Output and the -t trace to Trace. An error
// Apertium exits on ("unexpected expression" and the like) throws TransferException; Output then holds what was written up to that point.
//
// THE THREE MODES
//
//  - transfer: words are ^source/target$ units. A clip reads the source, target or reference side through the part's regular expression. Pattern positions count from 1, stored as pos-1.
//  - interchunk: words are chunks, ^name<tags>{...}$. Matching sees the name and tags; a clip reads the chunk through chunkPart(), which looks at the header first and the {...} body second.
//  - postchunk: matching sees the chunk's name only. A matched chunk is split into its words: word 0 is the chunk header, words 1..n the words inside, so clip positions are used as written
//    (pos="1" is the first word inside). A tag like <2> inside the chunk is replaced by the chunk's 2nd tag, and an uppercase chunk name uppercases its first word.
//
// TRAPS (kept on purpose, since the point is byte-identical output)
//
//  - postchunk's split appends the chunk's blanks to the blanks already read, and text before the chunk's first word is appended to the blank read after the chunk, which is a token in the
//    input buffer, so it changes when that token is read again. Tokens are therefore objects whose Content can change.
//  - transfer's main loop hands a rule every word read so far, not just the matched ones.
//
// CODE STRUCTURE
//
// RuleWord (a word as rules see it), Token, Instr (a compiled expression). TransferRun: the matcher (Init(), Step(), ClassifyFinals(), ApplyWord()), ReadToken(), Run()
// (the main loop) with WriteUnmatched() and ApplyRule()/ApplyPostchunkRule(), postchunk's chunk helpers (GetVecTags() .. SplitWordsAndBlanks()), then the interpreter:
// ProcessRule() > ProcessInstruction() > ProcessChoose()/ProcessLet()/ProcessOut()/ProcessCallMacro()..., ProcessLogical() for tests, EvalString()/EvalCached() for values.
//

using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace FTtranslator.Apertium;

// A word as the rules see it: transfer uses S/T/R; interchunk and postchunk use Chunk/Queue (InterchunkWord)
class RuleWord
{
	public string S = "", T = "", R = "";
	public string Chunk = "", Queue = "";

	public static RuleWord ForTransfer(string s, string t, string r) => new() { S = s, T = t, R = r };

	// InterchunkWord::init: split at the first unescaped '{'
	public static RuleWord ForChunk(string chunk)
	{

		for (int i = 0; i < chunk.Length; i++)
		{

			if (chunk[i] == '\\')
			{
				i++;
			}
			else if (chunk[i] == '{')
			{
				return new RuleWord { Chunk = chunk.Substring(0, i), Queue = chunk.Substring(i) };
			}
			else if (chunk[i] == ']' && i > 0 && chunk[i - 1] == ']')
			{
				throw new TransferException("[[word-bound blanks]] aren't supported by FTApertium (no FLExTrans rules file uses it)");
			}
		}

		return new RuleWord { Chunk = chunk };
	}

	// ApertiumRE::match: the first match anywhere, or ""
	public static string Match(Regex? re, string s)
	{

		if (re == null)
			return "";

		Match m = re.Match(s);

		return m.Success ? m.Value : "";
	}

	// ApertiumRE::replace: replace the first match; false when nothing matched
	public static bool Replace(Regex? re, ref string s, string value)
	{

		if (re == null)
			return false;

		Match m = re.Match(s);

		if (!m.Success)
			return false;

		s = s.Substring(0, m.Index) + value + s.Substring(m.Index + m.Length);

		return true;
	}

	// InterchunkWord::chunkPart: the header first; failing that, the body only if the part matches all of it; a match of the whole header is retried on header+body
	public string ChunkPart(Regex? re)
	{
		string result = Match(re, Chunk);

		if (result.Length == 0)
		{
			result = Match(re, Queue);

			return result.Length != Queue.Length ? "" : result;
		}

		if (result.Length == Chunk.Length)
			return Match(re, Chunk + Queue);

		return result;
	}

	public bool SetChunkPart(Regex? re, string value) => Replace(re, ref Chunk, value);
}

enum TokenType { Word, Blank, Eof }

class Token
{
	public string Content;
	public readonly TokenType Type;

	public Token(string content, TokenType type)
	{
		Content = content;
		Type = type;
	}
}

// What evalStringCache holds for an element
enum InstrType { ClipSl, ClipTl, ClipRef, LinkToSl, LinkToTl, LinkToRef, Var, Lit, B, GetCaseFrom, CaseOfSl, CaseOfTl, CaseOfRef, LuCount }

record Instr(InstrType Type, string Content, int Pos, XElement? Pointer = null, string StrVal = "");

public class TransferRun
{
	readonly TransferRules rules;
	readonly bool isTransfer, isInterchunk, isPostchunk;
	readonly string tool;
	readonly int[] input;
	int inPos;
	bool inWord;

	public readonly StringBuilder Output = new();
	public readonly StringBuilder Trace = new();

	readonly List<Token> buffer = new();
	int bufPos;

	List<string> tmpWord = new();
	readonly List<Token> tmpBlank = new();
	HashSet<MatchNode> ms = new();
	XElement? lastRule;
	int lastLWord;

	RuleWord?[]? word;
	int lword;
	readonly Queue<string> blankQueue = new();
	readonly Dictionary<string, string> variables;
	readonly Dictionary<XElement, Instr> cache = new();
	bool inOut;

	// Which elements (and caseless forms, multi-word matches and so on) actually ran, across all runs: so a 100% match can be read against what it covered
	public static readonly Dictionary<string, int> Coverage = new();

	// Off for normal use; the reference check (ReferenceCheck.cs) turns it on
	public static bool CollectCoverage;

	void Cover(string what)
	{
		what = rules.Mode + ": " + what;
		Coverage[what] = Coverage.TryGetValue(what, out int n) ? n + 1 : 1;
	}

	public TransferRun(TransferRules rules, string stream)
	{
		this.rules = rules;
		isTransfer = rules.Mode == "transfer";
		isInterchunk = rules.Mode == "interchunk";
		isPostchunk = rules.Mode == "postchunk";
		tool = "apertium-" + rules.Mode;
		input = stream.EnumerateRunes().Select(r => r.Value).ToArray();
		variables = new Dictionary<string, string>(rules.VariableDefaults);
	}

	int Line(XElement e) => rules.Line(e);

	static string S(int c) => c < 0 ? "" : char.ConvertFromUtf32(c);

	// ---- The matcher (MatchState) ----

	void Init() => ms = new HashSet<MatchNode> { rules.Initial };

	void Step(int symbol, int alt)
	{
		var next = new HashSet<MatchNode>();

		foreach (MatchNode node in ms)
		{

			if (node.Transitions.TryGetValue(symbol, out var to))
				next.UnionWith(to);

			if (alt != symbol && node.Transitions.TryGetValue(alt, out var to2))
				next.UnionWith(to2);
		}

		ms = next;
	}

	int ClassifyFinals()
	{
		int result = int.MaxValue;

		foreach (MatchNode node in ms)
		{

			if (node.Rule > 0 && node.Rule < result)
				result = node.Rule;
		}

		return result < int.MaxValue ? result : -1;
	}

	static int Lower(int c) => c <= 0xFFFF ? char.ToLowerInvariant((char)c) : c;

	void StepTag(int[] s, ref int i)
	{

		for (int j = i + 1; j < s.Length; j++)
		{

			if (s[j] == '>')
			{
				string tag = string.Concat(s[i..(j + 1)].Select(S));

				if (rules.TagSymbols.TryGetValue(tag, out int symbol))
					Step(symbol, TransferRules.AnyTag);
				else
					Step(TransferRules.AnyTag, TransferRules.AnyTag);

				i = j;
				return;
			}
		}
	}

	// applyWord: feed a word to the matcher. transfer: the source side; interchunk: name and tags up to '{'; postchunk: the name only (its '<' case falls through to '{')
	void ApplyWord(string w)
	{
		Step('^', '^');
		int[] s = w.EnumerateRunes().Select(r => r.Value).ToArray();

		for (int i = 0; i < s.Length; i++)
		{

			if (s[i] == '\\')
			{
				i++;

				if (i < s.Length)
					Step(Lower(s[i]), TransferRules.AnyChar);

				continue;
			}

			if (isTransfer)
			{

				if (s[i] == '[' && i + 1 < s.Length && s[i + 1] == '[')
					throw new TransferException("[[word-bound blanks]] aren't supported by FTApertium (no FLExTrans rules file uses it)");

				if (s[i] == '/')
					break;

				if (s[i] == '<')
				{
					StepTag(s, ref i);
					continue;
				}
			}
			else
			{

				if (s[i] == '<' && isInterchunk)
				{
					StepTag(s, ref i);
					continue;
				}

				if (s[i] == '{' || s[i] == '<')
				{
					Step('$', '$');
					return;
				}
			}

			Step(Lower(s[i]), TransferRules.AnyChar);
		}

		Step('$', '$');
	}

	// ---- Reading tokens (readToken) ----

	int Get() => inPos < input.Length ? input[inPos++] : -1;

	int Peek() => inPos < input.Length ? input[inPos] : -1;

	Token ReadToken()
	{

		if (bufPos < buffer.Count)
			return buffer[bufPos++];

		var content = new StringBuilder();

		while (true)
		{
			int val = Get();

			if (val < 0)
				return Add(new Token(content.ToString(), TokenType.Eof));

			if (val == '\\')
			{
				content.Append('\\').Append(S(Get()));
			}
			else if (val == '[')
			{
				content.Append('[');

				while (true)
				{
					int val2 = Get();

					if (val2 == '\\')
					{
						content.Append('\\').Append(S(Get()));
					}
					else if (val2 == '[' && isTransfer)
					{
						throw new TransferException("[[word-bound blanks]] aren't supported by FTApertium (no FLExTrans rules file uses it)");
					}
					else if (val2 == ']')
					{
						content.Append(']');
						break;
					}
					else if (val2 < 0)
					{
						break;
					}
					else
					{
						content.Append(S(val2));
					}
				}
			}
			else if (!isTransfer && inWord && val == '{')
			{
				// A chunk's body, up to a '}' followed by '$'
				content.Append('{');

				while (true)
				{
					int val2 = Get();

					if (val2 < 0)
						break;

					if (val2 == '\\')
					{
						content.Append('\\').Append(S(Get()));
					}
					else if (val2 == '}')
					{
						content.Append('}');

						if (Peek() == '$')
							break;
					}
					else
					{
						content.Append(S(val2));
					}
				}
			}
			else if (val == '$' && (isTransfer || inWord))
			{
				inWord = false;
				return Add(new Token(content.ToString(), TokenType.Word));
			}
			else if (val == '^')
			{
				inWord = true;
				return Add(new Token(content.ToString(), TokenType.Blank));
			}
			else
			{
				content.Append(S(val));
			}
		}
	}

	Token Add(Token t)
	{
		buffer.Add(t);
		bufPos = buffer.Count;

		return t;
	}

	// ---- The main loop (transfer(), interchunk(), postchunk()) ----

	void TraceRule(string verb, int ruleId)
	{
		Trace.Append($"\n{tool}: {verb}{ruleId} line {rules.RuleLines[ruleId - 1]}");

		foreach (string w in tmpWord)
			Trace.Append(' ').Append(w);

		Trace.Append('\n');
	}

	public void Run()
	{
		int last = bufPos;
		int lastRuleId = -1;
		Init();

		while (true)
		{

			if (ms.Count == 0)
			{

				if (lastRule != null)
				{

					// Only transfer traces the rule it applies (Apertium main after 2025-07)
					if (isTransfer)
						TraceRule("Applied rule ", lastRuleId);

					if (CollectCoverage)
						Cover($"rule applied, {lastLWord}-word pattern, {tmpWord.Count - lastLWord} extra word(s) read past it");
					int consume = ApplyRule();

					if (consume >= 0)
						throw new TransferException("reject-current-rule isn't supported by FTApertium (no FLExTrans rules file uses it)");

					bufPos = last;
					lastRuleId = -1;
				}
				else if (tmpWord.Count != 0)
				{
					if (CollectCoverage)
						Cover("word with no rule" + (rules.DefaultChunk ? " (default chunk)" : ""));
					WriteUnmatched(tmpWord[0]);
					tmpWord.Clear();
					bufPos = last + 1;
					last = bufPos;
					Init();
				}
				else if (tmpBlank.Count != 0)
				{
					Output.Append(tmpBlank[0].Content);
					tmpBlank.Clear();
					last = bufPos;
					Init();
				}
			}

			int val = ClassifyFinals();

			if (val != -1)
			{
				lastRule = rules.RuleActions[val - 1];
				lastRuleId = val;
				last = bufPos;
				lastLWord = tmpWord.Count;
				TraceRule(isTransfer ? "Matched rule " : "Rule ", val);
			}

			Token current = ReadToken();

			switch (current.Type)
			{
				case TokenType.Word:
					ApplyWord(current.Content);
					tmpWord.Add(current.Content);
					break;

				case TokenType.Blank:
					Step(' ', ' ');
					tmpBlank.Add(current);
					break;

				case TokenType.Eof:

					if (tmpWord.Count != 0)
					{
						tmpBlank.Add(current);
						ms.Clear();
					}
					else
					{
						Output.Append(current.Content);
						return;
					}

					break;
			}
		}
	}

	// A word no rule matched. transfer: its target side (in a default chunk with default="chunk"); interchunk: the chunk as it is; postchunk: the chunk unpacked
	void WriteUnmatched(string unit)
	{

		if (isInterchunk)
		{
			Output.Append('^').Append(unit).Append('$');
			return;
		}

		if (isPostchunk)
		{
			Unchunk(unit);
			return;
		}

		string tl = SplitTarget(unit);

		if (tl.Length == 0)
			return;

		if (!rules.DefaultChunk)
		{

			if (tl.Length < 2 || tl[0] != '[' || tl[1] != '[')
				Output.Append('^');

			Output.Append(tl).Append('$');
		}
		else
		{
			Output.Append(tl[0] == '*' ? "^unknown<unknown>{^" : "^default<default>{^");
			Output.Append(tl).Append("$}$");
		}
	}

	// The target side of a ^sl/tl$ unit, as the no-rule branch of Transfer::transfer splits it (cur.swap(x) leaves x's old contents in cur)
	static string SplitTarget(string unit)
	{
		var parts = new[] { "", "", "" };
		var cur = new StringBuilder();
		int seenSlash = 0;

		void SwapInto(int slot)
		{
			string old = parts[slot];
			parts[slot] = cur.ToString();
			cur.Clear().Append(old);
		}

		for (int i = 0; i < unit.Length; i++)
		{
			char c = unit[i];

			if (c == '\\')
			{
				cur.Append(c);
				i++;

				if (i < unit.Length)
					cur.Append(unit[i]);

				continue;
			}

			if (c == '/')
			{
				parts[2] = "";
				SwapInto(Math.Min(seenSlash, 2));
				seenSlash++;
				continue;
			}

			if (c == '<')
			{

				while (i < unit.Length && unit[i] != '>')
				{
					cur.Append(unit[i]);

					if (unit[i] == '\\')
					{
						i++;
						cur.Append(unit[i]);
					}

					i++;
				}

				if (i >= unit.Length)
					break;
			}

			cur.Append(unit[i]);
		}

		if (cur.Length > 0)
		{
			parts[2] = "";
			SwapInto(Math.Min(seenSlash, 2));
		}

		return parts[1];
	}

	int ApplyRule()
	{

		if (isPostchunk)
			return ApplyPostchunkRule();

		int limit = tmpWord.Count;
		word = new RuleWord?[limit];
		lword = limit;

		for (int i = 0; i < limit; i++)
		{

			if (i > 0 && blankQueue.Count < lastLWord - 1)
				blankQueue.Enqueue(tmpBlank[i - 1].Content);

			word[i] = isTransfer ? SplitWord(tmpWord[i]) : RuleWord.ForChunk(tmpWord[i]);
		}

		int consume = ProcessRule(lastRule!);
		lastRule = null;
		word = null;
		tmpWord.Clear();
		tmpBlank.Clear();
		Init();

		return consume;
	}

	// Postchunk::applyRule: word 0 is the chunk header, words 1..n the words inside it
	int ApplyPostchunkRule()
	{
		string chunk = tmpWord[0];
		tmpWord = new List<string>();
		SplitWordsAndBlanks(chunk, tmpWord, tmpBlank);
		word = new RuleWord?[tmpWord.Count + 1];
		lword = tmpWord.Count;
		word[0] = RuleWord.ForChunk(WordZero(chunk));

		for (int i = 1; i <= tmpWord.Count; i++)
		{

			if (i != 1)
				blankQueue.Enqueue(tmpBlank[i - 1].Content);

			word[i] = RuleWord.ForChunk(tmpWord[i - 1]);
		}

		int consume = ProcessRule(lastRule!);
		lastRule = null;
		word = null;
		tmpWord.Clear();
		tmpBlank.Clear();
		Init();

		return consume;
	}

	// The ^source/target/reference$ unit as Transfer::applyRule splits it with -b
	static RuleWord SplitWord(string unit)
	{
		var parts = new[] { new StringBuilder(), new StringBuilder(), new StringBuilder() };
		int seenSlash = 0;
		bool inTag = false;

		for (int i = 0; i < unit.Length; i++)
		{
			char c = unit[i];
			StringBuilder cur = parts[Math.Min(seenSlash, 2)];

			if (c == '\\')
			{
				cur.Append(c);
				i++;

				if (i < unit.Length)
					cur.Append(unit[i]);

				continue;
			}

			if (c == '[' && i + 1 < unit.Length && unit[i + 1] == '[')
				throw new TransferException("[[word-bound blanks]] aren't supported by FTApertium (no FLExTrans rules file uses it)");

			if (c == '/' && !inTag)
			{
				seenSlash++;
				parts[2].Clear();
				continue;
			}

			if (c == '<')
				inTag = true;
			else if (c == '>')
				inTag = false;

			cur.Append(c);
		}

		return RuleWord.ForTransfer(parts[0].ToString(), parts[1].ToString(), parts[2].ToString());
	}

	// ---- Postchunk's chunk helpers ----

	static List<string> GetVecTags(string chunk)
	{
		var tags = new List<string>();

		for (int i = 0; i < chunk.Length; i++)
		{

			if (chunk[i] == '\\')
			{
				i++;
			}
			else if (chunk[i] == '<')
			{
				var tag = new StringBuilder();

				do
				{
					tag.Append(chunk[i++]);
				}
				while (i < chunk.Length && chunk[i] != '>');

				tags.Add(tag.Append('>').ToString());
			}
			else if (chunk[i] == '{')
			{
				break;
			}
		}

		return tags;
	}

	static int BeginChunk(string chunk)
	{

		for (int i = 0; i < chunk.Length; i++)
		{

			if (chunk[i] == '\\')
				i++;
			else if (chunk[i] == '{')
				return i + 1;
		}

		return chunk.Length;
	}

	static string WordZero(string chunk)
	{

		for (int i = 0; i < chunk.Length; i++)
		{

			if (chunk[i] == '\\')
				i++;
			else if (chunk[i] == '{')
				return chunk.Substring(0, i);
		}

		return "";
	}

	static string PseudoLemma(string chunk)
	{

		for (int i = 0; i < chunk.Length; i++)
		{

			if (chunk[i] == '\\')
				i++;
			else if (chunk[i] == '<' || chunk[i] == '{')
				return chunk.Substring(0, i);
		}

		return "";
	}

	// The inside of ^...$ in a chunk's body, from just after '^' to its '$': tags like <2> become the chunk's 2nd tag, and the chunk name's case goes onto the first letter or digit (or all)
	static void CopyWord(string chunk, ref int i, StringBuilder into, List<string> vecTags, bool upperAll, ref bool upperFirst)
	{

		while (chunk[++i] != '$')
		{

			if (chunk[i] == '\\')
			{
				into.Append('\\').Append(chunk[++i]);
			}
			else if (chunk[i] == '<')
			{

				if (char.IsDigit(chunk[i + 1]))
				{
					int j = ++i;

					while (chunk[++i] != '>') { }

					// StringUtils::stoi is sscanf "%d": only the leading digits count, so a word's <3sg_cond> tag is taken as a reference to the chunk's 3rd tag too
					string digits = new string(chunk.Substring(j, i - j).TakeWhile(char.IsDigit).ToArray());
					int value = int.Parse(digits) - 1;

					if (value >= 0 && vecTags.Count > value)
						into.Append(vecTags[value]);
				}
				else
				{
					into.Append('<');

					while (chunk[++i] != '>')
						into.Append(chunk[i]);

					into.Append('>');
				}
			}
			else if (upperAll)
			{
				into.Append(char.ToUpperInvariant(chunk[i]));
			}
			else if (upperFirst && char.IsLetterOrDigit(chunk[i]))
			{
				into.Append(char.ToUpperInvariant(chunk[i]));
				upperFirst = false;
			}
			else
			{
				into.Append(chunk[i]);
			}
		}
	}

	// Postchunk::unchunk: a chunk no rule matched, written as its words
	void Unchunk(string chunk)
	{
		List<string> vecTags = GetVecTags(chunk);
		string caseInfo = CaseUtils.GetCase(PseudoLemma(chunk));
		bool upperAll = caseInfo == "AA";
		bool upperFirst = caseInfo == "Aa";
		int limit = chunk.Length - 2;

		for (int i = BeginChunk(chunk); i < limit; i++)
		{

			if (chunk[i] == '\\')
			{
				Output.Append('\\').Append(chunk[++i]);
			}
			else if (chunk[i] == '^')
			{
				var w = new StringBuilder();
				CopyWord(chunk, ref i, w, vecTags, upperAll, ref upperFirst);
				Output.Append('^').Append(w).Append('$');
			}
			else if (chunk[i] == '[')
			{
				Output.Append('[');

				while (chunk[++i] != ']')
				{

					if (chunk[i] == '\\')
						Output.Append('\\').Append(chunk[++i]);
					else
						Output.Append(chunk[i]);
				}

				Output.Append(']');
			}
			else
			{
				Output.Append(chunk[i]);
			}
		}
	}

	// Postchunk::splitWordsAndBlanks: the chunk's words, and its blanks appended to blanks (whose last entry may be a buffered token, changed in place; see TRAPS)
	static void SplitWordsAndBlanks(string chunk, List<string> words, List<Token> blanks)
	{
		List<string> vecTags = GetVecTags(chunk);
		string caseInfo = CaseUtils.GetCase(PseudoLemma(chunk));
		bool upperAll = caseInfo == "AA";
		bool upperFirst = caseInfo == "Aa";
		bool lastBlank = true;
		int limit = chunk.Length - 2;

		for (int i = BeginChunk(chunk); i < limit; i++)
		{

			if (chunk[i] == '^')
			{

				if (!lastBlank)
					blanks.Add(new Token("", TokenType.Blank));

				lastBlank = false;
				var w = new StringBuilder();
				CopyWord(chunk, ref i, w, vecTags, upperAll, ref upperFirst);
				words.Add(w.ToString());
			}
			else if (chunk[i] == '[')
			{

				if (chunk[i + 1] == '[')
					throw new TransferException("[[word-bound blanks]] aren't supported by FTApertium (no FLExTrans rules file uses it)");

				if (!(lastBlank && blanks.Count > 0))
					blanks.Add(new Token("", TokenType.Blank));

				var sb = new StringBuilder("[");

				while (chunk[++i] != ']')
				{

					if (chunk[i] == '\\')
						sb.Append('\\').Append(chunk[++i]);
					else
						sb.Append(chunk[i]);
				}

				sb.Append(chunk[i]);
				blanks[^1].Content += sb.ToString();
				lastBlank = true;
			}
			else
			{

				if (!lastBlank)
					blanks.Add(new Token("", TokenType.Blank));

				blanks[^1].Content += chunk[i] == '\\' ? "\\" + chunk[++i] : chunk[i].ToString();
				lastBlank = true;
			}
		}
	}

	// ---- The interpreter (transfer_base.cc and each tool's own) ----

	int ProcessRule(XElement action)
	{
		int consume = -1;

		foreach (XElement i in action.Elements())
		{
			consume = ProcessInstruction(i);

			if (consume != -1)
				break;
		}

		// Flush the remaining blanks that aren't a single space
		while (blankQueue.Count > 0)
		{
			string b = blankQueue.Dequeue();

			if (b != " ")
				Output.Append(b);
		}

		return consume;
	}

	int ProcessInstruction(XElement e)
	{
		if (CollectCoverage)
			Cover("instruction " + e.Name.LocalName);

		switch (e.Name.LocalName)
		{
			case "choose":
				return ProcessChoose(e);

			case "let":
				ProcessLet(e);
				break;

			case "append":
				ProcessAppend(e);
				break;

			case "out":
				ProcessOut(e);
				break;

			case "call-macro":
				ProcessCallMacro(e);
				break;

			case "modify-case":
				ProcessModifyCase(e);
				break;

			case "reject-current-rule":
				throw new TransferException("reject-current-rule isn't supported by FTApertium (no FLExTrans rules file uses it)");
		}

		return -1;
	}

	int ProcessChoose(XElement e)
	{
		int consume = -1;

		foreach (XElement option in e.Elements())
		{

			if (option.Name.LocalName == "when")
			{
				bool picked = false;

				foreach (XElement it in option.Elements())
				{

					if (it.Name.LocalName == "test")
					{

						if (!ProcessTest(it))
							break;

						picked = true;
					}
					else
					{
						consume = ProcessInstruction(it);

						if (consume != -1)
							return consume;
					}
				}

				if (picked)
					return consume;
			}
			else if (option.Name.LocalName == "otherwise")
			{

				foreach (XElement it in option.Elements())
				{
					consume = ProcessInstruction(it);

					if (consume != -1)
						return consume;
				}
			}
		}

		return consume;
	}

	void ProcessAppend(XElement e)
	{
		string name = (string)e.Attribute("n")!;

		foreach (XElement i in e.Elements())
			variables[name] = Var(name) + EvalString(i);
	}

	string Var(string name) => variables.TryGetValue(name, out string? v) ? v : "";

	bool ProcessTest(XElement e)
	{
		XElement? first = e.Elements().FirstOrDefault();

		return first != null && ProcessLogical(first);
	}

	static (XElement, XElement) TwoChildren(XElement e)
	{
		var list = e.Elements().Take(2).ToList();

		return (list[0], list[1]);
	}

	static bool Caseless(XElement e) => (string?)e.Attribute("caseless") == "yes";

	HashSet<string> List(XElement listElem, bool caseless)
	{
		// A <list> without n (some files write <list v="...">) is the empty list "", as getattr() gives Apertium
		string n = (string?)listElem.Attribute("n") ?? "";
		var lists = caseless ? rules.ListsLow : rules.Lists;

		if (!lists.TryGetValue(n, out var set))
		{
			set = new HashSet<string>();
			lists[n] = set;
		}

		return set;
	}

	bool ProcessLogical(XElement e)
	{
		if (CollectCoverage)
			Cover("test " + e.Name.LocalName + (Caseless(e) ? " caseless" : ""));

		switch (e.Name.LocalName)
		{
			case "equal":
			{
				var (a, b) = TwoChildren(e);

				if (Caseless(e))
					return CaseUtils.ToLower(EvalString(a)) == CaseUtils.ToLower(EvalString(b));

				return EvalString(a) == EvalString(b);
			}

			case "begins-with":
			{
				var (a, b) = TwoChildren(e);

				if (Caseless(e))
					return CaseUtils.ToLower(EvalString(a)).StartsWith(CaseUtils.ToLower(EvalString(b)), StringComparison.Ordinal);

				return EvalString(a).StartsWith(EvalString(b), StringComparison.Ordinal);
			}

			case "ends-with":
			{
				var (a, b) = TwoChildren(e);

				if (Caseless(e))
					return CaseUtils.ToLower(EvalString(a)).EndsWith(CaseUtils.ToLower(EvalString(b)), StringComparison.Ordinal);

				return EvalString(a).EndsWith(EvalString(b), StringComparison.Ordinal);
			}

			case "begins-with-list":
			{
				var (a, b) = TwoChildren(e);
				string needle = EvalString(a);
				bool caseless = Caseless(e);

				if (caseless)
					needle = CaseUtils.ToLower(needle);

				return List(b, caseless).Any(it => needle.StartsWith(it, StringComparison.Ordinal));
			}

			case "ends-with-list":
			{
				var (a, b) = TwoChildren(e);
				string needle = EvalString(a);
				bool caseless = Caseless(e);

				if (caseless)
					needle = CaseUtils.ToLower(needle);

				return List(b, caseless).Any(it => needle.EndsWith(it, StringComparison.Ordinal));
			}

			case "contains-substring":
			{
				var (a, b) = TwoChildren(e);

				if (Caseless(e))
					return CaseUtils.ToLower(EvalString(a)).Contains(CaseUtils.ToLower(EvalString(b)), StringComparison.Ordinal);

				return EvalString(a).Contains(EvalString(b), StringComparison.Ordinal);
			}

			case "or":
				return e.Elements().Any(ProcessLogical);

			case "and":
				return e.Elements().All(ProcessLogical);

			case "not":
			{
				XElement? first = e.Elements().FirstOrDefault();

				return first != null && !ProcessLogical(first);
			}

			case "in":
			{
				var (a, b) = TwoChildren(e);
				string sval = EvalString(a);

				if (Caseless(e))
					return List(b, true).Contains(CaseUtils.ToLower(sval));

				return List(b, false).Contains(sval);
			}
		}

		return false;
	}

	static string Tags(string v) => "<" + v.Replace(".", "><") + ">";

	static int IntAttr(XElement e, string name) => int.TryParse((string?)e.Attribute(name), out int v) ? v : 0;

	// A position attribute as each tool stores it: transfer and interchunk count from 0 (pos-1); postchunk keeps it as written, since its word 0 is the chunk header
	int PosAttr(XElement e) => isPostchunk ? IntAttr(e, "pos") : IntAttr(e, "pos") - 1;

	Regex? Attr(string part) => rules.AttrItems.TryGetValue(part, out Regex? re) ? re : null;

	// evalString: compile the element once, then evaluate it
	string EvalString(XElement e)
	{
		string name = e.Name.LocalName;
		if (CollectCoverage)
			Cover("expression " + name + (name == "clip" ? $" side={(string?)e.Attribute("side")} part={((string?)e.Attribute("part") is "lem" or "lemh" or "lemq" or "whole" or "tags" or "chcontent" or "content" ? (string?)e.Attribute("part") : "<attr>")}" + (e.Attribute("link-to") != null ? " link-to" : "") : ""));

		if (cache.ContainsKey(e))
			return EvalCached(e);

		switch (name)
		{
			case "clip":
				ProcessClip(e);
				break;

			case "lit-tag":
				cache[e] = new Instr(InstrType.Lit, Tags((string?)e.Attribute("v") ?? ""), 0);
				break;

			case "lit":
				cache[e] = new Instr(InstrType.Lit, (string?)e.Attribute("v") ?? "", 0);
				break;

			case "b":
				cache[e] = new Instr(InstrType.B, " ", -1);
				break;

			case "get-case-from":
				cache[e] = new Instr(InstrType.GetCaseFrom, "lem", IntAttr(e, "pos") - 1, e.Elements().FirstOrDefault());
				break;

			case "var":
				cache[e] = new Instr(InstrType.Var, (string)e.Attribute("n")!, 0);
				break;

			case "case-of":
			{
				string side = (string?)e.Attribute("side") ?? "";
				InstrType type = !isTransfer ? InstrType.CaseOfTl : side == "sl" ? InstrType.CaseOfSl : side == "ref" ? InstrType.CaseOfRef : InstrType.CaseOfTl;
				cache[e] = new Instr(type, (string?)e.Attribute("part") ?? "", PosAttr(e));
				break;
			}

			case "lu-count":

				if (!isPostchunk)
					throw new TransferException($"Error: unexpected expression: '{name}'");

				cache[e] = new Instr(InstrType.LuCount, "", 0);
				break;

			case "concat":
				return string.Concat(e.Elements().Select(EvalString));

			case "lu":

				if (isInterchunk)
					throw new TransferException($"Error: unexpected expression: '{name}'");

				return ProcessLu(e);

			case "mlu":
				throw new TransferException("<mlu> isn't supported by FTApertium (no FLExTrans rules file uses it)");

			case "chunk":

				if (isPostchunk)
					throw new TransferException($"Error: unexpected expression: '{name}'");

				return ProcessChunk(e);

			default:
				throw new TransferException($"Error: unexpected expression: '{name}'");
		}

		return EvalCached(e);
	}

	bool CheckIndex(XElement e, int index)
	{

		// postchunk allows index == limit (its words run 1..n)
		if (isPostchunk ? index > lword : index >= lword)
		{
			Trace.Append($"Error in tr.t{(isTransfer ? 1 : isInterchunk ? 2 : 3)}x: line {Line(e)}: index {(isPostchunk ? ">" : ">=")} limit\n");
			return false;
		}

		if (index < 0)
		{
			Trace.Append($"Error in tr.t{(isTransfer ? 1 : isInterchunk ? 2 : 3)}x: line {Line(e)}: index < 0\n");
			return false;
		}

		if (word![index] == null)
		{
			Trace.Append($"Error in tr.t{(isTransfer ? 1 : isInterchunk ? 2 : 3)}x: line {Line(e)}: Null access at word[index]\n");
			return false;
		}

		return true;
	}

	// A part of a word: transfer reads the chosen side; interchunk and postchunk read the chunk (interchunk's part="content" without its braces)
	string ReadPart(RuleWord w, InstrType type, string part)
	{

		if (!isTransfer)
		{
			string value = w.ChunkPart(Attr(part));

			return isInterchunk && part == "content" && value.Length >= 2 ? value.Substring(1, value.Length - 2) : value;
		}

		return RuleWord.Match(Attr(part), type is InstrType.ClipSl or InstrType.LinkToSl or InstrType.CaseOfSl ? w.S : type is InstrType.ClipRef or InstrType.LinkToRef or InstrType.CaseOfRef ? w.R : w.T);
	}

	string EvalCached(XElement e)
	{
		Instr ti = cache[e];

		switch (ti.Type)
		{
			case InstrType.ClipSl:
			case InstrType.ClipTl:
			case InstrType.ClipRef:
				return CheckIndex(e, ti.Pos) ? ReadPart(word![ti.Pos]!, ti.Type, ti.Content) : "";

			case InstrType.LinkToSl:
			case InstrType.LinkToTl:
			case InstrType.LinkToRef:
				return CheckIndex(e, ti.Pos) && ReadPart(word![ti.Pos]!, ti.Type, ti.Content).Length > 0 ? $"<{ti.StrVal}>" : "";

			case InstrType.Var:
				return Var(ti.Content);

			case InstrType.Lit:
				return ti.Content;

			case InstrType.LuCount:
				return tmpWord.Count.ToString();

			case InstrType.B:

				if (blankQueue.Count > 0)
					return inOut ? blankQueue.Dequeue() : blankQueue.Peek();

				return " ";

			case InstrType.GetCaseFrom:
			{
				// postchunk reads word pos (its words count from 1); the others word pos-1
				int pos = isPostchunk ? ti.Pos + 1 : ti.Pos;

				if (!CheckIndex(e, pos))
					return "";

				string source = isTransfer ? RuleWord.Match(Attr("lem"), word![pos]!.S) : word![pos]!.ChunkPart(Attr("lem"));

				return CopyCaseTags(source, EvalString(ti.Pointer!));
			}

			case InstrType.CaseOfSl:
			case InstrType.CaseOfTl:
			case InstrType.CaseOfRef:
				return CheckIndex(e, ti.Pos) ? CaseUtils.GetCase(ReadPart(word![ti.Pos]!, ti.Type, ti.Content)) : "";
		}

		return "";
	}

	// TransferBase::copycase: the case of src applied to dest's lemma; tags stay; anything after the tags follows the second letter's case
	static string CopyCaseTags(string src, string dest)
	{
		int loc = dest.IndexOf('<');
		int loc2 = dest.LastIndexOf('>');

		if (loc < 0 || loc2 < 0)
			return CaseUtils.CopyCase(src, dest);

		string cs = CaseUtils.GetCase(src);
		var ret = new StringBuilder(CaseUtils.CopyCase(cs, dest.Substring(0, loc)));
		ret.Append(dest, loc, loc2 - loc + 1);

		if (loc2 + 1 < dest.Length)
		{
			string rest = dest.Substring(loc2 + 1);
			ret.Append(char.IsUpper(cs[1]) ? CaseUtils.ToUpper(rest) : CaseUtils.ToLower(rest));
		}

		return ret.ToString();
	}

	void ProcessClip(XElement e)
	{
		string side = (string?)e.Attribute("side") ?? "";
		string part = (string?)e.Attribute("part") ?? "";
		int pos = PosAttr(e);
		string linkTo = (string?)e.Attribute("link-to") ?? "";

		// interchunk and postchunk ignore side and link-to
		if (!isTransfer)
			cache[e] = new Instr(InstrType.ClipTl, part, pos);
		else if (linkTo.Length > 0)
			cache[e] = new Instr(side == "sl" ? InstrType.LinkToSl : side == "ref" ? InstrType.LinkToRef : InstrType.LinkToTl, part, pos, null, linkTo);
		else
			cache[e] = new Instr(side == "sl" ? InstrType.ClipSl : side == "ref" ? InstrType.ClipRef : InstrType.ClipTl, part, pos);
	}

	string ProcessLu(XElement e)
	{
		var myword = new StringBuilder();

		foreach (XElement i in e.Elements())
			myword.Append(EvalString(i));

		if (myword.Length == 0)
			return "";

		// transfer leaves off the ^ when the word starts with a [[word-bound blank]]; postchunk doesn't check
		if (isTransfer && myword.Length >= 2 && myword[0] == '[' && myword[1] == '[')
			return myword + "$";

		return "^" + myword + "$";
	}

	void ProcessOut(XElement e)
	{
		inOut = true;

		foreach (XElement i in e.Elements())
		{
			string name = i.Name.LocalName;

			if (name == "mlu")
				throw new TransferException("<mlu> isn't supported by FTApertium (no FLExTrans rules file uses it)");

			if (isTransfer && !rules.DefaultChunk && name == "lu" || isPostchunk && name == "lu")
				Output.Append(ProcessLu(i));
			else if (!isPostchunk && (isInterchunk || rules.DefaultChunk) && name == "chunk")
				Output.Append(ProcessChunk(i));
			else
				Output.Append(EvalString(i));
		}

		inOut = false;
	}

	string ProcessChunk(XElement e)
	{

		// Interchunk::processChunk: ^ + the children + $
		if (isInterchunk)
			return "^" + string.Concat(e.Elements().Select(EvalString)) + "$";

		string name = (string?)e.Attribute("name") ?? "";
		string nameFrom = (string?)e.Attribute("namefrom") ?? "";
		string caseOfChunk = (string?)e.Attribute("case") ?? "aa";
		var result = new StringBuilder("^");

		string chunkName = name.Length > 0 ? name : nameFrom.Length > 0 ? Var(nameFrom) : throw new TransferException("Error: you must specify either 'name' or 'namefrom' for the 'chunk' element");

		result.Append(caseOfChunk.Length > 0 ? CaseUtils.CopyCase(Var(caseOfChunk), chunkName) : chunkName);

		foreach (XElement i in e.Elements())
		{

			switch (i.Name.LocalName)
			{
				case "tags":

					foreach (XElement tag in i.Elements("tag"))
					{

						foreach (XElement j in tag.Elements())
							result.Append(EvalString(j));
					}

					result.Append('{');
					break;

				case "lu":
					result.Append(ProcessLu(i));
					break;

				case "mlu":
					throw new TransferException("<mlu> isn't supported by FTApertium (no FLExTrans rules file uses it)");

				default:
					result.Append(EvalString(i));
					break;
			}
		}

		return result.Append("}$").ToString();
	}

	// Write a value into a part of a word: transfer's chosen side, or the chunk
	void SetPart(XElement stmt, RuleWord w, InstrType type, string part, string value, string what)
	{
		Regex? re = Attr(part);
		bool match;

		if (!isTransfer)
			match = w.SetChunkPart(re, value);
		else if (type == InstrType.ClipSl)
			match = RuleWord.Replace(re, ref w.S, value);
		else if (type == InstrType.ClipRef)
			match = RuleWord.Replace(re, ref w.R, value);
		else
			match = RuleWord.Replace(re, ref w.T, value);

		if (CollectCoverage)
			Cover($"{what} into a clip, value {(match ? "kept" : "discarded")}");

		if (!match)
			Trace.Append($"{tool} warning: <{what}> on line {Line(stmt)} sometimes discards its value.\n");
	}

	void ProcessLet(XElement e)
	{
		var children = e.Elements().Take(2).ToList();
		XElement left = children[0];
		XElement right = children[1];

		if (cache.TryGetValue(left, out Instr? ti))
		{

			switch (ti.Type)
			{
				case InstrType.Var:
					variables[ti.Content] = EvalString(right);
					return;

				case InstrType.ClipSl:
				case InstrType.ClipTl:
				case InstrType.ClipRef:

					// Only transfer checks the index here
					if (!isTransfer || CheckIndex(left, ti.Pos))
						SetPart(e, word![ti.Pos]!, ti.Type, ti.Content, EvalString(right), "let");

					return;

				default:
					return;
			}
		}

		if (left.Name.LocalName == "var")
		{
			string val = (string)left.Attribute("n")!;
			variables[val] = EvalString(right);
			cache[left] = new Instr(InstrType.Var, val, 0);
		}
		else if (left.Name.LocalName == "clip")
		{
			string side = (string?)left.Attribute("side") ?? "";
			string part = (string?)left.Attribute("part") ?? "";
			int pos = PosAttr(left);

			if (isTransfer && pos >= lword)
			{
				Trace.Append("Error: Transfer::processLet() bad access on pos >= lword\n");
				return;
			}

			if (isTransfer && word![pos] == null)
			{
				Trace.Append("Error: Transfer::processLet() null access on word[pos]\n");
				return;
			}

			InstrType type = !isTransfer ? InstrType.ClipTl : side == "tl" ? InstrType.ClipTl : side == "ref" ? InstrType.ClipRef : InstrType.ClipSl;
			SetPart(e, word![pos]!, type, part, EvalString(right), "let");
			cache[left] = new Instr(type, part, pos);
		}
	}

	void ProcessModifyCase(XElement e)
	{
		var children = e.Elements().Take(2).ToList();
		XElement left = children[0];
		XElement right = children[1];

		if (left.Name.LocalName == "clip")
		{
			string side = (string?)left.Attribute("side") ?? "";
			string part = (string?)left.Attribute("part") ?? "";
			RuleWord w = word![PosAttr(left)]!;
			InstrType type = !isTransfer ? InstrType.ClipTl : side == "sl" ? InstrType.ClipSl : side == "ref" ? InstrType.ClipRef : InstrType.ClipTl;
			string current = isTransfer ? ReadPart(w, type, part) : w.ChunkPart(Attr(part));
			SetPart(e, w, type, part, CaseUtils.CopyCase(EvalString(right), current), "modify-case");
		}
		else if (left.Name.LocalName == "var")
		{
			string val = (string)left.Attribute("n")!;
			variables[val] = CaseUtils.CopyCase(EvalString(right), Var(val));
		}
	}

	void ProcessCallMacro(XElement e)
	{
		string n = (string)e.Attribute("n")!;

		if (!rules.Macros.TryGetValue(n, out XElement? macro))
			throw new TransferException($"Undefined macro '{n}'");

		int npar = IntAttr(macro, "npar");
		RuleWord?[]? myword = null;
		bool indexesOk = true;

		if (isPostchunk)
		{

			if (npar <= 0)
				throw new TransferException("Postchunk::processCallMacro() assumes npar > 0, but got npar <= 0");

			// Word 0 stays the chunk header; positions are used as written, an out-of-range one makes the call skip the macro
			myword = new RuleWord?[npar + 1];
			myword[0] = word![0];
			int idx = 1;

			foreach (XElement i in e.Elements())
			{
				int pos = IntAttr(i, "pos");

				if (!CheckIndex(e, pos))
				{
					indexesOk = false;
					pos = 1;
				}

				myword[idx] = word[pos];
				idx++;
			}
		}
		else if (npar > 0)
		{
			myword = new RuleWord?[npar];
			int idx = 0;

			foreach (XElement i in e.Elements())
			{

				if (idx >= npar)
				{
					Trace.Append($"Error: processCallMacro() number of arguments >= npar at line {Line(i)}\n");
					return;
				}

				int pos = IntAttr(i, "pos") - 1;
				myword[idx] = pos >= 0 && pos < word!.Length ? word[pos] : null;
				idx++;
			}
		}

		(myword, word) = (word, myword);
		(npar, lword) = (lword, npar);

		if (indexesOk)
		{

			foreach (XElement i in macro.Elements())
				ProcessInstruction(i);
		}
		else
		{
			Trace.Append($"Warning: Not calling macro \"{n}\" from line {Line(e)} (empty word?)\n");
		}

		(myword, word) = (word, myword);
		(npar, lword) = (lword, npar);
	}
}
