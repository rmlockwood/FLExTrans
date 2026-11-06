// Bilingual.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. lt-proc -b (lttoolbox's bilingual lookup) in C#, loading bilingual.dix directly.
//
// OVERVIEW (AI generated, then edited)
//
// lt-proc -b -N1 -L1 (lttoolbox 3.8.3, FSTProcessor::bilingual) without lttoolbox. Instead of compiling bilingual.dix to lttoolbox's binary transducer, the dictionary is loaded straight into
// an in-memory transducer (a trie of input:output symbol pairs, plus Thompson-style fragments for <re> entries), and a stream is run through it the way bilingual() runs one through the
// compiled transducer:
//
//  - Each word's symbols (characters, and tags as single symbols) are stepped through the transducer. An uppercase character may also step as its lowercase form; a path that does is "dirty",
//    and its output is recased at the end (State::step_override, State::filterFinalsArray).
//  - The last symbol after which some path is final wins (longest match). The symbols after it (the "queue", normally the extra tags) are appended to the translation.
//  - A word without tags only counts as found on a complete match. A word not found comes back as source/@source.
//  - -N1: the lowest-weight result, ties in path order. lttoolbox's order comes from its minimized transducer; here it is file order. The two can differ only when a source key has several
//    translations, which is rare in FLExTrans dictionaries.
//
// FLExTrans dictionaries use only <e>, <p>/<l>/<r>, <i>, <s>, <b/> and <re>, all handled here; anything else throws, so a dictionary that needs more is noticed rather than mistranslated.
//
// CODE STRUCTURE
//
// Alphabet numbers tags; Node and Transition make the transducer. BilingualDictionary.Load() reads the .dix (AddEntry(), Symbols(), AddPairs(), RegexBuilder for <re>);
// Process() runs a stream: LtStreamReader splits it, Translate() looks up each unit with Step()/Advance()/EpsilonClosure() and Finals().
//

using System.Text;
using System.Xml.Linq;

namespace FTtranslator.Apertium;

// Symbols are ints: a character is its code point, a tag is a negative number from the alphabet, 0 is epsilon
public class Alphabet
{
	readonly Dictionary<string, int> tagIds = new();
	readonly List<string> tags = new() { "" };

	public int Tag(string tag)
	{

		if (!tagIds.TryGetValue(tag, out int id))
		{
			tags.Add(tag);
			id = -(tags.Count - 1);
			tagIds[tag] = id;
		}

		return id;
	}

	public static bool IsTag(int symbol) => symbol < 0;

	public void Append(StringBuilder sb, int symbol, bool uppercase = false)
	{

		if (symbol < 0)
		{
			sb.Append(tags[-symbol]);
		}
		else if (symbol > 0)
		{
			sb.Append(char.ConvertFromUtf32(uppercase ? ToUpper(symbol) : symbol));
		}
	}

	public static int ToUpper(int c) => c > 0xFFFF ? c : char.ToUpperInvariant((char)c);

	public static int ToLower(int c) => c > 0xFFFF ? c : char.ToLowerInvariant((char)c);

	public static bool IsUpper(int c) => c > 0 && c <= 0xFFFF && char.IsUpper((char)c);
}

// A transducer state. Transitions are indexed by input symbol (the root of a real dictionary has thousands), and each list keeps the order they were added in, which is the order results
// come out in (see -N1 in the overview)
public class Node
{
	const int IndexAbove = 8;

	readonly List<Transition> transitions = new();
	Dictionary<int, List<Transition>>? index;
	public bool IsFinal;
	public double FinalWeight;

	static readonly List<Transition> None = new();

	public void Add(Transition t)
	{
		transitions.Add(t);
		index = null;
	}

	// The transitions that may have this input: all of them for a node with a few (callers check t.Input), else the indexed ones, the index built on first use
	public List<Transition> Candidates(int input)
	{

		if (transitions.Count <= IndexAbove)
			return transitions;

		if (index == null)
		{
			index = new Dictionary<int, List<Transition>>();

			foreach (Transition t in transitions)
			{

				if (!index.TryGetValue(t.Input, out List<Transition>? list))
				{
					list = new List<Transition>();
					index[t.Input] = list;
				}

				list.Add(t);
			}
		}

		return index.TryGetValue(input, out List<Transition>? found) ? found : None;
	}
}

