// ExtractSourceText.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/bundleextract.py in C#: a text's analyses plus a bundle's lexicon in, the Apertium source stream and Extract Source Text's messages out.
//
// OVERVIEW (AI generated, then edited)
//
// The offline translator's Extract Source Text step: it does what FLExTrans' Extract Source Text does on its usual (non-TreeTran) path - turn an analyzed text into the Apertium stream that the
// bilingual lookup and transfer read - from plain data instead of an open FLEx project: the lexicon from the bundle (Lexicon.cs) and the text dump (TextDump.cs) after Approve Guesses.
// ExtractText() is the entry point; it returns the stream, with \n line ends, and the warnings and errors getInterlinData() gives, with the same English text, as (level, message) pairs.
//
// HOW CLOSE THE PORT IS
//
// Line for line with fttranslator/bundleextract.py, which is itself a line-for-line port of InterlinData.getInterlinData() and TextClasses.py. The names are bundleextract.py's (in PascalCase), in
// the same order, so the three can be read side by side: getInterlinData() and its helpers became ExtractText() and the Walker methods; TextEntirety, TextParagraph, TextSentence and TextWord
// became Text, Paragraph, Sentence and Word, keeping only what the non-TreeTran path uses; the few Utils functions involved come first, with their regexes. It was checked against the Python's
// recorded output for every text of two work projects (FTT-Scratch and Mato-Uma) and gives byte-identical streams and identical message lists. compareGolden() isn't ported.
//
// TRAPS (kept on purpose, because changing them would change the output)
//
//  - Affixes added before a root go in the root's slot: AddPlainTextAffix() on a word with affixes but no entries uses index len(eList) - 1 = -1, Python's last item, which the next AddEntry()
//    then leaves in slot 0 while the root's own slot is the new one. PyIndex() gives Python's negative indexing.
//  - A compound reuses its first root's stem features (Word.GetStemFeatures()): the first root with a non-empty list fills the cache, and any later root with a feature structure, even an empty
//    one, gets that cache. Null (no structure) and empty (an empty one) differ for that reason.
//  - EscapeReservedApertChars() is applied again to punctuation that is already escaped (InitWithComplex() adds the first component's initPunc, escaped, as initial punctuation). Its lookbehind
//    stops most double escaping, but not all, and the output depends on it.
//  - The complex-form cache keeps the first types list that matched an entry, and is sorted in place (most components first) every time a sentence looks at it. Python's sort is stable even with
//    reverse=True, so equal lengths keep their order; OrderByDescending() is stable too, List.Sort() isn't and must not be used.
//  - A lemma's capitalization comes from the occurrence's baseline text (DoCapitalization()), using Python's isupper() and upper() (PyStr), not .NET's.
//  - Where the original would crash (a sense whose msa isn't a stem msa when its category is read) this gives UNK instead, as bundleextract.py does.
//  - The "new sentence" test compares seg with null at the start (seg is an index, and can be 0), and a Word with no entries has no entry handle (null here, 0 in Python): neither is ever a key
//    of the complex-form cache.
//  - Sentence.SubstituteDiscontiguousComplexForms() sets match to false once, before the loop over the complex forms, not once per form, as the original does.
//
// PYTHON'S REGEXES IN .NET
//
// The regexes are the Python ones, adjusted where .NET reads them differently: re.match() is anchored only at the start, so the split-compounds pattern gets \A; reAddOne is \d$ with re.ASCII, so
// it is [0-9]$ here (.NET's \d takes every Unicode digit); re.sub()'s \1 is $1 in .NET's replacement syntax, where a backslash is literal. $ means the same in both (the end, or before a final
// \n). re.split() and Regex.Split() both put the captured delimiters in the result and both give an empty first item for a match at the start. The sentence-punctuation class is built from
// the SentencePunctuation setting as is, in both: characters with a meaning inside [] (\ ] ^ -) mean the same in both, but .NET's class subtraction (-[...]) and characters outside the BMP
// (one code point in Python, two code units here) would not. No FLExTrans project uses either.
//
// CODE STRUCTURE
//
// ExtractSourceText is a static class holding everything, so the nested class names (Word, Text...) can't clash with the rest of FTOffline. The copied Utils pieces come first
// (EscapeReservedApertChars(), ContainsInvalidLemmaChars(), AddOne(), Underscores(), SplitCompounds(), DoCapitalization()); then Word, Sentence, Paragraph and Text; then Walker, which holds
// getInterlinData()'s state and its per-occurrence steps (SetFlagsAndSpaces(), CheckForNewSentOrPar(), HandlePunctuationOnlyParagraph(), ProcessPunctuation(), ProcessInvalidObjError(),
// ProcessWord()); then ExtractText(), the entry point, which walks the occurrences with Walker, then warns for unknown words and substitutes complex forms through Text, and writes the stream.
//

using System.Text;
using System.Text.RegularExpressions;

namespace FTtranslator.Offline;

public static class ExtractSourceText
{
	// Copied from FLExTrans Utils, so this file needs neither FieldWorks nor FLExTrans
	const string APERT_RESERVED = @"\[\]@/^${}<>*";
	const string INVALID_LEMMA_CHARS = @"([\^$><{}])";

