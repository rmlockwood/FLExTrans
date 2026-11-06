// RegexBuilder.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. The <re> entries of a bilingual.dix, as lt-comp compiles them.
//
// OVERVIEW (AI generated, then edited)
//
// The <re> entries of a bilingual.dix as transducer fragments, each character mapping to itself (as lt-comp's RegexpCompiler compiles them). Supports what lttoolbox's regular expressions
// offer and FLExTrans dictionaries use: literal and \-escaped characters, [classes] with ranges, ( ) groups, | alternation and the * + ? repeats. The fragment starts behind an epsilon step,
// so the trie of ordinary entries can never wander into it.
//
// CODE STRUCTURE
//
// Build() parses with Alternation() > Sequence() > Repeat() > Atom() (recursive descent), each returning a (start, end) fragment.
//

namespace FTtranslator.Apertium;

public class RegexBuilder
{
	readonly int[] re;
	int pos;

	public RegexBuilder(string pattern)
	{
		re = pattern.EnumerateRunes().Select(r => r.Value).ToArray();
	}

	// A fragment is a start node and an end node; returns the end, which the rest of the entry continues from
	public Node Build(Node from)
	{
		(Node start, Node end) = Alternation();

		if (pos != re.Length)
			throw new NotSupportedException($"Unexpected '{char.ConvertFromUtf32(re[pos])}' in <re>");

		from.Add(new Transition(0, 0, start));

		return end;
	}

	static void Eps(Node a, Node b) => a.Add(new Transition(0, 0, b));

	(Node, Node) Alternation()
	{
		var branches = new List<(Node, Node)> { Sequence() };

		while (pos < re.Length && re[pos] == '|')
		{
			pos++;
			branches.Add(Sequence());
		}

		if (branches.Count == 1)
			return branches[0];

		Node start = new(), end = new();

		foreach ((Node s, Node e) in branches)
		{
			Eps(start, s);
			Eps(e, end);
		}

		return (start, end);
	}

	(Node, Node) Sequence()
	{
		Node start = new();
		Node current = start;

		while (pos < re.Length && re[pos] != '|' && re[pos] != ')')
		{
			(Node s, Node e) = Repeat();
			Eps(current, s);
			current = e;
		}

		return (start, current);
	}

	(Node, Node) Repeat()
	{
		(Node s, Node e) = Atom();

		while (pos < re.Length && (re[pos] == '*' || re[pos] == '+' || re[pos] == '?'))
		{
			int op = re[pos++];
			Node start = new(), end = new();
			Eps(start, s);
			Eps(e, end);

			if (op != '+')
				Eps(start, end);

			if (op != '?')
				Eps(e, s);

			(s, e) = (start, end);
		}

		return (s, e);
	}

	(Node, Node) Atom()
	{
		int c = re[pos++];
		Node start = new(), end = new();

		if (c == '(')
		{
			(Node s, Node e) = Alternation();

			if (pos >= re.Length || re[pos] != ')')
				throw new NotSupportedException("Unclosed ( in <re>");

			pos++;
			return (s, e);
		}

		if (c == '[')
		{

			if (pos < re.Length && re[pos] == '^')
				throw new NotSupportedException("[^...] in <re> isn't supported yet");

			var chars = new List<int>();

			while (pos < re.Length && re[pos] != ']')
			{
				int ch = re[pos++];

				if (ch == '\\')
					ch = re[pos++];

				// A range a-z
				if (pos + 1 < re.Length && re[pos] == '-' && re[pos + 1] != ']')
				{
					pos++;
					int hi = re[pos++];

					if (hi == '\\')
						hi = re[pos++];

					for (int x = ch; x <= hi; x++)
						chars.Add(x);
				}
				else
				{
					chars.Add(ch);
				}
			}

			pos++;

			foreach (int ch in chars.Distinct())
				start.Add(new Transition(ch, ch, end));

			return (start, end);
		}

		if (c == '\\')
			c = re[pos++];
		else if (c == '.')
			throw new NotSupportedException(". (any character) in <re> isn't supported yet");

		start.Add(new Transition(c, c, end));

		return (start, end);
	}
}