public readonly record struct Transition(int Input, int Output, Node To);

public class BilingualDictionary
{
	public readonly Alphabet Alphabet = new();
	public readonly Node Root = new();

	// lt-proc's escaped_chars: written with a backslash before them
	static readonly HashSet<int> EscapedChars = new() { '[', ']', '{', '}', '^', '$', '/', '\\', '@', '<', '>' };

	public static BilingualDictionary Load(string path)
	{
		var dict = new BilingualDictionary();
		XElement root = XDocument.Load(path).Root!;

		foreach (XElement section in root.Elements("section"))
		{

			foreach (XElement entry in section.Elements("e"))
			{
				dict.AddEntry(entry);
			}
		}

		return dict;
	}

	void AddEntry(XElement entry)
	{

		if (entry.Attribute("r") != null)
			throw new NotSupportedException("<e r=...> restrictions aren't supported");

		double weight = double.TryParse((string?)entry.Attribute("w"), System.Globalization.CultureInfo.InvariantCulture, out double w) ? w : 0;
		Node current = Root;

		foreach (XElement part in entry.Elements())
		{

			switch (part.Name.LocalName)
			{
				case "i":
					List<int> both = Symbols(part);
					current = AddPairs(current, both, both);
					break;

				case "p":
					current = AddPairs(current, Symbols(part.Element("l")!), Symbols(part.Element("r")!));
					break;

				case "re":
					current = new RegexBuilder(part.Value).Build(current);
					break;

				default:
					throw new NotSupportedException($"<{part.Name.LocalName}> in <e> isn't supported");
			}
		}

		current.IsFinal = true;
		current.FinalWeight = weight;
	}

	// The symbols of an <l>, <r> or <i>: text characters, <s n="..."/> as a tag, <b/> as a space (as lt-comp compiles them)
	List<int> Symbols(XElement elem)
	{
		var result = new List<int>();

		foreach (XNode node in elem.Nodes())
		{

			if (node is XText text)
			{

				foreach (Rune r in text.Value.EnumerateRunes())
					result.Add(r.Value);
			}
			else if (node is XElement child)
			{

				switch (child.Name.LocalName)
				{
					case "s":
						result.Add(Alphabet.Tag($"<{(string)child.Attribute("n")!}>"));
						break;

					case "b":
						result.Add(' ');
						break;

					default:
						throw new NotSupportedException($"<{child.Name.LocalName}> in <{elem.Name.LocalName}> isn't supported");
				}
			}
		}

		return result;
	}

	// The two sides aligned position by position, the shorter padded with epsilon (as lt-comp does), shared as a trie where input and output agree
	static Node AddPairs(Node from, List<int> input, List<int> output)
	{
		Node current = from;

		for (int i = 0; i < Math.Max(input.Count, output.Count); i++)
		{
			int inSym = i < input.Count ? input[i] : 0;
			int outSym = i < output.Count ? output[i] : 0;
			Node? next = null;

			foreach (Transition t in current.Candidates(inSym))
			{

				if (t.Input == inSym && t.Output == outSym && inSym != 0)
				{
					next = t.To;
					break;
				}
			}

			if (next == null)
			{
				next = new Node();
				current.Add(new Transition(inSym, outSym, next));
			}

			current = next;
		}

		return current;
	}

	// One path through the transducer: where it is, what it has output, whether it stepped through a lowercased character
	record PathState(Node Where, List<int> Output, bool Dirty);

	static List<PathState> EpsilonClosure(List<PathState> states)
	{
		var result = new List<PathState>(states);

		for (int i = 0; i < result.Count; i++)
		{

			foreach (Transition t in result[i].Where.Candidates(0))
			{

				if (t.Input != 0)
					continue;

				var output = new List<int>(result[i].Output);

				if (t.Output != 0)
					output.Add(t.Output);

				result.Add(new PathState(t.To, output, result[i].Dirty));
			}
		}

		return result;
	}

	// State::step_override(input, alt, ...): each path steps on the symbol itself, then on its lowercase alternative (making the path dirty)
	static List<PathState> Step(List<PathState> states, int symbol, int alt)
	{
		var next = new List<PathState>();

		foreach (PathState s in states)
		{
			Advance(s, symbol, s.Dirty, next);

			if (alt != symbol)
				Advance(s, alt, true, next);
		}

		return EpsilonClosure(next);
	}

