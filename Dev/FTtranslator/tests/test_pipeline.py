#
#   tests/test_pipeline
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Tests the profile, building the pipeline, hooks and the run loop with stub steps.
#
#   OVERVIEW (AI generated, then edited)
#
#   Unit tests for the parts of FTtranslator that don't need FieldWorks: loading a profile, building the pipeline from a collection with hooks in place, and the run loop's rules for stopping.
#   Each test builds a throwaway work project in a temporary folder (makeWorkProject()) and uses stub steps that only log their names, so nothing here imports FLExTrans or opens a project.
#   Run them from Dev\FTtranslator with python -m unittest discover -s tests.
#
#   FAKES
#
#   FakeReport stands in for flextoolslib's FTReporter. It keeps the two things pipeline.run() reads - messages and messageCounts - and uses the same message kinds (0 info to 3 blank).
#
#   CODE STRUCTURE
#
#   makeWorkProject(), FakeReport and stub() are the fixtures. TestPipeline holds the tests: entryKey(), the profile defaults, building (collection order, hooks, an unknown hook), then running
#   (stopping on False, on a reported error and on an exception, and a clean run).
#

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

# The package is one folder up from the tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import pipeline, profile  # noqa: E402

def makeWorkProject(rootDir, collection, fttIni=None, hooksPy=None):
    '''Create a minimal work project in rootDir with the given Drafting collection, and optionally an fttranslator.ini and a my_hooks.py. Returns its Config folder.'''

    configDir = Path(rootDir) / "Config"
    (configDir / "Collections").mkdir(parents=True)
    (configDir / "FlexTrans.config").write_text("SourceTextName=x\n", encoding="utf-8")
    (configDir / "flextools.ini").write_text("[DEFAULT]\ncurrentproject = 'Src'\n", encoding="utf-8")
    (configDir / "Collections" / "Drafting.ini").write_text(collection, encoding="utf-8")

    if fttIni:

        (configDir / "fttranslator.ini").write_text(textwrap.dedent(fttIni), encoding="utf-8")

    if hooksPy:

        (configDir / "my_hooks.py").write_text(textwrap.dedent(hooksPy), encoding="utf-8")

    return configDir

class FakeReport:
    '''Stands in for FTReporter. See FAKES above.'''

    ERROR = 2
    BLANK = 3

    def __init__(self):

        self.messages = []
        self.messageCounts = [0, 0, 0, 0]

    def _add(self, kind, message, reference=None):

        self.messages.append((kind, message, reference))
        self.messageCounts[kind] += 1

    def Info(self, message, reference=None):

        self._add(0, message, reference)

    def Warning(self, message, reference=None):

        self._add(1, message, reference)

    def Error(self, message, reference=None):

        self._add(2, message, reference)

    def Blank(self):

        self._add(3, None)

def stub(name, log, result=True, error=False):
    '''Return a built-in Step that logs its name when it runs, optionally reports an error, and returns result. Its source is a FLExTrans module path made from the name.'''

    def func(ctx):

        log.append(name)

        if error:

            ctx.report.Error(f"{name} broke")

        return result

    return pipeline.Step(name, func, "builtin", f"FLExTrans\\{name.replace(' ', '')}.py")

