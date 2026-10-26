#
#   fttranslator/translator
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The Translator API: one profile, set up once, translating any number of texts.
#
#   OVERVIEW (AI generated, then edited)
#
#   Translator is the API the command line uses, and the one a service or web app would use. Creating one sets up the process for a work project (env.bootstrap()) and loads its profile; after
#   that, translate() can be called any number of times. Each call opens the source project, runs the pipeline, releases the guessed approvals if the run stopped before doing so itself, closes
#   the project, and saves a run record.
#
#   TWO VIEWS OF ONE PROJECT
#
#   The source project is opened once per run, with flexicon and undoable=True, because the guessed approvals have to be undone afterwards; flexlibs opens with a session-long non-undoable task,
#   which would make that impossible. FLExTrans is written against flexlibs, though, and flexicon's same-named methods don't always behave the same (LexiconGetSenseCustomFieldNamed(None)
#   raises in flexicon instead of returning None). flexlibsView() therefore wraps the same open LcmCache in a flexlibs FLExProject for FLExTrans code. The view must never be closed; the flexicon
#   project owns the cache and closes it.
#
#   THE CONFIGURATION IS NEVER WRITTEN
#
#   Each run sets SourceTextName in its own copy of FlexTrans.config (Context.configMap), never in the file. Some FLExTrans code re-reads the configuration itself - RunApertium's makefile step,
#   and any custom module's MainFunction - so _configOverride() replaces ReadConfig.readConfig for the length of the run to hand back this run's copy instead.
#
#   RUN RECORDS
#
#   Every run that got as far as adding its text is saved as JSON in <work project>\Output\ftt_runs, named after the text's title. runs() reads them back, oldest first, for the runs command.
#
#   CODE STRUCTURE
#
#   Translator comes first: steps() builds the pipeline, readConfig() reads FlexTrans.config, translate() does a run, and runsDir(), saveRun() and runs() handle the run records. Then the
#   module-level helpers translate() uses: flexlibsView() and _configOverride().
#

import contextlib
import json
import re

from . import env as ftEnv
from . import pipeline
from . import profile as ftProfile
from .report import makeReporter

class Translator:
    '''Translates texts with one work project. Creating it sets up the process for that work project, which can only be done once per process (see env.bootstrap()).'''

    def __init__(self, workDir, modulesDir=None, verbose=False):

        self.env = ftEnv.bootstrap(workDir, modulesDir)
        self.profile = ftProfile.load(self.env.workDir)
        self.verbose = verbose

    def steps(self):
        '''Return the pipeline's steps: FTtranslator's own, the collection's and the hooks, in order.'''

        # Imported here because the step modules import FLExTrans code, which needs env.bootstrap() first
        from .steps import finish, flextrans, ingest

        return pipeline.build(self.profile, flextrans.builtins(), lambda entry: flextrans.loadFlexToolsModule(self.env, entry), before=ingest.STEPS, after=finish.STEPS, hookDirs=[self.profile.configDir])

    def readConfig(self, report):
        '''Return FlexTrans.config as a map. Stops with an error if it can't be read.'''

        import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

        configMap = ReadConfig.readConfig(report)

        if not configMap:

            raise SystemExit(f"Could not read {self.profile.configDir / ReadConfig.CONFIG_FILE}")

        return configMap

    def translate(self, text, options=None):
        '''Translate text and return the RunResult. The text is added to the source project as a new text, which is left there for review.'''

        from parse_priority import fw
        from .steps.ingest import releaseApprovals

        report = makeReporter(self.verbose)
        ctx = pipeline.Context(self.env, self.profile, None, report, self.readConfig(report), options or pipeline.Options())
        ctx.result.source = text
        steps = self.steps()

        # Undoable, so the guess approvals can be taken back after extraction
        ctx.db = fw.openProject(self.profile.sourceProject, write=True)
        ctx.ftDb = flexlibsView(ctx.db)

        # Afterwards, release the approvals if the run stopped before Extract Source Text did it, then close the project whatever happens
        try:
            with _configOverride(ctx):

                pipeline.run(steps, ctx)

        finally:
            try:
                releaseApprovals(ctx)
            finally:
                ctx.db.CloseProject()

        if ctx.result.title:

            self.saveRun(ctx.result)

        return ctx.result

    def runsDir(self):

        return self.env.workDir / "Output" / "ftt_runs"

    def saveRun(self, result):
        '''Save the run record as JSON, named after the text's title, and return its path.'''

        runsDir = self.runsDir()
        runsDir.mkdir(parents=True, exist_ok=True)

        # The title becomes the file name, so replace the characters Windows doesn't allow in one
        path = runsDir / (re.sub(r'[<>:"/\\|?*]', "_", result.title) + ".json")
        path.write_text(json.dumps(result.toDict(), ensure_ascii=False, indent=2), encoding="utf-8")
        result.record = str(path)

        return path

    def runs(self):
        '''Return the saved run records, oldest first.'''

        runsDir = self.runsDir()

        if not runsDir.is_dir():

            return []

        records = []

        for path in sorted(runsDir.glob("*.json"), key=lambda path: path.stat().st_mtime):

            records.append(json.loads(path.read_text(encoding="utf-8")))

        return records

def flexlibsView(project):
    '''Return a flexlibs FLExProject over a project flexicon already has open. See TWO VIEWS OF ONE PROJECT above. flexlibs' object is only a thin wrapper over the LcmCache, so it can share the
       open one. Never call CloseProject() on the view; the owner closes the project.'''

    import flexlibs

    view = flexlibs.FLExProject()
    view.project = project.project
    view.lp = view.project.LangProject
    view.lexDB = view.lp.LexDbOA
    view.writeEnabled = False

    return view

@contextlib.contextmanager
def _configOverride(ctx):
    '''For the length of the with block, make ReadConfig.readConfig() return this run's configuration. See THE CONFIGURATION IS NEVER WRITTEN above.'''

    import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

    original = ReadConfig.readConfig
    ReadConfig.readConfig = lambda report=None: dict(ctx.configMap)

    try:
        yield
    finally:
        ReadConfig.readConfig = original