	// INVALID_LEMMA_CHARS[3:-2]
	const string RAW_INVALID_LEMMA_CHARS = "^$><{}";

	static readonly Regex reApertReserved = new Regex(@"(?<!\\)([" + APERT_RESERVED + "])");
	static readonly Regex reApertBackslash = new Regex(@"(?<!\\)\\([^" + APERT_RESERVED + @"\\]|$)");
	static readonly Regex reInvalidLemmaChars = new Regex(INVALID_LEMMA_CHARS);

	// Python's \d$ with re.ASCII
	static readonly Regex reAddOne = new Regex("[0-9]$");
	static readonly Regex reDataStream = new Regex("(>[^$<])");

	// re.match(r'(.*?\^)(.*?)(\$.*)', s, re.DOTALL): re.match() is anchored at the start only
	static readonly Regex reSplitCompounds = new Regex(@"\A(.*?\^)(.*?)(\$.*)", RegexOptions.Singleline);

	// Copied from InterlinData and TextClasses
	const bool CHECK_DELIMITER = true;
	const string DELIMITER_STR = "{";
	const string WFI_ANALYSIS = "WfiAnalysis";
	const string WFI_GLOSS = "WfiGloss";
	const string WFI_WORD_FORM = "WfiWordform";
	const string ROOT_MISSING = "ROOT_MISSING";
	const string PART_MISSING = "PART_MISSING";
	const int MAX_SKIPPED_WORDS = 4;
	const string UNKNOWN_POS = "UNK";
	const string SENT_TAG = "sent";

	// Utils.escapeReservedApertChars(): escape the Apertium stream's reserved characters, and lone backslashes, unless already escaped
	static string EscapeReservedApertChars(string inStr)
	{
		inStr = reApertReserved.Replace(inStr, @"\$1");
		inStr = reApertBackslash.Replace(inStr, @"\\$1");

		return inStr;
	}

	static bool ContainsInvalidLemmaChars(string myStr)
	{
		return reInvalidLemmaChars.IsMatch(myStr);
	}

	// Utils.add_one(): a headword with no homograph number gets 1
	static string AddOne(string headWord)
	{

		if (!reAddOne.IsMatch(headWord))
		{
			return headWord + "1";
		}

		return headWord;
	}

	static string Underscores(string inStr)
	{
		return inStr.Replace(".", "_");
	}

	// Utils.split_compounds(): a word with several roots, ^a1.1<n>b1.1<n>$, becomes one lexical unit per root, ^a1.1<n>$^b1.1<n>$
	static string SplitCompounds(string outStr)
	{

		// Sentence punctuation units are left alone
		if (outStr.Contains("<sent>"))
		{
			return outStr;
		}

		Match match = reSplitCompounds.Match(outStr);
		string beforePunc;
		string middle;
		string afterPunc;

		if (match.Success)
		{
			beforePunc = match.Groups[1].Value;
			middle = match.Groups[2].Value;
			afterPunc = match.Groups[3].Value;
		}
		else
		{
			return outStr;
		}

		// Split where a > is followed by the start of the next lemma; the odd items are the two-character delimiters, which get $^ put in the middle. A delimiter's second character can be half
		// of a surrogate pair here where Python's is a whole code point, but the pieces are put back together in order, so the result is the same.
		string[] toks = reDataStream.Split(middle);

		if (toks.Length > 1)
		{
			var sb = new StringBuilder();

			for (int i = 0; i < toks.Length; i++)
			{
				string tok = toks[i];

				if ((i & 1) != 0)
				{
					tok = tok[0] + "$^" + tok[1];
				}

				sb.Append(tok);
			}

			middle = sb.ToString();
		}

		return beforePunc + middle + afterPunc;
	}

	// TextClasses.do_capitalization(): copy the model word's capitalization (all upper, or first letter upper) onto the word. [0] and [1:] are by code point, as in Python.
	static string DoCapitalization(string? wordToChange, string? modelWord)
	{

		if (!string.IsNullOrEmpty(wordToChange) && !string.IsNullOrEmpty(modelWord))
		{

			if (PyStr.IsUpper(modelWord))
			{
				return PyStr.Upper(wordToChange);
			}
			else if (PyStr.IsUpper(FirstCodePoint(modelWord)))
			{
				string first = FirstCodePoint(wordToChange);

				return PyStr.Upper(first) + wordToChange.Substring(first.Length);
			}
		}

		return wordToChange ?? "";
	}

	// s[0] in Python: the first code point, which is two UTF-16 code units outside the BMP
	static string FirstCodePoint(string s)
	{
		return char.IsHighSurrogate(s[0]) && s.Length > 1 && char.IsLowSurrogate(s[1]) ? s.Substring(0, 2) : s.Substring(0, 1);
	}

	// Python's list[i], where a negative index counts from the end
	static T PyIndex<T>(List<T> list, int i)
	{
		return list[i < 0 ? list.Count + i : i];
	}

	// One complex-form ref of the cache: the complex entry, its components and whether its type puts the inflection on the first element
	sealed record ComplexFormTuple(string CmplxEn, List<string> ComponentEList, bool InflectionOnFirstElement);