	static void Advance(PathState s, int input, bool dirty, List<PathState> into)
	{

		foreach (Transition t in s.Where.Candidates(input))
		{

			if (t.Input != input)
				continue;

			var output = new List<int>(s.Output);

			if (t.Output != 0)
				output.Add(t.Output);

			into.Add(new PathState(t.To, output, dirty));
		}
	}

	// State::filterFinalsArray with -N1 -L1: the final paths' outputs, recased, best weight first, duplicates dropped, at most one kept
	List<string> Finals(List<PathState> states, bool uppercase, bool firstUpper)
	{
		var candidates = new List<(string Text, double Weight)>();

		foreach (PathState s in states)
		{

			if (!s.Where.IsFinal)
				continue;

			var sb = new StringBuilder();

			foreach (int sym in s.Output)
			{

				if (EscapedChars.Contains(sym))
					sb.Append('\\');

				Alphabet.Append(sb, sym, s.Dirty && uppercase);
			}

			if (s.Dirty && firstUpper && sb.Length > 0)
			{
				int loc = sb[0] == '~' ? 1 : 0;

				if (loc < sb.Length)
					sb[loc] = char.ToUpperInvariant(sb[loc]);
			}

			candidates.Add((sb.ToString(), s.Where.FinalWeight));
		}

		// std::sort on a handful of items is an insertion sort, so equal weights keep their order; OrderBy is stable too
		return candidates.OrderBy(c => c.Weight).Select(c => c.Text).Distinct().Take(1).ToList();
	}

	// FSTProcessor::bilingual() for one reading: the text between ^ and $ (or the next /), already split into symbols
	public string Translate(Reading reading)
	{
		var sb = new StringBuilder("^");

		if (reading.Mark == '*')
		{
			sb.Append('*').Append(reading.Content).Append("/*").Append(reading.Content).Append('$');
			return sb.ToString();
		}

		List<int> symbols = reading.Symbols;

		if (symbols.Count == 0)
			return "^$";

		bool firstUpper = Alphabet.IsUpper(symbols[0]);
		bool uppercase = firstUpper && symbols.Count > 1 && Alphabet.IsUpper(symbols[1]);
		var states = EpsilonClosure(new List<PathState> { new PathState(Root, new List<int>(), false) });

		if (reading.Mark == '#')
			states = Step(states, '#', '#');

		bool seenTags = false;
		int queueStart = 0;
		var result = new List<string>();

		for (int i = 0; i < symbols.Count; i++)
		{
			int sym = symbols[i];
			seenTags |= Alphabet.IsTag(sym);
			int alt = Alphabet.IsTag(sym) ? sym : Alphabet.ToLower(sym);
			states = Step(states, sym, alt);

			if (states.Any(s => s.Where.IsFinal))
			{
				queueStart = i;
				result = Finals(states, uppercase, firstUpper);
			}
		}

		// If there are no tags, only a complete match counts
		if (!seenTags && queueStart + 1 < symbols.Count)
			result.Clear();

		// The source as written back: escaped characters get their backslash again
		var source = new StringBuilder();
		int queuePos = 0;

		if (reading.Mark == '#')
		{
			source.Append('#');
			queuePos = 1;
		}

		for (int i = 0; i < symbols.Count; i++)
		{

			if (EscapedChars.Contains(symbols[i]) || (i == 0 && symbols[i] == '*'))
				source.Append('\\');

			Alphabet.Append(source, symbols[i]);

			if (i == queueStart)
				queuePos = source.Length;
		}

		sb.Append(source).Append('/');

		if (result.Count > 0)
		{
			string queue = source.ToString(queuePos, source.Length - queuePos);
			sb.Append(string.Join("/", result.Select(r => r + queue)));
		}
		else
		{
			sb.Append('@').Append(source);
		}

		sb.Append('$');

		return sb.ToString();
	}

	// FSTProcessor::bilingual(): blanks are copied, each lexical unit is translated
	public string Process(string input)
	{
		var reader = new LtStreamReader(input, Alphabet);
		var output = new StringBuilder();

		while (reader.Next())
		{
			output.Append(reader.Blank).Append(reader.WBlank);

			if (reader.Readings.Count > 0)
				output.Append(Translate(reader.Readings[0]));
		}

		return output.ToString();
	}
}
