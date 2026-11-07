// Synthesis.cs - FTOffline
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. fttranslator/synthesis.py in C#: the target Apertium stream in, the HermitCrab-synthesized text out.
//
// OVERVIEW (AI generated, then edited)
//
// The last piece of the offline translator's runtime before the Text Out rules, ported from fttranslator/synthesis.py, which is itself a line-by-line port of FLExTrans' desktop code. On the
// desktop, after Run Apertium, Convert Text to Synthesizer Format (ConvertTextToSTAMPformat.py) turns the transfer results into the HermitCrab master file, breaking target complex forms into their
// components and swapping in irregularly inflected variants, and Synthesize Text (DoHermitCrabSynthesis.py) writes the parses file from it, runs HCSynthByGloss on it and puts the surface forms
// back into the transfer results. This file does the same from a bundle's synthesis folder: the target affix list, ConversionData's cache of the target complex forms and variants, and the target
// HermitCrab.config.
//
// Only synthesis.py's DLL path is ported. The Python can run HCSynthByGloss as a program (--hcsynth) or through HCSynthByGlossDll loaded with pythonnet; here the HCSynthByGlossDll class is compiled
// into the same assembly (see FTOffline.csproj), so the Synthesizer makes one object, loads the HermitCrab config into it once, and for each text only sets the gloss file and calls Process().
//
// HOW CLOSE THE PORT IS
//
// Line for line. Function names follow the Python's (in PascalCase) and come in the same order, so the two files can be read side by side, and the odd parts are kept because changing them would
// change the output (see TRAPS). The error lists keep FLExTrans' (message, 0/1/2) convention inside, with the same English text, and are turned into (level, message) pairs only at the end, in
// Synthesizer.Synthesize(). Against the Python's recorded runs (FTT-Scratch and Mato-Uma texts) every stage is identical: the master file, the parses file, the surface forms file, the synthesized
// text and the messages, apart from the work folder's name in one message and the order HCSynthByGloss gives the forms of an ambiguous word in (see TRAPS).
//
// PYTHON'S STR AND RE IN .NET
//
// Where the Python calls a str method whose .NET look-alike differs, this file calls PyStr's (upper(), lower(), capitalize(), title(), isupper(), strip(), split()); istitle() is ported here as
// IsTitle(). The regular expressions read the same in .NET's Regex as in Python's re with these adjustments:
//  - \d under re.A (ASCII) is written [0-9]; .NET's \d would take any Unicode digit.
//  - Replacements are MatchEvaluators returning the groups, never .NET's "$1" syntax, so a $ in the text can't be read as a group reference.
//  - produceSynthesisFile() passes the surface forms to re.sub() as the replacement, so Python reads backslashes in them (\\ is one backslash, \n a newline, \] stays as it is, \q is an error).
//    ExpandPyReplacement() does what Python's template parser does with them, and the escaped lexical unit is then replaced literally, which is what re.escape() plus re.sub() amounts to.
//  - re.split() with a group keeps the group's text between the pieces; PySplitWithGroup() does it from the matches rather than relying on Regex.Split.
//  - getHCparseStr() builds a pattern from a circumfix gloss without escaping it, as the original does; it is compiled as a .NET pattern, which reads ordinary glosses (letters, digits, dots)
//    the same.
//  - \s is left as .NET's: in the two patterns that use it a difference (\x1c-\x1f) could only change what split() then throws away.
//
// FILES
//
// The transfer results come in as a string and the synthesized text goes out as one; the master, parses and surface forms files are real files in the Synthesizer's work folder, with the
// desktop's names, because HCSynthByGlossDll reads and writes files. Python opens them in text mode, so the port does the same by hand: WritePyText() writes each \n as the platform's newline
// (\r\n on Windows, as FLExTrans' own files have), and ReadPyLines() reads with universal newlines (\r\n and \r become \n) and splits after each \n, as readlines() and iterating a file do. utf-8 keeps
// a byte order mark as a \ufeff character, utf-8-sig (the surface forms file, which HCSynthByGlossDll writes with one) drops it. Files are written without a byte order mark.
//
// TRAPS (carried over from synthesis.py)
//
//  - In HermitCrab mode WriteComponents() writes the components' parses itself and never calls WriteNonComplex(), so a component of a complex form doesn't get the variant substitution.
//  - The master file holds each distinct lexical unit once, and ProduceSynthesisFile() replaces every occurrence with one global substitution, in master file order, so an earlier replacement can
//    change the text a later lexical unit is looked for in. That is kept.
//  - CreateHermitCrabParsesFile() means to write @ words (unknown to the target lexicon) as blank lines and leave them out of luInfoList, but it tests the parse's second character, HCparseStr[1],
//    and the @ is the first. So @ words do go to HCSynthByGloss and come back as failures, %0%^@word<UNK>$%, on the desktop and here. The test is kept as it is (by code point, as Python indexes).
//  - ProcessComplexForm() sets the capitalization of the cached component objects themselves, and those live in ConversionData for the Synthesizer's life, so a capitalized complex form in one
//    text can change how the next text's uninflected component is capitalized. The Python shares the objects the same way; C# classes being references, the port keeps that.
//  - ChangeToVariant() deletes the matched tags from the prefix list at the tag position i even when the match was among the suffixes; Python's slice deletion clamps, so nothing goes. DelSlice()
//    clamps the same way.
//  - Sorting (the variant features) compares by code point, as Python does, not by UTF-16 unit.
//  - HCSynthByGloss lists the forms of an ambiguous word (%2%a%b%) in a different order from run to run, so a comparison with the desktop or the Python must treat them as a set.
//  - The language code passed to HCSynthByGloss is the one FLExTrans' interface uses (the manifest's interfaceLanguage); it chooses the language of HC's messages, which a failed word carries. The
//    DLL ignores its LocaleCode property, so SynthesizeWithHermitCrab() sets the UI culture itself before each Process(), as the Python DLL branch does. (Under .NET's invariant globalization mode
//    CultureInfo.GetCultureInfo() would refuse most codes; FTOffline's host must not turn that mode on.)
//  - GetCapitalLemmas() is called once, when the Synthesizer is made, rather than for each text as on the desktop; the config doesn't change between texts, so the map is the same. It reads the
//    config as Python's ElementTree does: the DOCTYPE's DTD is ignored, whitespace is kept, and an element's text is the character data before its first child.
//  - When ConvertIt() stops on an error the master file isn't rewritten, so the previous text's master file stays in the work folder, as with the Python.
//  - One HCSynthByGlossDll object writes one output file and must not be used by two threads at once; a Synthesizer handles one text at a time.
//
// CODE STRUCTURE
//
// Synthesis (internal, static) holds the Python module: the copied Utils pieces first (CapitalizeString(), UnescapeReservedApertChars()), then ANAInfo and ConversionData (cache loading only).
// The Convert Text to Synthesizer Format functions follow in the original's order: ChangeToVariant(), WriteNonComplex(), WriteComponents(), ProcessComplexForm(), GetContextWords(), ConvertIt(),
// CalculatePrePostPunctuation(), ProcessLUparseError(), ProcessLU() and ConvertToHermitCrab(). Then the DoHermitCrabSynthesis functions: ProduceSynthesisFile(), CreateHermitCrabParsesFile(),
// Capitalize(), ExtractRootAndFirstTag(), FixUpText(), GetCapitalLemmas() and SynthesizeWithHermitCrab(), and LoadHCSynthDll(), which makes the DLL object. The Python str and file helpers come
// last (WritePyText(), ReadPyLines(), IsTitle(), CompareCodePoints(), DelSlice(), PySplitWithGroup(), ExpandPyReplacement()). Synthesizer, public and at the end of the file, holds a bundle's
// synthesis data and the DLL object; its Synthesize() calls ConvertToHermitCrab() and then SynthesizeWithHermitCrab().
//

using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Xml;
using System.Xml.Linq;

using SIL.HCSynthByGloss;

namespace FTtranslator.Offline;

// An error list entry: FLExTrans' (message, code) pair, the code 0 info, 1 warning, 2 error
using ErrorList = List<(string Message, int Code)>;

internal static class Synthesis
{
	// Copied from FLExTrans Utils
	public const string CIRCUMFIX_TAG_A = "_cfx_part_a";
	public const string CIRCUMFIX_TAG_B = "_cfx_part_b";

	// Utils' APERT_RESERVED, \[\]@/^${}<>*, in its unescaping pattern: a backslash and then one of those or a backslash
	static readonly Regex reApertReservedEscaped = new(@"\\([\[\]@/^${}<>*\\])");

	// Copied from ConvertTextToSTAMPformat
	public const string COMPLEX_FORMS = "COMPLEX FORMS";
	public const string IRR_INFL_VARIANTS = "IRREGULARLY INFLECTED VARIANT FORMS";
	public const string VARIANT_STR = "_variant_";

	// The FlexTrans.config settings the manifest carries (ReadConfig's names)
	public const string SENTENCE_PUNCTUATION = "SentencePunctuation";
	public const string TARGET_FORMS_INFLECTION_1ST = "TargetComplexFormsWithInflectionOn1stElement";
	public const string TARGET_FORMS_INFLECTION_2ND = "TargetComplexFormsWithInflectionOn2ndElement";
	public const string CLEANUP_UNKNOWN_WORDS = "CleanUpUnknownTargetWords";

