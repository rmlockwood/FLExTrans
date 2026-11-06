#
#   apertium/tests/make_reference
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Makes reference output from real work projects with the Windows Apertium tools, for ftapertium check.
#
#   OVERVIEW (AI generated, then edited)
#
#   The fixtures in fixtures/ are small and made by hand; this is the wide check. For every work project under the given folders that has a source stream and a bilingual lexicon, every
#   distinct .t1x anywhere under the project (the current file, rule history, backups, Live Rule Tester copies) is run over the project's stream with the Apertium tools FLExTrans ships, and the
#   result goes into one case folder per rules file, in the layout ReferenceCheck.cs reads (see THE CASE FOLDER there). Then ftapertium check <output folder> runs FTApertium over the same
#   inputs. On 11/6/26 that was 284 rules files from 75 projects, every stream and trace identical.
#
#   ADVANCED TRANSFER
#
#   A .t1x with a .t2x and .t3x beside it of the same name (tr.t1x, tr.t2x, tr.t3x), or else in a project configured for advanced transfer (TransferRulesFile2 and 3), also gets the interchunk
#   and postchunk stages. Each stage reads the tool's output of the stage before, so a difference points at one stage.
#
#   KEEP THE OUTPUT OUT OF THE REPO
#
#   The case folders hold the projects' lexicons and texts, and the repository is public: write them somewhere else (the default is a folder in the system's temporary folder).
#
#   TRAPS
#
#    - The source stream is whichever of Build\source_text-aper.txt, Output\source_text.aper and Output\source_text.txt the project has (older projects and the Testbed use the Output names).
#    - A rules file apertium-preprocess-transfer rejects gets a SKIP file instead of output, since it isn't a test of the run-time; ReferenceCheck passes it over.
#    - Projects' streams written on Windows have \r\n line ends, which the tools pass through, so no line-end fix is needed here (compare make_fixtures.py).
#
#   CODE STRUCTURE
#
#   runTool() runs one tool, configValue() reads one FlexTrans.config setting, runStage() runs and saves one rules stage, and makeProject() makes a project's case folders. main() reads the
#   arguments and does every project in every root.
#

import argparse
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_TOOLS = Path.home() / "Documents" / "FLExTransTOFT" / "FlexTools" / "Tools"

# Ron's work project folders, used when no roots are given
DEFAULT_ROOTS = [r"C:\Data\FLExTrans\Dev\Active Projects\WorkProjects", r"C:\Data\FLExTrans\Dev\Test Projects\WorkProjects", str(Path.home() / "Documents" / "FLExTransTOFT" / "WorkProjects"),
                 r"C:\Data\FLExTrans\Testbed - Python3 - FlexTools2.2.1\FLExTransTestbed\WorkProjects"]

# Where a project's source stream may be, in order (see TRAPS above)
STREAMS = [r"Build\source_text-aper.txt", r"Output\source_text.aper", r"Output\source_text.txt"]

def runTool(toolsDir, args, data, cwd):

    return subprocess.run([str(toolsDir / (args[0] + ".exe"))] + args[1:], input=data, capture_output=True, cwd=cwd)

def configValue(project, key):
    '''A setting from the project's FlexTrans.config, or "" when there is none.'''

    config = project / "Config" / "FlexTrans.config"

    if not config.exists():

        return ""

    match = re.search(rf"^{key}=(.*)$", config.read_text(encoding="utf-8", errors="replace"), re.M)

    return match.group(1).strip() if match else ""

def runStage(toolsDir, caseDir, name, args, data):
    '''Run one rules stage and save its output, trace and exit code with the names ReferenceCheck reads. Returns the output, or None if the tool failed.'''

    result = runTool(toolsDir, args, data, caseDir)
    (caseDir / f"001.{name}.txt").write_bytes(result.stdout)
    (caseDir / ("001.trace.txt" if name == "transfer" else f"001.{name}-trace.txt")).write_bytes(result.stderr)

    if result.returncode != 0:

        (caseDir / ("001.exitcode.txt" if name == "transfer" else f"001.{name}-exitcode.txt")).write_text(str(result.returncode))

        return None

    return result.stdout