	// TextClasses.TextWord: one word (or sentence-punctuation unit) and the data its lexical unit is built from. Entries and senses are GUIDs into the Lexicon.
	sealed class Word
	{
		readonly Lexicon lexicon;
		public string InitPunc = "";
		public string FinalPunc = "";
		public string SurfaceForm = "";
		readonly List<string> lemmaList = new();
		readonly List<string> eList = new();
		readonly List<List<string>> affixLists = new();
		List<Word> componentList = new();
		readonly List<string?> senseList = new();
		readonly List<List<string>> inflFeatAbbrevsList = new();

		// Filled by the first root with stem features and then used for every root that has a feature structure. See GetStemFeatures().
		List<string> stemFeatAbbrList = new();

		public Word(Lexicon lexicon)
		{
			this.lexicon = lexicon;
		}

		public void AddAffixesFromList(List<string> strList)
		{
			affixLists[0].AddRange(strList);
		}

		public void AddEntry(string e)
		{
			eList.Add(e);
			affixLists.Add(new List<string>());
			inflFeatAbbrevsList.Add(new List<string>());
		}

		public void AddFinalPunc(string myStr)
		{
			FinalPunc += EscapeReservedApertChars(myStr);
		}

		public void AddInflFeatures(List<string> inflFeatAbbrevs)
		{
			inflFeatAbbrevsList[^1] = inflFeatAbbrevs;
		}

		public void AddInitialPunc(string myStr)
		{
			InitPunc += EscapeReservedApertChars(myStr);
		}

		public void AddLemma(string lemma)
		{
			lemmaList.Add(lemma);
		}

		public void AddPlainTextAffix(string myStr)
		{

			// Before any root the affix starts the first slot; after one it goes in the last root's slot (index -1, the last slot, when there are affixes but no entries yet)
			if (!IsInitialized())
			{
				affixLists.Add(new List<string> { myStr });
			}
			else
			{
				PyIndex(affixLists, eList.Count - 1).Add(myStr);
			}
		}

		public void AddSense(string? sense)
		{
			senseList.Add(sense);
		}

		public void BuildLemmaAndAdd(string? baseStr, int senseNum)
		{

			// The last entry added is the root the lemma is for
			string lem = DoCapitalization(lexicon.Headword(eList[^1]), baseStr);
			AddLemma(AddOne(lem) + "." + (senseNum + 1).ToString());
		}

		public List<string> GetAffixSymbols()
		{
			return affixLists[0];
		}

		public string GetDataStreamSymbols(int i)
		{
			var symbols = new List<string>();

			// Category first, except for <sent> units; then inflection class, stem features, irregular-form features and affixes. The order matters: GetStemFeatures() fills a cache.
			if (!IsSentPunctutationWord())
			{
				symbols = new List<string> { GetPOS(i) };
			}

			symbols.AddRange(GetInflClass(i));
			symbols.AddRange(GetStemFeatures(i));
			symbols.AddRange(GetInflFeatures(i));

			if (i < affixLists.Count)
			{
				symbols.AddRange(affixLists[i]);
			}

			return "<" + string.Join("><", symbols.Select(x => Underscores(x))) + ">";
		}

		// Python returns 0 when there are no entries; null never matches a cache key either
		public string? GetEntryHandle()
		{

			if (HasEntries())
			{
				return eList[0];
			}

			return null;
		}

		public string? GetFirstEntry()
		{

			if (HasEntries())
			{
				return eList[0];
			}

			return null;
		}

		public List<string> GetInflClass(int i)
		{

			// A class with an empty abbreviation still gives a (blank) tag, as in the original
			Lexicon.MsaRecord? msa = SenseMsa(i);

			if (msa?.InflClass != null)
			{
				return new List<string> { msa.InflClass };
			}

			return new List<string>();
		}

		public List<string> GetInflFeatures(int i)
		{

			if (i < inflFeatAbbrevsList.Count)
			{
				return new List<string>(inflFeatAbbrevsList[i]);
			}

			return new List<string>();
		}

		public string GetLemma(int i)
		{

			if (i < lemmaList.Count)
			{
				return lemmaList[i];
			}

			return "";
		}

		public string GetPOS(int i)
		{

			// A sense whose msa has no category (or isn't a stem msa, where the original would crash) gives UNK; a category with an empty abbreviation gives an empty tag
			string? pos = SenseMsa(i)?.Pos;

			if (pos != null)
			{
				return pos;
			}

			return UNKNOWN_POS;
		}

		public List<string> GetStemFeatures(int i)
		{

			// As the original: the first root with a non-empty list fills the cache, and any root with a feature structure (even an empty one) then gets the cache
			Lexicon.MsaRecord? msa = SenseMsa(i);

			if (msa?.StemFeatures == null)
			{
				return new List<string>();
			}

			if (stemFeatAbbrList.Count == 0)
			{
				stemFeatAbbrList = new List<string>(msa.StemFeatures);
			}

			return new List<string>(stemFeatAbbrList);
		}

		public bool HasEntries()
		{
			return eList.Count > 0;
		}

		public bool HasComponents()
		{
			return componentList.Count > 0;
		}

		public bool HasSenses()
		{
			return senseList.Count > 0;
		}

