#
#   fttranslator/profile
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Reads a translator profile: the work project plus an optional Config\fttranslator.ini.
#
#   OVERVIEW (AI generated, then edited)
#
#   A translator profile is one FLExTrans work project set up for a language pair. The work project is the single source of truth: the source project comes from Config\flextools.ini
#   (currentproject), and everything else FLExTrans needs comes from Config\FlexTrans.config, which is read later by FLExTrans' own ReadConfig. This file only adds what is specific to
#   FTtranslator, from an optional Config\fttranslator.ini.
#
#   FTTRANSLATOR.INI
#
#       [fttranslator]
#       collection = Drafting          ; the FlexTools collection to run
#       title_prefix = FTT             ; titles of the texts FTtranslator adds
#       source_project =               ; override flextools.ini's currentproject
#
#       [hooks]
#       ; Python callables run before/after a step: func(ctx) -> bool
#       after: Run Apertium = mypackage.fixups:tweak_transfer_output
#
#   The keys in the file keep their underscores (title_prefix, source_project) because they are what users write; the Python attributes they fill are camelCase. A hook key is read as
#   "<when>: <step name>", so the [hooks] section is parsed with '=' as its only delimiter - otherwise configparser would split the key at the colon.
#
#   NO IMPORTS OF FLEXTRANS OR FIELDWORKS
#
#   Nothing here imports FLExTrans or FieldWorks, so a profile can be loaded (and tested) before env.bootstrap() has run. flextools.ini is read with configparser directly; its values are
#   Python literals ('name', True, [...]), which _iniValue() turns back into Python values.
#
#   CODE STRUCTURE
#
#   Hook is one [hooks] entry and Profile is the loaded profile; Profile.collectionEntries() reads the collection .ini. _iniValue() decodes a flextools.ini value, parseHooks() reads the
#   [hooks] section, and load() puts it all together. Translator calls load(); pipeline.build() uses collectionEntries() and the hooks.
#

import ast
import configparser
from dataclasses import dataclass, field
from pathlib import Path

FTT_INI = "fttranslator.ini"

@dataclass
class Hook:
    '''One [hooks] entry. when is "before" or "after", step is the step name (compared case-insensitively) and target is "package.module:function".'''

    when: str
    step: str
    target: str

@dataclass
class Profile:
    '''A work project and the FTtranslator settings for it.'''

    workDir: Path
    sourceProject: str
    collection: str = "Drafting"
    titlePrefix: str = "FTT"
    hooks: list = field(default_factory=list)

    @property
    def configDir(self):

        return self.workDir / "Config"

    @property
    def collectionFile(self):

        return self.configDir / "Collections" / f"{self.collection}.ini"

    def collectionEntries(self):
        '''Return the section names of the collection .ini, in order. FlexTools runs the modules in this order.'''

        path = self.collectionFile

        if not path.exists():

            raise SystemExit(f"No collection '{self.collection}' ({path})")

        # Keep the case of the entries; configparser lowercases keys by default
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str  # type: ignore  # configparser documents replacing optionxform; the stubs type it as a method
        parser.read(path, encoding="utf-8")

        return parser.sections()

def _iniValue(raw):
    '''Decode a flextools.ini value, which is a Python literal ('name', True, [...]). Anything that isn't a literal comes back as the raw string.'''

    try:
        return ast.literal_eval(raw)

    except (ValueError, SyntaxError):

        return raw

def parseHooks(section):
    '''Return the Hooks in a [hooks] section. Each key is "before: Step Name" or "after: Step Name" and each value "module:function".'''

    hooks = []

    for key, target in section.items():

        when, separator, step = key.partition(":")
        when = when.strip().lower()

        if not separator or when not in ("before", "after") or ":" not in target:

            raise SystemExit(f"Bad hook '{key} = {target}'. Use 'before: Step Name = module:function'.")

        hooks.append(Hook(when, step.strip(), target.strip()))

    return hooks

def load(workDir):
    '''Load the profile for a work project: the source project from flextools.ini, then any settings and hooks from fttranslator.ini.'''

    workDir = Path(workDir).resolve()
    configDir = workDir / "Config"

    flexToolsIni = configparser.ConfigParser(interpolation=None)
    flexToolsIni.read(configDir / "flextools.ini", encoding="utf-8")
    sourceProject = _iniValue(flexToolsIni.get("DEFAULT", "currentproject", fallback="''"))

    profile = Profile(workDir, sourceProject)

    # '=' is the only delimiter, so a hook key like "after: Run Apertium" keeps its colon
    ownIni = configparser.ConfigParser(interpolation=None, delimiters=("=",))
    ownIni.optionxform = str  # type: ignore  # see collectionEntries()

    if (configDir / FTT_INI).exists():

        ownIni.read(configDir / FTT_INI, encoding="utf-8")

        if ownIni.has_section("fttranslator"):

            settings = ownIni["fttranslator"]
            profile.collection = settings.get("collection", profile.collection)
            profile.titlePrefix = settings.get("title_prefix", profile.titlePrefix)
            profile.sourceProject = settings.get("source_project") or profile.sourceProject

        if ownIni.has_section("hooks"):

            profile.hooks = parseHooks(ownIni["hooks"])

    if not profile.sourceProject:

        raise SystemExit(f"No source project: set currentproject in {configDir / 'flextools.ini'}")

    return profile