	// The work folder's files, named as in the desktop's Build folder
	public const string MASTER_FILE = "target_words-HC.txt";
	public const string PARSES_FILE = "target_words-parses.txt";
	public const string SURFACE_FORMS_FILE = "target_words-surface.txt";

	// synthexport.py's defaults for the bundle's synthesis folder
	public const string SYNTHESIS_DIR = "synthesis";
	public const string AFFIX_GLOSS_FILE = "target_affix_glosses.txt";
	public const string CONVERSION_CACHE_FILE = "conversion_to_STAMP_cache2.txt";
	public const string HERMIT_CRAB_CONFIG_FILE = "HermitCrab.config";

	// FLExTrans' error list codes, as the level names bundleextract.py uses
	public static readonly Dictionary<int, string> LEVEL_NAMES = new() { { 0, "info" }, { 1, "warning" }, { 2, "error" } };

	// The regexes of ANAInfo, convertIt(), produceSynthesisFile(), extractRootAndFirstTag() and fixUpText(), compiled once. [0-9] stands for \d under re.A.
	static readonly Regex rePrefixes = new(@"(.*)\s*<");
	static readonly Regex reRoot = new(@"< .+ (.+) >");
	static readonly Regex reRootPOS = new(@"< (.+) .+ >");
	static readonly Regex reSuffixes = new(@">\s*(.*)");
	static readonly Regex rePreDotRoot = new(@"< .+ (.+)\.[0-9]+ >");
	static readonly Regex reSenseNum = new(@"< .+ .+\.([0-9]+) >");
	static readonly Regex reSentLU = new(@"\^([^^]+?)<sent>\$");
	static readonly Regex reLexicalUnit = new(@"\^(.+?)\$");
	static readonly Regex reSentLUAfterSynthesis = new(@"([^%]|^|\$%)\^(.+?)<sent>\$");
	static readonly Regex reTag = new(@"<([^>]+)>");
	static readonly Regex reSenseNumbers = new(@"[0-9]+\.[0-9]+");
	static readonly Regex reSymbol = new(@"<.*?>");
	static readonly Regex reFailedWord = new(@"%0%\^{0,1}(.*?)\${0,1}%");

	// Utils.capitalizeString(): 2 is all upper case, 1 the first letter, 3 title case
	public static string CapitalizeString(string inStr, string capitalizeCode)
	{

		if (capitalizeCode == "2")
		{
			return PyStr.Upper(inStr);
		}

		else if (capitalizeCode == "1")
		{
			return PyStr.Capitalize(inStr);
		}

		else if (capitalizeCode == "3")
		{
			return PyStr.Title(inStr);
		}

		return inStr;
	}

	public static string UnescapeReservedApertChars(string inStr)
	{
		return reApertReservedEscaped.Replace(inStr, m => m.Groups[1].Value);
	}

	// One record of the ANA file: the analysis is kept as a string, 'pfx1 pfx2 < pos root > sfx1 sfx2', and the parts are pulled back out of it with regular expressions. Only the parts the
	// HermitCrab path uses are ported. The fields start out null, as the Python's attributes start out unset, when no root is given; every caller then sets the analysis.
	public sealed class ANAInfo
	{
		string Analysis = null!;
		string Capitalization = null!;
		string BeforePunc = "";
		string AfterPunc = "";
		string _originalLexicalUnitString = "";

		public ANAInfo()
		{
			SetBeforePunc("");
			SetAfterPunc("");
		}

		public ANAInfo(List<string> pfxList, List<string> sfxList, string pos, string root, List<string> infxList)
		{

			// If root is given, initialize with all the stuff (Python's "if root:", so an empty root counts as not given)
			if (root.Length > 0)
			{
				List<string> newList;

				// Treat the infixes as additional prefixes. (I believe we could put them either before or after the root)
				if (infxList.Count > 0)
				{
					newList = pfxList.Concat(infxList).ToList();
				}
				else
				{
					newList = pfxList;
				}

				SetAnalysisByPart(newList, pos, root, sfxList);
			}

			SetBeforePunc("");
			SetAfterPunc("");
		}

		static string AddUnderscores(string myStr)
		{
			return myStr.Replace(" ", "_");
		}

		static string CalcCase(string word)
		{

			if (PyStr.IsUpper(word))
			{
				return "2";
			}

			else if (word.Contains(' ') && IsTitle(word))
			{
				return "3";
			}

			// word[0] is the first code point
			else if (PyStr.IsUpper(char.ConvertFromUtf32(char.ConvertToUtf32(word, 0))))
			{
				return "1";
			}
			else
			{
				return "";
			}
		}

		string CapitalizeString(string myStr)
		{

			if (GetCapitalization() == "2")
			{
				return PyStr.Upper(myStr);
			}

			else if (GetCapitalization() == "1")
			{
				return PyStr.Capitalize(myStr);
			}

			else if (GetCapitalization() == "3")
			{
				return PyStr.Title(myStr);
			}
			else
			{
				return myStr;
			}
		}

		public string GetAfterPunc()
		{
			return AfterPunc;
		}

		public string GetAnalysis()
		{
			return Analysis;
		}

		// The regexes are the original's; the analysis always has the '< pos root >' part, so the searches can't fail
		public List<string> GetAnalysisPrefixes()  // returns [] if no prefix
		{
			return PyStr.Split(rePrefixes.Match(Analysis).Groups[1].Value);
		}

		public string GetAnalysisRoot()
		{
			return reRoot.Match(Analysis).Groups[1].Value;
		}

		// Apply the capitalization code algoritm to possibly capitalize the root string.
		public string GetCapitalizedAnalysisRoot()
		{
			return CapitalizeString(reRoot.Match(Analysis).Groups[1].Value);
		}

		public string GetAnalysisRootPOS()
		{
			return reRootPOS.Match(Analysis).Groups[1].Value;
		}

		public List<string> GetAnalysisSuffixes()
		{
			return PyStr.Split(reSuffixes.Match(Analysis).Groups[1].Value);
		}

		public string GetBeforePunc()
		{
			return BeforePunc;
		}

		public string GetCapitalization()
		{
			return Capitalization;
		}

		// The parse in HermitCrab order, <pfx1>...root<pos><sfx1>..., as the master file holds it
		public string GetHCparseStr()
		{
			string pfxs = string.Join("><", GetAnalysisPrefixes());

			if (pfxs.Length > 0)
			{

				// Remove circumfix extra stuff.
				pfxs = pfxs.Replace(CIRCUMFIX_TAG_A, "");

				// Turn underscores to dots
				pfxs = pfxs.Replace("_", ".");
				pfxs = "<" + pfxs + ">";
			}

			string sfxs = string.Join("><", GetAnalysisSuffixes());

			if (sfxs.Length > 0)
			{
				sfxs = "<" + sfxs + ">";

				// Remove the circumfix suffix entirely
				if (sfxs.Contains(CIRCUMFIX_TAG_B, StringComparison.Ordinal))
				{

					// find the end of the gloss
					int endGloss = sfxs.IndexOf(CIRCUMFIX_TAG_B, StringComparison.Ordinal);

					// find the beg of the gloss (rfind('<', 0, endGloss)+1; sfxs starts with '<', so endGloss is past it)
					int begGloss = sfxs.LastIndexOf('<', endGloss - 1) + 1;

					// pull out the gloss string
					string gloss = sfxs[begGloss..endGloss];

					// replace gloss string plus the tag (in angle-brackets) with nothing. The gloss goes into the pattern unescaped, as in the original.
					sfxs = Regex.Replace(sfxs, "<" + gloss + CIRCUMFIX_TAG_B + ">", m => "");
				}

				sfxs = sfxs.Replace("_", ".");
			}

			// roots need to have underscores converted to spaces
			string retStr = GetAnalysisRoot().Replace("_", " ");

			string pos = GetAnalysisRootPOS();

			// if we have a variant, append the 'POS' to the lemma
			if (pos == VARIANT_STR)
			{
				retStr += pos;
			}

			// add the POS
			retStr += "<" + pos + ">";

			retStr = pfxs + retStr + sfxs;
			return retStr;
		}

		public string GetOriginalLexicalUnitString()
		{
			return "^" + _originalLexicalUnitString + "$";
		}

		public string? GetPreDotRoot()  // in other words the headword
		{
			Match g = rePreDotRoot.Match(Analysis);

			if (g.Success)
			{
				string ret = RemoveUnderscores(g.Groups[1].Value);
				return ret;
			}

			return null;
		}

		// Only called for a root that GetPreDotRoot() found, so it has a sense number
		public string GetSenseNum()
		{
			return reSenseNum.Match(Analysis).Groups[1].Value;
		}

		static string RemoveUnderscores(string myStr)
		{
			return myStr.Replace("_", " ");
		}

		static string RemovePeriods(string myStr)
		{
			return myStr.Replace(".", "");
		}

		public void SetCapitalization(string myCapitalization)
		{
			Capitalization = myCapitalization;
		}

		public void SetAnalysis(string myAnalysis)
		{
			Analysis = myAnalysis;

			// Call setAnalysisByPart to ensure the root is converted to lowercase
			SetAnalysisByPart(GetAnalysisPrefixes(), GetAnalysisRootPOS(), GetAnalysisRoot(), GetAnalysisSuffixes());
		}

