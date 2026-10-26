#
#   parse_priority/fw
#
#   Ron Lockwood
#   SIL International
#   10/26/26
#
#   Version 3.17 - 10/26/26 - Ron Lockwood
#    Initial version. Opens and copies FieldWorks projects and loads the LCM types parse_priority uses.
#
#   OVERVIEW (AI generated, then edited)
#
#   The one place parse_priority (and FTtranslator's own steps) touch FieldWorks start-up. flexicon handles the FieldWorks and pythonnet bootstrapping - the registry lookup, ICU and the SLDR.
#   The SIL.LCModel imports can only be done after flexicon.FLExInitialize(), so they can't sit at the top of a module; loadLcm() does them once and keeps the types in the module-level lcm
#   namespace, which the rest of the package uses as fw.lcm.IWfiAnalysis and so on.
#
#   OPENING PROJECTS
#
#   openProject() always opens undoable, so a write run can be rolled back with Undo - the parse_priority commands use that for their dry runs, and FTtranslator to release its guessed approvals.
#   A project that is open in FLEx is locked; that error is turned into a message suggesting the copy command, which copies the project folder on disk and works even while FLEx has it open.
#
#   CODE STRUCTURE
#
#   loadLcm() comes first, then openProject(), projectsDir() and copyProject(). FTtranslator's env.bootstrap() calls loadLcm() after flexlibs has initialized FieldWorks.
#

import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import flexicon

# The LCM types used in this package, filled in by loadLcm(). None until then. Typed Any because every user runs after loadLcm(), and the .NET types have no stubs to check against anyway.
lcm: Any = None

def loadLcm():
    '''Initialize FieldWorks through flexicon and import the LCM types this package uses into the lcm namespace. Safe to call more than once.'''

    global lcm

    if lcm is not None:

        return lcm

    flexicon.FLExInitialize()

    # Only importable once FieldWorks is initialized
    from SIL.LCModel import IWfiWordform, IWfiAnalysis, IWfiGloss, ISegment, IStTxtPara, IText, IWfiWordformRepository, IPunctuationForm  # type: ignore
    from SIL.LCModel.DomainServices import AnalysisGuessServices, AnalysisOccurrence, ParagraphParser  # type: ignore
    from SIL.LCModel.Core.Text import TsStringUtils  # type: ignore

    lcm = SimpleNamespace(IWfiWordform=IWfiWordform, IWfiAnalysis=IWfiAnalysis, IWfiGloss=IWfiGloss, ISegment=ISegment, IStTxtPara=IStTxtPara, IText=IText, IWfiWordformRepository=IWfiWordformRepository, IPunctuationForm=IPunctuationForm, AnalysisGuessServices=AnalysisGuessServices, AnalysisOccurrence=AnalysisOccurrence, ParagraphParser=ParagraphParser, TsStringUtils=TsStringUtils)
    return lcm

def openProject(name, write=False):
    '''Open a project by name. It is always opened undoable, so a write run can be rolled back.'''

    loadLcm()

    # Typed Any because the FLExProject.pyi stub pyflexicon 4.13 ships is out of date: it lacks OpenProject's undoable parameter, Undo() and UndoableOperation(), which this package relies on
    project: Any = flexicon.FLExProject()

    try:
        project.OpenProject(name, writeEnabled=write, undoable=True)

    except Exception as err:

        # A project open in FLEx is locked; say what to do about it
        if "lock" in str(err).lower():

            raise SystemExit(f"Project '{name}' is locked -- close it in FieldWorks first (or work on a copy with the 'copy' command).") from err

        raise

    return project

def projectsDir():
    '''The FieldWorks projects folder.'''

    from flexicon.code import FLExGlobals

    return Path(FLExGlobals.FWProjectsDir)

def copyProject(sourceName, newName):
    '''Copy a project folder under a new name, renaming its .fwdata file to match, and return the new folder.'''

    loadLcm()
    rootDir = projectsDir()
    sourceDir, newDir = rootDir / sourceName, rootDir / newName

    if not (sourceDir / f"{sourceName}.fwdata").exists():

        raise SystemExit(f"No project '{sourceName}' in {rootDir}")

    if newDir.exists():

        raise SystemExit(f"'{newDir}' already exists; pick another name or delete it first")

    # Leave out FLEx's lock, its backups and its temporary files
    shutil.copytree(sourceDir, newDir, ignore=shutil.ignore_patterns("*.lock", "*.bak", "Temp"))
    (newDir / f"{sourceName}.fwdata").rename(newDir / f"{newName}.fwdata")

    return newDir
