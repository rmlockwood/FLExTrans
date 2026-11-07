// FixtureTests.cs - FTOffline.Tests
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. FTOffline's unit tests.
//
// OVERVIEW (AI generated, then edited)
//
// FTOffline is a port of the Python offline translator, so its tests hold it to the Python's output, made by make_fixtures.py: the FTT-Scratch texts in fixtures/ftt-scratch are translated
// from deploy/bundle and compared step by step through StageCheck (what ftoffline check does with a whole project), and the Text Out fixture, written to hit what TextOutRules.cs has to get
// right, is compared with textout.py's result and messages. The last tests pin down the Python string behaviour PyStr and FullCase reproduce, with the values Python 3.13 gives.
//
// CODE STRUCTURE
//
// FixtureTests: Fixture() finds a fixture folder; EveryStepMatchesPython() and TranslatesEndToEnd() use the FTT-Scratch fixtures; the TextOut*() tests use fixtures/textout; the rest test PyStr
// and FullCase directly.
//

using System.Reflection;
using System.Text;
using Xunit;

namespace FTtranslator.Offline.Tests;

public class FixtureTests
{
	static readonly UTF8Encoding Utf8 = new(false);

	static string Metadata(string key) => typeof(FixtureTests).Assembly.GetCustomAttributes<AssemblyMetadataAttribute>().First(a => a.Key == key).Value!;

	static string Fixture(string name) => Path.Combine(Metadata("FixturesDir"), name);

	static string Read(string fixture, string file) => File.ReadAllText(Path.Combine(Fixture(fixture), file), Utf8);

	[Fact]
	public void EveryStepMatchesPython()
	{
		using var translator = new OfflineTranslator(Metadata("BundleDir"));
		var report = new StringWriter();
		StageCheck check = StageCheck.Run(translator, Path.Combine(Fixture("ftt-scratch"), "stages"), report);

		Assert.True(check.AllIdentical, report.ToString());
		Assert.Equal(5, check.Texts);
	}

	[Fact]
	public void TranslatesEndToEnd()
	{
		using var translator = new OfflineTranslator(Metadata("BundleDir"));
		RunResult result = translator.Translate(Read("ftt-scratch", "texts/01-joue.txt"));

		// The Python translator's translation of the same text, from the recorded run record
		var recorded = System.Text.Json.Nodes.JsonNode.Parse(Read("ftt-scratch", "stages/01-joue.json"))!;

		Assert.True(result.Ok);
		Assert.Equal((string?)recorded["result"]!["translation"], result.Translation);
		Assert.Equal(new[] { "Import Text", "Parse Words", "Approve Guesses", "Extract Source Text", "Run Apertium", "Synthesize Text" }, result.Steps);

		// A second text starts from the bundle again and gives the same result
		Assert.Equal(result.Translation, translator.Translate(Read("ftt-scratch", "texts/01-joue.txt")).Translation);
	}

	[Fact]
	public void TextOutMatchesPython()
	{
		TextOutRules rules = TextOutRules.Parse(Read("textout", "rules.xml"));
		(string? text, string message, bool ok) = rules.Apply(Read("textout", "input.txt"));

		Assert.True(ok);
		Assert.Equal(Read("textout", "expected.txt"), text);
		Assert.Equal(Read("textout", "expected-message.txt"), message);
	}

	[Fact]
	public void TextOutFailureNamesTheRule()
	{
		TextOutRules rules = TextOutRules.Parse(Read("textout", "error.xml"));
		(string? text, string message, bool ok) = rules.Apply(Read("textout", "input.txt"));

		Assert.False(ok);
		Assert.Null(text);
		Assert.Equal(Read("textout", "error-message.txt"), message);
	}

	[Fact]
	public void PythonWordCharacters()
	{

		// Python's \w takes the ZWNJ and a Devanagari vowel sign (a spacing mark); .NET's alone takes neither
		Assert.Matches(TextOutRules.PythonPattern(@"^\w+$"), "mi\u200Cravad");
		Assert.Matches(TextOutRules.PythonPattern(@"^\w+$"), "का");
		Assert.DoesNotMatch(TextOutRules.PythonPattern(@"end\Z"), "end\n");

		// An escaped backslash before w is left alone
		Assert.Equal(@"\\w", TextOutRules.PythonPattern(@"\\w"));
	}

	[Fact]
	public void PythonCaseMappings()
	{
		Assert.Equal("STRASSE", FullCase.Upper("straße"));
		Assert.Equal("FINE", FullCase.Upper("ﬁne"));
		Assert.Equal("I", FullCase.Upper("ı"));
		Assert.Equal("i̇stanbul", FullCase.Lower("İstanbul"));
		Assert.Equal("οδος σοφος.", FullCase.Lower("ΟΔΟΣ ΣΟΦΟΣ."));
		Assert.Equal("ǅemal Straße", PyStr.Title("ǆemal straße"));
		Assert.Equal("They'Re", PyStr.Title("they're"));
		Assert.Equal("Ss", PyStr.Capitalize("ß"));
	}

	[Fact]
	public void PythonStringMethods()
	{
		Assert.Equal(new[] { "a", "b", "c", "d" }, PyStr.SplitLines("a\u001Cb\r\nc" + (char)0x2028 + "d\n"));
		Assert.Equal("x", PyStr.Strip("\u001F x \u001C"));
		Assert.Equal(new[] { "a", "b" }, PyStr.Split(" a　 b "));
		Assert.True(PyStr.IsUpper("ⅫABC"));
		Assert.False(PyStr.IsUpper("ǅ"));
		Assert.True(PyStr.IsLower("ʰa"));
		Assert.Equal("aXbXc", TextOutRules.ReplaceAll("abc", "", "X")[1..^1]);
	}
}