class TestPipeline(unittest.TestCase):

    def setUp(self):

        self.tmp = tempfile.TemporaryDirectory()
        self.rootDir = self.tmp.name

    def tearDown(self):

        self.tmp.cleanup()

    def builtins(self, log, **stubOptions):
        '''Stub built-in steps for three drafting modules, keyed both ways as flextrans.builtins() does. stubOptions maps a step name to stub()'s keyword arguments.'''

        table = {}

        for name in ["Extract Source Text", "Run Apertium", "Synthesize Text"]:

            step = stub(name, log, **stubOptions.get(name, {}))
            table[name.lower()] = table[pipeline.entryKey(step.source)] = step

        return table

    def test_entryKey(self):

        self.assertEqual(pipeline.entryKey("FLExTrans\\ExtractSourceText.py"), "extractsourcetext")
        self.assertEqual(pipeline.entryKey("FLExTrans/RunApertium.py"), "runapertium")
        self.assertEqual(pipeline.entryKey("FLExTrans.Run Apertium"), "run apertium")

    def test_profile_defaults(self):

        makeWorkProject(self.rootDir, "[FLExTrans\\RunApertium.py]\n")
        loaded = profile.load(self.rootDir)
        self.assertEqual(loaded.sourceProject, "Src")
        self.assertEqual(loaded.collection, "Drafting")
        self.assertEqual(loaded.collectionEntries(), ["FLExTrans\\RunApertium.py"])

    def test_build_mixes_builtins_and_custom_in_collection_order(self):

        makeWorkProject(self.rootDir, "[FLExTrans\\ExtractSourceText.py]\n\n[FLExTrans\\Custom.py]\n\n[FLExTrans.Synthesize Text]\n")
        log = []
        loadCustom = lambda entry: pipeline.Step("Custom", lambda ctx: log.append("Custom"), "flextools", entry)
        steps = pipeline.build(profile.load(self.rootDir), self.builtins(log), loadCustom, before=[stub("Import", log)], after=[stub("Collect", log)])
        self.assertEqual([step.name for step in steps], ["Import", "Extract Source Text", "Custom", "Synthesize Text", "Collect"])
        self.assertEqual(steps[2].kind, "flextools")

    def test_hooks_are_placed_around_named_steps(self):

        # One hook names its step by name, the other by its module file
        fttIni = """
            [hooks]
            before: Run Apertium = my_hooks:first
            after: extractsourcetext = my_hooks:second
        """
        hooksPy = """
            def first(ctx): return True
            def second(ctx): return True
        """
        configDir = makeWorkProject(self.rootDir, "[FLExTrans\\ExtractSourceText.py]\n\n[FLExTrans\\RunApertium.py]\n", fttIni=fttIni, hooksPy=hooksPy)
        log = []
        steps = pipeline.build(profile.load(self.rootDir), self.builtins(log), None, hookDirs=[configDir])
        self.assertEqual([step.name for step in steps], ["Extract Source Text", "my_hooks:second", "my_hooks:first", "Run Apertium"])

    def test_hook_for_unknown_step_is_an_error(self):

        makeWorkProject(self.rootDir, "[FLExTrans\\RunApertium.py]\n", fttIni="[hooks]\nafter: Nope = x:y\n")

        with self.assertRaises(SystemExit):

            pipeline.build(profile.load(self.rootDir), self.builtins([]), None)

    def runSteps(self, steps):
        '''Run the steps over a Context with a FakeReport and return the Context.'''

        ctx = pipeline.Context(None, None, None, FakeReport(), {}, pipeline.Options())
        pipeline.run(steps, ctx)

        return ctx

    def test_run_stops_on_false(self):

        log = []
        ctx = self.runSteps([stub("a", log), stub("b", log, result=False), stub("c", log)])
        self.assertEqual(log, ["a", "b"])
        self.assertFalse(ctx.result.ok)

    def test_run_stops_on_reported_error(self):

        log = []
        ctx = self.runSteps([stub("a", log, error=True), stub("b", log)])
        self.assertEqual(log, ["a"])
        self.assertFalse(ctx.result.ok)

    def test_run_catches_exceptions(self):

        def boom(ctx):

            raise ValueError("bad")

        log = []
        ctx = self.runSteps([pipeline.Step("boom", boom), stub("b", log)])
        self.assertEqual(log, [])
        self.assertIn("boom failed: bad", [message["message"] for message in ctx.result.messages])

    def test_run_ok(self):

        log = []
        ctx = self.runSteps([stub("a", log), pipeline.Step("none", lambda ctx: None)])
        self.assertTrue(ctx.result.ok)
        self.assertEqual(ctx.result.steps, ["a", "none"])

if __name__ == "__main__":

    unittest.main()
