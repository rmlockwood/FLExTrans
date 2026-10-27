#
#   fttranslator/pipeline
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17.2 - 10/27/26 - Ron Lockwood
#    Time each step and record the times in the run result.
#
#   Version 3.17.1 - 10/26/26 - Ron Lockwood
#    Updated the default title in the Options docstring.
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. The translation pipeline: the steps built from the collection and hooks, and the loop that runs them.
#
#   OVERVIEW (AI generated, then edited)
#
#   A translation is a list of steps run in order over one Context. FTtranslator's own steps go first (Import Text, Parse Words, Approve Guesses) and last (Collect Output). The middle is the
#   work project's FlexTools collection (Drafting by default), in the collection's own order:
#    - An entry for one of the standard FLExTrans drafting modules runs that module's core function directly, as TranslateText.py does (see steps/flextrans.py).
#    - Any other entry is treated as a FlexTools module and run through its FlexToolsModule.Run(), so a custom module is added the same way as in FlexTools: put it in the collection.
#   Hooks from fttranslator.ini add Python callables before or after any step, by name.
#
#   STEPS
#
#   A step is a callable func(ctx) -> bool. Returning False stops the pipeline, and so does any error reported while the step runs, even if the step then returns True - a FLExTrans core function
#   often reports an error and carries on. Returning None counts as success, so a hook that forgets to return still lets the run go on. An exception from a step is reported and stops the run;
#   SystemExit is let through, since it is how FTtranslator reports a set-up problem to the command line. Each step that runs is timed into ctx.result.timings, which --timing (or -v) prints.
#
#   NAMING A STEP
#
#   A collection entry can name a module two ways, as FlexTools allows: by path ('FLExTrans\ExtractSourceText.py') or by '<subfolder>.<FTM_Name>' ('FLExTrans.Extract Source Text').
#   entryKey() reduces both to one lower-case key, which is how built-in steps are looked up and how a hook can name a step by its module file as well as by its name. A hook that names no step in
#   the pipeline is an error, since a typo would otherwise silently skip the hook.
#
#   THE CONTEXT
#
#   Context is what every step and hook gets. Hooks are written by users, so its attributes are documented in README.md: db is the source project opened with flexicon (undoable), ftDb is a
#   flexlibs view of the same open project for FLExTrans code, configMap is this run's copy of FlexTrans.config, result is the RunResult being filled in, and state is free space for custom steps.
#   RunResult is saved as JSON for each run, so its field names are the run record's keys; renaming one breaks reading older records.
#
#   CODE STRUCTURE
#
#   Options, RunResult, Context and Step come first. entryKey() and resolveHook() are helpers for build(), which turns a profile into the list of steps with the hooks in place. run() runs that
#   list over a Context. Translator calls build() through its steps() method and run() from translate().
#

import importlib
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Callable

from .report import errorCount, messages

@dataclass
class Options:
    '''What the caller asked for. insert also inserts the result into the target project; keepApprovals leaves the guessed analyses approved in the source text; title names the new
       source text (default: the profile's title prefix, the date and time, and the text's first three words).'''

    insert: bool = False
    keepApprovals: bool = False
    title: str | None = None

@dataclass
class RunResult:
    '''The outcome of one run, saved as JSON in the run record. The field names are the record's keys.'''

    title: str | None = None
    source: str = ""
    translation: str | None = None
    ok: bool = False
    steps: list = field(default_factory=list)

    # Each approved word as {word, location, analysis, basis}
    approved: list = field(default_factory=list)

    # Words HermitCrab found no parse for, words left without an analysis, source words with no link to a target sense, and target words the synthesizer failed on
    unparsed: list = field(default_factory=list)
    unanalysed: list = field(default_factory=list)
    untranslated: list = field(default_factory=list)
    unsynthesized: list = field(default_factory=list)

    messages: list = field(default_factory=list)

    # Each step that ran as {step, seconds}, filled in by run(). totalSeconds is the whole of Translator.translate(), including opening and closing the source project.
    timings: list = field(default_factory=list)
    totalSeconds: float | None = None

    # Where the run record was saved, filled in by Translator.saveRun(). Not a field, so it isn't written into the record itself.
    record = None

    def toDict(self):

        return asdict(self)