		public void SetAnalysisByPart(List<string> prefixes, string pos, string root, List<string> suffixes)  // prefixes and suffixes are string lists
		{
			Capitalization = CalcCase(root);

			// change spaces to underscores in the root:
			string myRoot = AddUnderscores(root);

			// change spaces to underscores in the POS:
			string myPos = AddUnderscores(pos);

			// remove periods in the POS
			myPos = RemovePeriods(myPos);

			// if it's an unknown word, don't change the case, otherwise we always store lower case
			if (pos != "UNK")
			{
				myRoot = PyStr.Lower(myRoot);
			}

			Analysis = string.Join(" ", prefixes) + " < " + myPos + " " + myRoot + " > " + string.Join(" ", suffixes);
		}

		public void SetAfterPunc(string myAfterPunc)
		{
			AfterPunc = myAfterPunc;
		}

		public void SetBeforePunc(string myBeforePunc)
		{
			BeforePunc = myBeforePunc;
		}

		public void SetOriginalLexicalUnitString(string LUstr)
		{
			_originalLexicalUnitString = LUstr;
		}
	}

	// The target complex forms and irregularly inflected variants, loaded from the bundle's copy of ConversionData's cache file. Only loadFromCacheNew() and what it needs are ported; the desktop
	// decides whether the cache is current and rebuilds it when the bundle is exported (see synthexport.py). The file's layout is described in ConvertTextToSTAMPformat.py.
	public sealed class ConversionData
	{
		readonly string cacheFilePath;
		readonly Dictionary<string, (List<ANAInfo> ComponentAnaList, bool InflectionOnFirst)> rootComponentANAlistMap = new();
		readonly Dictionary<string, List<(ANAInfo VarAna, List<(string Name, string Val)> AbbrList)>> rootVariantANAandFeatlistMap = new();

		public ConversionData(string cacheFilePath)
		{
			this.cacheFilePath = cacheFilePath;
			LoadFromCacheNew();
		}

		static List<(string Name, string Val)> GetAbbrList(int indx, List<string> lines)
		{
			var abbrList = new List<(string Name, string Val)>();

			// Get number of abbreviations to read in
			int numAbbr = PyInt(lines[indx]);
			indx += 1;

			// read in the name value pairs in consecutive lines
			for (int n = 0; n < numAbbr; n++)
			{
				string name = PyStr.RStrip(lines[indx]);
				string val = PyStr.RStrip(lines[indx + 1]);
				indx += 2;

				// Add them to the list
				abbrList.Add((name, val));
			}

			return abbrList;
		}

		public string GetCacheFilePath()
		{
			return cacheFilePath;
		}

		public (Dictionary<string, (List<ANAInfo> ComponentAnaList, bool InflectionOnFirst)>, Dictionary<string, List<(ANAInfo VarAna, List<(string Name, string Val)> AbbrList)>>) GetData()
		{
			return (rootComponentANAlistMap, rootVariantANAandFeatlistMap);
		}

		bool LoadFromCacheNew()
		{
			List<string> fileLines = ReadPyLines(GetCacheFilePath(), false);

			var complexLines = new List<string>();
			var inflLines = new List<string>();

			// start with complex forms
			bool doingComplexForms = true;

			// Read each section of the cache file
			for (int i = 0; i < fileLines.Count; i++)
			{
				string line = fileLines[i];

				// Skip the first line
				if (i == 0)
				{
					continue;
				}

				// Next read the irregular forms. Skip this line
				if (PyStr.RStrip(line) == IRR_INFL_VARIANTS)
				{
					doingComplexForms = false;
					continue;
				}

				if (doingComplexForms == true)
				{
					complexLines.Add(PyStr.RStrip(line));
				}
				else  // variant forms
				{
					inflLines.Add(PyStr.RStrip(line));
				}
			}

			// Process complex forms
			int j = 0;
			int t = complexLines.Count;

			while (j < t)
			{

				// Get the basic info.
				string headWord = PyStr.RStrip(complexLines[j]);
				bool inflectionOnFirst = PyStr.RStrip(complexLines[j + 1]) == "True";
				int numComponents = PyInt(complexLines[j + 2]);

				j += 3;
				var componentAnaList = new List<ANAInfo>();

				// Get the components for the current complex form
				for (int n = 0; n < numComponents; n++)
				{
					var newANA = new ANAInfo();
					newANA.SetAnalysis(PyStr.RStrip(complexLines[j]));
					componentAnaList.Add(newANA);

					j += 1;
				}

				rootComponentANAlistMap[headWord] = (componentAnaList, inflectionOnFirst);
			}

			// Process irregular forms
			j = 0;
			t = inflLines.Count;

			while (j < t)
			{
				string headWord = PyStr.RStrip(inflLines[j]);
				int numVariants = PyInt(inflLines[j + 1]);
				j += 2;
				var variantANAandFeatlist = new List<(ANAInfo VarAna, List<(string Name, string Val)> AbbrList)>();

				for (int n = 0; n < numVariants; n++)
				{
					var newANA = new ANAInfo();
					newANA.SetAnalysis(PyStr.RStrip(inflLines[j]));

					j += 1;
					List<(string Name, string Val)> abbrList = GetAbbrList(j, inflLines);

					// move the i index past all the abbreviations. Length x2 since each abbr. has two lines (name, val). 1 more for the num of abbreviations at the start of the abbrev. block
					j += abbrList.Count * 2 + 1;

					variantANAandFeatlist.Add((newANA, abbrList));
				}

				rootVariantANAandFeatlistMap[headWord] = variantANAandFeatlist;
			}

			return true;
		}

		// Python's int() on a line: surrounding whitespace is allowed
		static int PyInt(string s)
		{
			return int.Parse(PyStr.Strip(s), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture);
		}
	}

	// Check if the tags (prefixes & suffixes) match the features of one of the main entry's variants. If so replace the main entry headword with the variant and remove the tags that matched.
	// E.g. if the main entry 'be1.1' has an irr. infl. form variant 'am1.1' with a variant type called 1Sg which has features [per: 1ST, num: SG] and the Ana entry is '< cop be1.1 >  1ST SG',
	// we want a new Ana entry that looks like this: '< _variant_ am1.1 >'. Only the HermitCrab branch is ported; the original's two branches are the same anyway.
	public static void ChangeToVariant(ANAInfo myAnaInfo, Dictionary<string, List<(ANAInfo VarAna, List<(string Name, string Val)> AbbrList)>> rootVariantANAandFeatlistMap)
	{
		string oldCap = myAnaInfo.GetCapitalization();
		List<string> pfxs = myAnaInfo.GetAnalysisPrefixes();
		int numPfxs = pfxs.Count;
		List<string> sfxs = myAnaInfo.GetAnalysisSuffixes();
		List<string> tags = pfxs.Concat(sfxs).ToList();
		int numFeatures = 0;
		bool variantMatches = false;
		int i = 0;
		ANAInfo? varAna = null;

		// loop through the irr. infl. form variant list for this main entry
		var variantANAandFeatlist = rootVariantANAandFeatlistMap[myAnaInfo.GetPreDotRoot()!];

		foreach (var (oneVarAna, featAbbrList) in variantANAandFeatlist)  // each tuple as form (entry, featAbbrList)
		{

			// Python's for loop leaves its variable set to the last item, so varAna is set at the top of each pass
			varAna = oneVarAna;

			// See if there is a variant that has inflection features that match the tags in this entry. sorted() by name is stable and compares by code point.
			variantMatches = false;
			List<string> featList = featAbbrList.OrderBy(x => x.Name, Comparer<string>.Create(CompareCodePoints)).Select(y => y.Val).ToList();
			numFeatures = featList.Count;

			// There has to be at least as many tags as features
			if (tags.Count >= numFeatures)
			{
				List<string> sortedFeatList = featList.OrderBy(x => x, Comparer<string>.Create(CompareCodePoints)).ToList();

				// Loop through slices of the tag list. i is used after the loops only when a slice matched, so where Python's loop variable is left otherwise doesn't matter.
				for (i = 0; i < tags.Count - numFeatures + 1; i++)
				{

					// See if we match regardless of order
					if (tags.GetRange(i, numFeatures).OrderBy(x => x, Comparer<string>.Create(CompareCodePoints)).SequenceEqual(sortedFeatList, StringComparer.Ordinal))
					{
						variantMatches = true;
						break;
					}
				}

				if (variantMatches)
				{
					break;
				}
			}
		}

		if (variantMatches && varAna != null)
		{

			// Remove the matched tags. The prefix deletion uses i even when the match was among the suffixes; the slice clamps (see TRAPS).
			DelSlice(pfxs, i, i + numFeatures);
			int beg = i - numPfxs;

			if (beg < 0)
			{
				beg = 0;
			}

			int end = i - numPfxs + numFeatures;

			if (end < 0)
			{
				end = 0;
			}

			DelSlice(sfxs, beg, end);

			// Reset the Ana info. For HermitCrab we put out the sense #. A variant can be a variant of an entry with multiple senses, whose categories could take affixes differently.
			myAnaInfo.SetAnalysisByPart(pfxs, VARIANT_STR, varAna.GetCapitalizedAnalysisRoot() + "." + myAnaInfo.GetSenseNum(), sfxs);

			// Change the case as necessary
			myAnaInfo.SetCapitalization(oldCap);
		}
	}

