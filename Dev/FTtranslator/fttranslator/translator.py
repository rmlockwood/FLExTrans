"""
The translator: one profile, set up once, translating any number of texts.

This is the API the CLI uses, and the one a service or web app would use.
"""

import contextlib
import json
import re
from pathlib import Path

from . import env as ftenv
from . import pipeline
from . import profile as ftprofile
from .report import make_reporter


class Translator:
    def __init__(self, work_dir, modules_dir=None, verbose=False):
        self.env = ftenv.bootstrap(work_dir, modules_dir)
        self.profile = ftprofile.load(self.env.work_dir)
        self.verbose = verbose

    def steps(self):
        from .steps import finish, flextrans, ingest
        return pipeline.build(
            self.profile,
            flextrans.builtins(),
            lambda entry: flextrans.load_flextools_module(self.env, entry),
            before=ingest.STEPS,
            after=finish.STEPS,
            hook_dirs=[self.profile.config_dir])

    def read_config(self, report):
        import ReadConfig
        config_map = ReadConfig.readConfig(report)
        if not config_map:
            raise SystemExit(f"Could not read {self.profile.config_dir / ReadConfig.CONFIG_FILE}")
        return config_map

    def translate(self, text, options=None):
        from parse_priority import fw
        from .steps.ingest import release_approvals

        report = make_reporter(self.verbose)
        ctx = pipeline.Context(self.env, self.profile, None, report,
                               self.read_config(report), options or pipeline.Options())
        ctx.result.source = text
        steps = self.steps()
        # Undoable, so the guess approvals can be taken back after extraction.
        ctx.db = fw.open_project(self.profile.source_project, write=True)
        ctx.ft_db = flexlibs_view(ctx.db)
        try:
            with _config_override(ctx):
                pipeline.run(steps, ctx)
        finally:
            try:
                release_approvals(ctx)  # if the run stopped before extraction
            finally:
                ctx.db.CloseProject()
        if ctx.result.title:
            self.save_run(ctx.result)
        return ctx.result

    def runs_dir(self):
        return self.env.work_dir / "Output" / "ftt_runs"

    def save_run(self, result):
        d = self.runs_dir()
        d.mkdir(parents=True, exist_ok=True)
        path = d / (re.sub(r'[<>:"/\\|?*]', "_", result.title) + ".json")
        path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        result.record = str(path)
        return path

    def runs(self):
        d = self.runs_dir()
        if not d.is_dir():
            return []
        out = []
        for p in sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime):
            out.append(json.loads(p.read_text(encoding="utf-8")))
        return out


def flexlibs_view(project):
    """A flexlibs FLExProject over a project flexicon already has open.

    FLExTrans is written against flexlibs, and flexicon's same-named methods
    don't always behave the same (e.g. LexiconGetSenseCustomFieldNamed(None)
    raises instead of returning None). flexlibs' object is only a thin wrapper
    over the LcmCache, so it can share the open one. Never call CloseProject()
    on the view; the owner closes the project.
    """
    import flexlibs
    view = flexlibs.FLExProject()
    view.project = project.project
    view.lp = view.project.LangProject
    view.lexDB = view.lp.LexDbOA
    view.writeEnabled = False
    return view


@contextlib.contextmanager
def _config_override(ctx):
    """FLExTrans code that re-reads FlexTrans.config (RunApertium.run_makefile,
    custom modules' MainFunction) gets this run's configuration instead."""
    import ReadConfig
    original = ReadConfig.readConfig
    ReadConfig.readConfig = lambda report=None: dict(ctx.config_map)
    try:
        yield
    finally:
        ReadConfig.readConfig = original