		// Make this word the complex form that replaces componentList. Affix tags come from the first or last component, by where the complex form's type puts the inflection.
		public void InitWithComplex(string cmplxE, List<Word> componentList, bool inflectionOnFirstElement)
		{
			AddEntry(cmplxE);
			this.componentList = componentList;
			SurfaceForm = string.Join(" ", componentList.Select(w => w.SurfaceForm));

			// Sense 1 of the complex entry, capitalized like the first component. senses[0] throws if the complex entry has none, as Python's IndexError would.
			BuildLemmaAndAdd(componentList[0].SurfaceForm, 0);
			AddSense(lexicon.Entries[cmplxE].Senses[0]);

			Word firstComponent = componentList[0];
			Word lastComponent = componentList[^1];
			List<string> affixList;

			if (inflectionOnFirstElement)
			{
				affixList = firstComponent.GetAffixSymbols();
			}
			else
			{
				affixList = lastComponent.GetAffixSymbols();
			}

			AddAffixesFromList(affixList);
			AddInitialPunc(firstComponent.InitPunc);
			AddFinalPunc(lastComponent.FinalPunc);
		}

		public bool IsInitialized()
		{

			if (!HasSenses() && affixLists.Count == 0)
			{
				return false;
			}

			return true;
		}

		public bool IsSentPunctutationWord()
		{

			if (affixLists.Count > 0 && affixLists[0].Count > 0)
			{

				if (affixLists[0][0] == SENT_TAG)
				{
					return true;
				}
			}

			return false;
		}

		public bool NotCompound()
		{
			return eList.Count <= 1;
		}

		public string OutputDataStream(bool escapeLemma = false)
		{
			return InitPunc + "^" + OutputDataForAllRoots(escapeLemma) + "$" + FinalPunc;
		}

		public bool PosMatchForMiddleItemInDiscontigousList(List<string> discontigPOSList)
		{
			return discontigPOSList.Contains(GetPOS(0));
		}

		public string Write()
		{
			return SplitCompounds(OutputDataStream(escapeLemma: true));
		}

		string OutputDataForAllRoots(bool escapeLemma)
		{

			if (IsSentPunctutationWord())
			{
				return EscapeReservedApertChars(GetLemma(0)) + GetDataStreamSymbols(0);
			}

			var retStr = new StringBuilder();

			for (int i = 0; i < lemmaList.Count; i++)
			{
				retStr.Append(escapeLemma ? EscapeReservedApertChars(GetLemma(i)) : GetLemma(i));
				retStr.Append(GetDataStreamSymbols(i));
			}

			return retStr.ToString();
		}

		// The msa record of the ith root's sense, or null (Python's {}) if there is no such sense
		Lexicon.MsaRecord? SenseMsa(int i)
		{

			if (i < senseList.Count && !string.IsNullOrEmpty(senseList[i]))
			{
				return lexicon.SenseMsa(senseList[i]!);
			}

			return null;
		}
	}

	// TextClasses.TextSentence: the words of one FLEx segment, and the complex-form substitution done on them
	sealed class Sentence
	{
		readonly List<(string Level, string Message)> messages;
		public List<Word> WordList = new();
		public List<string> FirstElemTypesList = new();

		public Sentence(List<(string Level, string Message)> messages)
		{
			this.messages = messages;
		}

		// Cache, for each single-root word's entry, the complex forms of a type in typesList that it is part of. An entry already cached (by an earlier types list) is not looked at again.
		public void FindComplexForms(Dictionary<string, List<ComplexFormTuple>> cmplxFormMap, List<string> typesList, Lexicon lexicon)
		{

			foreach (Word wrd in WordList)
			{
				string? handle = wrd.GetEntryHandle();

				if (wrd.HasEntries() && wrd.NotCompound() && !cmplxFormMap.ContainsKey(handle!))
				{
					var cmplxEntryTupList = new List<ComplexFormTuple>();

					// One item per complex-form ref, with its types; a ref matching several types is added once per type, as in the original
					foreach (Lexicon.ComplexFormRecord complexForm in lexicon.Entries[handle!].ComplexForms ?? new List<Lexicon.ComplexFormRecord>())
					{

						foreach (string typeName in complexForm.Types)
						{

							if (typesList.Contains(typeName))
							{
								bool inflectionOnFirstElement = FirstElemTypesList.Contains(typeName);
								cmplxEntryTupList.Add(new ComplexFormTuple(complexForm.Entry, complexForm.Components, inflectionOnFirstElement));
							}
						}
					}

					if (cmplxEntryTupList.Count > 0)
					{
						cmplxFormMap[handle!] = new List<ComplexFormTuple>(cmplxEntryTupList);
					}
				}
			}
		}

		public void ModifyList(int myIndex, int count, string complexEn, bool inflectionOnFirstElement, Lexicon lexicon)
		{
			var componentList = new List<Word>();

			for (int k = 0; k < count; k++)
			{
				componentList.Add(Pop(myIndex));
			}

			var newWord = new Word(lexicon);
			newWord.InitWithComplex(complexEn, componentList, inflectionOnFirstElement);
			WordList.Insert(myIndex, newWord);
		}