	// Write one master file line for a word that isn't a complex form, substituting a variant first when one matches. A lexical unit already written is skipped.
	public static void WriteNonComplex(ANAInfo myAnaInfo, Dictionary<string, List<(ANAInfo VarAna, List<(string Name, string Val)> AbbrList)>> rootVariantANAandFeatlistMap, StreamWriter fOutput, HashSet<string>? HCparseStrMap)
	{
		string? root = myAnaInfo.GetPreDotRoot();

		// A root of None is never in the map
		if (root != null && rootVariantANAandFeatlistMap.ContainsKey(root))
		{

			// replace main entry with variant entry and remove appropriate tags (pfxs & sfxs)
			ChangeToVariant(myAnaInfo, rootVariantANAandFeatlistMap);
		}

		string originalLexicalUnitStr = myAnaInfo.GetOriginalLexicalUnitString();

		// see if the orignal LU string for is already in our map
		if (HCparseStrMap != null && !HCparseStrMap.Contains(originalLexicalUnitStr))
		{

			// Get the string that we would write to the parses file
			string HCparseStr = myAnaInfo.GetHCparseStr();
			string cap = myAnaInfo.GetCapitalization();

			WritePyText(fOutput, originalLexicalUnitStr + "," + HCparseStr + ";" + cap + "\n");

			HCparseStrMap.Add(originalLexicalUnitStr);
		}
	}

	// Write one master file line for a complex form: its lexical unit, then each component's parse, separated by |. No variant substitution happens here (see TRAPS above).
	public static void WriteComponents(List<ANAInfo> componentList, StreamWriter fOutput, ANAInfo theAnaInfo, HashSet<string>? HCparseStrMap)
	{
		string originalLexicalUnitStr = theAnaInfo.GetOriginalLexicalUnitString();

		// see if the orignal LU string for this complex form is already in our map
		if (HCparseStrMap != null && !HCparseStrMap.Contains(originalLexicalUnitStr))
		{

			for (int i = 0; i < componentList.Count; i++)
			{
				ANAInfo listAnaInfo = componentList[i];

				// Get the string that we would write to the parses file
				string HCparseStr = listAnaInfo.GetHCparseStr();
				string cap = listAnaInfo.GetCapitalization();

				// First component, write the original LU string and the first component
				if (i == 0)
				{
					WritePyText(fOutput, originalLexicalUnitStr + "," + HCparseStr + ";" + cap);
				}

				// Write all other components
				else
				{
					WritePyText(fOutput, "|" + HCparseStr + ";" + cap);
				}
			}

			WritePyText(fOutput, "\n");
			HCparseStrMap.Add(originalLexicalUnitStr);
		}
	}

	public static List<ANAInfo> ProcessComplexForm(ANAInfo textAnaInfo, List<ANAInfo> componANAlist, bool inflectionOnFirst)
	{
		bool firstRoot = true;
		var newCompANAlist = new List<ANAInfo>();

		for (int index = 0; index < componANAlist.Count; index++)
		{
			ANAInfo myAnaInfo = componANAlist[index];
			ANAInfo currentAna;

			// See if we are at the beginning or the end, depending on where the inflection goes, write out all the stuff with inflection
			if ((inflectionOnFirst && firstRoot) || (!inflectionOnFirst && index == componANAlist.Count - 1))
			{

				// Create a new Ana info object
				var newAna = new ANAInfo();

				// add affixation to the ANA object. Affixes on the myAnaInfo are proclitics and enclitics if they exist. Put text prefixes after proclitics and suffixes before enclitics.
				newAna.SetAnalysisByPart(myAnaInfo.GetAnalysisPrefixes().Concat(textAnaInfo.GetAnalysisPrefixes()).ToList(), myAnaInfo.GetAnalysisRootPOS(), myAnaInfo.GetCapitalizedAnalysisRoot(), textAnaInfo.GetAnalysisSuffixes().Concat(myAnaInfo.GetAnalysisSuffixes()).ToList());

				newCompANAlist.Add(newAna);
				currentAna = newAna;
			}
			else
			{
				newCompANAlist.Add(myAnaInfo);
				currentAna = myAnaInfo;
			}

			// Set the capitalization of the first ANA object to be the same as the original complex form ANA object. This is because a complex form that is normally lower case might be capitalized
			// in the text. When currentAna is a cached component, this changes the cache (see TRAPS).
			if (firstRoot)
			{
				currentAna.SetCapitalization(textAnaInfo.GetCapitalization());
			}

			firstRoot = false;
		}

		return newCompANAlist;
	}

	public static (string Prev2words, string Foll2words) GetContextWords(int wrdCnt, List<string> wordToks)
	{
		string prev2words;
		string foll2words;

		// Determine the context words around the problem word
		if (wrdCnt - 2 >= 0)
		{
			prev2words = wordToks[wrdCnt - 2] + " " + wordToks[wrdCnt - 1];
		}
		else
		{

			if (wrdCnt - 1 >= 0)
			{
				prev2words = wordToks[wrdCnt - 1];
			}
			else
			{
				prev2words = "";
			}
		}

		if (wrdCnt + 2 < wordToks.Count)
		{
			foll2words = wordToks[wrdCnt + 1] + " " + wordToks[wrdCnt + 2];
		}
		else
		{

			if (wrdCnt + 1 < wordToks.Count)
			{
				foll2words = wordToks[wrdCnt + 1];
			}
			else
			{
				foll2words = "";
			}
		}

		return (prev2words, foll2words);
	}

	// Split the transfer results into lexical units and the punctuation between them, and return (errorList, the ANAInfo list). The original reads the transfer results file; this takes its text.
	public static (ErrorList, List<ANAInfo>) ConvertIt(string pfxName, string resultsFileStr)
	{
		var errorList = new ErrorList();
		var wordAnaInfoList = new List<ANAInfo>();
		ANAInfo? anaObj = null;

		var affixMap = new Dictionary<string, string>();

		// Read in the target affix list. Python unpacks re.split()'s result into two names, so a line without exactly one | raises.
		foreach (string line in ReadPyLines(pfxName, false))
		{
			string[] parts = PyStr.RStrip(line).Split('|');

			if (parts.Length != 2)
			{
				throw new InvalidDataException($"{(parts.Length < 2 ? "not enough" : "too many")} values to unpack (expected 2) in the target affix list {pfxName}: {PyStr.RStrip(line)}");
			}

			affixMap[parts[0]] = parts[1];
		}

		// Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x
		resultsFileStr = reSentLU.Replace(resultsFileStr, m => m.Groups[1].Value);  // use [^^] (meaning not caret because otherwise using . might match a ^)

		// Split the string into lexical units and 'punctuation' (non-lexical units)
		List<string> tokens = PySplitWithGroup(reLexicalUnit, resultsFileStr);

		// The lexical units, tokens[1::2]
		List<string> luTokens = tokens.Where((tok, n) => n % 2 == 1).ToList();

		// Pair up the tokens. The first is the punctuation, the second is the LU. Loop through pairs of tokens.
		for (int cnt = 0; cnt < luTokens.Count; cnt++)
		{
			string punc = tokens[cnt * 2];
			string lu = tokens[cnt * 2 + 1];
			List<string> morphs;

			// Special handling of first word (no post punctuation gets added)
			if (cnt == 0)
			{

				// Process the lexical unit string and get an ANA object back
				(anaObj, morphs) = ProcessLU(lu, affixMap);

				if (anaObj == null)
				{
					return (ProcessLUparseError(cnt, luTokens, morphs), wordAnaInfoList);
				}

				anaObj.SetBeforePunc(punc);
			}
			else
			{

				// Determine what part of the punctuation goes at the end of the last word and which goes to the beginning of the current word.
				var (pre, post) = CalculatePrePostPunctuation(punc);

				// 'post' belongs to the previous word (anaObj isn't reassigned to the current word until below). Guard in case the previous word never produced a valid ANA object.
				if (anaObj != null)
				{
					anaObj.SetAfterPunc(post);
				}

				// Process the lexical unit string and get an ANA object back
				(anaObj, morphs) = ProcessLU(lu, affixMap);

				if (anaObj == null)
				{
					return (ProcessLUparseError(cnt, luTokens, morphs), wordAnaInfoList);
				}

				anaObj.SetBeforePunc(pre);
			}

			wordAnaInfoList.Add(anaObj);
		}

		// Process a possible last punctuation string
		if (anaObj != null && tokens.Count > 0 && tokens[^1] != "")
		{
			string last = tokens[^1];
			anaObj.SetAfterPunc(last.StartsWith(' ') ? last[1..] : last);  // remove preceding space
		}

		return (errorList, wordAnaInfoList);
	}

	public static (string Pre, string Post) CalculatePrePostPunctuation(string puncStr)
	{
		string pre = "";
		string post = "";

		if (puncStr.Length > 0)
		{
			string[] puncList = puncStr.Split(' ');
			post = puncList[0];
			pre = string.Join(" ", puncList.Skip(1));

			// If post punctuation is non-empty add a trailing space. Otherwise we will get two words jammed together by STAMP. It doesn't put a space between words when \n is used.
			if (post.Length > 0 && post[^1] != '\n')
			{
				post += " ";
			}
		}

		return (pre, post);
	}

