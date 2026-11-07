#
#   offline/tests/make_textout_cases
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Applies every Text In/Out rule on this machine to real target texts with textout.py, for ftoffline check-textout.
#
#   OVERVIEW (AI generated, then edited)
#
#   The Text Out rules are regular expressions written for Python's regex module, and FTOffline applies them with .NET's Regex (TextOutRules.cs). This is the wide check that the two agree. It
#   finds every rules file (FLExTransSearchReplace, Text In or Text Out) under the given folders and every synthesized target text (Output\target_text*), then applies with textout.py each
#   distinct rule on its own, and each distinct rules file as a whole, to every text. It writes the texts once and, for each rule or file, the SHA-256 of each result and its message, so the
#   output stays a few MB. ftoffline check-textout <cases.json> applies the same rules with the C# port and compares.
#
#   On 11/6/26 that was 212 distinct rules (83 regular expressions) from 90 rules files (21 distinct) over 69 texts: all identical, once TextOutRules.cs gave \w and \b Python's meaning.
#
#   KEEP THE OUTPUT OUT OF THE REPO
#
#   The texts are the projects' own: write the cases file somewhere else (the default is the system's temporary folder).
#
#   CODE STRUCTURE
#
#   findRulesFiles() and findTexts() gather the data, ruleXml() makes a one-rule file, results() applies a rules file to every text, and main() writes the cases.
#

import argparse
import hashlib
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fttranslator.textout import TextOutRules

DEFAULT_ROOTS = [r"C:\Data\FLExTrans", str(Path.home() / "Documents" / "FLExTransTOFT" / "WorkProjects")]

def findRulesFiles(roots):
    '''The distinct rules files under the roots, as (path, contents), each parsed once to be sure it is well formed.'''

    seen = set()
    found = []

    for root in roots:

        for path in Path(root).rglob("*.xml"):

            try:
                data = path.read_bytes()

            except OSError:

                continue

            if b"FLExTransSearchReplace" not in data[:500] or data in seen:

                continue

            try:
                ET.fromstring(data)

            except ET.ParseError:

                continue

            seen.add(data)
            found.append((path, data.decode("utf-8")))

    return found

def findTexts(roots):
    '''The distinct synthesized target texts under the roots (Output\\target_text*, up to 2 MB).'''

    texts = []

    for root in roots:

        for path in Path(root).rglob("target_text*"):

            if "Output" not in path.parts or not path.is_file() or not 100 < path.stat().st_size < 2_000_000:

                continue

            try:
                texts.append(path.read_text(encoding="utf-8-sig"))

            except (OSError, UnicodeDecodeError):

                pass

    return list(dict.fromkeys(texts))

def ruleXml(search, replace, isRegex):

    root = ET.Element("FLExTransSearchReplace")
    container = ET.SubElement(root, "SearchReplaceRules")
    element = ET.SubElement(container, "SearchReplaceRule", {"RegEx": "yes" if isRegex else "no", "Inactive": "no", "Comment": ""})
    ET.SubElement(element, "SearchString").text = search
    ET.SubElement(element, "ReplaceString").text = replace

    return ET.tostring(root, encoding="unicode")

def results(xml, texts):
    '''[the SHA-256 of the result (None on a failure), the message] for each text.'''

    rules = TextOutRules(ET.ElementTree(ET.fromstring(xml)))
    out = []

    for text in texts:

        output, messages = rules.apply(text)
        out.append([None if output is None else hashlib.sha256(output.encode("utf-8")).hexdigest(), messages[0][1]])

    return out

def main():

    parser = argparse.ArgumentParser(description="Apply every Text In/Out rule found to real target texts with textout.py, for 'ftoffline check-textout'. Keep the output out of the repo.")
    parser.add_argument("out", nargs="?", default=str(Path(tempfile.gettempdir()) / "ftoffline-textout-cases.json"), help="the cases file to write")
    parser.add_argument("--roots", nargs="+", default=DEFAULT_ROOTS, help="folders to search for rules files and target texts")
    args = parser.parse_args()

    rulesFiles = findRulesFiles(args.roots)
    texts = findTexts(args.roots)
    cases = []
    rules = {}

    # Each distinct rule on its own, then each rules file as a whole
    for path, xml in rulesFiles:

        container = ET.fromstring(xml).find("SearchReplaceRules")

        for element in container if container is not None else []:

            if len(element) >= 2:

                rules.setdefault((element[0].text or "", element[1].text or "", element.get("RegEx") == "yes"), path)

    for (search, replace, isRegex), path in rules.items():

        xml = ruleXml(search, replace, isRegex)
        cases.append({"kind": "rule", "xml": xml, "results": results(xml, texts)})

    for path, xml in rulesFiles:

        cases.append({"kind": "file:" + str(path), "xml": xml, "results": results(xml, texts)})

    Path(args.out).write_text(json.dumps({"texts": texts, "cases": cases}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(rules)} distinct rules ({sum(1 for key in rules if key[2])} regular expressions), {len(rulesFiles)} distinct rules files, {len(texts)} texts. Now run:")
    print(f"  dotnet cli/bin/Release/net8.0/ftoffline.dll check-textout \"{args.out}\"")

if __name__ == "__main__":

    main()
