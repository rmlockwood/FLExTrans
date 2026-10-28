#
#   fttranslator/translator
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.2 - 10/27/26 - Ron Lockwood
#    Keep the source and target projects open across runs, saving after each one; added close().
#
#   Version 3.17.1 - 10/27/26 - Ron Lockwood
#    Record the total time of each run.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The Translator API: one profile, set up once, translating any number of texts.
#
#   OVERVIEW (AI generated, then edited)
#
#   Translator is the API the command line uses, and the one a service or web app would use. Creating one sets up the process for a work project (env.bootstrap()) and loads its profile; after
#   that, translate() can be called any number of times. Each call runs the pipeline, releases the guessed approvals if the run stopped before doing so itself, saves the projects, and saves a
#   run record. close() (or leaving a with block) closes the projects. The steps are timed by pipeline.run(); translate() adds the total, which also covers opening the source project and saving.
#
#   KEEPING THE PROJECTS OPEN
#
#   Opening a FieldWorks project the first time in a process takes a couple of seconds, so both projects stay open from the first translate() until close(), and a session of translations pays
#   that only once. The source project is opened by translate() itself. The target is opened by whichever FLExTrans module asks for it first and then shared through SharedTarget (see
#   sharedtarget.py), which is in place only for the length of each run. After every run both projects are saved, so a crash loses at most the run in progress and Generate HC Config, which
#   reads the target's .fwdata file, sees the target as it is. Leaving the projects open means FLEx can't open them meanwhile (unless sharing is on), so callers should close() promptly.
#
#   TWO VIEWS OF ONE PROJECT
#
#   The source project is opened with flexicon and undoable=True, because the guessed approvals have to be undone afterwards; flexlibs opens with a session-long non-undoable task,
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
#   Translator comes first: close() (also called on leaving a with block) closes the projects, _sharedTarget() gives the run its SharedTarget, steps() builds the pipeline, readConfig() reads
#   FlexTrans.config, translate() does a run, and runsDir(), saveRun() and runs() handle the run records. Then the
#   module-level helpers translate() uses: flexlibsView() and _configOverride().
#

import contextlib
import json
import re
import time

from . import env as ftEnv
from . import pipeline
from . import profile as ftProfile
from .report import makeReporter
from .sharedtarget import SharedTarget, projectKey

class Translator:
    '''Translates texts with one work project. Creating it sets up the process for that work project, which can only be done once per process (see env.bootstrap()).'''

    def __init__(self, workDir, modulesDir=None, verbose=False):

        self.env = ftEnv.bootstrap(workDir, modulesDir)
        self.profile = ftProfile.load(self.env.workDir)
        self.verbose = verbose

        # Both projects are opened by the first translate() and stay open until close()
        self.sourceDb = None
        self.sharedTarget = None

    def __enter__(self):

        return self

    def __exit__(self, *excInfo):

        self.close()

    def close(self):
        '''Save and close the source and target projects, if a translation opened them. Safe to call more than once.'''

        try:
            if self.sharedTarget:

                self.sharedTarget.close()
                self.sharedTarget = None

        finally:
            if self.sourceDb is not None:

                sourceDb = self.sourceDb
                self.sourceDb = None
                sourceDb.CloseProject()

    def _sharedTarget(self, configMap, report):
        '''Return the SharedTarget for the configured target project, creating it on the first run, or None when there is no separate target project (One project mode, or no target set).'''

        import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

        twoProjectMode = ReadConfig.getConfigVal(configMap, ReadConfig.TWO_PROJECT_MODE, report, giveError=False) != "n"
        targetProject = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_PROJECT, report, giveError=False)

        if not (twoProjectMode and targetProject):

            return None

        # A target that names the source project is the same open project, not a second one to share
        if projectKey(targetProject) == projectKey(self.profile.sourceProject):

            return None

        if self.sharedTarget is None:

            self.sharedTarget = SharedTarget(targetProject)

        return self.sharedTarget

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

        # The total covers the whole run: opening the source project (on the first run only) and saving afterwards as well as the steps
        startTime = time.perf_counter()
        report = makeReporter(self.verbose)
        configMap = self.readConfig(report)
        ctx = pipeline.Context(self.env, self.profile, None, report, configMap, options or pipeline.Options())
        ctx.result.source = text
        steps = self.steps()

        # Open the source project on the first run and keep it open (see KEEPING THE PROJECTS OPEN above). Undoable, so the guess approvals can be taken back after extraction.
        if self.sourceDb is None:

            self.sourceDb = fw.openProject(self.profile.sourceProject, write=True)

        ctx.db = self.sourceDb
        ctx.ftDb = flexlibsView(ctx.db)
        sharedTarget = self._sharedTarget(configMap, report)

        # Afterwards, release the approvals if the run stopped before Extract Source Text did it, then save both projects whatever happens
        try:
            with _configOverride(ctx), sharedTarget.patched() if sharedTarget else contextlib.nullcontext():

                pipeline.run(steps, ctx)

        finally:
            try:
                releaseApprovals(ctx)
            finally:
                ctx.db.SaveChanges()

                if sharedTarget:

                    sharedTarget.save()

        ctx.result.totalSeconds = round(time.perf_counter() - startTime, 3)

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