@dataclass
class Context:
    '''What every step and hook gets. See THE CONTEXT above.'''

    # Typed Any rather than object: the FieldWorks and flextoolslib types have no stubs, and object would make every ctx.db.Method() a type-checker warning
    env: Any                    # env.Env
    profile: Any                # profile.Profile
    db: Any                     # the source project: a flexicon FLExProject (undoable)
    report: Any                 # FTReporter
    configMap: dict             # FlexTrans.config, with this run's overrides
    options: Options
    result: RunResult = field(default_factory=RunResult)
    state: dict = field(default_factory=dict)   # free space for custom steps
    ftDb: Any = None            # the same project as a flexlibs FLExProject, for FLExTrans code

    def config(self, key, required=True):
        '''Return a FlexTrans.config value from this run's configuration. When required, a missing value is reported as an error.'''

        import ReadConfig  # FLExTrans Lib, only importable after env.bootstrap()

        return ReadConfig.getConfigVal(self.configMap, key, self.report, giveError=required)

@dataclass
class Step:
    '''One step of the pipeline. kind is builtin, flextools, hook or ftt; source is the collection entry or what a hook is attached to.'''

    name: str
    func: Callable
    kind: str = "builtin"
    source: str = ""

    def describe(self):
        '''One line for the steps command.'''

        where = f"  ({self.source})" if self.source else ""
        return f"{self.name:38s} {self.kind:9s}{where}"

def entryKey(entry):
    '''Reduce a collection entry to the key built-in steps are looked up by. 'FLExTrans\\ExtractSourceText.py' -> 'extractsourcetext'; 'FLExTrans.Extract Source Text' -> 'extract source text'.'''

    normalized = entry.replace("/", "\\")

    # A path: the file's stem
    if normalized.lower().endswith(".py"):

        return normalized.rsplit("\\", 1)[-1][:-3].lower()

    # '<subfolder>.<FTM_Name>': the name
    return normalized.partition(".")[2].lower() if "." in normalized else normalized.lower()

def resolveHook(target, searchDirs=()):
    '''Import the function a hook names ("package.module:function"), looking in searchDirs as well as on sys.path.'''

    moduleName, _, functionName = target.partition(":")

    for searchDir in searchDirs:

        if str(searchDir) not in sys.path:

            sys.path.insert(0, str(searchDir))

    return getattr(importlib.import_module(moduleName), functionName)

def build(profile, builtins, loadCustom, before=(), after=(), hookDirs=()):
    '''Return the pipeline's steps in order. builtins maps a key (a module file stem or FTM_Name, lowercased) to its Step; loadCustom turns any other collection entry into a Step; before and
       after are FTtranslator's own steps around the collection; hookDirs are extra folders hooks can be imported from.'''

    # The collection, with the standard drafting modules replaced by their built-in steps
    middle = []

    for entry in profile.collectionEntries():

        step = builtins.get(entryKey(entry))
        middle.append(step if step else loadCustom(entry))

    steps = list(before) + middle + list(after)

    # Put each hook just before or just after the step it names. A hook can name a step by its name or by its module file.
    withHooks = []

    for step in steps:

        names = {step.name.lower(), entryKey(step.source).lower() if step.source else ""}
        hooks = [hook for hook in profile.hooks if hook.step.lower() in names]

        for hook in hooks:

            if hook.when == "before":

                withHooks.append(Step(f"{hook.target}", resolveHook(hook.target, hookDirs), "hook", f"before {step.name}"))

        withHooks.append(step)

        for hook in hooks:

            if hook.when == "after":

                withHooks.append(Step(f"{hook.target}", resolveHook(hook.target, hookDirs), "hook", f"after {step.name}"))

    # A hook that names no step would otherwise be skipped without a word
    unknown = [hook for hook in profile.hooks if not any(hook.step.lower() in (step.name.lower(), entryKey(step.source)) for step in steps)]

    if unknown:

        raise SystemExit("Hooks name steps that are not in the pipeline: " + ", ".join(f"{hook.when}: {hook.step}" for hook in unknown))

    return withHooks

def run(steps, ctx):
    '''Run the steps in order over ctx, stopping at the first one that fails (see STEPS above). Fills in ctx.result and returns whether every step succeeded.'''

    report = ctx.report
    ctx.result.ok = False

    for step in steps:

        report.Blank()
        report.Info(f"== {step.name}")
        errorsBefore = errorCount(report)
        startTime = time.perf_counter()

        try:
            ok = step.func(ctx)

        except SystemExit:

            raise

        except Exception as err:

            report.Error(f"{step.name} failed: {err}", traceback.format_exc())
            ok = False

        # A failed step is timed too, so a slow failure shows up
        ctx.result.timings.append({"step": step.name, "seconds": round(time.perf_counter() - startTime, 3)})
        ctx.result.steps.append(step.name)

        # A step fails by returning False or by reporting an error
        if ok is False or errorCount(report) > errorsBefore:

            if ok is not False:

                report.Error(f"Stopped after '{step.name}' because it reported an error.")

            break
    else:
        ctx.result.ok = True

    ctx.result.messages = messages(report)
    return ctx.result.ok
