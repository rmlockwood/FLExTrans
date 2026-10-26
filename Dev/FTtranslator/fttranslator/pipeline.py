"""
The translation pipeline: a list of steps run in order over one Context.

The middle of the pipeline is the work project's FlexTools collection
(Drafting by default), read in order:
  * an entry for one of the standard FLExTrans drafting modules runs that
    module's core function directly (as TranslateText.py does);
  * any other entry is treated as a FlexTools module and run through its
    FlexToolsModule.Run(), so a custom module is added the same way as in
    FlexTools: put it in the collection.
FTtranslator's own steps go before (import, parse, approve) and after
(collect output). Hooks from fttranslator.ini add Python callables
before/after any step by name.

A step is a callable func(ctx) -> bool; False stops the pipeline, and so
does any error reported while the step runs.
"""

import importlib
import sys
import traceback
from dataclasses import dataclass, field, asdict
from typing import Callable

from .report import error_count, messages


@dataclass
class Options:
    insert: bool = False            # also insert the result into the target project
    keep_approvals: bool = False    # leave the guessed analyses approved in the source text
    title: str = None               # title for the new source text


@dataclass
class RunResult:
    title: str = None
    source: str = ""
    translation: str = None
    ok: bool = False
    steps: list = field(default_factory=list)
    approved: list = field(default_factory=list)       # {word, analysis, basis}
    unparsed: list = field(default_factory=list)       # words HermitCrab found no parse for
    unanalysed: list = field(default_factory=list)     # words left without an analysis
    untranslated: list = field(default_factory=list)   # source words with no link to a target sense
    unsynthesized: list = field(default_factory=list)  # target words the synthesizer failed on
    messages: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Context:
    env: object                 # env.Env
    profile: object             # profile.Profile
    db: object                  # source project: flexicon FLExProject (undoable)
    report: object              # FTReporter
    config_map: dict            # FlexTrans.config, with this run's overrides
    options: Options
    result: RunResult = field(default_factory=RunResult)
    state: dict = field(default_factory=dict)   # free space for custom steps
    ft_db: object = None        # the same project as a flexlibs FLExProject, for FLExTrans code

    def config(self, key, required=True):
        import ReadConfig
        return ReadConfig.getConfigVal(self.config_map, key, self.report, giveError=required)


@dataclass
class Step:
    name: str
    func: Callable
    kind: str = "builtin"       # builtin | flextools | hook | ftt
    source: str = ""

    def describe(self):
        where = f"  ({self.source})" if self.source else ""
        return f"{self.name:38s} {self.kind:9s}{where}"


def entry_key(entry):
    """'FLExTrans\\ExtractSourceText.py' -> 'extractsourcetext';
    'FLExTrans.Extract Source Text' -> 'extract source text'."""
    e = entry.replace("/", "\\")
    if e.lower().endswith(".py"):
        return e.rsplit("\\", 1)[-1][:-3].lower()
    return e.partition(".")[2].lower() if "." in e else e.lower()


def resolve_hook(target, search_dirs=()):
    module, _, func = target.partition(":")
    for d in search_dirs:
        if str(d) not in sys.path:
            sys.path.insert(0, str(d))
    return getattr(importlib.import_module(module), func)


def build(profile, builtins, load_custom, before=(), after=(), hook_dirs=()):
    """
    builtins:    {key: Step} where key is a module file stem or FTM_Name, lowercased
    load_custom: entry -> Step, for collection entries that aren't built in
    before/after: FTtranslator's own steps around the collection
    """
    middle = []
    for entry in profile.collection_entries():
        step = builtins.get(entry_key(entry))
        middle.append(step if step else load_custom(entry))
    steps = list(before) + middle + list(after)

    out = []
    for step in steps:
        names = {step.name.lower(), entry_key(step.source).lower() if step.source else ""}
        hooks = [h for h in profile.hooks if h.step.lower() in names]
        for h in hooks:
            if h.when == "before":
                out.append(Step(f"{h.target}", resolve_hook(h.target, hook_dirs), "hook", f"before {step.name}"))
        out.append(step)
        for h in hooks:
            if h.when == "after":
                out.append(Step(f"{h.target}", resolve_hook(h.target, hook_dirs), "hook", f"after {step.name}"))
    unknown = [h for h in profile.hooks
               if not any(h.step.lower() in (s.name.lower(), entry_key(s.source)) for s in steps)]
    if unknown:
        raise SystemExit("Hooks name steps that are not in the pipeline: "
                         + ", ".join(f"{h.when}: {h.step}" for h in unknown))
    return out


def run(steps, ctx):
    rep = ctx.report
    ctx.result.ok = False
    for step in steps:
        rep.Blank()
        rep.Info(f"== {step.name}")
        before = error_count(rep)
        try:
            ok = step.func(ctx)
        except SystemExit:
            raise
        except Exception as e:
            rep.Error(f"{step.name} failed: {e}", traceback.format_exc())
            ok = False
        ctx.result.steps.append(step.name)
        if ok is False or error_count(rep) > before:
            if ok is not False:
                rep.Error(f"Stopped after '{step.name}' because it reported an error.")
            break
    else:
        ctx.result.ok = True
    ctx.result.messages = messages(rep)
    return ctx.result.ok
