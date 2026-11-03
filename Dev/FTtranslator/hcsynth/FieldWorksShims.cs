// FieldWorksShims.cs
//
// Ron Lockwood
// SIL International
// 11/3/26
//
// Version 3.17 - 11/3/26 - Ron Lockwood
//  Initial version. Stands in for the few FieldWorks pieces HCSynthByGloss uses, so its unmodified source builds for .NET 8 on Linux.
//
// OVERVIEW (AI generated, then edited)
//
// HCSynthByGloss (the synthesizer FLExTrans runs for HermitCrab synthesis) lives in the FieldWorks repo and targets .NET Framework 4.8. Its project references three FieldWorks projects,
// but the code only touches two of them, and only in small ways. This file supplies those pieces, so the upstream .cs files in the upstream folder build unchanged:
//  - SIL.FieldWorks.WordWorks.Parser.HCParser (ParserCore): four string constants, the property keys FieldWorks' HermitCrab loader writes into the config. HcXmlTraceManager reads them
//    when it builds a trace. The values are copied from FieldWorks' HCParser.cs.
//  - SIL.Utils.XmlUtils (XMLUtils): CreateTransform(), which turns a trace into HTML using a stylesheet installed with FieldWorks. There is no such stylesheet here, so it throws; it is only
//    reached with -t (tracing), which FTtranslator never passes.
//  - The Icu namespace, which HCSynthByGlossDll.cs names in a using directive but never uses.
//

using System;
using System.Xml.Xsl;

namespace SIL.FieldWorks.WordWorks.Parser
{
	// Copied from FieldWorks' Src/LexText/ParserCore/HCParser.cs
	public static class HCParser
	{
		public const string MsaID = "ID";
		public const string Env = "Env";
		public const string PrefixEnv = "PrefixEnv";
		public const string SuffixEnv = "SuffixEnv";
	}
}

namespace SIL.Utils
{
	public static class XmlUtils
	{
		// Only used to show a trace as HTML (-t); see the overview above
		public static XslCompiledTransform CreateTransform(string xslName, string assemblyName)
		{
			throw new NotSupportedException("HTML trace output needs FieldWorks' stylesheets and isn't available in this build.");
		}
	}
}

namespace Icu
{
	// Only here so the using directive in HCSynthByGlossDll.cs resolves
	internal static class Unused
	{
	}
}