		public void ModifyDiscontiguousList(int myIndex, int skippedWordsCount, string complexEn, bool inflectionOnFirstElement, Lexicon lexicon)
		{

			// After the first pop everything moves up one, so the second component is at myIndex + skippedWordsCount
			var componentList = new List<Word>();
			componentList.Add(Pop(myIndex));
			componentList.Add(Pop(myIndex + skippedWordsCount));

			var newWord = new Word(lexicon);
			newWord.InitWithComplex(complexEn, componentList, inflectionOnFirstElement);
			WordList.Insert(myIndex + skippedWordsCount, newWord);
		}

		// list.pop(i)
		Word Pop(int index)
		{
			Word word = WordList[index];
			WordList.RemoveAt(index);

			return word;
		}

		// cmplxEnList.sort(key=lambda x: len(x[1]), reverse=True): most components first, in place. Python's sort is stable (reverse=True too), so equal lengths keep their order;
		// OrderByDescending() is stable as well, List.Sort() isn't.
		static void SortByComponentCount(List<ComplexFormTuple> cmplxEnList)
		{
			List<ComplexFormTuple> sorted = cmplxEnList.OrderByDescending(x => x.ComponentEList.Count).ToList();
			cmplxEnList.Clear();
			cmplxEnList.AddRange(sorted);
		}

		public void SubstituteComplexForms(Dictionary<string, List<ComplexFormTuple>> cmplxFormMap, Lexicon lexicon)
		{
			int myIndex = 0;

			// The last word can't start a match of two or more words
			while (myIndex < WordList.Count - 1)
			{
				Word wrd = WordList[myIndex];
				string? handle = wrd.GetEntryHandle();

				// The complex form that matched, if any. The original reads the loop variables after the loop; keeping the match here instead gives the same result.
				(int Count, string CmplxEn, bool InflectionOnFirstElement)? matched = null;

				if (handle != null && cmplxFormMap.ContainsKey(handle))
				{
					List<ComplexFormTuple> cmplxEnList = cmplxFormMap[handle];

					if (cmplxEnList.Count > 0)
					{

						// Most components first; see SortByComponentCount()
						SortByComponentCount(cmplxEnList);

						foreach (ComplexFormTuple tup in cmplxEnList)
						{
							bool match = false;
							int count = tup.ComponentEList.Count;

							if (count > 1 && myIndex + count - 1 < WordList.Count)
							{

								for (int j = 0; j < count; j++)
								{

									if (WordList[myIndex + j].GetFirstEntry() == tup.ComponentEList[j])
									{
										match = true;
									}
									else
									{
										match = false;
										break;
									}
								}

								if (match)
								{
									matched = (count, tup.CmplxEn, tup.InflectionOnFirstElement);
									break;
								}
							}
						}
					}

					if (matched != null)
					{
						ModifyList(myIndex, matched.Value.Count, matched.Value.CmplxEn, matched.Value.InflectionOnFirstElement, lexicon);
					}
				}

				myIndex += 1;
			}
		}

		public void SubstituteDiscontiguousComplexForms(Dictionary<string, List<ComplexFormTuple>> cmplxFormMap, List<string> discontigPOSList, Lexicon lexicon)
		{
			int myIndex = 0;

			while (myIndex < WordList.Count - 1)
			{
				int increment = 1;
				Word wrd = WordList[myIndex];
				string? handle = wrd.GetEntryHandle();

				if (handle != null && cmplxFormMap.ContainsKey(handle))
				{
					List<ComplexFormTuple> cmplxEnList = cmplxFormMap[handle];

					if (cmplxEnList.Count > 0)
					{
						SortByComponentCount(cmplxEnList);

						// Set once for all the complex forms, not per form, as in the original
						bool match = false;
						int skippedCount = 0;

						// The complex form that matched, if any, as in SubstituteComplexForms()
						(string CmplxEn, bool InflectionOnFirstElement)? matched = null;

						foreach (ComplexFormTuple tup in cmplxEnList)
						{

							// Only two-component complex forms can be discontiguous
							if (tup.ComponentEList.Count == 2 && WordList[myIndex].GetFirstEntry() == tup.ComponentEList[0])
							{
								int index = myIndex + 1;
								skippedCount = index - myIndex;

								// Look for the second component past up to MAX_SKIPPED_WORDS words of the allowed categories
								while (skippedCount <= MAX_SKIPPED_WORDS && index + 1 < WordList.Count)
								{

									if (!WordList[index].PosMatchForMiddleItemInDiscontigousList(discontigPOSList))
									{
										break;
									}

									if (WordList[index + 1].GetFirstEntry() == tup.ComponentEList[1])
									{
										match = true;
										break;
									}

									index += 1;
									skippedCount = index - myIndex;
								}

								if (match)
								{
									matched = (tup.CmplxEn, tup.InflectionOnFirstElement);
									break;
								}
							}
						}

						if (matched != null)
						{
							ModifyDiscontiguousList(myIndex, skippedCount, matched.Value.CmplxEn, matched.Value.InflectionOnFirstElement, lexicon);
							increment = skippedCount + 2 - 1;
						}
					}
				}

				myIndex += increment;
			}
		}

