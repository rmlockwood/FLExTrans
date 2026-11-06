#
#   apertium/tests/make_fixtures
#
#   Ron Lockwood
#   SIL International
#   11/6/26
#
#   Version 3.17 - 11/6/26 - Ron Lockwood
#    Initial version. Makes the expected output of FTApertium's test fixtures with the Windows Apertium tools FLExTrans ships.
#
#   OVERVIEW (AI generated, then edited)
#
#   FTApertium is checked against the Apertium tools, not against what anyone thinks they should do, so the expected output of each test fixture comes from running the real tools on it.
#   A fixture is a folder under fixtures/ holding the inputs written by hand: bilingual.dix, NNN.source.txt streams, and the rules files of the stages it tests (tr.t1x; tr.t2x and tr.t3x
#   for advanced transfer). This runs each stage as FLExTrans' makefiles do and writes beside them the files ReferenceCheck.cs compares against (see THE CASE FOLDER there).
#
#   WHEN TO RUN IT
#
#   After adding or changing a fixture, on Windows with FLExTrans' tools (FlexTools\Tools). Commit the inputs and the outputs together; the unit tests (FTApertium.Tests) only read them.
#
#   TRAPS
#
#    - Each stage reads the tool's output of the stage before, so a fixture tests one stage at a time, as ReferenceCheck reads it.
#    - Bytes in, bytes out: the streams are never decoded, so nothing is re-encoded.
#    - The Windows lt-proc turns each \n it writes into \r\n, a C runtime artifact the Linux build doesn't have. FLExTrans' own streams already have \r\n on Windows, so it never shows there;
#      a fixture written with \n would get \r\n back from lt-proc alone. runTool() undoes it when the input had no \r, so the expected output is what the tools do apart from that.
#    - A stage that fails gets an exit-code file and its later stages are skipped; ReferenceCheck then expects the port to fail with the same message.
#
#   CODE STRUCTURE
#
#   runTool() runs one tool; makeFixture() compiles a fixture's files and runs its streams through the stages, writing the output with writeStage(); main() does every fixture.
#

import subprocess
import sys
from pathlib import Path

DEFAULT_TOOLS = Path.home() / "Documents" / "FLExTransTOFT" / "FlexTools" / "Tools"

# The files this script writes, removed before a fixture is made again (the inputs stay)
GENERATED = ["*.bin", "*.biltrans.txt", "*.transfer.txt", "*.trace.txt", "*.exitcode.txt", "*.interchunk*.txt", "*.postchunk*.txt"]

# The rules stages: tool, its flags, the rules file, and the names of what it writes
STAGES = [("apertium-transfer", ["-b", "-t"], "tr.t1x", "transfer"), ("apertium-interchunk", ["-t"], "tr.t2x", "interchunk"), ("apertium-postchunk", ["-t"], "tr.t3x", "postchunk")]

def runTool(toolsDir, args, data, cwd):

    result = subprocess.run([str(toolsDir / (args[0] + ".exe"))] + args[1:], input=data, capture_output=True, cwd=cwd)

    # The Windows lt-proc writes each \n as \r\n (the C runtime's text mode), which the Linux tools and FTApertium don't do; undo it when the input had no \r (see TRAPS)
    if data is not None and b"\r" not in data:

        result.stdout = result.stdout.replace(b"\r\n", b"\n")

    return result

def writeStage(fixture, stem, name, result):
    '''Write a rules stage's output and trace with the names ReferenceCheck reads (the transfer stage's trace is NNN.trace.txt), and an exit-code file if it failed.'''

    (fixture / f"{stem}.{name}.txt").write_bytes(result.stdout)
    traceName = f"{stem}.trace.txt" if name == "transfer" else f"{stem}.{name}-trace.txt"
    (fixture / traceName).write_bytes(result.stderr)

    if result.returncode != 0:

        exitName = f"{stem}.exitcode.txt" if name == "transfer" else f"{stem}.{name}-exitcode.txt"
        (fixture / exitName).write_text(str(result.returncode))

def makeFixture(toolsDir, fixture):

    for pattern in GENERATED:

        for old in fixture.glob(pattern):

            old.unlink()

    # Compile as the makefiles do
    result = runTool(toolsDir, ["lt-comp", "lr", "bilingual.dix", "bilingual.bin"], None, fixture)

    if result.returncode != 0:

        raise SystemExit(f"{fixture.name}: lt-comp failed: {result.stderr.decode('utf-8', 'replace')}")

    stages = [stage for stage in STAGES if (fixture / stage[2]).exists()]

    for tool, flags, rulesFile, name in stages:

        result = runTool(toolsDir, ["apertium-preprocess-transfer", rulesFile, rulesFile + ".bin"], None, fixture)

        if result.returncode != 0:

            raise SystemExit(f"{fixture.name}: apertium-preprocess-transfer rejected {rulesFile}: {result.stderr.decode('utf-8', 'replace')}")

    for source in sorted(fixture.glob("*.source.txt")):

        stem = source.name[:3]
        result = runTool(toolsDir, ["lt-proc", "-b", "-N1", "-L1", "bilingual.bin"], source.read_bytes(), fixture)
        (fixture / f"{stem}.biltrans.txt").write_bytes(result.stdout)
        stream = result.stdout

        for tool, flags, rulesFile, name in stages:

            result = runTool(toolsDir, [tool] + flags + [rulesFile, rulesFile + ".bin"], stream, fixture)
            writeStage(fixture, stem, name, result)

            if result.returncode != 0:

                print(f"  {fixture.name} {stem}: {tool} failed: {result.stderr.decode('utf-8', 'replace').strip().splitlines()[-1:]}")
                break

            stream = result.stdout

    # The compiled files are only for the tools
    for old in fixture.glob("*.bin"):

        old.unlink()

    print(f"{fixture.name}: {len(list(fixture.glob('*.source.txt')))} stream(s), stages: lookup{''.join(', ' + s[3] for s in stages)}")

def main():

    toolsDir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TOOLS

    if not (toolsDir / "lt-proc.exe").exists():

        raise SystemExit(f"Usage: python make_fixtures.py [FlexTools\\Tools folder]  (no lt-proc.exe in {toolsDir})")

    for fixture in sorted(p for p in (Path(__file__).parent / "fixtures").iterdir() if p.is_dir()):

        makeFixture(toolsDir, fixture)

if __name__ == "__main__":

    main()