	public static ErrorList ProcessLUparseError(int cnt, List<string> tokList, List<string> morphs)
	{
		var (prev2words, foll2words) = GetContextWords(cnt, tokList);  // just pass the lexical units
		var errorList = new ErrorList { ($"Lemma or grammatical category missing for a target word near word {cnt + 1}. Found only: {string.Join(",", morphs)}. The preceding two words were: {prev2words}. The following two words were: {foll2words}. Processing stopped.", 2) };
		return errorList;
	}

	public static (ANAInfo?, List<string>) ProcessLU(string lexUnitStr, Dictionary<string, string> affixMap)
	{
		var prefixList = new List<string>();
		var suffixList = new List<string>();
		var infixList = new List<string>();
		var circumfixList = new List<string>();
		ANAInfo? wordAnaInfo = null;

		// Get the root, root category and any affixes, without the empty strings
		List<string> morphs = lexUnitStr.Split('<', '>').Where(tk => tk.Length > 0).ToList();

		// start at position 2 since this is where the affixes start
		for (int i = 2; i < morphs.Count; i++)
		{

			// If we don't have the item in the affix map, then it must be a feature. Treat it like a suffix, because change_to_variant will use the feature(s) to find a variant
			if (!affixMap.TryGetValue(morphs[i], out string? morphType))
			{
				suffixList.Add(morphs[i]);
			}

			// We use English morphnames as a standard in the target affix glosses file. prefix
			else if (morphType == "prefix" || morphType == "proclitic" || morphType == "prefixing interfix")
			{
				prefixList.Add(morphs[i]);
			}

			// infix
			else if (morphType == "infix" || morphType == "infixing interfix")
			{
				infixList.Add(morphs[i]);
			}

			// circumfix
			else if (morphType == "circumfix")
			{

				// Circumfixes are made of two parts, a prefix part and a suffix part when we encounter a new circumfix, give it a unique new gloss and add it to the prefix list. When we see one that
				// we've seen before, it must be the suffix part. Give it a unique new gloss and add it to the suffix list.
				if (!circumfixList.Contains(morphs[i]))
				{
					prefixList.Add(morphs[i] + CIRCUMFIX_TAG_A);
					circumfixList.Add(morphs[i]);
				}
				else
				{
					suffixList.Add(morphs[i] + CIRCUMFIX_TAG_B);
				}
			}

			// suffix. Treat everything else as a suffix (suffix, enclitic, suffixing interfix). The other types are not supported, but will end up here.
			else
			{
				suffixList.Add(morphs[i]);
			}
		}

		if (morphs.Count < 2)
		{
			return (wordAnaInfo, morphs);
		}

		// Create an ANA Info object. We have the root (morphs[0]) and the POS of the root (morphs[1])
		wordAnaInfo = new ANAInfo(prefixList, suffixList, morphs[1], morphs[0], infixList);
		wordAnaInfo.SetOriginalLexicalUnitString(lexUnitStr);

		return (wordAnaInfo, morphs);
	}

	// The HermitCrab half of convert_to_STAMP(): write the master file from the transfer results. Returns the error list. The type lists were checked when the bundle was exported.
	public static ErrorList ConvertToHermitCrab(ConversionData convData, string affixFile, string resultsFileStr, string HCmasterFile, List<string> complexForms1st, List<string> complexForms2nd, string? sentPunct)
	{
		var errorList = new ErrorList();

		if (!(affixFile.Length > 0 && !string.IsNullOrEmpty(sentPunct)))
		{
			errorList.Add(("Configuration file problem with targetANAFile or affixFile or transferResultsFile or sentPunct", 2));
			return errorList;
		}

		// Build the complex forms map. Create a map that tracks which complex form types are for first or for last. convert_to_STAMP() hands it to ConversionData, which only uses it when it
		// rebuilds its cache; the bundle's cache was made on the desktop, so here it is built only to keep the original's steps.
		var complexFormTypeMap = new Dictionary<string, int>();

		foreach (string cmplxType in complexForms1st)
		{
			complexFormTypeMap[cmplxType] = 0;  // 0 - inflection on first root
		}

		foreach (string cmplxType in complexForms2nd)
		{
			complexFormTypeMap[cmplxType] = 1;  // 1 - inflection on last root
		}

		// Convert the Apertium text to an ANA list
		var (errList, anaInfoList) = ConvertIt(affixFile, resultsFileStr);

		if (errList.Count > 0)
		{
			errorList.AddRange(errList);
			return errorList;
		}

		// retrieve the data that got initialized in the Conversion data class
		var (rootComponANAlistMap, rootVariantANAandFeatlistMap) = convData.GetData();

		// Now we are going to process the ANA list, breaking down each complex form into separate ANA records if needed. This is needed for instance if a source word maps to multiple words in the
		// target language.
		StreamWriter fOutput;

		try
		{
			fOutput = new StreamWriter(HCmasterFile, false, new UTF8Encoding(false));
		}

		catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
		{
			errorList.Add(("Error writing the output file.", 2));
			return errorList;
		}

		int count = 0;
		var HCparseStrMap = new HashSet<string>();

		// Loop through all the ANA pieces
		foreach (ANAInfo anaInfo in anaInfoList)
		{

			// If an ANA root matches a complex form, rewrite the ana file with complex forms broken down into components
			string? root = anaInfo.GetPreDotRoot();

			if (root != null && rootComponANAlistMap.TryGetValue(root, out var complexForm))
			{
				List<ANAInfo> newCompANAlist = ProcessComplexForm(anaInfo, complexForm.ComponentAnaList, complexForm.InflectionOnFirst);
				WriteComponents(newCompANAlist, fOutput, anaInfo, HCparseStrMap);
			}
			else  // write it out as normal. This also converts variant forms if needed.
			{
				WriteNonComplex(anaInfo, rootVariantANAandFeatlistMap, fOutput, HCparseStrMap);
			}

			count += 1;
		}

		errorList.Add(($"Converted target words put in the file: {HCmasterFile}", 0));
		errorList.Add(($"{count} records exported in HermitCrab format.", 0));

		fOutput.Close();

		return errorList;
	}

	// Put the surface forms into the transfer results. Returns (errorList, the synthesized text, or null on an error). The original reads the transfer results file and writes the synthesis file.
	public static (ErrorList, string?) ProduceSynthesisFile(List<(string LUStr, List<string> CapCodeList)> luInfoList, string surfaceFormsFile, string resultsFileStr)
	{
		var errorList = new ErrorList();
		List<string> surfaceFormsList;

		// Open the surface forms file and read in the surface forms (utf-8-sig)
		try
		{
			surfaceFormsList = ReadPyLines(surfaceFormsFile, true);
		}

		catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
		{
			errorList.Add(("There was an error opening the HermitCrab surface forms file.", 2));
			return (errorList, null);
		}

		// Remove blank lines
		surfaceFormsList = surfaceFormsList.Where(line => PyStr.Strip(line).Length > 0).ToList();

		// Do a sanity check to see if the number of surface forms matches the number of Lexical unit strings
		if (surfaceFormsList.Count != luInfoList.Count)
		{
			errorList.Add(("The number of surface forms does not match the number of Lexical Units.", 2));
			return (errorList, null);
		}

		// Loop through the surface forms file. Some lines will have multiple surface forms
		for (int i = 0; i < surfaceFormsList.Count; i++)
		{
			string line = PyStr.Strip(surfaceFormsList[i]);

			// parse multiple surface forms
			string[] surfaceStrList = line.Split(',');

			var (originalLUStr, capCodeList) = luInfoList[i];

			var newSurfaceList = new List<string>();

			// Loop through possible multiple surface forms
			for (int j = 0; j < surfaceStrList.Length; j++)
			{
				string surfaceStr = surfaceStrList[j];

				// See if we have an error E.g. %0%^iba1.1<n><PC.1Sg>$%
				if (surfaceStr.StartsWith("%0%", StringComparison.Ordinal))
				{

					// Everything left of the last % is what we are saving for the surface string
					string saveStr = surfaceStr[..(surfaceStr.LastIndexOf('%') + 1)];

					// Save the error. Everthing to the right of the last %. Make this a warning, code = 1
					string errStr = surfaceStr[(surfaceStr.LastIndexOf('%') + 1)..];

					if (PyStr.Strip(errStr) == "")
					{
						errStr = $"Synthesis failed. ({saveStr})";
					}

					errorList.Add((errStr, 1));
					surfaceStr = saveStr;
				}

				surfaceStr = CapitalizeString(surfaceStr, capCodeList[j]);
				newSurfaceList.Add(surfaceStr);
			}

			// substitute the Apertium parse with the surface form throughout the target text. The original's re.sub(re.escape(LU), forms, text) is a literal replacement of every occurrence
			// with the forms read as a Python replacement template (see PYTHON'S STR AND RE IN .NET).
			resultsFileStr = PyReplaceLiteral(resultsFileStr, originalLUStr, ExpandPyReplacement(string.Join(" ", newSurfaceList)));
		}

		// Handle the sentence punctuation. Replace ^x<sent>$ with just the lemma x. This regex looks for a non-% or beg. of string followed by a ^ in order to find the sentence lexical unit. The
		// non-% is needed because a word that didn't synthesize leaves an error string like %0%^iba1.1<n><PC.1Sg>$%, whose ^ must not start the match. An error string can also come right before it, so $%^.
		resultsFileStr = reSentLUAfterSynthesis.Replace(resultsFileStr, m => m.Groups[1].Value + m.Groups[2].Value);

		return (errorList, resultsFileStr);
	}