		public bool WarnForUnknownWords(Dictionary<string, int> unknownWordMap, bool noWarningProperNoun)
		{
			bool multipleUnknownWords = false;

			for (int myIndex = 0; myIndex < WordList.Count; myIndex++)
			{
				Word word = WordList[myIndex];

				// An uninitialized word is unknown; SFM markers are left alone
				if (word.IsInitialized() || (word.SurfaceForm.Length > 0 && word.SurfaceForm[0] == '\\'))
				{
					continue;
				}

				if (unknownWordMap.ContainsKey(word.SurfaceForm))
				{
					multipleUnknownWords = true;
				}

				// A capitalized word after the first is taken for a proper noun, if the setting says so (Python's isupper() on the first code point)
				else if (noWarningProperNoun && word.SurfaceForm.Length > 0 && PyStr.IsUpper(FirstCodePoint(word.SurfaceForm)) && myIndex > 0)
				{
					continue;
				}
				else
				{
					messages.Add(("warning", "No analysis found for the word: " + word.SurfaceForm + " Treating this as an unknown word."));
					unknownWordMap[word.SurfaceForm] = 1;
				}
			}

			return multipleUnknownWords;
		}

		public string Write()
		{
			return string.Concat(WordList.Select(word => word.Write()));
		}
	}

	// TextClasses.TextParagraph
	sealed class Paragraph
	{
		public List<Sentence> SentList = new();

		public string Write()
		{
			return string.Concat(SentList.Select(sent => sent.Write())) + "\n";
		}
	}

	// TextClasses.TextEntirety: the paragraphs of a text, and the complex-form processing done across them
	sealed class Text
	{
		public List<Paragraph> ParList = new();
		readonly Dictionary<string, List<ComplexFormTuple>> cmplxFormMap = new();

		public int GetSentCount()
		{
			return ParList.Sum(par => par.SentList.Count);
		}

		public void ProcessComplexForms(Lexicon lexicon)
		{

			// Both types lists fill one cache, paragraph by paragraph, the first-element list first; see Sentence.FindComplexForms()
			foreach (Paragraph par in ParList)
			{

				foreach (Sentence sent in par.SentList)
				{
					sent.FirstElemTypesList = lexicon.TypesInfl1stList;
				}

				foreach (List<string> typesList in new[] { lexicon.TypesInfl1stList, lexicon.TypesInfl2ndList })
				{

					foreach (Sentence sent in par.SentList)
					{
						sent.FindComplexForms(cmplxFormMap, typesList, lexicon);
					}
				}
			}

			foreach (Paragraph par in ParList)
			{

				foreach (Sentence sent in par.SentList)
				{
					sent.SubstituteComplexForms(cmplxFormMap, lexicon);
				}
			}
		}

		public void ProcessDiscontiguousComplexForms(Lexicon lexicon)
		{

			// The original only works when the discontiguous types are the first-element types (it then shares the cache); otherwise it stops with an AttributeError
			if (!lexicon.TypesInfl1stList.SequenceEqual(lexicon.DiscontigTypesList))
			{
				throw new NotImplementedException("Extract Source Text can't process discontiguous complex types that differ from the complex types with inflection on the first element.");
			}

			foreach (Paragraph par in ParList)
			{

				foreach (Sentence sent in par.SentList)
				{
					sent.SubstituteDiscontiguousComplexForms(cmplxFormMap, lexicon.DiscontigPOSList, lexicon);
				}
			}
		}

		public bool WarnForUnknownWords(bool noWarningProperNoun)
		{
			var unknownWordMap = new Dictionary<string, int>();
			bool multipleUnknownWords = false;

			foreach (Paragraph par in ParList)
			{

				foreach (Sentence sent in par.SentList)
				{

					if (sent.WarnForUnknownWords(unknownWordMap, noWarningProperNoun))
					{
						multipleUnknownWords = true;
					}
				}
			}

			return multipleUnknownWords;
		}

		public string Write()
		{
			return string.Concat(ParList.Select(par => par.Write()));
		}
	}

	// getInterlinData()'s state (InterlinData.interlinInfo) and the steps it takes for each occurrence
	sealed class Walker
	{
		readonly Lexicon lexicon;
		readonly List<(string Level, string Message)> messages;
		public Word? MyWord;
		Sentence? mySent;
		Paragraph myPar = new();
		public Text MyText = new();
		bool isNewSentence;
		bool isNewParagraph;
		public bool InMultiLinePuncBlock;
		public string SavedPrePunc = "";
		string spacesStr = "";
		int numSpaces;

		public Walker(Lexicon lexicon, List<(string Level, string Message)> messages)
		{
			this.lexicon = lexicon;
			this.messages = messages;

			// The first paragraph is there from the start
			MyText.ParList.Add(myPar);
		}

		public void SetFlagsAndSpaces(Occurrence occurrence, int prevEndOffset, int? currSeg)
		{

			// The gap since the last occurrence becomes the next word's leading spaces (' ' * a negative number is ''); a negative gap means a new paragraph (unless the current one is still empty)
			numSpaces = occurrence.Beg - prevEndOffset;
			spacesStr = numSpaces > 0 ? new string(' ', numSpaces) : "";

			if (numSpaces < 0 && myPar.SentList.Count > 0)
			{
				isNewParagraph = true;
			}

			if (occurrence.Seg != currSeg)
			{
				isNewSentence = true;
			}
		}

