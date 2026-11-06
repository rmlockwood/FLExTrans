// FixtureTests.cs - FTApertium.Tests
//
// Ron Lockwood
// SIL International
// 11/6/26
//
// Version 3.17 - 11/6/26 - Ron Lockwood
//  Initial version. FTApertium's unit tests.
//
// OVERVIEW (AI generated, then edited)
//
// The fixtures in fixtures/ are small inputs written to exercise what the real projects don't (see each file's comment), with expected output made by the Windows Apertium tools
// (make_fixtures.py). These tests hold the port to them two ways: stage by stage through ReferenceCheck, as ftapertium check does, and end to end through ApertiumTransfer, the object
// FTtranslator uses, which runs the stages on its own output and gathers their traces.
//
// CODE STRUCTURE
//
// FixtureTests: Fixture() finds a fixture folder; EveryStageMatchesTheTools() runs the reference check; the other tests run ApertiumTransfer on one fixture each.
//

using System.Reflection;
using System.Text;
using Xunit;

namespace FTtranslator.Apertium.Tests;

public class FixtureTests
{
	static readonly UTF8Encoding Utf8 = new(false);

	static string FixturesDir => typeof(FixtureTests).Assembly.GetCustomAttributes<AssemblyMetadataAttribute>().First(a => a.Key == "FixturesDir").Value!;

	static string Fixture(string name) => Path.Combine(FixturesDir, name);

	static string Read(string fixture, string file) => File.ReadAllText(Path.Combine(Fixture(fixture), file), Utf8);

	[Fact]
	public void EveryStageMatchesTheTools()
	{
		var report = new StringWriter();
		ReferenceCheck check = ReferenceCheck.Run(FixturesDir, null, report);

		Assert.True(check.AllIdentical, report.ToString());
	}

	[Fact]
	public void AdvancedTransferEndToEnd()
	{
		var transfer = new ApertiumTransfer(Fixture("advanced"), "tr.t1x", "tr.t2x", "tr.t3x");
		string output = transfer.Transfer(Read("advanced", "001.source.txt"));

		Assert.Equal(Read("advanced", "001.postchunk.txt"), output);

		// The log is the three stages' traces in order
		string expectedLog = Read("advanced", "001.trace.txt") + Read("advanced", "001.interchunk-trace.txt") + Read("advanced", "001.postchunk-trace.txt");
		Assert.Equal(expectedLog.Replace("\r\n", "\n"), transfer.Log);
	}

	[Fact]
	public void OneStageTransferEndToEnd()
	{
		var transfer = new ApertiumTransfer(Fixture("rules"), "tr.t1x");

		Assert.Equal(Read("rules", "001.transfer.txt"), transfer.Transfer(Read("rules", "001.source.txt")));
	}

	[Fact]
	public void RulesErrorStopsLikeApertium()
	{
		var transfer = new ApertiumTransfer(Fixture("error"), "tr.t1x");
		var e = Assert.Throws<TransferException>(() => transfer.Transfer(Read("error", "001.source.txt")));

		Assert.Equal("Error: unexpected expression: 'with-param'", e.Message);

		// The same object goes on working after an error
		Assert.Equal(Read("error", "002.transfer.txt"), transfer.Transfer(Read("error", "002.source.txt")));
	}
}