	public static ErrorList CreateHermitCrabParsesFile(string masterFile, string parsesFile, List<(string LUStr, List<string> CapCodeList)> luInfoList, Dictionary<string, string> HCcapitalLemmasMap)
	{
		var errorList = new ErrorList();
		List<string> masterLines;

		// Open master file
		try
		{
			masterLines = ReadPyLines(masterFile, false);
		}

		catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
		{
			errorList.Add(($"There was an error opening the HermitCrab master file. Do you have the setting \"Use HermitCrab Synthesis\" turned on? Did you run the Convert Text to Synthesizer Format module? File: {parsesFile}", 2));
			return errorList;
		}

		StreamWriter fParses;

		// Open parses file
		try
		{
			fParses = new StreamWriter(parsesFile, false, new UTF8Encoding(false));
		}

		catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
		{
			errorList.Add(("There was an error opening the HermitCrab parses file.", 2));
			return errorList;
		}

		// Parse each line - format: LU,HCparse1;capitalizationCode|HCparse2;capitalizationCode|...
		foreach (string masterLine in masterLines)
		{
			string line = PyStr.RStrip(masterLine);

			if (line.Length == 0)
			{
				continue;
			}

			// Get the lexical unit (expect exactly one comma separating LU and parses)
			string[] parts = line.Split(',');

			if (parts.Length != 2)
			{
				errorList.Add(($"Malformed Lexical Unit in HermitCrab master file skipping this line: {line}", 2));
				continue;
			}

			string luStr = parts[0];
			string HCparseStr = parts[1];

			// skip @ words. They have the form: ^@... (HCparseStr[1] is the second code point; see TRAPS)
			if (CodePointAt(HCparseStr, 1) == "@")
			{
				WritePyText(fParses, "\n");
				continue;
			}

			// Get the parses
			string[] HCparsesList = HCparseStr.Split('|');
			var capCodeList = new List<string>();

			// Get the parse and capitalization code pair
			foreach (string hcparseCombo in HCparsesList)
			{
				string[] pair = hcparseCombo.Split(';');

				// Python unpacks the split into two names, so anything but one ; raises
				if (pair.Length != 2)
				{
					fParses.Close();
					throw new InvalidDataException($"{(pair.Length < 2 ? "not enough" : "too many")} values to unpack (expected 2) in the HermitCrab master file: {hcparseCombo}");
				}

				string hcParse = pair[0];
				string capCode = pair[1];
				capCodeList.Add(capCode);

				// Capitalize if necessary
				if (capCode.Length > 0)
				{
					hcParse = Capitalize(hcParse, HCcapitalLemmasMap);
				}

				// Write the parse to the parses file
				WritePyText(fParses, "^" + hcParse + "$");
			}

			WritePyText(fParses, "\n");
			luInfoList.Add((luStr, capCodeList));
		}

		fParses.Close();
		return errorList;
	}

	public static string Capitalize(string hcParse, Dictionary<string, string> HCcapitalLemmasMap)
	{
		var (root, posName) = ExtractRootAndFirstTag(hcParse);

		if (root == null || posName == null)
		{
			return hcParse;  // fallback
		}

		string key = PyStr.Lower(root) + posName;
		string rootCap = HCcapitalLemmasMap.TryGetValue(key, out string? found) ? found : root;

		// Replace only the first occurrence of root with rootCap
		int at = hcParse.IndexOf(root, StringComparison.Ordinal);
		string rebuilt = at < 0 ? hcParse : hcParse[..at] + rootCap + hcParse[(at + root.Length)..];
		return rebuilt;
	}

	// Returns (root, firstTagAfterRoot) from a HermitCrab parse string. Example: <2s.S2>tang1.1<v><3sg><obj> -> ('tang1.1', 'v'). Positions are UTF-16 here and code points in Python, but they
	// are only compared with each other and used to slice the same string, so the results are the same.
	public static (string? Root, string? FirstTag) ExtractRootAndFirstTag(string hcParse)
	{

		// Find all tags. There should be at least one tag - the POS
		List<Match> tagMatches = reTag.Matches(hcParse).ToList();
		string? root;
		string? firstTagAfterRoot;

		// If there are no tags, the whole string is the root
		if (tagMatches.Count == 0)
		{
			return (hcParse, null);
		}

		// Find the root: the text between the last '>' and the next '<'
		for (int i = 0; i < tagMatches.Count; i++)
		{
			Match match = tagMatches[i];

			// No tags before the root
			if (i == 0 && match.Index > 0)
			{
				root = hcParse[..match.Index];

				// The first tag will this 0th match
				firstTagAfterRoot = match.Groups[1].Value;
				return (root, firstTagAfterRoot);
			}

			// Root must be after a prefix
			else if (i > 0)
			{
				Match prev = tagMatches[i - 1];
				int prevEnd = prev.Index + prev.Length;

				// The root will be found where there is a gap between tags
				if (prevEnd < match.Index)
				{
					root = hcParse[prevEnd..match.Index];

					// The first tag will be the ith match (the one after the gap)
					firstTagAfterRoot = match.Groups[1].Value;
					return (root, firstTagAfterRoot);
				}
			}
		}

		// If no root found in the loop, check after the last tag
		Match lastTag = tagMatches[^1];
		int lastEnd = lastTag.Index + lastTag.Length;

		if (lastEnd < hcParse.Length)
		{
			root = hcParse[lastEnd..];
			return (root, null);
		}

		// Fallback: no root found
		return (null, null);
	}

	// Remove @ signs at the beginning of words and N.N at the end of words if so desired in the settings, also symbols and ^%0%...%$. The original rewrites the synthesis file; this returns the text.
	public static string FixUpText(string synFileContents, bool cleanUpText)
	{

		if (cleanUpText)
		{

			// Remove n.n on lemmas (ASCII digits, as re.A gives)
			synFileContents = reSenseNumbers.Replace(synFileContents, m => "");

			// Remove at signs
			synFileContents = synFileContents.Replace("@", "");

			// Remove symbols, i.e. <xyz>
			synFileContents = reSymbol.Replace(synFileContents, m => "");

			// Remove the ^%0%...%$ (^ and $ are optional which is the case for unknown punctuation)
			synFileContents = reFailedWord.Replace(synFileContents, m => m.Groups[1].Value);
		}

		// Un-escape punctuation text that was escaped before running apertium tools. E.g. convert \] to ]
		synFileContents = UnescapeReservedApertChars(synFileContents);

		return synFileContents;
	}

	// A map from lower-cased gloss plus part of speech name to the gloss, for the target lexical entries whose gloss has an upper case letter; null when the config can't be read. ElementTree's
	// reading is copied: the DTD is ignored, whitespace is kept, './/X' looks below the root element, find() and findall() look at children.
	public static Dictionary<string, string>? GetCapitalLemmas(string HCconfigPath)
	{

		// Create a dictionary to store the extracted lemmas
		var HCcapitalLemmasMap = new Dictionary<string, string>();
		XElement root;

		// Parse the HermitCrab.config XML file
		try
		{
			var settings = new XmlReaderSettings { DtdProcessing = DtdProcessing.Ignore, XmlResolver = null };

			using XmlReader reader = XmlReader.Create(HCconfigPath, settings);
			root = XDocument.Load(reader, LoadOptions.PreserveWhitespace).Root!;
		}

		catch (Exception e) when (e is IOException || e is UnauthorizedAccessException || e is XmlException)
		{
			return null;
		}

		// Find the PartsOfSpeech element
		XElement? partsOfSpeechElem = root.Descendants("PartsOfSpeech").FirstOrDefault();

		// Build a dictionary mapping part of speech id to name
		var partOfSpeechMap = new Dictionary<string, string>();

		if (partsOfSpeechElem != null)
		{

			foreach (XElement posElem in partsOfSpeechElem.Elements("PartOfSpeech"))
			{
				string? posId = (string?)posElem.Attribute("id");
				XElement? nameElem = posElem.Element("Name");
				string? nameText = nameElem == null ? null : EtText(nameElem);

				if (!string.IsNullOrEmpty(posId) && nameElem != null && !string.IsNullOrEmpty(nameText))
				{
					partOfSpeechMap[posId] = nameText;
				}
			}
		}

		// Iterate over all LexicalEntry elements
		foreach (XElement lexEntry in root.Descendants("LexicalEntry"))
		{
			XElement? glossElem = lexEntry.Element("Gloss");
			string? posId = (string?)lexEntry.Attribute("partOfSpeech");
			string? glossText = glossElem == null ? null : EtText(glossElem);

			// Only proceed if both gloss and partOfSpeech are present and valid
			if (glossElem != null && !string.IsNullOrEmpty(glossText) && posId != null && partOfSpeechMap.TryGetValue(posId, out string? posName))
			{

				// Only add if any letter in the gloss is uppercase
				if (glossText.EnumerateRunes().Any(r => PyStr.IsUppercase(r.Value)))
				{

					// Build a key for the map of gloss name + POS
					string key = PyStr.Lower(glossText) + posName;
					HCcapitalLemmasMap[key] = glossText;
				}
			}
		}

		return HCcapitalLemmasMap;
	}

