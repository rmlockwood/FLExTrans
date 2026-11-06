// LtStreamReader.cs - FTApertium
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. lttoolbox's StreamReader for bilingual lookup.
//
// OVERVIEW (AI generated, then edited)
//
// lttoolbox 3.8.3's StreamReader::next() with the InputFile helpers it calls (readBlank, finishWBlank, readBlock): splits an Apertium stream into blanks and lexical units. A blank is everything
// up to the next ^, with backslash escapes and [superblanks] kept as written; a [[word-bound blank]] directly before a ^ is kept separately. A lexical unit is read up to $, as readings
// separated by /, each with an optional mark (* @ # = %) and its symbols: characters, with an escaped character as itself, and each <tag> as one symbol.
//
// CODE STRUCTURE
//
// Reading holds one reading of a unit. LtStreamReader.Next() reads a blank and the unit after it, with ReadBlank(), FinishWBlank() and ReadBlock().
//

using System.Text;

namespace FTtranslator.Apertium;

public class Reading
{
	public char Mark;
	public readonly StringBuilder ContentBuilder = new();
	public readonly List<int> Symbols = new();
	public string Content => ContentBuilder.ToString();
}

public class LtStreamReader
{
	readonly int[] text;
	int pos;
	readonly Alphabet alphabet;

	public string Blank = "";
	public string WBlank = "";
	public List<Reading> Readings = new();
	public bool AtEof;

	public LtStreamReader(string input, Alphabet alphabet)
	{
		text = input.EnumerateRunes().Select(r => r.Value).ToArray();
		this.alphabet = alphabet;
	}

	bool Eof => pos >= text.Length;
	int Get() => pos < text.Length ? text[pos++] : -1;
	int Peek() => pos < text.Length ? text[pos] : -1;
	void Unget() => pos--;

	static string S(int c) => c < 0 ? "" : char.ConvertFromUtf32(c);

	string ReadBlock(int start, int end)
	{
		var ret = new StringBuilder(S(start));
		int c = 0;

		while (c != end && !Eof)
		{
			c = Get();
			ret.Append(S(c));

			if (c == '\\')
				ret.Append(S(Get()));
		}

		return ret.ToString();
	}

	string FinishWBlank()
	{
		var ret = new StringBuilder("[[");

		while (!Eof)
		{
			int c = Get();
			ret.Append(S(c));

			if (c == '\\')
			{
				ret.Append(S(Get()));
			}
			else if (c == ']' && Peek() == ']')
			{
				ret.Append(S(Get()));
				break;
			}
		}

		return ret.ToString();
	}

	string ReadBlank()
	{
		var ret = new StringBuilder();

		while (!Eof)
		{
			int c = Get();

			if (c == '^')
			{
				Unget();
				break;
			}

			if (c == '[')
			{
				int c2 = Get();

				if (c2 == '[')
				{
					Unget();
					Unget();
					break;
				}

				if (c2 >= 0)
					Unget();

				ret.Append(ReadBlock(c, ']'));
			}
			else
			{
				ret.Append(S(c));

				if (c == '\\')
					ret.Append(S(Get()));
			}
		}

		return ret.ToString();
	}

	// One blank and the lexical unit after it; false once the stream is used up
	public bool Next()
	{
		Blank = "";
		WBlank = "";
		Readings = new List<Reading>();

		if (AtEof)
			return false;

		Blank = ReadBlank();
		int c = Get();

		if (c == '[')
		{
			Get();
			WBlank = FinishWBlank();

			if (Peek() != '^')
			{
				string temp = Blank + WBlank;
				Next();
				Blank = temp + Blank;
				return true;
			}

			c = Get();
		}

		if (c < 0)
		{
			AtEof = true;
			return true;
		}

		while (c != '$' && c >= 0)
		{
			var cur = new Reading();
			Readings.Add(cur);
			c = Peek();

			if (c == '*' || c == '@' || c == '#' || c == '=' || c == '%')
			{
				Get();
				cur.Mark = (char)c;
			}

			c = Get();

			while (c != '/' && c != '$' && c >= 0)
			{

				if (c == '<')
				{
					string tag = ReadBlock('<', '>');
					cur.ContentBuilder.Append(tag);
					cur.Symbols.Add(alphabet.Tag(tag));
				}
				else if (c == '{')
				{
					ReadBlock('{', '}');
				}
				else
				{
					cur.ContentBuilder.Append(S(c));

					if (c == '\\')
					{
						int c2 = Get();
						cur.Symbols.Add(c2);
						cur.ContentBuilder.Append(S(c2));
					}
					else
					{
						cur.Symbols.Add(c);
					}
				}

				c = Get();
			}
		}

		if (c < 0)
			AtEof = true;

		return true;
	}
}