		public void CheckForNewSentOrPar()
		{

			if (isNewSentence)
			{
				mySent = new Sentence(messages);
				isNewSentence = false;

				if (isNewParagraph)
				{
					myPar = new Paragraph();
					MyText.ParList.Add(myPar);
					isNewParagraph = false;
				}

				myPar.SentList.Add(mySent);
			}

			// Both are set on the first occurrence, which is always a new sentence
			mySent!.WordList.Add(MyWord!);
			MyWord!.AddInitialPunc(spacesStr);
		}

		public void HandlePunctuationOnlyParagraph(Word? prevWord)
		{

			// A new paragraph holding only punctuation: its punctuation goes on the previous word, or onto the saved punctuation after a newline
			if (numSpaces < 0)
			{

				if (prevWord != null && prevWord.FinalPunc.Length == 0 && !InMultiLinePuncBlock)
				{
					prevWord.AddFinalPunc(SavedPrePunc);
					SavedPrePunc = "";
				}
				else
				{
					SavedPrePunc += "\n";
				}

				// Keep the first paragraph from being empty
				if (MyText.ParList.Count == 1 && MyText.GetSentCount() == 0)
				{
					isNewParagraph = false;
				}
			}
		}

		public void ProcessPunctuation(string textPunct, Regex reSplitPuncObj)
		{

			// Odd items of the split are runs of sentence punctuation, even items the rest
			string[] puncList = reSplitPuncObj.Split(textPunct);

			for (int i = 0; i < puncList.Length; i++)
			{
				string currPunc = puncList[i];

				if (currPunc == "")
				{
					continue;
				}

				// Non-sentence punctuation, or sentence punctuation in the middle of a punctuation section (e.g. \xo 27.2-8)
				if (i % 2 == 0 || (i % 2 == 1 && MyWord != null && (MyWord.FinalPunc.Length > 0 || SavedPrePunc.Length > 0)))
				{

					if (MyWord != null && !MyWord.IsSentPunctutationWord() && !isNewSentence && (CHECK_DELIMITER && !(currPunc == DELIMITER_STR)))
					{
						MyWord.AddFinalPunc(spacesStr + currPunc);
						SavedPrePunc = "";
					}
					else if (numSpaces < 0)
					{

						if (SavedPrePunc.Length > 0 && MyWord != null && MyWord.FinalPunc.Length == 0 && !InMultiLinePuncBlock)
						{
							MyWord.AddFinalPunc(SavedPrePunc);
							SavedPrePunc = spacesStr + currPunc;
						}
						else if (SavedPrePunc.Length == 0)
						{
							SavedPrePunc += spacesStr + currPunc;
							InMultiLinePuncBlock = true;
						}
						else
						{
							SavedPrePunc += "\n" + spacesStr + currPunc;
						}
					}
					else
					{
						SavedPrePunc += spacesStr + currPunc;
					}
				}

				// Sentence punctuation becomes its own unit, e.g. ^.<sent>$
				else
				{
					MyWord = new Word(lexicon);
					MyWord.AddLemma(currPunc);
					MyWord.SurfaceForm = currPunc;
					MyWord.AddPlainTextAffix(SENT_TAG);

					if (SavedPrePunc.Length > 0)
					{
						MyWord.AddInitialPunc(SavedPrePunc);
						SavedPrePunc = "";
					}

					CheckForNewSentOrPar();
				}

				// The spaces are used up by the first item
				spacesStr = "";
			}
		}

		public void ProcessInvalidObjError(Word word, string? wordform, string msg)
		{

			// Part of the word isn't tied to an entry and sense: fall back to the wordform for the lemma, or mark the gap with a bogus affix
			if (word.GetLemma(0) == "" && wordform != null)
			{
				word.AddLemma(wordform);
			}
			else
			{
				word.AddPlainTextAffix(PART_MISSING);
			}

			messages.Add(("warning", msg + word.SurfaceForm));
		}