	// synthesizeWithHermitCrab(), the DLL branch: write the parses file, run the HCSynthByGlossDll object and put its surface forms into the transfer results. Returns (errorList, the synthesized
	// text or null). The capital lemmas map is made once by the Synthesizer (see TRAPS above), and clean is the CleanUpUnknownTargetWords value.
	public static (ErrorList, string?) SynthesizeWithHermitCrab(string languageCode, Dictionary<string, string>? HCcapitalLemmasMap, string parsesFile, string masterFile, string surfaceFormsFile, string resultsFileStr, string? clean, HCSynthByGlossDll DLLobj)
	{
		var luInfoList = new List<(string LUStr, List<string> CapCodeList)>();

		if (HCcapitalLemmasMap == null)
		{
			return (new ErrorList { ("Unable to open the HC master file.", 2) }, null);
		}

		ErrorList errorList = CreateHermitCrabParsesFile(masterFile, parsesFile, luInfoList, HCcapitalLemmasMap);

		foreach (var triplet in errorList)
		{

			if (triplet.Code == 2)  // error
			{
				return (errorList, null);
			}
		}

		// The program sets the UI culture from its language code, which chooses the language of HC's messages; the DLL doesn't, so it is done here (see TRAPS)
		CultureInfo culture = CultureInfo.GetCultureInfo(languageCode);
		CultureInfo.DefaultThreadCurrentUICulture = culture;
		Thread.CurrentThread.CurrentUICulture = culture;
		DLLobj.LocaleCode = languageCode;
		DLLobj.DoTracing = false;
		DLLobj.ShowTracing = false;

		try
		{

			if (DLLobj.SetGlossFile(parsesFile) != DLLobj.kSuccess)
			{
				errorList.Add(("An error happened when setting the gloss file for the HermitCrab Synthesize By Gloss tool (DLL).", 2));
				return (errorList, null);
			}
		}

		catch (Exception e)
		{
			errorList.Add(($"An exception happened when trying to set the gloss file for the HermitCrab Synthesize By Gloss tool (DLL). Error: {e.Message}", 2));
			return (errorList, null);
		}

		try
		{

			if (DLLobj.Process() != DLLobj.kSuccess)
			{
				errorList.Add(("An error happened when running the HermitCrab Synthesize By Gloss tool (DLL).", 2));
				return (errorList, null);
			}
		}

		catch (Exception e)
		{
			errorList.Add(($"An exception happened when trying to run (by calling Process) the HermitCrab Synthesize By Gloss tool (DLL). Error: {e.Message}", 2));
			return (errorList, null);
		}

		// Count the # of lexical units
		int LUsCount = ReadPyLines(parsesFile, false).Count(line => PyStr.Strip(line).Length > 0);

		errorList.Add(($"Processing {LUsCount} unique lexical units.", 0));

		// Produce synthesis file
		var (errList, synFileContents) = ProduceSynthesisFile(luInfoList, surfaceFormsFile, resultsFileStr);
		errorList.AddRange(errList);

		// check for fatal errors
		if (synFileContents == null || errorList.Any(triplet => triplet.Code == 2))
		{
			return (errorList, null);
		}

		if (string.IsNullOrEmpty(clean))
		{
			errorList.Add(($"Configuration file problem with the value: {CLEANUP_UNKNOWN_WORDS}.", 2));
			return (errorList, null);
		}

		bool cleanUpText;

		// clean[0].lower() == 'y', on the first code point
		if (PyStr.Lower(CodePointAt(clean, 0)) == "y")
		{
			cleanUpText = true;
		}
		else
		{
			cleanUpText = false;
		}

		synFileContents = FixUpText(synFileContents, cleanUpText);

		errorList.Add(("Synthesis complete.", 0));

		return (errorList, synFileContents);
	}

	// Make an HCSynthByGlossDll object that writes surfaceFormsFile, with the HermitCrab config already loaded, as Live Rule Tester's setUpHermitCrab() and extractHermitCrabConfig() do. Throws
	// InvalidOperationException (the Python's RuntimeError) saying what went wrong.
	public static HCSynthByGlossDll LoadHCSynthDll(string HCconfigPath, string surfaceFormsFile)
	{
		HCSynthByGlossDll DLLobj;
		string ret;

		try
		{
			DLLobj = new HCSynthByGlossDll(surfaceFormsFile);
		}

		catch (Exception e)
		{
			throw new InvalidOperationException($"An exception occurred. Could not initialize the HermitCrab synthesis DLL. Error: {e.Message}", e);
		}

		// Load the HermitCrab config, once for the life of the object
		try
		{
			ret = DLLobj.SetHcXmlFile(HCconfigPath);
		}

		catch (Exception e)
		{
			throw new InvalidOperationException($"An exception happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL) Error: {e.Message}", e);
		}

		if (ret != DLLobj.kSuccess)
		{
			throw new InvalidOperationException($"An error happened when loading HermitCrab Configuration file for the HC Synthesis obj. (DLL) {ret}");
		}

		return DLLobj;
	}

	// Python's text-mode write: each \n goes out as the platform's newline (os.linesep), so on Windows the files get \r\n as FLExTrans' own do
	static void WritePyText(StreamWriter writer, string text)
	{
		writer.Write(Environment.NewLine == "\n" ? text : text.Replace("\n", Environment.NewLine));
	}

	// Python's readlines() on a file opened in text mode: universal newlines (\r\n and a lone \r read as \n), lines split after each \n and keeping it, a last line without one kept. With
	// utf-8 a byte order mark stays as \ufeff, as Python's does; with utf-8-sig (sig true) it is dropped. Encoding.GetString keeps it, so it is removed by hand.
	static List<string> ReadPyLines(string path, bool sig)
	{
		string text = Encoding.UTF8.GetString(File.ReadAllBytes(path));

		if (sig && text.StartsWith('\ufeff'))
		{
			text = text[1..];
		}

		text = text.Replace("\r\n", "\n").Replace('\r', '\n');

		var lines = new List<string>();
		int start = 0;

		while (start < text.Length)
		{
			int nl = text.IndexOf('\n', start);

			if (nl < 0)
			{
				lines.Add(text[start..]);
				break;
			}

			lines.Add(text[start..(nl + 1)]);
			start = nl + 1;
		}

		return lines;
	}

	// s[index] in Python: the code point at that code point index, as a string. Past the end Python raises IndexError, and so does this.
	static string CodePointAt(string s, int index)
	{
		int n = 0;

		foreach (Rune rune in s.EnumerateRunes())
		{

			if (n == index)
			{
				return rune.ToString();
			}

			n++;
		}

		throw new IndexOutOfRangeException($"string index out of range: {index} in '{s}'");
	}

	// str.istitle(): upper and title case characters only after uncased ones, lower case only after cased ones, and at least one cased character
	static bool IsTitle(string s)
	{
		bool cased = false;
		bool previousIsCased = false;

		foreach (Rune rune in s.EnumerateRunes())
		{
			int cp = rune.Value;

			if (PyStr.IsUppercase(cp) || PyStr.IsTitlecase(cp))
			{

				if (previousIsCased)
				{
					return false;
				}

				previousIsCased = true;
				cased = true;
			}

			else if (PyStr.IsLowercase(cp))
			{

				if (!previousIsCased)
				{
					return false;
				}

				previousIsCased = true;
				cased = true;
			}
			else
			{
				previousIsCased = false;
			}
		}

		return cased;
	}

	// Python's string ordering: by code point. Ordinal comparison is by UTF-16 unit, which puts characters above the BMP before U+E000-U+FFFF.
	static int CompareCodePoints(string? a, string? b)
	{
		if (a == null || b == null)
		{
			return string.CompareOrdinal(a, b);
		}

		var ea = a.EnumerateRunes().GetEnumerator();
		var eb = b.EnumerateRunes().GetEnumerator();

		while (true)
		{
			bool hasA = ea.MoveNext();
			bool hasB = eb.MoveNext();

			if (!hasA || !hasB)
			{
				return hasA ? 1 : hasB ? -1 : 0;
			}

			if (ea.Current.Value != eb.Current.Value)
			{
				return ea.Current.Value < eb.Current.Value ? -1 : 1;
			}
		}
	}

	// del list[start:end] for non-negative bounds: Python clamps them to the list, so an out-of-range slice deletes what it covers, possibly nothing
	static void DelSlice(List<string> list, int start, int end)
	{
		start = Math.Min(start, list.Count);
		end = Math.Min(end, list.Count);

		if (end > start)
		{
			list.RemoveRange(start, end - start);
		}
	}

	// re.split() with a pattern that has one group: the text between the matches, with each match's group text between them
	static List<string> PySplitWithGroup(Regex regex, string text)
	{
		var pieces = new List<string>();
		int last = 0;

		foreach (Match m in regex.Matches(text))
		{
			pieces.Add(text[last..m.Index]);
			pieces.Add(m.Groups[1].Value);
			last = m.Index + m.Length;
		}

		pieces.Add(text[last..]);
		return pieces;
	}

	// re.sub(re.escape(find), repl, text) once repl is expanded: every non-overlapping occurrence, left to right. An empty find matches between every code point and at both ends, as in Python.
	static string PyReplaceLiteral(string text, string find, string repl)
	{

		if (find.Length > 0)
		{
			return text.Replace(find, repl, StringComparison.Ordinal);
		}

		var sb = new StringBuilder(repl);

		foreach (Rune rune in text.EnumerateRunes())
		{
			sb.Append(rune.ToString()).Append(repl);
		}

		return sb.ToString();
	}

