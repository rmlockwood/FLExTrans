"""
Opening a FieldWorks project and loading the LCM types this tool needs.

flexicon handles the FieldWorks/pythonnet bootstrapping (registry lookup,
ICU, SLDR). The LCM imports have to wait until after FLExInitialize(), so
they live in load_lcm() rather than at module level.
"""

import shutil
from pathlib import Path

import flexicon

_initialized = False
lcm = None  # filled in by load_lcm(): a namespace of the LCM types used here


class _Lcm:
    pass


def load_lcm():
    global _initialized, lcm
    if _initialized:
        return lcm
    flexicon.FLExInitialize()
    from SIL.LCModel import (IWfiWordform, IWfiAnalysis, IWfiGloss, ISegment,
                             IStTxtPara, IText, IWfiWordformRepository,
                             IPunctuationForm)
    from SIL.LCModel.DomainServices import (AnalysisGuessServices,
                                            AnalysisOccurrence, ParagraphParser)
    from SIL.LCModel.Core.Text import TsStringUtils
    ns = _Lcm()
    for name, val in list(locals().items()):
        if name not in ("ns",):
            setattr(ns, name, val)
    lcm = ns
    _initialized = True
    return lcm


def open_project(name, write=False):
    """Open a project by name. Write mode is undoable so a run can be rolled back."""
    load_lcm()
    project = flexicon.FLExProject()
    try:
        project.OpenProject(name, writeEnabled=write, undoable=True)
    except Exception as e:
        if "lock" in str(e).lower():
            raise SystemExit(
                f"Project '{name}' is locked -- close it in FieldWorks first "
                f"(or work on a copy with the 'copy' command).") from e
        raise
    return project


def projects_dir():
    from flexicon.code import FLExGlobals
    return Path(FLExGlobals.FWProjectsDir)


def copy_project(src_name, dst_name):
    """Copy a project folder under a new name (the .fwdata file is renamed to match)."""
    load_lcm()
    root = projects_dir()
    src, dst = root / src_name, root / dst_name
    if not (src / f"{src_name}.fwdata").exists():
        raise SystemExit(f"No project '{src_name}' in {root}")
    if dst.exists():
        raise SystemExit(f"'{dst}' already exists; pick another name or delete it first")
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.lock", "*.bak", "Temp"))
    (dst / f"{src_name}.fwdata").rename(dst / f"{dst_name}.fwdata")
    return dst