		// The word part of getInterlinData()'s loop, after the word is made and placed. Returns false if an invalid character means the whole text stops here.
		public bool ProcessWord(Occurrence occurrence)
		{
			Word word = MyWord!;

			// A word with no analysis has its surface form as its lemma
			if (occurrence.Kind == WFI_WORD_FORM)
			{
				word.AddLemma(occurrence.Surface ?? "");
				return true;
			}

			if (occurrence.Kind != WFI_ANALYSIS && occurrence.Kind != WFI_GLOSS)
			{
				return true;
			}

			// Python would stop with a TypeError on an analysis with no bundles list; there are none
			foreach (MorphBundle morphBundle in occurrence.Bundles ?? new List<MorphBundle>())
			{

				if (string.IsNullOrEmpty(morphBundle.Sense))
				{
					ProcessInvalidObjError(word, occurrence.Wordform, "No sense found for some part of the source word: ");
					break;
				}

				if (!(!string.IsNullOrEmpty(morphBundle.Msa) && !string.IsNullOrEmpty(morphBundle.MorphEntry)))
				{
					ProcessInvalidObjError(word, occurrence.Wordform, "No morphosyntactic analysis found for some part of the source word: ");
					break;
				}

				// Variants lead to the entry that has the sense, picking up an irregularly inflected form's features on the way
				(string tempEntry, List<string> inflFeatAbbrevs) = lexicon.Resolve(morphBundle.MorphEntry!);
				Lexicon.MsaRecord bundleMsa = lexicon.Msas[morphBundle.Msa!];

				// An affix or clitic (but not an enclitic standing alone, which is treated as a root)
				if (!bundleMsa.Stem || (lexicon.IsClitic(tempEntry) && !(lexicon.IsEnclitic(tempEntry) && !word.HasEntries())))
				{

					// A null gloss would stop Python with a TypeError in containsInvalidLemmaChars(); bundle.py writes "" for none in practice
					string gloss = lexicon.Senses[morphBundle.Sense].Gloss ?? "";

					if (ContainsInvalidLemmaChars(gloss))
					{
						messages.Add(("error", $"Invalid characters in the affix: {gloss}. The following characters are not allowed: {RAW_INVALID_LEMMA_CHARS}"));
						return false;
					}

					word.AddPlainTextAffix(gloss);
				}

				// A stem or stand-alone enclitic
				else
				{

					if (bundleMsa.Pos == null)
					{
						messages.Add(("warning", "No grammatical category found for the source word: " + word.SurfaceForm));
						break;
					}

					if (ContainsInvalidLemmaChars(lexicon.Headword(tempEntry)))
					{
						messages.Add(("error", $"Invalid characters in the affix: {lexicon.Headword(tempEntry)}. The following characters are not allowed: {RAW_INVALID_LEMMA_CHARS}"));
						return false;
					}

					word.AddEntry(tempEntry);
					word.AddInflFeatures(inflFeatAbbrevs);

					// The lemma's sense number is the bundle sense's place among the resolved entry's top-level senses
					List<string> entrySenses = lexicon.Entries[tempEntry].Senses;

					if (entrySenses.Contains(morphBundle.Sense))
					{
						word.AddSense(morphBundle.Sense);
						word.BuildLemmaAndAdd(occurrence.Baseline, entrySenses.IndexOf(morphBundle.Sense));
					}
					else
					{
						word.AddSense(null);
						messages.Add(("warning", "Couldn't find the sense for source headword: " + lexicon.Headword(tempEntry)));
					}
				}
			}

			// No root after all the bundles
			if (word.GetLemma(0) == "")
			{

				if (occurrence.Wordform != null)
				{
					word.AddLemma(occurrence.Wordform);
				}
				else
				{
					word.AddPlainTextAffix(ROOT_MISSING);
				}

				messages.Add(("warning", "No root or stem found for source word: " + word.SurfaceForm));
			}

			return true;
		}
	}

	// Extract Source Text for one text (the text dump after Approve Guesses) and a Lexicon: returns the Apertium stream, with \n line ends, and the messages as (level, text) pairs
	public static (string Stream, List<(string Level, string Message)> Messages) ExtractText(TextDump textDump, Lexicon lexicon)
	{
		var messages = new List<(string Level, string Message)>();
		var walker = new Walker(lexicon, messages);
		int prevEndOffset = 0;
		int? currSeg = null;
		List<Occurrence> occurrences = textDump.Occurrences;

		if (occurrences.Count == 0)
		{
			messages.Add(("warning", "No analyses found."));
		}

		// Sentence punctuation runs are split out, so sentence-final and other punctuation can be told apart. The class is built from the setting as is, as the Python does.
		var reSplitPuncObj = new Regex("([" + lexicon.SentPunct + "]+)");

		foreach (Occurrence occurrence in occurrences)
		{
			walker.SetFlagsAndSpaces(occurrence, prevEndOffset, currSeg);
			prevEndOffset = occurrence.End;
			currSeg = occurrence.Seg;

			// "punct" in occurrence
			if (occurrence.IsPunct)
			{
				walker.ProcessPunctuation(occurrence.Punct!, reSplitPuncObj);
				continue;
			}

			Word? prevWord = walker.MyWord;
			walker.MyWord = new Word(lexicon);

			if (walker.SavedPrePunc.Length > 0)
			{
				walker.HandlePunctuationOnlyParagraph(prevWord);
				walker.MyWord.AddInitialPunc(walker.SavedPrePunc);
				walker.SavedPrePunc = "";
			}

			walker.InMultiLinePuncBlock = false;
			walker.CheckForNewSentOrPar();
			walker.MyWord.SurfaceForm = occurrence.Surface ?? "";

			// An invalid character stops the whole text, as in the original, which returns the text as it stands
			if (!walker.ProcessWord(occurrence))
			{
				return (walker.MyText.Write(), messages);
			}
		}

		// Punctuation left over at the end of the text, in its own paragraph. Python stops with an AttributeError when the text has no word at all; this throws likewise.
		if (walker.SavedPrePunc.Length > 0)
		{
			walker.MyWord!.AddFinalPunc("\n" + walker.SavedPrePunc);
		}

		if (walker.MyText.WarnForUnknownWords(lexicon.NoWarningProperNoun))
		{
			messages.Add(("warning", "One or more unknown words occurred multiple times."));
		}

		walker.MyText.ProcessComplexForms(lexicon);

		if (lexicon.DiscontigTypesList.Count > 0 && lexicon.DiscontigPOSList.Count > 0 && (lexicon.TypesInfl1stList.Count > 0 || lexicon.TypesInfl2ndList.Count > 0))
		{
			walker.MyText.ProcessDiscontiguousComplexForms(lexicon);
		}

		return (walker.MyText.Write(), messages);
	}
}