	// What Python's re does with a replacement string when the pattern has no groups: \\ \a \b \f \n \r \t \v become their characters, \0 starts an octal escape (up to three octal digits in all),
	// another backslash and a non-letter stay as they are, and a group reference (\1, \g<...>), another ASCII letter or a trailing backslash is an error (re.error).
	static string ExpandPyReplacement(string repl)
	{

		if (!repl.Contains('\\'))
		{
			return repl;
		}

		var sb = new StringBuilder(repl.Length);
		int i = 0;

		while (i < repl.Length)
		{
			char c = repl[i];

			if (c != '\\')
			{
				sb.Append(c);
				i++;
				continue;
			}

			if (i + 1 >= repl.Length)
			{
				throw new ArgumentException($"bad escape (end of pattern) in the replacement: {repl}");
			}

			char next = repl[i + 1];
			i += 2;

			switch (next)
			{
				case '\\': sb.Append('\\'); break;
				case 'a': sb.Append('\a'); break;
				case 'b': sb.Append('\b'); break;
				case 'f': sb.Append('\f'); break;
				case 'n': sb.Append('\n'); break;
				case 'r': sb.Append('\r'); break;
				case 't': sb.Append('\t'); break;
				case 'v': sb.Append('\v'); break;

				case '0':
				{
					int value = 0;
					int digits = 0;

					while (digits < 2 && i < repl.Length && repl[i] >= '0' && repl[i] <= '7')
					{
						value = value * 8 + (repl[i] - '0');
						i++;
						digits++;
					}

					sb.Append((char)value);
					break;
				}

				default:

					if (next >= '1' && next <= '9')
					{
						throw new ArgumentException($"invalid group reference in the replacement: {repl}");
					}

					if (next < 128 && char.IsAsciiLetter(next))
					{
						throw new ArgumentException($"bad escape \\{next} in the replacement: {repl}");
					}

					// Any other escape is left alone, backslash included
					sb.Append('\\').Append(next);
					break;
			}
		}

		return sb.ToString();
	}

	// ElementTree's element.text: the character data before the first child element (comments and processing instructions don't end it), or null when there is none
	static string? EtText(XElement element)
	{
		var sb = new StringBuilder();
		bool any = false;

		foreach (XNode node in element.Nodes())
		{

			if (node is XElement)
			{
				break;
			}

			if (node is XText textNode)
			{
				sb.Append(textNode.Value);
				any = true;
			}
		}

		return any ? sb.ToString() : null;
	}
}

// A bundle's synthesis data, loaded once, and the HCSynthByGlossDll object that synthesizes with the target HermitCrab config. Synthesize() turns one target Apertium stream (Run Apertium's output)
// into the synthesized text. See the overview at the top of the file. Not for two threads at once.
public sealed class Synthesizer : IDisposable
{
	readonly string affixFile;
	readonly string HCconfigPath;
	readonly Synthesis.ConversionData convData;
	readonly Dictionary<string, string>? HCcapitalLemmasMap;
	readonly string? sentPunct;
	readonly List<string> complexForms1st;
	readonly List<string> complexForms2nd;
	readonly string languageCode;
	readonly HCSynthByGlossDll DLLobj;
	readonly bool ownsWorkDir;
	bool disposed;

	// CleanUpUnknownTargetWords: "y..." cleans up the synthesized text (FixUpText()). From the manifest; the offline server sets "y".
	public string? Clean { get; set; }

	public string WorkDir { get; }
	public string MasterFile { get; }
	public string ParsesFile { get; }
	public string SurfaceFormsFile { get; }

	// bundleDir holds manifest.json and the synthesis folder; workDir is where the three work files go (a new temporary folder, deleted by Dispose(), when null)
	public Synthesizer(string bundleDir, string? workDir = null)
	{
		JsonElement manifest;

		using (JsonDocument doc = JsonDocument.Parse(File.ReadAllText(Path.Combine(bundleDir, "manifest.json"), new UTF8Encoding(false))))
		{
			manifest = doc.RootElement.Clone();
		}

		// manifest["files"].get("synthesis"), which must be there and not empty
		JsonElement files = manifest.GetProperty("files");

		if (!files.TryGetProperty("synthesis", out JsonElement synthFiles) || !IsTruthy(synthFiles))
		{
			throw new InvalidOperationException($"The bundle in {bundleDir} has no synthesis data; export it again with export-bundle.");
		}

		string synthesisDir = Path.Combine(bundleDir, GetString(synthFiles, "dir") ?? Synthesis.SYNTHESIS_DIR);
		affixFile = Path.Combine(synthesisDir, GetString(synthFiles, "affixGlosses") ?? Synthesis.AFFIX_GLOSS_FILE);
		HCconfigPath = Path.Combine(synthesisDir, GetString(synthFiles, "hermitCrabConfig") ?? Synthesis.HERMIT_CRAB_CONFIG_FILE);
		convData = new Synthesis.ConversionData(Path.Combine(synthesisDir, GetString(synthFiles, "conversionCache") ?? Synthesis.CONVERSION_CACHE_FILE));
		HCcapitalLemmasMap = Synthesis.GetCapitalLemmas(HCconfigPath);

		JsonElement config = manifest.GetProperty("config");
		sentPunct = GetString(config, Synthesis.SENTENCE_PUNCTUATION);
		complexForms1st = GetStringList(config, Synthesis.TARGET_FORMS_INFLECTION_1ST);
		complexForms2nd = GetStringList(config, Synthesis.TARGET_FORMS_INFLECTION_2ND);
		Clean = GetString(config, Synthesis.CLEANUP_UNKNOWN_WORDS);

		// manifest.get("interfaceLanguage") or "en"
		string? interfaceLanguage = GetString(manifest, "interfaceLanguage");
		languageCode = string.IsNullOrEmpty(interfaceLanguage) ? "en" : interfaceLanguage;

		// The work folder, made if need be; a temporary one is ours to delete
		if (!string.IsNullOrEmpty(workDir))
		{
			WorkDir = workDir;
		}
		else
		{
			WorkDir = Directory.CreateTempSubdirectory("ftt_synthesis_").FullName;
			ownsWorkDir = true;
		}

		Directory.CreateDirectory(WorkDir);
		MasterFile = Path.Combine(WorkDir, Synthesis.MASTER_FILE);
		ParsesFile = Path.Combine(WorkDir, Synthesis.PARSES_FILE);
		SurfaceFormsFile = Path.Combine(WorkDir, Synthesis.SURFACE_FORMS_FILE);

		// The DLL object, which loads the HermitCrab config now, once
		DLLobj = Synthesis.LoadHCSynthDll(HCconfigPath, SurfaceFormsFile);
	}

	// Convert Text to Synthesizer Format and Synthesize Text on a target stream (Run Apertium's output). Returns the synthesized text, or null after an error, and the messages as (level, text)
	// pairs, the level info, warning or error.
	public (string? Text, List<(string Level, string Message)> Messages) Synthesize(string targetStream)
	{
		ObjectDisposedException.ThrowIf(disposed, this);

		var errorList = Synthesis.ConvertToHermitCrab(convData, affixFile, targetStream, MasterFile, complexForms1st, complexForms2nd, sentPunct);
		string? text = null;

		if (!errorList.Any(triplet => triplet.Code == 2))
		{
			var (errList, synthesized) = Synthesis.SynthesizeWithHermitCrab(languageCode, HCcapitalLemmasMap, ParsesFile, MasterFile, SurfaceFormsFile, targetStream, Clean, DLLobj);
			text = synthesized;
			errorList.AddRange(errList);
		}

		return (text, errorList.Select(e => (Synthesis.LEVEL_NAMES.TryGetValue(e.Code, out string? level) ? level : "error", e.Message)).ToList());
	}

	// Delete the work folder if this Synthesizer made it
	public void Close()
	{
		Dispose();
	}

	public void Dispose()
	{

		if (disposed)
		{
			return;
		}

		disposed = true;

		if (ownsWorkDir)
		{

			try
			{
				Directory.Delete(WorkDir, true);
			}

			catch (Exception e) when (e is IOException || e is UnauthorizedAccessException)
			{

				// A file still open elsewhere; the folder is in the temporary folder, so leaving it is harmless
			}
		}
	}

	// dict.get(name) for a string value; null when it's missing or JSON null
	static string? GetString(JsonElement obj, string name)
	{
		return obj.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.String ? value.GetString() : null;
	}

	// config.get(name) or []
	static List<string> GetStringList(JsonElement obj, string name)
	{

		if (obj.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.Array)
		{
			return value.EnumerateArray().Select(item => item.GetString() ?? "").ToList();
		}

		return new List<string>();
	}

	// Python truthiness of a JSON value: null, false, 0, "", [] and {} are false
	static bool IsTruthy(JsonElement value)
	{
		return value.ValueKind switch
		{
			JsonValueKind.Null or JsonValueKind.Undefined or JsonValueKind.False => false,
			JsonValueKind.Object => value.EnumerateObject().Any(),
			JsonValueKind.Array => value.GetArrayLength() > 0,
			JsonValueKind.String => value.GetString()!.Length > 0,
			JsonValueKind.Number => value.GetDouble() != 0,
			_ => true,
		};
	}
}
