"""Pipeline building and running, with stub steps (no FieldWorks needed)."""

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fttranslator import pipeline, profile  # noqa: E402


def make_work_project(root, collection, ftt_ini=None, hooks_py=None):
    cfg = Path(root) / "Config"
    (cfg / "Collections").mkdir(parents=True)
    (cfg / "FlexTrans.config").write_text("SourceTextName=x\n", encoding="utf-8")
    (cfg / "flextools.ini").write_text("[DEFAULT]\ncurrentproject = 'Src'\n", encoding="utf-8")
    (cfg / "Collections" / "Drafting.ini").write_text(collection, encoding="utf-8")
    if ftt_ini:
        (cfg / "fttranslator.ini").write_text(textwrap.dedent(ftt_ini), encoding="utf-8")
    if hooks_py:
        (cfg / "my_hooks.py").write_text(textwrap.dedent(hooks_py), encoding="utf-8")
    return cfg


class FakeReport:
    ERROR = 2
    BLANK = 3

    def __init__(self):
        self.messages, self.messageCounts = [], [0, 0, 0, 0]

    def _add(self, kind, msg, ref=None):
        self.messages.append((kind, msg, ref))
        self.messageCounts[kind] += 1

    def Info(self, msg, ref=None): self._add(0, msg, ref)
    def Warning(self, msg, ref=None): self._add(1, msg, ref)
    def Error(self, msg, ref=None): self._add(2, msg, ref)
    def Blank(self): self._add(3, None)


def stub(name, log, result=True, error=False):
    def func(ctx):
        log.append(name)
        if error:
            ctx.report.Error(f"{name} broke")
        return result
    return pipeline.Step(name, func, "builtin", f"FLExTrans\\{name.replace(' ', '')}.py")


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def builtins(self, log, **kw):
        names = ["Extract Source Text", "Run Apertium", "Synthesize Text"]
        table = {}
        for n in names:
            s = stub(n, log, **kw.get(n, {}))
            table[n.lower()] = table[pipeline.entry_key(s.source)] = s
        return table

    def test_entry_key(self):
        self.assertEqual(pipeline.entry_key("FLExTrans\\ExtractSourceText.py"), "extractsourcetext")
        self.assertEqual(pipeline.entry_key("FLExTrans/RunApertium.py"), "runapertium")
        self.assertEqual(pipeline.entry_key("FLExTrans.Run Apertium"), "run apertium")

    def test_profile_defaults(self):
        make_work_project(self.root, "[FLExTrans\\RunApertium.py]\n")
        p = profile.load(self.root)
        self.assertEqual(p.source_project, "Src")
        self.assertEqual(p.collection, "Drafting")
        self.assertEqual(p.collection_entries(), ["FLExTrans\\RunApertium.py"])

    def test_build_mixes_builtins_and_custom_in_collection_order(self):
        make_work_project(self.root, "[FLExTrans\\ExtractSourceText.py]\n\n[FLExTrans\\Custom.py]\n\n"
                                     "[FLExTrans.Synthesize Text]\n")
        log = []
        custom = lambda entry: pipeline.Step("Custom", lambda ctx: log.append("Custom"), "flextools", entry)
        steps = pipeline.build(profile.load(self.root), self.builtins(log), custom,
                               before=[stub("Import", log)], after=[stub("Collect", log)])
        self.assertEqual([s.name for s in steps],
                         ["Import", "Extract Source Text", "Custom", "Synthesize Text", "Collect"])
        self.assertEqual(steps[2].kind, "flextools")

    def test_hooks_are_placed_around_named_steps(self):
        cfg = make_work_project(
            self.root, "[FLExTrans\\ExtractSourceText.py]\n\n[FLExTrans\\RunApertium.py]\n",
            ftt_ini="""
                [hooks]
                before: Run Apertium = my_hooks:first
                after: extractsourcetext = my_hooks:second
            """,
            hooks_py="""
                def first(ctx): return True
                def second(ctx): return True
            """)
        log = []
        steps = pipeline.build(profile.load(self.root), self.builtins(log), None, hook_dirs=[cfg])
        self.assertEqual([s.name for s in steps],
                         ["Extract Source Text", "my_hooks:second", "my_hooks:first", "Run Apertium"])

    def test_hook_for_unknown_step_is_an_error(self):
        make_work_project(self.root, "[FLExTrans\\RunApertium.py]\n",
                          ftt_ini="[hooks]\nafter: Nope = x:y\n")
        with self.assertRaises(SystemExit):
            pipeline.build(profile.load(self.root), self.builtins([]), None)

    def run_steps(self, steps):
        ctx = pipeline.Context(None, None, None, FakeReport(), {}, pipeline.Options())
        pipeline.run(steps, ctx)
        return ctx

    def test_run_stops_on_false(self):
        log = []
        ctx = self.run_steps([stub("a", log), stub("b", log, result=False), stub("c", log)])
        self.assertEqual(log, ["a", "b"])
        self.assertFalse(ctx.result.ok)

    def test_run_stops_on_reported_error(self):
        log = []
        ctx = self.run_steps([stub("a", log, error=True), stub("b", log)])
        self.assertEqual(log, ["a"])
        self.assertFalse(ctx.result.ok)

    def test_run_catches_exceptions(self):
        def boom(ctx):
            raise ValueError("bad")
        log = []
        ctx = self.run_steps([pipeline.Step("boom", boom), stub("b", log)])
        self.assertEqual(log, [])
        self.assertIn("boom failed: bad", [m["message"] for m in ctx.result.messages])

    def test_run_ok(self):
        log = []
        ctx = self.run_steps([stub("a", log), pipeline.Step("none", lambda ctx: None)])
        self.assertTrue(ctx.result.ok)
        self.assertEqual(ctx.result.steps, ["a", "none"])


if __name__ == "__main__":
    unittest.main()
