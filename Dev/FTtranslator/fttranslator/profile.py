"""
A translator profile: one FLExTrans work project, set up for a language pair.

The work project is the single source of truth. The source project comes
from Config\\flextools.ini (currentproject), everything else from
Config\\FlexTrans.config. An optional Config\\fttranslator.ini adds what is
specific to FTtranslator:

    [fttranslator]
    collection = Drafting          ; the FlexTools collection to run
    title_prefix = FTT             ; titles of the texts FTtranslator adds
    source_project =               ; override flextools.ini's currentproject

    [hooks]
    ; Python callables run before/after a step: func(ctx) -> bool
    after: Run Apertium = mypackage.fixups:tweak_transfer_output

Nothing here imports FLExTrans or FieldWorks, so it can be used (and tested)
before the environment is set up.
"""

import ast
import configparser
from dataclasses import dataclass, field
from pathlib import Path

FTT_INI = "fttranslator.ini"


@dataclass
class Hook:
    when: str       # "before" or "after"
    step: str       # step name, compared case-insensitively
    target: str     # "package.module:function"


@dataclass
class Profile:
    work_dir: Path
    source_project: str
    collection: str = "Drafting"
    title_prefix: str = "FTT"
    hooks: list = field(default_factory=list)

    @property
    def config_dir(self):
        return self.work_dir / "Config"

    @property
    def collection_file(self):
        return self.config_dir / "Collections" / f"{self.collection}.ini"

    def collection_entries(self):
        """Section names of the collection .ini, in order (FlexTools runs them in this order)."""
        path = self.collection_file
        if not path.exists():
            raise SystemExit(f"No collection '{self.collection}' ({path})")
        cp = configparser.ConfigParser(interpolation=None)
        cp.optionxform = str
        cp.read(path, encoding="utf-8")
        return cp.sections()


def _ini_value(raw):
    """flextools.ini values are Python literals ('name', True, [...])."""
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


def parse_hooks(section):
    hooks = []
    for key, target in section.items():
        when, sep, step = key.partition(":")
        when = when.strip().lower()
        if not sep or when not in ("before", "after") or ":" not in target:
            raise SystemExit(f"Bad hook '{key} = {target}'. Use 'before: Step Name = module:function'.")
        hooks.append(Hook(when, step.strip(), target.strip()))
    return hooks


def load(work_dir):
    work_dir = Path(work_dir).resolve()
    cfg = work_dir / "Config"
    ft = configparser.ConfigParser(interpolation=None)
    ft.read(cfg / "flextools.ini", encoding="utf-8")
    source = _ini_value(ft.get("DEFAULT", "currentproject", fallback="''"))

    profile = Profile(work_dir, source)
    own = configparser.ConfigParser(interpolation=None, delimiters=("=",))
    own.optionxform = str
    if (cfg / FTT_INI).exists():
        own.read(cfg / FTT_INI, encoding="utf-8")
        if own.has_section("fttranslator"):
            s = own["fttranslator"]
            profile.collection = s.get("collection", profile.collection)
            profile.title_prefix = s.get("title_prefix", profile.title_prefix)
            profile.source_project = s.get("source_project") or profile.source_project
        if own.has_section("hooks"):
            profile.hooks = parse_hooks(own["hooks"])
    if not profile.source_project:
        raise SystemExit(f"No source project: set currentproject in {cfg / 'flextools.ini'}")
    return profile