def makeProject(toolsDir, outDir, project, counts):
    '''Make the case folders for one project, one per distinct rules file (with its stage 2 and 3 files). counts holds the running totals.'''

    dix = project / "Output" / "bilingual.dix"
    source = next((project / s for s in STREAMS if (project / s).exists() and (project / s).stat().st_size >= 50), None)

    if source is None or not dix.exists():

        return

    # The project's bilingual stream, made once
    work = outDir / "_bil" / f"{project.parent.parent.name[:10]}-{project.name}"
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dix, work / "bilingual.dix")

    if runTool(toolsDir, ["lt-comp", "lr", "bilingual.dix", "bilingual.bin"], None, work).returncode != 0:

        print(f"{project.name}: lt-comp failed, skipped")

        return

    stream = source.read_bytes()
    biltrans = runTool(toolsDir, ["lt-proc", "-b", "-N1", "-L1", "bilingual.bin"], stream, work).stdout

    # The project's configured stage 2 and 3 files, for a .t1x with none beside it
    configured = [project / configValue(project, "TransferRulesFile2"), project / configValue(project, "TransferRulesFile3")]
    configured = configured if all(p.suffix in (".t2x", ".t3x") and p.exists() for p in configured) else None
    seen = set()

    for t1x in sorted(project.rglob("*.t1x")):

        try:
            data = t1x.read_bytes()

        except OSError:

            continue

        if b"<transfer" not in data:

            continue

        siblings = [t1x.with_suffix(".t2x"), t1x.with_suffix(".t3x")]
        later = siblings if all(p.exists() for p in siblings) else configured
        key = hashlib.sha1(data + b"".join(p.read_bytes() for p in later or [])).hexdigest()

        if key in seen:

            continue

        seen.add(key)
        counts["cases"] += 1
        caseDir = outDir / f"{counts['cases']:04}-{project.name.replace(' ', '_')[:40]}"
        caseDir.mkdir()
        (caseDir / "tr.t1x").write_bytes(data)
        (caseDir / "rules-source.txt").write_text("\n".join(str(p) for p in [source, t1x] + (later or [])), encoding="utf-8")
        shutil.copyfile(dix, caseDir / "bilingual.dix")
        (caseDir / "001.source.txt").write_bytes(stream)
        (caseDir / "001.biltrans.txt").write_bytes(biltrans)
        result = runTool(toolsDir, ["apertium-preprocess-transfer", "tr.t1x", "transfer_rules.t1x.bin"], None, caseDir)

        # A rules file the compiler rejects isn't a test of the run-time (see TRAPS above)
        if result.returncode != 0:

            (caseDir / "SKIP-preprocess-failed.txt").write_bytes(result.stderr)
            counts["skipped"] += 1

            continue

        output = runStage(toolsDir, caseDir, "transfer", ["apertium-transfer", "-b", "-t", "tr.t1x", "transfer_rules.t1x.bin"], biltrans)

        if later is None or output is None:

            continue

        shutil.copyfile(later[0], caseDir / "tr.t2x")
        shutil.copyfile(later[1], caseDir / "tr.t3x")

        if not all(runTool(toolsDir, ["apertium-preprocess-transfer", f"tr.{x}", f"transfer_rules.{x}.bin"], None, caseDir).returncode == 0 for x in ("t2x", "t3x")):

            (caseDir / "tr.t2x").unlink()
            (caseDir / "tr.t3x").unlink()

            continue

        counts["advanced"] += 1
        output = runStage(toolsDir, caseDir, "interchunk", ["apertium-interchunk", "-t", "tr.t2x", "transfer_rules.t2x.bin"], output)

        if output is not None:

            runStage(toolsDir, caseDir, "postchunk", ["apertium-postchunk", "-t", "tr.t3x", "transfer_rules.t3x.bin"], output)

def main():

    parser = argparse.ArgumentParser(description="Make reference output from real work projects with the Windows Apertium tools, for 'ftapertium check'. Keep it out of the repo.")
    parser.add_argument("out", nargs="?", default=str(Path(tempfile.gettempdir()) / "ftapertium-reference"), help="the folder to write the case folders to (emptied first)")
    parser.add_argument("--roots", nargs="+", default=DEFAULT_ROOTS, help="folders holding work projects")
    parser.add_argument("--tools", default=str(DEFAULT_TOOLS), help="FlexTools\\Tools, with the Apertium tools")
    args = parser.parse_args()

    toolsDir = Path(args.tools)
    outDir = Path(args.out)

    if outDir.exists():

        shutil.rmtree(outDir)

    outDir.mkdir(parents=True)
    counts = {"cases": 0, "skipped": 0, "advanced": 0}

    for root in (Path(r) for r in args.roots):

        if not root.is_dir():

            print(f"Not a folder, skipped: {root}")

            continue

        for project in sorted(p for p in root.iterdir() if p.is_dir()):

            makeProject(toolsDir, outDir, project, counts)

    print(f"{counts['cases']} cases ({counts['advanced']} with advanced transfer), {counts['skipped']} skipped because apertium-preprocess-transfer rejected the rules file. Now run:")
    print(f"  dotnet cli/bin/Release/net8.0/ftapertium.dll check \"{outDir}\"")

if __name__ == "__main__":

    main()
